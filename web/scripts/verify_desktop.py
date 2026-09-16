"""Phase 6 Development checks. Mobile first, then laptop/monitor; no owner gate."""
import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/desktop/dev'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767').rstrip('/')
SLUGS = ['crosscheck', 'surgeline', 'driftwatch', 'duewatch', 'brandwall']
GPU = ['--enable-gpu', '--use-gl=angle', '--use-angle=gl-egl', '--ignore-gpu-blocklist']


async def position(page, selector, offset=0):
    # A header-nav Lenis scroll can still be easing its last pixels after the < 3 px arrival check;
    # a native scrollTo issued then is overwritten by Lenis. Re-issue until it lands, then assert.
    y = await page.locator(selector).evaluate('(el) => el.getBoundingClientRect().top + scrollY') + offset
    for _ in range(12):
        await page.evaluate('(y) => window.scrollTo(0, y)', y)
        await page.wait_for_timeout(300)
        if await page.evaluate('(y) => Math.abs(scrollY - Math.min(y, document.documentElement.scrollHeight - innerHeight)) < 3', y):
            break
    await page.wait_for_function('(y) => Math.abs(scrollY - Math.min(y, document.documentElement.scrollHeight - innerHeight)) < 3', arg=y)
    await page.wait_for_timeout(550)


async def entered(page):
    await page.get_by_role('button', name='Enter without sound', exact=True).click(timeout=30000)
    await page.wait_for_selector('.entry-gate[hidden]', state='attached')
    await page.wait_for_timeout(900)
    assert await page.locator('.observatory').get_attribute('data-scene') == 'ready'
    await page.evaluate('window.__phase6Canvas = document.querySelector("canvas")')


async def idle(page, slug=None):
    await page.wait_for_url(f'**/work/{slug}' if slug else URL + '/')
    await page.wait_for_selector('.observatory[data-flight="idle"]')
    await page.wait_for_timeout(500)
    assert await page.evaluate('document.querySelector("canvas") === window.__phase6Canvas')
    assert await page.locator('canvas').count() == 1


async def capture(page, name):
    overflow = await page.evaluate('document.documentElement.scrollWidth - innerWidth')
    assert overflow <= 1, (name, 'overflow', overflow)
    await page.screenshot(path=str(OUT / f'{name}.png'))


async def check_case(page, slug, tag, desktop):
    await capture(page, f'{slug}-brief-{tag}')
    await position(page, '#case-instrument')
    for i in range(3):
        button = page.locator('.instrument-hotspot').nth(i)
        await button.click()
        await page.wait_for_function("(i) => getComputedStyle(document.querySelector('.hotspot-' + i)).backgroundColor === 'rgb(242, 165, 65)'", arg=i)
        assert await button.get_attribute('aria-expanded') == 'true'
        card = await page.locator('.component-card').bounding_box()
        marker = await button.bounding_box()
        size = page.viewport_size
        assert card and marker
        assert card['x'] >= 0 and card['x'] + card['width'] <= size['width'] + 1
        assert card['y'] >= 80 and card['y'] + card['height'] < size['height'] - 45
        assert marker['width'] >= 44 and marker['height'] >= 44
        if desktop:
            assert card['x'] + card['width'] < marker['x'], (slug, 'card overlaps inspection pane')
        await capture(page, f'{slug}-hotspot-{i+1}-{tag}')
    # Endpoints are real projected coordinates, contained in the inspection viewport.
    endpoints = await page.locator('.hotspot-leaders').evaluate('''svg => [...svg.querySelectorAll('line')].map(line => ({
      x: Number(line.getAttribute('x2')), y: Number(line.getAttribute('y2')),
      width: svg.clientWidth, height: svg.clientHeight
    }))''')
    assert len(endpoints) == 3
    assert all(0 < p['x'] < p['width'] and 0 < p['y'] < p['height'] for p in endpoints), endpoints
    await position(page, '[aria-labelledby="flow-heading"]', 32)
    await capture(page, f'{slug}-flow-{tag}')
    if desktop and slug != 'crosscheck':  # CrossCheck: pinned inspection field (Phase 7A), see verify_crosscheck_room.py
        flow = await page.locator('.signal-flow li').evaluate_all('(els) => els.map(el => el.getBoundingClientRect().top)')
        assert max(flow) - min(flow) < 2, (slug, 'flow is not horizontal', flow)
    await position(page, '.case-readings', -130)
    await page.wait_for_timeout(1400)
    counts = await page.locator('[data-count]').evaluate_all('(els) => els.map(el => [el.dataset.count, el.textContent.replaceAll(",", "")])')
    # Mobile reveals readings in sequence; desktop shows both columns.
    if desktop:
        assert all(expected == actual for expected, actual in counts), counts
    await capture(page, f'{slug}-readings-{tag}')
    await position(page, '[aria-labelledby="demo-heading"]', -80)
    await capture(page, f'{slug}-demo-{tag}')
    assert await page.locator('video').get_attribute('preload') == 'none'
    return {'slug': slug, 'hotspots': 3, 'projectedEndpoints': endpoints, 'counts': counts}


