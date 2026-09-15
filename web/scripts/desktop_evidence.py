"""Phase 6 Testing evidence: desktop composition of the homepage and all five case files.
Records a 1440x900 MP4 of the main desktop flow (gate -> hero -> header Work -> five chapters ->
Skills -> About -> Contact -> Open case file -> five-case chain + wrap -> history -> header About ->
Return), checks 1366x768 and 1920x1080, a live resize across the 1024px breakpoint, a blocked
model on desktop, and three phone viewports (the approved mobile layout must be unchanged).
Writes one PNG per checklist item, labeled contact sheet, viewport sheets and evidence.json.

Target: local production preview (OBSERVATORY_URL default http://127.0.0.1:8767).
Chromium GPU emulation only; no physical-device fps claim.
"""
import asyncio
import io
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from case_files_evidence import CASES, FORBIDDEN, SECTIONS, difference, flight, glide, overflow, tile, top  # noqa: E402
from verify_case import URL, enter, idle  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/desktop/evidence'
DESK = (1440, 900)
TILE = (480, 300)
PHONES = [(390, 844), (360, 740), (430, 932)]
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']
AMBER = 'rgb(242, 165, 65)'
REGRESSIONS = {
    'verify_desktop.py (390×844 → 1366×768 → 1440×900 → 1920×1080)': 'assets/renders/desktop/dev/verification.json',
    'verify:mobile (homepage, 3 phones)': 'assets/renders/full-observatory/dev/verification.json',
    'verify_case.py (CrossCheck case, 3 phones)': 'assets/renders/case-crosscheck/dev/verification.json',
    'verify_cases.py (five cases + chain, 3 phones)': 'assets/renders/case-files/dev/verification.json',
}

ITEMS = {
    'gate': 'Gate (1440×900): two-column entry, title left, calibration + Enter right; Enter without sound works',
    'hero': 'Hero: text rail left, dome + Saturn on the right of a full-width Canvas; header shows Work / About / Contact instead of Menu',
    'headerNav': 'Header navigation: Work / About / Contact scroll to their sections, on the homepage and from a case file',
    'chapters': 'Five chapters: copy + reading rail left, instrument on the right, camera orbits on scroll, no overlap',
    'skills': 'Skills: heading left, accordion right with two-column items; a project link scrolls to its chapter',
    'about': 'About: portrait left, copy right, paragraphs grouped without stretched gaps',
    'contact': 'Contact: CTA left, four links right, correct targets',
    'flightIn': 'Open case file on desktop: text fades, scroll locked, camera flies in, focus on the case heading',
    'caseBrief': 'Case brief in two columns (title + deck left, brief right) in all five case files',
    'hotspots': 'Instrument inspection: 15 markers in the right pane, card on the left without overlap, leader lines end inside the pane',
    'flow': 'How it works: four steps laid out horizontally in all five cases',
    'readings': 'Readings: two-column grid counting up to the dossier values in all five cases',
    'toolsVideo': 'Tools in three columns linking to Skills; wide demo video, lazy-loaded, correct duration',
    'nextChain': 'Next instrument chain on desktop: CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall → CrossCheck, then Back / Forward',
    'returnFlight': 'Return on desktop: camera retreats, homepage scroll position and focus restored',
    'desktopViewports': '1366×768 and 1920×1080: same wide composition, chapter rail without overlap, card beside the pane',
    'resize': 'Live resize 390 → 768 → 1024 → 1440 → 1920 → 390: layout switches at 1024 px, same Canvas, leaders stay in the pane',
    'fallback': 'Model blocked on desktop: labeled still views on the right, notice clear of copy, cards and Return work',
    'phones': 'Phones not broken: 390×844, 360×740, 430×932 keep the approved mobile layout; mobile regression suites pass',
    'copy': 'Copy unchanged: identical homepage and case text on phone and desktop, no DRAFT label, no forbidden terms',
    'clean': 'One persistent Canvas, zero page errors, zero responses ≥400, no horizontal overflow in the desktop flow',
}

FINDINGS = {
    'caseBrief': 'For the owner, not an automatic fail: on wide screens the first view of a case file is the two-column brief with '
                 'the lower ~40% of the screen empty; the instrument starts below the fold. This is the Phase 4 arrival '
                 '(accepted as-is on mobile) laid out wide. Options: accept, or back to Development to bring the instrument '
                 'into the first desktop view.',
}


def box_right(b):
    return b['x'] + b['width']


def box_bottom(b):
    return b['y'] + b['height']


def centroid(png):
    """Horizontal centre of bright pixels (0-1) in a canvas-only screenshot."""
    gray = np.asarray(Image.open(io.BytesIO(png)).convert('L'), dtype=np.float32)
    weights = np.where(gray > 70, gray, 0)
    total = weights.sum()
    if not total:
        return 0.0
    return float((weights.sum(axis=0) * np.arange(gray.shape[1])).sum() / total / gray.shape[1])


async def frames(page, n=2):
    await page.evaluate('(n)=>new Promise(r=>{const f=k=>k?requestAnimationFrame(()=>f(k-1)):r();f(n)})', n)


