# Capability Dossier — BrandWall (Design QA / Visual Brand Testing)

> **Source material for the portfolio page.** This document summarizes *what can be shown to
> a client* from the `brandwall` project: the tools mastered, the skills proven, the numbers
> that can be defended, and the deliverables that actually exist on disk. Every claim here has
> a file or a command that proves it.

| Meta | Value |
|---|---|
| Project name | **BrandWall** |
| Category | Design QA · Visual Regression · Brand Asset Testing · Accessibility (WCAG) |
| Local repo | `/home/rayin/Projects/Testing/brandwall` (local git, initial commit `45b4918`) |
| Status | 14/14 technical phases done · acceptance **11/12 ✅ + 1 🟨** |
| Work period | 2026-08-29 → 2026-09-05 (14 phases, one phase = one session) |
| Target job | Upwork — *"Design QA: Test How 20–50 Real Brands Look on Our Publication Pages"* ($250 fixed) |
| Proven scale | **30 brands × 5 surfaces × 2 themes = 300 screenshots per run**, 5 consecutive runs with zero failures |

---

## 1. One-sentence pitch

> "I drop 30 of the most extreme brand assets onto 5 of your product surfaces in light and
> dark themes, shoot all three hundred combinations without a single click, and hand back not
> an opinion — but **numbered breakage classes, the exact point of failure in ratio /
> luminance / name length, and the CSS rules that close each class outright.**"

The key differentiator: most "design QA" stops at *"this logo looks broken"*. BrandWall answers
the question clients actually pay for: **"at what number does my design start to break, and
what rule closes it?"**

---

## 2. The problem being solved (client framing)

Every white-label / multi-tenant platform looks neat — with demo logos. Then the real tenants
arrive: one wordmark 12:1 wide, one pure-white logo, one 64-character publication name in
Arabic script, one 32 px icon, one asset that 404s. Headers break, logos get clipped, text
disappears in dark theme — and usually the team finds out only after a customer complains.

The common way of handling it: someone opens 5 pages, looks at 3 logos, says "looks fine",
and stops. Three things are never answered:

1. How many combinations has nobody actually ever looked at? (here: 300)
2. At what **number** does the design start to break? (here: 11 breakpoints from sweeps)
3. What rule closes an **entire class** of problems instead of patching one tenant?
   (here: 7 CSS rules + 5 asset acceptance rules)

---

## 3. System scope

### 3.1 The locked matrix

| Axis | Value | Note |
|---|---|---|
| Brands | **30 synthetic test assets** | self-generated, with measured extreme characteristics |
| Surfaces | **5** | S1 listing card · S2 publication page · S3 reader header · S4 article page · S5 share card |
| Themes | **2** | `light`, `dark` |
| Viewport | 1440×900 | except **S5 = 1200×630** (Open Graph standard) |
| Total cells | **300** | `capture_id` = `<brand_id>__<surface_id>__<theme>` |
| Output per cell | 1 JSONL row + 2 PNGs | full-page screenshot + logo-slot crop |

### 3.2 The five surfaces and why each one is dangerous

| Surface | Route | Logo slot | Characteristic failure mode |
|---|---|---|---|
| S1 listing card | `/cards?tenant=<id>` | 40×40 box in the card header | a 12:1 wordmark squeezed down to roughly 3 px tall |
| S2 publication page | `/p/<id>` | 200 px wide inside a fixed 72 px bar | portrait logos push the bar contents out |
| S3 reader header | `/reader/<id>` | 120 px wide inside a 44 px sticky strip | unconstrained height → covers the text |
| S4 article page | `/a/<id>/<slug>` | inline 20 px (byline) + 220 px (footer) | light logo on light footer → disappears |
| S5 share card | `/share/<id>` | 420 px wide above the title | extreme ratios wreck the OG composition |

### 3.3 Thirty test assets — designed, not collected

Every asset is **self-generated** (`scripts/gen_brands.py --seed 42`) to reproduce the
characteristics of real-world logos **without distributing anybody's logo**:

| Category | Assets |
|---|---|
| Small square icons | `b01-square-32.png`, `b02-square-64.png` |
| Wide wordmarks | `b03-wide-4x1` → `b07-wide-12x1` (4:1, 6:1, 8:1, 10:1, 12:1) |
| Portrait logos | `b08-tall-1x4.svg`, `b09-tall-1x3.png` |
| Deceptive transparency | `b10-alpha-edge.png`, `b11-alpha-halo.png` |
| Luminance extremes | `b12-white-only.svg`, `b13-near-white.png`, `b14-black-only.svg`, `b15-near-black.png` |
| Non-Latin scripts | `b16-arabic.svg`, `b17-japanese.svg`, `b18-cyrillic.svg` |
| File pathologies | `b19-lowres-48.png`, `b20-huge-4000.png`, `b21-svg-noviewbox.svg`, `b22-svg-currentcolor.svg` |
| Deceptive geometry | `b23-padded.svg`, `b24-offcenter.png`, `b25-thin-stroke.svg` |
| Heavy rendering | `b26-gradient.png`, `b27-photo-bg.jpg` |
| **Load failure** | `b28-broken` — **deliberately absent from disk** (a real 404, not a simulation) |
| Long name | `b29-longname.svg` |
| **Healthy control** | `b30-normal.svg` — must produce **0 findings** across its 10 cells |

