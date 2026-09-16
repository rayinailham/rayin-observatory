# Capability Dossier — DriftWatch (Self-Monitoring Scraping Pipeline / Data Drift Alarms)

> **Source material for the portfolio page.** This document summarizes *what can be shown to
> a client* from the `driftwatch` project: the tools used, the skills proven, the numbers that
> can be defended, and the deliverables that actually exist on disk. Every claim here has a
> file, a result manifest, or a command that proves it — and the numbers were re-checked
> against those files on 2026-09-13, not copied from memory.

| Meta | Value |
|---|---|
| Project name | **DriftWatch** |
| Category | Web Scraping · Data Pipeline QA · Change/Drift Monitoring · Scheduled Unattended Jobs · Alarm Testing |
| Public repo | `github.com/rayinailham/driftwatch` (public since 2026-09-04, personal account) |
| Status | **13/13 phases done (P0–P12) · acceptance 12/12 ✅** |
| Work period | 2026-08-27 → 2026-09-04 (build + 3-day unattended soak), English explainer video added 2026-09-05/06 |
| Target jobs | Upwork — *"Competitor SEO Data Collection & Monitoring"* (clean, repeatable content dataset: title / H1 / meta / word count / links, recurring monitoring; client $30K+ spent) **+** *"Simple Website Development with Scraping"* (scrape → LLM summary → results page) |
| Proven scale | **1,323 records/day across 4 sources · 0 duplicates · 100.0% required-field completeness · 3 consecutive unattended days (12/12 runs exit 0) · 11/11 planted failures caught, 0 false positives** |

---

## 1. One-sentence pitch

> "Most scrapers don't break loudly — a CSS class gets renamed, a column goes empty, and the
> data keeps flowing until *you* discover three weeks of reports were wrong. DriftWatch
> collects your sources every morning, compares them with yesterday, and **shouts first** when
> a source changes. I planted eleven different breakages in a test site and ran the same
> pipeline over them: **eleven caught, zero false alarms.**"

The key differentiator: the usual scraping deliverable is a `scrape.py` that works on the day
it is delivered. DriftWatch is built around the question clients only ask after they have been
burned once — **"How will I know when it stops working?"** — and it answers with a closed set of
alarm codes whose detection was *proven* against planted failures, not assumed.

---

## 2. The problem being solved (client framing)

The main target job asks for a **clean and repeatable** competitor-content dataset: crawl a
sitemap, extract title / H1 / meta description / word count / publish date / internal links,
standardize it, and turn it into a recurring monitoring process. The wording "clean &
repeatable" is a tell: this client has already been let down by a brittle scraper.

| Client need (from the job post) | The failure behind it | How DriftWatch answers it |
|---|---|---|
| Crawl the sitemap, extract SEO metadata | fragile selectors, content copied wholesale | recon first, selector contract per field, **metadata only** |
| Clean, standardized dataset | empty fields nobody can explain, duplicates | locked data contract, `missing_reason` for every empty field, DB-level dedupe |
| Repeatable process | one-off script that someone must run by hand | systemd timer at 09:00 + missed-run watchdog, proven 3 days hands-off |
| Monitoring over time | a daily dump with no idea what changed | dated snapshots never overwritten + diff: **added / changed / removed** |
| (unstated) Know when it breaks | scraper silently returns 0 rows for weeks | **10 alarm codes** with written thresholds, proven 11/11 |
| (unstated) Don't get us blocked or sued | aggressive crawling, fake browser UAs | `robots.txt` gate, 1 request/s measured, honest User-Agent with contact |

The secondary job (*scraping → LLM → results page*) maps to the demo page: harvested rows
rendered into a self-contained HTML page with an optional AI summary behind a cost fence.

Three questions a fragile scraper cannot answer, and DriftWatch can — with files:

1. **"What changed since yesterday?"** → `reports/<target>/<date>/diff.json`, per record and per field.
2. **"How do I know it ran while nobody was watching?"** → 3-day soak proof from `journalctl`,
   an independent next-day watchdog, and 12 run manifests with identical code version.
3. **"Would it tell me if the site changed its layout?"** → the planted-failure matrix: 11/11.

---

## 3. System scope

### 3.1 What was built

| Part | What it is | Why it exists |
|---|---|---|
| **Four sources with distinct roles** | volume, engine-downgrade proof, real SEO metadata, and a drift oracle (table below) | each source proves a different claim; no claim relies on one lucky site |
| **Ethics gate** | `robots.txt` + ToS + sitemap + volume checklist run *before* the second request | a target is chosen by passing 7 boxes, not by convenience |
| **Recon files** | `recon/<target>.json` × 4: routes, selectors, pagination, engine decision + rationale | code is written against a recorded map, not memory |
| **Scraper engine** | `src/scrape.py`: rate limit, retry, SQLite checkpoint, dedupe, streaming JSONL, logging, CLI | the six components that separate a pipeline from a one-off script |
| **Data contract + validator** | `src/contracts.py` + `src/validate.py`: 31 fields across 4 targets, 27 required | "clean" is enforced by code: unknown keys, wrong types, unexplained blanks all fail |
| **Diff engine** | `src/diff.py`: stable `record_id` + `content_hash` per record, compared to the last successful run | turns a daily dump into "what's new / changed / gone" |
| **Alarm engine** | `src/alarm.py`: closed enum of 10 codes, thresholds locked in a decision file | a broken scraper must be noisy — silence is the worst failure mode |
| **Local drift lab** | `driftlab`: a 200-item site on `127.0.0.1:8100`, served by a programmable stdlib `http.server`, mutated by 11 scenarios | public sandboxes never change, so alarms would never be tested without it |
| **Scheduler** | systemd user timer 09:00 WIB (`Persistent=true`) + watchdog timer 10:00 for missed runs | runs itself, catches up after the machine was off, and reports if the timer died |
| **Client reports** | `daily.md` digest per source per day, 4-line alarm notification, weekly 5-sheet `REPORT.xlsx` | a non-technical client can read the state of their data without asking |
| **Demo page** | `web/index.html`: one self-contained file, real rows, metadata only, optional AI summary | "show me the data" without a server, hosting, or a third-party library |
| **Packaging** | `make all`, secret audit, 51 unit tests, case-study PDF, diagrams, 2 silent videos | one command reproduces everything on a clean copy |

### 3.2 The four sources — each one proves something different