async def canvas_only(page):
    await page.evaluate("document.querySelector('.site-content').style.visibility='hidden'")
    await frames(page)
    shot = await page.screenshot()
    await page.evaluate("document.querySelector('.site-content').style.visibility=''")
    return shot


async def bbox(page, selector):
    return await page.locator(selector).first.bounding_box()


async def at_top(page, selector):
    """Wait until a section is scrolled to the top (clamped to the page end)."""
    await page.wait_for_function('''(s)=>{const e=document.querySelector(s); if(!e) return false;
      const y=Math.min(e.getBoundingClientRect().top+scrollY, document.documentElement.scrollHeight-innerHeight);
      return Math.abs(scrollY-y)<3}''', arg=selector, timeout=15000)
    await page.wait_for_timeout(500)


async def nav(page, name):
    await page.get_by_role('navigation', name='Desktop navigation').get_by_role('button', name=name, exact=True).click()


async def home_text(page):
    return re.sub(r'\s+', ' ', await page.locator('.page-content').text_content()).strip()


def row(images, path, size=TILE):
    sheet = Image.new('RGB', (size[0] * len(images), size[1]), 'black')
    for i, (source, label) in enumerate(images):
        sheet.paste(tile(source, label, size), (i * size[0], 0))
    sheet.save(path)


