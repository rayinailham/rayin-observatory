# Capability Dossier — DueWatch (Ops Automation: Expiry Tracking + Auto Follow-up)

> **Source material for the portfolio page.** This document summarizes *what can be shown to
> a client* from the `duewatch` project and its independent audit
> `duewatch-review-2026-09-06`: the tools mastered, the skills proven, the numbers that can be
> defended, the deliverables that actually exist on disk, and — deliberately — the findings
> that an adversarial review produced against our own work. Every claim here has a file or a
> command behind it.

| Meta | Value |
|---|---|
| Project name | **DueWatch** |
| Category | Ops Automation · Scheduled Jobs · Spreadsheet Tracking · Message Triage · n8n Workflow · Safety Guardrails |
| Local repo | `/home/rayin/Projects/Testing/duewatch` (no git yet — publication is a separately-authorized step, decision D9) |
| Independent review | `/home/rayin/Projects/Testing/duewatch-review-2026-09-06` (`probe.py`, `evidence.json`, `review.html`) |
| Status | 12 of 13 phases closed · acceptance **A1–A8 ✅**, **A9/A10 open** · packaging phase P12 not closed |
| Work period | 2026-09-04 → 2026-09-06 (12 phases); scheduler still running unattended as of 2026-09-13 |
| Target jobs | Upwork — *"Automated Storage Agreement Tracking System"* ($20–40/hr) **+** *"Build automated workflow for WhatsApp & Email follow up"* ($200 fixed) |
| Proven scale | **200 contracts recomputed per run · 18 runs recorded · 3,600 row-status records · 18 unattended-safe backups · 18 messages triaged with 0 external calls** |

---

## 1. One-sentence pitch

> "Your contract sheet re-checks itself every morning before anyone opens it, your inbox gets
> a decision on every message within about a second, complaints and payment problems are
> handed to a human *by design*, and nobody gets reminded twice — and every single number in
> the demo can be traced back to a file on disk."

The differentiator is not "I can write a cron job." It is this: **the system is built so that
it can be proven, and then it was actually attacked to see whether the proof held.** The
project shipped alongside a fault-injecting review that found seven real defects in its own
code — and that review is part of the portfolio, not hidden from it.

---

## 2. The problem being solved (client framing)

Two Upwork jobs, one complaint underneath both: **"nobody has time to do this every day."**

**Job A — storage/rental agreement tracking.** A dealership keeps agreements in a
spreadsheet. Somebody is supposed to work out, from each receipt date and term, when the
agreement expires, how many days are left, and which ones need renewing *this week*. In
practice the sheet is opened when someone remembers — which is after a customer complains.

**Job B — WhatsApp + email follow-up.** A small business is drowning in inbound questions.
They want automatic replies. What they *actually* need, and rarely ask for in the brief, is
the opposite guarantee: a system that knows **when not to answer**. An auto-responder that
cheerfully quotes a price to an angry customer chasing a double charge costs more than the
silence it replaced.

Three questions neither job description asks, and both clients will ask on the first call:

1. **What happens to my spreadsheet if the script crashes halfway?**
2. **What stops the bot from promising something I can't honour?**
3. **How do I know it ran yesterday, when nobody was watching?**

DueWatch is built around answering those three, with artifacts.

---

## 3. System scope

Two modules, one deliverable. They are joined because they answer the same complaint from
opposite ends: the sheet nobody re-checks, and the inbox nobody clears.

### 3.1 Module A — Expiry tracker (Python)

| Axis | Value |
|---|---|
| Master rows | **200 synthetic contracts** (`data/contracts_master.csv`) |
| Hard date categories | **15, three rows each = 45 deliberately hostile rows** |
| Locked statuses | **5**, mutually exclusive |
| Thresholds | active `> 60` days · due soon `8–60` · **needs renewal `0–7`** · expired `< 0` · bad data |
| Date source of truth | `receipt_date + relativedelta(months=term)` in Python — **never a spreadsheet formula** |
| Schedule | `systemd --user` timer, `OnCalendar=*-*-* 07:00`, `Persistent=true` (cron unit also shipped) |
| Per-run outputs | pre-write backup · derived CSV · SQLite run + row history · JSON summary · dated log |

### 3.2 Module B — Message triage + 24-hour follow-up (n8n)

| Axis | Value |
|---|---|
| Test inbox | **18 synthetic messages** (`fixtures/inbox/msg-001…018.json`) |
| Channels | email **8** · WhatsApp **10** |
| Locked intents | **6** — `tanya_harga`, `tanya_stok`, `tanya_status`, `komplain`, `masalah_pembayaran`, `lainnya` |
| Locked actions | **2** — `auto_reply`, `escalate` (there is no third, softer option) |
| Sensitive classes | **3 of 6** always escalate: complaint, payment problem, and *unknown* |
| Workflow | **19 nodes**, importable `n8n/duewatch.workflow.json`, runs on self-hosted n8n `1.107.4` |
| Delivery | **100% mock.** "Sent" means a row in `data/followup_ledger.json` + a line in `logs/followup.log` |

### 3.3 The fifteen hostile date categories — designed, not collected

Each category gets exactly three rows so that every case maps 1:1 onto a test:

| Category | Expected status on the 2026-09-04 reference date |
|---|---|
| Already past | `kedaluwarsa` |
| Due today | `perlu_perpanjangan` |
| Due tomorrow | `perlu_perpanjangan` |
| Due in 30 days | `segera_habis` |
| Due in 1 year | `aktif` |
| Empty `receipt_date` | `data_bermasalah` |
| Impossible date `31/02/2024` | `data_bermasalah` |
| Impossible month `2024-13-01` | `data_bermasalah` |
| Text format `Jan 5 2024` | `data_bermasalah` |
| Ambiguous format `05-01-2024` | `data_bermasalah` |
| `receipt_date` on 29 February | valid — calendar arithmetic must hold |
| Term **lands on** 29 February | valid — must clamp to 28 Feb in a non-leap year |
| Term zero | `data_bermasalah` |
| Term negative | `data_bermasalah` |
| Term non-numeric | `data_bermasalah` |

> **The two leap-year categories are the whole point.** `2023-02-28 + 12 months = 2024-02-28`
> but `2024-02-29 + 12 months = 2025-02-28`. Almost every hand-rolled "add a year" helper
> gets this wrong, and the bug surfaces once every four years — in production, on a customer's
> renewal date.

