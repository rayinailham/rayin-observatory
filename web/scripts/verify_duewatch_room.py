"""7D Development (Q49 update in 7F: hand-turned chapter, louvre curtain): reusable viewport/edges checks. Evidence paths resolve from the current project root.
Testing can call viewport/edges in its evidence pack (Q42), without repeating a separate suite.
"""
import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright
import q49

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/personal-duewatch/dev'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767').rstrip('/')
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']

async def idle(page):
    await page.wait_for_function("document.querySelector('.observatory')?.dataset.flight==='idle'")
    await page.wait_for_timeout(500)

async def enter(page, path=''):
    await page.goto(URL + path)
    await page.locator('.enter-button').click(timeout=90000)
    await idle(page)
    await page.wait_for_function("document.querySelector('.observatory')?.dataset.scene!=='loading'", timeout=90000)
    await page.wait_for_timeout(800)

async def land(page, selector, offset=-110):
    target = await page.locator(selector).first.evaluate('(e)=>e.getBoundingClientRect().top+scrollY') + offset
    for _ in range(12):
        await page.evaluate('(y)=>scrollTo(0,y)', max(0, target))
        await page.wait_for_timeout(160)
        if abs(await page.evaluate('scrollY') - max(0, min(target, await page.evaluate('document.documentElement.scrollHeight-innerHeight')))) < 3:
            return

async def clean(page):
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'horizontal overflow'
    fallback = await page.locator('.observatory').get_attribute('data-scene') == 'fallback'
    assert await page.locator('canvas').count() == (0 if fallback else 1)

async def shot(page, name, w, h):
    OUT.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(OUT / f'{name}-{w}x{h}.png'))

