"""Phase 4 Development: route/camera state, hotspots, readings, media, and return.
Mobile Chromium checks only; the separate Testing harness owns the gate evidence pack.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/case-crosscheck/dev'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767').rstrip('/')
# Q42: OBSERVATORY_PHONES=390x844 narrows an older phase's regression to one phone (run_regressions.py --phone-only).
PHONES = [tuple(map(int, s.split('x'))) for s in os.environ.get('OBSERVATORY_PHONES', '390x844,360x740,430x932').split(',')]
ONLY_FALLBACK = '--fallback-only' in sys.argv
REPORT_NAME = 'fallback-verification.json' if ONLY_FALLBACK else 'verification.json'
REPORT = {'fallbackOnly': ONLY_FALLBACK, 'status': 'running', 'scope': 'Phase 4 Development, Chromium mobile emulation', 'results': []}


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / REPORT_NAME).write_text(json.dumps(REPORT, indent=2) + '\n')


async def idle(page):
    await page.wait_for_function("document.querySelector('.observatory').dataset.flight==='idle'")
    await page.wait_for_timeout(500)


async def enter(page, path=''):
    await page.goto(URL + path)
    await page.locator('.silent-button').click(timeout=30000)
    await page.wait_for_selector('.entry-gate[hidden]', state='attached')
    await idle(page)


async def scroll_to(page, selector, offset=0):
    y = await page.locator(selector).evaluate('(e)=>e.getBoundingClientRect().top+scrollY') + offset
    await page.evaluate('(y)=>scrollTo(0,y)', y)
    await page.wait_for_timeout(700)
    return y


async def open_case(page, capture=None):
    before = await page.evaluate('scrollY')
    await page.locator('[data-open-case=crosscheck]').click()
    await page.wait_for_function("document.querySelector('.observatory').dataset.flight==='moving'")
    await page.mouse.wheel(0, 180)
    await page.wait_for_timeout(150)
    assert abs(await page.evaluate('scrollY') - before) < 2
    if capture:
        opacity = await page.locator('.page-content').evaluate('(e)=>Number(getComputedStyle(e).opacity)')
        # A loaded renderer may finish the text fade before this sample; zero is valid.
        assert 0 <= opacity < 1, opacity
        await page.screenshot(path=str(OUT / capture))
    await page.wait_for_url(URL + '/work/crosscheck')
    await idle(page)


async def home(page, selector='.case-brief .case-back'):
    await page.locator(selector).click()
    await page.wait_for_url(URL + '/')
    await idle(page)


async def run():
    REPORT['startedAt'] = datetime.now(timezone.utc).isoformat()
    save()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist'])
        for width, height in ([] if ONLY_FALLBACK else PHONES):
            print(f'Case file {width}x{height}', flush=True)
            context = await browser.new_context(viewport={'width': width, 'height': height}, is_mobile=True, has_touch=True)
            page = await context.new_page()
            errors, bad, videos = [], [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
            page.on('response', lambda response: bad.append([response.status, response.url]) if response.status >= 400 else None)
            page.on('request', lambda request: videos.append(request.url) if '/videos/' in request.url else None)
            await enter(page)
            await page.evaluate("window.__originalCanvas=document.querySelector('canvas')")
            y = await scroll_to(page, '#crosscheck', 280)
            await open_case(page, f'flight-{width}x{height}.png')
            assert await page.evaluate("window.__originalCanvas===document.querySelector('canvas')")
            assert await page.locator('canvas').count() == 1
            assert await page.locator('.case-page .draft-label').count() == 0  # Phase 7A copy approved at the gate (2026-09-16)
            assert await page.evaluate('scrollY') < 2
            assert not videos, videos
            await page.screenshot(path=str(OUT / f'brief-{width}x{height}.png'))
            await scroll_to(page, '#case-instrument')
            for i, title in enumerate(['Browser matrix', 'Access checks', 'End-to-end flows']):
                button = page.locator(f'.hotspot-{i}')
                box = await button.bounding_box()
                assert box['width'] >= 44 and box['height'] >= 44
                assert box['y'] >= 86 and box['y'] + box['height'] < height - 50
                await button.click()
                assert await page.locator('#component-card h3').inner_text() == title
                assert await button.get_attribute('aria-expanded') == 'true'
                card = await page.locator('#component-card').bounding_box()
                assert card['y'] > box['y'] + box['height'] and card['y'] + card['height'] < height
                await page.wait_for_function("(i)=>Array.from(document.querySelectorAll('.instrument-hotspot')).every((e,n)=>getComputedStyle(e).backgroundColor===(n===i?'rgb(242, 165, 65)':'rgba(11, 16, 32, 0.93)'))", arg=i)
                await page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                await page.screenshot(path=str(OUT / f'hotspot-{i+1}-{width}x{height}.png'))
            line_points = await page.locator('[data-hotspot-line]').evaluate_all("els=>els.map(e=>[Number(e.getAttribute('x2')),Number(e.getAttribute('y2'))])")
            assert all(0 < x < width and 100 < y < height for x, y in line_points), line_points
            await page.get_by_role('button', name='Close component card').click()
            assert await page.locator('.instrument-hotspot[aria-expanded=true]').count() == 0
            # Phase 7A: How it works is the pinned inspection field (four approved steps), details in verify_crosscheck_room.py.
            await scroll_to(page, '#flow-heading', -110)
            assert await page.locator('.inspection-steps li').count() == 4
            assert await page.locator('.inspection-matrix [data-chip]').count() == 18
            await page.screenshot(path=str(OUT / f'flow-{width}x{height}.png'))
            await page.locator('.case-reading').first.scroll_into_view_if_needed()
            await page.wait_for_function("(()=>{const n=Number(document.querySelector('[data-count]').textContent.replaceAll(',',''));return n>0&&n<1080})()")
            for i, value in enumerate(['1,080', '216', '18', '12']):
                reading = page.locator('.case-reading').nth(i)
                await reading.scroll_into_view_if_needed()
                await page.wait_for_function('(args)=>document.querySelectorAll("[data-count]")[args.i].textContent===args.value', arg={'i': i, 'value': value})
            await scroll_to(page, '#readings-heading', -110)
            await page.screenshot(path=str(OUT / f'readings-{width}x{height}.png'))
            await page.locator('.case-limits summary').click()
            assert await page.locator('.case-limits').get_attribute('open') is not None
            await page.locator('.case-video').scroll_into_view_if_needed()
            assert not videos, videos
            await page.locator('.case-video').evaluate('(v)=>v.play()')
            await page.wait_for_function('document.querySelector("video").currentTime>.3')
            await page.locator('.case-video').evaluate('(v)=>v.pause()')
            duration = await page.locator('.case-video').evaluate('(v)=>v.duration')
            assert 126 < duration < 128
            await page.screenshot(path=str(OUT / f'demo-{width}x{height}.png'))
            assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            await home(page)
            assert abs(await page.evaluate('scrollY') - y) < 2
            assert await page.locator('[data-open-case=crosscheck]').evaluate('(e)=>e===document.activeElement')
            assert await page.evaluate("window.__originalCanvas===document.querySelector('canvas')")
            await page.screenshot(path=str(OUT / f'return-{width}x{height}.png'))
            await open_case(page)
            await page.go_back()
            await page.wait_for_url(URL + '/')
            await idle(page)
            assert abs(await page.evaluate('scrollY') - y) < 2
            await page.go_forward()
            await page.wait_for_url(URL + '/work/crosscheck')
            await idle(page)
            await home(page, '.case-tools a >> nth=0')
            assert abs(await page.locator('#skills').evaluate('(e)=>e.getBoundingClientRect().top')) < 2
            await scroll_to(page, '#crosscheck', 280)
            await open_case(page)
            # Phase 5: Next chains to the SurgeLine case; its Return lands on the SurgeLine chapter.
            await page.locator('.case-next .case-button').click()
            await page.wait_for_url(URL + '/work/surgeline')
            await idle(page)
            await home(page)
            assert abs(await page.locator('#surgeline').evaluate('(e)=>e.getBoundingClientRect().top')) < 2
            assert await page.evaluate("window.__originalCanvas===document.querySelector('canvas')")
            assert not errors, errors
            assert not bad, bad
            REPORT['results'].append({'viewport': [width, height], 'caseAndReturn': True, 'flightFadeAndScrollLock': True, 'persistentCanvas': True,
                'hotspots': 3, 'projectedLensPoints': line_points, 'flow': True, 'readings': True, 'countUpObserved': True, 'lazyVideoPlayback': duration,
                'browserBackForward': True, 'toolsToSkills': True, 'nextChainsToSurgeLine': True, 'errors': errors, 'badResponses': bad})
            save()
            await context.close()
        # A fresh direct URL (and reload) must never need homepage DOM or history.
        for fallback in ([True] if ONLY_FALLBACK else [False, True]):
            context = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
            page = await context.new_page()
            if fallback:
                await page.route('**/models/ambient.glb', lambda route: route.abort())
            await enter(page, '/work/crosscheck')
            if fallback:
                # ambient.glb is the one model still fetched; blocking it fails the scene.
                await page.wait_for_selector('.observatory[data-scene="fallback"]', state='attached', timeout=30000)
                await scroll_to(page, '#case-instrument')
                assert await page.locator('.case-instrument-still').is_visible()
                notice = await page.locator('.fallback-notice').bounding_box()
                heading = await page.locator('.case-instrument-heading').bounding_box()
                assert notice['y'] + notice['height'] <= heading['y'], (notice, heading)
                await page.locator('.hotspot-1').click()
                assert await page.locator('#component-card h3').inner_text() == 'Access checks'
                await page.screenshot(path=str(OUT / 'fallback-390x844.png'))
            else:
                await page.reload()
                await page.locator('.silent-button').click(timeout=30000)
                await page.wait_for_selector('.entry-gate[hidden]', state='attached')
                await idle(page)
            await home(page)
            assert abs(await page.locator('#crosscheck').evaluate('(e)=>e.getBoundingClientRect().top')) < 2
            REPORT['results'].append({'directEntry': True, 'fallback': fallback, 'returnWithoutHistory': True})
            save()
            await context.close()
        await browser.close()
    REPORT['status'] = 'passed'
    REPORT['finishedAt'] = datetime.now(timezone.utc).isoformat()
    save()


if __name__ == '__main__':
    try:
        asyncio.run(run())
    except Exception as error:
        REPORT['status'] = 'failed'
        REPORT['error'] = repr(error)
        save()
        raise
