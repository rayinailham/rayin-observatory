"""Phase 8 Testing evidence pack — Launch ready, full round, against the production URL (PLAN Q40).

Run with OBSERVATORY_URL=https://rayin-observatory.vercel.app (default here). Nothing is served locally.
Reuses the 7F walkthrough machinery (observatory_evidence.py) for Chromium: both devices filmed, five rooms, Next chain,
history, direct URL + refresh, interruptions, blocked model, chain fps — but writes to assets/renders/launch/evidence/.
Adds what only launch needs:
  browsers  Chromium / Firefox / WebKit × 390×844, 768×1024, 1440×900: enter, hero, five chapters, five cases through the Next chain
  share     head tags of the homepage + five cases as WhatsApp / LinkedIn / Facebook crawlers get them, the 1200×630 card of each,
            drawn as a link preview (share-previews.jpg); robots.txt, sitemap.xml, icons, unknown slug 404
Exit 1 if an item fails.
"""
import asyncio
import json
import os
import re
import shutil
import sys
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import unescape
from io import BytesIO
from pathlib import Path

os.environ.setdefault('OBSERVATORY_URL', 'https://rayin-observatory.vercel.app')

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from playwright.async_api import async_playwright  # noqa: E402

import observatory_evidence as oe  # noqa: E402
import q49  # noqa: E402
from perf_quick import GPU  # noqa: E402
from verify_case import URL, enter, idle  # noqa: E402
from verify_cases import CASES, trace_numbers  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/launch/evidence'
oe.OUT, oe.RAW = OUT, OUT / 'raw'
IDS, NAMES, CHECKS, META = q49.IDS, oe.NAMES, {}, {'errors': {}}
FONT = '/usr/share/fonts/TTF/DejaVuSans.ttf'
FONT_B = '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf'
ENGINES = ['chromium', 'firefox', 'webkit']
VIEWPORTS = [(390, 844), (768, 1024), (1440, 900)]
CRAWLERS = {'WhatsApp': 'WhatsApp/2.23.20.0', 'LinkedIn': 'LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)',
            'Facebook': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'}
CATEGORIES = ['story', 'visual', 'animation', 'transition', 'mobile', 'desktop', 'browsers', 'share', 'source', 'performance']
ITEMS = {k: v for k, v in oe.ITEMS.items() if k in IDS + ['chain', 'history', 'interruptions', 'distinct', 'observatory', 'desktopShowpiece', 'fallback']}
ITEMS['fallback'] = (['visual', 'mobile'], 'Blocked model on each of the five cases: labelled still view, hotspot cards still open (production build)')
ITEMS.update({
    'browsers': (['browsers', 'mobile', 'desktop'], 'Chromium, Firefox and WebKit × 390×844, 768×1024, 1440×900 on the production URL: Enter works, hero + five chapters render, five case files reached through the Next chain, no page error, no response ≥ 400, no horizontal overflow'),
    'share': (['share'], 'Homepage + five cases as WhatsApp / LinkedIn / Facebook crawlers fetch them: title, description, canonical, og:image absolute on the production host, card 1200×630 JPEG ≤ 300 KB and reachable without cookies; per-case titles and cards carry that case\'s own story'),
    'discovery': (['share', 'source'], 'Production index: robots.txt allows crawling and lists the sitemap, sitemap.xml lists six URLs, icons load, unknown slug returns 404, security-relevant headers present'),
    'sources': (['source'], 'Case readings trace to the dossiers; share text numbers appear on the page they describe; no DRAFT label left; no forbidden claims'),
    'performance': (['performance', 'mobile', 'desktop'], 'Chain hops on production: phone 390×844 DPR 2 at 4× CPU and desktop 1440×900 ≥ 45 fps, ≤ 10% slow frames; first-load transfer before Enter measured'),
    'clean': (['mobile', 'desktop'], 'Zero page errors, zero responses ≥ 400, no horizontal overflow in both Chromium walkthroughs'),
})


def check(key, ok, detail, shot=None, **extra):
    CHECKS[key] = {'pass': bool(ok), 'detail': detail, 'screenshot': shot, **extra}


def fetch(path_or_url, ua='Mozilla/5.0', method='GET'):
    url = path_or_url if path_or_url.startswith('http') else URL + path_or_url
    req = urllib.request.Request(url, headers={'User-Agent': ua}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


# ---------------------------------------------------------------- browsers
async def engine_smoke(p, engine, w, h):
    tag = f'{engine}-{w}x{h}'
    opts = {'viewport': {'width': w, 'height': h}}
    if w <= 768:
        opts['has_touch'] = True
        if engine != 'firefox':
            opts.update(is_mobile=True, device_scale_factor=2)
    browser = await getattr(p, engine).launch(headless=True, **({'args': GPU} if engine == 'chromium' else {}))
    context = await browser.new_context(**opts)
    page = await context.new_page()
    sink = {'errors': [], 'bad': []}
    oe.watch(page, sink)
    if engine == 'webkit':
        # Playwright's headless WebKit (WPE) crashes the page on <source type="video/mp4"> in the case file (no media backend probe survives).
        # Harness workaround so the rest of WebKit is testable; the crash itself is reported as a finding (see webkitVideoCrash).
        await page.add_init_script("new MutationObserver(ms=>{for(const m of ms)for(const n of m.addedNodes){if(n.nodeType===1){(n.matches&&n.matches('source'))&&n.remove();n.querySelectorAll&&n.querySelectorAll('video source').forEach(x=>x.remove())}}}).observe(document,{childList:true,subtree:true})")
    r = {'tag': tag, 'engine': engine, 'viewport': [w, h], 'chapters': {}, 'cases': []}
    overflows = []
    try:
        await page.goto(URL, wait_until='load')
        await page.locator('.silent-button').click(timeout=60000)
        await page.wait_for_selector('.entry-gate[hidden]', state='attached', timeout=30000)
        await idle(page)
        r['scene'] = await page.locator('.observatory').get_attribute('data-scene')
        r['canvas'] = await page.locator('canvas').count()
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT / f'b-{tag}-hero.png'))
        overflows.append(await oe.overflow(page))
        for slug in IDS:
            await q49.to_chapter(page, slug)
            await page.wait_for_timeout(500)
            r['chapters'][slug] = {'shown': await page.locator('.observatory').get_attribute('data-chapter'),
                                   'strip': await page.locator(oe.STRIPS[slug]).is_visible(), 'copy': await page.locator(f'#{slug} .instrument-copy').is_visible()}
            overflows.append(await oe.overflow(page))
        await q49.to_chapter(page, 'crosscheck')
        await page.locator('[data-open-case=crosscheck]').click()
        await page.wait_for_function("location.pathname==='/work/crosscheck'", timeout=20000)
        await idle(page)
        for n, slug in enumerate(IDS):
            if n:
                await oe.at(page, '.case-next')
                await page.locator('.case-next .case-button').click()
                await page.wait_for_function(f"location.pathname==='/work/{slug}'", timeout=20000)
                await idle(page)
            heading = await page.locator('#case-heading').inner_text()
            await page.wait_for_timeout(600)
            await page.screenshot(path=str(OUT / f'b-{tag}-case-{slug}.png'))
            overflows.append(await oe.overflow(page))
            r['cases'].append({'slug': slug, 'heading': heading, 'ok': heading == NAMES[slug], 'curtain': await page.locator('.curtain').get_attribute('data-state')})
        r['canvasAtEnd'] = await page.locator('canvas').count()
    except Exception as error:  # noqa: BLE001
        traceback.print_exc()
        r['error'] = repr(error)
    r['errors'], r['bad'], r['maxOverflow'] = sink['errors'], sink['bad'], max(overflows, default=0)
    r['ok'] = (not r.get('error') and r.get('canvas') == 1 and r.get('canvasAtEnd') == 1 and len(r['cases']) == 5 and all(c['ok'] and c['curtain'] == 'open' for c in r['cases'])
               and all(c['shown'] == s and c['strip'] and c['copy'] for s, c in r['chapters'].items()) and len(r['chapters']) == 5
               and not [e for e in r['errors'] if 'pageerror' in e.lower()] and not r['bad'] and r['maxOverflow'] <= 1)
    await context.close()
    await browser.close()
    return r


