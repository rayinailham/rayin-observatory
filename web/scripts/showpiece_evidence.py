"""Phase 7 Testing evidence: sound design, final loader, micro-interactions, transitions and the
PLAN §11 mobile performance targets measured under emulation.

Records a 390x844 MP4 of the main flow WITH the site's real audio (the page's own Web Audio output is
tapped into a MediaRecorder, then muxed): slow-4G gate loading -> Enter with sound -> hero -> chapters
-> menu -> fly-in -> five-case chain with one hotspot tone per instrument -> BrandWall observe -> Return
-> mute -> reload with remembered mute. Separately measures, without recording: gate time on slow 4G +
4x CPU, frame rate under 4x CPU (6x as stress, informative), 3D asset sizes and the canvas pixel-ratio
cap. Reuses verify_showpiece (edges + 360x740 / 430x932 phones) and reads regression suite results.

Target: local production preview (OBSERVATORY_URL default http://127.0.0.1:8767).
Chromium GPU emulation on a laptop (host GPU is not throttled); no physical-phone claim (Phase 8).
Run from web/scripts/. Exit 1 when any item fails.
"""
import asyncio
import base64
import json
import platform
import shutil
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402
from playwright.async_api import async_playwright, expect  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_showpiece as vs  # noqa: E402
from case_files_evidence import CASES, flight, overflow, tile, top  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/showpiece/evidence'
MODELS = ROOT / 'web/public/models'
URL = vs.URL.rstrip('/')
W, H = 390, 844
GPU = vs.GPU
AMBER, OK = 'rgb(242, 165, 65)', 'rgb(91, 228, 155)'
# Chrome DevTools "Slow 4G" preset (latency 150 ms x 3.75, throughput x 0.9) — stricter than the
# 150 ms profile used in the Phase 1 evidence, which is measured too for comparison.
SLOW_4G = {'offline': False, 'latency': 562.5, 'downloadThroughput': 1.6e6 * .9 / 8, 'uploadThroughput': 750e3 * .9 / 8}
LIGHT_4G = {'offline': False, 'latency': 150, 'downloadThroughput': 1.6e6 / 8, 'uploadThroughput': 750e3 / 8}
NO_THROTTLE = {'offline': False, 'latency': 0, 'downloadThroughput': -1, 'uploadThroughput': -1}
CPU = 4
STABLE_MS = 1000 / 45  # PLAN §11: minimum stable 45 fps
REGRESSIONS = {
    'verify_audio.mjs (9 lifecycle groups)': 'assets/renders/showpiece/dev/audio-verification.json',
    'verify_showpiece.py (3 phones + edges)': 'assets/renders/showpiece/dev/verification.json',
    'verify:mobile (homepage, 3 phones)': 'assets/renders/full-observatory/dev/verification.json',
    'verify_case.py (CrossCheck case, 3 phones)': 'assets/renders/case-crosscheck/dev/verification.json',
    'verify_cases.py (five cases + chain, 3 phones)': 'assets/renders/case-files/dev/verification.json',
    'verify_desktop.py (phone + 3 desktops)': 'assets/renders/desktop/dev/verification.json',
}

ITEMS = {
    'loader': 'Final loader: dial + beacon fill without going backwards, green "Instruments calibrated" when ready; a stalled model shows the incomplete dial, then an amber still-view path',
    'soundEntry': 'Enter the Observatory starts the hum + a welcome sweep (real audio signal); Enter without sound creates no audio at all',
    'instrumentClicks': 'Instrument clicks: each of the five instruments has its own tone on a hotspot tap; menu/close click; every short voice ends and disconnects',
    'transitionSounds': 'Camera sweeps: fly-in, Next instrument (two-part sweep) and Return each play a sweep',
    'soundControl': 'Sound control: mute is silent at once and taps make no sound; choice remembered after reload; hidden tab goes silent and resumes; audio-unavailable notice',
    'microInteractions': 'Micro-interactions: buttons press (scale), active marker + leader + amber card border, menu panel slides in, hover effects only for mouse pointers',
    'transitions': 'Transitions: fly-in to a case (text fades, scroll locked), Next sweep through all five cases, Return lands on the chapter with focus, Back during a departure cancels cleanly',
    'perfGate': 'PLAN §11: gate with Enter shown in < 2.5 s on slow 4G + 4x CPU throttle',
    'perfAssets': 'PLAN §11: 3D assets on the homepage ≤ 8 MB total and each .glb ≤ 1.5 MB, Draco compressed',
    'perfFps': 'PLAN §11: under 4x CPU throttle, hero / five-chapter scroll / fly-in / inspection / Next sweep / Return hold ≥ 45 fps (target ~60)',
    'dprCap': 'PLAN §11: 3D pixel ratio capped on phones (canvas ≤ 1.5x at device pixel ratio 2 and 3)',
    'phones': '360×740 and 430×932 pass the same showpiece checks as 390×844; regression suites pass',
    'clean': 'One persistent Canvas, zero page errors, zero responses ≥ 400, no horizontal overflow',
}
FINDINGS = {}

