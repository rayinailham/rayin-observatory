"""Phase 7B Testing evidence: SurgeLine dispatch room, mobile first then desktop.

Records two walkthroughs with real input (phone 390x844 touch swipes + taps, desktop 1440x900 mouse wheel + clicks):
chapter strip (three browsers, lane 2 cut → resumed) → antenna pulse into the case → hotspots → dispatch board
Start / Cut / Resume traced frame by frame (A never moves, B back in line and sent twice for one receipt, F five
attempts → dead-letter, no confirmed record drawn twice) → reverse scroll, Replay, rapid taps, Cut before the form →
recorded proof (processed ≠ confirmed) → DriftWatch teaser → pulse return → Next, Back/Forward, direct URL + refresh;
desktop adds layout measurements and resize during recovery. Cuts a 0.25x slow-motion reel. Q42: re-runs the
Development checks (verify_surgeline_room.viewport/edges) on six viewports into the pack, then model late/failed,
reduced motion, frame rate under 4x CPU, copy/number sources and the regression ledger.

Output: assets/renders/personal-surgeline/evidence/ — PNG per item, walkthrough-mobile.mp4, walkthrough-desktop.mp4,
slow-motion.mp4, contact sheets, evidence.json with pass/fail per item and per category.
Chromium GPU emulation on a laptop; no physical-phone claim (Phase 8).

Run from web/scripts with the production preview on :8767:
  timeout 2400 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python surgeline_room_evidence.py [--only mobile,desktop,back,slow,reduced,viewports,fps]
Exit 1 when any item fails.
"""
import asyncio
import json
import math
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402
from playwright.async_api import async_playwright  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crosscheck_room_evidence as cre  # noqa: E402
import run_regressions as rr  # noqa: E402
import verify_surgeline_room as vsr  # noqa: E402
from case_files_evidence import tile  # noqa: E402
from crosscheck_room_evidence import Walk, duration, encode, overflow, swipe_until, top_of, watch, wheel_until  # noqa: E402
from verify_crosscheck_room import enter, idle, land  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/personal-surgeline/evidence'
RAW = OUT / 'raw'
cre.OUT, cre.RAW = OUT, RAW  # shared helpers (Walk.shot, slow_motion) write into this pack
URL = vsr.URL
GPU = vsr.GPU
DOSSIER = ROOT / 'portfolio/CAPABILITY_SURGELINE.md'
SLOW_MS = 1000 / 45
FRAMES = "(() => { window.__frames = []; const f = t => { window.__frames.push(t); requestAnimationFrame(f); }; requestAnimationFrame(f); })();"

# Antenna pulse: three rings; scale/opacity of each ring and the pulse origin, every frame until 420 frames.
PULSE = """()=>{const w=window.__pulse=[];const t0=performance.now();const p=document.querySelector('.dispatch-pulse');
  const tick=()=>{const m=new DOMMatrix(getComputedStyle(p).transform);
    w.push({t:Math.round(performance.now()-t0),x:m.e,y:m.f,path:location.pathname,
      rings:[...p.querySelectorAll('i')].map(e=>{const s=getComputedStyle(e);return {o:Math.round(Number(s.opacity)*1000)/1000,s:Math.round(new DOMMatrix(s.transform).a*100)/100}})});
    if(w.length<420)requestAnimationFrame(tick)};requestAnimationFrame(tick)}"""
RING_OPACITY = "Math.max(...[...document.querySelectorAll('.dispatch-pulse i')].map(e=>Number(getComputedStyle(e).opacity)))"
# A frame worth a photo: some ring clearly visible and small enough to read as a ring around the antenna.
RING_READABLE = "[...document.querySelectorAll('.dispatch-pulse i')].some(e=>{const s=getComputedStyle(e);return Number(s.opacity)>.3&&new DOMMatrix(s.transform).a<5})"
# Board trace: every chip (board-relative position, state, sends, opacity) each frame until __traceStop.
TRACE = """()=>{const b=document.querySelector('.dispatch-board');const chips=[...b.querySelectorAll('[data-chip]')];
  window.__trace=[];window.__traceStop=false;const t0=performance.now();
  const tick=()=>{const f=b.getBoundingClientRect();
    window.__trace.push({t:Math.round(performance.now()-t0),stage:document.querySelector('.dispatch-room').dataset.stage,count:b.querySelectorAll('[data-chip]').length,
      chips:Object.fromEntries(chips.map(c=>{const r=c.getBoundingClientRect();return [c.dataset.chip,[Math.round((r.left-f.left)*10)/10,Math.round((r.top-f.top)*10)/10,c.dataset.state,c.dataset.sends,Number(getComputedStyle(c).opacity)]]}))});
    if(!window.__traceStop&&window.__trace.length<2000)requestAnimationFrame(tick)};requestAnimationFrame(tick)}"""
SLOTS = """()=>{const b=document.querySelector('.dispatch-board');const f=b.getBoundingClientRect();
  return {chip:parseFloat(getComputedStyle(b).getPropertyValue('--chip')),slots:Object.fromEntries([...b.querySelectorAll('[data-slot]')].map(s=>{const r=s.getBoundingClientRect();return [s.dataset.slot,[r.left-f.left,r.top-f.top]]}))}}"""
LEADERS = cre.LEADERS

CATEGORIES = ['story', 'visual', 'animation', 'transition', 'mobile', 'desktop', 'source', 'performance']
ITEMS = {
    'story': (['story'], 'Story reads saved list → browsers → crash → resume → receipts: chapter strip under the CTA; case order Brief → instrument → dispatch room → recorded proof → readings → Next; illustration and recorded run labelled apart; copy approved at gate 7B; no DRAFT labels'),
    'chapterStrip': (['animation', 'mobile', 'desktop'], 'Chapter: three browser lanes fill with the orbit (amber sent → green receipt); lane 2 freezes with "cut" mid-orbit, then "resumed" continues where it stopped; scrolling back reverses; phone swipe and desktop wheel'),
    'pulseEntry': (['transition'], 'Open case file: three amber rings expand from the antenna, the case opens, focus on the case heading (phone + desktop)'),
    'hotspots': (['story', 'visual'], 'Hotspots explain the work list, the parallel workers and the confirmation proof; leaders only while the model is on screen; card inside the viewport'),
    'dispatchDemo': (['story', 'animation', 'mobile', 'desktop'], 'Board by tap/click: Start (A confirmed, C shakes at the form → rejected, B waits for its receipt) → Cut (B frozen stranded, browser 2 offline, A/C keep outcomes) → Resume (claim expires, B back in line, sent again ×2 → confirmed; D/E confirmed; F ×1…×5 → dead-letter); board + button fit one phone view'),
    'noDuplicate': (['story', 'animation'], 'Resume never duplicates a result: A does not move or re-send, six chips on every frame, no two confirmed chips drawn on one place, confirmed count only rises to 4, ledger keeps one row per record; reverse scroll keeps outcomes, only Replay clears'),
    'processedVsConfirmed': (['story', 'visual', 'source'], 'Finished processing is not success: recorded 48,273 confirmed (green) apart from 844 rejected and 833 dead-letter (red), totals sum to 49,950; board bins and ledger separate the three outcomes with reasons'),
    'returnNext': (['transition'], 'Return: rings contract into the antenna and the chapter reopens on the saved scroll position with focus on Open case file; DriftWatch teaser, Next opens DriftWatch'),
    'historyDirect': (['transition'], 'Back/Forward between SurgeLine and DriftWatch, direct URL /work/surgeline and refresh keep the dispatch room working'),
    'interruptions': (['transition', 'animation'], 'Interruptions: double tap on Open case file adds one history entry; rapid taps on the dispatch button end on one outcome per record; Cut before B reaches the form freezes B mid-lane; Back during the pulse clears the rings; resize during recovery and across 1024 px settles every chip'),
    'modelSlowFail': (['visual', 'mobile'], 'Model not on screen yet: no leader during the pulse flight; scene failed (still view): no leaders, dispatch room still works'),
    'reducedMotion': (['animation'], 'Reduced motion: no rings, chips snap to each stage, recovery message readable then complete'),
    'mobileViewports': (['mobile'], 'All Development checks pass at 390×844, 360×740, 430×932 and tablet 768×1024'),
    'desktopComposition': (['desktop', 'visual'], 'Desktop 1440×900 / 1920×1080: steps in one row, one wide board left → right (saved list | lanes | bins), control beside a two-column ledger, recorded checkpoints beside outcomes'),
    'sources': (['source'], 'Every number and quoted fact on the page traces to the SurgeLine dossier; A–F records labelled fictional; 6M stated as an estimate never run'),
    'performance': (['performance', 'mobile'], 'PLAN §11 / Q42 under 4x CPU (phone swipe): chapter, pulse flight, crash/resume demo, case scroll and return hold ≥ 45 fps with ≤ 10% slow frames'),
    'clean': (['mobile', 'desktop'], 'One persistent Canvas, zero page errors, zero responses ≥ 400, no horizontal overflow in both walkthroughs'),
    'regressions': (['mobile', 'desktop'], 'Regression ledger (run_regressions.py): all 11 suites passed on this exact source fingerprint'),
}
CHECKS, META = {}, {}
# Owner accepted all Testing findings at gate 7B on 2026-09-17.
OWNER = [
    "Copy approved at gate 7B (2026-09-17): chapter strip, three hotspot bodies, dispatch room narration/labels/ledger, recorded proof and DriftWatch teaser. DRAFT labels removed.",
    "Accepted at gate 7B (2026-09-17): Cut is allowed before B reaches the form — B freezes mid-lane, dashed red, still \"stranded\", and Resume completes normally (m05b-cut-before-form.png, slow-motion clip 4). The owner accepted this behavior as is",
    "Motion changed by the Testing fix: the return pulse now contracts onto the antenna point the visitor left from (phone 185,382 / desktop 989,353). Before the fix the case page had scrolled the dish away and the rings closed at the top edge (desktop y 126)",
    "Refresh on /work/surgeline restarts the illustration at \"Start dispatch\" (outcomes are not persisted) — by design, it is a demonstration, not saved state",
    "Rig limits: headless Chromium on the laptop GPU, CPU throttled 4x; all five segments 56.6-60 fps with at most 3% slow frames. Physical phone = Phase 8",
]
ONLY = set(sys.argv[sys.argv.index('--only') + 1].split(',')) if '--only' in sys.argv else None


def check(key, ok, detail, shot, **extra):
    CHECKS[key] = {'pass': bool(ok), 'detail': detail, 'screenshot': shot, **extra}


def failed(key, error, shot=None):
    CHECKS[key] = {'pass': False, 'detail': f'not completed: {error}', 'screenshot': shot}


