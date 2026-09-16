"""Focused development evidence for the dome rebuild and reversible scroll choreography.

Run against a production preview with OBSERVATORY_URL. Screenshots and a browser-only
video live under assets/renders/observatory-motion/dev; no physical-device FPS claim.
"""
import asyncio
import io
import json
import os
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from playwright.async_api import async_playwright

URL = os.environ.get('OBSERVATORY_URL', 'http://localhost:8769').rstrip('/')
OUT = Path(__file__).resolve().parents[2] / 'assets/renders/observatory-motion/dev'
GPU = ['--enable-gpu', '--use-gl=angle', '--use-angle=gl-egl', '--ignore-gpu-blocklist']


def difference(a, b):
    first = Image.open(io.BytesIO(a)).convert('RGB')
    second = Image.open(io.BytesIO(b)).convert('RGB')
    return sum(ImageStat.Stat(ImageChops.difference(first, second)).mean) / 3


async def capture(page, name):
    assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), name
    assert await page.locator('.observatory').get_attribute('data-scene') == 'ready', name
    assert await page.locator('canvas').count() == 1, name
    return await page.screenshot(path=str(OUT / f'{name}.png'))


async def scroll(page, y):
    await page.evaluate('(y) => window.scrollTo(0, y)', y)
    await page.wait_for_function('(y) => Math.abs(scrollY - y) < 3', arg=y)
    await page.wait_for_timeout(1700)


async def run():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'url': URL, 'status': 'running', 'checks': [], 'errors': []}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=GPU)
            context = await browser.new_context(viewport={'width': 1440, 'height': 900},
                record_video_dir=str(OUT / 'video'), record_video_size={'width': 1440, 'height': 900})
            page = await context.new_page()
            page.on('pageerror', lambda error: report['errors'].append(str(error)))
            page.on('console', lambda msg: report['errors'].append(msg.text) if msg.type == 'error' else None)
            page.on('response', lambda response: report['errors'].append(f'{response.status}: {response.url}') if response.status >= 400 else None)
            await page.goto(URL)
            await page.locator('.silent-button').click(timeout=30000)
            await page.wait_for_selector('.entry-gate[hidden]', state='attached')
            await page.wait_for_timeout(3500)
            first = await capture(page, 'desktop-hero')
            await page.wait_for_timeout(1500)
            moving = await capture(page, 'desktop-idle')
            delta = difference(first, moving)
            assert delta > .08, ('idle model did not move', delta)
            report['checks'].append({'name': 'animated hero', 'meanPixelChange': delta})
            # Real wheel input exercises the Lenis -> ScrollTrigger -> R3F path.
            for _ in range(5):
                await page.mouse.wheel(0, 125)
                await page.wait_for_timeout(180)
            await page.wait_for_timeout(2000)
            assert await page.evaluate('scrollY') > 450
            await capture(page, 'desktop-scroll')
            for slug in ['crosscheck', 'surgeline', 'driftwatch', 'brandwall']:
                y = await page.locator('#' + slug).evaluate('(e) => e.offsetTop + 150')
                await scroll(page, y)
                await capture(page, 'desktop-' + slug)
                assert await page.locator('.observatory').get_attribute('data-chapter') == slug
            report['checks'].append({'name': 'wheel scroll and four planetary chapters', 'pass': True})
            await scroll(page, 0)
            await capture(page, 'desktop-return')
            assert await page.locator('.observatory').get_attribute('data-chapter') == 'dome'
            for width, height in [(1920, 1080), (1024, 768), (390, 844), (360, 740)]:
                await page.set_viewport_size({'width': width, 'height': height})
                await page.wait_for_timeout(1200)
                await capture(page, f'hero-{width}x{height}')
                report['checks'].append({'name': f'resize {width}x{height}', 'pass': True})
            await page.set_viewport_size({'width': 1440, 'height': 900})
            await page.emulate_media(reduced_motion='reduce')
            await page.wait_for_function("document.querySelector('.observatory').dataset.motion === 'reduced'")
            await page.wait_for_timeout(5500)
            first = await capture(page, 'reduced-motion')
            await page.wait_for_timeout(1200)
            second = await page.screenshot()
            delta = difference(first, second)
            assert delta < .08, ('reduced-motion sky or dome still moves', delta)
            report['checks'].append({'name': 'live reduced-motion toggle freezes decoration', 'meanPixelChange': delta})
            y = await page.locator('#crosscheck').evaluate('(e) => e.offsetTop + 150')
            await scroll(page, y)
            await page.locator('[data-open-case="crosscheck"]').click()
            await page.wait_for_url('**/work/crosscheck')
            await page.wait_for_selector('.observatory[data-flight="idle"]')
            await capture(page, 'case-file')
            report['checks'].append({'name': 'case navigation after motion toggle', 'pass': True})
            assert not report['errors'], report['errors']
            await context.close()
            await page.video.save_as(str(OUT / 'walkthrough.webm'))
            await page.video.delete()
            await browser.close()
            report['status'] = 'passed'
    finally:
        (OUT / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    asyncio.run(run())
