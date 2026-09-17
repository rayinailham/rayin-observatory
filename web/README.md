# Rayin Observatory · Personal rooms

## Phase 7C — DriftWatch monitoring room (gate passed, 2026-09-17)

The owner accepted the 21/21 Testing pack and all findings on 2026-09-17. Copy is approved, including the
numbered Day 1–3 illustration; DRAFT labels are removed. The phone verdict distance after Compare is accepted.
The Testing fix (clip-window trace) is part of the approved motion.

Personal brief: a team needs repeatable content data and a way to know when it stops being trustworthy.
The story is last good snapshot → current collection → field diff → a reasoned verdict. Ordinary changes
stay healthy; an empty collection and a run that never started must never look healthy. The instrument is
an archive, not a live dashboard. The existing seismograph leads into a dated paper timeline.

Mobile first: stacked snapshots, tap scenario + Compare, readable before/after field details and an alarm
below. Desktop follows mobile verification: a wide time axis, two snapshots alongside a contextual verdict;
quiet editorial spacing rather than worker lanes. Existing 3D geometry is retained.

Copy approved at gate 7C (was DRAFT during Development/Testing): the room, hotspot bodies, brief clarification,
source ledger, soak timeline, DueWatch teaser and the chapter strip.

| Copy / evidence | Source / boundary |
|---|---|
| Last successful baseline; stable IDs; volatile timestamps excluded; dated snapshots kept | DriftWatch §4; §6 K3 |
| Added/changed/removed are ordinary changes, no alarm by themselves | §6 K1 DO-01–03; no claim that every change is an alarm |
| Layout break → empty collection; five alarm codes | §6 K1 DO-04; controlled test |
| Collector did not start fixture → empty collection | §6 K2; real pipeline failure; symptoms alone do not diagnose the cause |
| Missing run → RUN_MISSING, independent watchdog | §6 K1 DO-09; §6 K5 |
| Recovered failures marked resolved, not deleted; failed days never become baseline | §4; §6 K2 |
| Fictional /guide, /notes, /help, /start titles; comparison marked Day 1–3 | Clearly labelled illustration, not harvested rows or actual daily outcomes; no network collection. Numbered days, not calendar dates, so the illustrated failure never collides with the recorded 01–03 Sep soak (0 alarms) |
| 1,323/day: books 1,000, quotes 100, SEO 23, owned lab 200 | §3.2; §7; role/source labels, no affiliation |
| 11/11 test scenarios, zero false positives in that test | §6 K1; §7; includes three normal-change controls, not eleven alarm events |
| Three unattended days, 12/12 runs; 1–3 Sep 2026 | §6 K5; §9: Sep 1 indirect proof, Sep 2–3 journal; public sources unchanged |
| Dossier checked 13 Sep 2026; archive, not current status | dossier opening date; §9; no long-term monitoring claim |
| Next: scheduled contract checks and human handoff | DueWatch approved deck, teaser only |

Motion contract: chapter trace reveal is a pure function of chapter orbit (reverse scroll reverses it).
Compare draws a quiet trace then a local spike only for an alarm (0.8 s, linear; a clip window opens left → right
so the path never scales and the spike appears in place — Testing fix 2026-09-17), reveals the verdict
(0.2 s, power2.out); text stays stationary. Choosing another scenario kills the old motion and clears the
verdict; repeated Compare restarts the same deterministic comparison, no pending callback queue. Scroll
never resets a comparison. Reduced motion and keyboard compare settle immediately. The entry paper ribbon
unrolls from the projected needle into a full-width timeline (0.7 s, power2.inOut); Return rolls back to the
stored chapter origin. Route/history interruption kills the ribbon. No per-frame root CSS writes.

Development evidence belongs in `assets/renders/personal-driftwatch/dev/`; Testing makes the separate gate pack.

## Phase 7B — SurgeLine dispatch room (gate passed, 2026-09-17)

The owner accepted the 18/18 Testing pack and all findings on 2026-09-17. Copy is approved;
DRAFT labels are removed. Cut may freeze B before it reaches the Form; this behavior is accepted.

Brief: a client has a large spreadsheet and a form-only platform. The fear is a crash that
loses work or sends it twice. The story is saved work list → browser workers → interrupted claim
→ recovery → receipts and explicit failures. Amber means in flight; green means receipt saved only;
red means failed with a reason. The antenna geometry stays; entry/return use expanding/contracting antenna pulses.
Return aims the contracting rings at the antenna point the visitor left from (the case page has scrolled the dish away).

- **Chapter (mobile + desktop):** strip of three browser lanes × 8 records under Open case file, a pure
  function of the chapter orbit (amber sent → green receipt). Lane 2 freezes and shows `cut` between orbit
  .35–.6, then `resumed` and continues from where it stopped. Reverse scroll reverses it.
- **Case, mobile:** four steps → **dispatch board** (saved work list of A–F → three browser lanes ending at a
  Form → Confirmed / Rejected / Dead-letter bins) → narration + one tap button → saved-outcomes ledger.
  Board and button fit one 390×844 view.
- **Case, desktop ≥1024:** steps in one row; one wide board reading left to right (2×3 saved list, three long
  lanes, stacked bins); crash/resume control beside the two-column ledger.

Sources are **portfolio/CAPABILITY_SURGELINE.md in this repository** (Q41), not the former
sibling path. New chapter strip, hotspot bodies, dispatch-room narration, board labels, proof composition,
and DriftWatch introduction were approved at gate 7B. Existing pitch, deck, brief, readings and video stay approved.

| Copy / fact | Source / boundary |
|---|---|
| Queue on disk, atomic ownership, lease (claim) recovery, saved receipt | §3–4; §6 K1–K5 |
| Chapter “input rows · 49,950 unique”; 50,000 → 49,950; 50 duplicate input rows | §3.1; §6 K3; §7 |
| 48,273 confirmed / 844 validation rejections / 833 dead-letter | §6 K2; §7; totals sum to 49,950 |
| 10,621 → 21,508 → 48,273 receipts; two kills; zero duplicates; 7 recovered | §6 K1; §7; whole process group killed in the real run |
| Five attempts; validation not retried; failure reason retained | §3.2; §6 K2/K5 |
| “The 120-second claim expiry is compressed” | §6 K5 `LEASE_TIMEOUT_SECONDS` 120 |
| B sent twice, same receipt, recorded once | §3.2 target idempotency; a required boundary, not a universal platform guarantee |
| ≈3.0 days / conservative 4.1 days for 6M | §6 K7; §7/9; extrapolation only, local target without network delay/rate limit |
| Fictional A–F and DEMO-* receipts | Explicit illustration, not run evidence or a proportionate sample; no submission |
| Next: day-to-day changes | DriftWatch §1; teaser only, no Phase 7C implementation |

