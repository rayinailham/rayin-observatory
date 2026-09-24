"""Phase 7B Development (Q49 update in 7F: hand-turned strip, blinds curtain). Reusable viewport()/edges() for the future Testing evidence pack.
Real recorded totals stay separate from the fictional A–F state machine. One GPU at a time.
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from playwright.async_api import async_playwright
from verify_crosscheck_room import enter, idle, land, GPU, URL
import q49

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/personal-surgeline/dev'
SIZES = os.environ.get('OBSERVATORY_PHONES', '390x844,360x740,430x932,768x1024,1440x900,1920x1080')
if '--sizes' in sys.argv:
    SIZES = sys.argv[sys.argv.index('--sizes') + 1]

async def at(page, selector, offset=-100):
    await land(page, await page.locator(selector).evaluate('(e,o)=>e.getBoundingClientRect().top+scrollY+o', offset))

STRIP = """()=>{const o=Number(getComputedStyle(document.querySelector('#surgeline .dispatch-chapter')).getPropertyValue('--instrument-1-orbit'));
  const tick=(s,i,p)=>Number(getComputedStyle(document.querySelector(`.dispatch-strand[data-strand="${s}"] i:nth-child(${i})`),p).opacity);
  const sum=s=>[1,2,3,4,5,6,7,8].reduce((n,i)=>n+tick(s,i,'::before')+tick(s,i,'::after'),0);
  const em=[...document.querySelectorAll('.dispatch-strand em')].map(e=>Number(getComputedStyle(e).opacity));
  return {orbit:o,s0:sum(0),s1:sum(1),s0first:tick(0,1,'::before'),s0last:tick(0,8,'::after'),s1last:tick(1,8,'::after'),s2last:tick(2,8,'::after'),cut:em[0],resumed:em[1]}}"""

async def strip_at(page, orbit):
    # Q49: the chapter is one screen; the visitor turns the array by hand and the strip follows the turn.
    await q49.turn(page, 'surgeline', orbit)
    await page.wait_for_timeout(250)
    reading = await page.evaluate(STRIP)
    assert abs(reading['orbit'] - orbit) < .03, ('orbit target missed', orbit, reading)
    reading.pop('orbit')
    return reading

async def state(page, expected):
    await page.wait_for_selector(f'.dispatch-room[data-stage="{expected}"]')

# Board: each record chip must rest exactly on its slot once a stage settles, with the colour/send count it earned.
POSE = """()=>{const b=document.querySelector('.dispatch-board');
  return Object.fromEntries([...b.querySelectorAll('[data-chip]')].map(c=>{const r=c.getBoundingClientRect();
    return [c.dataset.chip,{x:r.left,y:r.top,state:c.dataset.state,sends:c.dataset.sends,opacity:getComputedStyle(c).opacity}]}))}"""
SLOT = """(slot)=>{const r=document.querySelector(`.dispatch-board [data-slot="${slot}"]`).getBoundingClientRect();return {x:r.left,y:r.top}}"""
QUEUED = {r: (f'queue-{i}', 'queued', '0') for i, r in enumerate('ABCDEF')}
POSES = {
    'ready': QUEUED,
    'sending': {**QUEUED, 'A': ('ok-0', 'confirmed', '1'), 'B': ('lane-2-end', 'sending', '1'), 'C': ('rejected-0', 'rejected', '1')},
    'crashed': {**QUEUED, 'A': ('ok-0', 'confirmed', '1'), 'B': ('lane-2-end', 'stranded', '1'), 'C': ('rejected-0', 'rejected', '1')},
    'complete': {'A': ('ok-0', 'confirmed', '1'), 'D': ('ok-1', 'confirmed', '1'), 'E': ('ok-2', 'confirmed', '1'),
                 'B': ('ok-3', 'confirmed', '2'), 'C': ('rejected-0', 'rejected', '1'), 'F': ('dead-0', 'dead-letter', '5')},
}

async def board_misses(page, pose, only=None):
    now = await page.evaluate(POSE)
    misses = []
    for rec, (slot, st, sends) in pose.items():
        if only and rec not in only:
            continue
        s = await page.evaluate(SLOT, slot)
        c = now[rec]
        if abs(c['x'] - s['x']) > 1.5 or abs(c['y'] - s['y']) > 1.5 or c['state'] != st or c['sends'] != sends or c['opacity'] != '1':
            misses.append((rec, slot, st, sends, c, s))
    return misses

async def settled(page, stage, only=None, timeout=8000):
    for _ in range(timeout // 100):
        if not await board_misses(page, POSES[stage], only):
            return
        await page.wait_for_timeout(100)
    raise AssertionError(('board not settled', stage, await board_misses(page, POSES[stage], only)))

async def exercise(page, tag):
    wide = page.viewport_size['width'] >= 1024
    await at(page, '.dispatch-board', -250 if wide else -100)
    await settled(page, 'ready')
    await page.locator('[data-dispatch-action=start]').click()
    await state(page, 'sending')
    await settled(page, 'sending')
    await page.evaluate('window.__savedA=document.querySelector("[data-record=A]")')
    a = await page.locator('[data-record=A]').inner_text()
    await page.locator('[data-dispatch-action=crash]').click()
    await state(page, 'crashed')
    assert await page.locator('[data-record=B]').get_attribute('data-status') == 'stranded'
    assert await page.locator('.board-lane[data-lane="2"]').get_attribute('data-status') == 'offline'
    await settled(page, 'crashed')
    b = (await page.evaluate(POSE))['B']
    await page.wait_for_timeout(500)
    assert (await page.evaluate(POSE))['B'] == b, 'stranded B moved while its browser was offline'
    await page.screenshot(path=str(OUT / f'crashed-{tag}.png'))
    # During recovery A must never move (not re-sent); B reaches the form a second time; F counts its five attempts.
    await page.evaluate("""()=>{const b=document.querySelector('.dispatch-board');const q=s=>b.querySelector(`[data-chip="${s}"]`);
      const a0=q('A').getBoundingClientRect();window.__recovery={aMoved:0,bSends:new Set(),fSends:new Set(),frames:0};
      const tick=()=>{const r=q('A').getBoundingClientRect();const w=window.__recovery;w.frames++;
        w.aMoved=Math.max(w.aMoved,Math.abs(r.left-a0.left),Math.abs(r.top-a0.top));w.bSends.add(q('B').dataset.sends);w.fSends.add(q('F').dataset.sends);
        if(document.querySelector('.dispatch-room').dataset.stage!=='complete')requestAnimationFrame(tick)};requestAnimationFrame(tick)}""")
    await page.locator('[data-dispatch-action=resume]').click()
    await state(page, 'resuming')
    await page.wait_for_timeout(700)
    await page.screenshot(path=str(OUT / f'resuming-{tag}.png'))
    await state(page, 'complete')
    await settled(page, 'complete')
    recovery = await page.evaluate('({aMoved:__recovery.aMoved,b:[...__recovery.bSends],f:[...__recovery.fSends],frames:__recovery.frames})')
    assert recovery['aMoved'] < .5, recovery
    assert '2' in recovery['b'], recovery
    reduced = await page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
    if not reduced:
        assert {'1', '2', '3', '4', '5'} <= set(recovery['f']), recovery
    assert await page.locator('[data-record=A]').inner_text() == a
    assert await page.evaluate('window.__savedA===document.querySelector("[data-record=A]")')
    assert await page.locator('[data-status=confirmed]').count() == 4
    assert await page.locator('[data-record=C]').get_attribute('data-status') == 'rejected'
    assert await page.locator('[data-record=F]').get_attribute('data-status') == 'dead-letter'
    assert await page.locator('[data-confirmed-count]').inner_text() == '4'
    assert await page.locator('[data-record]').count() == 6
    assert await page.locator('[data-chip]').count() == 6
    assert 'sent 2×, same receipt' in await page.locator('[data-record=B]').inner_text()
    await page.screenshot(path=str(OUT / f'complete-{tag}.png'))
    # Reverse scroll preserves outcomes. Only explicit Replay clears them.
    await at(page, '.dispatch-intro')
    await at(page, '.dispatch-ledger')
    assert await page.locator('[data-status=confirmed]').count() == 4
    await settled(page, 'complete')
    await page.locator('[data-dispatch-action=reset]').click()
    await state(page, 'ready')
    assert await page.locator('[data-status=queued]').count() == 6
    await settled(page, 'ready')
    # Rapid taps: repeated Start is ignored; Cut and Resume straight away still end with one outcome per record.
    await page.evaluate('''()=>{ for(let i=0;i<8;i++) document.querySelector('[data-dispatch-action=start]')?.click(); }''')
    await state(page, 'sending')
    await page.locator('[data-dispatch-action=crash]').click()
    await settled(page, 'crashed', only='AC')
    await page.locator('[data-dispatch-action=resume]').click()
    await state(page, 'complete')
    await settled(page, 'complete')
    assert await page.locator('[data-status=confirmed]').count() == 4

async def viewport(browser, width, height):
    tag = f'{width}x{height}'
    ctx = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=2 if width<431 else 1, is_mobile=width<431, has_touch=width<1024)
    page = await ctx.new_page()
    errors, bad = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda e: errors.append(e.text) if e.type=='error' else None)
    page.on('response', lambda r: bad.append([r.status, r.url]) if r.status>=400 else None)
    await enter(page)
    await page.evaluate('window.__canvas=document.querySelector("canvas")')
    assert await page.locator('.dispatch-chapter').count() == 1
    assert 'DRAFT' not in await page.locator('.dispatch-chapter small').inner_text()
    # Chapter strip is a pure function of the turn: lane 2 freezes while cut (.35–.6), then resumes; turning back reverses it.
    await q49.to_chapter(page, 'surgeline')
    strips = [await strip_at(page, o) for o in (.2, .42, .55, 1, .2)]
    early, cut1, cut2, done, back = strips
    assert early['cut'] == 0 and early['s0last'] == 0 and early['s0first'] > 0, early
    assert cut1['cut'] > .9 and cut2['cut'] > .9 and cut1['resumed'] == 0, (cut1, cut2)
    assert cut1['s1'] == cut2['s1'] and cut2['s0'] > cut1['s0'], ('lane 2 did not freeze while cut', cut1, cut2)
    assert done['s0last'] == 1 and done['s1last'] == 1 and done['s2last'] == 1 and done['cut'] == 0 and done['resumed'] == 1, done
    assert back == early, ('reverse turn did not restore the strip', back, early)
    await strip_at(page, .48)
    await page.screenshot(path=str(OUT / f'chapter-{tag}.png'))
    origin = await page.evaluate('scrollY')
    await q49.watch_curtain(page)
    await page.locator('[data-open-case=surgeline]').click()
    log = await q49.curtain_log(page, '/work/surgeline')
    assert q49.closed_styles(log) == ['blinds'], log
    await idle(page)
    assert await page.locator('.case-page .draft-label').count() == 0
    await at(page, '#case-instrument', 0)
    for i in range(3):
        await page.locator(f'.hotspot-{i}').click()
        box = await page.locator('#component-card').bounding_box()
        assert box['y']>=0 and box['y']+box['height']<=height, box
    await exercise(page, tag)
    await at(page, '.dispatch-evidence')
    await page.screenshot(path=str(OUT / f'evidence-{tag}.png'))
    totals = await page.locator('[data-outcome] > strong').all_text_contents()
    assert totals == ['48,273','844','833'], totals
    assert sum(int(v.replace(',','')) for v in totals)==49950
    body = await page.locator('.dispatch-evidence').inner_text()
    for token in ['50,000','49,950','10,621','21,508','6 million records were never run','not live telemetry']:
        assert token in body, token
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert await page.evaluate('window.__canvas===document.querySelector("canvas")')
    if width>=1024:
        bounds=await page.locator('.dispatch-flow,.dispatch-ledger').evaluate_all('els=>els.map(e=>{let r=e.getBoundingClientRect();return {x:r.x,w:r.width}})')
        assert bounds[1]['x']>bounds[0]['x']+bounds[0]['w']-1, bounds
    await at(page, '.case-next')
    assert 'one day' in await page.locator('.dispatch-next').inner_text()
    await page.locator('.case-next .case-back').click()
    await page.wait_for_url(URL+'/')
    await idle(page)
    assert abs(await page.evaluate('scrollY')-origin)<4
    await page.locator('[data-open-case=surgeline]').click()
    await page.wait_for_url(URL+'/work/surgeline')
    await idle(page)
    await at(page, '.case-next')
    await q49.watch_curtain(page)
    await page.locator('[data-case-target=driftwatch]').click()
    log = await q49.curtain_log(page, '/work/driftwatch')
    # Hand-over to DriftWatch: SurgeLine's blinds drop, DriftWatch's chart paper rolls up.
    assert q49.closed_styles(log) == ['blinds'] and ['moving', 'roller', '/work/driftwatch'] in log, log
    await idle(page)
    await page.go_back()
    await idle(page)
    assert page.url.endswith('/work/surgeline')
    await page.go_forward()
    await idle(page)
    assert page.url.endswith('/work/driftwatch')
    await page.goto(URL+'/work/surgeline')
    await page.locator('.silent-button').click(timeout=30000)
    await idle(page)
    await state(page,'ready')
    assert not errors and not bad, (errors,bad)
    await ctx.close()
    return {'viewport':tag,'status':'passed','checks':['chapter','chapter strip orbit/cut/reverse','hotspots','crash/resume','board poses','A never re-sent','B sent twice one receipt','F five attempts','stable receipts','failure reasons','replay','reverse scroll','rapid taps','recorded totals','return origin','Next','Back/Forward','direct reload','overflow','single canvas','clean'], 'errors':errors}

async def edges(browser):
    results={}
    ctx=await browser.new_context(viewport={'width':390,'height':844})
    page=await ctx.new_page()
    await enter(page)
    await at(page,'#surgeline',220)
    await page.locator('[data-open-case=surgeline]').click()
    await page.wait_for_url(URL+'/work/surgeline')
    await page.go_back()
    await idle(page)
    assert page.url.endswith('/')
    await page.wait_for_function("document.querySelector('.curtain').dataset.state==='open'", timeout=4000)
    results['interrupt']='passed'
    # Resize in the middle of recovery: the demonstration settles on its outcome at the new layout, nothing duplicated.
    await page.goto(URL+'/work/surgeline')
    await page.locator('.silent-button').click(timeout=30000)
    await idle(page)
    await at(page,'.dispatch-board',-100)
    for action in ['start','crash','resume']:
        await page.locator(f'[data-dispatch-action={action}]').click()
    await page.wait_for_timeout(800)
    await page.set_viewport_size({'width':1440,'height':900})
    await state(page,'complete')
    await settled(page,'complete')
    await page.set_viewport_size({'width':390,'height':844})
    await settled(page,'complete')
    assert await page.locator('[data-chip]').count()==6 and await page.locator('[data-status=confirmed]').count()==4
    results['resize']='passed'
    await ctx.close()
    for mode in ['fallback','reduced']:
        ctx=await browser.new_context(viewport={'width':390,'height':844}, reduced_motion='reduce' if mode=='reduced' else 'no-preference')
        page=await ctx.new_page()
        if mode=='fallback': await page.route('**/models/ambient.glb', lambda r:r.abort())
        await enter(page,'/work/surgeline')
        if mode=='fallback':
            await page.wait_for_selector('.observatory[data-scene=fallback]')
            await at(page,'#case-instrument',0)
            assert await page.locator('.case-inspection').get_attribute('data-leaders') is None
        await exercise(page,mode)
        await page.set_viewport_size({'width':1440,'height':900})
        await page.set_viewport_size({'width':390,'height':844})
        await state(page,'complete')
        await settled(page,'complete')
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        results[mode]='passed'
        await ctx.close()
    return results

async def run():
    OUT.mkdir(parents=True,exist_ok=True)
    report={'status':'running','scope':'7B Development, Chromium emulation','date':datetime.now(timezone.utc).isoformat(),'results':[]}
    def save(): (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        async with async_playwright() as p:
            browser=await p.chromium.launch(args=GPU)
            for size in SIZES.split(','):
                w,h=map(int,size.split('x'))
                report['results'].append(await viewport(browser,w,h)); save(); print('PASS',size,flush=True)
            if '--no-edges' not in sys.argv: report['edges']=await edges(browser)
            await browser.close()
        report['status']='passed'
    except Exception as e:
        report.update(status='failed',error=str(e)); raise
    finally: save()

if __name__=='__main__': asyncio.run(run())
