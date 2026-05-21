"""
[3단계] 원인 분석 및 수정 제안 리포트 생성

2단계에서 추출한 에러 로그 + 소스코드를 LLM에 전달하여
원인 분석 및 수정 제안을 담은 마크다운 리포트 생성

지원하는 LLM:
- Ollama (로컬 실행) - Qwen2.5-7B-Instruct 등
- OpenAI API
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import requests


class AnalysisReportGenerator:
    """LLM을 사용하여 에러 분석 리포트를 생성하는 클래스"""
    
    # 시스템 프롬프트 - 엄격한 가이드라인 포함
    SYSTEM_PROMPT = """당신은 Java 코드 에러 분석 전문가입니다.

당신의 역할:
1. 제공된 에러 로그와 Java 소스코드를 철저히 분석하여 근본 원인을 명확히 파악합니다.
2. 문제의 원인을 단계별로 설명하고, 안전한 수정 가이드라인을 제시합니다.
3. 수정된 Java 코드 예시를 제공합니다.

⚠️ 절대 금지 사항:
- 기존 Java 소스코드 파일을 직접 수정하거나 덮어쓰는 행위는 절대 금지됩니다.
- 파일 시스템에 직접 접근하거나 파일을 생성/수정하지 마십시오.
- 오직 분석 결과와 권장 사항을 텍스트로 제공하는 것만 허용됩니다.

출력 형식:
- 명확하고 구조화된 마크다운 형식으로 작성
- 원인 분석, 문제점, 수정 방법, 코드 예시를 포함
- 개발자가 쉽게 이해하고 적용할 수 있도록 작성"""

    def __init__(self, 
                 llm_type: str = "ollama",
                 model_name: str = "qwen2.5:7b",
                 api_base_url: str = "http://localhost:11434",
                 api_key: Optional[str] = None,
                 use_mock: bool = False):
        """
        Args:
            llm_type: LLM 타입 ("ollama", "openai", 또는 "mock")
            model_name: 모델 이름
                - Ollama: "qwen2.5:7b", "llama3", "codellama" 등
                - OpenAI: "gpt-4", "gpt-3.5-turbo" 등
                - Mock: "demo"
            api_base_url: API 베이스 URL
                - Ollama: "http://localhost:11434"
                - OpenAI: "https://api.openai.com/v1"
            api_key: API 키 (OpenAI 사용 시 필요)
            use_mock: Mock 모드 사용 여부 (Ollama 없이 테스트용)
        """
        self.llm_type = "mock" if use_mock else llm_type.lower()
        self.model_name = model_name
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        
        if self.llm_type == "mock":
            print(f"🎭 Mock 모드: 데모용 분석 생성 (실제 LLM 호출 없음)")
        else:
            print(f"🤖 LLM 설정: {self.llm_type} - {self.model_name}")
            print(f"🔗 API URL: {self.api_base_url}")
        print()
    
    def build_analysis_prompt(self, error_context: Dict) -> str:
        """
        에러 컨텍스트에서 LLM 프롬프트 생성
        
        Args:
            error_context: 2단계에서 추출한 에러 정보
                {
                    'email_file': '이메일파일명',
                    'exceptions': [...],
                    'contexts': [...]
                }
        
        Returns:
            LLM에 전달할 프롬프트 문자열
        """
        email_file = error_context.get('email_file', 'Unknown')
        exceptions = error_context.get('exceptions', [])
        contexts = error_context.get('contexts', [])
        
        # 성공한 컨텍스트만 필터링
        successful_contexts = [ctx for ctx in contexts if ctx.get('success', False)]
        
        if not successful_contexts:
            return None
        
        # 프롬프트 구성
        prompt_parts = []
        
        # 헤더
        prompt_parts.append("=" * 60)
        prompt_parts.append("🐛 에러 분석 요청")
        prompt_parts.append("=" * 60)
        prompt_parts.append(f"\n출처: {email_file}\n")
        
        # Exception 정보
        if exceptions:
            prompt_parts.append("## 발생한 Exception\n")
            for i, exc in enumerate(exceptions, 1):
                prompt_parts.append(f"{i}. **{exc['exception']}**")
                prompt_parts.append(f"   메시지: {exc['message']}\n")
        
        # 각 컨텍스트별 소스코드
        for i, ctx in enumerate(successful_contexts, 1):
            prompt_parts.append(f"\n## 에러 발생 위치 #{i}\n")
            prompt_parts.append(f"- **파일**: {ctx['file_path']}")
            prompt_parts.append(f"- **클래스**: {ctx['class_name']}")
            prompt_parts.append(f"- **메서드**: {ctx['method']}()")
            prompt_parts.append(f"- **에러 라인**: {ctx['error_line']}")
            prompt_parts.append(f"- **컨텍스트 범위**: 라인 {ctx['context_start']}-{ctx['context_end']}\n")
            
            # 소스코드 블록
            prompt_parts.append("### 소스코드\n")
            prompt_parts.append("```java")
            
            for line in ctx['context_lines']:
                # 에러 라인 강조
                marker = ">>> " if line['is_error_line'] else "    "
                line_num = str(line['line_number']).rjust(4)
                prompt_parts.append(f"{marker}{line_num}: {line['content']}")
            
            prompt_parts.append("```\n")
        
        # 분석 요청
        prompt_parts.append("\n" + "=" * 60)
        prompt_parts.append("📋 분석 요청 사항")
        prompt_parts.append("=" * 60)
        prompt_parts.append("""
