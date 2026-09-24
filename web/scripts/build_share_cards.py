"""Phase 8: share cards (Open Graph / WhatsApp / LinkedIn) and the site icon set.

Writes web/public/og/{home,<slug>}.jpg (1200×630, JPEG, each under 300 KB so WhatsApp shows the
preview) and web/app/{icon.svg,apple-icon.png,favicon.ico}. Card copy is read from the approved
strings in lib/instruments.ts and lib/cases.ts and app/page.tsx, so a card can never carry a number
the site does not already show. Re-run after any of those strings change.

  /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/build_share_cards.py
"""
from __future__ import annotations

import io
import random
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from playwright.sync_api import sync_playwright

WEB = Path(__file__).resolve().parents[1]
PUBLIC = WEB / 'public'
OUT = PUBLIC / 'og'
FONTS = PUBLIC / 'fonts'
W, H = 1200, 630
MAX_BYTES = 300_000

INK, PANEL, AMBER, IVORY, MUTED, LINE = '#0B1020', '#141B2E', '#F2A541', '#EDE8DC', '#A5AEC2', '#303A50'

# The site mark: an observatory dome with its shutter open on one amber star. Drawn on the ink panel.
ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#0B1020"/>
<path d="M12 44a20 20 0 0 1 40 0z" fill="#EDE8DC"/>
<path d="M29 24.3h6V44h-6z" fill="#0B1020"/>
<rect x="10" y="44" width="44" height="5" rx="1.5" fill="#303A50"/>
<circle cx="32" cy="15" r="3.6" fill="#F2A541"/>
</svg>
"""


def read(path: str) -> str:
    return (WEB / path).read_text(encoding='utf-8')


def instruments() -> list[dict[str, str]]:
    src = read('lib/instruments.ts')
    keys = ('id', 'name', 'category', 'reading', 'unit', 'context')
    rows = []
    for block in re.findall(r"\{ id: '[^}]+\}", src):
        row = {k: re.search(rf"\b{k}: '([^']*)'", block) for k in keys}
        if all(row.values()):
            rows.append({k: m.group(1) for k, m in row.items()})
    if len(rows) != 5:
        sys.exit(f'expected 5 instruments in lib/instruments.ts, found {len(rows)}')
    decks = dict(re.findall(r"id: '(\w+)', draft:.*?deck: \['([^\]]*)'\]", read('lib/cases.ts'), re.S))
    for row in rows:
        deck = decks.get(row['id'])
        if not deck:
            sys.exit(f"no deck for {row['id']} in lib/cases.ts")
        row['deck'] = [part.strip("' ") for part in deck.split("', '")]
    return rows


def hero() -> dict[str, str]:
    src = read('app/page.tsx')
    heading = re.search(r'id="hero-heading"[^>]*>(.*?)</h2>', src)
    positioning = re.search(r'className="positioning">(.*?)</p>', src)
    if not heading or not positioning:
        sys.exit('hero heading/positioning not found in app/page.tsx')
    return {'heading': heading.group(1).replace('<br />', '\n'), 'positioning': positioning.group(1)}


def font(name: str, size: int, weight: int | None = None) -> ImageFont.FreeTypeFont:
    face = ImageFont.truetype(str(FONTS / f'{name}.ttf'), size)
    if weight is not None:
        try:
            face.set_variation_by_axes([weight] + [a['default'] for a in face.get_variation_axes()[1:]])
        except OSError:
            pass  # static font: no axes
    return face


def sky() -> Image.Image:
    """Near-black top to deep blue horizon, a few stars; the homepage sky, flattened."""
    top, bottom = (5, 7, 16), (22, 38, 78)
    grad = Image.new('RGB', (1, H))
    for y in range(H):
        t = (y / (H - 1)) ** 1.6
        grad.putpixel((0, y), tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))
    img = grad.resize((W, H))
    draw = ImageDraw.Draw(img)
    rng = random.Random(8)  # fixed seed: the same card on every build
    for _ in range(140):
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.8)
        r, a = rng.choice((0.6, 0.8, 1.1, 1.5)), rng.randint(90, 230)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(a, a, min(255, a + 10)))
    return img


def place(card: Image.Image, render: str, box: tuple[int, int, int, int]) -> None:
    art = Image.open(PUBLIC / 'images' / render).convert('RGBA')
    art.thumbnail((box[2], box[3]), Image.LANCZOS)
    x = box[0] + (box[2] - art.width) // 2
    y = box[1] + (box[3] - art.height) // 2
    glow = Image.new('RGBA', card.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((x + art.width * 0.15, y + art.height * 0.2, x + art.width * 0.85, y + art.height * 0.9),
                                 fill=(242, 165, 65, 46))
    card.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70)))
    card.alpha_composite(art, (x, y))


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines, line = [], ''
    for word in text.split():
        trial = f'{line} {word}'.strip()
        if draw.textlength(trial, font=face) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + ([line] if line else [])


def footer(draw: ImageDraw.ImageDraw) -> None:
    draw.line((72, H - 78, W - 72, H - 78), fill=LINE, width=1)
    mono = font('jetbrains-mono', 20)
    draw.text((72, H - 58), 'RAYIN OBSERVATORY', font=mono, fill=AMBER)
    name = 'Rayina Ilham · Automation Engineer'
    draw.text((W - 72 - draw.textlength(name, font=font('inter', 22)), H - 60), name, font=font('inter', 22), fill=MUTED)


def home_card(copy: dict[str, str]) -> Image.Image:
    card = sky().convert('RGBA')
    place(card, 'dome-fallback.png', (640, 20, 540, 520))
    draw = ImageDraw.Draw(card)
    draw.text((72, 78), 'RAYINA ILHAM', font=font('jetbrains-mono', 24), fill=AMBER)
    y = 124
    for line in copy['heading'].split('\n'):
        draw.text((72, y), line, font=font('fraunces', 92, 600), fill=IVORY)
        y += 104
    body = font('inter', 30)
    for line in wrap(draw, copy['positioning'], body, 560):
        draw.text((72, y + 22), line, font=body, fill=MUTED)
        y += 42
    footer(draw)
    return card


def case_card(index: int, item: dict) -> Image.Image:
    card = sky().convert('RGBA')
    place(card, f"{item['id']}-fallback.png", (680, 30, 480, 480))
    draw = ImageDraw.Draw(card)
    draw.text((72, 70), f"{index + 1:02d} / {item['category'].upper()}", font=font('jetbrains-mono', 22), fill=AMBER)
    draw.text((72, 104), item['name'], font=font('fraunces', 84, 600), fill=IVORY)
    deck = font('fraunces', 36, 400)
    y = 214
    for line in item['deck']:
        draw.text((72, y), line, font=deck, fill=IVORY)
        y += 46
    y += 34
    figure = font('jetbrains-mono', 76, 600)
    draw.text((72, y), item['reading'], font=figure, fill=AMBER)
    unit_x = 72 + draw.textlength(item['reading'], font=figure) + 20
    draw.text((unit_x, y + 38), item['unit'], font=font('inter', 28), fill=IVORY)
    draw.text((72, y + 104), item['context'], font=font('inter', 24), fill=MUTED)
    footer(draw)
    return card


def save_jpeg(card: Image.Image, path: Path) -> int:
    for quality in (88, 84, 80, 76, 72):
        buf = io.BytesIO()
        card.convert('RGB').save(buf, 'JPEG', quality=quality, optimize=True, progressive=True)
        if buf.tell() <= MAX_BYTES:
            path.write_bytes(buf.getvalue())
            return buf.tell()
    sys.exit(f'{path.name} stays above {MAX_BYTES} bytes')


def icons() -> None:
    app = WEB / 'app'
    (app / 'icon.svg').write_text(ICON_SVG, encoding='utf-8')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 512, 'height': 512})
        page.set_content(f'<body style="margin:0;background:transparent">{ICON_SVG.replace("<svg ", "<svg width=512 height=512 ")}</body>')
        png = page.screenshot(omit_background=True, clip={'x': 0, 'y': 0, 'width': 512, 'height': 512})
        browser.close()
    mark = Image.open(io.BytesIO(png)).convert('RGBA')
    # Apple crops its own corners: fill the square instead of leaving transparent rounded edges.
    apple = Image.new('RGBA', mark.size, INK)
    apple.alpha_composite(mark)
    apple.resize((180, 180), Image.LANCZOS).convert('RGB').save(app / 'apple-icon.png', optimize=True)
    mark.save(app / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])


def main() -> None:
    OUT.mkdir(exist_ok=True)
    report = [('home', save_jpeg(home_card(hero()), OUT / 'home.jpg'))]
    for index, item in enumerate(instruments()):
        report.append((item['id'], save_jpeg(case_card(index, item), OUT / f"{item['id']}.jpg")))
    icons()
    for name, size in report:
        print(f'og/{name}.jpg  {size:,} B')
    print('app/icon.svg, app/apple-icon.png, app/favicon.ico')


if __name__ == '__main__':
    main()