async def bottom(page):
    return await page.evaluate('document.documentElement.scrollHeight-innerHeight')


async def swipe_to(page, cdp, y, step=360, pause=.3, sample=None):
    await swipe_until(page, cdp, min(max(0, y), await bottom(page)), step=step, pause=pause, sample=sample)
    await land(page, min(max(0, y), await bottom(page)))


# ---------------------------------------------------------------- analysis helpers
async def pulse_collect(page, path, capture):
    if capture:
        for _ in range(80):
            if await page.evaluate(RING_READABLE):
                await page.screenshot(path=str(OUT / capture))
                break
            await page.wait_for_timeout(15)
    await page.wait_for_url(URL + path, timeout=15000)
    await idle(page)
    return await page.evaluate('window.__pulse')


def pulse_summary(trace, direction, width, height):
    vis = [f for f in trace if max(r['o'] for r in f['rings']) > .03]
    if len(vis) < 5:
        return {'ok': False, 'visibleFrames': len(vis)}
    lead = [f['rings'][0]['s'] for f in vis if f['rings'][0]['o'] > .03]
    grows = lead[-1] > lead[0] * 3 if direction == 'out' else lead[-1] * 3 < lead[0]
    inside = all(0 <= f['x'] <= width and 0 <= f['y'] <= height for f in vis)
    stagger = any(f['rings'][0]['s'] != f['rings'][2]['s'] for f in vis)
    cleared = all(r['o'] == 0 for r in trace[-1]['rings'])
    return {'ok': grows and inside and stagger and cleared, 'visibleFrames': len(vis), 'visibleMs': vis[-1]['t'] - vis[0]['t'],
            'scale': [lead[0], lead[-1]], 'origin': [round(vis[0]['x']), round(vis[0]['y'])], 'inside': inside, 'staggered': stagger, 'clearedAfter': cleared}


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def states_of(trace, chip):
    seq = []
    for f in trace:
        s = f['chips'][chip][2]
        if not seq or seq[-1] != s:
            seq.append(s)
    return seq


def analyse_start(trace, layout):
    slots, size = layout['slots'], layout['chip']
    last = trace[-1]['chips']
    c_form = [f['chips']['C'][0] for f in trace if dist(f['chips']['C'][:2], slots['lane-3-end']) < size * .6]
    turns = sum(1 for a, b, c in zip(c_form, c_form[1:], c_form[2:]) if (b - a) * (c - b) < 0)
    return {'frames': len(trace), 'A': states_of(trace, 'A'), 'C': states_of(trace, 'C'), 'B': states_of(trace, 'B'),
            'cShakeTurns': turns, 'bAtForm': dist(last['B'][:2], slots['lane-2-end']) < 1.5, 'bSends': last['B'][3],
            'ok': last['A'][2] == 'confirmed' and last['C'][2] == 'rejected' and last['B'][2] == 'sending' and last['B'][3] == '1'
            and turns >= 3 and dist(last['B'][:2], slots['lane-2-end']) < 1.5 and 'sending' in states_of(trace, 'C')}


def analyse_resume(trace, layout):
    slots, size = layout['slots'], layout['chip']
    a0 = trace[0]['chips']['A']
    a_moved = max(max(abs(f['chips']['A'][0] - a0[0]), abs(f['chips']['A'][1] - a0[1])) for f in trace)
    a_sends = {f['chips']['A'][3] for f in trace}
    counts = {f['count'] for f in trace}
    confirmed = [sum(1 for c in f['chips'].values() if c[2] == 'confirmed') for f in trace]
    rising = all(b >= a for a, b in zip(confirmed, confirmed[1:]))
    overlaps = []
    for f in trace:
        ok = [(k, c) for k, c in f['chips'].items() if c[2] == 'confirmed']
        for i, (k1, c1) in enumerate(ok):
            for k2, c2 in ok[i + 1:]:
                if dist(c1[:2], c2[:2]) < size * .5:
                    overlaps.append((f['t'], k1, k2))
    final = trace[-1]['chips']
    rest = [(k1, k2) for i, (k1, c1) in enumerate(final.items()) for k2, c2 in list(final.items())[i + 1:] if dist(c1[:2], c2[:2]) < size * .5]
    reconfirmed = [k for k in final if states_of(trace, k).count('confirmed') > 1]
    b_back = min(dist(f['chips']['B'][:2], slots['queue-1']) for f in trace)  # one frame may already start the next leg
    f_sends = sorted({f['chips']['F'][3] for f in trace})
    b_sends = [s for s in dict.fromkeys(f['chips']['B'][3] for f in trace)]
    ok = (a_moved < .5 and a_sends == {'1'} and counts == {6} and rising and confirmed[-1] == 4 and not overlaps and not rest and not reconfirmed
          and b_back < size * .35 and {'1', '2', '3', '4', '5'} <= set(f_sends) and final['F'][2] == 'dead-letter' and final['B'][2:4] == ['confirmed', '2']
          and final['D'][2] == 'confirmed' and final['E'][2] == 'confirmed' and final['C'][2] == 'rejected')
    return {'ok': ok, 'frames': len(trace), 'ms': trace[-1]['t'], 'aMovedPx': a_moved, 'aSends': sorted(a_sends), 'chipCounts': sorted(counts),
            'confirmedRange': [confirmed[0], confirmed[-1]], 'confirmedOnlyRises': rising, 'confirmedOverlapFrames': len(overlaps),
            'restingOverlaps': rest, 'reconfirmed': reconfirmed, 'bBackInLinePx': round(b_back, 2), 'bSends': b_sends, 'fSends': f_sends,
            'final': {k: v[2:4] for k, v in final.items()}, 'B': states_of(trace, 'B'), 'F': states_of(trace, 'F')}


async def trace_start(page):
    layout = await page.evaluate(SLOTS)
    await page.evaluate(TRACE)
    return layout


async def trace_stop(page):
    await page.evaluate('window.__traceStop=true')
    await page.wait_for_timeout(50)
    return await page.evaluate('window.__trace')


async def ledger(page):
    return await page.locator('[data-record]').evaluate_all("els=>els.map(e=>[e.dataset.record,e.dataset.status,e.querySelector('small').textContent])")


async def press(page, action, tap):
    button = page.locator(f'[data-dispatch-action={action}]')
    await (button.tap() if tap else button.click())


async def chapter_strip(page, samples):
    reading = await page.evaluate(vsr.STRIP)
    samples.append({k: round(v, 3) for k, v in reading.items()})


def strip_summary(forward, backward):
    fwd = sorted(forward, key=lambda r: r['orbit'])
    grows = all(b['s0'] >= a['s0'] - .01 for a, b in zip(fwd, fwd[1:]))
    cut = [r for r in fwd if .39 <= r['orbit'] <= .56]
    frozen = len({round(r['s1'], 2) for r in cut}) == 1 if cut else False
    end = fwd[-1]
    back = backward[-1] if backward else None
    return {'ok': grows and bool(cut) and frozen and all(r['cut'] > .9 and r['resumed'] == 0 for r in cut)
            and end['s0last'] == 1 and end['s1last'] == 1 and end['s2last'] == 1 and end['resumed'] == 1 and end['cut'] == 0
            and back is not None and back['s0'] < end['s0'] and back['resumed'] == 0,
            'samples': len(fwd), 'cutSamples': len(cut), 'lane2FrozenAt': cut[0]['s1'] if cut else None, 'lane1Across': [cut[0]['s0'], cut[-1]['s0']] if cut else None,
            'end': end, 'back': back}


# ---------------------------------------------------------------- the board, shared by both walkthroughs
async def board_run(page, walk, prefix, tap, wide):
    """Start → Cut → Resume with frame traces; returns measurements. Screenshots at every stage."""
    data = {}
    await land(page, await top_of(page, '.dispatch-board') - (250 if wide else 100))
    await vsr.settled(page, 'ready')
    board = await page.locator('.dispatch-board').bounding_box()
    button = await page.locator('.dispatch-control .case-button').bounding_box()
    data['fitsOneView'] = board['y'] >= 0 and button['y'] + button['height'] <= page.viewport_size['height']
    await walk.shot(f'{prefix}-board-ready.png')
    walk.mark('start')
    layout = await trace_start(page)
    await press(page, 'start', tap)
    await vsr.state(page, 'sending')
    await page.wait_for_timeout(650)
    await walk.shot(f'{prefix}-board-in-flight.png')
    await vsr.settled(page, 'sending')
    await page.wait_for_timeout(300)
    data['start'] = analyse_start(await trace_stop(page), layout)
    data['start']['bRing'] = await page.locator('[data-chip=B]').evaluate("e=>getComputedStyle(e,'::before').animationName")
    await walk.shot(f'{prefix}-board-sending.png')
    before = await page.evaluate(vsr.POSE)
    walk.mark('cut')
    await press(page, 'crash', tap)
    await vsr.state(page, 'crashed')
    await vsr.settled(page, 'crashed')
    frozen = (await page.evaluate(vsr.POSE))['B']
    await page.wait_for_timeout(700)
    after = await page.evaluate(vsr.POSE)
    data['cut'] = {'bFrozen': after['B'] == frozen, 'bState': after['B']['state'], 'aKept': after['A'] == before['A'], 'cKept': after['C'] == before['C'],
                   'lane2': await page.locator('.board-lane[data-lane="2"]').get_attribute('data-status'),
                   'lane2Colour': await page.locator('.board-lane[data-lane="2"] .board-label span').evaluate('e=>getComputedStyle(e).color'),
                   'ledgerB': await page.locator('[data-record=B]').get_attribute('data-status'),
                   'narration': await page.locator('.dispatch-control h3').inner_text()}
    await walk.shot(f'{prefix}-board-crashed.png')
    ledger_a = await page.locator('[data-record=A]').inner_text()
    walk.mark('resume')
    layout = await trace_start(page)
    await press(page, 'resume', tap)
    await vsr.state(page, 'resuming')
    data['resumeButtonDisabled'] = await page.locator('.dispatch-control .case-button').is_disabled()
    await page.wait_for_timeout(1150)
    await walk.shot(f'{prefix}-board-resuming-b-back.png')
    await page.wait_for_timeout(1250)
    await walk.shot(f'{prefix}-board-resuming-f-retries.png')
    await vsr.state(page, 'complete')
    await vsr.settled(page, 'complete')
    data['resume'] = analyse_resume(await trace_stop(page), layout)
    walk.mark('resumeEnd')
    await walk.shot(f'{prefix}-board-complete.png')
    data['ledger'] = await ledger(page)
    data['ledgerAKept'] = await page.locator('[data-record=A]').inner_text() == ledger_a
    data['confirmedCount'] = await page.locator('[data-confirmed-count]').inner_text()
    await page.wait_for_timeout(300)  # chip colours transition for 0.2 s after the last landing
    data['colours'] = await page.evaluate("""()=>{const c=id=>getComputedStyle(document.querySelector(`[data-chip="${id}"]`)).borderTopColor;
      const bin=b=>getComputedStyle(document.querySelector(`[data-bin="${b}"] .board-label`)).color;
      return {A:c('A'),B:c('B'),D:c('D'),C:c('C'),F:c('F'),ok:bin('ok'),rejected:bin('rejected'),dead:bin('dead')}}""")
    await land(page, await top_of(page, '.dispatch-control' if wide else '.dispatch-ledger') - (40 if wide else 60))
    await walk.shot(f'{prefix}-ledger.png')
    return data


