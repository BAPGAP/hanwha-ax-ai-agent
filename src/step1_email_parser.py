"""
[1단계] 메일 파싱 및 에러 키워드 추출

이메일 텍스트나 로그 파일에서 Java Stack Trace를 파싱하여
클래스명, 메서드명, 오류 라인 번호를 추출하는 모듈
"""

import re
import os
import json
from pathlib import Path
from typing import List, Dict, Optional


class EmailParser:
    """이메일 및 로그 파일에서 에러 정보를 추출하는 클래스"""
    
    # Java Stack Trace 패턴
    # 예: at com.example.MyClass.myMethod(MyClass.java:123)
    JAVA_STACK_PATTERN = re.compile(
        r'at\s+(?P<full_class>[\w.$]+)\.(?P<method>[\w<>]+)\((?P<file>[\w.]+):(?P<line>\d+)\)'
    )
    
    # Exception 타입 패턴
    # 예: java.lang.NullPointerException: Cannot invoke method
    EXCEPTION_PATTERN = re.compile(
        r'(?P<exception>[\w.]+Exception):\s*(?P<message>.*)'
    )
    
    def __init__(self, email_folder: str = "email"):
        """
        Args:
            email_folder: 이메일 파일이 저장된 폴더 경로
        """
        self.email_folder = Path(email_folder)
        
    def read_email_file(self, file_path: str) -> str:
        """
        이메일 파일을 읽어서 텍스트로 반환
        
        Args:
            file_path: 이메일 파일 경로
            
        Returns:
            파일 내용 (텍스트)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # UTF-8 실패 시 다른 인코딩 시도
            try:
                with open(file_path, 'r', encoding='cp949') as f:
                    return f.read()
            except:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
    
    def read_all_emails_from_folder(self, folder_path: Optional[str] = None) -> Dict[str, str]:
        """
        폴더 내 모든 이메일 파일을 읽어서 딕셔너리로 반환
        
        Args:
            folder_path: 이메일 폴더 경로 (None이면 기본 email_folder 사용)
            
        Returns:
            {파일명: 파일내용} 형태의 딕셔너리
        """
        if folder_path is None:
            folder_path = self.email_folder
        else:
            folder_path = Path(folder_path)
            
        if not folder_path.exists():
            raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder_path}")
        
        email_contents = {}
        
        # 지원하는 파일 확장자
        supported_extensions = ['.txt', '.eml', '.log', '.msg']
        
        # 모든 파일 탐색 (하위 폴더 포함)
        for file_path in folder_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    content = self.read_email_file(str(file_path))
                    # 상대 경로를 키로 사용
                    relative_path = file_path.relative_to(folder_path)
                    email_contents[str(relative_path)] = content
                    print(f"✓ 읽기 성공: {relative_path}")
                except Exception as e:
                    print(f"✗ 읽기 실패: {file_path} - {e}")
        
        return email_contents
    
    def extract_stack_trace_info(self, text: str) -> List[Dict[str, any]]:
        """
        텍스트에서 Java Stack Trace 정보를 추출
        
        Args:
            text: 이메일 또는 로그 텍스트
            
        Returns:
            추출된 스택 트레이스 정보 리스트
            각 항목: {
                'full_class': 'com.example.MyClass',
                'package': 'com.example',
                'class_name': 'MyClass',
                'method': 'myMethod',
                'file': 'MyClass.java',
                'line': 123
            }
        """
        stack_traces = []
        
        for match in self.JAVA_STACK_PATTERN.finditer(text):
            full_class = match.group('full_class')
            method = match.group('method')
            file_name = match.group('file')
            line_number = int(match.group('line'))
            
            # 패키지명과 클래스명 분리
            parts = full_class.split('.')
            class_name = parts[-1] if parts else full_class
            package = '.'.join(parts[:-1]) if len(parts) > 1 else ''
            
            stack_info = {
                'full_class': full_class,
                'package': package,
                'class_name': class_name,
                'method': method,
                'file': file_name,
                'line': line_number
            }
            
            stack_traces.append(stack_info)
        
        return stack_traces
    
    def extract_exception_info(self, text: str) -> List[Dict[str, str]]:
        """
        텍스트에서 Exception 정보를 추출
        
        Args:
            text: 이메일 또는 로그 텍스트
            
        Returns:
            추출된 Exception 정보 리스트
            각 항목: {
                'exception': 'NullPointerException',
                'message': 'Cannot invoke method'
            }
        """
        exceptions = []
        
        for match in self.EXCEPTION_PATTERN.finditer(text):
            exception_info = {
                'exception': match.group('exception'),
                'message': match.group('message').strip()
            }
            exceptions.append(exception_info)
        
        return exceptions
    
    def parse_email(self, text: str) -> Dict[str, any]:
        """
        이메일 텍스트를 파싱하여 에러 정보를 추출
        
        Args:
            text: 이메일 또는 로그 텍스트
            
        Returns:
            JSON 구조의 에러 정보
            {
                'has_error': True/False,
                'exceptions': [...],
                'stack_traces': [...],
                'raw_text': '원본 텍스트 일부'
            }
        """
        exceptions = self.extract_exception_info(text)
        stack_traces = self.extract_stack_trace_info(text)
        
        result = {
            'has_error': len(stack_traces) > 0 or len(exceptions) > 0,
            'exceptions': exceptions,
            'stack_traces': stack_traces,
            'raw_text': text[:500]  # 처음 500자만 저장
        }
        
        return result
    
    def parse_all_emails(self, folder_path: Optional[str] = None) -> Dict[str, Dict[str, any]]:
        """
        폴더 내 모든 이메일을 파싱
        
        Args:
            folder_path: 이메일 폴더 경로
            
        Returns:
            {파일명: 파싱결과} 형태의 딕셔너리
        """
        email_contents = self.read_all_emails_from_folder(folder_path)
        parsed_results = {}
        
        for file_name, content in email_contents.items():
            parsed_results[file_name] = self.parse_email(content)
        
        return parsed_results
    
    def save_parsed_results(self, results: Dict[str, any], output_file: str = "parsed_errors.json"):
        """
        파싱 결과를 JSON 파일로 저장
        
        Args:
            results: 파싱 결과
            output_file: 출력 파일명
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 파싱 결과 저장 완료: {output_path}")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("[1단계] 메일 파싱 및 에러 키워드 추출")
    print("=" * 60)
    
    # EmailParser 인스턴스 생성
    parser = EmailParser(email_folder="email")
    
    # 모든 이메일 파싱
    try:
        print("\n📧 이메일 폴더에서 파일 읽기 중...")
        parsed_results = parser.parse_all_emails()
        
        print(f"\n📊 총 {len(parsed_results)}개 파일 처리 완료\n")
        
        # 결과 요약 출력
        for file_name, result in parsed_results.items():
            print(f"📄 파일: {file_name}")
            print(f"   - 에러 발견: {'예' if result['has_error'] else '아니오'}")
            print(f"   - Exception 수: {len(result['exceptions'])}")
            print(f"   - Stack Trace 수: {len(result['stack_traces'])}")
            
            if result['exceptions']:
                print(f"   - 주요 Exception: {result['exceptions'][0]['exception']}")
            
            if result['stack_traces']:
                first_trace = result['stack_traces'][0]
                print(f"   - 첫 번째 에러 위치: {first_trace['class_name']}.{first_trace['method']}() at line {first_trace['line']}")
            
            print()
        
        # JSON 파일로 저장
        parser.save_parsed_results(parsed_results, "output/step1_parsed_errors.json")
        
    except FileNotFoundError as e:
        print(f"\n⚠️  {e}")
        print("💡 'email' 폴더를 생성하고 에러 로그 파일을 넣어주세요.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()
