"""Development checks: entrance regression + Phase 3 homepage, mobile first.
This is focused developer verification, not the separate Testing-stage gate pack.
"""
import asyncio
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/full-observatory/dev'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767')
SLUGS = ['crosscheck', 'surgeline', 'driftwatch', 'duewatch', 'brandwall']
NAMES = ['CrossCheck', 'SurgeLine', 'DriftWatch', 'DueWatch', 'BrandWall']
READINGS = ['1,080', '50,000', '11/11', '200', '300']
CONTACTS = ['mailto:rayinailham9@gmail.com', 'https://www.linkedin.com/in/rayinailham/',
            'https://github.com/rayinailham', 'https://www.upwork.com/freelancers/~0107019e8124d357e2']
REPORT = {'status': 'running', 'startedAt': datetime.now(timezone.utc).isoformat(), 'url': URL,
          'scope': 'Phase 3 Development; Chromium mobile emulation, no physical-device performance claim', 'results': []}

def save():
    (OUT / 'verification.json').write_text(json.dumps(REPORT, indent=2) + '\n')

async def position(page, slug, extra=0):
    target = await page.locator('#'+slug).evaluate('(e)=>e.getBoundingClientRect().top+scrollY') + extra
    await page.evaluate('(y)=>window.scrollTo(0,y)', target)
    await page.wait_for_function('(y)=>Math.abs(scrollY-y)<2', arg=target)
    await page.wait_for_timeout(450)

async def pixel_image(page, clip):
    return Image.open(io.BytesIO(await page.screenshot(clip=clip))).convert('RGB')

def difference(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean)

async def menu_to(page, name, target):
    await page.get_by_role('button', name='Menu', exact=False).click()
    await page.locator('#navigation').get_by_role('button', name=name, exact=False).click()
    await page.wait_for_function('id=>Math.abs(document.querySelector(id).getBoundingClientRect().top)<2', arg=target, timeout=8000)
    await page.wait_for_timeout(300)

async def enter(page, silent=True):
    await page.goto(URL, wait_until='networkidle')
    await page.wait_for_function("!document.querySelector('.enter-button').disabled", timeout=30000)
    await page.get_by_role('button', name='Enter without sound' if silent else 'Enter the Observatory', exact=True).click()
    await page.wait_for_selector('.entry-gate[hidden]', state='attached')
    await page.wait_for_timeout(900)

async def verify_fallback(browser):
    results = []
    for width, height in [(390, 844), (360, 740), (430, 932)]:
        context = await browser.new_context(viewport={'width':width,'height':height}, is_mobile=True, has_touch=True)
        page = await context.new_page()
        await page.route('**/models/ambient.glb', lambda route: route.abort())
        await enter(page)
        # Instruments load behind the hero, so a blocked model can fail after Enter.
        await page.wait_for_selector('.observatory[data-scene="fallback"]', state='attached', timeout=30000)
        for slug in SLUGS:
            await position(page, slug, 2)
            fallback = page.locator('.'+slug+'-fallback')
            box = await fallback.bounding_box()
            assert box['y'] > 0 and box['y']+box['height'] < height
            assert await page.locator('#'+slug).get_by_role('button', name='Open case file').is_visible()
            notice = await page.locator('.fallback-notice').bounding_box()
            copy = await page.locator('#'+slug+' .instrument-copy').bounding_box()
            assert notice['y']+notice['height'] <= copy['y'], (slug, 'fallback notice overlaps copy', notice, copy)
            await page.screenshot(path=str(OUT/f'fallback-{slug}-{width}x{height}.png'))
        results.append({'viewport':[width,height], 'blockedAmbientModelFallback':SLUGS, 'noticeClearOfCopy':True})
        await context.close()
    (OUT/'fallback-verification.json').write_text(json.dumps({'status':'passed','finishedAt':datetime.now(timezone.utc).isoformat(),'results':results}, indent=2)+'\n')
    REPORT['results'].extend(results)