| Code | Source | Role | Engine chosen | Volume/day |
|---|---|---|---|---:|
| `books` | `books.toscrape.com` (official scraping sandbox) | dataset volume (≥ 1,000 rows) | `httpx + selectolax` | 1,000 |
| `quotes` | `quotes.toscrape.com` (official scraping sandbox) | proof of **"drop the browser"**: find the JSON endpoint, discard the browser | `httpx + json` | 100 |
| `seo` | `www.python-httpx.org` (open-source docs, 23-URL sitemap) | real SEO metadata monitoring — the job-22 use case | `httpx + selectolax` | 23 |
| `driftlab` | own local fixture, `127.0.0.1:8100` | **oracle** for diff and alarms — deliberately mutated | `httpx + selectolax` | 200 |

The two `toscrape.com` sandboxes exist specifically for scraping practice — zero ToS risk. The
real public site had to pass the ethics gate (§6, K6). The drift lab is where breakage is
*planted*; the detector is never told which scenario is active.

---

## 4. Architecture and data flow

```
             ONCE, AT BUILD TIME                               EVERY DAY, UNATTENDED
 ┌───────────────────────────────────────┐   ┌───────────────────────────────────────────────────────┐
 │ target site                           │   │ systemd timer 09:00 WIB (+ watchdog H+1 at 10:00)      │
 │  ├─ robots.txt / sitemap / headers    │   │   Persistent=true → a missed run is caught up on boot  │
 │  │    (cheapest check first: curl)    │   │   ▼                                                    │
 │  ├─ raw HTML: __NEXT_DATA__? ld+json? │   │ scripts/daily_run.sh   (flock: never two runs at once) │
 │  └─ network tab: JSON XHR?            │   │  (0) alarm.py --check-missing <yesterday>              │
 │       (MCP chrome-devtools, once)     │   │      + start the local drift lab, stop it on exit      │
 │        ▼                              │   │  (1) scrape.py --resume  → data/<t>/<date>/            │
 │ recon/<target>.json → engine decision │──▶│        records.jsonl · records.csv · run.json          │
 │   json_api      → httpx + json        │   │  (2) validate.py  → contract + field completeness      │
 │   server_html   → httpx + selectolax  │   │  (3) export.py    → Excel-ready CSV (UTF-8 BOM)        │
 │   js_required   → Playwright script   │   │  (4) diff.py      → reports/<t>/<date>/diff.json      │
 └───────────────────────────────────────┘   │  (5) alarm.py     → reports/alerts.jsonl + exit code  │
                                             │  (6) report.py    → daily.md + critical notification   │
                                             │  (7) publish.py   → web/data.json → web/index.html     │
                                             └───────────────────────────────────────────────────────┘
                                                        weekly: report.py --weekly → REPORT.xlsx
```

**Why this order:** diff before alarm, alarm before report. Alarms need numbers from the diff
("how many disappeared vs. baseline"), and the report needs both. A report that cannot mention
alarms is exactly what competitors deliver.

**Failure handling is explicit:** a critical alarm → `daily_run.sh` exits 1 → systemd marks the
unit failed (visible in `systemctl --user --failed`) + desktop notification + a line in
`alerts.jsonl`. One failing target never cancels the others. A failed publish step never
touches the harvested snapshot.

### Engine tiers — go down as fast as possible

```
Tier 1  MCP browser (playwright / chrome-devtools)  → recon only, expensive
Tier 2  Playwright script                            → only if the page truly needs JS
Tier 3  httpx + selectolax                           → static HTML
Tier 4  httpx + json                                 → a JSON endpoint exists. The goal.
```

Keeping a browser when `httpx` is enough is treated as a **design failure** in this project,
not a style choice. All four production engines ended at tier 3 or 4 — **0 browser processes
in the daily run**.

### Identity and change detection (the core of "monitoring")

- `record_id = "{target}:{key_field}:{value}"` — stable across runs, the dedupe primary key.
- `content_hash = sha256` over canonical JSON of the business fields (sorted keys, no spaces).
- `changed` = same `record_id`, different `content_hash`, with the list of fields that changed.
- **Volatile fields (`fetched_at`, `run_id`, `scrape_duration_ms`) are excluded from the hash.**
  Without that rule, 100% of records would look "changed" every day and the diff would be noise.
- `baseline` = the **last successful run** before the one being judged, never simply "yesterday"
  — so a failed day never becomes the reference for the next day.

---

## 5. Tools used and proven in this project

| Tool | Used for | Why this one |
|---|---|---|
| **`curl`** | robots/sitemap/header checks, re-testing discovered endpoints outside the browser | answers ~70% of recon questions with one request, before any browser is opened |
| **`httpx`** (async) | every production request | light, fast; a browser is only justified by evidence |
| **`selectolax`** | HTML parsing | ~10× faster than BeautifulSoup with an API that is enough |
| **`tenacity`** | retry with exponential backoff, **only** for 429/500/502/503/504 + network errors | 403/404 are findings, not glitches — never retried |
| **`typer`** | scraper CLI (`--target`, `--resume`, `--limit`, `--delay`, `--date`) | clean flags instead of `sys.argv` |
| **`pydantic`** + own contracts | data contract enforcement | wrong types and unknown keys fail loudly |
| **SQLite** (stdlib) | checkpoint (`progress`) + dedupe (`seen` PRIMARY KEY) per run folder | crash-resume without a database server on the client's machine |
| **`http.server`** (stdlib, custom handler) | the drift-lab fixture | two scenarios need a *programmable* server (15% HTTP 503, 4 s delays); zero install, no Docker |
| **systemd user timer** | daily 09:00 schedule + 10:00 missed-run watchdog | `Persistent=true` catch-up and structured logs — cron has neither |
| **GNU Make** | `make all / harvest / diff / report / publish / oracles / test / audit` | one command for the whole pipeline |
| **`openpyxl`** | weekly `REPORT.xlsx` (5 sheets, status colouring) | runs unattended at 09:00; non-technical clients open XLSX without an import dialog |
| **Anthropic Claude API** (`claude-haiku-4-5`) | optional 4-sentence insight on the demo page | cheapest adequate model, fenced (see K10); default cost **$0.00** |
| **`jq` / `sqlite3` / `wc`** | every verification | raw JSONL is never read into context — every claim is an aggregate |
| **`uv`** (Python 3.13, `uv.lock`) | reproducible environment | the client needs only Python ≥ 3.12 and `uv` |
| **`unittest`** | **51 tests** (contracts, scraper, export, diff/alarm, daily runner, report, publish) | no network in tests; fast (≈ 7 s) |
| **PlantUML** (device service) | architecture diagram (ID + EN) | build-time only |
| **`pandoc/core`** (disposable container) | one-page case-study PDF (ID + EN) | 305 MB image instead of an 8.73 GB TeX install |
| **`ffmpeg` + `wf-recorder`** | demo + explainer video: time-stretch, trim, burned-in captions, 1080p H.264, no audio | deterministic scripted assembly |
| **headless Chromium shell** | screenshot of the demo page for the video | build-time only |

