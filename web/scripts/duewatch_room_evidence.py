"""Phase 7D Testing evidence: DueWatch time control room, mobile first then desktop.

Records two walkthroughs with real input (phone 390x844 touch swipes + taps, desktop 1440x900 mouse wheel + clicks):
chapter business-time pointer (follows the orbit, reverses on scroll back, still when idle) → orbit ring from the orrery
unfolds into an agenda rail → hotspots → module A contract agenda: six day controls traced frame by frame (hand turns
650 ms, result card 200 ms, one category per boundary), unclear date → Bad data → module B message triage: six example
categories (approved text vs stop → a person, no draft), handoff signal 240 ms → separate reminder example: exact 24 h
pending, >24 h one mock reminder, six replays add nothing, customer replied, reset → interruptions (rapid taps, module
switch mid-motion, idle stillness, scroll away/back, keyboard) → recorded proof + business-date note + seven audit
findings → BrandWall teaser → ring folds back to its origin → Next, Back/Forward, direct URL + refresh; desktop adds the
two-desk composition and resize with state kept. Cuts a 0.25x slow-motion reel. Q42: re-runs the Development checks
(verify_duewatch_room.viewport/edges) on six viewports into the pack, then model late/failed, reduced motion, frame
rate under 4x CPU, copy/number sources and the regression ledger.

Output: assets/renders/personal-duewatch/evidence/ — PNG per item, walkthrough-mobile.mp4, walkthrough-desktop.mp4,
slow-motion.mp4, contact sheets, evidence.json with pass/fail per item and per category.
Chromium GPU emulation on a laptop; no physical-phone claim (Phase 8).

Run from web/scripts with the production preview on :8767:
  timeout 2700 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python duewatch_room_evidence.py [--only mobile,desktop,back,slow,reduced,viewports,fps]
Exit 1 when any item fails.
"""
import asyncio
import json
import math
import re
import shutil
import subprocess
import sys
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
import verify_duewatch_room as vdw  # noqa: E402
from case_files_evidence import tile  # noqa: E402
from crosscheck_room_evidence import Walk, duration, encode, overflow, swipe_until, top_of, watch, wheel_until  # noqa: E402
import verify_driftwatch_room as vdr  # noqa: E402
from verify_duewatch_room import enter, idle  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/personal-duewatch/evidence'
RAW = OUT / 'raw'
cre.OUT, cre.RAW = OUT, RAW  # shared helpers (Walk.shot, slow_motion) write into this pack
URL = vdw.URL
GPU = vdw.GPU
DOSSIER = ROOT / 'portfolio/CAPABILITY_DUEWATCH.md'
SLOW_MS = 1000 / 45
DAYS = ('61', '60', '8', '7', '0', '-1')
CATEGORY = {'61': 'active', '60': 'due', '8': 'due', '7': 'renew', '0': 'renew', '-1': 'expired'}
ANGLE = {d: i * 42 - 105 for i, d in enumerate(DAYS)}
MESSAGES = (('price', 'reply'), ('stock', 'reply'), ('status', 'reply'), ('complaint', 'human'), ('payment', 'human'), ('unknown', 'human'))
FRAMES = "(() => { window.__frames = []; const f = t => { window.__frames.push(t); requestAnimationFrame(f); }; requestAnimationFrame(f); })();"

# Chapter: orbit var on the section and the pointer position along its track (0 = Active, 1 = Renewal).
CHAPTER = r"""()=>{const s=document.querySelector('#duewatch');const t=document.querySelector('.time-chapter-track');const i=t.querySelector('i');
  const tr=t.getBoundingClientRect(),ir=i.getBoundingClientRect();
  return {orbit:Number(getComputedStyle(s).getPropertyValue('--instrument-3-orbit')||0),pointer:Math.round((ir.x-tr.x)/Math.max(1,tr.width-7)*1000)/1000}}"""
# Orbit ring flight: centre, scale X/Y, rotation, opacity and direction every frame until 260 frames.
RING = """()=>{const w=window.__ring=[];const t0=performance.now();const e=document.querySelector('.time-flight');
  const tick=()=>{const s=getComputedStyle(e);const m=new DOMMatrix(s.transform==='none'?undefined:s.transform);
    w.push({t:Math.round(performance.now()-t0),d:e.dataset.direction,o:Math.round(Number(s.opacity)*1000)/1000,sx:Math.round(Math.hypot(m.a,m.b)*1000)/1000,
      sy:Math.round(Math.hypot(m.c,m.d)*1000)/1000,rot:Math.round(Math.atan2(m.b,m.a)*1800/Math.PI)/10,x:Math.round(m.e),y:Math.round(m.f),display:s.display,path:location.pathname});
    if(w.length<260)requestAnimationFrame(tick)};requestAnimationFrame(tick)}"""
RING_READABLE = "(()=>{const e=document.querySelector('.time-flight');const s=getComputedStyle(e);const m=new DOMMatrix(s.transform==='none'?undefined:s.transform);return Number(s.opacity)>.5&&Math.hypot(m.a,m.b)>.95&&e.dataset.direction!=='idle'})()"
# Clock hand angle + result card opacity/offset + category every frame.
HAND = """()=>{const w=window.__hand=[];const t0=performance.now();const h=document.querySelector('.time-hand');const c=document.querySelector('.time-contract-result');
  const tick=()=>{const hs=getComputedStyle(h).transform;const m=new DOMMatrix(hs==='none'?undefined:hs);const cs=getComputedStyle(c);const cm=new DOMMatrix(cs.transform==='none'?undefined:cs.transform);
    w.push({t:Math.round(performance.now()-t0),a:Math.round(Math.atan2(m.b,m.a)*1800/Math.PI)/10,o:Math.round(Number(cs.opacity)*1000)/1000,y:Math.round(cm.f*100)/100,cat:c.dataset.category,n:h.getAnimations().length});
    if(w.length<window.__handFrames)requestAnimationFrame(tick)};requestAnimationFrame(tick)}"""
# Handoff signal dot + route every frame.
DOT = """()=>{const w=window.__dot=[];const t0=performance.now();const b=document.querySelector('.time-handoff > i > b');const h=document.querySelector('.time-handoff');
  const tick=()=>{const s=getComputedStyle(b);const m=new DOMMatrix(s.transform==='none'?undefined:s.transform);
    w.push({t:Math.round(performance.now()-t0),y:Math.round(m.f*10)/10,o:Math.round(Number(s.opacity)*1000)/1000,r:h.dataset.route,n:b.getAnimations().length});
    if(w.length<window.__dotFrames)requestAnimationFrame(tick)};requestAnimationFrame(tick)}"""
ROOM = """()=>{const q=s=>document.querySelector(s);const t=s=>q(s)?q(s).textContent:null;
  const vis=s=>{const e=q(s);return !!e&&e.getClientRects().length>0};
  const hand=q('.time-hand');const hs=getComputedStyle(hand).transform;const m=new DOMMatrix(hs==='none'?undefined:hs);
  const dot=getComputedStyle(q('.time-handoff > i > b')).transform;
  return {module:q('.time-room').dataset.module,agendaVisible:vis('#time-agenda'),triageVisible:vis('#time-triage'),
    modulePressed:[...document.querySelectorAll('.time-module-picker [aria-pressed=true]')].map(e=>e.textContent),
    category:q('.time-contract-result').dataset.category,heading:t('.time-contract-result h4'),result:t('.time-contract-result p'),
    current:[...document.querySelectorAll('.time-agenda-list li[data-current=true] b')].map(e=>e.textContent),marker:t('.time-agenda-list em'),
    pressedDays:[...document.querySelectorAll('[data-days][aria-pressed=true]')].map(e=>e.dataset.days),badPressed:q('[data-bad-date]').getAttribute('aria-pressed'),
    handAngle:Math.round(Math.atan2(m.b,m.a)*1800/Math.PI)/10,handAnimations:hand.getAnimations().length,
    route:q('.time-handoff').dataset.route,handoffTitle:t('.time-handoff > div b'),handoff:t('.time-handoff > div'),dot:dot,
    pressedMessage:[...document.querySelectorAll('[data-message][aria-pressed=true]')].map(e=>e.dataset.message),
    ledger:t('.time-ledger strong'),ledgerResult:q('.time-ledger').dataset.result,ledgerText:t('.time-ledger p')}}"""
LEADERS = cre.LEADERS

CATEGORIES = ['story', 'visual', 'animation', 'transition', 'mobile', 'desktop', 'source', 'performance']
ITEMS = {
    'story': (['story'], 'Story reads contract agenda and message triage as two separate routines: chapter pointer strip under the CTA; case order Brief → instrument → time control room → recorded proof + audit → readings → demo → Next; simulation labelled; copy approved at gate 7D (2026-09-18), no DRAFT labels'),
    'chapterPointer': (['animation', 'mobile', 'desktop'], 'Chapter: the business-time pointer follows the orbit from Active to Renewal, scrolling back returns it, it is still when scrolling stops; phone swipe and desktop wheel'),
    'ringEntry': (['transition'], 'Open case file: a ring leaves the orrery, unfolds into a flat agenda rail across the screen (~720 ms), fades (~180 ms); the case opens with focus on the case heading (phone + desktop)'),
    'hotspots': (['story', 'visual'], 'Hotspots explain the daily expiry check, message decisions with their audit limit and the saved reminder record; leaders only while the model is on screen; card inside the viewport'),
    'agendaDesk': (['story', 'animation', 'mobile', 'desktop'], 'Module A by tap/click: 61/60/8/7/0/past-due controls land on Active/Due soon/Due soon/Needs renewal/Needs renewal/Expired; the hand turns to its stop (~650 ms, no overshoot), the result card settles (~200 ms), exactly one agenda row marked "Example here"'),
    'badData': (['story', 'visual'], 'Unclear date: the example becomes Bad data with "a person corrects the row, others continue", its own agenda row; choosing a day clears it'),
    'humanHandoff': (['story', 'animation', 'visual'], 'Module B: price/stock/status → "Approved text → mock reply" (local mock log); complaint/payment/unclear → "Stop → a person takes over", no reply draft attached; the handoff signal drops to the decision box (~240 ms); the known mixed-intent gap is stated beside it'),
    'reminderReplay': (['story', 'animation'], 'Separate reminder example: check at exactly 24 h stays 0 (pending), after 24 h one mock reminder (1), six replays keep 1 ("adds no duplicate"), customer replied logs nothing further, reset → 0; replied before the check stays 0; re-import limit stated'),
    'twoModules': (['story', 'mobile', 'desktop'], 'Two modules never read as one pipeline: intro "a contract status does not send a message", phone shows one desk at a time via the A/B tap picker (≥ 44 px), state survives switching both ways; reminder example "independent of the category chosen above"; steps labelled A/ and B/'),
    'notLive': (['story', 'source'], 'Not live and no false urgency: simulation disclosure, "BUSINESS TIME / ILLUSTRATION" on the dial, no countdown or ticking clock (hand, card, ledger and signal still for 2.1 s idle), "live" only as a negation, recorded proof labelled "Recorded, not live"'),
    'evidenceAudit': (['story', 'visual', 'source'], 'Recorded proof kept apart: 200 contracts/run, 18 test messages + 6/6 escalated + 0 external calls, 12 stayed 12 with its limit; simulated business dates vs 8 real timer firings / 9 days; seven audit findings (4 High / 3 Medium) open to read, A9/A10 open, no production-ready claim'),
    'returnNext': (['transition'], 'Return: the rail folds back into the ring at the point it left from; the chapter reopens on the saved scroll position with focus on Open case file; BrandWall teaser, Next opens BrandWall'),
    'historyDirect': (['transition'], 'Back/Forward between DueWatch and BrandWall, direct URL /work/duewatch and refresh keep the room working (refresh restarts at 61 days / 0 reminders)'),
    'interruptions': (['transition', 'animation'], 'Interruptions: double tap Open case file adds one history entry; rapid day taps settle once on the last stop; switching module mid-turn leaves the hand final; rapid message taps settle on the last route; scroll away/back keeps state; keyboard choices are final at once; Back during the ring clears it; resize across 1024 px keeps every state'),
    'modelSlowFail': (['visual', 'mobile'], 'Model not on screen yet: no leader during the ring flight; scene failed (still view): no leaders, the room still works'),
    'reducedMotion': (['animation'], 'Reduced motion: no ring, chapter pointer final, hand and handoff signal jump without animation'),
    'mobileViewports': (['mobile'], 'All Development checks pass at 390×844, 360×740, 430×932 and tablet 768×1024'),
    'desktopComposition': (['desktop', 'visual'], 'Desktop 1440×900 / 1920×1080: agenda and triage desks side by side with distinct headings, agenda slightly wider, the chosen module outlined amber, warm gradient desks, steps in one row, three proof columns, business-date note in two columns, audit list set to the right'),
    'sources': (['source'], 'Every number and quoted fact on the page traces to the DueWatch dossier; examples labelled fictional; no live sending, production-ready or replay-safe claim'),
    'performance': (['performance', 'mobile'], 'PLAN §11 / Q42 under 4x CPU (phone swipe): chapter, ring flight, agenda + triage + reminder taps, case scroll and return hold ≥ 45 fps with ≤ 10% slow frames'),
    'clean': (['mobile', 'desktop'], 'One persistent Canvas, zero page errors, zero responses ≥ 400, no horizontal overflow in both walkthroughs'),
    'regressions': (['mobile', 'desktop'], 'Regression ledger (run_regressions.py): all 16 suites passed on this exact source fingerprint'),
}
CHECKS, META = {}, {}
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


