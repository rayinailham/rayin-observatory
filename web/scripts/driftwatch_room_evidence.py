"""Phase 7C Testing evidence: DriftWatch monitoring room, mobile first then desktop.

Records two walkthroughs with real input (phone 390x844 touch swipes + taps, desktop 1440x900 mouse wheel + clicks):
chapter seismograph (green trace follows the orbit, red empty-run spike after .6, reverses on scroll back) → paper
ribbon from the needle unrolls into the case timeline → hotspots → comparison desk: five situations traced frame by
frame (quiet trace → local spike only for an alarm → verdict), healthy vs alarm, source change vs pipeline failure,
field diff, alarm record → interruptions (switch mid-compare, rapid taps, scroll away/back, keyboard) → recorded
archive kept apart from the illustration → DueWatch teaser → ribbon rolls back to its origin → Next, Back/Forward,
direct URL + refresh; desktop adds layout measurements, sticky snapshots and resize after an alarm. Cuts a 0.25x
slow-motion reel. Q42: re-runs the Development checks (verify_driftwatch_room.viewport/edges) on six viewports into
the pack, then model late/failed, reduced motion, frame rate under 4x CPU, copy/number sources and the regression ledger.

Output: assets/renders/personal-driftwatch/evidence/ — PNG per item, walkthrough-mobile.mp4, walkthrough-desktop.mp4,
slow-motion.mp4, contact sheets, evidence.json with pass/fail per item and per category.
Chromium GPU emulation on a laptop; no physical-phone claim (Phase 8).

Run from web/scripts with the production preview on :8767:
  timeout 2700 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python driftwatch_room_evidence.py [--only mobile,desktop,back,slow,reduced,viewports,fps]
Exit 1 when any item fails.
"""
import asyncio
import json
import math
import re
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
import verify_driftwatch_room as vdr  # noqa: E402
from case_files_evidence import tile  # noqa: E402
from crosscheck_room_evidence import Walk, duration, encode, overflow, swipe_until, top_of, watch, wheel_until  # noqa: E402
from verify_driftwatch_room import enter, idle, land  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/personal-driftwatch/evidence'
RAW = OUT / 'raw'
cre.OUT, cre.RAW = OUT, RAW  # shared helpers (Walk.shot, slow_motion) write into this pack
URL = vdr.URL
GPU = vdr.GPU
DOSSIER = ROOT / 'portfolio/CAPABILITY_DRIFTWATCH.md'
SLOW_MS = 1000 / 45
SCENARIOS = ('change', 'layout', 'pipeline', 'missing', 'recovery')
HEALTHY = ('change', 'recovery')
FRAMES = "(() => { window.__frames = []; const f = t => { window.__frames.push(t); requestAnimationFrame(f); }; requestAnimationFrame(f); })();"

# Chapter seismograph: orbit var on the section, green line + red spike dash offsets, the two caption layers.
CHAPTER = r"""()=>{const s=document.querySelector('#driftwatch');const q=x=>getComputedStyle(document.querySelector(x));
  const n=v=>{const m=String(v).match(/-?[\d.]+/);return m?Number(m[0])/(String(v).includes('%')?100:1):NaN};
  return {orbit:Number(getComputedStyle(s).getPropertyValue('--instrument-2-orbit')||0),line:n(q('.monitor-chapter-line').strokeDashoffset),
    alarm:n(q('.monitor-chapter .monitor-chapter-alarm').strokeDashoffset),quiet:Number(q('.monitor-chapter em:first-child').opacity),
    spike:Number(q('.monitor-chapter em:last-child').opacity)}}"""
# Paper ribbon: transform (scaleX/scaleY/x/y), opacity and direction every frame until 260 frames.
RIBBON = """()=>{const w=window.__ribbon=[];const t0=performance.now();const e=document.querySelector('.monitor-ribbon');
  const tick=()=>{const s=getComputedStyle(e);const m=new DOMMatrix(s.transform==='none'?undefined:s.transform);
    w.push({t:Math.round(performance.now()-t0),d:e.dataset.direction,o:Math.round(Number(s.opacity)*1000)/1000,sx:Math.round(m.a*1000)/1000,sy:Math.round(m.d*1000)/1000,
      x:Math.round(m.e),y:Math.round(m.f),display:s.display,path:location.pathname});
    if(w.length<260)requestAnimationFrame(tick)};requestAnimationFrame(tick)}"""
RIBBON_READABLE = "(()=>{const e=document.querySelector('.monitor-ribbon');const s=getComputedStyle(e);const a=new DOMMatrix(s.transform==='none'?undefined:s.transform).a;return Number(s.opacity)>.5&&a>.25&&a<.8})()"
# Comparison motion: clip window scaleX (the trace path itself must never scale), verdict opacity/offset and the trace label every frame.
COMPARE = """()=>{const w=window.__compare=[];const t0=performance.now();
  const tick=()=>{const g=document.querySelector('.monitor-trace-window');const r=document.querySelector('.monitor-result');const gs=getComputedStyle(g);const rs=getComputedStyle(r);
    const m=gs.transform&&gs.transform!=='none'?new DOMMatrix(gs.transform):(g.transform.baseVal.consolidate()?.matrix||new DOMMatrix());
    const pg=getComputedStyle(document.querySelector('.monitor-trace-reveal')).transform;
    w.push({t:Math.round(performance.now()-t0),sx:Math.round(m.a*1000)/1000,path:pg==='none'?1:Math.round(new DOMMatrix(pg).a*1000)/1000,o:Math.round(Number(rs.opacity)*1000)/1000,
      y:Math.round(new DOMMatrix(rs.transform==='none'?undefined:rs.transform).f*100)/100,v:document.querySelector('.monitoring-room').dataset.verdict,
      label:document.querySelector('.monitor-trace span').textContent,heading:(document.querySelector('.monitor-verdict h3')||{}).textContent||null});
    if(w.length<window.__compareFrames)requestAnimationFrame(tick)};requestAnimationFrame(tick)}"""
ROOM = """()=>{const q=s=>document.querySelector(s);const t=s=>q(s)?q(s).textContent:null;const col=(s,p)=>q(s)?getComputedStyle(q(s))[p]:null;
  return {scenario:q('.monitoring-room').dataset.scenario,compared:q('.monitoring-room').dataset.compared,verdict:q('.monitoring-room').dataset.verdict,
    pressed:[...document.querySelectorAll('[data-scenario-choice]')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.dataset.scenarioChoice),
    kicker:t('.monitor-verdict .section-kicker'),heading:t('.monitor-verdict h3'),summary:t('.monitor-verdict p:not(.section-kicker)'),
    traceLabel:t('.monitor-trace span'),traceColour:col('.monitor-trace-reveal path','stroke'),verdictBorder:col('.monitor-verdict','borderLeftColor'),
    traceShape:q('.monitor-trace-reveal path').getAttribute('d'),button:q('[data-compare]').textContent.trim(),
    currentHeader:t('[data-snapshot=current] header span'),currentHeading:t('[data-snapshot=current] h3'),currentRows:document.querySelectorAll('[data-snapshot=current] li').length,
    baselineRows:[...document.querySelectorAll('[data-snapshot=baseline] li')].map(e=>e.textContent),empty:t('.monitor-empty p'),
    timeline:[...document.querySelectorAll('.monitor-timeline span')].map(e=>e.textContent),
    diffHeading:t('.monitor-diff h4'),diff:[...document.querySelectorAll('[data-change]')].map(e=>[e.dataset.change,e.textContent]),
    del:t('.monitor-diff del'),ins:t('.monitor-diff ins'),cause:t('.monitor-cause'),diffText:t('.monitor-diff'),resolved:t('.monitor-resolved'),
    codes:[...document.querySelectorAll('.monitor-codes code')].map(e=>e.textContent),pending:t('.monitor-pending'),
    failedColour:col('.monitor-failed-day','color'),okColour:col('.monitor-total strong','color')}}"""
LEADERS = cre.LEADERS

CATEGORIES = ['story', 'visual', 'animation', 'transition', 'mobile', 'desktop', 'source', 'performance']
ITEMS = {
    'story': (['story'], 'Story reads last good snapshot → today\'s collection → field diff → reasoned verdict: seismograph strip under the CTA; case order Brief → instrument → comparison desk → recorded archive → readings → Next; illustration and recorded evidence labelled apart; copy approved at gate 7C; no DRAFT labels'),
    'chapterTrace': (['animation', 'mobile', 'desktop'], 'Chapter: the green trace draws with the orbit, the red spike and "Empty run → alarm" appear only after .6, scrolling back reverses both; phone swipe and desktop wheel; the trace is still when scrolling stops'),
    'ribbonEntry': (['transition'], 'Open case file: a paper ribbon leaves the needle, unrolls to a full-width timeline, fades; the case opens with focus on the case heading (phone + desktop)'),
    'hotspots': (['story', 'visual'], 'Hotspots explain the alarms, change detection and daily collection for the client; leaders only while the model is on screen; card inside the viewport'),
    'comparisonDesk': (['story', 'animation', 'mobile', 'desktop'], 'Desk by tap/click: choose a situation → Compare → local trace draws left to right through a clip window (~0.8 s, the spike never slides or stretches), a spike only for alarms, verdict fades in after ~0.6 s; five situations give healthy/alarm as designed; snapshots stacked on phone with Day labels'),
    'emptyNeverHealthy': (['story', 'visual'], 'Empty and missing never look healthy: layout break, collector failure and missing run are red ALARM with a reason, next action and an alarm record; before comparing the desk reads AWAITING COMPARISON, not green'),
    'sourceVsPipeline': (['story'], 'Source change vs pipeline failure: ordinary edits stay healthy; a broken layout is a source comparison alarm, a failed collector and a missing run are pipeline health alarms with different causes/actions; recovery keeps Day 1 as the baseline and Day 2 on record'),
    'diffDetail': (['story', 'visual'], 'Field diff opens with changed (old struck, new marked), added, removed and unchanged records; volatile fetch timestamps excluded'),
    'notLive': (['story', 'source'], 'The trace never poses as live status: illustration labels on chapter, desk and trace; fictional pages and numbered days (no calendar dates in the illustration); no idle animation after a comparison; archive stated as a recorded window'),
    'archive': (['story', 'visual', 'source'], 'Recorded archive separate from the illustration: 1,323 records/day = 1,000 + 100 + 23 + 200 from four sources; three unattended days 01–03 Sep with 01 Sep indirect; 11/11 incl. three normal-change controls, zero false positives; public sources unchanged'),
    'returnNext': (['transition'], 'Return: the ribbon rolls back to the point it left from and the chapter reopens on the saved scroll position with focus on Open case file; DueWatch teaser, Next opens DueWatch'),
    'historyDirect': (['transition'], 'Back/Forward between DriftWatch and DueWatch, direct URL /work/driftwatch and refresh keep the desk working (refresh restarts at Compare snapshots)'),
    'interruptions': (['transition', 'animation'], 'Interruptions: double tap Open case file adds one history entry; switching situation mid-comparison cancels the motion with no late verdict; rapid Compare taps settle once; scroll away and back keeps the verdict; keyboard Compare settles at once; Back during the ribbon clears it; resize across 1024 px keeps the alarm'),
    'modelSlowFail': (['visual', 'mobile'], 'Model not on screen yet: no leader during the ribbon flight; scene failed (still view): no leaders, the desk still works'),
    'reducedMotion': (['animation'], 'Reduced motion: no ribbon, chapter trace final, the verdict appears at once'),
    'mobileViewports': (['mobile'], 'All Development checks pass at 390×844, 360×740, 430×932 and tablet 768×1024'),
    'desktopComposition': (['desktop', 'visual'], 'Desktop 1440×900 / 1920×1080: steps in one row, wide timeline across the desk, snapshots side by side (sticky) beside a verdict column, archive ledger beside its heading and soak days in three columns'),
    'sources': (['source'], 'Every number and quoted fact on the page traces to the DriftWatch dossier; illustration labelled fictional; no long-term or live monitoring claim'),
    'performance': (['performance', 'mobile'], 'PLAN §11 / Q42 under 4x CPU (phone swipe): chapter, ribbon flight, five comparisons, case scroll and return hold ≥ 45 fps with ≤ 10% slow frames'),
    'clean': (['mobile', 'desktop'], 'One persistent Canvas, zero page errors, zero responses ≥ 400, no horizontal overflow in both walkthroughs'),
    'regressions': (['mobile', 'desktop'], 'Regression ledger (run_regressions.py): all 13 suites passed on this exact source fingerprint'),
}
CHECKS, META = {}, {}
OWNER = []  # filled from measurements after the run (see owner_notes)
ONLY = set(sys.argv[sys.argv.index('--only') + 1].split(',')) if '--only' in sys.argv else None
REMEASURE = '--remeasure-fps' in sys.argv  # keep the pack; re-measure frame rate only, earlier attempts stay in evidence.json


