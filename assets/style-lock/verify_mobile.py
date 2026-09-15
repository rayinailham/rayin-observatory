"""Focused Phase 0 check; run with a Python environment containing Playwright."""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
URL = 'http://127.0.0.1:8766/style-lock/'


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=1)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
        page.on('requestfailed', lambda req: errors.append(req.url + ': ' + str(req.failure)))
        page.on('response', lambda response: errors.append(f'{response.status} {response.url}') if response.status >= 400 else None)
        await page.goto(URL, wait_until='networkidle')
        await page.evaluate('document.fonts.ready')
        await page.screenshot(path=str(ROOT/'assets/renders/mobile-390x844.png'))
        # Explicitly load all lazy images before the full-page evidence.
        await page.evaluate("async () => {for(const img of document.images){img.loading='eager';await img.decode();}}")
        await page.screenshot(path=str(ROOT/'assets/renders/style-review-mobile.png'), full_page=True)
        result = await page.evaluate("""() => ({
          viewport: {width: innerWidth, height: innerHeight},
          horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
          ctaBottom: document.querySelector('.cta').getBoundingClientRect().bottom,
          fonts: [...document.fonts].map(f => ({family:f.family,status:f.status})),
          images: [...document.images].map(i => ({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0})),
          lang: document.documentElement.lang,
          text: document.body.innerText
        })""")
        await page.get_by_role('link', name='Review the style').click()
        result['reviewAnchorWorks'] = await page.evaluate("location.hash === '#style-review' && Math.abs(document.querySelector('#style-review').getBoundingClientRect().top - 18) < 2")
        await page.get_by_text('Review notes and copy source', exact=True).click()
        result['notesOpen'] = await page.locator('details').evaluate('(e) => e.open')
        result['errors'] = errors
        report = ROOT/'assets/style-lock/verification.json'
        report.write_text(json.dumps(result, indent=2)+'\n')
        assert not result['horizontalOverflow'], 'Horizontal overflow'
        assert result['ctaBottom'] <= 844, 'CTA outside first mobile viewport'
        assert len(result['fonts']) == 3 and all(f['status']=='loaded' for f in result['fonts']), 'Font failed'
        assert len(result['images']) == 4 and all(i['loaded'] for i in result['images']), 'Image failed'
        assert result['reviewAnchorWorks'] and result['notesOpen'], 'Review interaction failed'
        assert result['lang'] == 'en' and 'DRAFT' in result['text'], 'Copy status missing'
        assert not errors, errors
        print(json.dumps({k:v for k,v in result.items() if k not in ['text','images']},indent=2))
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
