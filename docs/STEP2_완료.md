# 🎉 [2단계] 소스코드 실시간 접근 및 컨텍스트 추출 - 완료!

## ✅ 구현 완료 항목

### 1. 핵심 기능
- ✅ 1단계 JSON 데이터(클래스명, 라인 번호) 자동 읽기
- ✅ Java 프로젝트 디렉토리에서 `.java` 파일 **실시간 재귀 탐색**
- ✅ 클래스명 + 패키지명으로 정확한 파일 매칭
- ✅ **파일을 직접 열어 최신 수정 사항 반영**
- ✅ 에러 라인 기준 **앞뒤 30줄** (커스터마이징 가능) 추출
- ✅ 라인 번호와 함께 구조화된 데이터로 저장
- ✅ **에러 라인 하이라이팅** (`is_error_line: true`)
- ✅ 여러 이메일의 여러 에러를 일괄 처리

### 2. 제공되는 파일

#### 📂 소스코드
- `src/step2_code_extractor.py` - 코드 추출기 (350줄)
  - `CodeExtractor` 클래스
  - Java 파일 인덱싱, 탐색, 컨텍스트 추출 기능

#### 📂 사용 예시
- `examples/test_step2_examples.py` - 6가지 활용 예시

#### 📂 출력 결과
- `output/step2_code_contexts.json` - 추출된 코드 컨텍스트

## 🚀 사용 방법

### 기본 실행
```bash
# 프로젝트 루트 디렉토리에서
python src/step2_code_extractor.py
```

### 다양한 활용 예시 실행
```bash
python examples/test_step2_examples.py
```

## 📊 출력 JSON 구조

```json
{
  "이메일파일.txt": {
    "email_file": "이메일파일.txt",
    "exceptions": [
      {
        "exception": "java.lang.NullPointerException",
        "message": "Cannot invoke \"String.length()\" because \"customerName\" is null"
      }
    ],
    "contexts": [
      {
        "success": true,
        "file_path": "example_project/src/.../CustomerService.java",
        "total_lines": 60,
        "error_line": 145,
        "context_start": 115,
        "context_end": 60,
        "context_lines": [
          {
            "line_number": 143,
            "content": "    String customerName = customer.getName();",
            "is_error_line": false
          },
          {
            "line_number": 145,
            "content": "    if (customerName.length() < 2) {",
            "is_error_line": true
          }
        ],
        "raw_code": "전체 코드 텍스트...",
        "class_name": "CustomerService",
        "package": "com.hanwha.ax.service",
        "method": "validateCustomerData",
        "full_class": "com.hanwha.ax.service.CustomerService"
      }
    ],
    "total_traces": 9,
    "extracted_contexts": 3
  }
}
```

## 🎯 추출되는 정보

### 메타 정보
- `success`: 추출 성공 여부
- `file_path`: 실제 Java 파일 경로
- `total_lines`: 파일 전체 라인 수
- `error_line`: 에러 발생 라인 번호

### 컨텍스트 범위
- `context_start`: 추출된 코드 시작 라인
- `context_end`: 추출된 코드 끝 라인
- `context_lines`: 각 라인별 상세 정보
  - `line_number`: 라인 번호
  - `content`: 라인 내용
  - `is_error_line`: 에러 발생 라인 여부 (⭐)

### 코드 정보
- `raw_code`: 추출된 전체 코드 (문자열)
- `class_name`: 클래스명
- `package`: 패키지명
- `method`: 메서드명

## 💡 활용 예시

### 1. 단일 에러 위치 추출
```python
from step2_code_extractor import CodeExtractor

extractor = CodeExtractor(project_root="example_project", context_lines=30)

trace_info = {
    'class_name': 'CustomerService',
    'package': 'com.hanwha.ax.service',
    'file': 'CustomerService.java',
    'line': 145,
    'method': 'validateCustomerData'
}

context = extractor.extract_context_from_trace(trace_info)

if context['success']:
    print(f"파일: {context['file_path']}")
    print(f"추출 범위: {context['context_start']}-{context['context_end']}")
    print(f"코드:\n{context['raw_code']}")
```

### 2. 1단계 JSON에서 자동 추출
```python
extractor = CodeExtractor(project_root="example_project")
contexts = extractor.process_parsed_errors("output/step1_parsed_errors.json")
extractor.save_contexts(contexts, "output/step2_code_contexts.json")
```

### 3. 성공한 추출만 필터링
```python
import json

with open("output/step2_code_contexts.json", 'r', encoding='utf-8') as f:
    contexts = json.load(f)

successful = []
for email_file, data in contexts.items():
    for ctx in data['contexts']:
        if ctx.get('success', False):
            successful.append(ctx)

print(f"성공: {len(successful)}개")
```

### 4. 에러 라인만 추출
```python
for email_file, data in contexts.items():
    for ctx in data['contexts']:
        if ctx.get('success'):
            error_line = next(
                (line for line in ctx['context_lines'] if line['is_error_line']),
                None
            )
            if error_line:
                print(f"Line {error_line['line_number']}: {error_line['content']}")
```

### 5. 커스텀 컨텍스트 크기
```python
# 앞뒤 10줄만 추출
extractor = CodeExtractor(project_root="example_project", context_lines=10)

# 앞뒤 50줄 추출
extractor = CodeExtractor(project_root="example_project", context_lines=50)
```

## 🔍 실행 결과 예시