async def smoke_retry(p, engine, w, h):
    """WebKit (Playwright WPE, headless) is unstable here: up to 2 attempts, attempts recorded so a flaky pass is never hidden."""
    tries = []
    for _ in range(2 if engine == 'webkit' else 1):
        r = await engine_smoke(p, engine, w, h)
        tries.append({'ok': r['ok'], 'error': r.get('error')})
        if r['ok']:
            break
    r['attempts'] = tries
    return r


FINDINGS = [{
    'id': 'F1-webkit-video-crash', 'severity': 'needs owner check (iPhone Safari)',
    'what': 'Playwright headless WebKit (WPE, ubuntu24.04 fallback build) crashes the page ("Page crashed") on every case file (direct URL or via the Next chain), on the local build too. '
            'Bisect: with JS disabled it still crashes; removing the <video> markup or only its <source type="video/mp4"> stops it; a bare page with the same <video><source> does not crash. '
            'Without the source the five cases load in WebKit, but even then one of the runs crashes intermittently (see attempts). Chromium and Firefox: no crash.',
    'why_uncertain': 'Cannot tell whether this is the headless WPE build (no working media backend on this Arch host) or something real in real Safari. Real Safari / iPhone was not available to test.',
    'harness': 'WebKit runs strip <source> from <video> via init script so the rest of the case file is exercised; every WebKit result below is with that workaround.',
    'suggested': 'Owner opens a case file on iPhone Safari during the physical phone test. If the case crashes/reloads, add a JS-controlled video (create the <source> only after the user taps play).'}]


