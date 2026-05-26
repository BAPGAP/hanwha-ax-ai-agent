# 🤖 AI 에러 분석 리포트 (RAG 기반)

**생성 시간**: 2026-05-24 02:12:26  
**원본 이메일**: 증권번호 조회 화면 오류.eml  
**LLM**: groq (compound-beta)  
**검색 방법**: RAG (Retrieval-Augmented Generation)

---

## 📧 에러 정보

- **오류 요약**: 증권번호 조회 화면에서 전체 조회를 누를 때 조회 결과에 10건만 표시되고, 총 18건이라고 표시되는 오류가 발생했습니다. 이로 인해 사용자가 정확한 전체 데이터를 확인하지 못하고 있습니다.
- **심각도**: HIGH

---

## 🔎 RAG 검색 결과

**검색 쿼리**: `증권번호조회서비스 조회결과처리`

### 1. PolicySearchPSI.java (유사도: 54.52%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\psi\PolicySearchPSI.java`
- **청크 ID**: 8

```java
return "policySearch";
    }

    /**
     * 주민등록번호 마스킹 (로그 출력용)
     * 예: 900101-1234567 → 900101-*******
     */
    private String maskRrn(String rrn) {
        if (rrn == null || rrn.trim().isEmpty()) return "";
        if (rrn.length() >= 6) {
            return rrn.substring(0, 6) + "-*******";
        }
        return "***";
    }
}
```

### 2. PolicySearchResultVO.java (유사도: 53.24%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\vo\PolicySearchResultVO.java`
- **청크 ID**: 2

```java
/** 계약상태 (정상/실효/해지/만기) */
    private String contractStatus;

    /** 계약상태 코드 */
    private String contractStatusCode;

    /** 담당 설계사명 */
    private String agentName;

    /** 담당 지점명 */
    private String branchName;

    /** 전체 건수 (페이징용) */
    private int totalCount;
}
```

### 3. PolicySearchPSI.java (유사도: 53.14%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\psi\PolicySearchPSI.java`
- **청크 ID**: 7

```java
log.info("[PSI] 증권조회 결과 건수: {}", totalCount);

        // 화면에 전달할 데이터 설정
        model.addAttribute("searchVO", searchVO);
        model.addAttribute("resultList", resultList);
        model.addAttribute("totalCount", totalCount);
        model.addAttribute("searchExecuted", true);

        return "policySearch";
    }
```

---

## 🤖 AI 분석

## 1️⃣ 원인 분석  

| 구분 | 내용 |
|------|------|
| **현상** | “전체 조회” 버튼을 눌렀을 때 **총 건수는 18건**이라고 표시되지만, 화면에 실제로 보여지는 리스트는 **10건**만 출력됨 |
| **핵심 원인** | **페이징 로직**이 서버와 클라이언트 사이에서 일관되지 않게 적용돼서, `totalCount`(전체 건수)와 `resultList`(현재 페이지에 보여줄 데이터) 사이에 불일치가 발생함 |
| **구체적인 메커니즘** | 1. `PolicySearchPSI`‑Controller 에서는 DB/서비스에서 조회한 전체 건수(`totalCount`)와 현재 페이지에 해당하는 **일부** 데이터(`resultList`)를 모델에 담아 뷰에 전달한다. <br>2. 현재 구현에서는 **페이지 사이즈(pageSize)** 가 고정(예: 10) 혹은 기본값으로 설정돼 있어, `resultList` 에는 첫 페이지(10건)만 담긴다. <br>3. 뷰(HTML/JS)에서는 `totalCount` 를 그대로 표시하고, `resultList` 를 그대로 출력하기 때문에 “총 18건”이라는 문구와 “10건만 보임”이라는 불일치가 발생한다. <br>4. 만약 페이지 이동(다음 페이지) UI가 없거나, 페이지 파라미터가 전달되지 않으면 사용자는 나머지 8건을 볼 방법이 없게 된다. |
| **가능한 추가 원인** | - `PolicySearchResultVO.totalCount` 가 **페이징용**(전체 건수)으로 정의돼 있지만, 실제 서비스 로직에서 **전체 건수와 현재 페이지 건수를 혼용**했을 가능성 <br>- 프론트엔드 템플릿(예: Thymeleaf, JSP)에서 `resultList` 를 **고정된 10건만 반복**하도록 구현돼 있을 수 있음 <br>- `pageSize` 를 하드코딩하거나, `request` 파라미터(`page`, `size`)를 읽어오지 못하는 경우 |

---

## 2️⃣ 영향 범위  

