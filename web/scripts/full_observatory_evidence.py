"""Phase 3 Testing evidence: one PNG per checklist item, 390x844 walkthrough MP4, 360/430 layouts,
still-view fallback, dossier number trace, labeled contact sheet and evidence.json.

Default target is the local production preview; set OBSERVATORY_URL for a public tunnel.
Chromium mobile emulation only: no physical-device fps, speaker or carrier-network claim.
"""
import asyncio
import io
import json
import os
import shutil
import struct
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/full-observatory/evidence'
DOSSIERS = Path('/home/rayin/Projects/Testing/portfolio')
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767')
W, H = 390, 844
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']
SLUGS = ['crosscheck', 'surgeline', 'driftwatch', 'duewatch', 'brandwall']
NAMES = dict(zip(SLUGS, ['CrossCheck', 'SurgeLine', 'DriftWatch', 'DueWatch', 'BrandWall']))
# Reading shown on the site + a word that must share a dossier line with it.
READINGS = {'crosscheck': ('1,080', 'combinations'), 'surgeline': ('50,000', 'records'),
            'driftwatch': ('11/11', 'planted'), 'duewatch': ('200', 'contracts'), 'brandwall': ('300', 'screenshots')}
NEW_MODELS = ['surgeline', 'driftwatch', 'duewatch', 'brandwall']
NODES = {'surgeline': ['DishPivot0', 'DishPivot3'], 'driftwatch': ['NeedlePivot', 'PaperFeed', 'RollerPivot0', 'RollerPivot1'],
         'duewatch': ['OrbitPivot0', 'OrbitPivot2'], 'brandwall': ['PrismPivot', 'SpectrumPivot']}
CONTACTS = ['mailto:rayinailham9@gmail.com', 'https://www.linkedin.com/in/rayinailham/',
            'https://github.com/rayinailham', 'https://www.upwork.com/freelancers/~0107019e8124d357e2']
# PLAN §9: internal agent skill names never appear; unconfirmed daily-work tools are not published.
FORBIDDEN = ['drift-alarm', 'qa-sweep', 'oracle-target', 'durable-queue-worker', 'bulk-form-runner', 'visual-brand-qa',
             'triage-engine', 'evidence-guard', 'scheduled-ops', 'unattended-run', 'web-recon', 'scraper-forge', 'Amazon', 'Rayin Ailham']
UNCONFIRMED = {'Go', 'MySQL', 'TiDB', 'MySQL/TiDB', 'Redis'}
ITEMS = {
    'assets': 'Blender + .glb: antenna array, seismograph, orrery, prism spectrograph (Draco, size budget)',
    'order': 'Five chapters in PLAN §5 order',
    **{f'chapter-{s}': f'Chapter {NAMES[s]}: pinned, orbit, idle motion, reading, Open case file preview' for s in SLUGS},
    'numbers': 'Every homepage reading traces to its dossier',
    'skills': 'Skills grouped (PLAN §9), every item linked to a proving project, no internal/unconfirmed names',
    'skill-link': 'Choosing a project beside a skill returns to that instrument and highlights it',
    'about': 'About: stylised portrait, scan reveal, first-person DRAFT copy',
    'contact': 'Contact: Email CTA + Email / LinkedIn / GitHub / Upwork links',
    'copy': 'Homepage copy English, identity correct, every section labeled DRAFT',
    'viewports': '360x740 and 430x932: every section fits, no horizontal overflow',
    'fallback': 'Blocked model -> labeled still view, copy not covered',
    'clean': 'One Canvas, no page errors, no responses >= 400',
}


class Evidence:
    def __init__(self):
        self.checks, self.shots, self.n = {}, [], 0

    async def shot(self, page, name, folder=OUT):
        self.n += 1
        path = folder / f'{self.n:02d}-{name}.png'
        await page.screenshot(path=str(path))
        self.shots.append((path, name))
        return str(path.relative_to(OUT))

    def check(self, item, ok, detail, shot=None):
        self.checks[item] = {'pass': bool(ok), 'detail': detail, 'screenshot': shot}
        print(f"  {'PASS' if ok else 'FAIL'} {item}: {detail}", flush=True)

    async def step(self, item, coro):
        # A failed step is recorded, not fatal, so every checklist item gets a verdict.
        try:
            await coro
        except Exception as error:
            self.check(item, False, f'{type(error).__name__}: {str(error).splitlines()[0][:300]}')


