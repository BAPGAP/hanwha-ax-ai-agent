# AI Agent for Error Analysis

에러 메일을 분석하여 소스코드 상의 문제를 찾고 수정 제안을 제공하는 AI 에이전트

## ✅ 전체 완료!

**[1단계]** ✅ 메일 파싱 및 에러 키워드 추출  
**[2단계]** ✅ 소스코드 실시간 접근 및 컨텍스트 추출  
**[3단계]** ✅ 원인 분석 및 수정 제안 리포트 생성  

## 🚀 빠른 시작

```bash
# 전체 프로세스 한번에 실행
python src/step1_email_parser.py    # 이메일 파싱
python src/step2_code_extractor.py  # 소스코드 추출
python src/step3_analysis_report.py # AI 분석 (Mock 모드)

# 결과 확인
explorer reports
```

## 프로젝트 구조

```
ai-agent/
├── email/                          # 에러 메일/로그 파일 저장 폴더
│   ├── sample_error.txt           # 샘플 에러 메일
│   └── database_error.log         # 샘플 데이터베이스 에러 로그
├── example_project/               # 예시 Java 프로젝트
│   └── src/
│       └── com/hanwha/ax/
│           ├── controller/
│           │   └── OrderController.java
│           ├── service/
│           │   └── CustomerService.java
│           └── model/
│               ├── Customer.java
│               └── Order.java
├── src/                           # Python 소스코드
│   ├── step1_email_parser.py     # [1단계] 메일 파싱 및 에러 추출 ✅
│   ├── step2_code_extractor.py   # [2단계] 소스코드 실시간 접근 ✅
│   └── step3_analysis_report.py  # [3단계] 원인 분석 및 리포트 생성 ✅
├── examples/                      # 사용 예시 스크립트
│   ├── test_step1_examples.py    # 1단계 다양한 활용 예시
│   └── test_step2_examples.py    # 2단계 다양한 활용 예시
├── output/                        # 출력 결과 저장 폴더
│   ├── step1_parsed_errors.json  # 1단계 파싱 결과
│   └── step2_code_contexts.json  # 2단계 코드 컨텍스트
├── reports/                       # AI 분석 리포트
│   ├── 오류_분석_리포트_CustomerService.md
│   └── 오류_분석_리포트_OrderController.md
├── docs/                          # 문서
│   ├── STEP1_완료.md             # 1단계 상세 문서
│   ├── STEP2_완료.md             # 2단계 상세 문서
│   ├── STEP3_완료.md             # 3단계 상세 문서
│   └── LLM_설정_가이드.md        # Ollama/OpenAI 설정
└── README.md                      # 프로젝트 설명
```

## 🛠️ [1단계] 메일 파싱 및 에러 키워드 추출

### 기능
- 이메일 폴더에서 `.txt`, `.log`, `.eml`, `.msg` 파일 자동 탐색
- Java Stack Trace에서 클래스명, 메서드명, 라인 번호 추출
- Exception 타입 및 메시지 추출
- JSON 형식으로 결과 저장

### 실행 방법

```bash
cd src
python step1_email_parser.py
```

### 출력 예시

```json
{
  "sample_error.txt": {
    "has_error": true,
    "exceptions": [
      {
        "exception": "java.lang.NullPointerException",
        "message": "Cannot invoke \"String.length()\" because \"customerName\" is null"
      }
    ],
    "stack_traces": [
      {
        "full_class": "com.hanwha.ax.service.CustomerService",
        "package": "com.hanwha.ax.service",
        "class_name": "CustomerService",
        "method": "validateCustomerData",
        "file": "CustomerService.java",
        "line": 145
      }
    ]
  }
}
```

### 사용 예시 (코드에서 직접 사용)

```python
from step1_email_parser import EmailParser

# Parser 생성
parser = EmailParser(email_folder="email")

# 단일 이메일 파싱
email_text = parser.read_email_file("email/sample_error.txt")
result = parser.parse_email(email_text)

# 폴더 내 모든 이메일 파싱
all_results = parser.parse_all_emails()

# JSON 파일로 저장
parser.save_parsed_results(all_results, "output/parsed_errors.json")
```