### MCP servers used (and their limits)

| MCP | Used for | Limit held |
|---|---|---|
| `chrome-devtools` | reading the network tab on `quotes.toscrape.com/scroll` → found `XHR GET /api/quotes?page=N` | **recon only** (phase P2). The endpoint was re-tested with `curl` and the browser discarded |
| `playwright` | recon navigation | never used for repeated work — 1,000 pages through MCP would burn context and money |
| `serena` | symbol lookup as the codebase grew | not a substitute for reading the file |

> **Rule enforced throughout the project:** *allowed while BUILDING, must stand alone while
> RUNNING.* The machine's MySQL, Redis, TiDB, the Excel MCP, PlantUML, and Docker were all
> available — none of them is on the daily runtime path. Checkpoint stays SQLite, the report
> stays `openpyxl`, the fixture stays stdlib. Verified: `grep -ci docker` over the whole clean-copy
> `make all` log = **0**.

### Deliberately NOT used (and why — a good talking point)

| Not used | Reason |
|---|---|
| Scrapy | too heavy for 4 targets; its framework opinions get in the way of custom checkpointing |
| BeautifulSoup | ~10× slower than `selectolax` with no matching benefit |
| Selenium | Playwright is faster and already installed — and in the end no browser was needed at all |
| Pandas | the data streams; stdlib `csv` + `json` hold no RAM |
| Proxy rotators, captcha solvers, stealth fingerprints | violate the ethics rules — never, for any client |
| cron | loses missed runs and structured logging (systemd `Persistent=true` wins) |
| Docker for the fixture | a test fixture must not make Docker a requirement on the client's machine |

### Skills / methodologies applied

| Skill | Used in | For what |
|---|---|---|
| `phase-harness` | whole project | 13 phases, one phase = one session = one artifact = one commit; file-based memory (`STATE.md`, `PLAN.md`, `KICKSTART.md`, `docs/DECISIONS.md`) |
| `web-recon` | P2 | `recon/<target>.json` × 4 with selectors, pagination, render mode, engine rationale, ethics gate |
| `scraper-forge` | P4 | recon → production scraper with rate limit, retry, checkpoint, dedupe, JSONL, logging, honest UA, CLI |
| `drift-alarm` (the pattern) | P8 | dated snapshots never overwritten, key-based diff, tiered alarm catalogue, "zero rows = alarm, not success" |
| `oracle-target` (the pattern) | P1, P8 | a bug-planted local target + a recall gate (`make oracles` must be 11/11) |
| `unattended-run` (the pattern) | P7, P9 | runner contract (lock, `run.json`, meaningful exit codes), systemd timer, watchdog, N-day soak proof |
| `evidence-guard` (the pattern) | P12 | secret/leak audit with a planted-key bite test, clean-copy reproducibility gate |
| `deliverable-pack` (the pattern) | P11–P12 | daily digest, XLSX workbook, one-page PDF, silent captioned video |
| `claude-api` | P10 | model id and pricing read from the reference, not from memory |
| `device-screen-recording` | explainer | one allowlisted window on a disposable virtual output; never the physical monitor, never audio |

---

## 6. Proven capabilities (the core of the portfolio page)

Each capability below is something that **can be claimed to a client**, together with its proof.

### K1 — Alarms proven against planted failures: 11/11, 0 false positives (the headline)

Ten closed alarm codes, each with a threshold written down *before* testing:

| Code | Exact rule | Severity |
|---|---|---|
| `ZERO_RECORDS` | `records_unique == 0` | critical |
| `RECORD_COUNT_DROP` | `records_unique < baseline × 0.80` | critical |
| `FIELD_COMPLETENESS_DROP` | any required field `< 98%`, **or** a drop `> 10` points vs. baseline | critical |
| `SCHEMA_UNKNOWN_FIELD` | the parser produced a key outside the contract | warning |
| `HTTP_ERROR_SPIKE` | `≥ 10%` non-2xx responses after retries | critical |
| `RUN_MISSING` | no `run.json` for a scheduled date, checked the next day | critical |
| `RUN_FAILED` | `run.json.exit_code != 0` | critical |
| `DURATION_ANOMALY` | `duration > 3 ×` median of last 7 runs **and** `> 60 s` | warning |
| `RATE_LIMIT_VIOLATION` | observed minimum gap `< delay × 1000 × 0.9` ms | warning |
| `CHURN_SPIKE` | `(changed + removed) > 30%` of baseline | warning |

`critical` means **"don't trust today's data"**; `warning` means **"the data is valid, but a
human should look"**. The distinction is not cosmetic.

Then eleven failure scenarios were planted into the local drift lab — one at a time, reset in
between — and the unmodified production pipeline ran over each:

```
DO-01  records added (12)        added=12 changed=0 removed=0   alarms=[]                          PASS
DO-02  values changed (4 prices) added=0 changed=4 removed=0    alarms=[]                          PASS
DO-03  record removed (1)        added=0 changed=0 removed=1    alarms=[]                          PASS
DO-04  page structure broken     records=0    alarms=[CHURN_SPIKE, FIELD_COMPLETENESS_DROP,
                                                      RECORD_COUNT_DROP, RUN_FAILED, ZERO_RECORDS] PASS
DO-05  name missing on 30%       records=200  alarms=[FIELD_COMPLETENESS_DROP]                     PASS
DO-06  15% HTTP 503              records=200  alarms=[HTTP_ERROR_SPIKE]                            PASS
DO-07  unknown field appears     records=180  alarms=[RUN_FAILED, SCHEMA_UNKNOWN_FIELD]            PASS
DO-08  4 s delay on 10% of pages records=200  alarms=[DURATION_ANOMALY]                            PASS
DO-09  yesterday's run missing   records=0    alarms=[RUN_MISSING]                                 PASS
DO-10  category changed on 40%   changed=80   alarms=[CHURN_SPIKE]                                 PASS
DO-11  scraper run too fast      records=200  alarms=[RATE_LIMIT_VIOLATION]                        PASS
11/11 PASS   (make oracles, exit 0 — re-run on the clean copy too)
```

Why this is stronger than "it has alerts":