async def land(page, y):
    """Numeric scrollY (verify_duewatch_room.land takes a selector); clamped at the top."""
    await vdr.land(page, max(0, y))


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


class Dummy:
    def mark(self, *_):
        pass

    async def shot(self, name):
        return name


# ---------------------------------------------------------------- analysis helpers
async def chapter_sample(page, samples):
    samples.append(await page.evaluate(CHAPTER))


async def chapter_still(page):
    a = await page.evaluate(CHAPTER)
    await page.wait_for_timeout(1200)
    return a == await page.evaluate(CHAPTER)


def chapter_summary(forward, backward, still):
    fwd = sorted(forward, key=lambda r: r['orbit'])
    follows = all(abs(r['pointer'] - r['orbit']) < .03 for r in forward + backward)
    monotone = all(b['pointer'] >= a['pointer'] - .01 for a, b in zip(fwd, fwd[1:]))
    end = fwd[-1]
    back = backward[-1] if backward else None
    back_ok = back is not None and back['pointer'] < end['pointer'] - .3
    mids = [r for r in fwd if .15 < r['orbit'] < .85]
    return {'ok': follows and monotone and end['pointer'] > .97 and back_ok and still and len(mids) >= 3, 'samples': len(forward), 'midSamples': len(mids),
            'followsOrbit': follows, 'monotone': monotone, 'maxError': round(max(abs(r['pointer'] - r['orbit']) for r in forward + backward), 3),
            'end': end, 'back': back, 'stillWhenIdle': still}


async def ring_collect(page, path, capture):
    if capture:
        for _ in range(90):
            if await page.evaluate(RING_READABLE):
                await page.screenshot(path=str(OUT / capture))
                break
            await page.wait_for_timeout(12)
    await page.wait_for_url(URL + path, timeout=15000)
    await idle(page)
    await page.wait_for_timeout(200)
    return await page.evaluate('window.__ring')


def ring_summary(trace, direction, width, height):
    vis = [f for f in trace if f['o'] > .03]
    if len(vis) < 5:
        return {'ok': False, 'visibleFrames': len(vis)}
    rail = min(width - 48, 1000) / 180
    agenda = (width / 2, height * .43)
    sx = [f['sx'] for f in vis]
    widest = max(vis, key=lambda f: f['sx'])
    first, last = vis[0], vis[-1]
    near = lambda f, pose: abs(f['sx'] - pose[0]) < pose[0] * .06 and abs(f['sy'] - pose[1]) < .04 and abs(f['rot'] - pose[2]) < 3  # noqa: E731
    orbit_pose, rail_pose = (.65, .65, -28), (rail, .13, 0)
    if direction == 'out':
        shape = near(first, orbit_pose) and near(widest, rail_pose) and dist((widest['x'], widest['y']), agenda) < 6
        monotone = all(b >= a - .002 for a, b in zip(sx, sx[1:]))
        point = (first['x'], first['y'])
    else:
        shape = near(first, rail_pose) and dist((first['x'], first['y']), agenda) < 6 and near(last, orbit_pose)
        monotone = all(b <= a + .002 for a, b in zip(sx, sx[1:]))
        point = (last['x'], last['y'])
    inside = all(-10 <= f['x'] <= width + 10 and -10 <= f['y'] <= height + 10 for f in vis)
    cleared = trace[-1]['o'] == 0 and trace[-1]['d'] == 'idle'
    full = [f for f in vis if abs(f['sx'] - rail) < .02 * rail]
    return {'ok': shape and monotone and inside and cleared, 'visibleFrames': len(vis), 'visibleMs': vis[-1]['t'] - vis[0]['t'],
            'firstPose': [first['sx'], first['sy'], first['rot']], 'railPose': [widest['sx'], widest['sy'], widest['rot']], 'lastPose': [last['sx'], last['sy'], last['rot']],
            'railWidthPx': round(widest['sx'] * 180), 'orbitPoint': list(point), 'railCentre': [widest['x'], widest['y']], 'monotone': monotone,
            'railHeldMs': (full[-1]['t'] - full[0]['t']) if full else None, 'inside': inside, 'clearedAfter': cleared}


def hand_motion(frames, day, previous):
    """Hand turns from the previous stop to the chosen one; card fades/rises in; time zero = first frame with the new category."""
    expected, target, origin = CATEGORY[day], ANGLE[day], ANGLE[previous]
    start = next((i for i, f in enumerate(frames) if f['cat'] == expected and (f['n'] > 0 or abs(f['a'] - target) < .5)), None)
    if start is None:
        return {'ok': False, 'frames': len(frames)}
    t0 = frames[start]['t']
    fr = [{**f, 't': f['t'] - t0} for f in frames[start:]]
    step = 1 if target >= origin else -1
    monotone = all((b['a'] - a['a']) * step >= -.3 for a, b in zip(fr, fr[1:]))
    within = all(min(origin, target) - .5 <= f['a'] <= max(origin, target) + .5 for f in fr)
    settle = next((f['t'] for f in fr if abs(f['a'] - target) < .6 and all(abs(g['a'] - target) < .6 for g in fr if g['t'] >= f['t'])), None)
    card_in = next((f['t'] for f in fr if f['o'] >= .999 and abs(f['y']) < .05), None)
    moving = [f for f in fr if abs(f['a'] - target) >= .6]
    ok = (fr[-1]['n'] == 0 and abs(fr[-1]['a'] - target) < .6 and monotone and within and settle is not None and 500 <= settle <= 820
          and abs(fr[0]['a'] - origin) < abs(target - origin) * .35 + 1 and card_in is not None and card_in <= 330 and fr[0]['o'] < .9 and max(f['y'] for f in fr) <= 8.01)
    return {'ok': ok, 'frames': len(fr), 'from': origin, 'to': target, 'firstAngle': fr[0]['a'], 'settleMs': settle, 'movingFrames': len(moving),
            'monotone': monotone, 'overshoot': not within, 'cardStart': [fr[0]['o'], fr[0]['y']], 'cardSettledMs': card_in}


def dot_motion(frames, route):
    start = next((i for i, f in enumerate(frames) if f['r'] == route and f['n'] > 0), None)
    if start is None:
        return {'ok': False, 'frames': len(frames), 'animated': False, 'end': frames[-1] if frames else None}
    t0 = frames[start]['t']
    fr = [{**f, 't': f['t'] - t0} for f in frames[start:]]
    settle = next((f['t'] for f in fr if f['n'] == 0), None)
    ok = fr[0]['y'] < 12 and settle is not None and settle <= 340 and abs(fr[-1]['y'] - 24) < .2 and fr[-1]['o'] >= .999 and all(b['y'] >= a['y'] - .2 for a, b in zip(fr, fr[1:]))
    return {'ok': ok, 'animated': True, 'startY': fr[0]['y'], 'startOpacity': fr[0]['o'], 'settleMs': settle, 'endY': fr[-1]['y']}


# ---------------------------------------------------------------- module A: agenda
async def agenda_view(page, wide):
    await land(page, await top_of(page, '.time-clock') - (170 if wide else 70))


async def pick_module(page, name, tap, wide):
    await land(page, await top_of(page, '.time-module-picker') - (200 if wide else 120))
    button = page.get_by_role('button', name='A / Contract agenda' if name == 'agenda' else 'B / Message triage', exact=True)
    await (button.tap() if tap else button.click())
    await page.wait_for_timeout(250)


async def agenda_run(page, walk, prefix, tap, wide):
    data = {}
    await land(page, await top_of(page, '.time-room') - (80 if wide else 60))
    await walk.shot(f'{prefix}-room-intro.png')
    data['initialRoom'] = await page.evaluate(ROOM)
    if not wide:
        await land(page, await top_of(page, '.time-module-picker') - 200)
        await walk.shot(f'{prefix}-module-picker.png')
    await agenda_view(page, wide)
    await walk.shot(f'{prefix}-agenda-61.png')
    stops = {}
    previous = '61'
    walk.mark('agenda')
    for day in DAYS[1:] + ('61',):
        await agenda_view(page, wide)
        await page.evaluate('window.__handFrames=75')
        await page.evaluate(HAND)
        await press(page, f'[data-days="{day}"]', tap)
        if day in ('7', '-1'):
            await page.wait_for_timeout(260)
            await walk.shot(f'{prefix}-hand-turning-{day}.png')
        await page.wait_for_timeout(1150)
        frames = await page.evaluate('window.__hand')
        room = await page.evaluate(ROOM)
        stops[day] = {'motion': hand_motion(frames, day, previous), 'room': {k: room[k] for k in ('category', 'heading', 'result', 'current', 'marker', 'pressedDays', 'handAngle')}}
        if day != '61':
            await walk.shot(f'{prefix}-agenda-{day}.png')
        previous = day
    walk.mark('agendaEnd')
    data['stops'] = stops
    # Unclear date → Bad data; a day clears it.
    walk.mark('bad')
    await agenda_view(page, wide)
    await press(page, '[data-bad-date]', tap)
    await page.wait_for_timeout(500)
    data['bad'] = await page.evaluate(ROOM)
    await land(page, await top_of(page, '.time-contract-result') - (300 if wide else 200))
    await walk.shot(f'{prefix}-bad-data.png')
    await land(page, await top_of(page, '.time-agenda-list') - (160 if wide else 60))
    await walk.shot(f'{prefix}-bad-data-agenda.png')
    await agenda_view(page, wide)
    await press(page, '[data-days="7"]', tap)
    await page.wait_for_timeout(900)
    data['cleared'] = await page.evaluate(ROOM)
    walk.mark('badEnd')
    await land(page, await top_of(page, '.time-agenda-list') - (160 if wide else 60))
    await walk.shot(f'{prefix}-agenda-list.png')
    data['footnote'] = await page.locator('.time-agenda .time-footnote').text_content()
    data['clockLabel'] = await page.locator('.time-clock span').text_content()
    return data


# ---------------------------------------------------------------- module B: triage + reminders
async def triage_run(page, walk, prefix, tap, wide):
    data = {}
    if not wide:
        walk.mark('module')
        before = await page.evaluate(ROOM)
        await pick_module(page, 'triage', tap, wide)
        data['switchedIn'] = {'before': {k: before[k] for k in ('module', 'agendaVisible', 'triageVisible')}, 'after': await page.evaluate(ROOM)}
        await walk.shot(f'{prefix}-module-b.png')
    else:
        await pick_module(page, 'triage', tap, wide)
        data['switchedIn'] = {'after': await page.evaluate(ROOM)}
    routes = {}
    walk.mark('triage')
    for name, route in MESSAGES:
        await land(page, await top_of(page, '.time-message-picker') - (200 if wide else 70))
        await page.evaluate('window.__dotFrames=40')
        await page.evaluate(DOT)
        await press(page, f'[data-message={name}]', tap)
        if name == 'payment':
            await page.wait_for_timeout(90)
            await walk.shot(f'{prefix}-handoff-signal.png')
        await page.wait_for_timeout(700)
        frames = await page.evaluate('window.__dot')
        room = await page.evaluate(ROOM)
        routes[name] = {'expected': route, 'motion': dot_motion(frames, route), 'room': {k: room[k] for k in ('route', 'handoffTitle', 'handoff', 'pressedMessage')}}
        if name in ('price', 'complaint', 'unknown'):
            await walk.shot(f'{prefix}-message-{name}.png')
    walk.mark('triageEnd')
    data['routes'] = routes
    data['gap'] = await page.locator('.time-triage > .time-boundary-note').text_content()
    await land(page, await top_of(page, '.time-boundary-note') - (300 if wide else 250))
    await walk.shot(f'{prefix}-known-gap.png')
    return data


async def ledger(page):
    r = await page.evaluate(ROOM)
    return [r['ledger'], r['ledgerResult'], r['ledgerText']]


