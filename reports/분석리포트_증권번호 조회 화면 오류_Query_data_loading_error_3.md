# 🤖 AI 에러 분석 리포트 (RAG 기반)

**생성 시간**: 2026-05-24 02:10:26  
**원본 이메일**: 증권번호 조회 화면 오류.eml  
**LLM**: groq (compound-beta)  
**검색 방법**: RAG (Retrieval-Augmented Generation)

---

## 📧 에러 정보

- **오류 요약**: 증권번호 조회 화면에서 전체 조회 시 조회 결과에 10건만 표시되고, 총 18건이라고 표시되는 오류가 발생했습니다. 이 오류로 인해 사용자가 정확한 조회 결과를 확인하는데 문제가 있습니다.
- **심각도**: HIGH

---

## 🔎 RAG 검색 결과

**검색 쿼리**: `data loading error`

### 1. PolicySearchDSIImpl.java (유사도: 57.71%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\dsi\impl\PolicySearchDSIImpl.java`
- **청크 ID**: 1

```java
/**
 * =====================================================================
 * [DSI Impl] Data Service Interface 구현체 - 증권조회 서비스
 * =====================================================================
 *
 * 역할:
 *   - PolicySearchDSI 인터페이스의 실제 업무 로직 구현
 *   - MyBatis Mapper를 호출하여 DB 데이터 조회
 *   - 필요 시 여러 Mapper 호출 결과를 조합하는 오케스트레이션 수행
 *   - 주민번호 마스킹 등 개인정보 보호 처리
 *
 * 계층 구조:
 *   PSI → DSI → [DSI Impl] → MyBatis Mapper → DB
```

### 2. PolicySearchDSI.java (유사도: 57.00%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\dsi\PolicySearchDSI.java`
- **청크 ID**: 1

```java
/**
 * =====================================================================
 * [DSI] Data Service Interface - 증권조회 서비스 인터페이스
 * =====================================================================
 *
 * 역할:
 *   - PSI(컨트롤러)와 데이터 접근 계층(MyBatis Mapper) 사이의 인터페이스 정의
 *   - 업무 로직(비즈니스 규칙)을 캡슐화하는 서비스 계층의 계약(Contract)
 *   - 구현체(PolicySearchDSIImpl)와 분리하여 의존성 역전 원칙(DIP) 적용
 *
 * 계층 구조:
 *   PSI → [DSI Interface] → DSI Impl → MyBatis → DB
```

### 3. PolicySearchApplication.java (유사도: 55.85%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\PolicySearchApplication.java`
- **청크 ID**: 1

```java
/**
 * 한화AX 증권조회 데모 애플리케이션
 *
 * 계층 구조:
 *   화면 (Thymeleaf HTML)
 *     ↓
 *   PSI - Presentation Service Interface (Controller)
 *     ↓
 *   DSI - Data Service Interface (Service)
 *     ↓
 *   MyBatis Mapper (SQL)
 *     ↓
 *   DB (H2 In-Memory)
 */
@SpringBootApplication
@MapperScan("com.hanwha.ax.mapper")
public class PolicySearchApplication {

    public static void main(String[] args) {
        SpringApplication.run(PolicySearchApplication.class, args);
    }
}
```

---

## 🤖 AI 분석

## 1️⃣ 원인 분석  

| 가능성 | 설명 | 근거 |
|--------|------|------|
| **① 페이지네이션(페이징) 로직 오류** | 전체 조회 시 “전체 건수(18건)”는 DB에서 `COUNT(*)` 로 구했지만, 실제 데이터를 가져오는 쿼리에서는 `LIMIT 10` 혹은 `ROWNUM ≤ 10` 과 같은 제한이 남아 있어 첫 페이지에 10건만 반환한다. | 화면에 “총 18건”이 표시되면서도 리스트에 10건만 보이는 전형적인 페이징 불일치 현상. |
| **② MyBatis Mapper‑SQL 오류** | `selectPolicyList` 와 `selectPolicyCount` 가 서로 다른 조건(예: WHERE 절, JOIN) 을 사용해 결과가 일치하지 않는다. 특히 `WHERE` 절에 `deleted = false` 같은 필터가 하나에만 적용돼 전체 건수와 실제 데이터가 달라질 수 있다. | `PolicySearchDSIImpl` 은 여러 Mapper 를 조합한다는 주석이 있으므로, 하나의 Mapper에서만 조건이 빠졌을 가능성이 있음. |
| **③ 서비스 로직에서 결과 조합 실수** | `PolicySearchDSIImpl` 내부에서 `List` 를 잘라서 반환하거나, `PageInfo` 객체에 `total` 은 카운트 결과를 넣고 `list` 에는 페이지 처리된 서브리스트만 넣는 과정에서 `total` 과 `list.size()` 가 일치하지 않게 된다. | “전체 조회” 라는 UI 요구사항을 구현하면서 “전체 → 페이지” 로직을 별도로 구현했을 때 흔히 발생하는 실수. |
| **④ 프론트엔드(Thymeleaf) 페이지네이션 UI 버그** | 백엔드에서 전체 리스트를 반환했지만, 프론트엔드에서 `th:each` 로 10개까지만 반복하도록 제한했을 가능성. 하지만 “전체 조회” 버튼을 눌렀을 때 백엔드가 페이지 파라미터를 `0` 혹은 `null` 로 전달하지 않아 기본값(10) 이 적용될 수 있다. | UI와 백엔드 파라미터 전달 불일치가 원인일 경우도 존재. |

