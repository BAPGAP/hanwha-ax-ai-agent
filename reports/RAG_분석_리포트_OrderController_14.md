# 🤖 AI 에러 분석 리포트 (RAG 기반)

**생성 시간**: 2026-05-23 18:25:53  
**원본 이메일**: sample_error.txt  
**LLM**: ollama (qwen2.5:7b)  
**검색 방법**: RAG (Retrieval-Augmented Generation)

---

## 📧 에러 정보

- **클래스**: `OrderController`
- **메서드**: `createOrder()`
- **라인**: 67

---

## 🔎 RAG 검색 결과

**검색 쿼리**: `OrderController createOrder`

### 1. OrderController.java (유사도: -26.90%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\src\com\hanwha\ax\controller\OrderController.java`
- **청크 ID**: 1

```java
/**
 * 주문 처리 컨트롤러
 */
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @Autowired
    private CustomerService customerService;
    
    /**
     * 새 주문 생성
     */
    @PostMapping("/create")
    public Order createOrder(@RequestBody OrderRequest request) {
        // 고객 정보 조회
        Customer customer = new Customer();
        customer.setId(request.getCustomerId());
        customer.setName(request.getCustomerName());
```

### 2. Order.java (유사도: -34.29%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\src\com\hanwha\ax\model\Order.java`
- **청크 ID**: 1

```java
/**
 * 주문 정보 모델
 */
public class Order {
    private String orderId;
    private String customerId;
    private String productId;
    private Integer quantity;
    private String status;
    
    public String getOrderId() {
        return orderId;
    }
    
    public void setOrderId(String orderId) {
        this.orderId = orderId;
    }
    
    public String getCustomerId() {
        return customerId;
    }
    
    public void setCustomerId(String customerId) {
```

### 3. OrderController.java (유사도: -35.10%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\src\com\hanwha\ax\controller\OrderController.java`
- **청크 ID**: 0

```java
package com.hanwha.ax.controller;

import com.hanwha.ax.model.Customer;
import com.hanwha.ax.model.Order;
import com.hanwha.ax.service.CustomerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
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
