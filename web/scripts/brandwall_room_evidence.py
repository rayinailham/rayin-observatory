"""Phase 7E Testing evidence pack — BrandWall visual studio (light Testing rule Q47, PLAN §12.3).

Only the new 7E features, at 390×844 (touch, DPR 2) and 1440×900 (mouse wheel):
chapter spectrum → prism flight → recorded specimen pairs compared by tap → measured boundaries →
seven rules + limits → Return docks at the prism → Next reintroduces CrossCheck.
Development checks run inside the pack (Q42): verify_brandwall_room.viewport at both sizes and
verify_brandwall_room.edges once at 390×844 (reduced, blocked model, slow model, Back during flight, resize).
Frame rate is read from perf_quick's Development report when the source fingerprint matches (Q47).

Writes assets/renders/personal-brandwall/evidence/: walkthrough-mobile.mp4, walkthrough-desktop.mp4 (≤ ~90 s each),
PNG per item, contact-sheet.jpg, evidence.json. Exit 1 if an item fails. Server :8767 must run a build of this source.
"""
import asyncio
import json
import re
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

import crosscheck_room_evidence as cre
import run_regressions as rr
import verify_brandwall_room as vbr
from case_files_evidence import tile
from crosscheck_room_evidence import Walk, duration, encode, swipe_until, top_of, wheel_until
from verify_case import URL, enter, idle
from perf_quick import GPU, land

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/personal-brandwall/evidence'
RAW = OUT / 'raw'
cre.OUT, cre.RAW = OUT, RAW  # Walk.shot writes into this pack
DOSSIER = ROOT / 'portfolio/CAPABILITY_BRANDWALL.md'
SPECIMENS = ('portrait', 'contrast', 'name')
MODES = (('before', 'inset(0px 100% 0px 0px)'), ('split', 'inset(0px 50% 0px 0px)'), ('after', 'inset(0px 0% 0px 0px)'))
AXES = (('ratio', '1.00', '1.25'), ('light', '0.30', '0.35'), ('length', '28', '32'))

FLIGHT = """()=>{const w=window.__flight=[];const t0=performance.now();const e=document.querySelector('.brand-flight');
const f=()=>{const s=getComputedStyle(e);const m=new DOMMatrix(s.transform==='none'?undefined:s.transform);
w.push({t:Math.round(performance.now()-t0),o:+(+s.opacity).toFixed(3),d:e.dataset.direction,x:Math.round(m.e),y:Math.round(m.f),
sx:+Math.hypot(m.a,m.b).toFixed(3),sy:+Math.hypot(m.c,m.d).toFixed(3),path:location.pathname});
if(performance.now()-t0<2800)requestAnimationFrame(f)};requestAnimationFrame(f)}"""
BEAM = "()=>{const s=document.querySelector('#brandwall');const b=document.querySelector('.brand-chapter-beam');" \
       "return {scale:+new DOMMatrix(getComputedStyle(b).transform).a.toFixed(3),orbit:+(+getComputedStyle(document.documentElement).getPropertyValue('--instrument-4-orbit')||0).toFixed(3)," \
       "mark:+getComputedStyle(document.querySelector('.brand-chapter-specimens i')).opacity}}"
# The comparison: stacked captures share one frame, reveal is a clip; nothing may cover the specimen.
PAIR = """()=>{const q=s=>document.querySelector(s);const st=q('.brand-studio');const pair=q('.brand-pair');const r=pair.getBoundingClientRect();
const imgs=[...pair.querySelectorAll('.brand-image')].map(e=>{const b=e.getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)]});
const svg=pair.querySelector('svg');const vb=svg.viewBox.baseVal;const sb=svg.getBoundingClientRect();
const points=[[.25,.3],[.5,.5],[.75,.7],[.1,.9],[.9,.15]].map(([a,b])=>{const e=document.elementFromPoint(r.x+r.width*a,r.y+r.height*b);return !!e&&(pair.contains(e))});
const seam=q('.brand-seam');const flight=q('.brand-flight');
return {specimen:st.dataset.specimen,view:st.dataset.view,clip:getComputedStyle(q('.brand-after')).clipPath,views:[...pair.querySelectorAll('svg')].map(e=>e.getAttribute('viewBox')),
images:imgs,pair:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)],scale:+Math.min(sb.width/vb.width,sb.height/vb.height).toFixed(3),
unobstructed:points,seamOpacity:+getComputedStyle(seam).opacity,seamLeft:seam.style.left,flightOpacity:+getComputedStyle(flight).opacity,
verdict:q('.brand-verdict').textContent,title:q('.brand-comparison h3').textContent,caption:q('.brand-caption').textContent,measure:q('.brand-annotation').textContent,
pressed:[...document.querySelectorAll('[data-brand-view][aria-pressed=true]')].map(e=>e.dataset.brandView),
targets:[...document.querySelectorAll('[data-brand-view],[data-specimen-choice]')].map(e=>{const b=e.getBoundingClientRect();return [Math.round(b.width),Math.round(b.height)]}),
verdictFont:parseFloat(getComputedStyle(q('.brand-verdict')).fontSize),overflow:document.documentElement.scrollWidth-innerWidth}}"""
STORY = """()=>{const q=s=>document.querySelector(s);const t=s=>q(s)?q(s).innerText:'';
const order=['.case-brief','#case-instrument','.brand-studio','.brand-evidence','.brand-rules','.brand-record','.case-next'].map(s=>q(s)?Math.round(q(s).getBoundingClientRect().top+scrollY):null);
return {order,text:document.querySelector('.case-page').textContent,draft:document.querySelectorAll('.case-page .draft-label').length,
steps:[...document.querySelectorAll('.brand-steps li')].map(e=>e.textContent),teaser:t('.case-next'),record:t('.brand-record'),rules:t('.brand-rules'),
fonts:[...document.querySelectorAll('.brand-studio *,.brand-evidence *')].filter(e=>e.childNodes.length&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&e.getClientRects().length).map(e=>parseFloat(getComputedStyle(e).fontSize)).reduce((a,b)=>Math.min(a,b),99)}}"""

