"""
[2단계] 코드 추출기 사용 예시

step2_code_extractor.py의 다양한 사용 방법을 보여줍니다.
"""

import sys
sys.path.append('src')

from step2_code_extractor import CodeExtractor
import json


def example1_extract_single_error():
    """예시 1: 단일 에러의 컨텍스트 추출"""
    print("\n" + "="*60)
    print("예시 1: 단일 에러 위치의 소스코드 컨텍스트 추출")
    print("="*60)
    
    extractor = CodeExtractor(project_root="example_project", context_lines=30)
    
    # 가상의 stack trace 정보
    trace_info = {
        'class_name': 'CustomerService',
        'package': 'com.hanwha.ax.service',
        'file': 'CustomerService.java',
        'line': 145,
        'method': 'validateCustomerData',
        'full_class': 'com.hanwha.ax.service.CustomerService'
    }
    
    print(f"\n🎯 타겟: {trace_info['class_name']}.{trace_info['method']}() at line {trace_info['line']}\n")
    
    # 컨텍스트 추출
    context = extractor.extract_context_from_trace(trace_info)
    
    if context['success']:
        print("✅ 추출 성공!")
        print(f"   파일: {context['file_path']}")
        print(f"   전체 라인 수: {context['total_lines']}")
        print(f"   추출 범위: {context['context_start']}-{context['context_end']}")
        print(f"\n📝 에러 라인 주변 코드:")
        
        # 에러 라인 주변 5줄만 출력
        error_line = context['error_line']
        for line in context['context_lines']:
            if abs(line['line_number'] - error_line) <= 2:
                marker = ">>> " if line['is_error_line'] else "    "
                print(f"{marker}{line['line_number']:3d}: {line['content']}")
    else:
        print(f"❌ 실패: {context.get('error')}")


def example2_extract_from_json():
    """예시 2: 1단계 JSON에서 직접 추출"""
    print("\n" + "="*60)
    print("예시 2: 1단계 JSON 파일에서 자동으로 추출")
    print("="*60)
    
    extractor = CodeExtractor(project_root="example_project")
    
    # 1단계 JSON 읽기
    with open("output/step1_parsed_errors.json", 'r', encoding='utf-8') as f:
        parsed_data = json.load(f)
    
    print(f"\n📄 {len(parsed_data)}개 이메일 파일 발견\n")
    
    # 첫 번째 이메일의 첫 번째 에러만 처리
    first_email = list(parsed_data.keys())[0]
    first_error = parsed_data[first_email]
    
    if first_error['has_error'] and first_error['stack_traces']:
        trace = first_error['stack_traces'][0]
        
        print(f"📧 이메일: {first_email}")
        print(f"🐛 Exception: {first_error['exceptions'][0]['exception']}")
        print(f"🎯 위치: {trace['class_name']}.{trace['method']}() line {trace['line']}\n")
        
        context = extractor.extract_context_from_trace(trace)
        
        if context['success']:
            print(f"✅ 소스코드 추출 완료!")
            print(f"   추출된 라인 수: {len(context['context_lines'])}줄")


def example3_filter_successful_extractions():
    """예시 3: 성공적으로 추출된 컨텍스트만 필터링"""
    print("\n" + "="*60)
    print("예시 3: 성공한 컨텍스트만 필터링")
    print("="*60)
    
    # 2단계 결과 읽기
    with open("output/step2_code_contexts.json", 'r', encoding='utf-8') as f:
        contexts = json.load(f)
    
    successful_extractions = []
    
    for email_file, data in contexts.items():
        for ctx in data['contexts']:
            if ctx.get('success', False):
                successful_extractions.append({
                    'email': email_file,
                    'class': ctx['class_name'],
                    'method': ctx['method'],
                    'line': ctx['error_line'],
                    'file': ctx['file_path']
                })
    
    print(f"\n✅ 성공적으로 추출된 컨텍스트: {len(successful_extractions)}개\n")
    
    for i, ext in enumerate(successful_extractions, 1):
        print(f"{i}. [{ext['email']}]")
        print(f"   {ext['class']}.{ext['method']}() at line {ext['line']}")
        print(f"   파일: {ext['file']}\n")