> **Ambiguous format is rejected, not guessed.** `05-01-2024` is 5 January to half the world
> and 1 May to the other half. A tracker that quietly picks one is worse than a tracker that
> refuses: the row becomes `data_bermasalah` with a stated reason, and a human decides.

### 3.4 The six intent classes — and why "unknown" escalates

| Class | Action | Reason |
|---|---|---|
| `tanya_harga` / `tanya_stok` / `tanya_status` | `auto_reply` | factual, low-risk, answerable with approved text |
| `komplain` | `escalate` | an angry customer answered by a bot becomes a public complaint |
| `masalah_pembayaran` | `escalate` | money is never an auto-reply topic |
| `lainnya` | `escalate` | **the default is a human**, not a guess |

Conflict rule, locked in `docs/INTENT_CLASSES.md`: if several classes match, the *sensitive*
one wins. Not enough confidence → `lainnya` → human.

---

## 4. Architecture and data flow

```
                    systemd --user timer  (OnCalendar=*-*-* 07:00, Persistent=true)
                                 │
                                 ▼
   data/contracts_master.csv ─► src/daily.py ─► src/tracker.py
        (200 rows, synthetic)        │              │
                                     │              ├─1─► data/backups/<ISO-timestamp>/   BACKUP FIRST
                                     │              ├─2─► src/status.py ─► src/datecalc.py ─► python-dateutil
                                     │              │        (5 locked statuses, 60/7 thresholds)
                                     │              ├─3─► data/contracts_master_tracked.csv   (atomic tmp+replace)
                                     │              ├─4─► data/history.sqlite   runs + row_status (FK, PK, index)
                                     │              └─5─► data/run_summary.json (atomic tmp+replace)
                                     └───────────────────► logs/YYYY-MM-DD.log + data/daily_summary/YYYY-MM-DD.json

   fixtures/inbox/*.json  ──►  n8n (duewatch-n8n :5678, container-scoped)
        (18 messages)              │  Run Fixture Batch / Receive One Mock Message
                                   ▼
                        HTTP ─► duewatch-classifier:8080/classify
                                   │   (src/classify_server.py → src/classify.py, DUEWATCH_LLM=off)
                                   ▼
                        Auto Reply or Escalate  (switch)
                          ├── Log Mock Reply ──────┐
                          └── Log Mock Escalation ─┤
                                                   ▼
                                        Merge → Sort → JSON file
                                        data/n8n_run.json + data/followup_ledger.json
                                                   │
                          Schedule 24h Follow-up Check (scheduleTrigger)
                                                   ▼
                                  Apply Idempotent 24h Reminder (code)
                                  scripts/run_followup.py mirrors the same policy
                                                   ▼
                                  logs/followup.log  ("sent" = MOCK_LOCAL_LOG)
```

### Binding architectural rules

1. **Back up before you write. Always.** `src/tracker.py` copies the master into
   `data/backups/<ISO-timestamp>/` *before* reading a single row. Clients fear losing the
   sheet far more than they fear waiting one more day for the report.
2. **The master is never mutated.** Derived columns (`expiry_date`, `days_until_expiry`,
   `status`) go into a separate `_tracked.csv`. The input file and the output file are
   different files, with different jobs.
3. **Atomic publication.** Every CSV and JSON write goes to `path.tmp` and then
   `Path.replace()` — a reader never sees a half-written sheet, and a crash mid-write leaves
   the previous file intact.
4. **Bad rows never stop the run.** An unparseable date makes *that row* `data_bermasalah`
   with a recorded reason; the other 199 rows still get computed. A tracker that dies on row
   19 of 200 is not a tracker.
5. **One classification engine, one contract.** The n8n workflow does not re-implement
   classification in JavaScript; it calls the Python classifier over HTTP on an internal
   Docker network. The rules exist in exactly one place.
6. **Nothing leaves the machine.** The n8n workflow is validated to contain zero credentials,
   exactly one HTTP target (`http://duewatch-classifier:8080/classify`), and no node type
   outside a 10-entry allowlist. `external_calls = 0` is asserted, not asserted-by-vibes.
7. **The contract is locked before the code.** Phase P3 was a hard gate: no engine, no
   classifier, no sheet writer could be written until `docs/SCHEMA.md` and
   `docs/INTENT_CLASSES.md` were frozen. The `StrEnum`s in `src/schema.py` are the executable
   form of those documents.

---

## 5. Tools mastered and proven in this project

| Tool | Used for | Why this one |
|---|---|---|
| **python-dateutil** (`relativedelta`, `isoparse`) | calendar-month arithmetic, strict ISO parsing | month math that clamps correctly on 29 Feb and month-end; the single most error-prone part of the job |
| **SQLite (stdlib `sqlite3`)** | `data/history.sqlite` — `runs` + `row_status`, FK enforced, composite PK, status index | run history that survives restarts, with no server to install at the client |
| **systemd `--user` timer** | real unattended scheduling, `Persistent=true` catch-up | a timer the client's machine already has; no daemon, no root, no supervisor |
| **cron** (`deploy/crontab.txt`) | the same job for clients who don't run systemd | portability, one line |
| **n8n 1.107.4 (self-hosted, Docker)** | the message workflow the client can open, read, and edit themselves | the sales argument: the client owns the flow, not a black box |
| **Docker Compose** | `duewatch-n8n` + `duewatch-classifier`, private network, healthchecks, `--wait` | isolated from the host infra, no port collisions, reproducible bring-up |
| **`http.server` (stdlib)** | the classifier HTTP adapter for n8n | zero-dependency internal service; body-size limit + strict field validation |
| **pytest** | **44 tests**, 0.05 s | boundary tests as first-class deliverable |
| **uv (Python 3.13.13)** | venv + `uv.lock` | client onboarding is `uv sync` |
| **GNU Make** | `make setup / test / run / n8n-test / all` | one runner, matching the other projects |
| **ffmpeg / ffprobe** | normalize, burn captions, concat, then **verify** the result | deterministic CLI editing and machine-checkable output |
| **wf-recorder + Hyprland headless output** | record demo segments on a disposable virtual output, never the real monitor | privacy-safe recording on a Wayland desktop |
| **jq / grep / wc** | every claim check in the build guards | token-cheap, scriptable, auditable |
| **`unittest.mock` + `tempfile`** | fault injection during the review (see §7) | break the system on purpose, in a throwaway directory |

### MCP servers used (and the limits held)