CATEGORIES = ['story', 'visual', 'animation', 'transition', 'mobile', 'desktop', 'source', 'performance']
ITEMS = {
    'story': (['story'], 'Story order in the case: brief → prism instrument → visual studio (specimen → surface + theme → measure → compare) → measured boundaries → seven rules → production record + limits → Next; copy approved at gate 7E, no DRAFT labels'),
    'chapterSpectrum': (['animation', 'mobile', 'desktop'], 'Chapter: the spectrum beam opens with scroll and the light/dark specimen marks appear; scrolling back reverses it; still when scrolling stops (phone swipe + desktop wheel)'),
    'prismEntry': (['transition'], 'Open case file: a ray leaves the prism and opens into a gallery plane (~720 ms), the case arrives and the plane fades (~320 ms); same Canvas; phone + desktop'),
    'hotspots': (['story', 'visual'], 'Instrument hotspots: Test matrix / Measurement / Fix rules'),
    'comparator': (['story', 'visual', 'mobile', 'desktop'], 'Comparator used by tap only (no precise drag): three recorded specimens × Before / Compare / After; both captures share one viewBox and frame, the reveal is a clip (100% / 50% / 0%), buttons ≥ 44 px'),
    'defectClasses': (['story', 'visual'], 'Crop (BW-C1/C6), contrast (BW-C3), text overflow (BW-C7) readable in the pair, each with its measurement and rule; ratio (BW-C4) stated as 0 findings, no invented pair; overflow of the page = 0'),
    'effectsClear': (['visual'], 'Effects never cover the specimen: flight plane at 0 opacity on the case, seam hidden outside Compare, the pair centre is hit-tested to the pair itself'),
    'boundaries': (['story', 'animation'], 'Measured boundaries by tap: ratio 1.00 → 1.25, brightness 0.30 → 0.35, name length 28 → 32 (last safe / first failing); theme switch changes the illustration only'),
    'rulesLimits': (['story', 'source'], 'Seven class disclosures (C4 = 0, C5 reject the asset), production record 186 → 18 (gallery 182 → 18), 18 missing/empty assets rejected, A8 partial'),
    'interruptions': (['animation', 'transition'], 'Rapid view/specimen taps settle on the last choice; state survives scrolling away and back; edges once at 390×844 (reduced motion, blocked model, slow model, Back during flight, resize)'),
    'returnNext': (['transition'], 'Return: the plane folds back to the prism point it left from; chapter scroll position restored, focus on Open case file; Next reintroduces CrossCheck; Back/Forward and direct URL + refresh'),
    'desktopComposition': (['desktop', 'visual'], 'Desktop 1440×900: contact sheet beside a large comparison (> 45% width), annotation beside the pair, boundary desk and rules in columns'),
    'devChecks': (['mobile', 'desktop'], 'Development checks (verify_brandwall_room.viewport) pass inside the pack at 390×844 and 1440×900; 360/430/768/1920 from Development on the same fingerprint'),
    'sources': (['source'], 'Numbers on the chapter and case trace to the BrandWall dossier; captures labelled recorded/illustration; no live, client-logo or affiliation claim'),
    'performance': (['performance', 'mobile'], 'fps from perf_quick Development (same fingerprint, Q47): every segment ≥ 45 fps, ≤ 10% slow frames'),
    'clean': (['mobile', 'desktop'], 'One persistent Canvas, zero page errors, zero responses ≥ 400, no horizontal overflow in both walkthroughs'),
    'regressions': (['mobile', 'desktop'], 'Runner ledger: studio + cases + mobile (and suites touching shared files) passed on this fingerprint'),
}
CHECKS, META = {}, {}


def check(key, ok, detail, shot, **extra):
    CHECKS[key] = {'pass': bool(ok), 'detail': detail, 'screenshot': shot, **extra}


def flight_summary(trace, direction):
    seen = [f for f in trace if f['o'] > .05 and f['d'] == direction]
    if not seen:
        return {'ok': False, 'frames': 0}
    first, peak = seen[0], max(seen, key=lambda f: f['sx'])
    grow = [f['sx'] for f in seen]
    monotone = all(b >= a - .02 for a, b in zip(grow, grow[1:])) if direction == 'out' else all(b <= a + .02 for a, b in zip(grow, grow[1:]))
    last = seen[-1]
    end = trace[-1]
    return {'ok': monotone and peak['sx'] > .95 and end['o'] < .05, 'frames': len(seen), 'visibleMs': last['t'] - first['t'],
            'first': [first['x'], first['y'], first['sx']], 'peak': [peak['x'], peak['y'], peak['sx'], peak['sy']], 'last': [last['x'], last['y'], last['sx']],
            'monotone': monotone, 'endOpacity': end['o'], 'endPath': end['path']}


async def trace_flight(page, action, wait_url):
    await page.evaluate(FLIGHT)
    await action()
    await page.wait_for_url(wait_url)
    await idle(page)
    await page.wait_for_timeout(1200)  # the plane fades after arrival
    return await page.evaluate('window.__flight')