async def viewport(browser, w, h):
    recording = w in (390,1440)
    OUT.mkdir(parents=True, exist_ok=True)
    video_options = {'record_video_dir':str(OUT/'recordings'),'record_video_size':{'width':w,'height':h}} if recording else {}
    ctx = await browser.new_context(viewport={'width':w,'height':h}, is_mobile=w<768, has_touch=w<1024, device_scale_factor=1, **video_options)
    page = await ctx.new_page()
    errors, bad, external = [], [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda e: errors.append(e.text) if e.type=='error' else None)
    page.on('response', lambda r: bad.append([r.status,r.url]) if r.status>=400 else None)
    page.on('request', lambda r: external.append(r.url) if not r.url.startswith(URL) and r.url.startswith('http') else None)
    await enter(page)
    await page.evaluate("window.__originalCanvas=document.querySelector('canvas')")
    # Q49: one-screen chapter; the business-time pointer follows the visitor's hand turn, not scroll.
    await q49.to_chapter(page, 'duewatch')
    positions=[]
    for progress in (.1,.85,.1):
        await q49.turn(page, 'duewatch', progress)
        positions.append(await page.locator('.time-chapter-track i').evaluate('e=>e.getBoundingClientRect().x'))
    assert positions[1]>positions[0]+40 and abs(positions[2]-positions[0])<5, positions
    track=await page.locator('.time-chapter-track').bounding_box()
    assert all(track['x'] <= x <= track['x']+track['width']-7 for x in positions), (track,positions)
    await clean(page)
    await shot(page,'chapter',w,h)
    origin=await page.evaluate('scrollY')
    await q49.watch_curtain(page)
    await page.locator('[data-open-case=duewatch]').click()
    await page.wait_for_function("document.querySelector('.curtain').dataset.state==='moving'",timeout=3000)
    await page.wait_for_timeout(260)
    await shot(page,'louvre-entry',w,h)
    log=await q49.curtain_log(page,'/work/duewatch')
    assert q49.closed_styles(log)==['louvre'],log
    await idle(page)
    assert await page.locator('.case-page .draft-label').count()==0
    assert await page.evaluate("window.__originalCanvas===document.querySelector('canvas')")
    await shot(page,'brief',w,h)
    await land(page,'#case-instrument',0)
    for i, title in enumerate(('Daily expiry check','Message decisions','Saved reminder record')):
        await page.locator(f'.hotspot-{i}').click()
        assert await page.locator('#component-card h3').inner_text()==title
        await shot(page,f'hotspot-{i}',w,h)
    await land(page,'.time-room')
    assert 'Two separate routines' in await page.locator('.time-intro').inner_text()
    if w<1024:
        assert not await page.locator('#time-triage').is_visible()
    else:
        a=await page.locator('#time-agenda').bounding_box();b=await page.locator('#time-triage').bounding_box()
        assert b['x']>a['x']+a['width'] and abs(a['y']-b['y'])<3,(a,b)
    for days, expected in ((61,'active'),(60,'due'),(8,'due'),(7,'renew'),(0,'renew'),(-1,'expired')):
        await land(page,'.time-date-picker')
        await page.locator(f'[data-days="{days}"]').click()
        assert await page.locator('.time-contract-result').get_attribute('data-category')==expected
        assert await page.locator('.time-agenda-list [data-current=true] b').count()==1
        await clean(page)
    await page.locator('[data-bad-date]').click()
    assert await page.locator('.time-contract-result').get_attribute('data-category')=='bad'
    await land(page,'.time-contract-result');await shot(page,'bad-date',w,h)
    await land(page,'.time-date-picker');await page.locator('[data-days="7"]').click()
    await page.wait_for_timeout(700)
    await land(page,'.time-date-picker');await shot(page,'agenda',w,h)
    await land(page,'.time-module-picker')
    await page.get_by_role('button',name='B / Message triage',exact=True).click()
    assert await page.locator('#time-triage').is_visible()
    for name,route in (('price','reply'),('stock','reply'),('status','reply'),('complaint','human'),('payment','human'),('unknown','human')):
        await land(page,'.time-message-picker')
        await page.locator(f'[data-message={name}]').click()
        assert await page.locator('.time-handoff').get_attribute('data-route')==route
        if route=='human': assert 'No reply draft attached' in await page.locator('.time-handoff').inner_text()
    await land(page,'.time-handoff');await shot(page,'human-handoff',w,h)
    await land(page,'.time-reminder-actions')
    await page.locator('[data-reminder=boundary]').click()
    assert await page.locator('.time-ledger strong').inner_text()=='0'
    await page.locator('[data-reminder=later]').click()
    assert await page.locator('.time-ledger strong').inner_text()=='1'
    for _ in range(6):await page.locator('[data-reminder=replay]').click()
    assert await page.locator('.time-ledger').get_attribute('data-result')=='duplicate'
    assert await page.locator('.time-ledger strong').inner_text()=='1'
    await land(page,'.time-ledger');await shot(page,'replay',w,h)
    await page.locator('[data-reminder=reset]').click()
    await land(page,'.time-reminder-actions');await page.locator('[data-reminder=reply]').click()
    await page.locator('[data-reminder=later]').click()
    assert await page.locator('.time-ledger strong').inner_text()=='0'
    assert await page.locator('.time-ledger').get_attribute('data-result')=='replied'
    # Burst clicks settle immediately and don't change scroll by an animation queue.
    await page.evaluate("() => {for(let i=0;i<12;i++){document.querySelector('[data-message=price]').click();document.querySelector('[data-message=payment]').click();}}")
    assert await page.locator('.time-handoff').get_attribute('data-route')=='human'
    await land(page,'.time-module-picker');await page.get_by_role('button',name='A / Contract agenda',exact=True).click()
    assert await page.locator('.time-contract-result').get_attribute('data-category')=='renew'
    await page.get_by_role('button',name='B / Message triage',exact=True).click()
    assert await page.locator('.time-ledger').get_attribute('data-result')=='replied'
    if w>=1024:await land(page,'.time-desks');await shot(page,'two-desks',w,h)
    targets=await page.locator('.time-room button').evaluate_all("els=>els.filter(e=>e.getClientRects().length).map(e=>({text:e.textContent,w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height}))")
    assert all(t['w']>=44 and t['h']>=44 for t in targets),targets
    await land(page,'.time-evidence');await shot(page,'recorded-proof',w,h)
    assert await page.locator('.time-audit li').count()==7
    for item in await page.locator('.time-audit summary').all():await item.click()
    assert await page.locator('.time-audit details[open]').count()==7
    await land(page,'.time-audit');await shot(page,'audit',w,h)
    assert 'A9/A10' in await page.locator('.time-audit').inner_text()
    assert 'simulated business dates' in await page.locator('.time-dates-note').inner_text()
    assert 'simulated business dates' in await page.locator('#demo-heading + p').inner_text()
    await clean(page)
    await land(page,'.case-next')
    assert 'visual studio' in await page.locator('.time-next').inner_text()
    await page.locator('.case-next .case-back').click()
    await page.wait_for_url(URL+'/');await idle(page)
    assert abs(await page.evaluate('scrollY')-origin)<8
    assert await page.evaluate("document.activeElement?.dataset.openCase==='duewatch'")
    await page.go_back();await idle(page)
    assert await page.locator('.time-room').count()==1
    await page.go_forward();await idle(page)
    await page.locator('[data-open-case=duewatch]').click();await page.wait_for_url('**/work/duewatch');await idle(page)
    await land(page,'.case-next');await q49.watch_curtain(page);await page.locator('[data-case-target=brandwall]').click()
    log=await q49.curtain_log(page,'/work/brandwall');await idle(page)
    # Hand-over to BrandWall: DueWatch's louvre closes, BrandWall's pleats open.
    assert q49.closed_styles(log)==['louvre'] and ['moving','prism','/work/brandwall'] in log,log
    await page.go_back();await idle(page)
    await page.reload();await idle(page)
    assert await page.locator('.time-contract-result').get_attribute('data-category')=='active'
    assert await page.locator('.time-ledger strong').inner_text()=='0'
    await clean(page)
    assert not errors,errors
    assert not bad,bad
    assert not external,external
    video = page.video
    await ctx.close()
    if video:await video.save_as(str(OUT/f'walkthrough-{w}x{h}.webm'))
    return {'viewport':[w,h],'status':'passed','errors':errors,'badRequests':bad,'externalRequests':external,'chapterPositions':positions}

