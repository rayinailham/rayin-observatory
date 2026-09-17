"""Phase 5 Development: all five case files, the Next instrument chain and returns.
Mobile Chromium checks only; the separate Testing harness owns the gate evidence pack.
Run from web/scripts (imports verify_case helpers). Server :8767 must be running.
"""
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright
from verify_case import PHONES, URL, enter, idle, scroll_to

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/case-files/dev'
DOSSIERS = Path(__file__).resolve().parents[2] / 'portfolio'  # Q41: dossiers in the project root
REPORT = {'status': 'running', 'scope': 'Phase 5 Development, Chromium mobile emulation', 'results': []}
# Mirrors lib/cases.ts on purpose: the page must render exactly these.
CASES = [
    {'id': 'crosscheck', 'name': 'CrossCheck', 'draft': False, 'duration': 126.9,
     'cards': ['Browser matrix', 'Access checks', 'End-to-end flows'], 'readings': ['1,080', '216', '18', '12']},
    {'id': 'surgeline', 'name': 'SurgeLine', 'draft': False, 'duration': 115.2,
     'cards': ['Work list', 'Parallel workers', 'Confirmation proof'], 'readings': ['48,273', '0', '7', '81,915']},
    {'id': 'driftwatch', 'name': 'DriftWatch', 'draft': False, 'duration': 118.2,
     'cards': ['Alarms', 'Change detection', 'Daily collection'], 'readings': ['11', '1,323', '12', '1']},
    {'id': 'duewatch', 'name': 'DueWatch', 'draft': False, 'duration': 102.5,
     'cards': ['Daily expiry check', 'Safe message triage', '24-hour follow-up'], 'readings': ['200', '7', '6', '12']},
    {'id': 'brandwall', 'name': 'BrandWall', 'draft': False, 'duration': 125.0,
     'cards': ['Test matrix', 'Measurement', 'Fix rules'], 'readings': ['300', '18', '11', '0']},
]


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'verification.json').write_text(json.dumps(REPORT, indent=2) + '\n')


def trace_numbers():
    """Every multi-digit reading must appear verbatim in its dossier."""
    missing = []
    for case in CASES:
        text = (DOSSIERS / f"CAPABILITY_{case['id'].upper()}.md").read_text()
        for value in case['readings']:
            if len(value) > 1 and not re.search(rf'(?<![\d,]){re.escape(value)}(?![\d,])', text):
                missing.append([case['id'], value])
    assert not missing, missing
    return True