# ---------------------------------------------------------------- share + discovery
def meta_of(html):
    tags = {}
    for m in re.finditer(r'<meta\s+([^>]+?)/?>', html, re.I):
        attrs = dict((k.lower(), unescape(v)) for k, v in re.findall(r'([\w:-]+)="([^"]*)"', m.group(1)))
        key = attrs.get('property') or attrs.get('name')
        if key:
            tags[key] = attrs.get('content', '')
    title = re.search(r'<title[^>]*>(.*?)</title>', html, re.S)
    canon = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', html)
    tags['_title'] = unescape(title.group(1)).strip() if title else ''
    tags['_canonical'] = canon.group(1) if canon else ''
    return tags


def share_check():
    pages = {'home': '/'} | {s: f'/work/{s}' for s in IDS}
    rows, cards = {}, {}
    host = URL.split('://', 1)[1]
    for key, path in pages.items():
        row = rows[key] = {'crawlers': {}}
        html_by = {}
        for name, ua in CRAWLERS.items():
            status, headers, body = fetch(path, ua)
            html_by[name] = meta_of(body.decode('utf-8', 'replace'))
            row['crawlers'][name] = status
        t = html_by['WhatsApp']
        row.update(title=t['_title'], description=t.get('og:description', ''), ogTitle=t.get('og:title'), canonical=t['_canonical'], ogUrl=t.get('og:url'),
                   ogImage=t.get('og:image'), twitterCard=t.get('twitter:card'), twitterImage=t.get('twitter:image'), robots=t.get('robots'),
                   sameForAllCrawlers=all(html_by[n].get('og:image') == t.get('og:image') and html_by[n]['_title'] == t['_title'] for n in html_by))
        status, headers, body = fetch(row['ogImage'] or '/og/missing.jpg', CRAWLERS['WhatsApp'])
        img = Image.open(BytesIO(body)) if status == 200 else None
        row['image'] = {'status': status, 'type': headers.get('Content-Type') or headers.get('content-type'), 'bytes': len(body), 'size': list(img.size) if img else None}
        if img:
            cards[key] = img.convert('RGB')
        row['ok'] = (all(s == 200 for s in row['crawlers'].values()) and row['title'] and row['description'] and row['canonical'].startswith(URL) and (row['ogUrl'] or '').startswith(URL)
                     and (row['ogImage'] or '').startswith(URL) and row['image']['status'] == 200 and 'jpeg' in (row['image']['type'] or '') and row['image']['size'] == [1200, 630]
                     and row['image']['bytes'] <= 300_000 and row['twitterCard'] == 'summary_large_image' and row['sameForAllCrawlers'] and 'noindex' not in (row['robots'] or ''))
    titles = [rows[k]['title'] for k in rows]
    hashes = {k: hash(c.tobytes()) for k, c in cards.items()}
    distinct = len(set(titles)) == 6 and len(set(hashes.values())) == 6 and len({rows[k]['description'] for k in rows}) == 6
    share_previews(rows, cards, host)
    check('share', all(r['ok'] for r in rows.values()) and distinct,
          f"host {host}; six pages × three crawlers (WhatsApp, LinkedIn, Facebook) all 200 with identical tags; titles distinct {distinct}: "
          + ' | '.join(f"{k}: '{r['title']}' — '{r['description'][:110]}' card {r['image']['size']} {r['image']['bytes']} B {r['image']['type']} ok={r['ok']}" for k, r in rows.items()),
          'share-previews.jpg', rows=rows)
    return rows


