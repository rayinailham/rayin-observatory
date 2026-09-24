"""Q49 helpers shared by the suites (7F): native scroll, visitor-turned instruments, per-case curtains.

Since Q49 no chapter is pinned and scroll never turns an instrument. The visitor turns it: a sideways
drag across `.instrument-stage` sets the turn by hand (max(260 px, 55% of the stage) = one full turn),
a tap plays the whole turn (or winds it back). The shell writes the turn as `--instrument-<i>-orbit`
on the chapter section. Every flight draws the case's own curtain (`.curtain`, data-style/data-state).
"""
IDS = ['crosscheck', 'surgeline', 'driftwatch', 'duewatch', 'brandwall']
CURTAINS = {'crosscheck': 'stage', 'surgeline': 'blinds', 'driftwatch': 'roller', 'duewatch': 'louvre', 'brandwall': 'prism'}


async def land(page, y):
    """Native scroll that survives a Lenis tail: repeat until the page actually sits at y."""
    for _ in range(12):
        await page.evaluate('(y)=>scrollTo(0,y)', y)
        await page.wait_for_timeout(250)
        if abs(await page.evaluate('scrollY') - min(y, await page.evaluate('document.documentElement.scrollHeight-innerHeight'))) < 3:
            return
    raise AssertionError(f'could not land at {y}')


async def to_chapter(page, slug, offset=0):
    """Scroll so the chapter's single screen fills the viewport (plus `offset` px)."""
    y = await page.locator(f'#{slug}').evaluate('e=>e.getBoundingClientRect().top+scrollY')
    await land(page, y + offset)
    return y + offset


async def orbit(page, slug):
    i = IDS.index(slug)
    return float(await page.locator(f'#{slug}').evaluate(f"e=>getComputedStyle(e).getPropertyValue('--instrument-{i}-orbit')") or 0)


async def _stage(page, slug):
    return await page.locator(f'#{slug} .instrument-stage').evaluate(
        'e=>{const r=e.getBoundingClientRect();return {x:r.left,y:r.top,w:r.width,h:r.height,cw:e.clientWidth}}')


async def turn(page, slug, value, steps=12):
    """Drag the chapter's instrument to `value` (0–1) by hand. The chapter must be on screen."""
    box = await _stage(page, slug)
    start = await orbit(page, slug)
    dx = -(value - start) * max(260, box['cw'] * .55)
    x0 = box['x'] + box['w'] * (.85 if dx < 0 else .15)
    y0 = box['y'] + box['h'] * .42
    await page.mouse.move(x0, y0)
    await page.mouse.down()
    for k in range(1, steps + 1):
        await page.mouse.move(x0 + dx * k / steps, y0)
        await page.wait_for_timeout(16)
    await page.mouse.up()
    await page.wait_for_timeout(120)
    reached = await orbit(page, slug)
    assert abs(reached - max(0, min(1, value))) < .03, (slug, 'turn missed', value, reached)
    return reached


async def tap(page, slug, settle=True):
    """Tap the stage (not a control): plays the whole turn, or winds it back from past half way."""
    box = await _stage(page, slug)
    start = await orbit(page, slug)
    await page.mouse.click(box['x'] + box['w'] * .5, box['y'] + box['h'] * .42)
    if settle:
        # Settled = resting at the far end from where the tap started (a tap below half way plays to 1, else back to 0).
        end = 1 if start < .5 else 0
        await page.wait_for_function(f"Number(getComputedStyle(document.getElementById('{slug}')).getPropertyValue('--instrument-{IDS.index(slug)}-orbit'))==={end}", timeout=6000)
    return await orbit(page, slug)


# Records every distinct (state, style, path) of the curtain until read; survives client-side routing.
WATCH = """() => { const log = window.__curtainLog = []; let last = '';
  const tick = () => { const c = document.querySelector('.curtain'); if (c) { const k = [c.dataset.state, c.dataset.style, location.pathname].join('|');
    if (k !== last) { last = k; log.push(k.split('|')); } } if (window.__curtainLog === log) requestAnimationFrame(tick); };
  requestAnimationFrame(tick); }"""


async def watch_curtain(page):
    await page.evaluate(WATCH)


async def curtain_log(page, until_open_at=None, timeout=6000):
    """Wait until the curtain is open again (optionally on path `until_open_at`), return the log."""
    if until_open_at:
        await page.wait_for_function('(p)=>location.pathname===p&&document.querySelector(".curtain").dataset.state==="open"', arg=until_open_at, timeout=timeout)
    else:
        await page.wait_for_function('document.querySelector(".curtain").dataset.state==="open"', timeout=timeout)
    await page.wait_for_timeout(60)
    return await page.evaluate('window.__curtainLog.slice()')


def closed_styles(log):
    """Styles in which the curtain was fully closed, in order."""
    out = []
    for state, style, _ in log:
        if state == 'closed' and (not out or out[-1] != style):
            out.append(style)
    return out