async def reminder_run(page, walk, prefix, tap, wide):
    data = {}
    await land(page, await top_of(page, '.time-reminders') - (120 if wide else 60))
    await walk.shot(f'{prefix}-reminder-intro.png')
    data['intro'] = await page.locator('.time-reminders').text_content()
    target = await top_of(page, '.time-reminder-actions') - (260 if wide else 190)
    await land(page, target)
    walk.mark('reminder')
    seq = [['start'] + await ledger(page)]
    await press(page, '[data-reminder=boundary]', tap)
    seq.append(['24h'] + await ledger(page))
    await walk.shot(f'{prefix}-reminder-24h.png')
    await press(page, '[data-reminder=later]', tap)
    seq.append(['>24h'] + await ledger(page))
    await walk.shot(f'{prefix}-reminder-logged.png')
    for i in range(6):
        await press(page, '[data-reminder=replay]', tap)
        await page.wait_for_timeout(160)
        seq.append([f'replay{i + 1}'] + await ledger(page))
    await walk.shot(f'{prefix}-reminder-replayed.png')
    await press(page, '[data-reminder=reply]', tap)
    seq.append(['replied'] + await ledger(page))
    await press(page, '[data-reminder=later]', tap)
    seq.append(['>24h after reply'] + await ledger(page))
    await walk.shot(f'{prefix}-reminder-replied.png')
    await land(page, await top_of(page, '[data-reminder=reset]') - (400 if wide else 300))
    await press(page, '[data-reminder=reset]', tap)
    seq.append(['reset'] + await ledger(page))
    await land(page, target)
    await press(page, '[data-reminder=reply]', tap)
    seq.append(['replied first'] + await ledger(page))
    await press(page, '[data-reminder=later]', tap)
    seq.append(['>24h, already replied'] + await ledger(page))
    await walk.shot(f'{prefix}-reminder-replied-first.png')
    await press(page, '[data-reminder=reset]', tap)
    await press(page, '[data-reminder=later]', tap)
    seq.append(['reset → >24h'] + await ledger(page))
    walk.mark('reminderEnd')
    data['sequence'] = seq
    data['limit'] = await page.locator('.time-reminders .time-boundary-note').text_content()
    await land(page, await top_of(page, '.time-reminders .time-boundary-note') - (500 if wide else 420))
    await walk.shot(f'{prefix}-reminder-limit.png')
    return data


def reminder_ok(seq):
    s = {row[0]: row[1:] for row in seq}
    return (s['start'][:2] == ['0', 'pending'] and s['24h'][:2] == ['0', 'pending'] and 'exactly 24 hours' in s['24h'][2] and s['>24h'][:2] == ['1', 'logged']
            and all(s[f'replay{i}'][:2] == ['1', 'duplicate'] for i in range(1, 7)) and 'adds no duplicate' in s['replay6'][2]
            and s['replied'][:2] == ['1', 'replied'] and s['>24h after reply'][:2] == ['1', 'replied'] and s['reset'][:2] == ['0', 'pending']
            and s['replied first'][:2] == ['0', 'replied'] and s['>24h, already replied'][:2] == ['0', 'replied'] and s['reset → >24h'][:2] == ['1', 'logged'])


# ---------------------------------------------------------------- interruptions
async def interrupt_run(page, walk, prefix, tap, wide):
    data = {}
    # 1. Rapid day taps: the hand settles once on the last stop, no queue.
    if not wide:
        await pick_module(page, 'agenda', tap, wide)
    await agenda_view(page, wide)
    walk.mark('rapid')
    for day in DAYS + DAYS:
        await press(page, f'[data-days="{day}"]', tap)
        await page.wait_for_timeout(40)
    await page.evaluate('window.__handFrames=70')
    await page.evaluate(HAND)
    await page.wait_for_timeout(1300)
    frames = await page.evaluate('window.__hand')
    data['rapidDays'] = {'final': [frames[-1]['a'], frames[-1]['cat'], frames[-1]['n']], 'maxAnimations': max(f['n'] for f in frames),
                         'room': {k: v for k, v in (await page.evaluate(ROOM)).items() if k in ('category', 'current', 'pressedDays', 'handAngle')}}
    await walk.shot(f'{prefix}-rapid-days.png')
    walk.mark('rapidEnd')
    # 2. Module switch in the middle of a turn (phone): the hand is final when the agenda returns.
    await agenda_view(page, wide)
    await press(page, '[data-days="8"]', tap)
    await page.wait_for_timeout(150)
    if not wide:
        walk.mark('switch')
        await pick_module(page, 'triage', tap, wide)
        mid = await page.evaluate(ROOM)
        await page.wait_for_timeout(200)
        await pick_module(page, 'agenda', tap, wide)
        await page.wait_for_timeout(700)
        back = await page.evaluate(ROOM)
        data['switchMidTurn'] = {'triageShown': mid['triageVisible'] and not mid['agendaVisible'], 'agenda': [back['category'], back['handAngle'], back['handAnimations'], back['agendaVisible']]}
        await agenda_view(page, wide)
        await walk.shot(f'{prefix}-switch-mid-turn.png')
        walk.mark('switchEnd')
        await pick_module(page, 'triage', tap, wide)
    else:
        await page.wait_for_timeout(900)
    # 3. Rapid message taps: last route wins, the signal settles.
    await land(page, await top_of(page, '.time-message-picker') - (200 if wide else 70))
    for _ in range(6):
        await press(page, '[data-message=price]', tap)
        await press(page, '[data-message=payment]', tap)
    await page.wait_for_timeout(600)
    r = await page.evaluate(ROOM)
    data['rapidMessages'] = {'route': r['route'], 'pressed': r['pressedMessage'], 'dot': r['dot'], 'title': r['handoffTitle']}
    await walk.shot(f'{prefix}-rapid-messages.png')
    # 4. Idle: nothing ticks (no countdown, no live clock).
    await press(page, '[data-reminder=later]', tap)
    await page.wait_for_timeout(300)
    samples = []
    for _ in range(4):
        samples.append(await page.evaluate("(()=>{const r=(" + ROOM + ")();return JSON.stringify([r.handAngle,r.category,r.route,r.dot,r.ledger,r.ledgerResult,document.querySelector('.time-room').textContent.length])})()"))
        await page.wait_for_timeout(700)
    data['idleStill'] = len(set(samples)) == 1
    # 5. Scroll away to the readings and back: state kept.
    kept = await page.evaluate(ROOM)
    await land(page, await top_of(page, '#readings-heading') - 80)
    await page.wait_for_timeout(500)
    await land(page, await top_of(page, '.time-reminder-actions') - (260 if wide else 190))
    await page.wait_for_timeout(300)
    after = await page.evaluate(ROOM)
    keys = ('category', 'handAngle', 'route', 'ledger', 'ledgerResult', 'module')
    data['scrollBack'] = {'same': all(kept[k] == after[k] for k in keys), 'state': {k: after[k] for k in keys}}
    await walk.shot(f'{prefix}-scroll-back-kept.png')
    # 6. Keyboard: final at once, no motion.
    if not wide:
        await pick_module(page, 'agenda', tap, wide)
    await agenda_view(page, wide)
    await page.locator('[data-days="0"]').focus()
    await page.evaluate('window.__handFrames=10')
    await page.evaluate(HAND)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(250)
    kb = await page.evaluate('window.__hand')
    first = next((f for f in kb if f['cat'] == 'renew'), None)
    data['keyboard'] = {'firstRenewFrame': first, 'animations': max(f['n'] for f in kb)}
    if not wide:
        await pick_module(page, 'triage', tap, wide)
    await land(page, await top_of(page, '.time-message-picker') - (200 if wide else 70))
    await page.locator('[data-message=complaint]').focus()
    await page.evaluate('window.__dotFrames=10')
    await page.evaluate(DOT)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(250)
    kd = await page.evaluate('window.__dot')
    data['keyboardMessage'] = {'route': kd[-1]['r'], 'animations': max(f['n'] for f in kd), 'y': kd[-1]['y']}
    return data


# ---------------------------------------------------------------- story, evidence
STORY = """(()=>{const q=s=>document.querySelector(s);
  const order=['#case-heading','#case-instrument','.time-room','.time-evidence','#readings-heading','#demo-heading','.case-next'].map(s=>q(s)?q(s).getBoundingClientRect().top+scrollY:null);
  return {order, draft:[...document.querySelectorAll('.draft-label')].map(e=>e.textContent), text:q('main').textContent,
    intro:q('.time-intro').textContent, disclosure:q('.time-disclosure').textContent, steps:[...document.querySelectorAll('.time-steps li')].map(e=>e.textContent),
    agendaHeading:q('#agenda-heading').textContent, triageHeading:q('#triage-heading').textContent,
    evidenceKicker:q('.time-evidence .section-kicker').textContent, evidence:q('.time-evidence').textContent,
    proof:[...document.querySelectorAll('.time-proof-columns article')].map(e=>[e.querySelector('span').textContent,e.querySelector('h3').textContent,e.querySelector('p').textContent]),
    dates:q('.time-dates-note').textContent, audit:[...document.querySelectorAll('.time-audit summary')].map(e=>[e.querySelector('span').textContent,e.textContent]),
    demo:q('#demo-heading + p').textContent, teaser:(q('.time-next')||{}).textContent||null,
    labels:[...q('main').querySelectorAll('[aria-label]')].map(e=>e.getAttribute('aria-label')).join('\\n')}})()"""