Each asset's properties (intrinsic ratio, size, luminance, ink percentage) are **measured by
script** (`scripts/measure_brands.py` → `assets/brands.json`), never typed by hand.

> **The control asset is a feature, not a decoration.** If `b30-normal` gets accused, the
> detector is broken. That is how you prove the 186 findings are not just a paranoid detector.

---

## 4. Architecture and data flow

```
assets/brands/*.svg|png|jpg        (30 assets, generated with --seed 42)
        │
        ├── scripts/measure_brands.py ──► assets/brands.json (MEASURED properties)
        │                                        │
        │                                        ▼
        │                     target/app.py (FastAPI, container brandwall-target :8130)
        │                     5 surfaces × 2 themes × ?fix=0|1
        │                                        │
        │                                        ▼
        └────────────────────► src/capture.py ───┤  1 cell = (brand, surface, theme, fix)
                                                 │  Playwright headless + Pillow + NumPy
                                                 ▼
                              data/<run_id>/captures.jsonl   (300 rows)
                              data/<run_id>/shots/*.png      (300 full + 300 slot crops)
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    ▼                            ▼                            ▼
             src/detect.py               src/breakpoint.py                src/diff.py
          findings.json                 data/breakpoints.json          data/<run>/diff.json
          classes.json                  docs/BREAKPOINTS.md            baseline/<run_id>/
                    │                            │                            │
                    └────────────────┬───────────┴────────────────────────────┘
                                     ▼
              scripts/build_gallery.py ──► web/{index,before-after}.html + thumbs/ + heatmap
              src/report.py            ──► reports/REPORT.xlsx + one-pager PDF
              scripts/check_numbers.py ──► number guard (exit 1 on any mismatch)
              scripts/audit.py         ──► leak audit (7 rules)
```

### Five binding architectural rules

1. **One direction.** The detector only reads `captures.jsonl` — it **must never open a
   browser**. A detector that can open a browser cannot be tested without the network, and its
   results cannot be reproduced from stored data.
2. **The target knows nothing about the detector.** No QA code lives in `target/`.
3. **Runs are immutable.** `data/<run_id>/` is never rewritten; a new run means a new folder.
4. **Everything offline.** Fonts bundled, placeholder images local, gallery with no CDN.
   `make all` runs on a machine with no internet.
5. **MCP and skills are build-time tools only.** The deliverable's runtime stands on its own.

---

## 5. Tools mastered and proven in this project

| Tool | Used for | Why this one |
|---|---|---|
| **Playwright (Chromium, headless)** | 300-cell capture engine + DOM metric extraction | needs real rendering + `getBoundingClientRect()`, not static HTML parsing |
| **Pillow + NumPy** | luminance, alpha, intrinsic size, crops, pixel diff | pure-Python pixel loops are far too slow across 300 × 1440×900 |
| **FastAPI + Jinja2** | target app, 5 surfaces × 2 themes, brand injected by query | an owned test target whose CSS can be deliberately naive |
| **Docker + Compose** | hosting the target, env-driven ports | a clean copy can run side by side with the original run |
| **matplotlib** | breakpoint curves, 30×10 heatmap, per-class bar charts | deterministic PNG output under 2 MB |
| **openpyxl** | `reports/REPORT.xlsx`, 5 sheets with evidence links | deliverable runtime must stand alone |
| **ffmpeg** | trimming, speed-up (`setpts`), burned-in captions (`drawtext`), 1080p encode | the only deterministic editor available over CLI |
| **GNU Make** | `make all` (8 stages), `make audit`, `make audit-bite` | one command reproduces everything from scratch |
| **uv (Python 3.13)** | venv + lockfile | the client only needs `uv sync` |
| **unittest** | 184 tests with no extra dependency | consistent across projects |
| **jq / wc / sort** | token-cheap inspection | `captures.jsonl` is never read raw |
| **PlantUML (disposable container)** | architecture diagrams | `.puml` + `.png` committed to the repo |

### MCP servers used (and their limits)

| MCP | Used for | Limit held |
|---|---|---|
| `playwright` | recon on 1–2 pages while building selectors | **not** the production 300-cell engine |
| `chrome-devtools` | `emulate` theme/viewport during manual verification, optional `lighthouse_audit` | sanity checks only |
| `excel` | reading/inspecting the finished XLSX | **not** the report generator |
| `serena` | symbol/reference lookup once the codebase grew | not a substitute for reading the file |

> **Rule enforced throughout the project:** *allowed while BUILDING, must stand alone while
> RUNNING.* No MCP, no device services (MySQL/Redis/TiDB), and no CDN anywhere on the
> deliverable's runtime path.

### Skills / methodologies applied

| Skill | Used in | For what |
|---|---|---|
| `phase-harness` | whole project | 14 phases, one phase = one session = one artifact, file-based cross-session memory |
| `qa-sweep` (adapted) | P4–P5 | matrix-loop pattern + `captures.jsonl` structure + `shots/` layout |
| `visual-brand-qa` | P2–P9 | asset × surface × theme matrix, numbered breakage classes, breakpoints, baseline diff |
| `dataviz` | P7, P10, P11 | color/scale rules for curves, heatmaps, stat cards |
| `device-screen-recording` | P12 | record a single window on a virtual output, no audio, never the physical monitor |
| `deliverable-pack` | P10–P12 | offline gallery + XLSX + one-pager + captioned video |
| `evidence-guard` | P11, P13 | number guard + leak audit + clean-copy gate |
| `arch-playwright-provision` | whole project | 3 Playwright engines on Arch Linux without sudo/pacman |

