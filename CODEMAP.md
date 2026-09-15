# CODEMAP — Peta kode Rayin Observatory

> **Tujuan:** baca peta ini, bukan pindai seluruh kode. Buka berkas kode hanya jika peta
> menunjuknya dan berkas akan diubah. Update setiap berkas dibuat/diubah/dipindah/dihapus.
> Entri tidak cocok dengan kode = bug; perbaiki saat ditemukan.

**Terakhir diperbarui:** 2026-09-15 · Claude Code · revisi langit + animasi instrumen pasca Fase 3 (menunggu review pemilik). Fase 4 berikutnya.

## 1. Ringkasan arsitektur

Fase 0 sudah `done` (gate pemilik 2026-09-14); palet/font/foto/kubah FINAL di PLAN §8.
Fase 1 sudah `done` (gate pemilik 2026-09-15).
Fase 1 menambahkan aplikasi Next.js App Router + TypeScript di `web/`: satu Canvas root,
GLB kubah/planet dari Blender, gate loading, audio Web Audio, Lenis + GSAP ScrollTrigger.
Halaman `/` di-prerender statis; state interaktif hanya di client shell/scene. Copy homepage approved (gate Fase 3).

`app/layout.tsx` → `ObservatoryShell` → `ObservatoryScene` (client dynamic) + `app/page.tsx`.
Scene hidup sepanjang layout; scroll disimpan di ref, dibaca `useFrame`, bukan state React.
Font, decoder Draco, fallback PNG dan model disajikan lokal dari `web/public/`.

Fase 2 menambah section `#crosscheck` (sticky, 270svh) setelah hero: ScrollTrigger `reveal`
(masuk) + `orbit` (di-pin) ditulis ke ref `chapter`, dibaca `useFrame` untuk kamera orbit
di sekitar teleskop `crosscheck.glb`; idle = ayun `OpticsPivot` + nyala `Lens1..3Glow` bergiliran.
"Open case file" membuka dialog preview sementara (case file asli Fase 4).

Fase 3: `lib/instruments.ts` menjadi sumber lima chapter/copy/dialog; `lib/skills.ts` memetakan
skill ke project. Shell menghitung chapter aktif, orbit, transisi dan outro dari posisi section
nyata. Scene memuat tujuh GLB dalam satu Canvas; lima group instrumen berbagi kamera. Skills
memakai disclosure native; setiap tautan mengembalikan scroll/fokus ke project dan menyorot judul.
About: portrait approved + GSAP clip/scan. Contact: CTA `mailto:` + empat link asli dari pemilik.
Hero menegaskan Automation Engineer sesuai arahan pemilik sesi ini.

Preview pada port 8767. Preview Fase 0 tetap arsip HTML `assets/style-lock/` pada 8766.
Fase 3 menambahkan empat instrumen, Skills, About dan Contact. Case file dan desktop tetap fase berikutnya.

## 2. Perintah

Semua dari root project kecuali disebut lain.

| Perintah | Fungsi |
|---|---|
| `npm ci --prefix web` | Instal versi terkunci dari package-lock. |
| `npm run build --prefix web` | Build produksi + TypeScript + prerender statis. |
| `npm run start --prefix web` | Preview produksi `0.0.0.0:8767`. |
| `npm run dev --prefix web` | Dev server port 8767; gunakan saat produksi tidak berjalan. |
| `npm run lint --prefix web` / `npm run typecheck --prefix web` | ESLint / TypeScript terpisah. |
| `timeout 420 npm run verify:mobile --prefix web` | Tes Development Fase 3: entry + lima chapter + skills/about/contact; 390×844 → 360×740 → 430×932. JSON/PNG ke `assets/renders/full-observatory/dev/`; server :8767 aktif. |
| `timeout 600 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/full_observatory_evidence.py` | Arsip bukti gate Fase 3 (lolos) → `assets/renders/full-observatory/evidence/`; cek copy lama mengharapkan label DRAFT. |
| `timeout 400 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/revision_evidence.py` | Bukti revisi langit + animasi → `assets/renders/revision-sky-motion/evidence/`: MP4 390×844, PNG per item, contact sheet, `evidence.json`; server :8767 aktif. |
| `OBSERVATORY_URL=<url> timeout 200 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/chapter_walkthrough.py` | Bukti gate Fase 2: MP4 390×844 + 6 PNG ke `assets/renders/crosscheck/walkthrough/`. |
| Blender MCP: jalankan `assets/blender/build_full_observatory.py` dengan `__file__` dan `__name__='__main__'` | Buat empat scene baru, checkpoint, convert/join, ekspor Draco; menolak overwrite `<slug>-web.blend`. Render tiap scene terpisah lewat MCP. |
| Blender MCP: jalankan `assets/blender/export_crosscheck.py` dengan `__file__` dan `__name__='__main__'` | Salin scene teleskop, checkpoint, gabung mount/optik, ekspor Draco `crosscheck.glb`. Menolak overwrite `crosscheck-web.blend`. |
| `OBSERVATORY_URL=<url> timeout 540 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/gate_evidence.py` | Bukti gate Fase 1: 3 engine × 390×844, PNG per item checklist + MP4 + contact sheet + 4G lambat; exit 1 bila ada item fail. Default URL lokal :8767. |
| `docker logs rayin-observatory-preview-tunnel` | URL publik sementara; setup/stop di `web/README.md`. |
| Blender MCP: jalankan `assets/blender/export_first_light.py` dengan `__file__` dan `__name__='__main__'` | Salin scene kubah, checkpoint, ekspor Draco + planet. Menolak overwrite first-light.blend. |
| `python -m http.server 8766 --bind 0.0.0.0 --directory assets` | Preview; buka `/style-lock/`. Hentikan Ctrl+C. |
| `timeout 60 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python assets/style-lock/verify_mobile.py` | Cek Chromium HP 390×844; tulis JSON + screenshot. Server harus aktif. |
| `timeout 240 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python assets/style-lock/gate_audit.py` | Audit gate 3 engine × 3 viewport HP + kontras WCAG; exit 1 bila gagal. Server harus aktif. |
| `timeout 60 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python /home/rayin/Projects/Testing/crosscheck/scripts/verify_engines.py` | Smoke launch tiga engine; lingkungan CrossCheck tidak diubah. |
| Blender MCP: jalankan `assets/blender/build_style.py` dengan `__file__` diset dan `__name__='__main__'` | Bangun scene baru, simpan `.blend`; menolak overwrite hasil yang sudah ada. Gunakan tujuan versi baru untuk rebuild. |
| Blender MCP: `bpy.ops.render.render(write_still=True)` | Render scene review aktif ke path yang tersimpan. |

Preview Fase 1: `http://127.0.0.1:8767/`.
Arsip tautan HP Fase 1–2: `https://geological-ones-medline-loans.trycloudflare.com/`.
Sesi Fase 3: server lokal :8767 aktif; tunnel tidak dinyalakan (bukti direkam lokal, sesuai PLAN §12).
Buat tunnel baru mengikuti README bila pemilik minta link HP.
URL berganti ketika tunnel restart; kedua proses harus hidup. LAN: port 8767, IP mengikuti
mesin; ufw pernah memblokir akses HP. Tidak ada perubahan firewall/domain/DNS.
Preview arsip Fase 0: `http://127.0.0.1:8766/style-lock/` bila server Python dinyalakan.

