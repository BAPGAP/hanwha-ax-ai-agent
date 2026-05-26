"""화면 9: 리포트 원인 분석 상세 섹션 캡처
- Streamlit 리포트 뷰어에서 '🤖 AI 분석' 또는 '근본 원인 분석' 섹션을 찾아 캡처
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
            viewport={'width': 1400, 'height': 1200},
            device_scale_factor=1.5,
        )
        page = await ctx.new_page()

        print("🌐  앱 접속...")
        await page.goto(APP_URL, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)

        # 1단계: 전체 scrollHeight 확인 후 뷰포트 확장
        for attempt in range(3):
            full_h = await page.evaluate("document.documentElement.scrollHeight")
            print(f"  scrollHeight = {full_h}")
            if full_h > 2000:
                break
            await page.wait_for_timeout(1000)

        big_h = max(full_h + 500, 5000)
        await page.set_viewport_size({'width': 1400, 'height': big_h})
        await page.wait_for_timeout(1000)

        # 재측정
        full_h2 = await page.evaluate("document.documentElement.scrollHeight")
        print(f"  확장 후 scrollHeight = {full_h2}")

        # 2단계: '근본 원인 분석' 또는 '🤖 AI 분석' 텍스트를 포함하는 요소 찾기
        target_y = await page.evaluate("""() => {
            // h2/h3 중 '근본 원인 분석', 'AI 분석', '오류 원인' 텍스트 포함 요소
            const candidates = [...document.querySelectorAll('h2, h3, h4, strong, p')];
            const keywords = ['근본 원인', 'AI 분석', '🤖 AI', '1️⃣'];
            for (const kw of keywords) {
                const el = candidates.find(e => e.textContent.includes(kw));
                if (el) {
                    const rect = el.getBoundingClientRect();
                    return rect.top + window.scrollY;
                }
            }
            return null;
        }""")

        sidebar = await page.evaluate("""() => {
            const s = document.querySelector('[data-testid="stSidebar"]');
            return s ? s.getBoundingClientRect().right : 300;
        }""")

        print(f"  sidebar right = {sidebar}")

        if target_y is None:
            print("  ⚠️  '근본 원인 분석' 요소를 찾지 못했습니다")
            print("       → 대신 y=2200 이후 구간 캡처")
            target_y = 2200

        print(f"  대상 y = {target_y:.0f}")

        # 3단계: 해당 위치부터 900px 캡처
        capture_y = max(0, target_y - 20)
        capture_h = 900
        capture_w = 1400 - sidebar

        png = await page.screenshot(
            type='png', full_page=True,
            clip={'x': sidebar, 'y': capture_y, 'width': capture_w, 'height': capture_h}
        )
        out = SHOTS_DIR / "new_09_report_ai_analysis.png"
        out.write_bytes(png)
        print(f"  ✅  new_09_report_ai_analysis.png  ({len(png)//1024} KB)")

        # 확인용: 페이지 전체 scrollHeight 출력
        print(f"\n  (전체 페이지 높이: {full_h2}px)")

        await browser.close()

asyncio.run(main())