> **핵심 메커니즘**  
전체 건수(`totalCount`)와 실제 반환된 레코드(`resultList`)가 서로 다른 로직·쿼리·파라미터에 의해 산출되면서, UI는 `totalCount` 를 그대로 표시하고 `resultList` 를 그대로 출력하게 되므로 “총 18건 → 10건만 표시” 라는 불일치가 발생합니다.

---

## 2️⃣ 영향 범위  

| 영역 | 영향 | 심각도 |
|------|------|--------|
| **사용자 경험** | 조회 결과가 불완전하게 보여 신뢰도 저하 및 업무 처리 지연 | ★★★★★ (HIGH) |
| **비즈니스 로직** | 정확한 증권 번호 확인이 필요한 업무(예: 계약 검증, 청구)에서 오류 발생 가능 | ★★★★☆ |
| **통계·보고** | 전체 건수와 실제 데이터 불일치 → 잘못된 보고서·통계 생성 | ★★★★☆ |
| **시스템 부하** | 페이지당 10건만 반환하므로 실제 필요 데이터가 많을 경우 추가 호출이 발생 → API 호출량 증가 | ★★☆☆☆ |
| **법·규제** | 개인정보(주민번호 등) 마스킹 로직이 정상 동작하더라도, 데이터 누락이 규제 위반으로 이어질 가능성은 낮음 | ★★☆☆☆ |

---

## 3️⃣ 해결 방법 (우선순위)

1. **페이징 파라미터 검증 및 통합**  
   * `PolicySearchDSIImpl` 에서 `pageSize`, `pageNumber` 가 `null` 혹은 `0` 일 때 **전체 조회** 로 처리하도록 로직을 명확히 함.  
   * `LIMIT` / `OFFSET` 을 적용하는 MyBatis 쿼리에서 `pageSize` 가 `null` 이면 제한을 두지 않도록 `IF` 구문을 추가.

2. **카운트와 리스트 쿼리 조건 일치 시키기**  
   * `selectPolicyCount` 와 `selectPolicyList` 가 동일한 `WHERE` 절을 공유하도록 Mapper XML 혹은 어노테이션에 공통 `WHERE` 절을 정의.  
   * 예: `<sql id="policyBaseWhere">WHERE deleted = false AND status = #{status}</sql>` 을 두 쿼리 모두 `include`.

3. **서비스 레이어에서 `PageInfo`(또는 DTO) 구성 검증**  
   * `totalCount` 와 `list` 를 설정할 때, `list` 가 실제 전체 리스트(필터링 후)인지, 페이지 처리된 서브리스트인지 명확히 구분.  
   * 전체 조회 시 `list` 에는 **전체** 데이터를 넣고, UI에서 페이지네이션을 담당하도록 설계 변경.

4. **프론트엔드 파라미터 전달 점검**  
   * Thymeleaf 혹은 JavaScript 에서 `pageSize` 를 명시적으로 전달하거나, “전체 조회” 버튼 클릭 시 `pageSize=0` 혹은 `pageSize=null` 로 전송하도록 수정.  
   * UI에서 `th:if="${pageSize == 0}"` 와 같은 조건을 추가해 전체 리스트를 렌더링.

5. **테스트·검증**  
   * **단위 테스트** : `PolicySearchDSIImpl.getPolicies(page, size)` 에 대해 `size=null` 일 때 전체 18건이 반환되는지 검증.  
   * **통합 테스트** : 컨트롤러 → 서비스 → Mapper 흐름 전체를 실행해 `totalCount` 와 `resultList.size()` 가 일치하는지 확인.  
   * **UI 테스트** : 전체 조회 버튼 클릭 후 페이지에 표시되는 건수가 `totalCount` 와 동일한지 자동화 테스트(예: Selenium) 추가.

---

## 4️⃣ 참고 코드 (수정 예시)

> **※ 아래 코드는 참고용이며, 실제 파일에 바로 적용하지 말고 검토 후 적용하세요.**

### ① MyBatis Mapper (XML) – 조건 공유 & 페이지네이션 옵션

```xml
<!-- 공통 WHERE 절 정의 -->
<sql id="policyBaseWhere">
  WHERE deleted = false
    AND status = #{status}
</sql>

<!-- 전체 건수 조회 -->
<select id="selectPolicyCount" resultType="int">
  SELECT COUNT(*) FROM policy
  <include refid="policyBaseWhere"/>
</select>

<!-- 리스트 조회 (페이지네이션 적용) -->
<select id="selectPolicyList" resultMap="PolicyResultMap">
  SELECT *
  FROM policy
  <include refid="policyBaseWhere"/>
  <if test="pageSize != null and pageSize > 0">
    ORDER BY created_at DESC
    LIMIT #{pageSize} OFFSET #{offset}
  </if>
</select>
```

