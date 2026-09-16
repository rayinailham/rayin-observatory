"""Q42 Development frame-rate gate: catch a PLAN §11 regression before Testing does.

One phone (390x844, DPR 2, touch), sound on as a default visitor, 4x CPU throttle (Phase 7 swipe method):
homepage chapter of --slug → lens/camera flight into its case → swipe the whole case down to Next → Return.
A segment passes at ≥ 45 fps with ≤ 10% of frames slower than 45 fps. `--baseline URL` measures a second
preview the same way right after (e.g. a build of HEAD in a scratch copy) so a drop can be attributed.
Rig limits: headless Chromium, host GPU not throttled — a regression alarm, not a phone fps claim.

Run from web/scripts with the production preview on :8767:
  timeout 600 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python perf_quick.py --slug crosscheck [--baseline http://127.0.0.1:8781]
Writes assets/renders/perf-quick/<slug>.json; exit 1 when a segment fails.
"""
import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/perf-quick'
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']
W, H = 390, 844
SLOW_MS = 1000 / 45
FRAMES = "(() => { window.__frames = []; const f = t => { window.__frames.push(t); requestAnimationFrame(f); }; requestAnimationFrame(f); })();"


def stats(ts):
    d = sorted(b - a for a, b in zip(ts, ts[1:]))
    if not d:
        return {'fps': 0, 'frames': 0, 'slowPct': 100}
    return {'fps': round(1000 * len(d) / sum(d), 1), 'p95Ms': round(d[int(len(d) * .95)], 1), 'worstMs': round(d[-1], 1),
            'slowPct': round(100 * sum(x > SLOW_MS for x in d) / len(d), 1), 'frames': len(d)}


async def swipe(cdp, dist):
    y0 = H * .76 if dist > 0 else H * .24
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': W / 2, 'y': y0}]})
    for i in range(1, 15):
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': W / 2, 'y': y0 - dist * i / 14}]})
        await asyncio.sleep(.016)
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})


async def swipe_until(page, cdp, target):
    for _ in range(120):
        y = await page.evaluate('scrollY')
        if abs(y - target) < 50 or (target > y and await page.evaluate('scrollY>=document.documentElement.scrollHeight-innerHeight-2')):
            return
        await swipe(cdp, max(-300, min(300, target - y)))
        await asyncio.sleep(.25)


async def land(page, y):
    for _ in range(12):
        await page.evaluate('(y)=>scrollTo(0,y)', y)
        await page.wait_for_timeout(250)
        if abs(await page.evaluate('scrollY') - min(y, await page.evaluate('document.documentElement.scrollHeight-innerHeight'))) < 3:
            return


async def idle(page):
    await page.wait_for_function("document.querySelector('.observatory').dataset.flight==='idle'", timeout=20000)
    await page.wait_for_timeout(400)


async def measure(browser, url, slug):
    context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True, has_touch=True)
    await context.add_init_script(FRAMES)
    page = await context.new_page()
    cdp = await context.new_cdp_session(page)
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    await page.goto(url)
    await page.locator('.enter-button').click(timeout=90000)
    await idle(page)
    await page.wait_for_timeout(1500)
    segments = {}

    async def segment(name, action):
        n0 = await page.evaluate('__frames.length')
        await action()
        segments[name] = stats(await page.evaluate('(n)=>__frames.slice(n)', n0))

    section = await page.locator(f'#{slug}').evaluate('e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight})')
    await land(page, section['top'] - 100)
    await page.wait_for_timeout(800)
    await segment('chapter scroll', lambda: swipe_until(page, cdp, section['top'] + section['h'] - H))
    await land(page, section['top'] + .45 * (section['h'] - H))
    await page.wait_for_timeout(600)

    async def open_case():
        await page.locator(f'[data-open-case={slug}]').tap()
        await page.wait_for_url(f'**/work/{slug}')
        await idle(page)
    await segment('flight into the case', open_case)
    await page.wait_for_timeout(600)
    await segment('case scroll to Next', lambda: swipe_until(page, cdp, 10 ** 6))

    async def back():
        await land(page, await page.locator('.case-next').evaluate('e=>e.getBoundingClientRect().top+scrollY-100'))
        await page.locator('.case-next .case-back').tap()
        await page.wait_for_url(url.rstrip('/') + '/')
        await idle(page)
    await segment('return flight', back)
    await context.close()
    return {'url': url, 'segments': segments, 'errors': errors,
            'pass': not errors and all(s['fps'] >= 45 and s['slowPct'] <= 10 for s in segments.values())}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--slug', default='crosscheck')
    parser.add_argument('--baseline')
    args = parser.parse_args()
    url = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767').rstrip('/')
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        current = await measure(browser, url, args.slug)
        baseline = await measure(browser, args.baseline.rstrip('/'), args.slug) if args.baseline else None
        await browser.close()
    report = {'status': 'passed' if current['pass'] else 'failed', 'slug': args.slug, 'finishedAt': datetime.now(timezone.utc).isoformat(),
              'rule': '4x CPU, 390x844 DPR 2, sound on: every segment ≥ 45 fps and ≤ 10% frames slower than 45 fps',
              'current': current, 'baseline': baseline}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f'{args.slug}.json').write_text(json.dumps(report, indent=2) + '\n')
    for label, run in (('current', current), ('baseline', baseline)):
        if run:
            print(label, run['url'], '; '.join(f"{k} {v['fps']} fps ({v['slowPct']}% slow)" for k, v in run['segments'].items()))
    print(report['status'])
    return current['pass']


if __name__ == '__main__':
    sys.exit(0 if asyncio.run(main()) else 1)
