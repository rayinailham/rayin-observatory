"""7C Development checks (Q49 update in 7F: hand-turned trace, roller curtain); viewport()/edges() are reusable by the Testing evidence pack.
No collection requests; the room's illustrative rows stay separate from recorded evidence.
Run via run_regressions.py. --sizes and --no-edges support mobile-first development.
"""
import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright
import q49

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/personal-driftwatch/dev'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767').rstrip('/')
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']
SIZES = os.environ.get('OBSERVATORY_PHONES', '390x844,360x740,430x932,768x1024,1440x900,1920x1080')


async def idle(page):
    await page.wait_for_function("document.querySelector('.observatory')?.dataset.flight==='idle'")
    await page.wait_for_timeout(450)


async def enter(page, path='/'):
    await page.goto(URL + path)
    await page.locator('.silent-button').click(timeout=60000)
    await page.wait_for_selector('.has-entered')
    await idle(page)
    await page.wait_for_timeout(600)


async def land(page, y):
    for _ in range(12):
        await page.evaluate('(y)=>scrollTo(0,y)', y)
        await page.wait_for_timeout(120)
        if abs(await page.evaluate('scrollY') - min(y, await page.evaluate('document.documentElement.scrollHeight-innerHeight'))) < 3:
            return
    raise AssertionError(('scroll not settled', y, await page.evaluate('scrollY')))


async def at(page, selector, offset=-110):
    await land(page, await page.locator(selector).evaluate('(e,o)=>e.getBoundingClientRect().top+scrollY+o', offset))


async def shot(page, name):
    OUT.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(OUT / f'{name}.png'))


async def compare(page, scenario, touch):
    await at(page, '.monitor-scenarios')
    button = page.locator(f'[data-scenario-choice={scenario}]')
    await (button.tap() if touch else button.click())
    assert await page.locator('.monitoring-room').get_attribute('data-compared') == 'false'
    await at(page, '[data-compare]')
    button = page.locator('[data-compare]')
    await (button.tap() if touch else button.click())
    await page.wait_for_timeout(900)
    room = page.locator('.monitoring-room')
    expected = 'healthy' if scenario in ('change', 'recovery') else 'alarm'
    assert await room.get_attribute('data-verdict') == expected
    assert await page.locator(f'[data-diff={scenario}]').count() == 1
    assert await page.locator('[data-snapshot=baseline] li').count() == 3
    if scenario == 'change':
        assert await page.locator('[data-change]').count() == 4
        assert await page.locator('del').inner_text() == 'Getting started'
        assert await page.locator('ins').inner_text() == 'Getting started with the API'
        assert await page.locator('.monitor-codes').count() == 0
    elif scenario == 'recovery':
        assert 'Failed' in await page.locator('.monitor-failed-day').inner_text()
        assert 'Baseline remains Day 1' in await page.locator('.monitor-resolved').inner_text()
    else:
        assert await page.locator('[data-snapshot=current] li').count() == 0
        await page.locator('.monitor-codes summary').click()
        codes = await page.locator('.monitor-codes code').all_text_contents()
        assert codes == (['RUN_MISSING'] if scenario == 'missing' else ['ZERO_RECORDS', 'RECORD_COUNT_DROP', 'FIELD_COMPLETENESS_DROP', 'RUN_FAILED', 'CHURN_SPIKE'])
        text = await page.locator('.monitor-result').inner_text()
        assert ('pipeline health' if scenario in ('pipeline', 'missing') else 'source comparison') in text.lower()
    return expected


