"""Phase 7F Testing evidence pack — Five rooms, one observatory (full round; PROGRESS kontrak 7A–7F, PLAN §8.2 / §12).

One walkthrough per device, 390×844 (touch, DPR 2) and 1440×900 (mouse wheel), recorded:
for each of the five projects — scroll to its one-screen chapter, turn the instrument by hand and by tap (Q49),
open the case through that case's own curtain, play the room's own explanation (scan, crash/resume, snapshot compare,
business time + handoff, before/after), Return through the same curtain to the chapter. Then the whole Next chain
CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall → CrossCheck (origin curtain closes, destination curtain opens),
Back/Forward inside the chain, Return from the chain, direct URL + refresh of all five cases.
Separately (not filmed): interruptions per project (Back while the curtain moves, double Open, double Next, rapid taps on
the instrument, scroll during a curtain, resize on a case), blocked model per case, fps of the chain (phone 4× CPU, desktop).
Development results on the same source fingerprint are read, not re-run (Q42): six viewports per room suite, edges, perf_quick.

Writes assets/renders/personal-observatory/evidence/: walkthrough-mobile.mp4, walkthrough-desktop.mp4, slow-motion.mp4
(the ten curtain hops at 0.25×), contact-sheet-mobile.jpg, contact-sheet-desktop.jpg, strips i01…, PNG per step, evidence.json
(items + categories + per project/device results). Exit 1 if an item fails. Server :8767 must run a build of this source.
"""
import asyncio
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from playwright.async_api import async_playwright

import q49
import run_regressions as rr
from case_files_evidence import tile
from perf_quick import GPU, stats
from verify_case import URL, enter, idle
from verify_cases import CASES, trace_numbers

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/personal-observatory/evidence'
RAW = OUT / 'raw'
FONT = '/usr/share/fonts/TTF/DejaVuSans.ttf'
IDS = q49.IDS
NAMES = {c['id']: c['name'] for c in CASES}
STRIPS = {'crosscheck': '.scan-strip', 'surgeline': '.dispatch-chapter', 'driftwatch': '.monitor-chapter', 'duewatch': '.time-chapter', 'brandwall': '.brand-chapter'}
ROOMS = {'crosscheck': '.inspection-field', 'surgeline': '.dispatch-room', 'driftwatch': '.monitoring-room', 'duewatch': '.time-room', 'brandwall': '.brand-studio'}
EXPLAINS = {'crosscheck': 'scan three browsers → coverage matrix → evidence-backed findings',
            'surgeline': 'queue → three browsers → cut/resume → one outcome per record',
            'driftwatch': 'snapshot → diff → healthy change vs alarm with a reason',
            'duewatch': 'business-time agenda, separate message triage, human handoff',
            'brandwall': 'specimen → before / compare / after by tap'}
# One recorder at a time: a new call ends the previous loop (otherwise loops stack and fps multiplies).
FRAMES = "(() => { const id = (window.__framesId || 0) + 1; window.__framesId = id; window.__frames = []; const f = t => { if (window.__framesId !== id) return; window.__frames.push(t); requestAnimationFrame(f); }; requestAnimationFrame(f); })();"
FOCUS = "(()=>{const a=document.activeElement;return a?(a.id||a.dataset.openCase||a.tagName):null})()"

CATEGORIES = ['story', 'visual', 'animation', 'transition', 'mobile', 'desktop', 'source', 'performance']
ITEMS = {
    'crosscheck': (['story', 'visual', 'animation', 'transition', 'mobile', 'desktop'], 'CrossCheck on phone + desktop: chapter turned by drag and tap (scan strip follows), stage curtain in/out, inspection field plays itself + step button + Replay, finding evidence, Return restores scroll + focus'),
    'surgeline': (['story', 'visual', 'animation', 'transition', 'mobile', 'desktop'], 'SurgeLine on phone + desktop: chapter strands follow the turn, blinds curtain in/out, dispatch board Start → Cut → Resume → 4 confirmed / C rejected / F dead-letter, Return restores scroll + focus'),
    'driftwatch': (['story', 'visual', 'animation', 'transition', 'mobile', 'desktop'], 'DriftWatch on phone + desktop: chapter trace follows the turn, roller curtain in/out, snapshot compare: layout break = alarm with codes, source change = healthy diff, Return restores scroll + focus'),
    'duewatch': (['story', 'visual', 'animation', 'transition', 'mobile', 'desktop'], 'DueWatch on phone + desktop: business-time pointer follows the turn, louvre curtain in/out, agenda (7 days → renew) and triage (complaint → human handoff) stay separate modules, simulation label kept, Return restores scroll + focus'),
    'brandwall': (['story', 'visual', 'animation', 'transition', 'mobile', 'desktop'], 'BrandWall on phone + desktop: spectrum chapter follows the turn, prism curtain in/out, specimen compared Before / Compare / After by tap, Return restores scroll + focus'),
    'chain': (['transition', 'mobile', 'desktop'], 'Next chain CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall → CrossCheck on both devices: each hop closes the origin case curtain and opens the destination case curtain, lands at the top of the destination brief, same Canvas'),
    'history': (['transition', 'mobile', 'desktop'], 'Back/Forward inside the chain, Return from the chain lands on the current case chapter, direct URL + refresh of all five cases on both devices'),
    'interruptions': (['animation', 'transition', 'mobile', 'desktop'], 'Per project on both devices: Back while the curtain moves, double Open, rapid taps on the instrument; plus double Next, scroll during a curtain, resize on a case — no stuck curtain, locked scroll, skipped case or queued animation'),
    'distinct': (['story', 'visual', 'animation', 'transition'], 'Five rooms stay different: five curtain styles, five chapter illustrations, five case room layouts (different explanation, not only colour and name)'),
    'observatory': (['story', 'visual', 'mobile', 'desktop'], 'One observatory: same header, sound toggle, progress readout and Canvas on the homepage and all cases; phone menu + desktop navigation; Skills, About and Contact present'),
    'desktopShowpiece': (['desktop', 'visual'], 'Desktop 1440×900 is the main stage: chapter copy beside the instrument stage for all five, case rooms use the wide layout'),
    'viewports': (['mobile', 'desktop'], 'Six viewports per project (390/360/430/768/1440/1920) + edges from the Development room suites on this source fingerprint (Q42, not re-run)'),
    'fallback': (['visual', 'mobile'], 'Blocked model on each of the five cases: labelled still view, hotspot cards still open'),
    'sources': (['source'], 'Case readings trace to the dossiers; no DRAFT label left on any page except none; no forbidden claims (affiliation, live, guaranteed)'),
    'performance': (['performance', 'mobile', 'desktop'], 'perf_quick Development per project (390×844 DPR 2, 4× CPU, same fingerprint) + chain hops measured here on phone 4× CPU and desktop: ≥ 45 fps, ≤ 10% slow frames'),
    'clean': (['mobile', 'desktop'], 'Zero page errors, zero responses ≥ 400, no horizontal overflow in both walkthroughs'),
    'regressions': (['mobile', 'desktop'], 'Runner ledger: all 18 suites passed on this fingerprint'),
}
CHECKS, META = {}, {'errors': {}}


# ---------------------------------------------------------------- helpers (copied from the 7A archive script, which no longer imports since Q49)
def watch(page, sink):
    page.on('pageerror', lambda e: sink['errors'].append(str(e)))
    page.on('console', lambda m: sink['errors'].append(m.text) if m.type == 'error' else None)
    page.on('response', lambda r: sink['bad'].append([r.status, r.url]) if r.status >= 400 else None)


async def swipe(cdp, dist, width=390, height=844):
    """One real touch swipe; positive dist scrolls down."""
    x, y0, steps = width / 2, height * (.76 if dist > 0 else .24), 14
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y0}]})
    for i in range(1, steps + 1):
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y0 - dist * i / steps}]})
        await asyncio.sleep(.016)
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})


