"""Revision evidence (sky + instrument motion, 2026-09-15): 390x844 walkthrough MP4, one PNG per
revision item, labeled contact sheet and evidence.json.

Default target is the local production preview; set OBSERVATORY_URL for a public tunnel.
Chromium mobile emulation only: no physical-device fps claim.
"""
import asyncio
import io
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/revision-sky-motion/evidence'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767')
W, H = 390, 844
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']
STAGE = (0, 520, 780, 1290)  # instrument area at device scale 2
ITEMS = {
    'sky': 'Sky: pitch-black zenith easing into the blue horizon, twinkling stars, faint nebula',
    'saturn': 'Saturn: banded globe spins, ring dust orbits, two moons circle it',
    'crosscheck': 'CrossCheck: lenses light in turn, then all three together in green',
    'surgeline': 'SurgeLine: every dish moves on its own rhythm and fires its own pulse ring',
    'driftwatch': 'DriftWatch: paper feeds, live trace, red spike when drift is detected',
    'duewatch': 'DueWatch: planets ride their rings at Kepler speeds (outer slower), rings precess',
    'brandwall': 'BrandWall: detector off = wave pattern, tap = detector on = two particle bands',
    'clean': 'One Canvas, no page errors, no responses >= 400, frame rate',
}


def font(size):
    for path in ['/usr/share/fonts/TTF/DejaVuSans.ttf', '/usr/share/fonts/dejavu/DejaVuSans.ttf']:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def strip(frames, path):
    crops = [Image.open(io.BytesIO(f)).convert('RGB').crop(STAGE) for f in frames]
    w, h = crops[0].size
    sheet = Image.new('RGB', (w * len(crops) // 2, h // 2), 'black')
    for i, crop in enumerate(crops):
        sheet.paste(crop.resize((w // 2, h // 2)), (i * w // 2, 0))
    sheet.save(path)
    diffs = [sum(ImageStat.Stat(ImageChops.difference(crops[i], crops[i + 1])).mean) for i in range(len(crops) - 1)]
    return round(min(diffs), 2)


async def settle(page):
    last = None
    for _ in range(60):
        await page.wait_for_timeout(200)
        current = await page.evaluate('Math.round(scrollY)')
        if current == last:
            return
        last = current


async def wheel_to(page, target, step=120, pause=60):
    for _ in range(600):
        if await page.evaluate('scrollY') >= target - 2:
            break
        await page.mouse.wheel(0, step)
        await page.wait_for_timeout(pause)
    await settle(page)


async def frames(page, count, gap):
    shots = []
    for _ in range(count):
        shots.append(await page.screenshot())
        await page.wait_for_timeout(gap)
    return shots


async def run():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    checks = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True,
                                            has_touch=True, record_video_dir=str(OUT / 'raw'), record_video_size={'width': W, 'height': H})
        page = await context.new_page()
        errors, bad = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.on('response', lambda r: bad.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
        await page.goto(URL, wait_until='networkidle')
        await page.wait_for_function("!document.querySelector('.enter-button').disabled", timeout=60000)
        await page.wait_for_timeout(1200)
        await page.screenshot(path=str(OUT / '01-gate.png'))
        await page.get_by_role('button', name='Enter without sound', exact=True).click()
        await page.wait_for_timeout(2500)
        await page.screenshot(path=str(OUT / '02-sky-hero.png'))
        top_px = Image.open(OUT / '02-sky-hero.png').convert('RGB')
        zenith, horizon = top_px.getpixel((20, 30)), top_px.getpixel((20, 1500))
        checks['sky'] = {'pass': sum(zenith) < sum(horizon), 'detail': f'zenith px {zenith} darker than horizon px {horizon}', 'screenshot': '02-sky-hero.png'}
        saturn = await frames(page, 4, 1500)
        crops = [Image.open(io.BytesIO(f)).convert('RGB').crop((470, 680, 780, 940)) for f in saturn]
        sheet = Image.new('RGB', (310 * 4, 260))
        for i, crop in enumerate(crops):
            sheet.paste(crop, (i * 310, 0))
        sheet.save(OUT / '03-saturn.png')
        motion = min(sum(ImageStat.Stat(ImageChops.difference(crops[i], crops[i + 1])).mean) for i in range(3))
        checks['saturn'] = {'pass': motion > .5, 'detail': f'min frame difference {motion:.2f} over 1.5 s steps', 'screenshot': '03-saturn.png'}
        fps = await page.evaluate('''() => new Promise(r => { let n = 0; const s = performance.now();
          const f = t => { n++; if (t - s < 3000) requestAnimationFrame(f); else r(n / ((t - s) / 1000)); }; requestAnimationFrame(f); })''')
        plan = [('crosscheck', 6, 1100), ('surgeline', 5, 700), ('driftwatch', 6, 900), ('duewatch', 5, 1200)]
        for n, (slug, count, gap) in enumerate(plan, start=4):
            top = await page.locator('#' + slug).evaluate('e => e.getBoundingClientRect().top + scrollY')
            await wheel_to(page, top + 2)
            await page.wait_for_timeout(800)
            await page.screenshot(path=str(OUT / f'{n:02d}-{slug}.png'))
            diff = strip(await frames(page, count, gap), OUT / f'{n:02d}-{slug}-motion.png')
            checks[slug] = {'pass': diff > .1, 'detail': f'min difference between consecutive frames {diff}', 'screenshot': f'{n:02d}-{slug}-motion.png'}
            await wheel_to(page, top + 700)
            await page.wait_for_timeout(1200)
        top = await page.locator('#brandwall').evaluate('e => e.getBoundingClientRect().top + scrollY')
        await wheel_to(page, top + 900)
        await page.wait_for_function("document.getElementById('observer-readout').dataset.observed === 'false'", timeout=15000)
        await page.wait_for_timeout(4000)
        await page.screenshot(path=str(OUT / '08-brandwall-wave.png'))
        await page.mouse.click(W / 2, H * .55)
        await page.wait_for_timeout(300)
        observed = await page.evaluate("document.getElementById('observer-readout').dataset.observed")
        await page.wait_for_timeout(3200)
        await page.screenshot(path=str(OUT / '09-brandwall-observed.png'))
        a = Image.open(OUT / '08-brandwall-wave.png').convert('RGB').crop((440, 560, 780, 960))
        b = Image.open(OUT / '09-brandwall-observed.png').convert('RGB').crop((440, 560, 780, 960))
        pair = Image.new('RGB', (680, 400))
        pair.paste(a, (0, 0))
        pair.paste(b, (340, 0))
        pair.save(OUT / '10-brandwall-compare.png')
        checks['brandwall'] = {'pass': observed == 'true', 'detail': f'tap switched detector to observed={observed}; left wave, right particle', 'screenshot': '10-brandwall-compare.png'}
        await page.wait_for_timeout(3000)
        canvases = await page.locator('canvas').count()
        checks['clean'] = {'pass': canvases == 1 and not errors and not bad, 'detail': f'canvas={canvases}, errors={len(errors)}, bad={len(bad)}, fps≈{fps:.0f} (headless emulation)', 'screenshot': None}
        video = await page.video.path()
        await context.close()
        await browser.close()
    mp4 = OUT / 'revision-walkthrough.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', str(mp4)], check=True)
    shutil.rmtree(OUT / 'raw')
    labeled = [('01-gate.png', 'Gate'), ('02-sky-hero.png', 'Sky + Saturn'), ('04-crosscheck.png', 'CrossCheck'), ('05-surgeline.png', 'SurgeLine'),
               ('06-driftwatch.png', 'DriftWatch'), ('07-duewatch.png', 'DueWatch'), ('08-brandwall-wave.png', 'BrandWall · wave'), ('09-brandwall-observed.png', 'BrandWall · observed')]
    tiles = []
    for name, label in labeled:
        tile = Image.open(OUT / name).convert('RGB').resize((390, 844))
        draw = ImageDraw.Draw(tile)
        draw.rectangle((0, 0, 390, 34), fill=(11, 16, 32))
        draw.text((10, 7), label, fill=(242, 165, 65), font=font(18))
        tiles.append(tile)
    sheet = Image.new('RGB', (390 * 4, 844 * 2), 'black')
    for i, tile in enumerate(tiles):
        sheet.paste(tile, ((i % 4) * 390, (i // 4) * 844))
    sheet.save(OUT / 'contact-sheet.jpg', quality=88)
    report = {'status': 'passed' if all(c['pass'] for c in checks.values()) else 'failed', 'finishedAt': datetime.now(timezone.utc).isoformat(),
              'url': URL, 'viewport': [W, H], 'scope': 'Chromium mobile emulation; no physical-device claim',
              'items': {k: {'label': ITEMS[k], **checks.get(k, {'pass': False, 'detail': 'not reached'})} for k in ITEMS}, 'video': mp4.name}
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    for key, check in report['items'].items():
        print(f"{'PASS' if check['pass'] else 'FAIL'} {key}: {check['detail']}")
    print(report['status'])


if __name__ == '__main__':
    asyncio.run(run())
