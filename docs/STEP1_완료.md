# 🎉 [1단계] 메일 파싱 및 에러 키워드 추출 - 완료!

## ✅ 구현 완료 항목

### 1. 핵심 기능
- ✅ 이메일 폴더에서 `.txt`, `.log`, `.eml`, `.msg` 파일 자동 탐색
- ✅ 하위 폴더 포함 재귀적 탐색 지원
- ✅ 다양한 인코딩 자동 감지 (UTF-8, CP949, Latin-1)
- ✅ Java Stack Trace에서 클래스명, 메서드명, 라인 번호 정규표현식 추출
- ✅ Exception 타입 및 메시지 추출
- ✅ 패키지명과 클래스명 자동 분리
- ✅ JSON 구조로 결과 저장

### 2. 제공되는 파일

#### 📂 소스코드
- `src/step1_email_parser.py` - 메인 파서 모듈 (250줄)
  - `EmailParser` 클래스
  - 이메일 읽기, 파싱, JSON 저장 기능

#### 📂 예시 데이터
- `email/sample_error.txt` - NullPointerException 예시
- `email/database_error.log` - 데이터베이스 에러 예시

#### 📂 예시 Java 프로젝트
- `example_project/src/com/hanwha/ax/`
  - `controller/OrderController.java`
  - `service/CustomerService.java`
  - `model/Customer.java`
  - `model/Order.java`

#### 📂 사용 예시
- `examples/test_step1_examples.py` - 5가지 활용 예시

#### 📂 출력 결과
- `output/step1_parsed_errors.json` - 파싱 결과

## 🚀 사용 방법

### 기본 실행
```bash
# 프로젝트 루트 디렉토리에서
python src/step1_email_parser.py
```

### 다양한 활용 예시 실행
```bash
python examples/test_step1_examples.py
```

## 📊 출력 JSON 구조

```json
{
  "파일명.txt": {
    "has_error": true,
    "exceptions": [
      {
        "exception": "java.lang.NullPointerException",
        "message": "Cannot invoke \"String.length()\" because \"customerName\" is null"
      }
    ],
    "stack_traces": [
      {
        "full_class": "com.hanwha.ax.service.CustomerService",
        "package": "com.hanwha.ax.service",
        "class_name": "CustomerService",
        "method": "validateCustomerData",
        "file": "CustomerService.java",
        "line": 145
      }
    ],
    "raw_text": "원본 텍스트 일부..."
  }
}
```

## 🎯 추출되는 정보

### Exception 정보
- `exception`: Exception 전체 클래스명 (예: `java.lang.NullPointerException`)
- `message`: 에러 메시지

### Stack Trace 정보
- `full_class`: 전체 클래스명 (예: `com.hanwha.ax.service.CustomerService`)
- `package`: 패키지명 (예: `com.hanwha.ax.service`)
- `class_name`: 클래스명만 (예: `CustomerService`)
- `method`: 메서드명 (예: `validateCustomerData`)
- `file`: 파일명 (예: `CustomerService.java`)
- `line`: 라인 번호 (예: `145`)

## 💡 활용 예시

### 1. 단일 파일 파싱
```python
from step1_email_parser import EmailParser

parser = EmailParser()
email_text = parser.read_email_file("email/sample_error.txt")
result = parser.parse_email(email_text)

print(result['has_error'])  # True
print(result['exceptions'])  # Exception 리스트
print(result['stack_traces'])  # Stack Trace 리스트
```

### 2. 폴더 전체 파싱
```python
parser = EmailParser()
all_results = parser.parse_all_emails()

for filename, result in all_results.items():
    if result['has_error']:
        print(f"에러 발견: {filename}")
```

### 3. 특정 패키지만 필터링
```python
parser = EmailParser()
all_results = parser.parse_all_emails()

for filename, result in all_results.items():
    for trace in result['stack_traces']:
        if trace['package'].startswith('com.hanwha.ax'):
            print(f"{trace['class_name']}.{trace['method']}() at line {trace['line']}")
```

### 4. 에러 통계 생성
```python
parser = EmailParser()
all_results = parser.parse_all_emails()

# Exception 타입별 카운트
exception_count = {}
for result in all_results.values():
    for exc in result['exceptions']:
        exc_type = exc['exception']
        exception_count[exc_type] = exception_count.get(exc_type, 0) + 1

print(exception_count)
```

## 🔍 실행 결과 예시

```
============================================================
[1단계] 메일 파싱 및 에러 키워드 추출
============================================================

📧 이메일 폴더에서 파일 읽기 중...
✓ 읽기 성공: database_error.log
✓ 읽기 성공: sample_error.txt

📊 총 2개 파일 처리 완료

📄 파일: database_error.log
   - 에러 발견: 예
   - Exception 수: 2
   - Stack Trace 수: 8
   - 주요 Exception: DataAccessException
   - 첫 번째 에러 위치: ProductRepository.findProductById() at line 234

📄 파일: sample_error.txt
   - 에러 발견: 예
   - Exception 수: 1
   - Stack Trace 수: 9
   - 주요 Exception: NullPointerException
   - 첫 번째 에러 위치: CustomerService.validateCustomerData() at line 145

✓ 파싱 결과 저장 완료: output\step1_parsed_errors.json
```

## 🎨 주요 특징

### 1. 유연한 파일 탐색
- 지정된 폴더 내 모든 하위 폴더 자동 탐색
- 다양한 파일 확장자 지원 (`.txt`, `.log`, `.eml`, `.msg`)
- 이미지나 첨부 파일은 무시하고 텍스트만 처리

### 2. 강력한 정규표현식
- Java Stack Trace 패턴 정확히 매칭
  ```
  at com.example.MyClass.myMethod(MyClass.java:123)
  ```
- Exception 패턴 추출
  ```
  java.lang.NullPointerException: message
  ```

### 3. 인코딩 자동 감지
- UTF-8 → CP949 → Latin-1 순으로 시도
- 한글 파일명 및 내용 완벽 지원

### 4. 구조화된 데이터
- 패키지명과 클래스명 자동 분리
- 2단계에서 바로 활용 가능한 형태로 저장

## 📝 다음 단계 연계

이제 추출된 JSON 데이터를 활용하여:

### [2단계] 소스코드 실시간 접근 및 컨텍스트 추출
- `step1_parsed_errors.json` 읽기
- `class_name`, `file`, `line` 정보로 Java 파일 탐색
- 해당 라인 기준 앞뒤 30줄 추출

### [3단계] 원인 분석 및 수정 제안 리포트 생성
- 에러 로그 + 소스코드 컨텍스트를 LLM에 전달
- 마크다운 리포트 생성

## 🛠️ 커스터마이징

### 다른 언어 지원
Python, C#, JavaScript 등도 정규표현식만 수정하면 지원 가능합니다.

```python
# Python Stack Trace 패턴
PYTHON_STACK_PATTERN = re.compile(
    r'File "(?P<file>.*?)", line (?P<line>\d+), in (?P<method>\w+)'
)
```

### 추출 라인 수 변경
`raw_text`에서 저장하는 텍스트 길이를 조절할 수 있습니다.

```python
'raw_text': text[:500]  # 처음 500자 → 1000자로 변경
```

## 📞 지원

- 문제 발생 시 `examples/test_step1_examples.py`를 실행하여 정상 동작 확인
- JSON 결과가 비어있다면 Stack Trace 형식이 다를 수 있음 → 정규표현식 조정 필요

---

**✅ [1단계] 완료! 다음 단계인 [2단계] 소스코드 실시간 접근으로 진행할 준비가 되었습니다.**