async def evidence_run(page, walk, prefix, wide, cdp=None):
    async def go(selector, offset):
        y = await top_of(page, selector) - offset
        if cdp:
            await swipe_to(page, cdp, y)
        else:
            await wheel_until(page, y)
            await land(page, y)
    await go('.time-steps', 200 if wide else 80)
    await walk.shot(f'{prefix}-steps.png')
    await go('.time-evidence', 90 if wide else 40)
    await walk.shot(f'{prefix}-proof.png')
    if not wide:
        await go('.time-proof-columns article:nth-child(3)', 60)
        await walk.shot(f'{prefix}-proof-ledger.png')
    await go('.time-dates-note', 160 if wide else 60)
    await walk.shot(f'{prefix}-dates-note.png')
    await go('.time-audit', 90 if wide else 50)
    await walk.shot(f'{prefix}-audit-closed.png')
    summaries = await page.locator('.time-audit summary').all()
    for s in summaries:
        await (s.tap() if cdp else s.click())
        await page.wait_for_timeout(80)
    opened = await page.locator('.time-audit details[open]').count()
    await land(page, await top_of(page, '.time-audit ol') - (140 if wide else 60))
    await walk.shot(f'{prefix}-audit-open.png')
    await land(page, await top_of(page, '.time-audit li:nth-child(5)') - (140 if wide else 60))
    await walk.shot(f'{prefix}-audit-open-2.png')
    return {'opened': opened}


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
        # 1. Chapter pointer: swipe through the orbit, then back.
        section = await page.locator('#duewatch').evaluate("e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight,stage:e.querySelector('.instrument-stage').offsetHeight})")
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
        await walk.shot('m01c-chapter-renewal.png')
        await swipe_until(page, cdp, section['top'] + .2 * span, step=180, pause=.45, sample=lambda: chapter_sample(page, backward))
        await land(page, section['top'] + .2 * span)
        await page.wait_for_timeout(500)
        await chapter_sample(page, backward)
        await walk.shot('m01a-chapter-active.png')
        await land(page, section['top'] + .55 * span)
        await page.wait_for_timeout(500)
        await walk.shot('m01b-chapter-due.png')
        walk.mark('chapterEnd')
        data['chapter'] = chapter_summary(forward, backward, still)
        data['chapter']['raw'] = {'forward': forward, 'backward': backward}
        strip_box = await page.locator('.time-chapter').bounding_box()
        cta = await page.locator('[data-open-case=duewatch]').bounding_box()
        data['stripBelowCta'] = strip_box['y'] >= cta['y'] + cta['height']
        data['stripText'] = await page.locator('.time-chapter').text_content()
        data['stripLabel'] = await page.locator('.time-chapter').get_attribute('aria-label')
        await land(page, section['top'] + .45 * span)
        await page.wait_for_timeout(500)
        origin = await page.evaluate('scrollY')

        # 2. Ring into the case.
        walk.mark('entry')
        await page.evaluate(RING)
        await page.locator('[data-open-case=duewatch]').tap()
        trace = await ring_collect(page, '/work/duewatch', 'm02a-ring-rail.png')
        walk.mark('entryEnd')
        data['ringIn'] = {**ring_summary(trace, 'out', W, H), 'focus': await page.evaluate('document.activeElement.id')}
        await walk.shot('m02b-case-opened.png')
        data['story'] = await page.evaluate(STORY)

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

        # 4. Module A, module B, reminders by touch.
        await swipe_to(page, cdp, await top_of(page, '.time-room') - 60)
        data['agenda'] = await agenda_run(page, walk, 'm04', True, False)
        data['triage'] = await triage_run(page, walk, 'm05', True, False)
        data['reminders'] = await reminder_run(page, walk, 'm06', True, False)
        await pick_module(page, 'agenda', True, False)
        data['stateAfterSwitch'] = {'agenda': await page.evaluate(ROOM)}
        await agenda_view(page, False)
        await walk.shot('m06z-agenda-kept.png')
        await pick_module(page, 'triage', True, False)
        data['stateAfterSwitch']['triage'] = await page.evaluate(ROOM)
        data['targets'] = await page.locator('.time-room button').evaluate_all("els=>els.filter(e=>e.getClientRects().length).map(e=>[Math.round(e.getBoundingClientRect().width),Math.round(e.getBoundingClientRect().height)])")
        await pick_module(page, 'agenda', True, False)
        data['targets'] += await page.locator('.time-room button').evaluate_all("els=>els.filter(e=>e.getClientRects().length).map(e=>[Math.round(e.getBoundingClientRect().width),Math.round(e.getBoundingClientRect().height)])")

        # 5. Interruptions.
        data['interrupt'] = await interrupt_run(page, walk, 'm07', True, False)

        # 6. Proof, dates, audit, readings.
        data['evidence'] = await evidence_run(page, walk, 'm08', False, cdp)
        await swipe_to(page, cdp, await top_of(page, '#readings-heading') - 80)
        await page.wait_for_timeout(1200)
        await walk.shot('m08f-readings.png')
        await swipe_to(page, cdp, await top_of(page, '#demo-heading') - 80)
        await walk.shot('m08g-demo-note.png')

        # 7. Next teaser → ring return.
        await swipe_to(page, cdp, await top_of(page, '#next-heading') - 200)
        await page.wait_for_timeout(300)
        await walk.shot('m09-next-teaser.png')
        walk.mark('return')
        await page.evaluate(RING)
        await page.locator('.case-next .case-back').tap()
        trace = await ring_collect(page, '/', 'm10a-ring-return.png')
        walk.mark('returnEnd')
        await page.wait_for_timeout(300)
        await walk.shot('m10b-back-at-chapter.png')
        data['return'] = {**ring_summary(trace, 'in', W, H), 'scrollDelta': abs(await page.evaluate('scrollY') - origin),
                          'focus': await page.evaluate("document.activeElement.dataset.openCase || document.activeElement.id || document.activeElement.tagName")}

        # 8. Double tap Open case file, Next hop, Back/Forward.
        before = await page.evaluate('history.length')
        walk.mark('doubleTap')
        await page.locator('[data-open-case=duewatch]').tap()
        await page.wait_for_timeout(90)
        try:
            await page.locator('[data-open-case=duewatch]').tap(timeout=600)
            second = 'tapped'
        except Exception:  # noqa: BLE001 — homepage already locked during the flight, also correct
            second = 'not tappable during flight'
        await page.wait_for_url(URL + '/work/duewatch')
        await idle(page)
        data['doubleTap'] = {'historyDelta': await page.evaluate('history.length') - before, 'second': second}
        await swipe_to(page, cdp, await top_of(page, '.case-next') - 120)
        walk.mark('next')
        await page.locator('[data-case-target=brandwall]').tap()
        await page.wait_for_url(URL + '/work/brandwall', timeout=15000)
        await idle(page)
        await walk.shot('m11-next-brandwall.png')
        await page.go_back()
        await page.wait_for_url(URL + '/work/duewatch')
        await idle(page)
        await page.wait_for_timeout(500)
        back_ok = await page.locator('main').get_attribute('data-case') == 'duewatch' and await page.locator('.time-room').count() == 1
        await land(page, await top_of(page, '.time-room') - 60)
        await agenda_view(page, False)
        await page.locator('[data-days="-1"]').tap()
        await page.wait_for_timeout(900)
        back_room = await page.evaluate(ROOM)
        await walk.shot('m11b-history-back-room.png')
        await page.go_forward()
        await page.wait_for_url(URL + '/work/brandwall')
        await idle(page)
        data['history'] = {'backOk': back_ok, 'backRoom': [back_room['category'], back_room['handAngle']], 'forwardOk': await page.locator('main').get_attribute('data-case') == 'brandwall',
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
    await enter(page, '/work/duewatch')
    await land(page, await top_of(page, '.time-room') - 60)
    await agenda_view(page, False)
    await page.locator('[data-days="0"]').tap()
    await page.wait_for_timeout(900)
    direct = await page.evaluate(ROOM)
    await pick_module(page, 'triage', True, False)
    await land(page, await top_of(page, '.time-reminder-actions') - 190)
    await page.locator('[data-reminder=later]').tap()
    direct_ledger = await ledger(page)
    await page.reload()
    await page.locator('.silent-button').click(timeout=30000)
    await idle(page)
    await land(page, await top_of(page, '.time-room') - 60)
    refreshed = await page.evaluate(ROOM)
    await agenda_view(page, False)
    await page.screenshot(path=str(OUT / 'm12-direct-refresh.png'))
    data['direct'] = {'direct': [direct['category'], direct['handAngle']], 'directLedger': direct_ledger,
                      'refreshed': {k: refreshed[k] for k in ('module', 'category', 'handAngle', 'route', 'ledger', 'ledgerResult')},
                      'errors': sink['errors'], 'bad': sink['bad']}
    await context.close()
    return raw, walk, data


# ---------------------------------------------------------------- desktop walkthrough (recorded)
LAYOUT = """(()=>{const r=s=>document.querySelector(s).getBoundingClientRect();const all=s=>[...document.querySelectorAll(s)].map(e=>e.getBoundingClientRect());
  const cs=s=>getComputedStyle(document.querySelector(s));
  return {agenda:[Math.round(r('#time-agenda').left),Math.round(r('#time-agenda').top),Math.round(r('#time-agenda').width)],
    triage:[Math.round(r('#time-triage').left),Math.round(r('#time-triage').top),Math.round(r('#time-triage').width)],
    agendaBorder:cs('#time-agenda').borderTopColor,triageBorder:cs('#time-triage').borderTopColor,agendaBg:cs('#time-agenda').backgroundImage,
    amber:getComputedStyle(document.documentElement).getPropertyValue('--amber').trim(),module:document.querySelector('.time-room').dataset.module,
    steps:all('.time-steps li').map(b=>Math.round(b.top)),proof:all('.time-proof-columns article').map(b=>Math.round(b.top)),
    dates:all('.time-dates-note > *').map(b=>[Math.round(b.left),Math.round(b.top)]),audit:[Math.round(r('.time-audit').left),Math.round(r('.time-audit').right),Math.round(r('.time-audit').width)],
    room:[Math.round(r('.time-evidence').left),Math.round(r('.time-evidence').right)],vw:innerWidth}})()"""


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
        section = await page.locator('#duewatch').evaluate("e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight,stage:e.querySelector('.instrument-stage').offsetHeight})")
        span = section['h'] - section['stage']
        await wheel_until(page, section['top'] - 60)
        walk.mark('chapter')
        forward, backward = [], []
        await wheel_until(page, section['top'] + span, step=80, pause=70, sample=lambda: chapter_sample(page, forward), every=2)
        await land(page, section['top'] + span)
        await page.wait_for_timeout(500)
        await chapter_sample(page, forward)
        still = await chapter_still(page)
        await walk.shot('d01b-chapter-renewal.png')
        await wheel_until(page, section['top'] + .2 * span, step=80, pause=70, sample=lambda: chapter_sample(page, backward), every=2)
        await land(page, section['top'] + .2 * span)
        await page.wait_for_timeout(500)
        await chapter_sample(page, backward)
        await walk.shot('d01a-chapter-active.png')
        data['chapter'] = chapter_summary(forward, backward, still)
        await land(page, section['top'] + .45 * span)
        await page.wait_for_timeout(500)
        origin = await page.evaluate('scrollY')
        walk.mark('entry')
        await page.evaluate(RING)
        await page.locator('[data-open-case=duewatch]').click()
        trace = await ring_collect(page, '/work/duewatch', 'd02a-ring-rail.png')
        walk.mark('entryEnd')
        data['ringIn'] = {**ring_summary(trace, 'out', W, H), 'focus': await page.evaluate('document.activeElement.id')}
        await walk.shot('d02b-case-opened.png')
        await wheel_until(page, await top_of(page, '#case-instrument'))
        await land(page, await top_of(page, '#case-instrument'))
        await page.wait_for_selector('.case-inspection[data-leaders=live]', timeout=12000)
        await page.locator('.hotspot-1').click()
        await page.wait_for_timeout(700)
        await walk.shot('d03-hotspot-decisions.png')
        await page.get_by_role('button', name='Close component card').click()
        await wheel_until(page, await top_of(page, '.time-room') - 80)
        data['agenda'] = await agenda_run(page, walk, 'd04', False, True)
        await land(page, await top_of(page, '.time-desks') - 110)
        await page.wait_for_timeout(300)
        data['layout'] = await page.evaluate(LAYOUT)
        await walk.shot('d05a-two-desks-agenda.png')
        data['triage'] = await triage_run(page, walk, 'd05', False, True)
        await land(page, await top_of(page, '.time-desks') - 110)
        await page.wait_for_timeout(300)
        data['layoutTriage'] = await page.evaluate(LAYOUT)
        await walk.shot('d05b-two-desks-triage.png')
        data['reminders'] = await reminder_run(page, walk, 'd06', False, True)
        data['interrupt'] = await interrupt_run(page, walk, 'd07', False, True)
        data['evidence'] = await evidence_run(page, walk, 'd08', True)
        await wheel_until(page, await top_of(page, '#next-heading') - 250)
        await land(page, await top_of(page, '#next-heading') - 250)
        await walk.shot('d09-next-teaser.png')
        walk.mark('return')
        await page.evaluate(RING)
        await page.locator('.case-next .case-back').click()
        trace = await ring_collect(page, '/', 'd10a-ring-return.png')
        walk.mark('returnEnd')
        await walk.shot('d10b-back-at-chapter.png')
        data['return'] = {**ring_summary(trace, 'in', W, H), 'scrollDelta': abs(await page.evaluate('scrollY') - origin)}

        # Resize with state: desktop → phone → across 1024 → back.
        await page.locator('[data-open-case=duewatch]').click()
        await page.wait_for_url(URL + '/work/duewatch')
        await idle(page)
        await land(page, await top_of(page, '.time-clock') - 170)
        await page.locator('[data-days="0"]').click()
        await page.locator('[data-message=unknown]').click()
        await page.locator('[data-reminder=later]').click()
        await page.locator('[data-reminder=replay]').click()
        await page.wait_for_timeout(900)
        walk.mark('resize')
        resized = []
        for w, h in ((390, 844), (1024, 900), (900, 900), (1920, 1080), (1440, 900)):
            await page.set_viewport_size({'width': w, 'height': h})
            await page.wait_for_timeout(700)
            r = await page.evaluate(ROOM)
            resized.append({'size': f'{w}x{h}', 'overflow': await overflow(page), 'category': r['category'], 'hand': r['handAngle'], 'route': r['route'],
                            'ledger': [r['ledger'], r['ledgerResult']], 'visible': [r['agendaVisible'], r['triageVisible']]})
            if w == 390:
                await agenda_view(page, False)
                await page.wait_for_timeout(300)
                await page.screenshot(path=str(OUT / 'd11a-resized-390.png'))
        await land(page, await top_of(page, '.time-desks') - 110)
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(OUT / 'd11b-resized-back-1440.png'))
        walk.mark('resizeEnd')
        data['resize'] = {'after': resized, 'canvas': await page.evaluate("document.querySelector('canvas')===window.__canvas && document.querySelectorAll('canvas').length===1")}
        raw = await page.video.path()
    finally:
        await context.close()
    return raw, walk, data


# ---------------------------------------------------------------- edges
async def back_during_flight(browser):
    """Next from DueWatch starts the ring folding back; Back 0.3 s later must leave no ring on the arriving homepage."""
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await enter(page)
    await land(page, await page.locator('#duewatch').evaluate('e=>e.getBoundingClientRect().top+scrollY+300'))
    await page.locator('[data-open-case=duewatch]').tap()
    await page.wait_for_url(URL + '/work/duewatch', timeout=5000)
    await idle(page)
    await land(page, await top_of(page, '.case-next') - 120)
    await page.locator('.case-next .case-back').tap()
    await page.wait_for_timeout(300)
    mid = await page.locator('.time-flight').evaluate('e=>({o:Number(getComputedStyle(e).opacity),d:e.dataset.direction})')
    await page.go_back()
    await page.wait_for_timeout(200)
    await idle(page)
    await page.wait_for_timeout(1200)
    (OUT / 'edges').mkdir(exist_ok=True)
    await page.screenshot(path=str(OUT / 'edges/back-during-ring.png'))
    ring = page.locator('.time-flight')
    state = {'midFlight': mid, 'ringOpacity': await ring.evaluate('e=>Number(getComputedStyle(e).opacity)'), 'direction': await ring.get_attribute('data-direction'),
             'path': await page.evaluate('location.pathname'), 'contentOpacity': await page.locator('.page-content').evaluate('e=>Number(getComputedStyle(e).opacity)')}
    await context.close()
    return state