- **DO-01..DO-03 are false-positive tests.** New, changed and removed records are *normal* for a
  living site — the pipeline must report them and stay `HEALTHY`. An alarm that fires on normal
  data is as damaging as one that stays silent: clients stop reading alerts that are often wrong.
- **The detector does not know it is being tested.** Scenarios are applied through a marker file
  read by the fixture server, never by changing scraper code.
- **The fixture is reproducible:** generated from `--seed 1337`, with a pinned
  `reproducible_sha256` (`b09a1d16…`, 200 items). If the hash drifts, the oracle is invalid — so
  the check is part of the rules.
- DO-04 firing five codes is **correct, not noise**: zero records simultaneously satisfies five
  locked thresholds; suppressing one would violate the decision file.

Evidence: `docs/DRIFT_ORACLES.md`, `scripts/run_oracles.py`, `phases/phase-12-packaging.md`
(recorded run), `assets/v4_alarm_matrix_en.png` (11 × 10 matrix).

### K2 — The alarms caught a real bug in our own pipeline (unplanned proof)

Between 29 and 31 August the timer-triggered runs harvested **0 records** from the drift lab —
the daily script never started the local fixture server when systemd (rather than a manual
session) launched it. The alarms fired exactly as designed on each of those days
(`ZERO_RECORDS`, `RECORD_COUNT_DROP`, `FIELD_COMPLETENESS_DROP`, `RUN_FAILED`, `CHURN_SPIKE`),
and the unit exited 1.

The fix (decision D24) had two parts:

1. the daily runner now starts the fixture before the loop and stops it on exit (`trap EXIT`),
   with overridable hooks so shell tests need no real server;
2. **healed alarms are closed, never deleted:** a successful re-run stamps the old lines with
   `resolved_at`. Without this, the daily digest of a healed run still quoted the failure —
   "200 records, 100% complete" in the table next to "no data collected today" in the summary.
   Closing is **scoped** — a check only closes the codes it actually evaluated, so the narrow
   missing-run watchdog can never silently close a still-valid harvest finding. Two regression
   tests lock that.

The failed days are **shown, not hidden**, in the change timeline
(`assets/v3_diff_timeline_en.png`: "Failures shown honestly, not hidden") and the alert history
(`reports/alerts.jsonl`, 21 lines, append-only). This story is a portfolio asset: the monitoring
system proved itself on a failure nobody planted.

### K3 — Daily change detection: added / changed / removed, per field

Every day's run writes to `data/<target>/<YYYY-MM-DD>/` and **never overwrites yesterday** — a
run into an existing folder without `--resume` stops and asks. Overwriting a snapshot would
delete the diff baseline, i.e. the project's main evidence.

Result over 8 consecutive dates × 4 targets (27 Aug → 3 Sep 2026), from the real `diff.json`
files: day one establishes each baseline (1,000 / 100 / 23 / 200 added), the public sources then
stay unchanged every day (`unchanged = baseline_total`) — which is exactly what a stable source
should produce: **no phantom changes**, thanks to the volatile-field exclusion rule. The only
non-zero days are the two drift-lab failure days (200 removed), which were real failures (K2).

Diff output per record includes `fields_changed[]` with from → to values, capped at 50 details
and 200 characters per value so a restructure can't produce a megabyte report.

### K4 — Crash recovery: killed with SIGKILL, resumed 12 → 1,000, 0 duplicates

Procedure (`docs/RESUME_PROOF.md`): start a fresh `books` run, **`timeout --signal=KILL 30s`** —
no graceful shutdown — count the checkpoint, then `--resume`:

```text
before resume: progress ok=12    lines=12
after  resume: progress ok=1050  lines=1000  duplicates=0
{ "exit_code": 0, "resume_used": true, "records_unique": 1000,
  "rate_limit": { "delay_sec": 1.0, "concurrency": 1, "observed_min_gap_ms": 1000 } }
```

`progress ok=1050` = 1,000 detail pages + 50 catalogue pages. The resume **added 988 records**;
it did not re-fetch the first 12. Dedupe is enforced by the database (`seen` PRIMARY KEY), not by
a Python set.

### K5 — Runs itself: 3 consecutive days, 12/12 runs exit 0, 0 alarms, 0 intervention

The soak window 2026-09-01 → 2026-09-03 ran entirely from `driftwatch.timer`
(`OnCalendar=09:00 Asia/Jakarta`, `RandomizedDelaySec=300`, `Persistent=true`):

```
books     2026-09-01..03  exit=0 records=1000  ~1,052–1,060 s   code=git:a11555c
quotes    2026-09-01..03  exit=0 records=100   ~10 s             code=git:a11555c
seo       2026-09-01..03  exit=0 records=23    ~22.5 s           code=git:a11555c
driftlab  2026-09-01..03  exit=0 records=200   ~11 s             code=git:a11555c
→ 12/12 exit 0 · 1,323 records/day × 3 days · 0 alerts dated ≥ 2026-09-01
```

Four independent pieces of evidence that nobody touched it (`docs/SOAK_PROOF.md`):

1. **Start times are random inside the timer window** — `09:00:53` · `09:03:07` · `09:03:54`: the
   signature of `RandomizedDelaySec`, not of a human.
2. **No code file changed** during the window (latest `mtime` is 2026-08-31).
3. **`code_version` is identical** in all 12 `run.json` manifests (`git:a11555c`).
4. **The next-day watchdog** independently printed `check 2026-09-01: RUN_MISSING=[]` for all 4
   targets, from systemd, before anyone opened the files.

Plus a missed-run safety net: `Persistent=true` catches up a run the machine slept through, and
a separate **watchdog timer at 10:00** raises `RUN_MISSING` if the main timer died entirely —
because a preflight check inside the main pipeline can never run if the pipeline itself never
starts. Duplicate `RUN_MISSING` lines are de-duplicated by `(target, date, code)`.

### K6 — Ethics gate before the first line of code

A public site becomes a target only if **all seven boxes** pass: robots allows the paths ·
crawl-delay is achievable · sitemap exists · not a competitor who could be harmed · no login /
captcha / Cloudflare · metadata only · ≤ 500 URLs. The audit trail (`docs/TARGETS.md`):

| Candidate | Result | Why |
|---|---|---|
| **HTTPX docs** | ✅ **chosen** | 7/7 boxes; sitemap of exactly 23 URLs → real SEO monitoring with the **smallest load** on a public host |
| FastAPI docs | ✅ passed, not chosen | 151 URLs give no extra proof — minimising public load wins |
| Pydantic docs | ❌ rejected | 1,796 URLs fails the volume box; no sitemap page was crawled |
| Python docs | ❌ excluded | the audit order itself was wrong (sitemap requested before root robots) — so the candidate was disqualified; its disallowed paths were never requested |

