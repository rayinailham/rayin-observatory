# Capability Dossier — SurgeLine (Bulk Form Automation / Crash-Safe Web Automation)

> **Source material for the portfolio page.** This document summarizes *what can be shown to
> a client* from the `surgeline` project: the tools used, the skills proven, the numbers that
> can be defended, and the deliverables that actually exist on disk. Every claim here has a
> file, a database query, or a command that proves it.

| Meta | Value |
|---|---|
| Project name | **SurgeLine** |
| Category | Web Automation · Bulk Form Submission · Resilience / Chaos Testing · Data Pipeline QA |
| Public repo | `github.com/rayinailham/surgeline` (public since 2026-08-29, personal account) |
| Status | **15/15 phases done · acceptance 12/12 ✅** |
| Work period | 2026-08-28 → 2026-08-29 (P0–P14), English explainer video added 2026-09-06 |
| Target job | Upwork — *"Web Automation Developer for Bulk Form Processing"* (~6,000,000 Excel/CSV records → web forms, Playwright/Python, queues/workers, dashboard) |
| Proven scale | **50,000 records** end to end, **killed with `kill -9` twice mid-run**, finished 100%, **0 duplicates** |

---

## 1. One-sentence pitch

> "I take your Excel/CSV file, push every row through a web form that has no API, and save the
> **confirmation number** for every success. I pulled the plug on it twice in the middle of a
> 50,000-record run — it picked up where it stopped, finished every record, and **sent nothing
> twice**."

The key differentiator: most bulk-automation scripts are a loop that works until record
23,000 dies — and then nobody knows what was sent. SurgeLine answers the questions clients are
actually afraid of: **"What happens when it crashes? Will anything be sent twice? How long will
6 million records really take?"** — with numbers from a database, not promises.

---

## 2. The problem being solved (client framing)

The client in the job post has ~6,000,000 records and an authorized platform that only accepts
data through a web form. The list of requirements is really a list of the ways fragile
automation fails:

| Client requirement (from the job post) | The failure behind it | How SurgeLine answers it |
|---|---|---|
| Import & process Excel/CSV records | 6M rows blow up memory | streamed loader, memory stays flat |
| Automatically fill & submit forms | no API → must drive a browser | Playwright headless Chromium workers |
| Track success/failure & capture confirmation numbers | "success" with no proof | a success **without** a confirmation number is counted as a failure |
| Prevent duplicate submissions & log error reasons | resumes and reloads send twice | uniqueness enforced by the **database**, every failure keeps its reason |
| Auto retry failed records & resume after a crash | restart from zero, double-sends | retry ladder + dead-letter + lease recovery, state lives on disk |
| Simple dashboard: Total / Pending / Successful / Failed | numbers that drift from reality | read-only live dashboard, proven to match the database with **0 difference** |

The three questions no fragile script can answer, and SurgeLine can:

1. **Was anything lost or sent twice after the crash?** → 0 / 0, checked by SQL queries.
2. **What happens to the 5% of submissions the platform rejects or drops?** → each one is
   retried or recorded with its reason; none disappear.
3. **How long will 6 million really take?** → measured at 7 worker counts, extrapolated with
   the assumptions written down: **≈ 3.0 days** (conservative: 4.1 days) on one machine.

---

## 3. System scope

### 3.1 What was built

| Part | What it is | Why it exists |
|---|---|---|
| **Target app** | a form web app **I built and own**, running in Docker at `127.0.0.1:8110` | a legal stand-in for a "platform with no API" — nobody else's system is touched |
| **Chaos layer** | the target **deliberately fails 5%** of submissions: HTTP 500, slow response, validation rejection | resilience must be measured against a system that breaks, not assumed |
| **Data generator** | 50,000 synthetic records → CSV **and** XLSX, 50 deliberate duplicates | realistic volume, zero real personal data |
| **Loader** | streams the file into a queue; duplicates rejected by the database | flat memory, idempotent reloads |
| **Queue** | one SQLite file per run (WAL mode) | the single source of truth; runs on the client's machine with no DB server |
| **Workers** | N parallel Playwright headless Chromium workers | fill the form like a person, read the confirmation number from the result page |
| **Recovery** | retry + backoff, dead-letter, lease-based orphan recovery | crashes and flaky targets never lose or duplicate work |
| **Dashboard** | FastAPI + HTMX, read-only, refreshes every 2 s | live Total / Pending / In progress / Successful / Failed / Dead + throughput |
| **Throughput bench** | runs the same 800-record subset at N = 1, 2, 4, 8, 12, 16, 24 workers | a speed number the client can plan against |
| **Client report** | one-page digest + 5-sheet `REPORT.xlsx`, **zero-jargon gate** | a non-technical client can read and act on it |

### 3.2 The test target — designed to be difficult

Six form fields (`external_ref`, `full_name`, `email`, `policy_no`, `amount`, `notes`) with real
validation rules. Every successful submission returns a unique confirmation number
(`SL-` + 8 hex characters) **in the page DOM**, not in a JSON API — the worker has to read the
page.

| Chaos mode | What the target does | Nature | What the worker must do |
|---|---|---|---|
| `server_error` | HTTP 500 | transient | retry with backoff |
| `slow` | sleeps 2 s, then succeeds | transient (timeout) | retry; target idempotency prevents a double record |
| `validation` | HTTP 422 with error list | **permanent** | do **not** retry; mark `failed` with the reason |