async def beam_run(page, walk, wide, cdp=None):
    sec = await page.locator('#brandwall').evaluate("e=>({top:e.getBoundingClientRect().top+scrollY,h:e.offsetHeight})")
    h = await page.evaluate('innerHeight')
    span = sec['h'] - h
    await land(page, sec['top'] - h * .6)  # jump past the four earlier chapters; the film starts here
    await page.wait_for_timeout(500)
    walk.mark('start')
    forward, backward = [], []
    for p in (.02, .1, .2, .3, .45, .6, .8):
        await (land(page, sec['top'] + p * span) if not cdp else swipe_until(page, cdp, sec['top'] + p * span, step=200, pause=.35))
        await page.wait_for_timeout(350)
        forward.append(await page.evaluate(BEAM))
        if p == .1:
            await walk.shot(f"{walk.tag}01a-chapter-closed.png")
    await walk.shot(f"{walk.tag}01b-chapter-open.png")
    a = await page.evaluate(BEAM)
    await page.wait_for_timeout(700)
    still = a == await page.evaluate(BEAM)
    for p in (.3, .1):
        await (land(page, sec['top'] + p * span) if not cdp else swipe_until(page, cdp, sec['top'] + p * span, step=200, pause=.35))
        await page.wait_for_timeout(350)
        backward.append(await page.evaluate(BEAM))
    scales = [f['scale'] for f in forward]
    ok = all(b >= a - .01 for a, b in zip(scales, scales[1:])) and scales[-1] > .95 and scales[0] < .5 and backward[-1]['scale'] < scales[-1] and forward[-1]['mark'] > .9 and still
    return {'ok': ok, 'forward': scales, 'marks': [f['mark'] for f in forward], 'back': [b['scale'] for b in backward], 'still': still, 'mode': 'wheel' if wide else 'swipe'}


async def studio_run(page, walk, prefix):
    data = {'pairs': {}}
    await vbr.position(page, '.brand-studio')
    await walk.shot(f'{prefix}04-studio-intro.png')
    for specimen in SPECIMENS:
        await vbr.position(page, '.brand-contact-sheet')
        await page.locator(f'[data-specimen-choice={specimen}]').tap() if prefix == 'm' else await page.locator(f'[data-specimen-choice={specimen}]').click()
        await vbr.position(page, '.brand-comparison' if prefix == 'm' else '.brand-view-controls')  # caption clear of the fixed header
        for mode, clip in MODES:
            button = page.locator(f'[data-brand-view={mode}]')
            await (button.tap() if prefix == 'm' else button.click())
            await page.wait_for_timeout(420)
            state = await page.evaluate(PAIR)
            state['expectedClip'] = clip
            data['pairs'][f'{specimen}-{mode}'] = state
            await walk.shot(f'{prefix}05-{specimen}-{mode}.png')
    await page.locator('.brand-annotation').scroll_into_view_if_needed()
    await walk.shot(f'{prefix}05z-annotation.png')
    return data


async def evidence_run(page, walk, prefix):
    data = {'probes': {}}
    await vbr.position(page, '.brand-boundary-controls')
    for axis, safe, broken in AXES:
        tap = (lambda l: l.tap()) if prefix == 'm' else (lambda l: l.click())
        await tap(page.locator(f'[data-boundary={axis}]'))
        s = await page.locator('.brand-probe-result').inner_text()
        await tap(page.locator('[data-probe=broken]'))
        await page.wait_for_timeout(300)
        b = await page.locator('.brand-probe-result').inner_text()
        await vbr.position(page, '.brand-probe-view') if prefix == 'm' else None
        await walk.shot(f'{prefix}06-{axis}-broken.png')
        await vbr.position(page, '.brand-boundary-controls') if prefix == 'm' else None
        data['probes'][axis] = {'safe': s, 'broken': b, 'ok': safe in s and broken in b}
    await vbr.position(page, '.brand-probe-view')
    theme = page.locator('[data-brand-theme]')
    before = await page.locator('.brand-probe-result').inner_text()
    await (theme.tap() if prefix == 'm' else theme.click())
    await page.wait_for_timeout(300)
    data['theme'] = {'dark': await page.locator('.brand-probe-view').get_attribute('data-dark'),
                     'sameResult': before == await page.locator('.brand-probe-result').inner_text()}
    await walk.shot(f'{prefix}06z-dark-specimen.png')
    await vbr.position(page, '.brand-rules')
    for label in ('BW-C4', 'BW-C5'):
        await page.locator('.brand-rules summary').filter(has_text=label).click()
    data['rulesOpen'] = await page.locator('.brand-rules details[open]').count()
    data['rulesTotal'] = await page.locator('.brand-rules details').count()
    await walk.shot(f'{prefix}07-rules.png')
    await vbr.position(page, '.brand-record')
    await walk.shot(f'{prefix}08-record-limits.png')
    return data