Motion contract (board, `components/surgeline-room.tsx`): the guarded reducer owns the stage; GSAP moves chips
between measured `data-slot` places with transforms only, and a chip's colour/send count changes when it arrives.
- **Start** (≈2.1 s): A, B, C leave the list .22 s apart; each lane leg .36 s claim + .66 s travel; A lands in
  Confirmed, C shakes at the form and lands in Rejected, B waits at the form with a pulsing ring (receipt not saved).
- **Cut** (tap any time after Start): B freezes wherever it is, dashed red; lane 2 `offline`; A and C finish their trips.
- **Resume** (≈3.4 s, button disabled): lane 2 shows the claim expiring (.9 s), B returns to its list slot, is claimed
  again, reaches the form a second time (`×2`) and lands last in Confirmed; D and E run lanes 1 and 3; F retries four
  times at the form (`×2…×5`) and lands in Dead-letter; A gets a ring (kept, not re-sent) and never moves.
  Completion is the timeline's end.
- **Replay:** explicit only; chips fade out, return to the list, fade in staggered. Reverse scroll never resets.
- **Interruptions:** repeated taps ignored by the reducer; a width change (or an idle height change) re-rests every chip
  on its slot for the current stage, and a resize during recovery settles on the final outcome. Unmount kills motion.
- **Reduced motion:** chips snap to each stage's pose; recovery settles after 0.9 s so its message is readable.

Performance: scroll-driven custom properties now live on the element that uses them (orbit on each chapter section,
`--journey` on the progress readout, hero vars on `#first-light`, reveal/offset on the scene layer) instead of the root.
At 4× CPU, 390×844, the SurgeLine chapter went from 48.7 fps with 23% slow frames (same on HEAD) to 60.0 fps, 0% slow.

Development verification: `perf_quick.py --slug surgeline` and `run_regressions.py` (suites `dispatch`, `perf-surgeline`
plus all older suites). `dispatch` exports reusable `viewport()` and `edges()` for the Testing pack. Screenshots/JSON under
`assets/renders/personal-surgeline/dev/` are Development evidence only.

Phase 7A (CrossCheck inspection room) passed the owner's gate on 2026-09-16; its copy is approved. See below.

Phase 7 Development: sound design, calibration feedback, micro-interactions and camera transitions.
Phase 0–6 gates passed. All homepage and case copy remains **owner-approved**.
The owner accepted the DueWatch video with its existing simulated-date note at the Phase 5 gate.
Testing (Claude Code / Antigravity) follows developer verification and produces the gate evidence pack.

## Phase 7A — CrossCheck inspection room (gate passed, 2026-09-16)

The copy added in this phase was approved by the owner at the 7A gate (2026-09-16) and the DRAFT label is gone.
Homepage chapter copy, brief, deck, readings, tools, video text and the four flow steps kept their earlier
approval; the items listed below are the ones added in 7A.

### Personal brief

| | |
|---|---|
| Client | A team with a role-based web app (CRM, dealer platform) who needs QA across browsers, screen sizes and user roles, delivered as a spreadsheet they can act on. |
| Problem | The app works on one screen and fails elsewhere; manual passes are slow, can't be re-run, and report the same bug nine times. |
| Story | Three lenses scan three browser lanes → 1,080 visits (422 flagged) plus access checks and flows → 881 raw signals sorted by declared rules → 18 unique issues → open one finding with its steps, expected/actual and screenshot. |
| Proof | 1,080 combinations · 881 signals → 18 issues (562 removed by rule, the rest merged duplicates) · 12/12 planted bugs · 216 access checks → 3 verified. Owned demo target, not a client app. |
| Visual | Telescope + sighting frame, coverage matrix, finding desk. Green = checked clean, red only on problems, amber = inspection UI. |
| Motion | Chapter: lane strip fills with the orbit and follows the lit lens. Entry: iris opens out of the middle lens into an inspection grid, the case opens from the same point; Return closes the case into the lens and reopens at the chapter lens. Case: pinned matrix scrubbed by scroll (map → scan → sort → hand over), pure function of progress so scrolling back reverses it and flicks never queue. Finding tap: 220 ms panel settle + staggered evidence cells. |
| Mobile | One column: 4-step progress row + active step text, matrix fills the stage; 2×2 finding tabs, one screenshot at a time with a tap toggle (no hover, no drag). |
| Desktop | Steps rail left, matrix with route labels right; finding list sticky left, evidence desk right with before/expected side by side, evidence strip beside the reproduction steps; sighting frame around the telescope. |

### Data and evidence sources

- `lib/crosscheck-run.ts` is generated by `scripts/build_crosscheck_run.py` from the recorded CrossCheck run
  (`/home/rayin/Projects/Testing/crosscheck/qa/out/`: `results.jsonl`, `run_summary.json`, `permissions.csv`,
  `flows_results.json`, `issues.json`). The script refuses to write unless it reproduces the dossier totals:
  1,080 cells, 422 flagged, 877 sweep findings, 40 pages, 216 access checks / 3 violations, 5 flows / 1 failed,
  18 issues = 3 High / 14 Medium / 1 Low. Same source as dossier visual V1 (heatmap).
- `public/images/crosscheck/*.png` are crops (panels + their red/green annotation borders, no retouching) of
  the project's own English evidence images: V4 before/after 1–3 (`assets/v4_before_after_{1,2,3}_en.png`)
  and the flow screenshot at the failed step (`qa/out/shots/flow_update_post_and_crm_owner_step5.png`).
- The sorting beat in the matrix is simplified to whole page rows (rows without a reported issue grey out);
  the figure caption says so, and says it is a replay, not a live run.

### New copy (approved at the 7A gate) → dossier (`portfolio/CAPABILITY_CROSSCHECK.md`)

