"""Phase 1 gate evidence: checklist screenshots + video per engine at 390x844, plus a throttled load.

Default target is the local production preview; set OBSERVATORY_URL to test the public tunnel.
Emulated phones only: no physical-device fps, speaker, or carrier-network claim.
"""
import asyncio
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/first-light/gate-evidence'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767')
W, H = 390, 844
AUDIO_PROBE = '''window.__audioContexts=[]; const Native=window.AudioContext;
  window.AudioContext=class extends Native { constructor(...args) {super(...args); window.__audioContexts.push(this);} };'''
ITEMS = {
    'preview': 'Preview link opens (HTTP 200, scene ready)',
    'gate': 'Entry gate + calibrating loader + Enter without sound',
    'canvas': 'One persistent Canvas',
    'hero': 'Hero: open dome, sky + planet, DRAFT positioning line',
    'sound': 'Ambient sound + header toggle',
    'scroll': 'Smooth Lenis scroll + minimal header + progress readout',
    'clean': 'No page errors, no responses >= 400',
}
# Headless Chromium defaults to CPU WebGL (SwiftShader), which slows input + video to ~1 fps;
# ANGLE over EGL uses the machine GPU instead.
CHROMIUM_GPU = ['--use-angle=gl-egl', '--ignore-gpu-blocklist', '--enable-gpu']
# Lighthouse mobile throttling profile (slow 4G): 150 ms RTT, 1.6 Mbps down, 750 kbps up.
SLOW_4G = {'offline': False, 'latency': 150, 'downloadThroughput': 1.6e6 / 8, 'uploadThroughput': 0.75e6 / 8}


class Run:
    def __init__(self, engine, page, folder):
        self.engine, self.page, self.dir = engine, page, folder
        self.checks, self.shots = [], []

    async def shot(self, name):
        path = self.dir / f'{len(self.shots) + 1:02d}-{name}.png'
        await self.page.screenshot(path=str(path))
        self.shots.append(path.name)
        return path.name

    def check(self, item, ok, detail, shot=None):
        passed = None if ok is None else bool(ok)
        self.checks.append({'item': item, 'pass': passed, 'detail': detail, 'screenshot': shot})
        print(f"  {'N/A' if passed is None else 'PASS' if passed else 'FAIL'} {item}: {detail}", flush=True)

    async def step(self, item, coro):
        # One failed step is recorded, not fatal, so the report shows every checklist item.
        try:
            await coro
        except Exception as error:
            self.check(item, False, f'{type(error).__name__}: {str(error).splitlines()[0]}')


def to_mp4(folder, name):
    raw = folder / 'raw'
    webm = next(raw.glob('*.webm'), None)
    if webm:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(webm), '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(folder / name)], check=True)
    shutil.rmtree(raw, ignore_errors=True)


def contact_sheet(folder):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-pattern_type', 'glob', '-i', str(folder / '[0-9]*.png'),
                    '-vf', 'scale=390:-1,pad=iw+12:ih+12:6:6:0x0A0F1E,tile=5x2', '-frames:v', '1',
                    str(folder / 'contact-sheet.png')], check=True)


async def new_context(browser, engine, folder, **extra):
    opts = dict(viewport={'width': W, 'height': H}, device_scale_factor=2,
                record_video_dir=str(folder / 'raw'), record_video_size={'width': W, 'height': H}, **extra)
    if engine != 'firefox':
        opts.update(is_mobile=True, has_touch=True)
    return await browser.new_context(**opts)