async def viewport(browser, width, height):
    touch = width < 1024
    context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=2 if touch else 1, is_mobile=touch, has_touch=touch)
    page = await context.new_page()
    errors, requests = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('response', lambda r: requests.append([r.status, r.url]) if r.status >= 400 else None)
    await enter(page)
    await page.evaluate('window.__monitorCanvas=document.querySelector("canvas")')
    # Q49: one-screen chapter; the trace draws with the visitor's hand turn of the seismograph.
    await q49.to_chapter(page, 'driftwatch')
    trace = []
    for p in (.2, .8, .2):
        await q49.turn(page, 'driftwatch', p)
        read = r'e=>Number(getComputedStyle(e).strokeDashoffset.match(/[-\d.]+/)[0])'
        value = None
        for _ in range(20):
            await page.wait_for_timeout(100)
            sample = await page.locator('.monitor-chapter-line').evaluate(read)
            if sample == value:
                break
            value = sample
        trace.append(value)
    assert trace[1] < trace[0] and abs(trace[0] - trace[2]) < .03, trace
    await shot(page, f'chapter-{width}x{height}')
    origin = await page.evaluate('scrollY')
    # The chart-paper roller closes, the route changes behind it, and it rolls up again.
    await q49.watch_curtain(page)
    button = page.locator('[data-open-case=driftwatch]')
    await (button.tap() if touch else button.click())
    log = await q49.curtain_log(page, '/work/driftwatch')
    assert q49.closed_styles(log) == ['roller'], log
    await idle(page)
    assert await page.locator('.case-page .draft-label').count() == 0  # copy approved at gate 7C
    assert await page.locator('#case-heading').evaluate('e=>e===document.activeElement')
    await at(page, '#case-instrument', 0)
    for i in range(3):
        await page.locator(f'.hotspot-{i}').click()
        card = await page.locator('#component-card').bounding_box()
        assert card['y'] + card['height'] < height + 2, card
    await page.locator('[aria-label="Close component card"]').click()
    assert await page.locator('.monitor-steps li').count() == 4
    assert 'fictional pages and example days' in await page.locator('.monitor-disclosure').inner_text()
    # Illustrated failures must not borrow the recorded soak's calendar dates.
    assert ' Sep ' not in await page.locator('.monitoring-room').inner_text()
    results = {}
    for scenario in ('change', 'layout', 'pipeline', 'missing', 'recovery'):
        results[scenario] = await compare(page, scenario, touch)
        await at(page, '.monitor-result')
        await shot(page, f'{scenario}-{width}x{height}')
    # Scroll away/back preserves explicit comparison; repeated input settles on the last choice.
    await at(page, '#readings-heading')
    await at(page, '.monitor-result')
    assert await page.locator('.monitoring-room').get_attribute('data-scenario') == 'recovery'
    await page.evaluate("document.querySelector('[data-scenario-choice=layout]').click();document.querySelector('[data-compare]').dispatchEvent(new MouseEvent('click',{bubbles:true,detail:1}));document.querySelector('[data-scenario-choice=change]').click();document.querySelector('[data-compare]').dispatchEvent(new MouseEvent('click',{bubbles:true,detail:1}))")
    await page.wait_for_timeout(1000)
    assert await page.locator('.monitoring-room').get_attribute('data-verdict') == 'healthy'
    assert await page.locator('[data-diff=change]').count() == 1
    await at(page, '.monitor-snapshots')
    snaps = await page.locator('.monitor-snapshot').evaluate_all('es=>es.map(e=>({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y,w:e.offsetWidth}))')
    assert (abs(snaps[0]['y'] - snaps[1]['y']) < 2) if width >= 1024 else (snaps[1]['y'] > snaps[0]['y'] + 150), snaps
    await shot(page, f'snapshots-{width}x{height}')
    if width >= 1024:
        await page.locator('.monitor-workspace').screenshot(path=str(OUT / f'workspace-{width}x{height}.png'))
    await at(page, '.monitoring-evidence')
    evidence = await page.locator('.monitoring-evidence').inner_text()
    assert all(t in evidence for t in ('1,323', '11/11', '12/12', 'indirectly', '13 Sep 2026', 'public sources stayed unchanged'))
    await shot(page, f'archive-{width}x{height}')
    await at(page, '.case-next')
    assert 'DueWatch' in await page.locator('.monitor-next').inner_text()
    await page.locator('.case-next .case-back').click()
    await page.wait_for_url(URL + '/')
    await idle(page)
    assert abs(await page.evaluate('scrollY') - origin) < 4
    assert await page.locator('[data-open-case=driftwatch]').evaluate('e=>e===document.activeElement')
    await page.locator('[data-open-case=driftwatch]').click()
    await page.wait_for_url('**/work/driftwatch')
    await idle(page)
    await at(page, '.case-next')
    await q49.watch_curtain(page)
    await page.locator('[data-case-target=duewatch]').click()
    log = await q49.curtain_log(page, '/work/duewatch')
    # Hand-over to DueWatch: the roller comes down, DueWatch's time slots open.
    assert q49.closed_styles(log) == ['roller'] and ['moving', 'louvre', '/work/duewatch'] in log, log
    await idle(page)
    await page.go_back()
    await idle(page)
    assert page.url.endswith('/work/driftwatch')
    await page.go_forward()
    await idle(page)
    assert page.url.endswith('/work/duewatch')
    assert await page.evaluate('document.querySelectorAll("canvas").length===1 && window.__monitorCanvas===document.querySelector("canvas")')
    await enter(page, '/work/driftwatch')
    assert await page.locator('.monitoring-room').get_attribute('data-compared') == 'false'
    await page.reload()
    await page.locator('.silent-button').click(timeout=60000)
    await idle(page)
    assert await page.locator('.monitoring-room').count() == 1
    assert await page.evaluate('document.documentElement.scrollWidth-innerWidth') <= 1
    assert not errors and not requests, (errors, requests)
    await context.close()
    return {'viewport': [width, height], 'status': 'passed', 'scenarios': results, 'trace': trace, 'errors': errors, 'requests': requests}