| MCP | Used for | Limit held |
|---|---|---|
| `n8n` | node lookup, workflow validation, assembling `duewatch.workflow.json` | build-time only — the deliverable is a JSON file the client imports |
| `serena` | symbol and cross-file navigation once `src/` grew | never a substitute for reading the file being changed |
| `excel` | optional `.xlsx` I/O when a client's master is a workbook | **CSV + Python remain the source of truth**; no date logic in spreadsheet formulas |
| `chrome-devtools` / `playwright` | rendering the HTML evidence cards for the video | presentation only, never in the runtime path |

> **The rule enforced across the whole project:** *MCP and AI are allowed while BUILDING; the
> delivered system must run without them.* The shipped runtime is Python + SQLite + n8n +
> systemd. No MCP, no agent, no model call on the critical path — and `DUEWATCH_LLM=off` is
> the compose default.

### Skills / methodologies applied

| Skill | Used in | For what |
|---|---|---|
| `phase-harness` | whole project | 13 phases (P0–P12), one phase per session, file-based memory (`PLAN`/`STATE`/`DECISIONS`/`SCHEMA`/`ACCEPTANCE`/`phases/`) |
| `unattended-run` (pattern) | P6 | real timer, dated logs, simulated business dates kept separate from real execution time |
| `artifact-diagram` | P10 | `assets/n8n_flow.html` — inline-SVG flow diagram for non-technical readers |
| `artifact-css` | P10 | `assets/one_pager.html` — the Before/After one-pager |
| `device-screen-recording` | P11 | 8 segments on a disposable `HEADLESS-*` output, no audio, never `eDP-1` |
| `evidence-guard` (pattern) | P10–P11 | `docs/EVIDENCE.md` claim map + build-time number guards |
| `skill-harvest` | post-project | produced the reusable **`scheduled-ops`** skill (see §9) |

---

## 6. Proven capabilities

Each item is written as a capability that can be claimed to a client, with the proof beside it.

### K1 — Calendar-correct date engine, proven at the boundaries

**44 unit tests, 0.05 s, exit 0.** Not "it works on my data" — the boundaries are pinned:
days-remaining `61 / 60 / 8 / 7 / 0 / -1` each assert a specific status, so the 60-day and
7-day thresholds cannot drift silently. 17 tests cover parsing alone
(`tests/test_datecalc.py`), 25 cover status and thresholds (`tests/test_status.py`).

Leap-year behaviour is asserted both ways: a term that *starts* on 29 February, and a term
that *lands* on 29 February in a non-leap year (clamps to 28 Feb).

Strictness is a feature, encoded in regex, not in hope:

```python
ISO_DATE         = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
POSITIVE_INTEGER = re.compile(r"0*[1-9][0-9]*\Z")
```

`True` is rejected as a term (Python would otherwise happily treat it as `1`), `0` and `-3`
are rejected, `"1.5"` is rejected, `"Jan 5 2024"` is rejected, `"05-01-2024"` is rejected as
ambiguous rather than guessed.

### K2 — 100% agreement with a manual audit

**A2, the acceptance criterion clients actually care about:** on the 2026-09-04 reference
date, a manual audit of all 200 rows produced exactly **7** contracts needing renewal —
`DW-0004` … `DW-0009` plus `DW-0056`. The engine produced the same 7. `data/cases.md` records
the hand-audited list; `data/run_summary.json` records the machine's; they match 7/7.

`DW-0056` is the important one: it is not in the hand-crafted hostile block at all — it fell
into the renewal window by ordinary arithmetic among the 155 "normal" rows. The manual audit
found it because the audit covered all 200 rows, not just the interesting ones.

### K3 — The spreadsheet cannot be destroyed by a bad run

Four independent mechanisms, all verifiable on disk:

1. **Pre-write backup** — `data/backups/<ISO-timestamp>/contracts_master.csv`, one directory
   per run. **18 backup directories exist**, one per recorded run.
2. **Separate output file** — the master is opened read-only; derived data lands in
   `contracts_master_tracked.csv`.
3. **Atomic replace** — `tmp` file then `Path.replace()`, with `unlink(missing_ok=True)` in a
   `finally` so a failure leaves no `.tmp` litter.
4. **Structural validation before anything is written** — exact column tuple, non-empty
   `contract_id`, unique `contract_id`, non-empty `customer`. A mangled import fails *loudly*
   and early, instead of quietly producing a 200-row file of `data_bermasalah`.

### K4 — Real unattended execution, proven after the project ended

This is the strongest single piece of evidence in the project, and it accumulated **after**
the build was finished, without anyone touching it.

`duewatch.timer` is installed, `enabled`, `active`, and has been firing on its own:

| Real date | Fired at | Mode |
|---|---|---|
| 2026-09-05 | 07:00:55 | on schedule |
| 2026-09-06 | 10:31:09 | `Persistent=true` catch-up after boot |
| 2026-09-07 | 07:00:16 | on schedule |
| 2026-09-08 | 07:00:36 | on schedule |
| 2026-09-09 | 11:14:54 | catch-up after boot |
| 2026-09-10 | 07:00:27 | on schedule |
| 2026-09-11 | 11:33:32 | catch-up after boot |
| 2026-09-13 | 22:21:48 | catch-up after boot |

**8 unattended firings across 9 calendar days**, on a laptop that is not always on. Each one
produced a backup, a recomputed sheet, a SQLite run row, a JSON summary and a dated log —
`data/history.sqlite` holds **18 runs / 3,600 `row_status` rows**, all `outcome='success'`.

`systemctl --user list-timers` at the time of writing:

```
NEXT                        LEFT  LAST                           PASSED     UNIT
Mon 2026-09-14 07:00:00 WIB   8h  Sun 2026-09-13 22:21:48 WIB    31min ago  duewatch.timer
```

**And the honest part, which is the more valuable engineering lesson:** 2026-09-12 has no log
file. The machine was off all day. `Persistent=true` caught the *unit* up on the next boot —
but the catch-up run computed `today = 2026-09-13`, so the 12th's business date was never
computed at all. **Timer catch-up restores the schedule, not the missed business day.** A
production deployment that must not skip a business date needs a backfill step that walks
missing dates explicitly. That distinction is now written into the harvested skill.

### K5 — A "safe by default" classifier, with the brake in front of the model

The rule that sells the second job: **the safety decision is made by deterministic code, and
it overrides the language model.** From `src/classify.py`:

```python
# The deterministic sensitive match overrides every LLM decision.
if fallback in SENSITIVE_INTENTS:
    intent, draft, source = fallback, None, f"{source}+safety_override"
```

Four layered guards, in order:

