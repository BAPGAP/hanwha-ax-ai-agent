"""화면 4 단독 캡처: 2단계 RAG 진행 중 상태 (= 1단계 완료 직후)"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

APP_URL   = "http://localhost:8501"
SHOTS_DIR = Path(__file__).parent / "docs" / "screenshots"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={'width': 1400, 'height': 900},
            device_scale_factor=1.5,
        )
        page = await ctx.new_page()

        print("🌐  앱 접속 중...")
        await page.goto(APP_URL, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)

        # 전체 실행 버튼 클릭
        btn = await page.query_selector('button:has-text("전체 실행")')
        if not btn:
            print("❌  버튼을 찾지 못했습니다")
            return
        await btn.click()
        print("🖱️  버튼 클릭 완료")

        # 200ms 간격으로 폴링하여 2단계 RAG 진행 중 텍스트 확인
        TARGET = "2단계-RAG] 의미 기반 코드 검색 중"
        print(f"⏳  '{TARGET}' 텍스트 기다리는 중 (200ms 간격)...")

        found = False
        for i in range(600):  # 최대 120초
            await page.wait_for_timeout(200)
            txt = await page.evaluate("document.body.innerText")
            if TARGET in txt:
                print(f"  ✅  {i*0.2:.1f}초 후 발견!")
                found = True
                break
            if i % 25 == 0:
                print(f"  ... {i*0.2:.0f}초 경과")

        if not found:
            print("❌  타임아웃")
            return

        # 실행 현황 영역 캡처
        bounds = await page.evaluate("""() => {
            const headers = [...document.querySelectorAll('h2, h3, [data-testid="stHeadingWithActionElements"]')];
            const runHeader = headers.find(h => h.textContent.includes('실행 현황'));
            if (!runHeader) return null;
            const startY = runHeader.getBoundingClientRect().top + window.scrollY - 10;

            // '리포트 뷰어' 헤더 or 버튼 아래 ~150px
            const reportHeader = headers.find(h => h.textContent.includes('리포트 뷰어'));
            let endY;
            if (reportHeader) {
                endY = reportHeader.getBoundingClientRect().top + window.scrollY - 10;
            } else {
                const btn = [...document.querySelectorAll('button')].find(b => b.textContent.includes('전체 실행'));
                endY = btn ? btn.getBoundingClientRect().bottom + window.scrollY + 50 : startY + 400;
            }

            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            const sidebarRight = sidebar ? sidebar.getBoundingClientRect().right : 300;
            return { startY, endY, sidebarRight };
        }""")

        if not bounds:
            print("❌  실행 현황 영역을 찾지 못했습니다")
            return

        print(f"  📐  y={bounds['startY']:.0f}~{bounds['endY']:.0f}")
        vp = page.viewport_size
        x = bounds['sidebarRight']
        y = bounds['startY']
        h = bounds['endY'] - bounds['startY']
        w = vp['width'] - x

        png = await page.screenshot(
            type='png', full_page=True,
            clip={'x': x, 'y': y, 'width': w, 'height': h}
        )
        out = SHOTS_DIR / "new_04_step1_done_step2_running.png"
        out.write_bytes(png)
        print(f"  ✅  new_04_step1_done_step2_running.png  ({len(png)//1024} KB)")

        await browser.close()

asyncio.run(main())