# The site's own audio output → MediaRecorder, wrapped around verify_showpiece.AUDIO (analyser probe).
TAP = """(() => {
 const Base = window.AudioContext;
 window.__rec = {chunks: [], start: null};
 window.AudioContext = class extends Base {
  constructor(...args) {
   super(...args); const ctx = this, gain = this.createGain.bind(this);
   this.createGain = () => {
    const node = gain(), connect = node.connect.bind(node);
    node.connect = target => {
     if (target === ctx.destination && !window.__rec.recorder) {
      const dest = ctx.createMediaStreamDestination(); connect(dest);
      const recorder = new MediaRecorder(dest.stream, {mimeType: 'audio/webm;codecs=opus'});
      recorder.ondataavailable = e => e.data.size && window.__rec.chunks.push(e.data);
      recorder.start(250); window.__rec.recorder = recorder; window.__rec.start = Date.now();
     }
     return connect(target);
    };
    return node;
   };
  }
 };
})();"""
STOP_REC = """() => new Promise(resolve => {
 const r = window.__rec.recorder; if (!r) return resolve(null);
 r.onstop = () => { const reader = new FileReader(); reader.onload = () => resolve({start: window.__rec.start, data: reader.result.split(',')[1]});
  reader.readAsDataURL(new Blob(window.__rec.chunks, {type: 'audio/webm'})); };
 r.stop();
})"""
TIMING = """(() => {
 window.__t = {};
 new PerformanceObserver(l => l.getEntries().forEach(e => window.__t[e.name] = e.startTime)).observe({type: 'paint', buffered: true});
 new MutationObserver(() => {
  const b = document.querySelector('.enter-button');
  if (b && !window.__t.gateDom) window.__t.gateDom = performance.now();
  if (b && !b.disabled && !window.__t.enter) window.__t.enter = performance.now();
 }).observe(document, {subtree: true, childList: true, attributes: true});
})();"""
FRAMES = "(() => { window.__frames = []; const f = t => { window.__frames.push(t); requestAnimationFrame(f); }; requestAnimationFrame(f); })();"


def scale(value):
    """Computed CSS `scale` ('none' when unset) as a number."""
    try:
        return float(str(value).split()[0])
    except ValueError:
        return 1.0


def frame_stats(ts):
    d = sorted(b - a for a, b in zip(ts, ts[1:]))
    if not d:
        return {'fps': 0, 'frames': 0}
    return {'fps': round(1000 * len(d) / sum(d), 1), 'medianMs': round(d[len(d) // 2], 1), 'p95Ms': round(d[int(len(d) * .95)], 1),
            'worstMs': round(d[-1], 1), 'framesOver22ms': round(100 * sum(x > STABLE_MS for x in d) / len(d), 1), 'frames': len(d)}


def glb_info(path):
    data = path.read_bytes()
    length = struct.unpack_from('<I', data, 12)[0]
    gltf = json.loads(data[20:20 + length])
    return {'file': path.name, 'bytes': len(data), 'draco': 'KHR_draco_mesh_compression' in gltf.get('extensionsRequired', []),
            'images': len(gltf.get('images', []))}


async def swipe(cdp, dist=420, steps=14):
    """Real touch swipe (Chromium mobile emulation) — native scroll as on a phone."""
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 195, 'y': 640}]})
    for i in range(1, steps + 1):
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 195, 'y': 640 - dist * i / steps}]})
        await asyncio.sleep(.016)
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})


async def swipe_to(page, cdp, target, pause=.25):
    while await page.evaluate('scrollY') < target - 60:
        await swipe(cdp)
        await asyncio.sleep(pause)


async def settle_to(page, selector, offset=0):
    """Pin an exact position. Lenis overwrites a native scrollTo while it is still easing
    (after header/menu nav or syncTouch swipes), so re-issue until it lands."""
    for _ in range(12):
        y = await top(page, selector) + offset
        await page.evaluate('(y)=>scrollTo(0,y)', y)
        await page.wait_for_timeout(300)
        if abs(await page.evaluate('scrollY') - y) < 3:
            break


def phone_context(browser, **extra):
    return browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True, has_touch=True, **extra)


