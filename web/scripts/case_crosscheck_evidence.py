"""Phase 4 Testing evidence (CrossCheck case file): one PNG per checklist item, 390x844 MP4 of the
main flow (flight in, hotspots, readings, tools, video, return, history, next), labeled contact
sheet, 360x740 / 430x932 viewport sheet and evidence.json with pass/fail per item.

Default target is the local production preview; set OBSERVATORY_URL for a public tunnel.
Chromium mobile emulation only: no physical-device fps claim.
"""
import asyncio
import io
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_case import enter, idle  # noqa: E402  shared entry/flight helpers

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/case-crosscheck/evidence'
DOSSIER = Path(__file__).resolve().parents[2] / 'portfolio/CAPABILITY_CROSSCHECK.md'  # Q41: dossiers in the project root
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767').rstrip('/')
CASE = URL + '/work/crosscheck'
W, H = 390, 844
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']
SECTIONS = ['Brief', 'The instrument', 'How it works', 'Readings', 'Tools used', 'Demo video', 'Next instrument']
CARDS = ['Browser matrix', 'Access checks', 'End-to-end flows']
READINGS = ['1,080', '216', '18', '12']
FORBIDDEN = ['Amazon', 'Rayin Ailham']
ITEMS = {
    'route': 'Route /work/crosscheck follows the PLAN §7 template (7 sections in order), one Canvas',
    'flightIn': 'Open case file: homepage fades, scroll locked, camera flies in to the instrument',
    'hotspots': 'Three lens markers (tap ≥44 px) open the matching component card; leaders end on the lenses',
    'flow': 'How it works: four steps with a flowing signal',
    'readings': 'Readings count up like an instrument display to 1,080 / 216 / 18 / 12/12',
    'tools': 'Tools used: every tool traced to dossier §5 and linked back to homepage Skills',
    'video': 'Demo video: loads only on play, plays, 126.9 s silent English original',
    'next': 'Next instrument leads to the SurgeLine chapter',
    'returnFlight': 'Return: camera flies back, homepage scroll position and focus restored',
    'history': 'Browser Back / Forward move between homepage and case without breaking state',
    'fallback': 'Model blocked: labeled still view, component cards and return still work',
    'viewports': 'Case flow passes at 390×844, 360×740 and 430×932',
    'copy': 'Copy: DRAFT label, English, every number traceable to the CrossCheck dossier, no forbidden terms',
    'clean': 'One persistent Canvas, zero page errors, zero responses ≥400, no horizontal overflow',
}


FINDINGS = {  # tester's visual judgement from the MP4, kept next to the automated result
    'flightIn': 'Visual: homepage text fades and the telescope turns slightly, but it does not visibly zoom in; it then slides '
                'below the fold and the case opens on the Brief without the instrument. PLAN §7 asks for the camera to fly in '
                'and the instrument to become the main object. Owner decision: accept, or send back to Development.',
}


def font(size):
    for path in ['/usr/share/fonts/TTF/DejaVuSans.ttf', '/usr/share/fonts/dejavu/DejaVuSans.ttf']:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def tile(source, label, size=(W, H)):
    image = (Image.open(source) if isinstance(source, Path) else Image.open(io.BytesIO(source))).convert('RGB').resize(size)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, size[0], 34), fill=(11, 16, 32))
    draw.text((10, 7), label, fill=(242, 165, 65), font=font(18))
    return image


def row(tiles, path):
    sheet = Image.new('RGB', (W * len(tiles), H), 'black')
    for i, image in enumerate(tiles):
        sheet.paste(image, (i * W, 0))
    sheet.save(path)


def difference(a, b):
    first, second = (Image.open(io.BytesIO(x)).convert('RGB') for x in (a, b))
    return round(sum(ImageStat.Stat(ImageChops.difference(first, second)).mean), 2)


async def settle(page):
    last = None
    for _ in range(60):
        await page.wait_for_timeout(200)
        current = await page.evaluate('Math.round(scrollY)')
        if current == last:
            return
        last = current


