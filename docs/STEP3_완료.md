# 🎉 [3단계] 원인 분석 및 수정 제안 리포트 생성 - 완료!

## ✅ 구현 완료 항목

### 1. 핵심 기능
- ✅ 1, 2단계 JSON 데이터 통합 (에러 로그 + 소스코드)
- ✅ **OpenAI API / Ollama API 호환** 프롬프트 빌드
- ✅ **엄격한 시스템 프롬프트** - 파일 수정 금지 명시
- ✅ **Mock 모드** - Ollama 없이도 테스트 가능
- ✅ Ollama (Qwen2.5-7B) 지원
- ✅ OpenAI API 지원
- ✅ 클래스별 **마크다운 리포트** 자동 생성 (`오류_분석_리포트_[클래스명].md`)
- ✅ **절대 금지**: AI가 소스코드 파일 직접 수정 불가
- ✅ 에러 원인 분석, 수정 방법, 코드 예시, 권장 사항 포함

### 2. 제공되는 파일

#### 📂 소스코드
- `src/step3_analysis_report.py` - 리포트 생성기 (450줄)
  - `AnalysisReportGenerator` 클래스
  - Ollama / OpenAI / Mock 모드 지원
  - 프롬프트 빌드 및 LLM 호출
  - 마크다운 리포트 생성

#### 📂 문서
- `docs/LLM_설정_가이드.md` - Ollama 설치 및 설정 가이드

#### 📂 출력 결과
- `reports/오류_분석_리포트_CustomerService.md`
- `reports/오류_분석_리포트_OrderController.md`

## 🚀 사용 방법

### 기본 실행 (Mock 모드 - Ollama 불필요)
```bash
# 프로젝트 루트 디렉토리에서
python src/step3_analysis_report.py
```

### Ollama 사용 (실제 AI 분석)
```python
# step3_analysis_report.py 수정
generator = AnalysisReportGenerator(
    use_mock=False,  # Mock 비활성화
    llm_type="ollama",
    model_name="qwen2.5:7b",
    api_base_url="http://localhost:11434"
)
```

**사전 준비**:
1. Ollama 설치: https://ollama.com/download
2. 모델 다운로드: `ollama pull qwen2.5:7b`
3. 서버 실행: `ollama serve`

### OpenAI API 사용
```python
generator = AnalysisReportGenerator(
    llm_type="openai",
    model_name="gpt-4",
    api_key="your-api-key-here"
)
```

## 📊 생성되는 리포트 구조

```markdown
# 🐛 에러 분석 리포트: CustomerService

**생성 일시**: 2026-05-21 22:24:35
**분석 모델**: qwen2.5:7b
**출처**: sample_error.txt

---

## 📋 발생한 Exception
- **java.lang.NullPointerException**
  - Cannot invoke "String.length()" because "customerName" is null

## 📍 에러 발생 위치
- **파일**: `CustomerService.java`
- **클래스**: `CustomerService`
- **메서드**: `validateCustomerData()`
- **라인**: 145

---

## 🔍 AI 분석 결과

## 1. 에러 원인 분석
[근본 원인 설명...]

## 2. 문제가 되는 코드
[문제 코드 지적...]

## 3. 수정 방법
[안전한 수정 방법 제시...]

## 4. 수정된 코드 예시
```java
// 수정된 코드
```

## 5. 추가 권장 사항
[유사 에러 방지 팁...]

---

## ⚠️ 중요 공지
이 리포트는 AI가 생성한 분석 결과입니다.
AI가 기존 소스코드 파일을 직접 수정하지 않았습니다.
```

## 🔍 실행 결과 예시

```
============================================================
[3단계] 원인 분석 및 수정 제안 리포트 생성
============================================================

🎭 Mock 모드: 데모용 분석 생성 (실제 LLM 호출 없음)

============================================================
📧 처리 중: sample_error.txt
============================================================

🎯 클래스: CustomerService
🎭 Mock 분석 생성 중... (데모용)
   ✓ 분석 완료 (3354 문자)
   ✓ 리포트 저장: reports\오류_분석_리포트_CustomerService.md

============================================================
✅ 총 2개 리포트 생성 완료!
📁 저장 위치: C:\...\ai-agent\reports
============================================================
```

## 🎨 주요 특징

### 1. 엄격한 안전 장치
**시스템 프롬프트에 명시**:
```
⚠️ 절대 금지 사항:
- 기존 Java 소스코드 파일을 직접 수정하거나 덮어쓰는 행위는 절대 금지됩니다.
- 파일 시스템에 직접 접근하거나 파일을 생성/수정하지 마십시오.
- 오직 분석 결과와 권장 사항을 텍스트로 제공하는 것만 허용됩니다.
```

**코드 레벨 보호**:
- AI는 마크다운 텍스트만 반환
- 파일 쓰기 권한은 리포트 디렉토리에만 부여
- 소스코드 디렉토리에는 접근 불가

### 2. 다양한 LLM 지원
- **Mock 모드**: Ollama 없이 데모 분석 생성
- **Ollama**: 로컬 실행, 무료, 데이터 보안
- **OpenAI**: 빠른 응답, 고품질 분석

### 3. 지능적인 프롬프트 구성
- Exception 정보 + 소스코드 컨텍스트 통합
- 에러 라인 하이라이팅 (>>>)
- 라인 번호와 함께 제공
- 구조화된 분석 요청

### 4. 실용적인 리포트
- 명확한 원인 분석
- 구체적인 수정 방법 (코드 예시 포함)
- 추가 권장 사항 (테스트, 로깅, 베스트 프랙티스)
- 개발자가 바로 적용 가능

