# Rayin Observatory · Full observatory

Phase 3 Development: five mobile instrument chapters, project-linked skills, About and Contact.
Phase 0–3 gates passed (Phase 3 on 2026-09-15). All homepage copy is **owner-approved**; DRAFT labels removed.
The owner clarified the job focus as **Automation Engineer** on 2026-09-15.
Testing (Claude Code / Antigravity) follows developer verification and produces the gate evidence pack.

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
Open case file opens a project-specific **preview dialog**. Full routes remain Phase 4–5.

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
| The crash-recovery demo uses synthetic records and an owned form with server-side duplicate protection. | SurgeLine §3.2 and §9; DRAFT preview context |
| 03 / Data monitoring; DriftWatch | DriftWatch meta category, PLAN §5 order |
| I collect your web data on a schedule and flag source changes before silent failures spoil your reports. | DriftWatch §1, §3.1; DRAFT condensation |
| 11/11 planted failures caught · In a controlled failure test | DriftWatch meta Proven scale, §1, §3.1 local drift lab; controlled recall, not a universal detection guarantee |
| The detection reading comes from deliberately planted failures in an owned test site. | DriftWatch §3.1 / §3.2; DRAFT preview context |
| 04 / Expiry & follow-up; DueWatch | DueWatch meta category, PLAN §5 order |
| I build daily expiry checks and follow-up workflows that hand sensitive messages to a person. | DueWatch §1, §3.1 / §3.2 / §3.4; DRAFT, no live message delivery claim |
| 200 contracts checked per run · Synthetic contracts · mock delivery | DueWatch meta Proven scale, §3.1 master rows / §3.2 delivery |
| The demo uses synthetic contracts and mock message delivery. Live sending is not demonstrated. | DueWatch §3.1 / §3.2; DRAFT preview context |
| 05 / Visual design QA; BrandWall | BrandWall meta category, PLAN §5 order |
| I test brand assets across your product surfaces and themes, then report where layouts break and which CSS rules fix them. | BrandWall §1 / §2; DRAFT condensation |
| 300 screenshots per run · Generated brands · owned test app | BrandWall meta Proven scale, §3.1 / §3.3; generated assets, no brand affiliation |
| The screenshots use generated brand assets on an owned test app, with no claimed brand affiliation. | BrandWall §3.3 / §9; DRAFT preview context |
| I build tools that check web apps, move spreadsheet rows through forms, and keep watch over changing data. | About DRAFT: CrossCheck / SurgeLine / DriftWatch §1 |
| I test what happens when things go wrong, then turn the results into clear reports. The work here uses owned test apps, synthetic data and documented sources, with limits stated alongside the proof. | About DRAFT: CrossCheck §3 / §6, SurgeLine §3 / §6, DriftWatch §3.2, DueWatch §3 / §7, BrandWall §3 |
| What needs a closer look?; Tell me what you need to test, automate or monitor. | Contact DRAFT synthesis of the same project categories; no availability or commercial promise |
| Skills, with proof.; Choose a project beside each skill to explore the work behind it. | DRAFT interface copy; links are mapped in `lib/skills.ts` |
| The toolkit; Behind the instruments; Start a conversation; Email me | DRAFT labels, PLAN §4 / §6 / §9 |
| Daily work (Skills group) | PLAN §9 "Kerja harian"; owner confirmation 2026-09-15 |
| rayinailham9@gmail.com; LinkedIn / GitHub / Upwork links labeled "Rayina Ilham" | Owner-supplied destinations, chat 2026-09-15 |
| Open case file; Case file preview; The full case file is coming soon.; Return to the instrument; Scroll to orbit the instrument; menu/readout/error text; Back to the dome | DRAFT interface copy, PLAN §6; case routes deferred to Phase 4–5 |
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
- Mobile width stays capped at 430px. Desktop Phase 6, polish/performance Phase 7,
  launch Phase 8 and full accessibility Phase 9 remain outside this development scope.

## Verification

```sh
npm run lint --prefix web
npm run typecheck --prefix web
npm run build --prefix web
timeout 420 npm run verify:mobile --prefix web
```

The existing CrossCheck Playwright Python environment runs Chromium at 390×844 first, then
360×740 and 430×932. Checks: entry, audio on/off/memory, one Canvas, all five sticky chapters,
visible idle/orbit pixel differences, readings, per-project dialogs, paused scroll/focus return,
reverse navigation, every skill href, real skill navigation to all projects, portrait, contact
placeholder, readout, 390px touch swipe, and a deliberately blocked new model → five still views.
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