async def edges(browser):
    results=[]
    for mode in ('reduced','fallback','slow'):
        ctx=await browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce' if mode=='reduced' else 'no-preference')
        page=await ctx.new_page()
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        if mode=='fallback':await page.route('**/models/ambient.glb',lambda r:r.abort())
        if mode=='slow':
            async def delay(route):
                await asyncio.sleep(2);await route.continue_()
            await page.route('**/models/ambient.glb',delay)
        await enter(page,'/work/duewatch')
        if mode=='fallback':
            await page.wait_for_function("document.querySelector('.observatory').dataset.scene==='fallback'")
            assert await page.locator('.hotspot-leaders').evaluate("e=>getComputedStyle(e).visibility")=='hidden'
        elif mode=='reduced':assert await page.locator('.curtain').get_attribute('data-state')=='open'
        await land(page,'.time-date-picker');await page.locator('[data-days="0"]').click()
        assert await page.locator('.time-contract-result').get_attribute('data-category')=='renew'
        await page.locator('[data-days="60"]').focus();await page.keyboard.press('Enter')
        assert await page.locator('.time-contract-result').get_attribute('data-category')=='due'
        assert await page.locator('.time-hand').evaluate('e=>e.getAnimations().length')==0
        await shot(page,mode,390,844)
        await page.set_viewport_size({'width':1440,'height':900});await page.wait_for_timeout(800)
        assert await page.locator('#time-triage').is_visible()
        await page.set_viewport_size({'width':360,'height':740});await page.wait_for_timeout(800)
        await clean(page)
        expected_errors = ['Could not load /models/ambient.glb: Failed to fetch'] if mode=='fallback' else []
        unexpected = [e for e in errors if e not in expected_errors]
        assert not unexpected, unexpected
        await ctx.close();results.append({'mode':mode,'status':'passed','expectedModelErrors':errors})
    ctx=await browser.new_context(viewport={'width':390,'height':844})
    page=await ctx.new_page();await enter(page)
    await land(page,'#duewatch',200)
    await page.locator('[data-open-case=duewatch]').click();await page.wait_for_url('**/work/duewatch');await idle(page)
    await land(page,'.case-next');await page.locator('[data-case-target=brandwall]').click()
    await page.wait_for_timeout(150);await page.go_back();await idle(page);await page.wait_for_timeout(1800)
    assert page.url==URL+'/',page.url
    assert await page.locator('.curtain').get_attribute('data-state')=='open'
    await clean(page);await ctx.close();results.append({'mode':'history-interruption','status':'passed'})
    return results

async def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sizes',default=os.environ.get('OBSERVATORY_PHONES','390x844,360x740,430x932,768x1024,1440x900,1920x1080'));parser.add_argument('--no-edges',action='store_true');args=parser.parse_args()
    report={'status':'running','results':[],'finishedAt':None};OUT.mkdir(parents=True,exist_ok=True)
    try:
        async with async_playwright() as p:
            browser=await p.chromium.launch(headless=True,args=GPU)
            for size in args.sizes.split(','):
                w,h=map(int,size.split('x'));print('DueWatch',size,flush=True)
                report['results'].append(await viewport(browser,w,h))
            if not args.no_edges:report['edges']=await edges(browser)
            await browser.close()
        report['status']='passed'
    except Exception as e:
        report['status']='failed';report['error']=str(e);raise
    finally:
        report['finishedAt']=datetime.now(timezone.utc).isoformat()
        (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],flush=True)

if __name__=='__main__':asyncio.run(main())