1. **Keyword pre-classification runs first**, whatever the model later says.
2. **Sensitive override** — if the deterministic pass sees a complaint or a payment problem,
   the model's answer is discarded and the draft is dropped.
3. **Escalation drops the draft entirely** — an escalated message carries no
   `draft_reply` key at all, so there is nothing for a downstream node to accidentally send.
4. **Promise filter** — any surviving draft matching `harga|diskon|tenggat|deadline` is
   demoted to `escalate` with `source` marked `+draft_blocked`.

Every decision is stamped with its provenance: `fallback`, `llm`, `llm+safety_override`,
`fallback+draft_blocked`. A client auditing a bad reply can see *which layer* produced it.

Measured on the fixture set (`data/classify_report.json`): **18/18 intents, 18/18 actions,
6/6 sensitive messages escalated, 0 drafts on escalated messages, 0 errors.** Confusion matrix
is perfectly diagonal across all six classes.

> §7 documents exactly how far that claim does *not* reach — the review broke this guard, and
> the break is reported here rather than buried.

### K6 — Exactly-once reminders, replayed six times

The client's real fear on Job B is not "no reply", it is **"my customers get pestered."**

Policy: no reply from the customer within 24 hours → exactly one reminder, ever. Implemented
as ledger state (`reminder_sent_at`), not as a queue that can be re-drained.

`logs/followup.log`, six consecutive runs:

```
… followup_checked=18 new_reminders=12 total_reminders=12 replied_skipped=1 delivery=MOCK_LOCAL_LOG
… followup_checked=18 new_reminders=0  total_reminders=12 replied_skipped=1 delivery=MOCK_LOCAL_LOG
… followup_checked=18 new_reminders=0  total_reminders=12 replied_skipped=1 delivery=MOCK_LOCAL_LOG
… (three more identical lines)
```

**12 reminders after run 1; 12 after run 6.** Plus three behaviours asserted by a
self-check that ships with the script (`run_followup.py --self-check`, exit 0):

- a customer who replied is **skipped** (`reminder_status = skipped_customer_replied`) — 1 of 18;
- a message at **exactly** 24 hours is `pending`, not sent — the boundary is `>`, documented, tested;
- a `received_at` in the future raises instead of silently sending.

### K7 — WhatsApp's 24-hour window handled as policy, not as an afterthought

Meta's rules are not optional and are usually discovered by the freelancer *after* the client's
number gets restricted. DueWatch encodes them up front:

- inside 24 hours → free-form service reply allowed (still subject to the AI brake);
- outside 24 hours → free-form reply is **forbidden**; the ledger marks the entry
  `window: "template"`, and a production system would require a Meta-approved template;
- no approved template available → escalate to a human.

`7 of 10 WhatsApp entries` in `data/followup_ledger.json` carry `window: "template"`. Email
entries are correctly marked `not_applicable` — the rule is channel-specific, and the code
knows it. The project explicitly refuses to claim its mock templates are Meta-approved.

### K8 — A 19-node n8n workflow the client can open and read

`n8n/duewatch.workflow.json` imports cleanly into n8n 1.107.4 and contains nodes with names
written for the client, not for the developer: `Classify With P7 Rules`,
`Auto Reply or Escalate`, `Log Mock Escalation`, `Apply Idempotent 24h Reminder`.

Two entry points (a manual batch trigger and a webhook for single messages) plus a
`scheduleTrigger` for the follow-up branch. Measured on the P8 run over all 18 fixtures:
**9 auto-replies, 9 escalations, slowest decision 1,161 ms, `external_calls = 0`** — well
inside the acceptance target of under two minutes.

The workflow is also **machine-audited**, by `scripts/validate_n8n_run.py`:

- node types must be a subset of a 10-entry allowlist (no email node, no WhatsApp node, no
  arbitrary shell);
- exactly one HTTP target, and it must be the internal classifier;
- `assert all("credentials" not in node …)` — the export cannot leak a credential reference;
- every result's intent and action must equal its fixture's expectation;
- every sensitive message must be escalated **and** carry no `draft_reply`;
- no draft may contain a forbidden promise term;
- `delivery` must be `MOCK_LOCAL_LOG` on every row.

### K9 — Every number in the demo is traced to a file, and the build refuses to lie

`docs/EVIDENCE.md` is a claim map: ten client-facing claims, each with its canonical artifact
and **the exact command to re-derive it**. Example rows:

| Claim | Canonical source | Re-check command |
|---|---|---|
| 18/18 classification accuracy | `data/classify_report.json` | `jq '{total,overall_acc,action_acc,errors:(.errors\|length)}' data/classify_report.json` |
| 12 reminders, no duplicates | `data/followup_ledger.json` | `jq '[.[]\|select(.reminder_sent_at!=null)]\|length'` |
| 7 WhatsApp template-window entries | `data/followup_ledger.json` | `jq '[.[]\|select(.channel=="whatsapp" and .window=="template")]\|length'` |

More unusually, the document contains a **"Limits of these claims"** section that disarms its
own strongest-sounding numbers — including an explicit instruction that the `30 minutes/day`
figure is a brief scenario and **must not** be presented as measured ROI.

That instruction was then enforced in code: the video build script *excludes* it.
`scripts/build_explainer_video.sh` re-derives every caption figure from its artifact before
encoding a single frame, and `die`s on a mismatch:

```bash
contracts=$(jq -r '.total_rows' data/run_summary.json)
reminders=$(jq -r '[.[] | select(.reminder_sent_at != null)] | length' data/followup_ledger.json)
slowest_ms=$(jq -r '[.[].latency_ms] | max' data/n8n_run.json)
[[ "$slowest_ms" -ge 1000 && "$slowest_ms" -lt 2000 ]] \
  || die "slowest decision ${slowest_ms}ms no longer rounds to about one second"
expect_in_caption seg5_messages 'about one second' "data/n8n_run.json max ${slowest_ms}ms"
```

It also refuses to build if the rendered HTML cards no longer show the current evidence date —
because the daily timer keeps rewriting `run_summary.json` underneath the demo.

### K10 — A silent, captioned explainer video, verified by machine

`assets/explainer.mp4` — **102.5 s, 1920×1080, H.264, `yuv420p`, 30 fps, 2.12 MiB, and zero
audio streams**, confirmed by `ffprobe`, not by memory.

Eight segments of 12.0–14.4 s, each with a burned-in caption of ≤12 words. Captions are
burned into the picture, not shipped as a subtitle track: the video is fully understandable
with the sound off — which matters, because there is no sound. A persistent corner note reads
*"Synthetic data. Every delivery is a local mock log."* on every frame.