async def edges(browser):
    results = []
    for reduced, fallback in ((False, True), (True, False)):
        context = await browser.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce' if reduced else 'no-preference')
        page = await context.new_page()
        if fallback:
            await page.route('**/models/ambient.glb', lambda route: route.abort())
        await enter(page, '/work/driftwatch')
        await compare(page, 'layout', False)
        if fallback:
            assert await page.locator('.observatory').get_attribute('data-scene') == 'fallback'
            assert await page.locator('.case-inspection').get_attribute('data-leaders') != 'live'
        if reduced:
            assert await page.locator('.monitor-result').evaluate('e=>getComputedStyle(e).opacity') == '1'
            assert await page.locator('.curtain').get_attribute('data-state') == 'open'
        await shot(page, 'fallback' if fallback else 'reduced')
        await page.set_viewport_size({'width': 1440, 'height': 900})
        await page.wait_for_timeout(300)
        assert await page.locator('.monitoring-room').get_attribute('data-verdict') == 'alarm'
        assert await page.evaluate('document.documentElement.scrollWidth-innerWidth') <= 1
        await page.set_viewport_size({'width': 390, 'height': 844})
        await at(page, '.case-next')
        await page.locator('.case-next .case-back').click()
        await page.wait_for_url(URL + '/')
        await idle(page)
        await q49.to_chapter(page, 'driftwatch')
        await page.locator('[data-open-case=driftwatch]').click()
        await page.wait_for_url('**/work/driftwatch')
        await idle(page)
        await page.locator('.case-brief .case-back').click()
        await page.wait_for_timeout(120)
        await page.go_back()
        await idle(page)
        await page.wait_for_timeout(1200)
        assert await page.locator('.curtain').get_attribute('data-state') == 'open'
        results.append({'mode': 'fallback' if fallback else 'reduced', 'status': 'passed'})
        await context.close()
    return results


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', default=SIZES)
    parser.add_argument('--no-edges', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'status': 'running', 'scope': '7C Development; Chromium emulation, not gate evidence', 'results': [], 'edges': []}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=GPU)
            for size in args.sizes.split(','):
                w, h = map(int, size.split('x'))
                report['results'].append(await viewport(browser, w, h))
                print('PASS', size, flush=True)
            if not args.no_edges:
                report['edges'] = await edges(browser)
            await browser.close()
        report['status'] = 'passed'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = str(error)
        raise
    finally:
        report['finishedAt'] = datetime.now(timezone.utc).isoformat()
        (OUT / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    asyncio.run(main())