위 에러를 분석하여 다음 내용을 포함한 리포트를 작성해주세요:

1. **에러 원인 분석**
   - 에러가 발생한 근본 원인을 명확히 설명
   - 코드의 문제점을 구체적으로 지적

2. **문제가 되는 코드**
   - 정확히 어느 부분이 문제인지 표시
   - 왜 이 코드가 문제를 일으키는지 설명

3. **수정 방법**
   - 안전하고 올바른 수정 방법 제시
   - 수정 시 고려해야 할 사항 설명

4. **수정된 코드 예시**
   - 완전하고 안전한 Java 코드 제공
   - 주석으로 수정 포인트 표시

5. **추가 권장 사항**
   - 유사한 에러를 방지하기 위한 팁
   - 코드 품질 개선 제안

⚠️ 주의: 기존 파일을 수정하지 말고, 권장 사항만 제시해주세요.
""")
        
        return "\n".join(prompt_parts)
    
    def call_ollama_api(self, prompt: str) -> Optional[str]:
        """
        Ollama API 호출
        
        Args:
            prompt: 사용자 프롬프트
            
        Returns:
            LLM 응답 텍스트
        """
        url = f"{self.api_base_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": self.SYSTEM_PROMPT,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }
        }
        
        try:
            print(f"🔄 Ollama API 호출 중... (모델: {self.model_name})")
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Ollama 서버에 연결할 수 없습니다.")
            print(f"💡 Ollama가 실행 중인지 확인하세요: ollama serve")
            print(f"💡 모델이 다운로드되어 있는지 확인: ollama list")
            return None
        except requests.exceptions.Timeout:
            print(f"❌ 요청 시간 초과 (120초)")
            return None
        except Exception as e:
            print(f"❌ API 호출 실패: {e}")
            return None
    
    def call_openai_api(self, prompt: str) -> Optional[str]:
        """
        OpenAI API 호출
        
        Args:
            prompt: 사용자 프롬프트
            
        Returns:
            LLM 응답 텍스트
        """
        if not self.api_key:
            print("❌ OpenAI API 키가 설정되지 않았습니다.")
            return None
        
        url = f"{self.api_base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            print(f"🔄 OpenAI API 호출 중... (모델: {self.model_name})")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"❌ API 호출 실패: {e}")
            return None
    
    def call_mock_llm(self, prompt: str) -> str:
        """
        Mock LLM (테스트용 - Ollama 없이 데모 분석 생성)
        
        Args:
            prompt: 사용자 프롬프트
            
        Returns:
            데모 분석 텍스트
        """
        print(f"🎭 Mock 분석 생성 중... (데모용)")
        
        # 프롬프트에서 정보 추출
        is_null_pointer = "NullPointerException" in prompt
        is_db_error = "DataAccessException" in prompt or "SQLException" in prompt
        
        if is_null_pointer:
            return """
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
"""
        elif is_db_error:
            return """
## 1. 에러 원인 분석