---

## 6. Proven capabilities (the core of the portfolio page)

This section is written as a list of capabilities that **can be claimed to a client**, each
with its proof.

### K1 — Matrix automation at scale, headless, zero clicks

300 cells shot in **one command**, headless, 6 parallel workers with browser *reuse* (not a
fresh browser per cell). Proven: **0 manual interactions**, **0 failed cells** across 5
consecutive runs, ~61 seconds per full run (~200 ms/cell; the fastest run, P5, did 44.4 s /
148 ms per cell).

Including **resume**: a run interrupted at cell 280 was continued with
`make capture-resume RUN_ID=…` → exactly the 20 remaining cells were processed, in 4.1 seconds.
Not a restart from zero.

### K2 — Measurement, not eyeballing (the biggest technical differentiator)

The absolute rule: **no finding may be based on "it looks broken"**. Every finding must carry
`metric` + `threshold` + `actual` + `capture_id` + `shot`. The validator rejects any finding
missing one of the five. Three measurement techniques were developed in this project:

1. **Background color from real pixels, not from CSS.** The title text is set to
   `color: transparent` momentarily, the element is shot, then the modal color of the crop is
   taken. Gradients and background images make CSS variables lie; pixels do not. The mutation
   is reverted **after** the screenshot is saved, so the stored PNG is unaffected.
2. **Slot fill from the difference of two shots.** The slot is shot once as-is, and once with
   the logo set to `visibility: hidden` (which does not change layout). The pixels that change
   are the logo ink that actually rendered. `element.screenshot()` is always opaque, so the
   asset file's alpha cannot answer "how full is this slot" — the difference can.
3. **True ink color via two-background *unmix*.** The slot is shot over black **and** over
   white; from that pair the alpha and the true color of every pixel are solved back exactly
   (`unmix_alpha`), independent of the page theme. An `alpha ≥ 0.5` mask discards anti-aliased
   edge pixels, so `ink_p05/p95_luminance` is the **body** color of the logo, not its blend
   with the background.

Plus one precision guard: **the outermost ring of the slot crop is discarded** before ink is
computed, because the slot box has fractional dimensions (e.g. 180.66 × 541.97 px) and its
border pixels are a blend of the slot contents with whatever lies outside — their values shift
between runs following repaint history. Without this guard, the diff becomes noisy for no
visible reason.

### K3 — A breakage taxonomy locked before the numbers were visible

The seven breakage classes were **locked in phase 3**, before a single line of the detector was
written. The reason is explicit: *thresholds born after the numbers are visible will always be
nudged until the finding count "looks good", and the report loses its meaning.*

Every class carries **four** things that must not be empty: the source of the number (the field
name in `captures.jsonl`), the threshold, **the reason for that threshold**, and the severity
rule.

| Code | Class | Fail threshold | Reason for the threshold |
|---|---|---|---|
| `BW-C1` | `logo_clipped` | overflow > 2 px on any side | 2 px = the sub-pixel rounding tolerance of `getBoundingClientRect()` at `deviceScaleFactor=1` |
| `BW-C2` | `text_unreadable` | < 4.5:1 normal text · < 3:1 large text | WCAG 2.1 §1.4.3 |
| `BW-C3` | `logo_contrast_fail` | < 3:1 | WCAG 2.1 §1.4.11 (graphical components) |
| `BW-C4` | `aspect_broken` | deviation > 1% | ±1% ≈ the point where wordmark distortion becomes visible to the eye |
| `BW-C5` | `fallback_ugly` | binary (load failure / 0% ink) | not a matter of degree, so no threshold is needed |
| `BW-C6` | `overlap` | intersection > 0 px (floored first) | any intersection between header elements is a layout defect |
| `BW-C7` | `script_clipped` | difference > 1 px | `scrollWidth`/`clientWidth` are already ints, 1 px = browser rounding |

Two conventions were pinned once so that the breakpoint sweep never lands one step off:
**failure = strictly `actual > threshold`** (`actual == threshold` does not trigger), and
**the C6 intersection area is `floor`ed** so that "> 0 px" is identical to "≥ 1 px" without two
thresholds that could silently diverge.

**And that taxonomy turned out to be wrong — then was fixed honestly.** The first 300-cell run
proved that **4 of the 7 classes were measuring the wrong element**:

| Class | Old source | What was actually measured | Consequence |
|---|---|---|---|
| C2 | `title` only | the title uses theme tokens, min contrast 15.08:1 across 300/300 | 0 findings even though the meta text really is naive |
| C3 | `mean_luminance` of the difference mask | the mean swallowed anti-aliased edge pixels | **the control asset was accused** on S1 (2.34:1) and passed on S2 (3.68:1) — the same asset |
| C5 | `nontransparent_pct == 0` | "differs from the background below a threshold", not "is absent" | perfectly loaded assets were labeled *load failure* |
| C7 | `title.scroll_w − client_w` | the element stretches because of `nowrap` without `overflow:hidden` | difference of 0 across 300/300; what broke was the row, not the element |

The fix replaced the **source of the numbers** and bumped `SCHEMA_VERSION` to 2 — **without
changing a single threshold, WCAG formula, or class count**. The consequence was accepted
knowingly: schema-1 runs must not be compared with schema-2 runs, and old runs are kept as
archives, not as baselines.