The chaos is **deterministic**: `sha256(seed + external_ref)` decides each record's fate. The
same record always fails the same way, regardless of order or worker count — so every run can
be reproduced and every number re-derived.

The target is also **idempotent per record**: submitting the same `external_ref` twice returns
the same confirmation number and writes no second row. That is the last line of defense that
makes "0 duplicates" hold even when a worker dies after the server accepted the form but
before the worker saved the result.

`/docs` and `/redoc` are disabled — the target genuinely pretends to have no API.

---

## 4. Architecture and data flow

```
 Excel/CSV 50k            Loader                Queue (SQLite WAL)            Workers ×N
 scripts/gen_data.py  →   src/load.py      →    data/<run>/queue.db      →    src/worker.py
 synthetic, seeded        streamed +            table jobs:                   Playwright headless
                          INSERT OR IGNORE      pending / claimed /           atomic claim →
                          (UNIQUE dedup)        ok / failed / dead            fill the form →
                                                   ▲      │                   read confirmation
                                                   │      │                          │
                                  lease recovery ──┘      └── dashboard              ▼
                                  (orphaned job →             src/dashboard.py  ◄── write back
                                   pending)                   FastAPI + HTMX,       (ok + confirmation
                                                              read-only             | failed + reason)
                                                                                         │
                                        Target app (own Docker container, 127.0.0.1:8110) ◄┘
                                        fails 5% on purpose (500 / slow / validation)
                                        every success → unique confirmation number
```

### Job state machine

```
 loader ──▶ pending ──(BEGIN IMMEDIATE, one owner)──▶ claimed ──▶ ok      confirmation saved
               ▲                                        │   ├──▶ failed  permanent rejection
               └────── retry / lease expired ───────────┘   └──▶ dead    5 attempts used up
```

`ok`, `failed`, and `dead` are terminal. `claimed → claimed` is **illegal** — that is what a
double-claim looks like, so the state machine rejects it in code (`assert_transition()` raises
`SchemaError`), rather than merely "not expecting" it.

### Five structural reasons it is crash-safe (not lucky)

1. **State lives in the database, not in process memory.** A dead worker leaves its job as
   `pending` or `claimed` on disk; no progress dies with the process.
2. **Duplicates are rejected by the database** — `external_ref` is the primary key and the
   loader uses `INSERT OR IGNORE`. The same file can be loaded any number of times.
3. **Claims are atomic** (`BEGIN IMMEDIATE`): two workers never hold the same job.
4. **Lease timeout of 120 s**: a job carried to its grave by a killed worker returns to the
   queue instead of being lost forever.
5. **The confirmation number is the proof**: `confirmation` is `UNIQUE` in the queue, so one
   record can hold at most one confirmation number.

### Upgrade path (documented, deliberately not built)

SQLite → PostgreSQL only replaces the `store` layer (the claim becomes
`SELECT … FOR UPDATE SKIP LOCKED`). The `store` interface is intentionally narrow so the swap is
one file. It is written down in `docs/ARCHITECTURE.md` and kept out of scope on purpose.

---

## 5. Tools used and proven in this project

| Tool | Used for | Why this one |
|---|---|---|
| **Playwright (Python, headless Chromium)** | form-filling workers, reading confirmation numbers from the DOM | the pitch is "a platform with no API" → it must go through a real browser |
| **SQLite (WAL mode)** | queue, job state, dedup, audit trail of every attempt | no DB server needed on the client's machine; many readers + one writer |
| **FastAPI + uvicorn** | the target form app **and** the dashboard | light, one file each, easy to inject deterministic chaos |
| **HTMX** | live dashboard with 2-second polling | one page, no JavaScript build toolchain |
| **Docker + Compose** | hosting the target app, port and container name driven by env | a clean copy can run side by side with the original |
| **openpyxl** | 50k-row XLSX generation (write-only) and the 5-sheet client report | streamed writing keeps memory flat; the report runtime stands alone |
| **Faker** (seeded) | 50,000 synthetic records | realistic data with **zero** real personal data |
| **GNU Make** | `make all` (target → data → queue → workers → report → verification gate) | one command reproduces everything |
| **uv (Python 3.13)** | venv + `uv.lock` | the client only needs `uv sync --frozen` |
| **unittest** | **163 tests**, no extra dependency | consistent across projects; no network in unit tests |
| **sqlite3 CLI / jq / wc** | token-cheap verification | 50k rows are never read raw — every claim is an aggregate query |
| **Graphviz (`dot`)** | architecture diagrams (Indonesian + English + video variant) | text source committed, PNG rendered |
| **ffmpeg + wf-recorder** | demo and explainer video: trimming, speed-up, burned-in captions, 1080p H.264 | deterministic CLI assembly, no audio track |

### MCP servers used (and their limits)

| MCP | Used for | Limit held |
|---|---|---|
| `playwright` / `chrome-devtools` | recon on 1–2 sample pages of the target while defining selectors | **never** the production engine — workers run their own Playwright scripts |
| `serena` | symbol lookup as the codebase grew | not a substitute for reading the file |

