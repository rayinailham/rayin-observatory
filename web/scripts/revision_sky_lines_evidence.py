"""Owner revision 3 (after the Phase 4 gate): sparse top-30% stars and the CrossCheck leader lines.
Captures the sky on home/chapter/case and each hotspot, checks every leader line keeps clear of the
other two lenses, then writes PNGs, a labeled contact sheet and evidence.json.
"""
import asyncio
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright
from verify_case import URL, enter, scroll_to

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/renders/revision-sky-lines/evidence'
VIEWPORTS = [(390, 844), (360, 740), (430, 932)]
CLEARANCE = 30  # CSS px between a leader line and any lens it does not point at


def gap(p, a, b):
    ax, ay, bx, by, px, py = *a, *b, *p
    t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
    return math.dist(p, (ax + t * (bx - ax), ay + t * (by - ay)))


async def run():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'scope': 'Owner revision 3: sky stars + CrossCheck leader lines', 'startedAt': datetime.now(timezone.utc).isoformat(), 'results': []}
    shots = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--ignore-gpu-blocklist'])
        for width, height in VIEWPORTS:
            tag = f'{width}x{height}'
            context = await browser.new_context(viewport={'width': width, 'height': height}, is_mobile=True, has_touch=True, device_scale_factor=2)
            page = await context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
            await enter(page)
            for name, label in [('home', 'Sky / hero'), ('chapter', 'Sky / CrossCheck chapter')]:
                if name == 'chapter':
                    await scroll_to(page, '#crosscheck', 280)
                path = OUT / f'sky-{name}-{tag}.png'
                await page.screenshot(path=str(path))
                shots.append((path, f'{label} {tag}'))
            await enter(page, '/work/crosscheck')
            path = OUT / f'sky-case-{tag}.png'
            await page.screenshot(path=str(path))
            shots.append((path, f'Sky / case brief {tag}'))
            await scroll_to(page, '#case-instrument')
            lines = []
            for i in range(3):
                await page.locator(f'.hotspot-{i}').click()
                await page.wait_for_timeout(400)
                path = OUT / f'hotspot-{i + 1}-{tag}.png'
                await page.screenshot(path=str(path))
                shots.append((path, f'Hotspot 0{i + 1} {tag}'))
            stage = await page.locator('#case-instrument').bounding_box()
            for i in range(3):
                box = await page.locator(f'.hotspot-{i}').bounding_box()
                end = await page.locator('[data-hotspot-line]').nth(i).evaluate("e=>[Number(e.getAttribute('x2')),Number(e.getAttribute('y2'))]")
                lines.append(((box['x'] + box['width'] / 2, box['y'] + box['height'] / 2 - stage['y']), tuple(end)))
            clear = [round(min(gap(lines[j][1], *lines[i]) for j in range(3) if j != i), 1) for i in range(3)]
            passed = all(c >= CLEARANCE for c in clear) and not errors
            report['results'].append({'viewport': [width, height], 'leaders': [{'marker': m, 'lens': e} for m, e in lines],
                'clearanceToOtherLenses': clear, 'minClearance': CLEARANCE, 'errors': errors, 'pass': passed})
            await context.close()
        await browser.close()
    report['finishedAt'] = datetime.now(timezone.utc).isoformat()
    report['status'] = 'passed' if all(r['pass'] for r in report['results']) else 'failed'
    (OUT / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    font = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', 22) if Path('/usr/share/fonts/TTF/DejaVuSans.ttf').exists() else ImageFont.load_default()
    tile_w, cols = 300, 6
    tiles = []
    for path, label in shots:
        im = Image.open(path).convert('RGB')
        im = im.resize((tile_w, round(im.height * tile_w / im.width)))
        tiles.append((im, label))
    tile_h = max(im.height for im, _ in tiles) + 34
    sheet = Image.new('RGB', (cols * tile_w, math.ceil(len(tiles) / cols) * tile_h), '#05070d')
    draw = ImageDraw.Draw(sheet)
    for n, (im, label) in enumerate(tiles):
        x, y = n % cols * tile_w, n // cols * tile_h
        sheet.paste(im, (x, y + 34))
        draw.text((x + 8, y + 6), label, fill='#F2A541', font=font.font_variant(size=17) if hasattr(font, 'font_variant') else font)
    sheet.save(OUT / '00-contact-sheet.jpg', quality=88)
    print(json.dumps(report['results'], indent=1))
    assert report['status'] == 'passed', report['status']


if __name__ == '__main__':
    asyncio.run(run())