## 3. Pohon berkas

```text
Rayin Observatory/
├── PLAN.md                         rencana terkunci; §3 Q32 ditambah 2026-09-15 (gate Fase 3)
├── PROMPT.md                       prompt sesi; tidak diubah
├── PROGRESS.md                     status fase + checklist + log
├── CODEMAP.md                      peta ini
├── web/
│   ├── package.json               npm commands + pinned dependencies
│   ├── package-lock.json          generated npm dependency graph
│   ├── tsconfig.json              strict TypeScript / alias @/*
│   ├── next.config.ts             React strict / three transpilation
│   ├── eslint.config.mjs          Next core-web-vitals + TypeScript
│   ├── .gitignore                 excludes generated output / local env
│   ├── README.md                  run, gate, provenance, scope, verification
│   ├── app/
│   │   ├── layout.tsx             root persistent shell, fonts CSS, metadata
│   │   ├── page.tsx               hero + five chapters + Skills/About/Contact, approved copy
│   │   └── globals.css            locked tokens, mobile composition, gates/dialogs
│   ├── components/
│   │   ├── observatory-shell.tsx  entry/loading/audio/menu/scroll ownership
│   │   ├── observatory-scene.tsx  one Canvas, dome/Saturn + five instrument groups
│   │   ├── instrument-motion.ts   per-instrument idle rigs + Saturn rig (moons, ring dust)
│   │   └── sky.tsx                full-screen sky shader: gradient, stars, nebula
│   ├── lib/ambient.ts             original oscillator hum / fade / lifecycle
│   ├── lib/instruments.ts         ordered chapter copy, readings, dialog context + types
│   ├── lib/skills.ts              grouped skills and evidence-project IDs
│   ├── scripts/verify_mobile.py   focused browser interaction checks
│   ├── scripts/full_observatory_evidence.py  arsip bukti gate Fase 3
│   ├── scripts/gate_evidence.py   gate evidence Fase 1: 3 engines, screenshots, videos, slow 4G
│   ├── scripts/chapter_walkthrough.py  gate evidence Fase 2: video + 6 frames 390×844
│   ├── scripts/revision_evidence.py  bukti revisi langit/animasi: MP4 + PNG + contact sheet
│   └── public/
│       ├── models/                dome/ambient + five instrument GLBs, Draco
│       ├── fonts/                 approved 3 TTF + 3 OFL copies
│       ├── images/                dome + five fallback PNGs; approved portrait copy
│       └── draco/                 WASM decoder + wrapper + README.md + LICENSE.txt
└── assets/
    ├── blender/
    │   ├── build_full_observatory.py  Phase 3 generator (four instruments)
    │   ├── surgeline-web.blend[1]     array source + checkpoint
    │   ├── driftwatch-web.blend[1]    seismograph + roller refinement checkpoint
    │   ├── duewatch-web.blend[1]      orrery source + checkpoint
    │   ├── brandwall-web.blend[1]     spectrograph source + checkpoint
    │   ├── export_crosscheck.py   Phase 2 telescope export via GUI MCP
    │   ├── crosscheck-web.blend    telescope web-export scene (joined, OpticsPivot)
    │   ├── crosscheck-web.blend1   pre-conversion checkpoint
    │   ├── export_first_light.py  Phase 1 export via GUI MCP
    │   ├── first-light.blend       dome export scene + ambient planet scene
    │   ├── first-light.blend1      pre-conversion checkpoint
    │   ├── build_style.py          sumber prosedural via Blender MCP
    │   ├── dome.blend              kubah, scene aktif Dome / night review
    │   ├── crosscheck.blend        teleskop, scene aktif CrossCheck / three optics
    │   └── crosscheck.blend1       backup otomatis sebelum revisi kamera/material
    ├── photo/
    │   ├── rayina-crop.png         crop + edit latar tanpa logo
    │   └── rayina-duotone.png      treatment navy + scan
    ├── renders/
    │   ├── revision-sky-motion/    evidence/ revisi langit + animasi instrumen (2026-09-15)
    │   ├── full-observatory/       four Blender reviews + dev/ PNG/JSON/env-check + evidence/ (Testing)
    │   ├── crosscheck/             Phase 2 review render, verify_mobile PNG/JSON, walkthrough/
    │   ├── first-light/            arsip Phase 1: render, screenshots, evidence JSON, env-check.md
    │   ├── dome-night.png          render kubah 1000×1000 RGBA
    │   ├── crosscheck-night.png    render teleskop 1000×1000 RGBA
    │   ├── mobile-390x844.png      screenshot layar pertama
    │   ├── style-review-mobile.png screenshot halaman review penuh, lebar 390
    │   └── gate-audit/             output gate_audit.py: 9 layar + 3 penuh PNG, gate-audit.json
    └── style-lock/
        ├── index.html             contoh layar HP + bahan gate
        ├── README.md              cara review, sumber copy, alur Blender, batas verifikasi
        ├── env-check.md           bukti launch tiga engine
        ├── provenance.json        prompt foto + sumber font
        ├── verify_mobile.py       verifikasi fokus HP
        ├── gate_audit.py          audit gate lintas engine/viewport + kontras
        ├── verification.json      hasil verifikasi terakhir, termasuk teks halaman
        └── fonts/
            ├── fraunces.ttf
            ├── inter.ttf
            ├── jetbrains-mono.ttf
            ├── fraunces-LICENSE.txt
            ├── inter-LICENSE.txt
            └── jetbrains-mono-LICENSE.txt
```

## 4. Modul dan berkas

### `web/app/layout.tsx`
- **Peran:** root layout App Router; mempertahankan shell/Canvas di luar halaman.
- **Ekspor utama:** `RootLayout`, `metadata`, `viewport`.
- **Dipakai oleh:** Next.js untuk semua route.
- **Bergantung pada:** `ObservatoryShell`, `globals.css`, CSS Lenis.
- **State / efek samping:** tidak ada server state; metadata preview noindex, English `lang`.
- **Catatan:** title memakai Rayina Ilham / Rayin Observatory; meta launch lengkap Fase 8.

### `web/app/page.tsx`
- **Peran:** homepage statis: hero, lima section sticky, Skills, About, Contact.
- **Ekspor utama:** `Home`; anchors `#first-light`, lima project ID, `#skills`, `#about`, `#contact`;
  `[data-open-case]`, `[data-skill-project]`, `[data-scroll-target]` untuk delegasi shell.
- **Dipakai oleh:** route `/`, ScrollTrigger/ResizeObserver shell, scene chapter mapping.
- **Bergantung pada:** `lib/instruments.ts`, `lib/skills.ts`, Next Image, globals.css, portrait lokal.
- **State / efek samping:** tidak ada React state; disclosure native mengubah tinggi dokumen.
- **Catatan:** English, Automation Engineer sesuai arahan pemilik; copy approved di gate Fase 3 (tanpa label DRAFT). `EMAIL` +
  `contactLinks` = tujuan asli dari pemilik; label link "Rayina Ilham" (bukan handle). Eksternal
  `target=_blank rel=noopener noreferrer`. Skill `projects` kosong → tanpa div link. Case routes Fase 4–5.
  BrandWall: `orbit-hint` diganti `#observer-readout[data-observed]` (label DRAFT revisi 2026-09-15).

