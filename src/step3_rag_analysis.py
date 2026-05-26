"""
[3단계 - RAG 버전] RAG 검색 결과를 AI로 분석

RAG로 찾은 유사 코드들을 AI가 분석하여 원인과 해결책을 제시
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass


class RAGAnalysisReportGenerator:
    """RAG 결과 기반 AI 분석 리포트 생성"""
    
    # AI 시스템 프롬프트
    SYSTEM_PROMPT = """당신은 Java 에러 분석 전문가입니다.

사용자가 에러 정보와 관련 코드를 제공하면:
1. 에러의 근본 원인을 정확하고 상세하게 분석하세요
2. 실용적인 해결 방법을 우선순위 순으로 제시하세요
3. 유사한 패턴의 에러 예방 방법을 제안하세요
4. 영향 범위와 심각도를 평가하세요

⚠️ 절대 금지 사항:
- 실제 소스파일을 직접 수정하는 코드 제공 금지
- 파일 경로를 포함한 자동 수정 스크립트 제공 금지
- "이 파일을 이렇게 바꾸세요"라는 직접 수정 지시 금지

✅ 허용 사항:
- 문제 해결을 위한 참고용 코드 예시 (개발자가 수동 적용)
- 설계 개선 방향 제안
- 원인 설명 및 해결 전략 제시

반드시 한국어로 답변하세요.
"""
    
    def __init__(
        self,
        llm_type: str = "groq",
        model_name: str = "compound-beta",
        api_key: Optional[str] = None,
        use_mock: bool = False
    ):
        """
        Args:
            llm_type: LLM 타입 (groq, ollama, openai, mock)
            model_name: 모델 이름
            api_key: API 키 (Groq/OpenAI 사용 시)
            use_mock: Mock 모드 사용 여부
        """
        self.llm_type = llm_type
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.use_mock = use_mock
        
        if use_mock:
            print("🎭 Mock 모드: 데모용 분석 생성 (실제 LLM 호출 없음)\n")
        else:
            print(f"🤖 LLM: {llm_type} ({model_name})\n")
    
    def build_rag_prompt(self, error_info: Dict, search_results: List[Dict]) -> str:
        """
        1단계 AI 분석 결과 + RAG 검색 결과를 LLM 프롬프트로 변환
        """
        prompt = "## 🔍 에러 분석 요청\n\n"

        # ── 1단계 AI 분석 결과 (핵심 컨텍스트) ──────────────────────────
        error_summary = error_info.get('error_summary', '')[:1500]   # 413 방지: 최대 1500자
        root_cause    = error_info.get('root_cause', '')[:800]        # 413 방지: 최대 800자
        severity      = error_info.get('severity', 'MEDIUM')

        if error_summary:
            prompt += f"### 📝 오류 요약 (AI 1단계 분석)\n\n{error_summary}\n\n"

        if root_cause:
            prompt += f"### 🎯 추정 근본 원인\n\n{root_cause}\n\n"

        prompt += f"**심각도**: `{severity}`\n\n"

        # ── 에러 타입별 세부 정보 ────────────────────────────────────────
        error_type = error_info.get('error_type')

        if error_type == 'ai_query':
            prompt += f"**검색 키워드**: `{error_info.get('search_query', '')}`\n\n"

        elif error_type == 'exception':
            prompt += f"**Exception 타입**: `{error_info.get('exception_type', 'N/A')}`\n"
            prompt += f"**메시지**: {error_info.get('exception_message', 'N/A')}\n\n"

        elif error_type == 'stack_trace':
            prompt += f"**클래스**: `{error_info.get('class_name', 'N/A')}`\n"
            prompt += f"**메서드**: `{error_info.get('method', 'N/A')}()`\n"
            if error_info.get('line'):
                prompt += f"**라인**: {error_info['line']}\n"
            prompt += "\n"

        elif error_type == 'general':
            prompt += f"**검색 쿼리**: `{error_info.get('search_query', '')[:200]}`\n\n"

        # ── RAG 검색으로 찾은 관련 소스코드 ─────────────────────────────
        if search_results:
            prompt += "### 🔎 관련 소스코드 (RAG 검색 결과)\n\n"
            for i, result in enumerate(search_results[:2], 1):   # 413 방지: 최대 2개
                sim   = result.get('similarity_score', 0)
                fname = result.get('file_name', 'Unknown')
                fpath = result.get('file_path', '')
                code  = result.get('code_snippet', '')
                prompt += f"#### {i}. {fname}  (유사도: {sim:.1%})\n"
                prompt += f"경로: `{fpath}`\n\n"
                prompt += "```java\n"
                prompt += code[:500] + ("..." if len(code) > 500 else "")  # 413 방지: 최대 500자
                prompt += "\n```\n\n"
        else:
            prompt += "### ⚠️ RAG 검색 결과 없음\n"
            prompt += "소스코드가 인덱싱되지 않았거나 관련 코드를 찾지 못했습니다.\n\n"

        # ── 분석 요청 ────────────────────────────────────────────────────
        prompt += """### 📊 분석 요청