### 5. 클래스별 리포트
- 각 클래스마다 독립적인 리포트 생성
- 파일명: `오류_분석_리포트_[클래스명].md`
- 팀원과 공유하기 쉬운 형태

## 💡 활용 예시

### Mock 모드로 빠른 테스트
```python
from step3_analysis_report import AnalysisReportGenerator

# Mock 모드 (Ollama 불필요)
generator = AnalysisReportGenerator(use_mock=True)
generator.process_all_errors(
    "output/step2_code_contexts.json",
    "reports"
)
```

### Ollama로 실제 분석
```python
# Ollama 실행 (터미널)
# ollama serve

# Python 코드
generator = AnalysisReportGenerator(
    use_mock=False,
    llm_type="ollama",
    model_name="qwen2.5:7b"
)
generator.process_all_errors(
    "output/step2_code_contexts.json",
    "reports"
)
```

### OpenAI API 사용
```python
import os

generator = AnalysisReportGenerator(
    llm_type="openai",
    model_name="gpt-4",
    api_key=os.getenv('OPENAI_API_KEY')
)
generator.process_all_errors(
    "output/step2_code_contexts.json",
    "reports"
)
```

### 커스텀 프롬프트
```python
# step3_analysis_report.py의 SYSTEM_PROMPT 수정
SYSTEM_PROMPT = """
당신은 Java 코드 에러 분석 전문가입니다.
[커스텀 지시사항...]
"""
```

## 🔒 보안 및 안전성

### 절대 금지 사항 (코드 레벨 보호)
```python
# ❌ 이런 코드는 절대 포함되지 않음
# with open("CustomerService.java", "w") as f:
#     f.write(fixed_code)  # 파일 수정 금지!

# ✅ 오직 리포트 생성만
with open("reports/오류_분석_리포트_CustomerService.md", "w") as f:
    f.write(report)  # 리포트 저장만 허용
```

### 시스템 프롬프트 강제
- AI에게 "절대 금지 사항" 명시
- 파일 수정 불가 지시
- 텍스트 분석만 허용

### 검토 프로세스
1. **AI 리포트 생성** (자동)
2. **개발자 검토** (필수)
3. **팀 리뷰** (권장)
4. **수동 코드 수정** (개발자가 직접)
5. **테스트 및 검증**
6. **배포**

## 📝 생성된 리포트 활용 방법

### 1. 개인 검토
```bash
# 리포트 확인
cd reports
code 오류_분석_리포트_CustomerService.md
```

### 2. 팀 공유
- Git에 커밋하여 팀원과 공유
- 이슈 트래커에 첨부
- 코드 리뷰 시 참고 자료

### 3. 수정 적용
- 리포트의 "수정된 코드 예시" 참고
- 프로젝트 컨벤션에 맞게 조정
- 단위 테스트 작성
- 통합 테스트 실행

### 4. 문서화
- 기술 부채 해결 기록
- 지식 베이스 구축
- 온보딩 자료

## 🛠️ 트러블슈팅

### Ollama 연결 실패
```
❌ Ollama 서버에 연결할 수 없습니다.
```
**해결**: `ollama serve` 실행

### 모델 없음
```
Error: model 'qwen2.5:7b' not found
```
**해결**: `ollama pull qwen2.5:7b`

### 메모리 부족
**해결**: 더 작은 모델 사용
```bash
ollama pull qwen2.5:3b
```

### Mock 모드 전환
```python
# Mock 모드로 빠른 테스트
generator = AnalysisReportGenerator(use_mock=True)
```

## 🔄 전체 워크플로우

```
[1단계] 이메일 파싱
    ↓
   JSON (에러 정보)
    ↓
[2단계] 소스코드 추출
    ↓
   JSON (에러 + 코드)
    ↓
[3단계] AI 분석 ← 🎯 현재 단계
    ↓
   마크다운 리포트
    ↓
[개발자 검토]
    ↓
[수동 수정]
    ↓
[테스트]
    ↓
[배포]
```

## 📊 LLM 모델 비교

| 모델 | 속도 | 품질 | 비용 | 데이터 보안 |
|------|------|------|------|------------|
| **Qwen2.5-7B (Ollama)** | 중간 | 우수 | 무료 | ✅ 로컬 |
| **CodeLlama (Ollama)** | 빠름 | 좋음 | 무료 | ✅ 로컬 |
| **GPT-4 (OpenAI)** | 매우 빠름 | 최고 | 유료 | ⚠️ 클라우드 |
| **Mock** | 즉시 | 데모용 | 무료 | ✅ 로컬 |

## 📞 지원 및 확장

### 다른 언어 지원
Python, JavaScript 등도 프롬프트만 수정하면 지원 가능:
```python
prompt = f"""
다음 Python 에러를 분석해주세요:
{error_info}
```

### 커스텀 분석 항목
시스템 프롬프트에 추가:
```
- 성능 최적화 제안
- 보안 취약점 분석
- 코드 스멜 지적
```

---

**✅ [3단계] 완료! 전체 AI Agent가 완성되었습니다!**

**전체 프로세스**:
1. ✅ 메일 파싱 → 에러 키워드 추출
2. ✅ 소스코드 탐색 → 컨텍스트 추출  
3. ✅ AI 분석 → 마크다운 리포트 생성

**⚠️ 안전성 보장**:
- AI는 절대 소스코드 파일을 수정하지 않습니다
- 오직 분석 리포트만 생성합니다
- 개발자가 검토 후 수동으로 적용합니다