async def inspect(page, case, width, height, shots):
    """Checks one open case page: copy state, hotspots, leaders, readings, lazy video."""
    await page.wait_for_function('(n)=>document.getElementById("case-heading")?.textContent===n', arg=case['name'])
    assert await page.locator('canvas').count() == 1
    assert await page.evaluate("window.__originalCanvas===document.querySelector('canvas')")
    assert await page.locator('.observatory').get_attribute('data-chapter') == case['id']
    assert await page.locator('.case-page .draft-label').count() == (1 if case['draft'] else 0)
    assert await page.evaluate('scrollY') < 2
    if shots:
        await page.screenshot(path=str(OUT / f"{case['id']}-brief-{width}x{height}.png"))
    await scroll_to(page, '#case-instrument')
    for i, title in enumerate(case['cards']):
        button = page.locator(f'.hotspot-{i}')
        box = await button.bounding_box()
        assert box['width'] >= 44 and box['height'] >= 44
        assert box['y'] >= 86 and box['y'] + box['height'] < height - 50, box
        await button.click()
        assert await page.locator('#component-card h3').inner_text() == title
        card = await page.locator('#component-card').bounding_box()
        assert card['y'] + card['height'] < height
        await page.wait_for_function("(i)=>Array.from(document.querySelectorAll('.instrument-hotspot')).every((e,n)=>getComputedStyle(e).backgroundColor===(n===i?'rgb(242, 165, 65)':'rgba(11, 16, 32, 0.93)'))", arg=i)
        await page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
        if shots:
            await page.screenshot(path=str(OUT / f"{case['id']}-hotspot-{i + 1}-{width}x{height}.png"))
    # Leaders are projected from real (and, for DueWatch, orbiting) GLB nodes every frame.
    points = await page.locator('[data-hotspot-line]').evaluate_all("els=>els.map(e=>[Number(e.getAttribute('x2')),Number(e.getAttribute('y2'))])")
    assert len(points) == 3 and all(0 < x < width and 100 < y < height for x, y in points), points
    cards = [await page.locator('.hotspot-{}'.format(i)).bounding_box() for i in range(3)]
    top_of_card = (await page.locator('#component-card').bounding_box())['y']
    assert all(b['y'] + b['height'] < top_of_card for b in cards)
    await page.get_by_role('button', name='Close component card').click()
    # CrossCheck explains its flow as the Phase 7A inspection field; the others keep the shared list.
    flow = {'crosscheck': '.inspection-steps li', 'surgeline': '.dispatch-steps li'}.get(case['id'], '.signal-flow li')
    assert await page.locator(flow).count() == 4
    for i, value in enumerate(case['readings']):
        await page.locator('.case-reading').nth(i).scroll_into_view_if_needed()
        await page.wait_for_function('(a)=>document.querySelectorAll("[data-count]")[a.i].textContent===a.v', arg={'i': i, 'v': value})
    if shots:
        await scroll_to(page, '#readings-heading', -110)
        await page.screenshot(path=str(OUT / f"{case['id']}-readings-{width}x{height}.png"))
    await page.locator('.case-limits summary').click()
    assert await page.locator('.case-limits p').count() == 2
    video = page.locator('.case-video')
    assert await video.get_attribute('poster') == f"/images/{case['id']}-demo-poster.jpg"
    await video.scroll_into_view_if_needed()
    await video.evaluate('(v)=>v.play()')
    await page.wait_for_function('document.querySelector("video").currentTime>.3')
    await video.evaluate('(v)=>v.pause()')
    duration = await video.evaluate('(v)=>v.duration')
    assert abs(duration - case['duration']) < 1, duration
    assert await page.locator('.case-next h2').inner_text() == CASES[(CASES.index(case) + 1) % 5]['name']
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    return {'points': points, 'duration': duration}