async def viewport(browser, width, height):
    tag = f'{width}x{height}'
    desktop = width >= 1024
    context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=1)
    page = await context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.on('response', lambda response: errors.append(f'HTTP {response.status} {response.url}') if response.status >= 400 else None)
    await page.goto(URL)
    await page.get_by_role('button', name='Enter without sound', exact=True).wait_for()
    await capture(page, f'gate-{tag}')
    await entered(page)
    await capture(page, f'hero-{tag}')
    assert await page.locator('.desktop-navigation').is_visible() == desktop
    if desktop:
        assert await page.locator('.scene-layer').evaluate('el => el.clientWidth === innerWidth')
        await page.get_by_role('navigation', name='Desktop navigation').get_by_role('button', name='Work', exact=True).click()
        await page.wait_for_function('Math.abs(scrollY - document.getElementById("crosscheck").offsetTop) < 3')
    for slug in SLUGS:
        await position(page, f'#{slug}', 240)
        await capture(page, f'chapter-{slug}-{tag}')
        if desktop:
            copy = await page.locator(f'#{slug} .instrument-copy').bounding_box()
            reading = await page.locator(f'#{slug} .instrument-reading').bounding_box()
            assert copy and reading and copy['y'] + copy['height'] + 20 < reading['y'], (tag, slug, copy, reading)
    for section in ['skills', 'about', 'contact']:
        if desktop and section != 'skills':
            await page.get_by_role('navigation', name='Desktop navigation').get_by_role('button', name=section.title(), exact=True).click()
            await page.wait_for_function('(id) => Math.abs(scrollY - Math.min(document.getElementById(id).getBoundingClientRect().top + scrollY, document.documentElement.scrollHeight - innerHeight)) < 3', arg=section)
        else:
            await position(page, f'#{section}')
        if section == 'skills':
            await page.locator('.deck-arrow').last.click()
            await page.wait_for_timeout(700)
        await capture(page, f'{section}-{tag}')
    await position(page, '#crosscheck', 240)
    await page.locator('[data-open-case="crosscheck"]').click()
    await idle(page, 'crosscheck')
    results = []
    # Mobile detailed regression is also covered by verify_case/verify:mobile.
    for slug in (SLUGS if desktop else SLUGS[:1]):
        results.append(await check_case(page, slug, tag, desktop))
        await position(page, '.case-next', -100)
        await page.locator('[data-case-target]').click()
        next_slug = SLUGS[(SLUGS.index(slug) + 1) % len(SLUGS)]
        await idle(page, next_slug)
    if desktop:
        assert page.url.endswith('/work/crosscheck'), page.url
        await page.go_back()
        await idle(page, 'brandwall')
        await page.go_forward()
        await idle(page, 'crosscheck')
        # Header navigation from a case must restore the homepage anchor and Canvas.
        await page.get_by_role('navigation', name='Desktop navigation').get_by_role('button', name='About', exact=True).click()
        await idle(page)
        await page.wait_for_function('Math.abs(document.getElementById("about").getBoundingClientRect().top) < 3')
        await capture(page, f'case-to-about-{tag}')
    else:
        await page.locator('.case-brief .case-back').click()
        await idle(page)
    assert not errors, errors
    await context.close()
    print(f'{tag}: passed', flush=True)
    return {'viewport': [width, height], 'status': 'passed', 'cases': results, 'errors': errors}