### 다양한 활용 예시

더 많은 사용 예시를 보려면 아래 명령어를 실행하세요:

```bash
python examples/test_step1_examples.py
```

이 스크립트는 다음과 같은 예시를 포함합니다:
- 예시 1: 단일 이메일 파일 파싱
- 예시 2: 폴더 내 모든 이메일 파싱
- 예시 3: 에러 발생 위치만 추출
- 예시 4: 특정 패키지의 에러만 필터링
- 예시 5: 에러 요약 리포트 생성

## 🛠️ [2단계] 소스코드 실시간 접근 및 컨텍스트 추출

### 기능
- 1단계에서 추출한 JSON 데이터(클래스명, 라인 번호) 자동 읽기
- Java 프로젝트 디렉토리에서 `.java` 파일 실시간 재귀 탐색
- 클래스명 + 패키지명으로 정확한 파일 매칭
- **파일을 직접 열어 최신 수정 사항 반영**
- 에러 라인 기준 **앞뒤 30줄** 추출 (커스터마이징 가능)
- 에러 라인 하이라이팅 (`is_error_line: true`)
- JSON 형식으로 결과 저장

### 실행 방법

```bash
cd src
python step2_code_extractor.py
```

### 출력 예시

```json
{
  "sample_error.txt": {
    "email_file": "sample_error.txt",
    "exceptions": [
      {
        "exception": "java.lang.NullPointerException",
        "message": "Cannot invoke \"String.length()\" because \"customerName\" is null"
      }
    ],
    "contexts": [
      {
        "success": true,
        "file_path": "example_project/src/.../CustomerService.java",
        "total_lines": 60,
        "error_line": 145,
        "context_start": 115,
        "context_end": 60,
        "context_lines": [
          {
            "line_number": 145,
            "content": "    if (customerName.length() < 2) {",
            "is_error_line": true
          }
        ],
        "raw_code": "전체 코드 텍스트...",
        "class_name": "CustomerService",
        "method": "validateCustomerData"
      }
    ]
  }
}
```

### 사용 예시 (코드에서 직접 사용)

```python
from step2_code_extractor import CodeExtractor

# CodeExtractor 생성
extractor = CodeExtractor(
    project_root="example_project",  # Java 프로젝트 경로
    context_lines=30  # 앞뒤 30줄
)

# 1단계 결과에서 자동 추출
contexts = extractor.process_parsed_errors("output/step1_parsed_errors.json")

# JSON 파일로 저장
extractor.save_contexts(contexts, "output/step2_code_contexts.json")
```

### 다양한 활용 예시

더 많은 사용 예시를 보려면 아래 명령어를 실행하세요:

```bash
python examples/test_step2_examples.py
```

이 스크립트는 다음과 같은 예시를 포함합니다:
- 예시 1: 단일 에러 위치의 소스코드 컨텍스트 추출
- 예시 2: 1단계 JSON 파일에서 자동으로 추출
- 예시 3: 성공한 컨텍스트만 필터링
- 예시 4: 에러 라인의 실제 코드 표시
- 예시 5: LLM 프롬프트용 코드 스니펫 생성
- 예시 6: 커스텀 컨텍스트 크기로 추출

## 🛠️ [3단계] 원인 분석 및 수정 제안 리포트 생성

### 기능
- 1, 2단계 데이터 통합 (에러 로그 + 소스코드)
- **OpenAI API / Ollama API 호환** LLM 프롬프트 빌드
- **Mock 모드** - Ollama 없이도 테스트 가능
- Ollama (Qwen2.5-7B, CodeLlama 등) 지원
- OpenAI (GPT-4, GPT-3.5) 지원
- 클래스별 **마크다운 리포트** 자동 생성
- **엄격한 시스템 프롬프트** - AI가 소스코드 파일 직접 수정 금지
- 에러 원인, 수정 방법, 코드 예시, 권장 사항 포함