async def settle(page):
    last = None
    for _ in range(60):
        await page.wait_for_timeout(200)
        current = await page.evaluate('Math.round(scrollY)')
        if current == last:
            return
        last = current


async def wheel_to(page, target, step=110, pause=70):
    # Real wheel input so the video shows Lenis smoothing; wheel toward a position, not a step count.
    for _ in range(600):
        if await page.evaluate('scrollY') >= target - 2:
            break
        await page.mouse.wheel(0, step)
        await page.wait_for_timeout(pause)
    await settle(page)


async def top_of(page, selector):
    return await page.locator(selector).evaluate('(e)=>e.getBoundingClientRect().top+scrollY')


async def jump(page, y):
    await page.evaluate('(y)=>window.scrollTo(0,y)', y)
    await page.wait_for_function('(y)=>Math.abs(scrollY-y)<2', arg=y)
    await page.wait_for_timeout(500)


async def menu_to(page, name, target):
    await page.get_by_role('button', name='Menu', exact=False).click()
    await page.wait_for_timeout(350)
    await page.locator('#navigation').get_by_role('button', name=name, exact=False).click()
    await page.wait_for_function('id=>Math.abs(document.querySelector(id).getBoundingClientRect().top)<2', arg=target, timeout=8000)
    await page.wait_for_timeout(500)


async def enter(page):
    await page.goto(URL, wait_until='networkidle')
    await page.wait_for_function("!document.querySelector('.enter-button').disabled", timeout=60000)
    await page.get_by_role('button', name='Enter without sound', exact=True).click()
    await page.wait_for_selector('.entry-gate[hidden]', state='attached')
    await page.wait_for_timeout(1500)


def glb_json(data):
    length = struct.unpack_from('<I', data, 12)[0]
    return json.loads(data[20:20 + length])


def check_assets():
    detail, ok = {}, True
    for slug in SLUGS + ['dome', 'ambient']:
        data = urllib.request.urlopen(f'{URL}/models/{slug}.glb', timeout=30).read()
        gltf = glb_json(data)
        names = {node.get('name') for node in gltf.get('nodes', [])}
        draco = 'KHR_draco_mesh_compression' in gltf.get('extensionsRequired', [])
        missing = [n for n in NODES.get(slug, []) if n not in names]
        detail[slug] = {'bytes': len(data), 'draco': draco, 'images': len(gltf.get('images', [])), 'missingNodes': missing}
        ok &= draco and len(data) <= 1_500_000 and not missing
    total = sum(v['bytes'] for v in detail.values())
    return ok and total <= 8_000_000, {'totalBytes': total, 'models': detail}


def check_numbers():
    detail, ok = {}, True
    for slug, (reading, word) in READINGS.items():
        lines = (DOSSIERS / f'CAPABILITY_{slug.upper()}.md').read_text().splitlines()
        hit = next((f'L{i + 1}' for i, line in enumerate(lines) if reading in line and word in line.lower()), None)
        detail[slug] = {'reading': reading, 'dossierLine': hit}
        ok &= hit is not None
    return ok, detail


