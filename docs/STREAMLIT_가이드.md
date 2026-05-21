# 🎨 Streamlit 웹 대시보드 가이드

발표용 시각화 웹 인터페이스 사용 가이드

## 📋 목차

1. [설치](#설치)
2. [실행 방법](#실행-방법)
3. [주요 기능](#주요-기능)
4. [발표 시나리오](#발표-시나리오)
5. [문제 해결](#문제-해결)

---

## 🔧 설치

### 1. 필수 패키지 설치

```bash
# requirements.txt 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install streamlit requests
```

### 2. 설치 확인

```bash
streamlit --version
# Streamlit, version 1.28.0
```

---

## 🚀 실행 방법

### 기본 실행

```bash
cd "c:\Users\신상윤\Desktop\한화 AX\ai-agent"
streamlit run app.py
```

실행 후 자동으로 브라우저가 열립니다:
- 로컬: http://localhost:8501
- 네트워크: http://192.168.x.x:8501 (다른 컴퓨터에서 접속 가능)

### 포트 변경

```bash
streamlit run app.py --server.port 8080
```

### 자동 새로고침 비활성화 (발표 시)

```bash
streamlit run app.py --server.runOnSave false
```

---

## 🎯 주요 기능

### 1. 분석 방법 선택 ⭐ NEW!

**두 가지 모드 지원**
- **⚡ Traditional (정확 탐색)**: Stack Trace 있는 경우, 0.03초 초고속
- **🧠 RAG (의미 검색)**: Stack Trace 없는 경우, 의미 기반 코드 탐색

**모드별 차이**
| 항목 | Traditional | RAG |
|------|------------|-----|
| **필수 정보** | Stack Trace | 에러 키워드만 |
| **속도** | ⚡ 0.03초 | 🐢 5초 |
| **정확도** | 100% | 70% |
| **적용 시나리오** | 명확한 에러 | 애매한 에러 |

### 2. 워크플로우 시각화

```
📧 [1단계]       🔍 [2단계]        🤖 [3단계]
메일 파싱    →   소스코드 추출  →   AI 분석
```

- 각 단계의 Input/Process/Output 표시
- 실시간 진행 상황 (Progress Bar)
- 단계별 성공/실패 상태

### 3. 사이드바 설정

**분석 방법 선택** ⭐ NEW!
- ⚡ Traditional (정확 탐색)
- 🧠 RAG (의미 검색)

**프로젝트 설정**
- Java 프로젝트 경로
- 이메일 폴더 경로

**Traditional 모드 설정**
- 컨텍스트 라인 수 (슬라이더)

**RAG 모드 설정** ⭐ NEW!
- 청크 크기 (300-1000, 기본 500)
- Top-K 결과 수 (3-10, 기본 5)
- 벡터 DB 재생성 (체크박스)

**LLM 설정**
- LLM 타입 선택: Mock / Ollama / OpenAI
- 모델 선택 (드롭다운)
- API Key 입력 (OpenAI)

### 3. 실행 현황

- **Progress Bar**: 0% → 100% 진행 표시
- **상태 메시지**: 각 단계별 실시간 상태
- **성공/실패 알림**: 컬러 코딩
- **소요 시간**: 전체 실행 시간 표시

### 4. 결과 시각화

**탭 구조**
1. **1단계 결과**
   - 처리된 파일 수
   - Exception 수
   - Stack Trace 수
   - 상세 JSON 데이터

2. **2단계 결과**
   - 추출 시도 수
   - 성공/실패 카운트
   - 파일별 상세 정보

3. **3단계 결과**
   - 생성된 리포트 수
   - 사용된 LLM/모델
   - **리포트 미리보기** (드롭다운 선택)

### 5. 리포트 미리보기

- 생성된 모든 `.md` 리포트 목록
- 드롭다운으로 선택
- 마크다운 렌더링하여 표시
- 원인 분석, 수정 방법, 코드 예시 확인

---

## 🎤 발표 시나리오

### 시나리오 1: 기본 데모 (2분)

```
1️⃣ Streamlit 앱 실행
   streamlit run app.py

2️⃣ 화면 공유
   - 워크플로우 다이어그램 설명 (30초)
   - "3단계로 나뉘어져 있고, 자동으로 실행됩니다"

3️⃣ 설정 확인 (사이드바)
   - "example_project로 데모 실행"
   - "Mock 모드 사용" (30초)

4️⃣ '🚀 전체 실행' 버튼 클릭
   - Progress Bar 진행 보여주기
   - 각 단계 완료 메시지 설명 (1분)

5️⃣ 결과 확인
   - 탭별로 결과 보여주기
   - 리포트 미리보기 (30초)
```

### 시나리오 2: 실제 프로젝트 분석 (5분)

```
1️⃣ 실제 에러 로그 준비
   - email/ 폴더에 새 로그 추가
   - "실제 운영 중 발생한 에러입니다" (30초)

2️⃣ 프로젝트 경로 변경
   - 사이드바에서 실제 프로젝트 경로 입력
   - "우리 회사 백엔드 프로젝트입니다" (30초)

3️⃣ LLM 선택
   - Ollama 또는 OpenAI 선택
   - 모델 설명 (30초)

4️⃣ 실행 및 진행 상황
   - 실시간 진행 보여주기
   - 각 단계 설명 (2분)

5️⃣ 생성된 리포트 분석
   - 리포트 내용 읽기
   - 원인 분석 설명
   - 수정 방법 설명 (1.5분)

6️⃣ 질의응답 (30초)
```

### 시나리오 3: Traditional vs RAG 비교 데모 (4분) ⭐ NEW!

```
1️⃣ Traditional 모드 실행
   - "먼저 Stack Trace가 있는 경우입니다"
   - ⚡ Traditional 선택
   - 실행 → 0.03초 초고속 완료
   - 정확한 라인 번호로 코드 찾기 (1분)

2️⃣ RAG 모드 실행
   - "이번엔 Stack Trace 없는 경우입니다"
   - 🧠 RAG 선택
   - 벡터 DB 인덱싱 (첫 실행)
   - 의미 기반 검색 → 관련 코드 자동 발견 (1.5분)

3️⃣ 결과 비교
   - 2단계 결과 탭 비교
     * Traditional: 성공 4개, 실패 5개
     * RAG: 검색 20개, 유사도 기반
   - "RAG는 정확한 위치 몰라도 찾습니다!" (1분)

4️⃣ 실무 활용 설명
   - "현업 메일: '화면에서 오류 났어요'"
   - "RAG가 자동으로 관련 코드 검색"
   - "실전 대응 가능!" (30초)
```

### 시나리오 4: 비교 데모 (Mock vs Real AI)

```
1️⃣ Mock 모드로 실행
   - "먼저 데모 모드로 보여드리겠습니다"
   - 빠른 실행 (0.03초)

2️⃣ 결과 확인
   - Mock 분석 결과 보기

3️⃣ Ollama로 재실행
   - LLM 설정 변경
   - --skip-stage1 --skip-stage2 체크 (기능 추가 필요)
   - 실제 AI 분석

4️⃣ 결과 비교
   - Mock vs Ollama 차이점
   - "실제 AI가 더 정확하고 상세합니다"
```

---

## 🎨 발표 팁

### 1. 화면 준비

- **듀얼 모니터**: 한쪽은 Streamlit, 한쪽은 코드
- **브라우저 전체화면**: F11 (발표 모드)
- **확대**: Ctrl + 마우스휠 (가독성)

### 2. 데모 데이터 준비

```bash
# 발표 전 확인 사항
- email/ 폴더에 샘플 파일 2-3개
- example_project/ 또는 실제 프로젝트 준비
- Ollama 서버 실행 (실제 AI 사용 시)
```

### 3. 백업 계획

```bash
# 인터넷 없을 경우
- Mock 모드 사용 (항상 동작)
- 미리 생성된 리포트 보여주기

# Streamlit 오류 시
- 터미널 버전 사용: python run_all.py
- 생성된 리포트 직접 열기
```

### 4. 설명 포인트

**1단계**
- "정규표현식으로 자동 파싱"
- "사람이 수동으로 찾을 필요 없음"

**2단계**
- "실시간으로 최신 코드 읽음"
- "캐시 아닌 직접 파일 읽기"

**3단계**
- "AI가 원인 분석 및 해결책 제시"
- "⚠️ 코드 절대 수정 안함, 리포트만 생성"

---

## 🎬 데모 영상 촬영 (선택)

```bash
# OBS Studio 등으로 화면 녹화
1. Streamlit 실행
2. 전체 프로세스 실행
3. 결과 확인
4. 5분 미만으로 편집
```

---

## ⚙️ 커스터마이징

### 테마 변경

`.streamlit/config.toml` 생성:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### 로고 추가

```python
# app.py 상단
st.image("logo.png", width=200)
```

---

## 🐛 문제 해결

### 1. Streamlit 설치 오류

```bash
# 가상환경 사용
python -m venv venv
venv\Scripts\activate
pip install streamlit
```

### 2. 포트 충돌

```bash
# 다른 포트 사용
streamlit run app.py --server.port 8502
```

### 3. 한글 깨짐

```python
# app.py에서 UTF-8 명시
with open(file, "r", encoding="utf-8") as f:
    content = f.read()
```

### 4. 느린 실행

```bash
# 캐시 정리
streamlit cache clear
```

---

## 📊 성능 팁

### 발표 중 끊김 방지

```python
# app.py에 캐싱 추가
@st.cache_data
def load_data():
    # 데이터 로딩
    pass
```

### 실시간 업데이트

```python
# 진행 상황 스트리밍
with st.spinner("처리 중..."):
    result = process()
```

---

## 📝 체크리스트

### 발표 전 (10분 전)

- [ ] Streamlit 서버 실행 확인
- [ ] 브라우저 열기 (localhost:8501)
- [ ] 샘플 데이터 확인 (email/ 폴더)
- [ ] Ollama 서버 실행 (실제 AI 사용 시)
- [ ] 화면 공유 테스트
- [ ] 확대/축소 조정

### 발표 중

- [ ] 워크플로우 다이어그램 설명
- [ ] 설정 옵션 보여주기
- [ ] 전체 실행 버튼 클릭
- [ ] 진행 상황 설명
- [ ] 결과 탭별로 확인
- [ ] 리포트 미리보기

### 발표 후

- [ ] 질의응답 준비
- [ ] 추가 데모 (요청 시)

---

## 🎓 추가 학습

- **Streamlit 문서**: https://docs.streamlit.io
- **데모 갤러리**: https://streamlit.io/gallery
- **컴포넌트**: https://streamlit.io/components

---

## 📞 지원

문제 발생 시:
1. GitHub Issues
2. Streamlit Community Forum
3. 프로젝트 README.md 참고

---

**🎉 발표 성공을 기원합니다!** 🚀