**근본 원인**: 데이터베이스 테이블이 존재하지 않아 발생한 에러입니다.

에러 메시지를 보면:
```
SQLSyntaxErrorException: Table 'ax_db.products' doesn't exist
```

`products` 테이블이 데이터베이스에 존재하지 않는 상태에서 쿼리를 실행하여 에러가 발생했습니다.

**가능한 원인**:
1. 데이터베이스 마이그레이션이 실행되지 않음
2. 잘못된 데이터베이스에 연결
3. 테이블 이름 오타 (대소문자 구분)
4. 스키마가 생성되지 않음

## 2. 문제가 되는 코드

Repository나 SQL 쿼리에서 존재하지 않는 테이블을 참조:
```java
// ProductRepository.java
@Query("SELECT * FROM products WHERE id = ?")  // ❌ 테이블 없음
Product findProductById(Long id);
```

## 3. 수정 방법

### 방법 1: 데이터베이스 마이그레이션 실행

**Flyway 사용 예시**:
```sql
-- V1__create_products_table.sql
CREATE TABLE IF NOT EXISTS products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**실행**:
```bash
flyway migrate
```

### 방법 2: JPA Entity 확인 및 자동 생성

```java
@Entity
@Table(name = "products")  // 테이블 이름 명시
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String name;
    
    @Column(nullable = false)
    private BigDecimal price;
}
```

`application.properties`:
```properties
# 개발 환경에서만 사용 (프로덕션에서는 validate 사용)
spring.jpa.hibernate.ddl-auto=create-drop
```

### 방법 3: 데이터베이스 연결 확인

```properties
# application.properties
spring.datasource.url=jdbc:mysql://localhost:3306/ax_db?createDatabaseIfNotExist=true
spring.datasource.username=root
spring.datasource.password=password

# 로그로 실행되는 SQL 확인
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

## 4. 수정된 코드 예시

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    
    /**
     * ID로 제품 조회 (개선 버전)
     * - Optional 반환으로 null 처리
     * - 명확한 메서드명
     */
    Optional<Product> findById(Long id);
    
    /**
     * 존재 여부 확인
     */
    boolean existsById(Long id);
}

@Service
public class ProductService {
    
    @Autowired
    private ProductRepository productRepository;
    
    /**
     * 제품 조회 (안전한 버전)
     */
    public Product getProductDetails(Long productId) {
        // 존재하지 않는 경우 명확한 예외 발생
        return productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException(
                "Product not found with id: " + productId));
    }
}
```

## 5. 추가 권장 사항

### 데이터베이스 초기화 스크립트

```sql
-- schema.sql (src/main/resources)
CREATE TABLE IF NOT EXISTS products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_name ON products(name);
```

### 헬스체크 엔드포인트

```java
@RestController
@RequestMapping("/health")
public class HealthController {
    
    @Autowired
    private DataSource dataSource;
    