async def model_slow_fail(browser):
    """Instruments are procedural (instrument-models.ts): no instrument download can stall. (1) Poll leaders through the
    ring flight — never visible before data-leaders=live. (2) ambient.glb blocked → still view: no leaders, the room still works."""
    out = {}
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await enter(page)
    await land(page, await page.locator('#duewatch').evaluate('e=>e.getBoundingClientRect().top+scrollY+300'))
    await page.locator('[data-open-case=duewatch]').tap()
    samples, shot = [], False
    for _ in range(140):
        state = await page.evaluate(LEADERS)
        samples.append(state)
        if state['path'] == '/work/duewatch' and not shot:
            await page.screenshot(path=str(OUT / 'm13a-model-arriving.png'))
            shot = True
        if state['path'] == '/work/duewatch' and state['live']:
            break
        await page.wait_for_timeout(40)
    await idle(page)
    await land(page, await top_of(page, '#case-instrument'))
    await page.wait_for_selector('.case-inspection[data-leaders=live]', timeout=12000)
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(OUT / 'm13b-model-arrived.png'))
    out['flight'] = {'samples': len(samples), 'strayLeaders': [x for x in samples if not x['live'] and x['maxLeader'] > .01][:5],
                     'onCaseWithoutLive': sum(1 for x in samples if x['path'] == '/work/duewatch' and not x['live']),
                     'leaderAfter': await page.locator('[data-hotspot-line]').first.evaluate('e=>Number(getComputedStyle(e).opacity)')}
    await context.close()

    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await page.route('**/models/ambient.glb', lambda route: route.abort())
    await enter(page, '/work/duewatch')
    await page.wait_for_selector('.observatory[data-scene=fallback]', timeout=25000)
    await land(page, await top_of(page, '#case-instrument'))
    await page.wait_for_timeout(800)
    bad = await page.evaluate(LEADERS)
    bad['still'] = await page.locator('.case-instrument-still').evaluate('e=>e.getBoundingClientRect().height')
    await page.screenshot(path=str(OUT / 'm13c-model-failed.png'))
    await land(page, await top_of(page, '.time-room') - 60)
    await agenda_view(page, False)
    await page.locator('[data-days="-1"]').tap()
    await page.wait_for_timeout(900)
    await pick_module(page, 'triage', True, False)
    await land(page, await top_of(page, '.time-message-picker') - 70)
    await page.locator('[data-message=payment]').tap()
    await page.wait_for_timeout(500)
    r = await page.evaluate(ROOM)
    bad['room'] = [r['category'], r['route']]
    await page.screenshot(path=str(OUT / 'm13d-failed-room-works.png'))
    out['failed'] = bad
    await context.close()
    return out


async def reduced_motion(browser):
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, reduced_motion='reduce')
    page = await context.new_page()
    await enter(page)
    section = await page.locator('#duewatch').evaluate("e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight,stage:e.querySelector('.instrument-stage').offsetHeight})")
    await land(page, section['top'] + .2 * (section['h'] - section['stage']))
    await page.wait_for_timeout(500)
    chapter = await page.evaluate(CHAPTER)
    await page.screenshot(path=str(OUT / 'm14a-reduced-chapter.png'))
    await page.evaluate(RING)
    await page.locator('[data-open-case=duewatch]').tap()
    trace = await ring_collect(page, '/work/duewatch', None)
    await land(page, await top_of(page, '.time-room') - 60)
    await agenda_view(page, False)
    await page.evaluate('window.__handFrames=20')
    await page.evaluate(HAND)
    await page.locator('[data-days="-1"]').tap()
    await page.wait_for_timeout(500)
    hand = await page.evaluate('window.__hand')
    first = next((f for f in hand if f['cat'] == 'expired'), None)
    await page.screenshot(path=str(OUT / 'm14b-reduced-hand.png'))
    await pick_module(page, 'triage', True, False)
    await land(page, await top_of(page, '.time-message-picker') - 70)
    await page.evaluate('window.__dotFrames=12')
    await page.evaluate(DOT)
    await page.locator('[data-message=complaint]').tap()
    await page.wait_for_timeout(300)
    dot = await page.evaluate('window.__dot')
    state = {'chapter': chapter, 'ringMaxOpacity': max(f['o'] for f in trace), 'ringDisplay': trace[-1]['display'],
             'handFirstExpired': first, 'handAnimations': max(f['n'] for f in hand), 'dotAnimations': max(f['n'] for f in dot), 'dotY': dot[-1]['y'], 'route': dot[-1]['r']}
    await context.close()
    return state