async def swipe_until(page, cdp, target, step=360, pause=.3):
    for _ in range(80):
        y = await page.evaluate('scrollY')
        if abs(y - target) < 50 or (target > y and await page.evaluate('scrollY>=document.documentElement.scrollHeight-innerHeight-2')):
            break
        await swipe(cdp, max(-step, min(step, target - y)))
        await asyncio.sleep(pause)


async def wheel_until(page, target, step=120, pause=45):
    for _ in range(400):
        y = await page.evaluate('scrollY')
        if abs(y - target) < 80:
            break
        await page.mouse.wheel(0, step if target > y else -step)
        await page.wait_for_timeout(pause)
    await page.wait_for_timeout(500)


async def overflow(page):
    return await page.evaluate('document.documentElement.scrollWidth-innerWidth')


class Walk:
    """One recorded walkthrough: marks (seconds since start), screenshots, error sinks."""

    def __init__(self, page, tag):
        self.page, self.tag, self.t0, self.marks = page, tag, time.time(), {}
        self.sink, self.overflows = {'errors': [], 'bad': []}, []
        watch(page, self.sink)

    def mark(self, name):
        self.marks[name] = round(time.time() - self.t0, 2)

    async def shot(self, name):
        self.overflows.append(await overflow(self.page))
        await self.page.screenshot(path=str(OUT / name))
        return name


def encode(raw, mp4):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(raw), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21',
                    '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', '-movflags', '+faststart', str(mp4)], check=True)


def slow_motion(clips, mp4):
    """clips: (mp4 source, start, end, label, width). 0.25x by retiming the recorded frames (no interpolation), padded to 720×844."""
    parts = []
    for i, (source, start, end, label, width) in enumerate(clips):
        part = RAW / f'slow-{i}.mp4'
        scale = 'scale=390:844' if width == 390 else 'scale=720:-2'
        text = label.replace(':', ' ').replace("'", '')
        vf = (f"trim={max(0, start):.2f}:{end:.2f},setpts=(PTS-STARTPTS)*4,fps=25,{scale},pad=720:844:(ow-iw)/2:(oh-ih)/2:color=0x0b1020,"
              f"drawtext=fontfile={FONT}:text='{text}  ·  0.25x':x=16:y=16:fontsize=20:fontcolor=0xF2A541:box=1:boxcolor=0x0B1020@0.85:boxborderw=8")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(source), '-vf', vf, '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', str(part)], check=True)
        parts.append(part)
    listing = RAW / 'slow.txt'
    listing.write_text(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(listing), '-c', 'copy', '-movflags', '+faststart', str(mp4)], check=True)


def duration(mp4):
    probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name', '-of', 'json', str(mp4)],
                                      capture_output=True, text=True, check=True).stdout)
    return {'file': mp4.name, 'seconds': round(float(probe['format']['duration']), 1), 'size': [probe['streams'][0]['width'], probe['streams'][0]['height']],
            'codec': probe['streams'][0]['codec_name']}


def check(key, ok, detail, shot, **extra):
    CHECKS[key] = {'pass': bool(ok), 'detail': detail, 'screenshot': shot, **extra}


async def settle(page, ms=300):
    await page.wait_for_timeout(ms)


async def at(page, selector, offset=-110):
    await q49.land(page, max(0, await page.locator(selector).first.evaluate('(e,o)=>e.getBoundingClientRect().top+scrollY+o', offset)))


async def press(page, locator, touch):
    await (locator.tap() if touch else locator.click())


def image_diff(a, b):
    """Percent of pixels whose grey level changed by more than 24 (a small moving pointer still counts)."""
    ia, ib = Image.open(a).convert('L'), Image.open(b).convert('L').resize(Image.open(a).size)
    hist = ImageChops.difference(ia, ib).histogram()
    return round(100 * sum(hist[25:]) / (ia.size[0] * ia.size[1]), 2)


# ---------------------------------------------------------------- chapter: turn by hand + tap
async def touch_drag(cdp, x0, y0, dx, steps=14):
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x0, 'y': y0}]})
    for i in range(1, steps + 1):
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 + dx * i / steps, 'y': y0}]})
        await asyncio.sleep(.016)
    await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})


async def chapter(page, walk, slug, n, cdp):
    p = walk.tag
    touch = cdp is not None
    y = await page.locator(f'#{slug}').evaluate('e=>e.getBoundingClientRect().top+scrollY')
    # Arrive by the visitor's own scroll (swipe / wheel), then settle exactly on the chapter.
    await (swipe_until(page, cdp, y, step=300, pause=.25) if touch else wheel_until(page, y, step=160, pause=40))
    await q49.to_chapter(page, slug)
    await settle(page, 400)
    o0 = await q49.orbit(page, slug)
    before = OUT / f'{p}{n}0-strip-{slug}.png'
    await page.locator(STRIPS[slug]).screenshot(path=str(before))
    await walk.shot(f'{p}{n}1-chapter-{slug}.png')
    # Native scroll: the stage moves with the page and scroll does not turn the instrument.
    top0 = await page.locator(f'#{slug} .instrument-stage').evaluate('e=>e.getBoundingClientRect().top')
    await (swipe(cdp, 220, *page.viewport_size.values()) if touch else page.mouse.wheel(0, 220))
    await settle(page, 450)
    top1 = await page.locator(f'#{slug} .instrument-stage').evaluate('e=>e.getBoundingClientRect().top')
    o_scroll = await q49.orbit(page, slug)
    await q49.to_chapter(page, slug)
    await settle(page, 250)
    # Sideways drag turns it by hand (touch on the phone, mouse on desktop) …
    box = await page.locator(f'#{slug} .instrument-stage').bounding_box()
    width = max(260, box['width'] * .55)
    if touch:
        await touch_drag(cdp, box['x'] + box['width'] * .85, box['y'] + box['height'] * .42, -.35 * width)
        await settle(page, 200)
        o_drag = await q49.orbit(page, slug)
    else:
        o_drag = await q49.turn(page, slug, .35)
    # … and a tap plays the rest of the turn.
    t0 = time.time()
    if touch:
        await page.touchscreen.tap(box['x'] + box['width'] * .5, box['y'] + box['height'] * .42)
        await page.wait_for_function(f"Number(getComputedStyle(document.getElementById('{slug}')).getPropertyValue('--instrument-{IDS.index(slug)}-orbit'))===1", timeout=6000)
    else:
        await q49.tap(page, slug)
    tap_ms = round((time.time() - t0) * 1000)
    await settle(page, 300)
    after = OUT / f'{p}{n}2-strip-{slug}-turned.png'
    await page.locator(STRIPS[slug]).screenshot(path=str(after))
    await walk.shot(f'{p}{n}2-chapter-{slug}-turned.png')
    shown = await page.locator('.observatory').get_attribute('data-chapter')
    layout = await page.evaluate("""(s)=>{const r=q=>{const b=document.querySelector(q).getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)]};
      return {copy:r(`#${s} .instrument-copy`),stage:r(`#${s} .instrument-stage`),hint:!!document.querySelector(`#${s} .orbit-hint`)}}""", slug)
    return {'orbit': [o0, o_drag, 1.0 if touch else await q49.orbit(page, slug)], 'scrollMoved': round(top0 - top1), 'orbitAfterScroll': o_scroll,
            'tapMs': tap_ms, 'stripDiff': image_diff(before, after), 'dataChapter': shown, 'layout': layout,
            'ok': o0 < .05 and .15 < o_drag < .6 and abs((top0 - top1) - 220) < 40 and o_scroll == o0 and image_diff(before, after) > .2 and shown == slug}


