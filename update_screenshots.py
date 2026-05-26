"""마크다운의 시연 스크린샷을 새 이미지로 교체"""
import base64, re
from pathlib import Path

MD_PATH   = Path(__file__).parent / "docs" / "AX_시연_소개자료.md"
SHOTS_DIR = Path(__file__).parent / "docs" / "screenshots"

# alt 텍스트 → 새 PNG 파일 매핑
REPLACE_MAP = {
    "메인 대시보드":                SHOTS_DIR / "new_00_full_initial.png",
    "워크플로우 카드":               SHOTS_DIR / "new_02_workflow_cards.png",
    "사이드바 설정":                SHOTS_DIR / "new_03_sidebar_settings.png",
    "1단계 완료 2단계 진행 중":      SHOTS_DIR / "new_04_step1_done_step2_running.png",
    "2단계 RAG 결과":               SHOTS_DIR / "new_05_step2_rag_result.png",
    "3단계 AI 분석 진행 중":         SHOTS_DIR / "new_06_step3_ai_running.png",
    "리포트 - RAG 소스코드 매칭 결과": SHOTS_DIR / "new_07_report_viewer_p1.png",
    "리포트 - 오류 원인 상세 분석 표": SHOTS_DIR / "new_08_report_viewer_p2.png",
    "리포트 - 원인 분석 상세":         SHOTS_DIR / "new_09_report_ai_analysis.png",
}

md = MD_PATH.read_text(encoding='utf-8')
original_size = len(md)

for alt, png_path in REPLACE_MAP.items():
    if not png_path.exists():
        print(f"  ⚠️  파일 없음: {png_path}")
        continue

    b64 = base64.b64encode(png_path.read_bytes()).decode()
    new_img = f"![{alt}](data:image/png;base64,{b64})"
    pattern = rf'!\[{re.escape(alt)}\]\(data:image/[^)]+\)'

    if re.search(pattern, md):
        md = re.sub(pattern, new_img, md)
        print(f"  ✅ [{alt}] 교체 완료  ({len(b64)//1024} KB base64)")
    else:
        print(f"  ⚠️  패턴 없음: {alt}")

MD_PATH.write_text(md, encoding='utf-8')
print(f"\n저장: {MD_PATH.name}  ({len(md)//1024} KB  ← 기존 {original_size//1024} KB)")