| Where | Copy | Source |
|---|---|---|
| Chapter strip | Lane labels Chromium / Firefox / WebKit; aria "three browsers, each checked at three screen sizes as three user roles" | §3.1 |
| Hotspot 01 | "40 pages × 27 settings" · three browsers, three screen sizes, three roles, eleven checks | §3.1, §3.3, K8 (27 columns) |
| Hotspot 02 | 72 pages × each role against the written policy; suspected leaks reopened in a real browser; 3 confirmed, one not planted | K5, §3.2 (CC-002) |
| Hotspot 03 | Five tasks as editor, reload and read back; "Post updated" yet CRM Owner never stored | K6, §3.2 PB-12 |
| Step readouts | 72 found · 40 in matrix / 1,080 visits · 422 flagged · 216 access checks · 5 flows / 881 raw signals · 562 removed by declared rules / 18 unique issues · 3 High · 14 Medium · 1 Low | K1, §3.1, K2, K5, K6, K7, §7 |
| Matrix strips | "Access · 72 pages × 3 roles", "Flows · 5 tasks as Editor" | K5, K6 |
| Findings heading/intro | "Four of the 18, with their proof." + pick-a-finding sentence | K7, K8 |
| CC-003 | Title, where (Chromium · Desktop · Editor), steps, expected, actual — verbatim report row | K8 |
| CC-001 | Title, "access is denied with 403", compare with /admin/settings/ | V4 before/after 3 text; K5 (editor + viewer, HTTP 200, Chromium desktop) |
| CC-017 | Title, 390 px vs 768 px, expected/actual | V4 before/after 1 text; §3.2 PB-04; flagged in the 9 phone visits only (result file / V1) |
| CC-015 | Title, "overlap by 37%", stack without overlap | V4 before/after 2 text; §3.2 PB-10; 27 visits (result file / V1) |
| Next teaser | SurgeLine deck "Every row sent once. Every success proven." | approved SurgeLine case deck (Phase 5 gate) |
| Desktop frame label | "Sightline · Chromium · Firefox · WebKit" | §3.1 |

### Developer verification

```bash
/home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/build_crosscheck_run.py   # data + crops
cd web/scripts && timeout 900 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python verify_crosscheck_room.py
```

Writes `assets/renders/personal-crosscheck/dev/` (PNG per check and viewport, `verification.json`).

### Testing and gate (2026-09-16) — passed

The gate pack is built by `scripts/crosscheck_room_evidence.py` into `assets/renders/personal-crosscheck/evidence/`
(phone and desktop walkthroughs, a 0.25x slow-motion reel, contact sheets, `evidence.json`): 16 of 17 items pass.
Testing found and fixed a frame-rate regression: the scene wrote the lens position to a CSS variable on the
page root every frame, restyling the whole page (about 34 fps instead of 60 at 4x CPU). The position now lives in
`apertureScreen` (`lib/cases.ts`). The matrix scrub was lightened too: issue chips slide in without scaling, fades use
`fill-opacity`, cells render with crisp edges. The field scrub still has 11–13% slow frames at 4x CPU; that and the
barely legible CC-001 "Expected" crop were accepted as they are at the gate ("lulus semua aman").

From Phase 7B, regressions run through `scripts/run_regressions.py` and Development checks frame rate with
`scripts/perf_quick.py` before handing over (PLAN §12.3, Q42).

## Phase 7 review and handoff

The existing ambient hum now shares a mute-controlled audio bus with five instrument clicks
(CrossCheck → BrandWall), the welcome sweep, fly-in, return and the two-part Next transition.
Hotspot selection/close and the BrandWall detector produce quiet clicks. Silent entry creates no
AudioContext; muted or hidden tabs create no effects. One-shot sources disconnect after playback,
rapid clicks are rate limited and a transition replaces previous effects. No audio files are downloaded.

The loader follows asset/font readiness without rewinding between model batches. Its dial settles
green when ready; still-view readiness remains amber. Existing slow-load and error messages stay in use.
Since the owner's option B (2026-09-16) Enter waits only for the hero: dome, Saturn and fonts. The
five instrument models are requested after that and appear once loaded; a model that fails after
Enter still switches to the labelled still view. Hero models and the Draco decoder are preloaded
from the HTML, the 3D code ships with the first JavaScript, and fonts are served as Latin WOFF2
subsets of the approved TTFs. Measured on DevTools Slow 4G + 4× CPU (390×844): Enter active at
7.0 s instead of 12.5 s; 787,063 bytes before Enter instead of 1,370,869.
Buttons press without disturbing their layout positions; pointer-only hover arrows, selected leader/card
feedback and a short inspection/menu entrance complete the interaction pass. Navigation owns one
departure timeline and cancels it on route changes so browser Back cannot trigger a stale route push.

Development commands (run browser suites one at a time to avoid competing for the GPU):

```sh
npm run lint --prefix web
npm run typecheck --prefix web
npm run build --prefix web
node web/scripts/verify_audio.mjs
timeout 600 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_showpiece.py
timeout 420 npm run verify:mobile --prefix web
timeout 300 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_case.py
```

New PNGs/JSON: `assets/renders/showpiece/dev/`. The browser suite tests 390×844 → 360×740 →
430×932: actual Web Audio signal/silence, five distinct click schedules, chain/return, persistent
Canvas, loader monotonicity, remembered mute, hidden-tab lifecycle (simulated visibility event),
stalled-load escape, audio-unavailable entry and Back during a departure. The separate Node test
controls resume timing, voice limits and cleanup. These are Development checks. Testing must still
measure PLAN §11 with CPU throttle/slow 4G and supply MP4/PNG/contact sheet/`evidence.json` under
`assets/renders/showpiece/evidence/` before the owner gate. Physical-phone testing remains Phase 8.

## Phase 6 review and handoff (gate passed 2026-09-15)

Open the preview on a desktop, enter, then use Work / About / Contact in the header.
The desktop composition begins at 1024px: a left reading rail and a large instrument on the right.
Case files use a two-column brief, a separate inspection pane beside component cards, a horizontal
workflow, and reading/tool grids. The approved mobile composition remains below that breakpoint.
The portrait uses an appropriate desktop image size. Business copy, readings, routes and assets are unchanged.

Development verification (mobile first, then 1366×768, 1440×900 and 1920×1080):

```sh
timeout 900 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_desktop.py
timeout 420 npm run verify:mobile --prefix web
timeout 300 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_case.py
```

Development PNGs and `verification.json`: `assets/renders/desktop/dev/`.
The same script accepts `--breakpoints-only` (768→1024→1440→390, one live Canvas) and
`--hotspots-only` (wait for the selected marker color before recapturing); each writes a separate JSON result.
Testing evidence pack (owner gate), after the development suites above have passed on the current build:

```sh
cd web/scripts && timeout 1500 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python desktop_evidence.py
```

