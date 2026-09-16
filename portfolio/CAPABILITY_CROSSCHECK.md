# Capability Dossier — CrossCheck (Automated Web QA Sweep)

> **Source material for the portfolio page.** This document summarizes *what can be shown to
> a client* from the `crosscheck` project: the tools used, the skills proven, the numbers
> that can be defended, and the deliverables that actually exist on disk. Every claim here has
> a file or a command behind it.

| Meta | Value |
|---|---|
| Project name | **CrossCheck** |
| Category | Web QA · Cross-Browser / Cross-Device Testing · Role-Based Access Testing · E2E Flow Testing · Bug Triage & Reporting |
| Repo | `/home/rayin/Projects/Testing/crosscheck` — private GitHub repo on the personal account (`rayinailham/crosscheck`), latest commits `e572d87` / `cd6e5e3` |
| Status | **11/11 phases done** (P0–P10) · acceptance **11/11 ✅** · English explainer video done |
| Work period | 2026-08-23 → 2026-09-05 (11 phases, one phase = one session, plus an English video pass) |
| Target jobs | Upwork — *"Comprehensive QA Testing for New WordPress CRM and Dealer Management Platform"*, *"QA Tester for Web Application"*, *"QA Tester / QA Engineer – Manual + Automation"* |
| Proven scale | **40 pages × 3 browsers × 3 screen sizes × 3 user roles = 1,080 checks in 3.8 minutes**, plus 216 access checks and 5 end-to-end flows |

---

## 1. One-sentence pitch

> "I open every page of your web app in three browsers, three screen sizes, and three user
> levels, all in one command, and hand back a short spreadsheet of **unique, reproducible,
> verified issues** instead of a pile of logs. Each row has steps to reproduce, a screenshot,
> the affected browsers and devices, and a priority. Access leaks between roles get their own
> sheet."

The main differentiator: most automated QA stops at *"the script ran and printed errors."*
CrossCheck answers what the client is paying for: **"Which real problems do I have, how
do I reproduce each one, and can I trust that the list is complete and not noise?"** The
answer is in numbers: 881 raw signals → 18 unique issues, 562 false positives removed with
auditable rules, and 12/12 known bugs caught on every run.

---

## 2. The problem being solved (client framing)

A typical QA brief on Upwork (the WordPress CRM / dealer platform job is the model) asks for
all of these at once:

- test on **desktop, tablet, mobile** and **multiple browsers**
- check navigation, buttons, links, forms, search, filters, dashboards
- check **user permissions across roles**
- find broken layouts, overlapping elements, responsive issues, errors, failed actions,
  wrong data, slow pages
- deliver a **structured spreadsheet**: description, URL/section, steps to reproduce,
  expected vs actual, screenshot, browser & device, High/Medium/Low priority

Done by hand, that is hundreds of page views per role, repeated per browser and per screen
size. It takes days, the results can't be re-run next week, and the same bug gets reported
nine times because it appears in nine browser/screen combinations.

Three questions that manual testing usually cannot answer:

1. **How much of the app was actually covered?** (here: 1,080 combinations, shown as a heatmap)
2. **Is this list real or noise?** (here: every High issue and every access leak re-opened in a
   real browser before it enters the report; 0 false positives remain)
3. **Would you catch the same bugs again tomorrow?** (here: 12 known bugs planted in the target,
   caught 12/12 on every run)

---

## 3. System scope

### 3.1 The test matrix

| Axis | Values | Note |
|---|---|---|
| Pages | **72 discovered**, **40** selected for the full matrix | picked by a fixed rule (all bug pages → all permission-matrix pages → deterministic sample of public pages) |
| Browsers | **3** | Chromium 151, Firefox 153, WebKit 26.5 (Safari engine) |
| Screen sizes | **3** | desktop 1920×1080, tablet 768×1024, mobile 390×844 |
| User roles | **3** | `admin` (Administrator), `editor` (Editor), `viewer` (Subscriber) |
| Total matrix cells | **1,080** | 40 × 3 × 3 × 3 |
| Checks per cell | **11** automated detectors | see §3.3 |
| Extra layers | **216** permission checks (72 pages × 3 roles) + **5** end-to-end flows | access control and "saved but not really saved" bugs |

### 3.2 The test target: owned, realistic, with known bugs

The target is a **self-hosted WordPress 6.8.2 + a small CRM plugin** (Docker Compose,
MariaDB 11.4), bound to `127.0.0.1` only. It contains 55 pages and 7 posts in 4 categories,
generated deterministically by a seed plugin (seed version 4). The CRM area (customers,
leads, reports) and role-restricted admin pages make it structurally close to the
WordPress CRM/dealer platform in the job post.

**12 bugs were planted on purpose** (`docs/PLANTED_BUGS.md`), each mapped to the detector
that must catch it:

| ID | Where | Planted defect | Must be caught as |
|---|---|---|---|
| PB-01 | `/network-failure/` | `fetch()` to a REST endpoint that doesn't exist | `http_failed` |
| PB-02 | `/customer-profile/` | empty owner rendered as `undefined` | `text_leak` |
| PB-03 | `/broken-image/` | image points to a missing upload | `broken_image` |
| PB-04 | `/wide-report/` | fixed 1100 px block | `layout_overflow` (at 390 px) |
| PB-05 | `/dead-action/` | Export button is only `href="#"` | `dead_link` |
| PB-06 | `/admin/users/` | checks "logged in" instead of "is admin" | permission violation |
| PB-07 | `/console-error/` | `console.error()` from a widget | `console_error` |
| PB-08 | `/js-exception/` | reads a property of `undefined` | `js_exception` |
| PB-09 | `/slow-report/` | 4-second server delay | `slow_page` |
| PB-10 | `/overlap-toolbar/` | two buttons positioned over each other | `element_overlap` |
| PB-11 | `/empty-dashboard/` | main container never renders | `page_incomplete` |
| PB-12 | wp-admin → edit post → **CRM Owner** | save reports success but the field is never stored | end-to-end `flow_data_loss` |