async def glide(page, target):
    """Real wheel input (Lenis smoothing visible on video), then an exact final position."""
    # Clamp to the reachable range: a target past the page end would keep wheeling forever.
    target = max(0, min(round(target), await page.evaluate('document.documentElement.scrollHeight-innerHeight')))
    for _ in range(400):
        if await page.evaluate('scrollY') >= target - 160:
            break
        await page.mouse.wheel(0, 120)
        await page.wait_for_timeout(60)
    await settle(page)
    await page.evaluate('(y)=>scrollTo(0,y)', target)
    await page.wait_for_timeout(700)


async def top(page, selector):
    return await page.locator(selector).first.evaluate('(e)=>e.getBoundingClientRect().top+scrollY')


async def overflow(page):
    return await page.evaluate('document.documentElement.scrollWidth>innerWidth')


async def flight(page, click, url):
    """Capture start / mid / end frames of a camera flight triggered by `click`."""
    await page.evaluate('window.__flight=[]')
    before = await page.evaluate('scrollY')
    start = await page.screenshot()
    await click()
    await page.wait_for_function("document.querySelector('.observatory').dataset.flight==='moving'")
    await page.mouse.wheel(0, 180)
    await page.wait_for_timeout(120)
    locked = abs(await page.evaluate('scrollY') - before) < 2
    opacity = await page.locator('.page-content').evaluate('(e)=>Number(getComputedStyle(e).opacity)')
    mid = await page.screenshot()
    await page.wait_for_url(url)
    await idle(page)
    end = await page.screenshot()
    states = await page.evaluate('window.__flight')
    return {'start': start, 'mid': mid, 'end': end, 'locked': locked, 'midOpacity': round(opacity, 2), 'states': states}