async def main_flow(browser, checks, meta):
    context = await phone_context(browser, record_video_dir=str(OUT / 'raw'), record_video_size={'width': W, 'height': H})
    await context.add_init_script(vs.AUDIO)
    await context.add_init_script(TAP)
    page = await context.new_page()
    video_start = time.time()
    cdp = await context.new_cdp_session(page)
    errors, bad, overflows = [], [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('response', lambda r: bad.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
    starts = lambda: page.evaluate('audioProbe.starts.length')  # noqa: E731

    async def snap(name):
        overflows.append(await overflow(page))
        await page.screenshot(path=str(OUT / name))

    # 1. Gate on slow 4G so the dial fill is visible on video (network only; CPU unthrottled here).
    await cdp.send('Network.enable')
    await cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
    await cdp.send('Network.emulateNetworkConditions', SLOW_4G)
    await page.goto(URL, wait_until='commit', timeout=90000)
    await page.wait_for_selector('.calibration-track', timeout=60000)
    await page.wait_for_function("+document.querySelector('.calibration-track').getAttribute('aria-valuenow') >= 30", timeout=90000)
    await snap('01a-loader-calibrating.png')
    pending = await page.locator('.calibration-status').inner_text()
    await expect(page.locator('.enter-button')).to_be_enabled(timeout=120000)
    await cdp.send('Network.emulateNetworkConditions', NO_THROTTLE)
    await page.wait_for_timeout(700)  # dial/button transitions settle
    await snap('01b-loader-ready.png')
    samples = await page.evaluate('loaderSamples')
    dial = await page.locator('.calibration-orbit circle').evaluate('e=>getComputedStyle(e).stroke')
    status = await page.locator('.calibration-status').inner_text()
    contexts_before = await page.evaluate('audioProbe.contexts.length')
    meta['loader'] = {'samples': samples, 'dial': dial, 'status': status, 'pending': pending}

    # 2. Enter with sound (default) → hum + welcome sweep.
    await page.locator('.enter-button').click()
    await expect(page.locator('.entry-gate')).to_be_hidden(timeout=10000)
    await vs.idle(page)
    await page.wait_for_timeout(1000)
    rms_on = await page.evaluate('audioProbe.rms()')
    welcome = await starts()
    contexts = await page.evaluate('audioProbe.contexts.length')
    pressed = await page.locator('.sound-toggle').get_attribute('aria-pressed')
    await page.evaluate("""
        window.__canvas = document.querySelector('canvas');
        new MutationObserver(() => window.__flight && window.__flight.push(document.querySelector('.observatory').dataset.flight))
          .observe(document.querySelector('.observatory'), {attributes: true, attributeFilter: ['data-flight']});
    """)
    await snap('02-hero-sound-on.png')
    checks['soundEntry'] = {
        'pass': contexts_before == 0 and contexts == 1 and pressed == 'true' and welcome >= 2 and rms_on > .001,
        'detail': f"no AudioContext before the tap ({contexts_before}); after Enter: 1 context={contexts == 1}, toggle on={pressed}, "
                  f"{welcome} oscillators started (hum + welcome sweep), output RMS {rms_on:.4f}; silent entry → 0 contexts: see phones item (verify_showpiece)",
        'screenshot': '02-hero-sound-on.png',
    }

    # 3. Touch-swipe through the five chapters (video shows native phone scroll).
    for case in CASES:
        slug = case['id']
        await swipe_to(page, cdp, await top(page, f'#{slug}') + 260)
        await page.wait_for_timeout(500)
        await snap(f'03-chapter-{slug}.png')

    # 4. Menu: entrance animation + click tone, then Work.
    before = await starts()
    await page.locator('.menu-toggle').click()
    arrival = await page.evaluate("[...document.querySelectorAll('.navigation-dialog[open] nav, .navigation-dialog[open] .dialog-top')].map(e=>e.getAnimations().map(a=>a.animationName).join()).join('|')")
    await page.wait_for_timeout(320)
    await snap('04-menu.png')
    menu_tone = await starts() - before
    await page.get_by_role('navigation', name='Main navigation', exact=True).get_by_role('button', name='Work').click()
    await page.wait_for_function("Math.abs(document.getElementById('crosscheck').getBoundingClientRect().top) < 5", timeout=20000)
    await settle_to(page, '#crosscheck', 240)
    await page.wait_for_timeout(400)

    # 5. Fly-in to CrossCheck: press scale, sweep, fade, lock, focus.
    box = await page.locator('[data-open-case=crosscheck]').bounding_box()
    await page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
    await page.mouse.down()
    await page.wait_for_timeout(160)
    cta_scale = await page.locator('[data-open-case=crosscheck]').evaluate('e=>getComputedStyle(e).scale')
    before = await starts()
    f = await flight(page, page.mouse.up, f'{URL}/work/crosscheck')
    fly_in = await starts() - before
    for key, suffix in (('start', 'a'), ('mid', 'b'), ('end', 'c')):
        (OUT / f'05{suffix}-flight-{key}.png').write_bytes(f[key])
    focus = await page.evaluate('document.activeElement && document.activeElement.id')
    hops, pitches, cards, drained, presses = [], [], [], [], []
    for i, case in enumerate(CASES):
        slug = case['id']
        await expect(page.locator('main')).to_have_attribute('data-case', slug)
        await settle_to(page, '#case-instrument')
        await page.wait_for_timeout(700)  # previous sweep voices finish
        base = await page.evaluate('audioProbe.live')
        marker = page.locator('.hotspot-0')
        mb = await marker.bounding_box()
        await page.mouse.move(mb['x'] + mb['width'] / 2, mb['y'] + mb['height'] / 2)
        before = await starts()
        await page.mouse.down()
        await page.wait_for_function('parseFloat(getComputedStyle(document.querySelector(".hotspot-0")).scale) < .99')
        presses.append(await marker.evaluate('e=>getComputedStyle(e).scale'))
        await page.mouse.up()
        await expect(marker).to_have_attribute('aria-expanded', 'true')
        await page.wait_for_function('getComputedStyle(document.querySelector(".hotspot-0")).backgroundColor==="%s"' % AMBER)
        await page.wait_for_timeout(260)
        tone = await starts() - before
        pitches.append(await page.evaluate('audioProbe.starts.at(-1).frequency'))
        state = await page.evaluate('''() => ({
            leader: document.querySelector('.hotspot-leaders line').dataset.active,
            leaderOpacity: getComputedStyle(document.querySelector('.hotspot-leaders line')).opacity,
            card: document.querySelector('.component-card').dataset.selected,
            border: getComputedStyle(document.querySelector('.component-card')).borderTopColor})''')
        cards.append({'slug': slug, 'tone': tone, **state})
        await snap(f'06-{slug}-inspection.png')
        await page.locator('.hotspot-1').click()
        await page.wait_for_timeout(200)
        await page.locator('.hotspot-2').click()
        await page.wait_for_timeout(200)
        before_close = await starts()
        await page.get_by_role('button', name='Close component card').click()
        close_tone = await starts() - before_close
        await page.wait_for_timeout(900)
        drained.append({'slug': slug, 'base': base, 'after': await page.evaluate('audioProbe.live'), 'closeTone': close_tone})
        if i == 4:
            break
        await settle_to(page, '.case-next')
        nb = await page.locator('.case-next .case-button').bounding_box()
        await page.mouse.move(nb['x'] + nb['width'] / 2, nb['y'] + nb['height'] / 2)
        await page.mouse.down()
        await page.wait_for_timeout(160)
        next_scale = await page.locator('.case-next .case-button').evaluate('e=>getComputedStyle(e).scale')
        before = await starts()
        hop = await flight(page, page.mouse.up, f"{URL}/work/{CASES[i + 1]['id']}")
        hops.append({'from': slug, 'to': CASES[i + 1]['id'], 'sweepVoices': await starts() - before, 'locked': hop['locked'],
                     'moving': 'moving' in hop['states'], 'pressScale': next_scale})
        if i == 0:
            (OUT / '07-next-sweep.png').write_bytes(hop['mid'])

    # 6. BrandWall: tap the instrument → detector observes, with its own click.
    before = await starts()
    await page.locator('.case-inspection').click(position={'x': 180, 'y': 380})
    observe_tone = await starts() - before
    await page.wait_for_timeout(700)
    await snap('08-brandwall-observed.png')

    # 7. Return (sound on) → sweep, chapter BrandWall, focus on its Open case file.
    await settle_to(page, '.case-next')
    before = await starts()
    ret = await flight(page, lambda: page.locator('.case-next [data-home-target]').click(), URL + '/')
    return_voices = await starts() - before
    (OUT / '09-return-flight.png').write_bytes(ret['mid'])
    await page.wait_for_timeout(400)
    await snap('09b-return-home.png')
    landed = await page.evaluate("Math.abs(document.getElementById('brandwall').getBoundingClientRect().top) < 5")
    # After a chain the destination is #<slug> (no saved scroll), so the shell focuses the chapter heading;
    # focus on Open case file applies when returning to a saved position (verify_showpiece edges).
    focus_back = await page.locator('#brandwall h2').evaluate('e=>e===document.activeElement')

    # 8. Mute: silent immediately, taps make no voice.
    await page.locator('.sound-toggle').click()
    await expect(page.locator('.sound-toggle')).to_have_attribute('aria-pressed', 'false')
    before = await starts()
    await page.locator('.menu-toggle').click()
    await page.wait_for_timeout(300)
    await page.keyboard.press('Escape')
    await page.wait_for_timeout(1500)
    rms_muted = await page.evaluate('audioProbe.rms()')
    muted_voices = await starts() - before
    await snap('10-muted.png')

    # 9. Reload: remembered mute → Enter creates no audio. The reload ends this page's recorder, so collect it first.
    meta['audioCapture'] = await page.evaluate(STOP_REC)
    await page.reload()
    await expect(page.locator('.enter-button')).to_be_enabled(timeout=30000)
    await page.locator('.enter-button').click()
    await vs.idle(page)
    remembered = await page.evaluate('audioProbe.contexts.length') == 0 and await page.locator('.sound-toggle').get_attribute('aria-pressed') == 'false'
    await page.wait_for_timeout(600)
    canvases = await page.locator('canvas').count()

    raw = await page.video.path()
    await context.close()

    checks['instrumentClicks'] = {
        'pass': len(set(pitches)) == 5 and all(c['tone'] == 1 for c in cards) and all(d['after'] == d['base'] for d in drained)
                and menu_tone >= 1 and all(d['closeTone'] >= 1 for d in drained) and observe_tone == 1,
        'detail': '; '.join(f"{c['slug']} tone {round(p)} Hz" for c, p in zip(cards, pitches))
                  + f"; menu open tone={menu_tone}, card close tones={[d['closeTone'] for d in drained]}, BrandWall observe tone={observe_tone}; "
                  + f"live voices after taps back to hum-only baseline={[d['after'] == d['base'] for d in drained]}",
        'screenshot': '06-crosscheck-inspection.png',
    }
    checks['transitionSounds'] = {
        'pass': fly_in >= 2 and all(h['sweepVoices'] >= 4 for h in hops) and return_voices >= 2,
        'detail': f"fly-in {fly_in} sweep voices; Next hops {[h['sweepVoices'] for h in hops]} voices (two-part); Return {return_voices} voices",
        'screenshot': '05b-flight-mid.png',
    }
    checks['_mainSound'] = {'rmsOn': rms_on, 'rmsMuted': rms_muted, 'mutedVoices': muted_voices, 'remembered': remembered}
    checks['_micro'] = {'ctaScale': cta_scale, 'presses': presses, 'hops': hops, 'cards': cards, 'arrival': arrival}
    checks['_transitions'] = {'flight': {k: f[k] for k in ('locked', 'midOpacity', 'states')}, 'focus': focus, 'hops': hops,
                              'returnStates': ret['states'], 'returnLocked': ret['locked'], 'landed': landed, 'focusBack': focus_back}
    checks['clean'] = {
        'pass': canvases == 1 and not errors and not bad and not any(overflows),
        'detail': f"Canvas={canvases} (same element through fly-in, 4 hops, Return), page/console errors={errors or 0}, responses ≥400={bad or 0}, horizontal overflow={any(overflows)}",
        'screenshot': '02-hero-sound-on.png',
    }
    return raw, video_start


async def perf_gate(browser, checks, meta):
    runs = {}
    for name, profile in (('devtools-slow-4g', SLOW_4G), ('light-slow-4g', LIGHT_4G)):
        context = await phone_context(browser)
        await context.add_init_script(TIMING)
        page = await context.new_page()
        cdp = await context.new_cdp_session(page)
        await cdp.send('Network.enable')
        await cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
        await cdp.send('Network.emulateNetworkConditions', profile)
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': CPU})
        await page.goto(URL, wait_until='commit', timeout=90000)
        shot_at = None
        if name == 'devtools-slow-4g':
            await page.wait_for_function('performance.now() >= 2500', timeout=30000, polling=50)
            shot_at = round(await page.evaluate('performance.now()'))
            await page.screenshot(path=str(OUT / '11a-perf-gate-2.5s.png'))
            visible = await page.locator('.enter-button').evaluate('e=>{const r=e.getBoundingClientRect();return r.bottom<=innerHeight&&r.width>0&&getComputedStyle(e).visibility!=="hidden"}')
        await page.wait_for_function('window.__t && window.__t.enter', timeout=120000, polling=200)
        if name == 'devtools-slow-4g':
            await page.wait_for_timeout(400)
            await page.screenshot(path=str(OUT / '11b-perf-gate-enter.png'))
        t = await page.evaluate('window.__t')
        entries = await page.evaluate("""performance.getEntriesByType('navigation').concat(performance.getEntriesByType('resource'))
            .map(e=>({url:e.name, bytes:e.transferSize, type:e.initiatorType}))""")
        groups = {}
        for e in entries:
            u = e['url'].split('?')[0]
            kind = ('3D models' if u.endswith('.glb') else 'fonts' if u.endswith(('.ttf', '.woff2')) else 'JavaScript' if u.endswith('.js')
                    else 'Draco decoder' if u.endswith('.wasm') else 'CSS' if u.endswith('.css') else 'HTML' if e['type'] == 'navigation' else 'images/other')
            groups[kind] = groups.get(kind, 0) + e['bytes']
        runs[name] = {'firstContentfulPaintMs': round(t.get('first-contentful-paint', -1)), 'gateInDomMs': round(t.get('gateDom', -1)),
                      'enterEnabledMs': round(t['enter']), 'transferredBytes': sum(groups.values()), 'byType': groups,
                      **({'screenshotAtMs': shot_at, 'enterVisibleAt2500ms': visible} if shot_at else {})}
        await context.close()
    main = runs['devtools-slow-4g']
    meta['gate'] = runs
    checks['perfGate'] = {
        'pass': 0 < main['firstContentfulPaintMs'] < 2500 and main['enterVisibleAt2500ms'],
        'detail': f"DevTools Slow 4G + {CPU}x CPU: gate painted at {main['firstContentfulPaintMs']} ms with Enter on screen at 2.5 s={main['enterVisibleAt2500ms']}; "
                  f"Enter becomes active at {main['enterEnabledMs']} ms (all seven models + fonts, {main['transferredBytes']:,} bytes). "
                  f"Lighter 150 ms profile: paint {runs['light-slow-4g']['firstContentfulPaintMs']} ms, active {runs['light-slow-4g']['enterEnabledMs']} ms",
        'screenshot': '11-perf-gate.png',
    }
    FINDINGS['perfGate'] = (f"For the owner, not an automatic fail: the gate and a (disabled) Enter button appear in {main['firstContentfulPaintMs']/1000:.1f} s, "
                            f"but Enter only becomes tappable after {main['enterEnabledMs']/1000:.1f} s on slow 4G (it waits for all seven models and fonts; "
                            f"{main['transferredBytes']/1e6:.2f} MB). Options: accept, or back to Development to let Enter open earlier "
                            "(e.g. after the dome only, loading the instruments behind the hero).")


async def perf_fps(browser, checks, meta):
    results = {}
    for rate in (CPU, 6):
        context = await phone_context(browser)
        await context.add_init_script(FRAMES)
        page = await context.new_page()
        cdp = await context.new_cdp_session(page)
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': rate})
        await page.goto(URL)
        await page.locator('.enter-button').click(timeout=60000)  # sound on, as a default visitor
        await vs.idle(page)
        await page.wait_for_timeout(800)
        segs = {}

        async def measure(name, action):
            n0 = await page.evaluate('__frames.length')
            await action()
            segs[name] = await page.evaluate('(n)=>__frames.slice(n)', n0)

        await measure('hero idle', lambda: page.wait_for_timeout(3000))
        await measure('scroll: hero → five chapters → Skills', lambda: scroll_all(page, cdp))
        await settle_to(page, '#crosscheck', 240)
        await page.wait_for_timeout(600)

        async def fly():
            await page.locator('[data-open-case=crosscheck]').click()
            await page.wait_for_url('**/work/crosscheck')
            await vs.idle(page)
        await measure('fly-in to CrossCheck', fly)
        await settle_to(page, '#case-instrument')

        async def inspect():
            for i in range(3):
                await page.locator(f'.hotspot-{i}').click()
                await page.wait_for_timeout(900)
        await measure('case inspection (3 hotspots)', inspect)
        await settle_to(page, '.case-next')

        async def hop():
            await page.locator('.case-next .case-button').click()
            await page.wait_for_url('**/work/surgeline')
            await vs.idle(page)
        await measure('Next sweep → SurgeLine', hop)

        async def back():
            await page.locator('.case-brief [data-home-target]').click()
            await page.wait_for_url(URL + '/')
            await vs.idle(page)
        await measure('Return flight', back)
        results[rate] = {k: {**frame_stats(v), 'series': [round(b - a, 1) for a, b in zip(v, v[1:])]} for k, v in segs.items()}
        await context.close()
    meta['fps'] = {str(k): {s: {x: y for x, y in v.items() if x != 'series'} for s, v in r.items()} for k, r in results.items()}
    main = results[CPU]
    ok = all(s['fps'] >= 45 and s['p95Ms'] <= STABLE_MS for s in main.values())
    checks['perfFps'] = {
        'pass': ok,
        'detail': f"{CPU}x CPU: " + '; '.join(f"{k} {s['fps']} fps (p95 {s['p95Ms']} ms, {s['framesOver22ms']}% frames slower than 45 fps)" for k, s in main.items())
                  + " | 6x stress (informative): " + '; '.join(f"{k} {s['fps']} fps" for k, s in results[6].items()),
        'screenshot': '12-perf-fps.png',
    }
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), dpi=110, sharey=True)
    for ax, rate in zip(axes, (CPU, 6)):
        x = 0
        for name, s in results[rate].items():
            ys = s['series']
            ax.plot(range(x, x + len(ys)), ys, lw=.8, label=f"{name}: {s['fps']} fps")
            x += len(ys) + 20
        ax.axhline(1000 / 60, color='#5BE49B', ls='--', lw=1)
        ax.axhline(STABLE_MS, color='#FF5A5F', ls='--', lw=1)
        ax.set_ylim(0, 60)
        ax.set_ylabel('frame time (ms)')
        ax.set_title(f"{rate}x CPU throttle{' — PLAN §11 check' if rate == CPU else ' — stress, informative'} · green = 60 fps, red = 45 fps")
        ax.legend(fontsize=7, loc='upper right')
    axes[-1].set_xlabel('frames (segments in order)')
    fig.tight_layout()
    fig.savefig(OUT / '12-perf-fps.png')
    plt.close(fig)


