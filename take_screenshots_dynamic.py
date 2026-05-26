"""
화면 4~9 자동 캡처 스크립트
- 화면 4: 1단계 완료 + 2단계 RAG 진행 중
- 화면 5: 2단계 RAG 결과 탭
- 화면 6: 3단계 AI 오류 분석 중
- 화면 7~9: 리포트 뷰어 상단/중단/하단
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

APP_URL    = "http://localhost:8501"
SHOTS_DIR  = Path(__file__).parent / "docs" / "screenshots"
SHOTS_DIR.mkdir(exist_ok=True)

BASE_DIR   = Path(__file__).parent

# 앱 실행에 필요한 경로
EMAIL_FOLDER   = str(BASE_DIR / "email")
PROJECT_FOLDER = str(BASE_DIR / "example_project" / "policy-search-demo")


def snap_path(name: str) -> Path:
    return SHOTS_DIR / f"new_{name}.png"


async def full_crop(page, y_start: float, y_end: float, fname: str, x_start: float = 0):
    """지정 Y 범위를 전체 너비로 크롭 캡처"""
    vp = page.viewport_size
    h = y_end - y_start
    if h < 10:
        print(f"  ⚠️  너무 작은 영역 {fname}: {h}px")
        return
    png = await page.screenshot(
        type='png',
        full_page=True,
        clip={'x': x_start, 'y': y_start, 'width': vp['width'] - x_start, 'height': h}
    )
    p = snap_path(fname)
    p.write_bytes(png)
    print(f"  ✅ {fname}.png  ({len(png)//1024} KB,  y={y_start:.0f}~{y_end:.0f})")


async def element_crop(page, selector: str, fname: str, padding: int = 20):
    """요소 bbox 기준으로 크롭 캡처"""
    elem = await page.query_selector(selector)
    if not elem:
        print(f"  ⚠️  요소 없음: {selector}")
        return False
    bbox = await elem.bounding_box()
    if not bbox:
        return False
    vp = page.viewport_size
    x = max(0, bbox['x'] - padding)
    y = max(0, bbox['y'] - padding)
    w = min(vp['width'] - x, bbox['width'] + padding * 2)
    h = bbox['height'] + padding * 2
    png = await page.screenshot(
        type='png',
        full_page=True,
        clip={'x': x, 'y': y, 'width': w, 'height': h}
    )
    p = snap_path(fname)
    p.write_bytes(png)
    print(f"  ✅ {fname}.png  ({len(png)//1024} KB)")
    return True


async def get_content_bounds(page) -> dict:
    """실제 콘텐츠 영역의 최하단 Y 위치 반환"""
    return await page.evaluate("""() => {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const sidebarRight = sidebar ? sidebar.getBoundingClientRect().right : 300;
        const allElems = [...document.querySelectorAll('body *')];
        let maxY = 0;
        for (const el of allElems) {
            const r = el.getBoundingClientRect();
            if (r.height > 0 && r.width > 0 && r.bottom + window.scrollY > maxY
                && r.left >= sidebarRight - 10) {
                maxY = r.bottom + window.scrollY;
            }
        }
        return { contentEnd: maxY, sidebarRight };
    }""")


async def capture_execution_area(page, fname: str, label: str):
    """'실행 현황' 영역(상태메시지+progress+버튼)을 여백없이 캡처"""
    bounds = await page.evaluate("""() => {
        // '실행 현황' 헤더 찾기
        const headers = [...document.querySelectorAll('h2, h3, [data-testid="stHeadingWithActionElements"]')];
        const runHeader = headers.find(h => h.textContent.includes('실행 현황'));
        if (!runHeader) return null;

        const headerRect = runHeader.getBoundingClientRect();
        const startY = headerRect.top + window.scrollY - 10;

        // '리포트 뷰어' 헤더 찾기 (실행 현황 다음 섹션)
        const reportHeader = headers.find(h => h.textContent.includes('리포트 뷰어'));
        let endY;
        if (reportHeader) {
            endY = reportHeader.getBoundingClientRect().top + window.scrollY - 10;
        } else {
            // 없으면 실행 버튼 아래 ~150px
            const btn = [...document.querySelectorAll('button')].find(b => b.textContent.includes('전체 실행'));
            if (btn) {
                endY = btn.getBoundingClientRect().bottom + window.scrollY + 40;
            } else {
                endY = startY + 400;
            }
        }

        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const sidebarRight = sidebar ? sidebar.getBoundingClientRect().right : 300;

        return { startY, endY, sidebarRight };
    }""")

    if not bounds:
        print(f"  ⚠️  실행 현황 영역을 찾지 못함: {fname}")
        return

    print(f"  📐 실행 현황 영역: y={bounds['startY']:.0f}~{bounds['endY']:.0f}")
    vp = page.viewport_size
    x = bounds['sidebarRight']
    y = bounds['startY']
    w = vp['width'] - x
    h = bounds['endY'] - bounds['startY']

    png = await page.screenshot(
        type='png',
        full_page=True,
        clip={'x': x, 'y': y, 'width': w, 'height': h}
    )
    p = snap_path(fname)
    p.write_bytes(png)
    print(f"  ✅ {fname}.png  ({len(png)//1024} KB)  [{label}]")


async def wait_for_text(page, text: str, timeout: int = 60000) -> bool:
    """페이지에 특정 텍스트가 나타날 때까지 대기"""
    try:
        await page.wait_for_function(
            f'document.body.innerText.includes({repr(text)})',
            timeout=timeout
        )
        return True
    except Exception:
        return False


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={'width': 1400, 'height': 900},
            device_scale_factor=1.5,
        )
        page = await ctx.new_page()

        # ──────────────────────────────────────────────────────────────
        # 1. 앱 접속 + 초기 설정 확인
        # ──────────────────────────────────────────────────────────────
        print(f"\n🌐  Streamlit 앱 접속: {APP_URL}")
        await page.goto(APP_URL, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)

        # 전체 페이지 높이 확장
        full_h = await page.evaluate("document.documentElement.scrollHeight")
        await page.set_viewport_size({'width': 1400, 'height': max(full_h + 200, 2000)})
        await page.wait_for_timeout(500)

        # ──────────────────────────────────────────────────────────────
        # 2. 화면 7~9: 리포트 뷰어 (분석 전에도 기존 리포트 표시됨)
        # ──────────────────────────────────────────────────────────────
        print("\n\n📸  [화면 7~9] 리포트 뷰어 캡처")

        report_bounds = await page.evaluate("""() => {
            const headers = [...document.querySelectorAll('h2, h3, [data-testid="stHeadingWithActionElements"]')];
            const rh = headers.find(h => h.textContent.includes('리포트 뷰어'));
            if (!rh) return null;

            const startY = rh.getBoundingClientRect().top + window.scrollY - 10;
            const endY = document.documentElement.scrollHeight;

            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            const sidebarRight = sidebar ? sidebar.getBoundingClientRect().right : 300;
            return { startY, endY, sidebarRight };
        }""")

        if report_bounds:
            print(f"  리포트 뷰어: y={report_bounds['startY']:.0f}~{report_bounds['endY']:.0f}")
            x      = report_bounds['sidebarRight']
            y_top  = report_bounds['startY']
            y_end  = report_bounds['endY']
            w      = 1400 - x
            total  = y_end - y_top

            # 화면 7: 리포트 상단 (선택 드롭다운 + 내용 상단)
            h7 = min(900, total)
            png7 = await page.screenshot(
                type='png', full_page=True,
                clip={'x': x, 'y': y_top, 'width': w, 'height': h7}
            )
            snap_path('07_report_viewer_top').write_bytes(png7)
            print(f"  ✅ new_07_report_viewer_top.png  ({len(png7)//1024} KB)")

            # 화면 8: 리포트 중단 (오류 원인 분석 표)
            if total > 900:
                h8 = min(900, total - 900)
                png8 = await page.screenshot(
                    type='png', full_page=True,
                    clip={'x': x, 'y': y_top + 900, 'width': w, 'height': h8}
                )
                snap_path('08_report_viewer_mid').write_bytes(png8)
                print(f"  ✅ new_08_report_viewer_mid.png  ({len(png8)//1024} KB)")

            # 화면 9: 리포트 하단 (SQL 코드 하이라이트)
            if total > 1800:
                h9 = min(900, total - 1800)
                png9 = await page.screenshot(
                    type='png', full_page=True,
                    clip={'x': x, 'y': y_top + 1800, 'width': w, 'height': h9}
                )
                snap_path('09_report_viewer_bottom').write_bytes(png9)
                print(f"  ✅ new_09_report_viewer_bottom.png  ({len(png9)//1024} KB)")
        else:
            print("  ⚠️  리포트 뷰어 영역을 찾지 못했습니다.")

        # ──────────────────────────────────────────────────────────────
        # 3. 분석 실행 후 화면 4~6 캡처
        # ──────────────────────────────────────────────────────────────
        print("\n\n🚀  분석 실행 시작 (화면 4~6 캡처)")
        print("    ※ GROQ API 사용 — 실제 분석 결과로 캡처")

        # 뷰포트를 다시 900px로 설정 (실행 화면 캡처용)
        await page.set_viewport_size({'width': 1400, 'height': 900})
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)

        # '전체 실행' 버튼 클릭
        btn = await page.query_selector('button:has-text("전체 실행")')
        if not btn:
            print("  ⚠️  '전체 실행' 버튼을 찾지 못했습니다.")
        else:
            await btn.click()
            print("  🖱️  '전체 실행' 버튼 클릭")

            # 분석 시작 대기
            await page.wait_for_timeout(2000)

            # ── 화면 4: 1단계 완료 + 2단계 RAG 진행 중 ──
            print("\n  📸  [화면 4] 1단계 완료 + 2단계 RAG 진행 중 대기...")
            found4 = await wait_for_text(page, "1단계] 완료", timeout=120000)
            if found4:
                await page.wait_for_timeout(200)  # 렌더링 안정화
                await capture_execution_area(page, '04_step1_done_step2_running',
                                             '[1단계] 완료 → [2단계] RAG 진행 중')
            else:
                print("  ⚠️  화면 4 캡처 실패 (타임아웃)")

            # ── 화면 6: 3단계 AI 오류 분석 중 ──
            print("\n  📸  [화면 6] 3단계 AI 오류 분석 중 대기...")
            found6 = await wait_for_text(page, "3단계] AI 오류 분석 중", timeout=180000)
            if found6:
                await page.wait_for_timeout(200)
                await capture_execution_area(page, '06_step3_ai_running',
                                             '[3단계] AI 오류 분석 중')
            else:
                print("  ⚠️  화면 6 캡처 실패 (타임아웃)")

            # ── 전체 완료 대기 ──
            print("\n  ⏳  전체 완료 대기...")
            done = await wait_for_text(page, "전체 프로세스 완료", timeout=300000)
            if done:
                print("  🎉  전체 분석 완료!")
                await page.wait_for_timeout(2000)

                # ── 화면 5: 2단계 RAG 결과 탭 ──
                print("\n  📸  [화면 5] 2단계 RAG 결과 탭 클릭")
                # 결과 탭이 생겼는지 확인
                full_h = await page.evaluate("document.documentElement.scrollHeight")
                await page.set_viewport_size({'width': 1400, 'height': max(full_h + 200, 2000)})
                await page.wait_for_timeout(500)

                tab2 = await page.query_selector('[data-testid="stTabs"] button:nth-child(2)')
                if tab2:
                    await tab2.click()
                    await page.wait_for_timeout(1000)
                else:
                    # 탭 텍스트로 찾기
                    tabs = await page.query_selector_all('[role="tab"]')
                    for tab in tabs:
                        txt = await tab.inner_text()
                        if '2단계' in txt:
                            await tab.click()
                            await page.wait_for_timeout(1000)
                            break

                # 탭 + RAG 결과 영역 캡처
                rag_bounds = await page.evaluate("""() => {
                    const tabs = document.querySelector('[data-testid="stTabs"]');
                    if (!tabs) return null;
                    const r = tabs.getBoundingClientRect();

                    // 콘텐츠 최하단 찾기
                    const sidebar = document.querySelector('[data-testid="stSidebar"]');
                    const sidebarRight = sidebar ? sidebar.getBoundingClientRect().right : 300;
                    const children = [...document.querySelectorAll('[data-testid="stTabs"] *')];
                    let maxBottom = r.top + window.scrollY + 400;
                    for (const el of children) {
                        const cr = el.getBoundingClientRect();
                        if (cr.height > 0 && cr.width > 50) {
                            maxBottom = Math.max(maxBottom, cr.bottom + window.scrollY);
                        }
                    }

                    return {
                        startY: r.top + window.scrollY - 10,
                        endY: maxBottom + 30,
                        sidebarRight
                    };
                }""")

                if rag_bounds:
                    x = rag_bounds['sidebarRight']
                    y = rag_bounds['startY']
                    h = min(1200, rag_bounds['endY'] - y)
                    png5 = await page.screenshot(
                        type='png', full_page=True,
                        clip={'x': x, 'y': y, 'width': 1400 - x, 'height': h}
                    )
                    snap_path('05_step2_rag_result').write_bytes(png5)
                    print(f"  ✅ new_05_step2_rag_result.png  ({len(png5)//1024} KB)")
                else:
                    print("  ⚠️  RAG 결과 탭 영역을 찾지 못했습니다.")

            else:
                print("  ⚠️  전체 완료 대기 타임아웃")

        # ──────────────────────────────────────────────────────────────
        # 4. 완료 후 리포트 뷰어 재캡처 (최신 분석 결과 포함)
        # ──────────────────────────────────────────────────────────────
        print("\n\n📸  [화면 7~9] 리포트 뷰어 재캡처 (최신 분석 결과)")
        full_h = await page.evaluate("document.documentElement.scrollHeight")
        await page.set_viewport_size({'width': 1400, 'height': max(full_h + 200, 2000)})
        await page.wait_for_timeout(500)

        report_bounds = await page.evaluate("""() => {
            const headers = [...document.querySelectorAll('h2, h3, [data-testid="stHeadingWithActionElements"]')];
            const rh = headers.find(h => h.textContent.includes('리포트 뷰어'));
            if (!rh) return null;
            const startY = rh.getBoundingClientRect().top + window.scrollY - 10;
            const endY   = document.documentElement.scrollHeight;
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            const sidebarRight = sidebar ? sidebar.getBoundingClientRect().right : 300;
            return { startY, endY, sidebarRight };
        }""")

        if report_bounds:
            x     = report_bounds['sidebarRight']
            y_top = report_bounds['startY']
            y_end = report_bounds['endY']
            w     = 1400 - x
            total = y_end - y_top
            print(f"  리포트 영역: y={y_top:.0f}~{y_end:.0f}  (총 {total:.0f}px)")

            chunk = 900
            for i, y_off in enumerate(range(0, int(total), chunk), 7):
                h = min(chunk, int(total) - y_off)
                if h < 50:
                    break
                png = await page.screenshot(
                    type='png', full_page=True,
                    clip={'x': x, 'y': y_top + y_off, 'width': w, 'height': h}
                )
                name = f'0{i}_report_viewer_p{i-6}'
                snap_path(name).write_bytes(png)
                print(f"  ✅ new_{name}.png  ({len(png)//1024} KB)")

        await browser.close()

    print("\n\n✅  화면 4~9 캡처 완료!")
    print(f"   저장 위치: {SHOTS_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