| 영역 | 영향 정도 |
|------|-----------|
| **사용자 경험** | 전체 데이터를 확인하지 못해 업무 처리에 오류가 발생할 수 있음 → **높음** |
| **데이터 정확성** | 화면에 표시된 건수와 실제 건수가 다르므로, 보고·결정 과정에서 오해가 생김 → **중간~높음** |
| **시스템 신뢰도** | 금융·보험 분야에서 “조회 결과가 누락됐다”는 인식은 서비스 신뢰도 저하로 이어짐 → **높음** |
| **추가 개발 비용** | 페이징 로직을 재검토·수정해야 하며, UI/UX 테스트가 필요 → **중간** |
| **운영 위험** | 잘못된 데이터 제공이 계약·청구 등 핵심 비즈니스 로직에 영향을 줄 가능성 (특히 자동화된 배치·리포트와 연계된 경우) → **높음** |

---

## 3️⃣ 해결 방법 (우선순위)  

1. **페이징 파라미터 전달·처리 로직 점검**  
   - Controller 메서드에서 `page`(현재 페이지)와 `size`(페이지당 건수) 파라미터를 명시적으로 받도록 하고, 기본값을 설정한다.  
   - 서비스 레이어에서 **전체 건수**와 **현재 페이지 데이터**를 각각 구해 `totalCount`와 `resultList`에 정확히 매핑한다.  

2. **프론트엔드(뷰)에서 페이지 네비게이션 구현**  
   - `totalCount` 와 `pageSize` 를 이용해 페이지 수를 계산하고, “다음/이전” 버튼 혹은 페이지 번호 링크를 제공한다.  
   - 사용자가 페이지를 이동하면 해당 페이지 파라미터를 서버에 전달해 `resultList` 를 갱신한다.  

3. **`PolicySearchResultVO.totalCount` 용도 명확화**  
   - 주석에 “전체 건수(페이징용)”이라고 적힌 부분을 **‘전체 조회 건수(전체 레코드 수)’** 로 바꾸고, 별도 `pageSize`/`currentPage` 필드를 VO에 추가해도 좋다.  

4. **디폴트 페이지 사이즈를 설정하고, 설정값을 외부 프로퍼티로 관리**  
   - 하드코딩된 `10` 대신 `application.yml`(또는 `properties`)에 `search.pageSize=10` 과 같이 정의하고, 코드에서는 `@Value` 로 주입한다.  

5. **테스트 케이스 추가**  
   - **전체 건수 > 페이지 사이즈** 상황, **페이지 파라미터 누락** 상황, **페이지 번호 초과** 상황 등을 포함한 단위·통합 테스트를 작성한다.  

---

## 4️⃣ 참고 코드 (수정·적용 예시)

> **※ 아래 코드는 참고용이며, 실제 적용 전 반드시 리뷰와 테스트를 진행하세요.**  

### (1) Controller – 페이지 파라미터 받기  

```java
// PolicySearchPSI.java (예시)
@GetMapping("/policy/search")
public String searchPolicy(
        @ModelAttribute SearchVO searchVO,
        @RequestParam(defaultValue = "1") int page,          // 현재 페이지 (1‑based)
        @RequestParam(defaultValue = "10") int size,        // 페이지당 건수
        Model model) {

    // 1) 서비스에 페이지·사이즈 전달
    SearchResult result = policySearchService.search(searchVO, page, size);

    // 2) 모델에 필요한 값 셋팅
    model.addAttribute("searchVO", searchVO);
    model.addAttribute("resultList", result.getList());   // 현재 페이지 데이터
    model.addAttribute("totalCount", result.getTotalCount()); // 전체 건수
    model.addAttribute("pageSize", size);
    model.addAttribute("currentPage", page);
    model.addAttribute("searchExecuted", true);

    log.info("[PSI] 증권조회 결과 건수: {}", result.getTotalCount());

    return "policySearch";
}
```

### (2) Service – 전체 건수와 페이지 데이터 분리  

```java
public class SearchResult {
    private List<PolicySearchResultVO> list;   // 현재 페이지 데이터
    private int totalCount;                    // 전체 건수
    // getters / setters
}

public SearchResult search(SearchVO vo, int page, int size) {
    int offset = (page - 1) * size;

    // ① 전체 건수 조회
    int total = policyRepository.countByCriteria(vo);

    // ② 페이지에 해당하는 데이터 조회
    List<PolicySearchResultVO> pageData = policyRepository.findByCriteria(vo, offset, size);

    SearchResult sr = new SearchResult();
    sr.setTotalCount(total);
    sr.setList(pageData);
    return sr;
}
```

