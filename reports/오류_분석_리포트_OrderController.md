# 🐛 에러 분석 리포트: OrderController

**생성 일시**: 2026-05-22 00:56:09
**분석 모델**: mock-model
**출처**: sample_error.txt

---

## 📋 발생한 Exception

- **java.lang.NullPointerException**
  - Cannot invoke "String.length()" because "customerName" is null

## 📍 에러 발생 위치

- **파일**: `example_project\src\com\hanwha\ax\service\CustomerService.java`
- **클래스**: `CustomerService`
- **메서드**: `validateCustomerData()`
- **라인**: 145

- **파일**: `example_project\src\com\hanwha\ax\service\CustomerService.java`
- **클래스**: `CustomerService`
- **메서드**: `processCustomerOrder()`
- **라인**: 89

- **파일**: `example_project\src\com\hanwha\ax\controller\OrderController.java`
- **클래스**: `OrderController`
- **메서드**: `createOrder()`
- **라인**: 67

---

## 🔍 AI 분석 결과


## 1. 에러 원인 분석

**근본 원인**: Null Pointer Exception이 발생한 이유는 `customerName` 변수가 `null`인 상태에서 `.length()` 메서드를 호출했기 때문입니다.

코드를 보면:
```java
String customerName = customer.getName();
if (customerName.length() < 2) {  // ← 여기서 에러 발생
```

`customer.getName()`이 `null`을 반환할 수 있는데, null 체크 없이 바로 `.length()`를 호출하여 NullPointerException이 발생했습니다.

## 2. 문제가 되는 코드

```java
// 문제의 코드
String customerName = customer.getName();
if (customerName.length() < 2) {  // ❌ null 체크 없음
    throw new IllegalArgumentException("Customer name must be at least 2 characters");
}
```

**문제점**:
- `getName()`이 `null`을 반환할 가능성을 고려하지 않음
- Null 체크 없이 바로 메서드 호출
- 방어적 프로그래밍 원칙 위반

## 3. 수정 방법

**방법 1: Null 체크 추가** (권장)
```java
String customerName = customer.getName();
if (customerName == null || customerName.isEmpty()) {
    throw new IllegalArgumentException("Customer name is required");
}
if (customerName.length() < 2) {
    throw new IllegalArgumentException("Customer name must be at least 2 characters");
}
```

**방법 2: Optional 사용** (Java 8+)
```java
String customerName = Optional.ofNullable(customer.getName())
    .orElseThrow(() -> new IllegalArgumentException("Customer name is required"));
if (customerName.length() < 2) {
    throw new IllegalArgumentException("Customer name must be at least 2 characters");
}
```

## 4. 수정된 코드 예시

```java
/**
 * 고객 데이터 유효성 검증 (개선 버전)
 */
public void validateCustomerData(Customer customer) {
    // 고객 ID 검증
    if (customer.getId() == null || customer.getId().isEmpty()) {
        throw new IllegalArgumentException("Customer ID is required");
    }
    
    // 고객 이름 검증 - Null 체크 추가 ✅
    String customerName = customer.getName();
    if (customerName == null || customerName.trim().isEmpty()) {
        throw new IllegalArgumentException("Customer name is required");
    }
    if (customerName.trim().length() < 2) {
        throw new IllegalArgumentException("Customer name must be at least 2 characters");
    }
    
    // 이메일 검증
    String email = customer.getEmail();
    if (email == null || !email.contains("@")) {
        throw new IllegalArgumentException("Valid email is required");
    }
}
```

**주요 개선사항**:
- ✅ Null 체크 추가
- ✅ `trim()` 사용하여 공백 제거
- ✅ 명확한 에러 메시지

## 5. 추가 권장 사항

### Bean Validation 사용 권장
```java
import javax.validation.constraints.*;

public class Customer {
    @NotBlank(message = "Customer name is required")
    @Size(min = 2, message = "Customer name must be at least 2 characters")
    private String name;
    
    @NotBlank(message = "Email is required")
    @Email(message = "Valid email is required")
    private String email;
}
```

### 유닛 테스트 추가
```java
@Test
public void testValidateCustomerData_NullName() {
    Customer customer = new Customer();
    customer.setId("123");
    customer.setName(null);  // Null 케이스
    customer.setEmail("test@example.com");
    
    assertThrows(IllegalArgumentException.class, 
        () -> customerService.validateCustomerData(customer));
}
```

### 로깅 추가
```java
if (customerName == null || customerName.trim().isEmpty()) {
    log.warn("Validation failed: Customer name is null or empty for customer ID: {}", 
             customer.getId());
    throw new IllegalArgumentException("Customer name is required");
}
```

### 방어적 코딩 체크리스트
- [ ] 모든 외부 입력값에 대해 null 체크
- [ ] 메서드 파라미터에 `@NonNull` 어노테이션 사용
- [ ] 빈 문자열과 null을 모두 고려
- [ ] 적절한 예외 메시지 작성


---

## ⚠️ 중요 공지


이 리포트는 AI가 생성한 분석 결과입니다.

**주의사항**:
- 이 리포트는 참고용이며, 실제 수정 전 반드시 개발자가 검토해야 합니다.
- AI가 기존 소스코드 파일을 직접 수정하지 않았습니다.
- 제안된 코드를 적용하기 전 충분한 테스트를 수행하세요.
- 프로젝트의 코딩 컨벤션과 아키텍처를 고려하여 적용하세요.

**다음 단계**:
1. 이 리포트를 팀과 공유하여 검토
2. 제안된 수정 방법을 프로젝트에 맞게 조정
3. 수정 후 단위 테스트 및 통합 테스트 실시
4. 코드 리뷰 후 배포