Recording was done on a disposable Hyprland `HEADLESS-*` output on isolated workspace 91 —
never the physical monitor — with a throwaway browser profile in `--app` mode so no URL bar,
tab strip, bookmark or history appears, and assets served over `127.0.0.1:8765` rather than
`file://` so no machine-absolute path ends up in a window title.

### K11 — An automated language guard for a bilingual deliverable

The project is built and documented in Indonesian; the client-facing video is English. Instead
of eyeballing translations, `scripts/language_guard.sh` checks **11 sources** — the three
rendered HTML cards, the caption table, the storyboard, and the **live stdout of all six
report sections** — against a ~60-word Indonesian stopword list, and fails the build on a hit.

The detail that shows the work: word boundaries are matched as `[^A-Za-z]`, not `\b`,
specifically because `\b` treats `_` as a word character and would silently miss snake_case
status keys like `status_aktif`. Result: **11 sources checked, 0 Indonesian hits.**

Note the discipline in the *cut list* too: the raw fixture message bodies are Indonesian, and
the keyword classifier matches Indonesian terms — so translating them would have changed the
measured results. The video therefore shows each message's **decision**, never its body.
Presentation was adapted; measurements were not touched.

### K12 — Engineering discipline that can be audited

- **13 phase files**, each with a read-set, an explicit Definition of Done, a mandatory
  validation block, and **pasted real command output** as the evidence for closing.
- **11 locked decisions** (`docs/DECISIONS.md`) with a precedence rule written into the file:
  if a phase file contradicts DECISIONS, DECISIONS wins and the phase file is corrected in the
  same session.
- **A hard gate at P3.** No engine, no classifier, no writer before the schema and intent
  contracts were frozen — and `src/schema.py` is those documents in executable form
  (`StrEnum` + `MappingProxyType`, i.e. the thresholds and the intent→action map are
  immutable at runtime).
- **A scope exclusion list** written before the work started: no real sending, no
  auto-answering complaints, no client WhatsApp account verification.
- **Sensible, boring hygiene:** `.gitignore` excludes `.env`, `data/backups/`, `*.sqlite`,
  `logs/`, `qa/`. No credentials anywhere in the repo. No git history at all, because
  publication is a separately-authorized step (D9) — the discipline includes *not* running
  `git init` without being asked.

---

## 7. The differentiator: we audited our own work, and published what broke

On 2026-09-06 the project was put through an adversarial review that did not trust a single
document in the repo. It lives in `duewatch-review-2026-09-06/` and has three parts:

| File | What it is |
|---|---|
| `probe.py` (6.5 KB) | a read-only harness: runs the real commands, stubs the LLM, injects failures, and models replay — **all writes confined to `tempfile.TemporaryDirectory`** |
| `evidence.json` (4.4 KB) | the machine output: exit codes, stdout/stderr, probe results, a metrics snapshot, and **SHA-256 hashes of 7 source files** so the review is pinned to an exact code state |
| `review.html` (30 KB) | the rendered report, generated from `evidence.json` — every figure in the prose is interpolated from the JSON, so the report cannot drift from its evidence |

### How the review was done (this is the sellable methodology)

- **Nothing was taken on trust.** `STATE.md` said 7 renewals; disk said 1. The review quoted
  disk.
- **The classifier was attacked with stubs, not with the real API.** `unittest.mock.patch`
  replaced `_llm_classify` with a hostile return value, so a dangerous draft could be tested
  **without an API key and without a network call.**
- **Failures were injected.** `_connect_history` was patched to raise `OSError` mid-run, in a
  throwaway directory, to see what state the tracker leaves behind when storage dies after the
  sheet has been written.
- **The validator was given every chance.** When it failed on one assertion, the review
  equalized the two files *in a temporary copy* and re-ran it — exposing a **second,
  independent** failure that the first was masking.
- **Results were reported as data, and the harness said so:** *"a successful probe exit means
  collection finished, not that the project passed."*

### The seven findings — reproduced here on purpose

**4 High:**

1. **The ingest path overwrites follow-up history.** The n8n branch writes the batch result
   straight over `followup_ledger.json` without merging. Replay model: 18 reminders → 0 on a
   repeat of the same ledger → **18 again** once the ledger is replaced by a fresh batch. The
   idempotency proof in K6 is real, but it proves *sequential* idempotency on stored state —
   **not** replay-safe ingestion.
2. **The AI brake can be bypassed.** The forbidden-term regex is only
   `harga|diskon|tenggat|deadline`. Stubbed drafts *"Biayanya Rp500.000, selesai besok."* and
   *"You get 50% off; delivery guaranteed tomorrow."* both reached `auto_reply`. A keyword
   list does not stop synonyms, amounts, percentages or relative dates. And a mixed-intent
   message — *"What's the price? My money hasn't come back and I'm angry!"* — was classified
   `tanya_harga` → `auto_reply`, because the price keyword matched before the complaint one.
3. **The n8n gate was left behind at an older phase.** `Makefile` executes `duewatch-p8` while
   the export's ID is `duewatch-p9`; `validate_n8n_run.py` fails with *"P8 ledger and local
   run log differ"* and, once that was equalized in a temp copy, **still** rejects the P9
   `scheduleTrigger` node type. Verified again while writing this document: **exit 1.** Worse,
   the Make target deletes the evidence ledger before running the check.
4. **Simulated dates were narrated as autonomous days.** Seven `DUEWATCH_TODAY` business dates
   are a legitimate technique under decision D6 — but caption 4 reads *"Seven days in a row.
   Nobody had to remember."* Simulation must be labelled on screen where the claim appears,
   and real scheduler proof presented separately. (K4 above is that separate proof, and it is
   labelled as such.)

**3 Medium:**

5. **Demo figures are not bound to a frozen snapshot.** Because the timer legitimately keeps
   running, `one_pager.html` and `EVIDENCE.md` still say 7 renewals / 112 expired while disk
   said 1 / 118 at review time — and **0 / 119 today**, 2026-09-13. Regenerating HTML does not
   change pixels in a clip recorded a week ago; the fix is an immutable `evidence/<run_id>/`
   snapshot plus a capture manifest of hashes.
6. **A history failure leaves a partial result.** With storage forced to fail after the sheet
   was replaced: the tracked output had changed, but `history.sqlite` and `run_summary.json`
   did not exist. The master was still safe (the backup worked) — but a failed run can leave a
   new output sheet with no matching success/failure record.