# ---------------------------------------------------------------- curtains
async def through_curtain(page, walk, action, path, shot):
    await q49.watch_curtain(page)
    t0 = time.time()
    origin = await page.evaluate('location.pathname')
    await action()
    # Scroll is locked while the curtain closes over the page (measured before the route changes, which resets scroll).
    await page.wait_for_function("document.querySelector('.curtain').dataset.state==='moving'", timeout=3000)
    y = await page.evaluate('scrollY')
    await page.mouse.wheel(0, 240)
    await page.wait_for_timeout(80)
    same = await page.evaluate('location.pathname') == origin
    locked = abs(await page.evaluate('scrollY') - y) < 2 if same else None
    await page.wait_for_function("document.querySelector('.curtain').dataset.state==='closed'||document.querySelector('.curtain').dataset.state==='open'", timeout=5000)
    closed_ms = round((time.time() - t0) * 1000)
    if shot:
        await walk.shot(shot)
    log = await q49.curtain_log(page, path, timeout=8000)
    open_ms = round((time.time() - t0) * 1000)
    await idle(page)
    return {'closed': q49.closed_styles(log), 'log': log, 'closedMs': closed_ms, 'openMs': open_ms, 'lockedDuringCurtain': locked}


# ---------------------------------------------------------------- the rooms' own explanations
async def room(page, walk, slug, touch):
    p, n = walk.tag, IDS.index(slug) + 1
    out = {}
    if slug == 'crosscheck':
        await at(page, '.inspection-field', -70)
        await page.wait_for_function('Number(document.querySelector(".inspection-matrix").dataset.progress)>=.999', timeout=15000)
        await walk.shot(f'{p}{n}4-room-{slug}.png')
        await press(page, page.locator('.inspection-step-button', has_text='Run the checks'), touch)
        await page.wait_for_timeout(1400)
        mid = float(await page.locator('.inspection-matrix').get_attribute('data-progress'))
        await press(page, page.locator('.inspection-replay'), touch)
        await page.wait_for_function('Number(document.querySelector(".inspection-matrix").dataset.progress)>=.999', timeout=15000)
        await at(page, '#findings-heading', -90)
        await press(page, page.locator('[data-finding="CC-001"].finding-tab'), touch)
        await settle(page, 400)
        await walk.shot(f'{p}{n}5-room-{slug}-finding.png')
        out = {'stepProgress': mid, 'replayed': True, 'finding': await page.locator('[data-finding="CC-001"].finding-tab').get_attribute('aria-selected')}
        out['ok'] = 0 < mid < 1
    elif slug == 'surgeline':
        await at(page, '.dispatch-board', -250 if not touch else -100)
        await press(page, page.locator('[data-dispatch-action=start]'), touch)
        await page.wait_for_selector('.dispatch-room[data-stage="sending"]')
        await page.wait_for_timeout(1600)
        await press(page, page.locator('[data-dispatch-action=crash]'), touch)
        await page.wait_for_selector('.dispatch-room[data-stage="crashed"]')
        await page.wait_for_timeout(900)
        await walk.shot(f'{p}{n}4-room-{slug}.png')
        await press(page, page.locator('[data-dispatch-action=resume]'), touch)
        await page.wait_for_selector('.dispatch-room[data-stage="complete"]', timeout=20000)
        await page.wait_for_timeout(1200)
        await walk.shot(f'{p}{n}5-room-{slug}-complete.png')
        out = {'confirmed': await page.locator('[data-status=confirmed]').count(), 'C': await page.locator('[data-record=C]').get_attribute('data-status'),
               'F': await page.locator('[data-record=F]').get_attribute('data-status'), 'B': await page.locator('[data-record=B]').inner_text()}
        out['ok'] = out['confirmed'] == 4 and out['C'] == 'rejected' and out['F'] == 'dead-letter' and 'same receipt' in out['B']
    elif slug == 'driftwatch':
        verdicts = {}
        for scenario, shot in (('layout', f'{p}{n}4-room-{slug}.png'), ('change', f'{p}{n}5-room-{slug}-healthy.png')):
            await at(page, '.monitor-scenarios')
            await press(page, page.locator(f'[data-scenario-choice={scenario}]'), touch)
            await at(page, '[data-compare]')
            await press(page, page.locator('[data-compare]'), touch)
            await page.wait_for_timeout(1000)
            await at(page, '.monitor-result', -260 if touch else -330)
            verdicts[scenario] = await page.locator('.monitoring-room').get_attribute('data-verdict')
            if scenario == 'layout':
                await page.locator('.monitor-codes summary').click()
                verdicts['codes'] = await page.locator('.monitor-codes code').all_text_contents()
            await walk.shot(shot)
        out = {'verdicts': verdicts, 'ok': verdicts.get('layout') == 'alarm' and verdicts.get('change') == 'healthy' and 'ZERO_RECORDS' in verdicts.get('codes', [])}
    elif slug == 'duewatch':
        await at(page, '.time-date-picker')
        await press(page, page.locator('[data-days="7"]'), touch)
        await page.wait_for_timeout(700)
        category = await page.locator('.time-contract-result').get_attribute('data-category')
        await walk.shot(f'{p}{n}4-room-{slug}.png')
        triage_hidden = not await page.locator('#time-triage').is_visible()
        await at(page, '.time-module-picker')
        await press(page, page.get_by_role('button', name='B / Message triage', exact=True), touch)
        await at(page, '.time-message-picker')
        await press(page, page.locator('[data-message=complaint]'), touch)
        await page.wait_for_timeout(500)
        route = await page.locator('.time-handoff').get_attribute('data-route')
        await at(page, '.time-handoff', -200)
        await walk.shot(f'{p}{n}5-room-{slug}-handoff.png')
        text = await page.locator('.case-page').inner_text()
        out = {'agenda7': category, 'triageHiddenOnPhoneUntilPicked': triage_hidden if touch else None, 'complaint': route,
               'simulationLabel': bool(re.search(r'simulat|illustrat', text, re.I))}
        out['ok'] = category == 'renew' and route == 'human' and out['simulationLabel'] and (triage_hidden if touch else True)
    elif slug == 'brandwall':
        await at(page, '.brand-contact-sheet')
        await press(page, page.locator('[data-specimen-choice=portrait]'), touch)
        await at(page, '.brand-comparison' if touch else '.brand-view-controls')
        clips = {}
        for mode, shot in (('before', f'{p}{n}4-room-{slug}.png'), ('split', None), ('after', f'{p}{n}5-room-{slug}-after.png')):
            await press(page, page.locator(f'[data-brand-view={mode}]'), touch)
            await page.wait_for_timeout(500)
            clips[mode] = await page.locator('.brand-after').evaluate('e=>getComputedStyle(e).clipPath')
            if shot:
                await walk.shot(shot)
        out = {'clips': clips, 'ok': clips == {'before': 'inset(0px 100% 0px 0px)', 'split': 'inset(0px 50% 0px 0px)', 'after': 'inset(0px 0% 0px 0px)'}}
    return out


