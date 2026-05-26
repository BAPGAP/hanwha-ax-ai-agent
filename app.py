"""
AI Agent 에러 분석 시스템 - Streamlit 대시보드

발표용 시각화 웹 인터페이스
실시간 진행 상황, 입출력 데이터, 워크플로우 시각화
"""

import streamlit as st
import sys
import json
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Union
import traceback
import tkinter as tk
from tkinter import filedialog

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass

_GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))


def open_folder_dialog(session_key: str, title: str = "폴더 선택"):
    """OS 기본 폴더 선택 다이얼로그 (tkinter)"""
    try:
        current = st.session_state.get(session_key, str(Path.cwd()))
        initial = os.path.abspath(current) if os.path.exists(current) else str(Path.cwd())

        root = tk.Tk()
        root.withdraw()                    # 메인 창 숨김
        root.wm_attributes('-topmost', True)  # 최상단 표시
        folder = filedialog.askdirectory(
            parent=root,
            initialdir=initial,
            title=title
        )
        root.destroy()
        if folder:
            st.session_state[session_key] = folder
    except Exception as e:
        st.error(f"폴더 선택 오류: {e}")


def folder_picker(label: str, session_key: str, default: str, help_text: str = ""):
    """폴더 선택 위젯: 경로 표시 + 찾아보기 버튼"""
    if session_key not in st.session_state:
        st.session_state[session_key] = default

    st.markdown(f"**{label}**")
    col_input, col_btn = st.columns([5, 1])

    with col_input:
        # 경로를 직접 수정할 수 있는 텍스트 입력
        typed = st.text_input(
            label,
            value=st.session_state[session_key],
            label_visibility="collapsed",
            help=help_text,
            key=f"{session_key}_text"
        )
        st.session_state[session_key] = typed

    with col_btn:
        st.markdown("<div style='margin-top:4px'>", unsafe_allow_html=True)
        if st.button("📁", key=f"{session_key}_btn",
                     help="폴더 탐색기 열기 (더블클릭으로 탐색)",
                     use_container_width=True):
            open_folder_dialog(session_key, label)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 경로 유효성 표시
    selected = st.session_state[session_key]
    if selected and Path(selected).exists():
        st.caption(f"✅ {Path(selected).resolve()}")
    elif selected:
        st.caption(f"⚠️ 경로를 찾을 수 없음: {selected}")

    return st.session_state[session_key]


