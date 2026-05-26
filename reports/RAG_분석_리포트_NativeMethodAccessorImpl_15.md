# 🤖 AI 에러 분석 리포트 (RAG 기반)

**생성 시간**: 2026-05-23 18:25:57  
**원본 이메일**: sample_error.txt  
**LLM**: ollama (qwen2.5:7b)  
**검색 방법**: RAG (Retrieval-Augmented Generation)

---

## 📧 에러 정보

- **클래스**: `NativeMethodAccessorImpl`
- **메서드**: `invoke()`
- **라인**: 62

---

## 🔎 RAG 검색 결과

**검색 쿼리**: `NativeMethodAccessorImpl invoke`

### 1. CustomerService.java (유사도: -46.84%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\src\com\hanwha\ax\service\CustomerService.java`
- **청크 ID**: 0

```java
package com.hanwha.ax.service;

import com.hanwha.ax.model.Customer;
import com.hanwha.ax.model.Order;
import org.springframework.stereotype.Service;
```

### 2. PolicySearchVO.java (유사도: -55.05%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\vo\PolicySearchVO.java`
- **청크 ID**: 0

```java
package com.hanwha.ax.vo;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

/**
 * 증권조회 검색조건 VO
 * 화면에서 입력받는 조회 파라미터를 담는 객체
 */
@Getter
@Setter
@ToString
public class PolicySearchVO {

    /** 증권번호 */
    private String policyNo;

    /** 고객명 */
    private String customerName;

    /** 고객 주민등록번호 (앞 6자리만 입력 가능) */
    private String customerRrn;

    /** 페이지 번호 (기본값 1) */
    private int pageNo = 1;

    /** 페이지당 건수 (기본값 10) */
    private int pageSize = 10;
}
```

### 3. PolicySearchDSIImpl.java (유사도: -55.13%)

- **경로**: `C:\Users\kas12\OneDrive\바탕 화면\한화AX\hanwha-ax-ai-agent\example_project\policy-search-demo\src\main\java\com\hanwha\ax\dsi\impl\PolicySearchDSIImpl.java`
- **청크 ID**: 0

```java
package com.hanwha.ax.dsi.impl;

import com.hanwha.ax.dsi.PolicySearchDSI;
import com.hanwha.ax.mapper.PolicySearchMapper;
import com.hanwha.ax.vo.PolicySearchResultVO;
import com.hanwha.ax.vo.PolicySearchVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
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