# ---------------------------------------------------------------- phone walkthrough (recorded)
async def mobile_walk(browser):
    W, H = 390, 844
    context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True, has_touch=True,
                                        record_video_dir=str(RAW / 'mobile'), record_video_size={'width': W, 'height': H})
    page = await context.new_page()
    walk = Walk(page, 'm')
    cdp = await context.new_cdp_session(page)
    data = {}
    try:
        await enter(page)
        await page.evaluate("window.__canvas=document.querySelector('canvas')")
        # 1. Chapter strip: swipe through the orbit, then back.
        section = await page.locator('#surgeline').evaluate("e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight,stage:e.querySelector('.instrument-stage').offsetHeight})")
        span = section['h'] - section['stage']
        await swipe_to(page, cdp, section['top'] - 60)
        await page.wait_for_timeout(500)
        walk.mark('chapter')
        forward, backward = [], []
        await chapter_strip(page, forward)
        await swipe_to(page, cdp, section['top'] + span, step=100, pause=.45, sample=lambda: chapter_strip(page, forward))
        await page.wait_for_timeout(500)
        await chapter_strip(page, forward)
        await walk.shot('m01c-chapter-resumed.png')
        await swipe_until(page, cdp, section['top'] + .2 * span, step=180, pause=.45, sample=lambda: chapter_strip(page, backward))
        await land(page, section['top'] + .2 * span)
        await page.wait_for_timeout(400)
        await chapter_strip(page, backward)
        await walk.shot('m01a-chapter-sending.png')
        await land(page, section['top'] + .48 * span)
        await page.wait_for_timeout(400)
        await walk.shot('m01b-chapter-cut.png')
        data['strip'] = strip_summary(forward, backward)
        data['strip']['raw'] = {'forward': forward, 'backward': backward}
        strip = await page.locator('.dispatch-chapter').bounding_box()
        cta = await page.locator('[data-open-case=surgeline]').bounding_box()
        data['stripBelowCta'] = strip['y'] >= cta['y'] + cta['height']
        data['stripDraft'] = 'DRAFT' in await page.locator('.dispatch-chapter small').inner_text()
        origin = await page.evaluate('scrollY')

        # 2. Pulse into the case.
        walk.mark('entry')
        await page.evaluate(PULSE)
        await page.locator('[data-open-case=surgeline]').tap()
        trace = await pulse_collect(page, '/work/surgeline', 'm02a-pulse-out.png')
        walk.mark('entryEnd')
        data['pulseIn'] = {**pulse_summary(trace, 'out', W, H), 'focus': await page.evaluate('document.activeElement.id')}
        await walk.shot('m02b-case-opened.png')
        data['story'] = await page.evaluate("""(()=>{const q=s=>document.querySelector(s);
          const order=['#case-heading','#case-instrument','.dispatch-room','.dispatch-evidence','#readings-heading','.case-next'].map(s=>q(s)?q(s).getBoundingClientRect().top+scrollY:null);
          return {order, draft:[...document.querySelectorAll('.draft-label')].map(e=>e.textContent), text:q('main').textContent,
            disclosure:q('.dispatch-disclosure').textContent, source:q('.dispatch-source').textContent,
            labels:[...q('main').querySelectorAll('[aria-label]')].map(e=>e.getAttribute('aria-label')).join('\\n')}})()""")

        # 3. Hotspots.
        await swipe_to(page, cdp, await top_of(page, '#case-instrument'))
        await page.wait_for_selector('.case-inspection[data-leaders=live]', timeout=12000)
        cards = []
        for i in range(3):
            await page.locator(f'.hotspot-{i}').tap()
            await page.wait_for_timeout(700)
            box = await page.locator('#component-card').bounding_box()
            cards.append({'title': await page.locator('#component-card h3').first.inner_text(), 'body': await page.locator('#component-card').inner_text(),
                          'inside': box['y'] >= 0 and box['y'] + box['height'] <= H + 1,
                          'leader': await page.locator('[data-hotspot-line]').nth(i).evaluate('e=>Number(getComputedStyle(e).opacity)')})
            await walk.shot(f'm03-hotspot-0{i + 1}.png')
        await page.get_by_role('button', name='Close component card').tap()
        data['hotspots'] = cards

        # 4. Dispatch board by touch.
        await swipe_to(page, cdp, await top_of(page, '.dispatch-board') - 100)
        data['board'] = await board_run(page, walk, 'm04', True, False)

        # 5. Reverse scroll keeps outcomes; only Replay clears.
        walk.mark('reverse')
        await swipe_to(page, cdp, await top_of(page, '.dispatch-intro') - 80, step=300)
        await page.wait_for_timeout(300)
        await swipe_to(page, cdp, await top_of(page, '.dispatch-board') - 100, step=300)
        await vsr.settled(page, 'complete')
        data['afterScrollBack'] = {'confirmed': await page.locator('.dispatch-ledger [data-status=confirmed]').count(), 'stage': await page.locator('.dispatch-room').get_attribute('data-stage')}
        await walk.shot('m04i-after-scroll-back.png')
        walk.mark('reverseEnd')
        await press(page, 'reset', True)
        await vsr.state(page, 'ready')
        await vsr.settled(page, 'ready')
        data['replay'] = {'queued': await page.locator('.dispatch-ledger [data-status=queued]').count(), 'chips': await page.locator('[data-chip]').count()}
        await walk.shot('m04j-replay.png')

        # 6. Cut before B reaches the form (open design question), then rapid taps.
        walk.mark('rapid')
        slots = await page.evaluate(SLOTS)
        await press(page, 'start', True)
        await page.wait_for_timeout(760)  # B has left the list and is on lane 2, before the form
        await press(page, 'crash', True)
        await vsr.state(page, 'crashed')
        await vsr.settled(page, 'crashed', only='AC')
        early = await page.evaluate(vsr.POSE)
        frame = await page.locator('.dispatch-board').bounding_box()
        bx = early['B']['x'] - frame['x']
        await page.wait_for_timeout(500)
        data['cutEarly'] = {'bState': early['B']['state'], 'bX': round(bx, 1), 'laneStart': round(slots['slots']['lane-2-start'][0], 1), 'laneEnd': round(slots['slots']['lane-2-end'][0], 1),
                            'bStill': (await page.evaluate(vsr.POSE))['B'] == early['B']}
        await walk.shot('m05b-cut-before-form.png')
        await press(page, 'resume', True)
        await vsr.state(page, 'complete')
        await vsr.settled(page, 'complete')
        data['cutEarly']['completed'] = await page.locator('.dispatch-ledger [data-status=confirmed]').count() == 4
        await press(page, 'reset', True)
        await vsr.state(page, 'ready')
        await vsr.settled(page, 'ready')
        button = page.locator('.dispatch-control .case-button')
        for _ in range(7):
            try:
                await button.tap(timeout=300)
            except Exception:  # noqa: BLE001 — disabled while recovering, which is the point
                pass
            await page.wait_for_timeout(35)
        await vsr.state(page, 'complete')
        await vsr.settled(page, 'complete')
        data['rapid'] = {'stage': await page.locator('.dispatch-room').get_attribute('data-stage'), 'chips': await page.locator('[data-chip]').count(),
                         'ledger': await ledger(page)}
        await walk.shot('m05a-rapid-taps-settled.png')
        walk.mark('rapidEnd')

        # 7. Recorded proof, readings.
        await swipe_to(page, cdp, await top_of(page, '.dispatch-evidence') - 20)
        await walk.shot('m06a-evidence.png')
        await swipe_to(page, cdp, await top_of(page, '.dispatch-outcomes') - 60)
        await walk.shot('m06c-outcomes.png')
        data['evidence'] = await page.evaluate("""(()=>{const q=s=>document.querySelector(s);const col=s=>getComputedStyle(q(s)).color;
          return {heading:q('#dispatch-evidence-heading').textContent,totals:[...document.querySelectorAll('[data-outcome] > strong')].map(e=>e.textContent),
            ok:col('[data-outcome=confirmed] > strong'),rejected:col('[data-outcome=rejected] > strong'),dead:col('[data-outcome=dead-letter] > strong'),
            text:q('.dispatch-evidence').textContent}})()""")
        await swipe_to(page, cdp, await top_of(page, '#readings-heading') - 80)
        await page.wait_for_timeout(1200)
        await walk.shot('m06b-readings.png')

        # 8. Next teaser → Return through the pulse.
        await swipe_to(page, cdp, await top_of(page, '#next-heading') - 200)
        await page.wait_for_timeout(300)
        await walk.shot('m07-next-teaser.png')
        data['teaser'] = await page.locator('.dispatch-next').inner_text()
        walk.mark('return')
        await page.evaluate(PULSE)
        await page.locator('.case-next .case-back').tap()
        trace = await pulse_collect(page, '/', 'm08a-pulse-return.png')
        walk.mark('returnEnd')
        await page.wait_for_timeout(300)
        await walk.shot('m08b-back-at-chapter.png')
        data['return'] = {**pulse_summary(trace, 'in', W, H), 'scrollDelta': abs(await page.evaluate('scrollY') - origin),
                          'focus': await page.evaluate("document.activeElement.dataset.openCase || document.activeElement.id || document.activeElement.tagName")}

        # 9. Double tap Open case file, Next hop, Back/Forward.
        before = await page.evaluate('history.length')
        walk.mark('doubleTap')
        await page.locator('[data-open-case=surgeline]').tap()
        await page.wait_for_timeout(90)
        try:
            await page.locator('[data-open-case=surgeline]').tap(timeout=600)
            second = 'tapped'
        except Exception:  # noqa: BLE001 — homepage already locked during the flight, also correct
            second = 'not tappable during flight'
        await page.wait_for_url(URL + '/work/surgeline')
        await idle(page)
        data['doubleTap'] = {'historyDelta': await page.evaluate('history.length') - before, 'second': second}
        await swipe_to(page, cdp, await top_of(page, '.case-next') - 120)
        walk.mark('next')
        await page.locator('.case-next .case-button').tap()
        await page.wait_for_url(URL + '/work/driftwatch', timeout=15000)
        await idle(page)
        await walk.shot('m09-next-driftwatch.png')
        await page.go_back()
        await page.wait_for_url(URL + '/work/surgeline')
        await idle(page)
        await page.wait_for_timeout(500)
        back_ok = await page.locator('main').get_attribute('data-case') == 'surgeline' and await page.locator('.dispatch-board').count() == 1
        await land(page, await top_of(page, '.dispatch-board') - 100)
        await vsr.settled(page, 'ready')
        await press(page, 'start', True)
        await vsr.settled(page, 'sending')
        await walk.shot('m09b-history-back-surgeline.png')
        await page.go_forward()
        await page.wait_for_url(URL + '/work/driftwatch')
        await idle(page)
        data['history'] = {'backOk': back_ok, 'backBoardWorks': True, 'forwardOk': await page.locator('main').get_attribute('data-case') == 'driftwatch',
                           'canvas': await page.evaluate("document.querySelector('canvas')===window.__canvas && document.querySelectorAll('canvas').length===1")}
        walk.mark('end')
        raw = await page.video.path()
    finally:
        await context.close()

    # Direct URL + refresh (not recorded).
    context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    sink = {'errors': [], 'bad': []}
    watch(page, sink)
    await enter(page, '/work/surgeline')
    await land(page, await top_of(page, '.dispatch-board') - 100)
    for action in ('start', 'crash', 'resume'):
        await press(page, action, True)
        await page.wait_for_timeout(250)
    await vsr.state(page, 'complete')
    await vsr.settled(page, 'complete')
    direct = await page.locator('.dispatch-ledger [data-status=confirmed]').count()
    await page.reload()
    await page.locator('.silent-button').click(timeout=30000)
    await idle(page)
    await land(page, await top_of(page, '.dispatch-board') - 100)
    await vsr.settled(page, 'ready')
    refreshed_stage = await page.locator('.dispatch-room').get_attribute('data-stage')
    for action in ('start', 'crash', 'resume'):
        await press(page, action, True)
        await page.wait_for_timeout(250)
    await vsr.state(page, 'complete')
    await vsr.settled(page, 'complete')
    await page.screenshot(path=str(OUT / 'm10-direct-refresh.png'))
    data['direct'] = {'directConfirmed': direct, 'refreshedStage': refreshed_stage, 'refreshedConfirmed': await page.locator('.dispatch-ledger [data-status=confirmed]').count(),
                      'errors': sink['errors'], 'bad': sink['bad']}
    await context.close()
    return raw, walk, data