async def fallback(browser):
    context = await browser.new_context(viewport={'width': 1440, 'height': 900})
    await context.route('**/models/ambient.glb', lambda route: route.abort())
    page = await context.new_page()
    await page.goto(URL + '/work/brandwall')
    await page.get_by_role('button', name='Enter without sound', exact=True).click(timeout=30000)
    await page.wait_for_selector('.entry-gate[hidden]', state='attached')
    await page.wait_for_selector('.observatory[data-scene="fallback"]')
    await position(page, '#case-instrument')
    await page.locator('.instrument-hotspot').first.click()
    await page.wait_for_function("getComputedStyle(document.querySelector('.hotspot-0')).backgroundColor === 'rgb(242, 165, 65)'")
    assert await page.locator('.case-instrument-still').is_visible()
    await capture(page, 'fallback-brandwall-1440x900')
    await page.locator('.case-brief .case-back').click()
    await page.wait_for_url(URL + '/')
    await page.wait_for_selector('.observatory[data-flight="idle"]')
    await capture(page, 'fallback-home-1440x900')
    await context.close()
    return 'passed'


async def refresh_hotspots(browser, width, height):
    context = await browser.new_context(viewport={'width': width, 'height': height})
    page = await context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    await page.goto(URL + '/work/crosscheck')
    await entered(page)
    slugs = SLUGS if width >= 1024 else SLUGS[:1]
    for slug in slugs:
        await position(page, '#case-instrument')
        for i in range(3):
            await page.locator('.instrument-hotspot').nth(i).click()
            await page.wait_for_function("(i) => getComputedStyle(document.querySelector('.hotspot-' + i)).backgroundColor === 'rgb(242, 165, 65)'", arg=i)
            await capture(page, f'{slug}-hotspot-{i+1}-{width}x{height}')
        if slug != slugs[-1]:
            await position(page, '.case-next', -100)
            await page.locator('[data-case-target]').click()
            await idle(page, SLUGS[SLUGS.index(slug) + 1])
    assert not errors, errors
    await context.close()
    return {'status': 'passed', 'viewport': [width, height], 'hotspots': len(slugs) * 3, 'errors': errors}


async def breakpoints(browser):
    context = await browser.new_context(viewport={'width': 390, 'height': 844})
    page = await context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    await page.goto(URL + '/work/crosscheck')
    await entered(page)
    sizes = [(768, 900), (1024, 768), (1440, 900), (390, 844)]
    for width, height in sizes:
        await page.set_viewport_size({'width': width, 'height': height})
        await page.wait_for_timeout(700)
        await position(page, '#case-instrument')
        assert await page.evaluate('document.querySelector("canvas") === window.__phase6Canvas')
        pane = await page.locator('.case-inspection').bounding_box()
        canvas = await page.locator('canvas').bounding_box()
        assert pane and canvas
        points = await page.locator('.hotspot-leaders line').evaluate_all('(els) => els.map(el => Number(el.getAttribute("x2")))')
        assert all(0 < x < pane['width'] for x in points), (width, points, pane)
        if width == 768:
            assert abs(canvas['x'] - (width - 430) / 2) < 1
        if width >= 1024:
            assert canvas['width'] == width
        marker = page.locator('.instrument-hotspot').first
        if await marker.get_attribute('aria-expanded') != 'true':
            await marker.click()
        await page.wait_for_function("getComputedStyle(document.querySelector('.hotspot-0')).backgroundColor === 'rgb(242, 165, 65)'")
        await capture(page, f'resize-inspection-{width}x{height}')
    assert not errors, errors
    await context.close()
    return {'status': 'passed', 'viewports': sizes, 'errors': errors}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--breakpoints-only', action='store_true')
    parser.add_argument('--hotspots-only', action='store_true')
    parser.add_argument('--sizes', default='390x844,1366x768,1440x900,1920x1080')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    result = {'startedAt': datetime.now(timezone.utc).isoformat(), 'status': 'running', 'viewports': []}
    report = OUT / ('breakpoint-verification.json' if args.breakpoints_only else 'hotspot-verification.json' if args.hotspots_only else 'verification.json')
    report.write_text(json.dumps(result, indent=2))
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(args=GPU)
            result['browser'] = browser.version
            for size in ([] if args.breakpoints_only else args.sizes.split(',')):
                w, h = map(int, size.split('x'))
                result['viewports'].append(await (refresh_hotspots(browser, w, h) if args.hotspots_only else viewport(browser, w, h)))
                report.write_text(json.dumps(result, indent=2))
            if args.breakpoints_only:
                result['breakpoints'] = await breakpoints(browser)
            elif not args.hotspots_only:
                result['fallback'] = await fallback(browser)
            await browser.close()
        result['status'] = 'passed'
    except Exception as exc:
        result['status'] = 'failed'
        result['error'] = repr(exc)
        raise
    finally:
        result['finishedAt'] = datetime.now(timezone.utc).isoformat()
        report.write_text(json.dumps(result, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