That last row is the point: when **our own process** broke a rule, the candidate was dropped
rather than the rule bent. The ready-to-paste client sentence:

> "Before writing code, I check the target's `robots.txt` and ToS. If it forbids automated
> access, I'll tell you upfront and offer another route — an official API, a data partner, or an
> alternative source — rather than quietly getting around it. For sites that allow it, I run at
> 1 request per second with a User-Agent you can show them if asked. That's what keeps your
> pipeline from being blocked next month."

### K7 — Polite by measurement, and it polices itself

- Delay **1.0 s per request per host** (or a larger `Crawl-delay`), concurrency **≤ 3** on public hosts.
- User-Agent is fixed and honest: `DriftWatch/1.0 (+mailto:…)` — a real contact the site owner can
  write to, deliberately kept in the public repo because the contact *is* the feature.
- The gap between requests is **measured** and stored in every `run.json`
  (`observed_min_gap_ms`): **books 1,000 ms · quotes 1,001 ms · seo 1,001 ms** — all above the
  900 ms threshold.
- A violation triggers `RATE_LIMIT_VIOLATION` on that same run — proven by scenario DO-11
  (`--delay 0.1` against a 1.0 s policy).
- **403 and 404 are never retried** — proof: one controlled request to a missing page →
  `status=404 requests=1 retries=0`; unit tests enforce a single call for each of 403 and 404.
  Retrying them only wastes time and looks like an attack. Repeated 429s or an IP block are
  treated as a refusal: stop and report.

### K8 — "Drop the browser": 8 requests → 1 request

`quotes.toscrape.com/scroll` needs JavaScript, so a browser was used **once**: MCP
chrome-devtools read the network tab and found `XHR GET /api/quotes?page=N`. The endpoint was
immediately re-tested outside the browser with `curl` — HTTP 200, full JSON, no cookie, no
Authorization/CSRF header, no Referer — and the browser was thrown away.

| For the same 10 quotes | Requests |
|---|---:|
| Browser (HTML + CSS + jQuery + 2 fonts + XHR + favicon) | 8 |
| `httpx` against the JSON endpoint | **1** |

Full harvest of 100 quotes = **10 `httpx` requests, 0 browser processes, 0 Playwright
dependency**. The decision and its rationale live in `recon/quotes.json`
(`recommended_engine: "httpx+json"`). Client value: faster, cheaper to host, far less fragile —
and the engineering restraint is visible (`assets/v5_tier_drop_en.png`).

### K9 — Clean data, enforced by a contract (and checked by hand)

- **31 contract fields across 4 targets, 27 required** (books 11/10 · quotes 6/5 · seo 9/8 ·
  driftlab 5/4), each with type, real example, and source element in
  `docs/DATA_DICTIONARY.md`.