> This is the point worth displaying in a portfolio: **the ability to discover that your own
> detector is wrong, prove it with a control asset, then fix it without moving the thresholds.**

One dedupe rule was born from this too: findings whose numbers come from an element that is
**identical across all 30 brands** (page meta text) are recorded **once per surface × theme**,
not 30 times. *One page defect is not 30 brand defects.*

### K4 — Measured accessibility (WCAG 2.1), not a feeling

All 116 C2+C3 findings carry `metric: contrast_ratio`, `unit: ratio`, `threshold`, and `actual`
(e.g. `F-0077` 1.0 vs 3.0; `F-0007` 1.93 vs 4.5). Formula: relative luminance +
`(L1+0.05)/(L2+0.05)`. Thresholds: **4.5:1** normal text, **3:1** large text (≥24 px, or
≥18.66 px when `font-weight ≥ 700`) and graphical components. The ratio is **always recorded**,
not just pass/fail — so the client can set priorities.

### K5 — Breakpoints from sweeps, not interpolation

Every threshold comes out of a **probe sweep**: probe assets are generated in steps and shot
until the detector **changes state**. Reported as a range, complete with the step size.
Result: **11 breakpoints · 716 observations · 564 probe PNGs.**

| # | Axis | Surface | Class | Safe ≤ | Breaks ≥ | Step | Probes |
|---|---|---|---|---:|---:|---:|---:|
| BP1 | portrait ratio | S1 | `BW-C1` | 1.00 | **1.25** | 0.25 | 17 |
| BP2 | portrait ratio | S1 | `BW-C6` | 1.25 | **1.50** | 0.25 | 17 |
| BP3 | logo luminance | S1 (light) | `BW-C3` | 0.30 | **0.35** | 0.05 | 21 |
| BP4 | name length (Japanese) | S1 | `BW-C7` | 16 | **20** | 4 | 23 |
| BP5 | name length (Cyrillic) | S1 | `BW-C7` | 24 | **28** | 4 | 23 |
| BP6 | name length (Latin) | S1 | `BW-C7` | 28 | **32** | 4 | 23 |
| BP7 | name length (Arabic) | S1 | `BW-C7` | 32 | **36** | 4 | 23 |
| BP8–BP11 | logo luminance | S2–S5 (light) | `BW-C3` | 0.25–0.30 | **0.30–0.35** | 0.05 | 21 ea. |

**The honesty that was reported alongside it:** sweeping wide logos from 2:1 to 14:1 and
intrinsic sizes from 24 to 512 px produced **no** state transition. Both were still recorded as
observations, but **not faked into breakpoints**. In dark theme, the luminance transition runs
in the opposite direction (fail → safe as the logo gets brighter); the schema only represents
`safe_max < break_min`, so that reversed direction was not written up as a breakpoint.

**Cross-checked against the real matrix:** the sweep correctly predicted **6 of 8** actual
brands on the class/surface pairs that have a breakpoint. Two missed, and the reasons are
explained rather than hidden: `b28-broken` is a 404 (it has no ratio to predict from), and
`b05` has different glyph widths even though its character count is shorter than the Latin probe.

Each breakpoint also has a **quotable sentence** ready to drop straight into a client document:

> "On the listing card (S1), portrait logos are safe up to a 1:1 height ratio; clipping begins
> at 1.25:1 in both light and dark themes."

### K6 — Recommendations that close a class, not patch a tenant

Seven CSS rules, **one rule closing one class**, all of them real in `target/static/fixes.css`
(56 lines, 29 declarations) and *toggled* via `?fix=1` so the "before" run stays reproducible at
any time.

| Rule | Closes | Core |
|---|---|---|
| F1 | `BW-C1` | `.logo-slot { overflow:hidden; aspect-ratio:1/1; padding:4px }` |
| F2 | `BW-C2` | secondary text tokens get per-theme contrast (`[data-bw="meta"] { color:#000 }` / `#fff`) |
| F3 | `BW-C3` | per-theme monochrome variant: `filter:brightness(0)` / `brightness(0) invert(1)` |
| F4 | `BW-C4` | `object-fit: contain`, intrinsic ratio preserved |
| F5 | `BW-C5` | failed slots stay stable (`img:not([src]) { visibility:hidden }`) |
| F6 | `BW-C6` | explicit grid: `grid-template-columns: auto minmax(0,1fr) auto` |
| F7 | `BW-C7` | `min-width:0; overflow-wrap:anywhere; -webkit-line-clamp:2` |

