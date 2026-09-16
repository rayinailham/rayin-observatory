"""Phase 7 Development checks. Real Web Audio + mobile interactions; no gate/performance claim."""
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/showpiece/dev'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767')
# Q42: OBSERVATORY_PHONES=390x844 narrows an older phase's regression to one phone (run_regressions.py --phone-only).
PHONES = [tuple(map(int, s.split('x'))) for s in os.environ.get('OBSERVATORY_PHONES', '390x844,360x740,430x932').split(',')]
CASES = ['crosscheck', 'surgeline', 'driftwatch', 'duewatch', 'brandwall']
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']
# Instrument the browser's actual audio graph; no app debug globals or fake audio on the main flow.
AUDIO = """(() => {
 const Base = window.AudioContext;
 window.audioProbe = {contexts: [], starts: [], live: 0};
 window.AudioContext = class extends Base {
  constructor(...args) {
   super(...args); window.audioProbe.contexts.push(this);
   const create = this.createOscillator.bind(this);
   this.createOscillator = () => {
    const node = create(), start = node.start.bind(node), disconnect = node.disconnect.bind(node);
    const setFrequency = node.frequency.setValueAtTime.bind(node.frequency);
    let scheduledFrequency;
    node.frequency.setValueAtTime = (value, time) => { scheduledFrequency = value; return setFrequency(value, time); };
    let live = false;
    node.start = (...args) => {
     live = true; window.audioProbe.live++;
     window.audioProbe.starts.push({frequency: scheduledFrequency ?? node.frequency.value, time: this.currentTime});
     return start(...args);
    };
    node.disconnect = (...args) => { if (live) { live = false; window.audioProbe.live--; } return disconnect(...args); };
    return node;
   };
   const gain = this.createGain.bind(this);
   this.createGain = () => {
    const node = gain(), connect = node.connect.bind(node);
    node.connect = target => {
     if (target === this.destination) {
      const analyser = this.createAnalyser(); analyser.fftSize = 2048;
      connect(analyser); window.audioProbe.analyser = analyser;
     }
     return connect(target);
    };
    return node;
   };
  }
 };
 window.audioProbe.rms = () => {
  const a = window.audioProbe.analyser; if (!a) return 0;
  const data = new Float32Array(a.fftSize); a.getFloatTimeDomainData(data);
  return Math.sqrt(data.reduce((sum, value) => sum + value * value, 0) / data.length);
 };
 window.loaderSamples = [];
 const observer = new MutationObserver(() => {
  const bar = document.querySelector('.calibration-track');
  if (bar) window.loaderSamples.push(Number(bar.getAttribute('aria-valuenow')));
 });
 observer.observe(document, {subtree: true, childList: true, attributes: true, attributeFilter: ['aria-valuenow']});
})();"""

async def idle(page):
    await expect(page.locator('.observatory')).to_have_attribute('data-flight', 'idle', timeout=20000)
    await page.wait_for_function("Number(getComputedStyle(document.querySelector('.page-content')).opacity) > .99")

async def enter(page, silent=True):
    await expect(page.locator('.enter-button')).to_be_enabled(timeout=30000)
    await page.locator('.silent-button' if silent else '.enter-button').click()
    await expect(page.locator('.entry-gate')).to_be_hidden(timeout=10000)
    await idle(page)

async def position(page, selector):
    await page.locator(selector).evaluate("el => window.scrollTo(0, el.getBoundingClientRect().top + scrollY)")
    await page.wait_for_timeout(250)

async def starts(page):
    return await page.evaluate('audioProbe.starts.length')

async def shot(page, name):
    await page.screenshot(path=str(OUT / f'{name}.png'))