Output `assets/renders/desktop/evidence/`: 1440×900 MP4 of the main flow, one PNG per item, labeled
contact sheet, desktop/resize/phone sheets and `evidence.json` (exit 1 on any fail). Testing fixed the
desktop Skills/About grid (text rows no longer stretch to the portrait/accordion height).
The owner passed this gate on 2026-09-15 after reviewing the desktop video.

## Run

From the project root:

```sh
npm ci --prefix web
npm run build --prefix web
npm run start --prefix web
```

Open `http://127.0.0.1:8767/`. Development: `npm run dev --prefix web`.
The production preview binds to `0.0.0.0:8767`. On the same Wi-Fi, use the computer's LAN IP;
the local firewall may need an owner-managed rule. Do not change domain or DNS settings.

For a temporary phone preview without changing the firewall:

```sh
docker run --rm -d --name rayin-observatory-preview-tunnel --network host \
  cloudflare/cloudflared@sha256:b269e8abd07a5bf6f3f4be65d5050b2174eca89c56a0241a8ff32a16aec454e4 \
  tunnel --no-autoupdate --protocol http2 --url http://127.0.0.1:8767
docker logs rayin-observatory-preview-tunnel
```

Use the HTTPS `trycloudflare.com` link printed in the log. It exposes only this production
web app. The hostname is temporary and changes when the tunnel restarts. Stop after review:
`docker stop rayin-observatory-preview-tunnel`. Stop the app with Ctrl+C in its terminal.
This is a temporary development preview. Deployment belongs to Phase 8.

## Phase 3 review and handoff

Enter → scroll past the dome → CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall.
Each chapter pins, the camera orbits, and the instrument has its own idle movement.
Since Phase 5 every chapter's Open case file flies into `/work/<slug>`; the Phase 3 preview dialogs are removed.

Menu → Skills. Expand a group and choose a project beside a skill: the page returns to that
instrument, highlights its title and focuses the heading after the scroll finishes.
Menu → About shows the approved portrait with a scroll-driven scan reveal.
Menu → Contact shows the Email me CTA (`mailto:`) and Email / LinkedIn / GitHub / Upwork links.
Destinations were supplied by the owner on 2026-09-15 (Upwork share tracking parameter removed).
Link labels show the name "Rayina Ilham", never the account handle; only the email shows the address.

Daily-work tools Go, MySQL / TiDB and Redis were confirmed by the owner on 2026-09-15 and appear
in the Skills group "Daily work" without project links (they are not part of the five case files).
The CrossCheck pitch/reading was accepted at Phase 2; the rest of the homepage copy was approved
at the Phase 3 gate (2026-09-15). New copy in later phases starts as DRAFT again.

Developer screenshots and JSON: `assets/renders/full-observatory/dev/` from the project root.
This folder is separate from the later Testing pack at `assets/renders/full-observatory/evidence/`.
The owner judges the gate after Testing; no physical-phone test is requested before Phase 8.

## Copy provenance

All dossiers are in `/home/rayin/Projects/Testing/portfolio/CAPABILITY_<NAME>.md`.
Source references below describe portfolio demonstrations, not client production results.
Every row below was approved by the owner at the Phase 3 gate (PLAN §3 Q32); "DRAFT" in the
source column records how the wording was produced, not its current status.

| Visible copy | Source / status |
|---|---|
| Rayin Observatory; Rayina Ilham | Owner-locked identity, PLAN §8 |
| Enter the Observatory; Enter without sound; Calibrating instruments… | PLAN §6 |
| I automate. I test. | DRAFT synthesis: SurgeLine §1 + CrossCheck §1; automation emphasis requested by owner in this session |
| I’m an automation engineer. I build systems that test web apps, fill forms and monitor changing data. | Role: owner clarification; capabilities: CrossCheck / SurgeLine / DriftWatch §1; DRAFT wording |
| The observatory is open. | DRAFT interface copy, PLAN §6 |
| 01 / Web QA; CrossCheck | CrossCheck meta category, PLAN §5 order |
| I test your web app across browsers, screen sizes and user roles, then deliver a clear list of issues. | CrossCheck §1; accepted at Phase 2 gate |
| 1,080 test combinations · On an owned demo app | CrossCheck meta Proven scale + §3.1 / §3.2; accepted at Phase 2 gate |
| 02 / Form automation; SurgeLine | SurgeLine meta category, PLAN §5 order |
| I turn your spreadsheet into a resumable form-filling workflow, with a confirmation number for every success. | SurgeLine §1, §3.1; DRAFT condensation |
| 50,000 records processed · Synthetic data · owned test form | SurgeLine meta Proven scale, §3.1, §6 K1/K2; processed includes recorded terminal failures, not 50,000 successful submissions |
| The crash-recovery demo uses synthetic records and an owned form with server-side duplicate protection. | SurgeLine §3.2 and §9; preview-dialog context, removed from the site in Phase 5 |
| 03 / Data monitoring; DriftWatch | DriftWatch meta category, PLAN §5 order |
| I collect your web data on a schedule and flag source changes before silent failures spoil your reports. | DriftWatch §1, §3.1; DRAFT condensation |
| 11/11 planted failures caught · In a controlled failure test | DriftWatch meta Proven scale, §1, §3.1 local drift lab; controlled recall, not a universal detection guarantee |
| The detection reading comes from deliberately planted failures in an owned test site. | DriftWatch §3.1 / §3.2; preview-dialog context, removed from the site in Phase 5 |
| 04 / Expiry & follow-up; DueWatch | DueWatch meta category, PLAN §5 order |
| I build daily expiry checks and follow-up workflows that hand sensitive messages to a person. | DueWatch §1, §3.1 / §3.2 / §3.4; DRAFT, no live message delivery claim |
| 200 contracts checked per run · Synthetic contracts · mock delivery | DueWatch meta Proven scale, §3.1 master rows / §3.2 delivery |
| The demo uses synthetic contracts and mock message delivery. Live sending is not demonstrated. | DueWatch §3.1 / §3.2; preview-dialog context, removed from the site in Phase 5 |
| 05 / Visual design QA; BrandWall | BrandWall meta category, PLAN §5 order |
| I test brand assets across your product surfaces and themes, then report where layouts break and which CSS rules fix them. | BrandWall §1 / §2; DRAFT condensation |
| 300 screenshots per run · Generated brands · owned test app | BrandWall meta Proven scale, §3.1 / §3.3; generated assets, no brand affiliation |
| The screenshots use generated brand assets on an owned test app, with no claimed brand affiliation. | BrandWall §3.3 / §9; preview-dialog context, removed from the site in Phase 5 |
| I build tools that check web apps, move spreadsheet rows through forms, and keep watch over changing data. | About DRAFT: CrossCheck / SurgeLine / DriftWatch §1 |
| I test what happens when things go wrong, then turn the results into clear reports. The work here uses owned test apps, synthetic data and documented sources, with limits stated alongside the proof. | About DRAFT: CrossCheck §3 / §6, SurgeLine §3 / §6, DriftWatch §3.2, DueWatch §3 / §7, BrandWall §3 |
| What needs a closer look?; Tell me what you need to test, automate or monitor. | Contact DRAFT synthesis of the same project categories; no availability or commercial promise |
| Skills, with proof.; Choose a project beside each skill to explore the work behind it. | DRAFT interface copy; links are mapped in `lib/skills.ts` |
| The toolkit; Behind the instruments; Start a conversation; Email me | DRAFT labels, PLAN §4 / §6 / §9 |
| Daily work (Skills group) | PLAN §9 "Kerja harian"; owner confirmation 2026-09-15 |
| rayinailham9@gmail.com; LinkedIn / GitHub / Upwork links labeled "Rayina Ilham" | Owner-supplied destinations, chat 2026-09-15 |
| Open case file; Scroll to orbit the instrument; menu/readout/error text; Back to the dome | DRAFT interface copy, PLAN §6. "Case file preview", "The full case file is coming soon." and the dialog's "Return to the instrument" were removed with the preview dialogs in Phase 5 |
| Tap to observe · detector off, wave pattern / detector on, particle pattern | Owner-approved 2026-09-15 (revision): BrandWall observer readout replaces its orbit hint; double-slit metaphor, no project claim |