Plus **5 asset acceptance rules** — a gate before a tenant's assets reach production, derived
directly from the breakpoints (e.g. *"tenant names on S1 are capped by script, not by a single
Latin limit: Japanese ≤16, Cyrillic ≤24, Latin ≤28, Arabic ≤32"*).

### K7 — Before vs after evidence, in numbers

The fix run was executed over **the same 300 cells**:

| Class | What was broken | Before | Brands affected | After |
|---|---|---:|---:|---:|
| `BW-C3` logo_contrast_fail | logo blends into the theme background | 106 | 22 | **0** |
| `BW-C6` overlap | logo collides with the title / header elements | 40 | 11 | **0** |
| `BW-C5` fallback_ugly | asset fails to load / 0% ink | 18 | 2 | **18** |
| `BW-C2` text_unreadable | secondary text below the WCAG threshold | 10 | 1 | **0** |
| `BW-C1` logo_clipped | logo clipped outside its slot | 6 | 3 | **0** |
| `BW-C7` script_clipped | non-Latin names clipped | 6 | 3 | **0** |
| `BW-C4` aspect_broken | intrinsic ratio forcibly changed | 0 | 0 | **0** |
| **Total** | | **186** | 164 cells | **18 (−90.3%)** |

**New findings introduced by the fixes: 0.** No class was closed at the cost of another.

**The remaining 18 `BW-C5` are deliberately not closed with CSS**, and the reason is part of the
recommendation: `b28-broken` really is a 404 (10 cells) and `b25-thin-stroke` really does have
0% solid ink (8 cells). That is a binary class to be **rejected at the asset acceptance gate**,
not hidden in a stylesheet — hiding it with CSS would only make the tenant believe their asset
is fine.

### K8 — A two-layer baseline diff proven not to be noisy

This is the capability usually sold as "visual regression", but rarely proven.

- **The pixel layer** catches what is visible; tolerance **0.1%**, and any solid block larger
  than 32×32 px stays `CHANGED` even at a small percentage (a change concentrated on a small
  logo can easily be < 0.1% of the page).
- **The metric layer** catches an asset swapped for a different version that happens to *look*
  similar. This is not a nice-to-have: without it, the diff is blind to exactly the class of
  change that costs the most.
- **Joined on `capture_id`, never on file order.** One failed cell shifts every row if the join
  uses an index — that is the classic way to produce 300 false `CHANGED`s.

Two proofs run automatically inside `make all`:

| Test | Result |
|---|---|
| **Flake** — two consecutive clean runs must show 0 changes | **SAME 300 · CHANGED 0** (2×) |
| **Swap 1 asset** — the system must flag it on its own | **SAME 290 · CHANGED 10**, all of them `b30-normal`, 0 false positives |

The detail that proves the metric layer is needed: `b30-normal__S1__*` differed by only **0.02%**
of pixels (a 35×10 bbox) — below tolerance — yet stayed `CHANGED` because `natural_w` moved
from 600 → 2000. Without the metric layer, that asset swap would have slipped through silently.

And the principle that was held: **tolerance is never raised to cover up flake.**

### K9 — Deliverables ready to hand over, not a folder of raw output

| Deliverable | Contents | Evidence on disk |
|---|---|---|
| **Offline static gallery** | 300 thumbnails on one page, tagged by class & severity, filters for class/surface/theme/severity, before-after slider, 30×10 heatmap | `web/` 20 MB · `web/thumbs/` 300 PNGs · `web/index.html` + `before-after.html` |
| **Excel workbook** | 5 sheets: Summary (56 rows, including an 8-term glossary) · Breakpoints (13) · Findings by Class (9) · Detailed Findings (186) · Assets (32) | `reports/REPORT.xlsx` |
| **One-pager PDF** | problem → approach → numbered results → examples → deliverables, **1 page** | `assets/v8_case_study.pdf` |
| **Breakpoint document** | 11 thresholds + quotable sentences + 5 asset acceptance rules | `docs/BREAKPOINTS.md` |
| **Paste-ready CSS** | 7 rules, one per class | `target/static/fixes.css` |
| **Walkthrough video** | 4 min 32 s walkthrough, 1920×1080, **no audio track**, captions **burned into the image** | `assets/v_walkthrough.mp4` (18 MB) |
| **Explainer video (EN)** | 125.0 s, 1920×1080, 30 fps, 10.5 MB, 12 segments, 32 burned-in captions, **no audio track** | `assets/explainer.mp4` |
| **English gallery** | chrome + **300 evidence screenshots** in English | `gallery_en/` 21 MB |
| **English report** | 182 evidence links | `reports/REPORT_EN.xlsx` |
| **Supporting visuals** | heatmap, breakpoint curves, before-after, architecture diagram, stat cards | `assets/v2`–`v8` (ID & EN) |

Gallery quality was tested with commands, not feelings: opened from `file://` headless →
**0 console errors, 0 failed requests, 0 broken images out of the 302 that have a `src`**, load
time 0.03 seconds. Absolutely offline: `grep -rnE 'https?://' web/` = **0**.

Video quality was tested structurally: `ffprobe` proves **0 audio tracks and 0 separate subtitle
tracks** — captions are burned into the image, so they stay readable in any player. The script
follows its own rules: **0 lines over 12 words**, 0 superlatives, code shown on only 8 lines
during the fix act. Frames were inspected one by one for leaks: **0 of the user's work windows,
0 private paths, 0 credentials, 0 third-party logos** across 20 sampled frames.

### K10 — The number guard: the report cannot lie

`scripts/check_numbers.py` compares **every number** claimed in `REPORT.xlsx`, the one-pager
PDF, `README.md`, the `web/` gallery, and **the video captions** against numbers recomputed
from the result files. Three layers: fact sheet vs recompute · named claims vs recompute ·
**sweep** — every number in the one-pager and the Summary sheet must be traceable to one of the
result files; an untraceable number is a **failure**.

**Result: 4133 numbers checked, 0 mismatches.** And the guard is proven to bite — a negative
test (changing `11` → `12` in the README, `300` → `317` in a caption) does make it fail.

The reason is not tidiness: **hand-typed numbers go stale the moment a run is repeated, and one
stale number is enough to make a client doubt the entire report.**

One real trap this guard caught: a video caption quoted the recording run's duration (62
seconds) — **a machine number, not a result number**. In a clean copy that number is not
reborn, so it was pinned explicitly along with its source file rather than left to match by
coincidence.