def grid(entries, path, cols, size=TILE, quality=86):
    rows = (len(entries) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * size[0], rows * size[1]), 'black')
    for i, (name, label) in enumerate(entries):
        if (OUT / name).exists():
            sheet.paste(tile(OUT / name, label, size), ((i % cols) * size[0], (i // cols) * size[1]))
    sheet.save(path, quality=quality)


async def main_flow(browser, checks, text):
    W, H = DESK
    context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1,
                                        record_video_dir=str(OUT / 'raw'), record_video_size={'width': W, 'height': H})
    page = await context.new_page()
    errors, bad, videos, overflows = [], [], [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('response', lambda r: bad.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
    page.on('request', lambda r: videos.append(r.url) if '/videos/' in r.url else None)

    async def snap(name):
        overflows.append(await overflow(page))
        await page.screenshot(path=str(OUT / name))

    # Gate: two columns, Enter enabled after calibration.
    await page.goto(URL)
    await page.wait_for_function("!document.querySelector('.silent-button').disabled", timeout=30000)
    await page.wait_for_timeout(400)
    await snap('01-gate.png')
    title, button = await bbox(page, '.gate-main h1'), await bbox(page, '.enter-button')
    await page.locator('.silent-button').click()
    await page.wait_for_selector('.entry-gate[hidden]', state='attached')
    await idle(page)
    await page.evaluate("""
        window.__canvas = document.querySelector('canvas');
        new MutationObserver(() => window.__flight && window.__flight.push(document.querySelector('.observatory').dataset.flight))
          .observe(document.querySelector('.observatory'), {attributes: true, attributeFilter: ['data-flight']});
    """)
    checks['gate'] = {
        'pass': box_right(title) < button['x'] and button['x'] > W / 2 and await page.locator('.observatory').get_attribute('data-scene') == 'ready',
        'detail': f"title right edge {round(box_right(title))} px < Enter x {round(button['x'])} px; entered silently, scene ready",
        'screenshot': '01-gate.png',
    }

    # Hero
    await page.wait_for_timeout(1200)
    await snap('02-hero.png')
    hero = await bbox(page, '.hero-copy')
    hero_x = centroid(await canvas_only(page))
    nav_visible = await page.locator('.desktop-navigation').is_visible()
    menu_visible = await page.locator('.menu-toggle').is_visible()
    full = await page.locator('.scene-layer').evaluate('e=>e.clientWidth===innerWidth')
    checks['hero'] = {
        'pass': nav_visible and not menu_visible and full and box_right(hero) < W * .5 and hero_x > .55,
        'detail': f"nav visible={nav_visible}, Menu hidden={not menu_visible}, full-width Canvas={full}, copy right edge {round(box_right(hero))} px of {W}, 3D light centre at {hero_x:.2f} of width",
        'screenshot': '02-hero.png',
    }
    text['desktopHome'] = await home_text(page)

    # Header Work, then the five chapters with wheel scrolling (visible Lenis on video).
    await nav(page, 'Work')
    await at_top(page, '#crosscheck')
    nav_work = True
    chapter_results = []
    for case in CASES:
        slug = case['id']
        await glide(page, await top(page, f'#{slug}') + 240)
        await page.wait_for_timeout(600)
        await snap(f'03-chapter-{slug}.png')
        copy, reading = await bbox(page, f'#{slug} .instrument-copy'), await bbox(page, f'#{slug} .instrument-reading')
        a = await canvas_only(page)
        side = centroid(a)
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, f'#{slug}') + 240 + H * .8)
        await page.wait_for_timeout(700)
        orbit = difference(a, await canvas_only(page))
        ok = box_bottom(copy) + 20 < reading['y'] and max(box_right(copy), box_right(reading)) < W * .5 and side > .55 and orbit > 3
        chapter_results.append({'slug': slug, 'pass': ok, 'side': round(side, 2), 'orbit': orbit, 'gap': round(reading['y'] - box_bottom(copy))})
    checks['chapters'] = {
        'pass': all(r['pass'] for r in chapter_results),
        'detail': '; '.join(f"{r['slug']}: copy→reading gap {r['gap']} px, 3D centre {r['side']}, orbit change {r['orbit']}" for r in chapter_results),
        'screenshot': '03-chapter-crosscheck.png',
    }

    # Skills
    await glide(page, await top(page, '#skills'))
    # Second group (Test automation & QA) has several items, so the two-column grid is measurable.
    await page.locator('.skill-group summary').nth(1).click()
    await page.wait_for_timeout(500)
    await snap('04-skills.png')
    heading, groups = await bbox(page, '#skills-heading'), await bbox(page, '.skill-groups')
    items = await page.locator('.skill-group[open] li').evaluate_all('els=>els.map(e=>Math.round(e.getBoundingClientRect().left))')
    link = page.locator('.skill-group[open] [data-skill-project]').first
    project = await link.get_attribute('data-skill-project')
    await link.click()
    await at_top(page, f'#{project}')
    highlighted = await page.locator(f'#{project}.skill-highlight').count() == 1
    await snap('04b-skill-link.png')
    checks['skills'] = {
        'pass': box_right(heading) < groups['x'] and highlighted and len(set(items)) == 2,
        'detail': f"heading right {round(box_right(heading))} < accordion x {round(groups['x'])}; item columns x={sorted(set(items))}; project link → #{project} scrolled + highlighted={highlighted}",
        'screenshot': '04-skills.png',
    }

    # About (header)
    await nav(page, 'About')
    await at_top(page, '#about')
    await page.wait_for_timeout(1400)
    await snap('05-about.png')
    portrait, about_h = await bbox(page, '#about .portrait-scan'), await bbox(page, '#about-heading')
    paras = await page.locator('#about > p:not(.section-kicker)').evaluate_all('els=>els.map(e=>{const r=e.getBoundingClientRect();return [r.top,r.bottom]})')
    gaps = [round(paras[0][0] - box_bottom(about_h)), round(paras[1][0] - paras[0][1])]
    checks['about'] = {
        'pass': box_right(portrait) < about_h['x'] and gaps[0] < 100 and gaps[1] < 60,
        'detail': f"portrait right {round(box_right(portrait))} < heading x {round(about_h['x'])}; heading→paragraph {gaps[0]} px, paragraph→paragraph {gaps[1]} px",
        'screenshot': '05-about.png',
    }

    # Contact (header)
    await nav(page, 'Contact')
    await at_top(page, '#contact')
    await snap('06-contact.png')
    cta = await bbox(page, '.email-cta')
    links_box = await bbox(page, '.contact-links')
    mail = await page.locator('.email-cta').get_attribute('href')
    links = await page.locator('.contact-links a').evaluate_all('els=>els.map(e=>[e.getAttribute("href"), e.target, e.rel])')
    external_ok = all(href.startswith('mailto:') or (href.startswith('https://') and target == '_blank' and 'noopener' in rel) for href, target, rel in links)
    checks['contact'] = {
        'pass': box_right(cta) < links_box['x'] and mail.startswith('mailto:') and len(links) == 4 and external_ok,
        'detail': f"CTA right {round(box_right(cta))} < links x {round(links_box['x'])}; CTA {mail}; {len(links)} links, external open in new tab with noopener={external_ok}",
        'screenshot': '06-contact.png',
    }

    # Flight into CrossCheck from the chapter.
    await nav(page, 'Work')
    await at_top(page, '#crosscheck')
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#crosscheck') + 240)
    await page.wait_for_timeout(700)
    f = await flight(page, lambda: page.locator('[data-open-case=crosscheck]').click(), f'{URL}/work/crosscheck')
    for key, suffix in (('start', 'a'), ('mid', 'b'), ('end', 'c')):
        (OUT / f'07{suffix}-flight-{key}.png').write_bytes(f[key])
    row([(f['start'], 'Tap Open case file'), (f['mid'], 'Flying in · text fades'), (f['end'], 'CrossCheck case file')], OUT / '07-flight-in.png')
    focus = await page.evaluate('document.activeElement && document.activeElement.id')
    same = await page.evaluate("window.__canvas === document.querySelector('canvas')")
    checks['flightIn'] = {
        'pass': 'moving' in f['states'] and f['locked'] and f['midOpacity'] < 1 and same and focus == 'case-heading',
        'detail': f"flight states {f['states']}, scroll locked={f['locked']}, homepage opacity mid-flight {f['midOpacity']}, same Canvas={same}, focus #{focus}",
        'screenshot': '07-flight-in.png',
    }

    # Five cases in chain order.
    per = {k: {} for k in ('caseBrief', 'hotspots', 'flow', 'readings', 'toolsVideo')}
    chain = []
    for idx, case in enumerate(CASES):
        slug, name = case['id'], case['name']
        print(f'Desktop case: {name}', flush=True)
        await page.wait_for_function('(n)=>document.getElementById("case-heading")?.textContent===n', arg=name)
        await page.wait_for_timeout(400)
        await snap(f'08-{slug}-brief.png')
        body = await page.locator('.case-page').text_content()
        positions = [body.find(s) for s in SECTIONS]
        left, right = await bbox(page, '.case-title'), await bbox(page, '.case-brief-copy')
        per['caseBrief'][slug] = box_right(left) < right['x'] and right['y'] < box_bottom(left) and all(p >= 0 for p in positions) and positions == sorted(positions)

        # Hotspots. Lenis can pull a plain scrollTo back to its own wheel target, so pin the exact position.
        await glide(page, await top(page, '#case-instrument'))
        for _ in range(6):
            target = await top(page, '#case-instrument')
            await page.evaluate('(y)=>scrollTo(0,y)', target)
            await page.wait_for_timeout(350)
            if abs(await page.evaluate('scrollY') - target) < 3:
                break
        pane = await bbox(page, '.case-inspection')
        cards = []
        for i in range(3):
            marker = page.locator(f'.hotspot-{i}')
            await marker.click()
            await page.wait_for_function('(i)=>getComputedStyle(document.querySelector(".hotspot-"+i)).backgroundColor==="%s"' % AMBER, arg=i)
            await frames(page)
            await page.wait_for_timeout(350)  # marker/card transitions settle before measuring
            card, mark = await bbox(page, '#component-card'), await marker.bounding_box()
            cards.append({
                'title': await page.locator('#component-card h3').inner_text(),
                'beside': box_right(card) < pane['x'],
                'inPane': pane['x'] <= mark['x'] and box_right(mark) <= box_right(pane) + 1,
                'inView': card['y'] >= 80 and box_bottom(card) <= H - 45,
                'tap': min(mark['width'], mark['height']) >= 44,
            })
            if idx == 0 or i == 0:
                await snap(f'09-{slug}-hotspot-{i + 1}.png')
        leaders = await page.locator('.hotspot-leaders').evaluate('''svg=>[...svg.querySelectorAll('line')].map(l=>[+l.getAttribute('x2'),+l.getAttribute('y2'),svg.clientWidth,svg.clientHeight])''')
        await page.get_by_role('button', name='Close component card').click()
        per['hotspots'][slug] = {
            'pass': [c['title'] for c in cards] == case['cards'] and all(all(v for k, v in c.items() if k != 'title') for c in cards)
                    and len(leaders) == 3 and all(0 < x < w and 0 < y < h for x, y, w, h in leaders),
            'cards': cards, 'leaders': [[round(x), round(y)] for x, y, _, _ in leaders],
        }

        # Flow
        await glide(page, await top(page, '#flow-heading') - 110)
        steps = await page.locator('.signal-flow li').evaluate_all('els=>els.map(e=>Math.round(e.getBoundingClientRect().top))')
        await snap(f'10-{slug}-flow.png')
        per['flow'][slug] = len(steps) == 4 and max(steps) - min(steps) < 2

        # Readings
        await glide(page, await top(page, '#readings-heading') - 110)
        # Prerendered HTML already holds the final values; let the count-up restart and finish first.
        await page.wait_for_timeout(1800)
        for i, value in enumerate(case['countValues']):
            await page.wait_for_function('(a)=>document.querySelectorAll("[data-count]")[a.i].textContent===a.v', arg={'i': i, 'v': value}, timeout=15000)
        shown = await page.locator('.case-reading strong').evaluate_all('els=>els.map(e=>e.textContent)')
        columns = sorted(set(await page.locator('.case-reading').evaluate_all('els=>els.map(e=>Math.round(e.getBoundingClientRect().left))')))
        await snap(f'11-{slug}-readings.png')
        per['readings'][slug] = {'pass': shown == case['displayReadings'] and len(columns) == 2, 'shown': shown, 'columns': columns}

        # Tools + video
        await glide(page, await top(page, '#tools-heading') - 110)
        tools = await page.locator('.case-tools a').evaluate_all('els=>els.map(e=>[Math.round(e.getBoundingClientRect().left), e.getAttribute("href")])')
        tool_columns = len({x for x, _ in tools})
        await glide(page, await top(page, '#demo-heading') - 110)
        video = page.locator('.case-video')
        preload, poster = await video.get_attribute('preload'), await video.get_attribute('poster')
        before = len(videos)
        await video.evaluate('v=>v.play()')
        await page.wait_for_function('document.querySelector(".case-video").currentTime>.3', timeout=20000)
        meta = await video.evaluate('v=>({d:v.duration,muted:v.muted,w:v.getBoundingClientRect().width})')
        await video.evaluate('v=>v.pause()')
        await snap(f'12-{slug}-demo.png')
        per['toolsVideo'][slug] = {
            'pass': len(tools) == case['expectedTools'] and tool_columns == 3 and all(h == '/#skills' for _, h in tools)
                    and preload == 'none' and poster == f'/images/{slug}-demo-poster.jpg' and len(videos) > before
                    and abs(meta['d'] - case['duration']) < 1 and meta['muted'] and meta['w'] > W * .6,
            'detail': f"{len(tools)} tools in {tool_columns} columns; video {meta['d']:.1f}s, {round(meta['w'])} px wide, muted={meta['muted']}",
        }

        # Next instrument
        await glide(page, await top(page, '#next-heading') - 110)
        nxt = CASES[(idx + 1) % len(CASES)]
        heading_ok = await page.locator('.case-next h2').inner_text() == nxt['name']
        hop = await flight(page, lambda: page.locator('.case-next .case-button').click(), f"{URL}/work/{nxt['id']}")
        chain.append({'from': slug, 'to': nxt['id'], 'ok': heading_ok and 'moving' in hop['states'] and hop['locked']})
        if idx == 0:
            (OUT / '13-chain-sweep.png').write_bytes(hop['mid'])

    checks['caseBrief'] = {
        'pass': all(per['caseBrief'].values()),
        'detail': 'two columns + 7 template sections in order: ' + ', '.join(f"{k}={v}" for k, v in per['caseBrief'].items()),
        'screenshot': '08-crosscheck-brief.png',
    }
    checks['hotspots'] = {
        'pass': all(v['pass'] for v in per['hotspots'].values()),
        'detail': '; '.join(f"{k}: {[c['title'] for c in v['cards']]} leaders {v['leaders']}" + ('' if v['pass'] else f" FAILED cards {v['cards']}") for k, v in per['hotspots'].items()),
        'screenshot': '09-crosscheck-hotspot-1.png',
    }
    checks['flow'] = {
        'pass': all(per['flow'].values()),
        'detail': 'four steps on one row: ' + ', '.join(f"{k}={v}" for k, v in per['flow'].items()),
        'screenshot': '10-crosscheck-flow.png',
    }
    checks['readings'] = {
        'pass': all(v['pass'] for v in per['readings'].values()),
        'detail': '; '.join(f"{k}: {v['shown']} in {len(v['columns'])} columns" for k, v in per['readings'].items()),
        'screenshot': '11-crosscheck-readings.png',
    }
    checks['toolsVideo'] = {
        'pass': all(v['pass'] for v in per['toolsVideo'].values()),
        'detail': '; '.join(f"{k}: {v['detail']}" for k, v in per['toolsVideo'].items()),
        'screenshot': '12-crosscheck-demo.png',
    }

    # History inside the chain.
    await page.go_back()
    await page.wait_for_url(f'{URL}/work/brandwall')
    await idle(page)
    back_ok = await page.locator('#case-heading').inner_text() == 'BrandWall'
    await page.go_forward()
    await page.wait_for_url(f'{URL}/work/crosscheck')
    await idle(page)
    forward_ok = await page.locator('#case-heading').inner_text() == 'CrossCheck'
    checks['nextChain'] = {
        'pass': len(chain) == 5 and all(c['ok'] for c in chain) and back_ok and forward_ok,
        'detail': ' → '.join(c['from'] for c in chain) + f" → {chain[-1]['to']}; all flights locked + headings right={all(c['ok'] for c in chain)}; Back → BrandWall={back_ok}, Forward → CrossCheck={forward_ok}",
        'screenshot': '13-chain-sweep.png',
    }

    # Header About from a case file.
    await nav(page, 'About')
    await page.wait_for_url(URL + '/')
    await idle(page)
    await at_top(page, '#about')
    await snap('14-case-to-about.png')
    case_about = await page.evaluate("window.__canvas === document.querySelector('canvas')")
    checks['headerNav'] = {
        'pass': nav_work and highlighted is not None and case_about,
        'detail': 'Work → #crosscheck, About → #about, Contact → #contact on the homepage; About from /work/crosscheck lands on #about with the same Canvas=' + str(case_about),
        'screenshot': '14-case-to-about.png',
    }

    # Return flight restores scroll + focus.
    await nav(page, 'Work')
    await at_top(page, '#crosscheck')
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#crosscheck') + 240)
    await page.wait_for_timeout(700)
    origin = await page.evaluate('scrollY')
    await page.locator('[data-open-case=crosscheck]').click()
    await page.wait_for_url(f'{URL}/work/crosscheck')
    await idle(page)
    ret = await flight(page, lambda: page.locator('.case-brief .case-back').click(), URL + '/')
    row([(ret['start'], 'Tap Return'), (ret['mid'], 'Camera retreats'), (ret['end'], 'Back at CrossCheck')], OUT / '15-return-flight.png')
    back_y = await page.evaluate('scrollY')
    focused = await page.locator('[data-open-case=crosscheck]').evaluate('e=>e===document.activeElement')
    checks['returnFlight'] = {
        'pass': 'moving' in ret['states'] and ret['locked'] and abs(back_y - origin) < 2 and focused,
        'detail': f"flight states {ret['states']}, locked={ret['locked']}, scrollY {back_y} vs origin {origin}, focus on Open case file={focused}",
        'screenshot': '15-return-flight.png',
    }

    canvases = await page.locator('canvas').count()
    checks['clean'] = {
        'pass': canvases == 1 and not errors and not bad and not any(overflows),
        'detail': f"Canvas={canvases}, page/console errors={errors or 0}, responses ≥400={bad or 0}, horizontal overflow={any(overflows)}",
        'screenshot': '02-hero.png',
    }
    await page.goto(f'{URL}/work/crosscheck')
    await page.locator('.silent-button').click(timeout=30000)
    await idle(page)
    text['desktopCase'] = re.sub(r'\s+', ' ', await page.locator('.case-page').text_content()).strip()
    raw = await page.video.path()
    await context.close()
    return raw


async def desktop_size(browser, width, height):
    context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=1)
    page = await context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    tag = f'{width}x{height}'
    wide = []
    await enter(page)
    await page.wait_for_timeout(1000)
    await page.screenshot(path=str(OUT / f'viewports/hero-{tag}.png'))
    side = centroid(await canvas_only(page))
    nav_ok = await page.locator('.desktop-navigation').is_visible() and not await page.locator('.menu-toggle').is_visible()
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#crosscheck') + 240)
    await page.wait_for_timeout(800)
    await page.screenshot(path=str(OUT / f'viewports/chapter-{tag}.png'))
    copy, reading = await bbox(page, '#crosscheck .instrument-copy'), await bbox(page, '#crosscheck .instrument-reading')
    wide.append(await overflow(page))
    await page.locator('[data-open-case=crosscheck]').click()
    await page.wait_for_url(f'{URL}/work/crosscheck')
    await idle(page)
    wide.append(await overflow(page))
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#case-instrument'))
    await page.wait_for_timeout(700)
    await page.locator('.hotspot-0').click()
    await page.wait_for_function('getComputedStyle(document.querySelector(".hotspot-0")).backgroundColor==="%s"' % AMBER)
    card, pane = await bbox(page, '#component-card'), await bbox(page, '.case-inspection')
    await page.screenshot(path=str(OUT / f'viewports/hotspot-{tag}.png'))
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#readings-heading') - 110)
    await page.wait_for_timeout(1800)
    for i, value in enumerate(CASES[0]['countValues']):
        await page.wait_for_function('(a)=>document.querySelectorAll("[data-count]")[a.i].textContent===a.v', arg={'i': i, 'v': value}, timeout=15000)
    await page.screenshot(path=str(OUT / f'viewports/readings-{tag}.png'))
    wide.append(await overflow(page))
    await context.close()
    ok = nav_ok and side > .55 and box_bottom(copy) + 20 < reading['y'] and box_right(card) < pane['x'] and box_bottom(card) <= height - 45 and not any(wide) and not errors
    return {'viewport': tag, 'pass': ok, 'detail': f"{tag}: nav={nav_ok}, 3D centre {side:.2f}, copy→reading gap {round(reading['y'] - box_bottom(copy))} px, card right {round(box_right(card))} < pane x {round(pane['x'])}, overflow={any(wide)}, errors={len(errors)}"}


async def resize(browser, checks):
    context = await browser.new_context(viewport={'width': 390, 'height': 844})
    page = await context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    await enter(page, '/work/crosscheck')
    await page.evaluate('window.__canvas = document.querySelector("canvas")')
    results = []
    for width, height in [(390, 844), (768, 900), (1024, 768), (1440, 900), (1920, 1080), (390, 844)]:
        await page.set_viewport_size({'width': width, 'height': height})
        await page.wait_for_timeout(800)
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#case-instrument'))
        await page.wait_for_timeout(700)
        marker = page.locator('.hotspot-0')
        if await marker.get_attribute('aria-expanded') != 'true':
            await marker.click()
        await page.wait_for_function('getComputedStyle(document.querySelector(".hotspot-0")).backgroundColor==="%s"' % AMBER)
        await frames(page)
        pane = await bbox(page, '.case-inspection')
        xs = await page.locator('.hotspot-leaders line').evaluate_all('els=>els.map(e=>+e.getAttribute("x2"))')
        desktop = width >= 1024
        state = {
            'size': f'{width}x{height}',
            'sameCanvas': await page.evaluate('window.__canvas === document.querySelector("canvas")'),
            'nav': await page.locator('.desktop-navigation').is_visible() == desktop,
            'menu': await page.locator('.menu-toggle').is_visible() != desktop,
            'leaders': all(0 < x < pane['width'] for x in xs),
            'overflow': await overflow(page),
        }
        state['pass'] = state['sameCanvas'] and state['nav'] and state['menu'] and state['leaders'] and not state['overflow']
        results.append(state)
        await page.screenshot(path=str(OUT / f'viewports/resize-{width}x{height}.png'))
    await context.close()
    checks['resize'] = {
        'pass': all(r['pass'] for r in results) and not errors,
        'detail': '; '.join(f"{r['size']}: {'ok' if r['pass'] else r}" for r in results) + f"; errors={len(errors)}",
        'screenshot': 'viewports/resize-sheet.jpg',
    }


async def fallback(browser, checks):
    W, H = DESK
    context = await browser.new_context(viewport={'width': W, 'height': H})
    await context.route('**/models/brandwall.glb', lambda route: route.abort())
    page = await context.new_page()
    await enter(page)
    await page.wait_for_selector('.observatory[data-scene="fallback"]')
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#driftwatch') + 240)
    await page.wait_for_timeout(900)
    await page.screenshot(path=str(OUT / '16a-fallback-home.png'))
    still = await bbox(page, '.driftwatch-fallback')
    notice, copy = await bbox(page, '.fallback-notice'), await bbox(page, '#driftwatch .instrument-copy')
    clear = box_right(copy) < notice['x'] or box_bottom(notice) < copy['y']
    origin = await page.evaluate('scrollY')
    await page.locator('[data-open-case=driftwatch]').click()
    await page.wait_for_url(f'{URL}/work/driftwatch')
    await idle(page)
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#case-instrument'))
    await page.wait_for_timeout(700)
    await page.locator('.hotspot-1').click()
    card_title = await page.locator('#component-card h3').inner_text()
    case_still = await bbox(page, '.case-instrument-still')
    pane = await bbox(page, '.case-inspection')
    await page.screenshot(path=str(OUT / '16b-fallback-case.png'))
    await page.locator('.case-brief .case-back').click()
    await page.wait_for_url(URL + '/')
    await idle(page)
    back_y = await page.evaluate('scrollY')
    await context.close()
    row([(OUT / '16a-fallback-home.png', 'Model blocked · chapter still'), (OUT / '16b-fallback-case.png', 'Model blocked · case still + card')], OUT / '16-fallback.png', (720, 450))
    checks['fallback'] = {
        'pass': still['x'] > W * .4 and clear and card_title == CASES[2]['cards'][1] and case_still['x'] >= pane['x'] - 1 and abs(back_y - origin) < 2,
        'detail': f"chapter still x {round(still['x'])} px (right side), notice clear of copy={clear}, case still inside pane, card '{card_title}', Return → scrollY {back_y} vs origin {origin}",
        'screenshot': '16-fallback.png',
    }


async def phones(browser, checks, text):
    results = []
    for width, height in PHONES:
        tag = f'{width}x{height}'
        context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=2, is_mobile=True, has_touch=True)
        page = await context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        await enter(page)
        await page.wait_for_timeout(800)
        await page.screenshot(path=str(OUT / f'phones/hero-{tag}.png'))
        mobile_header = not await page.locator('.desktop-navigation').is_visible() and await page.locator('.menu-toggle').is_visible()
        if width == 390:
            text['phoneHome'] = await home_text(page)
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#crosscheck') + 280)
        await page.wait_for_timeout(700)
        await page.screenshot(path=str(OUT / f'phones/chapter-{tag}.png'))
        copy = await bbox(page, '#crosscheck .instrument-copy')
        stacked = copy['width'] > width * .7
        wide = [await overflow(page)]
        await page.locator('[data-open-case=crosscheck]').click()
        await page.wait_for_url(f'{URL}/work/crosscheck')
        await idle(page)
        await page.screenshot(path=str(OUT / f'phones/brief-{tag}.png'))
        if width == 390:
            text['phoneCase'] = re.sub(r'\s+', ' ', await page.locator('.case-page').text_content()).strip()
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#case-instrument'))
        await page.wait_for_timeout(600)
        await page.locator('.hotspot-0').click()
        card = await bbox(page, '#component-card')
        await page.screenshot(path=str(OUT / f'phones/hotspot-{tag}.png'))
        wide.append(await overflow(page))
        await page.locator('.case-brief .case-back').click()
        await page.wait_for_url(URL + '/')
        await idle(page)
        await context.close()
        ok = mobile_header and stacked and box_bottom(card) <= height and not any(wide) and not errors
        results.append({'viewport': tag, 'pass': ok, 'detail': f"{tag}: Menu header={mobile_header}, full-width copy={stacked}, card in view={box_bottom(card) <= height}, overflow={any(wide)}, errors={len(errors)}"})

    suites = []
    for label, path in REGRESSIONS.items():
        data = json.loads((ROOT / path).read_text())
        suites.append({'suite': label, 'status': data.get('status'), 'finishedAt': data.get('finishedAt')})
    size = (390, 844)
    sheet = Image.new('RGB', (size[0] * 3, size[1] * 4), 'black')
    for c, (w, h) in enumerate(PHONES):
        for r, kind in enumerate(['hero', 'chapter', 'brief', 'hotspot']):
            sheet.paste(tile(OUT / f'phones/{kind}-{w}x{h}.png', f'{w}x{h} · {kind}', size), (c * size[0], r * size[1]))
    sheet.save(OUT / 'phones/phones-sheet.jpg', quality=86)
    checks['phones'] = {
        'pass': all(r['pass'] for r in results) and all(s['status'] == 'passed' for s in suites),
        'detail': '; '.join(r['detail'] for r in results) + ' | regression suites: ' + '; '.join(f"{s['suite']}={s['status']}" for s in suites),
        'screenshot': 'phones/phones-sheet.jpg',
        'regressions': suites,
    }