def renders_sheet():
    # 2x2 of the four Blender review renders behind the new GLBs.
    tiles = [Image.open(ROOT / f'assets/renders/full-observatory/{s}-review.png').convert('RGB').resize((400, 400)) for s in NEW_MODELS]
    sheet = Image.new('RGB', (800, 800), '#0B1020')
    for i, tile in enumerate(tiles):
        sheet.paste(tile, ((i % 2) * 400, (i // 2) * 400))
    path = OUT / '00-instrument-renders.png'
    sheet.save(path)
    return str(path.relative_to(OUT))


async def main_flow(browser, ev):
    context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True,
                                        has_touch=True, record_video_dir=str(OUT / 'raw'), record_video_size={'width': W, 'height': H})
    page = await context.new_page()
    errors, bad = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('response', lambda r: bad.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
    await page.goto(URL, wait_until='networkidle')
    await page.wait_for_function("!document.querySelector('.enter-button').disabled", timeout=60000)
    await ev.shot(page, 'gate')
    await page.get_by_role('button', name='Enter without sound', exact=True).click()
    await page.wait_for_selector('.entry-gate[hidden]', state='attached')
    await page.wait_for_timeout(2000)
    hero = await ev.shot(page, 'hero')

    async def copy():
        text = await page.locator('main').inner_text()
        drafts = await page.locator('main .draft-label').count()
        found = [word for word in FORBIDDEN if word.lower() in text.lower()]
        lang = await page.locator('html').get_attribute('lang')
        ok = lang == 'en' and 'Rayina Ilham' in text and not found and drafts == 9
        ev.check('copy', ok, f'lang={lang}, DRAFT labels={drafts}/9 (hero, 5 chapters, skills, about, contact), forbidden terms={found}', hero)
    await ev.step('copy', copy())

    order = await page.locator('main .instrument-journey').evaluate_all('(els)=>els.map(e=>e.id)')
    for slug in SLUGS:
        async def chapter(slug=slug):
            section = page.locator('#' + slug)
            await wheel_to(page, await top_of(page, '#' + slug) + 2)
            await page.wait_for_timeout(900)
            chapter_id = await page.locator('.observatory').get_attribute('data-chapter')
            pinned = abs((await section.locator('.instrument-stage').bounding_box())['y']) < 2
            reading = await section.locator('.proof-reading strong').inner_text()
            clip = {'x': W * .08, 'y': H * .34, 'width': W * .84, 'height': H * .39}
            first = Image.open(io.BytesIO(await page.screenshot(clip=clip))).convert('RGB')
            start = await ev.shot(page, f'{slug}-start')
            idle = Image.open(io.BytesIO(await page.screenshot(clip=clip))).convert('RGB')
            await wheel_to(page, await page.evaluate('scrollY') + H * .9)
            await page.wait_for_timeout(900)
            orbit = Image.open(io.BytesIO(await page.screenshot(clip=clip))).convert('RGB')
            still_pinned = abs((await section.locator('.instrument-stage').bounding_box())['y']) < 2
            await ev.shot(page, f'{slug}-orbit')
            await section.get_by_role('button', name='Open case file', exact=True).click()
            dialog = page.get_by_role('dialog', name=NAMES[slug], exact=True)
            await dialog.wait_for(state='visible')
            await page.wait_for_timeout(500)
            dialog_shot = await ev.shot(page, f'{slug}-case-preview')
            await dialog.get_by_role('button', name='Return to the instrument').click()
            await page.wait_for_timeout(400)
            focus = await section.get_by_role('button', name='Open case file').evaluate('(e)=>e===document.activeElement')
            idle_diff = sum(ImageStat.Stat(ImageChops.difference(first, idle)).mean)
            orbit_diff = sum(ImageStat.Stat(ImageChops.difference(idle, orbit)).mean)
            ok = (chapter_id == slug and pinned and still_pinned and reading == READINGS[slug][0]
                  and idle_diff > .1 and orbit_diff > 2 and focus)
            ev.check(f'chapter-{slug}', ok, f'active={chapter_id}, pinned={pinned and still_pinned}, reading={reading}, '
                     f'idle pixel diff={idle_diff:.2f}, orbit pixel diff={orbit_diff:.2f}, preview dialog + focus return={focus}; '
                     f'preview: {dialog_shot}', start)
        await ev.step(f'chapter-{slug}', chapter())
    ev.check('order', order == SLUGS, f'DOM order={order}', None)

    async def skills():
        await menu_to(page, 'Skills', '#skills')
        groups = page.locator('.skill-group')
        count = await groups.count()
        await groups.nth(1).locator('summary').click()
        await page.wait_for_timeout(500)
        shot = await ev.shot(page, 'skills-open')
        items = await page.locator('.skill-group li').evaluate_all(
            '(els)=>els.map(li=>({name:li.querySelector("h3").textContent,links:[...li.querySelectorAll("a")].map(a=>a.getAttribute("href"))}))')
        unlinked = [i['name'] for i in items if not i['links'] or any(h not in [f'#{s}' for s in SLUGS] for h in i['links'])]
        unconfirmed = [i['name'] for i in items if i['name'] in UNCONFIRMED]
        names = [i['name'] for i in items]
        core = all(any(k in n for n in names) for k in ['Python', 'Playwright', 'pytest', 'httpx', 'n8n'])
        ev.check('skills', count >= 10 and not unlinked and not unconfirmed and core,
                 f'{count} groups, {len(items)} skills, unlinked={unlinked}, unconfirmed published={unconfirmed}, '
                 f'Python/testing/scraping/workflow core present={core}', shot)
    await ev.step('skills', skills())

    async def skill_link():
        link = page.locator('.skill-group').nth(1).locator('[data-skill-project=brandwall]').first
        await link.click()
        await page.wait_for_function("Math.abs(document.getElementById('brandwall').getBoundingClientRect().top)<2", timeout=8000)
        await page.wait_for_timeout(900)
        highlighted = 'skill-highlight' in (await page.locator('#brandwall').get_attribute('class'))
        color = await page.locator('#brandwall-heading').evaluate('(e)=>getComputedStyle(e).color')
        focused = await page.locator('#brandwall-heading').evaluate('(e)=>e===document.activeElement')
        shot = await ev.shot(page, 'skill-link-brandwall')
        ev.check('skill-link', highlighted and focused, f'Playwright -> BrandWall: section top 0, highlight={highlighted} '
                 f'(heading {color}), heading focused={focused}', shot)
    await ev.step('skill-link', skill_link())

    async def about():
        portrait = await top_of(page, '.portrait-scan')
        await jump(page, portrait - H * .95)
        await wheel_to(page, portrait - H * .55, step=60, pause=90)
        clip_mid = await page.locator('.portrait-scan img').evaluate('(e)=>getComputedStyle(e).clipPath')
        mid = await ev.shot(page, 'about-scan-mid')
        await menu_to(page, 'About', '#about')
        await wheel_to(page, portrait - H * .2, step=60, pause=90)
        clip_end = await page.locator('.portrait-scan img').evaluate('(e)=>getComputedStyle(e).clipPath')
        loaded = await page.locator('.portrait-scan img').evaluate('(e)=>e.complete&&e.naturalWidth>0')
        text = await page.locator('#about').inner_text()
        end = await ev.shot(page, 'about-portrait')
        ev.check('about', loaded and clip_mid != clip_end and 'I build' in text,
                 f'portrait loaded={loaded}, clip mid={clip_mid!r} -> end={clip_end!r}; mid-scan frame: {mid}', end)
    await ev.step('about', about())

    async def contact():
        await menu_to(page, 'Contact', '#contact')
        cta = await page.locator('.email-cta').get_attribute('href')
        links = await page.locator('.contact-links a').evaluate_all(
            '(els)=>els.map(a=>({href:a.getAttribute("href"),target:a.target,rel:a.rel,h:Math.round(a.getBoundingClientRect().height)}))')
        overflow = await page.evaluate('document.documentElement.scrollWidth > innerWidth')
        shot = await ev.shot(page, 'contact')
        ok = (cta == CONTACTS[0] and [l['href'] for l in links] == CONTACTS and all(l['h'] >= 44 for l in links)
              and all(l['target'] == '_blank' and 'noopener' in l['rel'] for l in links[1:]) and not overflow)
        ev.check('contact', ok, f'CTA={cta}; links={[l["href"] for l in links]}; external open in new tab with noopener; '
                 f'tap heights={[l["h"] for l in links]}', shot)
    await ev.step('contact', contact())

    await page.evaluate('window.scrollTo(0,document.documentElement.scrollHeight)')
    await page.wait_for_timeout(900)
    readout = await page.locator('.progress-readout output').inner_text()
    await page.get_by_role('button', name='Rayin Observatory, return to the dome').click()
    await page.wait_for_function('scrollY<2', timeout=8000)
    await page.wait_for_timeout(1200)
    await ev.shot(page, 'returned-to-dome')
    canvases = await page.locator('canvas').count()
    ev.check('clean', canvases == 1 and not errors and not bad,
             f'canvas={canvases}, readout at end={readout}, errors={errors[:3]}, bad responses={bad[:3]}', None)
    video = page.video
    await context.close()
    webm = Path(await video.path())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(webm), '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', str(OUT / 'full-observatory-walkthrough.mp4')], check=True)
    shutil.rmtree(OUT / 'raw', ignore_errors=True)


async def viewports(browser, ev):
    folder = OUT / 'viewports'
    folder.mkdir()
    problems, shots = [], []
    for width, height in [(360, 740), (430, 932)]:
        context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=2, is_mobile=True, has_touch=True)
        page = await context.new_page()
        await enter(page)
        for target in ['#first-light'] + [f'#{s}' for s in SLUGS] + ['#skills', '#about', '#contact']:
            await jump(page, await top_of(page, target) + 2)
            if await page.evaluate('document.documentElement.scrollWidth > innerWidth'):
                problems.append(f'{width}: overflow at {target}')
            if target[1:] in SLUGS:
                cta = await page.locator(target).get_by_role('button', name='Open case file').bounding_box()
                pitch = await page.locator(f'{target} .instrument-pitch').bounding_box()
                if not (pitch['y'] + pitch['height'] < cta['y'] and cta['y'] + cta['height'] < height - 40):
                    problems.append(f'{width}: {target} CTA/pitch layout')
            path = folder / f'{width}x{height}-{target[1:]}.png'
            await page.screenshot(path=str(path))
            shots.append(path)
        await context.close()
    sheet = contact_sheet(shots, folder / 'viewports-sheet.jpg', columns=9, label_dir=True)
    ev.check('viewports', not problems, f'{len(shots)} section screens at 360x740 + 430x932; problems={problems}', sheet)