### `web/app/globals.css`
- **Peran:** token FINAL §8, font lokal, komposisi HP, lima chapter, gate/menu/dialog, Skills/About/Contact.
- **Ekspor utama:** variables `--journey`, `--hero-journey`, `--chapter-reveal`, `--copy-opacity`,
  `--instrument-0-offset` … `--instrument-4-offset`; `.instrument-*`, `.skill-*`, `.portrait-scan`,
  `.scan-line`, `.text-section`, `.contact-links`, `.email-cta`.
- **Dipakai oleh:** layout, page, shell.
- **Bergantung pada:** tiga TTF, fallback PNG lokal (image paths disuplai shell), portrait.
- **State / efek samping:** transform/opacity, highlight skill target, sticky stages, fixed readout.
  `data-chapter` selain dome menyembunyikan CTA hero; outro mempertahankan notice still view.
- **Catatan:** >430px tetap batas komposisi HP; desktop Fase 6. Accordion native tetap keyboard-usable.
  `.fallback-notice` `margin:0` (default `<p>` 9px dulu menimpa copy chapter); di chapter `top:82px`.
  `.email-cta` sekarang `<a>`; `.contact-links a` baris 58px, nilai mono amber.
  Revisi langit: `.scene-layer` gradient (fallback bila WebGL gagal), overlay tinggal fade bawah ke ink;
  header gradient hitam transparan; gate gradient + bintang CSS `::before`; `#observer-readout` `.when-on/.when-off`.

### `web/components/observatory-shell.tsx`
- **Peran:** client shell persisten: loading, entry/audio, menu/dialog, scroll dan chapter state.
- **Ekspor utama:** `ObservatoryShell`; `scrollFromMenu`, `returnToDome`, `goToWork`, `openContact`;
  `measure`/`syncChapters` di efek GSAP; `selectedCase` untuk preview yang benar.
- **Dipakai oleh:** root layout.
- **Bergantung pada:** Scene dynamic, instruments, drei useProgress, GSAP/ScrollTrigger, Lenis, audio.
- **State / efek samping:** satu ticker Lenis; main trigger menulis readout dan chapter ref
  (`index`, `transition`, `reveal`, `orbit`, `outro`) dari bounds section. Hero trigger terpisah;
  dua trigger portrait untuk clip + scan-line. ResizeObserver main merefresh bounds saat accordion
  berubah. Dialog menghentikan Lenis; menu scroll memulai Lenis sebelum scrollTo, fokus heading
  saat selesai. Skill links menambah `.skill-highlight`; case CTA memilih project via data attribute.
- **Catatan:** Enter menunggu tujuh model + font settle; error → lima still view berlabel.
  Contact sekarang section, bukan dialog placeholder Fase 1–2. Cleanup trigger/ticker/observer/audio.
  Lenis start() dapat membatalkan scrollTo bila dipanggil setelah scroll dimulai; urutan dipertahankan.

### `web/components/observatory-scene.tsx`
- **Peran:** satu Canvas R3F, tujuh GLB, kamera orbit + transisi masuk/keluar lima group instrumen.
- **Ekspor utama:** `ObservatoryScene`, `World`, `SceneBoundary`; props memakai `ChapterState`.
- **Dipakai oleh:** shell dynamic (SSR off).
- **Bergantung pada:** R3F/drei/three, instruments.ts, tujuh GLB, decoder lokal. Node kontrak:
  `OpticsPivot`, `Lens1Glow..Lens3Glow`; `DishPivot0..3`; `NeedlePivot`, `PaperFeed`,
  `RollerPivot0..1`; `OrbitPivot0..2`; `PrismPivot`, `SpectrumPivot`.
- **State / efek samping:** clone material + disposal; useFrame membaca ref, tidak state React scroll.
  Aktif dan pendahulunya terlihat saat transisi; kamera interpolasi orbit. Idle per instrumen di
  `instrument-motion.ts` (`rig.update` hanya saat group terlihat). Klik di chapter BrandWall (bukan
  tombol/link/dialog) → `rig.observe()`; status detektor → `#observer-readout[data-observed]`.
  `pointScale` = DPR tiap frame. Satu environment lokal, DPR 1–1.5.
- **Catatan:** langit = `<Sky>` (titik bintang lama dihapus); Saturnus (`saturn()` rig) tetap ditambat ke kamera, wobble + skala .072. Kubah approved tetap utuh.
  SceneBoundary gagal satu model → still view menyeluruh; semua chapter tetap dapat dibaca.

### `web/components/sky.tsx`
- **Peran:** mesh layar penuh (renderOrder -10, tanpa depth) dengan shader langit: zenith hitam → ink → horizon biru,
  bintang prosedural 3 lapis (kelip, warna, parallax), jalur nebula tipis, dither.
- **Ekspor utama:** default `Sky({ progress })`.
- **Dipakai oleh:** `World` di scene.
- **State / efek samping:** uniform `uOffset` dari sudut kamera + progres hero + tinggi kamera; resolusi/DPR tiap frame.
- **Catatan:** dekorasi, bukan data astronomi. Warna shader ditulis langsung sebagai sRGB (tanpa colorspace chunk).

### `web/components/instrument-motion.ts`
- **Peran:** rig gerak idle per instrumen + Saturnus; objek tambahan dibuat runtime (tanpa ubah GLB/Blender).
- **Ekspor utama:** `rigInstrument(id, view, materials, onObserve)`, `saturn(source)`, `pointScale`, tipe `Rig`.
- **Dipakai oleh:** `observatory-scene.tsx`.
- **Bergantung pada:** node/material kontrak GLB (lihat scene) + nama material `surgeline signal`, `driftwatch alarm`,
  `duewatch signal/alarm/brass`, `Spectrum0..3`, `Amber light`, `First light / planet mineral`, `dusty rings`.
- **State / efek samping:** CrossCheck siklus 6.6 dtk (lensa 1→2→3, lalu ketiganya hijau). SurgeLine: parameter
  yaw/pitch/periode per piringan + 2 cincin pulsa additive per piringan. DriftWatch: `PaperFeed` lama disembunyikan,
  ribbon trace 150 titik dari `reading(t)` (sumbu waktu = z kertas), tick kertas bergerak, burst merah tiap 5.2 dtk.
  DueWatch: geometri planet di-clone lalu didudukkan ke bidang cincin; `rotation.y` planet = kecepatan Kepler
  `1.1·(0.65/r)^1.5`, cincin presesi pelan; planet merah berkedip di tanda "due". BrandWall: 64 foton/dtk
  collimator → prisma → layar; detektor off = pola interferensi cos², on (siklus 13 dtk atau tap 5 dtk) = dua pita.
  Saturnus: clone scene + shader onBeforeCompile (pita, badai, celah Cassini), 520 debu cincin (Kepler), dua bulan.
- **Catatan:** semua geometri/material buatan rig di-dispose lewat `rig.dispose()`; `frustumCulled=false` untuk objek dinamis.

### `web/lib/ambient.ts`
- **Peran:** hum observatorium sintetis original tanpa sample eksternal.
- **Ekspor utama:** `ObservatoryAudio.setEnabled`, `visibilityChanged`, `dispose`.
- **Dipakai oleh:** shell; AudioContext dibuat hanya dari gesture Enter/toggle.
- **Bergantung pada:** Web Audio API, document visibility.
- **State / efek samping:** oscillator/gain, resume/fade, mute tab tersembunyi, close pada cleanup;
  request generation menjaga hasil resume lama tidak membalik intent terbaru.