def copy_check(checks, text):
    found = [w for w in FORBIDDEN for key in text if w.lower() in text[key].lower()]
    same_home = text.get('phoneHome') == text.get('desktopHome')
    same_case = text.get('phoneCase') == text.get('desktopCase')
    draft = 'DRAFT' in ' '.join(text.values())
    checks['copy'] = {
        'pass': same_home and same_case and not draft and not found,
        'detail': f"homepage text identical 390 vs 1440={same_home} ({len(text.get('desktopHome', ''))} chars); CrossCheck case identical={same_case}; DRAFT present={draft}; forbidden terms={found or 'none'}",
        'screenshot': '08-crosscheck-brief.png',
    }


def sheets():
    tags = ['1366x768', '1440x900', '1920x1080']
    shutil.copy(OUT / '02-hero.png', OUT / 'viewports/hero-1440x900.png')
    shutil.copy(OUT / '03-chapter-crosscheck.png', OUT / 'viewports/chapter-1440x900.png')
    shutil.copy(OUT / '09-crosscheck-hotspot-1.png', OUT / 'viewports/hotspot-1440x900.png')
    shutil.copy(OUT / '11-crosscheck-readings.png', OUT / 'viewports/readings-1440x900.png')
    entries = [(f'viewports/{kind}-{tag}.png', f'{tag} · {kind}') for kind in ['hero', 'chapter', 'hotspot', 'readings'] for tag in tags]
    grid(entries, OUT / 'viewports/desktop-sheet.jpg', 3, (640, 400))
    resize_entries = [(f'viewports/resize-{s}.png', f'resize → {s}') for s in ['390x844', '768x900', '1024x768', '1440x900', '1920x1080']]
    grid(resize_entries, OUT / 'viewports/resize-sheet.jpg', 5, (384, 400))
    labeled = [
        ('01-gate.png', 'Gate · two columns'),
        ('02-hero.png', 'Hero · text left, dome right'),
        ('03-chapter-crosscheck.png', '01 CrossCheck chapter'),
        ('03-chapter-surgeline.png', '02 SurgeLine chapter'),
        ('03-chapter-driftwatch.png', '03 DriftWatch chapter'),
        ('03-chapter-duewatch.png', '04 DueWatch chapter'),
        ('03-chapter-brandwall.png', '05 BrandWall chapter'),
        ('04-skills.png', 'Skills · two columns'),
        ('05-about.png', 'About · portrait + copy'),
        ('06-contact.png', 'Contact · CTA + links'),
        ('07b-flight-mid.png', 'Flight in · text fades'),
        ('08-crosscheck-brief.png', 'CrossCheck · brief'),
        ('09-crosscheck-hotspot-1.png', 'CrossCheck · inspection'),
        ('10-crosscheck-flow.png', 'CrossCheck · flow'),
        ('11-crosscheck-readings.png', 'CrossCheck · readings'),
        ('12-crosscheck-demo.png', 'CrossCheck · tools + video'),
        ('13-chain-sweep.png', 'Next → SurgeLine sweep'),
        ('09-surgeline-hotspot-1.png', 'SurgeLine · inspection'),
        ('09-driftwatch-hotspot-1.png', 'DriftWatch · inspection'),
        ('09-duewatch-hotspot-1.png', 'DueWatch · inspection'),
        ('09-brandwall-hotspot-1.png', 'BrandWall · inspection'),
        ('14-case-to-about.png', 'Header About from a case'),
        ('15-return-flight.png', 'Return flight'),
        ('16b-fallback-case.png', 'Model blocked · still view'),
    ]
    grid([(n, f'{i + 1:02d} {label}') for i, (n, label) in enumerate(labeled)], OUT / 'contact-sheet.jpg', 4)