async def flow(p, engine):
    folder = OUT / engine
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    print(f'{engine} {W}x{H}', flush=True)
    browser = await getattr(p, engine).launch(headless=True, args=CHROMIUM_GPU if engine == 'chromium' else [])
    context = await new_context(browser, engine, folder)
    page = await context.new_page()
    r = Run(engine, page, folder)
    errors, bad = [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
    page.on('response', lambda response: bad.append({'url': response.url, 'status': response.status}) if response.status >= 400 else None)
    await page.add_init_script(AUDIO_PROBE)

    started = time.monotonic()
    response = await page.goto(URL, wait_until='domcontentloaded', timeout=60000)
    loader = await page.locator('.entry-gate').inner_text()
    loader_shot = await r.shot('loader')
    await page.wait_for_function("['ready','fallback'].includes(document.querySelector('.observatory')?.dataset.scene)", timeout=90000)
    await page.wait_for_function("!document.querySelector('.enter-button').disabled", timeout=90000)
    ready_s = round(time.monotonic() - started, 2)
    scene = await page.locator('.observatory').get_attribute('data-scene')
    gate_shot = await r.shot('gate-ready')
    r.check('preview', response and response.status == 200 and scene == 'ready',
            f'HTTP {response.status if response else None}, scene={scene}, Enter enabled after {ready_s}s', gate_shot)

    enter = page.get_by_role('button', name='Enter the Observatory', exact=True)
    box = await enter.bounding_box()
    silent_visible = await page.get_by_role('button', name='Enter without sound').is_visible()
    audio_before = await page.evaluate('window.__audioContexts.length')
    r.check('gate', 'calibrat' in loader.lower() and box['y'] + box['height'] <= H and silent_visible and audio_before == 0,
            f'loader text {loader.split(chr(10))[0:4]}, Enter bottom y={round(box["y"] + box["height"])}, '
            f'silent button visible={silent_visible}, audio contexts before gesture={audio_before}', loader_shot)

    await page.get_by_role('button', name='Enter without sound').click()
    await page.wait_for_selector('.entry-gate[hidden]', state='attached')
    await page.wait_for_timeout(1800)
    hero_shot = await r.shot('hero')
    heading = await page.locator('#hero-heading').inner_text()
    draft = await page.get_by_text('DRAFT COPY', exact=True).is_visible()
    overflow = await page.evaluate('document.documentElement.scrollWidth > innerWidth')
    r.check('hero', scene == 'ready' and 'I test.' in heading and draft and not overflow,
            f'heading={heading!r}, DRAFT label={draft}, horizontal overflow={overflow}, silent entry audio contexts='
            f"{await page.evaluate('window.__audioContexts.length')}", hero_shot)

    async def sound():
        await page.get_by_role('button', name='Turn sound on', exact=True).click()
        try:
            await page.wait_for_function("document.querySelector('.sound-toggle').getAttribute('aria-pressed') === 'true'", timeout=10000)
        except Exception:
            # Separate "this browser has no audio device" from "the site failed": resume a bare
            # AudioContext from a real click in the same page.
            await page.evaluate('''() => { const b = document.createElement('button'); b.id = '__audio-probe';
              b.style.cssText = 'position:fixed;left:0;top:0;z-index:99999'; b.textContent = 'probe';
              b.onclick = async () => { const a = new AudioContext();
                try { await a.resume(); window.__deviceProbe = a.state; } catch (e) { window.__deviceProbe = String(e); } };
              document.body.append(b); }''')
            await page.click('#__audio-probe')
            await page.wait_for_timeout(4500)
            device = await page.evaluate("document.getElementById('__audio-probe').remove(), window.__deviceProbe")
            label = await page.locator('.sound-toggle').get_attribute('aria-label')
            shot = await r.shot('sound-unavailable')
            r.check('sound', False if device == 'running' else None,
                    f'toggle stayed off, label={label!r}; bare AudioContext resume in this browser: {device}', shot)
            return
        await page.wait_for_timeout(600)
        state = await page.evaluate('window.__audioContexts[0]?.state')
        on_shot = await r.shot('sound-on')
        await page.get_by_role('button', name='Turn sound off', exact=True).click()
        await page.wait_for_function("localStorage.getItem('rayin-observatory:sound') === 'off'", timeout=10000)
        r.check('sound', state == 'running', f'AudioContext state after toggle={state}; mute saved to localStorage', on_shot)
    await r.step('sound', sound())

    async def dialogs():
        await page.get_by_role('button', name='Menu', exact=False).click()
        await page.wait_for_timeout(400)
        await r.shot('menu')
        await page.locator('#navigation').get_by_role('button', name='Contact').click()
        await page.wait_for_timeout(400)
        await r.shot('contact')
        await page.locator('.contact-dialog').get_by_role('button', name='Close').click()
        await page.wait_for_timeout(300)
    await r.step('scroll', dialogs())

    async def scroll():
        # Small increments so the video shows the smoothing. Chromium uses real touch swipes
        # (emulated DPR 2 halves wheel deltas); mobile WebKit has no wheel or touch-move input.
        readouts = []
        cdp = await context.new_cdp_session(page) if engine == 'chromium' else None
        for i in range(24):
            if cdp:
                if i % 4 == 0:
                    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 195, 'y': 640}]})
                    for y in range(610, 450, -30):
                        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 195, 'y': y}]})
                        await page.wait_for_timeout(16)
                    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
            elif engine == 'webkit':
                await page.evaluate('window.scrollBy(0, 50)')
            else:
                await page.mouse.wheel(0, 50)
            await page.wait_for_timeout(110)
            if i == 9:
                await page.wait_for_timeout(500)
                readouts.append(await page.locator('.progress-readout output').inner_text())
                await r.shot('scroll-mid')
        await page.wait_for_timeout(1800)
        readouts.append(await page.locator('.progress-readout output').inner_text())
        end_shot = await r.shot('scroll-end')
        lenis = await page.evaluate("document.documentElement.classList.contains('lenis')")
        header = await page.get_by_role('button', name='Rayin Observatory, return to the dome').is_visible()
        await page.get_by_role('button', name='Rayin Observatory, return to the dome').click()
        await page.wait_for_timeout(1600)
        top = await page.evaluate('scrollY')
        await r.shot('returned')
        r.check('scroll', lenis and header and int(readouts[-1].rstrip('%')) >= 95 and top < 2,
                f'readout {readouts}, lenis={lenis}, header visible={header}, scrollY after return={top}', end_shot)
    await r.step('scroll', scroll())

    canvases = await page.locator('canvas').count()
    r.check('canvas', canvases == 1, f'canvas elements after entry, dialogs, scroll and return={canvases}')
    r.check('clean', not errors and not bad, f'page/console errors={errors[:3]}, bad responses={bad[:3]}')
    await context.close()
    await browser.close()
    to_mp4(folder, f'{engine}-walkthrough.mp4')
    contact_sheet(folder)
    return {'engine': engine, 'readySeconds': ready_s, 'checks': r.checks, 'screenshots': r.shots,
            'video': f'{engine}/{engine}-walkthrough.mp4', 'contactSheet': f'{engine}/contact-sheet.png'}