async def interrupt_run(page, prefix):
    await vbr.position(page, '.brand-contact-sheet')
    await page.evaluate("['name','portrait','contrast','name','portrait'].forEach(x=>document.querySelector(`[data-specimen-choice=${x}]`).click())")
    await page.evaluate("['after','before','split','after','split'].forEach(x=>document.querySelector(`[data-brand-view=${x}]`).click())")
    await page.wait_for_timeout(420)
    rapid = await page.evaluate(PAIR)
    await vbr.position(page, '.case-next')
    await page.wait_for_timeout(300)
    await vbr.position(page, '.brand-view-controls')
    kept = await page.evaluate(PAIR)
    return {'rapid': [rapid['specimen'], rapid['view'], rapid['clip']], 'kept': [kept['specimen'], kept['view'], kept['clip']]}


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
        data['chapter'] = await beam_run(page, walk, False, cdp)
        await vbr.position(page, '[data-open-case=brandwall]')
        origin = await page.evaluate('scrollY')
        data['entry'] = flight_summary(await trace_flight(page, lambda: page.locator('[data-open-case=brandwall]').tap(), '**/work/brandwall'), 'out')
        data['focus'] = await page.evaluate('document.activeElement && (document.activeElement.id || document.activeElement.tagName)')
        await walk.shot('m02-case-arrived.png')
        data['story'] = await page.evaluate(STORY)
        walk.mark('cut0')  # hotspots: tested and photographed, left out of the film (Q47 length)
        await vbr.position(page, '#case-instrument')
        data['hotspots'] = []
        for n in range(3):
            await page.locator(f'.hotspot-{n}').tap()
            await page.wait_for_timeout(350)
            data['hotspots'].append(await page.locator('#component-card h3').inner_text())
            await walk.shot(f'm03-hotspot-{n + 1}.png')
        await page.get_by_role('button', name='Close component card').tap()
        walk.mark('cut1')
        data['studio'] = await studio_run(page, walk, 'm')
        data['evidence'] = await evidence_run(page, walk, 'm')
        walk.mark('cut2')
        data['interrupt'] = await interrupt_run(page, 'm')
        walk.mark('cut3')
        await vbr.position(page, '.case-next')
        await walk.shot('m09-next-teaser.png')
        back = page.locator('.case-next .case-back')
        data['return'] = flight_summary(await trace_flight(page, lambda: back.tap(), URL + '/'), 'in')
        data['returnScroll'] = abs(await page.evaluate('scrollY') - origin)
        data['returnFocus'] = await page.locator('[data-open-case=brandwall]').evaluate('e=>e===document.activeElement')
        await walk.shot('m10-back-at-chapter.png')
        walk.mark('end')
        await page.locator('[data-open-case=brandwall]').tap()
        await page.wait_for_url('**/work/brandwall')
        await idle(page)
        await vbr.position(page, '.case-next')
        await page.locator('[data-case-target=crosscheck]').tap()
        await page.wait_for_url('**/work/crosscheck')
        await idle(page)
        await walk.shot('m11-next-crosscheck.png')
        await page.go_back()
        await idle(page)
        data['history'] = {'back': page.url.endswith('/work/brandwall'), 'canvas': await page.evaluate("window.__canvas===document.querySelector('canvas')")}
        await page.go_forward()
        await idle(page)
        data['history']['forward'] = page.url.endswith('/work/crosscheck')
        await page.goto(URL + '/work/brandwall')
        await page.locator('.silent-button').click(timeout=30000)
        await idle(page)
        await vbr.position(page, '.brand-view-controls')
        await page.locator('[data-brand-view=after]').tap()
        await page.reload()
        await page.locator('.silent-button').click(timeout=30000)
        await idle(page)
        data['refresh'] = [await page.locator('.brand-studio').get_attribute('data-specimen'), await page.locator('.brand-studio').get_attribute('data-view')]
        await walk.shot('m12-direct-refresh.png')
    except Exception as error:  # noqa: BLE001 — keep the recording
        traceback.print_exc()
        META.setdefault('errors', {})['mobile'] = repr(error)
    await context.close()
    return await page.video.path(), walk, data


async def desktop_walk(browser):
    W, H = 1440, 900
    context = await browser.new_context(viewport={'width': W, 'height': H}, record_video_dir=str(RAW / 'desktop'), record_video_size={'width': W, 'height': H})
    page = await context.new_page()
    walk = Walk(page, 'd')
    data = {}
    try:
        await enter(page)
        await page.evaluate("window.__canvas=document.querySelector('canvas')")
        walk.mark('start')
        sec = await top_of(page, '#brandwall')
        await wheel_until(page, sec - 300)
        data['chapter'] = await beam_run(page, walk, True)
        await vbr.position(page, '[data-open-case=brandwall]')
        origin = await page.evaluate('scrollY')
        data['entry'] = flight_summary(await trace_flight(page, lambda: page.locator('[data-open-case=brandwall]').click(), '**/work/brandwall'), 'out')
        await walk.shot('d02-case-arrived.png')
        data['studio'] = await studio_run(page, walk, 'd')
        await vbr.position(page, '.brand-studio')
        data['layout'] = await page.evaluate("""()=>{const r=s=>{const b=document.querySelector(s).getBoundingClientRect();return [Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)]};
          return {sheet:r('.brand-contact-sheet'),comparison:r('.brand-comparison'),pair:r('.brand-pair'),annotation:r('.brand-annotation'),controls:r('.brand-boundary-controls'),probe:r('.brand-probe-view'),
          rulesCols:[...document.querySelectorAll('.brand-rules > div')].map(e=>Math.round(e.getBoundingClientRect().x)),record:[...document.querySelectorAll('.brand-record article')].map(e=>Math.round(e.getBoundingClientRect().y))}}""")
        await walk.shot('d04-gallery-wide.png')
        data['evidence'] = await evidence_run(page, walk, 'd')
        data['interrupt'] = await interrupt_run(page, 'd')
        await vbr.position(page, '.case-next')
        await walk.shot('d09-next-teaser.png')
        back = page.locator('.case-next .case-back')
        data['return'] = flight_summary(await trace_flight(page, lambda: back.click(), URL + '/'), 'in')
        data['returnScroll'] = abs(await page.evaluate('scrollY') - origin)
        data['returnFocus'] = await page.locator('[data-open-case=brandwall]').evaluate('e=>e===document.activeElement')
        data['canvas'] = await page.evaluate("window.__canvas===document.querySelector('canvas')")
        await walk.shot('d10-back-at-chapter.png')
        walk.mark('end')
    except Exception as error:  # noqa: BLE001
        traceback.print_exc()
        META.setdefault('errors', {})['desktop'] = repr(error)
    await context.close()
    return await page.video.path(), walk, data


