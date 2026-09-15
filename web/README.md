# Rayin Observatory · Desktop

Phase 6 Development: full-width homepage and five case files for laptop and monitor screens.
Phase 0–5 gates passed. All homepage and case copy is **owner-approved**; Phase 6 changes layout only.
The owner accepted the DueWatch video with its existing simulated-date note at the Phase 5 gate.
Testing (Claude Code / Antigravity) follows developer verification and produces the gate evidence pack.

## Phase 6 review and handoff

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
The phase stays open until the owner reviews that pack and grants the gate.

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
