"""7E Development (Q49 update in 7F: hand-turned chapter, prism curtain). Reusable viewport/edges for the separate Testing evidence pack.
Run via run_regressions.py --suites studio. --sizes allows mobile-before-desktop checks.
"""
import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright
from verify_case import URL, enter, idle
from perf_quick import GPU, land
from run_regressions import fingerprint
from q49 import to_chapter, turn, watch_curtain, curtain_log, closed_styles

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/personal-brandwall/dev'


async def position(page, selector):
    await land(page, await page.locator(selector).evaluate('e=>e.getBoundingClientRect().top+scrollY-110'))


async def shot(page, name):
    OUT.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(OUT / f'{name}.png'))


async def viewport(browser, width, height):
    tag = f'{width}x{height}'
    context = await browser.new_context(viewport={'width': width, 'height': height}, has_touch=width<1024, is_mobile=width<1024)
    page = await context.new_page()
    errors, bad = [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.on('response', lambda r: bad.append([r.status, r.url]) if r.status >= 400 else None)
    await enter(page)
    await page.evaluate('window.__studioCanvas=document.querySelector("canvas")')
    # Q49: the chapter is one screen; the visitor turns the prism by hand and the beam follows that turn.
    await to_chapter(page, 'brandwall')
    orbit = []
    for p in (.15, .8, .15):
        await turn(page, 'brandwall', p)
        orbit.append(await page.locator('.brand-chapter-beam').evaluate('e=>getComputedStyle(e).transform'))
    assert orbit[0] != orbit[1] and orbit[0] == orbit[2], orbit
    await shot(page, f'chapter-{tag}')
    origin = await page.evaluate('scrollY')
    await watch_curtain(page)
    await page.locator('[data-open-case=brandwall]').click()
    await page.wait_for_function("document.querySelector('.curtain').dataset.state==='moving'")
    await page.wait_for_timeout(260)
    await shot(page, f'prism-{tag}')
    log = await curtain_log(page, '/work/brandwall')
    assert closed_styles(log) == ['prism'], log
    await idle(page)
    assert await page.locator('.case-page .draft-label').count() == 0  # copy approved at gate 7E
    assert await page.evaluate('window.__studioCanvas===document.querySelector("canvas")')
    await position(page, '#case-instrument')
    for n, title in enumerate(('Test matrix', 'Measurement', 'Fix rules')):
        await page.locator(f'.hotspot-{n}').click()
        assert await page.locator('#component-card h3').inner_text() == title
    await page.get_by_role('button', name='Close component card').click()
    await position(page, '.brand-studio')
    assert await page.locator('.brand-steps li').count() == 4
    for specimen in ('portrait', 'contrast', 'name'):
        await position(page, '.brand-contact-sheet')
        await page.locator(f'[data-specimen-choice={specimen}]').click()
        assert await page.locator('.brand-studio').get_attribute('data-specimen') == specimen
        await position(page, '.brand-view-controls')
        for mode, clip in (('before', '100%'), ('split', '50%'), ('after', '0%')):
            await page.locator(f'[data-brand-view={mode}]').click()
            await page.wait_for_timeout(260)
            assert await page.locator('.brand-studio').get_attribute('data-view') == mode
            assert clip in await page.locator('.brand-after').evaluate('e=>e.style.clipPath')
            views = await page.locator('.brand-pair svg').evaluate_all('es=>es.map(e=>e.getAttribute("viewBox"))')
            assert views[0] == views[1], views
            await shot(page, f'{specimen}-{mode}-{tag}')
    if width >= 1024:
        layout = await page.evaluate('''() => {
          const a=document.querySelector('.brand-contact-sheet').getBoundingClientRect();
          const b=document.querySelector('.brand-comparison').getBoundingClientRect();
          return {galleryRight:a.right,comparisonLeft:b.left,comparisonWidth:b.width};
        }''')
        assert layout['galleryRight'] < layout['comparisonLeft'] and layout['comparisonWidth'] > width*.45, layout
    # Rapid changes must settle at the last choice, with no queued animation.
    await page.evaluate("['before','after','split','before'].forEach(x=>document.querySelector(`[data-brand-view=${x}]`).click())")
    await page.wait_for_timeout(260)
    assert await page.locator('.brand-after').evaluate('e=>getComputedStyle(e).clipPath') == 'inset(0px 100% 0px 0px)'
    await page.locator('.brand-source summary').click()
    assert await page.locator('.brand-source a').count() == 2
    await position(page, '.brand-boundary-controls')
    for axis, safe, broken in (('ratio','1.00','1.25'),('light','0.30','0.35'),('length','28','32')):
        await page.locator(f'[data-boundary={axis}]').click()
        assert safe in await page.locator('.brand-probe-result').inner_text()
        await page.locator('[data-probe=broken]').click()
        assert broken in await page.locator('.brand-probe-result').inner_text()
        await page.locator('[data-probe=safe]').click()
        assert safe in await page.locator('.brand-probe-result').inner_text()
    await position(page, '.brand-probe-view')
    await page.locator('[data-brand-theme]').click()
    assert await page.locator('.brand-probe-view').get_attribute('data-dark') == 'true'
    await shot(page, f'boundary-{tag}')
    await position(page, '.brand-rules')
    assert await page.locator('.brand-rules details').count() == 7
    for label in ('BW-C4', 'BW-C5'):
        await page.locator('.brand-rules summary').filter(has_text=label).click()
    assert '0 BW-C4 findings' in await page.locator('.brand-rules').inner_text()
    assert 'A8 is partial' in await page.locator('.brand-record').inner_text()
    await position(page, '.brand-record')
    await shot(page, f'limits-{tag}')
    assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    # Selected specimen and view survive scroll; reload starts a fresh demonstration.
    assert await page.locator('.brand-studio').get_attribute('data-specimen') == 'name'
    await position(page, '.case-next')
    await page.locator('.case-next .case-back').click()
    await page.wait_for_url(URL + '/')
    await idle(page)
    assert abs(await page.evaluate('scrollY') - origin) < 3
    assert await page.locator('[data-open-case=brandwall]').evaluate('e=>e===document.activeElement')
    await page.locator('[data-open-case=brandwall]').click()
    await page.wait_for_url('**/work/brandwall')
    await idle(page)
    await position(page, '.case-next')
    await page.locator('[data-case-target=crosscheck]').click()
    await page.wait_for_url('**/work/crosscheck')
    await idle(page)
    await page.go_back()
    await idle(page)
    assert page.url.endswith('/work/brandwall')
    await page.go_forward()
    await idle(page)
    assert page.url.endswith('/work/crosscheck')
    await enter(page, '/work/brandwall')
    assert await page.locator('.brand-studio').get_attribute('data-specimen') == 'portrait'
    await page.reload()
    await page.locator('.silent-button').click(timeout=30000)
    await idle(page)
    assert await page.locator('.brand-studio').get_attribute('data-view') == 'before'
    assert not errors and not bad, (errors, bad)
    await context.close()
    print('PASS', tag, flush=True)
    return {'viewport': tag, 'status': 'passed', 'chapter': orbit, 'errors': errors, 'httpFailures': bad}


async def edges(browser):
    results = []
    for mode in ('reduced', 'fallback', 'slow-model', 'interrupt-resize'):
        context = await browser.new_context(viewport={'width':390,'height':844}, reduced_motion='reduce' if mode=='reduced' else 'no-preference')
        if mode == 'fallback':
            await context.route('**/models/ambient.glb', lambda route: route.abort())
        if mode == 'slow-model':
            async def delayed(route):
                await asyncio.sleep(2)
                await route.continue_()
            await context.route('**/models/ambient.glb', delayed)
        page = await context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        await enter(page, '/work/brandwall')
        if mode == 'fallback':
            await page.wait_for_selector('[data-scene=fallback]')
            assert await page.locator('.hotspot-leaders').evaluate('e=>getComputedStyle(e).visibility') == 'hidden'
        await position(page, '.brand-view-controls')
        await page.locator('[data-brand-view=after]').focus()
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(260)
        assert await page.locator('.brand-studio').get_attribute('data-view') == 'after'
        if mode == 'reduced':
            assert await page.locator('.brand-after').evaluate('e=>getComputedStyle(e).transitionDuration') == '0s'
        if mode == 'interrupt-resize':
            await page.set_viewport_size({'width':1440,'height':900})
            await page.wait_for_timeout(400)
            assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
            await page.set_viewport_size({'width':390,'height':844})
            await page.goto(URL + '/')
            await page.locator('.silent-button').click(timeout=30000)
            await idle(page)
            await position(page, '#brandwall')
            await page.locator('[data-open-case=brandwall]').click()
            await page.wait_for_url('**/work/brandwall')
            await idle(page)
            await position(page, '.case-next')
            await page.locator('[data-case-target=crosscheck]').click()
            await page.wait_for_timeout(160)
            await page.go_back()
            await idle(page)
            await page.wait_for_timeout(1800)
            assert page.url == URL + '/'
            assert await page.locator('.curtain').get_attribute('data-state') == 'open'
        await shot(page, mode)
        unexpected = [e for e in errors if not (mode == 'fallback' and e == 'Could not load /models/ambient.glb: Failed to fetch')]
        assert not unexpected, unexpected
        await context.close()
        results.append({'edge': mode, 'status': 'passed'})
    return results


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', default=os.environ.get('OBSERVATORY_PHONES','390x844,360x740,430x932,768x1024,1440x900,1920x1080'))
    parser.add_argument('--no-edges', action='store_true')
    args = parser.parse_args()
    report = {'status': 'running', 'fingerprint': fingerprint()[0], 'results': [], 'edges': []}
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=GPU)
            for size in args.sizes.split(','):
                report['results'].append(await viewport(browser, *map(int,size.split('x'))))
            if not args.no_edges:
                report['edges'] = await edges(browser)
            await browser.close()
        report['status'] = 'passed'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = repr(error)
        raise
    finally:
        report['finishedAt'] = datetime.now(timezone.utc).isoformat()
        (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    asyncio.run(main())