async def viewports(browser):
    vdw.OUT = OUT / 'viewports'
    vdw.OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for size in ['390x844', '360x740', '430x932', '768x1024', '1440x900', '1920x1080']:
        w, h = map(int, size.split('x'))
        try:
            r = await vdw.viewport(browser, w, h)
            rows.append({'viewport': size, 'pass': r['status'] == 'passed', 'chapterPositions': r['chapterPositions']})
        except Exception as error:  # noqa: BLE001
            rows.append({'viewport': size, 'pass': False, 'error': repr(error).splitlines()[0][:300]})
        print(' ', rows[-1]['viewport'], rows[-1]['pass'], flush=True)
    try:
        edges = {e['mode']: e['status'] for e in await vdw.edges(browser)}
    except Exception as error:  # noqa: BLE001
        edges = {'error': repr(error).splitlines()[0][:300]}
    shutil.rmtree(vdw.OUT / 'recordings', ignore_errors=True)
    for webm in vdw.OUT.glob('*.webm'):
        webm.unlink()
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

    section = await page.locator('#duewatch').evaluate('e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight})')
    await land(page, section['top'] - 100)
    await page.wait_for_timeout(800)
    await measure('chapter orbit + pointer (swipe)', lambda: swipe_until(page, cdp, section['top'] + section['h'] - H, step=300, pause=.25))
    await land(page, section['top'] + .45 * (section['h'] - H))
    await page.wait_for_timeout(800)

    async def fly():
        await page.locator('[data-open-case=duewatch]').tap()
        await page.wait_for_url('**/work/duewatch')
        await idle(page)
    await measure('ring into the case', fly)
    await page.wait_for_timeout(600)

    async def room():
        await land(page, await top_of(page, '.time-room') - 60)
        for day in ('60', '8', '7', '0', '-1', '61'):
            await agenda_view(page, False)
            await page.locator(f'[data-days="{day}"]').tap()
            await page.wait_for_timeout(750)
        await pick_module(page, 'triage', True, False)
        for name, _ in MESSAGES:
            await land(page, await top_of(page, '.time-message-picker') - 70)
            await page.locator(f'[data-message={name}]').tap()
            await page.wait_for_timeout(350)
        await land(page, await top_of(page, '.time-reminder-actions') - 190)
        for sel in ('boundary', 'later', 'replay', 'replay', 'reply', 'reset'):
            await page.locator(f'[data-reminder={sel}]').tap()
            await page.wait_for_timeout(150)
    await measure('agenda + triage + reminder taps', room)
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
    await measure('ring return to the chapter', back)
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
    ax.set_title('DueWatch time control room · 390×844 DPR 2 · 4x CPU throttle · green = 60 fps, red = 45 fps')
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
        ('200 per run', '200 synthetic contracts'), ('45 difficult date rows', '45 deliberately hostile rows'), ('7 of 7 renewals', '7 / 7 = 100%'),
        ('4 September 2026', 'on the 2026-09-04 reference date'), ('18 test messages', 'Test inbox messages | **18**'), ('6 of 6 sensitive fixtures were escalated', '6/6 sensitive messages escalated'),
        ('with no draft attached', 'zero drafts attached'), ('external API calls: 0', 'External API calls in the whole flow | **0**'), ('local mock log', 'Every delivery is a local mock log'),
        ('12 stayed 12', '12 reminders after run 1; 12 after run 6'), ('Six sequential follow-up checks', 'six consecutive runs'),
        ('does not prove safe re-import or concurrent delivery', 'It does not establish replay-safe ingestion, concurrency safety'),
        ('8 unattended firings across 9 real days', '8 unattended firings across 9 calendar days'), ('5–13 September 2026', '(2026-09-05 → 09-13)'),
        ('One missed business date was not backfilled', "business date was never"), ('simulated business dates', 'Seven `DUEWATCH_TODAY` business dates'),
        ('Self-review / 6 September 2026', 'On 2026-09-06 the project was put through an adversarial review'), ('four High and three Medium', '7 (4 High, 3 Medium)'),
        ('A9/A10 remains open', 'Acceptance A9/A10 remain open'), ('Import can erase reminder history', 'The ingest path overwrites follow-up history'),
        ('Mixed price-and-complaint messages', "My money hasn't come back and I'm angry"), ('Optional AI drafts can bypass the forbidden-term filter', 'The AI brake can be bypassed'),
        ('Workflow validator is out of date', 'The n8n gate was left behind at an older phase'), ('Simulated dates need an explicit label', 'Simulated dates were narrated as autonomous days'),
        ('Demo figures can drift', 'Demo figures are not bound to a frozen snapshot'), ('History failure can leave a partial result', 'A history failure leaves a partial result'),
        ('Handoff remains unfinished', 'Packaging is genuinely unfinished'), ('More than 60 days', 'active `> 60` days'), ('8–60 days', 'due soon `8–60`'),
        ('0–7 days', '**needs renewal `0–7`**'), ('Before today', 'expired `< 0`'), ('Unclear date or term', 'Ambiguous format is rejected, not guessed'),
        ('An unclear row is flagged while other rows continue', 'Bad rows never stop the run'), ('Back up the master', 'Back up before you write'), ('separate tracked sheet', 'The master is never mutated'),
        ('At exactly 24 hours, no reminder is logged', 'a message at **exactly** 24 hours is `pending`'), ('Customer replied', 'a customer who replied is **skipped**'),
        ('Price question', '`tanya_harga`'), ('Complaint', '`komplain` | `escalate`'), ('Payment problem', '`masalah_pembayaran` | `escalate`'), ('Unclear message', '**the default is a human**'),
        ('leap-year', 'Leap-year behaviour is asserted both ways'),
    ]
    rows = [{'claim': c, 'onPage': c in text, 'needle': n, 'found': n.lower() in dossier.lower()} for c, n in claims]
    illustration = ['Interactive simulation · fictional examples · no messages sent', 'BUSINESS TIME / ILLUSTRATION', 'EXAMPLE CONTRACT', 'Evidence / Recorded, not live',
                    'This illustrates policy; it does not classify text.', 'Contract agenda / separate message triage · Illustration']
    labelled = {s: s in text for s in illustration}
    forbidden = [w for w in ('Upwork', 'Amazon', 'guaranteed', 'real-time', 'real time', '24/7', 'exactly-once', 'replay-safe', 'production ready', 'bulletproof') if re.search(r'\b' + re.escape(w) + r'\b', text, re.I)]
    production = [m.group(0) for m in re.finditer(r'.{0,40}production-ready.{0,20}', text, re.I)]
    production_bad = [x for x in production if 'not claims of a production-ready' not in x]
    live = [m.group(0) for m in re.finditer(r'.{0,30}\blive\b.{0,30}', text, re.I)]
    live_bad = [x for x in live if not re.search(r'no live|not live|live sending is not|No live', x, re.I)]
    ok = all(r['onPage'] and r['found'] for r in rows) and all(labelled.values()) and not forbidden and not live_bad and not production_bad
    detail = (f"{sum(r['onPage'] and r['found'] for r in rows)}/{len(rows)} claims on the page found in the dossier "
              f"({', '.join(r['claim'] for r in rows if not (r['onPage'] and r['found'])) or 'none missing'}); simulation/recorded labels {sum(labelled.values())}/{len(labelled)}; "
              f"forbidden wording {forbidden or 'none'}; 'production-ready' only as a negation={not production_bad}; 'live' only as a negation={not live_bad} ({live})")
    return ok, detail, {'claims': rows, 'labels': labelled, 'forbidden': forbidden, 'live': live, 'production': production}


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
    strip([('m01a-chapter-active.png', 'Orbit .2 · Active'), ('m01b-chapter-due.png', 'Orbit .55 · Due soon'), ('m01c-chapter-renewal.png', 'Orbit end · Renewal')], OUT / 'i01-chapter-pointer.png', P)
    strip([('m01b-chapter-due.png', 'Tap Open case file'), ('m02a-ring-rail.png', 'Ring unfolds into a rail'), ('m02b-case-opened.png', 'Case opens · heading focus')], OUT / 'i02-ring-entry.png', P)
    strip([('m03-hotspot-01.png', '01 Daily expiry check'), ('m03-hotspot-02.png', '02 Message decisions'), ('m03-hotspot-03.png', '03 Saved reminder record')], OUT / 'i03-hotspots.png', P)
    strip([('m04-agenda-61.png', '61 days · Active'), ('m04-agenda-60.png', '60 · Due soon'), ('m04-agenda-8.png', '8 · Due soon'), ('m04-hand-turning-7.png', '7 · hand turning'),
           ('m04-agenda-7.png', '7 · Needs renewal'), ('m04-agenda-0.png', 'Due today · renewal'), ('m04-agenda--1.png', 'Past due · Expired')], OUT / 'i04-agenda-desk.png', P)
    strip([('m04-bad-data.png', 'Unclear date · Bad data'), ('m04-bad-data-agenda.png', 'Own agenda row'), ('m04-agenda-list.png', 'Day chosen · cleared')], OUT / 'i05-bad-data.png', P)
    strip([('m05-module-b.png', 'Module B'), ('m05-message-price.png', 'Price · approved text'), ('m05-handoff-signal.png', 'Signal drops'), ('m05-message-complaint.png', 'Complaint · a person'),
           ('m05-message-unknown.png', 'Unclear · a person'), ('m05-known-gap.png', 'Known gap stated')], OUT / 'i06-human-handoff.png', P)
    strip([('m06-reminder-intro.png', 'Separate example'), ('m06-reminder-24h.png', 'Exactly 24 h · 0'), ('m06-reminder-logged.png', '> 24 h · 1'), ('m06-reminder-replayed.png', '6 replays · still 1'),
           ('m06-reminder-replied.png', 'Customer replied'), ('m06-reminder-replied-first.png', 'Replied first · 0'), ('m06-reminder-limit.png', 'Re-import limit')], OUT / 'i07-reminder-replay.png', P)
    strip([('m04-room-intro.png', 'Two separate routines'), ('m04-module-picker.png', 'Tap A / B'), ('m05-module-b.png', 'One desk at a time'), ('m06z-agenda-kept.png', 'State kept after switch'),
           ('m08-steps.png', 'Steps A/ and B/')], OUT / 'i08-two-modules.png', P)
    strip([('m04-room-intro.png', 'Simulation disclosure'), ('m04-agenda-7.png', 'Business time / illustration'), ('m07-scroll-back-kept.png', 'Still after acting'),
           ('m08-proof.png', 'Recorded, not live')], OUT / 'i09-not-live.png', P)
    strip([('m08-proof.png', '200 per run · 18 messages'), ('m08-proof-ledger.png', '12 stayed 12'), ('m08-dates-note.png', 'Business dates ≠ elapsed days'), ('m08-audit-closed.png', 'Seven defects'),
           ('m08-audit-open.png', 'Findings open'), ('m08g-demo-note.png', 'Video note')], OUT / 'i10-evidence-audit.png', P)
    strip([('m09-next-teaser.png', 'BrandWall teaser'), ('m10a-ring-return.png', 'Rail folds back'), ('m10b-back-at-chapter.png', 'Back at the chapter'),
           ('m11-next-brandwall.png', 'Next → BrandWall')], OUT / 'i11-return-next.png', P)
    strip([('m11-next-brandwall.png', 'BrandWall'), ('m11b-history-back-room.png', 'Back → room works'), ('m12-direct-refresh.png', 'Direct URL + refresh')], OUT / 'i12-history-direct.png', P)
    strip([('m07-rapid-days.png', 'Rapid day taps · one stop'), ('m07-switch-mid-turn.png', 'Switch mid-turn · final'), ('m07-rapid-messages.png', 'Rapid messages · last wins'),
           ('m07-scroll-back-kept.png', 'Scroll away/back · kept'), ('edges/back-during-ring.png', 'Back during the ring'), ('d11a-resized-390.png', 'Resize 1440 → 390 · kept')], OUT / 'i13-interruptions.png', P)
    strip([('m13a-model-arriving.png', 'Case arriving · no leaders'), ('m13b-model-arrived.png', 'Model projected · leaders'), ('m13c-model-failed.png', 'Scene failed · still view'),
           ('m13d-failed-room-works.png', 'Still view · room works')], OUT / 'i14-model-slow-fail.png', P)
    strip([('m14a-reduced-chapter.png', 'Reduced · pointer final'), ('m14b-reduced-hand.png', 'Reduced · hand at once')], OUT / 'i15-reduced-motion.png', P)
    strip([('d01b-chapter-renewal.png', 'Chapter 1440 · Renewal'), ('d02a-ring-rail.png', 'Ring → rail'), ('d05a-two-desks-agenda.png', 'Two desks · A chosen'), ('d05b-two-desks-triage.png', 'Two desks · B chosen'),
           ('d06-reminder-replayed.png', 'Reminder ledger'), ('d08-steps.png', 'Steps in one row'), ('d08-proof.png', 'Three proof columns'), ('d08-dates-note.png', 'Dates note'), ('d08-audit-open.png', 'Audit'),
           ('viewports/two-desks-1920x1080.png', '1920 two desks')], OUT / 'i17-desktop.png', D)
    grid = Image.new('RGB', (P[0] * 4, P[1] * 3), 'black')
    for c, tag in enumerate(['390x844', '360x740', '430x932', '768x1024']):
        for r, kind in enumerate(['chapter', 'agenda', 'human-handoff']):
            source = OUT / 'viewports' / f'{kind}-{tag}.png'
            if source.exists():
                grid.paste(tile(source, f'{tag} · {kind}', P), (c * P[0], r * P[1]))
    grid.save(OUT / 'i16-viewports.jpg', quality=85)
    contact([
        ('m01a-chapter-active.png', 'Chapter · Active'), ('m01c-chapter-renewal.png', 'Chapter · Renewal'), ('m02a-ring-rail.png', 'Ring → agenda rail'), ('m02b-case-opened.png', 'Case opened'),
        ('m03-hotspot-01.png', 'Hotspot 01'), ('m03-hotspot-02.png', 'Hotspot 02'), ('m03-hotspot-03.png', 'Hotspot 03'), ('m04-room-intro.png', 'Two routines'),
        ('m04-agenda-61.png', '61 days · Active'), ('m04-hand-turning-7.png', 'Hand turning'), ('m04-agenda-7.png', '7 days · renewal'), ('m04-agenda--1.png', 'Past due'),
        ('m04-bad-data.png', 'Bad data'), ('m04-agenda-list.png', 'Agenda rows'), ('m05-module-b.png', 'Module B'), ('m05-message-price.png', 'Approved text'),
        ('m05-message-complaint.png', 'Stop → a person'), ('m05-known-gap.png', 'Known gap'), ('m06-reminder-24h.png', 'Exactly 24 h'), ('m06-reminder-replayed.png', 'Six replays · 1'),
        ('m06-reminder-replied-first.png', 'Replied · 0'), ('m07-rapid-days.png', 'Rapid taps'), ('m08-proof.png', 'Recorded proof'), ('m08-dates-note.png', 'Business dates'),
        ('m08-audit-open.png', 'Seven findings'), ('m09-next-teaser.png', 'BrandWall teaser'), ('m10a-ring-return.png', 'Ring return'), ('m10b-back-at-chapter.png', 'Back at chapter'),
    ], OUT / 'contact-sheet-mobile.jpg', P, 7)
    contact([
        ('d01a-chapter-active.png', 'Chapter · Active'), ('d01b-chapter-renewal.png', 'Chapter · Renewal'), ('d02a-ring-rail.png', 'Ring → rail'), ('d03-hotspot-decisions.png', 'Hotspot · decisions'),
        ('d04-room-intro.png', 'Room intro'), ('d04-agenda-7.png', 'Agenda · renewal'), ('d04-bad-data.png', 'Bad data'), ('d05a-two-desks-agenda.png', 'Two desks · A'),
        ('d05-message-complaint.png', 'Complaint · a person'), ('d05b-two-desks-triage.png', 'Two desks · B'), ('d06-reminder-replayed.png', 'Six replays · 1'), ('d06-reminder-replied-first.png', 'Replied first'),
        ('d07-rapid-days.png', 'Rapid taps'), ('d08-steps.png', 'Steps'), ('d08-proof.png', 'Proof columns'), ('d08-dates-note.png', 'Business dates'),
        ('d08-audit-open.png', 'Audit'), ('d09-next-teaser.png', 'Next teaser'), ('d10a-ring-return.png', 'Ring return'), ('d10b-back-at-chapter.png', 'Back at chapter'),
    ], OUT / 'contact-sheet-desktop.jpg', D, 4)


# ---------------------------------------------------------------- verdicts
def agenda_ok(ag):
    stops = ag['stops']
    rooms = all(stops[d]['room']['category'] == CATEGORY[d] and len(stops[d]['room']['current']) == 1 and stops[d]['room']['marker'] == 'Example here'
                and stops[d]['room']['pressedDays'] == [d] and abs(stops[d]['room']['handAngle'] - ANGLE[d]) < .6 for d in stops)
    return rooms and all(stops[d]['motion']['ok'] for d in stops)


def agenda_text(ag):
    return '; '.join(f"{d} → {s['room']['heading']} ({s['room']['current']}) hand {s['motion'].get('from')}°→{s['motion'].get('to')}° settled {s['motion'].get('settleMs')} ms "
                     f"(first frame {s['motion'].get('firstAngle')}°, overshoot={s['motion'].get('overshoot')}), card in {s['motion'].get('cardSettledMs')} ms from {s['motion'].get('cardStart')}, ok={s['motion']['ok']}"
                     for d, s in ag['stops'].items())


def triage_ok(tr):
    return all(r['room']['route'] == r['expected'] and r['motion']['ok'] and r['room']['pressedMessage'] == [n]
               and (('Stop → a person takes over' == r['room']['handoffTitle'] and 'No reply draft attached' in r['room']['handoff']) if r['expected'] == 'human'
                    else ('Approved text → mock reply' == r['room']['handoffTitle'] and 'Local mock log only' in r['room']['handoff']))
               for n, r in tr['routes'].items())