# ---------------------------------------------------------------- one device, one film
async def walk_device(browser, wide):
    W, H = (1440, 900) if wide else (390, 844)
    opts = {'viewport': {'width': W, 'height': H}, 'record_video_dir': str(RAW / ('desktop' if wide else 'mobile')), 'record_video_size': {'width': W, 'height': H}}
    if not wide:
        opts.update(device_scale_factor=2, is_mobile=True, has_touch=True)
    context = await browser.new_context(**opts)
    page = await context.new_page()
    walk = Walk(page, 'd' if wide else 'm')
    cdp = None if wide else await context.new_cdp_session(page)
    touch = not wide
    data = {'projects': {}, 'chain': [], 'errors': []}
    try:
        await enter(page)
        await page.evaluate("window.__canvas=document.querySelector('canvas')")
        walk.mark('start')
        await walk.shot(f'{walk.tag}00-hero.png')
        # Five projects: chapter → own curtain → own room → Return through the same curtain.
        for n, slug in enumerate(IDS, 1):
            r = data['projects'][slug] = {}
            try:
                r['chapter'] = await chapter(page, walk, slug, n, cdp)
                await at(page, f'[data-open-case={slug}]', -H * .55)
                origin = await page.evaluate('scrollY')
                walk.mark(f'open-{slug}')
                r['entry'] = await through_curtain(page, walk, lambda: press(page, page.locator(f'[data-open-case={slug}]'), touch), f'/work/{slug}', f'{walk.tag}{n}3a-curtain-{slug}.png')
                r['entry'].update(heading=await page.locator('#case-heading').inner_text(), scrollY=await page.evaluate('scrollY'), focus=await page.evaluate(FOCUS),
                                  canvas=await page.evaluate("window.__canvas===document.querySelector('canvas')"), dataChapter=await page.locator('.observatory').get_attribute('data-chapter'))
                await walk.shot(f'{walk.tag}{n}3b-brief-{slug}.png')
                r['room'] = await room(page, walk, slug, touch)
                r['roomBox'] = await page.locator(ROOMS[slug]).evaluate('e=>{const b=e.getBoundingClientRect();return [Math.round(b.x),Math.round(b.width)]}')
                await at(page, '.case-next')
                await walk.shot(f'{walk.tag}{n}6-next-{slug}.png')
                walk.mark(f'return-{slug}')
                r['return'] = await through_curtain(page, walk, lambda: press(page, page.locator('.case-next .case-back'), touch), '/', None)
                r['return'].update(scrollDelta=abs(await page.evaluate('scrollY') - origin), focus=await page.locator(f'[data-open-case={slug}]').evaluate('e=>e===document.activeElement'))
                await walk.shot(f'{walk.tag}{n}7-return-{slug}.png')
            except Exception as error:  # noqa: BLE001 — keep the film, report the project
                traceback.print_exc()
                r['error'] = repr(error)
                await page.goto(URL + '/')
                await page.locator('.silent-button').click(timeout=30000)
                await idle(page)
        # One observatory: shared chrome on the homepage.
        data['chrome'] = {'home': await chrome(page, touch, walk)}
        # The Next chain, both ends included.
        await q49.to_chapter(page, 'crosscheck')
        await press(page, page.locator('[data-open-case=crosscheck]'), touch)
        await page.wait_for_url('**/work/crosscheck')
        await idle(page)
        walk.mark('chain')
        for n, slug in enumerate(IDS):
            nxt = IDS[(n + 1) % 5]
            await at(page, '.case-next')
            walk.mark(f'hop-{slug}')
            hop = await through_curtain(page, walk, lambda: press(page, page.locator('.case-next .case-button'), touch), f'/work/{nxt}', f'{walk.tag}h{n + 1}-hop-{slug}-{nxt}.png')
            hop.update({'from': slug, 'to': nxt, 'heading': await page.locator('#case-heading').inner_text(), 'scrollY': await page.evaluate('scrollY'),
                        'canvas': await page.evaluate("window.__canvas===document.querySelector('canvas')"),
                        'destinationOpened': ['moving', q49.CURTAINS[nxt], f'/work/{nxt}'] in hop['log']})
            if n == 0:
                data['chrome']['case'] = await chrome(page, touch, None)
            data['chain'].append(hop)
        walk.mark('chainEnd')
        await walk.shot(f'{walk.tag}h6-chain-closed.png')
        # History inside the chain, then Return lands on the current chapter.
        hist = {}
        await page.go_back()
        await page.wait_for_url('**/work/brandwall')
        await idle(page)
        hist['back1'] = await page.locator('#case-heading').inner_text()
        await page.go_back()
        await page.wait_for_url('**/work/duewatch')
        await idle(page)
        hist['back2'] = await page.locator('#case-heading').inner_text()
        await page.go_forward()
        await page.wait_for_url('**/work/brandwall')
        await idle(page)
        await page.go_forward()
        await page.wait_for_url('**/work/crosscheck')
        await idle(page)
        hist['forward2'] = await page.locator('#case-heading').inner_text()
        hist['curtainOpen'] = await page.locator('.curtain').get_attribute('data-state')
        await page.locator('.case-brief .case-back').click()
        await page.wait_for_url(URL + '/')
        await idle(page)
        hist['returnTop'] = round(await page.locator('#crosscheck').evaluate('e=>e.getBoundingClientRect().top'))
        hist['canvas'] = await page.evaluate("window.__canvas===document.querySelector('canvas')")
        await walk.shot(f'{walk.tag}h7-chain-return.png')
        walk.mark('end')
        # Direct URL + refresh for all five (tested, not filmed).
        hist['direct'] = {}
        for slug in IDS:
            await page.goto(URL + f'/work/{slug}')
            await page.locator('.silent-button').click(timeout=30000)
            await idle(page)
            first = await page.locator('#case-heading').inner_text()
            await page.reload()
            await page.locator('.silent-button').click(timeout=30000)
            await idle(page)
            hist['direct'][slug] = [first, await page.locator('#case-heading').inner_text(), await page.locator('.curtain').get_attribute('data-state'), round(await page.evaluate('scrollY'))]
        await walk.shot(f'{walk.tag}h8-direct-refresh.png')
        data['history'] = hist
    except Exception as error:  # noqa: BLE001
        traceback.print_exc()
        META['errors']['desktop' if wide else 'mobile'] = repr(error)
    await context.close()
    return await page.video.path(), walk, data


async def chrome(page, touch, walk):
    out = await page.evaluate("""()=>{const v=q=>{const e=document.querySelector(q);return !!e&&e.getClientRects().length>0};
      return {header:v('.site-header'),sound:v('.sound-toggle'),menu:v('.menu-toggle'),nav:v('.desktop-navigation'),readout:v('.progress-readout'),
        canvas:document.querySelectorAll('canvas').length,skills:!!document.getElementById('skills'),about:!!document.getElementById('about'),contact:!!document.getElementById('contact'),
        soundPressed:document.querySelector('.sound-toggle')?.getAttribute('aria-pressed')}}""")
    if walk and touch:
        await page.locator('.menu-toggle').tap()
        await page.wait_for_selector('.navigation-dialog[open]')
        await walk.shot('m08-menu.png')
        out['menuLinks'] = await page.locator('.navigation-dialog nav a, .navigation-dialog nav button').count()
        await page.keyboard.press('Escape')
        await settle(page, 300)
    if walk:
        for sec in ('skills', 'about', 'contact'):
            await at(page, f'#{sec}', -70)
            await walk.shot(f'{walk.tag}09-{sec}.png')
    return out