### Skill-to-project source map

The site lists ordinary market-facing skills, never internal agent skill names. Tools are linked
only to projects with dossier evidence. PLAN §9 groups remain the guide; exact links are narrowed
where the dossiers distinguish runtime use (e.g. cross-browser testing only CrossCheck;
HTMX only SurgeLine; cron only DueWatch). No change to locked PLAN decisions.

| Skill / tool | Project proof | Source |
|---|---|---|
| Python | All five | Each dossier §3–§5 |
| Playwright | CrossCheck, SurgeLine, BrandWall | Each §5 |
| Cross-browser Chromium / Firefox / WebKit | CrossCheck | CrossCheck §5; others use Chromium for runtime work |
| Visual regression / design QA; Pillow, NumPy | BrandWall | BrandWall §5 |
| pytest | DueWatch | DueWatch §5 |
| unittest | CrossCheck, SurgeLine, DriftWatch, BrandWall | Each §5 |
| httpx; tenacity | DriftWatch, CrossCheck | Both §5 |
| selectolax; pydantic | DriftWatch | DriftWatch §5 |
| FastAPI | BrandWall, SurgeLine | Both §5 |
| HTMX | SurgeLine | SurgeLine §5 |
| WordPress / PHP · test target | CrossCheck | CrossCheck §5 |
| SQLite | SurgeLine, DriftWatch, DueWatch, CrossCheck | Each §5 |
| n8n | DueWatch | DueWatch §5 |
| systemd timers; Linux | DriftWatch, DueWatch | Both §3 / §5 |
| cron | DueWatch | DueWatch §5; DriftWatch explicitly did not use it |
| Docker / Docker Compose; GNU Make; uv | BrandWall, SurgeLine, DueWatch, CrossCheck | Each §5 |
| Excel reporting · openpyxl | BrandWall, SurgeLine, DriftWatch, CrossCheck | Each §5 |
| matplotlib | BrandWall, CrossCheck | Both §5 |
| ffmpeg | All five | Each §5 |
| Anthropic Claude API | DriftWatch | DriftWatch §5, optional demo insight |
| AI-assisted engineering · Claude Code / MCP | All five | PLAN §9 + each dossier §5 build-time MCP; not runtime dependencies |
| Go; MySQL / TiDB; Redis | Daily work, no project link | PLAN §9 + owner confirmation 2026-09-15 (PLAN §3 Q33) |

## Assets and behavior

- `assets/blender/build_full_observatory.py` creates four new instrument scenes through Blender
  GUI MCP. It refuses existing output files and dirty GUI state, saves before convert/join,
  exports Draco GLBs and saves each `<slug>-web.blend`. Previous scenes are preserved.
- Render each scene using `bpy.ops.render.render(write_still=True)` via GUI MCP. The saved render
  path points to `assets/renders/full-observatory/<slug>-review.png`. Copy that render to
  `web/public/images/<slug>-fallback.png`. These are original procedural assets; no image textures.
- CrossCheck preserves `OpticsPivot` + `Lens1Glow..Lens3Glow`. New animation contracts:
  SurgeLine `DishPivot0..3`; DriftWatch `NeedlePivot`, `PaperFeed`, `RollerPivot0..1`;
  DueWatch `OrbitPivot0..2`; BrandWall `PrismPivot`, `SpectrumPivot`.
- Scene geometry stays in Blender. Runtime uses cloned materials and node transforms for idle,
  camera orbit, and incoming/outgoing instrument motion. One Canvas remains in the root shell.
- Scroll positions derive from actual chapter bounds. Accordion height changes trigger
  ScrollTrigger refresh via ResizeObserver. Lenis shares one GSAP ticker with ScrollTrigger.
- Approved portrait copied to `public/images/rayina-duotone.png`; Next Image supplies responsive
  sizes. GSAP scroll-triggered clipping and a scan line reveal it. Photo approval is Phase 0.
- Gate waits for all models plus fonts. Any model/WebGL failure offers a labeled still view for
  all five chapters. Slow load provides the same escape after the existing wait threshold.
- All assets, fonts and Draco decoder are local. Web Audio starts only from a user gesture;
  mute is remembered. No analytics, external font service or remote environment map.
- Below 1024px the approved mobile width stays capped at 430px; Phase 6 adds the full-width desktop composition.
  Polish/performance Phase 7, launch Phase 8 and full accessibility Phase 9 remain outside this development scope.

## Verification

```sh
npm run lint --prefix web
npm run typecheck --prefix web
npm run build --prefix web
timeout 420 npm run verify:mobile --prefix web
```

