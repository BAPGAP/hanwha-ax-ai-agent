"""
[2단계] 소스코드 실시간 접근 및 컨텍스트 추출

1단계에서 추출한 JSON 데이터를 바탕으로
실제 Java 소스코드 파일을 탐색하고 에러 발생 라인 주변 코드를 추출
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class CodeExtractor:
    """Java 소스코드에서 에러 컨텍스트를 추출하는 클래스"""
    
    def __init__(self, project_root: str = "example_project", context_lines: int = 30):
        """
        Args:
            project_root: Java 프로젝트 루트 디렉토리
            context_lines: 에러 라인 기준 앞뒤로 추출할 라인 수
        """
        self.project_root = Path(project_root)
        self.context_lines = context_lines
        self.java_file_cache = {}  # 파일 경로 캐시
        
    def build_file_index(self):
        """
        프로젝트 내 모든 .java 파일을 인덱싱
        클래스명을 키로, 파일 경로를 값으로 하는 딕셔너리 생성
        """
        print(f"\n📂 {self.project_root} 디렉토리 인덱싱 중...")
        
        if not self.project_root.exists():
            raise FileNotFoundError(f"프로젝트 디렉토리를 찾을 수 없습니다: {self.project_root}")
        
        self.java_file_cache = {}
        file_count = 0
        
        # 모든 .java 파일 탐색
        for java_file in self.project_root.rglob("*.java"):
            file_count += 1
            # 파일명에서 확장자 제거한 것을 클래스명으로 간주
            class_name = java_file.stem
            
            # 같은 클래스명이 여러 개 있을 수 있으므로 리스트로 관리
            if class_name not in self.java_file_cache:
                self.java_file_cache[class_name] = []
            
            self.java_file_cache[class_name].append(java_file)
        
        print(f"✓ {file_count}개 Java 파일 인덱싱 완료")
        print(f"✓ {len(self.java_file_cache)}개 고유 클래스 발견\n")
        
        return self.java_file_cache
    
    def find_java_file(self, class_name: str, package: Optional[str] = None) -> Optional[Path]:
        """
        클래스명(과 패키지명)으로 Java 파일 찾기
        
        Args:
            class_name: 클래스명 (예: "CustomerService")
            package: 패키지명 (예: "com.hanwha.ax.service")
            
        Returns:
            Java 파일 경로 또는 None
        """
        # 캐시에 클래스명이 없으면 인덱스 재구성
        if not self.java_file_cache:
            self.build_file_index()
        
        # 클래스명으로 찾기
        if class_name not in self.java_file_cache:
            return None
        
        candidates = self.java_file_cache[class_name]
        
        # 후보가 하나면 바로 반환
        if len(candidates) == 1:
            return candidates[0]
        
        # 여러 개면 패키지명으로 필터링
        if package:
            # 패키지 경로로 변환 (com.hanwha.ax → com/hanwha/ax)
            package_path = package.replace('.', os.sep)
            
            for candidate in candidates:
                if package_path in str(candidate):
                    return candidate
        
        # 패키지 매칭 실패하면 첫 번째 반환
        return candidates[0]
    
    def read_file_with_context(self, file_path: Path, line_number: int) -> Dict[str, any]:
        """
        파일을 열어서 지정된 라인 기준 앞뒤 N줄을 추출
        
        Args:
            file_path: Java 파일 경로
            line_number: 에러 발생 라인 번호 (1-based)
            
        Returns:
            컨텍스트 정보 딕셔너리
        """
        try:
            # 파일 읽기 (실시간으로 최신 내용 읽음)
            with open(file_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            total_lines = len(all_lines)
            
            # 추출 범위 계산 (1-based → 0-based)
            start_line = max(0, line_number - self.context_lines - 1)
            end_line = min(total_lines, line_number + self.context_lines)
            
            # 컨텍스트 추출
            context_lines = all_lines[start_line:end_line]
            
            # 라인 번호와 함께 저장
            numbered_lines = []
            for i, line in enumerate(context_lines, start=start_line + 1):
                is_error_line = (i == line_number)
                numbered_lines.append({
                    'line_number': i,
                    'content': line.rstrip('\n'),
                    'is_error_line': is_error_line
                })
            
            # 결과 반환
            return {
                'success': True,
                'file_path': str(file_path),
                'total_lines': total_lines,
                'error_line': line_number,
                'context_start': start_line + 1,
                'context_end': end_line,
                'context_lines': numbered_lines,
                'raw_code': ''.join(context_lines)
            }
            
        except UnicodeDecodeError:
            # UTF-8 실패 시 다른 인코딩 시도
            try:
                with open(file_path, 'r', encoding='cp949') as f:
                    all_lines = f.readlines()
                # 위와 동일한 로직 반복
                total_lines = len(all_lines)
                start_line = max(0, line_number - self.context_lines - 1)
                end_line = min(total_lines, line_number + self.context_lines)
                context_lines = all_lines[start_line:end_line]
                
                numbered_lines = []
                for i, line in enumerate(context_lines, start=start_line + 1):
                    is_error_line = (i == line_number)
                    numbered_lines.append({
                        'line_number': i,
                        'content': line.rstrip('\n'),
                        'is_error_line': is_error_line
                    })
                
                return {
                    'success': True,
                    'file_path': str(file_path),
                    'total_lines': total_lines,
                    'error_line': line_number,
                    'context_start': start_line + 1,
                    'context_end': end_line,
                    'context_lines': numbered_lines,
                    'raw_code': ''.join(context_lines)
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"파일 읽기 실패 (인코딩 오류): {e}"
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"파일 읽기 실패: {e}"
            }
    
    def extract_context_from_trace(self, trace_info: Dict[str, any]) -> Dict[str, any]:
        """
        Stack Trace 정보에서 소스코드 컨텍스트 추출
        
        Args:
            trace_info: 1단계에서 추출한 stack trace 정보
                {
                    'class_name': 'CustomerService',
                    'package': 'com.hanwha.ax.service',
                    'file': 'CustomerService.java',
                    'line': 145,
                    'method': 'validateCustomerData'
                }
        
        Returns:
            컨텍스트 정보 또는 에러 정보
        """
        class_name = trace_info.get('class_name')
        package = trace_info.get('package')
        line_number = trace_info.get('line')
        method = trace_info.get('method')
        
        print(f"🔍 {class_name}.{method}() at line {line_number} 탐색 중...")
        
        # Java 파일 찾기
        java_file = self.find_java_file(class_name, package)
        
        if not java_file:
            print(f"   ✗ 파일을 찾을 수 없음: {class_name}.java")
            return {
                'success': False,
                'class_name': class_name,
                'method': method,
                'package': package,
                'line': line_number,
                'error': f'{class_name}.java 파일을 찾을 수 없습니다.'
            }
        
        print(f"   ✓ 파일 발견: {java_file}")
        
        # 컨텍스트 추출
        context = self.read_file_with_context(java_file, line_number)
        
        # 메타 정보 추가
        if context['success']:
            context.update({
                'class_name': class_name,
                'package': package,
                'method': method,
                'full_class': trace_info.get('full_class')
            })
            print(f"   ✓ 컨텍스트 추출 완료 (라인 {context['context_start']}-{context['context_end']})\n")
        else:
            print(f"   ✗ {context.get('error')}\n")
        
        return context
    
    def process_parsed_errors(self, parsed_json_path: str) -> Dict[str, List[Dict]]:
        """
        1단계에서 생성된 JSON 파일을 읽어서 모든 에러의 컨텍스트 추출
        
        Args:
            parsed_json_path: 1단계 결과 JSON 파일 경로
            
        Returns:
            이메일 파일별 컨텍스트 정보
        """
        print("=" * 60)
        print("[2단계] 소스코드 실시간 접근 및 컨텍스트 추출")
        print("=" * 60)
        
        # JSON 파일 읽기
        with open(parsed_json_path, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)
        
        print(f"\n📄 {len(parsed_data)}개 이메일 파일의 에러 처리 중...")
        
        # 인덱스 구축
        self.build_file_index()
        
        # 결과 저장
        all_contexts = {}
        
        for email_file, error_data in parsed_data.items():
            print(f"\n{'='*60}")
            print(f"📧 처리 중: {email_file}")
            print(f"{'='*60}")
            
            if not error_data.get('has_error'):
                print("   ℹ️  에러 없음, 건너뜀\n")
                continue
            
            contexts = []
            stack_traces = error_data.get('stack_traces', [])
            
            # 우리 프로젝트(com.hanwha.ax)의 스택만 처리
            for trace in stack_traces:
                package = trace.get('package', '')
                
                # 외부 라이브러리 제외
                if not package.startswith('com.hanwha.ax'):
                    continue
                
                # 컨텍스트 추출
                context = self.extract_context_from_trace(trace)
                contexts.append(context)
            
            all_contexts[email_file] = {
                'email_file': email_file,
                'exceptions': error_data.get('exceptions', []),
                'contexts': contexts,
                'total_traces': len(stack_traces),
                'extracted_contexts': len(contexts)
            }
        
        return all_contexts
    
    def save_contexts(self, contexts: Dict, output_file: str = "output/step2_code_contexts.json"):
        """
        추출된 컨텍스트를 JSON 파일로 저장
        
        Args:
            contexts: 컨텍스트 데이터
            output_file: 출력 파일 경로
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(contexts, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✓ 컨텍스트 추출 결과 저장 완료: {output_path}")
        print(f"{'='*60}\n")
    
    def print_summary(self, contexts: Dict):
        """추출 결과 요약 출력"""
        print("\n" + "="*60)
        print("📊 컨텍스트 추출 요약")
        print("="*60)
        
        total_emails = len(contexts)
        total_contexts = sum(len(data['contexts']) for data in contexts.values())
        successful = sum(
            sum(1 for ctx in data['contexts'] if ctx.get('success', False))
            for data in contexts.values()
        )
        failed = total_contexts - successful
        
        print(f"\n📧 처리한 이메일: {total_emails}개")
        print(f"✅ 성공적으로 추출: {successful}개")
        print(f"❌ 실패: {failed}개")
        
        if successful > 0:
            print("\n📝 추출된 컨텍스트:")
            for email_file, data in contexts.items():
                if data['extracted_contexts'] > 0:
                    print(f"\n   [{email_file}]")
                    for ctx in data['contexts']:
                        if ctx.get('success'):
                            print(f"      - {ctx['class_name']}.{ctx['method']}() "
                                  f"(라인 {ctx['context_start']}-{ctx['context_end']})")
        
        print("\n" + "="*60)


def main():
    """메인 실행 함수"""
    
    # CodeExtractor 인스턴스 생성
    extractor = CodeExtractor(
        project_root="example_project",  # Java 프로젝트 경로
        context_lines=30  # 앞뒤 30줄
    )
    
    try:
        # 1단계 결과 파일 읽어서 처리
        contexts = extractor.process_parsed_errors("output/step1_parsed_errors.json")
        
        # 요약 출력
        extractor.print_summary(contexts)
        
        # JSON 파일로 저장
        extractor.save_contexts(contexts, "output/step2_code_contexts.json")
        
        print("✅ [2단계] 완료!\n")
        print("💡 다음 단계: output/step2_code_contexts.json 파일을 확인하세요.")
        
    except FileNotFoundError as e:
        print(f"\n❌ 오류: {e}")
        print("\n💡 먼저 [1단계]를 실행하여 step1_parsed_errors.json 파일을 생성해주세요.")
        print("   실행 명령: python src/step1_email_parser.py")
    
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
