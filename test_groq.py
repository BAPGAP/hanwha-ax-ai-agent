"""Groq API 직접 테스트 스크립트"""
import requests
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass

api_key = os.environ.get("GROQ_API_KEY", "")
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": "Bearer " + api_key,
    "Content-Type": "application/json"
}
payload = {
    "model": "compound-beta",
    "messages": [
        {"role": "system", "content": "당신은 Java 에러 분석 전문가입니다. 한국어로 답변하세요."},
        {"role": "user", "content": "Java NullPointerException의 가장 흔한 원인을 한 문장으로 설명해줘."}
    ],
    "temperature": 0.1,
    "max_tokens": 200
}

print("=" * 60)
print("  Groq API 직접 호출 테스트")
print("=" * 60)
print(f"모델: compound-beta")
print(f"API Key: {api_key[:20]}...")
print("호출 중...")

try:
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"HTTP 상태: {resp.status_code}")
    
    data = resp.json()
    if resp.status_code == 200:
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        print(f"\n✅ 성공!")
        print(f"응답: {content}")
        print(f"\n토큰 사용량:")
        print(f"  - 입력: {usage.get('prompt_tokens', '?')}")
        print(f"  - 출력: {usage.get('completion_tokens', '?')}")
        print(f"  - 합계: {usage.get('total_tokens', '?')}")
    else:
        print(f"\n❌ 오류 응답:")
        print(data)
        sys.exit(1)

except requests.exceptions.ConnectionError as e:
    print(f"\n❌ 연결 오류: {e}")
    sys.exit(1)
except requests.exceptions.Timeout:
    print(f"\n❌ 타임아웃 (30초)")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 예외: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("  step1 + step3 통합 테스트")
print("=" * 60)

sys.path.insert(0, str(Path(__file__).parent / "src"))

# step1 테스트
from step1_email_parser import LLMEmailAnalyzer
print("\n[step1] LLMEmailAnalyzer 초기화...")
analyzer = LLMEmailAnalyzer()  # 기본값: groq, compound-beta
print(f"  llm_type: {analyzer.llm_type}")
print(f"  model_name: {analyzer.model_name}")
print(f"  api_key: {analyzer.api_key[:20]}...")

sample = """
Subject: NullPointerException 발생
CustomerService.java:145 - validateCustomerData에서 NullPointerException 발생
java.lang.NullPointerException: Cannot read field "name" because "customer" is null
"""
print("\n[step1] 이메일 분석 중...")
result = analyzer.analyze(sample, "test_email.txt")
print(f"  ✅ 결과: {result.get('error_type')} / {result.get('severity')}")
print(f"     요약: {result.get('error_summary', '')[:80]}")

# step3 테스트  
from step3_rag_analysis import RAGAnalysisReportGenerator
print("\n[step3] RAGAnalysisReportGenerator 초기화...")
gen = RAGAnalysisReportGenerator()  # 기본값: groq, compound-beta
print(f"  llm_type: {gen.llm_type}")
print(f"  model_name: {gen.model_name}")
print(f"  api_key: {gen.api_key[:20]}...")

print("\n[step3] LLM 분석 중...")
prompt = "CustomerService.java:145에서 NullPointerException 발생. customer 객체가 null. 원인과 해결책을 간략히 설명해줘."
analysis = gen.call_llm(prompt)
print(f"  ✅ 결과: {analysis[:200]}")

print("\n✅ 모든 테스트 통과! Groq API 정상 동작 확인됨.")
