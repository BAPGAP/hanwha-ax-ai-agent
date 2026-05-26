# 증권조회 데모 프로젝트
## 한화AX - 화면 / PSI / DSI / MyBatis 계층 구조 예제

---

## 📐 시스템 계층 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                         화면 (View)                              │
│           src/main/resources/templates/policySearch.html         │
│    조회조건: 증권번호 / 고객명 / 고객 주민번호                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP POST /policy/search
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              PSI (Presentation Service Interface)                │
│           com.hanwha.ax.psi.PolicySearchPSI.java                 │
│    역할: HTTP 요청 수신 → DSI 호출 → 결과를 View에 전달          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ selectPolicyList(searchVO)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                DSI (Data Service Interface)                       │
│           com.hanwha.ax.dsi.PolicySearchDSI.java (Interface)     │
│           com.hanwha.ax.dsi.impl.PolicySearchDSIImpl.java (구현) │
│    역할: 업무 로직 수행, 주민번호 마스킹, Mapper 호출            │
└──────────────────────────┬──────────────────────────────────────┘
                           │ policySearchMapper.selectPolicyList()
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MyBatis Mapper                                 │
│           com.hanwha.ax.mapper.PolicySearchMapper.java            │
│           src/main/resources/mapper/PolicySearchMapper.xml        │
│    역할: SQL 정의 및 실행 (동적 쿼리 - <where>, <if> 태그)       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ SQL 실행
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DB (H2 In-Memory)                           │
│           TB_POLICY (증권) / TB_CUSTOMER (고객)                   │
│           10명 고객 / 20건 증권 샘플 데이터                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 프로젝트 구조

```
policy-search-demo/
├── pom.xml                                           # Maven 빌드 설정
├── run.ps1                                           # 실행 스크립트 (PowerShell)
├── mvnw.cmd                                          # Maven Wrapper
└── src/main/
    ├── java/com/hanwha/ax/
    │   ├── PolicySearchApplication.java              # Spring Boot 진입점
    │   ├── psi/
    │   │   ├── PolicySearchPSI.java                 # [PSI] 증권조회 컨트롤러
    │   │   └── RootPSI.java                         # 루트 경로 리다이렉트
    │   ├── dsi/
    │   │   ├── PolicySearchDSI.java                 # [DSI] 서비스 인터페이스
    │   │   └── impl/
    │   │       └── PolicySearchDSIImpl.java          # [DSI] 서비스 구현체
    │   ├── mapper/
    │   │   └── PolicySearchMapper.java              # [MyBatis] Mapper 인터페이스
    │   └── vo/
    │       ├── PolicySearchVO.java                  # 조회조건 VO
    │       └── PolicySearchResultVO.java            # 조회결과 VO
    └── resources/
        ├── application.yml                          # 앱 설정
        ├── schema.sql                               # DDL (테이블 생성)
        ├── data.sql                                 # DML (샘플 데이터)
        ├── mapper/
        │   └── PolicySearchMapper.xml               # [MyBatis] SQL 매퍼 XML
        └── templates/
            └── policySearch.html                    # [화면] Thymeleaf 템플릿
```

---

## 🗃️ 샘플 데이터

| 고객명 | 증권번호 | 상품명 | 가입기간 | 월보험료 | 보장금액 | 상태 |
|--------|----------|--------|----------|----------|----------|------|
| 김영수 | P20230001 | 한화생명 종신보험 Premium | 40년 | 85,000 | 200,000,000 | 정상 |
| 김영수 | P20210034 | 한화손해 운전자보험 | 10년 | 25,000 | 50,000,000 | 정상 |
| 이미영 | P20220156 | 한화생명 어린이보험 스마트 | 20년 | 62,000 | 100,000,000 | 정상 |
| 박철호 | P20180345 | 한화생명 종신보험 Premium | 40년 | 120,000 | 300,000,000 | 실효 |
| 박철호 | P20150123 | 한화생명 CI보험 | 10년 | - | 50,000,000 | 만기 |
| ... | ... | ... | ... | ... | ... | ... |

총 **10명 고객 / 20건 증권** 데이터 포함

---

## 🚀 실행 방법

### 방법 1: PowerShell 스크립트 (권장)
```powershell
cd example_project/policy-search-demo
.\run.ps1
```

### 방법 2: Maven 직접 실행 (Maven 설치된 경우)
```bash
cd example_project/policy-search-demo
mvn spring-boot:run
```

### 방법 3: IntelliJ IDEA / VS Code
1. `policy-search-demo` 폴더를 Maven 프로젝트로 열기
2. `PolicySearchApplication.java` → Run 실행

---

## 🌐 접속 방법

- **증권조회 화면**: http://localhost:8080
- **H2 DB 콘솔**: http://localhost:8080/h2-console
  - JDBC URL: `jdbc:h2:mem:policydb`
  - Username: `sa` / Password: (없음)

---

## 🔍 조회 테스트 시나리오

| 조회조건 | 입력값 | 예상결과 |
|----------|--------|----------|
| 조건 없음 (전체 조회) | (모두 공백) | 20건 전체 |
| 고객명으로 조회 | `김영수` | 2건 |
| 증권번호로 조회 | `P20230001` | 1건 |
| 고객명 부분 조회 | `김` | `김영수` 2건 |
| 상태 확인 | 고객명: `박철호` | 정상/실효/만기 혼합 |

---

## 🛠️ 기술 스택

| 계층 | 기술 |
|------|------|
| View | Thymeleaf 3.x |
| PSI | Spring MVC (Controller) |
| DSI | Spring Service (Interface + Impl) |
| Mapper | MyBatis 3.x |
| DB | H2 In-Memory Database |
| Build | Maven 3.9 + Spring Boot 2.7.18 |
| Java | JDK 1.8 |