async def fallback(browser, ev):
    context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await page.route('**/models/brandwall.glb', lambda route: route.abort())
    await enter(page)
    scene = await page.locator('.observatory').get_attribute('data-scene')
    await jump(page, await top_of(page, '#surgeline') + 2)
    notice = await page.locator('.fallback-notice').bounding_box()
    copy = await page.locator('#surgeline .instrument-copy').bounding_box()
    image = await page.locator('.surgeline-fallback').bounding_box()
    shot = await ev.shot(page, 'fallback-still-view')
    await context.close()
    ev.check('fallback', scene == 'fallback' and notice['y'] + notice['height'] <= copy['y'] and 0 < image['y'],
             f'brandwall.glb blocked -> scene={scene}; notice bottom={notice["y"] + notice["height"]:.1f} <= copy top={copy["y"]:.1f}', shot)


def contact_sheet(paths, target, columns=6, label_dir=False):
    font = ImageFont.truetype(str(ROOT / 'web/public/fonts/jetbrains-mono.ttf'), 15)
    tile_w, label_h, pad = 234, 30, 10
    tiles = []
    for path in paths:
        image = Image.open(path).convert('RGB')
        image = image.resize((tile_w, round(image.height * tile_w / image.width)))
        tiles.append((image, path.stem))
    tile_h = max(t[0].height for t in tiles)
    rows = -(-len(tiles) // columns)
    sheet = Image.new('RGB', (columns * (tile_w + pad) + pad, rows * (tile_h + label_h + pad) + pad), '#0B1020')
    draw = ImageDraw.Draw(sheet)
    for i, (image, label) in enumerate(tiles):
        x, y = pad + (i % columns) * (tile_w + pad), pad + (i // columns) * (tile_h + label_h + pad)
        draw.text((x, y + 6), label[:28], fill='#F2A541', font=font)
        sheet.paste(image, (x, y + label_h))
    sheet.save(target, quality=88)
    return str(target.relative_to(OUT))


async def run():
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True)
    ev = Evidence()
    report = {'status': 'running', 'startedAt': datetime.now(timezone.utc).isoformat(), 'url': URL, 'viewport': [W, H],
              'scope': 'Phase 3 Testing; Chromium mobile emulation; no physical-device fps/speaker/carrier claim', 'items': ITEMS}
    print('assets + numbers', flush=True)
    try:
        ok, detail = check_assets()
        ev.check('assets', ok, json.dumps(detail['totalBytes']) + ' bytes across 7 GLBs, all Draco, each <= 1.5 MB', renders_sheet())
        report['assets'] = detail
    except Exception as error:
        ev.check('assets', False, f'{type(error).__name__}: {error}')
    ok, detail = check_numbers()
    ev.check('numbers', ok, ', '.join(f'{s} {d["reading"]} -> CAPABILITY_{s.upper()}.md {d["dossierLine"]}' for s, d in detail.items()))
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        print(f'walkthrough {W}x{H}', flush=True)
        await main_flow(browser, ev)
        print('viewports', flush=True)
        await ev.step('viewports', viewports(browser, ev))
        print('fallback', flush=True)
        await ev.step('fallback', fallback(browser, ev))
        await browser.close()
    contact_sheet([p for p, _ in ev.shots], OUT / 'contact-sheet.jpg')
    missing = [item for item in ITEMS if item not in ev.checks]
    passed = not missing and all(c['pass'] for c in ev.checks.values())
    report.update(status='passed' if passed else 'failed', finishedAt=datetime.now(timezone.utc).isoformat(), missing=missing,
                  checks={item: ev.checks.get(item) for item in ITEMS}, video='full-observatory-walkthrough.mp4',
                  contactSheet='contact-sheet.jpg', screenshots=[str(p.relative_to(OUT)) for p, _ in ev.shots])
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['status'].upper()}: {sum(c['pass'] for c in ev.checks.values())}/{len(ITEMS)} items", flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if asyncio.run(run()) else 1)