7. **Packaging is genuinely unfinished.** No `README.md`, no `scripts/audit.py`, no
   `docs/CLOSEOUT.md`; `make all` is only `setup → test → run` and never touches Module B.
   Acceptance A9/A10 remain open, and this dossier does not pretend otherwise.

### Why this belongs on the portfolio page

A client reading this learns three things that a polished case study cannot tell them:

1. **What "done" means here.** Not "the demo ran" — "we tried to break it, and here is what
   broke."
2. **How defects are reported.** Every finding carries `file:line`, a reproduction, an impact
   statement, *and* a boundary on the impact (finding 2 notes that compose ships with
   `DUEWATCH_LLM=off`, so the draft bypass affects an optional mode — the mixed-intent
   weakness, however, hits the default path).
3. **That the numbers in the marketing material are not the numbers in the evidence file.**
   Where they diverged, the divergence is written down.

---

## 8. Numbers at a glance (stat cards for the portfolio page)

| Metric | Value | Source |
|---|---|---|
| Contracts recomputed per run | **200** | `data/run_summary.json` → `.total_rows` |
| Hostile date categories | **15 × 3 rows = 45** | `data/cases.md` |
| Unit tests / runtime | **44 / 0.05 s**, exit 0 | `uv run pytest -q tests` |
| Renewal rows vs manual audit | **7 / 7 = 100%** | `data/cases.md` vs `run_summary.json` (2026-09-04) |
| Recorded runs / row-status records | **18 / 3,600** | `data/history.sqlite` |
| Pre-write backups kept | **18** | `data/backups/` |
| Dated daily logs / summaries | **12 / 12** | `logs/*.log`, `data/daily_summary/*.json` |
| Unattended timer firings | **8 across 9 real days** (2026-09-05 → 09-13) | `systemctl --user list-timers`, `history.sqlite` |
| Test inbox messages | **18** (email 8 · WhatsApp 10) | `fixtures/inbox/*.json` |
| Classification accuracy on fixtures | **18/18 intent · 18/18 action · 0 errors** | `data/classify_report.json` |
| Sensitive messages escalated | **6 / 6**, zero drafts attached | `data/classify_report.json` |
| Slowest end-to-end decision | **1,161 ms** (target: < 2 min) | `data/n8n_run.json` |
| External API calls in the whole flow | **0** | `scripts/validate_n8n_run.py` |
| Reminders sent / after 6 replays | **12 / 12** — zero duplicates | `logs/followup.log`, `followup_ledger.json` |
| Customers skipped for having replied | **1** | `data/followup_ledger.json` |
| WhatsApp entries marked template-window | **7** | `data/followup_ledger.json` |
| n8n workflow nodes | **19**, 0 credentials, 1 HTTP target | `n8n/duewatch.workflow.json` |
| Explainer video | **102.5 s · 1920×1080 · H.264 · yuv420p · 30 fps · 0 audio streams** | `ffprobe assets/explainer.mp4` |
| Language guard | **11 sources, 0 Indonesian hits** | `bash scripts/language_guard.sh` |
| Self-review findings | **7 (4 High, 3 Medium)**, pinned to 7 file hashes | `duewatch-review-2026-09-06/evidence.json` |
| Phases closed | **12 of 13** · acceptance **A1–A8 ✅, A9/A10 open** | `STATE.md`, `docs/ACCEPTANCE.md` |

### Codebase at a glance

| Area | Lines |
|---|---|
| `src/` (engine, tracker, classifier, scheduler, HTTP adapter, EN labels) | 770 |
| `tests/` (44 tests across 4 files) | 199 |
| `scripts/` Python (generator, eval, follow-up, validator, reporters, renderers) | 1,256 |
| `scripts/` shell (video build, language guard, recording, demo) | 458 |
| `n8n/duewatch.workflow.json` | 333 |
| `docs/` (schema, intents, decisions, acceptance, evidence, tools, video plan) | 558 |
| `phases/` (P0–P12, with pasted validation output) | ~990 |
| Review harness + renderer (`probe.py` + `render_review.py`) | 218 |

---

## 9. Reusable asset produced: the `scheduled-ops` skill

The project did not end at the deliverable. It was harvested into a reusable methodology now
installed at `~/.config/opencode/skills/scheduled-ops/` (byte-identical to the draft in
`duewatch-review-2026-09-06/skill-draft/`), covering:

- **the operational contract** — timezone, calendar-month arithmetic, expiry-day inclusivity,
  threshold inclusivity, and keeping *simulated business time* separate from *actual execution
  time*;
- **reminder scope** — per message, thread, contract, or customer; what reply cancels what;
- **durable state** — "persist transitions, not the latest batch"; a batch result file is not
  a conversation ledger;
- **recovery** — which output is authoritative after a partial failure;
- **guardrails** — approved fixed text for automatic delivery, generated text to human review,
  and the explicit warning that a banned-word regex is supplementary;
- **cumulative verification** — one entry point covering the *final* state, with reset
  separated from verification;
- **frozen evidence** — snapshot bound to an evidence ID, business date, capture time, mode
  (`simulated` / `manual` / `scheduler`) and input hashes.

Its companion `references/failure-cases.md` is a table of ~18 trigger→invariant behavioural
checks, each one paid for by a real defect found in this project — including *"Output written,
history storage fails"*, *"Two workers select the same due item"*, *"Generated draft says
'50% off, guaranteed tomorrow'"*, and *"Card is regenerated but old clip is reused"*.

Its closing line is the honest summary of K6:

> *"Passing the repeated-check case alone proves sequential idempotency on that stored state.
> It does not establish replay-safe ingestion, concurrency safety, restart recovery, or
> exactly-once delivery."*

---

## 10. How to verify the claims above (real commands)