The existing CrossCheck Playwright Python environment runs Chromium at 390×844 first, then
360×740 and 430×932. Checks: entry, audio on/off/memory, one Canvas, all five sticky chapters,
visible idle/orbit pixel differences, readings, all five case routes/return (Phase 5), focus return,
reverse navigation, every skill href, real skill navigation to all projects, portrait, real contact links, readout, 390px touch swipe, and a deliberately blocked new model → five still views.
`verification.json` records running/passed/failed and timestamps; screenshots go to the dev folder.
These checks do not replace the separate Testing stage or prove physical-device FPS/4G targets.

Testing-stage evidence pack (server :8767 running):

```sh
timeout 600 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/full_observatory_evidence.py
```

Writes `assets/renders/full-observatory/evidence/`: one PNG per checklist item, 390×844
walkthrough MP4, `viewports/` (360×740 + 430×932 per section + sheet), labeled `contact-sheet.jpg`,
`evidence.json`. Also checks GLB Draco/size budget and traces each reading to its dossier line.
Exit 1 if any item fails.

Phase 1–2 evidence scripts remain archived: `gate_evidence.py` and `chapter_walkthrough.py`
reference earlier copy/selectors and must not be used as current Phase 3 acceptance tests.

### Native-scroll navigation regression

Browser focus/accordion scrolling can update window.scrollY before Lenis animatedScroll catches up.
Anchor destinations now use actual document coordinates before calling Lenis. The focused test
forces native scrolling and clicks a skill in the same task to reproduce that timing gap.


## Phase 4 review and handoff

Local: `http://127.0.0.1:8767/work/crosscheck`. Or enter the homepage, scroll to CrossCheck and
choose **Open case file**. The camera approaches the instrument while the homepage fades;
the root Canvas and audio engine survive route changes. **Return to the instrument** restores
the originating scroll position. A fresh case URL returns to the CrossCheck chapter.

The case follows PLAN §7: Brief, The instrument (tap three lens markers), How it works,
Readings, Tools used, Demo video, Next instrument. Tools return to homepage Skills. The Next
instrument link returns to the SurgeLine homepage chapter; case-to-case chaining belongs to
Phase 5. No route for another case was added.

All case copy, including labels, descriptions and the qualified readings, was **approved by the owner at the Phase 4 gate** (2026-09-15); the DRAFT label is removed.
Homepage copy remains owner-approved. The instrument is the existing approved Blender export;
this phase adds camera motion and DOM markers, with leaders projected from the actual lens
nodes. A labeled still view preserves the component controls when a model/WebGL fails.

The English demo is copied unchanged from `crosscheck/assets/explainer.mp4` to
`public/videos/crosscheck-explainer.mp4` (5,002,746 bytes; H.264, 1920×1080, 126.866667 seconds,
no audio stream, verified using ffprobe). Poster: frame at 1 second, scaled to 960×540.
`preload="none"` keeps video download behind playback; native controls and a full-size link
allow viewing the burned-in captions. The original footage contains a clearly labeled replay.

### Case copy provenance — approved at the Phase 4 gate

Source: `/home/rayin/Projects/Testing/portfolio/CAPABILITY_CROSSCHECK.md`.

| Visible copy / data | Dossier source |
|---|---|
| Find the gaps. Bring back proof.; Brief problem/approach paragraphs | §1–2, DRAFT synthesis |
| Owned WordPress + CRM demo; deliberately planted bugs | §3.2, §9 |
| Browser matrix card: selected pages, engines, sizes, roles, layout/content/error checks | §3.1, §3.3 |
| Access card: intended permissions, browser recheck before reporting | §6 K5 |
| Flow card: create/search/update, saved-data checks after reload | §6 K6 |
| How it works: map → check → verify/sort → spreadsheet and screenshot gallery | §4, §6 K1 / K5 / K7 / K8 |
| 1,080 combinations; 40 × 3 × 3 × 3 | §3.1, §7 |
| 216 permission checks; 72 × 3; Chromium desktop verification qualification | §6 K5, §9 |
| 18 unique issues from 881 signals; documented suppression; clean-copy raw-count change | §6 K7–K11, §7, §9 (881 includes permissions + flow, unlike sweep-only 877) |
| 12/12 planted bugs caught; controlled target, no universal guarantee | §3.2, §6 K10, §7, §9 |
| Emulated screens; scope excludes penetration/load testing and business-rule judgment | §6 K16, §9 |
| Every CrossCheck tool listed in `lib/cases.ts` | §5 (ordinary tools, no internal harness skill names) |
| Silent English demo, recorded footage and labeled replay | §6 K13, §9 |
| Case file 01, three lenses, component labels, inspection controls, section/navigation labels | PLAN §5 / §7; DRAFT interface text, ordinal labels rather than performance claims |
| SurgeLine next instrument | PLAN §5 sequence; destination remains existing homepage chapter |

### Developer verification

```sh
npm run lint --prefix web
npm run typecheck --prefix web
npm run build --prefix web
# Start/restart the production server after the build.
timeout 300 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_case.py
timeout 420 npm run verify:mobile --prefix web
```

`verify_case.py` checks 390×844 first, then 360×740 and 430×932: persistent Canvas identity,
route/scroll/focus restoration, three component cards and projected lens endpoints, selected-marker colors settled before capture, signal flow,
animated count-up (intermediate and final values), flight fade/scroll lock, video deferred download/playback, browser Back/Forward, tools/next destinations,
direct URL/reload and deliberately blocked model fallback. Outputs: `assets/renders/case-crosscheck/dev/`.
Developer screenshots are separate from the Testing harness's future `case-crosscheck/evidence/`
pack. Testing and owner copy approval/gate remain pending. No physical-device FPS claim.

Testing evidence pack (owner gate), server running:
`timeout 600 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/case_crosscheck_evidence.py`
→ `assets/renders/case-crosscheck/evidence/` (PNG per item, MP4, contact sheet, `evidence.json`; exit 1 on any fail).

After the fallback-only spacing fix, `verify_case.py --fallback-only` writes
`fallback-verification.json` and refreshes its screenshot, checking that the fixed notice clears
the instrument heading and that cards/return still work. Normal-route results remain in `verification.json`.

## Phase 5 review and handoff

Local: `http://127.0.0.1:8767/work/<slug>` for `crosscheck`, `surgeline`, `driftwatch`, `duewatch`,
`brandwall`, or any homepage chapter → **Open case file**. One template (`components/case-file.tsx`)
renders every case from `lib/cases.ts`; `/work/[slug]` prerenders the five routes and 404s any other slug.