### (3) View (Thymeleaf 예시) – 페이지 네비게이션 표시  

```html
<!-- totalCount 와 pageSize 로 페이지 수 계산 -->
<div>
    <p>총 <span th:text="${totalCount}"></span>건 중
       <span th:text="${currentPage}"></span> 페이지 표시 (1 페이지당 <span th:text="${pageSize}"></span>건)
    </p>
</div>

<table>
    <tr th:each="item : ${resultList}">
        <!-- 컬럼 출력 -->
    </tr>
</table>

<!-- 페이지 이동 링크 -->
<div class="pagination">
    <a th:if="${currentPage > 1}"
       th:href="@{/policy/search(page=${currentPage-1}, size=${pageSize})}">이전</a>

    <span th:each="i : ${#numbers.sequence(1, (totalCount / pageSize) + 1)}">
        <a th:classappend="${i == currentPage} ? 'active' : ''"
           th:href="@{/policy/search(page=${i}, size=${pageSize})}"
           th:text="${i}">1</a>
    </span>

    <a th:if="${currentPage < (totalCount / pageSize) + 1}"
       th:href="@{/policy/search(page=${currentPage+1}, size=${pageSize})}">다음</a>
</div>
```

### (4) `application.yml` – 페이지 사이즈 외부화  

```yaml
search:
  pageSize: 10
```

```java
@Value("${search.pageSize}")
private int defaultPageSize;
```

---

## 5️⃣ 예방 방법  

| 예방 조치 | 설명 |
|----------|------|
| **페이징 로직 표준화** | 서비스·DAO·Controller·View 모두 동일한 `page`, `size` 개념을 사용하도록 인터페이스·DTO를 정의하고, 팀 차원에서 가이드라인을 만든다. |
| **DTO/VO 명명 규칙** | `totalCount` → “전체 건수”, `pageSize` → “페이지당 건수”, `currentPage` → “현재 페이지” 등 명확히 구분한다. |
| **파라미터 검증** | `page`·`size` 가 누락되거나 비정상적인 값(음수, 0, 너무 큰 값)일 경우 기본값을 적용하고, 로그·예외로 남긴다. |
| **자동화 테스트** | **전체 건수 > 페이지 사이즈**, **페이지 파라미터 미전달**, **마지막 페이지 초과** 등 다양한 시나리오를 포함한 테스트 케이스를 CI에 추가한다. |
| **로그·모니터링** | `totalCount` 와 `resultList.size()` 를 함께 로그에 남겨, “표시 건수와 전체 건수 불일치”가 감지되면 알림을 발생시킨다. |
| **UI/UX 검증** | 화면에 “총 X건 중 Y~Z건 표시”와 같은 명시적인 문구를 넣어 사용자가 현재 보고 있는 범위를 명확히 알 수 있게 한다. |
| **설정값 외부화** | 페이지 사이즈·기본 페이지 번호 등을 `application.yml`·`properties` 로 관리해, 코드 변경 없이 운영 환경에 맞게 조정한다. |

---

### 정리  

- **근본 원인**은 서버‑클라이언트 간 페이징 정보(전체 건수 vs. 현재 페이지 데이터) 불일치이며, `totalCount`는 전체 건수를, `resultList`는 현재 페이지 데이터만 담고 있기 때문에 발생합니다.  
- **영향**은 사용자 경험 저하와 데이터 신뢰성 손상으로, 특히 금융·보험 서비스에서는 높은 위험을 초래합니다.  
- **해결**은 컨트롤러·서비스·뷰에서 페이지 파라미터를 명시적으로 처리하고, 페이지 네비게이션 UI를 제공하는 것이 가장 급선무이며, 이후 코드 정리·테스트·설정 외부화 등을 차례로 진행합니다.  
- **예방**은 페이징 로직을 표준화하고, 파라미터 검증·자동화 테스트·로그 모니터링을 체계화하는 것이 핵심입니다.  

위 내용대로 검토·수정 후, 충분한 테스트를 거치면 현재 “10건만 표시되는” 현상이 해소되고, 전체 18건을 정확히 조회·표시할 수 있게 됩니다. 🚀

---

## ⚠️ 안전성 공지

- ✅ AI는 소스코드 파일을 **절대 수정하지 않습니다**
- ✅ 이 리포트는 **참고 자료**입니다
- ✅ 개발자가 검토 후 수동으로 적용하세요
- ✅ RAG 검색 결과는 유사도 기반이므로 정확하지 않을 수 있습니다