def example4_display_error_code():
    """예시 4: 에러 발생 라인의 실제 코드 출력"""
    print("\n" + "="*60)
    print("예시 4: 에러 라인의 실제 코드 표시")
    print("="*60)
    
    # 2단계 결과 읽기
    with open("output/step2_code_contexts.json", 'r', encoding='utf-8') as f:
        contexts = json.load(f)
    
    print("\n🐛 발견된 에러 코드:\n")
    
    for email_file, data in contexts.items():
        for ctx in data['contexts']:
            if ctx.get('success', False):
                # 에러 라인 찾기
                error_line_obj = next(
                    (line for line in ctx['context_lines'] if line['is_error_line']),
                    None
                )
                
                if error_line_obj:
                    print(f"📄 파일: {ctx['class_name']}.java")
                    print(f"📍 라인 {error_line_obj['line_number']}:")
                    print(f"   >>> {error_line_obj['content']}")
                    print()


def example5_generate_code_snippets():
    """예시 5: LLM에 전달할 코드 스니펫 생성"""
    print("\n" + "="*60)
    print("예시 5: LLM 프롬프트용 코드 스니펫 생성")
    print("="*60)
    
    # 2단계 결과 읽기
    with open("output/step2_code_contexts.json", 'r', encoding='utf-8') as f:
        contexts = json.load(f)
    
    print("\n📋 3단계(LLM 분석)에 전달할 형식:\n")
    
    for email_file, data in contexts.items():
        if data['extracted_contexts'] == 0:
            continue
        
        print(f"{'='*60}")
        print(f"📧 이메일: {email_file}")
        print(f"{'='*60}\n")
        
        # Exception 정보
        if data['exceptions']:
            print("🔴 Exception:")
            for exc in data['exceptions']:
                print(f"   {exc['exception']}: {exc['message']}")
            print()
        
        # 각 컨텍스트의 코드
        for ctx in data['contexts']:
            if not ctx.get('success'):
                continue
            
            print(f"📍 {ctx['class_name']}.{ctx['method']}() - Line {ctx['error_line']}")
            print(f"   파일: {ctx['file_path']}")
            print(f"\n```java")
            print(f"// 라인 {ctx['context_start']}-{ctx['context_end']}")
            
            # 에러 라인 강조하여 출력
            for line in ctx['context_lines'][:15]:  # 처음 15줄만
                marker = ">>> " if line['is_error_line'] else "    "
                print(f"{marker}{line['content']}")
            
            if len(ctx['context_lines']) > 15:
                print(f"    ... ({len(ctx['context_lines']) - 15}줄 더 있음)")
            
            print("```\n")


def example6_custom_context_size():
    """예시 6: 커스텀 컨텍스트 크기로 추출"""
    print("\n" + "="*60)
    print("예시 6: 앞뒤 10줄만 추출 (커스텀 크기)")
    print("="*60)
    
    # 앞뒤 10줄만 추출
    extractor = CodeExtractor(project_root="example_project", context_lines=10)
    
    trace_info = {
        'class_name': 'CustomerService',
        'package': 'com.hanwha.ax.service',
        'file': 'CustomerService.java',
        'line': 145,
        'method': 'validateCustomerData',
        'full_class': 'com.hanwha.ax.service.CustomerService'
    }
    
    context = extractor.extract_context_from_trace(trace_info)
    
    if context['success']:
        print(f"\n✅ 추출 완료!")
        print(f"   추출 범위: 라인 {context['context_start']}-{context['context_end']}")
        print(f"   총 {len(context['context_lines'])}줄")
        print(f"\n💡 context_lines 매개변수를 조정하여 원하는 크기로 추출 가능!")


def main():
    """모든 예시 실행"""
    print("\n" + "🔥"*30)
    print("     [2단계] 코드 추출기 사용 예시 모음")
    print("🔥"*30)
    
    try:
        example1_extract_single_error()
        example2_extract_from_json()
        example3_filter_successful_extractions()
        example4_display_error_code()
        example5_generate_code_snippets()
        example6_custom_context_size()
        
        print("\n" + "="*60)
        print("✅ 모든 예시 실행 완료!")
        print("="*60)
        print("\n💡 Tip: 이 코드를 참고하여 원하는 방식으로 추출기를 활용할 수 있습니다.")
        print("💡 3단계에서는 이 컨텍스트를 LLM에 전달하여 분석합니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