> **Rule enforced throughout the project:** *allowed while BUILDING, must stand alone while
> RUNNING.* No MCP, no device services (the machine's MySQL, Redis, TiDB), no message broker, and
> no cloud service anywhere on the deliverable's runtime path. The queue is one SQLite file.

### Skills / methodologies applied

| Skill | Used in | For what |
|---|---|---|
| `phase-harness` | whole project | 15 phases, one phase = one session = one artifact = one commit; file-based cross-session memory (`STATE.md`, `PLAN.md`, `KICKSTART.md`, `docs/DECISIONS.md`) |
| `durable-queue-worker` (the pattern) | P4–P12 | atomic claim, retry ladder + backoff, dead-letter, lease recovery, DB-level dedup, crash-recovery proof, capacity proof |
| `bulk-form-runner` (the pattern) | P1–P13 | Excel/CSV intake, selector contract, confirmation number as evidence of success, parallel Playwright workers |
| `arch-playwright-provision` | whole project | Playwright on Arch Linux without `sudo`, `pacman`, or `install-deps` |
| `device-screen-recording` | P14 + explainer | record one allowlisted window on a disposable virtual output; never the physical monitor, never audio |
| `evidence-guard` (the pattern) | P14 | secret/leak audit with tests, clean-copy reproducibility gate |
| `deliverable-pack` (the pattern) | P13–P14 | client digest, XLSX workbook, silent captioned video |

---

## 6. Proven capabilities (the core of the portfolio page)

Each capability below is something that **can be claimed to a client**, together with its proof.

### K1 — Crash recovery, proven with `kill -9` (the headline)

On the full 50,000-record run, the whole process group (runner + all workers) was **killed
with `kill -9` twice** — the equivalent of pulling the power cord, not a polite shutdown.

| Moment | Successfully submitted (from the DB) |
|---|---|
| before kill #1 | 10,621 |
| before kill #2 | 21,508 |
| after restarting until done | **48,273** |

Progress rose monotonically (0 → 10,621 → 21,508 → 48,273): every restart continued from the
same SQLite state instead of starting over.

Final state, verified by SQL against `data/full50k/queue.db`:

```sql
SELECT COUNT(*)-COUNT(DISTINCT external_ref) FROM jobs;                     -- 0  duplicate records
SELECT COUNT(*)-COUNT(DISTINCT confirmation) FROM jobs WHERE status='ok';   -- 0  duplicate confirmations
SELECT COUNT(*) FROM jobs WHERE status IN ('pending','claimed');            -- 0  unfinished
SELECT COUNT(*) FROM jobs WHERE status='ok' AND confirmation IS NULL;       -- 0  success without proof
```

**7 orphaned jobs** (held by a worker at the moment it was killed) were reclaimed by the lease
sweep, and all 7 ended `ok` — none lost, none sent twice. The audit table shows exactly 7
`timeout` attempts: one per orphan, each closed by the sweep, not left dangling.

The same proof was run **three times** at different scales:

| Run | Records | Kills | Orphans recovered | Duplicates |
|---|---|---|---|---|
| P9 crash proof (`p09-crash-proof`) | 3,000 | 2× | 8 / 8 | 0 |
| P11 full run (`full50k`) | 49,950 | 2× | 7 / 7 | 0 / 0 |
| P14 demo recording | 49,950 | 2× | — | 0 / 0 |

Evidence: `docs/RESUME_PROOF.md` (commands, logs, before/after counts), `assets/demo.mp4`,
`assets/before.png`, `assets/crash.png`, `assets/after.png`.

### K2 — 100% accounted for against a target that fails 5% on purpose

The target deliberately broke 2,519 of 49,950 records (5.04%). The question is not "did it
succeed" but "**did every failure end up somewhere honest?**"

| Outcome | Count | Share | Meaning |
|---|---:|---:|---|
| `ok` — submitted, confirmation number saved | **48,273** | 96.6% | 48,273/48,273 carry a confirmation, 0 repeated, 0 empty |
| `failed` — rejected by validation (permanent) | 844 | 1.7% | **not** retried; reason stored per record |
| `dead` — still failing after 5 attempts | 833 | 1.7% | every one carries its last error message |
| unfinished | **0** | — | |

And the part that proves the retry logic is correct, not just busy: because the chaos is
deterministic, the expected outcome of every record could be **predicted in advance** and
compared with reality:

```
prediction : server_error=833  slow=842  validation=844  honest=47,431
actual     : ok=48,273  failed=844  dead=833
dead   == predicted server_error : True
failed == predicted validation   : True
every slow record ended ok       : True
every honest record ended ok     : True
```

`dead` is **exactly** the set of records the target returns HTTP 500 for forever (5 attempts
each), `failed` is **exactly** the validation set (1 attempt each, no pointless retries), and
every "slow" record eventually succeeded. Not one record fell through a crack.

**Bonus — an unplanned failure, also survived.** `REC-000002` was *not* a chaos record, yet it
got a real HTTP 500 in the first second of the run: a cold-start race inside the target
(`sqlite3.OperationalError: database is locked`). The worker classified it as retryable, and
the second attempt succeeded. The race was later fixed in the target (P14) with a lock around
initialisation plus `busy_timeout=15000`, with 2 regression tests — before: 15 connections and a
lock error; after: 1 connection, 0 errors.

### K3 — Duplicate prevention enforced by the database, not by hope

- `external_ref` is the natural key: `NOT NULL PRIMARY KEY` in `jobs`. (The explicit `NOT NULL`
  matters — SQLite otherwise allows `NULL` in a `TEXT PRIMARY KEY`, and dedup would leak.)
- The loader uses `INSERT OR IGNORE`. The generated file contains **50 deliberate duplicates**;
  50,000 rows in → **49,950 jobs**, 50 rejected by the database. Reloading the whole file again
  adds **0** rows and does **not** reset any finished job.
- `confirmation` is `UNIQUE` in the queue, so two jobs can never store the same confirmation.
- The target itself is idempotent per `external_ref` (resubmission → same number, no new row).

Three independent layers, each provable by a query. A known trap was paid for up front and
tested: `INSERT OR IGNORE` silently swallows **every** constraint violation, not only
duplicates — so the loader validates each record first and uses `rowcount` to tell "skipped
as duplicate" from "inserted"; otherwise malformed records would vanish without a trace.

### K4 — Parallel workers with atomic claiming (0 double-claims)

Claiming a job is one `BEGIN IMMEDIATE` transaction: the writer lock is taken **before** the
`SELECT`, so two workers can never pick the same job. (A `SELECT` then `UPDATE` in separate
transactions is the classic race.)

Proof (P7, 4 workers, 500 claims, 25.86 jobs/s):

```
double_success_multi_worker | 0
ok_jobs                     | 489
distinct_ok_refs            | 489
workers_seen                | 4
duplicate_attempt_refs      | 0
```

### K5 — Retry ladder, dead-letter, and lease recovery with reasoned numbers

Every number is locked in `docs/DECISIONS.md` together with the reason it was chosen:

| Setting | Value | Why |
|---|---|---|
| `MAX_ATTEMPTS` | 5 | enough to ride out transient failures, bounded so poison records end |
| Backoff | 1 · 2 · 4 · 8 · 16 s (base 1 s, ×2, cap 30 s) | never hammer a struggling platform |
| Jitter | deterministic 0–25% from `rowid % 100` | jobs released in the same second don't all return at once, yet runs stay reproducible |
| Retryable | 429 / 503 / 500 / timeout | transient by nature |
| Not retried | 422 validation | permanent — retrying only spins forever |
| `LEASE_TIMEOUT_SECONDS` | 120 | a normal submission takes < 1 s and the worker timeout is 15 s; a more aggressive sweep would steal jobs from *live* workers — the road to double submission |

Subtle rules that were thought through:

- The lease sweep does **not** increment `attempts` — the claim already spent that attempt;
  counting it twice would punish one attempt twice.
- An orphan whose attempts are used up goes straight to `dead`, not `pending`, so no job can
  sit in `pending` forever and block the run from ever being "done".
- The dead-letter decision is made **inside** the release transaction from freshly read
  `attempts`, never from a number the caller carried (which is stale once another worker
  touches the job).
- Retry eligibility (`READY_AT`) is computed in SQL from `updated_at + attempts`, generated
  from the **same** Python function, so the Python and SQL numbers can never silently diverge.

### K6 — A live dashboard that matches the database exactly

- FastAPI + HTMX, one page, polls every 2 seconds.
- Opens SQLite in **read-only** URI mode (`mode=ro`) — the dashboard physically cannot write
  to the queue.
- Binds to `127.0.0.1` only (no auth → never exposed to the network).
- Throughput comes from real attempt timestamps in a 60-second window, not a decorative number.

Proof: 64 polls during P10 and a full-scale check during P11 — **difference vs. the database: 0**.

```
dashboard :8120        DB
Total       49,950     total  | 49,950
Pending          0
In progress      0
Successful  48,273     ok     | 48,273
Failed         844     failed |    844
Dead-letter    833     dead   |    833     → difference 0
```

### K7 — Throughput measured, not guessed (and the ceiling found)

The same 800-record subset was run with 7 different worker counts. Because the chaos is
deterministic, all 7 runs faced **exactly the same failures** (every run ended `ok 776 /
failed 17 / dead 7`, 828 attempts) — only the worker count changed. That makes the comparison
fair.

| Workers | Records/hour | Speed-up | Gain vs. previous |
|---:|---:|---:|---:|
| 1 | 22,204 | 1.00× | — |
| 2 | 40,627 | 1.83× | +83.0% |
| 4 | 63,565 | 2.86× | +56.5% |
| **8** | **81,915** | 3.69× | +28.9% |
| 12 | 85,388 | 3.85× | +4.2% |
| 16 | 84,631 | 3.81× | −0.9% |
| 24 | 80,664 | 3.63× | −4.7% |

- **Saturation point: 8 workers.** Going from 8 → 12 adds only 4.2% while using 50% more
  processes; beyond 12 it gets *slower*.
- **Repeatable:** re-runs differ by < 1% (N=8: 81,915 vs 81,943).
- **The bottleneck was identified:** during N=12 the target container used ≤ 0.52 of 16 cores
  while the host CPU was ~68% busy — the limit is the workers' Chromium CPU, not the target and
  not SQLite. So "going faster" means more machines, not more processes.
- **The rate does not collapse as the queue grows:** a queue 62× larger, killed twice, only
  lowered the rate by 3.6% (63,565 → 61,270 at 4 workers).

**6,000,000-record extrapolation, with the assumptions shown:**

| Basis | Records/hour | 6M records |
|---|---:|---|
| 12 workers (subset peak) | 85,388 | ≈ 2.9 days |
| **8 workers (recommended operating point)** | **81,915** | **≈ 3.0 days** |
| 4 workers, full 50k run with 2 kills | 61,270 | ≈ 4.1 days (the conservative figure used for promises) |

Assumptions stated alongside it (`docs/THROUGHPUT.md` §5): local target with no network
latency or rate limit; one 16-core machine; the 5% failure pattern is already included;
6 million was **never actually run** (it is a measured extrapolation from 50,000); and the
platform's official rate limit always wins over these numbers.

### K8 — Memory stays flat on large Excel files

The 50k-row XLSX is generated with `openpyxl` write-only and read back with read-only
iteration; the loader inserts in batches (one transaction per batch — not per row, which is
slow, and not per file, which costs memory). Dedup is done by the database, not a Python `set`
of 50k keys.

Measured in P5 with `resource.getrusage(RUSAGE_CHILDREN)` around the loader: peak RSS
**50,600 KiB at 10k rows → 57,044 KiB at 50k rows (+12.7%, not 5×)**; the 50k load peaked at
55.71 MiB. (This measurement is recorded in the phase log; see the limitations section.)

### K9 — A client report that refuses to contain jargon

`src/report.py` rebuilds every number from the run's queue (read-only) each time it runs, and
produces:

- **A one-page digest** (`digest.md`) in plain language.
- **`REPORT.xlsx` with 5 sheets:** Summary · By outcome · Speed · Failures · Evidence.

The zero-jargon rule is **code, not intention**: 51 forbidden terms (`lease`, `backoff`,
`BEGIN IMMEDIATE`, `external_ref`, raw status names, …) are matched as whole words, and the
report writer **refuses to write the file** if any slips into a client-facing sheet. Whole-word
matching keeps it from flagging ordinary words that merely contain a term. The single,
deliberate exception is the **Evidence** sheet — it holds the exact SQL command that
reproduces each number, because a report with no way to check it is just a claim.

Raw error messages are never forwarded. Each failure is translated into an actionable sentence
(`human_reason()`): *"The receiving system checked this record and turned it down … the record
needs fixing at the source"* versus *"The receiving system was having trouble … the record is
intact and can be sent again at any point."* A client can do nothing with "HTTP 500"; they can
act on those sentences.

Honesty rules built in: the report never claims the job was killed unless the operator passes
`--kills` (there is a regression test for that), and there is exactly one definition of
duration everywhere (wall-clock from first to last attempt). Sanitised samples, with reference
numbers masked as `REC-••••••`: `assets/sample_daily.md` + `assets/sample_REPORT.xlsx`
(Indonesian, committed to the public repo) and `assets/sample_daily_en.md` +
`assets/sample_REPORT_en.xlsx` (English, on disk — see limitations).

### K10 — Reproducible on a clean copy, in one command

`make all` = target up → generate data → load → run workers → report → **verification gate**.
The gate (`make verify`) exits 1 if anything is unfinished, duplicated, or marked successful
without a confirmation number.

Proven on a clean copy (`rsync` without data/reports/venv, new venv, new container, ports
shifted to 8111/8121 so it runs beside the original):

```
$ make all RUN=p14-clean WORKERS=8 TARGET_PORT=8111 DASH_PORT=8121 \
           TARGET_CONTAINER=surgeline-target-clean
read=50000 inserted=49950 duplicates_rejected=50
total=49950 ok=48273 failed=844 dead=833 dup_ref=0 dup_conf=0 ok/hour=98,650
verify OK: queue finished, dup_ref=0, dup_conf=0, ok without confirmation=0
EXIT=0
```

The result is **identical** to the original full run (ok 48,273 / failed 844 / dead 833) —
deterministic chaos proven all the way down to the final numbers.

### K11 — A secret/leak audit before going public

`scripts/secret_audit.py` (`make audit`) scans what is actually **tracked** — the question is
"what ships if this repo is handed over", not "is my machine clean":

- credential patterns in file contents,
- runtime artifacts accidentally tracked (`.env`, `data/`, `reports/`, `*.db`, `*.sqlite*`),
- required `.gitignore` entries missing,
- absolute machine paths in client-facing files.

Two levels: **leak** (exit 1) and **note** (exit 0 — machine paths inside internal working
docs, printed so the decision to keep them is conscious). The audit has **15 tests** proving
each pattern actually catches its bait.

Before the repo was made public, the **entire history** was scanned, not just HEAD:
**91 tracked files · 0 leaks · 20 commits · 157 unique blobs · 0 credential patterns · no
`.env` / `data/` / `reports/` / `*.db` ever committed.**

### K12 — Silent, captioned videos a non-technical client can follow

| Video | Spec | Content |
|---|---|---|
| `assets/demo.mp4` | 113.9 s · 1920×1080 · H.264 · **no audio** | live dashboard sped up 10×, two `kill -9` moments, closing database queries |
| `assets/explainer.mp4` (English) | 115.2 s · 1920×1080 · 30 fps · **no audio stream** · 14 segments | the problem → how it works → one command → live run → power cut ×2 → the real 50k result → failures → no duplicates → speed → client report → legal boundary |

Rules held while recording: one allowlisted window per segment on a **disposable virtual
output** (never the physical monitor), no audio, no credentials, no personal paths, no other
user windows in frame. Captions are **burned into the image** (no subtitle track), so the video
is fully understandable with the sound off in any player. The English build runs a **language
guard** (`scripts/lang_guard.sh`) over its own caption table and fails on any Indonesian text;
takes with Indonesian on screen were re-recorded, never papered over with a caption. Every
number on screen is re-read from a result database at build time (`docs/VIDEO_PLAN.md` maps
each number to its source file).

The live footage uses a separate 3,000-record demonstration run (`vid-en`), killed twice on
camera (2,464 → 2,903 → 2,907 successes, 0 left, 0 duplicate references) — and the captions
name it as a demonstration so it is never confused with the 50,000-record run.

### K13 — Consultant-level scoping, not just scripting

`docs/CONSULTATION.md` is a one-page note meant to be attached to a proposal: **three questions
asked before agreeing to price and deadline**:

1. **Does the platform have an official API?** If yes, a browser robot is the wrong tool —
   an API call takes tens of milliseconds, is far less fragile, and costs far less to maintain.
   Said even though it shrinks the project.
2. **What is the official sending limit?** The platform's limit, not my speed, decides the
   duration. At 60 submissions/minute the real rate is 3,600/hour, and more machines won't help.
3. **Where is the written authorization?** Without it, "automation" becomes "unauthorized
   access". If the platform uses captcha, bot detection, or terms forbidding automation, the
   work stops and the owner gets a phone call — protections are never bypassed.

A ready-to-paste proposal sentence also exists (`docs/THROUGHPUT.md` §6): *"≈ 82,000 records
per hour with 8 workers on one 16-core machine, against a target that deliberately fails 5% of
requests; at that rate 6 million records take about 3 days — about 4 using the conservative
figure from the 50,000 run I killed twice … and if your platform has an API, a browser isn't
needed at all."*

### K14 — Legal and ethical boundaries enforced in code

- **The test target is owned, full stop.** The worker refuses any base URL whose host is not
  `127.0.0.1` / `localhost` / `::1` (`LOCAL_HOSTS` in `src/worker.py`) — the fence lives in the
  code, not just the README.
- **No protection bypassing:** no captcha solver, no anti-bot evasion, no stealth fingerprints.
- **100% synthetic data:** 50,000 records from a seeded Faker generator, no real people.
- The legal statement is at the **top** of the public README, not buried.

### K15 — Engineering discipline that can be audited

- **15 phases (P0–P14)**, one phase = one session = one artifact = **one commit whose body
  carries its metrics** (21 commits in total, including 2 remediation commits R1/R2 and the
  D16 decision).
- **16 locked decisions** (`D1`–`D16`) that outrank every other document and are not
  renegotiated per session.
- **An explicit document hierarchy** (DECISIONS → SCHEMA → ETHICS → phases → ACCEPTANCE/README):
  a lower document that contradicts a higher one is fixed in the same session.
- **12 acceptance criteria**, each paired with the command that proves it — all ✅.
- **A commit gate** per phase: audit → commit → push; a phase is not ✅ until push succeeds.
- **163 unit tests** (`unittest`, no network — HTML fixtures instead, so the clean-copy gate
  never depends on the internet).

### K16 — Environment engineering (Arch Linux, no sudo)

Playwright does not officially support Arch; it installs `ubuntu24.04-x64` builds.
`playwright install-deps` always fails here — it hardcodes `apt-get` (`spawn apt-get ENOENT`),
so even a sudo password would not help. The project runs with `playwright install chromium`
(no `--with-deps`), and missing WebKit libraries are patched in user space from a disposable
`ubuntu:24.04` container by an idempotent, sudo-free provisioning script. Lesson carried over
from the sibling projects and applied here from day one.

---

## 7. Numbers at a glance (for the portfolio page's stat cards)

| Metric | Number |
|---|---|
| Records processed end to end | **49,950** (50,000 rows, 50 duplicates rejected by the DB) |
| Submitted with a confirmation number | **48,273** (96.6%) — 0 successes without one |
| Forced kills (`kill -9`) during the full run | **2** — still finished 100% |
| Orphaned jobs recovered | **7 / 7** (full run) · 8 / 8 (P9 proof) |
| Duplicate records / duplicate confirmations | **0 / 0** |
| Unfinished jobs at the end | **0** |
| Deliberate target failure rate | **5%** (2,519 records, 3 failure modes) |
| Validation rejections (recorded, not retried) | 844 |
| Dead-letter after 5 attempts (all with a reason) | 833 |
| Total submission attempts | 53,290 |
| Full run duration | **47 min 16 s** (4 workers, including both kills) |
| Measured throughput | **81,915 records/hour** at 8 workers (saturation point) |
| Peak measured | 85,388 records/hour at 12 workers |
| 6M-record estimate | **≈ 3.0 days** (range 2.9–4.1 days, assumptions stated) |
| Throughput repeatability | < 1% spread between runs |
| Loader memory, 10k → 50k rows | +12.7% (not 5×) |
| Dashboard vs. database difference | **0** |
| Parallel claims tested | 500 claims, 4 workers, **0 double-claims** |
| Clean-copy reproduction | `make all` **exit 0**, identical final numbers |
| Leak audit | 91 files · **0 leaks** · 157 history blobs · 0 credential patterns |
| Unit tests | **163 / 163 green** |
| Jargon terms blocked from client reports | 51 |
| Report workbook | 5 sheets (Summary · By outcome · Speed · Failures · Evidence) |
| Videos | demo 113.9 s · explainer 115.2 s · 1080p · no audio · burned-in captions |
| Phases / commits / decisions / acceptance | 15 / 21 / 16 / **12 of 12** |
| Code size | ~3,300 lines engine · ~2,400 lines tests · ~1,550 lines scripts · ~320 lines target app |

---

## 8. How to verify the claims above (real commands)

```bash
git clone https://github.com/rayinailham/surgeline && cd surgeline

make setup        # uv sync --frozen + Playwright Chromium (no --with-deps)
make test         # 163 unit tests
make all          # target -> 50k data -> queue -> workers -> report -> verification gate
make verify       # exit 1 if anything is unfinished, duplicated, or unconfirmed
make audit        # secret/leak audit over tracked files -> 0 leaks
make dashboard    # live read-only status page at http://127.0.0.1:8120

# crash it yourself: stop the run mid-way, then simply
make run          # continues from where it stopped — no cleanup, no restart from zero

# clean copy beside the original
make all TARGET_PORT=8111 DASH_PORT=8121 TARGET_CONTAINER=surgeline-target-clean

# token-cheap inspection of any run
sqlite3 data/<run>/queue.db "SELECT status, COUNT(*) FROM jobs GROUP BY status;"
sqlite3 data/<run>/queue.db "SELECT COUNT(*)-COUNT(DISTINCT external_ref) FROM jobs;"
```

---

## 9. Limitations stated openly (do not hide these in the portfolio)

This section is what makes the other claims credible.

| Limitation | Honest status |
|---|---|
| **6 million records were never actually run** | 50,000 were run; 6M is a *measured* extrapolation with its assumptions written down. Per-job cost was shown flat up to 50k, not up to 6M. |
| **Local target, no network latency** | All speed numbers are against a container on `127.0.0.1` with no rate limit. A real platform will almost always be slower; its official rate limit wins. |
| **One machine, one SQLite file** | Multi-machine operation was not tested and is out of scope. The PostgreSQL upgrade path is documented, not implemented. |
| **Synthetic target, not a real platform** | A deliberate legal decision. The failure modes are realistic and measured, but a real platform will have its own quirks (sessions, logins, layout changes) that need recon first. |
| **Loader memory figure** | The +12.7% RSS result is recorded in the P5 phase log (command + output), but no separate run artifact file was kept on disk — so it was cut from the explainer video, which only shows numbers traceable to a result file. |
| **Lease sweep latency (found, then fixed)** | In the full run, 3 orphans from kill #2 were swept 27 minutes later instead of within ~60 s, because the sweep only ran when the queue looked empty. Impact was latency, not loss (7/7 still recovered). Fixed in remediation commit `R2` (sweep scheduled by time; 41.0 s → 23.0 s). |
| **Live demo run counters** | For the 3,000-record `vid-en` demo run, the queue's audit table records 4 lease-expired attempts, while the working notes mention 8 orphaned claims. The DB figure is the one to quote. |
| **English deliverables not yet in the public repo** | The English explainer video (`assets/explainer.mp4`), English sample report/digest, English diagrams, and the English-variant source edits (dashboard, report, loader, target locale) exist on disk but are **not committed yet**; the public repo's last commit (2026-08-29) predates them. The public repo currently carries the Indonesian demo video, screenshots, diagram, and sample report. Commit + push them before linking the repo from the portfolio page. |
| **No captcha / anti-bot work, ever** | By design. If a client's platform needs that to be "automated", the answer is to stop and ask for authorization or an API. |
| **Linux only** | Windows/macOS support is out of scope (D15). |

---

## 10. What can be offered to the next client

The pipeline is **portable**: the client-specific parts are the target URL, the form selectors
(a small contract table), and the input file's columns. Everything else — the queue, atomic
claiming, retry/dead-letter, lease recovery, dedup, dashboard, throughput bench, report, and
verification gate — works against a data contract, not one particular form.

**Service packages that already have proof:**

1. **Bulk Form Submission System** — Excel/CSV → authorized web platform with no API, with
   confirmation-number capture, duplicate prevention, retries, and crash-resume.
2. **Crash-Safe Queue Engine for Any Bulk Job** — the same engine for calling an API, sending
   messages, or downloading files record by record, where nothing may be lost or doubled.
3. **Resilience / Chaos Testing of an Automation** — prove how an existing script behaves when
   the target fails 5%, is killed mid-run, or is run twice; delivered as numbers.
4. **Capacity Planning for Large Jobs** — measured records/hour per worker count, the
   saturation point, and an honest "N records ≈ Y days" with assumptions.
5. **Live Operations Dashboard** — read-only status page that is proven to match the source of
   truth.
6. **Client Hand-off Pack** — plain-language digest, 5-sheet workbook with an evidence sheet,
   and a silent captioned video explainer.
7. **Pre-project Consultation** — the three questions (API? rate limit? authorization?) that
   often change the price, the timeline, or whether the project should exist at all.

---

## 11. Technical lessons worth telling (material for an "engineering notes" section)

Real traps, found at the cost of real time:

1. **Ordering the queue by `rowid` lets one poison job eat the whole run.** A released job was
   immediately the "best" candidate again: **24 consecutive attempts hit `REC-000215` while 23
   other jobs were never touched.** Fix: claim by `updated_at, rowid`, so a released job moves to
   the back of the line — the same column later carried the backoff schedule.
2. **"Nothing claimable right now" is not "queue empty".** Treating them the same makes workers
   exit while jobs are merely waiting out a one-second backoff. `time_until_ready()` tells the
   two apart.
3. **`INSERT OR IGNORE` swallows every constraint violation, not only duplicates** — validate
   first, check `rowcount`, or bad records vanish silently. And never switch it to
   `INSERT OR REPLACE`: that would wipe status, confirmation, and attempts on reload.
4. **`journal_mode` persists in the file; `busy_timeout` does not.** Open the DB without the
   shared `connect()` helper and you get WAL but no busy timeout → `database is locked` under N
   workers.
5. **A lease that is too short causes double submission.** The sweep would steal jobs that live
   workers are still processing. The lease must exceed a normal submission plus margin.
6. **A periodic sweep that only runs when the queue is empty is not periodic.** Found in the
   full run (27-minute sweep latency), fixed by scheduling the sweep by time.
7. **Cold starts are where concurrency bugs hide.** Four workers hitting a fresh target
   triggered a real `database is locked` inside the target — caught because the worker
   classified it as retryable and the audit trail kept it.
8. **Deterministic chaos turns "it seems to work" into "it matched the prediction".** Because
   each record's fate is known in advance, `dead == server_error set` and
   `failed == validation set` could be checked as booleans.

---

## 12. Repo structure (for the "behind the scenes" section)

| Path | Contents |
|---|---|
| `target/` | the app under test: FastAPI form, confirmation numbers, deterministic 5% chaos, Dockerfile |
| `src/schema.py` · `src/store.py` | locked schema, state machine, atomic claim, backoff, dead-letter, lease recovery |
| `src/load.py` | streamed CSV/XLSX loader with DB-level dedup |
| `src/worker.py` · `src/run.py` · `src/recover.py` | Playwright worker, multi-worker runner, standalone orphan recovery |
| `src/dashboard.py` + `templates/` | read-only FastAPI + HTMX dashboard |
| `src/throughput.py` · `src/report.py` · `src/report_en.py` | speed measurement, client reports (ID/EN) with jargon gate |
| `src/test_*.py` · `src/tests/` | 163 unit tests (schema, loader, worker, concurrency, resilience, dashboard, throughput, report, audit, target contract/chaos/cold-start) |
| `scripts/` | data generator, target oracles, scale bench, run summary, secret audit, video build scripts, language guard |
| `docs/` | 14 documents: decisions, schema, target, chaos, architecture, resume proof, throughput, ethics, consultation, client report, data dictionary, tools, acceptance, video plan |
| `phases/` | 15 phase files, each with its Definition of Done ticked against real output |
| `assets/` | architecture diagrams, before/crash/after screenshots, `demo.mp4`, `explainer.mp4`, sanitised sample reports |
| `data/` · `reports/` | run queues and raw output — **gitignored**, never overwritten (one run = one folder) |

---

## 13. Glossary (for non-technical readers of the portfolio page)

| Term | Short meaning |
|---|---|
| **Queue / work list** | the list of records still to send, kept in a file on disk so it survives a crash |
| **Worker** | one automated browser that fills and submits the form; several run in parallel |
| **Confirmation number** | the reference the platform shows after a successful submission — the proof it went through |
| **Duplicate submission** | the same record sent twice — what fragile scripts do after a restart |
| **Crash recovery / resume** | after being stopped, continuing from where it left off instead of starting over |
| **`kill -9`** | stopping a program instantly with no chance to clean up — like cutting the power |
| **Orphaned job** | a record that was mid-submission when its worker died |
| **Lease** | a time limit on how long a worker may hold a record; after it, the record returns to the queue |
| **Retry with backoff** | trying again after waiting a little longer each time (1, 2, 4, 8, 16 seconds) |
| **Dead-letter** | records that still failed after every retry — parked with their reason, never lost |
| **Chaos testing** | making the test system fail on purpose to prove the automation survives it |
| **Throughput** | how many records per hour are successfully submitted |
| **Saturation point** | the worker count after which adding more no longer makes it faster |
| **Clean copy** | a fresh copy of the project on a different folder and ports, used to prove results reproduce |

---

*This document was assembled from `surgeline/README.md`, `STATE.md`, `PLAN.md`,
`docs/DECISIONS.md`, `docs/ACCEPTANCE.md`, `docs/ARCHITECTURE.md`, `docs/SCHEMA.md`,
`docs/TARGET.md`, `docs/CHAOS.md`, `docs/RESUME_PROOF.md`, `docs/THROUGHPUT.md`,
`docs/CONSULTATION.md`, `docs/CLIENT_REPORT.md`, `docs/ETHICS.md`, `docs/TOOLS.md`,
`docs/VIDEO_PLAN.md`, `phases/phase-05/06/07/08/10/11/14-*.md`, the `Makefile`, the code in
`src/` + `scripts/`, and direct read-only queries against `data/full50k/queue.db`,
`data/full50k/run.json`, and `data/vid-en/queue.db`. Every headline number above was re-checked
against the result database, not copied from memory.*