### K11 — A leak audit that actually rejects

`scripts/audit.py` works over the **shipped set**: the entire repo **minus** whatever
`.gitignore` excludes — the question is not "is my machine clean", but **"what ships along if
this folder is handed to someone else"**. Seven rules:

1. no third-party brand assets ship
2. credentials (`.env`, tokens, API keys, passwords)
3. absolute paths from this machine (`/home/<user>`) in docs, reports, gallery
4. files over 10 MB shipping
5. 36 third-party brand names matched against assets + manifests
6. external URLs in the gallery (it must be offline)
7. the legal statement must be present in the README

**Result: 861 files / 35.0 MB scanned · 2384 checks · 0 findings · exit 0.**

And — this is the part that is rarely there — **the audit is negatively tested**.
`make audit-bite` plants **7 bait files, one per rule**, confirms the audit rejects all seven and
exits 1, then removes the bait and confirms the audit is clean again. *An audit that never
rejects anything proves nothing.*

This audit also found a real defect on its very first run: two absolute machine paths in
`docs/TOOLS.md`. Those were **fixed, not whitelisted**.

### K12 — Reproducible on a clean copy, in one command

`make all` runs **8 stages from scratch**: target up → capture 300 (the "before" run) → detect +
lock baseline → breakpoint sweep → **two flake tests** → **asset-swap test** → fix run → gallery
→ report + number guard + audit.

Proven on a clean copy (`rsync` with none of the run output, 61 MB, ports shifted to 8131/8133
so it can run side by side with the original):

| Clean-copy test | Result |
|---|---|
| `make all` | **exit 0** |
| 5 runs × 300 cells | 300/300 every time, 0 failures, 60.8–61.3 s/run |
| findings-per-class diff (original vs clean) | **EMPTY** — 186 findings, C1 6 · C2 10 · C3 106 · C4 0 · C5 18 · C6 40 · C7 6 |
| breakpoint diff | **EMPTY** — 11 thresholds · 716 observations · 564 probe PNGs |
| flake | SAME 300 · CHANGED 0 (2×) |
| swap 1 asset | SAME 290 · CHANGED 10 |
| fix run | 186 → 18 (−90.3%) |
| number guard | 4133 numbers · **0 mismatches** |

**The hidden dependency this gate uncovered:** port `8130` turned out to be *hardcoded* in 5
places (`src/capture.py`, `scripts/verify_target.py`, `scripts/probe_ring_check.py`,
`scripts/demo_video.py`, `docker-compose.yml`) — meaning the clean copy would quietly have been
shooting the original run's target and "passing" for the wrong reason. All of them were moved to
env vars, with 8130 kept as the default so existing commands still work.

### K13 — Engineering discipline that can be audited

- **14 phases**, one phase = one session = one real artifact, with file-based cross-session
  memory (`STATE.md`, `docs/DECISIONS.md`, `docs/ACCEPTANCE.md`, `phases/phase-NN-*.md`).
- **17 locked decisions** (`D1`–`D17`) that outrank every other document and are **not
  renegotiated each session** — including the self-limiting ones (synthetic assets only, an
  owned target only, no git operations without explicit permission).
- **An explicit document hierarchy**: if a lower document contradicts a higher one, the lower
  one is fixed **in the same session**.
- **A per-phase Definition of Done** ticked only against real command output, never a claim.
- **12 acceptance criteria**, each with the command that proves it, not an empty checkbox.

### K14 — Environment engineering (Arch Linux, no sudo)

Playwright does not officially support Arch; the installed engines are `ubuntu24.04-x64` builds
that demand Ubuntu sonames (`libicuuc.so.74`, `libxml2.so.2`, `libflite*`) that do not exist on
Arch. The solution is neither `sudo` nor `pacman`:

- `playwright install-deps` **always fails** on Arch — it *hardcodes* `apt-get`
  (`spawn apt-get ENOENT`), so even a sudo password would not help, and the Arch packages do not
  match because their sonames differ (icu 78 ≠ 74).
- Libraries are patched in **user space** from a disposable `ubuntu:24.04` container, cached,
  then copied into `sys/lib` inside the WebKit bundle — which is already on its wrapper's
  `LD_LIBRARY_PATH`.
- **Both WebKit bundles** (`minibrowser-wpe` for headless, `minibrowser-gtk` for headed) must be
  patched; fixing only one breeds a bug that surfaces much later.
- `scripts/arch_provision.sh` is **idempotent and sudo-free**, and is copied into the deliverable
  repo so it never has to reach across projects.

Health verification: Chromium 151.0.7922.34 · Firefox 153.0 · WebKit 26.5.

### K15 — Bilingual deliverables from a single source of numbers

The gallery, report, one-pager, diagrams, and explainer video exist in **Indonesian and
English** — not as a forked script, but as separate generators that each read their own fact
sheet, plus a **language guard** (`scripts/check_language_en.sh`) that runs before the English
video is built.

And this is where the numeric discipline was tested hardest. The English video was filmed over
an **English evidence run** (because the gallery and report appear on screen), and that run
produced **slightly different** numbers:

| | production run (ID) | evidence run (EN) |
|---|---|---|
| findings | 186 → 18 · **−90.3%** · 164 cells | 182 → 18 · **−90.1%** · 162 cells |
| `BW-C7` | 6 | **2** |