async def dev_checks(browser):
    rows, edges = [], []
    vbr.OUT = OUT / 'dev-checks'
    for w, h in ((390, 844), (1440, 900)):
        try:
            rows.append(await vbr.viewport(browser, w, h))
        except Exception as error:  # noqa: BLE001
            rows.append({'viewport': f'{w}x{h}', 'status': 'failed', 'error': repr(error)})
    try:
        edges = await vbr.edges(browser)
    except Exception as error:  # noqa: BLE001
        edges = [{'edge': 'edges', 'status': 'failed', 'error': repr(error)}]
    return rows, edges


def sources_check(chapter_text, text):
    dossier = DOSSIER.read_text()
    claims = [('300', '300'), ('screenshots per run', '300 screenshots'), ('30 synthetic assets', '30 synthetic'), ('5 surfaces', '5 surfaces'), ('2 themes', '2 themes'),
              ('11 boundaries', '11'), ('186 → 18', '186'), ('182 → 18', '182'), ('1.25', '1.25'), ('0.35', '0.35'), ('0.30', '0.30'), ('28', '28'), ('32', '32'),
              ('3:1', '3:1'), ('2 px', '2 px'), ('1%', '1%'), ('A8 is partial', 'A8'), ('0 BW-C4 findings', 'C4')]
    full = chapter_text + '\n' + text
    rows = [{'claim': c, 'onPage': c in full, 'needle': n, 'found': n in dossier} for c, n in claims]
    labels = {s: s in full for s in ('ILLUSTRATION / NOT A CAPTURE', 'These are archived screenshots, not a live test.', 'synthetic assets')}
    forbidden = [w for w in ('Upwork', 'Amazon', 'guaranteed', 'real-time', 'production-ready', 'client logo', 'bulletproof') if re.search(re.escape(w), full, re.I)]
    live = [m.group(0) for m in re.finditer(r'.{0,30}\blive\b.{0,20}', full, re.I)]
    live_bad = [x for x in live if not re.search(r'not a live|no live|not live', x, re.I)]
    ok = all(r['onPage'] and r['found'] for r in rows) and all(labels.values()) and not forbidden and not live_bad
    return ok, (f"{sum(r['onPage'] and r['found'] for r in rows)}/{len(rows)} claims on page + in dossier "
                f"(missing: {[r['claim'] for r in rows if not (r['onPage'] and r['found'])] or 'none'}); labels {sum(labels.values())}/{len(labels)}; forbidden {forbidden or 'none'}; "
                f"'live' only as negation={not live_bad} {live}"), {'claims': rows, 'labels': labels}


def pair_ok(pairs):
    return all(p['clip'] == p['expectedClip'] and p['views'][0] == p['views'][1] and p['images'][0] == p['images'][1] and all(p['unobstructed'])
               and p['flightOpacity'] == 0 and (p['seamOpacity'] > .9 if p['view'] == 'split' else p['seamOpacity'] < .05) and p['overflow'] <= 1
               and all(w >= 44 and h >= 44 for w, h in p['targets']) and p['pressed'] == [p['view']] for p in pairs.values())