def email_picker() -> Union[str, list]:
    """
    이메일/로그 파일 선택 위젯
    - 📁 폴더 모드: 폴더 내 모든 지원 파일 자동 탐색
    - 📄 파일 모드: 개별 파일 다중 선택 (.eml/.log/.txt 등)
    반환값: 폴더 경로(str) 또는 파일 경로 목록(list)
    """
    SUPPORTED_EXT = ['.eml', '.log', '.txt', '.msg', '.csv', '.xml', '.json', '.err']

    st.markdown("**📧 이메일 / 로그 파일**")
    mode = st.radio(
        "입력 방식",
        ["📁 폴더 전체", "📄 개별 파일 선택"],
        key="email_mode",
        horizontal=True
    )

    if mode == "📁 폴더 전체":
        if 'email_folder' not in st.session_state:
            st.session_state['email_folder'] = str(Path(__file__).parent / "email")

        col_in, col_btn = st.columns([5, 1])
        with col_in:
            typed = st.text_input(
                "이메일 폴더",
                value=st.session_state['email_folder'],
                label_visibility="collapsed",
                key="email_folder_text"
            )
            st.session_state['email_folder'] = typed
        with col_btn:
            if st.button("📁", key="email_folder_btn",
                         help="폴더 탐색기 열기", use_container_width=True):
                open_folder_dialog('email_folder', "이메일/로그 폴더 선택")
                st.rerun()

        selected = st.session_state['email_folder']
        if selected and Path(selected).exists():
            found = [f for f in Path(selected).rglob('*')
                     if f.is_file() and f.suffix.lower() in SUPPORTED_EXT]
            st.caption(f"✅ {len(found)}개 파일 감지됨 ({', '.join(SUPPORTED_EXT)})")
            for f in found[:8]:
                st.caption(f"  • {f.name}")
            if len(found) > 8:
                st.caption(f"  … 외 {len(found)-8}개")
        elif selected:
            st.caption(f"⚠️ 경로를 찾을 수 없음: {selected}")

        return st.session_state['email_folder']

    else:  # 개별 파일 선택
        if 'email_files' not in st.session_state:
            st.session_state['email_files'] = []

        if st.button("📄 파일 추가", key="email_add_btn",
                     help="다중 선택 가능", use_container_width=True):
            try:
                root = tk.Tk()
                root.withdraw()
                root.wm_attributes('-topmost', True)
                chosen = filedialog.askopenfilenames(
                    parent=root,
                    title="이메일/로그 파일 선택 (Ctrl/Shift로 다중 선택)",
                    filetypes=[
                        ("이메일/로그 파일", "*.eml *.log *.txt *.msg *.csv *.xml *.err"),
                        ("EML (이메일)", "*.eml"),
                        ("로그 파일", "*.log"),
                        ("텍스트 파일", "*.txt"),
                        ("모든 파일", "*.*"),
                    ]
                )
                root.destroy()
                if chosen:
                    existing = set(st.session_state['email_files'])
                    for f in chosen:
                        existing.add(f)
                    st.session_state['email_files'] = sorted(existing)
                    st.rerun()
            except Exception as e:
                st.error(f"파일 선택 오류: {e}")

        files = st.session_state['email_files']
        if files:
            st.caption(f"📋 {len(files)}개 파일 선택됨")
            for i, fp in enumerate(files):
                p = Path(fp)
                c1, c2 = st.columns([9, 1])
                with c1:
                    ext_icon = {"eml": "📧", "log": "📋", "txt": "📄",
                                "msg": "📨"}.get(p.suffix.lstrip('.'), "📁")
                    st.caption(f"{ext_icon} {p.name}")
                with c2:
                    if st.button("✕", key=f"rm_{i}", help="제거"):
                        st.session_state['email_files'].pop(i)
                        st.rerun()

            if st.button("🗑️ 전체 초기화", key="email_clear"):
                st.session_state['email_files'] = []
                st.rerun()
        else:
            st.caption("파일을 선택해주세요 (.eml .log .txt 등)")

        return st.session_state['email_files']