The cause is real and was reported rather than smoothed over: English tenant names have
different text metrics, so two brands no longer overflow the card header. Every other class is
identical. The production run, the Indonesian gallery, and `REPORT.xlsx` were **left untouched**.

> The portfolio point: when two numbers disagree, the move is not to make them agree, but to
> **explain the cause and keep the two runs separate.**

### K16 — Legal and ethical boundaries enforced automatically

This is usually a throwaway paragraph. In this project it is **enforced by script**:

- **The test target is owned, full stop** — the capture engine is never pointed at anyone's
  site, platform, or property. Even "just one page for comparison" is not allowed without
  written authorization.
- **All brand assets are self-made synthetics** — no third-party logo is in the repo, and no
  affiliation is claimed. If a real logo is used locally for a sanity check, it goes into a
  gitignored folder and never appears in the gallery, video, or client attachments.
- Enforced by **`make audit` rules 1 and 5** (36 brand names matched against every asset and
  manifest) and **rule 7** (the legal statement must be present in the README).
- For a real client, the boundary is written first: it **is** allowed to run this pipeline
  against the client's staging with **written permission** and brand assets **the client
  themselves** provide; it is **not** allowed to pull logos from third-party sites and mount
  them on the client's property.

---

## 7. Numbers at a glance (for the portfolio page's stat cards)

| Metric | Number |
|---|---|
| Screenshots per run | **300** (0 failed cells) |
| Screenshots stored per run | 600 (300 full page + 300 slot crops) |
| Consecutive full runs with no failures | **5** |
| Time for one full run | **~61 seconds** (~200 ms/cell; fastest 148 ms/cell) |
| Findings before fixes | **186** across 164 cells · 6 of 7 classes populated |
| Severity | 115 High · 61 Medium · 10 Low |
| Findings after fixes | **18** (**−90.3%**), new findings: **0** |
| Classes closed 100% | **5** (C1, C2, C3, C6, C7) |
| Documented breakpoints | **11** · 716 observations · 564 probe PNGs |
| Closing CSS rules | **7** (56 lines, 29 declarations) |
| Asset acceptance rules | **5** |
| Flake between two identical runs | **0 / 300** (proven 2×) |
| Asset-swap test | **10 CHANGED / 290 SAME**, 0 false positives |
| Number guard | **4133 numbers checked, 0 mismatches** |
| Leak audit | **861 files / 35.0 MB · 2384 checks · 0 findings** |
| Audit negative test | **7/7 rules rejected their bait** |
| Unit tests | **184/184 green** |
| Lines of code | ~3,700 (engine) + ~2,000 (tests) + ~6,100 (scripts) + ~670 (target app) |
| Excel report sheets | **5** · 186 detailed findings · 186 evidence links, 0 broken |
| Work phases | **14** (P0–P13) |
| Locked decisions | **17** (D1–D17) |
| Acceptance criteria | **12**, proven **11 ✅ + 1 🟨** |

---

## 8. How to verify the claims above (real commands)

```bash
cd /home/rayin/Projects/Testing/brandwall

make env          # core tool versions + port status
make test         # 184 unit tests
make all          # the full 8-stage pipeline from scratch (~tens of minutes)
make audit        # leak audit over the shipped set → 0 findings, exit 0
make audit-bite   # negative test: 7 baits, the audit MUST reject all seven
make gallery-serve   # gallery at http://127.0.0.1:8132

# clean copy, running side by side with the original
BRANDWALL_TARGET_PORT=8131 BRANDWALL_GALLERY_PORT=8133 make all

# token-cheap inspection
wc -l data/<run_id>/captures.jsonl
jq -r '.class' data/<run_id>/findings.json | sort | uniq -c | sort -rn
jq length data/breakpoints.json
```

---

## 9. Limitations stated openly (do not hide these in the portfolio)

This section is exactly what makes the other claims credible.

| Limitation | Honest status |
|---|---|
| **A8 is still 🟨** | The gallery is proven to open without errors and to be offline, but the *"understandable without a verbal explanation"* part needs a non-technical human tester. That test has not been run — and was **deliberately not role-played by an AI**, because that would falsify the acceptance. The test protocol is ready (6 questions + a pass threshold written before testing). |
| **Publishing the gallery** | Permission exists, but the publishing path is technically blocked: GitHub Pages needs a public repo (this project is deliberately local), and Artifacts are capped at 16 MB while the gallery is 20 MB. It needs a slimmed gallery build (smaller / sprited thumbnails), not just an upload. |
| **Synthetic assets, not real logos** | A conscious (legal) decision. The extreme characteristics are reproduced in measured form, so the test results are identical — but this still has to be stated, not blurred. |
| **Desktop only** | Viewport 1440×900 (and 1200×630 for the share card). Multi-viewport / multi-engine testing is the scope of a different QA sweep project, not this one. |
| **The 18 remaining `BW-C5`** | Deliberately not closed with CSS. 404 assets and 0%-ink assets are rejected at the asset acceptance gate, because closing them with CSS would hide the problem from the tenant. |
| **`assets/v_demo.mp4`** | Not stored in the repo because of its size; rebuild it with `make video`. Its caption script is stored (`assets/sub_demo.srt`). The walkthrough and the EN explainer are on disk. |
| **Not pushed to a remote** | A local git repo with an initial commit; moving its contents off this machine requires separate permission. |

---

## 10. What can be offered to the next client