async def phone(browser, width, height):
    context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=2, is_mobile=True, has_touch=True)
    await context.add_init_script(AUDIO)
    page = await context.new_page()
    errors, bad = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda e: errors.append(e.text) if e.type == 'error' else None)
    page.on('response', lambda r: bad.append(f'{r.status} {r.url}') if r.status >= 400 else None)
    tag = f'{width}x{height}'
    await page.goto(URL)
    await expect(page.locator('.enter-button')).to_be_enabled(timeout=30000)
    samples = await page.evaluate('loaderSamples')
    assert samples and samples[-1] == 100 and samples == sorted(samples), samples
    assert await page.evaluate('audioProbe.contexts.length') == 0
    await shot(page, f'gate-{tag}')
    await enter(page)
    assert await page.evaluate('audioProbe.contexts.length') == 0, 'Silent entry constructed audio'
    await page.evaluate('window.originalCanvas = document.querySelector("canvas")')
    await page.locator('.sound-toggle').click()
    await expect(page.locator('.sound-toggle')).to_have_attribute('aria-pressed', 'true')
    await page.wait_for_timeout(1100)
    audible = await page.evaluate('audioProbe.rms()')
    assert audible > .001, audible
    await page.locator('.menu-toggle').click()
    await page.wait_for_timeout(280)
    await shot(page, f'menu-{tag}')
    await page.get_by_role('navigation', name='Main navigation', exact=True).get_by_role('button', name='Work').click()
    await page.wait_for_function("Math.abs(document.getElementById('crosscheck').getBoundingClientRect().top) < 5", timeout=20000)
    # The menu scroll's Lenis tail still moves a few px after the chapter is in place; sample once settled.
    await page.wait_for_function("new Promise(r=>{const y=scrollY;setTimeout(()=>r(Math.abs(scrollY-y)<1),400)})", timeout=10000)
    origin = await page.evaluate('scrollY')
    before = await starts(page)
    await page.locator('[data-open-case=crosscheck]').click()
    await expect(page.locator('.observatory')).to_have_attribute('data-flight', 'moving')
    await shot(page, f'flight-{tag}')
    await page.wait_for_url('**/work/crosscheck')
    await idle(page)
    assert await starts(page) >= before + 2
    pitches = []
    for i, slug in enumerate(CASES):
        await expect(page.locator('main')).to_have_attribute('data-case', slug)
        await position(page, '#case-instrument')
        await page.wait_for_timeout(200)
        before = await starts(page)
        if i == 0:
            box = await page.locator('.hotspot-0').bounding_box()
            await page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
            await page.mouse.down()
            await page.wait_for_function('parseFloat(getComputedStyle(document.querySelector(".hotspot-0")).scale) < .99')
            await page.mouse.up()
        else:
            await page.locator('.hotspot-0').click()
        await expect(page.locator('.hotspot-0')).to_have_attribute('aria-expanded', 'true')
        await expect(page.locator('.hotspot-leaders line').nth(0)).to_have_attribute('data-active', 'true')
        await page.wait_for_timeout(240)
        await shot(page, f'{slug}-inspection-{tag}')
        assert await starts(page) == before + 1, (slug, before, await starts(page))
        pitches.append(await page.evaluate('audioProbe.starts.at(-1).frequency'))
        # Rapid card replacement must settle on the last selection; finished voices disconnect.
        await page.locator('.hotspot-1').click()
        await page.locator('.hotspot-2').click()
        await expect(page.locator('.hotspot-2')).to_have_attribute('aria-expanded', 'true')
        await page.get_by_role('button', name='Close component card').click()
        await expect(page.locator('.component-card')).to_have_attribute('data-selected', 'false')
        await page.wait_for_timeout(900)
        assert await page.evaluate('audioProbe.live') == 4
        assert await page.evaluate('document.querySelectorAll("canvas").length === 1 && document.querySelector("canvas") === originalCanvas')
        assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        if i < 4:
            await position(page, '.case-next')
            before = await starts(page)
            await page.locator('[data-case-target]').click()
            await page.wait_for_url(f'**/work/{CASES[i+1]}')
            await idle(page)
            assert await starts(page) >= before + 4, 'Missing chain sweep'
    assert len(set(pitches)) == 5, pitches
    # BrandWall detector responds only on the instrument area, with its own click.
    before = await starts(page)
    await page.locator('.case-inspection').click(position={'x': 180, 'y': 380})
    assert await starts(page) == before + 1
    await page.wait_for_timeout(200)
    await page.locator('.sound-toggle').click()
    await expect(page.locator('.sound-toggle')).to_have_attribute('aria-pressed', 'false')
    before = await starts(page)
    await page.locator('.hotspot-0').click()
    assert await starts(page) == before, 'Muted click created a voice'
    await page.wait_for_timeout(1500)
    muted = await page.evaluate('audioProbe.rms()')
    assert muted < .00005, muted
    await page.locator('.case-next [data-home-target]').click()
    await page.wait_for_url(URL + '/')
    await idle(page)
    assert await starts(page) == before, 'Muted return created a sweep'
    await page.wait_for_timeout(200)
    await shot(page, f'return-{tag}')
    await page.reload()
    await enter(page, silent=False)
    assert await page.evaluate('audioProbe.contexts.length') == 0, 'Remembered mute ignored'
    assert not errors and not bad, {'errors': errors, 'http': bad}
    await context.close()
    return {'viewport': tag, 'loaderSamples': samples, 'pitches': pitches, 'audibleRms': audible, 'mutedRms': muted, 'errors': errors, 'httpErrors': bad, 'originScroll': origin, 'status': 'passed'}

