"""Read actual R3F groups through React's test-only DevTools hook; no app debug API.

Checks one visible planet, forward/reverse order, wheel continuity, camera anchoring,
idle motion, reduced motion, resize, and case navigation. Records browser-only video.
"""
import asyncio
import json
import math
import os
from pathlib import Path
from playwright.async_api import async_playwright

URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8780')
OUT = Path(__file__).resolve().parents[2] / 'assets/renders/planetary-motion/dev'
NAMES = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
HOOK = '''window.__roots=new Set(); window.__REACT_DEVTOOLS_GLOBAL_HOOK__={supportsFiber:true,renderers:new Map(),inject(r){const id=this.renderers.size+1;this.renderers.set(id,r);return id},onCommitFiberRoot:(id,root)=>window.__roots.add(root),onCommitFiberUnmount:()=>{}};'''
PROBE = '''() => {
 const groups=new Map(); const visit=f=>{if(!f)return;const o=f.stateNode?.object;if(o?.name?.startsWith('JourneyPlanet-'))groups.set(o.name,o);visit(f.child);visit(f.sibling)};
 window.__roots.forEach(r=>visit(r.current));
 if(groups.size!==8)throw new Error(`Expected 8 planet groups, found ${groups.size}`);
 window.planetGroups=[...groups.values()];
 window.planetSample=()=>window.planetGroups.filter(g=>g.visible).map(g=>{
  const {camera,size}=g.__r3f.root.getState();const p=g.position.clone().project(camera);
  let opacity=1;g.traverse(o=>{if(o.material?.uniforms?.uOpacity)opacity=o.material.uniforms.uOpacity.value});
  return {name:g.name.replace('JourneyPlanet-',''),x:(p.x+1)*size.width/2,y:(1-p.y)*size.height/2,opacity};
 });
 return window.planetSample();
}'''

async def at(page, progress):
    await page.evaluate('(p)=>window.scrollTo(0,p*(document.documentElement.scrollHeight-innerHeight))', progress)
    await page.wait_for_timeout(1100)
    return await page.evaluate('window.planetSample()')