# ---------------------------------------------------------------- desktop walkthrough (recorded)
async def desktop_walk(browser):
    W, H = 1440, 900
    context = await browser.new_context(viewport={'width': W, 'height': H}, record_video_dir=str(RAW / 'desktop'), record_video_size={'width': W, 'height': H})
    page = await context.new_page()
    walk = Walk(page, 'd')
    data = {}
    try:
        await enter(page)
        await page.mouse.move(W * .7, H * .5)
        await page.evaluate("window.__canvas=document.querySelector('canvas')")
        section = await page.locator('#surgeline').evaluate("e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight,stage:e.querySelector('.instrument-stage').offsetHeight})")
        span = section['h'] - section['stage']
        await wheel_until(page, section['top'] - 60)
        walk.mark('chapter')
        forward, backward = [], []
        await wheel_until(page, section['top'] + span, step=80, pause=70, sample=lambda: chapter_strip(page, forward), every=2)
        await land(page, section['top'] + span)
        await page.wait_for_timeout(400)
        await chapter_strip(page, forward)
        await wheel_until(page, section['top'] + .48 * span, step=80, pause=70, sample=lambda: chapter_strip(page, backward), every=2)
        await land(page, section['top'] + .48 * span)
        await page.wait_for_timeout(400)
        await chapter_strip(page, backward)
        await walk.shot('d01-chapter-cut.png')
        data['strip'] = strip_summary(forward, backward)
        origin = await page.evaluate('scrollY')
        walk.mark('entry')
        await page.evaluate(PULSE)
        await page.locator('[data-open-case=surgeline]').click()
        trace = await pulse_collect(page, '/work/surgeline', 'd02a-pulse-out.png')
        walk.mark('entryEnd')
        data['pulseIn'] = {**pulse_summary(trace, 'out', W, H), 'focus': await page.evaluate('document.activeElement.id')}
        await wheel_until(page, await top_of(page, '#case-instrument'))
        await land(page, await top_of(page, '#case-instrument'))
        await page.wait_for_selector('.case-inspection[data-leaders=live]', timeout=12000)
        await page.locator('.hotspot-1').click()
        await page.wait_for_timeout(700)
        await walk.shot('d03-hotspot-workers.png')
        await page.get_by_role('button', name='Close component card').click()
        await wheel_until(page, await top_of(page, '.dispatch-room') - 80)
        await land(page, await top_of(page, '.dispatch-room') - 80)
        await walk.shot('d04-room-intro-steps.png')
        data['layout'] = await page.evaluate("""(()=>{const r=s=>document.querySelector(s).getBoundingClientRect();
          const steps=[...document.querySelectorAll('.dispatch-steps li')].map(e=>Math.round(e.getBoundingClientRect().top));
          const rows=new Set([...document.querySelectorAll('.dispatch-ledger li')].map(e=>Math.round(e.getBoundingClientRect().left)));
          return {steps, queueRight:r('.board-queue').right, lanesLeft:r('.board-lanes').left, lanesRight:r('.board-lanes').right, binsLeft:r('.board-bins').left,
            controlRight:r('.dispatch-control').right, ledgerLeft:r('.dispatch-ledger').left, controlTop:Math.round(r('.dispatch-control').top), ledgerTop:Math.round(r('.dispatch-ledger').top),
            ledgerColumns:rows.size, boardWidth:r('.dispatch-board').width, chip:parseFloat(getComputedStyle(document.querySelector('.dispatch-board')).getPropertyValue('--chip'))}})()""")
        data['board'] = await board_run(page, walk, 'd05', False, True)
        await wheel_until(page, await top_of(page, '.dispatch-evidence') - 60)
        await land(page, await top_of(page, '.dispatch-proof-grid') - 200)
        await walk.shot('d06-evidence.png')
        data['proofLayout'] = await page.evaluate("(()=>{const r=s=>document.querySelector(s).getBoundingClientRect();return {checkpointsRight:r('.dispatch-checkpoints').right,outcomesLeft:r('.dispatch-outcomes').left}})()")
        await wheel_until(page, await top_of(page, '#next-heading') - 250)
        await land(page, await top_of(page, '#next-heading') - 250)
        await walk.shot('d07-next-teaser.png')
        walk.mark('return')
        await page.evaluate(PULSE)
        await page.locator('.case-next .case-back').click()
        trace = await pulse_collect(page, '/', 'd08a-pulse-return.png')
        walk.mark('returnEnd')
        await walk.shot('d08b-back-at-chapter.png')
        data['return'] = {**pulse_summary(trace, 'in', W, H), 'scrollDelta': abs(await page.evaluate('scrollY') - origin)}

        # Resize in the middle of recovery (desktop → phone), then across 1024 px at rest.
        await page.locator('[data-open-case=surgeline]').click()
        await page.wait_for_url(URL + '/work/surgeline')
        await idle(page)
        await land(page, await top_of(page, '.dispatch-board') - 250)
        for action in ('start', 'crash'):
            await press(page, action, False)
            await page.wait_for_timeout(500)
        walk.mark('resize')
        await press(page, 'resume', False)
        await page.wait_for_timeout(900)
        await page.set_viewport_size({'width': 390, 'height': 844})
        await vsr.state(page, 'complete')
        await vsr.settled(page, 'complete')
        await land(page, await top_of(page, '.dispatch-board') - 100)
        await page.screenshot(path=str(OUT / 'd09a-resized-mid-resume-390.png'))
        resized = [{'size': '390x844', 'overflow': await overflow(page), 'chips': await page.locator('[data-chip]').count(),
                    'confirmed': await page.locator('.dispatch-ledger [data-status=confirmed]').count()}]
        for w, h in ((1024, 900), (900, 900), (1920, 1080), (1440, 900)):
            await page.set_viewport_size({'width': w, 'height': h})
            await page.wait_for_timeout(700)
            await vsr.settled(page, 'complete')
            resized.append({'size': f'{w}x{h}', 'overflow': await overflow(page), 'chips': await page.locator('[data-chip]').count(),
                            'confirmed': await page.locator('.dispatch-ledger [data-status=confirmed]').count()})
        await land(page, await top_of(page, '.dispatch-board') - 250)
        await page.screenshot(path=str(OUT / 'd09b-resized-back-1440.png'))
        walk.mark('resizeEnd')
        data['resize'] = {'after': resized, 'canvas': await page.evaluate("document.querySelector('canvas')===window.__canvas && document.querySelectorAll('canvas').length===1")}
        raw = await page.video.path()
    finally:
        await context.close()
    return raw, walk, data


# ---------------------------------------------------------------- edges
async def back_during_flight(browser):
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await enter(page)
    await land(page, await page.locator('#surgeline').evaluate('e=>e.getBoundingClientRect().top+scrollY+300'))
    await page.locator('[data-open-case=surgeline]').tap()
    await page.wait_for_url(URL + '/work/surgeline', timeout=5000)
    await page.go_back()
    await page.wait_for_url(URL + '/')
    await idle(page)
    await page.wait_for_timeout(300)
    (OUT / 'edges').mkdir(exist_ok=True)
    await page.screenshot(path=str(OUT / 'edges/back-during-flight.png'))
    state = {'rings': await page.evaluate(RING_OPACITY), 'path': await page.evaluate('location.pathname'),
             'contentOpacity': await page.locator('.page-content').evaluate('e=>Number(getComputedStyle(e).opacity)')}
    await context.close()
    return state


