# 🤖 AI 에러 분석 리포트 (RAG 기반)

**생성 시간**: 2026-05-23 18:26:17  
**원본 이메일**: sample_error.txt  
**LLM**: ollama (qwen2.5:7b)  
**검색 방법**: RAG (Retrieval-Augmented Generation)

---

## 📧 에러 정보

- **클래스**: `ServletInvocableHandlerMethod`
- **메서드**: `invokeAndHandle()`
- **라인**: 105

---

## 🔎 RAG 검색 결과

**검색 쿼리**: `ServletInvocableHandlerMethod invokeAndHandle`

### 1. OrderController.java (유사도: -33.30%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\src\com\hanwha\ax\controller\OrderController.java`
- **청크 ID**: 2

```java
customer.setEmail(request.getCustomerEmail());
        
        // 주문 생성
        Order order = new Order();
        order.setProductId(request.getProductId());
        order.setQuantity(request.getQuantity());
        
        // 주문 처리 - Line 67에서 CustomerService 호출
        return customerService.processCustomerOrder(customer, order);
    }
    
    /**
     * 주문 제출
     */
    @PostMapping("/submit")
    public Order submitOrder(@RequestBody Order order) {
        // 주문 제출 로직
```

### 2. PolicySearchPSI.java (유사도: -35.89%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\psi\PolicySearchPSI.java`
- **청크 ID**: 0

```java
package com.hanwha.ax.psi;

import com.hanwha.ax.dsi.PolicySearchDSI;
import com.hanwha.ax.vo.PolicySearchResultVO;
import com.hanwha.ax.vo.PolicySearchVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
```

### 3. OrderController.java (유사도: -38.14%)

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