async def sample_frames(page, count=90):
    return await page.evaluate('''n=>new Promise(resolve=>{const frames=[];function tick(){frames.push({time:performance.now(),y:scrollY,planets:window.planetSample()});if(frames.length===n)resolve(frames);else requestAnimationFrame(tick)}requestAnimationFrame(tick)})''', count)

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report={'status':'running','checks':[],'errors':[]}
    try:
        async with async_playwright() as p:
            browser=await p.chromium.launch(headless=True,args=['--enable-gpu','--use-gl=angle','--use-angle=gl-egl','--ignore-gpu-blocklist'])
            context=await browser.new_context(viewport={'width':390,'height':844},record_video_dir=str(OUT/'video'),record_video_size={'width':1440,'height':900})
            await context.add_init_script(HOOK)
            page=await context.new_page()
            page.on('pageerror',lambda e:report['errors'].append(str(e)))
            page.on('console',lambda e:report['errors'].append(e.text) if e.type=='error' else None)
            await page.goto(URL)
            await page.locator('.silent-button').click(timeout=30000)
            await page.wait_for_selector('.entry-gate[hidden]',state='attached')
            await page.wait_for_timeout(1000)
            await page.evaluate(PROBE)
            for width,height in [(390,844),(1440,900)]:
                await page.set_viewport_size({'width':width,'height':height})
                await page.wait_for_timeout(700)
                for direction,indices in [('forward',range(8)),('reverse',range(7,-1,-1))]:
                    order=[]
                    for i in indices:
                        shown=await at(page,i/7)
                        assert len(shown)==1 and shown[0]['name']==NAMES[i], (width,direction,i,shown)
                        assert shown[0]['opacity']>.99, shown
                        order.append(shown[0]['name'])
                        if direction=='forward':
                            await page.screenshot(path=str(OUT/f'{width}-{i+1}-{NAMES[i].lower()}.png'))
                    report['checks'].append({'viewport':width,'direction':direction,'order':order})
                # Camera sweeps sharply at chapter changes; a parked planet must remain
                # in its margin instead of inheriting the camera's previous-frame pose.
                await at(page,2.32/7)
                for direction in [1,-1,1,-1]:
                    await page.mouse.wheel(0, direction*1500)
                    frames=await sample_frames(page,70)
                    assert all(len(f['planets'])<=1 for f in frames)
                    steps=[]
                    wrong_direction=[]
                    for a,b in zip(frames,frames[1:]):
                        if a['planets'] and b['planets']:
                            x,y=a['planets'][0],b['planets'][0]
                            if x['name']==y['name'] and min(x['opacity'],y['opacity'])>.5:
                                steps.append(math.hypot(x['x']-y['x'],x['y']-y['y']))
                                # Forward passes move upward; reverse retraces downward.
                                # Ignore subpixel idle orbit, but reject scroll-induced jitter.
                                if (y['y']-x['y'])*direction>1:
                                    wrong_direction.append([x,y])
                    assert steps and not wrong_direction, wrong_direction
                    assert abs(frames[-1]['y']-frames[0]['y'])>300, 'wheel did not scroll'
                    report['checks'].append({'viewport':width,'wheel':direction*1500,'maxFrameStepPx':round(max(steps),3),'onePlanet':True,'noScrollReversal':True})
                faded=await at(page,2.43/7)
                assert len(faded)==1 and .05<faded[0]['opacity']<.5, ('shader fade not applied',faded)
                report['checks'].append({'viewport':width,'actualMaterialFade':round(faded[0]['opacity'],3)})
                await at(page,3/7)
                frames=await sample_frames(page,100)
                first,last=frames[0]['planets'][0],frames[-1]['planets'][0]
                movement=math.hypot(first['x']-last['x'],first['y']-last['y'])
                assert movement>.2, ('idle frozen',movement)
                report['checks'].append({'viewport':width,'idleMovementPx':round(movement,3)})
            # Resize without resetting to Mercury or putting a planet over the copy.
            for width,height in [(360,740),(430,932),(1024,768),(1920,1080)]:
                await page.set_viewport_size({'width':width,'height':height})
                await page.wait_for_timeout(700)
                shown=await at(page,5/7)
                assert len(shown)==1 and shown[0]['name']=='Saturn',shown
                assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                await page.screenshot(path=str(OUT/f'resize-{width}.png'))
            report['checks'].append({'resize':[360,430,1024,1920],'pass':True})
            await page.emulate_media(reduced_motion='reduce')
            await page.wait_for_timeout(1500)
            await at(page,2/7)
            frames=await sample_frames(page,50)
            first,last=frames[0]['planets'][0],frames[-1]['planets'][0]
            assert math.hypot(first['x']-last['x'],first['y']-last['y'])<.001
            report['checks'].append({'reducedMotion':'stationary Earth; scroll still selects planets'})
            y=await page.locator('#crosscheck').evaluate('e=>e.offsetTop+100')
            await page.evaluate('y=>window.scrollTo(0,y)',y)
            await page.wait_for_timeout(1000)
            await page.locator('[data-open-case="crosscheck"]').click()
            await page.wait_for_url('**/work/crosscheck')
            await page.wait_for_selector('.observatory[data-flight="idle"]')
            assert await page.evaluate('window.planetSample()')==[]
            await page.go_back()
            await page.wait_for_selector('#crosscheck')
            await page.wait_for_timeout(1200)
            assert len(await at(page,2/7))==1
            assert await page.locator('canvas').count()==1
            report['checks'].append({'caseAndReturn':'planets hidden in case; restored on home; one Canvas'})
            assert not report['errors'],report['errors']
            await context.close()
            await page.video.save_as(str(OUT/'walkthrough.webm'))
            await page.video.delete()
            await browser.close()
            report['status']='passed'
    except Exception:
        report['status']='failed'
        raise
    finally:
        (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))

if __name__=='__main__':
    asyncio.run(main())