### 실행 방법

```bash
# Mock 모드 (Ollama 없이 데모 분석)
python src/step3_analysis_report.py

# Ollama 사용 (실제 AI 분석)
# 1. Ollama 설치: https://ollama.com/download
# 2. 모델 다운로드: ollama pull qwen2.5:7b
# 3. 서버 실행: ollama serve
# 4. step3_analysis_report.py에서 use_mock=False로 변경
```

### 생성되는 리포트 예시

**파일**: `reports/오류_분석_리포트_CustomerService.md`

```markdown
# 🐛 에러 분석 리포트: CustomerService

## 📋 발생한 Exception
- **java.lang.NullPointerException**
  - Cannot invoke "String.length()" because "customerName" is null

## 📍 에러 발생 위치
- **클래스**: CustomerService
- **메서드**: validateCustomerData()
- **라인**: 145

## 🔍 AI 분석 결과

### 1. 에러 원인 분석
Null 체크 없이 .length() 메서드 호출...

### 2. 문제가 되는 코드
[문제 코드 지적]

### 3. 수정 방법
[안전한 수정 방법]

### 4. 수정된 코드 예시
```java
// Null 체크 추가
if (customerName == null || customerName.isEmpty()) {
    throw new IllegalArgumentException("Customer name is required");
}
```

### 5. 추가 권장 사항
- Bean Validation 사용
- 유닛 테스트 추가
- 로깅 강화

## ⚠️ 중요 공지
AI가 기존 소스코드 파일을 직접 수정하지 않았습니다.
개발자가 검토 후 수동으로 적용하세요.
```

### 사용 예시 (코드에서 직접 사용)

```python
from step3_analysis_report import AnalysisReportGenerator

# Mock 모드 (데모용)
generator = AnalysisReportGenerator(use_mock=True)

# Ollama 사용
generator = AnalysisReportGenerator(
    use_mock=False,
    llm_type="ollama",
    model_name="qwen2.5:7b"
)

# OpenAI 사용
generator = AnalysisReportGenerator(
    llm_type="openai",
    model_name="gpt-4",
    api_key="your-api-key"
)

# 리포트 생성
generator.process_all_errors(
    "output/step2_code_contexts.json",
    "reports"
)
```

### 안전성 보장

**시스템 프롬프트에 명시**:
```
⚠️ 절대 금지 사항:
- 기존 Java 소스코드 파일을 직접 수정하거나 덮어쓰는 행위는 절대 금지
- 파일 시스템에 직접 접근 금지
- 오직 분석 결과를 텍스트로 제공만 허용
```

**코드 레벨 보호**:
- AI는 마크다운 텍스트만 반환
- 리포트 디렉토리에만 쓰기 권한
- 소스코드 디렉토리 접근 불가

## 📋 완료 상황

- **[1단계]** ✅ 메일 파싱 및 에러 키워드 추출 - **완료**
- **[2단계]** ✅ 소스코드 실시간 접근 및 컨텍스트 추출 - **완료**
- **[3단계]** ✅ 원인 분석 및 수정 제안 리포트 생성 - **완료**

## 📚 상세 문서

- [docs/STEP1_완료.md](docs/STEP1_완료.md) - 1단계 상세 가이드
- [docs/STEP2_완료.md](docs/STEP2_완료.md) - 2단계 상세 가이드
- [docs/STEP3_완료.md](docs/STEP3_완료.md) - 3단계 상세 가이드
- [docs/LLM_설정_가이드.md](docs/LLM_설정_가이드.md) - Ollama/OpenAI 설정

## 🎯 주요 특징

### 1. 완전 자동화된 워크플로우
```
이메일 수신 → 에러 파싱 → 소스코드 탐색 → AI 분석 → 리포트 생성
```