async def slow_load(p):
    folder = OUT / 'chromium-slow-4g'
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    print('chromium slow-4g load', flush=True)
    browser = await p.chromium.launch(headless=True, args=CHROMIUM_GPU)
    context = await new_context(browser, 'chromium', folder)
    page = await context.new_page()
    cdp = await context.new_cdp_session(page)
    await cdp.send('Network.enable')
    await cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
    await cdp.send('Network.emulateNetworkConditions', SLOW_4G)
    started = time.monotonic()
    await page.goto(URL, wait_until='domcontentloaded', timeout=90000)
    first_paint_s = round(time.monotonic() - started, 2)
    await page.wait_for_timeout(1500)
    await page.screenshot(path=str(folder / '01-loading.png'))
    await page.wait_for_function("!document.querySelector('.enter-button').disabled", timeout=120000)
    ready_s = round(time.monotonic() - started, 2)
    scene = await page.locator('.observatory').get_attribute('data-scene')
    await page.screenshot(path=str(folder / '02-ready.png'))
    await page.get_by_role('button', name='Enter without sound').click()
    await page.wait_for_timeout(1800)
    await page.screenshot(path=str(folder / '03-hero.png'))
    transferred = await page.evaluate("performance.getEntriesByType('resource').reduce((s, e) => s + (e.transferSize || 0), 0) + (performance.getEntriesByType('navigation')[0]?.transferSize || 0)")
    await context.close()
    await browser.close()
    to_mp4(folder, 'chromium-slow-4g-load.mp4')
    print(f'  DOM {first_paint_s}s, Enter enabled {ready_s}s, scene={scene}, {transferred} bytes', flush=True)
    return {'profile': 'Lighthouse slow 4G: 150 ms RTT, 1.6 Mbps down (emulated)', 'domContentLoadedSeconds': first_paint_s,
            'enterEnabledSeconds': ready_s, 'scene': scene, 'transferBytes': transferred,
            'video': 'chromium-slow-4g/chromium-slow-4g-load.mp4'}


async def run():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'status': 'running', 'startedAt': datetime.now(timezone.utc).isoformat(), 'url': URL,
              'viewport': [W, H], 'scope': 'Phase 1 checklist, emulated phones; no physical-device fps/speaker/carrier claim',
              'items': ITEMS, 'engines': []}
    async with async_playwright() as p:
        for engine in ('chromium', 'webkit', 'firefox'):
            try:
                report['engines'].append(await flow(p, engine))
            except Exception as error:
                report['engines'].append({'engine': engine, 'error': f'{type(error).__name__}: {str(error).splitlines()[0]}'})
                print(f'  ERROR {engine}: {error}', flush=True)
        try:
            report['slow4g'] = await slow_load(p)
        except Exception as error:
            report['slow4g'] = {'error': f'{type(error).__name__}: {str(error).splitlines()[0]}'}
    # pass=None means the environment cannot exercise the item (e.g. no audio device); not a failure.
    verdict = {}
    for item in ITEMS:
        verdict[item] = {}
        for e in report['engines']:
            results = [c['pass'] for c in e.get('checks', []) if c['item'] == item]
            verdict[item][e['engine']] = ('fail' if 'error' in e or False in results or not results
                                          else 'n/a' if None in results else 'pass')
    passed = all('fail' not in v.values() for v in verdict.values()) and 'error' not in report['slow4g']
    report.update(status='passed' if passed else 'failed', finishedAt=datetime.now(timezone.utc).isoformat(), verdict=verdict)
    (OUT / 'gate-evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(verdict, indent=2))
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if asyncio.run(run()) else 1)