def share_previews(rows, cards, host):
    """Draw each page as a chat / LinkedIn link preview (card image, title, description, domain) so the owner sees what a share looks like."""
    fb, ft, fs = ImageFont.truetype(FONT_B, 17), ImageFont.truetype(FONT, 14), ImageFont.truetype(FONT, 12)
    W, cardW = 540, 540
    sheet = Image.new('RGB', (W * 3, 2 * 420), (11, 16, 32))
    for i, key in enumerate(['home'] + IDS):
        x, y = (i % 3) * W, (i // 3) * 420
        d = ImageDraw.Draw(sheet)
        d.rectangle([x + 8, y + 8, x + W - 8, y + 412], fill=(30, 38, 58), outline=(60, 72, 100))
        if key in cards:
            c = cards[key].resize((cardW - 16, int((cardW - 16) * 630 / 1200)))
            sheet.paste(c, (x + 8, y + 8))
            top = y + 8 + c.size[1] + 8
        else:
            top = y + 20
        r = rows[key]
        d.text((x + 18, top), host, font=fs, fill=(150, 165, 190))
        d.text((x + 18, top + 18), (r['ogTitle'] or r['title'])[:58], font=fb, fill=(245, 245, 250))
        words, line, ly = r['description'].split(), '', top + 44
        for wd in words:
            if d.textlength(line + ' ' + wd, font=ft) > W - 44:
                d.text((x + 18, ly), line, font=ft, fill=(200, 210, 225))
                line, ly = wd, ly + 18
            else:
                line = (line + ' ' + wd).strip()
        d.text((x + 18, ly), line, font=ft, fill=(200, 210, 225))
        d.text((x + 18, y + 392), f'{key} · link preview drawn from the tags above', font=fs, fill=(242, 165, 65))
    sheet.save(OUT / 'share-previews.jpg', quality=84)


def discovery_check():
    out = {}
    s, h, b = fetch('/robots.txt')
    robots = b.decode()
    out['robots'] = {'status': s, 'allows': bool(re.search(r'^Allow:\s*/', robots, re.M)) and not re.search(r'^Disallow:\s*/\s*$', robots, re.M), 'sitemap': f'{URL}/sitemap.xml' in robots}
    s, h, b = fetch('/sitemap.xml')
    locs = re.findall(r'<loc>([^<]+)</loc>', b.decode())
    out['sitemap'] = {'status': s, 'urls': locs, 'ok': len(locs) == 6 and all(l.startswith(URL) for l in locs)}
    out['icons'] = {p: fetch(p)[0] for p in ('/icon.svg', '/apple-icon.png', '/favicon.ico')}
    out['unknownSlug'] = fetch('/work/does-not-exist')[0]
    s, h, _ = fetch('/')
    hl = {k.lower(): v for k, v in h.items()}
    out['headers'] = {k: hl.get(k) for k in ('strict-transport-security', 'x-content-type-options', 'cache-control', 'content-type')}
    out['assets'] = {p: fetch(p, method='HEAD')[0] for p in ('/models/ambient.glb', '/models/crosscheck.glb', '/videos/crosscheck-explainer.mp4', '/fonts/', '/draco/draco_decoder.wasm') if not p.endswith('/')}
    ok = (out['robots']['status'] == 200 and out['robots']['allows'] and out['robots']['sitemap'] and out['sitemap']['ok'] and all(v == 200 for v in out['icons'].values())
          and out['unknownSlug'] == 404 and out['headers']['strict-transport-security'] and all(v == 200 for v in out['assets'].values()))
    check('discovery', ok, json.dumps(out, ensure_ascii=False), None, data=out)
    return out


async def transfer_before_enter(browser):
    """Bytes fetched before Enter becomes usable (production, cache off) — for the record, no threshold beyond Development's 787 KB ceiling ×1.25."""
    context = await browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    sizes = []
    page.on('response', lambda r: sizes.append(r))
    await page.goto(URL, wait_until='load')
    await page.wait_for_function("!document.querySelector('.silent-button')?.disabled", timeout=60000)
    total = 0
    for r in sizes:
        try:
            total += len(await r.body())
        except Exception:  # noqa: BLE001
            pass
    await context.close()
    return total


def sources_check(m, share_rows):
    oe.CHECKS.clear()
    oe.sources_check(m)
    base = oe.CHECKS['sources']
    texts = {'home': m.get('texts', [''])[0]} | {s: t for s, t in zip(IDS, m.get('texts', [])[1:])}
    missing = {}
    for key, row in share_rows.items():
        for num in re.findall(r'\d[\d,]*', row['description'] + ' ' + row['title']):
            if num not in texts.get(key, '') and not (key != 'home' and num in texts.get('home', '')):
                missing.setdefault(key, []).append(num)
    check('sources', base['pass'] and not missing, base['detail'] + f'; share-text numbers not found on their page: {missing or "none"}')


def flush_oe():
    for k, v in oe.CHECKS.items():
        CHECKS.setdefault(k, v)


async def run():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    oe.RAW.mkdir(parents=True)
    share_rows, disc = share_check(), discovery_check()
    smoke = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        mobile = await oe.walk_device(browser, False)
        desktop = await oe.walk_device(browser, True)
        im = await oe.interruptions(browser, False)
        idd = await oe.interruptions(browser, True)
        fb = await oe.fallback(browser)
        fps = {'phone 4× CPU': await oe.chain_fps(browser, False), 'desktop': await oe.chain_fps(browser, True)}
        texts, drafts = await oe.page_texts(browser)
        transfer = await transfer_before_enter(browser)
        await browser.close()
        for engine in ENGINES:
            for w, h in VIEWPORTS:
                smoke.append(await smoke_retry(p, engine, w, h))
                print('browser', smoke[-1]['tag'], 'ok' if smoke[-1]['ok'] else 'FAIL', smoke[-1].get('error') or '')
    m, d = mobile[2], desktop[2]
    m['texts'], m['drafts'] = texts, drafts
    errors = mobile[1].sink['errors'] + desktop[1].sink['errors']
    bad = mobile[1].sink['bad'] + desktop[1].sink['bad']
    overflow = mobile[1].overflows + desktop[1].overflows
    check('clean', not errors and not bad and max(overflow, default=0) <= 1 and not oe.META['errors'],
          f"errors {errors}; ≥400 {bad}; max overflow {max(overflow, default=0)} px over {len(overflow)} shots; script errors {oe.META['errors'] or 'none'}")
    per = {}
    try:
        oe.CHECKS.clear()
        # verdicts() also reads the local Development ledger for viewport/perf items; those keys are dropped below (production has no ledger).
        try:
            per, _ = oe.verdicts(m, d, im, idd, fb, {'phone 4× CPU': fps['phone 4× CPU'], 'desktop': fps['desktop']})
        except Exception:  # noqa: BLE001
            traceback.print_exc()
        for key in IDS + ['chain', 'history', 'interruptions', 'distinct', 'observatory', 'desktopShowpiece', 'fallback']:
            if key in oe.CHECKS:
                CHECKS[key] = oe.CHECKS[key]
        sources_check(m, share_rows)
    except Exception as error:  # noqa: BLE001
        traceback.print_exc()
        META['errors']['verdicts'] = repr(error)
    # Cross-engine.
    bad_runs = [s['tag'] for s in smoke if not s['ok']]
    scenes = {s['tag']: s.get('scene') for s in smoke}
    check('browsers', not bad_runs and len(smoke) == 9,
          f"{len(smoke)} runs; failed {bad_runs or 'none'}; scene state per run {scenes}; overflow max {max((s['maxOverflow'] for s in smoke), default=None)} px; "
          f"page errors {sum(len(s['errors']) for s in smoke)}; ≥400 {sum(len(s['bad']) for s in smoke)}", 'i14-browsers.png', runs=smoke)
    # Performance.
    chain_meas = {dev: {k: v for k, v in r.items() if isinstance(v, dict)} for dev, r in fps.items()}
    perf_ok = all(v['fps'] >= 45 and v['slowPct'] <= 10 for r in chain_meas.values() for v in r.values()) and all(len(r) == 6 for r in chain_meas.values())
    check('performance', perf_ok,
          f"first-load transfer before Enter (phone, cache off): {transfer:,} B; " + '; '.join(f"{dev}: " + ', '.join(f"{k} {v['fps']} fps ({v['slowPct']}% slow)" for k, v in r.items()) for dev, r in chain_meas.items()),
          None, data={'chain': chain_meas, 'transferBeforeEnterBytes': transfer})
    videos = []
    try:
        videos = oe.films(mobile, desktop)
    except Exception as error:  # noqa: BLE001
        traceback.print_exc()
        META['errors']['films'] = repr(error)
    shutil.rmtree(oe.RAW, ignore_errors=True)
    oe.sheets()
    (OUT / 'i12-viewports.png').unlink(missing_ok=True)
    sheet_browsers(smoke)
    categories = {c: {'pass': all(CHECKS.get(k, {}).get('pass') for k, (cats, _) in ITEMS.items() if c in cats), 'items': [k for k, (cats, _) in ITEMS.items() if c in cats]} for c in CATEGORIES}
    passed = all(CHECKS.get(k, {}).get('pass') for k in ITEMS)
    report = {
        'status': 'passed' if passed else 'failed', 'phase': 'Phase 8 — Launch ready', 'stage': 'Testing (full round, production URL)',
        'finishedAt': datetime.now(timezone.utc).isoformat(), 'url': URL,
        'scope': 'Production URL (Q40). Chromium GPU (ANGLE) walkthroughs 390×844 DPR 2 touch + 1440×900 mouse wheel, recorded; Chromium/Firefox/WebKit × 390/768/1440 smoke; '
                 'share tags as three crawlers; blocked model; chain fps phone 4× CPU + desktop. Physical phone (scroll feel, fps, sound, 4G) = owner test.',
        'categories': categories, 'items': {k: {'label': label, 'categories': cats, **CHECKS.get(k, {'pass': False, 'detail': 'not executed'})} for k, (cats, label) in ITEMS.items()},
        'perProjectDevice': per,
        'measurements': {'mobile': {k: v for k, v in m.items() if k != 'texts'}, 'desktop': d, 'interruptions': {'phone': im, 'desktop': idd}, 'fallback': fb, 'chainFps': fps,
                         'marks': {'mobile': mobile[1].marks, 'desktop': desktop[1].marks}, 'discovery': disc},
        'videos': videos, 'contactSheets': ['contact-sheet-mobile.jpg', 'contact-sheet-desktop.jpg', 'share-previews.jpg'], 'errors': (oe.META['errors'] | META['errors']) or None, 'findings': FINDINGS,
    }
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + '\n')
    for key, item in report['items'].items():
        print(f"{'PASS' if item['pass'] else 'FAIL'} {key}: {item['detail'][:500]}")
    print('categories:', {c: v['pass'] for c, v in categories.items()})
    print('videos:', videos)
    return passed


