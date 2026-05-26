"""
Streamlit 앱 스크린샷 자동 캡처 스크립트
- 각 화면을 요소 단위로 정확하게 캡처 (여백 없음)
- 결과 파일: docs/screenshots/new_*.png
"""

import asyncio
import base64
import os
import re
from pathlib import Path
from playwright.async_api import async_playwright

APP_URL    = "http://localhost:8501"
DOCS_DIR   = Path(__file__).parent / "docs"
SHOTS_DIR  = DOCS_DIR / "screenshots"
MD_PATH    = DOCS_DIR / "AX_시연_소개자료.md"

# 캡처할 화면 정의
# key → (파일명, 설명)
SCREENS = {
    "화면1": ("new_01_main_dashboard.png",  "[화면 1] 메인 대시보드 — 타이틀 및 사이드바"),
    "화면2": ("new_02_workflow_cards.png",   "[화면 2] 3단계 AI 분석 워크플로우 카드"),
    "화면3": ("new_03_sidebar_settings.png", "[화면 3] 사이드바 설정 패널"),
}

# 마크다운에서 이미지를 교체할 alt 텍스트 매핑
ALT_MAP = {
    "화면1": "메인 대시보드",
    "화면2": "워크플로우 카드",
    "화면3": "사이드바 설정",
}


async def crop_screenshot(page, selector_or_bbox, output_path: Path, padding=16):
    """
    특정 요소(selector) 또는 bbox 영역을 잘라서 저장.
    padding: 상하좌우 여백(px)
    """
    if isinstance(selector_or_bbox, str):
        elem = await page.query_selector(selector_or_bbox)
        if elem is None:
            print(f"  ⚠️  요소를 찾지 못함: {selector_or_bbox}")
            return None
        bbox = await elem.bounding_box()
    else:
        bbox = selector_or_bbox

    if bbox is None:
        print("  ⚠️  bounding_box 없음")
        return None

    vp = page.viewport_size
    x      = max(0, bbox['x'] - padding)
    y      = max(0, bbox['y'] - padding)
    width  = min(vp['width']  - x, bbox['width']  + padding * 2)
    height = min(vp['height'] - y, bbox['height'] + padding * 2)

    png = await page.screenshot(
        type='png',
        clip={'x': x, 'y': y, 'width': width, 'height': height}
    )
    output_path.write_bytes(png)
    print(f"  ✅ 저장: {output_path.name}  ({len(png)//1024} KB)")
    return png


async def scroll_into_view_and_capture(page, selector, output_path: Path, extra_height=0, padding=16):
    """요소를 뷰포트 상단으로 스크롤 후 캡처"""
    elem = await page.query_selector(selector)
    if elem is None:
        print(f"  ⚠️  요소를 찾지 못함: {selector}")
        return None
    await elem.scroll_into_view_if_needed()
    await page.wait_for_timeout(500)

    bbox = await elem.bounding_box()
    if bbox is None:
        return None

    vp = page.viewport_size
    x      = max(0, bbox['x'] - padding)
    y      = max(0, bbox['y'] - padding)
    width  = min(vp['width']  - x, bbox['width']  + padding * 2)
    height = min(vp['height'] - y, bbox['height'] + padding * 2 + extra_height)

    png = await page.screenshot(
        type='png',
        clip={'x': x, 'y': y, 'width': width, 'height': height}
    )
    output_path.write_bytes(png)
    print(f"  ✅ 저장: {output_path.name}  ({len(png)//1024} KB)")
    return png


async def capture_full_content(page, output_path: Path):
    """콘텐츠 전체 높이 기준으로 전체 캡처 (빈 공간 제거)"""
    # 실제 콘텐츠가 있는 마지막 y 위치 계산
    content_height = await page.evaluate("""() => {
        // Streamlit 메인 콘텐츠 영역
        const main = document.querySelector('[data-testid="stMainBlockContainer"]')
                  || document.querySelector('.main .block-container')
                  || document.querySelector('.stApp');
        if (!main) return document.documentElement.scrollHeight;
        const children = Array.from(main.querySelectorAll('*'));
        let maxBottom = 0;
        for (const el of children) {
            const rect = el.getBoundingClientRect();
            if (rect.height > 0 && rect.width > 0) {
                maxBottom = Math.max(maxBottom, rect.bottom + window.scrollY);
            }
        }
        return maxBottom || main.getBoundingClientRect().bottom + window.scrollY;
    }""")

    vp = page.viewport_size
    png = await page.screenshot(
        type='png',
        clip={'x': 0, 'y': 0, 'width': vp['width'], 'height': min(content_height + 32, vp['height'])}
    )
    output_path.write_bytes(png)
    print(f"  ✅ 저장: {output_path.name}  ({len(png)//1024} KB,  height={content_height:.0f}px)")
    return png