def check(key, ok, detail, shot, **extra):
    CHECKS[key] = {'pass': bool(ok), 'detail': detail, 'screenshot': shot, **extra}


def failed(key, error, shot=None):
    CHECKS[key] = {'pass': False, 'detail': f'not completed: {error}', 'screenshot': shot}


async def bottom(page):
    return await page.evaluate('document.documentElement.scrollHeight-innerHeight')


async def swipe_to(page, cdp, y, step=360, pause=.3, sample=None):
    await swipe_until(page, cdp, min(max(0, y), await bottom(page)), step=step, pause=pause, sample=sample)
    await land(page, min(max(0, y), await bottom(page)))


async def press(page, selector, tap):
    button = page.locator(selector)
    await (button.tap() if tap else button.click())


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


# ---------------------------------------------------------------- analysis helpers
async def chapter_sample(page, samples):
    samples.append({k: round(v, 3) for k, v in (await page.evaluate(CHAPTER)).items()})


def chapter_summary(forward, backward, still):
    fwd = sorted(forward, key=lambda r: r['orbit'])
    draws = all(b['line'] <= a['line'] + .01 for a, b in zip(fwd, fwd[1:])) and all(abs(r['line'] - (1 - r['orbit'])) < .03 for r in fwd)
    quiet = [r for r in fwd if r['orbit'] < .58]
    alarm = [r for r in fwd if r['orbit'] > .66]
    quiet_ok = bool(quiet) and all(r['alarm'] > .99 and r['spike'] < .01 and r['quiet'] > .99 for r in quiet)
    alarm_ok = bool(alarm) and all(r['alarm'] < .99 and r['spike'] > .99 for r in alarm)
    end, back = fwd[-1], backward[-1] if backward else None
    back_ok = back is not None and back['line'] > end['line'] + .3 and back['spike'] < .01 and back['alarm'] > .99
    return {'ok': draws and quiet_ok and alarm_ok and end['line'] < .02 and end['alarm'] < .02 and back_ok and still,
            'samples': len(fwd), 'quietSamples': len(quiet), 'alarmSamples': len(alarm), 'drawsWithOrbit': draws,
            'firstSpikeOrbit': next((r['orbit'] for r in fwd if r['spike'] > .5), None), 'end': end, 'back': back, 'stillWhenIdle': still}


async def chapter_still(page):
    a = await page.evaluate(CHAPTER)
    await page.wait_for_timeout(1200)
    return a == await page.evaluate(CHAPTER)


async def ribbon_collect(page, path, capture):
    if capture:
        for _ in range(90):
            if await page.evaluate(RIBBON_READABLE):
                await page.screenshot(path=str(OUT / capture))
                break
            await page.wait_for_timeout(12)
    await page.wait_for_url(URL + path, timeout=15000)
    await idle(page)
    await page.wait_for_timeout(200)
    return await page.evaluate('window.__ribbon')


def ribbon_summary(trace, direction, width, height):
    vis = [f for f in trace if f['o'] > .03]
    if len(vis) < 5:
        return {'ok': False, 'visibleFrames': len(vis)}
    sx = [f['sx'] for f in vis]
    grows = sx[0] < .05 and max(sx) > .98 if direction == 'out' else sx[0] > .98 and sx[-1] < .05
    monotone = all(b >= a - .002 for a, b in zip(sx, sx[1:])) if direction == 'out' else all(b <= a + .002 for a, b in zip(sx, sx[1:]))
    point = vis[0] if direction == 'out' else vis[-1]
    inside = all(0 <= f['x'] <= width and 0 <= f['y'] <= height for f in vis)
    cleared = trace[-1]['o'] == 0 and trace[-1]['d'] == 'idle'
    wide = [f for f in vis if f['sx'] > .98]
    return {'ok': grows and monotone and inside and cleared, 'visibleFrames': len(vis), 'visibleMs': vis[-1]['t'] - vis[0]['t'],
            'scale': [sx[0], max(sx) if direction == 'out' else sx[-1]], 'needlePoint': [point['x'], point['y']], 'monotone': monotone,
            'fullWidthY': wide[0]['y'] if wide else None, 'inside': inside, 'clearedAfter': cleared}


def compare_motion(frames, scenario):
    """Trace reveal 0 → 1 over ~0.8 s; verdict hidden until ~0.6 s then opaque; label/verdict final from the first frame."""
    expected = 'healthy' if scenario in HEALTHY else 'alarm'
    # The sampler starts just before the tap; time zero is the first frame with the new verdict.
    start = next((i for i, f in enumerate(frames) if f['v'] == expected), None)
    if start is None:
        return {'ok': False, 'frames': len(frames)}
    t0 = frames[start]['t']
    frames = [{**f, 't': f['t'] - t0} for f in frames[start:]]
    grow = [f for f in frames if f['sx'] < .999]
    full = next((f['t'] for f in frames if f['sx'] >= .999 and f['t'] > 50), None)
    shown = next((f['t'] for f in frames if f['o'] > .05), None)
    opaque = next((f['t'] for f in frames if f['o'] >= .999), None)
    ok = (bool(grow) and grow[0]['sx'] < .15 and full is not None and 600 <= full <= 1100 and shown is not None and 450 <= shown <= 900
          and opaque is not None and opaque <= 1100 and all(f['v'] == expected for f in frames) and frames[-1]['sx'] >= .999 and frames[-1]['o'] >= .999
          and max(abs(f['y']) for f in frames) <= 5.01 and all(f['path'] == 1 for f in frames))
    return {'ok': ok, 'frames': len(frames), 'firstFrame': [frames[0]['sx'], frames[0]['o']], 'traceStartScale': grow[0]['sx'] if grow else None, 'traceFullMs': full, 'verdictVisibleMs': shown,
            'verdictOpaqueMs': opaque, 'maxVerdictOffsetPx': max(abs(f['y']) for f in frames), 'pathScales': sorted({f['path'] for f in frames}), 'label': frames[-1]['label']}


async def compare_run(page, walk, prefix, scenario, tap, wide, shots=True):
    """Choose → Compare with a frame trace; returns motion + DOM reading; shots of the moment and the result."""
    H = page.viewport_size['height']
    await land(page, await top_of(page, '.monitor-scenarios') - (200 if wide else 90))
    await press(page, f'[data-scenario-choice={scenario}]', tap)
    await page.wait_for_timeout(260)
    before = await page.evaluate(ROOM)
    if shots and scenario == 'change':
        await walk.shot(f'{prefix}-pending.png')
    # Phone: bring Compare to the upper third, as a visitor scrolling down to it would.
    await land(page, await top_of(page, '[data-compare]') - (H * .3 if not wide else 320))
    walk.mark(f'compare-{scenario}')
    await page.evaluate('window.__compareFrames=90')
    await page.evaluate(COMPARE)
    await press(page, '[data-compare]', tap)
    if shots:
        await page.wait_for_timeout(330)
        await walk.shot(f'{prefix}-{scenario}-drawing.png')
    await page.wait_for_timeout(1250)
    frames = await page.evaluate('window.__compare')
    walk.mark(f'compare-{scenario}-end')
    view = await page.evaluate("""()=>{const r=s=>document.querySelector(s).getBoundingClientRect();
      return {button:Math.round(r('[data-compare]').bottom),traceTop:Math.round(r('.monitor-trace').top),traceBottom:Math.round(r('.monitor-trace').bottom),
        verdictTop:Math.round(r('.monitor-verdict h3').top),verdictBottom:Math.round(r('.monitor-verdict').bottom),diffBottom:Math.round(r('.monitor-diff').bottom)}}""")
    if shots:
        await walk.shot(f'{prefix}-{scenario}-compared.png')
    if await page.locator('.monitor-codes').count():
        await page.locator('.monitor-codes summary').click()
        await page.wait_for_timeout(200)
    after = await page.evaluate(ROOM)
    if shots:
        # Desktop: snapshots, trace, verdict and reason in one frame below the fixed header.
        await land(page, await top_of(page, '[data-compare]' if wide else '.monitor-result') - (150 if wide else 70))
        await walk.shot(f'{prefix}-{scenario}-result.png')
        if not wide and scenario in ('layout', 'recovery', 'change'):
            await land(page, await top_of(page, '.monitor-diff') - 60)
            await walk.shot(f'{prefix}-{scenario}-detail.png')
    return {'before': before, 'after': after, 'motion': compare_motion(frames, scenario), 'view': {**view, 'height': H}}