### 2. 실시간 소스코드 접근
- 최신 수정 사항 즉시 반영
- 캐싱이 아닌 직접 파일 읽기
- 정확한 라인 번호 추출

### 3. 다양한 LLM 지원
- **Mock 모드**: 테스트용 (무료)
- **Ollama**: 로컬 실행 (무료, 데이터 보안)
- **OpenAI**: 클라우드 (유료, 고품질)

### 4. 절대적인 안전성
- ⚠️ **AI가 소스코드 파일을 절대 수정하지 않음**
- 오직 분석 리포트만 생성
- 개발자가 검토 후 수동 적용

### 5. 실용적인 출력
- 마크다운 형식 리포트
- 원인 분석 + 수정 방법 + 코드 예시
- 팀 공유 및 문서화 용이

## 🔄 전체 워크플로우

```
┌─────────────────────────────────────────────────────────┐
│ [1단계] 메일 파싱                                        │
│  • 이메일/로그 파일 읽기                                  │
│  • Stack Trace 정규표현식 파싱                           │
│  • 클래스명, 메서드명, 라인 번호 추출                      │
│  • JSON으로 저장                                         │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ [2단계] 소스코드 추출                                     │
│  • Java 프로젝트 디렉토리 탐색                            │
│  • 클래스명으로 파일 찾기                                 │
│  • 에러 라인 기준 ±30줄 추출                              │
│  • JSON으로 저장                                         │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ [3단계] AI 분석                                          │
│  • 에러 로그 + 소스코드 통합                              │
│  • LLM 프롬프트 빌드                                     │
│  • Ollama/OpenAI API 호출                                │
│  • 원인 분석 및 수정 제안                                 │
│  • 마크다운 리포트 생성                                   │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ [개발자 검토 및 적용]                                     │
│  • 리포트 검토                                           │
│  • 팀 리뷰                                               │
│  • 수동으로 코드 수정                                     │
│  • 테스트 및 검증                                         │
│  • 배포                                                  │
└─────────────────────────────────────────────────────────┘
```

## 🛡️ 보안 및 안전성

### AI 소스코드 수정 금지 (3중 보호)

**1. 시스템 프롬프트 레벨**
```
⚠️ 절대 금지 사항:
- 기존 Java 소스코드 파일을 직접 수정하거나 덮어쓰는 행위는 절대 금지
```

**2. 코드 레벨**
```python
# ❌ 이런 코드는 존재하지 않음
# with open("CustomerService.java", "w") as f:
#     f.write(fixed_code)

# ✅ 오직 리포트만
with open("reports/오류_분석_리포트.md", "w") as f:
    f.write(report)
```

**3. 프로세스 레벨**
- AI 출력: 마크다운 텍스트
- 개발자 검토: 필수
- 수동 적용: 개발자가 직접

## 💻 요구사항

- Python 3.7+
- 외부 라이브러리:
  - `requests` (HTTP 요청용)
- 선택 사항:
  - Ollama (로컬 LLM)
  - OpenAI API 키 (클라우드 LLM)

## 📖 사용 가이드

### 새 에러 분석하기

1. **이메일/로그 파일 추가**
```bash
# email/ 폴더에 .txt, .log 파일 추가
cp new_error.log email/
```

2. **전체 프로세스 실행**
```bash
python src/step1_email_parser.py
python src/step2_code_extractor.py
python src/step3_analysis_report.py
```

3. **리포트 확인**
```bash
explorer reports
# 또는
code reports/오류_분석_리포트_*.md
```

### 프로젝트 경로 변경

```python
# step2_code_extractor.py
extractor = CodeExtractor(
    project_root="your-java-project-path",  # 변경
    context_lines=30
)
```

### 다른 모델 사용

```python
# step3_analysis_report.py
generator = AnalysisReportGenerator(
    llm_type="ollama",
    model_name="codellama"  # 또는 "llama3", "mistral"
)
```

## 요구사항

- Python 3.7+
- 외부 라이브러리 없음 (표준 라이브러리만 사용)