- **Catatan:** kualitas/volume pada speaker HP fisik tetap bahan gate pemilik.

### `web/scripts/verify_mobile.py`
- **Peran:** verifikasi Development Fase 3 dan regresi entry, Chromium 390×844 → 360×740 → 430×932.
- **Ekspor utama:** `run`, `position`, `menu_to`, `enter`, `difference`; `OBSERVATORY_URL` override.
- **Dipakai oleh:** `npm run verify:mobile`; CrossCheck venv Python Playwright + Pillow.
- **Bergantung pada:** server :8767, selector page/shell, Chromium ANGLE gl-egl.
- **State / efek samping:** PNG + `verification.json` ke `assets/renders/full-observatory/dev/`;
  timestamp/status running/passed/failed; error navigasi menyimpan detail + screenshot.
- **Catatan:** audio/entry/mute, satu Canvas, lima sticky/idle/orbit/readings/dialog, fokus/scroll lock,
  reverse navigation, semua skill href dan lima klik project, scan clip berbeda, About, Contact
  (`CONTACTS` href persis, tap ≥44, noopener), readout 100%, touch swipe 390px, block BrandWall →
  lima fallback + notice tidak menimpa copy (`fallback-verification.json`); nol `.draft-label`; grup "Daily work" = 3 item tanpa link.
  Bukan tahap Testing atau klaim FPS/4G HP fisik.

### `web/scripts/full_observatory_evidence.py`
- **Peran:** arsip bukti gate Fase 3 (lolos 2026-09-15); cek `copy` masih mengharapkan 9 label DRAFT, jadi gagal bila dijalankan ulang sekarang.
- **Ekspor utama:** async `run()`, `main_flow`, `viewports`, `fallback`; `check_assets`, `check_numbers`,
  `contact_sheet`, `renders_sheet`; `ITEMS` (16 item), `READINGS`, `CONTACTS`, `FORBIDDEN`, `OBSERVATORY_URL`.
- **Dipakai oleh:** agen Testing; venv CrossCheck (Playwright + Pillow) + ffmpeg.
- **Bergantung pada:** server :8767; selector page/shell; dossier `/home/rayin/Projects/Testing/portfolio/`;
  render review `assets/renders/full-observatory/<slug>-review.png`; font JetBrains Mono lokal.
- **State / efek samping:** hapus lalu tulis ulang `assets/renders/full-observatory/evidence/`.
- **Catatan:** Chromium GPU ANGLE, DPR 2, wheel nyata supaya video memperlihatkan Lenis. Cek nama
  terlarang "Rayin Ailham" sebagai frasa (handle `rayinailham` di URL/email sah). Bukan klaim fps HP.

### `web/scripts/chapter_walkthrough.py`
- **Peran:** arsip bukti visual gate Fase 2; selector lama, bukan tes Fase 3 (bukan tes pass/fail).
- **Ekspor utama:** async `run()`, `scroll()`; `OBSERVATORY_URL`, `SIZE`, `GPU`.
- **Dipakai oleh:** agen saat menyiapkan bahan gate; venv CrossCheck + ffmpeg.
- **Bergantung pada:** preview (lokal/tunnel); label tombol sama dengan page/shell.
- **State / efek samping:** hapus lalu tulis ulang `assets/renders/crosscheck/walkthrough/`
  (`01-gate` … `06-orbit-end` PNG DPR 2, `crosscheck-walkthrough.mp4` H.264).
- **Catatan:** Chromium silent entry; `scroll()` me-wheel sampai `scrollY` target lalu menunggu diam
  (Lenis menyerap sebagian delta saat fps rekam rendah). Video Playwright fps rendah = bukti alur, bukan kehalusan.

### `web/scripts/gate_evidence.py`
- **Peran:** arsip bukti gate Fase 1 per checklist; selector/copy lama, bukan tes Fase 3.
- **Ekspor utama:** async `run()`, `flow()` per engine, `slow_load()`; `ITEMS`, `CHROMIUM_GPU`, `SLOW_4G`, `OBSERVATORY_URL` override.
- **Dipakai oleh:** agen saat menyiapkan bukti gate; Python Playwright venv CrossCheck + ffmpeg.
- **Bergantung pada:** preview produksi (lokal atau tunnel); selector/label sama dengan `verify_mobile.py`.
- **State / efek samping:** hapus lalu tulis ulang `assets/renders/first-light/gate-evidence/<engine>/`
  (PNG DPR 2, MP4 H.264, contact-sheet) dan `gate-evidence.json`; browser sementara.
- **Catatan:** Chromium diluncurkan dengan GPU (ANGLE gl-egl); default SwiftShader membuat input
  dan video ≈1 fps. Scroll: Chromium swipe CDP, WebKit `scrollBy`, Firefox wheel. Sound `n/a` bila
  AudioContext polos pun gagal (headless WebKit: tanpa perangkat audio) — bukan fail. Video
  Playwright ≈6–11 fps: bukti alur, bukan bukti kehalusan/fps HP fisik.

### `web/package.json`, `web/package-lock.json`
- **Peran:** owning package tunggal; npm scripts dan dependensi versi terkunci.
- **Ekspor utama:** dev/build/start/typecheck/lint/verify:mobile.
- **Dipakai oleh:** npm dan Next.js; Node 24 pada sesi ini.
- **Bergantung pada:** Next 16.3.5, React 19.2.8, R3F 9.7.0, drei 10.7.8, three 0.186.0,
  GSAP 3.15.0, Lenis 1.3.26; versi dev dependencies tercantum di manifest.
- **State / efek samping:** install menghasilkan node_modules; lock dibuat npm, tidak diedit manual.
- **Catatan:** tidak ada workspace monorepo / shared package baru.

### `web/tsconfig.json`, `web/next.config.ts`, `web/eslint.config.mjs`, `web/.gitignore`
- **Peran:** konfigurasi TypeScript strict, build/runtime Next, lint dan artefak lokal.
- **Ekspor utama:** alias `@/*`; transpile three; React strict; Next core-web-vitals/TypeScript.
- **Dipakai oleh:** npm scripts / framework.
- **Bergantung pada:** dev dependencies di manifest.
- **State / efek samping:** build menghasilkan `.next/`, `next-env.d.ts`, `tsconfig.tsbuildinfo`;
  direktori/berkas tersebut generated, bukan sumber dan tidak diedit tangan.
- **Catatan:** `.gitignore` dibuat sebagai konfigurasi; tidak ada operasi git sesi ini.

### `web/README.md`
- **Peran:** run/preview, handoff Fase 3, tabel sumber semua copy bisnis/angka dan skill-project.
- **Ekspor utama:** commands build/start/verify/tunnel; status copy dan kontak; Blender node contracts.
- **Dipakai oleh:** pemilik dan harness Testing.
- **Bergantung pada:** PLAN §4–§12 relevan, lima dossier §1/§3/§5 dan batas demonstrasi masing-masing.
- **State / efek samping:** tidak ada.
- **Catatan:** fokus Automation Engineer dari klarifikasi pemilik; copy approved Fase 3; skill harian terpasang
  dinyatakan; kontak asli tercatat. Perintah paket bukti Testing ada di Verification.
  Script bukti Fase 1–2 diarsipkan, bukan acceptance Fase 3.