async def scroll_all(page, cdp):
    await swipe_to(page, cdp, await top(page, '#skills'))


async def dpr_cap(browser, checks):
    rows = []
    for (w, h, dpr) in ((390, 844, 2), (430, 932, 3)):
        context = await browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr, is_mobile=True, has_touch=True)
        page = await context.new_page()
        await page.goto(URL)
        await page.locator('.silent-button').click(timeout=30000)
        await vs.idle(page)
        ratio = await page.evaluate('(()=>{const c=document.querySelector("canvas");return c.width/c.clientWidth})()')
        rows.append({'viewport': f'{w}x{h}', 'devicePixelRatio': dpr, 'canvasRatio': round(ratio, 3)})
        await context.close()
    checks['dprCap'] = {
        'pass': all(r['canvasRatio'] <= 1.501 for r in rows),
        'detail': '; '.join(f"{r['viewport']} at DPR {r['devicePixelRatio']} → canvas {r['canvasRatio']}x" for r in rows),
        'screenshot': '02-hero-sound-on.png',
    }


def assets_check(checks, meta):
    glbs = [glb_info(p) for p in sorted(MODELS.glob('*.glb'))]
    total = sum(g['bytes'] for g in glbs)
    meta['assets'] = glbs
    checks['perfAssets'] = {
        'pass': len(glbs) == 7 and total <= 8e6 and all(g['bytes'] <= 1.5e6 and g['draco'] for g in glbs),
        'detail': f"7 GLB total {total:,} bytes (limit 8,000,000); largest {max(glbs, key=lambda g: g['bytes'])['file']} {max(g['bytes'] for g in glbs):,} (limit 1,500,000); "
                  f"all Draco={all(g['draco'] for g in glbs)}, image textures={sum(g['images'] for g in glbs)}; demo videos load only on play",
        'screenshot': '11-perf-gate.png',
    }