# ---------------------------------------------------------------- interruptions (not filmed)
async def interruptions(browser, wide):
    W, H = (1440, 900) if wide else (390, 844)
    opts = {'viewport': {'width': W, 'height': H}}
    if not wide:
        opts.update(device_scale_factor=2, is_mobile=True, has_touch=True)
    context = await browser.new_context(**opts)
    page = await context.new_page()
    sink = {'errors': [], 'bad': []}
    watch(page, sink)
    res = {'perProject': {}}
    try:
        await enter(page)
        for slug in IDS:
            r = res['perProject'][slug] = {}
            await q49.to_chapter(page, slug)
            # Rapid taps on the instrument: settles at one end, never stuck mid-turn.
            box = await page.locator(f'#{slug} .instrument-stage').bounding_box()
            for _ in range(5):
                await page.mouse.click(box['x'] + box['width'] * .5, box['y'] + box['height'] * .42)
                await page.wait_for_timeout(90)
            await page.wait_for_timeout(3600)
            r['rapidTapOrbit'] = await q49.orbit(page, slug)
            # Back while the curtain is still moving on the case (the URL changes behind the closed curtain;
            # Back before that would leave the site, which is the browser's own behaviour).
            y = await page.evaluate('scrollY')
            await page.locator(f'[data-open-case={slug}]').click()
            await page.wait_for_function(f"location.pathname==='/work/{slug}'&&document.querySelector('.curtain').dataset.state!=='open'", polling='raf')
            await page.go_back()
            await page.wait_for_timeout(2500)
            await idle(page)
            r['backMidCurtain'] = {'path': await page.evaluate('location.pathname'), 'curtain': await page.locator('.curtain').get_attribute('data-state'),
                                   'scrollDelta': abs(await page.evaluate('scrollY') - y)}
            await page.mouse.wheel(0, 300)
            await page.wait_for_timeout(500)
            r['backMidCurtain']['scrollFree'] = abs(await page.evaluate('scrollY') - y) > 150
            # Double Open in one frame: one case, one history entry.
            await q49.to_chapter(page, slug)
            await page.evaluate(f"(()=>{{const b=document.querySelector('[data-open-case={slug}]');b.click();b.click();}})()")
            await page.wait_for_url(f'**/work/{slug}')
            await idle(page)
            r['doubleOpen'] = {'path': await page.evaluate('location.pathname'), 'curtain': await page.locator('.curtain').get_attribute('data-state')}
            # One history entry: a single Back leaves the case for the homepage (history.length can't tell, the push drops the Forward entry).
            await page.go_back()
            await page.wait_for_url(URL + '/')
            await idle(page)
            r['doubleOpen']['oneBackHome'] = await page.evaluate('location.pathname') == '/'
            r['ok'] = (r['rapidTapOrbit'] in (0, 1) and r['backMidCurtain']['path'] == '/' and r['backMidCurtain']['curtain'] == 'open' and r['backMidCurtain']['scrollFree']
                       and r['doubleOpen']['path'] == f'/work/{slug}' and r['doubleOpen']['oneBackHome'] and r['doubleOpen']['curtain'] == 'open')
        # Double Next in one frame lands on the next case, not two ahead; scroll is locked while the curtain moves.
        await page.goto(URL + '/work/crosscheck')
        await page.locator('.silent-button').click(timeout=30000)
        await idle(page)
        await at(page, '.case-next')
        await page.evaluate("(()=>{const b=document.querySelector('.case-next .case-button');b.click();b.click();})()")
        await page.wait_for_function("document.querySelector('.curtain').dataset.state!=='open'")
        y = await page.evaluate('scrollY')
        await page.mouse.wheel(0, 400)
        await page.wait_for_timeout(120)
        locked = abs(await page.evaluate('scrollY') - y) < 2
        await page.wait_for_url('**/work/surgeline')
        await idle(page)
        await page.wait_for_timeout(800)
        res['doubleNext'] = {'path': await page.evaluate('location.pathname'), 'lockedDuringCurtain': locked, 'curtain': await page.locator('.curtain').get_attribute('data-state')}
        # Resize while on a case.
        sizes = [(1440, 900), (390, 844)] if not wide else [(390, 844), (1440, 900)]
        seen = []
        for w, h in sizes:
            await page.set_viewport_size({'width': w, 'height': h})
            await page.wait_for_timeout(700)
            seen.append({'size': [w, h], 'overflow': await overflow(page), 'heading': await page.locator('#case-heading').is_visible(),
                         'curtain': await page.locator('.curtain').get_attribute('data-state')})
        res['resize'] = seen
        await page.screenshot(path=str(OUT / f"{'d' if wide else 'm'}10-after-resize.png"))
    except Exception as error:  # noqa: BLE001
        traceback.print_exc()
        res['error'] = repr(error)
    res['errors'], res['bad'] = sink['errors'], sink['bad']
    await context.close()
    return res


async def fallback(browser):
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await page.route('**/models/ambient.glb', lambda route: route.abort())
    out = {}
    try:
        await enter(page, '/work/crosscheck')
        await page.wait_for_selector('.observatory[data-scene="fallback"]', state='attached', timeout=30000)
        for n, slug in enumerate(IDS):
            if n:
                await at(page, '.case-next')
                await page.locator('.case-next .case-button').click()
                await page.wait_for_url(f'**/work/{slug}')
                await idle(page)
            await at(page, '#case-instrument', 0)
            still = page.locator('.case-instrument-still')
            bg = await still.evaluate('e=>getComputedStyle(e).backgroundImage')
            await page.locator('.hotspot-0').click()
            card = await page.locator('#component-card h3').inner_text()
            await page.screenshot(path=str(OUT / f'f{n + 1}-fallback-{slug}.png'))
            await page.get_by_role('button', name='Close component card').click()
            out[slug] = {'still': await still.is_visible(), 'image': f'{slug}-fallback.png' in bg, 'label': await page.locator('.fallback-notice').is_visible(), 'card': card,
                         'ok': await still.is_visible() and f'{slug}-fallback.png' in bg and card == CASES[n]['cards'][0]}
    except Exception as error:  # noqa: BLE001
        traceback.print_exc()
        out['error'] = repr(error)
    await context.close()
    return out


async def chain_fps(browser, wide):
    """Frames during the five Next hops: phone 390×844 DPR 2 at 4× CPU (perf_quick rule), desktop 1440×900 unthrottled."""
    opts = {'viewport': {'width': 1440, 'height': 900}} if wide else {'viewport': {'width': 390, 'height': 844}, 'device_scale_factor': 2, 'is_mobile': True, 'has_touch': True}
    context = await browser.new_context(**opts)
    page = await context.new_page()
    out = {}
    try:
        await enter(page, '/work/crosscheck')
        if not wide:
            cdp = await context.new_cdp_session(page)
            await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
        await page.wait_for_timeout(1500)
        for n, slug in enumerate(IDS):
            nxt = IDS[(n + 1) % 5]
            await at(page, '.case-next')
            await page.wait_for_timeout(400)
            await page.evaluate(FRAMES)
            await page.locator('.case-next .case-button').click()
            await page.wait_for_url(f'**/work/{nxt}')
            await page.wait_for_function("document.querySelector('.curtain').dataset.state==='open'", timeout=10000)
            frames = await page.evaluate('window.__frames')
            out[f'{slug} → {nxt}'] = stats(frames)
            await idle(page)
        # Chapter scroll + turn on the homepage, the stretch the visitor spends longest in.
        await page.locator('.case-brief .case-back').click()
        await page.wait_for_url(URL + '/')
        await idle(page)
        await page.evaluate(FRAMES)
        for _ in range(24):
            await page.mouse.wheel(0, 160)
            await page.wait_for_timeout(60)
        out['homepage wheel scroll'] = stats(await page.evaluate('window.__frames'))
    except Exception as error:  # noqa: BLE001
        traceback.print_exc()
        out['error'] = repr(error)
    await context.close()
    return out


# ---------------------------------------------------------------- verdicts
def project_verdict(slug, m, d):
    rows = {}
    for dev, data in (('phone', m), ('desktop', d)):
        r = data.get('projects', {}).get(slug, {})
        c, e, ret, room_ = r.get('chapter', {}), r.get('entry', {}), r.get('return', {}), r.get('room', {})
        style = q49.CURTAINS[slug]
        rows[dev] = {
            'chapter': bool(c.get('ok')), 'entry': e.get('closed') == [style] and e.get('heading') == NAMES[slug] and e.get('scrollY', 9) < 2 and e.get('canvas') and e.get('lockedDuringCurtain') and e.get('dataChapter') == slug,
            'room': bool(room_.get('ok')), 'return': ret.get('closed') == [style] and ret.get('scrollDelta', 9) < 3 and ret.get('focus') is True and ret.get('lockedDuringCurtain'),
            'error': r.get('error')}
    ok = all(v for dev in rows.values() for k, v in dev.items() if k != 'error') and not any(dev['error'] for dev in rows.values())
    pm, pd = m.get('projects', {}).get(slug, {}), d.get('projects', {}).get(slug, {})
    detail = (f"phone {rows['phone']} | desktop {rows['desktop']}; curtain '{q49.CURTAINS[slug]}' closed→open in {pm.get('entry', {}).get('openMs')} ms phone / {pd.get('entry', {}).get('openMs')} ms desktop; "
              f"turn orbit phone {pm.get('chapter', {}).get('orbit')} (touch drag → tap {pm.get('chapter', {}).get('tapMs')} ms), strip change {pm.get('chapter', {}).get('stripDiff')} / {pd.get('chapter', {}).get('stripDiff')}; "
              f"scroll moved stage {pm.get('chapter', {}).get('scrollMoved')} px with orbit unchanged; room: {EXPLAINS[slug]} → phone {({k: v for k, v in pm.get('room', {}).items() if k != 'ok'})}; "
              f"return scroll ±{pm.get('return', {}).get('scrollDelta')} / ±{pd.get('return', {}).get('scrollDelta')} px, focus on Open case file {pm.get('return', {}).get('focus')} / {pd.get('return', {}).get('focus')}")
    n = IDS.index(slug) + 1
    check(slug, ok, detail, f'i0{n}-{slug}.png', devices=rows)
    return rows