async def main():
    SHOTS_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ── 1280px wide × 900px tall 뷰포트
        ctx = await browser.new_context(
            viewport={'width': 1400, 'height': 900},
            device_scale_factor=1.5,   # 고해상도
        )
        page = await ctx.new_page()

        print(f"\n🌐  Streamlit 앱 접속: {APP_URL}")
        await page.goto(APP_URL, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)   # 렌더링 대기

        # ─────────────────────────────────────────────────────────────────
        # [화면 1] 메인 대시보드 — 상단 타이틀 + 워크플로우 소개까지
        # ─────────────────────────────────────────────────────────────────
        print("\n📸  [화면 1] 메인 대시보드")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)

        # 타이틀 영역 + 사이드바 포함한 전체 상단 캡처
        # Streamlit 전체 앱 영역
        app_bbox = await page.evaluate("""() => {
            const app = document.querySelector('.stApp')
                     || document.querySelector('#root');
            if (!app) return null;
            return app.getBoundingClientRect();
        }""")

        # 상단 ~750px만 캡처 (타이틀 + 워크플로우 카드 상단)
        vp = page.viewport_size
        png1 = await page.screenshot(
            type='png',
            clip={'x': 0, 'y': 0, 'width': vp['width'], 'height': 700}
        )
        out1 = SHOTS_DIR / "new_01_main_dashboard.png"
        out1.write_bytes(png1)
        print(f"  ✅ 저장: {out1.name}  ({len(png1)//1024} KB)")

        # ─────────────────────────────────────────────────────────────────
        # [화면 2] 워크플로우 카드 — 카드 전체가 보이도록 스크롤 후 캡처
        # ─────────────────────────────────────────────────────────────────
        print("\n📸  [화면 2] 워크플로우 카드")

        # 페이지 전체를 충분히 큰 뷰포트로 확장
        full_h = await page.evaluate("document.documentElement.scrollHeight")
        print(f"  전체 스크롤 높이: {full_h}px")
        await page.set_viewport_size({'width': 1400, 'height': max(full_h + 100, 2000)})
        await page.wait_for_timeout(500)

        # 워크플로우 섹션 bbox 계산 (헤더부터 카드 끝까지)
        card_bbox = await page.evaluate("""() => {
            // '워크플로우' 텍스트를 가진 헤더 찾기
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            let node;
            let wfNode = null;
            while ((node = walker.nextNode())) {
                if (node.textContent.trim().includes('워크플로우')) {
                    wfNode = node.parentElement;
                    break;
                }
            }
            if (!wfNode) return null;

            // 헤더의 상위 섹션 컨테이너 찾기
            let section = wfNode;
            while (section && section !== document.body) {
                const r = section.getBoundingClientRect();
                if (r.width > 900) break;
                section = section.parentElement;
            }
            if (!section) return null;

            const sectionRect = section.getBoundingClientRect();
            const sectionTop = sectionRect.top + window.scrollY;

            // 카드 컬럼들 찾기 (stColumns 또는 stHorizontalBlock)
            const colContainers = [...document.querySelectorAll(
                '[data-testid="stColumns"], [data-testid="stHorizontalBlock"], [data-testid="column"]'
            )];

            let maxBottom = sectionTop + 400;
            for (const col of colContainers) {
                const r = col.getBoundingClientRect();
                const bottom = r.bottom + window.scrollY;
                if (bottom > sectionTop && r.top + window.scrollY < sectionTop + 600) {
                    maxBottom = Math.max(maxBottom, bottom);
                }
            }

            return {
                x: sectionRect.left + window.scrollX,
                y: sectionTop - 20,
                width: sectionRect.width,
                height: maxBottom - sectionTop + 60
            };
        }""")

        print(f"  card_bbox: {card_bbox}")

        if card_bbox and card_bbox['height'] > 100:
            png2 = await page.screenshot(
                type='png',
                full_page=True,
                clip={
                    'x': max(0, card_bbox['x']),
                    'y': max(0, card_bbox['y']),
                    'width': min(card_bbox['width'], 1400),
                    'height': card_bbox['height']
                }
            )
        else:
            # fallback: 전체 페이지에서 y=280~900 크롭
            print("  card_bbox 실패 → fallback 사용")
            png2 = await page.screenshot(
                type='png',
                full_page=True,
                clip={'x': 0, 'y': 280, 'width': 1400, 'height': 600}
            )

        out2 = SHOTS_DIR / "new_02_workflow_cards.png"
        out2.write_bytes(png2)
        print(f"  ✅ 저장: {out2.name}  ({len(png2)//1024} KB)")

        # 뷰포트 원복
        await page.set_viewport_size({'width': 1400, 'height': 900})

        # ─────────────────────────────────────────────────────────────────
        # [화면 3] 사이드바 설정 패널
        # ─────────────────────────────────────────────────────────────────
        print("\n📸  [화면 3] 사이드바 설정 패널")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)

        sidebar_bbox = await page.evaluate("""() => {
            const sidebar = document.querySelector('[data-testid="stSidebar"]')
                         || document.querySelector('.css-1d391kg')
                         || document.querySelector('section[data-testid="stSidebar"]');
            if (!sidebar) return null;
            const rect = sidebar.getBoundingClientRect();
            return {x: rect.left, y: rect.top, width: rect.width, height: rect.height};
        }""")

        print(f"  sidebar_bbox: {sidebar_bbox}")

        if sidebar_bbox:
            # 사이드바 전체 높이 캡처
            full_h = await page.evaluate("document.documentElement.scrollHeight")
            await page.set_viewport_size({'width': 1400, 'height': full_h + 100})
            await page.wait_for_timeout(200)

            sidebar_full = await page.evaluate("""() => {
                const sidebar = document.querySelector('[data-testid="stSidebar"]')
                             || document.querySelector('section[data-testid="stSidebar"]');
                if (!sidebar) return null;
                const rect = sidebar.getBoundingClientRect();
                return {x: rect.left, y: rect.top + window.scrollY, width: rect.width, height: rect.height};
            }""")

            if sidebar_full:
                png3 = await page.screenshot(
                    type='png',
                    full_page=True,
                    clip={
                        'x': sidebar_full['x'],
                        'y': sidebar_full['y'],
                        'width': sidebar_full['width'],
                        'height': sidebar_full['height']
                    }
                )
                out3 = SHOTS_DIR / "new_03_sidebar_settings.png"
                out3.write_bytes(png3)
                print(f"  ✅ 저장: {out3.name}  ({len(png3)//1024} KB)")

            await page.set_viewport_size({'width': 1400, 'height': 900})
        else:
            print("  ⚠️  사이드바를 찾지 못했습니다.")

        # ─────────────────────────────────────────────────────────────────
        # [화면 1+2 합본] 메인 대시보드 전체 (사이드바 포함)
        # ─────────────────────────────────────────────────────────────────
        print("\n📸  [화면 1+2 합본] 전체 초기 화면")

        full_h = await page.evaluate("document.documentElement.scrollHeight")
        await page.set_viewport_size({'width': 1400, 'height': full_h + 50})
        await page.wait_for_timeout(300)

        # 실제 콘텐츠 끝 위치
        content_end = await page.evaluate("""() => {
            const all = [...document.querySelectorAll('body *')];
            let maxY = 0;
            for (const el of all) {
                if (el.children.length > 0) continue;
                const r = el.getBoundingClientRect();
                if (r.height > 0 && r.width > 0 && r.bottom > 0) {
                    maxY = Math.max(maxY, r.bottom + window.scrollY);
                }
            }
            return maxY;
        }""")

        print(f"  콘텐츠 끝 위치: {content_end}px")

        png_full = await page.screenshot(
            type='png',
            full_page=True,
            clip={'x': 0, 'y': 0, 'width': 1400, 'height': min(content_end + 32, full_h)}
        )
        out_full = SHOTS_DIR / "new_00_full_initial.png"
        out_full.write_bytes(png_full)
        print(f"  ✅ 저장: {out_full.name}  ({len(png_full)//1024} KB)")

        await browser.close()

    print("\n\n✅  스크린샷 캡처 완료!")
    print(f"   저장 위치: {SHOTS_DIR}")
    print("\n📌  [화면 4~9]는 앱을 실행한 후 수동으로 캡처해야 합니다.")
    print("   (AI 분석 진행 중, RAG 결과, 리포트 뷰어 등 동적 화면)")


if __name__ == "__main__":
    asyncio.run(main())
