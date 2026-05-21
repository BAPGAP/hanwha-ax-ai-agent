"""
[3단계 - RAG 버전] RAG 검색 결과를 AI로 분석

RAG로 찾은 유사 코드들을 AI가 분석하여 원인과 해결책을 제시
"""

import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class RAGAnalysisReportGenerator:
    """RAG 결과 기반 AI 분석 리포트 생성"""
    
    # AI 시스템 프롬프트
    SYSTEM_PROMPT = """당신은 Java 에러 분석 전문가입니다.

사용자가 에러 메시지와 관련 코드를 제공하면:
1. 에러의 원인을 정확히 분석
2. 실용적인 해결 방법 제시
3. 수정된 코드 예시 제공

⚠️ 중요: 기존 소스 파일을 절대 직접 수정하지 마세요!
오직 분석 결과와 제안만 제공하세요.
"""
    
    def __init__(
        self,
        llm_type: str = "ollama",
        model_name: str = "qwen2.5:7b",
        api_key: Optional[str] = None,
        use_mock: bool = False
    ):
        """
        Args:
            llm_type: LLM 타입 (ollama, openai, mock)
            model_name: 모델 이름
            api_key: API 키 (OpenAI 사용 시)
            use_mock: Mock 모드 사용 여부
        """
        self.llm_type = llm_type
        self.model_name = model_name
        self.api_key = api_key
        self.use_mock = use_mock
        
        if use_mock:
            print("🎭 Mock 모드: 데모용 분석 생성 (실제 LLM 호출 없음)\n")
        else:
            print(f"🤖 LLM: {llm_type} ({model_name})\n")
    
    def build_rag_prompt(self, error_info: Dict, search_results: List[Dict]) -> str:
        """
        RAG 검색 결과를 프롬프트로 변환
        
        Args:
            error_info: 에러 정보
            search_results: RAG 검색 결과
            
        Returns:
            LLM용 프롬프트
        """
        prompt = "## 🔍 에러 정보\n\n"
        
        error_type = error_info.get('error_type')
        
        if error_type == 'exception':
            prompt += f"**Exception 타입**: {error_info['exception_type']}\n"
            prompt += f"**메시지**: {error_info.get('exception_message', 'N/A')}\n\n"
        
        elif error_type == 'stack_trace':
            prompt += f"**클래스**: {error_info['class_name']}\n"
            prompt += f"**메서드**: {error_info['method']}()\n"
            if error_info.get('line'):
                prompt += f"**라인**: {error_info['line']}\n"
            prompt += "\n"
        
        elif error_type == 'general':
            prompt += f"**일반 에러**: 검색 키워드로 관련 코드를 찾았습니다.\n\n"
        
        prompt += f"## 📝 검색 쿼리\n\n```\n{error_info['search_query']}\n```\n\n"
        
        prompt += "## 🔎 유사한 코드 (RAG 검색 결과)\n\n"
        
        for i, result in enumerate(search_results[:3], 1):  # 상위 3개만
            prompt += f"### {i}. {result['file_name']} (유사도: {result['similarity_score']:.2%})\n\n"
            prompt += f"**파일 경로**: `{result['file_path']}`\n\n"
            prompt += "```java\n"
            prompt += result['code_snippet']
            prompt += "\n```\n\n"
        
        prompt += """## 📊 분석 요청

위 정보를 바탕으로:

1. **원인 분석**: 에러가 발생한 원인을 상세히 설명
2. **영향 범위**: 이 에러가 시스템에 미치는 영향
3. **수정 방법**: 구체적인 해결 방법 (우선순위 순)
4. **코드 예시**: 수정된 코드 예시
5. **예방 방법**: 향후 유사 에러 방지 방법

⚠️ 주의: 실제 파일 수정 코드를 제공하지 말고, 개발자가 참고할 수 있는 예시만 제공하세요.
"""
        
        return prompt
    
    def call_llm(self, prompt: str) -> str:
        """
        LLM 호출 (Ollama, OpenAI, Mock)
        """
        if self.use_mock:
            return self.call_mock_llm(prompt)
        elif self.llm_type == "ollama":
            return self.call_ollama_api(prompt)
        elif self.llm_type == "openai":
            return self.call_openai_api(prompt)
        else:
            raise ValueError(f"지원하지 않는 LLM 타입: {self.llm_type}")
    
    def call_ollama_api(self, prompt: str) -> str:
        """Ollama API 호출"""
        url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": f"{self.SYSTEM_PROMPT}\n\n{prompt}",
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()['response']
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
    
    def generate_report_markdown(
        self,
        email_file: str,
        error_info: Dict,
        search_results: List[Dict],
        analysis: str
    ) -> str:
        """마크다운 리포트 생성"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# 🤖 AI 에러 분석 리포트 (RAG 기반)

**생성 시간**: {timestamp}  
**원본 이메일**: {email_file}  
**LLM**: {self.llm_type} ({self.model_name})  
**검색 방법**: RAG (Retrieval-Augmented Generation)

---

## 📧 에러 정보

"""
        
        error_type = error_info.get('error_type')
        
        if error_type == 'exception':
            report += f"- **Exception 타입**: `{error_info['exception_type']}`\n"
            report += f"- **메시지**: {error_info.get('exception_message', 'N/A')}\n"
        elif error_type == 'stack_trace':
            report += f"- **클래스**: `{error_info['class_name']}`\n"
            report += f"- **메서드**: `{error_info['method']}()`\n"
            if error_info.get('line'):
                report += f"- **라인**: {error_info['line']}\n"
        elif error_type == 'general':
            report += "- **타입**: 일반 에러 (Stack Trace 없음)\n"
            report += f"- **검색 쿼리**: `{error_info['search_query'][:100]}...`\n"
        
        report += "\n---\n\n"
        report += "## 🔎 RAG 검색 결과\n\n"
        report += f"**검색 쿼리**: `{error_info['search_query']}`\n\n"
        
        for i, result in enumerate(search_results[:3], 1):
            report += f"### {i}. {result['file_name']} (유사도: {result['similarity_score']:.2%})\n\n"
            report += f"- **경로**: `{result['file_path']}`\n"
            report += f"- **청크 ID**: {result['chunk_id']}\n\n"
            report += "```java\n"
            report += result['code_snippet'][:500] + ("..." if len(result['code_snippet']) > 500 else "")
            report += "\n```\n\n"
        
        report += "---\n\n"
        report += "## 🤖 AI 분석\n\n"
        report += analysis
        report += "\n\n---\n\n"
        report += "## ⚠️ 안전성 공지\n\n"
        report += "- ✅ AI는 소스코드 파일을 **절대 수정하지 않습니다**\n"
        report += "- ✅ 이 리포트는 **참고 자료**입니다\n"
        report += "- ✅ 개발자가 검토 후 수동으로 적용하세요\n"
        report += "- ✅ RAG 검색 결과는 유사도 기반이므로 정확하지 않을 수 있습니다\n"
        
        return report
    
    def process_all_errors(
        self,
        contexts_json_path: str = "output/step2_rag_contexts.json",
        reports_dir: str = "reports"
    ) -> int:
        """모든 에러 처리 및 리포트 생성"""
        
        print("=" * 60)
        print("[3단계 - RAG] AI 분석 리포트 생성")
        print("=" * 60)
        
        # 2단계 결과 로드
        with open(contexts_json_path, 'r', encoding='utf-8') as f:
            rag_data = json.load(f)
        
        # 리포트 디렉토리 생성
        os.makedirs(reports_dir, exist_ok=True)
        
        report_count = 0
        
        for email_file, data in rag_data.items():
            print(f"\n📧 처리 중: {email_file}")
            
            for search in data['searches']:
                error_type = search['error_type']
                search_results = search['found_codes']
                
                if not search_results:
                    print(f"   ⚠️ 검색 결과 없음: {search['search_query']}")
                    continue
                
                # 식별자 생성
                if error_type == 'exception':
                    identifier = search['exception_type'].replace('.', '_')
                elif error_type == 'stack_trace':
                    identifier = search['class_name']
                else:
                    identifier = "General_Error"
                
                print(f"   🎯 {identifier} 분석 중...")
                
                # 프롬프트 생성
                prompt = self.build_rag_prompt(search, search_results)
                
                # LLM 호출
                analysis = self.call_llm(prompt)
                
                # 리포트 생성
                report = self.generate_report_markdown(
                    email_file,
                    search,
                    search_results,
                    analysis
                )
                
                # 파일명 생성
                report_filename = f"RAG_분석_리포트_{identifier}_{report_count + 1}.md"
                report_path = Path(reports_dir) / report_filename
                
                # 저장
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                print(f"   ✓ 리포트 저장: {report_filename}")
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