async def model_slow_fail(browser):
    """Instruments are procedural (instrument-models.ts): no instrument download can stall. (1) Poll leaders through the
    pulse flight — never visible before data-leaders=live. (2) ambient.glb blocked → still view: no leaders, board still works."""
    out = {}
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await enter(page)
    await land(page, await page.locator('#surgeline').evaluate('e=>e.getBoundingClientRect().top+scrollY+300'))
    await page.locator('[data-open-case=surgeline]').tap()
    samples, shot = [], False
    for _ in range(120):
        state = await page.evaluate(LEADERS)
        samples.append(state)
        if state['path'] == '/work/surgeline' and not shot:
            await page.screenshot(path=str(OUT / 'm11a-model-arriving.png'))
            shot = True
        if state['path'] == '/work/surgeline' and state['live']:
            break
        await page.wait_for_timeout(40)
    await idle(page)
    await land(page, await top_of(page, '#case-instrument'))
    await page.wait_for_selector('.case-inspection[data-leaders=live]', timeout=12000)
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(OUT / 'm11b-model-arrived.png'))
    out['flight'] = {'samples': len(samples), 'strayLeaders': [x for x in samples if not x['live'] and x['maxLeader'] > .01][:5],
                     'onCaseWithoutLive': sum(1 for x in samples if x['path'] == '/work/surgeline' and not x['live']),
                     'leaderAfter': await page.locator('[data-hotspot-line]').first.evaluate('e=>Number(getComputedStyle(e).opacity)')}
    await context.close()

    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await page.route('**/models/ambient.glb', lambda route: route.abort())
    await enter(page, '/work/surgeline')
    await page.wait_for_selector('.observatory[data-scene=fallback]', timeout=25000)
    await land(page, await top_of(page, '#case-instrument'))
    await page.wait_for_timeout(800)
    bad = await page.evaluate(LEADERS)
    bad['still'] = await page.locator('.case-instrument-still').evaluate('e=>e.getBoundingClientRect().height')
    await page.screenshot(path=str(OUT / 'm11c-model-failed.png'))
    await land(page, await top_of(page, '.dispatch-board') - 100)
    for action in ('start', 'crash', 'resume'):
        await press(page, action, True)
        await page.wait_for_timeout(400)
    await vsr.state(page, 'complete')
    await vsr.settled(page, 'complete')
    bad['confirmed'] = await page.locator('.dispatch-ledger [data-status=confirmed]').count()
    await page.screenshot(path=str(OUT / 'm11d-failed-board-complete.png'))
    out['failed'] = bad
    await context.close()
    return out


async def reduced_motion(browser):
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, reduced_motion='reduce')
    page = await context.new_page()
    await enter(page)
    await land(page, await page.locator('#surgeline').evaluate('e=>e.getBoundingClientRect().top+scrollY+300'))
    await page.evaluate(PULSE)
    await page.locator('[data-open-case=surgeline]').tap()
    trace = await pulse_collect(page, '/work/surgeline', None)
    rings = max(max(r['o'] for r in f['rings']) for f in trace)
    await land(page, await top_of(page, '.dispatch-board') - 100)
    snaps = {}
    for action, stage in (('start', 'sending'), ('crash', 'crashed')):
        await press(page, action, True)
        started = time.time()
        await vsr.settled(page, stage, timeout=3000)
        snaps[stage] = round((time.time() - started) * 1000)
    await page.screenshot(path=str(OUT / 'm12a-reduced-crashed.png'))
    await press(page, 'resume', True)
    await vsr.state(page, 'resuming')
    started = time.time()
    await vsr.state(page, 'complete')
    readable = round((time.time() - started) * 1000)
    await vsr.settled(page, 'complete', timeout=2000)
    await page.screenshot(path=str(OUT / 'm12b-reduced-complete.png'))
    state = {'ringsMaxOpacity': rings, 'settleMs': snaps, 'resumingVisibleMs': readable, 'confirmed': await page.locator('.dispatch-ledger [data-status=confirmed]').count()}
    await context.close()
    return state


async def viewports(browser):
    vsr.OUT = OUT / 'viewports'
    vsr.OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for size in ['390x844', '360x740', '430x932', '768x1024', '1440x900', '1920x1080']:
        w, h = map(int, size.split('x'))
        try:
            r = await vsr.viewport(browser, w, h)
            rows.append({'viewport': r['viewport'], 'pass': True, 'checks': r['checks']})
        except Exception as error:  # noqa: BLE001
            rows.append({'viewport': size, 'pass': False, 'error': repr(error).splitlines()[0][:300]})
        print(' ', rows[-1]['viewport'], rows[-1]['pass'], flush=True)
    try:
        edges = await vsr.edges(browser)
    except Exception as error:  # noqa: BLE001
        edges = {'error': repr(error).splitlines()[0][:300]}
    return rows, edges