# 1단계는 항상 사용 (즉시 임포트). 2·3단계 RAG 모듈은 lazy import.
from step1_email_parser import EmailParser


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
    """3단계 워크플로우 다이어그램"""
    st.markdown("### 🔄 AI 에러 분석 워크플로우")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="stage-card">
            <div class="stage-header">🤖 [1단계] AI 메일 분석</div>
            <p><b>Input:</b> .eml / .log / .txt / 첨부파일 포함</p>
            <p><b>Model:</b> Groq compound-beta</p>
            <p><b>Output:</b> step1_parsed_errors.json</p>
            <p style="margin-top:1rem;">
                ✓ 자연어 이메일 분석<br>
                ✓ 첨부파일 내용 추출<br>
                ✓ 오류 요약 및 RAG 키워드 생성
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stage-card">
            <div class="stage-header">🧠 [2단계] RAG 코드 검색</div>
            <p><b>Input:</b> AI 분석 결과 (검색 키워드)</p>
            <p><b>Process:</b> 벡터 DB 유사도 검색</p>
            <p><b>Output:</b> step2_rag_contexts.json</p>
            <p style="margin-top:1rem;">
                ✓ 코드베이스 임베딩<br>
                ✓ 의미 기반 검색<br>
                ✓ <b>코드 변경시만 실행</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stage-card">
            <div class="stage-header">📊 [3단계] AI 오류 분석</div>
            <p><b>Input:</b> 오류 요약 + 코드 컨텍스트</p>
            <p><b>Process:</b> LLM 종합 분석</p>
            <p><b>Output:</b> reports/*.md</p>
            <p style="margin-top:1rem;">
                ✓ 정확한 원인 분석<br>
                ✓ 해결 방법 제시<br>
                ✓ 코드 수정 예시
            </p>
        </div>
        """, unsafe_allow_html=True)


def run_stage1(email_selection, status_placeholder, progress_bar,
               llm_type: str = "groq", model_name: str = "compound-beta",
               api_key: str = None, use_mock: bool = False):
    """1단계: AI 기반 메일 분석"""
    try:
        mode_label = "Mock 데모" if use_mock else f"{llm_type} ({model_name})"
        status_placeholder.info(f"🤖 [1단계] AI 메일 분석 중... ({mode_label})")
        progress_bar.progress(10)

        parser = EmailParser(
            llm_type=llm_type,
            model_name=model_name,
            api_key=api_key,
            use_mock=use_mock
        )
        time.sleep(0.3)
        progress_bar.progress(20)

        # 선택 방식에 따라 파싱
        if isinstance(email_selection, list):
            if not email_selection:
                status_placeholder.warning("⚠️ 이메일 파일을 선택해주세요")
                return {"success": False, "error": "파일 미선택"}
            parsed_results = parser.parse_files(email_selection)
        else:
            parser.email_folder = Path(email_selection)
            parsed_results = parser.parse_all_emails()
        
        progress_bar.progress(50)

        # 결과를 파일로 저장 (2단계 RAG에서 읽어감)
        parser.save_parsed_results(parsed_results, "output/step1_parsed_errors.json")

        total_files       = len(parsed_results)
        total_errors      = sum(1 for r in parsed_results.values() if r.get('has_error'))
        critical_count    = sum(1 for r in parsed_results.values() if r.get('severity') == 'CRITICAL')
        high_count        = sum(1 for r in parsed_results.values() if r.get('severity') == 'HIGH')

        result = {
            "success": True,
            "total_files": total_files,
            "total_errors": total_errors,
            "critical_count": critical_count,
            "high_count": high_count,
            "llm_model": model_name,
            "use_mock": use_mock,
            "parsed_results": parsed_results
        }

        status_placeholder.success(
            f"✅ [1단계] 완료: {total_files}개 파일 분석, "
            f"CRITICAL {critical_count}건 / HIGH {high_count}건"
        )
        return result
        
    except Exception as e:
        status_placeholder.error(f"❌ [1단계] 실패: {str(e)}")
        return {"success": False, "error": str(e)}


def run_stage2_rag(project_root: str, chunk_size: int, top_k: int, 
                   status_placeholder, progress_bar, reindex: bool = False):
    """2단계-RAG: 의미 기반 코드 검색"""
    try:
        # Lazy import: RAG 모듈은 사용할 때만 임포트
        from step2_rag_extractor import RAGCodeExtractor
        
        status_placeholder.info("🧠 [2단계-RAG] 의미 기반 코드 검색 중...")
        progress_bar.progress(60)
        
        extractor = RAGCodeExtractor(
            project_root=project_root,
            chunk_size=chunk_size,
            top_k=top_k
        )
        time.sleep(0.3)
        
        # 재인덱싱 옵션
        if reindex and Path(extractor.vector_db_path).exists():
            status_placeholder.info("🔄 벡터 DB 재생성 중...")
            import shutil
            shutil.rmtree(extractor.vector_db_path)
        
        progress_bar.progress(70)
        contexts = extractor.process_parsed_errors(
            parsed_json_path="output/step1_parsed_errors.json",
            output_path="output/step2_rag_contexts.json"
        )
        
        progress_bar.progress(80)

        # 통계 계산 (step2_rag_extractor 반환 키: searches)
        total_searches = sum(c.get('search_count', 0) for c in contexts.values())

        result = {
            "success": True,
            "total_searches": total_searches,
            "contexts": contexts,
            "method": "rag",
            "chunk_size": chunk_size,
            "top_k": top_k
        }
        
        status_placeholder.success(f"✅ [2단계-RAG] 완료: {total_searches}개 검색 완료")
        return result
        
    except Exception as e:
        status_placeholder.error(f"❌ [2단계-RAG] 실패: {str(e)}")
        st.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


def run_stage3(llm_type: str, model_name: str, api_key: str, use_mock: bool,
               status_placeholder, progress_bar, skip_rag: bool = False):
    """3단계: AI 오류 분석 리포트 생성 (소스코드 수정 금지)"""
    try:
        status_placeholder.info(f"🤖 [3단계] AI 오류 분석 중 ({llm_type} - {model_name})...")
        progress_bar.progress(85)

        from step3_rag_analysis import RAGAnalysisReportGenerator

        generator = RAGAnalysisReportGenerator(
            llm_type=llm_type,
            model_name=model_name,
            api_key=api_key if api_key else None,
            use_mock=use_mock
        )

        time.sleep(0.3)
        progress_bar.progress(90)

        # 2단계 결과 없으면 1단계만으로 분석 (step3가 자동 처리)
        report_count = generator.process_all_errors(
            contexts_json_path="output/step2_rag_contexts.json",
            step1_json_path="output/step1_parsed_errors.json"
        )

        progress_bar.progress(100)

        mode_str = "Mock 모드" if use_mock else f"{llm_type} ({model_name})"
        status_placeholder.success(f"✅ [3단계] 완료: {report_count}개 리포트 생성 ({mode_str})")
        return {
            "success":      True,
            "report_count": report_count,
            "llm_type":    llm_type,
            "model_name":  model_name,
            "use_mock":    use_mock
        }

    except Exception as e:
        status_placeholder.error(f"❌ [3단계] 실패: {str(e)}")
        st.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


def display_stage1_results(result):
    """1단계 AI 분석 결과 표시"""
    if not result.get("success"):
        st.error(f"오류: {result.get('error', '알 수 없는 오류')}")
        return

    st.markdown("### 🤖 1단계: AI 메일 분석 결과")

    model_label = "Mock 데모" if result.get("use_mock") else result.get("llm_model", "?")
    st.caption(f"🤖 사용 모델: {model_label}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📄 분석 파일", result["total_files"])
    col2.metric("⚠️ 오류 감지", result["total_errors"])
    col3.metric("🔴 CRITICAL", result.get("critical_count", 0))
    col4.metric("🟠 HIGH", result.get("high_count", 0))

    SEV_COLOR = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}

    for file_name, data in result["parsed_results"].items():
        sev   = data.get("severity", "MEDIUM")
        icon  = SEV_COLOR.get(sev, "❓")
        label = f"{icon} [{sev}] {file_name}"

        with st.expander(label, expanded=(sev in ("CRITICAL", "HIGH"))):
            # 요약
            summary = data.get("error_summary", "")
            if summary:
                st.info(f"📝 **오류 요약**\n\n{summary}")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**오류 유형:** `{data.get('error_type','?')}`")
                st.markdown(f"**심각도:** `{sev}`")
                rc = data.get("root_cause", "")
                if rc:
                    st.markdown(f"**근본 원인:** {rc}")
            with c2:
                comps = data.get("affected_components", [])
                if comps:
                    st.markdown("**영향 컴포넌트:**")
                    for c in comps:
                        line_str = f" (Line {c['line']})" if c.get('line') else ""
                        st.markdown(f"  - `{c.get('class_name','?')}.{c.get('method_name','?')}(){line_str}`")

            queries = data.get("search_queries", [])
            if queries:
                st.markdown("**🔍 RAG 검색 키워드:**")
                for q in queries:
                    st.code(q, language="")


def display_stage2_results(result):
    """2단계 RAG 결과 표시"""
    if not result.get("success"):
        st.error(f"오류: {result.get('error', '알 수 없는 오류')}")
        return

    st.markdown("### 🧠 2단계: RAG 코드 검색 결과")

    col1, col2, col3 = st.columns(3)
    col1.metric("🔍 검색 수", result["total_searches"])
    col2.metric("📦 청크 크기", result["chunk_size"])
    col3.metric("🎯 Top-K", result["top_k"])

    with st.expander("📋 코드 검색 상세 보기"):
        for email_file, data in result["contexts"].items():
            st.markdown(f"**{email_file}**")
            # step2_rag_extractor 반환 키: searches
            for i, search in enumerate(data.get('searches', []), 1):
                query  = search.get('search_query', 'N/A')
                codes  = search.get('found_codes', [])
                sev    = search.get('severity', '')
                st.info(f"🔍 검색 {i}: {query}" + (f"  [{sev}]" if sev else ""))
                for code in codes[:3]:
                    sim = code.get('similarity_score', 0)  # step2 반환 키: similarity_score
                    fp  = code.get('file_path', 'Unknown')
                    st.write(f"  • {fp} (유사도: {sim:.1%})")


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
        report_files = sorted(
            reports_dir.glob("*.md"),
            key=lambda f: f.stat().st_mtime,
            reverse=True  # 최신 순
        )
        
        if report_files:
            st.markdown("### 📁 생성된 리포트")
            
            report_names = [f.name for f in report_files]
            selected_report = st.selectbox(
                "리포트 선택",
                report_names,
                index=0  # 최신 리포트 자동 선택
            )
            
            if selected_report:
                report_path = reports_dir / selected_report
                with open(report_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                
                st.markdown("---")
                st.markdown(report_content)


def main():
    """메인 함수"""

    # 세션 상태 기본값 초기화 (groq 우선)
    if "stage1_llm" not in st.session_state:
        st.session_state["stage1_llm"] = "groq"
    if "stage3_llm" not in st.session_state:
        st.session_state["stage3_llm"] = "groq"

    # 헤더
    st.markdown('<h1 class="main-header">🤖 AI Agent 에러 분석 시스템</h1>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")

        # ── 1단계: AI 모델 설정 ─────────────────────────────
        st.subheader("🤖 1단계: 메일 분석 AI")
        st.caption("이메일에서 오류를 추출하는 AI 모델")

        stage1_llm = st.selectbox(
            "모델 선택",
            ["groq", "ollama", "openai", "mock"],
            key="stage1_llm",
            help="Groq: 클라우드 API (빠름) | Ollama: 로컈 | OpenAI: GPT | Mock: 데모"
        )
        if stage1_llm == "groq":
            stage1_model = st.selectbox(
                "Groq 모델",
                ["compound-beta", "compound-beta-mini", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
                key="stage1_model_groq"
            )
            stage1_key  = _GROQ_API_KEY
            stage1_mock = False
        elif stage1_llm == "ollama":
            stage1_model = st.selectbox(
                "Ollama 모델",
                ["llama3.1:8b", "llama3.2:3b", "qwen2.5-coder:7b", "qwen2.5:7b", "qwen2.5-coder:14b",
                 "codellama", "llama3", "mistral"],
                key="stage1_model"
            )
            stage1_key  = None
            stage1_mock = False
        elif stage1_llm == "openai":
            stage1_model = st.selectbox(
                "OpenAI 모델",
                ["gpt-4o", "gpt-4", "gpt-3.5-turbo"],
                key="stage1_model_oai"
            )
            stage1_key  = st.text_input("API Key", type="password", key="s1_key")
            stage1_mock = False
        else:
            stage1_model = "mock-model"
            stage1_key   = None
            stage1_mock  = True
            st.info("💡 Mock 모드: Ollama 없이 데모 실행")

        # ── 2단계: RAG 설정 ────────────────────────────────
        st.markdown("---")
        st.subheader("🧠 2단계: RAG 코드 검색")
        st.caption("소스코드 변경 시에만 재실행 필요")

        chunk_size = st.slider(
            "청크 크기", min_value=300, max_value=1000, value=500, step=100,
            help="코드를 나눌 청크 크기 (문자 수)"
        )
        top_k = st.slider(
            "Top-K 결과 수", min_value=3, max_value=10, value=5,
            help="유사도 높은 상위 K개 반환"
        )
        reindex = st.checkbox(
            "🔄 벡터 DB 재생성", value=False,
            help="소스코드 변경 시 체크"
        )
        skip_rag = st.checkbox(
            "⏭️ 2단계 건너뛰기", value=False,
            help="이미 인덱싱 완료된 경우 체크 → 기존 step2 결과 재사용"
        )

        # ── 3단계: 분석 LLM 설정 ───────────────────────────
        st.markdown("---")
        st.subheader("📊 3단계: 오류 분석 LLM")
        st.caption("추출된 코드 + 오류 요약 → 분석 리포트")

        llm_type = st.selectbox(
            "LLM 타입",
            ["groq", "ollama", "openai", "mock"],
            help="Groq: 클라우드 API (빠름) | Mock: 데모용, Ollama: 로컈, OpenAI: GPT"
        )
        if llm_type == "groq":
            model_name = st.selectbox(
                "Groq 모델",
                ["compound-beta", "compound-beta-mini", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
            )
            api_key  = _GROQ_API_KEY
            use_mock = False
        elif llm_type == "ollama":
            model_name = st.selectbox(
                "Ollama 모델",
                ["llama3.1:8b", "llama3.2:3b", "qwen2.5-coder:7b", "qwen2.5:7b", "codellama", "llama3", "mistral"]
            )
            api_key  = None
            use_mock = False
        elif llm_type == "openai":
            model_name = st.selectbox(
                "OpenAI 모델",
                ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]
            )
            api_key  = st.text_input("API Key", type="password", key="s3_key")
            use_mock = False
        else:
            model_name = "mock-model"
            api_key    = None
            use_mock   = True

        # ── 프로젝트 / 이메일 경로 ─────────────────────────
        st.markdown("---")
        st.subheader("📂 프로젝트 설정")
        project_root = folder_picker(
            "Java 프로젝트 경로",
            session_key="project_root",
            default=str(Path(__file__).parent / "example_project" / "policy-search-demo"),
            help_text="분석할 Java 프로젝트의 루트 디렉토리"
        )

        st.markdown("---")
        email_selection = email_picker()

        st.markdown("---")
        st.info("""
        💡 **사용 방법**
        1. 1단계 AI 모델 선택
        2. 이메일/로그 파일 선택
        3. '🚀 전체 실행' 클릭
        4. 코드 변경 시 벡터 DB 재생성 체크
        5. 생성된 리포트 확인
        """)
    
    # 워크플로우 다이어그램
    st.markdown("---")
    show_workflow_diagram()
    st.markdown("---")
    
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

            # 1단계: AI 메일 분석
            result1 = run_stage1(
                email_selection, status_placeholder, progress_bar,
                llm_type=stage1_llm, model_name=stage1_model,
                api_key=stage1_key, use_mock=stage1_mock
            )
            st.session_state.results['stage1'] = result1

            if result1.get("success"):
                # 2단계: RAG 코드 검색 (선택 사항 - 건너뛰기 가능)
                if skip_rag:
                    step2_cache = Path("output/step2_rag_contexts.json")
                    if step2_cache.exists():
                        status_placeholder.info("⏭️ [2단계] 건너뜀 - 이전 RAG 결과 재사용 (output/step2_rag_contexts.json)")
                    else:
                        status_placeholder.info("⏭️ [2단계] 건너뜀 - RAG 없이 1단계 결과만으로 분석")
                    progress_bar.progress(80)
                    result2 = {
                        "success": True,
                        "skipped": True,
                        "total_searches": 0,
                        "contexts": {},
                        "chunk_size": chunk_size,
                        "top_k": top_k
                    }
                else:
                    result2 = run_stage2_rag(
                        project_root, chunk_size, top_k,
                        status_placeholder, progress_bar, reindex
                    )
                st.session_state.results['stage2'] = result2

                if result2.get("success"):
                    # 3단계: AI 오류 분석 (소스코드 수정 금지)
                    result3 = run_stage3(
                        llm_type, model_name, api_key, use_mock,
                        status_placeholder, progress_bar,
                        skip_rag=skip_rag
                    )
                    st.session_state.results['stage3'] = result3

            elapsed = time.time() - start_time

            if all(st.session_state.results.get(f'stage{i}', {}).get("success") for i in [1,2,3]):
                status_placeholder.success(f"🎉 전체 프로세스 완료! (소요 시간: {elapsed:.2f}초)")
                st.balloons()
            else:
                status_placeholder.error("❌ 일부 단계 실패")
    if st.session_state.results:
        st.markdown("---")
        st.header("📈 실행 결과")
        
        tabs = st.tabs(["1단계 결과", "2단계 결과", "3단계 결과"])
        
        with tabs[0]:
            if 'stage1' in st.session_state.results:
                display_stage1_results(st.session_state.results['stage1'])
        
        with tabs[1]:
            if 'stage2' in st.session_state.results:
                r2 = st.session_state.results['stage2']
                if r2.get('skipped'):
                    st.info("⏭️ 2단계가 건너뛰어졌습니다. 기존 벡터 DB 인덱스를 사용하여 3단계가 분석합니다.")
                else:
                    display_stage2_results(r2)
        
        with tabs[2]:
            if 'stage3' in st.session_state.results:
                display_stage3_results(st.session_state.results['stage3'])
    
    # ── 리포트 뷰어 (항상 표시) ─────────────────────────────
    st.markdown("---")
    st.header("📂 리포트 뷰어")

    reports_dir = Path("reports")
    if reports_dir.exists():
        report_files = sorted(
            reports_dir.glob("*.md"),
            key=lambda f: f.stat().st_mtime,
            reverse=True  # 최신 순
        )
        if report_files:
            report_names = [f.name for f in report_files]
            selected_report = st.selectbox(
                "리포트 선택 (최신 순)",
                report_names,
                index=0,
                key="report_viewer_select"
            )
            if selected_report:
                report_path = reports_dir / selected_report
                with open(report_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                st.markdown("---")
                st.markdown(report_content)
        else:
            st.info("📝 아직 생성된 리포트가 없습니다. '🚀 전체 실행'을 클릭하세요.")
    else:
        st.info("📝 아직 생성된 리포트가 없습니다. '🚀 전체 실행'을 클릭하세요.")

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
