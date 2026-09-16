"""Phase 7A Development: CrossCheck inspection room, mobile first then tablet and desktop.

Chapter lane strip (fills with the orbit, follows the lenses) → lens iris into the case → leaders only
on a model → pinned inspection field scrubbed forward, backward and by fast flicks → four findings with
evidence → Next teaser → iris back into the chapter lens. Edge cases on 390×844: Back during the
flight, model blocked (still view), reduced motion. Not the Testing evidence pack.

Run from web/scripts with the production preview on :8767:
  timeout 900 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python verify_crosscheck_room.py [--sizes 390x844,1440x900]
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/personal-crosscheck/dev'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767').rstrip('/')
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']
SIZES = [(390, 844), (360, 740), (430, 932), (768, 1024), (1440, 900), (1920, 1080)]
if '--sizes' in sys.argv:
    SIZES = [tuple(map(int, s.split('x'))) for s in sys.argv[sys.argv.index('--sizes') + 1].split(',')]
EDGES = '--no-edges' not in sys.argv
FINDINGS = {'CC-003': ('flow', 1), 'CC-001': ('access', 2), 'CC-017': ('matrix', 9), 'CC-015': ('matrix', 27)}
REPORT = {'scope': 'Phase 7A Development, Chromium emulation', 'status': 'running', 'results': [], 'edges': {}}


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'verification.json').write_text(json.dumps(REPORT, indent=2) + '\n')


async def idle(page):
    await page.wait_for_function("document.querySelector('.observatory').dataset.flight==='idle'", timeout=20000)
    await page.wait_for_timeout(400)


async def enter(page, path=''):
    await page.goto(URL + path)
    await page.locator('.silent-button').click(timeout=30000)
    await page.wait_for_selector('.entry-gate[hidden]', state='attached')
    await idle(page)


async def land(page, y):
    """Native scroll that survives a Lenis tail: repeat until the page actually sits at y."""
    for _ in range(12):
        await page.evaluate('(y)=>scrollTo(0,y)', y)
        await page.wait_for_timeout(250)
        if abs(await page.evaluate('scrollY') - min(y, await page.evaluate('document.documentElement.scrollHeight-innerHeight'))) < 3:
            return
    raise AssertionError(f'could not land at {y}')


async def field_at(page, p):
    y = await page.locator('.inspection-field').evaluate('(e,p)=>e.getBoundingClientRect().top+scrollY+p*(e.offsetHeight-innerHeight)', p)
    await land(page, y)
    await page.wait_for_function('(p)=>Math.abs(Number(document.querySelector(".inspection-matrix").dataset.progress)-p)<.015', arg=p, timeout=5000)
    return await page.evaluate('({step: Number(document.querySelector(".inspection-field").dataset.step), progress: Number(document.querySelector(".inspection-matrix").dataset.progress), stageTop: document.querySelector(".inspection-stage").getBoundingClientRect().top, active: document.querySelector(".inspection-steps li[data-active=true] h3").textContent})')


async def iris_trace(page, until_path, limit=4000, capture=None):
    """Poll the iris while a flight runs; returns the ordered distinct states and centres.
    `capture` = (state, radius px, path): one screenshot once that state passes that radius."""
    seen, centres = [], []
    for _ in range(limit // 40):
        state = await page.evaluate("(()=>{const e=document.querySelector('.lens-iris');return [e.dataset.state,parseFloat(e.style.getPropertyValue('--iris-x'))||0,parseFloat(e.style.getPropertyValue('--iris-y'))||0,location.pathname]})()")
        if not seen or seen[-1] != state[0]:
            seen.append(state[0])
        if state[0] != 'hidden':
            centres.append(state[1:3])
        if capture and state[0] == capture[0] and await page.evaluate("parseFloat(document.querySelector('.lens-iris').style.getPropertyValue('--iris-r'))") > capture[1]:
            await page.screenshot(path=capture[2])
            capture = None
        if state[3] == until_path and state[0] == 'hidden' and len(seen) > 1:
            break
        await page.wait_for_timeout(40)
    return seen, centres


async def overflow(page):
    return await page.evaluate('document.documentElement.scrollWidth-innerWidth')


async def viewport(browser, width, height):
    tag = f'{width}x{height}'
    wide = width >= 1024
    phone = width < 431
    context = await browser.new_context(viewport={'width': width, 'height': height}, is_mobile=width < 1024, has_touch=width < 1024, device_scale_factor=2 if phone else 1)
    page = await context.new_page()
    errors, bad = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('response', lambda r: bad.append([r.status, r.url]) if r.status >= 400 else None)
    result = {'viewport': tag}
    shot = lambda name: page.screenshot(path=str(OUT / f'{name}-{tag}.png'))

    await enter(page)
    await page.evaluate("window.__canvas=document.querySelector('canvas')")
    # A. Chapter lane strip: fills with the orbit, follows the lenses.
    section = await page.locator('#crosscheck').evaluate('e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight})')
    fills = []
    for p in (0, .5, 1):
        await land(page, section['top'] + p * (section['h'] - height))
        await page.wait_for_timeout(500)
        fills.append(await page.evaluate("[...document.querySelectorAll('.scan-lane i')].filter(i=>Number(getComputedStyle(i,'::after').opacity)>.5).length"))
    assert fills[0] <= 3 and fills[1] > fills[0] and fills[2] == 27, fills
    await land(page, section['top'] + .45 * (section['h'] - height))
    lanes = set()
    for _ in range(36):
        lanes.add(await page.evaluate("document.querySelector('.observatory').dataset.scan"))
        await page.wait_for_timeout(200)
    assert {'0', '1', '2', 'agree'} <= lanes, lanes
    strip = await page.locator('.scan-strip').bounding_box()
    button = await page.locator('[data-open-case=crosscheck]').bounding_box()
    assert strip['y'] >= button['y'] + button['height'] and strip['y'] + strip['height'] < height - 20, (strip, button)
    await page.wait_for_function("document.querySelector('.observatory').dataset.scan==='agree'", timeout=8000)
    await shot('chapter-scan')
    result['chapterStrip'] = {'litCells': fills, 'lanesSeen': sorted(lanes)}
    origin = await page.evaluate('scrollY')

    # B. Into the case through the lens.
    await page.locator('[data-open-case=crosscheck]').click()
    states, centres = await iris_trace(page, '/work/crosscheck', capture=('disc', width * .35, str(OUT / f'iris-closing-{tag}.png')))
    assert states[:3] == ['disc', 'hole', 'hidden'] or states[:4] == ['hidden', 'disc', 'hole', 'hidden'], states
    assert all(0 <= x <= width and 0 <= y <= height for x, y in centres), centres
    await idle(page)
    assert await page.evaluate("document.activeElement.id") == 'case-heading'
    result['irisIn'] = states
    # C. Leaders only once projected onto the model.
    await page.locator('#case-instrument').scroll_into_view_if_needed()
    await page.wait_for_selector('.case-inspection[data-leaders=live]', timeout=10000)
    opacity = await page.locator('[data-hotspot-line]').first.evaluate('e=>Number(getComputedStyle(e).opacity)')
    assert opacity > .3, opacity
    await page.locator('.hotspot-0').click()
    card = await page.locator('#component-card').bounding_box()
    assert card['y'] + card['height'] <= height + 1, card
    await page.wait_for_timeout(300)
    await shot('case-hotspot')
    await page.get_by_role('button', name='Close component card').click()

    # D. Inspection field: forward, backward, flick.
    forward = [await field_at(page, p) for p in (0, .3, .62, .9, 1)]
    steps = [f['step'] for f in forward]
    assert steps == sorted(steps) and steps[0] == 0 and steps[-1] == 3, forward
    assert all(abs(f['stageTop']) < 2 for f in forward), forward
    for p in (.3, .62, 1):
        await field_at(page, p)
        await shot(f'field-{int(p * 100):03d}')
    chips = await page.evaluate("[...document.querySelectorAll('[data-chip]')].map(c=>Number(c.style.fillOpacity))")
    assert len(chips) == 18 and min(chips) > .95, chips
    back = await field_at(page, .3)
    assert back['step'] == 1 and back['active'] == 'Run the checks', back
    chips = await page.evaluate("Math.max(...[...document.querySelectorAll('[data-chip]')].map(c=>Number(c.style.fillOpacity)))")
    assert chips < .05, chips
    top = await page.locator('.inspection-field').evaluate('e=>e.getBoundingClientRect().top+scrollY')
    h = await page.locator('.inspection-field').evaluate('e=>e.offsetHeight-innerHeight')
    for y in (top, top + h, top + .2 * h, top + h * .95, top + .5 * h):
        await page.evaluate('(y)=>scrollTo(0,y)', y)
        await page.wait_for_timeout(30)
    flick = await field_at(page, .5)
    assert flick['step'] == 1, flick
    labels = await page.evaluate("[...document.querySelectorAll('.lane-label')].map(t=>t.getBoundingClientRect().width>0)")
    assert all(labels) and len(labels) == 3
    svg = await page.locator('.inspection-matrix').bounding_box()
    assert svg['height'] > (300 if not wide else 420) and svg['x'] >= 0 and svg['x'] + svg['width'] <= width + 1, svg
    result['field'] = {'forward': forward, 'backTo30': back, 'afterFlick': flick, 'svg': svg}

    # E. Findings: every card selects its own evidence.
    await page.locator('#findings-heading').scroll_into_view_if_needed()
    per = {}
    for i, (finding, (layer, hits)) in enumerate(FINDINGS.items()):
        tab = page.locator(f'[data-finding="{finding}"].finding-tab')
        box = await tab.bounding_box()
        assert box['height'] >= 44
        await tab.click()
        await page.wait_for_function('(id)=>document.querySelector("#finding-evidence").dataset.finding===id', arg=finding)
        assert await tab.get_attribute('aria-pressed') == 'true'
        count = await page.locator('#finding-evidence [data-hit=true]').count()
        assert count == hits, (finding, count)
        await page.locator('#finding-evidence .finding-shot img').first.scroll_into_view_if_needed()
        # Hidden figures (mobile toggle) stay lazy until shown; check the visible ones.
        await page.wait_for_function("[...document.querySelectorAll('#finding-evidence .finding-shot img')].filter(i=>i.getBoundingClientRect().height>0).every(i=>i.complete&&i.naturalWidth>0)", timeout=10000)
        figures = await page.locator('#finding-evidence .finding-shot').evaluate_all('els=>els.map(e=>e.getBoundingClientRect().height>0)')
        if len(figures) == 2:
            assert figures == ([True, True] if wide else [True, False]), (finding, figures)
            if not wide:
                await page.locator('.finding-proof-toggle button').nth(1).click()
                figures = await page.locator('#finding-evidence .finding-shot').evaluate_all('els=>els.map(e=>e.getBoundingClientRect().height>0)')
                assert figures == [False, True], figures
                await page.wait_for_function("[...document.querySelectorAll('#finding-evidence .finding-shot img')][1].naturalWidth>0", timeout=10000)
        steps_text = await page.locator('#finding-evidence .finding-repro ol li').count()
        assert steps_text >= 2
        await page.locator('#finding-evidence').scroll_into_view_if_needed()
        await shot(f'finding-{finding.lower()}')
        per[finding] = {'hits': count, 'figures': len(figures), 'steps': steps_text}
        assert await overflow(page) <= 1, (finding, 'overflow')
    result['findings'] = per

    # F. Next teaser, then back into the chapter lens.
    teaser = await page.locator('.case-next-deck').inner_text()
    assert 'Every row sent once.' in teaser and 'Every success proven.' in teaser, teaser
    await page.locator('#next-heading').scroll_into_view_if_needed()
    await shot('next-teaser')
    await page.locator('.case-next .case-back').click()
    states, centres = await iris_trace(page, '/', capture=('disc', width * .25, str(OUT / f'iris-return-{tag}.png')))
    assert 'hole' in states and 'disc' in states and states[-1] == 'hidden', states
    await idle(page)
    assert abs(await page.evaluate('scrollY') - origin) < 3
    assert await page.evaluate("document.querySelector('canvas')===window.__canvas && document.querySelectorAll('canvas').length===1")
    result['irisOut'] = states
    result['overflow'] = await overflow(page)
    assert result['overflow'] <= 1
    assert not errors, errors
    assert not bad, bad
    result['pass'] = True
    await context.close()
    return result


async def edges(browser):
    out = {}
    # Back during the flight: the iris must still clear and the homepage stays usable.
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    page = await context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    await enter(page)
    await land(page, await page.locator('#crosscheck').evaluate('e=>e.getBoundingClientRect().top+scrollY+300'))
    await page.locator('[data-open-case=crosscheck]').click()
    await page.wait_for_url(URL + '/work/crosscheck', timeout=5000)
    await page.go_back()
    await page.wait_for_url(URL + '/')
    await page.wait_for_function("document.querySelector('.lens-iris').dataset.state==='hidden'", timeout=4000)
    await idle(page)
    assert not errors, errors
    out['backDuringFlight'] = 'iris cleared, homepage idle'
    await context.close()

    # Model blocked: still view, no leaders into empty space, iris still clears.
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await page.route('**/models/ambient.glb', lambda route: route.abort())
    await enter(page)
    await page.wait_for_selector('.observatory[data-scene=fallback]', timeout=20000)
    await land(page, await page.locator('#crosscheck').evaluate('e=>e.getBoundingClientRect().top+scrollY+300'))
    await page.locator('[data-open-case=crosscheck]').click()
    await page.wait_for_url(URL + '/work/crosscheck')
    await idle(page)
    await page.wait_for_function("document.querySelector('.lens-iris').dataset.state==='hidden'", timeout=4000)
    await page.locator('#case-instrument').scroll_into_view_if_needed()
    await page.wait_for_timeout(500)
    assert await page.locator('.case-inspection[data-leaders]').count() == 0
    lines = await page.locator('[data-hotspot-line]').evaluate_all('els=>els.map(e=>Number(getComputedStyle(e).opacity))')
    still = await page.locator('.case-instrument-still').bounding_box()
    assert max(lines) == 0 and still and still['height'] > 100, (lines, still)
    await page.screenshot(path=str(OUT / 'fallback-case-390x844.png'))
    out['fallback'] = {'leaderOpacity': lines, 'still': still}
    await context.close()

    # Reduced motion: final state at once, no iris.
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, reduced_motion='reduce')
    page = await context.new_page()
    await enter(page, '/work/crosscheck')
    await page.locator('.inspection-field').scroll_into_view_if_needed()
    await page.wait_for_timeout(400)
    state = await page.evaluate("({step: document.querySelector('.inspection-field').dataset.step, chips: Math.min(...[...document.querySelectorAll('[data-chip]')].map(c=>Number(c.style.fillOpacity)))})")
    assert state == {'step': '3', 'chips': 1}, state
    await page.locator('.case-brief .case-back').click()
    await page.wait_for_url(URL + '/')
    assert await page.evaluate("document.querySelector('.lens-iris').dataset.state") == 'hidden'
    await page.screenshot(path=str(OUT / 'reduced-motion-field-390x844.png'))
    out['reducedMotion'] = state
    await context.close()
    return out


async def run():
    REPORT['startedAt'] = datetime.now(timezone.utc).isoformat()
    save()
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=GPU)
            for width, height in SIZES:
                print(f'CrossCheck room {width}x{height}', flush=True)
                REPORT['results'].append(await viewport(browser, width, height))
                save()
            if EDGES:
                print('edges', flush=True)
                REPORT['edges'] = await edges(browser)
            await browser.close()
        REPORT['status'] = 'passed'
    except Exception as error:
        REPORT['status'] = 'failed'
        REPORT['error'] = repr(error)
        raise
    finally:
        REPORT['finishedAt'] = datetime.now(timezone.utc).isoformat()
        save()


if __name__ == '__main__':
    asyncio.run(run())