> **Planted bugs are an oracle, never an input.** The detectors are generic. It is verified
> by command that none of the bug page slugs appear in the sweep code
> (`grep -c 'customer-profile\|wide-report\|slow-report' qa/sweep.py` = 0). The oracle only
> measures recall.

And the sweep found one problem that was **not** on the planted list: `CC-002`, the
`viewer` role can open the **CRM dashboard** (`/crm/`). The target's access rule only guards
pages *under* `/crm/` (`crosscheck_is_child_of('crm')`), so the parent page itself is
unguarded. This is the kind of gap a detector should find without being told where to look.

### 3.3 Eleven detectors, thresholds locked before the first run

The detector list is a **closed enum** (decision D1), and every threshold was written down
(D3) before the sweep engine existed, so nobody could tune it later to make the numbers look
good.

| Detector | Exact rule | What it catches |
|---|---|---|
| `console_error` | console event `type == "error"`, excluding favicon / DevTools noise / cross-origin | silent JavaScript breakage |
| `js_exception` | `pageerror` event, no filter | runtime crashes |
| `http_failed` | same-origin response with status ≥ 400 | dead APIs, missing assets |
| `slow_page` | `load` event > **3000 ms** | performance problems |
| `layout_overflow` | `scrollWidth > innerWidth + 2 px` | horizontal scroll on mobile |
| `element_overlap` | visible interactive elements overlapping ≥ **25%** of the smaller one | buttons that can't be clicked |
| `text_leak` | `undefined`, `NaN`, `[object Object]`, `Error:` in page text; standalone `null` | broken data binding |
| `broken_image` | visible `<img>` with `naturalWidth === 0` and `complete === true` | 404 images |
| `dead_link` | `href` is `#`, empty, or `javascript:void(0)` with no click handler | dead-end navigation |
| `page_incomplete` | a key element listed for that page is missing after load | half-rendered pages |
| `nav_failed` | navigation throws (timeout, DNS, connection) | infrastructure failures |

---

## 4. Architecture and data flow

```
qa/config.yaml + .env (credentials, never in YAML)
        │
        ▼
scripts/login.py ──► qa/auth/{admin,editor,viewer}.json   (saved login sessions)
        │
        ▼
scripts/discover.py ──► qa/routes.json   (72 pages: 58 sitemap · 6 seed · 5 crawl · 3 nav)
        │
        ├──────────────────────────┬──────────────────────────────┐
        ▼                          ▼                              ▼
qa/sweep.py (Playwright)     scripts/permissions.py        qa/flows.py (Playwright)
3 browsers × 3 sizes ×       httpx: 216 page×role checks   5 end-to-end flows as editor
3 roles × 40 pages           + real-browser re-check of    (create, search, update +
6 workers · SQLite resume    every VIOLATION / REVIEW       CRM Owner, reject empty, logout)
        │                          │                              │
        ▼                          ▼                              ▼
results.jsonl (1,080 rows)   permissions.csv (216 rows)     flows_results.json (5)
shots/ (failures + samples)  violations.json (3 verified)
        │                          │                              │
        └──────────────┬───────────┴──────────────────────────────┘
                       ▼
               qa/triage.py  ──► issues.json   (881 raw → 18 unique, 562 false positives removed)
                       ▼
               qa/report.py  ──► REPORT.xlsx (Security · Issues · Summary · Coverage)
                                 + qa/out/gallery/ (indexed, annotated screenshots)
                       ▼
     scripts/visuals.py · before_after.py · case_study.py · make_video.py
                                 ──► heatmap, permission grid, before/after, one-pager PDF, video
```

### Binding architectural rules

1. **Cheapest tool that still works.** Browser MCP for recon only (P1–P2); production runs are
   Playwright scripts; the 216 permission checks use plain `httpx` with each role's session
   cookies (no browser, seconds instead of minutes); a real browser is launched only to confirm a
   suspected violation.
2. **Log in once per role, not once per page.** Saved `storage_state` sessions are reused
   across the whole matrix. A session guard re-authenticates if a page bounces to the login
   screen.
3. **One browser per worker, many pages inside it.** Loop order: browser (most expensive) →
   role → viewport → page (cheapest).
4. **The detector is generic.** It knows nothing about the planted bugs.
5. **Result files follow a locked schema** (`docs/SCHEMA.md`), written before the engine.
6. **The target is fixed, not the detector.** When the target produced noise (see K9), the
   target was corrected and the thresholds stayed.

---

## 5. Tools used and proven in this project