async def hover_check(browser):
    context = await browser.new_context(viewport={'width': 1440, 'height': 900})
    page = await context.new_page()
    await page.goto(URL)
    await expect(page.locator('.enter-button')).to_be_enabled(timeout=30000)
    fine = await page.evaluate("matchMedia('(hover: hover) and (pointer: fine)').matches")
    await page.locator('.enter-button').hover()
    await page.wait_for_timeout(300)
    hovered = await page.locator('.enter-button').evaluate('e=>[getComputedStyle(e).backgroundColor, getComputedStyle(e.querySelector("span")).transform]')
    await context.close()
    context = await phone_context(browser)
    page = await context.new_page()
    await page.goto(URL)
    coarse = await page.evaluate("matchMedia('(hover: hover) and (pointer: fine)').matches")
    await context.close()
    return {'mouseMatches': fine, 'hoverBackground': hovered[0], 'hoverArrow': hovered[1], 'phoneMatches': coarse}


async def phones_check(browser, checks, meta):
    vs.OUT = OUT / 'phones'
    vs.OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for w, h in ((360, 740), (430, 932)):
        try:
            r = await vs.phone(browser, w, h)
            results.append({'viewport': r['viewport'], 'pass': True, 'pitches': [round(p) for p in r['pitches']]})
        except Exception as error:  # noqa: BLE001 — record, keep going
            results.append({'viewport': f'{w}x{h}', 'pass': False, 'error': str(error).splitlines()[0]})
    suites = []
    for label, path in REGRESSIONS.items():
        file = ROOT / path
        data = json.loads(file.read_text()) if file.exists() else {}
        status = data.get('status', 'passed' if file.exists() and label.startswith('verify_audio') else 'missing')
        suites.append({'suite': label, 'status': status, 'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat(timespec='minutes') if file.exists() else None})
    meta['regressions'] = suites
    checks['phones'] = {
        'pass': all(r['pass'] for r in results) and all(s['status'] == 'passed' for s in suites),
        'detail': '; '.join(f"{r['viewport']}: {'showpiece checks pass, tones ' + str(r['pitches']) if r['pass'] else 'FAILED ' + r['error']}" for r in results)
                  + ' | regression suites: ' + '; '.join(f"{s['suite']}={s['status']} ({s['modified']})" for s in suites),
        'screenshot': 'phones/phones-sheet.jpg',
        'regressions': suites,
    }


async def edges_check(browser, checks, meta):
    vs.OUT = OUT / 'edges'
    vs.OUT.mkdir(parents=True, exist_ok=True)
    try:
        edge = await vs.edges(browser)
        meta['edges'] = edge
        return True, None
    except Exception as error:  # noqa: BLE001
        return False, str(error).splitlines()[0] if str(error) else type(error).__name__


def mux(raw, audio, video_start, mp4):
    if not audio:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', '-movflags', '+faststart', str(mp4)], check=True)
        return None
    track = OUT / 'raw/audio.webm'
    track.write_bytes(base64.b64decode(audio['data']))
    delay = max(0, round(audio['start'] - video_start * 1000))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-i', str(track), '-map', '0:v', '-map', '1:a',
                    '-af', f'adelay={delay}:all=1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22',
                    '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(mp4)], check=True)
    level = subprocess.run(['ffmpeg', '-i', str(mp4), '-map', '0:a', '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    stats = {l.split('] ')[1].split(':')[0]: l.split(': ')[1] for l in level.splitlines() if 'volumedetect' in l and ('mean_volume' in l or 'max_volume' in l)}
    return {'offsetMs': delay, **stats}


def sheets():
    def strip(names, path, size=(390, 844)):
        sheet = Image.new('RGB', (size[0] * len(names), size[1]), 'black')
        for i, (name, label) in enumerate(names):
            if (OUT / name).exists():
                sheet.paste(tile(OUT / name, label, size), (i * size[0], 0))
        sheet.save(path, quality=88)
    strip([('05a-flight-start.png', 'Tap Open case file'), ('05b-flight-mid.png', 'Flying in · sweep'), ('05c-flight-end.png', 'CrossCheck case')], OUT / '05-flight-in.png')
    strip([('11a-perf-gate-2.5s.png', 'Slow 4G + 4x CPU · 2.5 s'), ('11b-perf-gate-enter.png', 'Enter active')], OUT / '11-perf-gate.png')
    strip([('01a-loader-calibrating.png', 'Calibrating · dial filling'), ('01b-loader-ready.png', 'Calibrated · green'),
           ('edges/loader-pending-390x844.png', 'Model stalled · incomplete'), ('edges/loader-fallback-390x844.png', 'Still view · amber')], OUT / '01-loader.png')
    strip([('06-crosscheck-inspection.png', 'Marker pressed · leader · card'), ('04-menu.png', 'Menu slides in')], OUT / '13-micro.png')
    strip([('10-muted.png', 'Muted'), ('edges/audio-unavailable-390x844.png', 'Audio unavailable notice')], OUT / '14-sound-control.png')
    size = (390, 844)
    sheet = Image.new('RGB', (size[0] * 3, size[1] * 4), 'black')
    for c, tag in enumerate(['390x844', '360x740', '430x932']):
        for r, kind in enumerate(['gate', 'flight', 'crosscheck-inspection', 'return']):
            source = (OUT / 'phones' / f'{kind}-{tag}.png') if tag != '390x844' else OUT / {'gate': '01b-loader-ready.png', 'flight': '05b-flight-mid.png',
                                                                                          'crosscheck-inspection': '06-crosscheck-inspection.png', 'return': '09b-return-home.png'}[kind]
            if source.exists():
                sheet.paste(tile(source, f'{tag} · {kind}', size), (c * size[0], r * size[1]))
    sheet.save(OUT / 'phones/phones-sheet.jpg', quality=86)
    labeled = [
        ('01a-loader-calibrating.png', 'Loader · calibrating (slow 4G)'),
        ('01b-loader-ready.png', 'Loader · calibrated'),
        ('edges/loader-fallback-390x844.png', 'Loader · still-view path'),
        ('02-hero-sound-on.png', 'Enter with sound · hero'),
        ('03-chapter-crosscheck.png', 'CrossCheck chapter'),
        ('03-chapter-surgeline.png', 'SurgeLine chapter'),
        ('03-chapter-driftwatch.png', 'DriftWatch chapter'),
        ('03-chapter-duewatch.png', 'DueWatch chapter'),
        ('03-chapter-brandwall.png', 'BrandWall chapter'),
        ('04-menu.png', 'Menu entrance + tone'),
        ('05b-flight-mid.png', 'Fly-in · sweep'),
        ('05c-flight-end.png', 'CrossCheck case'),
        ('06-crosscheck-inspection.png', 'CrossCheck tone'),
        ('06-surgeline-inspection.png', 'SurgeLine tone'),
        ('06-driftwatch-inspection.png', 'DriftWatch tone'),
        ('06-duewatch-inspection.png', 'DueWatch tone'),
        ('06-brandwall-inspection.png', 'BrandWall tone'),
        ('07-next-sweep.png', 'Next sweep'),
        ('08-brandwall-observed.png', 'BrandWall observed'),
        ('09-return-flight.png', 'Return sweep'),
        ('09b-return-home.png', 'Back at BrandWall'),
        ('10-muted.png', 'Muted · silent'),
        ('11a-perf-gate-2.5s.png', 'Slow 4G · 2.5 s'),
        ('11b-perf-gate-enter.png', 'Slow 4G · Enter active'),
    ]
    cols, tsize = 6, (390, 844)
    rows = (len(labeled) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tsize[0], rows * tsize[1]), 'black')
    for i, (name, label) in enumerate(labeled):
        if (OUT / name).exists():
            sheet.paste(tile(OUT / name, f'{i + 1:02d} {label}', tsize), ((i % cols) * tsize[0], (i // cols) * tsize[1]))
    sheet.save(OUT / 'contact-sheet.jpg', quality=84)


async def run():
    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ('raw', 'phones', 'edges'):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    checks, meta = {}, {}
    audio = None
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU + ['--autoplay-policy=no-user-gesture-required'])
        try:
            print('main flow (recorded)', flush=True)
            raw, video_start, audio = await main_flow_with_audio(browser, checks, meta)
            print('edges', flush=True)
            edges_ok, edges_error = await edges_check(browser, checks, meta)
            print('hover', flush=True)
            hover = await hover_check(browser)
            print('perf gate', flush=True)
            await perf_gate(browser, checks, meta)
            print('perf fps', flush=True)
            await perf_fps(browser, checks, meta)
            await dpr_cap(browser, checks)
            assets_check(checks, meta)
            print('phones', flush=True)
            await phones_check(browser, checks, meta)
        finally:
            await browser.close()

    loader = meta['loader']
    samples = loader['samples']
    checks['loader'] = {
        'pass': bool(samples) and samples == sorted(samples) and samples[-1] == 100 and loader['dial'] == OK
                and loader['status'].startswith('Instruments calibrated') and edges_ok,
        'detail': f"{len(samples)} progress updates on slow 4G, never backwards={samples == sorted(samples)}, "
                  f"first/last {samples[0] if samples else None}/{samples[-1] if samples else None}; pending text '{loader['pending'].splitlines()[0]}'; "
                  f"ready: dial {loader['dial']} (signal-ok), '{loader['status'].splitlines()[0]}'; stalled model → incomplete dial, then amber still view={edges_ok}",
        'screenshot': '01-loader.png',
    }
    s = checks.pop('_mainSound')
    checks['soundControl'] = {
        'pass': s['rmsMuted'] < .00005 and s['mutedVoices'] == 0 and s['remembered'] and edges_ok,
        'detail': f"muted RMS {s['rmsMuted']:.6f}, voices started while muted={s['mutedVoices']}, remembered mute after reload (no AudioContext)={s['remembered']}; "
                  f"hidden tab silent + resumes, audio-unavailable notice (verify_showpiece edges)={edges_ok}" + (f" — {edges_error}" if edges_error else ''),
        'screenshot': '14-sound-control.png',
    }
    m = checks.pop('_micro')
    checks['microInteractions'] = {
        'pass': scale(m['ctaScale']) < 1 and all(scale(x) < .99 for x in m['presses']) and all(scale(h['pressScale']) < 1 for h in m['hops'])
                and all(c['leader'] == 'true' and c['leaderOpacity'] == '1' and c['card'] == 'true' and c['border'] == AMBER for c in m['cards'])
                and 'control-arrival' in m['arrival'] and hover['mouseMatches'] and not hover['phoneMatches']
                and hover['hoverArrow'] not in ('none', '') and hover['hoverBackground'] == 'rgb(237, 232, 220)',
        'detail': f"press scale: Open case file {m['ctaScale']}, markers {m['presses']}, Next {[h['pressScale'] for h in m['hops']]}; "
                  f"active leader + amber card border in 5/5={all(c['border'] == AMBER and c['leader'] == 'true' for c in m['cards'])}; "
                  f"menu animations '{m['arrival']}'; hover rules on mouse={hover['mouseMatches']} (Enter → {hover['hoverBackground']}, arrow {hover['hoverArrow']}), on phone={hover['phoneMatches']}",
        'screenshot': '13-micro.png',
    }
    t = checks.pop('_transitions')
    checks['transitions'] = {
        'pass': 'moving' in t['flight']['states'] and t['flight']['locked'] and t['flight']['midOpacity'] < 1 and t['focus'] == 'case-heading'
                and len(t['hops']) == 4 and all(h['moving'] and h['locked'] for h in t['hops'])
                and 'moving' in t['returnStates'] and t['returnLocked'] and t['landed'] and t['focusBack'] and edges_ok,
        'detail': f"fly-in states {t['flight']['states']}, locked={t['flight']['locked']}, homepage opacity mid-flight {t['flight']['midOpacity']}, focus #{t['focus']}; "
                  f"Next {' → '.join([h['from'] for h in t['hops']] + [t['hops'][-1]['to']])} all locked={all(h['locked'] for h in t['hops'])}; "
                  f"Return landed on #brandwall={t['landed']} with focus on its chapter heading={t['focusBack']}; "
                  f"exact scroll restore + Back during departure (verify_showpiece edges)={edges_ok}",
        'screenshot': '05-flight-in.png',
    }

    mp4 = OUT / 'showpiece-walkthrough.mp4'
    sound = mux(raw, audio, video_start, mp4)
    shutil.rmtree(OUT / 'raw', ignore_errors=True)
    sheets()
    probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,codec_name,width,height',
                                       '-of', 'json', str(mp4)], capture_output=True, text=True, check=True).stdout)

    passed = all(checks.get(k, {}).get('pass') for k in ITEMS)
    report = {
        'status': 'passed' if passed else 'failed',
        'phase': 'Phase 7 — Showpiece polish',
        'stage': 'Testing',
        'finishedAt': datetime.now(timezone.utc).isoformat(),
        'url': URL,
        'scope': f'Chromium GPU (ANGLE) emulation, phones at DPR 2; CPU throttle via DevTools protocol on {platform.processor() or platform.machine()} host '
                 '(Intel i7-11800H, RTX 3060 Laptop GPU — the GPU is not throttled, so phone GPU cost is not represented); physical phone = Phase 8',
        'items': {k: {'label': ITEMS[k], **checks.get(k, {'pass': False, 'detail': 'not executed'}), **({'finding': FINDINGS[k]} if k in FINDINGS else {})} for k in ITEMS},
        'measurements': {'gate': meta.get('gate'), 'fps': meta.get('fps'), 'assets': meta.get('assets'), 'regressions': meta.get('regressions')},
        'video': {'file': mp4.name, 'size': [W, H], 'seconds': round(float(probe['format']['duration']), 1),
                  'streams': probe['streams'], 'audio': sound,
                  'note': "Audio track = the site's own Web Audio output captured in the browser (not re-created); aligned to the video within ~0.1-0.3 s"},
        'contactSheet': 'contact-sheet.jpg',
        'sheets': ['01-loader.png', '05-flight-in.png', '11-perf-gate.png', '12-perf-fps.png', '13-micro.png', '14-sound-control.png', 'phones/phones-sheet.jpg'],
    }
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    for key, check in report['items'].items():
        print(f"{'PASS' if check['pass'] else 'FAIL'} {key}: {check['detail']}")
    print(f"Overall: {report['status']} · video {report['video']['seconds']}s · audio {sound}")
    return passed


async def main_flow_with_audio(browser, checks, meta):
    """main_flow plus the audio captured before its reload."""
    raw, start = await main_flow(browser, checks, meta)
    return raw, start, meta.get('audioCapture')


if __name__ == '__main__':
    sys.exit(0 if asyncio.run(run()) else 1)