### `web/lib/instruments.ts`
- **Peran:** urutan lima instrumen + sumber data copy chapter/dialog bersama.
- **Ekspor utama:** `instruments`, `InstrumentId`, `ChapterState`.
- **Dipakai oleh:** page, shell, scene, skills type.
- **Bergantung pada:** tabel provenance README; dossier pemilik. Tidak ada dependency runtime luar.
- **State / efek samping:** tidak ada; readonly data, copy approved (gate Fase 3).
- **Catatan:** readings 1,080 / 50,000 / 11/11 / 200 / 300, masing-masing konteks demo eksplisit.

### `web/lib/skills.ts`
- **Peran:** kelompok skill PLAN §9, tiap item punya project pembukti.
- **Ekspor utama:** `skillGroups`; tipe lokal `Skill` / `SkillGroup`.
- **Dipakai oleh:** page.tsx untuk disclosure + project anchors.
- **Bergantung pada:** InstrumentId; dossier §5 dan PLAN §9.
- **State / efek samping:** tidak ada.
- **Catatan:** link diperinci menurut dossier (cross-browser hanya CrossCheck; cron hanya DueWatch).
  Grup "Daily work" (Go, MySQL / TiDB, Redis; konfirmasi pemilik, `projects: []` → tanpa link). Tanpa nama internal skill agen.

### `assets/blender/build_full_observatory.py`
- **Peran:** generator original empat instrumen Fase 3 via Blender GUI MCP.
- **Ekspor utama:** `make`, `setup`, `material`, `box`, `cylinder`, `sphere`, `line`, `ring`, `pivot`,
  `roller_marks`; `ROOT`, `SLUGS`; `result` dict.
- **Dipakai oleh:** execute_blender_code dengan __file__ eksplisit, __name__='__main__'.
- **Bergantung pada:** bpy, mathutils, pathlib; GUI mode OBJECT; Cycles OptiX tersedia (fallback CPU).
- **State / efek samping:** buat scene baru tanpa menghapus scene awal; save checkpoint sebelum
  mesh convert/join; gabung per parent animasi; ekspor Draco active scene; save sumber per slug.
- **Catatan:** menolak dirty GUI/output sudah ada. Render melalui MCP terpisah memakai filepath
  scene. Refinement DriftWatch menambahkan witness lines drum, disimpan setelah checkpoint.

### `assets/blender/surgeline-web.blend`, `driftwatch-web.blend`, `duewatch-web.blend`, `brandwall-web.blend` dan masing-masing `.blend1`
- **Peran:** sumber empat aset + checkpoint; file dapat menyimpan scene sebelumnya juga.
- **Ekspor utama:** scene `<slug> / web review`; empty/node animasi sesuai scene module di atas.
- **Dipakai oleh:** Blender GUI MCP → render PNG dan GLB.
- **Bergantung pada:** material/mesh internal; tanpa tekstur/file eksternal.
- **State / efek samping:** save/render/export; `.blend1` berubah saat save berikutnya.
- **Catatan:** checkpoint DriftWatch mencakup refinement drum; file Fase 0–2 tidak diubah.

### `web/public/models/surgeline.glb`, `driftwatch.glb`, `duewatch.glb`, `brandwall.glb`
- **Peran:** empat model runtime dengan node animasi terpisah.
- **Ekspor utama:** Draco GLB, masing-masing 75,328 / 52,836 / 59,748 / 40,888 byte.
- **Dipakai oleh:** Scene useGLTF array.
- **Bergantung pada:** `<slug>-web.blend`; decoder lokal.
- **State / efek samping:** read-only di browser.
- **Catatan:** nama node diverifikasi dari JSON GLB; 0 image textures. Total tujuh GLB 737,440 byte.

### `web/public/images/surgeline-fallback.png`, `driftwatch-fallback.png`, `duewatch-fallback.png`, `brandwall-fallback.png`, `rayina-duotone.png`
- **Peran:** still view dari render Blender + portrait approved untuk About.
- **Ekspor utama:** empat PNG RGBA 800×800; portrait 1086×1448.
- **Dipakai oleh:** shell fallback backgrounds; page Next Image.
- **Bergantung pada:** `assets/renders/full-observatory/<slug>-review.png`, `assets/photo/rayina-duotone.png`.
- **State / efek samping:** salinan runtime read-only; optimasi portrait oleh Next Image saat diminta.
- **Catatan:** tidak mengedit gambar/foto; exact copies dari aset sumber.

### `assets/renders/full-observatory/`
- **Peran:** render review baru dan verifikasi developer Fase 3.
- **Ekspor utama:** `surgeline-review.png`, `driftwatch-review.png`, `duewatch-review.png`,
  `brandwall-review.png`; `dev/` berisi `gate-`, `hero-`, lima `<slug>-`, `<slug>-dialog-`,
  `skills-`, `about-`, `contact-` PNG tiap viewport; `skills-daily-work-390x844.png` (grup Daily work); lima `fallback-<slug>-390x844.png`;
  `verification.json`, `asset-verification.json`, `env-check.md`; bila gagal `navigation-failure-<width>.png`.
- **Dipakai oleh:** developer review; handoff ke harness Testing.
- **Bergantung pada:** Blender MCP renders; verify_mobile.py; parsing GLB untuk byte/node/Draco;
  smoke launch CrossCheck verify_engines.py.
- **State / efek samping:** generated results ditulis ulang oleh alat; tidak diubah tangan.
- **Catatan:** Dev screenshots bukan gate. `evidence/` (tahap Testing, `full_observatory_evidence.py`):
  `00-instrument-renders.png`, `01-gate` … `24-fallback-still-view.png`, `full-observatory-walkthrough.mp4`
  (390×844 H.264), `contact-sheet.jpg` berlabel, `viewports/` (18 PNG + sheet), `evidence.json` 16/16 pass.

### `assets/blender/export_first_light.py`
- **Peran:** turunan ekspor dari scene kubah approved + membuat planet bercincin via GUI MCP.
- **Ekspor utama:** `export_first_light()`, `OUTPUT`, `MODELS`.
- **Dipakai oleh:** Blender MCP `execute_blender_code`, dengan `__file__` eksplisit.
- **Bergantung pada:** bpy, scene `Dome / night review`, pathlib.
- **State / efek samping:** scene/datablock baru; save sebelum convert/join salinan; dua GLB
  Draco dengan `use_active_scene=True`; save sumber `first-light.blend`.
- **Catatan:** menolak file output yang sudah ada dan GUI dirty; sumber Fase 0 tetap utuh.

### `assets/blender/first-light.blend`, `assets/blender/first-light.blend1`
- **Peran:** sumber aset Fase 1 dan checkpoint sebelum konversi salinan geometri.
- **Ekspor utama:** scene `First light / dome export` (objek `ObservatoryDome`) dan
  `First light / ambient planet` (`AmbientPlanet`); scene lama tetap tersimpan.
- **Dipakai oleh:** Blender GUI/MCP → render review dan GLB.
- **Bergantung pada:** material/geometri internal, tanpa tekstur/library eksternal.
- **State / efek samping:** render/save/export; backup dapat berganti pada save berikutnya.
- **Catatan:** `.blend1` sengaja dipertahankan; GLB hanya scene aktif, tidak membawa CrossCheck.

