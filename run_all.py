r"""
전체 3단계 AI Agent 통합 실행 스크립트

이메일 파싱 → 소스코드 추출 → AI 분석 리포트 생성을 한 번에 실행합니다.

사용법:
    # 기본 실행 (example_project 사용)
    python run_all.py
    
    # 실제 Java 프로젝트 경로 지정
    python run_all.py --project "C:\workspace\hanwha-ax-backend"
    
    # Mock 모드로 실행 (Ollama 없이 테스트)
    python run_all.py --mock
    
    # OpenAI 사용
    python run_all.py --llm openai --model gpt-4
    
    # Ollama 사용 (기본)
    python run_all.py --llm ollama --model qwen2.5:7b
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))

from step1_email_parser import EmailParser
from step2_code_extractor import CodeExtractor
from step3_analysis_report import AnalysisReportGenerator


def print_header(stage: int, title: str):
    """단계 헤더 출력"""
    print("\n" + "=" * 70)
    print(f"  [{stage}단계] {title}")
    print("=" * 70 + "\n")


def print_success(message: str):
    """성공 메시지 출력"""
    print(f"✅ {message}")


def print_error(message: str):
    """에러 메시지 출력"""
    print(f"❌ {message}")


def print_info(message: str):
    """정보 메시지 출력"""
    print(f"ℹ️  {message}")


def run_stage1(email_folder: str = "email") -> bool:
    """
    1단계: 메일 파싱 및 에러 키워드 추출
    
    Returns:
        bool: 성공 여부
    """
    print_header(1, "메일 파싱 및 에러 키워드 추출")
    
    try:
        parser = EmailParser(email_folder=email_folder)
        parsed_results = parser.parse_all_emails()
        
        # 통계 출력
        total_files = len(parsed_results)
        total_exceptions = sum(len(r['exceptions']) for r in parsed_results.values())
        total_traces = sum(len(r['stack_traces']) for r in parsed_results.values())
        
        print_success(f"{total_files}개 파일 파싱 완료")
        print_info(f"발견된 Exception: {total_exceptions}개")
        print_info(f"발견된 Stack Trace: {total_traces}개")
        print_info("출력: output/step1_parsed_errors.json")
        
        return True
        
    except Exception as e:
        print_error(f"1단계 실행 중 오류 발생: {e}")
        return False


def run_stage2(project_root: str = "example_project", context_lines: int = 30) -> bool:
    """
    2단계: 소스코드 실시간 접근 및 컨텍스트 추출
    
    Args:
        project_root: Java 프로젝트 루트 디렉토리
        context_lines: 에러 라인 기준 앞뒤로 추출할 라인 수
        
    Returns:
        bool: 성공 여부
    """
    print_header(2, "소스코드 실시간 접근 및 컨텍스트 추출")
    
    try:
        extractor = CodeExtractor(
            project_root=project_root,
            context_lines=context_lines
        )
        
        contexts = extractor.process_parsed_errors(
            parsed_json_path="output/step1_parsed_errors.json"
        )
        
        # 통계 출력
        total_contexts = sum(c['extracted_contexts'] for c in contexts.values())
        successful = sum(1 for c in contexts.values() 
                        for ctx in c['contexts'] if ctx.get('success'))
        failed = sum(1 for c in contexts.values() 
                    for ctx in c['contexts'] if not ctx.get('success'))
        
        print_success(f"{total_contexts}개 컨텍스트 추출 완료")
        print_info(f"성공: {successful}개, 실패: {failed}개")
        print_info("출력: output/step2_code_contexts.json")
        
        if failed > 0:
            print_info(f"일부 파일을 찾을 수 없습니다 (프로젝트 경로: {project_root})")
        
        return True
        
    except Exception as e:
        print_error(f"2단계 실행 중 오류 발생: {e}")
        return False


def run_stage3(
    llm_type: str = "mock",
    model_name: str = "qwen2.5:7b",
    api_key: str = None,
    use_mock: bool = True
) -> bool:
    """
    3단계: 원인 분석 및 수정 제안 리포트 생성
    
    Args:
        llm_type: LLM 타입 (ollama, openai, mock)
        model_name: 모델 이름
        api_key: API 키 (OpenAI 사용 시)
        use_mock: Mock 모드 사용 여부
        
    Returns:
        bool: 성공 여부
    """
    print_header(3, "원인 분석 및 수정 제안 리포트 생성")
    
    try:
        generator = AnalysisReportGenerator(
            llm_type=llm_type,
            model_name=model_name,
            api_key=api_key,
            use_mock=use_mock
        )
        
        report_count = generator.process_all_errors(
            contexts_json_path="output/step2_code_contexts.json"
        )
        
        print_success(f"{report_count}개 리포트 생성 완료")
        print_info("출력: reports/*.md")
        
        if use_mock:
            print_info("⚠️  Mock 모드로 실행됨 (실제 LLM 미사용)")
            print_info("실제 AI 분석을 원하면 --llm 옵션을 사용하세요")
        
        return True
        
    except Exception as e:
        print_error(f"3단계 실행 중 오류 발생: {e}")
        return False


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="3단계 Java 에러 분석 AI Agent 통합 실행",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 기본 실행 (Mock 모드)
  python run_all.py
  
  # 실제 프로젝트 분석
  python run_all.py --project "C:\\workspace\\hanwha-ax-backend"
  
  # Ollama 사용
  python run_all.py --llm ollama --model qwen2.5:7b
  
  # OpenAI 사용
  python run_all.py --llm openai --model gpt-4 --api-key YOUR_KEY
        """
    )
    
    # 인자 정의
    parser.add_argument(
        "--project",
        default="example_project",
        help="Java 프로젝트 루트 디렉토리 경로 (기본: example_project)"
    )
    
    parser.add_argument(
        "--email",
        default="email",
        help="이메일/로그 파일이 있는 폴더 (기본: email)"
    )
    
    parser.add_argument(
        "--context-lines",
        type=int,
        default=30,
        help="에러 라인 기준 추출할 앞뒤 라인 수 (기본: 30)"
    )
    
    parser.add_argument(
        "--llm",
        choices=["mock", "ollama", "openai"],
        default="mock",
        help="사용할 LLM 타입 (기본: mock)"
    )
    
    parser.add_argument(
        "--model",
        default="qwen2.5:7b",
        help="LLM 모델 이름 (기본: qwen2.5:7b)"
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI API 키 (OpenAI 사용 시 필수)"
    )
    
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Mock 모드로 실행 (실제 LLM 미사용)"
    )
    
    parser.add_argument(
        "--skip-stage1",
        action="store_true",
        help="1단계 건너뛰기 (이미 실행한 경우)"
    )
    
    parser.add_argument(
        "--skip-stage2",
        action="store_true",
        help="2단계 건너뛰기 (이미 실행한 경우)"
    )
    
    args = parser.parse_args()
    
    # 시작 시간 기록
    start_time = datetime.now()
    
    print("\n" + "🚀" * 35)
    print("  Java 에러 분석 AI Agent - 전체 실행")
    print("🚀" * 35)
    print(f"\n⏰ 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 프로젝트 경로: {args.project}")
    print(f"📧 이메일 폴더: {args.email}")
    print(f"🤖 LLM: {args.llm} ({args.model})")
    
    # Mock 모드 결정
    use_mock = args.mock or args.llm == "mock"
    
    success = True
    
    # 1단계 실행
    if not args.skip_stage1:
        if not run_stage1(email_folder=args.email):
            print_error("1단계 실패. 실행을 중단합니다.")
            sys.exit(1)
    else:
        print_info("1단계 건너뛰기")
    
    # 2단계 실행
    if not args.skip_stage2:
        if not run_stage2(
            project_root=args.project,
            context_lines=args.context_lines
        ):
            print_error("2단계 실패. 실행을 중단합니다.")
            sys.exit(1)
    else:
        print_info("2단계 건너뛰기")
    
    # 3단계 실행
    if not run_stage3(
        llm_type=args.llm,
        model_name=args.model,
        api_key=args.api_key,
        use_mock=use_mock
    ):
        print_error("3단계 실패. 실행을 중단합니다.")
        sys.exit(1)
    
    # 종료 시간 및 소요 시간 계산
    end_time = datetime.now()
    elapsed = end_time - start_time
    
    print("\n" + "🎉" * 35)
    print("  전체 프로세스 완료!")
    print("🎉" * 35)
    print(f"\n⏰ 종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  소요 시간: {elapsed.total_seconds():.2f}초")
    print("\n📊 생성된 파일:")
    print("   - output/step1_parsed_errors.json")
    print("   - output/step2_code_contexts.json")
    print("   - reports/*.md")
    print("\n💡 리포트를 확인하세요:")
    print("   explorer reports  (Windows)")
    print("   open reports      (Mac)")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 실행을 중단했습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