def verdicts(m, d, vp, edges, slow, reduced, fps, back_flight, sources):
    if m:
        s = m['story']
        order = [o for o in s['order'] if o is not None]
        check('story', order == sorted(order) and len(order) == 7 and m['stripBelowCta'] and s['draft'] == [] and 'DRAFT' not in m['stripText']
              and 'Two separate routines' in s['intro'] and 'no messages sent' in s['disclosure'] and 'Recorded, not live' in s['evidenceKicker'],
              f"case sections in story order={order == sorted(order)} ({len(order)}/7: brief, instrument, time control room, recorded proof + audit, readings, demo, Next); pointer strip under the CTA={m['stripBelowCta']}; "
              f"intro '{s['intro'][s['intro'].find('Two'):][:110]}'; disclosure '{s['disclosure']}'; proof kicker '{s['evidenceKicker']}'; DRAFT labels on case {s['draft']} + chapter strip={'DRAFT' in m['stripText']} (copy approved at gate 7D)",
              'i08-two-modules.png')
        mc, dc = m['chapter'], d['chapter'] if d else {}
        check('chapterPointer', mc['ok'] and dc.get('ok'),
              f"phone swipe {mc['samples']} samples ({mc['midSamples']} mid-orbit): pointer = orbit (max error {mc['maxError']}), monotone={mc['monotone']}, end pointer {mc['end']['pointer']}; swipe back → {mc['back']['pointer'] if mc['back'] else '?'}; "
              f"still when idle={mc['stillWhenIdle']} | desktop wheel {dc.get('samples')} samples same rule={dc.get('ok')} (max error {dc.get('maxError')}); labels '{m['stripText']}'", 'i01-chapter-pointer.png')
        ri, dri = m['ringIn'], d['ringIn'] if d else {}
        check('ringEntry', ri['ok'] and ri['focus'] == 'case-heading' and dri.get('ok') and dri.get('focus') == 'case-heading',
              f"phone: ring visible {ri.get('visibleMs')} ms over {ri['visibleFrames']} frames, from the orrery at {ri.get('orbitPoint')} as scale/rotation {ri.get('firstPose')} to an agenda rail {ri.get('railWidthPx')} px wide {ri.get('railPose')} centred {ri.get('railCentre')} "
              f"(monotone={ri.get('monotone')}), cleared after; focus #{ri['focus']} | desktop: {dri.get('visibleMs')} ms from {dri.get('orbitPoint')} to a {dri.get('railWidthPx')} px rail at {dri.get('railCentre')}, focus #{dri.get('focus')}", 'i02-ring-entry.png')
        cards = m['hotspots']
        explain = ['leap-year' in cards[0]['body'] and 'flagged for a person' in cards[0]['body'], 'Six sensitive fixtures' in cards[1]['body'] and 'mixed-intent weakness' in cards[1]['body'],
                   'Repeat checks on the same saved ledger add nothing' in cards[2]['body'] and 'Re-import can erase' in cards[2]['body']]
        check('hotspots', all(c['inside'] for c in cards) and all(c['leader'] > .3 for c in cards) and all(explain) and [c['title'] for c in cards] == ['Daily expiry check', 'Message decisions', 'Saved reminder record'],
              f"cards {[c['title'] for c in cards]} inside viewport={[c['inside'] for c in cards]}, leader opacity {[round(c['leader'], 2) for c in cards]}; "
              f"bodies explain recompute + unclear dates to a person / six fixtures + mixed-intent weakness / same ledger adds nothing + re-import limit={explain}", 'i03-hotspots.png')
        ma, da = m['agenda'], d['agenda'] if d else None
        check('agendaDesk', agenda_ok(ma) and bool(da) and agenda_ok(da) and ma['initialRoom']['category'] == 'active',
              'phone (tap): ' + agenda_text(ma) + (' | desktop (click): ' + agenda_text(da) if da else ''), 'i04-agenda-desk.png')
        b, cl = ma['bad'], ma['cleared']
        bad_ok = lambda b, cl: (b['category'] == 'bad' and b['heading'] == 'Bad data' and 'cannot be read safely' in b['result'] and 'Keep checking the others' in b['result']  # noqa: E731
                                and b['current'] == ['Bad data'] and b['badPressed'] == 'true' and b['pressedDays'] == [] and cl['category'] == 'renew' and cl['badPressed'] == 'false')
        check('badData', bad_ok(b, cl) and (not d or bad_ok(d['agenda']['bad'], d['agenda']['cleared'])),
              f"unclear date → '{b['heading']}': '{b['result']}', agenda row {b['current']}, day buttons pressed {b['pressedDays']}, hand left at {b['handAngle']}°; choosing 7 days → {cl['category']} (unclear released={cl['badPressed']}); desktop same={bool(d) and bad_ok(d['agenda']['bad'], d['agenda']['cleared'])}", 'i05-bad-data.png')
        mt, dt = m['triage'], d['triage'] if d else None
        gap_ok = 'mixed-intent' in mt['gap'] and 'known bypass' in mt['gap']
        check('humanHandoff', triage_ok(mt) and bool(dt) and triage_ok(dt) and gap_ok,
              'phone: ' + '; '.join(f"{n} → '{r['room']['handoffTitle']}' signal {r['motion'].get('startY')}→{r['motion'].get('endY')} px in {r['motion'].get('settleMs')} ms" for n, r in mt['routes'].items())
              + f"; human routes carry 'No reply draft attached', reply routes 'Local mock log only'; gap note '{mt['gap']}' | desktop all six={bool(dt) and triage_ok(dt)}", 'i06-human-handoff.png')
        mr, dr = m['reminders'], d['reminders'] if d else None
        check('reminderReplay', reminder_ok(mr['sequence']) and bool(dr) and reminder_ok(dr['sequence']) and 'independent of the category' in mr['intro'] and 'import can erase reminder history' in mr['limit'],
              'phone: ' + ' → '.join(f"{r[0]} {r[1]}/{r[2]}" for r in mr['sequence']) + f"; limit '{mr['limit']}' | desktop same sequence={bool(dr) and reminder_ok(dr['sequence'])}", 'i07-reminder-replay.png')
        sw = m['triage']['switchedIn']
        st = m['stateAfterSwitch']
        targets_ok = all(w >= 44 and h >= 44 for w, h in m['targets'])
        lay = d['layout'] if d else {}
        both = bool(lay) and lay['triage'][0] > lay['agenda'][0] + lay['agenda'][2] and abs(lay['triage'][1] - lay['agenda'][1]) < 3
        check('twoModules', 'A contract status does not send a message' in s['intro'] and sw['before']['module'] == 'agenda' and sw['before']['agendaVisible'] and not sw['before']['triageVisible']
              and sw['after']['module'] == 'triage' and sw['after']['triageVisible'] and not sw['after']['agendaVisible'] and st['agenda']['category'] == 'renew' and abs(st['agenda']['handAngle'] - ANGLE['7']) < .6
              and st['triage']['route'] == 'human' and st['triage']['ledgerResult'] == 'logged' and targets_ok and 'independent of the category chosen above' in mr['intro']
              and [x[:4] for x in s['steps']] == ['A / ', 'A / ', 'B / ', 'B / '] and s['agendaHeading'] != s['triageHeading'] and both,
              f"intro says a contract status does not send a message; phone before tap: agenda shown={sw['before']['agendaVisible']}, triage shown={sw['before']['triageVisible']} → after B: agenda {sw['after']['agendaVisible']}, triage {sw['after']['triageVisible']}; "
              f"switch back keeps agenda {st['agenda']['category']} at {st['agenda']['handAngle']}° and triage {st['triage']['route']} / ledger {st['triage']['ledger']} {st['triage']['ledgerResult']}; {len(m['targets'])} visible buttons ≥44 px={targets_ok}; "
              f"steps {[x[:4] for x in s['steps']]}; headings '{s['agendaHeading']}' vs '{s['triageHeading']}'; desktop desks side by side={both}", 'i08-two-modules.png')
        it = m['interrupt']
        live_ok = bool(sources) and all(sources[2]['labels'].values()) and not [x for x in sources[2]['live'] if not re.search(r'no live|not live|live sending is not', x, re.I)]
        countdown = re.findall(r'\b\d{1,2}:\d{2}\b|countdown|hurry|urgent', s['text'], re.I)
        check('notLive', it['idleStill'] and bool(d) and d['interrupt']['idleStill'] and mc['stillWhenIdle'] and ma['clockLabel'] == 'BUSINESS TIME / ILLUSTRATION' and live_ok
              and 'dates move only when you choose' in ma['footnote'] and countdown == ['countdown'] and 'no messages sent' in s['disclosure'],
              f"disclosure '{s['disclosure']}'; dial '{ma['clockLabel']}'; footnote '{ma['footnote']}'; hand/category/route/signal/ledger/text still for 2.1 s idle phone={it['idleStill']} desktop={bool(d) and d['interrupt']['idleStill']}; "
              f"chapter still={mc['stillWhenIdle']}; clock-time / urgency words on the page {countdown} (only in 'No live countdown'); 'live' only as a negation={live_ok}", 'i09-not-live.png')
        proof = s['proof']
        audit = s['audit']
        sev = [a[0] for a in audit]
        ev_ok = (proof[0][1] == '200 per run.' and '45 difficult date rows' in proof[0][2] and '7 of 7' in proof[0][2] and proof[1][1] == '18 test messages.' and '6 of 6' in proof[1][2]
                 and 'external API calls: 0' in proof[1][2] and proof[2][1] == '12 stayed 12.' and 'does not prove safe re-import' in proof[2][2]
                 and 'simulated business dates' in s['dates'] and '8 unattended firings across 9 real days' in s['dates'] and 'not backfilled' in s['dates']
                 and len(audit) == 7 and sev.count('High') == 4 and sev.count('Medium') == 3 and m['evidence']['opened'] == 7 and 'A9/A10' in s['evidence']
                 and 'not claims of a production-ready system' in s['evidence'] and 'simulated business dates' in s['demo'])
        check('evidenceAudit', ev_ok and (not d or d['evidence']['opened'] == 7),
              f"proof columns {[p[1] for p in proof]} ({[p[0] for p in proof]}); dates note: simulated video dates vs 8 firings / 9 real days, missed date not backfilled; audit {len(audit)} findings {sev.count('High')} High / {sev.count('Medium')} Medium, "
              f"opened phone {m['evidence']['opened']}/7 desktop {d and d['evidence']['opened']}/7; A9/A10 open; production-ready only as a negation; demo note '{s['demo'][:90]}…'", 'i10-evidence-audit.png')
        rt = m['return']
        drt = d['return'] if d else {}
        same = [rt.get('orbitPoint') and dist(rt['orbitPoint'], ri['orbitPoint']) < 4, drt.get('orbitPoint') and dri.get('orbitPoint') and dist(drt['orbitPoint'], dri['orbitPoint']) < 4]
        check('returnNext', rt['ok'] and all(same) and rt['scrollDelta'] < 3 and rt['focus'] == 'duewatch' and s['teaser'] and 'BrandWall' in s['teaser'] and drt.get('ok') and drt.get('scrollDelta', 9) < 3,
              f"phone: rail {rt.get('railPose')} folds back into the ring {rt.get('lastPose')} in {rt.get('visibleMs')} ms onto {rt.get('orbitPoint')}, the point it left from {ri.get('orbitPoint')} (same={same[0]}), saved chapter position ±{rt['scrollDelta']:.1f} px, focus on Open case file={rt['focus'] == 'duewatch'}; "
              f"teaser '{s['teaser']}', Next opened BrandWall; desktop onto {drt.get('orbitPoint')} left from {dri.get('orbitPoint')} (same={same[1]}) ±{drt.get('scrollDelta')} px", 'i11-return-next.png')
        h, di = m['history'], m['direct']
        check('historyDirect', h['backOk'] and h['backRoom'][0] == 'expired' and h['forwardOk'] and h['canvas'] and di['direct'][0] == 'renew' and di['directLedger'][:2] == ['1', 'logged']
              and di['refreshed'] == {'module': 'agenda', 'category': 'active', 'handAngle': -105, 'route': 'human', 'ledger': '0', 'ledgerResult': 'pending'} and not di['errors'] and not di['bad'],
              f"Back BrandWall → DueWatch room works (past due → {h['backRoom']})={h['backOk']}, Forward → BrandWall={h['forwardOk']}, same Canvas={h['canvas']}; direct /work/duewatch due today → {di['direct']}, reminder → {di['directLedger'][:2]}; "
              f"refresh → {di['refreshed']} (illustration restarts); errors {len(di['errors'])}, ≥400 {len(di['bad'])}", 'i12-history-direct.png')
        rd, rm, kb, km = it['rapidDays'], it['rapidMessages'], it['keyboard'], it['keyboardMessage']
        sm = it['switchMidTurn']
        rapid_ok = abs(rd['final'][0] - ANGLE['-1']) < .6 and rd['final'][1] == 'expired' and rd['final'][2] == 0 and rd['maxAnimations'] <= 1 and rd['room']['current'] == ['Expired']
        switch_ok = sm['triageShown'] and sm['agenda'][0] == 'due' and abs(sm['agenda'][1] - ANGLE['8']) < .6 and sm['agenda'][2] == 0 and sm['agenda'][3]
        msg_ok = rm['route'] == 'human' and rm['pressed'] == ['payment'] and 'matrix(1, 0, 0, 1, 0, 24)' == rm['dot']
        kb_ok = bool(kb['firstRenewFrame']) and abs(kb['firstRenewFrame']['a'] - ANGLE['0']) < .6 and kb['animations'] == 0 and km['route'] == 'human' and km['animations'] == 0
        dint = d['interrupt'] if d else {}
        d_ok = bool(dint) and abs(dint['rapidDays']['final'][0] - ANGLE['-1']) < .6 and dint['rapidMessages']['route'] == 'human' and dint['scrollBack']['same'] and dint['keyboard']['animations'] == 0
        rz = d['resize'] if d else None
        rz_ok = bool(rz) and all(x['overflow'] <= 1 and x['category'] == 'renew' and abs(x['hand'] - ANGLE['0']) < .6 and x['route'] == 'human' and x['ledger'] == ['1', 'duplicate'] for x in rz['after']) and rz['canvas'] \
            and all(x['visible'] == [True, True] for x in rz['after'] if int(x['size'].split('x')[0]) >= 1024) and all(x['visible'].count(True) == 1 for x in rz['after'] if int(x['size'].split('x')[0]) < 1024)
        bf = back_flight or {}
        check('interruptions', m['doubleTap']['historyDelta'] == 1 and rapid_ok and switch_ok and msg_ok and it['scrollBack']['same'] and kb_ok and d_ok
              and bf.get('ringOpacity') == 0 and bf.get('direction') == 'idle' and bf.get('path') == '/' and bf.get('contentOpacity', 0) > .99 and rz_ok and edges and edges.get('history-interruption') == 'passed',
              f"double tap Open case file → history +{m['doubleTap']['historyDelta']} ({m['doubleTap']['second']}); 12 day taps 40 ms apart → hand {rd['final'][0]}° {rd['final'][1]}, running animations {rd['final'][2]} (max {rd['maxAnimations']}); "
              f"switch to B 150 ms into a turn and back → {sm['agenda']} (category, angle, animations, shown); 12 alternating message taps → {rm['route']} {rm['pressed']} signal {rm['dot']}; scroll to readings and back same={it['scrollBack']['same']} {it['scrollBack']['state']}; "
              f"keyboard Enter → hand {kb['firstRenewFrame'] and kb['firstRenewFrame']['a']}° on the first frame, animations {kb['animations']}, message animations {km['animations']}; desktop rapid/scroll/keyboard={d_ok}; "
              f"Back 0.3 s into the return ring (mid {bf.get('midFlight')}) → opacity {bf.get('ringOpacity')} '{bf.get('direction')}' on {bf.get('path')}, content {bf.get('contentOpacity')}; "
              + (f"resize after acting 1440→390/1024/900/1920/1440: overflow {[x['overflow'] for x in rz['after']]}, state {[(x['category'], x['route'], x['ledger'][0]) for x in rz['after']]}, desks shown {[x['visible'] for x in rz['after']]}" if rz else 'resize not run')
              + f"; Development edge history-interruption={edges and edges.get('history-interruption')}", 'i13-interruptions.png')
    if slow:
        fl, bad = slow['flight'], slow['failed']
        check('modelSlowFail', not fl['strayLeaders'] and fl['leaderAfter'] > .3 and bad['scene'] == 'fallback' and bad['live'] == 0 and bad['maxLeader'] == 0 and bad['still'] > 100
              and bad['room'] == ['expired', 'human'] and edges and edges.get('fallback') == 'passed' and edges.get('slow') == 'passed',
              f"instruments are procedural (no instrument download can stall); ring flight polled {fl['samples']}×: leaders visible without a projected model {len(fl['strayLeaders'])}×, "
              f"case frames before projection {fl['onCaseWithoutLive']} with leaders hidden, leader opacity {round(fl['leaderAfter'], 2)} once live; scene failed (ambient.glb blocked): scene '{bad['scene']}', "
              f"leaders {bad['live']}/{bad['maxLeader']}, still image {round(bad['still'])} px, room past due + payment → {bad['room']}; Development fallback/slow ambient={edges and edges.get('fallback')}/{edges and edges.get('slow')}", 'i14-model-slow-fail.png')
    if reduced:
        ch, hf = reduced['chapter'], reduced['handFirstExpired']
        check('reducedMotion', reduced['ringMaxOpacity'] == 0 and reduced['ringDisplay'] == 'none' and ch['pointer'] > .97 and hf and abs(hf['a'] - ANGLE['-1']) < .6
              and reduced['handAnimations'] == 0 and reduced['dotAnimations'] == 0 and abs(reduced['dotY'] - 24) < .2 and reduced['route'] == 'human' and edges and edges.get('reduced') == 'passed',
              f"ring display '{reduced['ringDisplay']}', max opacity {reduced['ringMaxOpacity']} during entry; chapter at orbit {round(ch['orbit'], 2)} pointer already final ({ch['pointer']}); "
              f"past due tap → hand {hf and hf['a']}° on the first expired frame, animations {reduced['handAnimations']}; complaint → signal at {reduced['dotY']} px, animations {reduced['dotAnimations']}; Development reduced exercise={edges and edges.get('reduced')}", 'i15-reduced-motion.png')
    if vp:
        phones = [r for r in vp if int(r['viewport'].split('x')[0]) < 1024]
        wide = [r for r in vp if int(r['viewport'].split('x')[0]) >= 1024]
        check('mobileViewports', len(phones) == 4 and all(r['pass'] for r in phones),
              '; '.join(f"{r['viewport']} {'pass (chapter pointer x ' + str([round(x) for x in r['chapterPositions']]) + ')' if r['pass'] else 'FAIL ' + r.get('error', '')}" for r in phones), 'i16-viewports.jpg')
        lay, lt = (d['layout'], d['layoutTriage']) if d else ({}, {})
        amber_rgb = None
        comp = False
        if lay:
            hexa = lay['amber'].lstrip('#')
            amber_rgb = f"rgb({int(hexa[0:2], 16)}, {int(hexa[2:4], 16)}, {int(hexa[4:6], 16)})" if len(hexa) == 6 else lay['amber']
            comp = (lay['triage'][0] > lay['agenda'][0] + lay['agenda'][2] and abs(lay['triage'][1] - lay['agenda'][1]) < 3 and lay['agenda'][2] > lay['triage'][2]
                    and lay['agendaBorder'] == amber_rgb and lay['triageBorder'] != amber_rgb and lt['triageBorder'] == amber_rgb and lt['agendaBorder'] != amber_rgb
                    and 'gradient' in lay['agendaBg'] and len(set(lay['steps'])) == 1 and len(set(lay['proof'])) == 1 and len(lay['dates']) == 2 and lay['dates'][1][0] > lay['dates'][0][0]
                    and abs(lay['dates'][1][1] - lay['dates'][0][1]) < 80 and lay['audit'][2] <= 900 and abs(lay['audit'][1] - (lay['triage'][0] + lay['triage'][2])) <= 2)
        check('desktopComposition', len(wide) == 2 and all(r['pass'] for r in wide) and comp,
              f"1440/1920 Development checks {[r['viewport'] + ' ' + ('pass' if r['pass'] else 'FAIL') for r in wide]}; agenda desk x/y/width {lay.get('agenda')} beside triage {lay.get('triage')} (agenda wider); "
              f"chosen module outlined {amber_rgb}: A chosen → agenda {lay.get('agendaBorder')} / triage {lay.get('triageBorder')}, B chosen → agenda {lt.get('agendaBorder')} / triage {lt.get('triageBorder')}; warm gradient={'gradient' in lay.get('agendaBg', '')}; "
              f"steps one row {lay.get('steps')}; proof columns one row {lay.get('proof')}; dates note two columns {lay.get('dates')}; audit {lay.get('audit')} right edge = triage desk right edge {lay and lay['triage'][0] + lay['triage'][2]}", 'i17-desktop.png')
    if sources:
        check('sources', sources[0], sources[1], 'i10-evidence-audit.png', data=sources[2])
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
    full = {'time', 'time-state', 'perf-duewatch', 'audio', 'desktop-a', 'desktop-b', 'perf-crosscheck', 'perf-surgeline', 'perf-driftwatch'}
    suites = [{'suite': n, 'status': ledger_data.get(n, {}).get('status', 'missing'), 'current': ledger_data.get(n, {}).get('fingerprint') == fp,
               'phones': ledger_data.get(n, {}).get('phones'), 'finishedAt': ledger_data.get(n, {}).get('finishedAt')} for n in rr.SUITES]
    check('regressions', len(suites) == 16 and all(s['status'] == 'passed' and s['current'] and (s['suite'] not in full or s['phones'] in ('full', None)) for s in suites),
          f"source fingerprint {fp}; " + '; '.join(f"{s['suite']}={s['status']}{'' if s['current'] else ' (stale)'} {s['phones']}" for s in suites), 'i16-viewports.jpg', suites=suites)


