"""
[1단계] AI 기반 메일 분석 및 오류 정보 추출

Qwen 2.5 Coder 7B Instruct (또는 Qwen 2.5 7B Instruct)를 활용하여
이메일(본문 + 첨부파일 포함)에서 정확한 오류 내용을 추출하고
다음 단계(2단계 RAG 검색)를 위한 구조화된 요약을 생성합니다.

출력 구조:
  - error_summary       : 오류 요약 (한국어, 2-3문장)
  - error_type          : 예외 클래스명
  - error_message       : 오류 메시지 원문
  - severity            : CRITICAL / HIGH / MEDIUM / LOW
  - affected_components : [{"class_name", "method_name", "line"}]
  - root_cause          : 근본 원인 추정
  - search_queries      : RAG 검색용 키워드 목록
  - has_stack_trace     : bool
  - has_attachment      : bool
"""

import os
import time
import re
import json
import sys
import io
import email as email_module
from email import policy as email_policy
from pathlib import Path
from typing import List, Dict, Optional
import requests

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass

# Windows cp949 콘솔에서 유니코드 문자(✓,✗,이모지) 출력 시 오류 방지
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, io.UnsupportedOperation):
    pass


# ──────────────────────────────────────────────────────────────────────────────
# 1. 파일 읽기 (포맷 자동 감지)
# ──────────────────────────────────────────────────────────────────────────────

class EmailReader:
    """이메일/로그 파일을 읽어 순수 텍스트로 변환"""

    SUPPORTED_EXTENSIONS = {'.txt', '.eml', '.log', '.msg', '.csv', '.xml', '.json', '.err'}

    def read_file_smart(self, file_path: str) -> str:
        """확장자 감지 → EML은 MIME 파싱, 나머지는 텍스트 읽기"""
        ext = Path(file_path).suffix.lower()
        if ext == '.eml':
            return self._read_eml(file_path)
        return self._read_text(file_path)

    def _read_text(self, file_path: str) -> str:
        """다중 인코딩 시도 텍스트 읽기"""
        for enc in ('utf-8', 'cp949', 'euc-kr', 'latin-1'):
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    return f.read()
            except (UnicodeDecodeError, LookupError):
                continue
        with open(file_path, 'rb') as f:
            return f.read().decode('utf-8', errors='replace')

    def _read_eml(self, file_path: str) -> str:
        """EML 파일 MIME 파싱 → 헤더 + 본문 + 첨부파일 텍스트 추출"""
        texts = []
        try:
            with open(file_path, 'rb') as f:
                raw = f.read()
            try:
                msg = email_module.message_from_bytes(raw, policy=email_policy.default)
            except Exception:
                msg = email_module.message_from_bytes(raw)

            # 헤더
            texts += [
                "[메일 헤더]",
                f"제목: {msg.get('subject', '')}",
                f"발신: {msg.get('from', '')}",
                f"날짜: {msg.get('date', '')}",
                "---"
            ]

            body_written = False
            for part in msg.walk():
                content_type = part.get_content_type()
                disp         = str(part.get('Content-Disposition', ''))
                filename     = part.get_filename()

                # 본문 (text/plain)
                if 'attachment' not in disp and content_type == 'text/plain':
                    try:
                        payload = part.get_content()
                    except Exception:
                        payload = part.get_payload(decode=True)
                        payload = payload.decode('utf-8', errors='replace') if payload else ''
                    texts += ["[본문]", payload]
                    body_written = True

                # 본문 (text/html → 태그 제거)
                elif content_type == 'text/html' and 'attachment' not in disp and not body_written:
                    try:
                        payload = part.get_content()
                    except Exception:
                        payload = part.get_payload(decode=True)
                        payload = payload.decode('utf-8', errors='replace') if payload else ''
                    clean = re.sub(r'<[^>]+>', ' ', payload)
                    clean = re.sub(r'\s+', ' ', clean).strip()
                    texts += ["[본문(HTML→텍스트)]", clean]
                    body_written = True

                # 첨부파일 (텍스트 형식만 내용 추출)
                elif 'attachment' in disp and filename:
                    ext = Path(filename).suffix.lower()
                    texts.append(f"\n[첨부파일: {filename}]")
                    if ext in ('.txt', '.log', '.xml', '.json', '.csv', '.err'):
                        try:
                            raw_bytes = part.get_payload(decode=True)
                            if raw_bytes:
                                texts.append(raw_bytes.decode('utf-8', errors='replace'))
                        except Exception:
                            pass

        except Exception as e:
            texts += [f"[EML 파싱 오류: {e} - 텍스트 fallback]",
                      self._read_text(file_path)]

        return '\n'.join(texts)

    def read_folder(self, folder_path: str) -> Dict[str, str]:
        """폴더 내 지원 파일 전부 읽기"""
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder_path}")
        result = {}
        for fp in sorted(folder.rglob('*')):
            if fp.is_file() and fp.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    content = self.read_file_smart(str(fp))
                    key = str(fp.relative_to(folder))
                    result[key] = content
                    print(f"✓ 읽기 성공: {key}")
                except Exception as e:
                    print(f"✗ 읽기 실패: {fp} - {e}")
        return result

    def read_files(self, file_paths: List[str]) -> Dict[str, str]:
        """지정된 파일 목록 읽기"""
        result = {}
        for fp in file_paths:
            p = Path(fp)
            if not p.exists():
                print(f"✗ 파일 없음: {fp}")
                continue
            try:
                content = self.read_file_smart(fp)
                result[p.name] = content
                print(f"✓ 읽기 성공: {p.name}")
            except Exception as e:
                print(f"✗ 읽기 실패: {fp} - {e}")
        return result


