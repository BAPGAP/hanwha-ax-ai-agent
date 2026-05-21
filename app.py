"""
AI Agent 에러 분석 시스템 - Streamlit 대시보드

발표용 시각화 웹 인터페이스
실시간 진행 상황, 입출력 데이터, 워크플로우 시각화
"""

import streamlit as st
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import traceback

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))

from step1_email_parser import EmailParser
from step2_code_extractor import CodeExtractor
from step3_analysis_report import AnalysisReportGenerator


# 페이지 설정
st.set_page_config(
    page_title="AI 에러 분석 시스템",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stage-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .stage-header {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .workflow-arrow {
        text-align: center;
        font-size: 2rem;
        color: #667eea;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def show_workflow_diagram():
    """워크플로우 다이어그램 표시"""
    st.markdown("### 🔄 워크플로우")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stage-card">
            <div class="stage-header">📧 [1단계] 메일 파싱</div>
            <p><b>Input:</b> email/*.txt, *.log</p>
            <p><b>Process:</b> Stack Trace 정규표현식 파싱</p>
            <p><b>Output:</b> step1_parsed_errors.json</p>
            <p style="margin-top: 1rem;">
                ✓ 클래스명 추출<br>
                ✓ 메서드명 추출<br>
                ✓ 라인 번호 추출
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stage-card">
            <div class="stage-header">🔍 [2단계] 소스코드 추출</div>
            <p><b>Input:</b> step1_parsed_errors.json</p>
            <p><b>Process:</b> 실시간 파일 탐색 및 읽기</p>
            <p><b>Output:</b> step2_code_contexts.json</p>
            <p style="margin-top: 1rem;">
                ✓ Java 파일 찾기<br>
                ✓ 에러 라인 ±30줄<br>
                ✓ 최신 코드 반영
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stage-card">
            <div class="stage-header">🤖 [3단계] AI 분석</div>
            <p><b>Input:</b> step2_code_contexts.json</p>
            <p><b>Process:</b> LLM 분석 (Ollama/OpenAI)</p>
            <p><b>Output:</b> reports/*.md</p>
            <p style="margin-top: 1rem;">
                ✓ 원인 분석<br>
                ✓ 수정 방법<br>
                ✓ 코드 예시
            </p>
        </div>
        """, unsafe_allow_html=True)


def run_stage1(email_folder: str, status_placeholder, progress_bar):
    """1단계: 메일 파싱"""
    try:
        status_placeholder.info("📧 [1단계] 메일 파싱 중...")
        progress_bar.progress(10)
        
        parser = EmailParser(email_folder=email_folder)
        time.sleep(0.3)  # 시각적 효과
        
        progress_bar.progress(30)
        parsed_results = parser.parse_all_emails()
        
        progress_bar.progress(50)
        
        # 통계 계산
        total_files = len(parsed_results)
        total_exceptions = sum(len(r['exceptions']) for r in parsed_results.values())
        total_traces = sum(len(r['stack_traces']) for r in parsed_results.values())
        
        result = {
            "success": True,
            "total_files": total_files,
            "total_exceptions": total_exceptions,
            "total_traces": total_traces,
            "parsed_results": parsed_results
        }
        
        status_placeholder.success(f"✅ [1단계] 완료: {total_files}개 파일, {total_traces}개 Stack Trace 추출")
        return result
        
    except Exception as e:
        status_placeholder.error(f"❌ [1단계] 실패: {str(e)}")
        return {"success": False, "error": str(e)}


def run_stage2(project_root: str, context_lines: int, status_placeholder, progress_bar):
    """2단계: 소스코드 추출"""
    try:
        status_placeholder.info("🔍 [2단계] 소스코드 추출 중...")
        progress_bar.progress(60)
        
        extractor = CodeExtractor(
            project_root=project_root,
            context_lines=context_lines
        )
        time.sleep(0.3)
        
        progress_bar.progress(70)
        contexts = extractor.process_parsed_errors(
            parsed_json_path="output/step1_parsed_errors.json"
        )
        
        progress_bar.progress(80)
        
        # 통계 계산
        total_contexts = sum(c['extracted_contexts'] for c in contexts.values())
        successful = sum(1 for c in contexts.values() 
                        for ctx in c['contexts'] if ctx.get('success'))
        failed = sum(1 for c in contexts.values() 
                    for ctx in c['contexts'] if not ctx.get('success'))
        
        result = {
            "success": True,
            "total_contexts": total_contexts,
            "successful": successful,
            "failed": failed,
            "contexts": contexts
        }
        
        status_placeholder.success(f"✅ [2단계] 완료: {successful}개 성공, {failed}개 실패")
        return result
        
    except Exception as e:
        status_placeholder.error(f"❌ [2단계] 실패: {str(e)}")
        return {"success": False, "error": str(e)}


def run_stage3(llm_type: str, model_name: str, api_key: str, use_mock: bool, 
               status_placeholder, progress_bar):
    """3단계: AI 분석"""
    try:
        status_placeholder.info(f"🤖 [3단계] AI 분석 중 ({llm_type} - {model_name})...")
        progress_bar.progress(85)
        
        generator = AnalysisReportGenerator(
            llm_type=llm_type,
            model_name=model_name,
            api_key=api_key if api_key else None,
            use_mock=use_mock
        )
        time.sleep(0.3)
        
        progress_bar.progress(90)
        report_count = generator.process_all_errors(
            contexts_json_path="output/step2_code_contexts.json"
        )
        
        progress_bar.progress(100)
        
        result = {
            "success": True,
            "report_count": report_count,
            "llm_type": llm_type,
            "model_name": model_name,
            "use_mock": use_mock
        }
        
        mode_str = "Mock 모드" if use_mock else f"{llm_type} ({model_name})"
        status_placeholder.success(f"✅ [3단계] 완료: {report_count}개 리포트 생성 ({mode_str})")
        return result
        
    except Exception as e:
        status_placeholder.error(f"❌ [3단계] 실패: {str(e)}")
        return {"success": False, "error": str(e)}


def display_stage1_results(result):
    """1단계 결과 표시"""
    if not result.get("success"):
        st.error(f"오류: {result.get('error', '알 수 없는 오류')}")
        return
    
    st.markdown("### 📊 1단계 결과")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 처리된 파일", result["total_files"])
    col2.metric("⚠️ Exception 수", result["total_exceptions"])
    col3.metric("📍 Stack Trace 수", result["total_traces"])
    
    # 상세 결과
    with st.expander("📋 상세 결과 보기"):
        for file_name, data in result["parsed_results"].items():
            st.markdown(f"**{file_name}**")
            st.write(f"- Exception: {len(data['exceptions'])}개")
            st.write(f"- Stack Trace: {len(data['stack_traces'])}개")
            if data['stack_traces']:
                st.json(data['stack_traces'][0])  # 첫 번째 trace 예시


def display_stage2_results(result):
    """2단계 결과 표시"""
    if not result.get("success"):
        st.error(f"오류: {result.get('error', '알 수 없는 오류')}")
        return
    
    st.markdown("### 📊 2단계 결과")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🔍 추출 시도", result["total_contexts"])
    col2.metric("✅ 성공", result["successful"], delta=None)
    col3.metric("❌ 실패", result["failed"], delta=None if result["failed"] == 0 else -result["failed"])
    
    # 상세 결과
    with st.expander("📋 상세 결과 보기"):
        for email_file, data in result["contexts"].items():
            st.markdown(f"**{email_file}**")
            for ctx in data['contexts']:
                if ctx.get('success'):
                    st.success(f"✅ {ctx['class_name']}.{ctx['method']}() - 라인 {ctx['context_start']}-{ctx['context_end']}")
                else:
                    st.error(f"❌ {ctx['class_name']}.{ctx['method']}() - {ctx.get('error', '실패')}")


def display_stage3_results(result):
    """3단계 결과 표시"""
    if not result.get("success"):
        st.error(f"오류: {result.get('error', '알 수 없는 오류')}")
        return
    
    st.markdown("### 📊 3단계 결과")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📝 생성된 리포트", result["report_count"])
    col2.metric("🤖 LLM", result["llm_type"])
    col3.metric("📦 모델", result["model_name"])
    
    if result["use_mock"]:
        st.warning("⚠️ Mock 모드로 실행됨 (데모용 분석)")
    
    # 생성된 리포트 목록
    reports_dir = Path("reports")
    if reports_dir.exists():
        report_files = list(reports_dir.glob("*.md"))
        
        if report_files:
            st.markdown("### 📁 생성된 리포트")
            
            selected_report = st.selectbox(
                "리포트 선택",
                [f.name for f in report_files]
            )
            
            if selected_report:
                report_path = reports_dir / selected_report
                with open(report_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                
                st.markdown("---")
                st.markdown(report_content)


def main():
    """메인 함수"""
    
    # 헤더
    st.markdown('<h1 class="main-header">🤖 AI Agent 에러 분석 시스템</h1>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # 워크플로우 다이어그램
    show_workflow_diagram()
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        st.subheader("📂 프로젝트 설정")
        project_root = st.text_input(
            "Java 프로젝트 경로",
            value="example_project",
            help="분석할 Java 프로젝트의 루트 디렉토리"
        )
        
        email_folder = st.text_input(
            "이메일 폴더",
            value="email",
            help="에러 메일/로그 파일이 있는 폴더"
        )
        
        context_lines = st.slider(
            "컨텍스트 라인 수",
            min_value=10,
            max_value=100,
            value=30,
            help="에러 라인 기준 앞뒤로 추출할 라인 수"
        )
        
        st.markdown("---")
        st.subheader("🤖 LLM 설정")
        
        llm_type = st.selectbox(
            "LLM 타입",
            ["mock", "ollama", "openai"],
            help="Mock: 데모용, Ollama: 로컬, OpenAI: 클라우드"
        )
        
        if llm_type == "ollama":
            model_name = st.selectbox(
                "Ollama 모델",
                ["qwen2.5:7b", "codellama", "llama3", "mistral"]
            )
            api_key = None
            use_mock = False
        elif llm_type == "openai":
            model_name = st.selectbox(
                "OpenAI 모델",
                ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
            )
            api_key = st.text_input(
                "API Key",
                type="password",
                help="OpenAI API 키"
            )
            use_mock = False
        else:  # mock
            model_name = "mock-model"
            api_key = None
            use_mock = True
        
        st.markdown("---")
        st.info("""
        💡 **사용 방법**
        1. 설정 확인
        2. '🚀 전체 실행' 버튼 클릭
        3. 실시간 진행 상황 확인
        4. 생성된 리포트 확인
        """)
    
    # 메인 컨텐츠
    st.header("📊 실행 현황")
    
    # 상태 표시 영역
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    # 결과 저장용 세션 상태
    if 'results' not in st.session_state:
        st.session_state.results = {}
    
    # 실행 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 전체 실행", use_container_width=True, type="primary"):
            start_time = time.time()
            
            st.session_state.results = {}
            
            # 1단계 실행
            result1 = run_stage1(email_folder, status_placeholder, progress_bar)
            st.session_state.results['stage1'] = result1
            
            if result1.get("success"):
                # 2단계 실행
                result2 = run_stage2(project_root, context_lines, status_placeholder, progress_bar)
                st.session_state.results['stage2'] = result2
                
                if result2.get("success"):
                    # 3단계 실행
                    result3 = run_stage3(llm_type, model_name, api_key, use_mock, 
                                        status_placeholder, progress_bar)
                    st.session_state.results['stage3'] = result3
            
            elapsed = time.time() - start_time
            
            if all(st.session_state.results.get(f'stage{i}', {}).get("success") for i in [1,2,3]):
                status_placeholder.success(f"🎉 전체 프로세스 완료! (소요 시간: {elapsed:.2f}초)")
                st.balloons()
            else:
                status_placeholder.error("❌ 일부 단계 실패")
    
    # 결과 표시
    if st.session_state.results:
        st.markdown("---")
        st.header("📈 실행 결과")
        
        tabs = st.tabs(["1단계 결과", "2단계 결과", "3단계 결과"])
        
        with tabs[0]:
            if 'stage1' in st.session_state.results:
                display_stage1_results(st.session_state.results['stage1'])
        
        with tabs[1]:
            if 'stage2' in st.session_state.results:
                display_stage2_results(st.session_state.results['stage2'])
        
        with tabs[2]:
            if 'stage3' in st.session_state.results:
                display_stage3_results(st.session_state.results['stage3'])
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🤖 AI Agent 에러 분석 시스템 v1.0</p>
        <p>한화 AX | Powered by Python + Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
