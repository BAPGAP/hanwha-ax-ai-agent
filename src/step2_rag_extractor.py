"""
[2단계 - RAG 버전] 의미 기반 소스코드 검색

정확한 라인 번호나 클래스명이 없어도, 에러 메시지의 의미를 분석하여
관련 코드를 자동으로 찾아주는 RAG 시스템

특징:
- 전체 코드베이스를 벡터 DB에 임베딩
- 에러 메시지로 유사도 검색
- 정확한 위치 몰라도 관련 코드 검색
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# RAG 관련 라이브러리
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


class RAGCodeExtractor:
    """RAG 기반 코드 추출 시스템"""
    
    def __init__(
        self,
        project_root: str = "example_project",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        vector_db_path: str = "vector_db",
        top_k: int = 5
    ):
        """
        Args:
            project_root: Java 프로젝트 루트 디렉토리
            chunk_size: 코드 청크 크기 (문자 수)
            chunk_overlap: 청크 간 오버랩 (문자 수)
            vector_db_path: 벡터 DB 저장 경로
            top_k: 검색할 상위 결과 수
        """
        self.project_root = Path(project_root)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_db_path = vector_db_path
        self.top_k = top_k
        
        print(f"\n🤖 RAG 기반 코드 검색 시스템 초기화")
        print(f"📂 프로젝트: {self.project_root}")
        print(f"📊 청크 크기: {chunk_size}, 오버랩: {chunk_overlap}")
        
        # 임베딩 모델 초기화 (HuggingFace, 무료)
        print("🔄 임베딩 모델 로딩 중...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # 텍스트 분할기
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.vectorstore = None
        
    def index_codebase(self):
        """
        전체 코드베이스를 인덱싱하여 벡터 DB 생성
        """
        print("\n" + "=" * 60)
        print("📚 코드베이스 인덱싱 시작")
        print("=" * 60)
        
        if not self.project_root.exists():
            raise FileNotFoundError(f"프로젝트 디렉토리를 찾을 수 없습니다: {self.project_root}")
        
        # 모든 Java 파일 수집
        java_files = list(self.project_root.rglob("*.java"))
        print(f"\n📄 Java 파일 {len(java_files)}개 발견")
        
        if len(java_files) == 0:
            raise ValueError("Java 파일을 찾을 수 없습니다!")
        
        documents = []
        
        for java_file in java_files:
            print(f"   ✓ {java_file.name} 읽는 중...")
            
            try:
                # 파일 읽기 (여러 인코딩 시도)
                content = None
                for encoding in ['utf-8', 'cp949', 'latin-1']:
                    try:
                        with open(java_file, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if not content:
                    print(f"      ⚠️ 인코딩 오류: {java_file.name}")
                    continue
                
                # 코드를 청크로 분할
                chunks = self.text_splitter.split_text(content)
                
                # 각 청크를 Document로 변환
                for i, chunk in enumerate(chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            'source': str(java_file),
                            'file_name': java_file.name,
                            'chunk_id': i,
                            'total_chunks': len(chunks),
                            'class_name': java_file.stem  # 파일명에서 클래스명 추출
                        }
                    )
                    documents.append(doc)
                
                print(f"      → {len(chunks)}개 청크 생성")
                
            except Exception as e:
                print(f"      ❌ 오류: {e}")
                continue
        
        print(f"\n📊 총 {len(documents)}개 청크 생성됨")
        
        # 벡터 DB 생성 (코사인 유사도 공간 사용 - 유사도 계산 정확도 향상)
        print("\n🔄 벡터 DB 생성 중... (시간이 걸릴 수 있습니다)")
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.vector_db_path,
            collection_metadata={"hnsw:space": "cosine"}
        )
        
        print(f"✅ 벡터 DB 저장 완료: {self.vector_db_path}")
        print("=" * 60 + "\n")
        
    def load_vectorstore(self):
        """
        기존 벡터 DB 로드 (이미 인덱싱한 경우)
        """
        if Path(self.vector_db_path).exists():
            print(f"📂 기존 벡터 DB 로드 중: {self.vector_db_path}")
            self.vectorstore = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
            print("✅ 벡터 DB 로드 완료\n")
            return True
        return False
    
    def search_similar_code(self, error_message: str, top_k: int = None) -> List[Dict]:
        """
        에러 메시지로 유사한 코드 검색
        
        Args:
            error_message: 에러 메시지 또는 설명
            top_k: 반환할 결과 수
            
        Returns:
            유사한 코드 청크 리스트
        """
        if not self.vectorstore:
            raise ValueError("벡터 DB가 초기화되지 않았습니다. index_codebase() 또는 load_vectorstore()를 먼저 실행하세요.")
        
        if top_k is None:
            top_k = self.top_k
        
        print(f"🔍 검색 중: '{error_message[:100]}...'")
        
        # 유사도 검색
        results = self.vectorstore.similarity_search_with_score(
            error_message,
            k=top_k
        )
        
        formatted_results = []
        
        for i, (doc, score) in enumerate(results, 1):
            result = {
                'rank': i,
                # 거리 → 유사도: 1/(1+d) 로 항상 (0,1] 범위 보장
                # (L2²/cosine 등 어떤 거리 메트릭이든 음수 방지)
                'similarity_score': float(1.0 / (1.0 + score)),
                'file_path': doc.metadata['source'],
                'file_name': doc.metadata['file_name'],
                'class_name': doc.metadata['class_name'],
                'chunk_id': doc.metadata['chunk_id'],
                'code_snippet': doc.page_content,
                'snippet_length': len(doc.page_content)
            }
            formatted_results.append(result)
            
            print(f"   {i}. {result['file_name']} (유사도: {result['similarity_score']:.3f})")
        
        return formatted_results
    
    def process_parsed_errors(
        self,
        parsed_json_path: str = "output/step1_parsed_errors.json",
        output_path: str = "output/step2_rag_contexts.json"
    ) -> Dict[str, List[Dict]]:
        """
        1단계 AI 분석 결과를 RAG로 처리.

        1단계 출력 포맷 우선순위:
          1) search_queries (AI가 생성한 RAG 검색 키워드) → 직접 사용
          2) exceptions / stack_traces (호환 필드) → fallback
          3) error_summary / raw_text → 최후 fallback
        """
        print("=" * 60)
        print("[2단계 - RAG] 의미 기반 코드 검색")
        print("=" * 60)

        # 벡터 DB 로드 또는 생성
        if not self.load_vectorstore():
            print("⚠️ 벡터 DB가 없습니다. 코드베이스를 인덱싱합니다...\n")
            self.index_codebase()

        # 1단계 결과 로드
        print(f"📂 1단계 결과 로드: {parsed_json_path}")
        with open(parsed_json_path, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)

        email_count = len(parsed_data)
        print(f"📧 {email_count}개 이메일 파일 처리 중...\n")

        all_results = {}

        for email_file, data in parsed_data.items():
            print("=" * 60)
            print(f"📧 처리 중: {email_file}")
            print("=" * 60)

            results = []

            # ── 우선순위 1: AI가 생성한 search_queries 직접 사용 ──────────
            search_queries = data.get('search_queries', [])
            if search_queries:
                print(f"\n✅ AI 생성 검색 키워드 {len(search_queries)}개 사용")
                for q in search_queries:
                    if not q or not q.strip():
                        continue
                    print(f"\n🔍 검색: {q}")
                    found = self.search_similar_code(q, top_k=self.top_k)
                    results.append({
                        'error_type':  'ai_query',
                        'search_query': q,
                        'error_summary': data.get('error_summary', ''),
                        'severity':     data.get('severity', 'MEDIUM'),
                        'found_codes':  found
                    })

            # ── 우선순위 2: exceptions fallback ──────────────────────────
            if not results:
                for exc in data.get('exceptions', []):
                    exc_type    = exc.get('exception', exc.get('type', 'Unknown'))
                    exc_message = exc.get('message', '')
                    if not exc_type:
                        continue
                    print(f"\n🔍 Exception 검색: {exc_type}")
                    query = f"{exc_type} {exc_message}".strip()
                    found = self.search_similar_code(query, top_k=3)
                    results.append({
                        'error_type':       'exception',
                        'exception_type':    exc_type,
                        'exception_message': exc_message,
                        'search_query':      query,
                        'found_codes':       found
                    })

            # ── 우선순위 3: stack_traces fallback ────────────────────────
            if not results:
                for trace in data.get('stack_traces', []):
                    class_name = trace.get('class_name', 'Unknown')
                    method     = trace.get('method', 'Unknown')
                    print(f"\n🔍 Stack Trace 검색: {class_name}.{method}()")
                    query = f"{class_name} {method}"
                    found = self.search_similar_code(query, top_k=3)
                    results.append({
                        'error_type':  'stack_trace',
                        'class_name':  class_name,
                        'method':      method,
                        'line':        trace.get('line'),
                        'search_query': query,
                        'found_codes': found
                    })

            # ── 우선순위 4: 오류 요약 또는 원본 텍스트 최후 fallback ─────
            if not results:
                fallback_text = (
                    data.get('error_summary')
                    or data.get('raw_text', '')[:500]
                )
                if fallback_text:
                    print(f"\n🔍 오류 요약 기반 검색")
                    found = self.search_similar_code(fallback_text, top_k=5)
                    results.append({
                        'error_type':  'general',
                        'search_query': fallback_text[:200],
                        'found_codes': found
                    })

            all_results[email_file] = {
                'email_file':   email_file,
                'has_error':    data.get('has_error', False),
                'error_summary': data.get('error_summary', ''),
                'severity':     data.get('severity', 'MEDIUM'),
                'root_cause':   data.get('root_cause', ''),
                'search_count': len(results),
                'searches':     results
            }

            print(f"\n✅ {email_file}: {len(results)}개 검색 완료\n")

        # 결과 저장
        os.makedirs(Path(output_path).parent, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        print("=" * 60)
        print(f"✅ RAG 검색 결과 저장: {output_path}")
        print("=" * 60 + "\n")

        return all_results


def main():
    """메인 실행 함수"""
    
    # RAG 추출기 초기화
    extractor = RAGCodeExtractor(
        project_root="example_project",
        chunk_size=500,
        chunk_overlap=50,
        top_k=5
    )
    
    # 1단계 결과 처리
    results = extractor.process_parsed_errors(
        parsed_json_path="output/step1_parsed_errors.json",
        output_path="output/step2_rag_contexts.json"
    )
    
    # 요약 통계
    total_searches = sum(r['search_count'] for r in results.values())
    print(f"📊 총 {total_searches}개 검색 완료")


if __name__ == "__main__":
    main()