| Tool | Used for | Why this one |
|---|---|---|
| **Playwright (Python, sync API) 1.62** | sweep engine, flows, browser re-verification, PDF rendering | the only mainstream API that drives Chromium, Firefox **and** WebKit in one run |
| **Chromium 151 · Firefox 153 · WebKit 26.5** | the three engines under test | WebKit is the Safari engine, which usually goes untested |
| **httpx** | 216 permission checks with role cookies | thousands of requests per minute, no browser needed |
| **tenacity** | retry with exponential backoff | retries **only** timeouts, network errors, and 429/500/502/503/504, never 403/404 (those are findings) |
| **SQLite** | `progress.db` checkpoint table for resume | no server, one file |
| **typer** | CLI flags (`--browser --viewport --role --workers --resume`) | self-documenting CLI |
| **openpyxl** | `REPORT.xlsx` with conditional formatting | the report builds without Excel installed |
| **matplotlib + Pillow** | coverage heatmap, permission grid, findings charts, annotated before/after images | deterministic PNG output |
| **Docker Compose** | WordPress 6.8.2 + MariaDB 11.4 target, loopback-only | a disposable target where bugs can be planted |
| **PHP (WordPress must-use plugin)** | seed content, CRM pages, planted bugs, target fixes | the whole target is one reviewable file (296 lines) |
| **ffmpeg** | trimming, speed-up (`setpts`), burned-in captions, concat, H.264 1080p | CLI video editing that can be repeated |
| **wf-recorder** (built from source into `~/.local`) | single-window screen recording on Wayland | the packaged version would have forced a system-wide ffmpeg upgrade |
| **PlantUML / Graphviz** | architecture diagrams (`.puml` ID, `.dot` EN) | source kept next to the PNG, can be edited |
| **GNU Make** | `make all` one-command pipeline, 13+ targets | `just` isn't installed; `make` is available everywhere |
| **uv (Python 3.13)** | venv + lockfile | the client only needs `uv sync` |
| **unittest** | engine and flow tests | no extra dependency |
| **jq / wc / sort / uniq** | token-cheap inspection of `results.jsonl` | the raw file is never read into context |

### MCP servers used (and their limits)

| MCP | Used for | Limit held |
|---|---|---|
| `playwright` | recon in P1–P2: login form selectors, wp-admin menu (`#adminmenu`), hidden routes | **not** used to run the sweep (too token-expensive for 1,080 cells) |
| `chrome-devtools` | deeper console/network inspection during recon | pinned to Chromium revision 1228, which is deliberately never pruned |
| `excel` | inspecting the finished workbook | the workbook itself is generated by `openpyxl` |
| `serena` | symbol lookup once the codebase grew | not a substitute for reading the file |

### Skills / methodologies applied

| Skill | Used in | For what |
|---|---|---|
| `phase-harness` | whole project | 11 phases, one phase = one session = one artifact; `STATE.md` as the only cross-session memory |
| `arch-playwright-provision` | P0 + every session | three engines on Arch Linux without sudo |
| `web-recon` pattern | P1–P2 | route map, login flow, key selectors before writing any script |
| `qa-sweep` | P3–P4 | matrix loop, per-cell checks, screenshot policy |
| `oracle-target` | P1, P3, P7 | planted-bug target + recall gate (12/12) |
| `triage-engine` | P7 | normalization, auditable suppression, dedupe, priority, non-technical wording |
| `durable-queue-worker` pattern | P4 | SQLite checkpoint + resume proven by killing a run mid-way |
| `deliverable-pack` | P8–P9 | spreadsheet + gallery + one-pager + captioned video |
| `evidence-guard` | P10 | secret-leak audit + clean-copy reproduction gate |
| `device-screen-recording` | P9 + EN video | one allowlisted window on a disposable virtual output, never the physical monitor, never audio |

---

## 6. Proven capabilities (the core of the portfolio page)

Each capability below can be claimed to a client, and each comes with its proof.

### K1 — Automatic page discovery

The page list is not typed by hand. `scripts/discover.py` builds `qa/routes.json` from four
sources, in order: seed pages from config → `wp-sitemap.xml` → the wp-admin menu found during
recon → a same-origin crawl of internal links (depth 3), skipping anything destructive.

**Result: 72 pages discovered from 6 seeds** (58 from the sitemap, 5 from the crawl, 3 from the
admin nav). Each page gets a `type`, an `area` (its row in the permission matrix, or `public`),
and the `key_elements` that must exist for it to count as fully rendered.

### K2 — 1,080 combinations in under 4 minutes, with resume

| Metric | Value |
|---|---|
| Combinations | **1,080 / 1,080** done, exit 0, 0 schema violations |
| Runtime | **230.93 s (3.8 min)** with 6 parallel workers ≈ 214 ms per combination |
| Acceptance target | < 15 minutes → met with a large margin |
| Clean-copy run | 275.29 s on a fresh copy |
| Failed / passed cells | 422 / 658 |
| Raw findings | 877 across 10 detector kinds (`nav_failed` = 0) |

**Resume is proven, not assumed.** A 360-cell run was killed at row 121
(`progress.db`: done = 121, pending = 239), then restarted with `--resume`: exactly 239 new
rows, 360 total, 360 unique keys, **0 duplicates**, `resume_used: true`.

**Retry policy is proven too.** The log shows **0 retries** even though there were **99 HTTP 403
responses**. A 403 means the page refused access, so it is recorded as a result. It is not a
network hiccup to retry.

### K3 — Session handling that doesn't re-login 1,080 times

Each role logs in once; its session (`storage_state`) is reused for every page. The session
guard was tested on purpose: cookies were wiped mid-test, the engine detected the bounce to
`/wp-login.php`, logged in again, and the page result was still correct.

### K4 — Evidence screenshots with a clear policy