def sheet_browsers(smoke):
    T = (300, 360)
    grid = Image.new('RGB', (T[0] * 3, T[1] * 3), 'black')
    for r, engine in enumerate(ENGINES):
        for c, (w, h) in enumerate(VIEWPORTS):
            src = OUT / f'b-{engine}-{w}x{h}-hero.png'
            if src.exists():
                grid.paste(oe.tile(src, f'{engine} {w}×{h}', T), (c * T[0], r * T[1]))
    grid.save(OUT / 'i14-browsers.png')
    labels = [(f'b-{e}-{w}x{h}-case-crosscheck.png', f'{e} {w}×{h} · CrossCheck') for e in ENGINES for (w, h) in VIEWPORTS]
    sheet = Image.new('RGB', (T[0] * 3, T[1] * 3), 'black')
    for i, (name, label) in enumerate(labels):
        if (OUT / name).exists():
            sheet.paste(oe.tile(OUT / name, label, T), ((i % 3) * T[0], (i // 3) * T[1]))
    sheet.save(OUT / 'browsers-case-sheet.jpg', quality=82)




async def redo_browsers():
    """Re-run only the 9 cross-engine runs into the existing pack (after a harness change); the other items are kept."""
    path = OUT / 'evidence.json'
    report = json.loads(path.read_text())
    smoke = []
    async with async_playwright() as p:
        for engine in ENGINES:
            for w, h in VIEWPORTS:
                smoke.append(await smoke_retry(p, engine, w, h))
                print('browser', smoke[-1]['tag'], 'ok' if smoke[-1]['ok'] else 'FAIL', [a['ok'] for a in smoke[-1]['attempts']])
    bad_runs = [s['tag'] for s in smoke if not s['ok']]
    flaky = [s['tag'] for s in smoke if s['ok'] and len(s['attempts']) > 1]
    check('browsers', not bad_runs and len(smoke) == 9,
          f"{len(smoke)} runs; failed {bad_runs or 'none'}; passed only on the 2nd attempt {flaky or 'none'}; WebKit with the <video> <source> workaround (finding F1: without it every case file crashes headless WebKit); "
          f"scene state {[s.get('scene') for s in smoke]}; overflow max {max(s['maxOverflow'] for s in smoke)} px; page errors {sum(len(s['errors']) for s in smoke)}; ≥400 {sum(len(s['bad']) for s in smoke)}",
          'i14-browsers.png', runs=smoke)
    report['items']['browsers'] = {'label': ITEMS['browsers'][1], 'categories': ITEMS['browsers'][0], **CHECKS['browsers']}
    report['findings'] = FINDINGS
    report['categories'] = {c: {'pass': all(report['items'][k]['pass'] for k, (cats, _) in ITEMS.items() if c in cats), 'items': [k for k, (cats, _) in ITEMS.items() if c in cats]} for c in CATEGORIES}
    report['status'] = 'passed' if all(report['items'][k]['pass'] for k in ITEMS) else 'failed'
    sheet_browsers(smoke)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + '\n')
    print(report['status'], {c: v['pass'] for c, v in report['categories'].items()})
    print(CHECKS['browsers']['detail'][:600])
    return report['status'] == 'passed'


if __name__ == '__main__':
    sys.exit(0 if asyncio.run(redo_browsers() if '--redo-browsers' in sys.argv else run()) else 1)
