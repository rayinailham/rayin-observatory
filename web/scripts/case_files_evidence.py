"""Phase 5 Testing evidence: all five case files and the chained Next instrument.
Records 390x844 MP4 walkthrough of the full chain (homepage -> CrossCheck -> SurgeLine ->
DriftWatch -> DueWatch -> BrandWall -> CrossCheck wrap -> Return -> history -> SurgeLine return),
captures one PNG per checklist item, labeled contact sheet, 360x740 / 430x932 viewport sheet,
and writes evidence.json with pass/fail per item.

Target: local production preview (OBSERVATORY_URL default http://127.0.0.1:8767).
Chromium mobile emulation only; no physical-device fps claim.
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
from verify_case import enter, idle, scroll_to  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/case-files/evidence'
DOSSIERS = Path('/home/rayin/Projects/Testing/portfolio')
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767').rstrip('/')
W, H = 390, 844
GPU = ['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist']
SECTIONS = ['Brief', 'The instrument', 'How it works', 'Readings', 'Tools used', 'Demo video', 'Next instrument']
FORBIDDEN = ['Amazon', 'Rayin Ailham']

CASES = [
    {
        'id': 'crosscheck', 'name': 'CrossCheck', 'draft': False, 'duration': 126.9,
        'cards': ['Browser matrix', 'Access checks', 'End-to-end flows'],
        'countValues': ['1,080', '216', '18', '12'],
        'displayReadings': ['1,080', '216', '18', '12/12'],
        'expectedTools': 15,
    },
    {
        'id': 'surgeline', 'name': 'SurgeLine', 'draft': False, 'duration': 115.2,
        'cards': ['Work list', 'Parallel workers', 'Confirmation proof'],
        'countValues': ['48,273', '0', '7', '81,915'],
        'displayReadings': ['48,273', '0', '7/7', '81,915'],
        'expectedTools': 12,
    },
    {
        'id': 'driftwatch', 'name': 'DriftWatch', 'draft': False, 'duration': 118.2,
        'cards': ['Alarms', 'Change detection', 'Daily collection'],
        'countValues': ['11', '1,323', '12', '1'],
        'displayReadings': ['11/11', '1,323', '12/12', '1'],
        'expectedTools': 13,
    },
    {
        'id': 'duewatch', 'name': 'DueWatch', 'draft': False, 'duration': 102.5,
        'cards': ['Daily expiry check', 'Safe message triage', '24-hour follow-up'],
        'countValues': ['200', '7', '6', '12'],
        'displayReadings': ['200', '7/7', '6/6', '12'],
        'expectedTools': 11,
    },
    {
        'id': 'brandwall', 'name': 'BrandWall', 'draft': False, 'duration': 125.0,
        'cards': ['Test matrix', 'Measurement', 'Fix rules'],
        'countValues': ['300', '18', '11', '0'],
        'displayReadings': ['300', '18', '11', '0/300'],
        'expectedTools': 13,
    },
]

ITEMS = {
    'crosscheck': 'CrossCheck case file (/work/crosscheck): approved copy (no DRAFT), updated Next block, readings (1,080 / 216 / 18 / 12/12), demo video (126.9 s)',
    'surgeline': 'SurgeLine case file (/work/surgeline): brief, 3 dish feed hotspots, flow, readings (48,273 / 0 / 7 / 81,915), tools, demo video (115.2 s), approved copy (no DRAFT)',
    'driftwatch': 'DriftWatch case file (/work/driftwatch): brief, 3 needle/bed/roller hotspots, flow, readings (11 / 1,323 / 12 / 1), tools, demo video (118.2 s), approved copy (no DRAFT)',
    'duewatch': 'DueWatch case file (/work/duewatch): brief, 3 orbiting planet hotspots, flow, readings (200 / 7 / 6 / 12), tools, demo video (102.5 s), approved copy (no DRAFT)',
    'brandwall': 'BrandWall case file (/work/brandwall): brief, 3 collimator/prism/spectrum hotspots, flow, readings (300 / 18 / 11 / 0), tools, demo video (125.0 s), approved copy (no DRAFT)',
    'nextChain': 'Next instrument chain: CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall → CrossCheck (full cycle with retreat, sweep, and flight in)',
    'flightIn': 'Open case file: homepage text fades, scroll locked during flight, camera flies into instrument, arrival focuses #case-heading',
    'returnFlight': 'Return: camera flies back, homepage scroll position and focus restored to case chapter',
    'hotspots': 'Hotspots on all 5 instruments (15 cards, tap >= 44 px) open within viewport; leader lines project from 3D GLB nodes to hotspots every frame',
    'readings': 'Readings count up like instrument display across all 5 cases; limits disclosure opens with caveats',
    'tools': 'Tools used: all tools link back to homepage Skills (/#skills) and trace to respective dossier §5',
    'videos': 'Demo videos: lazy loaded on play, H.264, 0 audio streams, correct durations within 1 s, posters present',
    'history': 'Browser Back / Forward move between cases and between homepage and cases without broken state',
    'fallback': 'Model blocked: labeled still view with matching fallback PNG, component cards and return work',
    'viewports': 'All 5 case flows pass at 390×844, 360×740, and 430×932 without horizontal overflow',
    'copy': 'Copy: all 5 cases approved (no DRAFT label); English language; all multi-digit numbers in dossiers; no forbidden terms',
    'clean': 'One persistent Canvas across all 5 cases and navigations, zero page errors, zero responses ≥400, no horizontal overflow',
}

FINDINGS = {
    'duewatch': 'Owner decision needed: DueWatch explainer video includes caption "Seven days in a row. Nobody had to remember." over simulated business dates (flagged in self-review §7 finding 4). The case file notes this under the video. Alternatives: accept with note, drop video, or re-cut in DueWatch project.',
}


def font(size):
    for path in ['/usr/share/fonts/TTF/DejaVuSans.ttf', '/usr/share/fonts/dejavu/DejaVuSans.ttf']:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def tile(source, label, size=(W, H)):
    image = (Image.open(source) if isinstance(source, (Path, str)) else Image.open(io.BytesIO(source))).convert('RGB').resize(size)
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
    for _ in range(30):
        await page.wait_for_timeout(150)
        current = await page.evaluate('Math.round(scrollY)')
        if current == last:
            return
        last = current


async def glide(page, target):
    """Wheel input with Lenis smoothing visible on video, then exact final position."""
    max_scroll = await page.evaluate('document.documentElement.scrollHeight-innerHeight')
    target = max(0, min(round(target), max_scroll))
    for _ in range(250):
        current = await page.evaluate('scrollY')
        if current >= target - 160:
            break
        await page.mouse.wheel(0, 160)
        await page.wait_for_timeout(40)
    await settle(page)
    await page.evaluate('(y)=>scrollTo(0,y)', target)
    await page.wait_for_timeout(400)


async def top(page, selector):
    return await page.locator(selector).first.evaluate('(e)=>e.getBoundingClientRect().top+scrollY')


async def overflow(page):
    return await page.evaluate('document.documentElement.scrollWidth>innerWidth')


async def flight(page, click_action, url):
    """Capture start / mid / end frames of a camera flight triggered by click_action."""
    await page.evaluate('window.__flight=[]')
    before = await page.evaluate('scrollY')
    start = await page.screenshot()
    await click_action()
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


async def main_flow(browser, checks):
    context = await browser.new_context(
        viewport={'width': W, 'height': H},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
        record_video_dir=str(OUT / 'raw'),
        record_video_size={'width': W, 'height': H}
    )
    page = await context.new_page()
    errors, bad, videos = [], [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('response', lambda r: bad.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
    page.on('request', lambda r: videos.append(r.url) if '/videos/' in r.url else None)
    overflows = []

    # 1. Gate entry
    await enter(page)
    await page.evaluate("""
        window.__canvas = document.querySelector('canvas');
        new MutationObserver(() => window.__flight && window.__flight.push(document.querySelector('.observatory').dataset.flight))
          .observe(document.querySelector('.observatory'), {attributes: true, attributeFilter: ['data-flight']});
    """)
    await page.screenshot(path=str(OUT / '01-gate-entered.png'))

    # Scroll to first chapter (CrossCheck)
    await glide(page, await top(page, '#crosscheck') + 280)
    home_y = await page.evaluate('scrollY')
    await page.screenshot(path=str(OUT / '02-crosscheck-chapter.png'))

    # Flight into CrossCheck
    f = await flight(page, lambda: page.locator('[data-open-case=crosscheck]').click(), f'{URL}/work/crosscheck')
    (OUT / '03a-flight-start.png').write_bytes(f['start'])
    (OUT / '03b-flight-mid.png').write_bytes(f['mid'])
    (OUT / '03c-flight-end.png').write_bytes(f['end'])
    row([tile(f['start'], 'Tap Open case file'), tile(f['mid'], 'Flying in · text fades'), tile(f['end'], 'CrossCheck arrived')], OUT / '03-flight-in.png')
    moved = difference(f['start'], f['end'])
    focus = await page.evaluate("document.activeElement && document.activeElement.id")
    same_canvas = await page.evaluate("window.__canvas === document.querySelector('canvas')")
    checks['flightIn'] = {
        'pass': 'moving' in f['states'] and f['locked'] and f['midOpacity'] < 1 and moved > 3 and same_canvas and focus == 'case-heading' and await page.evaluate('scrollY') < 2,
        'detail': f"flight states {f['states']}, scroll locked={f['locked']}, homepage opacity mid-flight {f['midOpacity']}, frame change {moved}, same Canvas={same_canvas}, focus #{focus}",
        'screenshot': '03-flight-in.png'
    }

    # Test Return flight back to homepage (preserves scroll & focus)
    ret = await flight(page, lambda: page.locator('.case-brief .case-back').click(), URL + '/')
    (OUT / '05a-return-start.png').write_bytes(ret['start'])
    (OUT / '05b-return-mid.png').write_bytes(ret['mid'])
    (OUT / '05c-return-end.png').write_bytes(ret['end'])
    row([tile(ret['start'], 'Tap Return to instrument'), tile(ret['mid'], 'Flying back · case fades'), tile(ret['end'], 'Restored to CrossCheck')], OUT / '05-return-flight.png')
    back_y = await page.evaluate('scrollY')
    focus_cta = await page.locator('[data-open-case=crosscheck]').evaluate('(e)=>e===document.activeElement')
    same_canvas_ret = await page.evaluate("window.__canvas === document.querySelector('canvas')")
    checks['returnFlight'] = {
        'pass': 'moving' in ret['states'] and ret['locked'] and abs(back_y - home_y) < 2 and focus_cta and same_canvas_ret,
        'detail': f"flight states {ret['states']}, scroll locked={ret['locked']}, scrollY {back_y} vs origin {home_y}, focus on Open case file={focus_cta}, same Canvas={same_canvas_ret}",
        'screenshot': '05-return-flight.png'
    }
    await page.screenshot(path=str(OUT / '06-returned-crosscheck.png'))

    # Re-open CrossCheck to start the full 5-case chain
    await page.locator('[data-open-case=crosscheck]').click()
    await page.wait_for_url(f'{URL}/work/crosscheck')
    await idle(page)

    # Inspect all five cases in chain sequence
    chain_records = []
    hotspot_results = {}
    readings_results = {}
    tools_results = {}
    video_results = {}

    for idx, case in enumerate(CASES):
        slug = case['id']
        name = case['name']
        print(f"Inspecting case in chain: {name} (/work/{slug})", flush=True)

        # Ensure page matches case
        await page.wait_for_function('(n)=>document.getElementById("case-heading")?.textContent===n', arg=name)
        overflows.append(await overflow(page))
        canvases = await page.locator('canvas').count()
        assert canvases == 1

        # Brief screenshot
        await page.screenshot(path=str(OUT / f'case-{slug}-brief.png'))

        # Template check: 7 sections in order
        text = await page.locator('.case-page').text_content()
        positions = [text.find(s) for s in SECTIONS]
        template_ok = all(p >= 0 for p in positions) and positions == sorted(positions)

        # Hotspots
        await glide(page, await top(page, '#case-instrument'))
        card_checks = []
        for i, card_title in enumerate(case['cards']):
            btn = page.locator(f'.hotspot-{i}')
            box = await btn.bounding_box()
            await btn.click()
            await page.wait_for_function("(i)=>Array.from(document.querySelectorAll('.instrument-hotspot')).every((e,n)=>getComputedStyle(e).backgroundColor===(n===i?'rgb(242, 165, 65)':'rgba(11, 16, 32, 0.93)'))", arg=i)
            await page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
            card_box = await page.locator('#component-card').bounding_box()
            shown_title = await page.locator('#component-card h3').inner_text()
            card_checks.append({
                'title': shown_title,
                'tap': [round(box['width']), round(box['height'])],
                'expanded': await btn.get_attribute('aria-expanded'),
                'inView': card_box['y'] + card_box['height'] <= H and card_box['y'] >= 0,
            })
            if idx == 0 or i == 0:
                await page.screenshot(path=str(OUT / f'case-{slug}-hotspot-{i+1}.png'))
            await page.wait_for_timeout(300)

        # Project leaders check
        leaders = await page.locator('[data-hotspot-line]').evaluate_all("els=>els.map(e=>[Math.round(+e.getAttribute('x2')),Math.round(+e.getAttribute('y2'))])")
        leaders_ok = len(leaders) == 3 and all(0 < x < W and 80 < y < H for x, y in leaders)

        await page.get_by_role('button', name='Close component card').click()
        closed = await page.locator('.instrument-hotspot[aria-expanded=true]').count() == 0
        hotspots_ok = [c['title'] for c in card_checks] == case['cards'] and all(min(c['tap']) >= 44 and c['expanded'] == 'true' and c['inView'] for c in card_checks) and leaders_ok and closed
        hotspot_results[slug] = {
            'pass': hotspots_ok,
            'detail': f"{slug}: cards {[c['title'] for c in card_checks]}, leaders {leaders}, close button closes={closed}",
            'screenshot': f'case-{slug}-hotspot-1.png'
        }

        # Signal flow
        await glide(page, await top(page, '#flow-heading') - 110)
        steps = await page.locator('.signal-flow li h3').all_inner_texts()
        anim = await page.locator('.signal-flow li').first.evaluate("e=>getComputedStyle(e,'::after').animationName")
        flow_ok = len(steps) == 4 and anim == 'case-signal'

        # Readings
        await glide(page, await top(page, '#readings-heading') - 110)
        for i, val in enumerate(case['countValues']):
            await page.locator('.case-reading').nth(i).scroll_into_view_if_needed()
            await page.wait_for_function('(a)=>document.querySelectorAll("[data-count]")[a.i].textContent===a.v', arg={'i': i, 'v': val})
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#readings-heading') - 110)
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT / f'case-{slug}-readings.png'))
        shown_readings = await page.locator('.case-reading strong').evaluate_all('els=>els.map(e=>e.textContent)')
        await page.locator('.case-limits summary').click()
        limits_open = await page.locator('.case-limits').get_attribute('open') is not None
        readings_ok = shown_readings == case['displayReadings'] and limits_open
        readings_results[slug] = {
            'pass': readings_ok,
            'detail': f"{slug}: shown {shown_readings} vs expected {case['displayReadings']}, limits={limits_open}",
            'screenshot': f'case-{slug}-readings.png'
        }

        # Tools used
        await glide(page, await top(page, '#tools-heading') - 110)
        tools = await page.locator('.case-tools a').evaluate_all("els=>els.map(e=>[e.textContent.replace('↗','').trim(),e.getAttribute('href')])")
        tools_ok = len(tools) == case['expectedTools'] and all(href == '/#skills' for _, href in tools)
        tools_results[slug] = {
            'pass': tools_ok,
            'detail': f"{slug}: {len(tools)} tools (expected {case['expectedTools']}), all link to /#skills",
        }

        # Demo video
        await glide(page, await top(page, '#demo-heading') - 110)
        before_video_reqs = list(videos)
        video_el = page.locator('.case-video')
        poster = await video_el.get_attribute('poster')
        poster_ok = poster == f"/images/{slug}-demo-poster.jpg"
        await video_el.evaluate('(v)=>v.play()')
        await page.wait_for_function('document.querySelector(".case-video").currentTime>.3', timeout=20000)
        v_meta = await video_el.evaluate('(v)=>({d:v.duration,t:v.currentTime,muted:v.muted,w:v.videoWidth,h:v.videoHeight})')
        await video_el.evaluate('(v)=>v.pause()')
        after_video_reqs = list(videos)
        duration_ok = abs(v_meta['d'] - case['duration']) < 1.0
        video_ok = poster_ok and duration_ok and v_meta['muted'] and v_meta['w'] == 1920 and len(after_video_reqs) > len(before_video_reqs)
        video_results[slug] = {
            'pass': video_ok,
            'detail': f"{slug}: duration {v_meta['d']:.2f}s (exp {case['duration']}s), {v_meta['w']}x{v_meta['h']}, muted={v_meta['muted']}, poster={poster}",
            'screenshot': f'case-{slug}-brief.png'
        }

        # Individual case item verification
        draft_label_count = await page.locator('.case-page .draft-label').count()
        expected_draft = 1 if case['draft'] else 0
        draft_ok = draft_label_count == expected_draft
        case_item_pass = template_ok and hotspots_ok and flow_ok and readings_ok and tools_ok and video_ok and draft_ok
        checks[slug] = {
            'pass': case_item_pass,
            'detail': f"template={template_ok}, hotspots={hotspots_ok}, flow={flow_ok}, readings={readings_ok}, tools={tools_ok}, video={video_ok}, draft_label({draft_label_count})={draft_ok}",
            'screenshot': f'case-{slug}-brief.png'
        }
        if slug in FINDINGS:
            checks[slug]['finding'] = FINDINGS[slug]

        # Next instrument section
        await glide(page, await top(page, '#next-heading') - 110)
        next_case = CASES[(idx + 1) % 5]
        next_title = await page.locator('.case-next h2').inner_text()
        assert next_title == next_case['name']

        # Trigger Next instrument chain transition
        next_btn = page.locator('.case-next .case-button')
        next_flight = await flight(page, lambda: next_btn.click(), f"{URL}/work/{next_case['id']}")
        chain_records.append({
            'from': slug,
            'to': next_case['id'],
            'flight_states': next_flight['states'],
            'locked': next_flight['locked']
        })
        if idx == 0:
            (OUT / '04-chain-sweep-surgeline.png').write_bytes(next_flight['mid'])

    # All 5 cases chained through, wrapped around to CrossCheck!
    all_chains_ok = len(chain_records) == 5 and all('moving' in r['flight_states'] and r['locked'] for r in chain_records)
    checks['nextChain'] = {
        'pass': all_chains_ok,
        'detail': f"Chained 5 transitions: {' → '.join([r['from'] for r in chain_records])} → {chain_records[-1]['to']}; all locked={all(r['locked'] for r in chain_records)}",
        'screenshot': '04-chain-sweep-surgeline.png'
    }

    # Consolidated hotspot check
    all_hotspots_ok = all(r['pass'] for r in hotspot_results.values())
    checks['hotspots'] = {
        'pass': all_hotspots_ok,
        'detail': f"All 5 instruments (15 cards): " + "; ".join([f"{k}: ok" if v['pass'] else f"{k}: fail" for k, v in hotspot_results.items()]),
        'screenshot': 'case-crosscheck-hotspot-1.png'
    }

    # Consolidated readings check
    all_readings_ok = all(r['pass'] for r in readings_results.values())
    checks['readings'] = {
        'pass': all_readings_ok,
        'detail': f"All 5 instruments counted up to verified values: " + "; ".join([f"{k}: ok" if v['pass'] else f"{k}: fail" for k, v in readings_results.items()]),
        'screenshot': 'case-crosscheck-readings.png'
    }

    # Consolidated tools check
    all_tools_ok = all(r['pass'] for r in tools_results.values())
    checks['tools'] = {
        'pass': all_tools_ok,
        'detail': f"All 5 cases tools point to /#skills: " + "; ".join([f"{k}: {v['pass']}" for k, v in tools_results.items()]),
        'screenshot': 'case-crosscheck-brief.png'
    }

    # Consolidated videos check
    all_videos_ok = all(r['pass'] for r in video_results.values())
    checks['videos'] = {
        'pass': all_videos_ok,
        'detail': f"All 5 explainer videos load on play, 0 audio, correct duration: " + "; ".join([f"{k}: ok" if v['pass'] else f"{k}: fail" for k, v in video_results.items()]),
        'screenshot': 'case-crosscheck-brief.png'
    }

    # Browser Back / Forward inside the chain
    await page.go_back()
    await page.wait_for_url(f'{URL}/work/brandwall')
    await idle(page)
    back_brandwall_ok = await page.locator('#case-heading').inner_text() == 'BrandWall'
    await page.go_forward()
    await page.wait_for_url(f'{URL}/work/crosscheck')
    await idle(page)
    fwd_heading = await page.locator('#case-heading').is_visible()
    checks['history'] = {
        'pass': back_brandwall_ok and fwd_heading,
        'detail': f"Back -> BrandWall ({back_brandwall_ok}); Forward -> CrossCheck ({fwd_heading})",
        'screenshot': '06-returned-crosscheck.png'
    }

    # Chain to SurgeLine, then Return lands on SurgeLine chapter
    await glide(page, await top(page, '#next-heading') - 110)
    await page.locator('.case-next .case-button').click()
    await page.wait_for_url(f'{URL}/work/surgeline')
    await idle(page)
    await page.locator('.case-brief .case-back').click()
    await page.wait_for_url(URL + '/')
    await idle(page)
    surgeline_top = await page.locator('#surgeline').evaluate('(e)=>Math.round(e.getBoundingClientRect().top)')
    same_canvas_surge = await page.evaluate("window.__canvas === document.querySelector('canvas')")
    await page.screenshot(path=str(OUT / '07-returned-surgeline.png'))
    assert abs(surgeline_top) < 2 and same_canvas_surge

    # Copy and numbers verification across all 5 dossiers
    dossier_traces = {}
    forbidden_found = []
    for case in CASES:
        slug = case['id']
        dossier_path = DOSSIERS / f"CAPABILITY_{slug.upper()}.md"
        dossier_text = dossier_path.read_text()
        # Direct visit to read entire text
        await page.goto(f'{URL}/work/{slug}')
        await page.locator('.silent-button').click(timeout=30000)
        await idle(page)
        case_text = await page.locator('.case-page').text_content()
        for word in FORBIDDEN:
            if word.lower() in case_text.lower():
                forbidden_found.append(f"{slug}:{word}")
        # Trace numbers
        for num in case['countValues']:
            if len(num) > 1:
                found = bool(re.search(rf'(?<![\d,]){re.escape(num)}(?![\d,])', dossier_text))
                dossier_traces[f"{slug}:{num}"] = found

    all_traces_ok = all(dossier_traces.values()) and not forbidden_found
    checks['copy'] = {
        'pass': all_traces_ok,
        'detail': f"All readings traced to dossiers ({len(dossier_traces)} checks passed); forbidden terms: {forbidden_found or 'none'}",
        'screenshot': 'case-crosscheck-brief.png'
    }

    # Clean check
    canvases_final = await page.locator('canvas').count()
    checks['clean'] = {
        'pass': canvases_final == 1 and not errors and not bad and not any(overflows),
        'detail': f"Canvas={canvases_final}, page errors={len(errors)}, responses >= 400={len(bad)}, horizontal overflow={any(overflows)}",
        'screenshot': '01-gate-entered.png'
    }

    raw_video = await page.video.path()
    await context.close()
    return raw_video


async def fallback_check(browser, checks):
    """Model blocked fallback: labeled still view, component cards, and return work."""
    context = await browser.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = await context.new_page()
    await page.route('**/models/surgeline.glb', lambda route: route.abort())
    await enter(page, '/work/surgeline')
    # Instruments load behind the hero (Phase 7), so a blocked model can fail after Enter.
    await page.wait_for_selector('.observatory[data-scene="fallback"]', state='attached', timeout=30000)
    scene = await page.locator('.observatory').get_attribute('data-scene')
    await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#case-instrument'))
    await page.wait_for_timeout(600)
    still = await page.locator('.case-instrument-still').is_visible()
    bg = await page.locator('.case-instrument-still').evaluate('(e)=>getComputedStyle(e).backgroundImage')
    notice = await page.locator('.fallback-notice').bounding_box()
    heading = await page.locator('.case-instrument-heading').bounding_box()
    await page.locator('.hotspot-1').click()
    card_title = await page.locator('#component-card h3').inner_text()
    await page.screenshot(path=str(OUT / '08-fallback-still-view.png'))
    await page.locator('.case-brief .case-back').click()
    await page.wait_for_url(URL + '/')
    await idle(page)
    surgeline_top = await page.locator('#surgeline').evaluate('(e)=>Math.round(e.getBoundingClientRect().top)')
    checks['fallback'] = {
        'pass': scene == 'fallback' and still and 'surgeline-fallback.png' in bg and notice['y'] + notice['height'] <= heading['y'] and card_title == 'Parallel workers' and abs(surgeline_top) < 2,
        'detail': f"data-scene={scene}, still visible={still}, bg={bg}, notice clears heading={notice['y'] + notice['height'] <= heading['y']}, card={card_title}, return top={surgeline_top}",
        'screenshot': '08-fallback-still-view.png'
    }
    await context.close()


async def viewports_check(browser, checks):
    (OUT / 'viewports').mkdir(parents=True, exist_ok=True)
    results = []
    for width, height in [(360, 740), (430, 932)]:
        context = await browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=2, is_mobile=True, has_touch=True)
        page = await context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        await enter(page)
        name = f'{width}x{height}'

        # Check CrossCheck & SurgeLine in this viewport
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#crosscheck') + 280)
        await page.wait_for_timeout(600)
        origin = await page.evaluate('scrollY')
        await page.locator('[data-open-case=crosscheck]').click()
        await page.wait_for_url(f'{URL}/work/crosscheck')
        await idle(page)
        await page.screenshot(path=str(OUT / f'viewports/brief-{name}.png'))
        wide = await overflow(page)
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#case-instrument'))
        await page.wait_for_timeout(500)
        await page.locator('.hotspot-0').click()
        box = await page.locator('#component-card').bounding_box()
        await page.screenshot(path=str(OUT / f'viewports/hotspot-{name}.png'))
        await page.evaluate('(y)=>scrollTo(0,y)', await top(page, '#readings-heading') - 110)
        for i, val in enumerate(CASES[0]['countValues']):
            await page.locator('.case-reading').nth(i).scroll_into_view_if_needed()
            await page.wait_for_function('(a)=>document.querySelectorAll("[data-count]")[a.i].textContent===a.v', arg={'i': i, 'v': val})
        await page.screenshot(path=str(OUT / f'viewports/readings-{name}.png'))
        await page.locator('.case-next .case-back').click()
        await page.wait_for_url(URL + '/')
        await idle(page)
        back = await page.evaluate('scrollY')
        ok = not wide and box['y'] + box['height'] <= height and abs(back - origin) < 2 and not errors
        results.append({'viewport': name, 'pass': ok, 'overflow': wide, 'cardBottom': round(box['y'] + box['height']), 'returnScroll': [back, origin], 'errors': errors})
        await context.close()

    for kind, src in (('brief', 'case-crosscheck-brief.png'), ('hotspot', 'case-crosscheck-hotspot-1.png'), ('readings', 'case-crosscheck-readings.png')):
        shutil.copy(OUT / src, OUT / f'viewports/{kind}-390x844.png')

    sheet = Image.new('RGB', (3 * W, 3 * H), 'black')
    for c, name in enumerate(['390x844', '360x740', '430x932']):
        for r, kind in enumerate(['brief', 'hotspot', 'readings']):
            sheet.paste(tile(OUT / f'viewports/{kind}-{name}.png', f'{name} · {kind}'), (c * W, r * H))
    sheet.save(OUT / 'viewports/viewports-sheet.jpg', quality=86)

    checks['viewports'] = {
        'pass': all(r['pass'] for r in results),
        'detail': '; '.join([f"{r['viewport']}: pass={r['pass']}, overflow={r['overflow']}" for r in results]),
        'screenshot': 'viewports/viewports-sheet.jpg'
    }


def make_contact_sheet():
    labeled = [
        ('01-gate-entered.png', 'Gate · Enter'),
        ('02-crosscheck-chapter.png', 'Chapter 01 · CrossCheck'),
        ('03b-flight-mid.png', 'Flight in · text fades'),
        ('case-crosscheck-brief.png', 'CrossCheck · Brief (Approved)'),
        ('case-crosscheck-hotspot-1.png', 'CrossCheck · Hotspots'),
        ('case-crosscheck-readings.png', 'CrossCheck · Readings'),
        ('04-chain-sweep-surgeline.png', 'Chain sweep → SurgeLine'),
        ('case-surgeline-brief.png', 'SurgeLine · Brief (DRAFT)'),
        ('case-surgeline-hotspot-1.png', 'SurgeLine · Hotspots'),
        ('case-surgeline-readings.png', 'SurgeLine · Readings'),
        ('case-driftwatch-brief.png', 'DriftWatch · Brief (DRAFT)'),
        ('case-driftwatch-hotspot-1.png', 'DriftWatch · Hotspots'),
        ('case-driftwatch-readings.png', 'DriftWatch · Readings'),
        ('case-duewatch-brief.png', 'DueWatch · Brief (DRAFT)'),
        ('case-duewatch-hotspot-1.png', 'DueWatch · Hotspots'),
        ('case-duewatch-readings.png', 'DueWatch · Readings'),
        ('case-brandwall-brief.png', 'BrandWall · Brief (DRAFT)'),
        ('case-brandwall-hotspot-1.png', 'BrandWall · Hotspots'),
        ('case-brandwall-readings.png', 'BrandWall · Readings'),
        ('05b-return-mid.png', 'Return flight · fading'),
        ('06-returned-crosscheck.png', 'Returned · CrossCheck floor'),
        ('07-returned-surgeline.png', 'Chain return · SurgeLine floor'),
        ('08-fallback-still-view.png', 'Model blocked · Fallback still'),
        ('viewports/viewports-sheet.jpg', 'Viewports 390 / 360 / 430'),
    ]

    cols = 6
    rows = (len(labeled) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * W, rows * H), 'black')
    for i, (name, lbl) in enumerate(labeled):
        img_path = OUT / name
        if img_path.exists():
            sheet.paste(tile(img_path, f'{i+1:02d} {lbl}'), ((i % cols) * W, (i // cols) * H))
    sheet.save(OUT / 'contact-sheet.jpg', quality=86)


async def run():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    checks = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        try:
            raw_video = await main_flow(browser, checks)
            await fallback_check(browser, checks)
            await viewports_check(browser, checks)
        finally:
            await browser.close()

    # Transcode video to final MP4
    mp4 = OUT / 'case-files-walkthrough.mp4'
    subprocess.run([
        'ffmpeg', '-y', '-loglevel', 'error',
        '-i', raw_video,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart',
        str(mp4)
    ], check=True)
    shutil.rmtree(OUT / 'raw', ignore_errors=True)

    # Contact sheet
    make_contact_sheet()

    # Evidence report
    all_passed = all(c['pass'] for c in checks.values()) and len(checks) == len(ITEMS)
    report = {
        'status': 'passed' if all_passed else 'failed',
        'phase': 'Phase 5 — All case files',
        'stage': 'Testing',
        'finishedAt': datetime.now(timezone.utc).isoformat(),
        'url': URL,
        'viewport': [W, H],
        'scope': 'Chromium mobile emulation (GPU ANGLE, DPR 2); 390×844, 360×740, 430×932',
        'items': {
            k: {
                'label': ITEMS[k],
                **checks.get(k, {'pass': False, 'detail': 'not executed'}),
                **({'finding': FINDINGS[k]} if k in FINDINGS else {})
            } for k in ITEMS
        },
        'video': mp4.name,
        'contactSheet': 'contact-sheet.jpg',
        'viewportsSheet': 'viewports/viewports-sheet.jpg'
    }
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')

    for key, check in report['items'].items():
        print(f"{'PASS' if check['pass'] else 'FAIL'} {key}: {check['detail']}")
    print(f"Overall status: {report['status']}")
    return all_passed


if __name__ == '__main__':
    ok = asyncio.run(run())
    sys.exit(0 if ok else 1)