- **Next instrument chains case to case:** CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall →
  CrossCheck. The camera backs away from the current instrument, sweeps to the next one (the homepage
  chapter move), then the next route flies in. The same root Canvas and audio engine stay alive.
- **Return** goes back to the scroll position the case was opened from; after a chain it lands on the
  current case's homepage chapter. Direct URLs return to their own chapter.
- **Hotspots:** three per instrument, leaders projected every frame from real GLB nodes. SurgeLine points
  at dish feeds, DriftWatch at the needle pivot / paper bed / front roller, DueWatch at the orbiting
  planets (its leaders follow them), BrandWall at the collimator, prism and spectrum bands. BrandWall's
  tap-to-observe also works on its case page.
- CrossCheck's approved copy is unchanged except its Next block: it now reads **Open the next case file**
  and opens the SurgeLine case (was "Explore on the observatory floor" → homepage chapter). Approved at the Phase 5 gate.

### Demo videos (Phase 5)

Each copied byte-identical from `/home/rayin/Projects/Testing/<project>/assets/explainer.mp4`
(checked with `cmp`); H.264 1920×1080, **0 audio streams** (ffprobe). Posters are 960×540 JPEG frames.

| Public file | Bytes | Duration | Poster frame |
|---|---:|---:|---|
| `surgeline-explainer.mp4` | 1,812,889 | 115.233 s | 1 s |
| `driftwatch-explainer.mp4` | 2,227,965 | 118.167 s | 1 s |
| `duewatch-explainer.mp4` | 2,221,217 | 102.500 s | 8 s (the 1 s frame shows a browser full-screen notice) |
| `brandwall-explainer.mp4` | 10,457,918 | 124.967 s | 1 s |

**Owner accepted option 1 at the Phase 5 gate (2026-09-15):** DueWatch's video includes the caption *"Seven days in a row. Nobody had to
remember."* over simulated business dates, which its own self-review (dossier §7 finding 4) flagged.
The case keeps the note under the video and gives the real timer record in its notes, as approved.

### Case copy provenance — approved at the Phase 5 gate

Dossiers: `/home/rayin/Projects/Testing/portfolio/CAPABILITY_<NAME>.md`. Section labels, "Case file NN",
instrument headings and component labels originate as DRAFT interface text (PLAN §5 / §7), not claims.
All rows below were approved on 2026-09-15; DRAFT in a source column records drafting history.

**SurgeLine**

| Visible copy / data | Dossier source |
|---|---|
| Every row sent once. Every success proven.; Brief | §1–§2, DRAFT synthesis |
| Owned test form, synthetic records, 5% deliberate failures | §3.1–§3.2, §6 K14 |
| Work list card: one list on disk, repeated rows rejected, reload adds nothing | §4, §6 K3 |
| Parallel workers card: headless browsers, one record per worker | §6 K4 |
| Confirmation proof card: success only with a saved confirmation number; reasons kept | §6 K2, K9 |
| How it works: load → fill → retry/set aside → resume/report | §4, §6 K1 / K5 / K6 / K9 |
| 48,273 with confirmation; 49,950 unique; 1,677 = 844 validation + 833 after five attempts | §6 K2, §7 |
| 0 duplicate submissions after two forced stops, database query | §6 K1 / K3, §7 |
| 7/7 interrupted records recovered | §6 K1, §7 |
| 81,915 records/hour at 8 workers, one machine, local form | §6 K7, §7, §9 |
| Limits: 50,000 rows / 50 duplicates; no larger run; local speed; authorization, no bypass | §7, §9, §6 K13–K14 |
| Tools | §5 (runtime/build tools; no internal skill names) |
| Video note: separate 3,000-record demonstration run, labeled | §6 K12 |

**DriftWatch**

| Visible copy / data | Dossier source |
|---|---|
| Collect every day. Speak up when it changes.; Brief | §1–§2, DRAFT synthesis |
| Two sandboxes, one docs site after robots.txt check, owned planted-failure site | §3.2, §6 K6 |
| Alarms card: ten rules written before testing; normal changes quiet | §6 K1 |
| Change detection card: dated snapshots vs last successful run; volatile fields ignored | §4, §6 K3 |
| Daily collection card: 1 request/s, honest User-Agent, resume | §6 K4, K5, K7 |
| How it works: source check → schedule + watchdog → compare/judge → plain reports | §4, §6 K5–K8, K10 |
| 11/11 planted failures, 0 false alarms, 3 normal-change scenarios | §1, §6 K1, §7 |
| 1,323 records/day, 4 sources, 0 duplicates, required fields filled | §6 K9, §7 |
| 12/12 unattended runs over 3 days | §6 K5, §7, §9 (2 direct + 1 indirect journal proof) |
| 1 request where a browser needed 8 (same 10 quotes) | §6 K8, §7 |
| Limits: public sources unchanged; proof from planted site + real unplanned failure; 23-page site | §6 K2, §9 |
| Tools | §5 |
| Video note: terminal footage recorded in a disposable copy | §6 K14 |

**DueWatch**

| Visible copy / data | Dossier source |
|---|---|
| Checked every morning. Hard messages go to a person.; Brief | §1–§2, DRAFT synthesis |
| Synthetic data; every "sent" message is a local mock log | §3.2, §11 items 1–2 |
| Expiry card: recomputed daily, month/leap-year math, unclear dates flagged | §3.3, §6 K1 |
| Triage card: approved replies for simple questions; sensitive/unclear to a person, no draft | §3.4, §6 K5 |
| Follow-up card: one reminder after 24 h, replied customer skipped, re-run adds nothing | §6 K6 |
| How it works: backup → recompute → n8n sort → ledger follow-up | §4 rules 1–5, §6 K3 / K6 / K8 |
| 200 contracts per run, 45 hostile date rows | §3.1, §3.3, §8 |
| 7/7 renewals matched the manual audit on the reference date | §6 K2, §8 |
| 6/6 sensitive test messages to a person, 0 drafts | §6 K5, §8 |
| 12 reminders unchanged after six replays | §6 K6, §8 |
| Limits: self-review findings (mixed-intent auto reply, import overwrites history); 18-message baseline; 8 timer firings / 9 days; no backfill | §7 findings 1–2, §6 K4, §11 items 3–4, 10 |
| Tools | §5 |

**BrandWall**