```bash
cd /home/rayin/Projects/Testing/duewatch

# engine
uv run pytest -q tests                    # 44 passed
uv run python -m src.status --summary data/contracts_master.csv

# a full daily run (backup → compute → sheet → sqlite → summary → log)
make run
ls data/backups | wc -l                   # one directory per run
sqlite3 data/history.sqlite "select count(*) from runs; select count(*) from row_status;"

# real scheduling
systemctl --user list-timers duewatch.timer --all
ls logs/????-??-??.log                    # one per business date actually computed

# message side
uv run python scripts/eval_classify.py
jq '{total,overall_acc,action_acc,sensitive_total,sensitive_acc,errors:(.errors|length)}' \
   data/classify_report.json

# follow-up idempotency (run it as many times as you like)
for i in 1 2 3; do DUEWATCH_NOW=2026-09-05T09:00:00 uv run python scripts/run_followup.py; done
jq '[.[] | select(.reminder_sent_at != null)] | length' data/followup_ledger.json    # 12
jq '[.[] | select(.customer_replied==true and .reminder_sent_at!=null)] | length' \
   data/followup_ledger.json                                                        # 0
uv run python scripts/run_followup.py --self-check

# workflow, end to end, in Docker
make n8n-test                             # currently exits 1 — see §7 finding 3

# video and language
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,pix_fmt \
        -of json assets/explainer.mp4
bash scripts/language_guard.sh            # language_guard=PASS checked=11 indonesian_hits=0

# the self-review, reproducible from scratch
cd ../duewatch-review-2026-09-06 && python probe.py
```

---

## 11. Limitations stated openly (do not hide these on the portfolio page)

1. **Nothing is ever sent.** No WhatsApp message, no email, no external API call. "Sent"
   means `MOCK_LOCAL_LOG` in `data/followup_ledger.json`. This was a deliberate decision (D3):
   a mis-sent test blast can get a WhatsApp Business number permanently restricted, and a
   portfolio needs proof that the *flow* is correct, not proof that a message left the
   building.
2. **All data is synthetic.** 200 fictional contracts, 18 fictional messages, fictional
   customer names, `@example.test` addresses, `wa_mock_*` handles. No client data, ever.
3. **100% accuracy means 18 fixtures, not production.** The denominator is small and the
   fixtures were written by the same person who wrote the keyword rules. It is a regression
   baseline, not an accuracy guarantee.
4. **Idempotency is proven sequentially, not under replay or concurrency.** See §7 finding 1.
5. **The AI brake has a known bypass** in its optional LLM mode, and a known mixed-intent
   weakness in its default path. See §7 finding 2.
6. **`make n8n-test` currently fails** (exit 1, verified 2026-09-13). The workflow runs; the
   validator was not carried forward from P8 to P9. See §7 finding 3.
7. **Published demo figures are stale by design drift.** `one_pager.html` and `EVIDENCE.md`
   say 7 renewals / 112 expired; the video says 1 / 118 (2026-09-06); disk today says **0 /
   119** (2026-09-13). The timer is doing its job and the documents did not follow. The fix is
   a frozen snapshot, and it is not yet built.
8. **The `30 min/day → 0 min` figure is a scenario, not a measurement.** It is labelled as such
   in `docs/EVIDENCE.md` and deliberately excluded from the video. It must not appear on a
   portfolio page as measured ROI.
9. **Packaging is incomplete.** No README, no leak-audit script, no closeout doc, no
   clean-copy reproduction gate. A9 and A10 are open.
10. **`Persistent=true` does not backfill business dates.** 2026-09-12 was never computed. See
    K4.
11. **Repo hygiene:** copies of neighbouring projects (`crosscheck/`, `driftwatch/`) sit inside
    the project directory, so a bare `pytest` from the root collects them and errors. Run
    `pytest tests` — or fix the layout before handing the repo over.
12. **No git history.** Deliberate (D9): publication requires explicit authorization and the
    personal account, so `git init` was never run.

---

## 12. What can be offered to the next client

**Directly sellable, today:**

- A daily expiry/renewal tracker over CSV, Excel, or Google Sheets, with calendar-correct date
  math, a locked status ladder, pre-write backups, atomic writes, and run history in SQLite.
- A real scheduler (systemd user timer or cron) with dated logs, plus a documented
  distinction between missed *units* and missed *business dates*.
- Inbound message triage with a locked intent taxonomy, an escalation-by-default policy for
  anything sensitive or unclear, and provenance stamped on every decision.
- A 24-hour follow-up policy with ledger-based state, an explicit boundary rule, and
  reply-cancellation.
- WhatsApp Business 24-hour-window and template policy encoded as behaviour, not prose.
- An n8n workflow the client owns and can edit, with an automated audit that rejects
  credentials, non-allowlisted nodes, and unexpected HTTP targets.
- Client-facing deliverables: an SVG flow diagram, a Before/After one-pager, a silent
  captioned explainer video, and an evidence index mapping every claim to a command.

**The methodology itself, which is the harder thing to buy:**

- Contract-first delivery: freeze the schema and the decision list, *then* write code.
- Phase-based execution with per-phase Definition of Done and pasted command output.
- An evidence map where every client-facing number names its file and its re-check command.
- Build-time guards that refuse to ship a report whose numbers no longer match disk.
- An adversarial self-review with fault injection, replay modelling, and source hashes.

**Honest scope boundary:** live delivery through WhatsApp Cloud API, SMTP/IMAP, or a real
Google Sheets account is *implementable* but was deliberately not implemented here. It
requires the client's credentials, their number verification, and their approved templates —
and it deserves its own authorization, its own outbox with provider idempotency, and its own
reconciliation step, as the `scheduled-ops` skill spells out.

---

## 13. Engineering notes worth telling (material for a "behind the scenes" section)

1. **`relativedelta`, not `timedelta(days=365)`.** Calendar months clamp; 29 February is the
   test that catches everyone.
2. **`isinstance(value, bool)` before `isinstance(value, int)`.** In Python, `True` is an
   `int` equal to 1 — a term of `True` would silently become a one-month contract.
3. **`\b` is the wrong word boundary for snake_case.** `\b` treats `_` as a word character, so
   a language guard using it silently misses `status_aktif`. `[^A-Za-z]` catches it.
4. **The safety decision must not be downstream of the model.** Classify deterministically
   first, let the model refine, then let the deterministic result override. A prompt asking a
   model to "always escalate complaints" is a request; an `if` statement is a guarantee.
5. **An escalated message should carry no draft at all.** Leaving a `draft_reply` key on an
   escalated row is a loaded gun for the next node that iterates the ledger.
6. **A batch result file is not a ledger.** This is finding 1, and it is the single most
   transferable lesson in the project: incoming events must *merge* with durable state, keyed
   by conversation identity, or replaying an ingest wipes the history that proves you only
   reminded someone once.
7. **A validator must be cumulative.** A gate that pins phase N's exact output will reject
   phase N+1's legitimate extensions. Validate *preserved fields and invariants*, not
   byte-equality — and never "fix" a failing gate by deleting the evidence it reads
   (`make n8n-test` currently does exactly that).