This pipeline is **portable**: the only client-specific parts are `target/` (the test pages) and
`assets/brands/` (the assets). Everything else — capture engine, detector, breakpoint sweep,
diff, gallery, report, number guard, audit — works against a data contract, not against one
particular product.

**Service packages that already have proof:**

1. **Brand Asset Stress Test** — the client sends N assets + staging access; the output is a
   screenshot matrix, numbered breakage classes, and asset acceptance rules.
2. **Multi-tenant / white-label Design QA Audit** — find which pages the branding breaks on,
   with the closing CSS per class.
3. **Accessibility Contrast Audit (WCAG 2.1)** — text and graphical-component contrast measured
   from real pixels, reported as ratios rather than pass/fail.
4. **Visual Regression Baseline** — a baseline plus a two-layer diff proven not to be noisy
   (0 flake across 300 cells) and proven to catch a nearly invisible asset swap.
5. **Asset Acceptance Rules** — a numeric gate for the product team: maximum ratio, minimum
   luminance, name length per script, fallback policy.
6. **Client Hand-off Pack** — offline gallery + Excel workbook with evidence links + one-pager
   PDF + captioned audio-free video, in two languages.

**Real working time for scope this size:** 14 structured sessions. For a typical client scope
(1 product, 20–50 assets, 3–5 surfaces) the pipeline already exists — what remains is adapting
the target, curating the assets, and writing the report.

---

## 11. Technical lessons worth telling (material for an "engineering notes" section)

Five real traps found **at the cost of real time** — and that is what separates experience from
theory:

1. **Mean luminance lies about small logos.** The mean of the difference mask swallows
   anti-aliased edge pixels, so the same logo measures paler the smaller it is rendered — enough
   to accuse the control asset on one surface and clear it on another. The fix: two-background
   unmix + an alpha ≥ 0.5 mask + discarding the edge ring.
2. **Zero findings does not mean clean.** `BW-C7` produced a difference of 0 across 300/300
   cells not because nothing was clipped, but because `white-space:nowrap` without
   `overflow:hidden` makes **the element stretch** — what broke was the row, not the element.
3. **A hardcoded port makes the reproduction gate pass for the wrong reason.** The clean copy was
   quietly shooting the original run's target. Found only because the gate was genuinely run on
   a different port.
4. **Machine numbers disguised as result numbers.** The run duration quoted in a video caption
   was the recorder's number, not a result number — in a clean copy it is never reborn. It had to
   be pinned explicitly along with its source file.
5. **A quality gate that never rejects anything is decoration.** Hence the audit has a negative
   test (`make audit-bite`), the number guard has a negative test (change one number, it must
   fail), and the detector has a control asset (`b30-normal` must yield 0 findings).

---

## 12. Repo structure (for the "behind the scenes" section)

| Path | Contents |
|---|---|
| `target/` | the app under test: FastAPI, 5 surfaces, 2 themes, **deliberately naive** CSS, bundled Noto fonts |
| `assets/brands/` | 30 synthetic test assets + `brands.json` (properties measured by script) |
| `assets/probes/` | probe assets for the breakpoint sweep |
| `src/` | the engine: `capture`, `detect`, `breakpoint`, `diff`, `report`, `run_matrix`, `schema`, `contrast` + 184 tests |
| `scripts/` | asset & probe generators, gallery, number guard, audit, video, Arch provisioning |
| `web/` · `gallery_en/` | static ID & EN galleries: contact sheet + before/after slider |
| `data/` · `baseline/` | immutable runs (JSONL + PNG) and the official baseline |
| `reports/` | `REPORT.xlsx`, `REPORT_EN.xlsx`, fact sheet JSON |
| `docs/` | 17 documents: locked decisions, schema, data dictionary, breakage classes, breakpoints, acceptance, ethics, architecture, manual verification protocol |
| `phases/` | 14 phase files — one phase = one session = one artifact |

---

## 13. Glossary (for non-technical readers of the portfolio page)

| Term | Short meaning |
|---|---|
| **Surface** | one type of page/component where a brand appears (listing card, article page, …) |
| **Matrix** | every combination under test: brand × surface × theme |
| **Capture / cell** | one combination, shot once; there are 300 here |
| **Breakage class** | a type of problem, not a list of brands. One fix rule closes one class |
| **Breakpoint** | the exact number at which the design starts to fail (ratio, luminance, name length) |
| **Baseline diff** | comparing today's output against already-approved output, to catch unintended changes |
| **Flake** | a false difference between two runs that should be identical |
| **WCAG contrast ratio** | the standard readability measure; 4.5:1 for normal text, 3:1 for large text & graphical elements |
| **Luminance** | how bright a color is (0 = black, 1 = white) |
| **Fallback** | the backup rendering when an asset fails to load |
| **Shipped set** | the files that actually travel along if this folder is handed to someone else |

---

*This document was assembled from `brandwall/README.md`, `STATE.md`, `CLOSEOUT.md`,
`docs/DECISIONS.md`, `docs/ACCEPTANCE.md`, `docs/BREAKAGE_CLASSES.md`, `docs/BREAKPOINTS.md`,
`docs/ARCHITECTURE.md`, `docs/TOOLS.md`, `docs/ETHICS.md`, `reports/REPORT_FACTS{,_EN}.json`,
the `Makefile`, and the code in `src/` + `scripts/`. Every number above comes from a result
file, not from memory.*
