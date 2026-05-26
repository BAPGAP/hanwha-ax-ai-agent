# 🤖 AI Agent 에러 분석 시스템

Java 에러 이메일/로그를 받아 소스코드에서 원인을 찾고 AI 분석 리포트를 생성하는 시스템.

---

## 📐 아키텍처

```
이메일/로그 파일 (.eml / .log / .txt)
        │
        ▼
┌─────────────────────────┐
│  1단계: AI 메일 분석     │  LLM: Groq compound-beta
│  step1_email_parser.py  │  출력: 오류 요약, 심각도, RAG 검색 키워드
└────────────┬────────────┘
             │ output/step1_parsed_errors.json
             ▼
┌─────────────────────────┐
│  2단계: RAG 코드 검색    │  ChromaDB + all-MiniLM-L6-v2
│  step2_rag_extractor.py │  출력: 유사 소스코드 청크 (유사도 순)
└────────────┬────────────┘
             │ output/step2_rag_contexts.json
             ▼
┌─────────────────────────┐
│  3단계: AI 분석 리포트   │  LLM: Groq compound-beta
│  step3_rag_analysis.py  │  출력: 통합 마크다운 리포트
└─────────────────────────┘
             │
             ▼
   reports/{YYYYMMDD_HHMMSS}_분석리포트_{이메일명}.md
```

**핵심 특징**

- Stack Trace가 없는 "화면에서 이런 오류 났어요" 수준의 메일도 분석 가능
- **이메일 1개 → 리포트 파일 1개** (여러 검색 쿼리 결과를 페이지 형태로 통합)
- 일부 쿼리 분석 실패 시에도 오류 메시지를 해당 섹션에 포함, 리포트 생성 계속
- `429 Rate Limit` → 5·15·30초 자동 재시도
- `413 Payload Too Large` → 프롬프트 절반 축소 후 자동 재시도

---

## ⚡ 빠른 시작

### 1. 환경 준비

```powershell
# 패키지 설치
pip install -r requirements.txt

# Groq API 키 발급: https://console.groq.com (무료)
# .env 파일 생성
Set-Content .env "GROQ_API_KEY=gsk_여기에_발급받은_키_입력"
```

### 2. Streamlit 대시보드 (추천)

```powershell
# 실행 전 기존 프로세스 정리
Get-Process python* 2>$null | Stop-Process -Force 2>$null

cd "한화AX\hanwha-ax-ai-agent"
python -m streamlit run app.py --server.port 8501 --server.fileWatcherType none
# → 브라우저에서 http://localhost:8501 접속
```

### 3. CLI 실행 (배치 처리)

```powershell
# 기본 실행 (Groq + 예시 프로젝트)
python run_all_rag.py

# 실제 Java 프로젝트 지정
python run_all_rag.py --project "C:\workspace\backend" --email "C:\mail\inbox"

# Mock 모드 (API 키 없이 데모)
python run_all_rag.py --llm mock

# 벡터 DB 재생성 (소스코드 변경 시)
python run_all_rag.py --reindex

# 도움말
python run_all_rag.py --help
```

---

## 📁 프로젝트 구조

```
hanwha-ax-ai-agent/
├── .env                          # Groq API 키 (GROQ_API_KEY=...)
├── app.py                        # Streamlit 웹 대시보드
├── run_all_rag.py                # CLI 전체 파이프라인 실행
├── requirements.txt              # Python 의존성
│
├── email/                        # 분석할 이메일/로그 파일 저장소
│   ├── sample_error.txt
│   └── database_error.log
│
├── src/                          # 핵심 파이프라인 모듈
│   ├── step1_email_parser.py     # [1단계] Groq로 이메일 파싱 → JSON
│   ├── step2_rag_extractor.py    # [2단계] 벡터 DB 의미 유사도 검색
│   └── step3_rag_analysis.py     # [3단계] Groq로 통합 분석 리포트 생성
│
├── example_project/              # 샘플 Java 프로젝트 (RAG 인덱스 대상)
│   └── policy-search-demo/
│
├── output/                       # 파이프라인 중간 결과 (자동 생성)
│   ├── step1_parsed_errors.json
│   └── step2_rag_contexts.json
│
├── vector_db/                    # ChromaDB 벡터 인덱스 (자동 생성)
│
├── reports/                      # 최종 분석 리포트 (Markdown)
│   └── {YYYYMMDD_HHMMSS}_분석리포트_{이메일명}.md
│
└── docs/                         # 추가 문서
```

---

## 🧩 단계별 상세

### 1단계 — AI 메일 분석 (`step1_email_parser.py`)

| 항목 | 내용 |
|------|------|
| **LLM** | Groq compound-beta (기본), Ollama / OpenAI 선택 가능 |
| **입력** | `.eml` `.log` `.txt` `.msg` `.csv` `.xml` `.err` |
| **출력** | `output/step1_parsed_errors.json` |
| **기능** | EML MIME 파싱, 첨부파일 텍스트 추출, 오류 요약·심각도·RAG 키워드 생성 |
| **폴백** | LLM 실패 시 정규식으로 Stack Trace 자동 파싱 |