# ---------------------------------------------------------------- frame rate
async def perf(browser):
    W, H = 390, 844
    context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True, has_touch=True)
    await context.add_init_script(FRAMES)
    page = await context.new_page()
    cdp = await context.new_cdp_session(page)
    await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    await page.goto(URL)
    await page.locator('.enter-button').click(timeout=90000)
    await idle(page)
    await page.wait_for_timeout(1500)
    segs = {}

    async def measure(name, action):
        n0 = await page.evaluate('__frames.length')
        await action()
        segs[name] = await page.evaluate('(n)=>__frames.slice(n)', n0)

    section = await page.locator('#surgeline').evaluate('e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight})')
    await land(page, section['top'] - 100)
    await page.wait_for_timeout(800)
    await measure('chapter orbit + strip (swipe)', lambda: swipe_until(page, cdp, section['top'] + section['h'] - H, step=300, pause=.25))
    await land(page, section['top'] + .45 * (section['h'] - H))
    await page.wait_for_timeout(800)

    async def fly():
        await page.locator('[data-open-case=surgeline]').tap()
        await page.wait_for_url('**/work/surgeline')
        await idle(page)
    await measure('antenna pulse into the case', fly)
    await land(page, await top_of(page, '.dispatch-board') - 100)
    await page.wait_for_timeout(800)

    async def demo():
        await press(page, 'start', True)
        await page.wait_for_timeout(2300)
        await press(page, 'crash', True)
        await page.wait_for_timeout(600)
        await press(page, 'resume', True)
        await page.wait_for_selector('.dispatch-room[data-stage=complete]', timeout=15000)
        await page.wait_for_timeout(300)
    await measure('Start → Cut → Resume (board)', demo)
    await land(page, 0)
    await page.wait_for_timeout(600)
    end = await bottom(page)
    await measure('case scroll to Next (swipe)', lambda: swipe_until(page, cdp, end, step=300, pause=.25))
    await land(page, await top_of(page, '.case-next') - 100)
    await page.wait_for_timeout(600)

    async def back():
        await page.locator('.case-next .case-back').tap()
        await page.wait_for_url(URL + '/')
        await idle(page)
    await measure('pulse return to the chapter', back)
    await context.close()

    def stats(ts):
        d = sorted(b - a for a, b in zip(ts, ts[1:]))
        return {'fps': round(1000 * len(d) / sum(d), 1), 'medianMs': round(d[len(d) // 2], 1), 'p95Ms': round(d[int(len(d) * .95)], 1),
                'worstMs': round(d[-1], 1), 'slowPct': round(100 * sum(x > SLOW_MS for x in d) / len(d), 1), 'frames': len(d)} if d else {'fps': 0, 'slowPct': 100, 'p95Ms': 0}
    results = {k: {**stats(v), 'series': [round(b - a, 1) for a, b in zip(v, v[1:])]} for k, v in segs.items()}
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=110)
    x = 0
    for name, s in results.items():
        ax.plot(range(x, x + len(s['series'])), s['series'], lw=.8, label=f"{name}: {s['fps']} fps ({s['slowPct']}% slow, p95 {s['p95Ms']} ms)")
        x += len(s['series']) + 20
    ax.axhline(1000 / 60, color='#5BE49B', ls='--', lw=1)
    ax.axhline(SLOW_MS, color='#FF5A5F', ls='--', lw=1)
    ax.set_ylim(0, 70)
    ax.set_ylabel('frame time (ms)')
    ax.set_xlabel('frames (segments in order)')
    ax.set_title('SurgeLine dispatch room · 390×844 DPR 2 · 4x CPU throttle · green = 60 fps, red = 45 fps')
    ax.legend(fontsize=7, loc='upper right')
    fig.tight_layout()
    fig.savefig(OUT / 'p01-fps-4x.png')
    plt.close(fig)
    return {k: {a: b for a, b in v.items() if a != 'series'} for k, v in results.items()}


# ---------------------------------------------------------------- sources
def sources_check(page_text, cards):
    dossier = DOSSIER.read_text()
    text = page_text + '\n' + '\n'.join(c['body'] for c in cards)
    claims = [
        ('50,000 input rows', '50,000 records'), ('49,950 unique records', '49,950'), ('50 duplicate input rows rejected at import', '50 deliberate duplicates'),
        ('10,621', 'before kill #1 | 10,621'), ('21,508', 'before kill #2 | 21,508'), ('48,273', '**48,273**'),
        ('844', 'rejected by validation (permanent) | 844'), ('833', 'still failing after 5 attempts | 833'),
        ('0 duplicate submissions', '0 duplicates'), ('All 7 stranded records recovered', '7 orphaned jobs'),
        ('killed the entire worker group twice', 'whole process group'), ('five attempts', '5 attempts'),
        ('120-second claim expiry', 'LEASE_TIMEOUT_SECONDS` | 120'), ('returns the same confirmation', 'same confirmation number'),
        ('3.0 days', '3.0 days'), ('4.1 days', '4.1 days'), ('6 million records were never run', 'extrapolated'),
        ('81,915', '**81,915**'), ('fails 5% of submissions on purpose', 'fails 5%'), ('August 2026', '2026-08-28'),
    ]
    rows = [{'claim': c, 'onPage': c in text, 'needle': n, 'found': n.lower() in dossier.lower()} for c, n in claims]
    illustration = ['Interactive illustration · fictional records and receipts · time compressed', 'not the illustration above', 'Recorded snapshot, not live telemetry', 'No forms are submitted here']
    labelled = {s: s in text for s in illustration}
    forbidden = [w for w in ('Upwork', 'Amazon', 'guaranteed') if w.lower() in text.lower()]
    ok = all(r['onPage'] and r['found'] for r in rows) and all(labelled.values()) and not forbidden
    detail = (f"{sum(r['onPage'] and r['found'] for r in rows)}/{len(rows)} claims on the page found in the dossier "
              f"({', '.join(r['claim'] for r in rows if not (r['onPage'] and r['found'])) or 'none missing'}); illustration/recorded labels {sum(labelled.values())}/{len(labelled)}; "
              f"48,273 + 844 + 833 = {48273 + 844 + 833:,}; forbidden wording {forbidden or 'none'}")
    return ok, detail, {'claims': rows, 'labels': labelled, 'forbidden': forbidden}


# ---------------------------------------------------------------- sheets
def strip(names, path, size):
    present = [(n, label) for n, label in names if (OUT / n).exists()]
    if not present:
        return
    sheet = Image.new('RGB', (size[0] * len(present), size[1]), 'black')
    for i, (name, label) in enumerate(present):
        sheet.paste(tile(OUT / name, label, size), (i * size[0], 0))
    sheet.save(path, quality=88)


def contact(labeled, path, size, cols):
    present = [(n, lab) for n, lab in labeled if (OUT / n).exists()]
    if not present:
        return
    rows = (len(present) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * size[0], rows * size[1]), 'black')
    for i, (name, label) in enumerate(present):
        sheet.paste(tile(OUT / name, f'{i + 1:02d} {label}', size), ((i % cols) * size[0], (i // cols) * size[1]))
    sheet.save(path, quality=82)


def sheets():
    P, D = (390, 844), (720, 450)
    strip([('m01a-chapter-sending.png', 'Orbit .2 · lanes sending'), ('m01b-chapter-cut.png', 'Orbit .48 · browser 2 cut'), ('m01c-chapter-resumed.png', 'Orbit end · resumed, all green')], OUT / 'i01-chapter-strip.png', P)
    strip([('m01b-chapter-cut.png', 'Tap Open case file'), ('m02a-pulse-out.png', 'Pulse leaves the antenna'), ('m02b-case-opened.png', 'Case opens · heading focus')], OUT / 'i02-pulse-entry.png', P)
    strip([('m03-hotspot-01.png', '01 Work list'), ('m03-hotspot-02.png', '02 Parallel workers'), ('m03-hotspot-03.png', '03 Confirmation proof')], OUT / 'i03-hotspots.png', P)
    strip([('m04-board-ready.png', 'Ready · saved list'), ('m04-board-in-flight.png', 'Start · in flight'), ('m04-board-sending.png', 'A ok · C rejected · B waits'),
           ('m04-board-crashed.png', 'Cut · B stranded'), ('m04-board-resuming-b-back.png', 'Resume · B back in line'), ('m04-board-resuming-f-retries.png', 'F retries · B ×2'),
           ('m04-board-complete.png', 'Complete · 4 / 1 / 1')], OUT / 'i04-dispatch-demo.png', P)
    strip([('m04-board-complete.png', 'Complete · one chip per record'), ('m04-ledger.png', 'Ledger · B sent 2×, one receipt'), ('m04i-after-scroll-back.png', 'Scrolled away and back · kept'),
           ('m04j-replay.png', 'Replay · explicit reset'), ('m05a-rapid-taps-settled.png', 'Rapid taps · still 4 / 1 / 1')], OUT / 'i05-no-duplicate.png', P)
    strip([('m06a-evidence.png', 'Recorded run · intake + checkpoints'), ('m06c-outcomes.png', '48,273 · 844 · 833'), ('m04-ledger.png', 'Illustration ledger · reasons'),
           ('m06b-readings.png', 'Readings')], OUT / 'i06-processed-vs-confirmed.png', P)
    strip([('m07-next-teaser.png', 'DriftWatch teaser'), ('m08a-pulse-return.png', 'Rings contract to the antenna'), ('m08b-back-at-chapter.png', 'Back at the chapter'),
           ('m09-next-driftwatch.png', 'Next → DriftWatch')], OUT / 'i07-return-next.png', P)
    strip([('m09-next-driftwatch.png', 'DriftWatch'), ('m09b-history-back-surgeline.png', 'Back → board works'), ('m10-direct-refresh.png', 'Direct URL + refresh')], OUT / 'i08-history-direct.png', P)
    strip([('m05b-cut-before-form.png', 'Cut before the form · B mid-lane'), ('m05a-rapid-taps-settled.png', 'Rapid taps settled'), ('edges/back-during-flight.png', 'Back during the pulse'),
           ('d09a-resized-mid-resume-390.png', 'Resize 1440 → 390 mid-resume')], OUT / 'i09-interruptions.png', P)
    strip([('m11a-model-arriving.png', 'Case arriving · no leaders'), ('m11b-model-arrived.png', 'Model projected · leaders'), ('m11c-model-failed.png', 'Scene failed · still view'),
           ('m11d-failed-board-complete.png', 'Still view · board works')], OUT / 'i10-model-slow-fail.png', P)
    strip([('m12a-reduced-crashed.png', 'Reduced motion · snapped'), ('m12b-reduced-complete.png', 'Reduced motion · complete')], OUT / 'i12-reduced-motion.png', P)
    strip([('d01-chapter-cut.png', 'Chapter 1440 · cut'), ('d04-room-intro-steps.png', 'Steps in one row'), ('d05-board-sending.png', 'Wide board · sending'),
           ('d05-board-resuming-b-back.png', 'Resume · lanes in parallel'), ('d05-board-complete.png', 'Complete'), ('d05-ledger.png', 'Control beside ledger'),
           ('d06-evidence.png', 'Checkpoints beside outcomes'), ('viewports/complete-1920x1080.png', '1920 complete')], OUT / 'i13-desktop.png', D)
    grid = Image.new('RGB', (P[0] * 4, P[1] * 3), 'black')
    for c, tag in enumerate(['390x844', '360x740', '430x932', '768x1024']):
        for r, kind in enumerate(['chapter', 'crashed', 'complete']):
            source = OUT / 'viewports' / f'{kind}-{tag}.png'
            if source.exists():
                grid.paste(tile(source, f'{tag} · {kind}', P), (c * P[0], r * P[1]))
    grid.save(OUT / 'i11-viewports.jpg', quality=85)
    contact([
        ('m01a-chapter-sending.png', 'Chapter · three lanes sending'), ('m01b-chapter-cut.png', 'Chapter · browser 2 cut'), ('m01c-chapter-resumed.png', 'Chapter · resumed'),
        ('m02a-pulse-out.png', 'Pulse out of the antenna'), ('m02b-case-opened.png', 'Case opened'), ('m03-hotspot-01.png', 'Hotspot 01 · work list'),
        ('m03-hotspot-02.png', 'Hotspot 02 · workers'), ('m03-hotspot-03.png', 'Hotspot 03 · proof'), ('m04-board-ready.png', 'Board ready'),
        ('m04-board-in-flight.png', 'Start · in flight'), ('m04-board-sending.png', 'B waits for receipt'), ('m04-board-crashed.png', 'Cut · B stranded'),
        ('m04-board-resuming-b-back.png', 'Resume · B back in line'), ('m04-board-resuming-f-retries.png', 'F retries'), ('m04-board-complete.png', 'Complete'),
        ('m04-ledger.png', 'Ledger'), ('m04j-replay.png', 'Replay'), ('m05b-cut-before-form.png', 'Cut before the form'), ('m05a-rapid-taps-settled.png', 'Rapid taps'),
        ('m06a-evidence.png', 'Recorded run'), ('m06c-outcomes.png', 'Outcomes'), ('m07-next-teaser.png', 'DriftWatch teaser'), ('m08a-pulse-return.png', 'Pulse return'),
        ('m08b-back-at-chapter.png', 'Back at chapter'), ('m09-next-driftwatch.png', 'Next → DriftWatch'), ('m10-direct-refresh.png', 'Direct + refresh'),
        ('m11c-model-failed.png', 'Scene failed · still view'), ('m12b-reduced-complete.png', 'Reduced motion'),
    ], OUT / 'contact-sheet-mobile.jpg', P, 7)
    contact([
        ('d01-chapter-cut.png', 'Chapter · cut'), ('d02a-pulse-out.png', 'Pulse out'), ('d03-hotspot-workers.png', 'Hotspot · workers'), ('d04-room-intro-steps.png', 'Intro + steps'),
        ('d05-board-ready.png', 'Board ready'), ('d05-board-in-flight.png', 'In flight'), ('d05-board-sending.png', 'B waits'), ('d05-board-crashed.png', 'Cut'),
        ('d05-board-resuming-b-back.png', 'Resume'), ('d05-board-resuming-f-retries.png', 'F retries'), ('d05-board-complete.png', 'Complete'), ('d05-ledger.png', 'Control + ledger'),
        ('d06-evidence.png', 'Recorded proof'), ('d07-next-teaser.png', 'Next teaser'), ('d08a-pulse-return.png', 'Pulse return'), ('d08b-back-at-chapter.png', 'Back at chapter'),
        ('d09b-resized-back-1440.png', 'Resized back to 1440'), ('viewports/complete-1920x1080.png', '1920 complete'),
    ], OUT / 'contact-sheet-desktop.jpg', D, 4)


# ---------------------------------------------------------------- verdicts
def board_ok(b, wide):
    s, c, r = b['start'], b['cut'], b['resume']
    col = b['colours']
    colours = col['A'] == col['B'] == col['D'] and col['C'] == col['F'] and col['A'] != col['C'] and col['ok'] != col['rejected'] == col['dead']
    return (s['ok'] and s['bRing'] == 'dispatch-hold' and c['bFrozen'] and c['bState'] == 'stranded' and c['aKept'] and c['cKept'] and c['lane2'] == 'offline'
            and c['ledgerB'] == 'stranded' and b['resumeButtonDisabled'] and r['ok'] and b['confirmedCount'] == '4' and colours and (wide or b['fitsOneView']))


def board_text(b):
    s, c, r = b['start'], b['cut'], b['resume']
    return (f"Start: A {s['A']}, C {s['C']} (shake turns at the form {s['cShakeTurns']}), B waits at the form ×{s['bSends']} ring '{s['bRing']}'; "
            f"Cut: B frozen={c['bFrozen']} ({c['bState']}), browser 2 '{c['lane2']}', A/C kept={c['aKept'] and c['cKept']}; "
            f"Resume ({r['ms']} ms, button disabled={b['resumeButtonDisabled']}): B {r['B']} back in line ±{r['bBackInLinePx']} px, sends {r['bSends']}; F sends {r['fSends']} → {r['final']['F']}; "
            f"ledger {b['confirmedCount']}/6 confirmed; board+button in one view={b['fitsOneView']}")


def verdicts(m, d, vp, edges, slow, reduced, fps, back_flight, sources):
    if m:
        s = m['story']
        order = [o for o in s['order'] if o is not None]
        check('story', order == sorted(order) and len(order) == 6 and m['stripBelowCta'] and s['draft'] == [] and not m['stripDraft']
              and 'fictional records' in s['disclosure'] and 'not live telemetry' in s['source'] and 'Finished processing.' in s['text'],
              f"case sections in story order={order == sorted(order)} ({len(order)}/6: brief, instrument, dispatch room, recorded proof, readings, Next); strip under the CTA={m['stripBelowCta']}; "
              f"illustration disclosure '{s['disclosure'].strip()}'; recorded proof '{s['source'].strip()}'; DRAFT on case {s['draft']} and chapter strip={m['stripDraft']} (copy approved at gate 7B)",
              'i01-chapter-strip.png')
        ms, ds = m['strip'], d['strip'] if d else {}
        check('chapterStrip', ms['ok'] and ds.get('ok'),
              f"phone swipe {ms['samples']} samples: browser 1 keeps filling {ms['lane1Across']} while browser 2 frozen at {ms['lane2FrozenAt']} over {ms['cutSamples']} samples in orbit .39–.56 with 'cut' shown; "
              f"end all three lanes green + 'resumed'={ms['end']['s1last'] == 1 and ms['end']['resumed'] == 1}; swipe back → browser 1 {ms['back']['s0'] if ms['back'] else '?'} (from {ms['end']['s0']}), 'resumed' hidden; "
              f"desktop wheel {ds.get('samples')} samples same rule={ds.get('ok')}", 'i01-chapter-strip.png')
        pi, dpi = m['pulseIn'], d['pulseIn'] if d else {}
        check('pulseEntry', pi['ok'] and pi['focus'] == 'case-heading' and dpi.get('ok') and dpi.get('focus') == 'case-heading',
              f"phone: 3 staggered rings visible {pi.get('visibleMs')} ms over {pi['visibleFrames']} frames, lead ring scale {pi.get('scale')} from antenna {pi.get('origin')} inside the viewport, cleared after; focus #{pi['focus']} | "
              f"desktop: {dpi.get('visibleMs')} ms, scale {dpi.get('scale')}, origin {dpi.get('origin')}, focus #{dpi.get('focus')}", 'i02-pulse-entry.png')
        cards = m['hotspots']
        explain = ['49,950' in cards[0]['body'], 'lease expires' in cards[1]['body'], '48,273' in cards[2]['body'] and 'Processed does not mean successful' in cards[2]['body']]
        check('hotspots', all(c['inside'] for c in cards) and all(c['leader'] > .3 for c in cards) and all(explain),
              f"cards {[c['title'] for c in cards]} inside viewport={[c['inside'] for c in cards]}, leader opacity {[round(c['leader'], 2) for c in cards]}; "
              f"bodies explain work list 49,950 / lease expiry / 48,273 + 'processed ≠ successful'={explain}", 'i03-hotspots.png')
        check('dispatchDemo', board_ok(m['board'], False) and d and board_ok(d['board'], True),
              'phone (tap): ' + board_text(m['board']) + (' | desktop (click): ' + board_text(d['board']) if d else ''), 'i04-dispatch-demo.png')
        r = m['board']['resume']
        dr = d['board']['resume'] if d else {}
        rapid = m['rapid']
        rapid_ok = rapid['stage'] == 'complete' and rapid['chips'] == 6 and [x[1] for x in rapid['ledger']] == ['confirmed', 'confirmed', 'rejected', 'confirmed', 'confirmed', 'dead-letter']
        check('noDuplicate', r['ok'] and dr.get('ok') and m['board']['ledgerAKept'] and len(m['board']['ledger']) == 6 and m['afterScrollBack'] == {'confirmed': 4, 'stage': 'complete'}
              and m['replay'] == {'queued': 6, 'chips': 6} and rapid_ok,
              f"phone resume traced {r['frames']} frames: A moved {r['aMovedPx']} px, A sends {r['aSends']}; chips per frame {r['chipCounts']}; confirmed {r['confirmedRange'][0]} → {r['confirmedRange'][1]} only rising={r['confirmedOnlyRises']}; "
              f"frames with two confirmed chips on one place {r['confirmedOverlapFrames']}; resting overlaps {r['restingOverlaps'] or 0}; re-confirmed chips {r['reconfirmed'] or 0}; ledger rows {len(m['board']['ledger'])}, A row unchanged={m['board']['ledgerAKept']} | "
              f"desktop {dr.get('frames')} frames: A moved {dr.get('aMovedPx')} px, overlaps {dr.get('confirmedOverlapFrames')} | scroll away and back keeps {m['afterScrollBack']}; Replay → {m['replay']}; "
              f"7 rapid taps → {rapid['stage']} with {rapid['chips']} chips, ledger {[x[1] for x in rapid['ledger']]}", 'i05-no-duplicate.png')
        ev = m['evidence']
        led = {x[0]: x for x in m['board']['ledger']}
        reasons = 'reason kept' in led['C'][2] and 'last error kept' in led['F'][2] and 'same receipt' in led['B'][2]
        check('processedVsConfirmed', 'Not all successful.' in ev['heading'] and ev['totals'] == ['48,273', '844', '833'] and ev['ok'] != ev['rejected'] == ev['dead']
              and sum(int(t.replace(',', '')) for t in ev['totals']) == 49950 and reasons and m['board']['colours']['ok'] != m['board']['colours']['rejected'],
              f"heading '{ev['heading']}'; recorded outcomes {ev['totals']} sum {sum(int(t.replace(',', '')) for t in ev['totals']):,}; confirmed colour {ev['ok']} vs rejected {ev['rejected']} / dead-letter {ev['dead']}; "
              f"board bins Confirmed (green) apart from Rejected / Dead-letter (red); ledger reasons: C '{led['C'][2]}', F '{led['F'][2]}', B '{led['B'][2]}'", 'i06-processed-vs-confirmed.png')
        rt = m['return']
        drt = d['return'] if d else {}
        same = [rt.get('origin') and dist(rt['origin'], pi['origin']) < 4, drt.get('origin') and dpi.get('origin') and dist(drt['origin'], dpi['origin']) < 4]
        check('returnNext', rt['ok'] and all(same) and rt['scrollDelta'] < 3 and rt['focus'] == 'surgeline' and 'one day' in m['teaser'] and drt.get('ok') and drt.get('scrollDelta', 9) < 3,
              f"phone: rings contract (scale {rt.get('scale')}) {rt.get('visibleMs')} ms onto the antenna point {rt.get('origin')} it left from {pi.get('origin')} (same={same[0]}), back on the saved chapter position ±{rt['scrollDelta']:.1f} px, focus on Open case file={rt['focus'] == 'surgeline'}; "
              f"teaser '{m['teaser'].replace(chr(10), ' ')}', Next opened DriftWatch; desktop return scale {drt.get('scale')} onto {drt.get('origin')} left from {dpi.get('origin')} (same={same[1]}) ±{drt.get('scrollDelta')} px", 'i07-return-next.png')
        h, di = m['history'], m['direct']
        check('historyDirect', h['backOk'] and h['forwardOk'] and h['canvas'] and di['directConfirmed'] == 4 and di['refreshedStage'] == 'ready' and di['refreshedConfirmed'] == 4 and not di['errors'] and not di['bad'],
              f"Back DriftWatch → SurgeLine room works (board ready → Start settles)={h['backOk']}, Forward → DriftWatch={h['forwardOk']}, same Canvas={h['canvas']}; "
              f"direct /work/surgeline demo → {di['directConfirmed']} confirmed; refresh → stage '{di['refreshedStage']}' (illustration restarts) → demo again {di['refreshedConfirmed']} confirmed; errors {len(di['errors'])}, ≥400 {len(di['bad'])}",
              'i08-history-direct.png')
        ce = m['cutEarly']
        rz = d['resize'] if d else None
        rz_ok = bool(rz) and all(x['overflow'] <= 1 and x['chips'] == 6 and x['confirmed'] == 4 for x in rz['after']) and rz['canvas']
        mid_lane = ce['laneStart'] - 1 <= ce['bX'] < ce['laneEnd'] - 2
        check('interruptions', m['doubleTap']['historyDelta'] == 1 and rapid_ok and ce['bState'] == 'stranded' and ce['bStill'] and mid_lane and ce['completed']
              and back_flight and back_flight['rings'] == 0 and back_flight['path'] == '/' and rz_ok and edges and edges.get('resize') == 'passed' and edges.get('interrupt') == 'passed',
              f"double tap Open case file → history +{m['doubleTap']['historyDelta']} ({m['doubleTap']['second']}); 7 rapid taps → one outcome per record; "
              f"Cut ~0.8 s after Start → B stranded at x {ce['bX']} between lane start {ce['laneStart']} and form {ce['laneEnd']} (mid-lane={mid_lane}), still={ce['bStill']}, Resume completes={ce['completed']}; "
              f"Back during the pulse → rings {back_flight and back_flight['rings']} on {back_flight and back_flight['path']}; "
              + (f"resize 1440→390 mid-resume then 1024/900/1920/1440: overflow {[x['overflow'] for x in rz['after']]}, chips {[x['chips'] for x in rz['after']]}, confirmed {[x['confirmed'] for x in rz['after']]}" if rz else 'resize not run')
              + f"; Development edges interrupt/resize={edges and edges.get('interrupt')}/{edges and edges.get('resize')}", 'i09-interruptions.png')
    if slow:
        fl, bad = slow['flight'], slow['failed']
        check('modelSlowFail', not fl['strayLeaders'] and fl['leaderAfter'] > .3 and bad['scene'] == 'fallback' and bad['live'] == 0 and bad['maxLeader'] == 0 and bad['still'] > 100
              and bad['confirmed'] == 4 and edges and edges.get('fallback') == 'passed',
              f"instruments are procedural (no instrument download can stall); pulse flight polled {fl['samples']}×: leaders visible without a projected model {len(fl['strayLeaders'])}×, "
              f"case frames before projection {fl['onCaseWithoutLive']} with leaders hidden, leader opacity {round(fl['leaderAfter'], 2)} once live; scene failed (ambient.glb blocked): scene '{bad['scene']}', "
              f"leaders {bad['live']}/{bad['maxLeader']}, still image {round(bad['still'])} px, board demo → {bad['confirmed']} confirmed; Development fallback exercise={edges and edges.get('fallback')}", 'i10-model-slow-fail.png')
    if reduced:
        check('reducedMotion', reduced['ringsMaxOpacity'] == 0 and all(v < 800 for v in reduced['settleMs'].values()) and 500 <= reduced['resumingVisibleMs'] <= 2500
              and reduced['confirmed'] == 4 and edges and edges.get('reduced') == 'passed',
              f"rings max opacity {reduced['ringsMaxOpacity']} during entry; chips settled {reduced['settleMs']} ms after each tap (snap); recovery message shown {reduced['resumingVisibleMs']} ms then complete "
              f"({reduced['confirmed']} confirmed); Development reduced exercise={edges and edges.get('reduced')}", 'i12-reduced-motion.png')
    if vp:
        phones = [r for r in vp if int(r['viewport'].split('x')[0]) < 1024]
        wide = [r for r in vp if int(r['viewport'].split('x')[0]) >= 1024]
        check('mobileViewports', len(phones) == 4 and all(r['pass'] for r in phones),
              '; '.join(f"{r['viewport']} {'pass (' + str(len(r['checks'])) + ' checks)' if r['pass'] else 'FAIL ' + r.get('error', '')}" for r in phones), 'i11-viewports.jpg')
        lay, pl = (d['layout'], d['proofLayout']) if d else ({}, {})
        comp = bool(lay) and len(set(lay['steps'])) == 1 and lay['queueRight'] <= lay['lanesLeft'] + 1 and lay['lanesRight'] <= lay['binsLeft'] + 1 \
            and lay['controlRight'] <= lay['ledgerLeft'] and lay['ledgerColumns'] == 2 and pl['checkpointsRight'] <= pl['outcomesLeft']
        check('desktopComposition', len(wide) == 2 and all(r['pass'] for r in wide) and comp,
              f"1440/1920 Development checks {[r['viewport'] + ' ' + ('pass' if r['pass'] else 'FAIL') for r in wide]}; steps one row (tops {lay.get('steps')}); board left → right "
              f"queue|lanes|bins={lay and lay['queueRight'] <= lay['lanesLeft'] + 1 and lay['lanesRight'] <= lay['binsLeft'] + 1} at width {lay.get('boardWidth')} px, chip {lay.get('chip')} px; "
              f"control beside ledger={lay and lay['controlRight'] <= lay['ledgerLeft']}, ledger columns {lay.get('ledgerColumns')}; checkpoints beside outcomes={pl and pl['checkpointsRight'] <= pl['outcomesLeft']}", 'i13-desktop.png')
    if sources:
        check('sources', sources[0], sources[1], 'i06-processed-vs-confirmed.png', data=sources[2])
    if fps:
        low = {k: v for k, v in fps.items() if v['fps'] < 45 or v['slowPct'] > 10}
        check('performance', not low,
              '4x CPU: ' + '; '.join(f"{k} {v['fps']} fps ({v['slowPct']}% slower than 45 fps, p95 {v['p95Ms']} ms)" for k, v in fps.items()), 'p01-fps-4x.png')
    if m and d:
        walks = META['walks']
        check('clean', walks['canvas'] and not walks['errors'] and not walks['bad'] and max(walks['overflow']) <= 1 and not m['direct']['errors'],
              f"same Canvas through phone flow + desktop resize={walks['canvas']}; page/console errors {walks['errors'] or 0}; responses ≥400 {walks['bad'] or 0}; max horizontal overflow {max(walks['overflow'])} px",
              'contact-sheet-mobile.jpg')
    fp, _ = rr.fingerprint()
    ledger_data = json.loads(rr.LEDGER.read_text()) if rr.LEDGER.exists() else {}
    full = {'dispatch', 'perf-surgeline', 'audio', 'desktop-a', 'desktop-b', 'perf-crosscheck'}
    suites = [{'suite': n, 'status': ledger_data.get(n, {}).get('status', 'missing'), 'current': ledger_data.get(n, {}).get('fingerprint') == fp,
               'phones': ledger_data.get(n, {}).get('phones'), 'finishedAt': ledger_data.get(n, {}).get('finishedAt')} for n in rr.SUITES]
    check('regressions', all(s['status'] == 'passed' and s['current'] and (s['suite'] not in full or s['phones'] == 'full') for s in suites),
          f"source fingerprint {fp}; " + '; '.join(f"{s['suite']}={s['status']}{'' if s['current'] else ' (stale)'} {s['phones']}" for s in suites), 'i11-viewports.jpg', suites=suites)


# ---------------------------------------------------------------- run
async def step(name, coro, key=None, tag=None):
    if ONLY is not None and tag not in ONLY:
        coro.close()
        return None
    print(name, flush=True)
    try:
        return await coro
    except Exception as error:  # noqa: BLE001 — record the failure, keep building the pack
        traceback.print_exc()
        META.setdefault('errors', {})[name] = repr(error)
        for k in ([key] if isinstance(key, str) else key or []):
            failed(k, repr(error).splitlines()[0])
        return None


async def run():
    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ('raw', 'viewports', 'edges'):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        try:
            mobile = await step('phone walkthrough (recorded)', mobile_walk(browser), ['story', 'chapterStrip', 'pulseEntry', 'hotspots', 'dispatchDemo', 'noDuplicate', 'processedVsConfirmed', 'returnNext', 'historyDirect', 'interruptions', 'clean', 'sources'], tag='mobile')
            desktop = await step('desktop walkthrough (recorded)', desktop_walk(browser), ['desktopComposition'], tag='desktop')
            back_flight = await step('back during the pulse', back_during_flight(browser), tag='back')
            slow = await step('model late / failed', model_slow_fail(browser), 'modelSlowFail', tag='slow')
            reduced = await step('reduced motion', reduced_motion(browser), 'reducedMotion', tag='reduced')
            vp = await step('six viewports + edges (verify_surgeline_room)', viewports(browser), ['mobileViewports', 'desktopComposition'], tag='viewports')
            fps = await step('frame rate 4x CPU', perf(browser), 'performance', tag='fps')
        finally:
            await browser.close()
    m = mobile[2] if mobile else None
    d = desktop[2] if desktop else None
    META['walks'] = {
        'canvas': bool(m and m['history']['canvas'] and d and d['resize']['canvas']),
        'errors': (mobile[1].sink['errors'] if mobile else []) + (desktop[1].sink['errors'] if desktop else []),
        'bad': (mobile[1].sink['bad'] if mobile else []) + (desktop[1].sink['bad'] if desktop else []),
        'overflow': (mobile[1].overflows if mobile else [0]) + (desktop[1].overflows if desktop else [0]),
    }
    sources = None
    if m:
        try:
            sources = sources_check(m['story']['text'] + '\n' + m['story']['labels'], m['hotspots'])
        except Exception as error:  # noqa: BLE001
            failed('sources', repr(error))
    rows, edges = vp if vp else (None, None)
    try:
        verdicts(m, d, rows, edges, slow, reduced, fps, back_flight, sources)
    except Exception as error:  # noqa: BLE001 — a verdict bug must not lose the recordings
        traceback.print_exc()
        META.setdefault('errors', {})['verdicts'] = repr(error)

    videos = []
    if mobile:
        encode(mobile[0], OUT / 'walkthrough-mobile.mp4')
        videos.append(duration(OUT / 'walkthrough-mobile.mp4'))
    if desktop:
        encode(desktop[0], OUT / 'walkthrough-desktop.mp4')
        videos.append(duration(OUT / 'walkthrough-desktop.mp4'))
    if mobile and desktop:
        mm, dm = mobile[1].marks, desktop[1].marks
        mp4m, mp4d = OUT / 'walkthrough-mobile.mp4', OUT / 'walkthrough-desktop.mp4'
        clips = [
            (mp4m, mm['entry'] - .4, mm['entryEnd'] + .4, 'Phone - antenna pulse into the case', 390),
            (mp4m, mm['start'] - .3, mm['cut'] + 1.2, 'Phone - Start then Cut browser 2', 390),
            (mp4m, mm['resume'] - .3, mm['resumeEnd'] + .3, 'Phone - Resume without re-sending A', 390),
            (mp4m, mm['rapid'] - .3, min(mm['rapid'] + 3.5, mm['rapidEnd']), 'Phone - Cut before B reaches the form', 390),
            (mp4m, mm['return'] - .4, mm['returnEnd'] + .4, 'Phone - pulse return to the antenna', 390),
            (mp4d, dm['entry'] - .4, dm['entryEnd'] + .4, 'Desktop - antenna pulse into the case', 720),
            (mp4d, dm['resume'] - .3, dm['resumeEnd'] + .3, 'Desktop - Resume on the wide board', 720),
            (mp4d, dm['return'] - .4, dm['returnEnd'] + .4, 'Desktop - pulse return', 720),
            (mp4d, dm['resize'] - .3, min(dm['resize'] + 4, dm['resizeEnd']), 'Desktop - resize to 390 during recovery', 720),
        ]
        try:
            cre.slow_motion(clips, OUT / 'slow-motion.mp4')
            videos.append(duration(OUT / 'slow-motion.mp4'))
        except subprocess.CalledProcessError as error:
            META.setdefault('errors', {})['slow-motion'] = repr(error)
        META['marks'] = {'mobile': mm, 'desktop': dm}
    shutil.rmtree(RAW, ignore_errors=True)
    sheets()

    categories = {c: {'pass': all(CHECKS.get(k, {}).get('pass') for k, (cats, _) in ITEMS.items() if c in cats),
                      'items': [k for k, (cats, _) in ITEMS.items() if c in cats]} for c in CATEGORIES}
    passed = all(CHECKS.get(k, {}).get('pass') for k in ITEMS)
    trimmed = m and {k: v for k, v in m.items() if k not in ('story',)}
    if trimmed and 'strip' in trimmed:
        trimmed['strip'] = {k: v for k, v in trimmed['strip'].items() if k != 'raw'}
    report = {
        'status': 'passed' if passed else 'failed',
        'phase': 'Phase 7B — SurgeLine: dispatch room',
        'stage': 'Testing',
        'finishedAt': datetime.now(timezone.utc).isoformat(),
        'url': URL,
        'scope': 'Chromium GPU (ANGLE) emulation on the local production preview; phones at DPR 2 with touch, desktop with mouse wheel. '
                 'CPU throttle via DevTools protocol; the host GPU is not throttled. Physical phone = Phase 8.',
        'categories': categories,
        'items': {k: {'label': label, 'categories': cats, **CHECKS.get(k, {'pass': False, 'detail': 'not executed'})} for k, (cats, label) in ITEMS.items()},
        'measurements': {'fps4x': fps, 'viewports': rows, 'edges': edges, 'modelSlowFail': slow, 'reducedMotion': reduced, 'backDuringFlight': back_flight,
                         'mobile': trimmed, 'desktop': d},
        'videos': videos,
        'contactSheets': ['contact-sheet-mobile.jpg', 'contact-sheet-desktop.jpg'],
        'forOwner': OWNER,
        'errors': META.get('errors'),
    }
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + '\n')
    for key, item in report['items'].items():
        print(f"{'PASS' if item['pass'] else 'FAIL'} {key}: {item['detail']}")
    print('categories:', {c: v['pass'] for c, v in categories.items()})
    print('videos:', videos)
    return passed


if __name__ == '__main__':
    sys.exit(0 if asyncio.run(run()) else 1)