OWNER_NOTES = [  # findings from reviewing the 2026-09-17 Testing pack that need an owner decision
    "Accepted at gate 7D — ring → agenda rail reads faintly: the ring is a 1 px outline, so scaling it to a flat rail (scaleY .13; 1000 px wide on desktop) leaves hairline strokes over the moving orrery, "
    "and the rail fades before the case appears at its Brief (the agenda desk is further down). Motion and timing pass (720 + 180 ms, lands on its origin). Accept, or return to Development "
    "for a stronger stroke / rail (m02a-ring-rail.png, d02a-ring-rail.png, slow-motion clips 2 and 9).",
    "Accepted at gate 7D — the dial's six ticks carry no labels; the chosen day button, the result card and the agenda row marked 'Example here' name the category. Accept, or add tick labels in Development (m04-agenda-7.png).",
    "Development follow-ups closed on the integrated build: the time suite now passes six viewports + edges (fallback allows only the deliberately blocked ambient model error); perf-surgeline passes at 57.0–60.0 fps "
    "(≤3.0% slow). The earlier 18.9% / 21.6% slow frames were measured on the isolated copy and did not reproduce. One stale test fixed: verify_cases expected the old DueWatch hotspot title.",
]


def owner_notes(m):
    notes = ["Approved at gate 7D (2026-09-18), DRAFT labels removed — copy 7D: chapter pitch + pointer strip, deck/brief/instrument heading, three hotspot bodies, time control room (intro, disclosure, module A agenda: day controls, five categories and actions, footnote; "
             "module B: six example categories, handoff texts, known-gap note; separate reminder example: four checks, ledger texts, reset, limit), four steps, recorded proof (three columns, business-date note, seven audit findings) and the BrandWall teaser."]
    notes.extend(OWNER_NOTES)
    notes.append("Refresh on /work/duewatch restarts the illustration at 61 days, module A and 0 reminders (no saved state), same as SurgeLine and DriftWatch — by design.")
    notes.append("Rig limits: headless Chromium on the laptop GPU, CPU throttled 4x; the host GPU is not throttled. Physical phone = Phase 8.")
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
    load = Path('/proc/loadavg').read_text().split()[:3]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        try:
            fps = await perf(browser)
        finally:
            await browser.close()
    verdicts(None, None, None, None, None, None, fps, None, None)
    attempts = report['measurements'].get('fps4xAttempts') or [{'finishedAt': report['finishedAt'], 'fps4x': report['measurements']['fps4x'], 'pass': report['items']['performance']['pass']}]
    attempts.append({'finishedAt': datetime.now(timezone.utc).isoformat(), 'loadAvgBefore': load, 'fps4x': fps, 'pass': CHECKS['performance']['pass']})
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
            mobile = await step('phone walkthrough (recorded)', mobile_walk(browser), ['story', 'chapterPointer', 'ringEntry', 'hotspots', 'agendaDesk', 'badData', 'humanHandoff', 'reminderReplay', 'twoModules', 'notLive', 'evidenceAudit', 'returnNext', 'historyDirect', 'interruptions', 'clean', 'sources'], tag='mobile')
            desktop = await step('desktop walkthrough (recorded)', desktop_walk(browser), ['desktopComposition'], tag='desktop')
            back_flight = await step('back during the ring', back_during_flight(browser), tag='back')
            slow = await step('model late / failed', model_slow_fail(browser), 'modelSlowFail', tag='slow')
            reduced = await step('reduced motion', reduced_motion(browser), 'reducedMotion', tag='reduced')
            vp = await step('six viewports + edges (verify_duewatch_room)', viewports(browser), ['mobileViewports', 'desktopComposition'], tag='viewports')
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
            sources = sources_check(m['story']['text'] + '\n' + m['story']['labels'], m['hotspots'], m['stripText'] + '\n' + (m['stripLabel'] or ''))
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
            (mp4m, mm['chapter'], min(mm['chapter'] + 4, mm['chapterEnd']), 'Phone - business-time pointer follows the orbit', 390),
            (mp4m, mm['entry'] - .4, mm['entryEnd'] + .4, 'Phone - orbit ring unfolds into the agenda rail', 390),
            (mp4m, mm['agenda'] - .3, min(mm['agenda'] + 6, mm['agendaEnd']), 'Phone - hand turns to each boundary', 390),
            (mp4m, mm['bad'] - .3, mm['badEnd'], 'Phone - unclear date goes to a person', 390),
            (mp4m, mm['triage'] - .3, min(mm['triage'] + 6, mm['triageEnd']), 'Phone - approved text vs stop at a person', 390),
            (mp4m, mm['reminder'] - .3, min(mm['reminder'] + 5, mm['reminderEnd']), 'Phone - replay adds no reminder', 390),
            (mp4m, mm['rapid'] - .3, mm['rapidEnd'], 'Phone - rapid taps settle once', 390),
            (mp4m, mm['return'] - .4, mm['returnEnd'] + .4, 'Phone - rail folds back to the orrery', 390),
            (mp4d, dm['entry'] - .4, dm['entryEnd'] + .4, 'Desktop - ring into the case', 720),
            (mp4d, dm['agenda'] - .3, min(dm['agenda'] + 5, dm['agendaEnd']), 'Desktop - agenda beside the triage desk', 720),
            (mp4d, dm['return'] - .4, dm['returnEnd'] + .4, 'Desktop - ring return', 720),
            (mp4d, dm['resize'] - .3, min(dm['resize'] + 4, dm['resizeEnd']), 'Desktop - resize keeps every state', 720),
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
        'phase': 'Phase 7D — DueWatch: time control room',
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