위 정보를 바탕으로 아래 항목을 **한국어**로 분석해 주세요:

1. **원인 분석**: 에러가 발생한 정확한 원인과 메커니즘
2. **영향 범위**: 이 에러가 시스템에 미치는 영향
3. **해결 방법**: 구체적인 해결 방법 (우선순위 순)
4. **참고 코드**: 개발자가 참고할 수 있는 수정 예시 (직접 수정하지 말 것)
5. **예방 방법**: 향후 유사 에러 방지 방법

주의: 실제 소스 파일의 직접 수정 지시는 제공하지 마세요. 개발자가 검토 후 수동 적용합니다.
"""
        # ── 최종 안전장치: 전체 프롬프트 6000자 이내로 제한 (413 방지) ──
        MAX_PROMPT = 6000
        if len(prompt) > MAX_PROMPT:
            prompt = prompt[:MAX_PROMPT] + "\n\n...(내용 축약됨 - 토큰 한도 초과 방지)\n\n### 📊 분석 요청\n위 정보를 바탕으로 원인 분석, 해결 방법, 예방 방법을 한국어로 답해주세요."
        return prompt
    
    def call_llm(self, prompt: str) -> str:
        """
        LLM 호출 (Ollama, Groq, OpenAI, Mock)
        """
        if self.use_mock:
            return self.call_mock_llm(prompt)
        elif self.llm_type == "groq":
            return self.call_groq_api(prompt)
        elif self.llm_type == "ollama":
            return self.call_ollama_api(prompt)
        elif self.llm_type == "openai":
            return self.call_openai_api(prompt)
        else:
            raise ValueError(f"지원하지 않는 LLM 타입: {self.llm_type}")
    
    def call_groq_api(self, prompt: str) -> str:
        """Groq API 호출 (compound-beta, 429 자동 재시도)"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4096
        }
        retry_waits = [5, 15, 30]
        for attempt, wait in enumerate(retry_waits + [None], start=1):
            try:
                prompt_len = len(payload["messages"][1]["content"])
                print(f"      ⏳ Groq API 호출 중... (프롬프트 {prompt_len:,}자)", flush=True)
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                result = response.json()["choices"][0]["message"]["content"]
                tokens = response.json().get("usage", {}).get("completion_tokens", "?")
                print(f"      ✅ 완료 (총 {tokens} tokens)")
                return result
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and wait is not None:
                    print(f"      ⚠ Rate limit (429), {wait}초 대기 후 재시도 ({attempt}/{len(retry_waits)})...", flush=True)
                    time.sleep(wait)
                    continue
                if e.response.status_code == 413 and wait is not None:
                    # 페이로드 초과 → 프롬프트 절반으로 줄이고 재시도
                    cur = payload["messages"][1]["content"]
                    payload["messages"][1]["content"] = cur[:len(cur)//2] + "\n...(내용 축약됨)"
                    print(f"      ⚠ Payload Too Large (413), 프롬프트 축약 후 재시도 ({attempt}/{len(retry_waits)})...", flush=True)
                    time.sleep(2)
                    continue
                if e.response.status_code == 401:
                    return "❌ Groq API 키가 유효하지 않습니다."
                return f"❌ Groq API HTTP 오류: {e}"
            except requests.exceptions.ConnectionError:
                return "❌ Groq API에 연결할 수 없습니다. 인터넷 연결을 확인하세요."
            except Exception as e:
                return f"❌ Groq API 오류: {e}"
        return "❌ Groq Rate Limit 시도 실패 - 잠시 후 다시 시도하세요."

    def call_ollama_api(self, prompt: str) -> str:
        """Ollama API 호출 (스트리밍 모드 - 타임아웃 방지)"""
        url = "http://localhost:11434/api/generate"

        payload = {
            "model": self.model_name,
            "prompt": f"{self.SYSTEM_PROMPT}\n\n{prompt}",
            "stream": True,       # 스트리밍: 첫 토큰부터 즉시 수신 → read timeout 없음
            "num_predict": 400    # CPU 환경 성능: 응답 최대 400토큰 (약 3분 이내)
        }

        try:
            # connect timeout=10s, read timeout=없음(스트리밍이므로 청크 단위 수신)
            response = requests.post(url, json=payload, stream=True, timeout=(10, None))
            response.raise_for_status()

            full_text = []
            token_count = 0
            for line in response.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                token = chunk.get("response", "")
                if token:
                    full_text.append(token)
                    token_count += 1
                    # 50토큰마다 진척도 출력
                    if token_count % 50 == 0:
                        print(f"      ✍️  생성 중... ({token_count} tokens)", flush=True)
                if chunk.get("done"):
                    break

            result = "".join(full_text)
            print(f"      ✅ 완료 (총 {token_count} tokens)")
            return result

        except requests.exceptions.ConnectionError:
            return "❌ Ollama 서버에 연결할 수 없습니다. `ollama serve` 실행 확인 필요."
        except Exception as e:
            return f"❌ Ollama API 오류: {e}"
    
    def call_openai_api(self, prompt: str) -> str:
        """OpenAI API 호출"""
        if not self.api_key:
            return "❌ OpenAI API 키가 설정되지 않았습니다."
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"❌ OpenAI API 오류: {e}"
    
    def call_mock_llm(self, prompt: str) -> str:
        """Mock LLM (데모용)"""
        return """## 1. 원인 분석

RAG 검색 결과를 기반으로 분석한 결과, 해당 에러는 다음과 같은 원인으로 발생했습니다:

- **주요 원인**: Null 체크 누락 또는 예외 처리 부재
- **발생 위치**: 검색된 코드 조각들에서 공통적으로 발견되는 패턴
- **트리거 조건**: 특정 입력값이나 상태에서 발생

## 2. 영향 범위

- **직접 영향**: 해당 기능 사용 불가
- **간접 영향**: 연관된 트랜잭션 롤백 가능성
- **사용자 영향**: 에러 메시지 노출, 서비스 중단

## 3. 수정 방법

### 우선순위 1: 즉시 수정

```java
// 수정 전
if (data != null && data.getValue() != null) {
    process(data.getValue());
}

// 수정 후
if (data != null && data.getValue() != null) {
    process(data.getValue());
} else {
    log.warn("데이터가 null입니다: {}", data);
    // 기본값 처리 또는 예외 발생
}
```

### 우선순위 2: 구조 개선

- Optional 활용
- 방어적 프로그래밍
- 예외 처리 추가

## 4. 코드 예시

```java
// 개선된 코드
public void processData(Data data) {
    Objects.requireNonNull(data, "Data must not be null");
    
    Optional.ofNullable(data.getValue())
        .ifPresentOrElse(
            value -> process(value),
            () -> log.warn("Value is null, using default")
        );
}
```

## 5. 예방 방법

- **코드 리뷰**: Null 체크 필수 확인
- **정적 분석**: SpotBugs, SonarQube 활용
- **단위 테스트**: Null 케이스 테스트 추가
- **문서화**: Nullable 파라미터 명시

---

**⚠️ 참고**: 이 분석은 RAG로 검색된 유사 코드를 기반으로 생성되었습니다.
실제 적용 시 프로젝트 상황에 맞게 조정하세요.
"""
    
    def generate_query_section(
        self,
        query_num: int,
        total_queries: int,
        error_info: Dict,
        search_results: List[Dict],
        analysis: str
    ) -> str:
        """단일 쿼리 분석 결과를 마크다운 섹션으로 생성 (통합 리포트의 일부)"""

        search_query = error_info.get('search_query', 'N/A')
        error_type   = error_info.get('error_type', 'general')

        section = f"## 🔍 분석 {query_num}/{total_queries}: `{search_query}`\n\n"

        # 오류 상세 정보
        section += "### 📧 오류 정보\n\n"
        if error_type == 'exception':
            section += f"- **Exception**: `{error_info.get('exception_type', 'N/A')}`\n"
            section += f"- **메시지**: {error_info.get('exception_message', 'N/A')}\n"
        elif error_type == 'stack_trace':
            section += f"- **클래스**: `{error_info.get('class_name', 'N/A')}`\n"
            section += f"- **메서드**: `{error_info.get('method', 'N/A')}()`\n"
            if error_info.get('line'):
                section += f"- **라인**: {error_info['line']}\n"
        else:
            if error_info.get('error_summary'):
                section += f"- **오류 요약**: {error_info['error_summary'][:300]}\n"
            if error_info.get('root_cause'):
                section += f"- **추정 원인**: {error_info['root_cause'][:200]}\n"
        section += f"- **심각도**: `{error_info.get('severity', 'MEDIUM')}`\n\n"

        # RAG 검색 결과
        if search_results:
            section += "### 🔎 관련 소스코드 (RAG 검색 결과)\n\n"
            for i, result in enumerate(search_results[:3], 1):
                section += f"**{i}. {result['file_name']}** (유사도: {result['similarity_score']:.2%})\n"
                section += f"경로: `{result['file_path']}`\n\n"
                section += "```java\n"
                section += result['code_snippet'][:400] + ("..." if len(result['code_snippet']) > 400 else "")
                section += "\n```\n\n"
        else:
            section += "### 🔎 RAG 검색 결과\n\n> ⚠️ 관련 소스코드를 찾지 못했습니다.\n\n"

        # AI 분석 결과
        section += "### 🤖 AI 분석\n\n"
        section += analysis
        section += "\n\n"

        return section

    def generate_combined_report(
        self,
        email_file: str,
        data_overview: Dict,
        query_sections: List[str]
    ) -> str:
        """여러 쿼리 분석 결과를 하나의 통합 리포트로 생성 (이메일 1개 → 파일 1개)"""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total     = len(query_sections)

        report  = f"# 🤖 AI 에러 분석 리포트\n\n"
        report += f"| 항목 | 내용 |\n|---|---|\n"
        report += f"| 📧 원본 파일 | `{email_file}` |\n"
        report += f"| 🕐 생성 시간 | {timestamp} |\n"
        report += f"| 🤖 LLM | {self.llm_type} / {self.model_name} |\n"
        report += f"| 🔍 분석 쿼리 수 | {total}개 |\n"
        report += f"| ⚠️ 심각도 | `{data_overview.get('severity', 'MEDIUM')}` |\n\n"

        if data_overview.get('error_summary'):
            report += f"> **오류 요약**: {data_overview['error_summary'][:400]}\n\n"

        report += "---\n\n"

        # 목차
        if total > 1:
            report += "## 📋 목차\n\n"
            for i in range(1, total + 1):
                report += f"{i}. [분석 {i}/{total}](#분석-{i})\n"
            report += "\n---\n\n"

        # 각 쿼리 분석 섹션
        for section in query_sections:
            report += section
            report += "---\n\n"

        # 안전성 공지
        report += "## ⚠️ 안전성 공지\n\n"
        report += "- ✅ AI는 소스코드 파일을 **절대 수정하지 않습니다**\n"
        report += "- ✅ 이 리포트는 **참고 자료**입니다\n"
        report += "- ✅ 개발자가 검토 후 수동으로 적용하세요\n"
        report += "- ✅ RAG 검색 결과는 유사도 기반이므로 정확하지 않을 수 있습니다\n"

        return report

    def process_all_errors(
        self,
        contexts_json_path: str = "output/step2_rag_contexts.json",
        step1_json_path: str = "output/step1_parsed_errors.json",
        reports_dir: str = "reports"
    ) -> int:
        """모든 에러 처리 및 리포트 생성.

        contexts_json_path 파일이 없으면 step1 결과만으로 분석합니다 (2단계 스킵 지원).
        """
        print("=" * 60)
        print("[3단계 - RAG] AI 분석 리포트 생성")
        print("=" * 60)

        # ── 2단계 결과 로드 (없으면 1단계 결과로 대체) ─────────────────
        step2_exists = Path(contexts_json_path).exists()
        if step2_exists:
            with open(contexts_json_path, 'r', encoding='utf-8') as f:
                rag_data = json.load(f)
            print(f"📂 2단계 RAG 결과 로드: {contexts_json_path}")

            # step2에 없는 이메일이 step1에 있으면 폴백으로 추가
            if Path(step1_json_path).exists():
                with open(step1_json_path, 'r', encoding='utf-8') as f:
                    step1_data = json.load(f)
                missing = [k for k in step1_data if k not in rag_data]
                if missing:
                    print(f"⚠️  step2에 없는 이메일 {len(missing)}개 → step1 폴백으로 추가")
                    for email_file in missing:
                        d = step1_data[email_file]
                        rag_data[email_file] = {
                            'email_file':    email_file,
                            'has_error':     d.get('has_error', False),
                            'error_summary': d.get('error_summary', ''),
                            'severity':      d.get('severity', 'MEDIUM'),
                            'root_cause':    d.get('root_cause', ''),
                            'search_count':  1,
                            'searches': [{
                                'error_type':    'general',
                                'search_query':  d.get('error_summary', '')[:200],
                                'error_summary': d.get('error_summary', ''),
                                'root_cause':    d.get('root_cause', ''),
                                'severity':      d.get('severity', 'MEDIUM'),
                                'found_codes':   []
                            }]
                        }
        else:
            print(f"⚠️  2단계 결과 없음 → 1단계 결과로 분석: {step1_json_path}")
            if not Path(step1_json_path).exists():
                print(f"❌ 1단계 결과도 없습니다: {step1_json_path}")
                return 0
            with open(step1_json_path, 'r', encoding='utf-8') as f:
                step1_data = json.load(f)
            # 1단계 데이터를 step2 형식으로 변환
            rag_data = {}
            for email_file, d in step1_data.items():
                rag_data[email_file] = {
                    'email_file':    email_file,
                    'has_error':     d.get('has_error', False),
                    'error_summary': d.get('error_summary', ''),
                    'severity':      d.get('severity', 'MEDIUM'),
                    'root_cause':    d.get('root_cause', ''),
                    'search_count':  1,
                    'searches': [{
                        'error_type':    'general',
                        'search_query':  d.get('error_summary', '')[:200],
                        'error_summary': d.get('error_summary', ''),
                        'root_cause':    d.get('root_cause', ''),
                        'severity':      d.get('severity', 'MEDIUM'),
                        'found_codes':   []   # RAG 없음
                    }]
                }

        os.makedirs(reports_dir, exist_ok=True)
        report_count = 0

        # 처리할 총 쿼리 수 계산 (진척도용)
        total_items = sum(
            len(d.get('searches', [])) for d in rag_data.values()
            if d.get('has_error', True)
        )
        current_item = 0

        for email_file, data in rag_data.items():
            # has_error=False 항목은 건너뜀 (오류 없는 이메일 분석 불필요)
            if not data.get('has_error', True):
                print(f"\n⏭️  건너뜀 (오류 없음): {email_file}")
                continue

            searches = data.get('searches', [])
            print(f"\n📧 처리 중: {email_file}  (쿼리 {len(searches)}개)")

            query_sections = []   # 이메일 내 각 쿼리의 분석 섹션을 수집

            for idx, search in enumerate(searches, 1):
                current_item += 1
                error_type     = search.get('error_type', 'general')
                search_results = search.get('found_codes', [])
                if not isinstance(search_results, list):
                    search_results = []

                if not search_results:
                    print(f"   ℹ️  RAG 검색 결과 없음 - 오류 요약만으로 분석")

                # 식별자 (로그 표시용)
                if error_type == 'exception':
                    identifier = search.get('exception_type', 'Exception').replace('.', '_')
                elif error_type == 'stack_trace':
                    identifier = search.get('class_name', 'StackTrace')
                elif error_type == 'ai_query':
                    q = search.get('search_query', 'query')[:30].replace(' ', '_')
                    identifier = f"Query_{q}"
                else:
                    identifier = "General_Error"

                print(f"\n   [{current_item}/{total_items}] 🎯 {identifier} 분석 중...")

                # 프롬프트 생성 및 LLM 호출
                prompt   = self.build_rag_prompt(search, search_results)
                analysis = self.call_llm(prompt)

                # 쿼리별 섹션 생성 (파일 저장 없이 메모리에 수집)
                section = self.generate_query_section(
                    idx, len(searches), search, search_results, analysis
                )
                query_sections.append(section)

            # ── 이메일 1개 → 통합 리포트 파일 1개 저장 ─────────────────
            combined_report = self.generate_combined_report(email_file, data, query_sections)

            ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_file = Path(email_file).stem[:40].replace('/', '_').replace('\\', '_')
            report_filename = f"{ts}_분석리포트_{safe_file}.md"
            report_path = Path(reports_dir) / report_filename

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(combined_report)

            print(f"\n   ✅ 통합 리포트 저장: {report_filename}  ({len(searches)}개 분석 포함)")
            report_count += 1

        print("\n" + "=" * 60)
        print(f"✅ 총 {report_count}개 리포트 생성 완료!")
        print(f"📁 저장 위치: {Path(reports_dir).absolute()}")
        print("=" * 60 + "\n")
        return report_count


def main():
    """메인 실행 함수"""
    
    generator = RAGAnalysisReportGenerator(
        llm_type="mock",
        model_name="qwen2.5:7b",
        use_mock=True
    )
    
    generator.process_all_errors(
        contexts_json_path="output/step2_rag_contexts.json",
        reports_dir="reports"
    )


if __name__ == "__main__":
    main()