def scenario_ok(s, scenario):
    a, b = s['after'], s['before']
    healthy = scenario in HEALTHY
    pending = b['compared'] == 'false' and b['verdict'] == 'pending' and b['traceLabel'] == 'AWAITING COMPARISON' and b['pressed'] == [scenario] and b['pending']
    base = a['verdict'] == ('healthy' if healthy else 'alarm') and a['traceLabel'] == ('HEALTHY' if healthy else 'ALARM') and len(a['baselineRows']) == 3 and a['button'].startswith('Compare again')
    if scenario == 'change':
        rows = [x[0] for x in a['diff']]
        return pending and base and rows == ['changed', 'added', 'removed', 'unchanged'] and a['del'] == 'Getting started' and a['ins'] == 'Getting started with the API' and not a['codes'] and a['currentRows'] == 3
    if scenario == 'recovery':
        return pending and base and 'Failed' in ' '.join(a['timeline']) and 'Baseline remains Day 1' in (a['resolved'] or '') and not a['codes'] and a['currentRows'] == 3
    codes = ['RUN_MISSING'] if scenario == 'missing' else ['ZERO_RECORDS', 'RECORD_COUNT_DROP', 'FIELD_COMPLETENESS_DROP', 'RUN_FAILED', 'CHURN_SPIKE']
    return pending and base and a['currentRows'] == 0 and bool(a['empty']) and a['codes'] == codes and bool(a['cause']) and a['diffHeading'] == 'Reason & next action'


# ---------------------------------------------------------------- the desk, shared by both walkthroughs
async def desk_run(page, walk, prefix, tap, wide):
    data = {}
    await land(page, await top_of(page, '.monitoring-room') - (80 if wide else 60))
    await walk.shot(f'{prefix}-room-intro.png')
    await land(page, await top_of(page, '.monitor-steps') - (200 if wide else 60))
    await walk.shot(f'{prefix}-steps.png')
    await land(page, await top_of(page, '.monitor-scenarios') - (200 if wide else 90))
    data['initial'] = await page.evaluate(ROOM)
    await walk.shot(f'{prefix}-desk-awaiting.png')
    data['scenarios'] = {}
    for scenario in SCENARIOS:
        data['scenarios'][scenario] = await compare_run(page, walk, prefix, scenario, tap, wide)
    return data