# ──────────────────────────────────────────────────────────────────────────────
# 2. LLM 기반 오류 분석기
# ──────────────────────────────────────────────────────────────────────────────

class LLMEmailAnalyzer:
    """
    LLM 기반 이메일 오류 분석기 (기본: Groq compound-beta, Ollama/OpenAI 선택 가능).
    이메일 내용을 받아 구조화된 오류 정보 + RAG 검색 쿼리를 생성합니다.
    """

    OLLAMA_URL = "http://localhost:11434"

    SYSTEM_PROMPT = """당신은 Java 엔터프라이즈 애플리케이션 오류를 전문적으로 분석하는 AI입니다.
이메일 또는 로그 파일 내용을 읽고, 오류 정보를 정확하게 추출하여 구조화된 JSON으로 반환하세요.
이 정보는 다음 단계에서 RAG 기반 소스코드 검색에 활용됩니다.

반드시 다음 JSON 형식만 출력하세요 (설명 없이 JSON만):
{
  "error_summary": "오류 요약 (한국어, 2-3문장, 오류 상황과 영향 포함)",
  "error_type": "예외 클래스명 (예: NullPointerException, SQLException, RuntimeException 등)",
  "error_message": "오류 메시지 원문",
  "severity": "CRITICAL 또는 HIGH 또는 MEDIUM 또는 LOW",
  "affected_components": [
    {"class_name": "클래스명만", "method_name": "메서드명", "line": 라인번호_정수_또는_null}
  ],
  "root_cause": "근본 원인 추정 (한국어, 구체적으로 작성)",
  "search_queries": [
    "클래스명 메서드명 형태의 검색어1",
    "관련 비즈니스 로직 키워드2",
    "오류 관련 코드 패턴 키워드3"
  ],
  "has_stack_trace": true 또는 false,
  "has_attachment": true 또는 false
}"""

    MOCK_RESULT = {
        "error_summary": "[Mock 데모] CustomerService.validateCustomerData()에서 NullPointerException이 발생했습니다. 고객명(customerName) 필드가 null인 상태로 문자열 처리 메서드가 호출되어 시스템 오류가 발생했습니다.",
        "error_type": "NullPointerException",
        "error_message": "Cannot invoke \"String.length()\" because \"customerName\" is null",
        "severity": "HIGH",
        "affected_components": [
            {"class_name": "CustomerService",  "method_name": "validateCustomerData",  "line": 45},
            {"class_name": "CustomerService",  "method_name": "processCustomerOrder", "line": 102},
            {"class_name": "OrderController",  "method_name": "createOrder",           "line": 67}
        ],
        "root_cause": "고객 이름 입력값에 대한 null 체크가 누락되어 있으며, 유효성 검증 로직 실행 전에 문자열 처리를 시도하고 있음",
        "search_queries": [
            "CustomerService validateCustomerData",
            "OrderController createOrder customer",
            "customer name null validation"
        ],
        "has_stack_trace": True,
        "has_attachment": False
    }

    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, llm_type: str = "groq",
                 model_name: str = "compound-beta",
                 api_key: str = None,
                 use_mock: bool = False,
                 ollama_url: str = None):
        self.llm_type   = llm_type
        self.model_name = model_name
        self.api_key    = api_key or os.environ.get("GROQ_API_KEY", "")
        self.use_mock   = use_mock
        self.ollama_url = ollama_url or self.OLLAMA_URL

    def analyze(self, email_content: str, file_name: str = "") -> Dict:
        """이메일 내용 → 구조화된 오류 정보 Dict"""
        if self.use_mock:
            result = dict(self.MOCK_RESULT)
            result["file_name"]  = file_name
            result["llm_model"]  = "mock"
            print(f"  [Mock] {file_name}")
            return result

        try:
            if self.llm_type == "ollama":
                return self._call_ollama(email_content, file_name)
            elif self.llm_type == "openai":
                return self._call_openai(email_content, file_name)
            elif self.llm_type == "groq":
                return self._call_groq(email_content, file_name)
            else:
                raise ValueError(f"지원하지 않는 LLM: {self.llm_type}")
        except Exception as e:
            print(f"  ⚠ LLM 오류 ({e}), 정규식 fallback 실행")
            return self._fallback_regex(email_content, file_name)

    # ── Ollama ──────────────────────────────────────────────
    def _call_ollama(self, content: str, file_name: str) -> Dict:
        truncated = content[:6000] if len(content) > 6000 else content

        payload = {
            "model":  self.model_name,
            "system": self.SYSTEM_PROMPT,
            "prompt": (
                f"파일명: {file_name}\n\n"
                f"=== 이메일/로그 내용 ===\n{truncated}\n=== 끝 ==="
            ),
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1, "num_ctx": 8192}
        }

        resp = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=180
        )
        resp.raise_for_status()

        raw    = resp.json().get("response", "{}")
        result = self._parse_json(raw)
        result.update({"file_name": file_name, "llm_model": self.model_name})
        print(f"  ✓ Ollama({self.model_name}): {result.get('error_type','?')} / {result.get('severity','?')}")
        return result

    # ── Groq ────────────────────────────────────────────────
    def _call_groq(self, content: str, file_name: str) -> Dict:
        truncated = content[:6000] if len(content) > 6000 else content
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user",   "content": (
                    f"파일명: {file_name}\n\n"
                    f"=== 이메일/로그 내용 ===\n{truncated}\n=== 끝 ==="
                )}
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        retry_waits = [5, 15, 30]
        for attempt, wait in enumerate(retry_waits + [None], start=1):
            try:
                resp = requests.post(
                    self.GROQ_URL,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                resp.raise_for_status()
                raw    = resp.json()["choices"][0]["message"]["content"]
                result = self._parse_json(raw)
                result.update({"file_name": file_name, "llm_model": self.model_name})
                print(f"  ✓ Groq({self.model_name}): {result.get('error_type','?')} / {result.get('severity','?')}")
                return result
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and wait is not None:
                    print(f"  ⚠ Rate limit (429), {wait}초 대기 후 재시도 ({attempt}/{len(retry_waits)})...")
                    time.sleep(wait)
                    continue
                raise  # 다른 HTTP 오류는 상위로 전파
        raise RuntimeError("Groq API Rate Limit 시도 초과")

    # ── OpenAI ──────────────────────────────────────────────
    def _call_openai(self, content: str, file_name: str) -> Dict:
        import openai
        client    = openai.OpenAI(api_key=self.api_key)
        truncated = content[:8000] if len(content) > 8000 else content

        resp = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user",   "content": f"파일: {file_name}\n\n{truncated}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        raw    = resp.choices[0].message.content
        result = self._parse_json(raw)
        result.update({"file_name": file_name, "llm_model": self.model_name})
        print(f"  ✓ OpenAI({self.model_name}): {result.get('error_type','?')}")
        return result

    # ── JSON 파싱 ────────────────────────────────────────────
    def _parse_json(self, raw: str) -> Dict:
        cleaned = re.sub(r'```(?:json)?\s*', '', raw).replace('```', '').strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
        return {
            "error_summary": cleaned[:500],
            "error_type":    "Unknown",
            "error_message": "",
            "severity":      "MEDIUM",
            "affected_components": [],
            "root_cause":    "JSON 파싱 실패",
            "search_queries": [],
            "has_stack_trace": False,
            "has_attachment":  False
        }

    # ── 정규식 Fallback ──────────────────────────────────────
    _STACK_RE = re.compile(r'at\s+([\w.$]+)\.([\w<>]+)\(([\w.]+):(\d+)\)')
    _EXC_RE   = re.compile(r'([\w.]+Exception):\s*(.*)')
    _LIB_PREFIXES = ('java.', 'sun.', 'org.springframework.', 'org.apache.',
                     'com.sun.', 'jdk.', 'javax.', 'ch.qos.')

    def _fallback_regex(self, content: str, file_name: str) -> Dict:
        exceptions    = self._EXC_RE.findall(content)
        stack_matches = self._STACK_RE.findall(content)

        components = []
        seen = set()
        for full_cls, method, _file, line in stack_matches:
            if any(full_cls.startswith(p) for p in self._LIB_PREFIXES):
                continue
            class_name = full_cls.split('.')[-1]
            key = f"{class_name}.{method}"
            if key not in seen:
                seen.add(key)
                components.append({"class_name": class_name, "method_name": method, "line": int(line)})
            if len(components) >= 8:
                break

        exc_type = exceptions[0][0] if exceptions else "Unknown"
        exc_msg  = exceptions[0][1].strip() if exceptions else ""
        queries  = list(dict.fromkeys(
            f"{c['class_name']} {c['method_name']}" for c in components[:5]
        ))

        return {
            "file_name":   file_name,
            "llm_model":   "regex-fallback",
            "error_summary": f"[정규식 분석] {exc_type}: {exc_msg[:300]}",
            "error_type":    exc_type,
            "error_message": exc_msg,
            "severity":      "HIGH" if components else "MEDIUM",
            "affected_components": components,
            "root_cause":    "LLM 없이 정규식으로 Stack Trace 추출",
            "search_queries": queries,
            "has_stack_trace": bool(stack_matches),
            "has_attachment":  "[첨부파일:" in content,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 3. 통합 파서 (앱 / CLI 공용 진입점)
# ──────────────────────────────────────────────────────────────────────────────

class EmailParser:
    """
    1단계 통합 클래스.
    EmailReader(파일 읽기) + LLMEmailAnalyzer(AI 분석)를 조합합니다.
    기존 인터페이스(parse_all_emails, parse_files, save_parsed_results) 호환.
    """

    SUPPORTED_EXTENSIONS = EmailReader.SUPPORTED_EXTENSIONS

    def __init__(self, email_folder: str = "email",
                 llm_type: str = "groq",
                 model_name: str = "compound-beta",
                 api_key: str = None,
                 use_mock: bool = False):
        self.email_folder = Path(email_folder)
        self.reader   = EmailReader()
        self.analyzer = LLMEmailAnalyzer(
            llm_type=llm_type, model_name=model_name,
            api_key=api_key, use_mock=use_mock
        )

    def parse_all_emails(self, folder_path: Optional[str] = None) -> Dict:
        """폴더 내 모든 지원 파일을 읽어 AI 분석"""
        folder   = folder_path or str(self.email_folder)
        contents = self.reader.read_folder(folder)
        return self._analyze_all(contents)

    def parse_files(self, file_paths: List[str]) -> Dict:
        """개별 파일 목록을 읽어 AI 분석"""
        contents = self.reader.read_files(file_paths)
        return self._analyze_all(contents)

    def _analyze_all(self, contents: Dict[str, str]) -> Dict:
        results = {}
        total   = len(contents)
        for idx, (file_name, content) in enumerate(contents.items(), 1):
            print(f"\n🤖 [{idx}/{total}] AI 분석: {file_name}")
            analysis = self.analyzer.analyze(content, file_name)

            # 2단계(RAG extractor) 호환 필드 생성
            results[file_name] = {
                **analysis,
                "has_error": bool(
                    analysis.get("affected_components") or
                    analysis.get("error_type", "Unknown") != "Unknown"
                ),
                "raw_text": content[:500],
                # RAG가 참조하는 stack_traces 형식
                "stack_traces": [
                    {
                        "class_name": c.get("class_name", ""),
                        "method":     c.get("method_name", ""),
                        "full_class": c.get("class_name", ""),
                        "package":    "",
                        "file":       f"{c.get('class_name','')}.java",
                        "line":       c.get("line")
                    }
                    for c in analysis.get("affected_components", [])
                ],
                "exceptions": [
                    {
                        "exception": analysis.get("error_type", ""),
                        "message":   analysis.get("error_message", "")
                    }
                ]
            }
        return results

    def save_parsed_results(self, results: Dict,
                            output_file: str = "output/step1_parsed_errors.json"):
        out = Path(output_file)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ AI 분석 결과 저장: {out}")


# ──────────────────────────────────────────────────────────────────────────────
# CLI 실행
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("[1단계] AI 기반 이메일 오류 분석")
    print("=" * 60)

    parser = EmailParser(
        email_folder="email",
        llm_type="ollama",
        model_name="qwen2.5-coder:7b",
        use_mock=False
    )

    try:
        print("\n📧 이메일 폴더 읽는 중...")
        results = parser.parse_all_emails()

        print(f"\n📊 총 {len(results)}개 파일 처리 완료")
        for file_name, r in results.items():
            print(f"\n📄 {file_name}")
            print(f"   심각도   : {r.get('severity','?')}")
            print(f"   오류 유형: {r.get('error_type','?')}")
            print(f"   요약     : {r.get('error_summary','')[:120]}...")

        parser.save_parsed_results(results, "output/step1_parsed_errors.json")

    except FileNotFoundError as e:
        print(f"\n⚠  {e}")
        print("💡 'email' 폴더를 생성하고 분석할 파일을 넣어주세요.")
    except Exception as e:
        import traceback
        print(f"\n❌ 오류: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
