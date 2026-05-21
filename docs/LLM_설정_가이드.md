# 🤖 [3단계] LLM 설정 가이드

## Ollama 설치 및 설정

### 1. Ollama 설치

**Windows:**
```powershell
# Ollama 다운로드 및 설치
# https://ollama.com/download 에서 Windows 버전 다운로드
```

**확인:**
```powershell
ollama --version
```

### 2. Qwen2.5-7B 모델 다운로드

```powershell
# Qwen2.5 7B 모델 다운로드 (약 4.7GB)
ollama pull qwen2.5:7b

# 모델 목록 확인
ollama list
```

**다른 추천 모델:**
```powershell
# Llama 3 (8B)
ollama pull llama3

# CodeLlama (7B - 코드 특화)
ollama pull codellama

# Mistral (7B)
ollama pull mistral
```

### 3. Ollama 서버 실행

```powershell
# Ollama 서버 시작 (기본 포트: 11434)
ollama serve
```

새 터미널에서:
```powershell
# 테스트
ollama run qwen2.5:7b "Hello, how are you?"
```

### 4. Python 의존성 설치

```powershell
# requests 라이브러리 (표준 라이브러리가 아닌 경우)
pip install requests
```

## 사용 방법

### Ollama (로컬) 사용
```python
from step3_analysis_report import AnalysisReportGenerator

generator = AnalysisReportGenerator(
    llm_type="ollama",
    model_name="qwen2.5:7b",
    api_base_url="http://localhost:11434"
)

generator.process_all_errors(
    contexts_json_path="output/step2_code_contexts.json",
    output_dir="reports"
)
```

### OpenAI API 사용
```python
generator = AnalysisReportGenerator(
    llm_type="openai",
    model_name="gpt-4",
    api_base_url="https://api.openai.com/v1",
    api_key="your-api-key-here"  # 환경변수 권장: os.getenv('OPENAI_API_KEY')
)
```

## 실행

```powershell
# 프로젝트 루트에서
python src/step3_analysis_report.py
```

## 트러블슈팅

### Ollama 연결 실패
```
❌ Ollama 서버에 연결할 수 없습니다.
```

**해결:**
1. Ollama 서버가 실행 중인지 확인: `ollama serve`
2. 포트 확인: 기본 11434 포트가 사용 중인지 확인
3. 방화벽 설정 확인

### 모델을 찾을 수 없음
```
Error: model 'qwen2.5:7b' not found
```

**해결:**
```powershell
ollama pull qwen2.5:7b
ollama list  # 설치된 모델 확인
```

### 메모리 부족
Qwen2.5-7B는 약 8GB RAM이 필요합니다.

**더 작은 모델 사용:**
```powershell
# 3B 모델 (더 작음)
ollama pull qwen2.5:3b
```

스크립트에서 모델명 변경:
```python
model_name="qwen2.5:3b"
```

### 응답 속도가 느림
- GPU 가속 사용 권장 (CUDA/ROCm)
- 더 작은 모델 사용
- `temperature` 값 조정

## 모델 비교

| 모델 | 크기 | 특징 | 권장 용도 |
|------|------|------|----------|
| qwen2.5:7b | 4.7GB | 균형잡힌 성능, 한국어 지원 | **추천** |
| llama3 | 4.7GB | Meta의 최신 모델 | 일반 분석 |
| codellama | 3.8GB | 코드 특화 | 코드 리뷰 |
| qwen2.5:3b | 2.0GB | 가벼움, 빠름 | 저사양 PC |
| mistral | 4.1GB | 효율적 | 빠른 분석 |

## API 비용

### Ollama (로컬)
- ✅ **완전 무료**
- ✅ 데이터가 로컬에 머뭄
- ✅ 인터넷 필요 없음
- ❌ 초기 다운로드 필요 (4-5GB)
- ❌ GPU 권장

### OpenAI API
- ❌ 사용량 기반 과금
- ✅ 빠른 응답 속도
- ✅ 설치 불필요
- ❌ 인터넷 필요
- ❌ API 키 필요

## 환경 변수 설정 (권장)

### Windows PowerShell
```powershell
# 현재 세션
$env:OPENAI_API_KEY = "your-api-key-here"

# 영구 설정
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-api-key-here", "User")
```

### 코드에서 사용
```python
import os

api_key = os.getenv('OPENAI_API_KEY')

generator = AnalysisReportGenerator(
    llm_type="openai",
    model_name="gpt-4",
    api_key=api_key
)
```

## 프롬프트 커스터마이징

시스템 프롬프트를 수정하려면 `step3_analysis_report.py`의 `SYSTEM_PROMPT` 변수를 편집하세요:

```python
SYSTEM_PROMPT = """당신의 커스텀 프롬프트..."""
```

## 출력 형식

생성되는 리포트 파일명:
```
reports/오류_분석_리포트_CustomerService.md
reports/오류_분석_리포트_OrderController.md
```

각 리포트 포함 내용:
- 발생한 Exception 요약
- 에러 발생 위치
- AI 분석 결과 (원인, 문제점, 수정 방법, 코드 예시)
- 주의사항 및 다음 단계

## 보안 주의사항

⚠️ **절대 금지**:
- AI가 소스코드 파일을 직접 수정하는 기능 추가 금지
- 프로덕션 환경에서 자동 배포 금지
- API 키를 코드에 하드코딩 금지

✅ **권장**:
- 리포트 검토 후 수동으로 코드 수정
- 테스트 환경에서 충분히 검증
- API 키는 환경변수로 관리