- **Required-field completeness: 100.0% on all four targets.** The only blanks are optional and
  deliberate (e.g. `seo.og_title` — the source pages simply don't set that tag).
- **Every empty field must carry a reason** (`missing_fields` + `missing_reason`). "Empty with no
  explanation" is counted as a **data defect** by the validator — 0 such records.
- **Dataset A1:** 1,000 books, `jq … | sort | uniq -d | wc -l` = **0 duplicates**.
- **Manual verification** (`docs/MANUAL_VERIFY.md`): records **1, 500 and 1,000** were re-fetched
  and re-parsed with the production parser and compared field by field with the live page →
  **3/3 records, 30/30 required values match** (e.g. UPC `a897fe39b1053632`).
- **CSV opens straight in Excel:** `utf-8-sig`, business columns in contract order, list values
  joined with `"; "`, technical columns on the right. JSONL stays the source of truth; CSV is
  always derived from it.

### K10 — Client-readable reporting with a jargon gate

| When | What | Length |
|---|---|---|
| Every day | `daily.md` per source — status first, then numbers, max 3 examples per category | ≤ 1 screen |
| On a critical alarm | 4-line notification: **what happened · how bad · likely cause · what I'm doing about it** | 4 lines |
| Weekly | `REPORT.xlsx`: Summary · Changes · New Data · Pipeline Health · Data Dictionary | 5 sheets |

Rules that are **code, not intention**:

- A **jargon validator** runs inside the build: 12 forbidden words (`selector`, `selectolax`,
  `tenacity`, `XPath`, `stacktrace`, `traceback`, `regex`, `checkpoint`, `SQLite`, `exception`,
  `storage_state`, `semaphore`) make the build fail and the digest is not written. Values quoted
  verbatim from the source are exempt — an HTTPX docs page is really titled "Exceptions", and
  that is client data, not our vocabulary.
- **Quiet days are still reported.** "0 new, 0 changed, 0 removed, pipeline healthy" is proof the
  pipeline is alive; a client who hears nothing for three days will assume the worst.
- The **Data Dictionary sheet is generated from the contract code**, so it can never go stale —
  the sheet clients ask for three months later.
- Cell colours: green = healthy, yellow = warning, red = critical. No decorative charts.
- Stack traces, selector names and file names stay in `alerts.jsonl` (`likely_cause`,
  `next_action`) for the developer — never in the client notification.

Sanitised samples in the repo: `assets/sample_daily.md` + `assets/sample_REPORT.xlsx`
(Indonesian) and `assets/sample_daily_en.md` + `assets/sample_REPORT_en.xlsx` (English).

### K11 — Demo page + optional AI summary with a cost fence

`web/index.html` / `web/index_en.html` is **one self-contained file**: the JSON payload is embedded,
no `fetch`, no third-party library — it opens from `file://` with no server. It shows real
harvested rows (max **200 per source**, new/changed rows sorted to the top), attribution and an
ethics note per source, and **metadata only** (quote texts are never stored; book descriptions are
only word-counted). The local drift lab is never published — internal hosts must not appear on a
public page.

The optional AI insight (the "scrape → LLM → show the user" pattern from the second job):

| Fence | How it is enforced (`src/publish.py`) |
|---|---|
| Cheapest adequate model | `claude-haiku-4-5` ($1 / $5 per million tokens in/out) — summarising ~20 aggregate lines needs no large model |
| Max 1 call per source per day | today's insight is reused from the cached payload |
| Aggregates in, not the dataset | counts, completeness deltas, alarm codes, top-10 rows |
| `max_tokens = 400` | the summary cannot balloon |
| Zero cost on demand | `--no-llm` — the SDK isn't even imported |
| Missing key / API error ≠ crash | falls back to no-AI mode; the page still publishes with full numbers |
| Cost is measured | input/output tokens written into `web/data.json`; the block is always labelled AI-generated |

Current state: key left empty → **0 tokens, $0.00/day**. Estimated with a key: ≈ $0.005/day.
The provider is swappable (the job post named OpenAI); the fencing pattern is the deliverable.

### K12 — Reproducible on a clean copy, one command, no Docker

`make all` = `setup → lab-up → harvest → diff → report → publish`. Proven 2026-09-04 on a clean
copy (`rsync` without data/reports/venv/git, fresh `.env`, fixture on a shifted port 8101):

```
LAB_PORT=8101 make all → EXIT_CODE=0, 1,086 s (18 min 6 s)
driftlab 200 · books 1,000 · quotes 100 · seo 23 = 1,323 records, all exit=0
diff.json + daily.md for 4 targets · REPORT.xlsx · web/index.html published
grep -ci docker <whole make-all log> = 0
make oracles → 11/11 PASS · make test → 48/48 OK   (51/51 today, after the English switch tests)
```

The only prerequisites are Python ≥ 3.12 and `uv`. The fixture is stdlib, the checkpoint is
SQLite, the report is `openpyxl` — nothing that needs a server or a container.

### K13 — Secret/leak audit before going public (with a bite test)

`scripts/secret_audit.py` (`make audit`) checks four things: `.env` values, 7 third-party key
patterns (`sk-ant-`, `sk-`, `AKIA`, `gh[pousr]_`, `xox[baprs]-`, PEM private keys, URLs with
passwords), sensitive files tracked by git (`.env`, `data/`, `reports/`, `auth/`, `logs/`, `*.db`),
and the **entire commit history**.

- Result at P12: **0 leaks** in 91 tracked files + 92 on the clean copy; 52,847 history diff lines scanned.
- Re-run on 2026-09-13: **0 leaks, 55,154 history diff lines, 0 matches.**
- **The gate was proven non-empty:** planting `sk-ant-api03-AAAA…` in a tracked file made the audit
  **fail with exit 1**, and it passed again once removed. (An audit that scans zero files always
  "passes" — this lesson was paid for.)
- A separate **IDENTITY class** reports intentional values (User-Agent contact, fixture port,
  timezone) without failing — so keeping them is a conscious decision, not an oversight.

### K14 — Silent, captioned videos a non-technical client can follow

| Video | Spec (checked with `ffprobe`) | Content |
|---|---|---|
| `assets/v1_resume_demo.mp4` | 59.2 s · 1920×1080 · H.264 · **no audio** · Indonesian captions | `kill -9` → `--resume` → an alarm fires → demo page |
| `assets/explainer.mp4` | **118.2 s** · 1920×1080 · H.264 · 30 fps · **no audio stream** · 10 segments · English | problem → how it works → one command → crash recovery → a real failure caught live → 11/11 coverage → 8→1 request → the client page → deliverables → closing numbers |

Rules held while producing them: terminal takes recorded live in a **disposable sandbox copy**
(never the repo working tree), one allowlisted window on a **disposable virtual output** (never
the physical monitor), no audio, captions **burned into the image** (≤ 12 words each). The English
build runs a **language guard** over 61 caption/source files and fails on any Indonesian word;
every number on screen is mapped to its source file in `docs/VIDEO_PLAN.md`. Two banned-number
rules were applied to the video itself: the 18-min clean-copy figure was left out because its
artifact no longer exists on disk, and live footage of the local fixture is never presented as
the 1,323-records/day figure.

### K15 — Consultant-level scoping and a ready pitch

- `docs/PITCH.md`: a 60-second pitch (138 words) plus one-sentence answers to the follow-ups clients
  actually ask — *install time? what if the site changes completely? power cut overnight? data
  format? legal? AI cost?* — each tied to a proof file.
- A proposal sentence written for the "clean & repeatable" job: *"I don't send a single
  `scrape.py`. You get a pipeline that runs itself every morning, keeps dated snapshots, sends a
  daily 'what's new, what changed, what disappeared' summary, and warns you **the same day** if the
  target changes its structure — not three weeks later."*
- A retainer framing: *"Sites change — it's not if, it's when. A monthly retainer covers fixes when
  the structure changes, new columns, and making sure the pipeline actually runs every day."*

### K16 — Engineering discipline that can be audited

- **13 phases (P0–P12)**, one phase = one session = one artifact = **one commit whose message
  carries its metrics** (27 commits total including planning, gate-evidence and remediation commits).
- **22 locked decisions** in `docs/DECISIONS.md` that outrank every other document; each change is dated.
- **Explicit document hierarchy** (DECISIONS → SCHEMA → ETHICS → phases → ACCEPTANCE/README): a
  lower document that contradicts a higher one is fixed in the same session.
- **12 acceptance criteria**, each with the command that proves it — all ✅, with honest notes
  attached where a proof is indirect (A6).
- **A commit gate** per phase: audit → commit → push; a phase is not ✅ until the push succeeds.
- **51 unit tests**, no network; `make oracles` as the recall gate; `make audit` as the leak gate.
- **Zero resource footprint at close-out:** timers disabled, fixture ports closed, temporary
  sandboxes deleted, fixture hash unchanged.

---

## 7. Numbers at a glance (for the portfolio page's stat cards)

| Metric | Number |
|---|---|
| Records collected per day | **1,323** (books 1,000 · drift lab 200 · quotes 100 · seo 23) |
| Duplicates | **0** |
| Required-field completeness | **100.0%** on all 4 sources (27 required of 31 contract fields) |
| Unexplained empty fields | **0** |
| Manual spot-check vs. live pages | **3/3 records · 30/30 required values match** |
| Planted failure scenarios caught | **11/11** — **0 false positives** |
| Alarm codes (closed set, written thresholds) | **10** (6 critical · 4 warning) |
| Crash recovery (`SIGKILL` → `--resume`) | **12 → 1,000 records, 0 duplicates**, 0 pages fetched twice |
| Unattended soak | **3 consecutive days · 12/12 runs exit 0 · 0 alarms · 0 interventions** |
| Snapshot history | 8 consecutive dated snapshots × 4 sources (27 Aug → 3 Sep 2026) |
| Request gap measured on public sources | **1,000–1,001 ms** (policy: 1 req/s, threshold 900 ms) |
| Browser → direct HTTP | **8 requests → 1** for the same data; **0 browser processes** in the daily run |
| Clean-copy `make all` | **exit 0 in 1,086 s**, 1,323 records, **0 Docker calls** |
| Leak audit | **0 leaks** · 55,154 history diff lines scanned · bite test fails on a planted key |
| Unit tests | **51 / 51 OK** (≈ 7 s) |
| Client-report jargon words blocked | 12 |
| Weekly workbook | 5 sheets (Summary · Changes · New Data · Pipeline Health · Data Dictionary) |
| AI summary cost | **$0.00/day** by default (≈ $0.005/day with a key, fenced) |
| Videos | demo 59.2 s · explainer 118.2 s · 1080p · no audio · burned-in captions |
| Phases / commits / decisions / acceptance | 13 / 27 / 22 / **12 of 12** |
| Code size | ~2,550 lines pipeline (10 modules) · ~1,050 lines tests · ~2,270 lines scripts (24 files) |

---

## 8. How to verify the claims above (real commands)

```bash
git clone https://github.com/rayinailham/driftwatch && cd driftwatch
cp .env.example .env          # ANTHROPIC_API_KEY may stay empty

make all          # setup → lab-up → harvest → diff → report → publish
make oracles      # 11 planted failure scenarios → must be 11/11, exit 0
make test         # 51 unit tests
make audit        # secret/leak audit → must be 0
LAB_PORT=8101 make all   # clean copy beside an existing fixture

# token-cheap inspection of any run
jq '{exit_code,records_unique,duplicates_rejected,rate_limit,field_completeness}' data/books/<date>/run.json
jq -r .record_id data/books/<date>/records.jsonl | sort | uniq -d | wc -l      # duplicates → 0
jq .counts reports/books/<date>/diff.json                                      # added/changed/removed
sqlite3 data/books/<date>/progress.db "SELECT status, COUNT(*) FROM progress GROUP BY status;"
jq -r 'select(.severity=="critical") | "\(.date) \(.target) \(.code)"' reports/alerts.jsonl

# crash it yourself
timeout --signal=KILL 30s .venv/bin/python src/scrape.py --target books
.venv/bin/python src/scrape.py --target books --resume

# schedule it (Linux + systemd user session)
cp deploy/driftwatch*.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now driftwatch.timer driftwatch-watchdog.timer
```

---

## 9. Limitations stated openly (do not hide these in the portfolio)

This section is what makes the other claims credible.

| Limitation | Honest status |
|---|---|
| **The public sources never actually changed** | Over 8 days, books/quotes/seo produced 0 added/changed/removed after day one. Drift detection is proven on the **planted** local lab (11/11) and on one **real, unplanned** failure (K2) — not on a real third-party site changing its layout. |
| **Small real SEO target** | The `seo` source is 23 URLs, chosen on purpose as the lowest-load candidate that passed the ethics gate — not because the pipeline can't do more. |
| **Soak proof is 2 direct + 1 indirect** | `journalctl` shows 2 of the 3 timer triggers directly; the machine's journal had rotated past the 1 Sep morning. That run is proven by its 4 `run.json` manifests, complete data/report folders, and the independent watchdog line — stated as indirect, not as a journal line. |
| **First timer window had failures** | Of the first 5 timer-triggered days (27–31 Aug), 3 exited 1 because the fixture was never started by the timer — found by the alarms and fixed (D24). The clean 3-day soak window started after the fix. |
| **Duration warnings from a noisy baseline** | `books` raised `DURATION_ANOMALY` warnings on 28–30 Aug because the median was built from near-instant `--resume` re-runs of already-finished snapshots during development (0.036–0.068 s). Warning-level, kept in history, not deleted. |
| **Clean-copy timing is document-only** | The 1,086 s `make all` result is recorded with its commands and output, but the `/tmp` clean copy was deleted afterwards — so that figure was excluded from the explainer video. |
| **No public URL for the demo page** | `web/index.html` is a self-contained file opened via `file://` (decision D18); it is ready to host as-is but is not hosted. |
| **AI summary switched off** | No API key was set, so the live page shows the labelled empty AI block and a $0 cost. The fencing is implemented and tested; the paid path was not exercised in the soak. |
| **English deliverables not yet in the public repo** | The English explainer video, English diagrams/charts, English sample report/digest, English demo page data, and the `--lang en` switch edits exist on disk but are **uncommitted**; the public repo's last commit (2026-09-04) predates them. Commit + push before linking them from the portfolio. |
| **Pitch timing is estimated** | The 60-second pitch is 138 words (≈ 53–59 s by word count); it has not been timed aloud. |
| **Linux + systemd only** | No Windows/macOS support; scheduling uses a systemd user timer, not cron or Task Scheduler. |
| **Deliberately out of scope** | No interactive dashboard, multi-user auth, external DB, job queue, cloud deploy, admin UI — every extra service becomes an install requirement on the client's machine. |
| **Never: protection bypass** | No captcha solving, Cloudflare/WAF bypass, stealth fingerprints, proxy rotation, scraping behind other people's logins, personal data, or copyrighted content redistribution. |

---

## 10. What can be offered to the next client

The pipeline is **portable**: the client-specific parts are the target URLs, the recon file, and
the field contract. Everything else — rate limiting, checkpoint/resume, dedupe, dated snapshots,
diff, the 10-code alarm catalogue, daily digest, weekly workbook, demo page, scheduler + watchdog,
audit, and `make all` — works against a data contract, not against one particular site.

**Service packages that already have proof:**

1. **Competitor / SEO Content Monitoring** — sitemap crawl → title, H1, meta description, canonical,
   headings, word and link counts → dated snapshots → daily "what changed" digest.
2. **Self-Monitoring Scraping Pipeline** — any authorized source, with alarms that fire the day the
   source breaks instead of returning zero rows for weeks.
3. **Scraper Health Audit / Alarm Retrofit** — plant failures against an existing scraper and report
   which ones it catches; add the missing alarms.
4. **Unattended Scheduling with Proof** — turn a script into a daily job with a lock, manifests,
   meaningful exit codes, catch-up, a missed-run watchdog, and an N-day soak report.
5. **Clean Dataset Delivery** — contract-validated JSONL + Excel-ready CSV + data dictionary, with
   every empty field explained and a manual spot-check against source pages.
6. **Scrape → AI Summary → Results Page** — a self-contained results page with a cost-fenced LLM
   summary that degrades gracefully to $0.
7. **Pre-project Scraping Consultation** — robots/ToS gate, API-first check, engine-tier decision,
   and an honest "don't scrape this, here's the alternative" when that's the right answer.

---

## 11. Technical lessons worth telling (material for an "engineering notes" section)

Real traps, found at the cost of real time:

1. **Hash only what matters.** Including `fetched_at` or `run_id` in the content hash makes every
   record "changed" every day — the diff becomes garbage. Volatile fields are excluded by rule.
2. **Baseline = last *successful* run, not yesterday.** Otherwise one failed day becomes the
   reference and tomorrow's healthy run looks like a massive change.
3. **A preflight check can't detect a scheduler that never fires.** The missed-run check inside the
   daily script never runs if the timer is dead — hence a second, independent watchdog timer.
4. **Unit tests don't prove the scheduled environment.** Manual sessions had the fixture already
   running; the systemd-launched run did not. Only the real timer exposed it — and the alarms did
   their job (K2).
5. **Healed alarms must be closed, and closing must be scoped.** Otherwise the digest contradicts
   itself — or the narrow watchdog silently closes findings it never evaluated.
6. **A stale test server looks like a detector regression.** DO-06 fails each path only once per
   server lifetime; re-using a server made the scenario pass silently with `alarms=[]`. `make
   oracles` therefore restarts the fixture every time.
7. **`kill -9 $!` on `uv run …` kills only the wrapper.** For crash proofs, call the venv's Python
   directly or the "crash" never reaches the scraper.
8. **`Type=oneshot` units log `Starting …`, not `Started …`.** The documented grep pattern was
   wrong and would have undercounted the soak — found and corrected in the proof document.
9. **An audit that scans zero files always passes.** Every gate got a bite test with a planted fake key.
10. **Duration baselines get polluted by no-op re-runs.** Near-instant resume runs dragged the
    median down and produced warnings on normal runs — a real lesson about which runs belong in a
    baseline.
11. **Video tooling quirks:** `wf-recorder` keeps capturing after the window closes (caught by a
    per-frame mean-colour scan, fixed with a tail trim); `$0.00` inside a bash caption table expands
    `$0` to the script name; plain `chrome --headless --screenshot` hangs on this machine.

---

## 12. Repo structure (for the "behind the scenes" section)

| Path | Contents |
|---|---|
| `src/scrape.py` · `src/store.py` | async `httpx` fetcher with rate limit, retry policy, SQLite checkpoint + dedupe, `run.json` manifest |
| `src/contracts.py` · `src/validate.py` | locked field contracts (31 fields), validation, `content_hash`, completeness |
| `src/export.py` | JSONL → Excel-ready CSV |
| `src/diff.py` · `src/alarm.py` | diff vs. last successful run; 10-code alarm engine, scoped resolve, missing-run check |
| `src/report.py` · `src/publish.py` | daily digest / notifications / weekly XLSX with jargon gate; self-contained demo page + fenced AI insight (ID/EN) |
| `src/test_*.py` | 51 unit tests (contracts, scraper, export, diff/alarm, daily runner, report, publish) |
| `scripts/` | fixture generator + programmable server, drift-lab mutator, oracle runner, daily runner, watchdog, secret audit, visuals, case study, demo/explainer video builds, language guard |
| `deploy/` | `driftwatch.{service,timer}` + `driftwatch-watchdog.{service,timer}` |
| `recon/` | 4 recon files with engine decision, rationale and ethics gate |
| `fixtures/site/` | the 200-item drift-lab site (seeded, hash-pinned) |
| `web/` | `index.html` / `index_en.html` demo pages + payloads |
| `docs/` | 15 documents: decisions, schema, ethics, targets, pipeline, tools, drift oracles, data dictionary, acceptance, manual verify, resume proof, soak proof, client report, pitch, video plan |
| `phases/` | 13 phase files, each Definition of Done ticked against real command output |
| `assets/` | architecture diagram, diff timeline, alarm matrix, tier-drop chart, case-study PDF, sample reports, 2 videos, explainer cards (ID + EN) |
| `data/` · `reports/` | dated snapshots and reports — **gitignored**, never overwritten |

---

## 13. Glossary (for non-technical readers of the portfolio page)

| Term | Short meaning |
|---|---|
| **Scraping / harvesting** | automatically collecting public information from web pages |
| **Snapshot** | the full set of data collected on one date, kept forever as a reference |
| **Diff** | the comparison with the previous snapshot: what is new, what changed, what disappeared |
| **Drift** | a source changing in a way that can silently corrupt the data (layout, fields, errors) |
| **Alarm code** | a named, pre-defined warning with an exact rule for when it fires |
| **False positive** | an alarm that fires when nothing is wrong — why clients stop reading alerts |
| **Planted failure / oracle** | a breakage made on purpose in a test site to prove the alarm catches it |
| **Checkpoint / resume** | saved progress, so a stopped run continues instead of starting over |
| **Soak test** | letting the system run on its own for days to prove it really is unattended |
| **Watchdog** | a separate check that raises an alarm if the daily job didn't happen at all |
| **`robots.txt`** | a site's published rules for automated visitors |
| **Rate limit** | how fast requests are sent — here 1 per second, measured on every run |
| **Data contract** | the agreed list of columns, their types, and which are required |
| **Field completeness** | the share of records where a column is actually filled |
| **Clean copy** | a fresh copy in another folder/port, used to prove the results reproduce |

---

*This document was assembled from `driftwatch/README.md`, `STATE.md`, `PLAN.md`,
`docs/DECISIONS.md`, `docs/ACCEPTANCE.md`, `docs/PIPELINE.md`, `docs/TARGETS.md`,
`docs/ETHICS.md`, `docs/DRIFT_ORACLES.md`, `docs/RESUME_PROOF.md`, `docs/SOAK_PROOF.md`,
`docs/MANUAL_VERIFY.md`, `docs/DATA_DICTIONARY.md`, `docs/TOOLS.md`, `docs/CLIENT_REPORT.md`,
`docs/PITCH.md`, `docs/VIDEO_PLAN.md`, `phases/phase-12-packaging.md`, `recon/*.json`, the
`Makefile`, `deploy/`, `scripts/daily_run.sh`, and the code in `src/`. Numbers were re-checked on
2026-09-13 against `data/*/*/run.json`, `reports/*/*/diff.json`, `reports/alerts.jsonl`,
`reports/REPORT_en.xlsx`, `ffprobe` on both videos, `git log`, a fresh `make test` run (51/51 OK),
and a fresh `make audit` run (0 leaks).*
