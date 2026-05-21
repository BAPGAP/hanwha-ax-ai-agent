"""
[1단계] 메일 파서 사용 예시 및 테스트

이 스크립트는 step1_email_parser.py의 다양한 사용 방법을 보여줍니다.
"""

import sys
sys.path.append('src')

from step1_email_parser import EmailParser
import json


def example1_parse_single_email():
    """예시 1: 단일 이메일 파일 파싱"""
    print("\n" + "="*60)
    print("예시 1: 단일 이메일 파일 파싱")
    print("="*60)
    
    parser = EmailParser()
    
    # 단일 파일 읽기
    email_text = parser.read_email_file("email/sample_error.txt")
    
    # 파싱
    result = parser.parse_email(email_text)
    
    # 결과 출력
    print(f"\n✅ 에러 발견 여부: {result['has_error']}")
    print(f"📊 Exception 개수: {len(result['exceptions'])}")
    print(f"📊 Stack Trace 개수: {len(result['stack_traces'])}")
    
    if result['exceptions']:
        print("\n🔴 발견된 Exception:")
        for exc in result['exceptions']:
            print(f"   - {exc['exception']}: {exc['message']}")
    
    if result['stack_traces']:
        print("\n📍 Stack Trace 정보:")
        for i, trace in enumerate(result['stack_traces'][:3], 1):  # 최대 3개만 표시
            print(f"   {i}. {trace['class_name']}.{trace['method']}()")
            print(f"      파일: {trace['file']}, 라인: {trace['line']}")


def example2_parse_all_emails():
    """예시 2: 폴더 내 모든 이메일 파싱"""
    print("\n" + "="*60)
    print("예시 2: 폴더 내 모든 이메일 파싱")
    print("="*60)
    
    parser = EmailParser()
    
    # 모든 이메일 파싱
    all_results = parser.parse_all_emails()
    
    print(f"\n📧 총 {len(all_results)}개 파일 파싱 완료\n")
    
    # 각 파일별 요약
    for filename, result in all_results.items():
        print(f"📄 {filename}")
        print(f"   에러: {'있음' if result['has_error'] else '없음'}")
        
        if result['has_error'] and result['stack_traces']:
            first_trace = result['stack_traces'][0]
            print(f"   메인 에러: {first_trace['class_name']}.{first_trace['method']}() 라인 {first_trace['line']}")


def example3_extract_error_locations():
    """예시 3: 에러 발생 위치만 추출"""
    print("\n" + "="*60)
    print("예시 3: 에러 발생 위치만 추출하여 리스트화")
    print("="*60)
    
    parser = EmailParser()
    all_results = parser.parse_all_emails()
    
    # 모든 에러 위치를 하나의 리스트로 통합
    error_locations = []
    
    for filename, result in all_results.items():
        if result['has_error'] and result['stack_traces']:
            # 첫 번째 stack trace만 추출 (실제 에러 발생 위치)
            first_trace = result['stack_traces'][0]
            error_locations.append({
                'source_file': filename,
                'class': first_trace['class_name'],
                'method': first_trace['method'],
                'java_file': first_trace['file'],
                'line': first_trace['line'],
                'package': first_trace['package']
            })
    
    print(f"\n🎯 추출된 에러 위치: {len(error_locations)}개\n")
    
    for i, loc in enumerate(error_locations, 1):
        print(f"{i}. [{loc['source_file']}]")
        print(f"   → {loc['package']}.{loc['class']}")
        print(f"   → {loc['method']}() at {loc['java_file']}:{loc['line']}\n")
    
    return error_locations


def example4_filter_by_package():
    """예시 4: 특정 패키지의 에러만 필터링"""
    print("\n" + "="*60)
    print("예시 4: 특정 패키지(com.hanwha.ax)의 에러만 필터링")
    print("="*60)
    
    parser = EmailParser()
    all_results = parser.parse_all_emails()
    
    target_package = "com.hanwha.ax"
    filtered_traces = []
    
    for filename, result in all_results.items():
        if result['has_error']:
            for trace in result['stack_traces']:
                if trace['package'].startswith(target_package):
                    filtered_traces.append({
                        'file': filename,
                        'class': trace['full_class'],
                        'method': trace['method'],
                        'line': trace['line']
                    })
    
    print(f"\n🔍 {target_package} 패키지의 에러: {len(filtered_traces)}개\n")
    
    for trace in filtered_traces:
        print(f"📌 {trace['class']}.{trace['method']}() - 라인 {trace['line']}")
        print(f"   출처: {trace['file']}\n")


def example5_generate_summary_report():
    """예시 5: 에러 요약 리포트 생성"""
    print("\n" + "="*60)
    print("예시 5: 에러 요약 리포트 생성")
    print("="*60)
    
    parser = EmailParser()
    all_results = parser.parse_all_emails()
    
    # 통계 수집
    total_files = len(all_results)
    files_with_errors = sum(1 for r in all_results.values() if r['has_error'])
    total_exceptions = sum(len(r['exceptions']) for r in all_results.values())
    total_traces = sum(len(r['stack_traces']) for r in all_results.values())
    
    # Exception 타입별 카운트
    exception_types = {}
    for result in all_results.values():
        for exc in result['exceptions']:
            exc_type = exc['exception'].split('.')[-1]  # 짧은 이름만
            exception_types[exc_type] = exception_types.get(exc_type, 0) + 1
    
    # 리포트 출력
    print("\n" + "="*60)
    print("📊 에러 분석 요약 리포트")
    print("="*60)
    print(f"\n📁 분석 파일 수: {total_files}개")
    print(f"⚠️  에러 포함 파일: {files_with_errors}개")
    print(f"🔴 총 Exception 수: {total_exceptions}개")
    print(f"📍 총 Stack Trace 수: {total_traces}개")
    
    print("\n🏷️  Exception 타입별 통계:")
    for exc_type, count in sorted(exception_types.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {exc_type}: {count}회")
    
    # 가장 많이 등장하는 클래스
    class_count = {}
    for result in all_results.values():
        for trace in result['stack_traces']:
            if trace['package'].startswith('com.hanwha.ax'):  # 우리 프로젝트만
                class_count[trace['class_name']] = class_count.get(trace['class_name'], 0) + 1
    
    if class_count:
        print("\n🎯 에러 발생 빈도가 높은 클래스 (Top 5):")
        for cls, count in sorted(class_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {cls}: {count}회")
    
    print("\n" + "="*60)


def main():
    """모든 예시 실행"""
    print("\n" + "🔥"*30)
    print("     [1단계] 메일 파서 사용 예시 모음")
    print("🔥"*30)
    
    try:
        example1_parse_single_email()
        example2_parse_all_emails()
        example3_extract_error_locations()
        example4_filter_by_package()
        example5_generate_summary_report()
        
        print("\n✅ 모든 예시 실행 완료!")
        print("\n💡 Tip: 이 코드를 참고하여 원하는 방식으로 파서를 활용할 수 있습니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