출력 예시:
```json
{
  "sample_error.txt": {
    "has_error": true,
    "error_summary": "CustomerService.validateCustomerData()에서 NPE 발생...",
    "error_type": "NullPointerException",
    "severity": "HIGH",
    "root_cause": "customerName null 체크 누락",
    "search_queries": [
      "CustomerService validateCustomerData",
      "null check String validation",
      "customer data processing error"
    ]
  }
}
```

---

### 2단계 — RAG 코드 검색 (`step2_rag_extractor.py`)

| 항목 | 내용 |
|------|------|
| **벡터 DB** | ChromaDB (로컬 `vector_db/` 폴더 자동 생성) |
| **임베딩** | `all-MiniLM-L6-v2` (HuggingFace) |
| **입력** | `step1_parsed_errors.json` + Java 프로젝트 경로 |
| **출력** | `output/step2_rag_contexts.json` |
| **기능** | Java 코드를 청크로 분할 → 벡터 임베딩 → 검색 쿼리로 유사 코드 탐색 |

> 소스코드가 변경되지 않으면 재실행 불필요.
> UI에서 **"2단계 건너뛰기"** 체크 또는 CLI에서 기존 `step2_rag_contexts.json` 재사용.

---

### 3단계 — AI 분석 리포트 (`step3_rag_analysis.py`)

| 항목 | 내용 |
|------|------|
| **LLM** | Groq compound-beta (기본), Ollama / OpenAI 선택 가능 |
| **입력** | `step2_rag_contexts.json` (없으면 `step1_parsed_errors.json` 자동 폴백) |
| **출력** | `reports/{YYYYMMDD_HHMMSS}_분석리포트_{이메일명}.md` |
| **비율** | **이메일 1개 = 리포트 파일 1개** (쿼리 수와 무관) |

생성 리포트 구조:
```markdown
# 🤖 AI 에러 분석 리포트

| 원본 파일 | sample_error.txt |
| 생성 시간 | 2026-05-24 03:11 |
| 분석 수   | 3개              |
| 심각도    | HIGH             |

> 오류 요약: ...

---

## 📋 목차
1. 분석 1/3
2. 분석 2/3
3. 분석 3/3

---

## 🔍 분석 1/3: `CustomerService validateCustomerData`
### 📧 오류 정보
### 🔎 관련 소스코드 (RAG 검색 결과)
### 🤖 AI 분석

---

## 🔍 분석 2/3: ...
## 🔍 분석 3/3: ...

---

## ⚠️ 안전성 공지
- AI는 소스코드를 직접 수정하지 않습니다
- 이 리포트는 참고 자료입니다. 개발자가 검토 후 수동 적용하세요.
```

---

## 🖥️ Streamlit 대시보드

| 기능 | 설명 |
|------|------|
| **모델 선택** | 1단계·3단계 각각 Groq / Ollama / OpenAI / Mock 선택 |
| **파일 입력** | 폴더 전체 또는 개별 파일 다중 선택 (OS 탐색기 연동) |
| **RAG 설정** | 청크 크기, Top-K, 벡터 DB 재생성, 2단계 건너뛰기 |
| **실행 현황** | Progress Bar + 단계별 성공/실패 실시간 표시 |
| **결과 탭** | 1·2·3단계 결과 각각 탭으로 확인 |
| **리포트 뷰어** | 생성된 모든 리포트를 최신 순으로 선택·렌더링 (항상 화면 하단 표시) |

---

## 🛠️ 환경 설정

### 지원 LLM

| LLM | 설정 | 비고 |
|-----|------|------|
| **Groq** (기본) | `.env`에 `GROQ_API_KEY=...` | 빠름, 무료 플랜 있음 |
| **Ollama** | `ollama serve` 실행 후 모델 선택 | 로컬 실행, 인터넷 불필요 |
| **OpenAI** | UI에서 API 키 직접 입력 | GPT-4o 등 |
| **Mock** | 설정 불필요 | 데모·테스트용 더미 응답 |

### Groq 지원 모델

| 모델 | 특징 |
|------|------|
| `compound-beta` | **기본값**, 웹 검색 통합 |
| `compound-beta-mini` | 경량 버전 |
| `llama-3.3-70b-versatile` | 고성능 |
| `llama-3.1-8b-instant` | 빠른 응답 |

---

## 🔒 보안

- API 키는 반드시 `.env` 파일에 저장 — 소스코드에 직접 기재하지 마세요
- `.env`는 `.gitignore`에 추가 권장
- AI는 소스코드 파일을 **절대 직접 수정하지 않습니다** — 리포트는 참고 자료
- 시스템 프롬프트에 코드 수정 금지 지침 명시되어 있습니다

---

## 📝 라이선스

한화AX 내부용 / Internal Use Only