async def main_flow(browser, checks, dossier):
    context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True, has_touch=True,
                                        record_video_dir=str(OUT / 'raw'), record_video_size={'width': W, 'height': H})
    page = await context.new_page()
    errors, bad, videos = [], [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('response', lambda r: bad.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
    page.on('request', lambda r: videos.append(r.url) if '/videos/' in r.url else None)
    overflows = []
    await enter(page)
    await page.evaluate("""window.__canvas=document.querySelector('canvas');
      new MutationObserver(()=>window.__flight&&window.__flight.push(document.querySelector('.observatory').dataset.flight))
        .observe(document.querySelector('.observatory'),{attributes:true,attributeFilter:['data-flight']})""")
    await glide(page, await top(page, '#crosscheck') + 280)
    home_y = await page.evaluate('scrollY')
    await page.screenshot(path=str(OUT / '01-crosscheck-chapter.png'))

    # Flight in.
    f = await flight(page, lambda: page.locator('[data-open-case=crosscheck]').click(), CASE)
    for key, name in (('start', '02a-flight-start'), ('mid', '02b-flight-mid'), ('end', '02c-flight-end')):
        (OUT / f'{name}.png').write_bytes(f[key])
    row([tile(f['start'], 'Tap Open case file'), tile(f['mid'], 'Flying in · homepage fades'), tile(f['end'], 'Case file arrived')], OUT / '02-flight-in.png')
    moved = difference(f['start'], f['end'])
    focus = await page.evaluate("document.activeElement&&document.activeElement.id")
    same_canvas = await page.evaluate("window.__canvas===document.querySelector('canvas')")
    checks['flightIn'] = {'pass': 'moving' in f['states'] and f['locked'] and f['midOpacity'] < 1 and moved > 3 and same_canvas and focus == 'case-heading'
                          and await page.evaluate('scrollY') < 2,
                          'detail': f"flight states {f['states']}, scroll locked={f['locked']}, homepage opacity mid-flight {f['midOpacity']}, "
                                    f"frame change start→end {moved}, same Canvas={same_canvas}, focus #{focus}", 'screenshot': '02-flight-in.png'}

    # Route + template.
    await page.screenshot(path=str(OUT / '03-case-brief.png'))
    overflows.append(await overflow(page))
    text = await page.locator('.case-page').text_content()
    positions = [text.find(s) for s in SECTIONS]
    canvases = await page.locator('canvas').count()
    checks['route'] = {'pass': page.url == CASE and all(p >= 0 for p in positions) and positions == sorted(positions) and canvases == 1,
                       'detail': f'url {page.url}; section order {dict(zip(SECTIONS, positions))}; canvases {canvases}', 'screenshot': '03-case-brief.png'}

    # Readings recorder is installed before any reading scrolls into view.
    await page.evaluate("""window.__counts=[];const el=document.querySelector('[data-count]');
      new MutationObserver(()=>window.__counts.push(el.textContent)).observe(el,{childList:true,characterData:true,subtree:true})""")

    # Hotspots.
    await glide(page, await top(page, '#case-instrument'))
    hotspot = []
    for i, title in enumerate(CARDS):
        button = page.locator(f'.hotspot-{i}')
        box = await button.bounding_box()
        await button.click()
        await page.wait_for_function("(i)=>Array.from(document.querySelectorAll('.instrument-hotspot')).every((e,n)=>getComputedStyle(e).backgroundColor===(n===i?'rgb(242, 165, 65)':'rgba(11, 16, 32, 0.93)'))", arg=i)
        await page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
        card = await page.locator('#component-card').bounding_box()
        shown = await page.locator('#component-card h3').inner_text()
        hotspot.append({'title': shown, 'tap': [round(box['width']), round(box['height'])], 'expanded': await button.get_attribute('aria-expanded'),
                        'cardInView': card['y'] + card['height'] <= H and card['y'] >= 0})
        await page.screenshot(path=str(OUT / f'04-hotspot-{i + 1}.png'))
        await page.wait_for_timeout(500)
    leaders = await page.locator('[data-hotspot-line]').evaluate_all("els=>els.map(e=>[Math.round(+e.getAttribute('x2')),Math.round(+e.getAttribute('y2'))])")
    await page.get_by_role('button', name='Close component card').click()
    closed = await page.locator('.instrument-hotspot[aria-expanded=true]').count() == 0
    row([tile(OUT / f'04-hotspot-{i + 1}.png', f'Marker 0{i + 1} · {CARDS[i]}') for i in range(3)], OUT / '05-hotspots.png')
    checks['hotspots'] = {'pass': [h['title'] for h in hotspot] == CARDS and all(min(h['tap']) >= 44 and h['expanded'] == 'true' and h['cardInView'] for h in hotspot)
                          and all(0 < x < W and 100 < y < H for x, y in leaders) and closed,
                          'detail': f'cards {hotspot}; leader endpoints {leaders}; close button collapses={closed}', 'screenshot': '05-hotspots.png'}

    # How it works.
    await glide(page, await top(page, '#flow-heading') - 110)
    steps = await page.locator('.signal-flow li h3').all_inner_texts()
    animation = await page.locator('.signal-flow li').first.evaluate("e=>getComputedStyle(e,'::after').animationName")
    await page.screenshot(path=str(OUT / '06-flow.png'))
    overflows.append(await overflow(page))
    checks['flow'] = {'pass': len(steps) == 4 and animation == 'case-signal', 'detail': f'steps {steps}; signal animation {animation}', 'screenshot': '06-flow.png'}

    # Readings.
    await glide(page, await top(page, '#readings-heading') - 110)
    for i, value in enumerate(READINGS):
        await page.locator('.case-reading').nth(i).scroll_into_view_if_needed()
        await page.wait_for_function('(a)=>document.querySelectorAll("[data-count]")[a.i].textContent===a.v', arg={'i': i, 'v': value})
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#readings-heading') - 110)
    await page.wait_for_timeout(700)
    await page.screenshot(path=str(OUT / '07-readings.png'))
    counts = await page.evaluate('window.__counts')
    between = [c for c in counts if 0 < int(c.replace(',', '')) < 1080]
    shown = await page.locator('.case-reading strong').evaluate_all('els=>els.map(e=>e.textContent)')
    await page.locator('.case-limits summary').click()
    limits = await page.locator('.case-limits').get_attribute('open') is not None
    checks['readings'] = {'pass': shown == ['1,080', '216', '18', '12/12'] and len(between) >= 3 and limits,
                          'detail': f'final {shown}; first display passed through {len(between)} intermediate values (e.g. {between[:4]}); limits disclosure opens={limits}',
                          'screenshot': '07-readings.png'}

    # Tools.
    await glide(page, await top(page, '#tools-heading') - 110)
    await page.screenshot(path=str(OUT / '08-tools.png'))
    tools = await page.locator('.case-tools a').evaluate_all("els=>els.map(e=>[e.textContent.replace('↗','').trim(),e.getAttribute('href')])")
    section5 = dossier.split('## 5.')[1].split('## 6.')[0].lower()
    untraced = [name for name, _ in tools if not all(part.strip().lower() in section5 for part in name.split('/'))]
    checks['tools'] = {'pass': len(tools) == 15 and not untraced and all(href == '/#skills' for _, href in tools),
                       'detail': f'{len(tools)} tools, all href /#skills; not found in dossier §5: {untraced or "none"}', 'screenshot': '08-tools.png'}

    # Demo video.
    await glide(page, await top(page, '#demo-heading') - 110)
    before_play = list(videos)
    await page.locator('.case-video').evaluate('(v)=>v.play()')
    await page.wait_for_function('document.querySelector(".case-video").currentTime>.3', timeout=20000)
    # 0:48 is the coverage heatmap with its burned-in English caption; the native controls
    # hide after a few seconds of untouched playback, so the caption is visible in the capture.
    await page.locator('.case-video').evaluate('(v)=>new Promise(r=>{v.addEventListener("seeked",r,{once:true});v.currentTime=48;})')
    await page.mouse.move(W / 2, 40)
    await page.wait_for_timeout(4000)
    await page.screenshot(path=str(OUT / '09-demo-video.png'))
    video = await page.locator('.case-video').evaluate('(v)=>({d:v.duration,t:v.currentTime,muted:v.muted,w:v.videoWidth,h:v.videoHeight})')
    await page.locator('.case-video').evaluate('(v)=>v.pause()')
    checks['video'] = {'pass': not before_play and bool(videos) and 126 < video['d'] < 128 and video['t'] > 20 and video['muted'] and video['w'] == 1920,
                       'detail': f"requests before play {len(before_play)}, after play {len(set(videos))}; duration {video['d']:.2f} s; "
                                 f"{video['w']}×{video['h']}; muted={video['muted']}; seek to {video['t']:.1f} s", 'screenshot': '09-demo-video.png'}

    # Next section, then Return with the camera flight back.
    await glide(page, await top(page, '#next-heading') - 110)
    await page.screenshot(path=str(OUT / '10-next-section.png'))
    overflows.append(await overflow(page))
    r = await flight(page, lambda: page.locator('.case-next .case-back').click(), URL + '/')
    for key, name in (('start', '11a-return-start'), ('mid', '11b-return-mid'), ('end', '11c-return-end')):
        (OUT / f'{name}.png').write_bytes(r[key])
    row([tile(r['start'], 'Tap Return to CrossCheck'), tile(r['mid'], 'Flying back · case fades'), tile(r['end'], 'Back on the observatory floor')], OUT / '11-return-flight.png')
    await page.screenshot(path=str(OUT / '12-returned-home.png'))
    back_y = await page.evaluate('scrollY')
    focus_cta = await page.locator('[data-open-case=crosscheck]').evaluate('(e)=>e===document.activeElement')
    checks['returnFlight'] = {'pass': 'moving' in r['states'] and r['locked'] and abs(back_y - home_y) < 2 and focus_cta
                              and await page.evaluate("window.__canvas===document.querySelector('canvas')"),
                              'detail': f"flight states {r['states']}, scroll locked={r['locked']}, case opacity mid-flight {r['midOpacity']}; "
                                        f"scrollY {back_y} vs origin {home_y}; focus on Open case file={focus_cta}", 'screenshot': '11-return-flight.png'}

    # Browser history.
    await page.locator('[data-open-case=crosscheck]').click()
    await page.wait_for_url(CASE)
    await idle(page)
    await page.go_back()
    await page.wait_for_url(URL + '/')
    await idle(page)
    history_y = await page.evaluate('scrollY')
    await page.screenshot(path=str(OUT / '13-history-back.png'))
    await page.go_forward()
    await page.wait_for_url(CASE)
    await idle(page)
    forward_heading = await page.locator('#case-heading').is_visible()
    checks['history'] = {'pass': abs(history_y - home_y) < 2 and forward_heading,
                         'detail': f'Back → homepage scrollY {history_y} (origin {home_y}); Forward → case heading visible={forward_heading}', 'screenshot': '13-history-back.png'}

    # Tools link → Skills, then Next → SurgeLine.
    await page.locator('.case-tools a').first.click()
    await page.wait_for_url(URL + '/')
    await idle(page)
    skills_top = await page.locator('#skills').evaluate('(e)=>Math.round(e.getBoundingClientRect().top)')
    await page.screenshot(path=str(OUT / '14-tools-to-skills.png'))
    checks['tools']['pass'] = checks['tools']['pass'] and abs(skills_top) < 2
    checks['tools']['detail'] += f'; tapping a tool lands on Skills (top {skills_top})'
    checks['tools']['screenshots'] = ['08-tools.png', '14-tools-to-skills.png']
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#crosscheck') + 280)
    await page.wait_for_timeout(900)
    await page.locator('[data-open-case=crosscheck]').click()
    await page.wait_for_url(CASE)
    await idle(page)
    await glide(page, await top(page, '#next-heading') - 110)
    await page.locator('.case-next .case-button').click()
    await page.wait_for_url(URL + '/')
    await idle(page)
    await page.wait_for_timeout(1200)
    surge_top = await page.locator('#surgeline').evaluate('(e)=>Math.round(e.getBoundingClientRect().top)')
    chapter = await page.locator('.observatory').get_attribute('data-chapter')
    await page.screenshot(path=str(OUT / '15-next-surgeline.png'))
    checks['next'] = {'pass': abs(surge_top) < 2 and chapter == 'surgeline', 'detail': f'SurgeLine section top {surge_top}; data-chapter {chapter}', 'screenshot': '15-next-surgeline.png'}

    # Copy, read from a fresh direct entry.
    await page.goto(CASE)
    await page.locator('.silent-button').click(timeout=30000)
    await idle(page)
    text = await page.locator('.case-page').text_content()
    draft = await page.locator('.draft-label').inner_text()
    lang = await page.evaluate('document.documentElement.lang')
    traces = {
        '1,080 = 40 × 3 × 3 × 3': '40 pages × 3 browsers × 3 screen sizes × 3' in text and '1,080' in dossier and '40 × 3 × 3 × 3' in dossier,
        '216 = 72 pages × 3 roles': '72 pages × 3 roles' in text and '216** permission checks (72 pages × 3 roles)' in dossier,
        '18 unique issues from 881 signals': '881' in text and '881 raw signals → 18 unique issues' in dossier,
        '12/12 planted bugs': '12/12' in dossier and 'planted' in dossier,
        '126.87 s silent English explainer': '126.87 s' in dossier and '0 audio tracks' in dossier,
    }
    found = [word for word in FORBIDDEN if word.lower() in text.lower()]
    numbers = sorted(set(re.findall(r'\d[\d,/]*', text)))
    checks['copy'] = {'pass': draft == 'DRAFT' and lang == 'en' and all(traces.values()) and not found,
                      'detail': f'label {draft}; lang {lang}; traced {traces}; numbers on page {numbers}; forbidden terms {found or "none"}',
                      'screenshot': '03-case-brief.png'}
    canvases = await page.locator('canvas').count()
    checks['clean'] = {'pass': canvases == 1 and not errors and not bad and not any(overflows),
                       'detail': f'canvas={canvases} (same element across 6 route changes), page errors={errors or 0}, responses ≥400={bad or 0}, horizontal overflow={any(overflows)}',
                       'screenshot': None}
    path = await page.video.path()
    await context.close()
    return path


async def fallback(browser, checks):
    context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await page.route('**/models/ambient.glb', lambda route: route.abort())
    await enter(page, '/work/crosscheck')
    scene = await page.locator('.observatory').get_attribute('data-scene')
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#case-instrument'))
    await page.wait_for_timeout(700)
    still = await page.locator('.case-instrument-still').is_visible()
    notice = await page.locator('.fallback-notice').bounding_box()
    heading = await page.locator('.case-instrument-heading').bounding_box()
    await page.locator('.hotspot-1').click()
    card = await page.locator('#component-card h3').inner_text()
    await page.screenshot(path=str(OUT / '16-fallback.png'))
    await page.locator('.case-brief .case-back').click()
    await page.wait_for_url(URL + '/')
    await idle(page)
    landed = await page.locator('#crosscheck').evaluate('(e)=>Math.round(e.getBoundingClientRect().top)')
    checks['fallback'] = {'pass': scene == 'fallback' and still and notice['y'] + notice['height'] <= heading['y'] and card == 'Access checks' and abs(landed) < 2,
                          'detail': f'data-scene {scene}; still visible={still}; notice clears heading={notice["y"] + notice["height"] <= heading["y"]}; '
                                    f'card {card}; Return without history lands on CrossCheck (top {landed})', 'screenshot': '16-fallback.png'}
    await context.close()


async def viewports(browser, checks):
    (OUT / 'viewports').mkdir()
    results = []
    for width, height in [(360, 740), (430, 932)]:
        context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=2, is_mobile=True, has_touch=True)
        page = await context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        await enter(page)
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#crosscheck') + 280)
        await page.wait_for_timeout(900)
        origin = await page.evaluate('scrollY')
        await page.locator('[data-open-case=crosscheck]').click()
        await page.wait_for_url(CASE)
        await idle(page)
        name = f'{width}x{height}'
        await page.screenshot(path=str(OUT / f'viewports/brief-{name}.png'))
        wide = await overflow(page)
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#case-instrument'))
        await page.wait_for_timeout(700)
        await page.locator('.hotspot-0').click()
        box = await page.locator('#component-card').bounding_box()
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT / f'viewports/hotspot-{name}.png'))
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#readings-heading') - 110)
        for i, value in enumerate(READINGS):
            await page.locator('.case-reading').nth(i).scroll_into_view_if_needed()
            await page.wait_for_function('(a)=>document.querySelectorAll("[data-count]")[a.i].textContent===a.v', arg={'i': i, 'v': value})
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#readings-heading') - 110)
        await page.wait_for_timeout(700)
        await page.screenshot(path=str(OUT / f'viewports/readings-{name}.png'))
        await page.locator('.case-next .case-back').click()
        await page.wait_for_url(URL + '/')
        await idle(page)
        back = await page.evaluate('scrollY')
        ok = not wide and box['y'] + box['height'] <= height and abs(back - origin) < 2 and not errors
        results.append({'viewport': name, 'pass': ok, 'overflow': wide, 'cardBottom': round(box['y'] + box['height']), 'returnScroll': [back, origin], 'errors': errors})
        await context.close()
    for kind, source in (('brief', '03-case-brief.png'), ('hotspot', '04-hotspot-1.png'), ('readings', '07-readings.png')):
        shutil.copy(OUT / source, OUT / f'viewports/{kind}-390x844.png')
    sheet = Image.new('RGB', (3 * W, 3 * H), 'black')
    for c, name in enumerate(['390x844', '360x740', '430x932']):
        for r, kind in enumerate(['brief', 'hotspot', 'readings']):
            sheet.paste(tile(OUT / f'viewports/{kind}-{name}.png', f'{name} · {kind}'), (c * W, r * H))
    sheet.save(OUT / 'viewports/viewports-sheet.jpg', quality=86)
    main_ok = all(checks[k]['pass'] for k in ('route', 'flightIn', 'hotspots', 'readings', 'returnFlight'))
    checks['viewports'] = {'pass': main_ok and all(r['pass'] for r in results),
                           'detail': f'390x844 = main flow above (pass={main_ok}); ' + '; '.join(f"{r['viewport']}: overflow={r['overflow']}, card bottom {r['cardBottom']}, "
                                                                                                 f"return scroll {r['returnScroll']}, errors={len(r['errors'])}" for r in results),
                           'screenshot': 'viewports/viewports-sheet.jpg'}


