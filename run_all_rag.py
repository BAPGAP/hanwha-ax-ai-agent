r"""
RAG 기반 전체 3단계 통합 실행 스크립트

현업에서 정확한 라인 번호나 클래스명이 없는 에러에도 대응 가능!
의미 기반 검색으로 관련 코드를 자동으로 찾아줍니다.

사용법:
    # 기본 실행 (Mock 모드)
    python run_all_rag.py
    
    # 실제 Java 프로젝트
    python run_all_rag.py --project "C:\workspace\backend"
    
    # Ollama로 실제 AI 분석
    python run_all_rag.py --llm ollama
    
    # 벡터 DB 재생성
    python run_all_rag.py --reindex
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

from step1_email_parser import EmailParser
from step2_rag_extractor import RAGCodeExtractor
from step3_rag_analysis import RAGAnalysisReportGenerator


def print_header(stage: int, title: str):
    """단계 헤더"""
    print("\n" + "=" * 70)
    print(f"  [{stage}단계] {title}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="RAG 기반 Java 에러 분석 AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--project", default="example_project", help="Java 프로젝트 경로")
    parser.add_argument("--email", default="email", help="이메일 폴더")
    parser.add_argument("--llm", choices=["mock", "ollama", "openai"], default="mock", help="LLM 타입")
    parser.add_argument("--model", default="qwen2.5:7b", help="모델 이름")
    parser.add_argument("--api-key", help="OpenAI API 키")
    parser.add_argument("--chunk-size", type=int, default=500, help="코드 청크 크기")
    parser.add_argument("--top-k", type=int, default=5, help="검색할 상위 결과 수")
    parser.add_argument("--reindex", action="store_true", help="벡터 DB 재생성")
    
    args = parser.parse_args()
    
    start_time = datetime.now()
    
    print("\n" + "🤖" * 35)
    print("  RAG 기반 Java 에러 분석 AI Agent")
    print("🤖" * 35)
    print(f"\n⏰ 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 프로젝트: {args.project}")
    print(f"📧 이메일: {args.email}")
    print(f"🤖 LLM: {args.llm} ({args.model})")
    print(f"📊 청크 크기: {args.chunk_size}, Top-K: {args.top_k}")
    
    # 1단계: 이메일 파싱
    print_header(1, "메일 파싱")
    parser_obj = EmailParser(email_folder=args.email)
    parsed_results = parser_obj.parse_all_emails()
    print(f"✅ {len(parsed_results)}개 파일 파싱 완료")
    
    # 2단계: RAG 기반 코드 검색
    print_header(2, "RAG 기반 코드 검색")
    extractor = RAGCodeExtractor(
        project_root=args.project,
        chunk_size=args.chunk_size,
        top_k=args.top_k
    )
    
    # 재인덱싱 옵션
    if args.reindex and Path(extractor.vector_db_path).exists():
        print("🔄 기존 벡터 DB 삭제 중...")
        import shutil
        shutil.rmtree(extractor.vector_db_path)
        print("✅ 삭제 완료\n")
    
    rag_results = extractor.process_parsed_errors()
    print(f"✅ RAG 검색 완료")
    
    # 3단계: AI 분석
    print_header(3, "AI 분석 리포트 생성")
    use_mock = args.llm == "mock"
    generator = RAGAnalysisReportGenerator(
        llm_type=args.llm,
        model_name=args.model,
        api_key=args.api_key,
        use_mock=use_mock
    )
    
    report_count = generator.process_all_errors()
    
    end_time = datetime.now()
    elapsed = end_time - start_time
    
    print("\n" + "🎉" * 35)
    print("  전체 프로세스 완료!")
    print("🎉" * 35)
    print(f"\n⏰ 종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  소요 시간: {elapsed.total_seconds():.2f}초")
    print(f"\n📊 결과:")
    print(f"   - 이메일: {len(parsed_results)}개")
    print(f"   - 리포트: {report_count}개")
    print(f"\n📁 생성 파일:")
    print(f"   - output/step1_parsed_errors.json")
    print(f"   - output/step2_rag_contexts.json")
    print(f"   - reports/RAG_분석_리포트_*.md")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  실행 중단")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