```
============================================================
[2단계] 소스코드 실시간 접근 및 컨텍스트 추출
============================================================

📄 2개 이메일 파일의 에러 처리 중...

📂 example_project 디렉토리 인덱싱 중...
✓ 4개 Java 파일 인덱싱 완료
✓ 4개 고유 클래스 발견

============================================================
📧 처리 중: sample_error.txt
============================================================
🔍 CustomerService.validateCustomerData() at line 145 탐색 중...
   ✓ 파일 발견: example_project\src\com\hanwha\ax\service\CustomerService.java
   ✓ 컨텍스트 추출 완료 (라인 115-60)

============================================================
📊 컨텍스트 추출 요약
============================================================

📧 처리한 이메일: 2개
✅ 성공적으로 추출: 4개
❌ 실패: 5개

📝 추출된 컨텍스트:
   [sample_error.txt]
      - CustomerService.validateCustomerData() (라인 115-60)
      - CustomerService.processCustomerOrder() (라인 59-60)
      - OrderController.createOrder() (라인 37-47)
```

## 🎨 주요 특징

### 1. 실시간 파일 읽기
- 매번 파일을 새로 열어서 **최신 수정 사항 즉시 반영**
- 개발 중 소스코드가 변경되어도 항상 최신 버전 읽음
- 캐싱이 아닌 직접 파일 시스템 접근

### 2. 지능적인 파일 탐색
- 프로젝트 전체를 재귀적으로 탐색하여 `.java` 파일 인덱싱
- 클래스명이 같은 파일이 여러 개 있어도 패키지명으로 정확히 매칭
- 빠른 재탐색을 위한 인덱스 캐싱

### 3. 정확한 컨텍스트 추출
- 에러 라인 기준 앞뒤 N줄을 정확히 계산 (1-based 인덱싱)
- 파일 시작/끝 경계 자동 처리
- 각 라인마다 번호와 에러 여부 표시

### 4. 구조화된 데이터
- 3단계(LLM 분석)에서 바로 사용 가능한 형태
- `raw_code`로 전체 텍스트 제공
- `context_lines`로 라인별 상세 정보 제공

### 5. 에러 핸들링
- 파일을 찾을 수 없을 때 명확한 에러 메시지
- 인코딩 문제 자동 처리 (UTF-8, CP949)
- 부분 실패해도 다른 에러는 계속 처리

## 📝 다음 단계 연계

이제 추출된 컨텍스트를 활용하여:

### [3단계] 원인 분석 및 수정 제안 리포트 생성
- `step2_code_contexts.json` 읽기
- Exception 메시지 + 실제 소스코드를 LLM에 전달
- LLM이 원인 분석 및 수정 제안
- 마크다운 리포트 생성 (`오류_분석_리포트_[클래스명].md`)

### 3단계에 전달할 프롬프트 예시
```
다음은 운영 서버에서 발생한 에러입니다:

Exception: java.lang.NullPointerException
Message: Cannot invoke "String.length()" because "customerName" is null

에러가 발생한 코드:
파일: CustomerService.java
메서드: validateCustomerData()
라인 145:

[소스코드]
140: if (customer.getId() == null || customer.getId().isEmpty()) {
141:     throw new IllegalArgumentException("Customer ID is required");
142: }
143: 
144: String customerName = customer.getName();
145: if (customerName.length() < 2) {  // ← 에러 발생
146:     throw new IllegalArgumentException("Customer name must be at least 2 characters");
147: }

위 코드의 문제점을 분석하고 안전한 수정 방법을 제안해주세요.
```

## 🛠️ 커스터마이징

### 다른 언어 지원
Python, JavaScript 등도 파일 확장자만 변경하면 동일하게 사용 가능합니다.

```python
# Python 프로젝트 탐색
for py_file in self.project_root.rglob("*.py"):
    # ...
```

### 컨텍스트 크기 조정
```python
# 앞뒤 10줄만
extractor = CodeExtractor(context_lines=10)

# 앞뒤 100줄
extractor = CodeExtractor(context_lines=100)
```

### 특정 패키지만 처리
```python
# 우리 프로젝트(com.hanwha.ax)만 처리
if not package.startswith('com.hanwha.ax'):
    continue
```

## 🔧 주요 메서드

### `build_file_index()`
프로젝트 내 모든 Java 파일을 인덱싱하여 클래스명→파일경로 매핑 생성

### `find_java_file(class_name, package)`
클래스명과 패키지명으로 Java 파일 찾기

### `read_file_with_context(file_path, line_number)`
파일을 열어서 지정 라인 기준 앞뒤 N줄 추출

### `extract_context_from_trace(trace_info)`
Stack Trace 정보에서 소스코드 컨텍스트 추출

### `process_parsed_errors(json_path)`
1단계 JSON 파일을 읽어서 모든 에러 처리

### `save_contexts(contexts, output_file)`
추출된 컨텍스트를 JSON으로 저장

## 💻 코드 품질

- ✅ Type Hints 사용 (`Dict`, `List`, `Optional`)
- ✅ Docstrings로 모든 메서드 문서화
- ✅ 명확한 에러 핸들링
- ✅ 진행 상황 실시간 출력
- ✅ 외부 라이브러리 의존성 없음 (표준 라이브러리만)

## 📞 지원

- 문제 발생 시 `examples/test_step2_examples.py`를 실행하여 정상 동작 확인
- Java 파일을 찾지 못한다면 `project_root` 경로가 올바른지 확인
- 라인 번호가 맞지 않는다면 파일이 수정되었을 가능성 (실시간으로 최신 버전 읽음)

---

**✅ [2단계] 완료! 다음 단계인 [3단계] 원인 분석 및 수정 제안 리포트 생성으로 진행할 준비가 되었습니다.**