| Visible copy / data | Dossier source |
|---|---|
| Find where brands break. Close it with one rule.; Brief | §1–§2, DRAFT synthesis |
| Owned test app, 30 generated assets, no real logos or affiliation | §3.3, §6 K16 |
| Test matrix card: 5 surfaces × 2 themes, automatic capture, control asset | §3.1–§3.3, §6 K1 |
| Measurement card: value + threshold + screenshot; pixels, WCAG 2.1 contrast, name length per script | §6 K2, K4, K5 |
| Fix rules card: seven classes, one CSS rule each, same 300 retested | §6 K3, K6, K7 |
| How it works: matrix → capture → measure/sweep → fix and prove | §4, §6 K1 / K5 / K7 / K9 |
| 300 screenshots per run, five runs, 0 failed cells | §3.1, §6 K1, §7 |
| 18 findings left from 186, 0 new; 404 file + 0%-ink asset rejected at the asset gate | §6 K7, §7 |
| 11 breakpoints from 716 observations | §6 K5, §7 |
| 0/300 false changes between identical runs; one-asset swap flagged | §6 K8, §7 |
| Limits: desktop sizes in Chromium; English run 182 vs 186 kept separate | §9, §6 K15 |
| Tools | §5 |
| Video note: filmed on the English evidence run | §6 K15 |

### Phase 5 developer verification

```sh
npm run lint --prefix web && npm run typecheck --prefix web && npm run build --prefix web
# restart the production server after the build, then from web/scripts:
cd web/scripts && timeout 900 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python verify_cases.py
cd ../.. && timeout 300 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_case.py
timeout 420 npm run verify:mobile --prefix web
```

`verify_cases.py` (390×844, then 360×740 and 430×932): every chapter opens its own case and Return restores
scroll + focus; the full Next chain with wrap to CrossCheck; per case the heading, DRAFT label state, three
hotspot cards, projected leader endpoints, four count-ups, limits, lazy video duration and next name; Back/Forward
inside the chain; Return after a chain lands on that chapter; five direct URLs; `/work/unknown` → 404;
blocked model → DueWatch still view. Multi-digit readings must appear verbatim in their dossier.
Output: `assets/renders/case-files/dev/`. Not the Testing-stage gate pack.

## Phase 7D — DueWatch time control room (gate passed, 2026-09-18)

Personal brief, isolation and integration rules: `../assets/development/phase-7d/HANDOFF.md`.
The site demonstrates two independent routines. It does not run the underlying DueWatch service,
classify visitor text, send messages or store reminders outside local component state.

| New copy / visible data | Source in `portfolio/CAPABILITY_DUEWATCH.md` |
|---|---|
| Chapter, deck, brief, three component cards | §1–4, §7; DRAFT synthesis with audit limits |
| Active >60; due soon 8–60; renewal 0–7; expired <0; bad data | §3.1; English translations of locked statuses |
| 61/60/8/7/0/−1 day controls and example indicator | Illustrative boundary inputs, not run totals; policy from §3.1 |
| Six category buttons, human handoff, no draft | §3.4, §6 K5; intended policy, explicitly not a classifier |
| Mixed-intent and optional draft-filter weaknesses | §7 finding 2; adjacent to handoff illustration |
| Exact 24h pending; >24h eligible; replied skipped | §6 K6; isolated eligible email example, not WhatsApp sending policy |
| Example ledger 0→1, repeated checks stay 1 | Illustrative state, distinct from recorded run; §6 K6; no re-import/concurrency claim |
| 200 contracts; 45 hostile rows; 7/7 reference renewals | §3.1–3.3, §6 K2, §8 (4 September 2026 reference date) |
| 18 fixtures, 6/6 sensitive, 0 external API calls | §6 K5/K8, §8; local mock log, not production accuracy |
| 12 reminders after six sequential checks | §6 K6, §7 finding 1; saved ledger only |
| 8 timer firings / 9 real days, 5–13 September; no backfill | §6 K4, §8, §11 item 10 |
| Seven audit findings (four High / three Medium); A9/A10 open | §7, §8, §11; dossier snapshot, not fresh audit |
| Video simulated business-date disclosure | §7 finding 4, owner decision Q35 retained |
| BrandWall Next teaser | PLAN §5.5; DRAFT connective copy |

No change to existing model geometry or Blender assets. Existing orrery anchors remain in use.
Mobile is verified before desktop composition. Scope-specific tests live in `verify_duewatch_room.py`
(reusable `viewport` and `edges`), `verify_duewatch_state.mjs`, and DueWatch segments in `perf_quick.py`.

### Integration and verification exception — 2026-09-17

The owner requested integration after 7C stabilized, with no repeated tests in this session.
All 7C copy approvals and its trace-motion fix were preserved. Integration metadata and pre-merge
backups: `../assets/development/phase-7d/INTEGRATION.json` and `integration-before/`.

Before integration, lint/typecheck/build, all six viewport journeys and the DueWatch GPU fps gate passed
on the isolated copy. Full regressions did not finish. The isolated `time` suite last failed on the
expected blocked-model error; that assertion was corrected but not rerun. The SurgeLine fps gate failed
its slow-frame limit (chapter 18.9%, case scroll 21.6%; allowed 10%) and was not attributed with a baseline.
These remain explicit Testing follow-ups. Source integration was inspected; the merged build was not tested
or rebuilt at the owner’s request. Existing :8767 preview still serves the previous build; :8784 serves
the isolated DueWatch preview. Copy 7D remains DRAFT; no 7D gate is claimed.

### Testing — 2026-09-17 (Claude Code) → awaiting gate

The integrated build was rebuilt and tested on :8767. Lint, typecheck and build exit 0; `run_regressions.py` passed all
16 suites on source `f19aac05262f34b3`. The `time` suite now passes six viewports and its edges; `perf-surgeline` measured
57.0–60.0 fps with at most 3.0% slow frames, so the earlier isolated-copy failure did not reproduce. One stale test was fixed
(`verify_cases.py` expected the old DueWatch hotspot title). No application code changed.
Evidence pack `assets/renders/personal-duewatch/evidence/` (`duewatch_room_evidence.py`): 22/22 items, mobile and desktop walkthroughs,
0.25x slow motion, contact sheets, `evidence.json`. Motion contract measured: chapter pointer equals orbit; ring .65/−28° → flat rail
(~830 ms visible); hand turns monotonically and settles at about 550–620 ms, result card about 150 ms; handoff signal 0→24 px about 250 ms;
keyboard and reduced motion are final at once.

Gate 2026-09-18 ("semuanya approved"): all new 7D copy approved and DRAFT labels removed (the chapter strip now reads
"Illustration"). Accepted as they are: the faint hairline ring → rail and the unlabelled dial ticks.