### ② Service Impl – 파라미터 처리 로직

```java
@Service
public class PolicySearchDSIImpl implements PolicySearchDSI {

    @Autowired private PolicyMapper policyMapper;

    @Override
    public PolicySearchResult search(String status, Integer pageNumber, Integer pageSize) {
        // 전체 조회(페이지 사이즈가 null 혹은 0) 처리
        boolean isAll = (pageSize == null || pageSize <= 0);
        int total = policyMapper.selectPolicyCount(status);

        List<Policy> list;
        if (isAll) {
            // 전체 데이터를 한 번에 조회 (필요 시 스트리밍)
            list = policyMapper.selectPolicyList(status, null, null);
        } else {
            int offset = (pageNumber - 1) * pageSize;
            list = policyMapper.selectPolicyList(status, pageSize, offset);
        }

        return new PolicySearchResult(total, list);
    }
}
```

### ③ DTO 예시

```java
public class PolicySearchResult {
    private final int totalCount;
    private final List<Policy> policies;

    public PolicySearchResult(int totalCount, List<Policy> policies) {
        this.totalCount = totalCount;
        this.policies = policies;
    }
    // getters …
}
```

### ④ Thymeleaf – 전체 조회 버튼 파라미터

```html
<form th:action="@{/policy/search}" method="get">
    <input type="hidden" name="status" th:value="${status}" />
    <!-- 전체 조회: pageSize=0 -->
    <button type="submit" name="pageSize" value="0">전체 조회</button>
    <!-- 페이지별 조회 -->
    <button type="submit" name="pageSize" value="10">10건씩 보기</button>
</form>
```

---

## 5️⃣ 예방 방법  

| 방안 | 구체적 내용 |
|------|-------------|
| **① 표준화된 페이징 인터페이스 도입** | `PageRequest`(page, size) 객체를 모든 서비스·Mapper에 동일하게 전달하고, `size <= 0` 은 “전체 조회” 로 해석하도록 계약을 명시. |
| **② 쿼리 재사용** | `WHERE` 절을 별도 `<sql>` 로 정의해 카운트와 리스트 쿼리가 언제든 동일하게 유지되도록 함. |
| **③ 자동화 테스트** | - **단위 테스트** : `PolicySearchDSIImpl` 의 `search` 메서드에 대해 다양한 `pageSize`(null, 0, 10) 테스트.<br>- **통합 테스트** : SpringBootTest 로 컨트롤러 → 서비스 → DB 흐름 검증.<br>- **E2E 테스트** : Selenium/Playwright 로 UI 전체 조회 버튼 클릭 후 리스트 건수 검증. |
| **④ 로깅·모니터링** | 서비스 레이어에서 `totalCount`, `pageSize`, `resultSize` 를 INFO 레벨에 로깅하고, `totalCount != resultSize` 가 감지되면 알림을 발생시킴. |
| **⑤ 코드 리뷰 체크리스트** | - “전체 건수와 반환 리스트 크기가 일치하는가?”<br>- “페이지 파라미터가 null/0 일 때 전체 조회 로직이 존재하는가?”<br>- “Mapper 쿼리에서 동일한 WHERE 절을 사용하고 있는가?” |
| **⑥ 문서화** | API 스펙에 **전체 조회** 파라미터(`pageSize=0` 혹은 `null`) 를 명시하고, 기대 동작을 문서에 기록. |

---

### 정리  

* **근본 원인**은 페이지네이션 파라미터와 DB 쿼리·서비스 로직 간 불일치(특히 전체 조회 시 `LIMIT` 가 남아 있음) 입니다.  
* **영향**은 사용자 신뢰도 저하와 업무 효율성 감소이며, 통계·보고에도 오류를 초래할 수 있습니다.  
* **해결**은 파라미터 검증·통합, 쿼리 조건 일치, 서비스 레이어에서 전체/페이지 데이터를 명확히 구분하는 로직을 적용하고, UI와 백엔드 간 파라미터 전달을 일관되게 만드는 것입니다.  
* **예방**은 표준화된 페이징 인터페이스, 쿼리 재사용, 자동화 테스트·모니터링·코드 리뷰, 그리고 명확한 API 문서화로 달성할 수 있습니다.  

위 내용을 바탕으로 해당 모듈을 점검하고, 필요한 부분을 단계적으로 개선하면 현재 발생한 “총 18건 → 10건만 표시” 문제를 해결할 수 있습니다. 🚀

---

## ⚠️ 안전성 공지

- ✅ AI는 소스코드 파일을 **절대 수정하지 않습니다**
- ✅ 이 리포트는 **참고 자료**입니다
- ✅ 개발자가 검토 후 수동으로 적용하세요
- ✅ RAG 검색 결과는 유사도 기반이므로 정확하지 않을 수 있습니다
