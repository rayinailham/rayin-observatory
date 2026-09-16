"""Instrument detail evidence: every instrument in its chapter and its case file.

Run against a preview with OBSERVATORY_URL. Pass a stage name (`before`/`after`) as the
first argument; screenshots land in assets/renders/instrument-detail/<stage>.
"""
import asyncio
import io
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from playwright.async_api import async_playwright

URL = os.environ.get('OBSERVATORY_URL', 'http://localhost:8767').rstrip('/')
STAGE = (sys.argv[1] if len(sys.argv) > 1 else 'after')
OUT = Path(__file__).resolve().parents[2] / 'assets/renders/instrument-detail' / STAGE
GPU = ['--enable-gpu', '--use-gl=angle', '--use-angle=gl-egl', '--ignore-gpu-blocklist']
SLUGS = ['crosscheck', 'surgeline', 'driftwatch', 'duewatch', 'brandwall']


def difference(a, b):
    first = Image.open(io.BytesIO(a)).convert('RGB')
    second = Image.open(io.BytesIO(b)).convert('RGB')
    return sum(ImageStat.Stat(ImageChops.difference(first, second)).mean) / 3


async def moved(page, first, samples=6, gap=700):
    """Largest change against the opening frame over a window.

    A single fixed-interval diff is phase-sensitive: CrossCheck's channels idle quietly
    between ignitions, and the outer orrery track creeps. Sampling across the window
    measures whether anything moves at all, not what it happened to be doing.
    """
    peak = 0.0
    for _ in range(samples):
        await page.wait_for_timeout(gap)
        peak = max(peak, difference(first, await page.screenshot()))
    return peak


async def capture(page, name):
    assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), name
    assert await page.locator('.observatory').get_attribute('data-scene') == 'ready', name
    assert await page.locator('.entry-gate').get_attribute('hidden') is not None, name
    return await page.screenshot(path=str(OUT / f'{name}.png'))


async def scroll(page, y):
    await page.evaluate('(y) => window.scrollTo(0, y)', y)
    await page.wait_for_function('(y) => Math.abs(scrollY - y) < 3', arg=y)
    await page.wait_for_timeout(1700)


async def enter(page, url):
    await page.goto(url)
    await page.locator('.silent-button').click(timeout=45000)
    await page.wait_for_selector('.entry-gate[hidden]', state='attached')
    await page.wait_for_timeout(3500)


async def chapters(page, report, label):
    for slug in SLUGS:
        y = await page.locator('#' + slug).evaluate('(e) => e.offsetTop + 150')
        await scroll(page, y)
        assert await page.locator('.observatory').get_attribute('data-chapter') == slug, slug
        first = await capture(page, f'{label}-chapter-{slug}')
        delta = await moved(page, first)
        report['checks'].append({'name': f'{label} chapter {slug}', 'peakIdleMeanPixelChange': round(delta, 4)})
        assert delta > .02, (f'{label} {slug} idle motion stalled', delta)


async def cases(page, report, label):
    """Open every case file the way a visitor does, then return through history."""
    for slug in SLUGS:
        y = await page.locator('#' + slug).evaluate('(e) => e.offsetTop + 150')
        await scroll(page, y)
        await page.locator(f'[data-open-case="{slug}"]').click()
        await page.wait_for_url(f'**/work/{slug}')
        await page.wait_for_selector('.observatory[data-flight="idle"]')
        # The instrument only enters frame at the inspection section; capture it there.
        y = await page.locator('#case-instrument').evaluate('(e) => e.offsetTop')
        await scroll(page, y)
        await page.wait_for_timeout(1200)
        first = await capture(page, f'{label}-case-{slug}')
        delta = await moved(page, first)
        report['checks'].append({'name': f'{label} case {slug}', 'peakIdleMeanPixelChange': round(delta, 4)})
        assert delta > .0015, (f'{label} case {slug} idle motion stalled', delta)
        box = await page.locator('.case-inspection').bounding_box()
        # Blank the endpoints first: a leader line that no longer resolves its anchor keeps
        # its last value, which would otherwise pass the bounds check on stale data.
        await page.evaluate("""() => document.querySelectorAll('[data-hotspot-line]')
            .forEach(l => { l.setAttribute('x2', '-9999'); l.setAttribute('y2', '-9999'); })""")
        await page.wait_for_timeout(500)
        lines = await page.evaluate("""() => [...document.querySelectorAll('[data-hotspot-line]')]
            .map(l => ({ id: l.dataset.hotspotLine, x: +l.getAttribute('x2'), y: +l.getAttribute('y2') }))""")
        assert len(lines) == 3, (slug, lines)
        for item in lines:
            assert 0 <= item['x'] <= box['width'] and 0 <= item['y'] <= box['height'], (slug, item, box)
        assert len({(round(i['x']), round(i['y'])) for i in lines}) == 3, (slug, lines)
        report['checks'].append({'name': f'{label} leader endpoints {slug}', 'lines': lines})
        await page.go_back()
        await page.wait_for_url(lambda url: '/work/' not in url)
        await page.wait_for_selector('.observatory[data-flight="idle"]')
        await page.wait_for_timeout(900)
    report['checks'].append({'name': f'{label} history return from every case', 'pass': True})


async def run():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'url': URL, 'stage': STAGE, 'status': 'running', 'checks': [], 'errors': []}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=GPU)
            context = await browser.new_context(viewport={'width': 1440, 'height': 900},
                record_video_dir=str(OUT / 'video'), record_video_size={'width': 1440, 'height': 900})
            page = await context.new_page()
            page.on('pageerror', lambda error: report['errors'].append(str(error)))
            page.on('console', lambda msg: report['errors'].append(msg.text) if msg.type == 'error' else None)
            page.on('response', lambda r: report['errors'].append(f'{r.status}: {r.url}') if r.status >= 400 else None)
            await enter(page, URL)
            await chapters(page, report, 'desktop')
            await cases(page, report, 'desktop')
            # Mobile: the same five chapters at the narrowest supported width.
            await page.set_viewport_size({'width': 390, 'height': 844})
            await enter(page, URL)
            await chapters(page, report, 'mobile')
            await cases(page, report, 'mobile')
            # Reduced motion: models must hold perfectly still.
            await page.set_viewport_size({'width': 1440, 'height': 900})
            await page.emulate_media(reduced_motion='reduce')
            await enter(page, URL)
            await page.wait_for_function("document.querySelector('.observatory').dataset.motion === 'reduced'")
            y = await page.locator('#surgeline').evaluate('(e) => e.offsetTop + 150')
            await scroll(page, y)
            await page.wait_for_timeout(2500)
            first = await capture(page, 'reduced-motion-surgeline')
            await page.wait_for_timeout(1600)
            delta = difference(first, await page.screenshot())
            assert delta < .08, ('reduced motion still animates', delta)
            report['checks'].append({'name': 'reduced motion holds still', 'meanPixelChange': round(delta, 4)})
            assert not report['errors'], report['errors']
            await context.close()
            await page.video.save_as(str(OUT / 'walkthrough.webm'))
            await page.video.delete()
            await browser.close()
            report['status'] = 'passed'
    except Exception as error:  # noqa: BLE001 - the report must record why a stage failed.
        report['status'] = 'failed'
        report['failure'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        (OUT / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    asyncio.run(run())