def verdicts(m, d, im, idd, fb, fps):
    per = {s: project_verdict(s, m, d) for s in IDS}
    # Chain.
    def chain_ok(ch):
        return len(ch) == 5 and all(h['closed'] == [q49.CURTAINS[h['from']]] and h['destinationOpened'] and h['heading'] == NAMES[h['to']] and h['scrollY'] < 2 and h['canvas'] for h in ch)
    mc, dc = m.get('chain', []), d.get('chain', [])
    check('chain', chain_ok(mc) and chain_ok(dc),
          f"phone hops {[(h['from'], h['to'], h['closed'], h['openMs']) for h in mc]}; desktop {[(h['from'], h['to'], h['closed'], h['openMs']) for h in dc]}; "
          f"destination curtain opened phone {[h['destinationOpened'] for h in mc]} desktop {[h['destinationOpened'] for h in dc]}; scroll locked during every curtain {all(h['lockedDuringCurtain'] for h in mc + dc)}",
          'i06-chain.png')
    def hist_ok(h):
        return (h.get('back1') == 'BrandWall' and h.get('back2') == 'DueWatch' and h.get('forward2') == 'CrossCheck' and h.get('curtainOpen') == 'open' and abs(h.get('returnTop', 9)) < 3
                and h.get('canvas') and all(v[0] == v[1] == NAMES[k] and v[2] == 'open' and v[3] < 2 for k, v in h.get('direct', {}).items()) and len(h.get('direct', {})) == 5)
    mh, dh = m.get('history', {}), d.get('history', {})
    check('history', hist_ok(mh) and hist_ok(dh), f"phone {mh} | desktop {dh}", 'i07-history.png')
    def int_ok(r):
        dn = r.get('doubleNext', {})
        return (all(p.get('ok') for p in r.get('perProject', {}).values()) and len(r.get('perProject', {})) == 5 and dn.get('path') == '/work/surgeline' and dn.get('lockedDuringCurtain')
                and dn.get('curtain') == 'open' and all(s['overflow'] <= 1 and s['heading'] and s['curtain'] == 'open' for s in r.get('resize', [])) and not r.get('errors') and not r.get('bad') and not r.get('error'))
    check('interruptions', int_ok(im) and int_ok(idd),
          f"phone per project {{rapid-tap orbit, back mid-curtain, double open}}: {{{', '.join(f'{k}: {v.get('rapidTapOrbit')}/{v.get('backMidCurtain', {}).get('curtain')}/{v.get('doubleOpen', {}).get('oneBackHome')}' for k, v in im.get('perProject', {}).items())}}}; "
          f"double Next → {im.get('doubleNext')}; resize {im.get('resize')} | desktop per project ok {[v.get('ok') for v in idd.get('perProject', {}).values()]}, double Next {idd.get('doubleNext')}, resize {idd.get('resize')}; "
          f"errors {im.get('errors', []) + idd.get('errors', [])} {im.get('error', '')}{idd.get('error', '')}", 'i08-interruptions.png')
    # Distinct rooms: five curtain styles seen, five chapter illustrations, five room screenshots that differ.
    styles = [h['closed'][0] if h['closed'] else None for h in mc]
    hashes = {s: hashlib.md5((OUT / f'm{IDS.index(s) + 1}4-room-{s}.png').read_bytes()).hexdigest() if (OUT / f'm{IDS.index(s) + 1}4-room-{s}.png').exists() else None for s in IDS}
    strips = {s: m.get('projects', {}).get(s, {}).get('chapter', {}).get('stripDiff') for s in IDS}
    check('distinct', len(set(styles)) == 5 and len(set(h for h in hashes.values() if h)) == 5 and all(v and v > .2 for v in strips.values()),
          f"curtain styles in hop order {styles}; five room classes {list(ROOMS.values())}; room screenshots distinct {len(set(h for h in hashes.values() if h))}/5; "
          f"chapter illustrations {list(STRIPS.values())} each change with the turn (diff {strips}); explanations: {EXPLAINS}", 'i09-distinct.png')
    mcr, dcr = m.get('chrome', {}), d.get('chrome', {})
    def chrome_ok(c, wide):
        return all(c.get(k, {}).get('header') and c.get(k, {}).get('sound') and c.get(k, {}).get('canvas') == 1 and (c.get(k, {}).get('nav') if wide else c.get(k, {}).get('menu')) for k in ('home', 'case')) \
            and c.get('home', {}).get('skills') and c.get('home', {}).get('about') and c.get('home', {}).get('contact')
    check('observatory', chrome_ok(mcr, False) and chrome_ok(dcr, True) and mcr.get('home', {}).get('menuLinks', 0) >= 3,
          f"phone home {mcr.get('home')} case {mcr.get('case')} | desktop home {dcr.get('home')} case {dcr.get('case')}", 'i10-observatory.png')
    lay = {s: d.get('projects', {}).get(s, {}).get('chapter', {}).get('layout') for s in IDS}
    boxes = {s: d.get('projects', {}).get(s, {}).get('roomBox') for s in IDS}
    beside = {s: bool(l) and l['copy'][0] + l['copy'][2] <= l['stage'][0] + l['stage'][2] * .5 for s, l in lay.items()}
    check('desktopShowpiece', all(beside.values()) and all(b and b[1] >= 1440 * .6 for b in boxes.values()),
          f"chapter copy vs stage (x,y,w,h) {lay}; copy left of stage centre {beside}; case room [x, width] {boxes}", 'i11-desktop.png')
    # Development viewports + edges on this fingerprint.
    fp = rr.fingerprint()[0]
    ledger = json.loads((ROOT / 'assets/renders/regression-ledger.json').read_text())
    suites = ledger.get('suites', ledger)
    vp = {}
    for slug, suite in zip(IDS, ('room', 'dispatch', 'monitor', 'time', 'studio')):
        info = suites.get(suite, {})
        rep = json.loads((ROOT / info['report']).read_text()) if info.get('report') else {}
        rows = rep.get('results', [])
        vp[slug] = {'suite': suite, 'fingerprint': info.get('fingerprint') == fp, 'status': info.get('status'),
                    'viewports': [(r.get('viewport'), r.get('status', 'passed' if r.get('pass', True) else 'failed')) for r in rows],
                    'edges': rep.get('edges') if isinstance(rep.get('edges'), dict) else [(e.get('mode') or e.get('edge'), e.get('status')) for e in rep.get('edges', [])]}
    check('viewports', all(v['fingerprint'] and v['status'] == 'passed' and len(v['viewports']) == 6 for v in vp.values()),
          '; '.join(f"{s} ({v['suite']}): {v['status']} same-fingerprint={v['fingerprint']} {len(v['viewports'])} viewports, edges {v['edges']}" for s, v in vp.items()), 'i12-viewports.png', data=vp)
    check('fallback', all(fb.get(s, {}).get('ok') for s in IDS) and not fb.get('error'), f"{fb}", 'i13-fallback.png')
    # Performance.
    segs = {}
    for slug in IDS:
        rep = json.loads((ROOT / f'assets/renders/perf-quick/{slug}.json').read_text())
        segs[slug] = {'same': rep.get('fingerprint') == fp, 'status': rep['status'], 'segments': {k: (v['fps'], v['slowPct']) for k, v in rep['current']['segments'].items()}}
    dev_ok = all(v['same'] and v['status'] == 'passed' for v in segs.values())
    chain_meas = {dev: {k: v for k, v in r.items() if isinstance(v, dict)} for dev, r in fps.items()}
    chain_ok_ = all(v['fps'] >= 45 and v['slowPct'] <= 10 for r in chain_meas.values() for v in r.values()) and all(len(r) == 6 for r in chain_meas.values())
    check('performance', dev_ok and chain_ok_,
          f"perf_quick (phone 4× CPU): {segs} | chain here: " + '; '.join(f"{dev}: " + ', '.join(f"{k} {v['fps']} fps ({v['slowPct']}% slow)" for k, v in r.items()) for dev, r in chain_meas.items()),
          None, data={'perfQuick': segs, 'chain': chain_meas})
    return per, vp


