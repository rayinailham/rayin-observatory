"""Phase 2 gate walkthrough: 390x844 video + key frames of the CrossCheck chapter for owner review."""
import asyncio
import os
import shutil
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/crosscheck/walkthrough'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767')
SIZE = {'width': 390, 'height': 844}
# Default headless Chromium uses SwiftShader (~1 fps); same GPU flags as verify_mobile.py.
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']


async def scroll(page, pixels, step=40, pause=100):
    # Wheel deltas are partly absorbed by Lenis at low capture fps, so wheel toward a target
    # position rather than counting steps.
    target = await page.evaluate('scrollY') + pixels
    for _ in range(400):
        if await page.evaluate('scrollY') >= target - 2:
            break
        await page.mouse.wheel(0, step)
        await page.wait_for_timeout(pause)
    # Lenis lerps per frame and video capture lowers fps, so wait for the scroll to settle
    # instead of a fixed delay; otherwise frames show a mid-transition state.
    last = None
    for _ in range(60):
        await page.wait_for_timeout(250)
        current = await page.evaluate('Math.round(scrollY)')
        if current == last:
            return
        last = current


async def run():
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        context = await browser.new_context(viewport=SIZE, device_scale_factor=2, is_mobile=True, has_touch=True,
                                            record_video_dir=str(OUT), record_video_size=SIZE)
        page = await context.new_page()
        await page.goto(URL, wait_until='networkidle')
        await page.wait_for_function("!document.querySelector('.enter-button').disabled", timeout=60000)
        await page.screenshot(path=str(OUT / '01-gate.png'))
        await page.get_by_role('button', name='Enter without sound').click()
        await page.wait_for_timeout(2200)
        await page.screenshot(path=str(OUT / '02-hero.png'))
        await scroll(page, await page.evaluate("document.querySelector('#crosscheck').offsetTop"))
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT / '03-chapter.png'))
        await scroll(page, SIZE['height'] * .85)
        await page.wait_for_timeout(1200)
        await page.screenshot(path=str(OUT / '04-orbit.png'))
        await page.get_by_role('button', name='Open case file', exact=True).click()
        await page.wait_for_timeout(1200)
        await page.screenshot(path=str(OUT / '05-case-file.png'))
        await page.get_by_role('button', name='Return to the instrument').click()
        await page.wait_for_timeout(600)
        await scroll(page, SIZE['height'] * 1.2)
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT / '06-orbit-end.png'))
        video = page.video
        await context.close()
        webm = Path(await video.path())
        await browser.close()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(webm), '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', str(OUT / 'crosscheck-walkthrough.mp4')], check=True)
    webm.unlink()
    print('\n'.join(sorted(item.name for item in OUT.iterdir())))


asyncio.run(run())