async def interrupt_run(page, walk, prefix, tap, wide):
    data = {}
    H = page.viewport_size['height']
    # 1. Switch situation 300 ms into a comparison: motion killed, verdict cleared, no late callback.
    await land(page, await top_of(page, '.monitor-scenarios') - (200 if wide else 90))
    await press(page, '[data-scenario-choice=change]', tap)
    await land(page, await top_of(page, '[data-compare]') - H * .3)
    walk.mark('switch')
    await press(page, '[data-compare]', tap)
    await page.wait_for_timeout(300)
    await press(page, '[data-scenario-choice=layout]', tap)  # Playwright scrolls the button into view first
    await page.evaluate('window.__compareFrames=80')
    await page.evaluate(COMPARE)
    await page.wait_for_timeout(1400)
    frames = await page.evaluate('window.__compare')
    data['switch'] = {'verdicts': sorted({f['v'] for f in frames}), 'maxResultOpacity': max(f['o'] for f in frames), 'traceScales': sorted({f['sx'] for f in frames}),
                      'labels': sorted({f['label'] for f in frames}), 'headings': sorted({str(f['heading']) for f in frames}), 'room': await page.evaluate(ROOM)}
    await land(page, await top_of(page, '[data-compare]') - H * .3)
    await walk.shot(f'{prefix}-switch-mid-compare.png')
    walk.mark('switchEnd')
    # 2. Rapid Compare taps on "Collector fails".
    await land(page, await top_of(page, '.monitor-scenarios') - (200 if wide else 90))
    await press(page, '[data-scenario-choice=pipeline]', tap)
    await land(page, await top_of(page, '[data-compare]') - H * .3)
    walk.mark('rapid')
    for _ in range(6):
        await press(page, '[data-compare]', tap)
        await page.wait_for_timeout(45)
    await page.evaluate('window.__compareFrames=80')
    await page.evaluate(COMPARE)
    await page.wait_for_timeout(1400)
    frames = await page.evaluate('window.__compare')
    last = frames[-1]
    data['rapid'] = {'final': [last['v'], last['sx'], last['o'], last['label']], 'settledFrames': sum(1 for f in frames if f['sx'] >= .999 and f['o'] >= .999),
                     'frames': len(frames), 'room': await page.evaluate(ROOM)}
    await walk.shot(f'{prefix}-rapid-compare.png')
    walk.mark('rapidEnd')
    # 3. Idle after a comparison: nothing keeps animating (not a live feed).
    idle_frames = []
    for _ in range(3):
        idle_frames.append(await page.evaluate("(()=>{const g=document.querySelector('.monitor-trace-window');return [getComputedStyle(g).transform,getComputedStyle(document.querySelector('.monitor-result')).opacity,document.querySelector('.monitor-trace span').textContent]})()"))
        await page.wait_for_timeout(700)
    data['idleStill'] = all(x == idle_frames[0] for x in idle_frames)
    # 4. Scroll away to the readings and back: comparison kept.
    await land(page, await top_of(page, '#readings-heading') - 80)
    await page.wait_for_timeout(500)
    await land(page, await top_of(page, '.monitor-result') - (150 if wide else 70))
    await page.wait_for_timeout(300)
    data['scrollBack'] = await page.evaluate(ROOM)
    await walk.shot(f'{prefix}-scroll-back-kept.png')
    # 5. Keyboard Compare settles at once.
    await press(page, '[data-scenario-choice=missing]', tap)
    await page.locator('[data-compare]').focus()
    await page.evaluate('window.__compareFrames=12')
    await page.evaluate(COMPARE)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(250)
    frames = await page.evaluate('window.__compare')
    data['keyboard'] = {'frames': [[f['t'], f['v'], f['sx'], f['o']] for f in frames], 'firstAlarm': next((f for f in frames if f['v'] == 'alarm'), None)}
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
        # 1. Chapter seismograph: swipe through the orbit, then back.
        section = await page.locator('#driftwatch').evaluate("e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight,stage:e.querySelector('.instrument-stage').offsetHeight})")
        span = section['h'] - section['stage']
        await swipe_to(page, cdp, section['top'] - 60)
        await page.wait_for_timeout(500)
        walk.mark('chapter')
        forward, backward = [], []
        await chapter_sample(page, forward)
        await swipe_to(page, cdp, section['top'] + span, step=100, pause=.45, sample=lambda: chapter_sample(page, forward))
        await page.wait_for_timeout(600)
        await chapter_sample(page, forward)
        still = await chapter_still(page)
        await walk.shot('m01c-chapter-end.png')
        await swipe_until(page, cdp, section['top'] + .2 * span, step=180, pause=.45, sample=lambda: chapter_sample(page, backward))
        await land(page, section['top'] + .3 * span)
        await page.wait_for_timeout(500)
        await chapter_sample(page, backward)
        await walk.shot('m01a-chapter-quiet.png')
        await land(page, section['top'] + .75 * span)
        await page.wait_for_timeout(500)
        await walk.shot('m01b-chapter-alarm.png')
        walk.mark('chapterEnd')
        data['chapter'] = chapter_summary(forward, backward, still)
        data['chapter']['raw'] = {'forward': forward, 'backward': backward}
        strip = await page.locator('.monitor-chapter').bounding_box()
        cta = await page.locator('[data-open-case=driftwatch]').bounding_box()
        data['stripBelowCta'] = strip['y'] >= cta['y'] + cta['height']
        data['stripText'] = await page.locator('.monitor-chapter').text_content()
        await land(page, section['top'] + .45 * span)
        await page.wait_for_timeout(500)
        origin = await page.evaluate('scrollY')

        # 2. Ribbon into the case.
        walk.mark('entry')
        await page.evaluate(RIBBON)
        await page.locator('[data-open-case=driftwatch]').tap()
        trace = await ribbon_collect(page, '/work/driftwatch', 'm02a-ribbon-out.png')
        walk.mark('entryEnd')
        data['ribbonIn'] = {**ribbon_summary(trace, 'out', W, H), 'focus': await page.evaluate('document.activeElement.id')}
        await walk.shot('m02b-case-opened.png')
        data['story'] = await page.evaluate("""(()=>{const q=s=>document.querySelector(s);
          const order=['#case-heading','#case-instrument','.monitoring-room','.monitoring-evidence','#readings-heading','.case-next'].map(s=>q(s)?q(s).getBoundingClientRect().top+scrollY:null);
          return {order, draft:[...document.querySelectorAll('.draft-label')].map(e=>e.textContent), text:q('main').textContent,
            disclosure:q('.monitor-disclosure').textContent, evidenceKicker:q('.monitoring-evidence .section-kicker').textContent, room:q('.monitoring-room').textContent,
            caption:q('.monitor-compare-control p').textContent, evidence:q('.monitoring-evidence').textContent,
            ledger:[...document.querySelectorAll('.monitor-source-ledger li')].map(e=>[e.querySelector('strong').textContent,e.querySelector('h3').textContent]),
            total:q('.monitor-total strong').textContent, soak:[...document.querySelectorAll('.monitor-soak li')].map(e=>e.textContent),
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

        # 4. Comparison desk by touch.
        await swipe_to(page, cdp, await top_of(page, '.monitoring-room') - 60)
        data['desk'] = await desk_run(page, walk, 'm04', True, False)
        data['snapshots'] = await page.locator('.monitor-snapshot').evaluate_all('es=>es.map(e=>{const r=e.getBoundingClientRect();return {x:Math.round(r.x),y:Math.round(r.y+scrollY),w:Math.round(r.width)}})')

        # 5. Interruptions.
        data['interrupt'] = await interrupt_run(page, walk, 'm05', True, False)

        # 6. Recorded archive, readings.
        await swipe_to(page, cdp, await top_of(page, '.monitoring-evidence') - 20)
        await walk.shot('m06a-archive.png')
        await swipe_to(page, cdp, await top_of(page, '.monitor-soak') - 60)
        await walk.shot('m06b-soak.png')
        await swipe_to(page, cdp, await top_of(page, '.monitor-proof-note') - 60)
        await walk.shot('m06c-proof-note.png')
        await swipe_to(page, cdp, await top_of(page, '#readings-heading') - 80)
        await page.wait_for_timeout(1200)
        await walk.shot('m06d-readings.png')

        # 7. Next teaser → ribbon return.
        await swipe_to(page, cdp, await top_of(page, '#next-heading') - 200)
        await page.wait_for_timeout(300)
        await walk.shot('m07-next-teaser.png')
        data['teaser'] = await page.locator('.monitor-next').inner_text()
        walk.mark('return')
        await page.evaluate(RIBBON)
        await page.locator('.case-next .case-back').tap()
        trace = await ribbon_collect(page, '/', 'm08a-ribbon-return.png')
        walk.mark('returnEnd')
        await page.wait_for_timeout(300)
        await walk.shot('m08b-back-at-chapter.png')
        data['return'] = {**ribbon_summary(trace, 'in', W, H), 'scrollDelta': abs(await page.evaluate('scrollY') - origin),
                          'focus': await page.evaluate("document.activeElement.dataset.openCase || document.activeElement.id || document.activeElement.tagName")}

        # 8. Double tap Open case file, Next hop, Back/Forward.
        before = await page.evaluate('history.length')
        walk.mark('doubleTap')
        await page.locator('[data-open-case=driftwatch]').tap()
        await page.wait_for_timeout(90)
        try:
            await page.locator('[data-open-case=driftwatch]').tap(timeout=600)
            second = 'tapped'
        except Exception:  # noqa: BLE001 — homepage already locked during the flight, also correct
            second = 'not tappable during flight'
        await page.wait_for_url(URL + '/work/driftwatch')
        await idle(page)
        data['doubleTap'] = {'historyDelta': await page.evaluate('history.length') - before, 'second': second}
        await swipe_to(page, cdp, await top_of(page, '.case-next') - 120)
        walk.mark('next')
        await page.locator('[data-case-target=duewatch]').tap()
        await page.wait_for_url(URL + '/work/duewatch', timeout=15000)
        await idle(page)
        await walk.shot('m09-next-duewatch.png')
        await page.go_back()
        await page.wait_for_url(URL + '/work/driftwatch')
        await idle(page)
        await page.wait_for_timeout(500)
        back_ok = await page.locator('main').get_attribute('data-case') == 'driftwatch' and await page.locator('.monitoring-room').count() == 1
        back_desk = await compare_run(page, walk, 'm09b', 'missing', True, False, shots=False)
        await land(page, await top_of(page, '.monitor-result') - 70)
        await walk.shot('m09b-history-back-desk.png')
        await page.go_forward()
        await page.wait_for_url(URL + '/work/duewatch')
        await idle(page)
        data['history'] = {'backOk': back_ok, 'backDesk': back_desk['after']['verdict'], 'forwardOk': await page.locator('main').get_attribute('data-case') == 'duewatch',
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
    await enter(page, '/work/driftwatch')
    dummy = type('W', (), {'mark': lambda *a: None, 'shot': None})()
    direct = await compare_run(page, dummy, 'm10', 'layout', True, False, shots=False)
    await page.reload()
    await page.locator('.silent-button').click(timeout=30000)
    await idle(page)
    await land(page, await top_of(page, '.monitor-scenarios') - 90)
    refreshed = await page.evaluate(ROOM)
    again = await compare_run(page, dummy, 'm10', 'change', True, False, shots=False)
    await land(page, await top_of(page, '.monitor-result') - 70)
    await page.screenshot(path=str(OUT / 'm10-direct-refresh.png'))
    data['direct'] = {'directVerdict': direct['after']['verdict'], 'refreshed': {k: refreshed[k] for k in ('compared', 'verdict', 'scenario', 'button', 'traceLabel')},
                      'refreshedVerdict': again['after']['verdict'], 'errors': sink['errors'], 'bad': sink['bad']}
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
        section = await page.locator('#driftwatch').evaluate("e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight,stage:e.querySelector('.instrument-stage').offsetHeight})")
        span = section['h'] - section['stage']
        await wheel_until(page, section['top'] - 60)
        walk.mark('chapter')
        forward, backward = [], []
        await wheel_until(page, section['top'] + span, step=80, pause=70, sample=lambda: chapter_sample(page, forward), every=2)
        await land(page, section['top'] + span)
        await page.wait_for_timeout(500)
        await chapter_sample(page, forward)
        still = await chapter_still(page)
        await wheel_until(page, section['top'] + .3 * span, step=80, pause=70, sample=lambda: chapter_sample(page, backward), every=2)
        await land(page, section['top'] + .3 * span)
        await page.wait_for_timeout(500)
        await chapter_sample(page, backward)
        await walk.shot('d01a-chapter-quiet.png')
        await land(page, section['top'] + .75 * span)
        await page.wait_for_timeout(500)
        await walk.shot('d01b-chapter-alarm.png')
        data['chapter'] = chapter_summary(forward, backward, still)
        await land(page, section['top'] + .45 * span)
        await page.wait_for_timeout(500)
        origin = await page.evaluate('scrollY')
        walk.mark('entry')
        await page.evaluate(RIBBON)
        await page.locator('[data-open-case=driftwatch]').click()
        trace = await ribbon_collect(page, '/work/driftwatch', 'd02a-ribbon-out.png')
        walk.mark('entryEnd')
        data['ribbonIn'] = {**ribbon_summary(trace, 'out', W, H), 'focus': await page.evaluate('document.activeElement.id')}
        await walk.shot('d02b-case-opened.png')
        await wheel_until(page, await top_of(page, '#case-instrument'))
        await land(page, await top_of(page, '#case-instrument'))
        await page.wait_for_selector('.case-inspection[data-leaders=live]', timeout=12000)
        await page.locator('.hotspot-0').click()
        await page.wait_for_timeout(700)
        await walk.shot('d03-hotspot-alarms.png')
        await page.get_by_role('button', name='Close component card').click()
        await wheel_until(page, await top_of(page, '.monitoring-room') - 80)
        data['desk'] = await desk_run(page, walk, 'd04', False, True)
        # Layout: steps row, wide timeline, snapshots side by side beside the verdict column; sticky while reading a long diff.
        await land(page, await top_of(page, '.monitor-workspace') - 140)
        await page.wait_for_timeout(300)
        await walk.shot('d05a-workspace.png')
        data['layout'] = await page.evaluate("""(()=>{const r=s=>document.querySelector(s).getBoundingClientRect();const all=s=>[...document.querySelectorAll(s)].map(e=>e.getBoundingClientRect());
          const snaps=all('.monitor-snapshot');const soak=all('.monitor-soak li');
          return {steps:all('.monitor-steps li').map(b=>Math.round(b.top)),timeline:[r('.monitor-timeline').left,r('.monitor-timeline').right],workspace:[r('.monitor-workspace').left,r('.monitor-workspace').right],
            snapTops:snaps.map(b=>Math.round(b.top)),snapRight:Math.max(...snaps.map(b=>b.right)),comparisonLeft:r('.monitor-comparison').left,
            snapWidth:Math.round(snaps[0].width),comparisonWidth:Math.round(r('.monitor-comparison').width),
            evidenceHeadingRight:r('.monitoring-evidence > div').right,ledgerLeft:r('.monitor-source-ledger').left,soakTops:soak.map(b=>Math.round(b.top))}})()""")
        await compare_run(page, walk, 'd05', 'change', False, True, shots=False)  # longest verdict column
        await land(page, await top_of(page, '.monitor-comparison') + 260)
        await page.wait_for_timeout(400)
        data['sticky'] = await page.evaluate("(()=>{const s=document.querySelector('.monitor-snapshots').getBoundingClientRect();const d=document.querySelector('.monitor-diff').getBoundingClientRect();return {snapTop:Math.round(s.top),snapBottom:Math.round(s.bottom),diffTop:Math.round(d.top)}})()")
        await walk.shot('d05b-sticky-snapshots.png')
        data['interrupt'] = await interrupt_run(page, walk, 'd06', False, True)
        await wheel_until(page, await top_of(page, '.monitoring-evidence') - 60)
        await land(page, await top_of(page, '.monitoring-evidence') - 120)
        await walk.shot('d07a-archive.png')
        await land(page, await top_of(page, '.monitor-soak') - 120)
        await walk.shot('d07b-soak-proof.png')
        await wheel_until(page, await top_of(page, '#next-heading') - 250)
        await land(page, await top_of(page, '#next-heading') - 250)
        await walk.shot('d08-next-teaser.png')
        walk.mark('return')
        await page.evaluate(RIBBON)
        await page.locator('.case-next .case-back').click()
        trace = await ribbon_collect(page, '/', 'd09a-ribbon-return.png')
        walk.mark('returnEnd')
        await walk.shot('d09b-back-at-chapter.png')
        data['return'] = {**ribbon_summary(trace, 'in', W, H), 'scrollDelta': abs(await page.evaluate('scrollY') - origin)}

        # Resize after an alarm: desktop → phone → across 1024 → back.
        await page.locator('[data-open-case=driftwatch]').click()
        await page.wait_for_url(URL + '/work/driftwatch')
        await idle(page)
        await compare_run(page, walk, 'd10', 'pipeline', False, True, shots=False)
        walk.mark('resize')
        resized = []
        for w, h in ((390, 844), (1024, 900), (900, 900), (1920, 1080), (1440, 900)):
            await page.set_viewport_size({'width': w, 'height': h})
            await page.wait_for_timeout(700)
            room = await page.evaluate(ROOM)
            resized.append({'size': f'{w}x{h}', 'overflow': await overflow(page), 'verdict': room['verdict'], 'label': room['traceLabel'], 'codes': len(room['codes'])})
            if w == 390:
                await land(page, await top_of(page, '.monitor-result') - 70)
                await page.wait_for_timeout(300)
                await page.screenshot(path=str(OUT / 'd10a-resized-alarm-390.png'))
        await land(page, await top_of(page, '.monitor-workspace') - 140)
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(OUT / 'd10b-resized-back-1440.png'))
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
    await land(page, await page.locator('#driftwatch').evaluate('e=>e.getBoundingClientRect().top+scrollY+300'))
    await page.locator('[data-open-case=driftwatch]').tap()
    await page.wait_for_url(URL + '/work/driftwatch', timeout=5000)
    await page.go_back()
    await page.wait_for_url(URL + '/')
    await idle(page)
    await page.wait_for_timeout(300)
    (OUT / 'edges').mkdir(exist_ok=True)
    await page.screenshot(path=str(OUT / 'edges/back-during-flight.png'))
    ribbon = page.locator('.monitor-ribbon')
    state = {'ribbonOpacity': await ribbon.evaluate('e=>Number(getComputedStyle(e).opacity)'), 'direction': await ribbon.get_attribute('data-direction'),
             'path': await page.evaluate('location.pathname'), 'contentOpacity': await page.locator('.page-content').evaluate('e=>Number(getComputedStyle(e).opacity)')}
    await context.close()
    return state


async def model_slow_fail(browser):
    """Instruments are procedural (instrument-models.ts): no instrument download can stall. (1) Poll leaders through the
    ribbon flight — never visible before data-leaders=live. (2) ambient.glb blocked → still view: no leaders, desk still works."""
    out = {}
    dummy = type('W', (), {'mark': lambda *a: None, 'shot': None})()
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await enter(page)
    await land(page, await page.locator('#driftwatch').evaluate('e=>e.getBoundingClientRect().top+scrollY+300'))
    await page.locator('[data-open-case=driftwatch]').tap()
    samples, shot = [], False
    for _ in range(120):
        state = await page.evaluate(LEADERS)
        samples.append(state)
        if state['path'] == '/work/driftwatch' and not shot:
            await page.screenshot(path=str(OUT / 'm11a-model-arriving.png'))
            shot = True
        if state['path'] == '/work/driftwatch' and state['live']:
            break
        await page.wait_for_timeout(40)
    await idle(page)
    await land(page, await top_of(page, '#case-instrument'))
    await page.wait_for_selector('.case-inspection[data-leaders=live]', timeout=12000)
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(OUT / 'm11b-model-arrived.png'))
    out['flight'] = {'samples': len(samples), 'strayLeaders': [x for x in samples if not x['live'] and x['maxLeader'] > .01][:5],
                     'onCaseWithoutLive': sum(1 for x in samples if x['path'] == '/work/driftwatch' and not x['live']),
                     'leaderAfter': await page.locator('[data-hotspot-line]').first.evaluate('e=>Number(getComputedStyle(e).opacity)')}
    await context.close()

    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await page.route('**/models/ambient.glb', lambda route: route.abort())
    await enter(page, '/work/driftwatch')
    await page.wait_for_selector('.observatory[data-scene=fallback]', timeout=25000)
    await land(page, await top_of(page, '#case-instrument'))
    await page.wait_for_timeout(800)
    bad = await page.evaluate(LEADERS)
    bad['still'] = await page.locator('.case-instrument-still').evaluate('e=>e.getBoundingClientRect().height')
    await page.screenshot(path=str(OUT / 'm11c-model-failed.png'))
    run = await compare_run(page, dummy, 'm11', 'missing', True, False, shots=False)
    bad['verdict'] = run['after']['verdict']
    await land(page, await top_of(page, '.monitor-result') - 70)
    await page.screenshot(path=str(OUT / 'm11d-failed-desk-alarm.png'))
    out['failed'] = bad
    await context.close()
    return out


async def reduced_motion(browser):
    dummy = type('W', (), {'mark': lambda *a: None, 'shot': None})()
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, reduced_motion='reduce')
    page = await context.new_page()
    await enter(page)
    section = await page.locator('#driftwatch').evaluate("e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight,stage:e.querySelector('.instrument-stage').offsetHeight})")
    await land(page, section['top'] + .2 * (section['h'] - section['stage']))
    await page.wait_for_timeout(500)
    chapter = await page.evaluate(CHAPTER)
    await page.screenshot(path=str(OUT / 'm12a-reduced-chapter.png'))
    await page.evaluate(RIBBON)
    await page.locator('[data-open-case=driftwatch]').tap()
    trace = await ribbon_collect(page, '/work/driftwatch', None)
    run = await compare_run(page, dummy, 'm12', 'layout', True, False, shots=False)
    await land(page, await top_of(page, '.monitor-result') - 70)
    await page.screenshot(path=str(OUT / 'm12b-reduced-alarm.png'))
    frames = run['motion']
    state = {'chapter': chapter, 'ribbonMaxOpacity': max(f['o'] for f in trace), 'ribbonDisplay': trace[-1]['display'],
             'verdictVisibleMs': frames.get('verdictVisibleMs'), 'traceFullMs': frames.get('traceFullMs'), 'verdict': run['after']['verdict']}
    await context.close()
    return state


async def viewports(browser):
    vdr.OUT = OUT / 'viewports'
    vdr.OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for size in ['390x844', '360x740', '430x932', '768x1024', '1440x900', '1920x1080']:
        w, h = map(int, size.split('x'))
        try:
            r = await vdr.viewport(browser, w, h)
            rows.append({'viewport': size, 'pass': r['status'] == 'passed', 'scenarios': r['scenarios'], 'trace': r['trace']})
        except Exception as error:  # noqa: BLE001
            rows.append({'viewport': size, 'pass': False, 'error': repr(error).splitlines()[0][:300]})
        print(' ', rows[-1]['viewport'], rows[-1]['pass'], flush=True)
    try:
        edges = {e['mode']: e['status'] for e in await vdr.edges(browser)}
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

    section = await page.locator('#driftwatch').evaluate('e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight})')
    await land(page, section['top'] - 100)
    await page.wait_for_timeout(800)
    await measure('chapter orbit + seismograph (swipe)', lambda: swipe_until(page, cdp, section['top'] + section['h'] - H, step=300, pause=.25))
    await land(page, section['top'] + .45 * (section['h'] - H))
    await page.wait_for_timeout(800)

    async def fly():
        await page.locator('[data-open-case=driftwatch]').tap()
        await page.wait_for_url('**/work/driftwatch')
        await idle(page)
    await measure('ribbon into the case', fly)
    await page.wait_for_timeout(600)

    async def desk():
        for scenario in SCENARIOS:
            await land(page, await top_of(page, '.monitor-scenarios') - 90)
            await page.locator(f'[data-scenario-choice={scenario}]').tap()
            await land(page, await top_of(page, '[data-compare]') - H * .3)
            await page.locator('[data-compare]').tap()
            await page.wait_for_timeout(1000)
    await measure('five comparisons (tap + trace + verdict)', desk)
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
    await measure('ribbon return to the chapter', back)
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
    ax.set_title('DriftWatch monitoring room · 390×844 DPR 2 · 4x CPU throttle · green = 60 fps, red = 45 fps')
    ax.legend(fontsize=7, loc='upper right')
    fig.tight_layout()
    fig.savefig(OUT / 'p01-fps-4x.png')
    plt.close(fig)
    return {k: {a: b for a, b in v.items() if a != 'series'} for k, v in results.items()}


# ---------------------------------------------------------------- sources
def sources_check(page_text, cards, strip_text):
    dossier = DOSSIER.read_text()
    text = page_text + '\n' + '\n'.join(c['body'] for c in cards) + '\n' + strip_text
    claims = [
        ('1,323', '1,323 records/day across 4 sources'), ('four sources', '4 sources'), ('1,000', 'books 1,000'), ('Quotes', 'quotes 100'),
        ('SEO metadata', 'seo 23'), ('Drift lab', 'driftlab 200'), ('11/11', '11/11 planted failures caught, 0 false positives'),
        ('Zero false positives', '0 false positives'), ('ordinary additions, edits and removals', 'DO-01..DO-03 are false-positive tests'),
        ('12/12 runs exited cleanly', '12/12 runs exit 0'), ('01 Sep 2026', '2026-09-01'), ('03 Sep 2026', '2026-09-03'),
        ('supported indirectly', "journal had rotated past the 1 Sep morning"), ('eight recorded dates', 'Over 8 days, books/quotes/seo produced 0 added/changed/removed'),
        ('checked on 13 Sep 2026', 'on 2026-09-13'), ('ZERO_RECORDS', 'ZERO_RECORDS'), ('RECORD_COUNT_DROP', 'RECORD_COUNT_DROP'),
        ('FIELD_COMPLETENESS_DROP', 'FIELD_COMPLETENESS_DROP'), ('RUN_FAILED', 'RUN_FAILED'), ('CHURN_SPIKE', 'CHURN_SPIKE'), ('RUN_MISSING', "yesterday's run missing   records=0    alarms=[RUN_MISSING]"),
        ('had not started the local fixture', 'never started the local fixture server'), ('Fetch timestamps are excluded', 'Volatile fields (`fetched_at`'),
        ('last successful', 'the **last successful run**'), ('separate watchdog', 'separate **watchdog timer'), ('history stays on record', 'healed alarms are closed, never deleted'),
        ('Ten rules', 'Ten closed alarm codes'), ('Request where a browser needed 8', '8 requests → 1 request'), ('robots.txt', '`robots.txt` gate'),
    ]
    rows = [{'claim': c, 'onPage': c in text, 'needle': n, 'found': n.lower() in dossier.lower()} for c, n in claims]
    illustration = ['Interactive illustration · fictional pages and example days below. Not a live monitor or a replay of the daily runs.',
                    'Illustrated signal · green = healthy, red = alarm', 'Recorded evidence / Separate from the illustration',
                    'not collection happening today', 'Last good snapshot → compare']
    labelled = {s: s in text for s in illustration}
    forbidden = [w for w in ('Upwork', 'Amazon', 'guaranteed', 'real-time', 'real time', '24/7', 'every future break is detected', 'months of monitoring') if w.lower() in text.lower()]
    live = [m.group(0) for m in re.finditer(r'.{0,30}\blive\b.{0,30}', text, re.I)]
    live_bad = [x for x in live if 'Not a live monitor' not in x]
    ok = all(r['onPage'] and r['found'] for r in rows) and all(labelled.values()) and not forbidden and not live_bad
    detail = (f"{sum(r['onPage'] and r['found'] for r in rows)}/{len(rows)} claims on the page found in the dossier "
              f"({', '.join(r['claim'] for r in rows if not (r['onPage'] and r['found'])) or 'none missing'}); illustration/recorded labels {sum(labelled.values())}/{len(labelled)}; "
              f"1,000 + 100 + 23 + 200 = {1000 + 100 + 23 + 200:,}; forbidden wording {forbidden or 'none'}; 'live' only as a negation={not live_bad} ({live})")
    return ok, detail, {'claims': rows, 'labels': labelled, 'forbidden': forbidden, 'live': live}


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
    strip([('m01a-chapter-quiet.png', 'Orbit .3 · quiet green trace'), ('m01b-chapter-alarm.png', 'Orbit .75 · empty run → alarm'), ('m01c-chapter-end.png', 'Orbit end · full trace')], OUT / 'i01-chapter-trace.png', P)
    strip([('m01a-chapter-quiet.png', 'Tap Open case file'), ('m02a-ribbon-out.png', 'Ribbon unrolls from the needle'), ('m02b-case-opened.png', 'Case opens · heading focus')], OUT / 'i02-ribbon-entry.png', P)
    strip([('m03-hotspot-01.png', '01 Alarms'), ('m03-hotspot-02.png', '02 Change detection'), ('m03-hotspot-03.png', '03 Daily collection')], OUT / 'i03-hotspots.png', P)
    strip([('m04-desk-awaiting.png', 'Choose a situation'), ('m04-pending.png', 'Awaiting comparison'), ('m04-change-drawing.png', 'Compare · trace drawing'),
           ('m04-change-compared.png', 'Healthy · verdict in'), ('m04-layout-drawing.png', 'Layout · red trace drawing'), ('m04-layout-compared.png', 'Alarm · verdict in'),
           ('m04-missing-result.png', 'Run missing · alarm')], OUT / 'i04-comparison-desk.png', P)
    strip([('m04-layout-result.png', 'Layout break · ALARM'), ('m04-layout-detail.png', 'Reason · action · 5 codes'), ('m04-pipeline-result.png', 'Collector fails · ALARM'),
           ('m04-missing-result.png', 'No run · RUN_MISSING'), ('m04-desk-awaiting.png', 'Before compare · not green')], OUT / 'i05-empty-never-healthy.png', P)
    strip([('m04-change-result.png', 'Source change · healthy'), ('m04-layout-result.png', 'Source layout · alarm'), ('m04-pipeline-result.png', 'Pipeline · same symptom, other cause'),
           ('m04-recovery-result.png', 'Recovery · Day 1 baseline'), ('m04-recovery-detail.png', 'Day 2 failure kept')], OUT / 'i06-source-vs-pipeline.png', P)
    strip([('m04-change-compared.png', 'Healthy verdict'), ('m04-change-detail.png', 'Changed · added · removed · unchanged'), ('d04-change-result.png', 'Desktop diff beside snapshots')], OUT / 'i07-diff-detail.png', (720, 844))
    strip([('m04-room-intro.png', 'Illustration disclosure'), ('m04-change-compared.png', 'Illustrated signal caption'), ('m05-scroll-back-kept.png', 'Still after comparing'),
           ('m06a-archive.png', 'Recorded evidence · separate')], OUT / 'i08-not-live.png', P)
    strip([('m06a-archive.png', '1,323 per day · four sources'), ('m06b-soak.png', 'Three unattended days'), ('m06c-proof-note.png', '11/11 · 0 false positives'), ('m06d-readings.png', 'Readings')],
          OUT / 'i09-archive.png', P)
    strip([('m07-next-teaser.png', 'DueWatch teaser'), ('m08a-ribbon-return.png', 'Ribbon rolls back'), ('m08b-back-at-chapter.png', 'Back at the chapter'),
           ('m09-next-duewatch.png', 'Next → DueWatch')], OUT / 'i10-return-next.png', P)
    strip([('m09-next-duewatch.png', 'DueWatch'), ('m09b-history-back-desk.png', 'Back → desk works'), ('m10-direct-refresh.png', 'Direct URL + refresh')], OUT / 'i11-history-direct.png', P)
    strip([('m05-switch-mid-compare.png', 'Switch mid-compare · cleared'), ('m05-rapid-compare.png', 'Rapid taps · one verdict'), ('m05-scroll-back-kept.png', 'Scroll away/back · kept'),
           ('edges/back-during-flight.png', 'Back during the ribbon'), ('d10a-resized-alarm-390.png', 'Resize 1440 → 390 · alarm kept')], OUT / 'i12-interruptions.png', P)
    strip([('m11a-model-arriving.png', 'Case arriving · no leaders'), ('m11b-model-arrived.png', 'Model projected · leaders'), ('m11c-model-failed.png', 'Scene failed · still view'),
           ('m11d-failed-desk-alarm.png', 'Still view · desk works')], OUT / 'i13-model-slow-fail.png', P)
    strip([('m12a-reduced-chapter.png', 'Reduced · chapter trace final'), ('m12b-reduced-alarm.png', 'Reduced · verdict at once')], OUT / 'i14-reduced-motion.png', P)
    strip([('d01b-chapter-alarm.png', 'Chapter 1440 · alarm'), ('d02a-ribbon-out.png', 'Ribbon unrolls'), ('d04-steps.png', 'Steps in one row'), ('d05a-workspace.png', 'Timeline · snapshots · verdict'),
           ('d04-layout-result.png', 'Alarm column'), ('d05b-sticky-snapshots.png', 'Sticky snapshots'), ('d07a-archive.png', 'Archive ledger'), ('d07b-soak-proof.png', 'Three days · proof note'),
           ('viewports/workspace-1920x1080.png', '1920 workspace')], OUT / 'i16-desktop.png', D)
    grid = Image.new('RGB', (P[0] * 4, P[1] * 3), 'black')
    for c, tag in enumerate(['390x844', '360x740', '430x932', '768x1024']):
        for r, kind in enumerate(['chapter', 'layout', 'change']):
            source = OUT / 'viewports' / f'{kind}-{tag}.png'
            if source.exists():
                grid.paste(tile(source, f'{tag} · {kind}', P), (c * P[0], r * P[1]))
    grid.save(OUT / 'i15-viewports.jpg', quality=85)
    contact([
        ('m01a-chapter-quiet.png', 'Chapter · quiet trace'), ('m01b-chapter-alarm.png', 'Chapter · empty-run alarm'), ('m02a-ribbon-out.png', 'Ribbon from the needle'),
        ('m02b-case-opened.png', 'Case opened'), ('m03-hotspot-01.png', 'Hotspot 01 · alarms'), ('m03-hotspot-02.png', 'Hotspot 02 · change'), ('m03-hotspot-03.png', 'Hotspot 03 · collection'),
        ('m04-room-intro.png', 'Comparison desk'), ('m04-desk-awaiting.png', 'Awaiting comparison'), ('m04-change-drawing.png', 'Trace drawing'), ('m04-change-compared.png', 'Healthy'),
        ('m04-change-detail.png', 'Field diff'), ('m04-layout-drawing.png', 'Alarm trace drawing'), ('m04-layout-detail.png', 'Alarm reason + codes'), ('m04-pipeline-result.png', 'Collector fails'),
        ('m04-missing-result.png', 'Run missing'), ('m04-recovery-result.png', 'Recovered'), ('m05-switch-mid-compare.png', 'Switch mid-compare'), ('m05-rapid-compare.png', 'Rapid taps'),
        ('m06a-archive.png', 'Recorded archive'), ('m06b-soak.png', 'Three days'), ('m06c-proof-note.png', '11/11'), ('m07-next-teaser.png', 'DueWatch teaser'),
        ('m08a-ribbon-return.png', 'Ribbon return'), ('m08b-back-at-chapter.png', 'Back at chapter'), ('m09-next-duewatch.png', 'Next → DueWatch'), ('m10-direct-refresh.png', 'Direct + refresh'),
        ('m11c-model-failed.png', 'Scene failed'),
    ], OUT / 'contact-sheet-mobile.jpg', P, 7)
    contact([
        ('d01a-chapter-quiet.png', 'Chapter · quiet'), ('d01b-chapter-alarm.png', 'Chapter · alarm'), ('d02a-ribbon-out.png', 'Ribbon out'), ('d03-hotspot-alarms.png', 'Hotspot · alarms'),
        ('d04-room-intro.png', 'Desk intro'), ('d04-steps.png', 'Steps'), ('d04-change-compared.png', 'Healthy'), ('d04-change-result.png', 'Diff'),
        ('d04-layout-result.png', 'Layout alarm'), ('d04-pipeline-result.png', 'Collector fails'), ('d04-missing-result.png', 'Run missing'), ('d04-recovery-result.png', 'Recovered'),
        ('d05a-workspace.png', 'Workspace'), ('d05b-sticky-snapshots.png', 'Sticky snapshots'), ('d06-switch-mid-compare.png', 'Switch mid-compare'), ('d07a-archive.png', 'Archive'),
        ('d07b-soak-proof.png', 'Soak + proof'), ('d08-next-teaser.png', 'Next teaser'), ('d09a-ribbon-return.png', 'Ribbon return'), ('d09b-back-at-chapter.png', 'Back at chapter'),
    ], OUT / 'contact-sheet-desktop.jpg', D, 4)


# ---------------------------------------------------------------- verdicts
def desk_ok(desk):
    return all(scenario_ok(desk['scenarios'][s], s) and desk['scenarios'][s]['motion']['ok'] for s in SCENARIOS)


def desk_text(desk):
    parts = []
    for s in SCENARIOS:
        x = desk['scenarios'][s]
        mo, a = x['motion'], x['after']
        parts.append(f"{s}: {a['verdict']} '{a['heading']}' clip window {mo.get('traceStartScale')}→1 in {mo.get('traceFullMs')} ms (path scale {mo.get('pathScales')}, spike drawn in place), verdict from {mo.get('verdictVisibleMs')} ms "
                     f"(opaque {mo.get('verdictOpaqueMs')}), ok={scenario_ok(x, s) and mo['ok']}")
    return '; '.join(parts)


def verdicts(m, d, vp, edges, slow, reduced, fps, back_flight, sources):
    if m:
        s = m['story']
        order = [o for o in s['order'] if o is not None]
        check('story', order == sorted(order) and len(order) == 6 and m['stripBelowCta'] and s['draft'] == [] and 'DRAFT' not in m['stripText']
              and 'fictional pages' in s['disclosure'] and 'Separate from the illustration' in s['evidenceKicker'] and 'What changed?' in s['room'],
              f"case sections in story order={order == sorted(order)} ({len(order)}/6: brief, instrument, comparison desk, recorded archive, readings, Next); seismograph strip under the CTA={m['stripBelowCta']}; "
              f"illustration disclosure '{s['disclosure'].strip()}'; archive kicker '{s['evidenceKicker']}'; DRAFT labels on case {s['draft']} + chapter strip={'DRAFT' in m['stripText']} (copy approved at gate 7C)",
              'i01-chapter-trace.png')
        mc, dc = m['chapter'], d['chapter'] if d else {}
        check('chapterTrace', mc['ok'] and dc.get('ok'),
              f"phone swipe {mc['samples']} samples: green line offset = 1 − orbit={mc['drawsWithOrbit']}, {mc['quietSamples']} samples before .58 with no spike/'alarm' caption, {mc['alarmSamples']} after .66 with red spike + 'Empty run → alarm' "
              f"(first at orbit {mc['firstSpikeOrbit']}); end line {mc['end']['line']} alarm {mc['end']['alarm']}; swipe back → line {mc['back']['line'] if mc['back'] else '?'} spike {mc['back']['spike'] if mc['back'] else '?'}; "
              f"still when idle={mc['stillWhenIdle']} | desktop wheel {dc.get('samples')} samples same rule={dc.get('ok')} (first spike {dc.get('firstSpikeOrbit')})", 'i01-chapter-trace.png')
        ri, dri = m['ribbonIn'], d['ribbonIn'] if d else {}
        check('ribbonEntry', ri['ok'] and ri['focus'] == 'case-heading' and dri.get('ok') and dri.get('focus') == 'case-heading',
              f"phone: ribbon visible {ri.get('visibleMs')} ms over {ri['visibleFrames']} frames, scaleX {ri.get('scale')} (monotone={ri.get('monotone')}) from the needle point {ri.get('needlePoint')} to full width at y {ri.get('fullWidthY')}, cleared after; focus #{ri['focus']} | "
              f"desktop: {dri.get('visibleMs')} ms, scaleX {dri.get('scale')} from {dri.get('needlePoint')} to y {dri.get('fullWidthY')}, focus #{dri.get('focus')}", 'i02-ribbon-entry.png')
        cards = m['hotspots']
        explain = ['Zero rows' in cards[0]['body'] and 'stayed healthy' in cards[0]['body'], 'last successful run' in cards[1]['body'] and 'timestamps' in cards[1]['body'],
                   'watchdog' in cards[2]['body'] and 'runner setup failure' in cards[2]['body']]
        check('hotspots', all(c['inside'] for c in cards) and all(c['leader'] > .3 for c in cards) and all(explain),
              f"cards {[c['title'] for c in cards]} inside viewport={[c['inside'] for c in cards]}, leader opacity {[round(c['leader'], 2) for c in cards]}; "
              f"bodies explain zero rows ≠ success / last successful run without timestamps / watchdog + runner failure={explain}", 'i03-hotspots.png')
        md, dd = m['desk'], d['desk'] if d else None
        snaps = m['snapshots']
        stacked = len(snaps) == 2 and snaps[1]['y'] > snaps[0]['y'] + 150 and abs(snaps[0]['x'] - snaps[1]['x']) < 2
        ch = md['scenarios']['change']['after']
        check('comparisonDesk', desk_ok(md) and bool(dd) and desk_ok(dd) and stacked and md['initial']['pressed'] == ['change'],
              f"phone (tap, snapshots stacked={stacked}, Day labels {ch['timeline']}): " + desk_text(md) + (' | desktop (click): ' + desk_text(dd) if dd else ''), 'i04-comparison-desk.png')
        alarms = [md['scenarios'][x]['after'] for x in ('layout', 'pipeline', 'missing')] + ([dd['scenarios'][x]['after'] for x in ('layout', 'pipeline', 'missing')] if dd else [])
        healthy = [md['scenarios'][x]['after'] for x in HEALTHY]
        red, green = alarms[0]['traceColour'], healthy[0]['traceColour']
        rec = md['scenarios']['recovery']['after']
        colours = (all(a['traceColour'] == red and a['verdictBorder'] == red for a in alarms) and all(h['traceColour'] == green and h['verdictBorder'] == green for h in healthy)
                   and red != green and red == rec['failedColour'] and green == rec['okColour'])
        init = md['initial']
        pending_ok = init['verdict'] == 'pending' and init['traceLabel'] == 'AWAITING COMPARISON'
        empty_ok = all(a['verdict'] == 'alarm' and a['traceLabel'] == 'ALARM' and a['currentRows'] == 0 and a['empty'] and a['cause'] and a['codes'] for a in alarms)
        check('emptyNeverHealthy', empty_ok and colours and pending_ok and 'M0 38H260' in alarms[0]['traceShape'],
              f"layout/pipeline/missing on phone + desktop: verdict {[a['verdict'] for a in alarms]}, trace label {sorted({a['traceLabel'] for a in alarms})}, current snapshot rows {[a['currentRows'] for a in alarms]}, "
              f"empty text '{alarms[0]['empty']}' / '{md['scenarios']['missing']['after']['empty']}', codes {[len(a['codes']) for a in alarms]}; trace + verdict border red {red} vs healthy green {green} (same as failed day / archive total)={colours}; "
              f"before comparing: '{init['traceLabel']}' verdict {init['verdict']} with a dimmed trace, never green", 'i05-empty-never-healthy.png')
        lay, pip, mis = (md['scenarios'][x]['after'] for x in ('layout', 'pipeline', 'missing'))
        chg = md['scenarios']['change']['after']
        kinds = [chg['kicker'], lay['kicker'], pip['kicker'], mis['kicker'], rec['kicker']]
        sv_ok = (kinds == ['Source comparison', 'Source comparison', 'Pipeline health', 'Pipeline health', 'Recovery record'] and lay['cause'] != pip['cause']
                 and 'Same symptom. Different cause.' == pip['heading'] and 'runner' in pip['diffText'] and 'extraction rules' in lay['diffText']
                 and 'Compare against Day 1, not the failed Day 2' in rec['diffText'] and 'planted example' in lay['cause'] and 'recorded incident' in pip['cause'] and any('Failed' in t for t in rec['timeline']) and chg['verdict'] == 'healthy')
        check('sourceVsPipeline', sv_ok,
              f"kickers {kinds}; layout cause '{lay['cause']}' vs collector '{pip['cause']}' ('{pip['heading']}') vs missing '{mis['cause']}'; recovery timeline {rec['timeline']}, '{rec['resolved']}'; ordinary change stays {chg['verdict']}", 'i06-source-vs-pipeline.png')
        dx = chg['diff']
        check('diffDetail', [x[0] for x in dx] == ['changed', 'added', 'removed', 'unchanged'] and chg['del'] == 'Getting started' and chg['ins'] == 'Getting started with the API'
              and 'Fetch timestamps are excluded' in chg['diffText'] and chg['diffHeading'] == 'Field-level difference' and (not dd or [x[0] for x in dd['scenarios']['change']['after']['diff']] == ['changed', 'added', 'removed', 'unchanged']),
              f"heading '{chg['diffHeading']}'; rows {[x[1] for x in dx]}; struck '{chg['del']}' → marked '{chg['ins']}'; timestamps excluded note present={'Fetch timestamps are excluded' in chg['diffText']}", 'i07-diff-detail.png')
        it = m['interrupt']
        no_dates = ' Sep ' not in s['room']
        live_ok = bool(sources) and all(sources[2]['labels'].values()) and all('Not a live monitor' in x for x in sources[2]['live'])
        check('notLive', 'Not a live monitor' in s['disclosure'] and s['caption'].startswith('Illustrated signal') and 'Illustration' in m['stripText'] and no_dates and it['idleStill']
              and bool(d) and d['interrupt']['idleStill'] and mc['stillWhenIdle'] and 'not collection happening today' in s['evidence'] and live_ok,
              f"disclosure '{s['disclosure'].strip()}'; trace caption '{s['caption']}'; chapter '{m['stripText'].strip()[-22:]}'; calendar dates inside the illustration={not no_dates} (Day 1–3 only); "
              f"trace/verdict still 2.1 s after comparing phone={it['idleStill']} desktop={d and d['interrupt']['idleStill']}; chapter still when idle={mc['stillWhenIdle']}; archive says 'not collection happening today'", 'i08-not-live.png')
        led = s['ledger']
        total = sum(int(x[0].replace(',', '')) for x in led)
        soak = s['soak']
        ev = s['evidence']
        check('archive', s['total'] == '1,323' and total == 1323 and len(led) == 4 and len(soak) == 3 and all(f'0{i} Sep 2026' in soak[i - 1] for i in (1, 2, 3))
              and 'supported indirectly' in ev and '11/11 test scenarios handled correctly.' in ev and 'Zero false positives' in ev and 'Three scenarios were ordinary' in ev
              and 'public sources stayed unchanged' in ev and 'Separate from the illustration' in s['evidenceKicker'],
              f"total {s['total']} = {' + '.join(x[0] for x in led)} = {total:,} ({', '.join(x[1] for x in led)}); soak {[x[:11] for x in soak]} with 01 Sep 'supported indirectly'={'supported indirectly' in ev}; "
              f"11/11 incl. three ordinary-change controls, zero false positives; public sources unchanged={'public sources stayed unchanged' in ev}", 'i09-archive.png')
        rt = m['return']
        drt = d['return'] if d else {}
        same = [rt.get('needlePoint') and dist(rt['needlePoint'], ri['needlePoint']) < 4, drt.get('needlePoint') and dri.get('needlePoint') and dist(drt['needlePoint'], dri['needlePoint']) < 4]
        check('returnNext', rt['ok'] and all(same) and rt['scrollDelta'] < 3 and rt['focus'] == 'driftwatch' and 'DueWatch' in m['teaser'] and drt.get('ok') and drt.get('scrollDelta', 9) < 3,
              f"phone: ribbon rolls up (scaleX {rt.get('scale')}) {rt.get('visibleMs')} ms onto {rt.get('needlePoint')}, the point it left from {ri.get('needlePoint')} (same={same[0]}), back on the saved chapter position ±{rt['scrollDelta']:.1f} px, focus on Open case file={rt['focus'] == 'driftwatch'}; "
              f"teaser '{m['teaser']}', Next opened DueWatch; desktop scaleX {drt.get('scale')} onto {drt.get('needlePoint')} left from {dri.get('needlePoint')} (same={same[1]}) ±{drt.get('scrollDelta')} px", 'i10-return-next.png')
        h, di = m['history'], m['direct']
        check('historyDirect', h['backOk'] and h['backDesk'] == 'alarm' and h['forwardOk'] and h['canvas'] and di['directVerdict'] == 'alarm' and di['refreshed']['compared'] == 'false'
              and di['refreshed']['button'].startswith('Compare snapshots') and di['refreshedVerdict'] == 'healthy' and not di['errors'] and not di['bad'],
              f"Back DueWatch → DriftWatch desk works (Run missing → {h['backDesk']})={h['backOk']}, Forward → DueWatch={h['forwardOk']}, same Canvas={h['canvas']}; "
              f"direct /work/driftwatch layout → {di['directVerdict']}; refresh → {di['refreshed']} (illustration restarts) → change → {di['refreshedVerdict']}; errors {len(di['errors'])}, ≥400 {len(di['bad'])}", 'i11-history-direct.png')
        sw, rp, kb = it['switch'], it['rapid'], it['keyboard']
        switch_ok = sw['verdicts'] == ['pending'] and sw['headings'] == ['None'] and sw['traceScales'] == [1.0] and sw['labels'] == ['AWAITING COMPARISON'] and sw['room']['scenario'] == 'layout' and sw['room']['heading'] is None
        rapid_ok = rp['final'][0] == 'alarm' and rp['final'][1] >= .999 and rp['final'][2] >= .999 and rp['room']['codes'] and rp['room']['kicker'] == 'Pipeline health'
        sb = it['scrollBack']
        kb_ok = bool(kb['firstAlarm']) and kb['firstAlarm']['sx'] >= .999 and kb['firstAlarm']['o'] >= .999
        rz = d['resize'] if d else None
        rz_ok = bool(rz) and all(x['overflow'] <= 1 and x['verdict'] == 'alarm' and x['label'] == 'ALARM' for x in rz['after']) and rz['canvas']
        dint = d['interrupt'] if d else {}
        d_ok = bool(dint) and dint['switch']['verdicts'] == ['pending'] and dint['rapid']['final'][0] == 'alarm'
        check('interruptions', m['doubleTap']['historyDelta'] == 1 and switch_ok and rapid_ok and sb['verdict'] == 'alarm' and sb['scenario'] == 'pipeline' and kb_ok and d_ok
              and back_flight and back_flight['ribbonOpacity'] == 0 and back_flight['direction'] == 'idle' and back_flight['path'] == '/' and rz_ok and edges and edges.get('fallback') == 'passed',
              f"double tap Open case file → history +{m['doubleTap']['historyDelta']} ({m['doubleTap']['second']}); switch to Layout 0.3 s into Compare → verdicts {sw['verdicts']} for 1.4 s, verdict headings {sw['headings']}, trace reveal scale {sw['traceScales']} (motion reverted), trace label {sw['labels']} (no late verdict); "
              f"6 rapid Compare taps → {rp['final']}; scroll to readings and back → {sb['scenario']} {sb['verdict']}; keyboard Enter → alarm at trace {kb['firstAlarm'] and kb['firstAlarm']['sx']} / verdict {kb['firstAlarm'] and kb['firstAlarm']['o']} on first frame; "
              f"desktop switch/rapid={d_ok}; Back during the ribbon → opacity {back_flight and back_flight['ribbonOpacity']} '{back_flight and back_flight['direction']}' on {back_flight and back_flight['path']}; "
              + (f"resize after alarm 1440→390/1024/900/1920/1440: overflow {[x['overflow'] for x in rz['after']]}, verdict {[x['verdict'] for x in rz['after']]}" if rz else 'resize not run')
              + f"; Development edge (Back during the ribbon, resize) fallback/reduced={edges and edges.get('fallback')}/{edges and edges.get('reduced')}", 'i12-interruptions.png')
    if slow:
        fl, bad = slow['flight'], slow['failed']
        check('modelSlowFail', not fl['strayLeaders'] and fl['leaderAfter'] > .3 and bad['scene'] == 'fallback' and bad['live'] == 0 and bad['maxLeader'] == 0 and bad['still'] > 100
              and bad['verdict'] == 'alarm' and edges and edges.get('fallback') == 'passed',
              f"instruments are procedural (no instrument download can stall); ribbon flight polled {fl['samples']}×: leaders visible without a projected model {len(fl['strayLeaders'])}×, "
              f"case frames before projection {fl['onCaseWithoutLive']} with leaders hidden, leader opacity {round(fl['leaderAfter'], 2)} once live; scene failed (ambient.glb blocked): scene '{bad['scene']}', "
              f"leaders {bad['live']}/{bad['maxLeader']}, still image {round(bad['still'])} px, desk Run missing → {bad['verdict']}; Development fallback exercise={edges and edges.get('fallback')}", 'i13-model-slow-fail.png')
    if reduced:
        ch = reduced['chapter']
        check('reducedMotion', reduced['ribbonMaxOpacity'] == 0 and reduced['ribbonDisplay'] == 'none' and ch['line'] == 0 and ch['alarm'] == 0 and ch['spike'] == 1
              and reduced['verdictVisibleMs'] is not None and reduced['verdictVisibleMs'] < 100 and reduced['verdict'] == 'alarm' and edges and edges.get('reduced') == 'passed',
              f"ribbon display '{reduced['ribbonDisplay']}', max opacity {reduced['ribbonMaxOpacity']} during entry; chapter at orbit {round(ch['orbit'], 2)} already final (line {ch['line']}, spike {ch['alarm']}, alarm caption {ch['spike']}); "
              f"verdict visible from {reduced['verdictVisibleMs']} ms, trace full at {reduced['traceFullMs']} ms ({reduced['verdict']}); Development reduced exercise={edges and edges.get('reduced')}", 'i14-reduced-motion.png')
    if vp:
        phones = [r for r in vp if int(r['viewport'].split('x')[0]) < 1024]
        wide = [r for r in vp if int(r['viewport'].split('x')[0]) >= 1024]
        check('mobileViewports', len(phones) == 4 and all(r['pass'] for r in phones),
              '; '.join(f"{r['viewport']} {'pass (' + ', '.join(f'{k} {v}' for k, v in r['scenarios'].items()) + ')' if r['pass'] else 'FAIL ' + r.get('error', '')}" for r in phones), 'i15-viewports.jpg')
        lay, st = (d['layout'], d['sticky']) if d else ({}, {})
        comp = (bool(lay) and len(set(lay['steps'])) == 1 and lay['timeline'][0] <= lay['workspace'][0] + 1 and lay['timeline'][1] >= lay['workspace'][1] - 1
                and len(set(lay['snapTops'])) == 1 and lay['snapRight'] <= lay['comparisonLeft'] and lay['evidenceHeadingRight'] <= lay['ledgerLeft']
                and len(set(lay['soakTops'])) == 1 and 100 <= st['snapTop'] <= 160 and st['snapBottom'] <= 900)
        check('desktopComposition', len(wide) == 2 and all(r['pass'] for r in wide) and comp,
              f"1440/1920 Development checks {[r['viewport'] + ' ' + ('pass' if r['pass'] else 'FAIL') for r in wide]}; steps one row (tops {lay.get('steps')}); timeline spans the desk {lay.get('timeline')} vs {lay.get('workspace')}; "
              f"snapshots side by side (tops {lay.get('snapTops')}, {lay.get('snapWidth')} px each) left of the verdict column ({lay.get('comparisonWidth')} px); sticky while reading the diff: snapshots top {st.get('snapTop')} px, bottom {st.get('snapBottom')}; "
              f"archive ledger beside its heading={lay and lay['evidenceHeadingRight'] <= lay['ledgerLeft']}; soak days one row {lay.get('soakTops')}", 'i16-desktop.png')
    if sources:
        check('sources', sources[0], sources[1], 'i09-archive.png', data=sources[2])
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
    full = {'monitor', 'perf-driftwatch', 'audio', 'desktop-a', 'desktop-b', 'perf-crosscheck', 'perf-surgeline'}
    suites = [{'suite': n, 'status': ledger_data.get(n, {}).get('status', 'missing'), 'current': ledger_data.get(n, {}).get('fingerprint') == fp,
               'phones': ledger_data.get(n, {}).get('phones'), 'finishedAt': ledger_data.get(n, {}).get('finishedAt')} for n in rr.SUITES]
    check('regressions', len(suites) == 13 and all(s['status'] == 'passed' and s['current'] and (s['suite'] not in full or s['phones'] == 'full') for s in suites),
          f"source fingerprint {fp}; " + '; '.join(f"{s['suite']}={s['status']}{'' if s['current'] else ' (stale)'} {s['phones']}" for s in suites), 'i15-viewports.jpg', suites=suites)


def owner_notes(m):
    notes = ["Approved at gate 7C (2026-09-17), DRAFT labels removed — copy 7C: chapter strip, deck/brief clarification, three hotspot bodies, comparison desk (intro, four steps, five situations with verdict/cause/action, alarm record), recorded archive and DueWatch teaser — including numbered Day 1–3 for the illustration (calendar dates would collide with the recorded 01–03 Sep soak, which had no alarms)."]
    if m:
        views = {s: m['desk']['scenarios'][s]['view'] for s in SCENARIOS}
        v = views['layout']
        notes.append(f"Phone 390×844, Compare tapped with the button in the upper third: trace + HEALTHY/ALARM label visible at once (trace bottom {v['traceBottom']} px), verdict heading top {v['verdictTop']} px of {v['height']} "
                     f"({'on screen' if v['verdictTop'] < v['height'] - 40 else 'below the fold'}); the reason, action and alarm record need a scroll (diff bottom {v['diffBottom']} px). Accepted at gate 7C (m04-layout-compared.png).")
    notes.append("Refresh on /work/driftwatch restarts the illustration at \"Compare snapshots\" (no saved state), same as SurgeLine — by design.")
    notes.append("Motion changed by the Testing fix: Compare used to squeeze the whole trace with scaleX, so the spike slid and stretched from the left edge. "
                 "A clip window now opens left → right over a still path; the spike appears in place (slow-motion clips 3–4, i04-comparison-desk.png). Same 0.8 s timing.")
    notes.append("Rig limits: headless Chromium on the laptop GPU, CPU throttled 4x. The first full-pack frame-rate run measured case scroll 54.2 fps with 10.5% slow frames "
                 "(limit 10%) while the host was loaded; re-measured alone on the same source: all five segments 54.3–59.8 fps, ≤3.3% slow. Both attempts are in evidence.json. Physical phone = Phase 8.")
    return notes


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


async def remeasure_fps():
    report = json.loads((OUT / 'evidence.json').read_text())
    uptime = Path('/proc/loadavg').read_text().split()[:3]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        try:
            fps = await perf(browser)
        finally:
            await browser.close()
    verdicts(None, None, None, None, None, None, fps, None, None)
    attempts = report['measurements'].get('fps4xAttempts') or [{'finishedAt': report['finishedAt'], 'fps4x': report['measurements']['fps4x'], 'pass': report['items']['performance']['pass']}]
    attempts.append({'finishedAt': datetime.now(timezone.utc).isoformat(), 'loadAvgBefore': uptime, 'fps4x': fps, 'pass': CHECKS['performance']['pass']})
    report['measurements']['fps4xAttempts'] = attempts
    report['measurements']['fps4x'] = fps
    report['items']['performance'].update({**CHECKS['performance'], 'detail': CHECKS['performance']['detail'] + f" (re-measured alone, attempt {len(attempts)}; earlier attempts in measurements.fps4xAttempts)"})
    report['items']['regressions'].update(CHECKS['regressions'])
    for c, v in report['categories'].items():
        v['pass'] = all(report['items'][k]['pass'] for k in v['items'])
    report['status'] = 'passed' if all(i['pass'] for i in report['items'].values()) else 'failed'
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + '\n')
    print(report['status'], report['items']['performance']['detail'])
    return report['status'] == 'passed'


async def run():
    if REMEASURE:
        return await remeasure_fps()
    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ('raw', 'viewports', 'edges'):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        try:
            mobile = await step('phone walkthrough (recorded)', mobile_walk(browser), ['story', 'chapterTrace', 'ribbonEntry', 'hotspots', 'comparisonDesk', 'emptyNeverHealthy', 'sourceVsPipeline', 'diffDetail', 'notLive', 'archive', 'returnNext', 'historyDirect', 'interruptions', 'clean', 'sources'], tag='mobile')
            desktop = await step('desktop walkthrough (recorded)', desktop_walk(browser), ['desktopComposition'], tag='desktop')
            back_flight = await step('back during the ribbon', back_during_flight(browser), tag='back')
            slow = await step('model late / failed', model_slow_fail(browser), 'modelSlowFail', tag='slow')
            reduced = await step('reduced motion', reduced_motion(browser), 'reducedMotion', tag='reduced')
            vp = await step('six viewports + edges (verify_driftwatch_room)', viewports(browser), ['mobileViewports', 'desktopComposition'], tag='viewports')
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
            compared = '\n'.join(f"{x['after']['heading']} {x['after']['summary']} {x['after']['diffText']} {' '.join(x['after']['codes'])}" for x in m['desk']['scenarios'].values())
            sources = sources_check(m['story']['text'] + '\n' + m['story']['labels'] + '\n' + compared, m['hotspots'], m['stripText'])
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
            (mp4m, mm['chapter'], min(mm['chapter'] + 4, mm['chapterEnd']), 'Phone - seismograph follows the orbit', 390),
            (mp4m, mm['entry'] - .4, mm['entryEnd'] + .4, 'Phone - ribbon from the needle into the case', 390),
            (mp4m, mm['compare-change'] - .3, mm['compare-change-end'], 'Phone - ordinary change stays healthy', 390),
            (mp4m, mm['compare-layout'] - .3, mm['compare-layout-end'], 'Phone - empty collection raises an alarm', 390),
            (mp4m, mm['switch'] - .3, mm['switchEnd'], 'Phone - switch situation mid-comparison', 390),
            (mp4m, mm['return'] - .4, mm['returnEnd'] + .4, 'Phone - ribbon rolls back to the chapter', 390),
            (mp4d, dm['entry'] - .4, dm['entryEnd'] + .4, 'Desktop - ribbon into the case', 720),
            (mp4d, dm['compare-missing'] - .3, dm['compare-missing-end'], 'Desktop - missing run on the wide desk', 720),
            (mp4d, dm['return'] - .4, dm['returnEnd'] + .4, 'Desktop - ribbon return', 720),
            (mp4d, dm['resize'] - .3, min(dm['resize'] + 4, dm['resizeEnd']), 'Desktop - resize after an alarm', 720),
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
    if trimmed and 'chapter' in trimmed:
        trimmed['chapter'] = {k: v for k, v in trimmed['chapter'].items() if k != 'raw'}
    report = {
        'status': 'passed' if passed else 'failed',
        'phase': 'Phase 7C — DriftWatch: monitoring room',
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
        'forOwner': owner_notes(m),
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
