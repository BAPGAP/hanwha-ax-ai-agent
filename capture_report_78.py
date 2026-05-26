"""화면 7, 8 재캡처 (5000px 뷰포트 → 완전 렌더링)
- 화면 7: 리포트 뷰어 헤더 + 메타 + 목차
- 화면 8: 관련 소스코드 (RAG 검색 결과) 섹션
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

APP_URL   = "http://localhost:8501"
SHOTS_DIR = Path(__file__).parent / "docs" / "screenshots"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={'width': 1400, 'height': 6000},   # 처음부터 크게 설정
            device_scale_factor=1.5,
        )
        page = await ctx.new_page()

        print("🌐  앱 접속 (6000px 뷰포트)...")
        await page.goto(APP_URL, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(4000)  # 완전 렌더링 대기

        # 페이지 전체 높이 확인
        full_h = await page.evaluate("document.documentElement.scrollHeight")
        print(f"  scrollHeight = {full_h}")

        # 사이드바 오른쪽 경계
        sidebar_right = await page.evaluate("""() => {
            const s = document.querySelector('[data-testid="stSidebar"]');
            return s ? s.getBoundingClientRect().right : 300;
        }""")
        print(f"  sidebar right = {sidebar_right}")
        x = sidebar_right
        w = 1400 - x

        # ──────────────────────────────────────────────
        # 화면 7: 리포트 뷰어 헤더 ~ 목차 끝 (900px)
        # ──────────────────────────────────────────────
        report_header_y = await page.evaluate("""() => {
            const headers = [...document.querySelectorAll('h1, h2, h3, [data-testid="stHeadingWithActionElements"]')];
            const rh = headers.find(h => h.textContent.includes('리포트 뷰어'));
            return rh ? rh.getBoundingClientRect().top + window.scrollY - 10 : null;
        }""")

        if report_header_y is not None:
            png7 = await page.screenshot(
                type='png', full_page=True,
                clip={'x': x, 'y': report_header_y, 'width': w, 'height': 900}
            )
            out7 = SHOTS_DIR / "new_07_report_viewer_p1.png"
            out7.write_bytes(png7)
            print(f"  ✅  new_07_report_viewer_p1.png  ({len(png7)//1024} KB)  y={report_header_y:.0f}")
        else:
            print("  ⚠️  리포트 뷰어 헤더 없음")

        # ──────────────────────────────────────────────
        # 화면 8: '관련 소스코드 (RAG 검색 결과)' 섹션 (900px)
        # ──────────────────────────────────────────────
        rag_section_y = await page.evaluate("""() => {
            const all = [...document.querySelectorAll('h1, h2, h3, h4, strong')];
            const el = all.find(e => e.textContent.includes('관련 소스코드') ||
                                     e.textContent.includes('RAG 검색 결과'));
            return el ? el.getBoundingClientRect().top + window.scrollY - 20 : null;
        }""")

        if rag_section_y is not None:
            png8 = await page.screenshot(
                type='png', full_page=True,
                clip={'x': x, 'y': rag_section_y, 'width': w, 'height': 900}
            )
            out8 = SHOTS_DIR / "new_08_report_viewer_p2.png"
            out8.write_bytes(png8)
            print(f"  ✅  new_08_report_viewer_p2.png  ({len(png8)//1024} KB)  y={rag_section_y:.0f}")
        else:
            print("  ⚠️  RAG 소스코드 섹션 없음")

        await browser.close()
        print("\n✅  화면 7, 8 재캡처 완료!")

asyncio.run(main())