    @GetMapping("/db")
    public Map<String, Object> checkDatabase() {
        try (Connection conn = dataSource.getConnection()) {
            DatabaseMetaData metaData = conn.getMetaData();
            
            // 테이블 존재 여부 확인
            ResultSet tables = metaData.getTables(null, null, "products", null);
            boolean tableExists = tables.next();
            
            return Map.of(
                "status", tableExists ? "UP" : "DOWN",
                "message", tableExists ? "Database OK" : "Table 'products' not found"
            );
        } catch (Exception e) {
            return Map.of("status", "DOWN", "error", e.getMessage());
        }
    }
}
```

### 테스트 환경 설정

```properties
# application-test.properties
spring.datasource.url=jdbc:h2:mem:testdb
spring.jpa.hibernate.ddl-auto=create-drop
spring.sql.init.mode=always
```

### 체크리스트
- [ ] 데이터베이스 마이그레이션 스크립트 작성
- [ ] Entity 클래스와 테이블명 일치 확인
- [ ] 개발/테스트/프로덕션 환경별 설정 분리
- [ ] 헬스체크 엔드포인트 추가
- [ ] 에러 핸들링 강화
"""
        else:
            return """
## 1. 에러 원인 분석

제공된 에러 로그와 소스코드를 분석한 결과, 다음과 같은 문제점이 발견되었습니다.

(Mock 모드: 실제 LLM을 사용하면 더 상세한 분석이 제공됩니다)

## 2. 문제가 되는 코드

코드의 주요 문제점을 식별했습니다.

## 3. 수정 방법

권장하는 수정 방법은 다음과 같습니다.

## 4. 수정된 코드 예시

```java
// 수정된 코드 예시
// (Mock 모드: 실제 LLM 사용 시 구체적인 코드 제공)
```

## 5. 추가 권장 사항

- 유닛 테스트 추가
- 에러 핸들링 강화
- 로깅 개선

💡 **실제 LLM을 사용하려면**: Ollama를 설치하거나 OpenAI API 키를 설정하세요.
"""
    
    def call_llm(self, prompt: str) -> Optional[str]:
        """
        LLM 호출 (타입에 따라 자동 선택)
        
        Args:
            prompt: 사용자 프롬프트
            
        Returns:
            LLM 응답 텍스트
        """
        if self.llm_type == "mock":
            return self.call_mock_llm(prompt)
        elif self.llm_type == "ollama":
            return self.call_ollama_api(prompt)
        elif self.llm_type == "openai":
            return self.call_openai_api(prompt)
        else:
            print(f"❌ 지원하지 않는 LLM 타입: {self.llm_type}")
            return None
    
    def generate_report_markdown(self, 
                                 error_context: Dict, 
                                 analysis: str,
                                 class_name: str) -> str:
        """
        마크다운 리포트 생성
        
        Args:
            error_context: 에러 컨텍스트 정보
            analysis: LLM 분석 결과
            class_name: 클래스명
            
        Returns:
            마크다운 형식의 리포트
        """
        report_parts = []
        
        # 헤더
        report_parts.append(f"# 🐛 에러 분석 리포트: {class_name}")
        report_parts.append(f"\n**생성 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_parts.append(f"**분석 모델**: {self.model_name}")
        report_parts.append(f"**출처**: {error_context.get('email_file', 'Unknown')}\n")
        report_parts.append("---\n")
        
        # Exception 요약
        exceptions = error_context.get('exceptions', [])
        if exceptions:
            report_parts.append("## 📋 발생한 Exception\n")
            for exc in exceptions:
                report_parts.append(f"- **{exc['exception']}**")
                report_parts.append(f"  - {exc['message']}\n")
        
        # 에러 위치 요약
        successful_contexts = [ctx for ctx in error_context.get('contexts', []) 
                              if ctx.get('success', False)]
        
        if successful_contexts:
            report_parts.append("## 📍 에러 발생 위치\n")
            for ctx in successful_contexts:
                report_parts.append(f"- **파일**: `{ctx['file_path']}`")
                report_parts.append(f"- **클래스**: `{ctx['class_name']}`")
                report_parts.append(f"- **메서드**: `{ctx['method']}()`")
                report_parts.append(f"- **라인**: {ctx['error_line']}\n")
        
        # LLM 분석 결과
        report_parts.append("---\n")
        report_parts.append("## 🔍 AI 분석 결과\n")
        report_parts.append(analysis)
        
        # 푸터 - 경고
        report_parts.append("\n---\n")
        report_parts.append("## ⚠️ 중요 공지\n")
        report_parts.append("""
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
""")
        
        return "\n".join(report_parts)
    
    def process_all_errors(self, contexts_json_path: str, output_dir: str = "reports"):
        """
        2단계 JSON 파일을 읽어서 모든 에러 분석 및 리포트 생성
        
        Args:
            contexts_json_path: step2_code_contexts.json 파일 경로
            output_dir: 리포트 저장 디렉토리
        """
        print("=" * 60)
        print("[3단계] 원인 분석 및 수정 제안 리포트 생성")
        print("=" * 60)
        print(f"\n📂 입력: {contexts_json_path}")
        
        # JSON 읽기
        with open(contexts_json_path, 'r', encoding='utf-8') as f:
            all_contexts = json.load(f)
        
        print(f"📊 처리할 이메일: {len(all_contexts)}개\n")
        
        # 출력 디렉토리 생성
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        report_count = 0
        
        for email_file, error_context in all_contexts.items():
            # 성공한 컨텍스트가 없으면 스킵
            successful_contexts = [ctx for ctx in error_context.get('contexts', [])
                                  if ctx.get('success', False)]
            
            if not successful_contexts:
                print(f"⏭️  건너뜀: {email_file} (추출된 컨텍스트 없음)\n")
                continue
            
            print(f"\n{'='*60}")
            print(f"📧 처리 중: {email_file}")
            print(f"{'='*60}")
            
            # 각 클래스별로 리포트 생성
            processed_classes = set()
            
            for ctx in successful_contexts:
                class_name = ctx['class_name']
                
                # 이미 처리한 클래스는 스킵
                if class_name in processed_classes:
                    continue
                
                processed_classes.add(class_name)
                
                print(f"\n🎯 클래스: {class_name}")
                
                # 프롬프트 생성
                prompt = self.build_analysis_prompt(error_context)
                
                if not prompt:
                    print(f"   ✗ 프롬프트 생성 실패")
                    continue
                
                # LLM 호출
                analysis = self.call_llm(prompt)
                
                if not analysis:
                    print(f"   ✗ LLM 호출 실패")
                    continue
                
                print(f"   ✓ 분석 완료 ({len(analysis)} 문자)")
                
                # 리포트 생성
                report_md = self.generate_report_markdown(
                    error_context, 
                    analysis, 
                    class_name
                )
                
                # 파일 저장
                report_filename = f"오류_분석_리포트_{class_name}.md"
                report_path = output_path / report_filename
                
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(report_md)
                
                print(f"   ✓ 리포트 저장: {report_path}")
                report_count += 1
        
        # 요약
        print(f"\n{'='*60}")
        print(f"✅ 총 {report_count}개 리포트 생성 완료!")
        print(f"📁 저장 위치: {output_path.absolute()}")
        print(f"{'='*60}\n")


def main():
    """메인 실행 함수"""
    
    print("=" * 60)
    print("🤖 LLM 설정")
    print("=" * 60)
    print("\n사용 가능한 모드:")
    print("  1. Mock 모드 (데모용 - Ollama 불필요)")
    print("  2. Ollama (로컬 실행)")
    print("  3. OpenAI API")
    print()
    
    # 설정
    # ===================================================================
    # 옵션 1: Mock 모드 (Ollama 없이 테스트용 - 기본값)
    # ===================================================================
    generator = AnalysisReportGenerator(
        use_mock=True  # Mock 모드 활성화
    )
    
    # ===================================================================
    # 옵션 2: Ollama (로컬 실행) - Ollama 설치 후 사용
    # ===================================================================
    # generator = AnalysisReportGenerator(
    #     llm_type="ollama",
    #     model_name="qwen2.5:7b",  # 또는 "llama3", "codellama" 등
    #     api_base_url="http://localhost:11434"
    # )
    
    # ===================================================================
    # 옵션 3: OpenAI API - API 키 필요
    # ===================================================================
    # generator = AnalysisReportGenerator(
    #     llm_type="openai",
    #     model_name="gpt-4",
    #     api_base_url="https://api.openai.com/v1",
    #     api_key="your-api-key-here"  # 또는 os.getenv('OPENAI_API_KEY')
    # )
    
    try:
        # 2단계 결과 처리
        generator.process_all_errors(
            contexts_json_path="output/step2_code_contexts.json",
            output_dir="reports"
        )
        
        print("💡 생성된 리포트를 확인하고 개발자가 검토하세요.")
        print("⚠️  AI는 파일을 직접 수정하지 않았습니다. 리포트만 생성되었습니다.")
        
        if generator.llm_type == "mock":
            print("\n" + "=" * 60)
            print("🎭 Mock 모드로 실행되었습니다")
            print("=" * 60)
            print("실제 AI 분석을 사용하려면:")
            print("  1. Ollama 설치: https://ollama.com/download")
            print("  2. 모델 다운로드: ollama pull qwen2.5:7b")
            print("  3. 서버 실행: ollama serve")
            print("  4. 코드에서 use_mock=False로 변경")
            print("=" * 60)
        
        print()
        
    except FileNotFoundError as e:
        print(f"\n❌ 오류: {e}")
        print("\n💡 먼저 [2단계]를 실행하여 step2_code_contexts.json 파일을 생성해주세요.")
        print("   실행 명령: python src/step2_code_extractor.py")
    
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