### `assets/blender/export_crosscheck.py`
- **Peran:** turunan ekspor teleskop CrossCheck approved untuk web via GUI MCP.
- **Ekspor utama:** `export_crosscheck()`, `OUTPUT`.
- **Dipakai oleh:** Blender MCP `execute_blender_code`, dengan `__file__` eksplisit.
- **Bergantung pada:** bpy, scene `CrossCheck / three optics` di file yang terbuka.
- **State / efek samping:** FULL_COPY scene → `CrossCheck / web export`; save checkpoint sebelum
  convert/join; gabung `OpticsBody` + `CrossCheckMount`, `Lens1..3` terpisah dengan material
  `Lens<n>Glow`, semua optik di bawah empty `OpticsPivot` (z 2.3); ekspor Draco level 6; save lagi.
- **Catatan:** menolak bila `crosscheck-web.blend` sudah ada atau GUI dirty; sumber Fase 0 tetap utuh.

### `assets/blender/crosscheck-web.blend`, `assets/blender/crosscheck-web.blend1`
- **Peran:** sumber ekspor teleskop Fase 2 dan checkpoint sebelum konversi.
- **Ekspor utama:** scene `CrossCheck / web export` (objek di atas) + scene lama tersalin.
- **Dipakai oleh:** Blender GUI/MCP → `crosscheck.glb`, render `crosscheck-web-review.png`.
- **Bergantung pada:** material/geometri internal, tanpa tekstur eksternal.
- **State / efek samping:** save berikutnya dapat mengganti `.blend1`.
- **Catatan:** `.blend1` sengaja dipertahankan.

### `web/public/models/crosscheck.glb`, `web/public/images/crosscheck-fallback.png`
- **Peran:** model runtime teleskop / still view chapter bila WebGL/model gagal.
- **Ekspor utama:** node `CrossCheckMount`, `OpticsPivot` > `OpticsBody`, `Lens1..3`;
  `KHR_draco_mesh_compression` wajib; 0 image texture.
- **Dipakai oleh:** Scene `useGLTF`; CSS `.crosscheck-fallback`.
- **Bergantung pada:** `crosscheck-web.blend`; fallback = salinan `crosscheck-web-review.png`.
- **State / efek samping:** read-only di browser.
- **Catatan:** 317336 / 731597 byte. Subtotal GLB Fase 1–2 508640 byte; total Fase 3 737440 byte (≤8 MB / file ≤1,5 MB).

### `assets/renders/crosscheck/`
- **Peran:** render review ekspor + bukti HP Fase 2.
- **Ekspor utama:** `crosscheck-web-review.png`; `gate-`, `hero-`, `menu-`, `crosscheck-start-`,
  `crosscheck-orbit-`, `crosscheck-end-`, `case-preview-` × `390x844|360x740|430x932`;
  `fallback-390x844.png`, `fallback-crosscheck-390x844.png`; `verification.json`;
  `walkthrough/` (6 PNG + `crosscheck-walkthrough.mp4`).
- **Dipakai oleh:** review pemilik, PROGRESS.
- **Bergantung pada:** export_crosscheck.py render; verify_mobile.py; chapter_walkthrough.py.
- **State / efek samping:** ditulis ulang saat verifikasi; jangan hand-edit.
- **Catatan:** emulasi Chromium, bukan uji HP fisik/fps.

### `web/public/models/dome.glb`, `web/public/models/ambient.glb`
- **Peran:** model runtime kubah / planet.
- **Ekspor utama:** satu scene/satu node root per file, `KHR_draco_mesh_compression` wajib.
- **Dipakai oleh:** Scene `useGLTF`.
- **Bergantung pada:** first-light.blend dan decoder lokal.
- **State / efek samping:** read-only di browser; cache drei.
- **Catatan:** 157308 / 33996 byte. Tidak ada image texture; KTX2 tidak diperlukan.

### `web/public/fonts/`, `web/public/images/dome-fallback.png`, `web/public/draco/`
- **Peran:** aset lokal font, fallback, dan decoder; tidak membutuhkan CDN.
- **Ekspor utama:** `fraunces.ttf`, `inter.ttf`, `jetbrains-mono.ttf`, masing-masing
  `*-LICENSE.txt`; `dome-fallback.png`; `draco_decoder.wasm`, `draco_wasm_wrapper.js`,
  `README.md` upstream dan `LICENSE.txt` Apache 2.0.
- **Dipakai oleh:** CSS / useGLTF.
- **Bergantung pada:** salinan aset style-lock/render; decoder distribusi three 0.186.0;
  teks lisensi Apache dari apache.org/licenses/LICENSE-2.0.txt.
- **State / efek samping:** hanya download/cache browser; salinan vendor tidak diedit.
- **Catatan:** fallback sama dengan dome-night.png approved, bukan pengganti diam-diam scene.

### `assets/renders/first-light/`
- **Peran:** arsip render Blender, screenshot HP, bukti alur dan environment Fase 1
  (sejak Fase 2 `verify_mobile.py` menulis ke `assets/renders/crosscheck/`).
- **Ekspor utama:** `dome-web-review.png`; `gate-`, `hero-`, `menu-`, `dome-scroll-` masing-masing
  `390x844.png`, `360x740.png`, `430x932.png`; `fallback-390x844.png`; `verification.json`;
  `env-check.md`; `preview-verification.json` / `preview-390x844.png` (cek tautan publik);
  `gate-evidence/` (`chromium|webkit|firefox/` 9 PNG + `*-walkthrough.mp4` + `contact-sheet.png`,
  `chromium-slow-4g/` 3 PNG + MP4, `gate-evidence.json`).
- **Dipakai oleh:** review pemilik, PROGRESS, harness berikutnya.
- **Bergantung pada:** Blender MCP render; verify_mobile.py / gate_evidence.py / Playwright.
- **State / efek samping:** PNG/JSON ditulis ulang saat verifikasi; jangan hand-edit hasil tes.
- **Catatan:** tidak mengklaim uji HP fisik, 4G atau performa fase polish.


### `assets/style-lock/index.html`
- **Peran:** contoh chapter CrossCheck di HP; setelah CTA tersedia render, foto, palet, font.
- **Ekspor utama:** HTML `lang=en`, anchor `#style-review`, CSS token §8 di `:root`.
- **Dipakai oleh:** server Python dan `verify_mobile.py`.
- **Bergantung pada:** tiga TTF lokal, dua render PNG, foto duotone; link ke crop foto.
- **State / efek samping:** anchor browser dan disclosure `<details>` native; tanpa JS/audio/Canvas.
- **Catatan:** full English, copy DRAFT; lebar maksimum 430px, desktop belum dirancang.
  Foto memuat disclosure edit AI di review notes. Tombol menuju bahan review, bukan case file.

### `assets/blender/build_style.py`
- **Peran:** membuat material, kubah terbuka, teleskop tiga lensa, kamera dan lampu.
- **Ekspor utama:** `build()`, `scene_setup()`, `material()`, `cylinder()`, `ring()`, `beam()`, `curve()`.
- **Dipakai oleh:** eksekusi kode melalui Blender MCP GUI.
- **Bergantung pada:** `bpy`, `mathutils`, `math`, `pathlib`; tidak memerlukan aset pihak ketiga.
- **State / efek samping:** membuat scene/datablock baru, memilih scene aktif, menyimpan dua `.blend`.
  Mencoba OptiX GPU; fallback CPU bila tidak tersedia. Render dipicu terpisah.