8. **Separate runtime state from demo evidence before you record anything.** A correctly
   working timer rewrote `run_summary.json` mid-production and invalidated the rendered cards.
   The build script now refuses to encode when the cards go stale — which is the right
   behaviour, but the real fix is an immutable `evidence/<run_id>/` snapshot.
9. **Choose the audience's language before building, not at the video stage.** Retro-fitting
   English produced a parallel set of renderers, a parallel label module, and a guard script
   to police them. One data model plus a string catalogue would have been cheaper.
10. **Two desktop hazards, found the expensive way, documented in `docs/VIDEO_PLAN.md`:** the
    Caelestia shell paints layer surfaces on *every* output including a fresh headless one
    (fixed by cropping 64 px left / 20 px right), and the session lock covers all outputs while
    `loginctl … LockedHint` still reports `no` — five takes were recorded of a lock screen and
    deleted. Check the first take back before recording the batch.
11. **A terminal recording needs a tail margin.** When the window closes, the bare desktop is
    visible for a fraction of a second before the recorder stops; `TAIL_MARGIN=1.2` makes the
    build fail rather than freeze a wallpaper widget as the closing frame.
12. **Fault injection belongs in a temp directory.** The whole review wrote nothing into the
    project — `tempfile.TemporaryDirectory` plus `unittest.mock.patch` proved the failure modes
    without touching a single real artifact.

---

## 14. Repo structure (for the "behind the scenes" section)

```
duewatch/
├── PLAN.md                 # locked roadmap: 2 modules, 11 decisions, 13 phases, A1–A10
├── STATE.md                # cross-session memory; "disk beats claims", kept under 100 lines
├── KICKSTART.md            # the working prompt for the next session
├── AGENTS.md               # project-specific operating rules
├── Makefile                # setup / test / run / n8n-test / all
├── docker-compose.yml      # duewatch-n8n + duewatch-classifier, private net, healthchecks
├── docs/
│   ├── SCHEMA.md           # LOCKED: columns, 5 statuses, thresholds, sqlite DDL, summary shape
│   ├── INTENT_CLASSES.md   # LOCKED: 6 intents, 2 actions, AI brake, WhatsApp 24h policy
│   ├── DECISIONS.md        # D1–D11, with a precedence rule over the phase files
│   ├── ACCEPTANCE.md       # A1–A10 tracker; evidence filled only by the owning phase
│   ├── EVIDENCE.md         # claim → artifact → re-check command, plus limits of each claim
│   ├── TOOLS_AND_SKILLS.md # tool/MCP/skill inventory per phase, incl. what was NOT used and why
│   └── VIDEO_PLAN.md       # storyboard, caption traceability, recording hazards
├── src/
│   ├── schema.py           # the locked contracts as StrEnum + MappingProxyType
│   ├── datecalc.py         # strict ISO parsing + calendar-month arithmetic
│   ├── status.py           # 5-status ladder, DUEWATCH_TODAY override, run summary
│   ├── tracker.py          # backup → validate → compute → atomic write → sqlite → summary
│   ├── daily.py            # one scheduled run: tracker + dated log + daily summary
│   ├── classify.py         # keyword pass + optional LLM + safety override + promise filter
│   ├── classify_server.py  # stdlib HTTP adapter for n8n (body limit, strict validation)
│   └── labels_en.py        # English label catalogue for the video-facing reporter
├── tests/                  # 44 tests: parsing, thresholds, boundaries, backup+idempotency
├── scripts/
│   ├── gen_master.py       # deterministic 200-row generator (SHA-256 stable across runs)
│   ├── eval_classify.py    # fixture accuracy + confusion matrix → classify_report.json
│   ├── run_followup.py     # 24h policy + --self-check
│   ├── validate_n8n_run.py # workflow + result audit (allowlist, no credentials, 0 external)
│   ├── report_en.py        # 6 English evidence sections, read live from artifacts
│   ├── render_video_assets.py / render_closing_card.py
│   ├── language_guard.sh   # 11 sources, Indonesian stopword scan, [^A-Za-z] boundaries
│   ├── record_terminal_segments.sh / build_explainer_video.sh
│   └── demo_terminal.sh / serve_assets.sh / foot-video.conf
├── n8n/duewatch.workflow.json   # 19 nodes, importable, no credentials
├── deploy/                 # duewatch.service, duewatch.timer, crontab.txt
├── fixtures/inbox/         # 18 synthetic messages with expected intent + action
├── data/                   # master, tracked sheet, backups/, history.sqlite, run_summary,
│                           # classify_report, n8n_run, followup_ledger, daily_summary/
├── logs/                   # YYYY-MM-DD.log per business date + followup.log
├── assets/                 # n8n_flow(.en).html, one_pager(.en).html, closing_card_en.html,
│                           # explainer.mp4
└── phases/                 # phase-00 … phase-12, each with DoD + pasted validation output

duewatch-review-2026-09-06/
├── probe.py                # read-only harness; all writes in TemporaryDirectory
├── evidence.json           # exit codes, probes, snapshot, 7 source hashes
├── review.html             # report rendered from evidence.json (figures interpolated)
└── skill-draft/scheduled-ops/   # the harvested skill + failure-cases.md
```

---

## 15. Glossary (for non-technical readers of the portfolio page)

| Term | Plain meaning |
|---|---|
| **Idempotent** | Running it again changes nothing. Run the reminder job six times, the customer still gets exactly one reminder. |
| **Escalate** | Hand it to a human. The system deliberately stops and does not answer. |
| **AI brake** | Hard-coded rules that override the AI's decision when the topic is sensitive — the AI cannot argue with them. |
| **Fixture** | A fake but realistic test case, written by hand so the correct answer is known in advance. |
| **Fault injection** | Deliberately breaking a part of the system to see what state it leaves behind. |
| **Atomic write** | Write to a temporary file, then swap it in. A reader never sees a half-written file. |
| **Ledger** | The permanent record of what was decided and what was sent, one row per message. |
| **24-hour window (WhatsApp)** | Meta's rule: outside 24 hours from the customer's last message, a business may only send a pre-approved template. |
| **Mock delivery** | Everything up to the moment of sending is real; the send itself writes a log line instead of contacting a customer. |
| **Systemd timer** | The operating system's built-in alarm clock. It starts the job at 07:00 whether or not anyone is logged in. |
| **Simulated business date** | Pretending "today" is a different date so a week of behaviour can be tested in seconds. Always labelled as simulated. |
| **Snapshot / frozen evidence** | A copy of the results, dated and hashed, so a demo recorded last week still matches the numbers it shows. |