def sources_check(m):
    ok_readings = trace_numbers()
    text = ' '.join(m.get('texts', []))
    # Claim words are allowed only inside a negation or in the reviewed, already-approved contexts below.
    reviewed = ('not claims of a production-ready system', 'The machine the jobs actually live on', 'Live footage comes from a separate', 'live sending is not demonstrated',
                'live dashboard')
    hits = [m.group(0) for m in re.finditer(r'.{0,60}\b(guaranteed|real-time|production-ready|bulletproof|affiliated|partner of|live)\b.{0,40}', text, re.I)]
    forbidden = [h for h in hits if not re.search(r'\bnot\b|\bno\b|aria-live', h, re.I) and not any(r.lower() in h.lower() for r in reviewed)]
    live = hits
    live_bad = forbidden
    drafts = m.get('drafts')
    check('sources', ok_readings and not forbidden and not live_bad and drafts == 0,
          f"case readings in dossiers={ok_readings} (verify_cases.trace_numbers, 20 values); DRAFT labels on homepage + five cases = {drafts}; forbidden {forbidden or 'none'}; "
          f"claim-word contexts reviewed {len(live)} (all negations or approved copy={not live_bad}); Upwork = owner's own contact link; new interface hint 'Drag or tap the instrument to turn it' (Q49) is interface copy awaiting owner approval", None)


async def page_texts(browser):
    context = await browser.new_context(viewport={'width': 1440, 'height': 900})
    page = await context.new_page()
    texts, drafts = [], 0
    await enter(page)
    texts.append(await page.locator('main').inner_text())
    drafts += await page.locator('.draft-label').count()
    for slug in IDS:
        await page.goto(URL + f'/work/{slug}')
        await page.locator('.silent-button').click(timeout=30000)
        await idle(page)
        texts.append(await page.locator('.case-page').evaluate('e=>e.textContent'))
        drafts += await page.locator('.draft-label').count()
    await context.close()
    return texts, drafts


def ledger_verdict():
    fp = rr.fingerprint()[0]
    ledger = json.loads((ROOT / 'assets/renders/regression-ledger.json').read_text())
    suites = ledger.get('suites', ledger)
    status = {k: (v.get('status'), v.get('fingerprint') == fp) for k, v in suites.items()}
    check('regressions', len(status) == 18 and all(s == 'passed' and same for s, same in status.values()), f"fingerprint {fp}: {status}", None)


# ---------------------------------------------------------------- sheets + films
def strip(names, path, size):
    present = [(n, label) for n, label in names if (OUT / n).exists()]
    if present:
        sheet = Image.new('RGB', (size[0] * len(present), size[1]), 'black')
        for i, (name, label) in enumerate(present):
            sheet.paste(tile(OUT / name, label, size), (i * size[0], 0))
        sheet.save(path)


