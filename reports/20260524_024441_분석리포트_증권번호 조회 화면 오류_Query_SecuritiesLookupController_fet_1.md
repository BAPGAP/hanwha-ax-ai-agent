# 🤖 AI 에러 분석 리포트 (RAG 기반)

**생성 시간**: 2026-05-24 02:44:41  
**원본 이메일**: 증권번호 조회 화면 오류.eml  
**LLM**: groq (compound-beta)  
**검색 방법**: RAG (Retrieval-Augmented Generation)

---

## 📧 에러 정보

- **오류 요약**: 증권번호 조회 화면에서 전체 조회를 누를 때 조회 결과에 10건만 표시되고 총 18건이라고 표시되는 오류가 발생했습니다. 이로 인해 사용자는 전체 데이터를 확인하지 못하고 있습니다.
- **심각도**: HIGH

---

## 🔎 RAG 검색 결과

**검색 쿼리**: `SecuritiesLookupController fetchAllResults`

### 1. PolicySearchMapper.java (유사도: 59.43%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\mapper\PolicySearchMapper.java`
- **청크 ID**: 3

```java
/**
     * 증권 목록 조회
     * SQL ID: selectPolicyList
     *
     * @param searchVO 조회조건 VO
     * @return 증권 목록
     */
    List<PolicySearchResultVO> selectPolicyList(PolicySearchVO searchVO);

    /**
     * 증권 단건 상세 조회
     * SQL ID: selectPolicyDetail
     *
     * @param policyNo 증권번호
     * @return 증권 상세 정보
     */
    PolicySearchResultVO selectPolicyDetail(String policyNo);
}
```

### 2. PolicySearchDSI.java (유사도: 58.89%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\dsi\PolicySearchDSI.java`
- **청크 ID**: 2

```java
* =====================================================================
 */
public interface PolicySearchDSI {
```

### 3. PolicySearchDSIImpl.java (유사도: 57.88%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\dsi\impl\PolicySearchDSIImpl.java`
- **청크 ID**: 5

```java
log.info("[DSI] 증권목록 조회 완료 - 조회 건수: {}", resultList.size());
        return resultList;
    }

    /**
     * 증권 단건 상세 조회
     */
    @Override
    public PolicySearchResultVO selectPolicyDetail(String policyNo) {
        log.info("[DSI] 증권상세 조회 - 증권번호: {}", policyNo);

        PolicySearchResultVO result = policySearchMapper.selectPolicyDetail(policyNo);

        if (result != null) {
            applyPrivacyMasking(result);
        }

        return result;
    }
```

---

## 🤖 AI 분석

❌ Groq API HTTP 오류: 413 Client Error: Payload Too Large for url: https://api.groq.com/openai/v1/chat/completions

---

## ⚠️ 안전성 공지

- ✅ AI는 소스코드 파일을 **절대 수정하지 않습니다**
- ✅ 이 리포트는 **참고 자료**입니다
- ✅ 개발자가 검토 후 수동으로 적용하세요
- ✅ RAG 검색 결과는 유사도 기반이므로 정확하지 않을 수 있습니다