- **Catatan:** menolak bila `dome.blend`/`crosscheck.blend` sudah ada; gunakan output versi baru.
  Scene awal tetap utuh. Kamera ortografis teleskop 5.4; render Cycles 48 sampel dengan denoise.

### `assets/blender/dome.blend`
- **Peran:** sumber kubah review malam, shell per panel dan bukaan berpemandu amber.
- **Ekspor utama:** scene `Dome / night review` (80 objek).
- **Dipakai oleh:** Blender GUI/MCP → `assets/renders/dome-night.png`.
- **Bergantung pada:** material/mesh prosedural internal; tanpa linked library/tekstur eksternal.
- **State / efek samping:** render menulis PNG ke path project yang tersimpan.
- **Catatan:** juga menyimpan scene startup asli. Turunannya diekspor untuk Fase 1 melalui `first-light.blend`.

### `assets/blender/crosscheck.blend` dan `assets/blender/crosscheck.blend1`
- **Peran:** sumber teleskop tiga optik; `.blend1` backup otomatis sebelum penyempurnaan.
- **Ekspor utama:** scene aktif `CrossCheck / three optics` (100 objek),
  `Optic 1 lens`, `Optic 2 lens`, `Optic 3 lens`.
- **Dipakai oleh:** Blender GUI/MCP → `assets/renders/crosscheck-night.png`.
- **Bergantung pada:** material/mesh internal; juga berisi scene kubah dan startup asli.
- **State / efek samping:** render menulis PNG. Save berikutnya dapat memperbarui backup `.blend1`.
- **Catatan:** `.blend` adalah versi review approved; ekspor web lewat salinan `crosscheck-web.blend`.

### `assets/style-lock/verify_mobile.py`
- **Peran:** verifikasi fokus contoh HP setelah perubahan visual.
- **Ekspor utama:** async `main()`; `URL` port 8766.
- **Dipakai oleh:** perintah Python dari venv CrossCheck yang sudah tersedia.
- **Bergantung pada:** Python Playwright; server lokal; `index.html` beserta asetnya.
- **State / efek samping:** browser headless sementara; overwrite dua screenshot + `verification.json`.
- **Catatan:** cek overflow, CTA dalam viewport, 4 elemen gambar, 3 font, marker English/DRAFT,
  error browser, anchor dan disclosure. Bukan QA lintas engine atau performa HP fisik.

### `assets/style-lock/gate_audit.py`
- **Peran:** audit teknis gate Fase 0 di Chromium/Firefox/WebKit × 390×844, 360×740, 430×932.
- **Ekspor utama:** async `main()`, `run()`, `PROBE` (JS), `PAIRS` (pasangan kontras), `ratio()`.
- **Dipakai oleh:** agen saat menyiapkan bukti gate; perintah di §2.
- **Bergantung pada:** Python Playwright (venv CrossCheck, tiga engine); server lokal :8766.
- **State / efek samping:** overwrite `assets/renders/gate-audit/` (PNG DPR 2 + `gate-audit.json`).
- **Catatan:** cek overflow, teks terpotong, CTA layar pertama, tap ≥44px, font/gambar, identitas
  (brand, nama, DRAFT, tanpa "Amazon"), anchor/disclosure, error, kontras AA 4.5:1. Firefox tanpa
  `is_mobile`. Hasil terakhir 9/9 PASS, kontras 7/7. Bukan penilaian selera/kemiripan foto.

### `assets/style-lock/verification.json`
- **Peran:** bukti terstruktur hasil check HP terakhir.
- **Ekspor utama:** `viewport`, `horizontalOverflow`, `ctaBottom`, `fonts`, `images`, `text`,
  `reviewAnchorWorks`, `notesOpen`, `errors`.
- **Dipakai oleh:** review dan dokumentasi sesi; bukan data aplikasi.
- **Bergantung pada:** output `verify_mobile.py`.
- **State / efek samping:** ditulis ulang saat cek; jangan hand-edit hasil.
- **Catatan:** final 390×844, CTA y=789, nol error, semua aset/font termuat.

### `assets/style-lock/fonts/`
- **Peran:** self-host tiga font regular weight 400 dan lisensi SIL OFL.
- **Ekspor utama:** `fraunces.ttf`, `inter.ttf`, `jetbrains-mono.ttf`;
  `fraunces-LICENSE.txt`, `inter-LICENSE.txt`, `jetbrains-mono-LICENSE.txt`.
- **Dipakai oleh:** `index.html` lewat `@font-face`, `font-display:swap`.
- **Bergantung pada:** font dari Google Fonts; lisensi dari paket `@fontsource` 5.3.0.
- **State / efek samping:** tidak ada; browser hanya request server lokal.
- **Catatan:** URL sumber dicatat di `provenance.json`. Weight diperiksa dengan fontTools.

### `assets/photo/rayina-crop.png` dan `assets/photo/rayina-duotone.png`
- **Peran:** portrait crop tanpa signage dan treatment navy + scan untuk gate Fase 0.
- **Ekspor utama:** dua PNG portrait 1086×1448.
- **Dipakai oleh:** review `index.html`; crop ditautkan untuk pembandingan.
- **Bergantung pada:** foto pemilik `/home/rayin/Documents/profile foto.jpg`; built-in imagegen.
- **State / efek samping:** tidak ada. Foto asli tidak diubah.
- **Catatan:** crop mencakup edit AI pada latar untuk menjaga bahu; kemiripan disetujui di gate Fase 0.
  Prompt lengkap di `provenance.json`.

### `assets/renders/`
- **Peran:** dua render model dan dua screenshot HP sebagai bukti visual.
- **Ekspor utama:** `dome-night.png`, `crosscheck-night.png`, `mobile-390x844.png`,
  `style-review-mobile.png`.
- **Dipakai oleh:** `index.html`, pemilik saat gate, log sesi.
- **Bergantung pada:** dua scene Blender untuk render; `verify_mobile.py` untuk screenshot.
- **State / efek samping:** overwrite saat render/check diulang.
- **Catatan:** screenshot penuh menampilkan review notes masih tertutup; interaksinya dites terpisah.

### `assets/style-lock/README.md`, `env-check.md`, `provenance.json`
- **Peran:** instruksi review/rebuild, bukti environment, sumber aset dan prompt.
- **Ekspor utama:** status gate Fase 0 approved; perintah verifikasi; tiga versi engine;
  sumber foto/font dan dua prompt imagegen persis.
- **Dipakai oleh:** pemilik dan harness sesi berikutnya.
- **Bergantung pada:** PLAN §5/§8/§11, dossier CrossCheck §1/§3.1, hasil tools sesi ini.
- **State / efek samping:** tidak ada.
- **Catatan:** README mencatat gate Fase 0 yang telah diberikan pemilik; copy chapter tetap DRAFT.
  Sesi 2026-09-15 membetulkan heading/paragraf approval lama dan pointer ekspor Fase 1.