def verdicts(m, d, rows, edges, sources):
    mt = m.get('story', {})
    order = [o for o in mt.get('order', []) if o is not None]
    check('story', order == sorted(order) and len(order) == 7 and mt.get('draft') == 0 and mt.get('steps') == ['Specimen', 'Surface + theme', 'Measure', 'Compare'],
          f"sections in order={order == sorted(order)} ({len(order)}/7); steps {mt.get('steps')}; DRAFT labels on case {mt.get('draft')} (copy approved at gate 7E)", 'i01-story.png')
    mc, dc = m.get('chapter', {}), d.get('chapter', {})
    check('chapterSpectrum', mc.get('ok') and dc.get('ok'),
          f"phone swipe beam scaleX {mc.get('forward')} → back {mc.get('back')}, specimen marks {mc.get('marks')}, still={mc.get('still')} | desktop wheel {dc.get('forward')} → back {dc.get('back')}, still={dc.get('still')}", 'i02-chapter.png')
    me, de = m.get('entry', {}), d.get('entry', {})
    check('prismEntry', me.get('ok') and de.get('ok') and d.get('canvas'),
          f"phone: plane visible {me.get('visibleMs')} ms / {me.get('frames')} frames, ray at {me.get('first')} → gallery {me.get('peak')} (x,y,scaleX,scaleY), growth monotone={me.get('monotone')}, "
          f"cleared to {me.get('endOpacity')}; focus {m.get('focus')} | desktop {de.get('visibleMs')} ms, {de.get('first')} → {de.get('peak')}; same Canvas={d.get('canvas')}", 'i03-prism-entry.png')
    check('hotspots', m.get('hotspots') == ['Test matrix', 'Measurement', 'Fix rules'], f"cards {m.get('hotspots')}", 'i04-hotspots.png')
    mp, dp = m.get('studio', {}).get('pairs', {}), d.get('studio', {}).get('pairs', {})
    check('comparator', len(mp) == 9 and len(dp) == 9 and pair_ok(mp) and pair_ok(dp),
          f"phone tap: 3 specimens × 3 modes, clip {sorted({p['clip'] for p in mp.values()})}, viewBox pairs equal={all(p['views'][0] == p['views'][1] for p in mp.values())}, "
          f"captures same frame={all(p['images'][0] == p['images'][1] for p in mp.values())}, targets min {min((min(w, h) for p in mp.values() for w, h in p['targets']), default=0)} px; "
          f"pair {mp.get('portrait-split', {}).get('pair')} px on phone, {dp.get('portrait-split', {}).get('pair')} px on desktop; no drag used", 'i05-comparator.png')
    scales = {k.split('-')[0]: v['scale'] for k, v in mp.items()}
    dscales = {k.split('-')[0]: v['scale'] for k, v in dp.items()}
    verdict = {k: (mp[f'{k}-before']['verdict'], mp[f'{k}-after']['verdict'], mp[f'{k}-before']['caption']) for k in SPECIMENS if f'{k}-before' in mp}
    classes = all(c in ' '.join(v[2] for v in verdict.values()) for c in ('BW-C1', 'BW-C3', 'BW-C7')) and '0 BW-C4 findings' in mt.get('rules', '')
    check('defectClasses', classes and len(verdict) == 3 and all(v[0] != v[1] for v in verdict.values()),
          f"crop/contrast/overflow captions {[v[2] for v in verdict.values()]}; before→after verdicts differ; capture scale phone {scales} (CSS px per source px), desktop {dscales}; "
          f"C4 stated as 0 findings, no pair invented; smallest text in studio/evidence phone {mt.get('fonts')} px", 'i06-defects.png')
    mi = [p for p in mp.values()] + [p for p in dp.values()]
    check('effectsClear', mi and all(p['flightOpacity'] == 0 and all(p['unobstructed']) for p in mi) and all(p['seamOpacity'] < .05 for p in mi if p['view'] != 'split'),
          f"flight plane opacity on case {sorted({p['flightOpacity'] for p in mi})}; 5 hit-test points inside the pair on all {len(mi)} states={all(all(p['unobstructed']) for p in mi)}; "
          f"seam only in Compare (opacity {sorted({p['seamOpacity'] for p in mi})})", 'i05-comparator.png')
    ev, dev = m.get('evidence', {}), d.get('evidence', {})
    check('boundaries', ev.get('probes') and all(p['ok'] for p in ev['probes'].values()) and dev.get('probes') and all(p['ok'] for p in dev['probes'].values())
          and ev.get('theme', {}).get('dark') == 'true' and ev['theme']['sameResult'],
          f"phone {[(k, p['safe'], p['broken']) for k, p in ev.get('probes', {}).items()]}; theme dark={ev.get('theme')} (recorded boundary unchanged); desktop all ok={dev.get('probes') and all(p['ok'] for p in dev['probes'].values())}", 'i07-boundaries.png')
    rec, rules = mt.get('record', ''), mt.get('rules', '')
    lim = all(s in rec for s in ('186 → 18', '182 → 18', 'Reject, don’t disguise', 'A8 is partial', 'remaining 18 findings')) and '0 BW-C4 findings' in rules
    check('rulesLimits', lim and ev.get('rulesTotal') == 7 and ev.get('rulesOpen') == 2,
          f"7 disclosures={ev.get('rulesTotal')}, C4+C5 opened={ev.get('rulesOpen')}; record 186 → 18 / gallery 182 → 18, 18 missing/empty rejected, A8 partial={lim}", 'i08-rules-limits.png')
    mint, dint = m.get('interrupt', {}), d.get('interrupt', {})
    edge_ok = edges and all(e.get('status') == 'passed' for e in edges)
    check('interruptions', mint.get('rapid') == ['portrait', 'split', 'inset(0px 50% 0px 0px)'] and mint.get('kept') == mint.get('rapid') and dint.get('rapid') == mint.get('rapid') and edge_ok,
          f"5 specimen + 5 view clicks in one frame → {mint.get('rapid')}; after scrolling to Next and back {mint.get('kept')}; desktop {dint.get('rapid')}; edges 390×844 {[(e['edge'], e['status']) for e in edges or []]}", 'i09-interruptions.png')
    mr, dr, h = m.get('return', {}), d.get('return', {}), m.get('history', {})
    dock = lambda r, e: bool(r.get('last') and e.get('first')) and abs(r['last'][0] - e['first'][0]) <= 4 and abs(r['last'][1] - e['first'][1]) <= 4  # noqa: E731
    check('returnNext', mr.get('ok') and dr.get('ok') and dock(mr, me) and dock(dr, de) and m.get('returnScroll', 9) < 3 and d.get('returnScroll', 9) < 3 and m.get('returnFocus') and d.get('returnFocus')
          and 'CrossCheck' in mt.get('teaser', '') and h.get('back') and h.get('forward') and h.get('canvas') and m.get('refresh') == ['portrait', 'before'],
          f"phone plane {mr.get('peak')} folds to {mr.get('last')} = departure {me.get('first')} (dock={dock(mr, me)}) in {mr.get('visibleMs')} ms, scroll ±{m.get('returnScroll')} px, focus={m.get('returnFocus')}; "
          f"desktop {dr.get('last')} vs {de.get('first')} (dock={dock(dr, de)}); Next teaser mentions CrossCheck; Back={h.get('back')} Forward={h.get('forward')} Canvas={h.get('canvas')}; refresh → {m.get('refresh')}", 'i10-return-next.png')
    lay = d.get('layout', {})
    comp = bool(lay) and lay['sheet'][0] + lay['sheet'][2] <= lay['comparison'][0] and lay['comparison'][2] > 1440 * .45 and lay['controls'][0] + lay['controls'][2] <= lay['probe'][0] and len(set(lay['rulesCols'])) == 2
    check('desktopComposition', comp, f"contact sheet {lay.get('sheet')} left of comparison {lay.get('comparison')}; pair {lay.get('pair')}; annotation {lay.get('annotation')}; boundary controls {lay.get('controls')} beside probe {lay.get('probe')}; rules columns x {lay.get('rulesCols')}; record rows y {lay.get('record')}", 'i11-desktop.png')
    check('devChecks', len(rows) == 2 and all(r.get('status') == 'passed' for r in rows), f"{[(r['viewport'], r['status'], r.get('error', '')[:120]) for r in rows]}", 'i12-dev-checks.png')
    if sources:
        check('sources', sources[0], sources[1], 'i08-rules-limits.png', data=sources[2])


