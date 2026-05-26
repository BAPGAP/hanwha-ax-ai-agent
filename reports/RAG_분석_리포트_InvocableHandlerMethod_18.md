# 🤖 AI 에러 분석 리포트 (RAG 기반)

**생성 시간**: 2026-05-23 18:26:09  
**원본 이메일**: sample_error.txt  
**LLM**: ollama (qwen2.5:7b)  
**검색 방법**: RAG (Retrieval-Augmented Generation)

---

## 📧 에러 정보

- **클래스**: `InvocableHandlerMethod`
- **메서드**: `doInvoke()`
- **라인**: 190

---

## 🔎 RAG 검색 결과

**검색 쿼리**: `InvocableHandlerMethod doInvoke`

### 1. Order.java (유사도: -51.40%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\src\com\hanwha\ax\model\Order.java`
- **청크 ID**: 3

```java
public void setStatus(String status) {
        this.status = status;
    }
}
```

### 2. CustomerService.java (유사도: -51.42%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\src\com\hanwha\ax\service\CustomerService.java`
- **청크 ID**: 1

```java
/**
 * 고객 정보 처리 서비스
 */
@Service
public class CustomerService {
    
    /**
     * 고객 주문 처리
     */
    public Order processCustomerOrder(Customer customer, Order order) {
        System.out.println("Processing order for customer: " + customer.getId());
        
        // 고객 데이터 검증
        validateCustomerData(customer);
        
        // 주문 처리 로직
        order.setStatus("PROCESSING");
        order.setCustomerId(customer.getId());
        
        return order;
    }
    
    /**
```

### 3. PolicySearchDSIImpl.java (유사도: -57.91%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\dsi\impl\PolicySearchDSIImpl.java`
- **청크 ID**: 6

```java
return result;
    }

    /**
     * 개인정보 마스킹 처리
     * - 주민등록번호: 앞 6자리 표시 후 뒷 7자리 * 처리
     * 예: 900101-1234567 → 900101-*******
     */
    private void applyPrivacyMasking(PolicySearchResultVO vo) {
        String rawRrn = vo.getCustomerRrnMasked();
        if (rawRrn == null || rawRrn.trim().isEmpty()) return;
```

---

## 🤖 AI 분석

❌ Ollama 서버에 연결할 수 없습니다. `ollama serve` 실행 확인 필요.

---

## ⚠️ 안전성 공지

- ✅ AI는 소스코드 파일을 **절대 수정하지 않습니다**
- ✅ 이 리포트는 **참고 자료**입니다
- ✅ 개발자가 검토 후 수동으로 적용하세요
- ✅ RAG 검색 결과는 유사도 기반이므로 정확하지 않을 수 있습니다