async def run():
    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ('viewports', 'phones'):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    checks, text = {}, {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        try:
            raw = await main_flow(browser, checks, text)
            sizes = [await desktop_size(browser, w, h) for w, h in [(1366, 768), (1920, 1080)]]
            checks['desktopViewports'] = {
                'pass': all(s['pass'] for s in sizes),
                'detail': '; '.join(s['detail'] for s in sizes),
                'screenshot': 'viewports/desktop-sheet.jpg',
            }
            await resize(browser, checks)
            await fallback(browser, checks)
            await phones(browser, checks, text)
            copy_check(checks, text)
        finally:
            await browser.close()

    mp4 = OUT / 'desktop-walkthrough.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-crf', '22', '-movflags', '+faststart', str(mp4)], check=True)
    shutil.rmtree(OUT / 'raw', ignore_errors=True)
    sheets()
    duration = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(mp4)],
                                    capture_output=True, text=True, check=True).stdout)

    passed = all(c['pass'] for c in checks.values()) and len(checks) == len(ITEMS)
    report = {
        'status': 'passed' if passed else 'failed',
        'phase': 'Phase 6 — Desktop',
        'stage': 'Testing',
        'finishedAt': datetime.now(timezone.utc).isoformat(),
        'url': URL,
        'scope': 'Chromium GPU (ANGLE) emulation; desktop 1366×768 / 1440×900 / 1920×1080 at DPR 1, phones 390×844 / 360×740 / 430×932 at DPR 2',
        'items': {k: {'label': ITEMS[k], **checks.get(k, {'pass': False, 'detail': 'not executed'}), **({'finding': FINDINGS[k]} if k in FINDINGS else {})} for k in ITEMS},
        'video': {'file': mp4.name, 'size': list(DESK), 'seconds': round(duration, 1)},
        'contactSheet': 'contact-sheet.jpg',
        'viewportSheets': ['viewports/desktop-sheet.jpg', 'viewports/resize-sheet.jpg', 'phones/phones-sheet.jpg'],
    }
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    for key, check in report['items'].items():
        print(f"{'PASS' if check['pass'] else 'FAIL'} {key}: {check['detail']}")
    print(f"Overall: {report['status']} · video {duration:.1f}s")
    return passed


if __name__ == '__main__':
    sys.exit(0 if asyncio.run(run()) else 1)
