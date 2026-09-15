"""Phase 0 gate audit (run with the CrossCheck venv; server on :8766): 3 engines x 3 phone viewports, technical checks + contrast."""
import asyncio, json, sys
from pathlib import Path
from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:8766/style-lock/'
OUT = Path(__file__).resolve().parents[1] / 'renders' / 'gate-audit'
OUT.mkdir(exist_ok=True)
VIEWPORTS = [(390, 844), (360, 740), (430, 932)]


def lum(hexc):
    h = hexc.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


PAIRS = {
    'ivory on ink (body)': ('#EDE8DC', '#0B1020', 4.5),
    'muted on ink (small labels)': ('#A5AEC2', '#0B1020', 4.5),
    'amber on ink (project label)': ('#F2A541', '#0B1020', 4.5),
    'ink on amber (CTA)': ('#0B1020', '#F2A541', 4.5),
    'ivory on panel': ('#EDE8DC', '#141B2E', 4.5),
    'signal-ok on ink': ('#5BE49B', '#0B1020', 4.5),
    'signal-alarm on ink': ('#FF5A5F', '#0B1020', 4.5),
}

PROBE = """() => {
  const W = innerWidth;
  const offenders = [...document.querySelectorAll('body *')].filter(e => {
    const r = e.getBoundingClientRect();
    return r.width && (r.right > W + 0.5 || r.left < -0.5) && !e.closest('.instrument');
  }).map(e => e.tagName + '.' + e.className);
  const clipped = [...document.querySelectorAll('h1,h2,p,a,span,div,figcaption,summary')]
    .filter(e => e.children.length === 0 && e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflow !== 'visible')
    .map(e => e.textContent.trim().slice(0, 40));
  const cta = document.querySelector('.cta').getBoundingClientRect();
  const sum = document.querySelector('summary').getBoundingClientRect();
  const h1 = document.querySelector('h1').getBoundingClientRect();
  const txt = document.body.innerText;
  return {
    overflowX: document.documentElement.scrollWidth > W,
    offenders, clipped,
    ctaBottom: Math.round(cta.bottom), ctaInFirstScreen: cta.bottom <= innerHeight,
    ctaHeight: Math.round(cta.height), summaryHeight: Math.round(sum.height),
    h1Width: Math.round(h1.width), h1Lines: Math.round(h1.height / (parseFloat(getComputedStyle(document.querySelector('h1')).lineHeight) || 1)),
    fonts: [...document.fonts].map(f => f.family + ':' + f.status),
    images: [...document.images].map(i => i.complete && i.naturalWidth > 0),
    lang: document.documentElement.lang,
    brand: txt.includes('Rayin Observatory'), fullName: txt.includes('Rayina Ilham'),
    badName: /Rayin Ailham/i.test(txt), draft: txt.includes('DRAFT'),
    amazon: /amazon/i.test(txt),
  };
}"""


async def run(p, engine, vw, vh):
    b = await getattr(p, engine).launch(headless=True)
    opts = dict(viewport={'width': vw, 'height': vh}, device_scale_factor=2)
    if engine != 'firefox':
        opts.update(is_mobile=True, has_touch=True)
    ctx = await b.new_context(**opts)
    page = await ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('requestfailed', lambda r: errors.append(r.url + ' ' + str(r.failure)))
    page.on('response', lambda r: errors.append(f'{r.status} {r.url}') if r.status >= 400 else None)
    await page.goto(URL, wait_until='networkidle')
    await page.evaluate('document.fonts.ready')
    tag = f'{engine}-{vw}x{vh}'
    await page.screenshot(path=str(OUT / f'{tag}.png'))
    await page.evaluate("async () => {for (const i of document.images){i.loading='eager'; try{await i.decode()}catch(e){}}}")
    res = await page.evaluate(PROBE)
    await page.locator('.cta').click()
    await page.wait_for_timeout(300)
    res['anchor'] = await page.evaluate("location.hash === '#style-review'")
    await page.locator('summary').click()
    res['detailsOpen'] = await page.locator('details').evaluate('e => e.open')
    if (vw, vh) == (390, 844):
        await page.screenshot(path=str(OUT / f'{tag}-full.png'), full_page=True)
    res['errors'] = errors
    await b.close()
    fails = []
    if res['overflowX'] or res['offenders']: fails.append('overflow')
    if res['clipped']: fails.append('clipped text')
    if not res['ctaInFirstScreen']: fails.append('CTA below fold')
    if res['ctaHeight'] < 44 or res['summaryHeight'] < 44: fails.append('tap target <44')
    if len(res['fonts']) != 3 or not all(f.endswith('loaded') for f in res['fonts']): fails.append('fonts')
    if len(res['images']) != 4 or not all(res['images']): fails.append('images')
    if res['lang'] != 'en' or not res['brand'] or not res['fullName'] or res['badName'] or not res['draft'] or res['amazon']: fails.append('copy/identity')
    if not res['anchor'] or not res['detailsOpen']: fails.append('interaction')
    if errors: fails.append('browser errors')
    return tag, res, fails


async def main():
    results, all_fails = {}, {}
    async with async_playwright() as p:
        for engine in ('chromium', 'firefox', 'webkit'):
            for vw, vh in VIEWPORTS:
                try:
                    tag, res, fails = await run(p, engine, vw, vh)
                except Exception as e:
                    tag, res, fails = f'{engine}-{vw}x{vh}', {'exception': str(e)}, ['launch/run error']
                results[tag] = res
                all_fails[tag] = fails
                print(f'{tag:22} ctaBottom={res.get("ctaBottom")!s:>4}  {"PASS" if not fails else "FAIL " + ", ".join(fails)}')
    contrast = {k: {'ratio': ratio(a, b), 'min': m, 'pass': ratio(a, b) >= m} for k, (a, b, m) in PAIRS.items()}
    print('\nContrast (WCAG AA 4.5:1 normal text):')
    for k, v in contrast.items():
        print(f'  {k:30} {v["ratio"]:>5}  {"PASS" if v["pass"] else "FAIL"}')
    (OUT / 'gate-audit.json').write_text(json.dumps({'results': results, 'fails': all_fails, 'contrast': contrast}, indent=2))
    sys.exit(1 if any(all_fails.values()) or not all(v['pass'] for v in contrast.values()) else 0)


asyncio.run(main())