def sheets():
    P, D = (390, 844), (720, 450)
    for n, slug in enumerate(IDS, 1):
        name = NAMES[slug]
        strip([(f'm{n}1-chapter-{slug}.png', f'{name} chapter'), (f'm{n}2-chapter-{slug}-turned.png', 'Turned (drag + tap)'), (f'm{n}3a-curtain-{slug}.png', f'Curtain · {q49.CURTAINS[slug]}'),
               (f'm{n}3b-brief-{slug}.png', 'Case brief'), (f'm{n}4-room-{slug}.png', 'Room'), (f'm{n}5-room-{slug}' + {'crosscheck': '-finding', 'surgeline': '-complete', 'driftwatch': '-healthy', 'duewatch': '-handoff', 'brandwall': '-after'}[slug] + '.png', 'Room result'),
               (f'm{n}7-return-{slug}.png', 'Return')], OUT / f'i0{n}-{slug}.png', P)
    strip([(f'mh{i}-hop-{a}-{b}.png', f'{NAMES[a]} → {NAMES[b]} · {q49.CURTAINS[b]} opens') for i, (a, b) in enumerate(zip(IDS, IDS[1:] + IDS[:1]), 1)], OUT / 'i06-chain.png', P)
    strip([('mh6-chain-closed.png', 'Chain closed at CrossCheck'), ('mh7-chain-return.png', 'Return from chain'), ('mh8-direct-refresh.png', 'Direct + refresh'),
           ('dh7-chain-return.png', 'Desktop return')], OUT / 'i07-history.png', P)
    strip([('m10-after-resize.png', 'Phone after resize'), ('d10-after-resize.png', 'Desktop after resize')], OUT / 'i08-interruptions.png', P)
    strip([(f'm{n}4-room-{s}.png', NAMES[s]) for n, s in enumerate(IDS, 1)], OUT / 'i09-distinct.png', P)
    strip([('m00-hero.png', 'Hero'), ('m08-menu.png', 'Menu'), ('m09-skills.png', 'Skills'), ('m09-about.png', 'About'), ('m09-contact.png', 'Contact')], OUT / 'i10-observatory.png', P)
    strip([(f'd{n}2-chapter-{s}-turned.png', f'{NAMES[s]} chapter') for n, s in enumerate(IDS, 1)], OUT / 'i11-desktop.png', D)
    strip([(f'f{n}-fallback-{s}.png', f'{NAMES[s]} blocked model') for n, s in enumerate(IDS, 1)], OUT / 'i13-fallback.png', P)
    # Six viewports per project, from the Development room suites (same fingerprint): chapter screenshots, one row per project.
    T = (240, 300)
    sizes = ('390x844', '360x740', '430x932', '768x1024', '1440x900', '1920x1080')
    grid = Image.new('RGB', (T[0] * 6, T[1] * 5), 'black')
    for r, slug in enumerate(IDS):
        for c, size in enumerate(sizes):
            src = ROOT / f'assets/renders/personal-{slug}/dev' / (f'chapter-scan-{size}.png' if slug == 'crosscheck' else f'chapter-{size}.png')
            if src.exists():
                grid.paste(tile(src, f'{NAMES[slug]} {size}', T), (c * T[0], r * T[1]))
    grid.save(OUT / 'i12-viewports.png')
    for prefix, name, T in (('m', 'contact-sheet-mobile.jpg', P), ('d', 'contact-sheet-desktop.jpg', D)):
        labeled = []
        for n, slug in enumerate(IDS, 1):
            labeled += [(f'{prefix}{n}2-chapter-{slug}-turned.png', f'{NAMES[slug]} · chapter'), (f'{prefix}{n}3a-curtain-{slug}.png', f'curtain {q49.CURTAINS[slug]}'),
                        (f'{prefix}{n}4-room-{slug}.png', 'room'), (f'{prefix}{n}7-return-{slug}.png', 'return')]
        present = [(x, lab) for x, lab in labeled if (OUT / x).exists()]
        cols = 4
        rows = (len(present) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * T[0], max(1, rows) * T[1]), 'black')
        for i, (x, lab) in enumerate(present):
            sheet.paste(tile(OUT / x, f'{i + 1:02d} {lab}', T), ((i % cols) * T[0], (i // cols) * T[1]))
        sheet.save(OUT / name, quality=82)


def films(mobile, desktop):
    videos = []
    clips = []
    for (raw, walk), name, width in (((mobile[0], mobile[1]), 'walkthrough-mobile.mp4', 390), ((desktop[0], desktop[1]), 'walkthrough-desktop.mp4', 1440)):
        marks = walk.marks
        cut = RAW / f'cut-{name}.webm'
        keep = (max(0, marks.get('start', 0) - .3), marks.get('end', 9999) + .8)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(raw), '-vf', f"trim={keep[0]:.2f}:{keep[1]:.2f},setpts=PTS-STARTPTS", '-an', str(cut)], check=True)
        encode(cut, OUT / name)
        videos.append(duration(OUT / name))
        for slug in IDS:
            if f'hop-{slug}' in marks:
                a = marks[f'hop-{slug}'] - keep[0]
                clips.append((OUT / name, a + .1, a + 2.4, f"{'Phone' if width == 390 else 'Desktop'} Next {NAMES[slug]} to {NAMES[IDS[(IDS.index(slug) + 1) % 5]]}", width))
    if clips:
        slow_motion(clips, OUT / 'slow-motion.mp4')
        videos.append(duration(OUT / 'slow-motion.mp4'))
    return videos


async def run():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        mobile = await walk_device(browser, False)
        desktop = await walk_device(browser, True)
        im = await interruptions(browser, False)
        idd = await interruptions(browser, True)
        fb = await fallback(browser)
        fps = {'phone 4× CPU': await chain_fps(browser, False), 'desktop': await chain_fps(browser, True)}
        texts, drafts = await page_texts(browser)
        await browser.close()
    m, d = mobile[2], desktop[2]
    m['texts'], m['drafts'] = texts, drafts
    errors = mobile[1].sink['errors'] + desktop[1].sink['errors']
    bad = mobile[1].sink['bad'] + desktop[1].sink['bad']
    overflow = mobile[1].overflows + desktop[1].overflows
    check('clean', not errors and not bad and max(overflow, default=0) <= 1 and not META['errors'],
          f"errors {errors}; ≥400 {bad}; max overflow {max(overflow, default=0)} px over {len(overflow)} shots; script errors {META['errors'] or 'none'}", None)
    per, vp = {}, {}
    try:
        per, vp = verdicts(m, d, im, idd, fb, fps)
        sources_check(m)
    except Exception as error:  # noqa: BLE001 — a verdict bug must not lose the recordings
        traceback.print_exc()
        META['errors']['verdicts'] = repr(error)
    ledger_verdict()
    videos = []
    try:
        videos = films(mobile, desktop)
    except Exception as error:  # noqa: BLE001
        traceback.print_exc()
        META['errors']['films'] = repr(error)
    shutil.rmtree(RAW, ignore_errors=True)
    sheets()
    categories = {c: {'pass': all(CHECKS.get(k, {}).get('pass') for k, (cats, _) in ITEMS.items() if c in cats),
                      'items': [k for k, (cats, _) in ITEMS.items() if c in cats]} for c in CATEGORIES}
    passed = all(CHECKS.get(k, {}).get('pass') for k in ITEMS)
    strip_m = lambda x: {k: v for k, v in x.items() if k not in ('texts',)}  # noqa: E731
    report = {
        'status': 'passed' if passed else 'failed',
        'phase': 'Phase 7F — Five rooms, one observatory',
        'stage': 'Testing (full round)',
        'finishedAt': datetime.now(timezone.utc).isoformat(),
        'fingerprint': rr.fingerprint()[0],
        'url': URL,
        'scope': 'Chromium GPU (ANGLE) emulation on the local production preview. Walkthroughs 390×844 DPR 2 touch + 1440×900 mouse wheel, recorded; '
                 'interruptions per project on both; blocked model per case 390×844; chain fps phone 4× CPU + desktop. 360/430/768/1920 + edges from the '
                 'Development room suites on the same fingerprint (Q42). Physical phone, Firefox/WebKit = Phase 8.',
        'categories': categories,
        'items': {k: {'label': label, 'categories': cats, **CHECKS.get(k, {'pass': False, 'detail': 'not executed'})} for k, (cats, label) in ITEMS.items()},
        'perProjectDevice': per,
        'measurements': {'mobile': strip_m(m), 'desktop': d, 'interruptions': {'phone': im, 'desktop': idd}, 'fallback': fb, 'chainFps': fps, 'viewports': vp,
                         'marks': {'mobile': mobile[1].marks, 'desktop': desktop[1].marks}},
        'videos': videos,
        'contactSheets': ['contact-sheet-mobile.jpg', 'contact-sheet-desktop.jpg'],
        'errors': META['errors'] or None,
    }
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + '\n')
    for key, item in report['items'].items():
        print(f"{'PASS' if item['pass'] else 'FAIL'} {key}: {item['detail'][:600]}")
    print('categories:', {c: v['pass'] for c, v in categories.items()})
    print('videos:', videos)
    return passed


async def redo_interruptions():
    """Re-run only the interruption checks into an existing pack of the same fingerprint (after a test-harness fix)."""
    path = OUT / 'evidence.json'
    report = json.loads(path.read_text())
    assert report['fingerprint'] == rr.fingerprint()[0], 'pack is from another source fingerprint; run the full pack'
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        im = await interruptions(browser, False)
        idd = await interruptions(browser, True)
        await browser.close()
    verdicts({}, {}, im, idd, {}, {})  # fills CHECKS; only the interruptions item is taken from it
    item = CHECKS['interruptions']
    report['items']['interruptions'] = {'label': ITEMS['interruptions'][1], 'categories': ITEMS['interruptions'][0], **item,
                                        'rerun': datetime.now(timezone.utc).isoformat() + ' (harness fix: double Open measured by one Back → homepage)'}
    report['measurements']['interruptions'] = {'phone': im, 'desktop': idd}
    report['categories'] = {c: {'pass': all(report['items'][k]['pass'] for k, (cats, _) in ITEMS.items() if c in cats),
                                'items': [k for k, (cats, _) in ITEMS.items() if c in cats]} for c in CATEGORIES}
    report['status'] = 'passed' if all(report['items'][k]['pass'] for k in ITEMS) else 'failed'
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + '\n')
    print(f"{'PASS' if item['pass'] else 'FAIL'} interruptions: {item['detail'][:900]}")
    print('status', report['status'], {c: v['pass'] for c, v in report['categories'].items()})
    return report['status'] == 'passed'


async def redo_fps():
    """Re-measure only the chain fps into an existing pack of the same fingerprint (after the recorder fix)."""
    path = OUT / 'evidence.json'
    report = json.loads(path.read_text())
    assert report['fingerprint'] == rr.fingerprint()[0], 'pack is from another source fingerprint; run the full pack'
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        fps = {'phone 4× CPU': await chain_fps(browser, False), 'desktop': await chain_fps(browser, True)}
        await browser.close()
    verdicts({}, {}, {}, {}, {}, fps)
    item = CHECKS['performance']
    report['items']['performance'] = {'label': ITEMS['performance'][1], 'categories': ITEMS['performance'][0], **item,
                                      'rerun': datetime.now(timezone.utc).isoformat() + ' (harness fix: stacked rAF recorders multiplied fps after the first hop)'}
    report['measurements']['chainFps'] = fps
    report['categories'] = {c: {'pass': all(report['items'][k]['pass'] for k, (cats, _) in ITEMS.items() if c in cats),
                                'items': [k for k, (cats, _) in ITEMS.items() if c in cats]} for c in CATEGORIES}
    report['status'] = 'passed' if all(report['items'][k]['pass'] for k in ITEMS) else 'failed'
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + '\n')
    print(f"{'PASS' if item['pass'] else 'FAIL'} performance: {item['detail'][-900:]}")
    print('status', report['status'])
    return report['status'] == 'passed'


if __name__ == '__main__':
    if '--redo-fps' in sys.argv:
        sys.exit(0 if asyncio.run(redo_fps()) else 1)
    if '--redo-interruptions' in sys.argv:
        sys.exit(0 if asyncio.run(redo_interruptions()) else 1)
    sys.exit(0 if asyncio.run(run()) else 1)