async def run():
    REPORT['startedAt'] = datetime.now(timezone.utc).isoformat()
    REPORT['readingsInDossiers'] = trace_numbers()
    save()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist'])
        for width, height in PHONES:
            print(f'Case files {width}x{height}', flush=True)
            context = await browser.new_context(viewport={'width': width, 'height': height}, is_mobile=True, has_touch=True)
            page = await context.new_page()
            errors, bad, videos = [], [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
            page.on('response', lambda response: bad.append([response.status, response.url]) if response.status >= 400 else None)
            page.on('request', lambda request: videos.append(request.url) if '/videos/' in request.url else None)
            await enter(page)
            await page.evaluate("window.__originalCanvas=document.querySelector('canvas')")
            result = {'viewport': [width, height], 'opened': [], 'chain': []}
            # Every homepage chapter opens its own case, and Return restores scroll + focus.
            for case in CASES:
                y = await scroll_to(page, '#' + case['id'], 280)
                await page.locator(f"[data-open-case={case['id']}]").click()
                await page.wait_for_function("document.querySelector('.observatory').dataset.flight==='moving'")
                await page.wait_for_url(f"{URL}/work/{case['id']}")
                await idle(page)
                assert not videos, videos
                await page.wait_for_function('(n)=>document.getElementById("case-heading")?.textContent===n', arg=case['name'])
                await page.locator('.case-brief .case-back').click()
                await page.wait_for_url(URL + '/')
                await idle(page)
                assert abs(await page.evaluate('scrollY') - y) < 2
                assert await page.locator(f"[data-open-case={case['id']}]").evaluate('(e)=>e===document.activeElement')
                result['opened'].append(case['id'])
            # Chain: CrossCheck → … → BrandWall → CrossCheck, inspecting each case on the way.
            await scroll_to(page, '#crosscheck', 280)
            await page.locator('[data-open-case=crosscheck]').click()
            await page.wait_for_url(URL + '/work/crosscheck')
            await idle(page)
            for n, case in enumerate(CASES):
                details = await inspect(page, case, width, height, shots=True)
                result['chain'].append({'id': case['id'], **details})
                nxt = CASES[(n + 1) % 5]
                await page.locator('.case-next .case-button').click()
                await page.wait_for_function("document.querySelector('.observatory').dataset.flight==='moving'")
                if n == 0 and width == 390:
                    await page.wait_for_timeout(900)
                    await page.screenshot(path=str(OUT / f'chain-sweep-{width}x{height}.png'))
                await page.wait_for_url(f"{URL}/work/{nxt['id']}")
                await idle(page)
            # History inside the chain, then Return lands on the current case's chapter.
            await page.go_back()
            await page.wait_for_url(URL + '/work/brandwall')
            await idle(page)
            await page.wait_for_function('document.getElementById("case-heading")?.textContent==="BrandWall"')
            await page.go_forward()
            await page.wait_for_url(URL + '/work/crosscheck')
            await idle(page)
            await page.locator('.case-next .case-button').click()
            await page.wait_for_url(URL + '/work/surgeline')
            await idle(page)
            await page.locator('.case-brief .case-back').click()
            await page.wait_for_url(URL + '/')
            await idle(page)
            assert abs(await page.locator('#surgeline').evaluate('(e)=>e.getBoundingClientRect().top')) < 2
            assert await page.evaluate("window.__originalCanvas===document.querySelector('canvas')")
            await page.screenshot(path=str(OUT / f'return-surgeline-{width}x{height}.png'))
            assert not errors, errors
            assert not bad, bad
            result.update({'errors': errors, 'badResponses': bad, 'chainReturn': 'surgeline'})
            REPORT['results'].append(result)
            save()
            await context.close()
        # Direct URLs never need homepage DOM; a blocked model still gives a labeled still view.
        context = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        page = await context.new_page()
        response = await page.goto(URL + '/work/unknown')
        assert response.status == 404
        for case in CASES:
            await enter(page, '/work/' + case['id'])
            await page.wait_for_function('(n)=>document.getElementById("case-heading")?.textContent===n', arg=case['name'])
            await page.locator('.case-brief .case-back').click()
            await page.wait_for_url(URL + '/')
            await idle(page)
            assert abs(await page.locator('#' + case['id']).evaluate('(e)=>e.getBoundingClientRect().top')) < 2
        await context.close()
        context = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        page = await context.new_page()
        await page.route('**/models/ambient.glb', lambda route: route.abort())
        await enter(page, '/work/duewatch')
        # Instruments load behind the hero, so a blocked model can fail after Enter.
        await page.wait_for_selector('.observatory[data-scene="fallback"]', state='attached', timeout=30000)
        await scroll_to(page, '#case-instrument')
        still = page.locator('.case-instrument-still')
        assert await still.is_visible()
        assert 'duewatch-fallback.png' in await still.evaluate('(e)=>getComputedStyle(e).backgroundImage')
        notice = await page.locator('.fallback-notice').bounding_box()
        heading = await page.locator('.case-instrument-heading').bounding_box()
        assert notice['y'] + notice['height'] <= heading['y'], (notice, heading)
        await page.locator('.hotspot-1').click()
        assert await page.locator('#component-card h3').inner_text() == 'Safe message triage'
        await page.screenshot(path=str(OUT / 'fallback-duewatch-390x844.png'))
        await context.close()
        REPORT['results'].append({'directEntry': [case['id'] for case in CASES], 'unknownSlug404': True, 'fallback': 'duewatch'})
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
