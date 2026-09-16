"""Frame cost per instrument chapter: draw calls, triangles and frame timing.

Counts real GL draw calls by wrapping the context methods before the page loads, so the
numbers come from the browser rather than from the application's own bookkeeping.
Run with OBSERVATORY_URL against a preview; pass a stage name for the output file.
"""
import asyncio
import json
import os
import statistics
import sys
from pathlib import Path

from playwright.async_api import async_playwright

URL = os.environ.get('OBSERVATORY_URL', 'http://localhost:8767').rstrip('/')
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'after'
OUT = Path(__file__).resolve().parents[2] / 'assets/renders/instrument-detail'
GPU = ['--enable-gpu', '--use-gl=angle', '--use-angle=gl-egl', '--ignore-gpu-blocklist']
SLUGS = ['crosscheck', 'surgeline', 'driftwatch', 'duewatch', 'brandwall']

# Wrap draw calls and requestAnimationFrame before any application script runs.
PROBE = """
window.__probe = { calls: 0, tris: 0, frames: [], last: 0, on: false };
const MODE = { 0: 1, 1: 2, 2: 2, 3: 2, 4: 3, 5: 1, 6: 1 };
for (const proto of [WebGLRenderingContext.prototype, WebGL2RenderingContext.prototype]) {
  for (const name of ['drawElements', 'drawArrays', 'drawElementsInstanced', 'drawArraysInstanced']) {
    const original = proto[name];
    if (!original) continue;
    proto[name] = function (mode, a, b, c, d) {
      if (window.__probe.on) {
        window.__probe.calls++;
        const count = name.startsWith('drawElements') ? a : b;
        const instances = name.endsWith('Instanced') ? (name === 'drawElementsInstanced' ? d : c) : 1;
        window.__probe.tris += Math.floor(count / (MODE[mode] ?? 3)) * (instances || 1);
      }
      return original.apply(this, arguments);
    };
  }
}
const raf = window.requestAnimationFrame;
window.requestAnimationFrame = cb => raf(time => {
  const p = window.__probe;
  if (p.on && p.last) p.frames.push(time - p.last);
  p.last = time;
  cb(time);
});
"""

SAMPLE = """() => {
  const p = window.__probe;
  Object.assign(p, { calls: 0, tris: 0, frames: [], last: 0, on: true });
  return new Promise(resolve => setTimeout(() => {
    p.on = false;
    resolve({ calls: p.calls, tris: p.tris, frames: p.frames });
  }, 2000));
}"""


async def run():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'url': URL, 'stage': STAGE, 'chapters': {}}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=GPU)
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        await context.add_init_script(PROBE)
        page = await context.new_page()
        transferred = {'bytes': 0, 'models': [], 'script': 0}

        async def sized(response):
            model = '/models/' in response.url or response.url.endswith('.glb')
            script = response.url.endswith('.js') or '/_next/static/chunks/' in response.url
            if not (model or script):
                return
            try:
                body = await response.body()
            except Exception:  # noqa: BLE001 - a cancelled response has no body to weigh.
                return
            if script:
                transferred['script'] += len(body)
                return
            transferred['bytes'] += len(body)
            transferred['models'].append({'url': response.url.rsplit('/', 1)[-1], 'bytes': len(body)})

        page.on('response', lambda response: asyncio.create_task(sized(response)))
        await page.goto(URL)
        start = await page.evaluate('performance.now()')
        await page.locator('.silent-button').click(timeout=45000)
        await page.wait_for_selector('.entry-gate[hidden]', state='attached')
        report['msToEnterReady'] = round(await page.evaluate('performance.now()') - start)
        await page.wait_for_timeout(4000)
        for slug in SLUGS:
            y = await page.locator('#' + slug).evaluate('(e) => e.offsetTop + 150')
            await page.evaluate('(y) => window.scrollTo(0, y)', y)
            await page.wait_for_timeout(1800)
            sample = await page.evaluate(SAMPLE)
            frames = [f for f in sample['frames'] if f > 0]
            count = max(1, len(frames))
            report['chapters'][slug] = {
                'drawCallsPerFrame': round(sample['calls'] / count, 1),
                'trianglesPerFrame': round(sample['tris'] / count),
                'medianFrameMs': round(statistics.median(frames), 2) if frames else None,
                'p95FrameMs': round(sorted(frames)[int(len(frames) * .95)], 2) if len(frames) > 4 else None,
                'frames': len(frames),
            }
        report['modelBytes'] = transferred['bytes']
        report['scriptBytes'] = transferred['script']
        report['models'] = transferred['models']
        await browser.close()
    (OUT / f'frame-cost-{STAGE}.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    asyncio.run(run())