def fps_verdict():
    report = json.loads((ROOT / 'assets/renders/perf-quick/brandwall.json').read_text())
    same = report.get('fingerprint') == rr.fingerprint()[0]
    segs = report['current']['segments']
    low = {k: v for k, v in segs.items() if v['fps'] < 45 or v['slowPct'] > 10}
    check('performance', same and report['status'] == 'passed' and not low,
          f"perf_quick Development {report['finishedAt'][:10]} on fingerprint {report.get('fingerprint')} (current same={same}), {report['current']['renderer']}: "
          + '; '.join(f"{k} {v['fps']} fps ({v['slowPct']}% slow)" for k, v in segs.items()), None)
    return segs


def ledger_verdict():
    fp = rr.fingerprint()[0]
    ledger = json.loads((ROOT / 'assets/renders/regression-ledger.json').read_text())
    suites = ledger.get('suites', ledger)
    need = ['studio', 'cases', 'mobile', 'case', 'room', 'dispatch', 'monitor', 'time', 'showpiece', 'desktop-b', 'perf-brandwall']
    status = {k: (suites.get(k, {}).get('status'), suites.get(k, {}).get('fingerprint') == fp) for k in need}
    check('regressions', all(s == 'passed' and same for s, same in status.values()), f"fingerprint {fp}: {status}", None)


def strip(names, path, size):
    present = [(n, label) for n, label in names if (OUT / n).exists()]
    if present:
        sheet = Image.new('RGB', (size[0] * len(present), size[1]), 'black')
        for i, (name, label) in enumerate(present):
            sheet.paste(tile(OUT / name, label, size), (i * size[0], 0))
        sheet.save(path)