async def run():
    OUT.mkdir(parents=True, exist_ok=True)
    save()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist'])
        for width, height in [(390, 844), (360, 740), (430, 932)]:
            print(f'Checking {width}x{height}', flush=True)
            context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=1, is_mobile=True, has_touch=True)
            page = await context.new_page()
            errors, bad = [], []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
            page.on('response', lambda r: bad.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
            await page.add_init_script('''window.__audioContexts=[]; const Native=window.AudioContext;
              window.AudioContext=class extends Native {constructor(...args){super(...args);window.__audioContexts.push(this);}};''')
            await page.goto(URL, wait_until='networkidle')
            await page.wait_for_function("!document.querySelector('.enter-button').disabled", timeout=30000)
            assert await page.locator('.observatory').get_attribute('data-scene') == 'ready'
            assert await page.evaluate('window.__audioContexts.length') == 0
            gate_box = await page.locator('.enter-button').bounding_box()
            assert gate_box['y'] + gate_box['height'] <= height
            await page.screenshot(path=str(OUT / f'gate-{width}x{height}.png'))
            await page.get_by_role('button', name='Enter without sound').click()
            await page.wait_for_selector('.entry-gate[hidden]', state='attached')
            await page.wait_for_timeout(1200)
            assert await page.evaluate('window.__audioContexts.length') == 0
            assert await page.locator('canvas').count() == 1
            assert await page.locator('html').get_attribute('lang') == 'en'
            assert await page.evaluate('document.fonts.check("16px Fraunces") && document.fonts.check("16px Inter") && document.fonts.check(\'16px "JetBrains Mono"\')')
            await page.screenshot(path=str(OUT / f'hero-{width}x{height}.png'))
            await page.get_by_role('button', name='Turn sound on', exact=True).click()
            await page.wait_for_function("document.querySelector('.sound-toggle').getAttribute('aria-pressed')==='true'")
            assert await page.evaluate('window.__audioContexts[0].state') == 'running'
            await page.get_by_role('button', name='Turn sound off', exact=True).click()
            await page.wait_for_function("localStorage.getItem('rayin-observatory:sound')==='off'")
            await menu_to(page, 'Work', '#crosscheck')
            assert await page.locator('.hero-contact').is_hidden()
            chapters = []
            for slug, name, reading in zip(SLUGS, NAMES, READINGS):
                await position(page, slug, 2)
                section = page.locator('#'+slug)
                assert await page.locator('.observatory').get_attribute('data-chapter') == slug
                assert abs((await section.locator('.instrument-stage').bounding_box())['y']) < 2
                assert await section.locator('.proof-reading strong').inner_text() == reading
                assert await page.locator('.draft-label').count() == 0
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                cta = section.get_by_role('button', name='Open case file', exact=True)
                box = await cta.bounding_box()
                pitch = await section.locator('.instrument-pitch').bounding_box()
                assert box['height'] >= 44 and box['y'] + box['height'] < height-40
                assert box['y'] > pitch['y'] + pitch['height']
                await page.screenshot(path=str(OUT / f'{slug}-{width}x{height}.png'))
                clip = {'x': width*.08, 'y': height*.34, 'width': width*.84, 'height': height*.39}
                first = await pixel_image(page, clip)
                await page.wait_for_timeout(950)
                idle = await pixel_image(page, clip)
                idle_diff = difference(first, idle)
                assert idle_diff > .1, (slug, 'frozen idle', idle_diff)
                y = await page.evaluate('scrollY')
                await page.mouse.wheel(0, height*.7)
                await page.wait_for_function('(y)=>scrollY>y+100', arg=y)
                await page.wait_for_timeout(1300)
                orbit = await pixel_image(page, clip)
                orbit_diff = difference(idle, orbit)
                assert orbit_diff > 2, (slug, 'frozen orbit', orbit_diff)
                assert abs((await section.locator('.instrument-stage').bounding_box())['y']) < 2
                # Phase 5: every chapter opens its own case route (the preview dialogs are gone).
                await cta.click()
                await page.wait_for_url(URL.rstrip('/') + '/work/' + slug)
                await page.wait_for_function("document.querySelector('.observatory').dataset.flight==='idle'")
                assert await page.locator('#case-heading').inner_text() == name
                await page.locator('.case-brief .case-back').click()
                await page.wait_for_url(URL.rstrip('/') + '/')
                await page.wait_for_function("document.querySelector('.observatory').dataset.flight==='idle'")
                await page.wait_for_timeout(100)
                assert await cta.evaluate('(e)=>e===document.activeElement')
                assert await page.locator('dialog').count() == 1  # only the (closed) navigation menu remains
                chapters.append({'id': slug, 'pinned': True, 'reading': reading, 'idlePixelDifference': idle_diff, 'orbitPixelDifference': orbit_diff, 'caseRoute': True})
                print(f'  {slug} PASS', flush=True)
            # Later chapters -> earlier chapter: camera, sticky pin and active label recover.
            for slug in reversed(SLUGS):
                await position(page, slug, 2)
                assert await page.locator('.observatory').get_attribute('data-chapter') == slug
            await menu_to(page, 'Skills', '#skills')
            await page.locator('.skill-group').first.locator('summary').click()
            await page.wait_for_timeout(300)
            links = await page.locator('[data-skill-project]').evaluate_all('(els)=>els.map(e=>({id:e.dataset.skillProject,href:e.getAttribute("href"),text:e.textContent}))')
            assert links and all(link['id'] in SLUGS and link['href'] == '#'+link['id'] for link in links)
            daily = page.locator('.skill-group', has=page.locator('summary', has_text='Daily work'))
            await daily.locator('summary').click()
            assert await daily.locator('h3').all_inner_texts() == ['Go', 'MySQL / TiDB', 'Redis']
            assert await daily.locator('a').count() == 0 and await daily.locator('h3').first.is_visible()
            assert await page.get_by_text('awaiting confirmation').count() == 0
            await daily.locator('summary').click()
            await page.screenshot(path=str(OUT / f'skills-{width}x{height}.png'))
            # Reproduce browser-native scrolling before Lenis gets its next animation frame.
            await page.locator('.skill-group').first.locator('[data-skill-project=crosscheck]').evaluate('(e)=>{window.scrollBy(0,-120);e.click();}')
            await page.wait_for_function("Math.abs(document.getElementById('crosscheck').getBoundingClientRect().top)<2", timeout=8000)
            # Python proves all five; exercise one real skill link per destination after accordion resize.
            for slug in SLUGS:
                await menu_to(page, 'Skills', '#skills')
                await page.locator('.skill-group').first.locator(f'[data-skill-project={slug}]').click()
                try:
                    await page.wait_for_function('id=>Math.abs(document.getElementById(id).getBoundingClientRect().top)<2', arg=slug, timeout=8000)
                except Exception:
                    REPORT['navigationFailure'] = await page.evaluate('(id)=>({id,y:scrollY,top:document.getElementById(id).getBoundingClientRect().top,focus:document.activeElement.outerHTML,chapter:document.querySelector(".observatory").dataset.chapter,highlight:document.querySelector(".skill-highlight")?.id})', slug)
                    await page.screenshot(path=str(OUT / f'navigation-failure-{width}.png'))
                    raise
                assert 'skill-highlight' in (await page.locator('#'+slug).get_attribute('class'))
                assert await page.locator('.observatory').get_attribute('data-chapter') == slug
            # Scan must actually change clipping as the portrait crosses the viewport.
            portrait_top = await page.locator('.portrait-scan').evaluate('(e)=>e.getBoundingClientRect().top+scrollY')
            await page.evaluate('(y)=>window.scrollTo(0,y)', portrait_top-height*.85)
            await page.wait_for_timeout(400)
            scan_before = await page.locator('.portrait-scan img').evaluate('(e)=>getComputedStyle(e).clipPath')
            await menu_to(page, 'About', '#about')
            scan_after = await page.locator('.portrait-scan img').evaluate('(e)=>getComputedStyle(e).clipPath')
            assert scan_before != scan_after, ('scan did not reveal', scan_before, scan_after)
            await page.wait_for_function("document.querySelector('.portrait-scan img').naturalWidth>0")
            assert await page.get_by_role('heading', name='I’m Rayina Ilham.').is_visible()
            await page.screenshot(path=str(OUT / f'about-{width}x{height}.png'))
            await menu_to(page, 'Contact', '#contact')
            assert await page.locator('.email-cta').get_attribute('href') == 'mailto:rayinailham9@gmail.com'
            contacts = await page.locator('.contact-links a').evaluate_all('(els)=>els.map(e=>({href:e.getAttribute("href"),target:e.target,rel:e.rel,h:e.getBoundingClientRect().height}))')
            assert [c['href'] for c in contacts] == CONTACTS, contacts
            assert all(c['h'] >= 44 for c in contacts)
            assert all(c['target'] == '_blank' and 'noopener' in c['rel'] for c in contacts[1:])
            assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            await page.screenshot(path=str(OUT / f'contact-{width}x{height}.png'))
            await page.evaluate('window.scrollTo(0,document.documentElement.scrollHeight)')
            await page.wait_for_function("document.querySelector('.progress-readout output').textContent==='100%'")
            await page.get_by_role('button', name='Rayin Observatory, return to the dome').click()
            await page.wait_for_function('scrollY<2', timeout=8000)
            if width == 390:
                cdp = await context.new_cdp_session(page)
                await cdp.send('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':[{'x':190,'y':620}]})
                for y in [550,470,390,310,230]:
                    await cdp.send('Input.dispatchTouchEvent', {'type':'touchMove','touchPoints':[{'x':190,'y':y}]})
                await cdp.send('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]})
                await page.wait_for_timeout(900)
                assert await page.evaluate('scrollY') > 100
                await cdp.detach()
            await enter(page, silent=False)
            assert await page.locator('.sound-toggle').get_attribute('aria-pressed') == 'false'
            assert await page.evaluate('window.__audioContexts.length') == 0
            assert await page.locator('canvas').count() == 1
            assert not errors, errors
            assert not bad, bad
            REPORT['results'].append({'viewport':[width,height], 'chapters':chapters, 'skillLinks':len(links), 'skillNavigation':SLUGS, 'aboutPortrait':True, 'scanClipping':[scan_before,scan_after], 'contactLinks':CONTACTS, 'silentEntry':True, 'audioResumed':True, 'muteRemembered':True, 'readout':'100%', 'reverseNavigation':True, 'nativeScrollNavigation':True, 'errors':errors, 'badResponses':bad})
            save()
            await context.close()
        context = await browser.new_context(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True)
        page = await context.new_page()
        await enter(page, silent=False)
        await page.wait_for_function("document.querySelector('.sound-toggle').getAttribute('aria-pressed')==='true'")
        await context.close()
        await verify_fallback(browser)
        await browser.close()
    REPORT.update(status='passed', finishedAt=datetime.now(timezone.utc).isoformat())
    save()
    print('PASS: all focused development checks', flush=True)

if __name__ == '__main__':
    try:
        asyncio.run(run())
    except BaseException as error:
        REPORT.update(status='failed', error=f'{type(error).__name__}: {error}')
        save()
        raise