Screenshots are saved for **every failed combination** plus **one passing control sample per
browser × screen size** (decision D4). File names are predictable:
`{role}_{browser}_{viewport}__{page}.png`.

**Result: 422 failure screenshots + 9 control samples = 431, 0 orphans** (24 MB in total,
including permission and flow evidence). Height is capped at 4,000 px so a runaway page can't
produce a giant file.

### K5 — Role-based access testing (the finding clients value most)

Every one of the **72 pages is checked for each of the 3 roles = 216 cells**, against a
written policy of who *should* be allowed (`docs/TARGET.md`). Every cell gets a verdict:
`OK`, `VIOLATION` (should be denied, was allowed), `BROKEN_ACCESS` (should be allowed, was
denied), or `REVIEW` (ambiguous).

Fast path first, real browser second: `httpx` with each role's cookies classifies all 216
cells in seconds; then **every** `VIOLATION` and `REVIEW` is re-opened in a real Chromium
browser, with a screenshot, before it can enter the report. `REVIEW` must reach zero before
the phase can close.

| Result | Count |
|---|---:|
| Cells checked | **216** (0 empty) |
| `OK` | 213 |
| `VIOLATION`, browser-verified | **3** |
| `REVIEW` remaining | **0** |
| False positives in `violations.json` | **0** |

The three violations:

| ID | Page | Role | What happened |
|---|---|---|---|
| PERM-001 | `/admin/users/` | editor | user directory visible (HTTP 200) |
| PERM-002 | `/admin/users/` | viewer | user directory visible (HTTP 200) |
| PERM-003 | `/crm/` | viewer | CRM dashboard visible (HTTP 200); not a planted bug |

A known WordPress behaviour was handled correctly: subscribers *are* allowed into `/wp-admin/`
but only see their own profile. That is written into the policy as "allowed, limited" and is
**not** reported as a leak.

### K6 — End-to-end flows that assert the data, not the screen

Five business flows run in wp-admin as the `editor` role. Each one checks the **stored data
after a reload**, not just the success message:

| Flow | Result | Time |
|---|---|---:|
| Create post | ✅ passed | 1.44 s |
| Search post | ✅ passed | 0.36 s |
| Update post + **CRM Owner** field | ❌ **`flow_data_loss`** at step 5 | 1.28 s |
| Reject empty post (negative test) | ✅ passed | 0.67 s |
| Login and logout | ✅ passed | 0.15 s |

The failure is exactly the class of bug that manual click-through testing misses: WordPress
shows "Post updated" (success), but after a reload the CRM Owner value is gone. The flow
catches it **without the flow code knowing that PB-12 exists**.

Test data is tagged with the run ID and **cleaned up at the end** (moved to trash, count
logged), so repeated runs don't pollute the app.

### K7 — Triage: 881 raw signals → 18 unique issues

Raw signals are not a report. `qa/triage.py` turns them into issues a developer can act on:

1. **Normalize** each detail message (numbers → `<n>`, hex IDs → `<id>`, timestamps → `<ts>`,
   URL query strings stripped) so the "same error with a different ID" collapses into one.
2. **Suppress false positives with declared rules**, never by hand:
   - findings on a page where the role was *correctly* denied (a 403 is not a bug on that page)
   - WordPress core admin UI patterns (`href="#"` Screen Options / Help handled by jQuery,
     admin toolbar overlap)
   - one-off timing spikes: a `slow_page` must repeat in **3+ cells** to count
3. **Deduplicate across browsers, screen sizes and roles** on (page, kind, normalized detail).
4. **Merge** permission violations (by page) and failed flows into the same issue list.
5. **Prioritize**: access leaks and data loss = High; functional/visual defects = Medium;
   leaked internal values = Low.
6. **Write steps to reproduce, expected, actual**, list affected browsers/devices/roles, attach
   the screenshot, and assign stable IDs (`CC-001`…).

| Triage metric | Value |
|---|---|
| Raw signals | **881** (877 sweep + 3 permission violations + 1 failed flow) |
| False positives removed | **562**, all by declared rules |
| Unique issues | **18** |
| Compression | **48.9 : 1** |
| Priority split | **3 High · 14 Medium · 1 Low** |
| Security issues (flagged separately) | **2** |
| Duplicates left | **0** |
| Oracle recall | **12 / 12** |

The count reconciles exactly: 877 sweep findings − 562 false positives = **315** sweep
occurrences, and the sum of `occurrences` over the 15 sweep issues is also 315.

The triage logic has a built-in self-test (`python qa/triage.py --self-test` → 6/6), and a
validator refuses to write `issues.json` if any issue lacks steps, expected/actual, affected
browsers, or an existing screenshot file.

### K8 — A report a non-technical client can read

`REPORT.xlsx`, four sheets:

| Sheet | Contents |
|---|---|
| **Security** (first, because it's non-empty) | the 2 access-control issues |
| **Issues** | 18 rows, exact QA columns: No · Issue · URL/Section · Steps to Reproduce · Expected · Actual · Screenshot · Browser & Device · Priority · Status |
| **Summary** | counts by priority and by module/area, coverage numbers, one-paragraph conclusion |
| **Coverage** | 40 pages × 27 role/browser/size columns, PASS/FAIL with conditional formatting |

A real row from the English report:

| Field | Value |
|---|---|
| No | CC-003 |
| Issue | CRM Owner changes disappear after saving |
| Steps | 1. Sign in as Editor. 2. Open /wp-admin/. 3. Edit both fields, save, reload, and compare both values. |
| Expected | The title and CRM Owner remain saved after reloading. |
| Actual | CRM Owner disappears and is appended to the title after reloading. |
| Browser & Device | Chromium · Desktop · Roles: Editor |
| Priority | High |

Readability is enforced by code, not by hope: the report validator **rejects tool jargon**
(`networkidle`, `pageerror`, `storage_state`, …) and fails the build if any screenshot link is
broken. **Result: 18/18 screenshots linked, 0 jargon.** The report also exists in English
(`reports/REPORT_EN.xlsx`), with the same structure.

The report is paired with `qa/out/gallery/`, an indexed screenshot gallery where every issue
has a thumbnail and High issues have an annotated version (red box + caption).

### K9 — Fix the target, don't loosen the detector

Twice, the target produced results that were technically true but useless. Both times the
**target was corrected** and the detector thresholds stayed untouched:

- **D17, theme placeholder navigation.** The WordPress block theme ships a demo menu with 8
  `href="#"` links on every page → by the locked rule, **1,080/1,080 cells would fail** as
  `dead_link`, the real dead-link bug (PB-05) would be drowned out, and the 9 clean control
  samples would be impossible. Fix: a render filter maps those 8 labels to real pages. Proof:
  `href="#"` = 0 on every page except `/dead-action/` = 1.
- **D18, "Welcome to the editor" modal.** On a fresh install, WordPress's one-time onboarding
  modal covers the Publish button → 4 of 5 flows failed as `flow_blocked` in the clean copy.
  The original environment had never shown it because the modal had been dismissed by hand
  earlier, which means the result depended on manual state that doesn't reproduce. Fix: the
  target disables the modal per user, idempotently. Adding "close the modal if present" to the
  test code would only have hidden the dependency.

> Portfolio point: **when the numbers look wrong, find out whether the app or the test is
> lying, and fix the one that is actually wrong, without moving the thresholds.**

### K10 — Measured recall: the tool still catches the known bugs

`scripts/verify_oracles.py` confirms the 12 planted bugs are alive on the target before any
run, and triage reports recall as `caught / 12`.

**Result: 12/12, 0 missed**, re-checked after every target change (D17, D18). If the
detector ever regresses, it shows up in that run, not in a client report.

How the 18 issues map back:

| Source | Issues |
|---|---|
| PB-01…PB-11 (page bugs) | 15 issues. PB-03 produced 3 (image, request, console), PB-01 produced 2, PB-08 split per browser (3 different exception messages across Chromium / Firefox / WebKit) |
| PB-06 (access) | `CC-001` (editor + viewer on `/admin/users/`) |
| PB-12 (data loss) | `CC-003` |
| **Not planted** | `CC-002` (viewer on `/crm/`) |

### K11 — One command, reproducible on a clean copy

`make all` = setup → target up → oracle check → login → discover → sweep → permissions →
flows → triage + report. `.NOTPARALLEL:` is set on purpose because the user shell exports
`MAKEFLAGS=-j16`, which would otherwise run pipeline stages out of order.

Proven on a clean `rsync` copy with a new `.env` built from `.env.example`, a **different port
(8091)** and a different Compose project name, so it runs next to the original without touching
it:

| Clean-copy test | Result |
|---|---|
| `make all` | **exit 0 in 5 min 35 s** |
| `REPORT.xlsx` | produced |
| Issues | **18, identical** to the main run (ID, priority, kind) |
| Raw findings | 876 vs 877 (after D18); triage output identical |

The first clean-copy attempt **failed**, and that is the point of the gate. It exposed the
D18 onboarding-modal dependency, which would otherwise have shipped.

### K12 — Leak audit before anything leaves the machine

`make audit` (`scripts/secret_audit.py`) checks three layers:

1. every literal value in `.env` is searched across the repo; **secret-class values
   (password / secret / token / API key) must appear in 0 files**
2. `.env`, `qa/auth/` (session cookies) and `qa/out/` must be git-ignored and **0** of them
   tracked
3. `REPORT.xlsx` is unzipped and scanned for passwords and real host URLs

**Result: CLEAN, 0 leaks.** 5 secret-class values appear in 0 files, 0 sensitive files
tracked, the report has 0 passwords and 0 host URLs. The audit was run as a gate before the
P2–P10 commit was pushed to the private repo.

It is also reported honestly: identity-class values (`admin`, `editor`, `viewer`,
`crosscheck`) *do* appear in many files. They are demo account names on a loopback target,
not secrets.

### K13 — Visuals that sell the work without a call

| Visual | Contents | File |
|---|---|---|
| **V1 Coverage heatmap** | 40 pages × 9 browser/size combinations, green / yellow / red | `assets/v1_heatmap.png` · `_en` |
| **V2 Permission grid** | 72 pages × 3 roles, violations in red | `assets/v2_permissions.png` · `_en` |
| **V3 Demo video** | 85.5 s, 1920×1080, burned-in subtitles | `assets/v3_demo.mp4` (Indonesian) |
| **V4 Before/after** | 3 annotated pairs (red box + one-line caption) | `assets/v4_before_after_{1,2,3}.png` · `_en` |
| **V5 Architecture** | pipeline diagram with human decision points | `assets/v5_architecture.{puml,png}` · `_en.{dot,png}` |
| **V6 Findings chart** | issues by priority and by area | `assets/v6_findings.png` · `_en` |
| **V7 Number card** | headline numbers for profile/proposal | `assets/v7_numbers.png` · `_en` |
| **V8 One-page case study** | problem → approach → numbers → examples → deliverables, **1 A4 page** | `assets/v8_case_study.pdf` · `_en.pdf` |
| **English explainer video** | 126.87 s, 1920×1080, 30 fps, H.264, 4.8 MB, 11 segments, **5 real screen recordings**, **0 audio tracks** | `assets/explainer.mp4` |

Every image is under 2 MB (largest 0.23 MB). All numbers on the one-pager trace to a result
file (40 pages · 1,080 combinations · 422 failed · 877 findings · 3.8 min · 6 workers · 431
screenshots).

The explainer video follows strict honesty rules:

- **No sweep was re-run to film it.** The terminal segment prints numbers read live from the
  result files.
- The "progress" segment is a **replay** of a recorded 810-combination demo run, with a
  permanent on-screen banner (`REPLAY of a recorded run`) and the line *"No browser was
  launched to draw this screen"*, so it can never pass as a live run.
- `ffprobe` confirms **0 audio streams**. Captions are burned into the image and readable in
  any player.
- A **language guard** (`make language-check-en`) scans 14 English text sources + 10 generated
  assets for Indonesian stopwords and is called from the video build script, so a rebuild can't
  quietly slip back into Indonesian.

### K14 — Engineering discipline that can be audited

- **11 phases**, one phase = one session = one artifact; `KICKSTART.md` is a single universal
  prompt, and the agent works out its own position from `STATE.md`.
- **18 locked decisions** (D1–D18) that outrank every other document: detector enum,
  thresholds, screenshot policy, page sampling rule, permission defaults, verdict enum, git
  policy, and so on. They aren't renegotiated each session.
- **A locked result schema** (`docs/SCHEMA.md`) written before the engine.
- **Per-phase Definition of Done**, ticked only against real command output.
- **11 acceptance criteria** (A1–A11), each with the command that proves it.
- **Token discipline**: `results.jsonl` is aggregated with `jq`, never read raw; screenshots
  are counted with `ls | wc -l`, not opened one by one.

### K15 — Environment engineering (Arch Linux, no sudo)

Playwright does not officially support Arch. Its engines are `ubuntu24.04-x64` builds, and
WebKit needs Ubuntu library versions (`libicuuc.so.74`, `libxml2.so.2`, `libflite*.so.1`) that
Arch doesn't ship.

- `playwright install-deps` **cannot work** here: it hardcodes `apt-get`
  (`spawn apt-get ENOENT`), so even a sudo password wouldn't help, and Arch's own packages have
  different sonames (icu 78 ≠ 74).
- The libraries are pulled from a disposable `ubuntu:24.04` container, cached
  (`~/.cache/crosscheck/webkit-ubuntu24-libs.tar`, ~65 MB), and copied into the WebKit bundle's
  own `sys/lib`, which is already on its `LD_LIBRARY_PATH`.
- **Both** WebKit bundles are patched: `minibrowser-wpe` (headless) and `minibrowser-gtk`
  (headed). The first fix only covered headless, and a later check found **17 libraries still
  missing** in the headed bundle.
- `scripts/arch_provision.sh` is idempotent, sudo-free, re-scans with `ldd` and **fails hard**
  if anything is still missing, then proves a real launch of all three engines.
- Screen recording on Wayland: `wf-recorder` was **built from source** against the existing
  ffmpeg 8.1.2, because the packaged version would have pulled ffmpeg 9 and broken `mpv` / VLC.

Health check: `chromium: 151.0.7922.34 · firefox: 153.0 · webkit: 26.5`.

### K16 — Scope and legal boundaries stated up front

The README says what CrossCheck **does not** do, because that's what makes a client trust
the rest:

- **Not penetration testing.** It checks whether the wrong role can open the wrong page. It
  doesn't look for SQL injection or XSS, and it doesn't exploit anything.
- **Not load testing.** One user session per combination. "Slow" means slower than 3 s when
  the server is quiet.
- **Doesn't fix bugs.** It reports them with evidence and reproduction steps.
- **Doesn't replace human functional testing.** It doesn't know whether the business rules are
  right.
- **Web only.** Mobile means screen-size emulation, not native apps.

Legal: run it **only** against your own app or one you have written permission to test. It
signs in as real users and opens restricted pages. The demo target is bound to `127.0.0.1`
because it contains deliberate access bugs and weak credentials. The demo numbers come from
that planted-bug target, **not** from a real client application.

---

## 7. Numbers at a glance (for the portfolio page's stat cards)

| Metric | Number |
|---|---|
| Pages discovered automatically | **72** (from 6 seeds) |
| Pages in the full matrix | **40** |
| Browsers × screen sizes × roles | **3 × 3 × 3** |
| Combinations per run | **1,080** (exit 0) |
| Full sweep runtime | **3.8 min** (230.93 s, 6 workers, ~214 ms per combination) |
| Raw signals → unique issues | **881 → 18** (48.9 : 1) |
| False positives removed by rule | **562** |
| Priority | **3 High · 14 Medium · 1 Low** · 2 security |
| Permission checks | **216** → **3** verified violations · 0 REVIEW left |
| End-to-end flows | **5** → 4 passed · 1 data-loss bug caught |
| Planted-bug recall | **12 / 12** |
| Bugs found outside the planted list | **1** (viewer can open the CRM dashboard) |
| Evidence screenshots | **431** (422 failures + 9 control samples), 18/18 issues linked |
| Resume test | killed at 121/360 → resumed 239 → **0 duplicates** |
| Retries on 403/404 | **0** (out of 99 × 403) |
| Clean-copy `make all` | **exit 0 in 5 min 35 s**, 18 identical issues |
| Leak audit | **0 leaks** |
| Report jargon | **0** |
| Explainer video | **126.87 s**, 1080p, 0 audio tracks, 5 real screen recordings |
| Demo video | **85.5 s**, 1080p, subtitled |
| Code | ~5,860 lines (engine, scripts, target plugin, tests) |
| Phases · decisions · acceptance | **11** · **18** · **11/11 ✅** |

---

## 8. How to verify the claims above (real commands)

```bash
cd /home/rayin/Projects/Testing/crosscheck

bash scripts/arch_provision.sh                      # 3 engines ready on Arch, no sudo
bash scripts/seed_target.sh                         # target up + idempotent seed
uv run --no-sync python scripts/verify_oracles.py   # must print 12/12

make all          # full pipeline -> REPORT.xlsx
make test         # unit tests (sweep + flows)
make audit        # leak audit -> "BERSIH — 0 kebocoran" (clean, 0 leaks), exit 0
make help         # every single-stage target

# token-cheap inspection
wc -l qa/out/results.jsonl                                      # 1080
jq -r '.findings[].kind' qa/out/results.jsonl | sort | uniq -c  # 877 findings by kind
jq length qa/out/issues.json                                     # 18
cut -d, -f7 qa/out/permissions.csv | sort | uniq -c              # 213 OK / 3 VIOLATION
jq -c '.[] | {name,status,kind}' qa/out/flows_results.json

# clean copy, side by side with the original
TUT_PORT=8091 COMPOSE_PROJECT_NAME=crosscheck-tut-clean make all
```

---

## 9. Limitations stated openly (do not hide these in the portfolio)

| Limitation | Honest status |
|---|---|
| **Demo target, not a client app** | All numbers come from an owned WordPress + CRM target with 12 planted bugs. The pipeline is generic, but the page must say it's a demo. |
| **Oral pitch rehearsal** | The only unticked DoD item in P10. The 2-minute script is ready (`docs/PITCH.md`, ≈124 s at 150 wpm), but only a human can rehearse it. |
| **Artifacts pre-date D18** | `REPORT.xlsx` and the P9 visuals were generated before the D18 target fix. The post-D18 clean run gave 876 findings (vs 877) and **the same 18 issues**, so the artifacts were kept rather than regenerated, to keep every number consistent. |
| **"877 → 18, 49:1" in the README** | The README pairs 877 (sweep only) with a 49:1 ratio. The exact triage figure is **881 → 18 = 48.94:1** (881 includes 3 permission violations + 1 failed flow). Use 881 / 48.9:1 on the portfolio page. |
| **Permission checks are desktop-Chromium verified** | The fast pass is HTTP-level; each violation is confirmed in one real browser (Chromium desktop), not in all 9 browser/size combinations. |
| **`--high-verified` is an attestation flag** | High issues are marked `verified` because the oracle and permission scripts re-checked them in a real browser. The flag records that fact; it doesn't re-run the check itself. |
| **1 of 6 unit tests needs the live target** | `test_session_guard_reauthenticates_once` logs in to the real target. On 2026-09-13 it failed because the target's database container was stopped (`crosscheck-tut-db-1` exited); the other 5 tests passed. Run `scripts/seed_target.sh` first. |
| **Demo video is Indonesian** | `assets/v3_demo.mp4` has Indonesian subtitles; the English piece is `assets/explainer.mp4`. |
| **Repo is private** | Making it public needs a separate permission, after one more audit. |
| **Not pen-testing, not load testing** | See K16. That's the scope boundary. |

---

## 10. What can be offered to the next client

The pipeline is **portable**: the client-specific parts are `qa/config.yaml` (base URL,
seed pages, critical flows), `.env` (test credentials), and `docs/TARGET.md` (who should see
what). Discovery, sweep, permission matrix, flows engine, triage, report, gallery, and audit
work against a data contract, not against one particular app.

**Service packages that already have proof:**

1. **Cross-Browser / Cross-Device QA Sweep.** Every page × Chromium/Firefox/WebKit ×
   desktop/tablet/mobile, delivered as a spreadsheet of unique issues with steps, screenshots,
   and priority. (Fits: *"QA Tester for Web Application"*, *"WordPress CRM & Dealer Platform
   QA"*.)
2. **Role & Permission Audit.** Page × role matrix against your intended policy; every leak
   verified in a real browser before it's reported. (Fits: marketplaces with student / coach /
   admin roles, CRMs with sales / manager / admin.)
3. **Critical Flow Automation.** Create / search / update / negative / logout flows that
   assert the stored data after a reload; reusable as a regression suite for the
   *Build → Test → Report → Fix → Retest* loop. (Fits: *"QA Engineer – Manual + Automation"*.)
4. **Bug Triage & Report Clean-up.** Turn noisy automated output (or another tool's log) into a
   short, deduplicated, prioritized list a developer can pick up.
5. **Regression Re-run.** Same command after the fixes; the same IDs and the same evidence
   format make "verified fixed" a diff, not an opinion.
6. **Client Hand-off Pack.** Spreadsheet (Security / Issues / Summary / Coverage), screenshot
   gallery, one-page case study, and a captioned, audio-free video.

**Real working time at this scope:** 11 structured sessions to build from zero. For a typical
client app (1 web app, 3 roles, a few dozen pages) the pipeline already exists; the remaining
work is configuring URLs/roles/flows, writing the permission policy, running it, and reviewing
the High items by hand.

---

## 11. Technical lessons worth telling (material for an "engineering notes" section)

Real traps, each paid for in time:

1. **Theme boilerplate can fail every page.** A demo navigation menu full of `href="#"` would
   have marked 1,080/1,080 cells as failed and buried the real dead-link bug. The fix belonged in
   the target, not in a looser threshold.
2. **A test that passes only on your machine depends on hidden state.** The editor's welcome
   modal had been dismissed by hand months earlier, so only a genuinely clean copy showed that
   4 of 5 flows were blocked.
3. **403 is a result, not a failure to retry.** Retrying 403/404 inflates runtime and turns
   access findings into "flaky network" noise. Retry only timeouts, network errors, and
   429/5xx.
4. **"Saved" is not the same as stored.** The CRM Owner bug shows a success message. Only an
   assertion *after reload* catches it.
5. **A correctly denied page still produces errors.** When a viewer is (rightly) denied a page,
   the 403 and its console noise are expected behaviour. Without a rule that cross-references
   the permission matrix, triage would report the security control itself as a bug.
6. **Fixing only one WebKit bundle creates a delayed bug.** The headless bundle worked; the
   headed bundle was still missing 17 libraries and would have broken the first time anyone
   debugged visually.
7. **`MAKEFLAGS=-j16` in the user's shell silently parallelizes a pipeline.** `.NOTPARALLEL:` in
   the Makefile keeps stages in order.
8. **A replayed screen must say it's a replay.** Honest demo footage gets a permanent banner
   instead of passing off an old run as a live one.

---

## 12. Repo structure (for the "behind the scenes" section)

| Path | Contents |
|---|---|
| `target/mu-plugins/crosscheck-tut.php` | the whole test target: seed content, CRM pages, 12 planted bugs, D17/D18 target fixes |
| `docker-compose.yml` | WordPress 6.8.2 + MariaDB 11.4, bound to `127.0.0.1:${TUT_PORT}` |
| `qa/config.yaml` · `qa/routes.json` | base URL, roles, seeds, flows · the 72 discovered pages |
| `qa/sweep.py` | the matrix engine: 11 detectors, session guard, retry, SQLite resume, screenshot policy |
| `qa/flows.py` | 5 end-to-end flows with post-reload assertions and run-ID cleanup |
| `qa/triage.py` | normalization, rule-based suppression, dedupe, priority, stable IDs |
| `qa/report.py` | `REPORT.xlsx` (4 sheets) + annotated gallery + jargon/evidence validator |
| `scripts/` | provisioning, seed, login, discovery, permissions, oracle check, visuals, case study, video, audit, English variants + language guard |
| `qa/out/` (git-ignored) | `results.jsonl`, `run_summary.json`, `permissions.csv`, `violations.json`, `flows_results.json`, `issues.json`, `shots/`, `gallery/`, `gallery_en/` |
| `assets/` | V1–V8 visuals (ID + EN), demo video, explainer video, one-page case study |
| `REPORT.xlsx` · `reports/REPORT_EN.xlsx` | client report, Indonesian and English |
| `docs/` | DECISIONS (D1–D18), SCHEMA, TARGET, ACCEPTANCE, PLANTED_BUGS, SKILLS, VISUALS, PITCH, VIDEO_PLAN |
| `phases/` | 11 phase files, one phase = one session = one artifact |

---

## 13. Glossary (for non-technical readers of the portfolio page)

| Term | Short meaning |
|---|---|
| **Sweep** | opening every selected page in every browser / screen size / role combination and running the checks |
| **Combination / cell** | one page × one browser × one screen size × one role; there are 1,080 here |
| **Role** | a user level (admin, editor, viewer) with different permissions |
| **Permission violation** | a role can open a page it should be denied |
| **End-to-end flow** | a full user task (create → save → reload → check) run automatically |
| **Raw signal / finding** | one detector hit in one combination, before any clean-up |
| **Triage** | merging duplicates, removing false positives, and prioritizing, so raw signals become issues |
| **False positive** | a signal that looks like a bug but isn't one |
| **Planted bug / oracle** | a bug put into the test app on purpose, to prove the tool still catches it |
| **Recall** | how many of the known bugs were caught (12 / 12) |
| **Resume** | continuing an interrupted run without redoing finished work |
| **Clean copy** | a fresh copy of the project run from scratch, to prove the results reproduce |
| **WebKit** | the browser engine behind Safari |

---

*This document was assembled from `crosscheck/README.md`, `STATE.md`, `PLAN.md`,
`docs/DECISIONS.md`, `docs/ACCEPTANCE.md`, `docs/SCHEMA.md`, `docs/TARGET.md`,
`docs/PLANTED_BUGS.md`, `docs/SKILLS.md`, `docs/VISUALS.md`, `docs/VIDEO_PLAN.md`,
`docs/PITCH.md`, `env-check.md`, the `phases/` files, the `Makefile`, the code in `qa/` +
`scripts/` + `target/`, and live aggregation of `qa/out/*` result files, `REPORT_EN.xlsx`,
and `ffprobe` / `pdfinfo` on the media assets (2026-09-13). Every number comes from a result
file or a command, not from memory.*