async def edges(browser):
    context = await browser.new_context(viewport={'width': 390, 'height': 844})
    await context.add_init_script(AUDIO)
    page = await context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    await page.goto(URL)
    await enter(page, silent=False)
    await expect(page.locator('.sound-toggle')).to_have_attribute('aria-pressed', 'true')
    await page.wait_for_timeout(1000)
    assert await page.evaluate('audioProbe.contexts.length') == 1
    assert await starts(page) == 6, 'Welcome sweep missing'
    # Simulate the browser visibility property/event, while keeping a real running AudioContext.
    await page.evaluate("Object.defineProperty(document, 'hidden', {configurable: true, get: () => true}); document.dispatchEvent(new Event('visibilitychange'))")
    await page.wait_for_timeout(1500)
    assert await page.evaluate('audioProbe.rms()') < .00005
    before = await starts(page)
    await page.locator('.menu-toggle').click()
    assert await starts(page) == before
    await page.evaluate("delete document.hidden; document.dispatchEvent(new Event('visibilitychange'))")
    await page.wait_for_timeout(1000)
    assert await page.evaluate('audioProbe.rms()') > .001
    await page.get_by_role('navigation', name='Main navigation', exact=True).get_by_role('button', name='Work').click()
    await page.wait_for_function("Math.abs(document.getElementById('crosscheck').getBoundingClientRect().top) < 5", timeout=20000)
    # The menu scroll's Lenis tail still moves a few px after the chapter is in place; sample once settled.
    await page.wait_for_function("new Promise(r=>{const y=scrollY;setTimeout(()=>r(Math.abs(scrollY-y)<1),400)})", timeout=10000)
    origin = await page.evaluate('scrollY')
    await page.locator('[data-open-case=crosscheck]').click()
    await page.wait_for_url('**/work/crosscheck')
    await idle(page)
    await page.locator('.case-brief [data-home-target]').click()
    await page.wait_for_url(URL + '/')
    await idle(page)
    assert abs(await page.evaluate('scrollY') - origin) < 5
    await page.wait_for_function('document.querySelector("[data-open-case=crosscheck]") === document.activeElement')
    await page.go_back()
    await idle(page)
    await position(page, '.case-next')
    await page.locator('[data-case-target]').click()
    await page.wait_for_timeout(120)
    await page.go_back()
    await page.wait_for_url(URL + '/')
    await idle(page)
    await page.wait_for_timeout(1800)
    assert page.url == URL + '/', 'Stale departure hijacked browser Back'
    assert not errors, errors
    await context.close()

    # Stalled GLB (Saturn is the one model still fetched): visible incomplete loader, then
    # the existing still-view escape after 15s.
    context = await browser.new_context(viewport={'width': 390, 'height': 844})
    page = await context.new_page()
    release = asyncio.Event()
    async def stall(route):
        await release.wait()
        await route.abort()
    await page.route('**/models/ambient.glb', stall)
    await page.goto(URL, wait_until='domcontentloaded')
    await expect(page.locator('.enter-button')).to_be_disabled()
    await page.wait_for_timeout(1500)
    await shot(page, 'loader-pending-390x844')
    assert int(await page.locator('.calibration-track').get_attribute('aria-valuenow')) < 100
    await page.get_by_role('button', name='Continue with a still view').click(timeout=25000)
    await expect(page.locator('.enter-button')).to_be_enabled()
    await expect(page.locator('.entry-gate')).to_have_attribute('data-fallback', 'true')
    await page.wait_for_timeout(450)  # Capture the completed dial/button transition, not its first frame.
    await shot(page, 'loader-fallback-390x844')
    release.set()
    await enter(page)
    await expect(page.locator('.fallback-notice')).to_be_visible()
    await context.close()

    context = await browser.new_context(viewport={'width': 390, 'height': 844})
    await context.add_init_script("window.AudioContext = class { constructor() { throw new Error('Audio unavailable test'); } }")
    page = await context.new_page()
    await page.goto(URL)
    await enter(page, silent=False)
    await expect(page.locator('.audio-notice')).to_be_visible()
    await expect(page.locator('.sound-toggle')).to_have_attribute('aria-pressed', 'false')
    await shot(page, 'audio-unavailable-390x844')
    await context.close()
    return {'status': 'passed', 'checks': ['default audio and welcome', 'hidden tab silence and resume', 'return scroll and focus', 'Back interrupts departure', 'stalled loader escape', 'audio unavailable entry']}

async def run():
    OUT.mkdir(parents=True, exist_ok=True)
    result = {'status': 'running', 'timestamp': datetime.now(timezone.utc).isoformat(), 'phones': []}
    path = OUT / 'verification.json'
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=GPU)
            for width, height in PHONES:
                result['phones'].append(await phone(browser, width, height))
                print(f'PASS {width}x{height}', flush=True)
                path.write_text(json.dumps(result, indent=2))
            result['edges'] = await edges(browser)
            await browser.close()
        result['status'] = 'passed'
    except Exception as e:
        result.update(status='failed', error=str(e))
        raise
    finally:
        path.write_text(json.dumps(result, indent=2))
    print('PASS showpiece development', flush=True)

if __name__ == '__main__':
    asyncio.run(run())