async def run():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    checks = {}
    dossier = DOSSIER.read_text()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        try:
            video = await main_flow(browser, checks, dossier)
            await fallback(browser, checks)
            await viewports(browser, checks)
        finally:
            await browser.close()
    mp4 = OUT / 'case-crosscheck-walkthrough.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', str(mp4)], check=True)
    shutil.rmtree(OUT / 'raw')
    labeled = [('01-crosscheck-chapter.png', 'Homepage · CrossCheck'), ('02b-flight-mid.png', 'Flying in'), ('03-case-brief.png', 'Case file · Brief'),
               ('04-hotspot-1.png', 'Marker 01 · Browser matrix'), ('04-hotspot-2.png', 'Marker 02 · Access checks'), ('04-hotspot-3.png', 'Marker 03 · Flows'),
               ('06-flow.png', 'How it works'), ('07-readings.png', 'Readings'), ('08-tools.png', 'Tools used'),
               ('09-demo-video.png', 'Demo video'), ('10-next-section.png', 'Next instrument'), ('11b-return-mid.png', 'Flying back'),
               ('12-returned-home.png', 'Returned · scroll restored'), ('13-history-back.png', 'Browser Back'), ('14-tools-to-skills.png', 'Tool → Skills'),
               ('15-next-surgeline.png', 'Next → SurgeLine'), ('16-fallback.png', 'Model blocked · still view')]
    sheet = Image.new('RGB', (6 * W, 3 * H), 'black')
    for i, (name, label) in enumerate(labeled):
        sheet.paste(tile(OUT / name, f'{i + 1:02d} {label}'), ((i % 6) * W, (i // 6) * H))
    sheet.save(OUT / 'contact-sheet.jpg', quality=86)
    report = {'status': 'passed' if all(c['pass'] for c in checks.values()) and len(checks) == len(ITEMS) else 'failed',
              'finishedAt': datetime.now(timezone.utc).isoformat(), 'url': URL, 'viewport': [W, H],
              'scope': 'Chromium mobile emulation (GPU ANGLE, DPR 2); no physical-device fps claim',
              'items': {k: {'label': ITEMS[k], **checks.get(k, {'pass': False, 'detail': 'not reached'}),
                            **({'finding': FINDINGS[k]} if k in FINDINGS else {})} for k in ITEMS},
              'video': mp4.name, 'contactSheet': 'contact-sheet.jpg'}
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    for key, check in report['items'].items():
        print(f"{'PASS' if check['pass'] else 'FAIL'} {key}: {check['detail']}")
    print(report['status'])
    return report['status'] == 'passed'


if __name__ == '__main__':
    sys.exit(0 if asyncio.run(run()) else 1)