### `PROGRESS.md` dan `CODEMAP.md`
- **Peran:** sumber status fase dan peta berkas terkini.
- **Ekspor utama:** fase aktif, checklist, blocker, log; entri aset/modul/perintah.
- **Dipakai oleh:** seluruh harness saat mulai dan menutup sesi.
- **Bergantung pada:** pekerjaan nyata, bukti verifikasi, gate eksplisit pemilik. Mulai Fase 3 tiap fase punya
  tahap Development (Codex/Claude Code) lalu Testing (Claude Code/Antigravity, paket bukti di
  `assets/renders/<slug-fase>/evidence/`); lihat PLAN §12 dan `PROMPT.md`.
- **State / efek samping:** diperbarui setiap sesi; tidak menandai fase done tanpa gate pemilik.
- **Catatan:** Fase 0 `done` 2026-09-14; Fase 1 `done` 2026-09-15; Fase 2 `done` 2026-09-15; Fase 3 `done` 2026-09-15. Log sesi dijaga ringkas.

## 5. Aset

Ukuran byte aset Fase 0 diukur 2026-09-14; aset Fase 1 pada 2026-09-15.

| Aset | Sumber | Ekspor GLB | Ukuran | Dipakai di |
|---|---|---|---:|---|
| `dome.glb` | `first-light.blend` via GUI MCP | Draco | 157308 | hero runtime |
| `ambient.glb` | `first-light.blend` via GUI MCP | Draco | 33996 | planet ambient |
| `surgeline.glb` | `surgeline-web.blend` via MCP | Draco | 75328 | chapter SurgeLine |
| `driftwatch.glb` | `driftwatch-web.blend` via MCP | Draco | 52836 | chapter DriftWatch |
| `duewatch.glb` | `duewatch-web.blend` via MCP | Draco | 59748 | chapter DueWatch |
| `brandwall.glb` | `brandwall-web.blend` via MCP | Draco | 40888 | chapter BrandWall |
| `crosscheck.glb` | `crosscheck-web.blend` via GUI MCP | Draco | 317336 | chapter CrossCheck |
| `crosscheck-web.blend` | `export_crosscheck.py` via MCP | — | 1474273 | sumber ekspor |
| `crosscheck-web.blend1` | checkpoint sebelum konversi | — | 357959 | pemulihan lokal |
| `crosscheck-fallback.png` | salinan `crosscheck-web-review.png` | — | 731597 | still view chapter |
| `dome.blend` | `build_style.py` via MCP | — | 201852 | Blender/review |
| `crosscheck.blend` | `build_style.py` + refinement via MCP | — | 282373 | Blender/review |
| `crosscheck.blend1` | backup Blender sebelum refinement | — | 277138 | pemulihan lokal |
| `dome-night.png` | `dome.blend` | — | 707523 | review HTML |
| `crosscheck-night.png` | `crosscheck.blend` | — | 731509 | chapter + review |
| `rayina-crop.png` | foto pemilik + imagegen | — | 1935310 | tautan review |
| `rayina-duotone.png` | crop + imagegen | — | 1700824 | portrait review |
| `mobile-390x844.png` | Playwright | — | 87502 | bukti gate |
| `style-review-mobile.png` | Playwright | — | 355265 | bukti gate |
| `fraunces.ttf` | Google Fonts | — | 71580 | heading |
| `inter.ttf` | Google Fonts | — | 324820 | body |
| `jetbrains-mono.ttf` | Google Fonts | — | 112172 | readout |

## 6. Alur penting

Fase 3:
1. Page map instruments → lima section sticky; main trigger menghitung index/transisi/orbit/outro.
2. Scene membaca chapter ref → kamera + group incoming/outgoing + node idle, tetap satu Canvas.
3. Skills disclosure → ResizeObserver → refresh bounds; link → Lenis scroll + highlight + fokus heading.
4. About portrait masuk viewport → GSAP clipping + scan line; Contact → `mailto:` + tiga link eksternal tab baru.
5. Case CTA → selectedCase → dialog context per project; tutup memulihkan fokus dan scroll.
6. Error model baru → semua instrumen tetap tersedia sebagai still view berlabel.

Fase 2:
1. Scroll lewat hero → trigger reveal `#crosscheck` (top bottom → top top) → kamera mulai
   berputar, teleskop naik, kubah hilang, `data-chapter=crosscheck`.
2. Section sticky → trigger orbit (top top → bottom bottom) → sudut kamera; mundur = menelusur balik.
3. Idle `useFrame`: ayun `OpticsPivot`, gelombang emissive `Lens1..3Glow` bergiliran.
4. Klik `[data-open-case]` → delegasi shell → dialog case preview → Lenis stop → Return → fokus kembali.
5. Menu → Work → `scrollFromMenu('#crosscheck')`.

Fase 1:
1. Root layout → shell persisten → gate + lazy Canvas → GLB/decoder/font lokal.
2. Model decode/render + font settle → Enter aktif → gesture membuat/resume audio.
3. GSAP ticker → Lenis → ScrollTrigger → ref progress + readout DOM → useFrame kubah.
4. Toggle → Web Audio fade + localStorage; hidden tab → audio fade out.
5. Load/WebGL gagal → still view berlabel; menu/contact → native dialog.
6. Produksi `:8767` → quick tunnel sementara → review pemilik; tidak deploy Vercel/domain.

Arsip Fase 0:

1. `build_style.py` via MCP → scene baru + `.blend` → render PNG RGBA.
2. Foto asli → imagegen crop/edit latar → imagegen duotone → dua PNG lokal.
3. HTTP server `assets/` → `style-lock/index.html` → font/render/foto lokal.
4. CTA → `#style-review` → gambar besar/palet/font; disclosure menjelaskan sumber dan status DRAFT.
5. `verify_mobile.py` → Chromium 390×844 → screenshot + JSON → pemilik melihat dan memberi gate.

## 7. Konvensi

- Token persis PLAN §8 (FINAL sejak gate Fase 0), termasuk bantu `muted` #A5AEC2 dan `line` #303A50.
- English penuh, nama Rayina Ilham, brand Rayin Observatory; copy baru DRAFT sampai approve; homepage approved Fase 3.
- Fase 0 di `assets/style-lock/`; Fase 1–3 di `web/`. Gate Fase 1 dan Fase 2 lolos 2026-09-15.
- Instrumen baru mengikuti pola CrossCheck: skrip ekspor salinan `<nama>-web.blend`, node/material
  bernama untuk gerak idle, section sticky + trigger reveal/orbit, fallback PNG.
- Geometri Blender dibuat lewat MCP; save sebelum operasi destruktif; jangan hapus scene awal.
- Font lokal dengan lisensi; layar contoh Fase 0 tetap tanpa JS. Aplikasi Fase 1 memakai manifest npm.
- Perubahan gambar/HTML → cek ulang viewport HP (emulasi) dan perbarui screenshot/JSON, CODEMAP, PROGRESS.
- Bukti gate (tahap Testing): contoh pola ada di `gate_evidence.py` (per item + MP4 + contact sheet) dan
  `chapter_walkthrough.py`; keluaran baru ke `assets/renders/<slug-fase>/evidence/`.

### Catatan fix navigasi Fase 3

`scrollFromMenu` menyelesaikan anchor menjadi angka `element.getBoundingClientRect().top +
window.scrollY` sebelum `lenis.scrollTo`. Bukti repro: browser y=13751, Lenis animatedScroll=14241
saat klik skill; anchor string meleset 490px. Tes kini memicu native scroll + klik dalam satu task
untuk menjaga regresi ini. Sorotan hanya warna heading, sehingga kicker tidak terdorong.