def sheets():
    P, D = (390, 844), (720, 450)
    strip([('m02-case-arrived.png', 'Brief'), ('m04-studio-intro.png', 'Specimen → compare'), ('m07-rules.png', 'Seven rules'), ('m08-record-limits.png', 'Record + limits')], OUT / 'i01-story.png', P)
    strip([('m01a-chapter-closed.png', 'Beam closed'), ('m01b-chapter-open.png', 'Beam open'), ('d01a-chapter-closed.png', 'Desktop closed'), ('d01b-chapter-open.png', 'Desktop open')], OUT / 'i02-chapter.png', P)
    strip([('m01b-chapter-open.png', 'Tap Open case file'), ('m02-case-arrived.png', 'Gallery arrived')], OUT / 'i03-prism-entry.png', P)
    strip([(f'm03-hotspot-{n}.png', t) for n, t in ((1, 'Test matrix'), (2, 'Measurement'), (3, 'Fix rules'))], OUT / 'i04-hotspots.png', P)
    strip([(f'm05-portrait-{m}.png', f'Crop · {m}') for m in ('before', 'split', 'after')], OUT / 'i05-comparator.png', P)
    strip([('m05-portrait-before.png', 'Crop before'), ('m05-portrait-after.png', 'Crop after'), ('m05-contrast-before.png', 'Contrast before'), ('m05-contrast-after.png', 'Contrast after'),
           ('m05-name-before.png', 'Overflow before'), ('m05-name-after.png', 'Overflow after')], OUT / 'i06-defects.png', P)
    strip([('m06-ratio-broken.png', 'Ratio 1.25'), ('m06-light-broken.png', 'Brightness 0.35'), ('m06-length-broken.png', 'Length 32'), ('m06z-dark-specimen.png', 'Dark specimen')], OUT / 'i07-boundaries.png', P)
    strip([('m07-rules.png', 'C4 = 0 · C5 reject'), ('m08-record-limits.png', '186 → 18 · A8 partial')], OUT / 'i08-rules-limits.png', P)
    strip([('dev-checks/reduced.png', 'Reduced motion'), ('dev-checks/fallback.png', 'Model blocked'), ('dev-checks/slow-model.png', 'Slow model'), ('dev-checks/interrupt-resize.png', 'Back mid-flight + resize')], OUT / 'i09-interruptions.png', P)
    strip([('m09-next-teaser.png', 'Next → CrossCheck'), ('m10-back-at-chapter.png', 'Return at prism'), ('m11-next-crosscheck.png', 'CrossCheck'), ('m12-direct-refresh.png', 'Direct + refresh')], OUT / 'i10-return-next.png', P)
    strip([('d04-gallery-wide.png', 'Gallery + comparison'), ('d05-name-split.png', 'Overflow compare'), ('d06-light-broken.png', 'Boundary desk'), ('d07-rules.png', 'Rules')], OUT / 'i11-desktop.png', D)
    strip([('dev-checks/chapter-390x844.png', '390 dev'), ('dev-checks/portrait-split-390x844.png', '390 compare'), ('dev-checks/chapter-1440x900.png', '1440 dev')], OUT / 'i12-dev-checks.png', P)
    labeled = [('m01b-chapter-open.png', 'Chapter spectrum'), ('m02-case-arrived.png', 'Prism → gallery'), ('m03-hotspot-2.png', 'Measurement'), ('m04-studio-intro.png', 'Visual studio'),
               ('m05-portrait-before.png', 'Crop before'), ('m05-portrait-split.png', 'Compare'), ('m05-portrait-after.png', 'Crop after'), ('m05-contrast-before.png', 'Contrast before'),
               ('m05-contrast-after.png', 'Contrast after'), ('m05-name-before.png', 'Overflow before'), ('m05-name-after.png', 'Overflow after'), ('m06-ratio-broken.png', 'Ratio boundary'),
               ('m06z-dark-specimen.png', 'Dark specimen'), ('m07-rules.png', 'Seven rules'), ('m08-record-limits.png', 'Limits'), ('m10-back-at-chapter.png', 'Return'),
               ('d04-gallery-wide.png', 'Desktop gallery'), ('d05-contrast-split.png', 'Desktop compare'), ('d06-ratio-broken.png', 'Desktop boundary'), ('d10-back-at-chapter.png', 'Desktop return')]
    present = [(n, lab) for n, lab in labeled if (OUT / n).exists()]
    cols, T = 7, (390, 844)
    rows = (len(present) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * T[0], rows * T[1]), 'black')
    for i, (name, label) in enumerate(present):
        size = T if name.startswith('m') else (390, 244)
        sheet.paste(tile(OUT / name, f'{i + 1:02d} {label}', size), ((i % cols) * T[0], (i // cols) * T[1] + (0 if size == T else 300)))
    sheet.save(OUT / 'contact-sheet.jpg', quality=82)


async def run():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        mobile = await mobile_walk(browser)
        desktop = await desktop_walk(browser)
        rows, edges = await dev_checks(browser)
        await browser.close()
    m, d = mobile[2], desktop[2]
    errors = mobile[1].sink['errors'] + desktop[1].sink['errors']
    bad = mobile[1].sink['bad'] + desktop[1].sink['bad']
    overflow = mobile[1].overflows + desktop[1].overflows
    canvas = m.get('history', {}).get('canvas') and d.get('canvas')
    check('clean', canvas and not errors and not bad and max(overflow, default=0) <= 1, f"one Canvas={canvas}; errors {errors}; ≥400 {bad}; max overflow {max(overflow, default=0)} px over {len(overflow)} shots", None)
    sources = None
    try:
        # Chapter copy + every state of the studio data (probe values/measures render one at a time).
        chapter = (ROOT / 'web/lib/instruments.ts').read_text() + (ROOT / 'web/lib/brandwall-room.ts').read_text()
        sources = sources_check(chapter, m.get('story', {}).get('text', ''))
    except Exception as error:  # noqa: BLE001
        META.setdefault('errors', {})['sources'] = repr(error)
    try:
        verdicts(m, d, rows, edges, sources)
    except Exception as error:  # noqa: BLE001 — a verdict bug must not lose the recordings
        traceback.print_exc()
        META.setdefault('errors', {})['verdicts'] = repr(error)
    fps = fps_verdict()
    ledger_verdict()
    for (raw, walk), name in (((mobile[0], mobile[1]), 'walkthrough-mobile.mp4'), ((desktop[0], desktop[1]), 'walkthrough-desktop.mp4')):
        cut = RAW / f'cut-{name}.webm'
        start, end = walk.marks.get('start', 0), walk.marks.get('end')
        keep = [(max(0, start - .3), end + .5)]
        marks = walk.marks
        for a, b in (('cut0', 'cut1'), ('cut2', 'cut3')):
            if a in marks and b in marks:
                lo, hi = keep.pop()
                keep += [(lo, marks[a] + .2), (marks[b] - .2, hi)]
        META.setdefault('filmed', {})[name] = [[round(x, 1) for x in k] for k in keep]
        expr = '+'.join(f'between(t,{a},{b})' for a, b in keep)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(raw), '-vf', f"select='{expr}',setpts=N/FRAME_RATE/TB", '-an', str(cut)], check=True)
        encode(cut, OUT / name)
    videos = [duration(OUT / 'walkthrough-mobile.mp4'), duration(OUT / 'walkthrough-desktop.mp4')]
    shutil.rmtree(RAW, ignore_errors=True)
    sheets()
    categories = {c: {'pass': all(CHECKS.get(k, {}).get('pass') for k, (cats, _) in ITEMS.items() if c in cats),
                      'items': [k for k, (cats, _) in ITEMS.items() if c in cats]} for c in CATEGORIES}
    passed = all(CHECKS.get(k, {}).get('pass') for k in ITEMS)
    report = {
        'status': 'passed' if passed else 'failed',
        'phase': 'Phase 7E — BrandWall: visual studio',
        'stage': 'Testing (light rule Q47)',
        'finishedAt': datetime.now(timezone.utc).isoformat(),
        'fingerprint': rr.fingerprint()[0],
        'url': URL,
        'scope': 'New 7E features only. Chromium GPU (ANGLE) emulation on the local production preview: 390×844 DPR 2 touch, 1440×900 mouse wheel; '
                 'edges once at 390×844; fps from the Development perf_quick report on the same fingerprint. Physical phone = Phase 8.',
        'categories': categories,
        'items': {k: {'label': label, 'categories': cats, **CHECKS.get(k, {'pass': False, 'detail': 'not executed'})} for k, (cats, label) in ITEMS.items()},
        'measurements': {'fps4x': fps, 'devChecks': rows, 'edges': edges, 'mobile': {k: v for k, v in m.items() if k != 'story'}, 'desktop': d,
                         'story': {k: v for k, v in m.get('story', {}).items() if k != 'text'}, 'marks': {'mobile': mobile[1].marks, 'desktop': desktop[1].marks}},
        'videos': videos,
        'filmed': {'segments': META.get('filmed'), 'note': 'Recording seconds kept in each film. Hotspots and rapid-tap interruptions are tested and photographed but cut from the phone film to stay near the Q47 length; gate loading and the history/refresh tail likewise.'},
        'contactSheets': ['contact-sheet.jpg'],
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
