# CODEMAP — Peta kode Rayin Observatory

Revisi terbaru 2026-09-16 · Claude Code: **Gate 7A lolos → `done`** (DRAFT CrossCheck dilepas); sebelumnya Testing 7A + alat efisiensi tes Q42; lihat “Fase 7A — Testing” dan “Alat tes Q42” di §4.
Sebelumnya · Claude Code: Fase 7A Development (CrossCheck inspection room).
Sebelumnya · Codex: urutan delapan planet + perbaikan gerak/fade; lihat “Revisi urutan planet”.

> **Tujuan:** baca peta ini, bukan pindai seluruh kode. Buka berkas kode hanya jika peta
> menunjuknya dan berkas akan diubah. Update setiap berkas dibuat/diubah/dipindah/dihapus.
> Entri tidak cocok dengan kode = bug; perbaiki saat ditemukan.

**Terakhir diperbarui:** 2026-09-16 · Claude Code · **Gate 7A lolos → `done`**: `cases.ts` CrossCheck `draft: false`; `verify_case.py` (draft label 0), `verify_cases.py` (CrossCheck `draft: False`), `crosscheck_room_evidence.py` (story: label 0). Sebelumnya Testing 7A: paket bukti `crosscheck_room_evidence.py` 16/17; fix regresi fps (posisi lensa ke objek JS, bukan CSS akar) + scrub SVG lebih ringan; `run_regressions.py` + `perf_quick.py` + hook `OBSERVATORY_PHONES` (Q42).
Sebelumnya: 2026-09-16 · Claude Code · Fase 7A Development → `ready-for-test`.
Sebelumnya: 2026-09-16 · Claude Code · Fase 7 **Testing ulang** setelah fix "Enter aktif lebih cepat": item bukti baru `enterEarly` di `showpiece_evidence.py` (14 item) membuktikan lima GLB instrumen baru diminta sesudah Enter aktif dan chapter/case aman selama jeda. Paket bukti diperbarui 14/14 pass; diukur ulang: gate 1.41 dtk, Enter aktif **6.39 dtk** (dulu 12.2), transfer sebelum Enter 787,063 B, instrumen selesai +3.0 dtk. Enam suite regresi diulang `passed`. **Gate Fase 7 lolos 2026-09-16** (jeda instrumen ±3 dtk diterima apa adanya) → Fase 7 `done`, berikutnya Fase 8 Launch ready.
Sebelumnya (Development hari yang sama): Enter menunggu hero saja (kubah + Saturnus + font), preload GLB/Draco dari HTML, Scene diimpor statis, font WOFF2 subset; tes fallback menunggu `data-scene=fallback`.

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
Sejak Fase 5 kelima "Open case file" terbang ke `/work/<slug>`; dialog preview Fase 3 dihapus.

Fase 3: `lib/instruments.ts` menjadi sumber lima chapter/copy; `lib/skills.ts` memetakan
skill ke project. Shell menghitung chapter aktif, orbit, transisi dan outro dari posisi section
nyata. Scene memuat tujuh GLB dalam satu Canvas; lima group instrumen berbagi kamera. Skills
memakai disclosure native; setiap tautan mengembalikan scroll/fokus ke project dan menyorot judul.
About: portrait approved + GSAP clip/scan. Contact: CTA `mailto:` + empat link asli dari pemilik.
Hero menegaskan Automation Engineer sesuai arahan pemilik sesi ini.

Preview pada port 8767. Preview Fase 0 tetap arsip HTML `assets/style-lock/` pada 8766.
Fase 3 menambahkan empat instrumen, Skills, About dan Contact. Fase 4 menambahkan case file CrossCheck.
Fase 5: satu template case (`case-file.tsx`) dari data `lib/cases.ts` untuk lima route statis `/work/[slug]`;
Next instrument berantai (mundur → sapuan chapter ke instrumen berikut → terbang masuk), BrandWall → CrossCheck. Fase 6: stage desktop penuh, teks kiri/objek kanan, header nav langsung; case brief dua kolom, panel inspeksi, alur mendatar, readings/tools grid.

## 2. Perintah

Semua dari root project kecuali disebut lain.

| Perintah | Fungsi |
|---|---|
| `cd web/scripts && timeout 1500 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python showpiece_evidence.py` | Paket bukti Testing Fase 7 → `assets/renders/showpiece/evidence/`: 14 item (termasuk `enterEarly`: urutan unduh instrumen sesudah Enter + scroll/case dini), MP4 390×844 **dengan audio asli situs**, performa PLAN §11 (gate slow 4G + CPU 4×, fps 4×/6×, GLB, DPR), contact sheet, `evidence.json`; exit 1 bila ada fail. Jalankan setelah 6 suite regresi (item `phones` membaca JSON-nya). Server :8767 aktif. |
| `/home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/run_regressions.py [--suites a,b] [--phone-only mobile,case,cases,showpiece] [--force] [--list]` | **Q42 — pakai ini untuk semua regresi.** Suite berurutan (room, audio, mobile, case, cases, showpiece, desktop-a, desktop-b, perf-crosscheck); lewati suite yang sudah `passed` pada sidik jari sumber sama (`assets/renders/regression-ledger.json`); `--phone-only` = 390×844 saja; menolak jalan bila build lebih tua dari sumber. Dari root, server :8767 aktif. |
| `cd web/scripts && timeout 600 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python perf_quick.py --slug <project> [--baseline <url>]` | **Q42 — gerbang fps Development** sebelum `ready-for-test`: 390×844 DPR 2, suara nyala, CPU 4×, chapter → terbang → scroll case → Return; tiap segmen ≥45 fps dan ≤10% frame lambat → `assets/renders/perf-quick/<slug>.json`. `--baseline` = build pembanding (mis. salinan HEAD di port lain) untuk atribusi. |
| `cd web/scripts && timeout 2400 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python crosscheck_room_evidence.py [--only mobile,desktop,back,slow,viewports,fps,images]` | Paket bukti Testing 7A → `assets/renders/personal-crosscheck/evidence/` (17 item, 8 kategori, 3 MP4, contact sheet HP + desktop, `evidence.json`); `--only` untuk debug (paket tetap dihapus dulu). Jalankan sesudah runner regresi; ±25 menit. |
| `/home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/build_crosscheck_run.py` | Fase 7A: baca hasil run CrossCheck (read-only), assert total = dossier, tulis `web/lib/crosscheck-run.ts` + 7 crop bukti `web/public/images/crosscheck/`. Gagal (tanpa menulis) bila angka beda. |
| `cd web/scripts && timeout 900 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python verify_crosscheck_room.py [--sizes WxH,...] [--no-edges]` | Fase 7A Development: strip lane chapter, iris lensa masuk/kembali, leader hanya saat model ada, scrub inspection field maju/mundur/flick, 4 temuan + bukti, teaser Next; 390/360/430 → 768 → 1440/1920; edge Back saat terbang, model diblok, reduced motion → `assets/renders/personal-crosscheck/dev/`. Server :8767 aktif. |
| `node web/scripts/verify_audio.mjs` | Fase 7: 9 tes lifecycle audio (resume race, batas voice, hidden, mute, cleanup) → `showpiece/dev/audio-verification.json`. |
| `timeout 600 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_showpiece.py` | Fase 7 Development: tiga HP, Web Audio nyata, loader, lima pitch, chain/return/history/fallback → `showpiece/dev/`. Server :8767 aktif; suite GPU dijalankan bergantian. |
| `npm ci --prefix web` | Instal versi terkunci dari package-lock. |
| `npm run build --prefix web` | Build produksi + TypeScript + prerender statis. |
| `npm run start --prefix web` | Preview produksi `0.0.0.0:8767`. |
| `npm run dev --prefix web` | Dev server port 8767; gunakan saat produksi tidak berjalan. |
| `npm run lint --prefix web` / `npm run typecheck --prefix web` | ESLint / TypeScript terpisah. |
| `cd web/scripts && timeout 1500 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python desktop_evidence.py` | Paket bukti Testing Fase 6 → `assets/renders/desktop/evidence/`: 21 item pass/fail, MP4 1440×900, contact sheet, sheet desktop/resize/HP, `evidence.json`; exit 1 bila ada fail. Jalankan setelah regresi dev (item `phones` membaca status JSON-nya). Server :8767 aktif. |
| `timeout 900 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_desktop.py` | Development Fase 6: HP → tiga desktop, layout + 5-case chain/history/hotspot/fallback → `assets/renders/desktop/dev/`. |
| `timeout 300 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_case.py` | Tes fokus Fase 4: tiga viewport HP, route/return/history, Canvas sama, hotspot, readings, video, direct URL + fallback → `assets/renders/case-crosscheck/dev/`. |
| `cd web/scripts && timeout 900 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python verify_cases.py` | Tes fokus Fase 5: lima case, buka-dari-chapter + Return, rantai Next penuh (wrap), Back/Forward, 5 direct URL, slug asing 404, fallback DueWatch; 3 viewport HP → `assets/renders/case-files/dev/`. Server :8767 aktif. |
| `cd web/scripts && timeout 900 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python case_files_evidence.py` | Paket bukti Testing Fase 5 → `assets/renders/case-files/evidence/`: 17 item pass/fail, MP4 390×844 walkthrough rantai penuh, contact sheet 24 frame, viewports sheet, `evidence.json`; exit 1 bila ada fail. Server :8767 aktif. |
| `timeout 600 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/case_crosscheck_evidence.py` | Paket bukti Testing Fase 4 → `assets/renders/case-crosscheck/evidence/`: 14 item pass/fail, MP4 390×844, contact sheet, viewports sheet; exit 1 bila ada fail. Server :8767 aktif. |
| `timeout 420 npm run verify:mobile --prefix web` | Regresi homepage setelah Fase 4: CrossCheck route/return + entry + lima chapter + skills/about/contact; 390×844 → 360×740 → 430×932. JSON/PNG ke `assets/renders/full-observatory/dev/`; server :8767 aktif. |
| `timeout 600 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/full_observatory_evidence.py` | Arsip bukti gate Fase 3 (lolos) → `assets/renders/full-observatory/evidence/`; cek copy lama mengharapkan label DRAFT. |
| `timeout 400 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/revision_evidence.py` | Bukti revisi langit + animasi → `assets/renders/revision-sky-motion/evidence/`: MP4 390×844, PNG per item, contact sheet, `evidence.json`; server :8767 aktif. |
| `cd web/scripts && timeout 400 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python revision_sky_lines_evidence.py` | Bukti revisi 3 (bintang + leader line) → `assets/renders/revision-sky-lines/evidence/`: PNG langit home/chapter/case + 3 hotspot × 3 viewport, contact sheet, `evidence.json` (jarak leader ke lens lain ≥30px); exit 1 bila gagal. Server :8767 aktif. |
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
├── PROMPT.md                       prompt sesi; 2026-09-16 + aturan commit/push wajib tiap akhir fase
├── PROGRESS.md                     status fase + checklist + log
├── CODEMAP.md                      peta ini
├── .gitignore                      root: assets/, *.blend1, Python cache/venv, env, OS files
├── web/
│   ├── package.json               npm commands + pinned dependencies
│   ├── package-lock.json          generated npm dependency graph
│   ├── tsconfig.json              strict TypeScript / alias @/*
│   ├── next.config.ts             React strict / three transpilation
│   ├── eslint.config.mjs          Next core-web-vitals + TypeScript
│   ├── .gitignore                 excludes generated output / local env
│   ├── README.md                  run, gate, provenance, scope, verification
│   ├── app/
│   │   ├── layout.tsx             root persistent shell, fonts CSS, metadata, hero asset preloads
│   │   ├── page.tsx               hero + five chapters + Skills/About/Contact, approved copy
│   │   ├── work/[slug]/page.tsx   five prerendered case routes → client CaseFile
│   │   └── globals.css            locked tokens, mobile + desktop composition, gate/menu
│   ├── components/
│   │   ├── case-file.tsx           case template: brief, hotspots, flow, readings, tools, video, Next
│   │   ├── crosscheck-room.tsx     Fase 7A: InspectionField (SVG matrix scrub), FindingSheet, NextTeaser
│   │   ├── observatory-shell.tsx  entry/loading/audio/menu/scroll ownership
│   │   ├── observatory-scene.tsx  one Canvas, dome/Saturn + five instrument groups
│   │   ├── instrument-models.ts   procedural build of the five instruments (shared kit + palette)
│   │   ├── instrument-motion.ts   per-instrument idle rigs + Saturn rig (moons, ring dust)
│   │   └── sky.tsx                full-screen sky shader: gradient, stars, nebula
│   ├── lib/cases.ts                five case files (CrossCheck hotspot copy DRAFT, 7A) + CaseView + aperture
│   ├── lib/crosscheck-room.ts      Fase 7A DRAFT copy: lanes, four steps' readouts, four findings
│   ├── lib/crosscheck-run.ts       GENERATED run data: 40×27 matrix, 18 issues, access/flows, evidence cells
│   ├── lib/ambient.ts             original hum + five clicks + camera sweeps / mute / lifecycle
│   ├── lib/instruments.ts         ordered chapter copy, readings, dialog context + types
│   ├── lib/skills.ts              grouped skills and evidence-project IDs
│   ├── scripts/build_crosscheck_run.py  Phase 7A data + evidence crops from the CrossCheck run (asserted)
│   ├── scripts/verify_crosscheck_room.py  Phase 7A focused checks, six viewports + edges
│   ├── scripts/crosscheck_room_evidence.py  Phase 7A Testing evidence pack (phone + desktop walkthroughs, slow motion, fps, sources)
│   ├── scripts/run_regressions.py  Q42 regression runner + ledger (skip suites already green on the same source)
│   ├── scripts/perf_quick.py      Q42 Development fps gate (4x CPU, one phone)
│   ├── scripts/case_files_evidence.py  Phase 5 Testing evidence pack (all 5 cases + chain)
│   ├── scripts/desktop_evidence.py  Phase 6 Testing evidence pack (desktop MP4 + 21 items)
│   ├── scripts/verify_audio.mjs    Phase 7 controlled audio lifecycle checks
│   ├── scripts/verify_showpiece.py  Phase 7 real audio + loader + transitions, three phones
│   ├── scripts/showpiece_evidence.py  Phase 7 Testing evidence pack (MP4 + real audio, PLAN §11 perf)
│   ├── scripts/verify_desktop.py  Phase 6 Development: HP → desktop, 5-case chain + layout checks
│   ├── scripts/verify_cases.py    focused Phase 5 checks: five cases + Next chain
│   ├── scripts/verify_case.py     focused Phase 4 development checks (CrossCheck detail)
│   ├── scripts/case_crosscheck_evidence.py  Phase 4 Testing evidence pack
│   ├── scripts/verify_mobile.py   focused browser interaction checks
│   ├── scripts/full_observatory_evidence.py  arsip bukti gate Fase 3
│   ├── scripts/gate_evidence.py   gate evidence Fase 1: 3 engines, screenshots, videos, slow 4G
│   ├── scripts/chapter_walkthrough.py  gate evidence Fase 2: video + 6 frames 390×844
│   ├── scripts/revision_evidence.py  bukti revisi langit/animasi: MP4 + PNG + contact sheet
│   ├── scripts/revision_sky_lines_evidence.py  bukti revisi 3: bintang + jarak leader line
│   └── public/
│       ├── videos/<slug>-explainer.mp4  five original silent English demos (byte-identical copies)
│       ├── models/                dome/ambient + five instrument GLBs, Draco
│       ├── fonts/                 3 WOFF2 subset (served) + approved 3 TTF (source) + 3 OFL copies
│       ├── images/                dome + five fallback PNGs; five demo posters; approved portrait copy
│       ├── images/crosscheck/     Fase 7A: 7 crops of CrossCheck's own evidence images (CC-001/003/015/017)
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
    │   ├── personal-crosscheck/dev/  Phase 7A Development PNGs + verification.json (verify_crosscheck_room)
    │   ├── personal-crosscheck/evidence/  Phase 7A Testing gate pack (MP4 ×3, sheets, evidence.json)
    │   ├── perf-quick/<slug>.json  Q42 fps gate results
    │   ├── regression-ledger.json  Q42 runner ledger (suite → source fingerprint, status)
    │   ├── showpiece/evidence/   Phase 7 Testing: MP4 390×844 + real audio, contact sheet, perf PNG/chart, phones/ + edges/, evidence.json
│   ├── showpiece/dev/        Phase 7 PNGs, verification.json, audio-verification.json, env-check.md
    │   ├── desktop/evidence/     Phase 6 Testing: PNG per item, MP4 1440×900, contact sheet, viewports/ + phones/ sheets, evidence.json
    │   ├── desktop/dev/          Phase 6 before/review/final PNGs, verification.json, env-check.md
    │   ├── case-files/evidence/   Phase 5 Testing evidence: 17 items, MP4 walkthrough, contact sheet, viewports sheet, evidence.json
    │   ├── case-files/dev/        Phase 5 verify_cases PNG per case/viewport + verification.json
    │   ├── case-crosscheck/dev/   Phase 4 screenshots, verification.json, env-check.md
    │   ├── case-crosscheck/evidence/  Phase 4 Testing: PNG per item, MP4, contact sheet, evidence.json
    │   ├── revision-sky-motion/    evidence/ revisi langit + animasi instrumen (2026-09-15)
    │   ├── revision-sky-lines/     evidence/ revisi 3: bintang jarang + leader line CrossCheck
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

### Alat tes Q42 (2026-09-16, Claude Code, sesi Testing 7A)
Aturan pakai: PLAN §12.3. Tujuan: Testing tidak mengulang yang sudah hijau; regresi fps ketahuan di Development.

#### `web/scripts/run_regressions.py`
- **Peran:** satu pintu regresi; suite berurutan (satu GPU), ledger per suite.
- **Ekspor utama:** `SUITES` (nama → perintah, cwd, timeout, JSON hasil, hormati `OBSERVATORY_PHONES`, salin JSON), `fingerprint()`, `main()`.
- **Dipakai oleh:** Development + Testing semua fase berikut; tambah suite baru fase aktif (mis. `room`, `perf-<slug>`) ke `SUITES`.
- **Bergantung pada:** venv CrossCheck, node, server :8767, `web/.next/BUILD_ID`.
- **State / efek samping:** tulis `assets/renders/regression-ledger.json` {fingerprint, status, phones one|full, exit, seconds, finishedAt, report}; `desktop-a` menyalin JSON ke `desktop/dev/verification-390-1366.json` (verify_desktop menimpa JSON yang sama).
- **Catatan:** sidik jari = isi `web/app|components|lib|public` (berkas >5 MB: ukuran + mtime) + lockfile + next config → build ulang dengan isi sama tidak memaksa ulang. Status gagal bila exit ≠ 0 atau JSON `status` ≠ passed. Phone-only tidak memenuhi permintaan full. Ledger dimulai 2026-09-16 (`audio`; `case` + `cases` phone-only di build gate 7A); run 8 suite penuh hari itu terjadi sebelum runner ada. Jebakan: jangan `pkill -f` dengan pola yang juga ada di baris perintah shell sendiri.

#### `web/scripts/perf_quick.py`
- **Peran:** gerbang fps Development per project.
- **Ekspor utama:** `measure(browser, url, slug)`, `stats`, `swipe_until`; CLI `--slug`, `--baseline`.
- **State / efek samping:** `assets/renders/perf-quick/<slug>.json` (`current`, `baseline`, `rule`); exit 1 bila segmen gagal.
- **Catatan:** aturan ≥45 fps + ≤10% frame >22 ms (lebih longgar dari p95 ketat paket bukti Fase 7/7A; frame headless terkuantisasi 16.7/33.3 ms sehingga p95 biner). Ukur 2026-09-16 build final: chapter 55.9, terbang 47.8, scroll case 57.7, Return 56.2 fps; HEAD `ac01ca4` 59.0/56.7/59.8/56.8.

#### Hook `OBSERVATORY_PHONES` (verify_mobile.py, verify_case.py, verify_cases.py via `verify_case.PHONES`, verify_showpiece.py)
- Default `390x844,360x740,430x932` (perilaku lama); runner `--phone-only` mengisi `390x844`.

### Fase 7A — Testing (2026-09-16, Claude Code)

#### `web/scripts/crosscheck_room_evidence.py`
- **Peran:** generator paket bukti gate 7A (bukan tes Development).
- **Ekspor utama:** `ITEMS` (17 item → kategori), `CATEGORIES`, `REGRESSIONS`, `OWNER` (temuan untuk pemilik), `mobile_walk`, `desktop_walk`, `model_slow_fail`, `perf`, `image_weight`, `sources_check`, `viewports` (memanggil `verify_crosscheck_room.viewport/edges` dengan `vcr.OUT` = `evidence/viewports`), `back_during_flight_shot`, `slow_motion`, `sheets`, `verdicts`; `--only` debug.
- **Bergantung pada:** `verify_crosscheck_room` (enter/idle/land/field_at/iris_trace), `case_files_evidence.tile`, dossier `portfolio/CAPABILITY_CROSSCHECK.md`, `/home/rayin/Projects/Testing/crosscheck/scripts/prepare_video_assets_en.py` (sumber "37%" dan "403"), node (parse `crosscheck-run.ts`), ffmpeg drawtext DejaVuSans, matplotlib/Pillow.
- **State / efek samping:** hapus + tulis ulang `assets/renders/personal-crosscheck/evidence/`; menjalankan `build_crosscheck_run.py` untuk cek byte-identik lalu **mengembalikan mtime** output (agar runner tidak menganggap build basi).
- **Catatan:** HP = touch CDP (`swipe` ± arah), desktop = wheel Lenis; posisi pasti tetap `land`. Slow motion = rekaman di-retime 4× (tanpa interpolasi), label drawtext. Cek `performance` memakai aturan ketat Fase 7 (≥45 fps **dan** p95 ≤22.2 ms). Instrumen prosedural → "model lambat" diuji sebagai leader selama terbang + `ambient.glb` diblok. `innerText` melewatkan readout step HP yang tersembunyi → sumber memakai `textContent` + teks tiap temuan.

#### `assets/renders/personal-crosscheck/evidence/`
- `walkthrough-mobile.mp4` (390×844, 266 dtk), `walkthrough-desktop.mp4` (1440×900, 80 dtk), `slow-motion.mp4` (720×844, 147 dtk), `contact-sheet-mobile.jpg`, `contact-sheet-desktop.jpg`, strip `i01`…`i12`, `p01-fps-4x.png`, PNG sumber `m*`/`d*`, `viewports/` (vcr 6 viewport + fallback/reduced motion), `edges/back-during-flight.png`, `evidence.json` (items, categories, measurements, videos, forOwner). Generated; jangan edit tangan (pengecualian 2026-09-16: `forOwner` diisi dari `OWNER` setelah run).
- Hasil 2026-09-16 (build final): 16/17 pass; `performance` gagal ketat — 4× CPU: chapter 58.6, iris 56.4, scrub maju 54.1 (11% lambat), scrub balik 52.5 (13%), tap temuan 59.4, Return 51.7 fps; gambar bukti 8 berkas 115,575 B.

### Fase 7A — CrossCheck inspection room (2026-09-16, Claude Code, Development)
Brief personal + tabel sumber copy DRAFT: `web/README.md` bagian Phase 7A.

#### `web/components/crosscheck-room.tsx`
- **Peran:** ruang inspeksi khusus CrossCheck di case file; dipasang `case-file.tsx` hanya untuk `id === 'crosscheck'` (empat case lain tetap `.signal-flow` sampai fasenya).
- **Ekspor utama:** `InspectionField` (`section.inspection-field[aria-labelledby=flow-heading][data-step]`, stage sticky, `ol.inspection-steps` 4 step approved + readout, `.inspection-detail` mobile, `svg.inspection-matrix[data-progress]`), `FindingSheet` (`#findings-heading`, `.finding-tab[data-finding][aria-pressed]`, `#finding-evidence[data-finding]`, `EvidenceStrip` `[data-hit]`, `.finding-proof[data-pair][data-view]` toggle, `.finding-repro`), `NextTeaser` (`.case-next-deck`).
- **Dipakai oleh:** `case-file.tsx`; tes `verify_crosscheck_room.py`, `verify_case.py`, `verify_cases.py`.
- **Bergantung pada:** `lib/crosscheck-run.ts`, `lib/crosscheck-room.ts`, GSAP ScrollTrigger (register sendiri: efek anak jalan sebelum shell pada direct URL), `use-reduced-motion`, next/image (`/images/crosscheck/*`).
- **State / efek samping:** SVG dirender sekali (path per layer; baris "kept" = grup per route); satu ScrollTrigger (start top top → end bottom bottom) menulis target, `gsap.ticker` meng-ease 0.2/frame lalu `draw(p)` menulis ±40 atribut. Fade memakai `fill-opacity`/`stroke-opacity` (bukan `opacity` grup); chip hanya `translate` (tanpa `scale`: glyph dirasterisasi ulang tiap frame); sel `crispEdges` (CSS) — fix fps Testing 7A. `BEATS` map 0–.12 / scan .12–.5 / sort .52–.76 / hand .78–.96; semua fungsi murni progress → scroll balik membalik, flick tidak mengantre. Reduced motion = `draw(1)` statis. Tes membaca chip lewat `style.fillOpacity`. `useWide` (≥1024) mengganti layout viewBox (label route + chip 6 kolom). Finding: WAAPI 220 ms, strip bukti CSS stagger 12 ms/sel; toggle before/expected mobile, desktop keduanya tampil.
- **Catatan:** jebakan: jangan set `style.transform` pada elemen SVG yang memakai atribut `transform` — CSS menimpanya. Gambar hidden (toggle) tetap lazy → tes hanya cek gambar terlihat. Baris "removed by rule" = penyederhanaan per baris route (caption jujur).

#### `web/lib/crosscheck-room.ts`
- **Peran:** copy 7A (approved gate 2026-09-16): `scanLanes`, `inspectionSteps` (judul/body approved Fase 5 + `readout` baru + `source`), `inspectionNote`, `findings` (CC-003, CC-001, CC-017, CC-015: title/where/steps/expected/actual/gambar/alt/caption/source), `findingsIntro`.
- **Dipakai oleh:** `crosscheck-room.tsx`, `app/page.tsx` (`scanLanes`).
- **Catatan:** setiap fakta punya `source` ke dossier atau gambar bukti; tabel lengkap README.

#### `web/lib/crosscheck-run.ts` (GENERATED)
- **Peran:** data run tercatat: `routes` (40), `columns` (27 = browser → size → role), `matrix` (baris '0/1'), `issues` (18: id/priority/source sweep|access|flow/row), `accessPages` 72, `violations` [page, role], `flows` (5), `evidenceCells` CC-017/CC-015.
- **Bergantung pada:** `scripts/build_crosscheck_run.py`; jangan edit tangan.

#### `web/scripts/build_crosscheck_run.py`
- **Peran:** generator data + crop; assert 1,080/422/877/40/216→3/5→1/18=3·14·1 sebelum menulis. Box crop diukur dari piksel border merah/hijau gambar V4.
- **Bergantung pada:** `/home/rayin/Projects/Testing/crosscheck/qa/out/*`, `assets/v4_before_after_{1,2,3}_en.png`, `qa/out/shots/flow_update_post_and_crm_owner_step5.png`; Pillow (venv CrossCheck).

#### `web/public/images/crosscheck/`
- `cc-003-actual.png` 1280×440, `cc-001-before/expected.png` 744×420, `cc-017-before.png` 383×824, `cc-017-expected.png` 619×824, `cc-015-before/expected.png` 383×824 (ukuran juga di `shotSize` komponen). Crop tanpa retouch.

#### `web/scripts/verify_crosscheck_room.py`
- **Peran:** tes fokus Development 7A (bukan paket gate). Viewport default 390/360/430/768/1440/1920 + edges (390).
- **Cek:** strip lane menyala 0 → >0 → 27 mengikuti orbit + `data-scan` melihat 0/1/2/agree, tidak menimpa tombol; iris `disc → hole → hidden` masuk, `hole → disc → hidden` kembali, pusat dalam viewport, scroll asal ±3 px, fokus heading; `data-leaders=live` + opacity leader; kartu hotspot dalam viewport; field progress 0/.3/.62/.9/1 → step 0..3 monoton, stage top 0, 18 chip opacity 1, mundur ke .3 → step 1 chip 0, flick 5 lompatan → progress akurat; empat temuan (hit 1/2/9/27, gambar termuat, toggle mobile / dua figur desktop, langkah ≥2); teaser SurgeLine; satu Canvas, 0 error/≥400/overflow. Edge: Back saat terbang → iris hidden; `ambient.glb` diblok → tanpa `data-leaders`, leader opacity 0, still tampil; reduced motion → step 3 + chip 1, iris hidden.
- **Jebakan:** screenshot DPR 2 makan ±300 ms → fase iris terlewat; screenshot diambil di dalam `iris_trace` saat radius melewati ambang.

#### Perubahan berkas lama (7A)
- `components/case-file.tsx`: import room; CrossCheck merender `InspectionField` + `FindingSheet` menggantikan section flow; `NextTeaser` (deck case berikut) hanya CrossCheck.
- `lib/cases.ts`: `apertureScreen` {x,y} (NaN sampai scene menulis; dibaca `lensCentre` shell); tipe `CaseFile.aperture?` (node lensa masuk/keluar); CrossCheck `draft: false` (gate 7A), `aperture: 'Lens2'`, tiga body hotspot ditulis ulang sebagai hasil inspeksi (approved gate 7A).
- `app/page.tsx`: chapter CrossCheck mengganti `orbit-hint` dengan `.scan-strip[role=img]` 3 × `.scan-lane[data-lane]` × 9 `<i style=--c>`.
- `components/observatory-shell.tsx`: `syncChapters` menulis `--instrument-<i>-orbit` (1 sudah lewat, orbit aktif, 0 belum). Iris modul-level (`setIris`, `irisTween`, `lensCentre` membaca `apertureScreen`, `irisCentre`): `openCase` menambah disc 0→jangkau (.5 s, mulai .32) bila `aperture`; `leaveCase('return')` hole jangkau→0 (.48 s); layout effect pathname selalu membuka iris yang sedang menutup (case: hole dari pusat beku; home: disc mengecil ke lensa chapter live; interupsi: uncover singkat). Reduced motion: tanpa iris. `.lens-iris` di dalam `.site-content` (z 3, di bawah header).
- `components/observatory-scene.tsx`: `showScan` → `.observatory[data-scan]`; per frame proyeksi node `aperture` instrumen terlihat → objek `apertureScreen` di `lib/cases.ts` (px, `size.left/top`). **Jangan** tulis ke CSS variable di `.observatory`: lensa berayun tiap frame → style recalc seluruh halaman (Testing 7A: 60 → ±34 fps di 4× CPU); `.case-inspection[data-leaders=live]` hanya saat `mix > .99` dan model case ada.
- `components/instrument-motion.ts`: `rigInstrument(..., onScan?)`; rig CrossCheck melapor lane '0'|'1'|'2'|'agree'|'idle' saat berubah (siklus 6.6 dtk sama).
- `app/globals.css`: blok "Phase 7A" sebelum reduced-motion: `.scan-strip/.scan-lane` (fill `clamp` dari `--instrument-0-orbit`), `.lens-iris` (mask radial disc/hole, grid inspeksi, ring + garis bidik), sel matriks `shape-rendering: crispEdges`, `.cells-pass`/`.cells-removed-grey` default `fill-opacity`, leader `opacity 0` tanpa `data-leaders=live`, `.inspection-*`, SVG matrix, `.finding-*`, `.evidence-*`, `.case-next-deck`; ≥1024: stage dua kolom, steps rail, finding desk grid, bingkai bidik `[data-case=crosscheck] .case-inspection::before/::after`.
- Rig (bukan situs): `verify_cases.py`, `case_files_evidence.py`, `case_crosscheck_evidence.py`, `full_observatory_evidence.py` membaca dossier dari `portfolio/` root (Q41; path sibling lama sudah tidak ada). `verify_mobile.py` mengulang `scrollTo` bawah di dalam `wait_for_function` sampai readout 100%; `verify_showpiece.py` menunggu scroll diam 400 ms sebelum mencatat origin (2 tempat). Keduanya gagal identik di HEAD `ac01ca4` sebelum 7A (ekor Lenis menimpa lompatan native).
- Performa (ukur 2026-09-16, 390×844 DPR 2, scrollTo tiap rAF 6 dtk): CPU 4× scrub matriks 243 frame vs pembanding scroll bagian lain 264 frame; CPU 1× 60 fps datar. `put()` di `draw` hanya menulis nilai yang berubah; "removed by rule" = crossfade dua layer (`removed` merah → `removed-grey` muted .32), bukan `color-mix` per frame (tidak mengubah angka ukur — biaya dominan = raster SVG + scroll).
- Tes: `verify_case.py` (draft label 1, cek inspection steps + 18 chip), `verify_cases.py` (CrossCheck `draft: True`, steps alih-alih `.signal-flow`), `verify_desktop.py` (lewati cek flow horizontal CrossCheck). Arsip bukti `case_files_evidence.py`, `desktop_evidence.py`, `case_crosscheck_evidence.py` masih mengharapkan `.signal-flow`/tanpa DRAFT untuk CrossCheck → gagal bila diulang (arsip gate lama).


### `web/app/work/[slug]/page.tsx`
- **Peran:** lima route statis `/work/<slug>` (generateStaticParams), template PLAN §7.
- **Ekspor utama:** `CasePage`, `generateStaticParams`, `dynamicParams = false` (slug lain 404 saat build).
- **Dipakai oleh:** Next App Router di dalam root shell yang persisten.
- **Bergantung pada:** `components/case-file.tsx`, `lib/cases.ts`. `params` = Promise (Next 16).
- **State / efek samping:** tidak ada server state; `key={slug}` me-remount template antar case (kartu reset).
- **Catatan:** direct URL tetap melewati entry gate; tidak membuat Canvas kedua. Menggantikan `work/crosscheck/page.tsx`.

### `web/components/case-file.tsx`
- **Peran:** template satu case: Brief, The instrument, How it works, Readings, Tools used, Demo video, Next instrument.
- **Ekspor utama:** `CaseFile({ id })`; `main[data-case]`, `#case-heading`, `#case-instrument`, `.hotspot-<i>` (posisi inline dari data),
  `data-hotspot-line=<component id>`, `data-home-target`, `data-case-target=<next slug>`, `.draft-label` bila `draft`.
- **Dipakai oleh:** route `[slug]`, shell navigasi (delegasi klik), scene proyeksi leader, verify_case / verify_cases.
- **Bergantung pada:** `lib/cases.ts`, `lib/instruments.ts` (nama/kategori), GSAP, Next Link; `/images/<slug>-fallback.png`,
  `/images/<slug>-demo-poster.jpg`, `/videos/<slug>-explainer.mp4`.
- **State / efek samping:** selected card; `inspect(next, pointer)` mengubah selection + WAAPI opacity/translate 180ms untuk pointer; animasi lama dibatalkan saat tap berikut/cleanup. `data-active` pada leader, `data-selected` pada kartu. IntersectionObserver count-up sekali per reading; cleanup tween/observer.
  Video native controls, muted, playsInline, preload none.
- **Catatan:** pengganti `crosscheck-case.tsx`; teks CrossCheck identik kecuali blok Next (kini "Open the next case file" → case SurgeLine, approved di gate Fase 5).
  Fase 6: wrapper `.case-title` + `.case-brief-copy` untuk brief desktop; `.case-inspection` berisi still/SVG/marker dengan koordinat lokal, terpisah dari heading/kartu. Mobile tetap satu stage.
  Next = case berikut urutan PLAN §5, BrandWall → CrossCheck. Link `onNavigate` preventDefault; modifier-click tetap link normal.

### `web/lib/cases.ts`
- **Peran:** sumber data lima case file + tipe transisi kamera.
- **Ekspor utama:** `caseFiles`, `caseIndex(id)`, tipe `CaseFile`, `CaseComponent` (`node`, `part?`, `marker`), `CaseReading`, `CaseView` (`mix`, `active`, `index`).
- **Dipakai oleh:** case-file, route, scene (anchor leader), shell (route ↔ index, chain).
- **Bergantung pada:** lima dossier CAPABILITY_* (kolom `source` per reading); provenance README.
- **State / efek samping:** readonly; `CaseView` runtime = ref shell.
- **Catatan:** Lima case approved di gate Fase 4–5; body hotspot CrossCheck 7A approved di gate 7A (`draft: false`) + `aperture: 'Lens2'`. CrossCheck Lens3/Lens2/Lens1, revisi 3. Anchor: SurgeLine `DishPivot1/2/3` part `signal`;
  DriftWatch `NeedlePivot` (origin), `driftwatchMount` + `ceramic` (kertas), `RollerPivot0` + `ceramic`; DueWatch `OrbitPivot0/1/2` part
  `ceramic`/`alarm`/`ceramic` (planet mengorbit → leader ikut); BrandWall `brandwallMount` + `ceramic` (kolimator), `PrismPivot` + `Prism`,
  `SpectrumPivot` + `Spectrum0`. Marker dipilih lewat screenshot 390×844 agar leader tak memotong bagian lain.

### `web/public/videos/<slug>-explainer.mp4`, `web/public/images/<slug>-demo-poster.jpg`
- **Peran:** demo English asli tiap project + poster sebelum playback.
- **Ekspor utama:** MP4 H.264 1920×1080, 0 audio streams: crosscheck 126.867 s / 5,002,746 B; surgeline 115.233 s / 1,812,889 B;
  driftwatch 118.167 s / 2,227,965 B; duewatch 102.5 s / 2,221,217 B; brandwall 124.967 s / 10,457,918 B. Poster 960×540 JPEG, frame 1 s
  (DueWatch 8 s: frame 1 s memuat notice full-screen browser).
- **Dipakai oleh:** video di tiap case.
- **Bergantung pada:** salinan byte-identik (`cmp`) `/home/rayin/Projects/Testing/<project>/assets/explainer.mp4`; poster via ffmpeg.
- **State / efek samping:** browser download hanya setelah play; bukan bukti baru.
- **Catatan:** caption English dibakar. DueWatch memuat caption "Seven days in a row…" atas tanggal simulasi (dossier §7 temuan 4);
  case menyebutnya di bawah video — pemilik memilih opsi 1 di gate Fase 5 (terima dengan catatan).

### `web/scripts/verify_cases.py`
- **Peran:** tes fokus Development Fase 5, bukan paket gate Testing.
- **Ekspor utama:** async `run()`, `inspect(page, case, …)`, `trace_numbers()`; `CASES` (cermin sengaja dari `lib/cases.ts`).
- **Dipakai oleh:** perintah §2 (jalankan dari `web/scripts/`, impor `verify_case.URL/enter/idle/scroll_to`).
- **Bergantung pada:** server :8767, Chromium ANGLE gl-egl, dossier portfolio.
- **State / efek samping:** tulis PNG (`<slug>-brief|hotspot-1..3|readings-<vp>`, `chain-sweep-390x844`, `return-surgeline-<vp>`,
  `fallback-duewatch-390x844`) + `verification.json` ke `assets/renders/case-files/dev/`.
- **Catatan:** 3 viewport; open-from-chapter + Return (scroll/fokus) ×5, rantai penuh + wrap, Back/Forward, Return pasca-rantai → chapter case,
  5 direct URL, `/work/unknown` 404, fallback DueWatch (model SurgeLine diblok). Reading multi-digit wajib ada verbatim di dossier.

### `assets/renders/case-files/dev/`
- **Peran:** screenshot + JSON Development Fase 5; terpisah dari paket gate `case-files/evidence/` (tahap Testing).
- **Ekspor utama:** lihat verify_cases; `verification.json` status running/passed/failed.
- **Dipakai oleh:** review developer, handoff Testing.
- **Bergantung pada:** verify_cases.py.
- **State / efek samping:** generated; jangan edit tangan.
- **Catatan:** emulasi Chromium; bukan klaim fps/HP fisik.

### `web/scripts/case_files_evidence.py`
- **Peran:** generator paket bukti Testing Fase 5 untuk gate pemilik.
- **Ekspor utama:** async `run()`, `main_flow`, `fallback_check`, `viewports_check`, `make_contact_sheet`; `ITEMS` (17), `CASES` (5).
- **Dipakai oleh:** agen Testing Antigravity / Claude Code; perintah §2.
- **Bergantung pada:** server :8767, Chromium GPU ANGLE gl-egl, ffmpeg, Pillow, dossier portfolio `CAPABILITY_*.md`.
- **State / efek samping:** menulis PNG per item, MP4 walkthrough rantai penuh (`case-files-walkthrough.mp4`), `contact-sheet.jpg` (24 frame), `viewports/viewports-sheet.jpg`, dan `evidence.json` (17/17 pass) ke `assets/renders/case-files/evidence/`.
- **Catatan:** merekam alur utama 390×844: gate → CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall → CrossCheck (wrap) → Return → history → SurgeLine return; fallback model diblok; viewports 360×740 dan 430×932; verifikasi semua angka di dossier.

### `assets/renders/case-files/evidence/`
- **Peran:** paket bukti gate Testing Fase 5 untuk penilaian pemilik.
- **Ekspor utama:** `case-files-walkthrough.mp4` (H.264 390×844, 130.4 s), `contact-sheet.jpg` (2340×3376, 24 frame), `viewports/viewports-sheet.jpg` (1170×2532), `evidence.json` (status `passed`, 17/17 pass), screenshot per item (brief, hotspot, readings, flight, return, fallback).
- **Dipakai oleh:** pemilik saat evaluasi gate Fase 5; PROGRESS.
- **Bergantung pada:** `case_files_evidence.py`.
- **State / efek samping:** generated; jangan diedit tangan.
- **Catatan:** emulasi Chromium GPU; bukan klaim fps/HP fisik (diuji di Fase 8).

### `web/scripts/desktop_evidence.py`
- **Peran:** generator paket bukti Testing Fase 6 (gate pemilik), bukan tes Development.
- **Ekspor utama:** async `run()`, `main_flow`, `desktop_size`, `resize`, `fallback`, `phones`, `copy_check`, `sheets`, `centroid` (pusat piksel terang screenshot Canvas-saja → objek 3D di kanan); `ITEMS` (21), `FINDINGS`, `REGRESSIONS`.
- **Dipakai oleh:** agen Testing; jalankan dari `web/scripts/` (impor `case_files_evidence.CASES/flight/glide/tile…` + `verify_case.enter/idle`).
- **Bergantung pada:** server :8767, Chromium GPU ANGLE gl-egl, NumPy + Pillow + ffmpeg/ffprobe (venv CrossCheck); JSON status empat suite regresi dev (`REGRESSIONS`).
- **State / efek samping:** hapus lalu tulis ulang `assets/renders/desktop/evidence/`.
- **Catatan:** alur utama 1440×900 DPR 1 direkam (gate → hero → nav Work → 5 chapter + orbit → Skills + link → About → Contact → flight in → rantai 5 case + wrap → Back/Forward → nav About dari case → Return); lalu 1366×768 + 1920×1080, resize 390→768→1024→1440→1920→390 (Canvas sama), model BrandWall diblok (still DriftWatch), tiga HP DPR 2, teks homepage/case identik HP vs desktop. `FINDINGS.caseBrief` = penilaian visual tester (brief desktop tanpa instrumen di layar pertama).
  Jebakan: HTML prerender sudah memuat nilai akhir readings; cek `[data-count]` = nilai akhir langsung lolos sebelum observer me-reset + count-up → tunggu ±1.8 dtk setelah scroll dulu. Fallback Return dibandingkan dengan scrollY asal (bukan top section).

### `assets/renders/desktop/evidence/`
- **Peran:** paket bukti gate Fase 6 untuk penilaian pemilik.
- **Ekspor utama:** `desktop-walkthrough.mp4` (H.264 1440×900), `contact-sheet.jpg` (24 frame berlabel), `01-gate` … `16-fallback.png` (per item; `07-flight-in`/`15-return-flight`/`16-fallback` komposit), `viewports/desktop-sheet.jpg` + `resize-sheet.jpg`, `phones/phones-sheet.jpg`, `evidence.json`.
- **Dipakai oleh:** pemilik saat gate; PROGRESS.
- **Bergantung pada:** `desktop_evidence.py`.
- **State / efek samping:** generated; jangan edit tangan.
- **Catatan:** emulasi Chromium GPU; bukan klaim fps/HP fisik (Fase 7/8).

### `web/scripts/verify_audio.mjs`
- **Peran:** tes lifecycle deterministik kelas audio produksi, dengan AudioContext/clock terkendali.
- **Ekspor utama:** script Node; transpile `lib/ambient.ts` in-memory lewat TypeScript lokal, lalu 9 assertion groups.
- **Dipakai oleh:** Development / Testing Fase 7; tidak memerlukan server.
- **Bergantung pada:** Node built-ins, TypeScript dari `web/node_modules`.
- **State / efek samping:** tulis `audio-verification.json` hanya sesudah semua assert lulus; gagal → exit 1.
- **Catatan:** membuktikan silent entry, resume-vs-mute/dispose race, rate limit/batas voice, penggantian sweep, hidden tab, disconnect dan close; browser suite menguji sinyal audio nyata.

### `web/scripts/verify_showpiece.py`
- **Peran:** verifikasi fokus Fase 7 Development pada 390×844 → 360×740 → 430×932.
- **Ekspor utama:** `run`, `phone`, `edges`, `AUDIO` (instrumentasi AudioContext asli), `enter`, `idle`, `position`; `OBSERVATORY_URL` override.
- **Dipakai oleh:** Development; tidak menghasilkan paket gate.
- **Bergantung pada:** venv CrossCheck Python Playwright; Chromium GPU ANGLE gl-egl; preview produksi :8767.
- **State / efek samping:** PNG dan `verification.json` running/passed/failed ke `showpiece/dev/`.
- **Catatan:** monotonic loader, silent entry tanpa AudioContext, RMS On/Off nyata, lima frekuensi terjadwal (bukan AudioParam.value awal quantum), hotspot/card/leader + press scale, bounded/disconnected voices, Next/Return, Canvas sama, nol overflow/error/HTTP ≥400. Edge: default welcome, visibility simulasi + master nyata, scroll/focus return, history interrupt, model sengaja ditahan sampai still-view escape 15s, AudioContext sengaja gagal. Bukan uji FPS/4G atau speaker HP.

### `web/scripts/showpiece_evidence.py`
- **Peran:** generator paket bukti Testing Fase 7 (gate pemilik), bukan tes Development.
- **Ekspor utama:** async `run()`, `main_flow`, `perf_gate`, `enter_early`, `perf_fps`, `dpr_cap`, `assets_check`, `hover_check`, `phones_check`, `edges_check`, `mux`, `sheets`; `ITEMS` (14), `FINDINGS`, `REGRESSIONS`, `SLOW_4G` (preset DevTools), `LIGHT_4G` (profil Fase 1), `TAP`/`STOP_REC`, `TIMING`, `FRAMES`, `MODEL_RESOURCES`/`INSTRUMENTS_DONE` (timing resource GLB).
- **Dipakai oleh:** agen Testing; jalankan dari `web/scripts/` (impor `verify_showpiece` sebagai `vs` + `case_files_evidence.CASES/flight/overflow/tile/top`).
- **Bergantung pada:** server :8767, Chromium GPU ANGLE, matplotlib + Pillow + ffmpeg/ffprobe (venv CrossCheck); JSON status 6 suite regresi.
- **State / efek samping:** hapus lalu tulis ulang `assets/renders/showpiece/evidence/`; mengalihkan `vs.OUT` ke `evidence/edges` dan `evidence/phones` agar screenshot `vs.edges`/`vs.phone` masuk paket.
- **Catatan:** 2026-09-16 (Testing ulang): item `enterEarly` = dua context slow 4G + CPU 4×. (1) homepage: Enter diklik begitu aktif lalu langsung scroll ke `#crosscheck` → sebelum Enter hanya `dome.glb`+`ambient.glb` terunduh, lima GLB instrumen `startTime` ≥ waktu Enter aktif, copy chapter kebaca tanpa model, lalu model muncul (diff piksel `difference()`); (2) direct `/work/crosscheck`: heading kebaca, `[data-hotspot-line] x2` `50%` → nilai piksel saat model mendarat. Bukti `15a`–`15d` + strip `15-enter-early.png`. Jebakan: `x2` default `50%` (string persen) — bandingkan apa adanya, jangan `float()` sebelum model ada.
  2026-09-16 (Development opsi B): teks `perfGate` detail + `FINDINGS.perfGate` kini menyebut Enter menunggu kubah + Saturnus + font (angka lama 12.2 s / 1.37 MB sebagai pembanding); logika ukur tidak diubah. Byte `transferredBytes` = resource selesai sampai Enter aktif.
  audio MP4 = output Web Audio situs sendiri (gain → destination disadap ke `MediaStreamDestination` + `MediaRecorder`), dihentikan sebelum reload lalu di-mux dengan `adelay` = selisih mulai rekaman vs mulai video. Scroll HP = touch swipe CDP `Input.dispatchTouchEvent` (`synthesizeScrollGesture` tidak menggulir halaman ini). FPS = interval rAF (beban main thread); GPU host tidak di-throttle → bukan klaim GPU HP. Jebakan: Lenis (`syncTouch`, nav header/menu) masih mengayun setelah cek jarak < 3 px; `scrollTo` native saat itu ditimpa → `settle_to` mengulang sampai mendarat (jangan menunggu kelas `lenis-scrolling`, bisa bertahan). Setelah rantai, Return ke `#<slug>` memfokus `h2` chapter (bukan tombol Open case file; itu hanya bila kembali ke posisi scroll tersimpan).

### `assets/renders/showpiece/dev/`
- **Peran:** foto dan hasil uji Development Fase 7; terpisah dari paket Testing.
- **Ekspor utama:** `gate-`, `menu-`, `flight-`, `<slug>-inspection-`, `return-` × `390x844|360x740|430x932`; `loader-pending-390x844.png`, `loader-fallback-390x844.png`, `audio-unavailable-390x844.png`; `verification.json`, `audio-verification.json`, `env-check.md`.
- **Dipakai oleh:** developer review, handoff Testing.
- **Bergantung pada:** verify_showpiece.py, verify_audio.mjs, real engine launch check.
- **State / efek samping:** PNG/JSON generated dan dapat ditimpa saat rerun; jangan edit tangan.
- **Catatan:** paket gate Testing ada di `showpiece/evidence/` (lihat entri berikut); `verification.json` di sini ditulis ulang tiap rerun `verify_showpiece`.

### `assets/renders/showpiece/evidence/`
- **Peran:** paket bukti gate Fase 7 untuk penilaian pemilik.
- **Ekspor utama:** `showpiece-walkthrough.mp4` (H.264 + AAC, 390×844, ±112 dtk, audio asli situs mulai ±13.4 dtk saat Enter); `contact-sheet.jpg` (24 frame);
  `01-loader.png`, `05-flight-in.png`, `11-perf-gate.png`, `12-perf-fps.png` (grafik frame 4×/6×), `13-micro.png`, `14-sound-control.png`,
  `15-enter-early.png` (strip `15a` chapter tanpa model → `15b` instrumen tiba → `15c` case dini → `15d` leader tersambung) + PNG sumber `01a`…`11b`, `15a`…`15d`;
  `phones/` (`vs.phone` 360×740/430×932 + `phones-sheet.jpg`), `edges/` (loader stall/fallback, audio unavailable); `evidence.json` (14 item + `measurements`).
- **Dipakai oleh:** pemilik saat gate; PROGRESS.
- **Bergantung pada:** `showpiece_evidence.py`.
- **State / efek samping:** generated; jangan edit tangan.
- **Catatan:** hasil 2026-09-16 (Testing ulang, 14/14 pass): gate FCP 1,408 ms, Enter aktif 6,394 ms, transfer sebelum Enter 787,063 B (JS 507 KB, 3D 139 KB, Draco 64 KB, font 60 KB, HTML/CSS 17 KB); instrumen selesai +3.0 s; fps 4× 56–60; GLB 737,440 B; canvas 1.5× di DPR 2/3; MP4 105.9 s H.264+AAC. Arsip 2026-09-15: Enter aktif 12.2 s, transfer 1,370,869 B. Status `verify_desktop` di JSON = run 1440×900 + 1920×1080 (390×844/1366×768 lolos di run terpisah hari itu; JSON hanya memuat run terakhir).

### `web/scripts/verify_desktop.py`
- **Peran:** verifikasi Development Fase 6, HP 390×844 dahulu lalu 1366×768, 1440×900, 1920×1080.
- **Ekspor utama:** `main`, `viewport`, `check_case`, `position`, `capture`, `fallback`; `--sizes` untuk rerun fokus, `--breakpoints-only` untuk resize, `--hotspots-only` untuk bukti marker stabil; `OBSERVATORY_URL` opsional.
- **Dipakai oleh:** Codex Development; Testing dapat memakai ulang, tetapi paket gate dibuat tahap Testing.
- **Bergantung pada:** Python Playwright dari venv CrossCheck, Chromium ANGLE GPU, preview produksi.
- **State / efek samping:** tulis PNG dan `verification.json` ke `assets/renders/desktop/dev/`; failed check menghasilkan exit 1. Capture hotspot/fallback/resize menunggu warna aktif selesai bertransisi; data hasil terpisah dari suite penuh.
- **Catatan:** Testing Fase 7: `position()` mengulang `scrollTo` (≤12 × 300 ms) sampai mendarat, lalu assert — dulu 1440×900 timeout konsisten setelah nav Contact (ekor animasi Lenis menimpa lompatan; tes saja, bukan bug situs). Menunggu kelas `lenis-scrolling` hilang tidak dipakai: kelas itu bisa bertahan setelah scroll native.
  Verifikasi rail tidak tumpang tindih, header nav, 3 hotspot/case + endpoint nyata, alur horizontal, readings, rantai Next penuh/wrap, history, case→About, satu Canvas, nol overflow/error/HTTP ≥400 alur normal; fallback diblok sengaja. Resize 768→1024→1440→390 memeriksa pane, proyeksi, dan identitas Canvas.

### `assets/renders/desktop/dev/`
- **Peran:** baseline dan bukti verifikasi Development Fase 6; bukan paket gate.
- **Ekspor utama:** `before-{hero,chapter}-390x844.png` dan `before-{hero,chapter}-1440x900.png`; screenshot final `gate-`, `hero-`, `chapter-<slug>-`, `skills-`, `about-`, `contact-`, `<slug>-brief/hotspot-1/2/3/flow/readings/demo-`, `case-to-about-` per viewport; `fallback-*`, `resize-inspection-*`, `verification.json`, `breakpoint-verification.json`, `hotspot-verification.json`, `env-check.md`.
- **Dipakai oleh:** review developer, handoff Testing.
- **Bergantung pada:** `verify_desktop.py`; baseline/smoke via Playwright sementara (`/tmp/observatory_baseline.py`, `/tmp/observatory_review.py`). `review-{hero,crosscheck,brief,inspection}-1440x900.png` adalah smoke awal, bukan hasil final. Dua smoke salah posisi (`review-about-1440x900.png`, `review-contact-1440x900.png`) dihapus; bukti section yang benar bernama `about-*`/`contact-*`.
- **State / efek samping:** hasil generated ditulis ulang saat rerun; jangan edit manual.
- **Catatan:** Chromium emulasi; paket video/foto gate akan ditaruh Testing di `assets/renders/desktop/evidence/`.
  2026-09-16: suite dijalankan dua run (`--sizes 390x844,1366x768` lalu `1440x900,1920x1080`, masing-masing <10 menit); `verification.json` hanya memuat ukuran run terakhir.

### `web/scripts/verify_case.py`
- **Peran:** tes fokus Development Fase 4, bukan paket gate Testing.
- **Ekspor utama:** `run`, `enter`, `open_case`, `home`, `scroll_to`; `OBSERVATORY_URL` opsional.
- **Dipakai oleh:** perintah §2; venv Playwright CrossCheck yang sudah ada.
- **Bergantung pada:** Chromium headless ANGLE gl-egl, server produksi lokal.
- **State / efek samping:** menulis screenshot + verification.json; status running/passed/failed.
- **Catatan:** HP 390×844 → 360×740 → 430×932; Canvas identity, route/scroll/focus, 3 cards,
  projected endpoints, warna marker aktif selesai sebelum screenshot, flight fade/scroll lock, flow, reading count-up, lazy video/playback, Back/Forward, Skills,
  Next → `/work/surgeline` lalu Return → chapter SurgeLine (Fase 5), direct/reload,
  model diblok → fallback + return tanpa history; `--fallback-only` menguji ulang cabang fallback dan notice/heading tanpa mengulang alur normal. Nol error/HTTP ≥400 pada alur normal.

### `web/scripts/revision_sky_lines_evidence.py`
- **Peran:** bukti revisi 3 pasca gate Fase 4 (bintang jarang + leader line CrossCheck).
- **Ekspor utama:** async `run()`, `gap()` (jarak titik ke segmen), `CLEARANCE` = 30 px CSS.
- **Dipakai oleh:** agen Testing; jalankan dari `web/scripts/` (impor `verify_case`).
- **Bergantung pada:** `verify_case.URL/enter/scroll_to`; server :8767; Pillow + font DejaVu.
- **State / efek samping:** tulis PNG, `00-contact-sheet.jpg`, `evidence.json` ke `assets/renders/revision-sky-lines/evidence/`.
- **Catatan:** 3 viewport DPR 2; tiap leader harus berjarak ≥30px dari dua lens lain + nol console error.

### `web/scripts/case_crosscheck_evidence.py`
- **Peran:** paket bukti tahap Testing Fase 4 (gate pemilik), bukan tes Development.
- **Ekspor utama:** async `run()`, `main_flow`, `fallback`, `viewports`, `flight`, `glide`; `ITEMS` (14), `FINDINGS`, `CARDS`, `READINGS`, `SECTIONS`, `FORBIDDEN`.
- **Dipakai oleh:** agen Testing; venv CrossCheck (Playwright + Pillow) + ffmpeg.
- **Bergantung pada:** `verify_case.enter/idle`; server :8767; dossier `portfolio/CAPABILITY_CROSSCHECK.md` (angka + tools §5); font DejaVu untuk label.
- **State / efek samping:** hapus lalu tulis ulang `assets/renders/case-crosscheck/evidence/`.
- **Catatan:** Chromium GPU ANGLE, DPR 2. Flow utama 390×844 direkam: flight in (frame start/mid/end), 3 hotspot, flow, count-up
  (MutationObserver), tools, video lazy + seek 0:48, Return flight, Back/Forward, Tool→Skills, Next→SurgeLine; lalu fallback model
  diblok dan 360×740/430×932. `glide` = wheel nyata lalu posisi pas, target di-clamp ke scroll maksimum (dulu loop 30 dtk).
  `FINDINGS.flightIn` = penilaian visual tester, diterima pemilik di gate. Arsip gate Fase 4: cek `copy` mengharapkan label DRAFT, jadi gagal bila dijalankan ulang sekarang. Screenshot saat WebGL sibuk memberi kilatan frame kecil di MP4 (artefak rekaman).

### `assets/renders/case-crosscheck/evidence/`
- **Peran:** paket bukti gate Fase 4.
- **Ekspor utama:** `01-crosscheck-chapter` … `16-fallback.png` (`02-flight-in`/`05-hotspots`/`11-return-flight` komposit + frame `02a–c`, `11a–c`),
  `case-crosscheck-walkthrough.mp4` (H.264 390×844, ±62 dtk), `contact-sheet.jpg` (17 frame berlabel), `viewports/` (9 PNG + sheet), `evidence.json` 14/14.
- **Dipakai oleh:** pemilik saat gate; PROGRESS.
- **Bergantung pada:** `case_crosscheck_evidence.py`.
- **State / efek samping:** generated; jangan edit tangan.
- **Catatan:** emulasi Chromium; bukan klaim fps/HP fisik.

### `assets/renders/case-crosscheck/dev/`
- **Peran:** screenshot dan hasil verifikasi Development Fase 4; terpisah dari paket gate.
- **Ekspor utama:** `brief-`, `flight-`, `hotspot-1/2/3-`, `flow-`, `readings-`, `demo-`, `return-` per viewport;
  `fallback-390x844.png`, `verification.json`, `fallback-verification.json`, `env-check.md`; `instrument-390x844.png` arsip smoke awal.
- **Dipakai oleh:** review developer dan handoff ke Claude Code / Antigravity Testing.
- **Bergantung pada:** verify_case.py; smoke awal; verify_engines.py (3 launch sehat).
- **State / efek samping:** output generated, jangan edit manual hasil tes.
- **Catatan:** bukan gate pemilik; site cross-browser/FPS/HP fisik belum diklaim.

### `web/app/layout.tsx`
- **Peran:** root layout App Router; mempertahankan shell/Canvas di luar halaman.
- **Ekspor utama:** `RootLayout`, `metadata`, `viewport`; `HERO_ASSETS` (dome/ambient GLB + wrapper/wasm Draco).
- **Dipakai oleh:** Next.js untuk semua route.
- **Bergantung pada:** `ObservatoryShell`, `globals.css`, CSS Lenis, `preload` react-dom.
- **State / efek samping:** tidak ada server state; metadata preview noindex, English `lang`. `preload(href, {as:'fetch', crossOrigin:'anonymous'})` → `<link rel=preload>` di head; cocok dengan request FileLoader three (cors + same-origin credentials) sehingga dipakai ulang (waterfall: satu request per berkas). Ganti path model/decoder → ubah daftar ini juga.
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
  `target=_blank rel=noopener noreferrer`. Skill `projects` kosong → tanpa div link. Fase 5: kelima CTA `[data-open-case]` membuka route case (tanpa `aria-haspopup`).
  Fase 6: portrait `sizes` memasok gambar hingga 440px desktop; urutan DOM/copy sama.
  BrandWall: `orbit-hint` diganti `#observer-readout[data-observed]` (label revisi, approved pemilik 2026-09-15).

### `web/app/globals.css`
- **Peran:** token FINAL §8, font lokal, komposisi HP, lima chapter, gate/menu, Skills/About/Contact, komposisi desktop mulai 1024px.
- **Ekspor utama:** variables `--journey`, `--hero-journey`, `--chapter-reveal`, `--copy-opacity`,
  `--instrument-0-offset` … `--instrument-4-offset`; `.instrument-*`, `.skill-*`, `.portrait-scan`,
  `.scan-line`, `.text-section`, `.contact-links`, `.email-cta`.
- **Dipakai oleh:** layout, page, shell.
- **Bergantung pada:** tiga TTF, fallback PNG lokal (image paths disuplai shell), portrait.
- **State / efek samping:** transform/opacity, highlight skill target, sticky stages, fixed readout.
  `data-chapter` selain dome menyembunyikan CTA hero; outro mempertahankan notice still view.
- **Catatan:** 431–1023px mempertahankan komposisi HP 430px; mulai 1024px komposisi desktop penuh (Fase 6). Accordion native tetap keyboard-usable.
  `.fallback-notice` `margin:0` (default `<p>` 9px dulu menimpa copy chapter); di chapter `top:82px`.
  Fase 4 menambah `.case-*`, `.instrument-hotspot`, `.component-card`, `.signal-flow` dan `.draft-label`; kartu aman di atas readout; fallback case memberi jarak label/heading dari notice fixed.
  Fase 5: posisi `.hotspot-<i>` inline dari data (aturan `.hotspot-0..2` dihapus); `.case-instrument-still` tanpa url (gambar inline per slug);
  `.contact-dialog` dihapus bersama dialog preview.
  Fase 6: `--page-gutter`, breakpoint 1024px; hero/chapter rail kiri, gate dua kolom, Skills/About/Contact grid; case brief dua kolom, `.case-inspection` kanan, kartu kiri, flow horizontal, readings dua kolom dan tools tiga kolom. Fallback mengikuti area objek.
  `@font-face` memuat WOFF2 subset (Fase 7 Enter lebih cepat); TTF approved tetap sebagai sumber.
  Fase 7: dial SVG progres dan beacon loader; status ready hijau / fallback amber; press memakai `scale` terpisah (transform posisi tetap), hover arrow hanya pointer fine; border/leader kartu aktif, menu entrance singkat.
  Testing Fase 6: `#skills` + `.about-section` `grid-template-rows: auto auto auto 1fr` — accordion/portrait yang span semua baris dulu meregangkan baris teks (paragraf About berjarak ±115px).
  `.email-cta` sekarang `<a>`; `.contact-links a` baris 58px, nilai mono amber.
  Revisi langit: `.scene-layer` gradient (fallback bila WebGL gagal), overlay tinggal fade bawah ke ink;
  header gradient hitam transparan; gate gradient + bintang CSS `::before`; `#observer-readout` `.when-on/.when-off`.

### `web/components/observatory-shell.tsx`
- **Peran:** client shell persisten: loading, entry/audio, menu/dialog, scroll dan chapter state.
- **Ekspor utama:** `ObservatoryShell`; `scrollFromMenu`, `returnToDome`, `goToWork`, `openContact`, `openCase(index)`,
  `chainCase(index)`, `leaveCase(target)`; `caseOf(path)`; `measure`/`syncChapters` di efek GSAP.
- **Dipakai oleh:** root layout.
- **Bergantung pada:** Scene import statis, instruments, drei useProgress, GSAP/ScrollTrigger, Lenis, audio.
- **State / efek samping:** satu ticker Lenis; main trigger menulis readout dan chapter ref
  (`index`, `transition`, `reveal`, `orbit`, `outro`) dari bounds section. `planetProgress` terpisah = scrollY / rentang scroll homepage (diukur ulang saat resize); tidak reset saat chapter berganti. Hero trigger terpisah;
  dua trigger portrait untuk clip + scan-line. ResizeObserver main merefresh bounds saat accordion
  berubah. Menu menghentikan Lenis; menu scroll memulai Lenis sebelum scrollTo, fokus heading
  saat selesai. Skill links menambah `.skill-highlight`. Delegasi klik: `[data-home-target]` → leaveCase,
  `[data-case-target]` → chainCase, `[data-open-case]` → openCase (dialog preview dihapus Fase 5).
- **Catatan:** Fase 7: subscribe progress drei dengan high-water mark antar batch; Enter menunggu hero (kubah + Saturnus render frame ke-2) + font settle, tanpa minimum loading delay. `ready` diteruskan ke Scene sebagai `loadInstruments` (lima GLB baru diminta sesudahnya; opsi B pemilik 2026-09-16). Scene diimpor statis (dulu `dynamic ssr:false`) supaya chunk three ikut unduhan JS pertama, bukan sesudah hidrasi. Dial `data-ready` / `data-fallback`; error → lima still view berlabel. Audio gesture entry/welcome, hotspot/close/menu/summary click, fly-in/out/Next sweep. Satu `flight` timeline mencakup departure + sweep; dibatalkan saat pathname berubah/unmount (Back saat terbang tidak boleh push route lama).
  Contact sekarang section, bukan dialog placeholder Fase 1–2. Fase 4 memisahkan lifecycle Lenis root dari trigger per pathname; homeScroll/homeChapter/homeTarget, `CaseView` mix, `data-route` / `data-flight`, root `pageContent` fade + inert. Focus dipulihkan sesudah inert dilepas. Cleanup trigger/ticker/observer/audio.
  Fase 5: `isCase` = `/work/<slug>` dikenal; layout effect set `caseView.index` + chapter case. `chainCase`: mix 1→0 (mundur), chapter
  `{index: next, from: prev, transition 0→1}` (sapuan), lalu push → arrival terbang masuk; homeScroll/homeChapter di-null supaya Return → `#<slug>` case aktif.
  Pulang dari case mana pun: tujuan default `#<slug>` asal, fokus ke `[data-open-case=<slug>]` bila kembali ke posisi scroll.
  Fase 6: `.desktop-navigation` Work/About/Contact memakai handler scroll/leaveCase yang sama; inert saat flight. Menu tetap untuk <1024px.
  Lenis start() dapat membatalkan scrollTo bila dipanggil setelah scroll dimulai; urutan dipertahankan.
  Guard `live()` (Testing Fase 4): ResizeObserver/scroll homepage lama bisa memicu refresh/update setelah DOM case menggantikan
  homepage tapi sebelum cleanup React → dulu TypeError `#skills` null; kini onRefresh/onUpdate diabaikan bila section homepage terlepas.

### `web/components/observatory-scene.tsx`
- **Peran:** satu Canvas R3F, kubah + lima instrumen prosedural, satu GLB (Saturnus), kamera orbit + transisi masuk/keluar lima group instrumen.
- **Ekspor utama:** `ObservatoryScene`, `World`, `Instruments`, `SceneBoundary`; props memakai `ChapterState` + `loadInstruments`.
- **Dipakai oleh:** shell (import statis; server hanya me-render container Canvas, modul aman SSR).
- **Bergantung pada:** R3F/drei/three, instruments.ts, `instrument-models.ts`, `ambient.glb` (satu-satunya GLB
  yang masih diunduh), decoder lokal. Node kontrak: `OpticsPivot`, `FocusPivot0..2`, `Lens1..Lens3`,
  `Lens1Glow..Lens3Glow`; `DishPivot0..3`; `NeedlePivot`, `RollerPivot0..1`; `OrbitPivot0..2`,
  `PlanetPivot0..2`; `PrismPivot`, `SpectrumPivot`; plus grup mount `<id>Mount` yang dipakai `cases.ts`.
- **State / efek samping:** clone material + disposal; useFrame membaca ref, tidak state React scroll.
  Aktif dan pendahulunya terlihat saat transisi; kamera interpolasi orbit. Idle per instrumen di
  `instrument-motion.ts` (`rig.update` hanya saat group terlihat). Klik di chapter BrandWall (bukan
  tombol/link/dialog; hanya `#brandwall .instrument-stage` / `.case-inspection`, sudah entered, flight idle) → `rig.observe()` + prop `onInstrumentTap(4)`; status detektor → `#observer-readout[data-observed]`.
  `pointScale` = DPR tiap frame. Satu environment lokal, DPR 1–1.5. Material instrumen tidak lagi di-clamp
  (dulu `roughness>=.5`, `metalness<=.55` untuk menjinakkan ekspor Blender); nilai ditulis langsung di model.
- **Catatan:** Muat bertahap (Fase 7, opsi B): `World` membangun kubah lewat `buildObservatory()` dan memuat `ambient.glb` → frame ke-2 `onReady`. `<Instruments>` di `<Suspense>` sendiri, di-mount hanya bila `loadInstruments`; ia membangun lima instrumen lewat `buildInstrument()`, mengisi ref `views` lewat `useLayoutEffect` (kosong = belum ada model), memiliki handler tap BrandWall, dan me-render group `visible={false}` sampai frame loop `World` menempatkannya. Frame loop + leader aman saat `views.current` kosong (chapter/case sementara tanpa model, termasuk direct `/work/<slug>`). Instrumen kini prosedural, jadi satu-satunya model yang masih bisa gagal memuat adalah `ambient.glb`;
  kegagalannya naik ke `SceneBoundary` → still view + notice seperti biasa (skrip verifikasi memblokir model itu).
  langit = `<Sky>` (titik bintang lama dihapus); rig Saturnus diserahkan ke `PlanetaryJourney`, hanya tampil pada urutan keenam. `World.useFrame` prioritas -1 memperbarui kamera sebelum posisi planet (prioritas 0), mencegah selisih kamera satu frame. Kubah baru bergerak ke kiri saat hero keluar.
  SceneBoundary gagal satu model → still view menyeluruh; semua chapter tetap dapat dibaca. `CaseView` mix menginterpolasi sudut, jarak, zoom ortografis; model `caseView.index` mengikuti bounds `#case-instrument` (skala case = min(w·.62, h·.33)/fit, fit 4.4 CrossCheck / 3.5 lain). Canvas tetap root.
  Fase 6: breakpoint 1024px sama dengan CSS. Kamera menempatkan instrumen di kanan dan membatasi skala terhadap tinggi/lebar; dome/Saturnus ikut dikomposisi. Case mengikuti bounds `.case-inspection`; x2 leader dikurangi posisi pane relatif Canvas (penting saat Canvas HP terpusat di tablet).
  Fase 5: `anchor()` = origin node, atau pusat bounding sphere child mesh yang nama materialnya memuat `part`, → proyeksi ke SVG `[data-hotspot-line=<id>]`
  tiap frame (planet DueWatch bergerak → leader ikut). Outgoing = `chapter.from ?? index-1` supaya sapuan rantai (termasuk BrandWall → CrossCheck) benar.

### Revisi observatorium + scroll (2026-09-16)
- `observatory-model.ts`: bangunan prosedural; panel, rel, balkon, jendela, tangga, teleskop/finder.
  Geometri statis digabung per material/pivot: 20 mesh, 45.132 segitiga. Dispose dimiliki rig.
- `planetary-journey.tsx`: delapan planet (Merkurius → Neptunus), satu group terlihat tiap tahap pada desktop dan HP. Membaca progres homepage tunggal; damping tanpa overshoot, keluar kanan-atas sebelum planet berikut masuk kanan-bawah. Orbit elips idle hanya memakai waktu, terpisah dari scroll. Quaternion mengikuti kamera pada frame yang sama; shader/material opacity untuk handoff, rig Saturnus lama digunakan ulang. Reduced motion menonaktifkan perpindahan/idle, pilihan planet tetap mengikuti scroll. Semua planet disembunyikan pada case file.
- `use-reduced-motion.ts`: media query reaktif; shell menghentikan smooth wheel/parallax,
  mempersingkat transisi, scene membekukan gerak idle. Scroll sentuh memakai perilaku native.
- Shell: GSAP matchMedia untuk parallax hero + reveal heading; cleanup saat route/breakpoint berubah.
- Efek singularity/accretion disk dihapus atas permintaan pemilik; langit, bintang, dan planet tetap.
- Upgrade lima instrumen (`INSTRUMENT-DETAIL-PROMPT.md`) dieksekusi 2026-09-16 → `instrument-models.ts`.
- Verifikasi: `OBSERVATORY_URL=http://localhost:8769 timeout 180 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_observatory_motion.py`.
  Bukti: `assets/renders/observatory-motion/dev/` (PNG, WebM, JSON). Preview produksi lokal: port 8769.

### Revisi urutan planet (2026-09-16)
- `web/lib/planetary-motion.ts`: `planets` (delapan nama, warna, shader, ukuran tampilan, kemiringan/rotasi) dan `samplePlanetJourney(progress, time, desktop, reducedMotion)`; fungsi murni, tanpa DOM/Three. Scroll menentukan planet/transit, waktu menentukan orbit elips tertutup dengan arah sama. Ini koreografi dekoratif, bukan skala astronomi.
- `web/scripts/verify_planetary_motion.mjs`: `node web/scripts/verify_planetary_motion.mjs`; uji urutan 10.001 sampel scroll, kedua sisi batas hilang, 16 orbit tertutup desktop/HP, arah konsisten, seam, reduced motion, clamp ujung.
- `web/scripts/verify_planetary_browser.py`: Chromium membaca group R3F nyata melalui hook DevTools khusus test, tanpa debug API aplikasi. Urutan delapan planet maju/mundur di 390×844 dan 1440×900, wheel bolak-balik (maksimal satu planet/frame), idle, resize 360/430/1024/1920, reduced motion, case → home. PNG, WebM, JSON ke `assets/renders/planetary-motion/dev/`; bukan klaim performa HP fisik.
- Hasil: build/TypeScript/lint + uji jalur + 19 cek Chromium lulus, 0 error. Frame wheel 1500 px diverifikasi tidak berbalik arah/bertumpuk; ini bukan jaminan FPS. R3F 9.7 mempertahankan wrapper uniform sendiri, jadi animasi menulis `material.uniforms` melalui ref (mutasi object props saja tidak bekerja).
- Preview produksi revisi: `http://127.0.0.1:8780/`. Jalankan `OBSERVATORY_URL=http://127.0.0.1:8780 timeout 360 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/verify_planetary_browser.py`.

### `web/components/sky.tsx`
- **Peran:** mesh layar penuh (renderOrder -10, tanpa depth) dengan shader langit: zenith hitam → ink → horizon biru,
  bintang prosedural (kelip, warna, parallax), jalur nebula tipis, dither. Revisi 3 pemilik: kepadatan setara
  bintang gate, 2 lapis penuh hanya di 30% atas layar (`reach` smoothstep .62–.74); 70% bawah 1 lapis sangat jarang + redup.
- **Ekspor utama:** default `Sky({ progress, chapter, reducedMotion })`.
- **Dipakai oleh:** `World` di scene.
- **State / efek samping:** uniform `uOffset` dari sudut kamera + progres hero/chapter + tinggi kamera; interpolasi damping. Reduced motion membekukan langit. Resolusi/DPR tiap frame.
- **Catatan:** dekorasi, bukan data astronomi. Warna shader ditulis langsung sebagai sRGB (tanpa colorspace chunk).

### `web/components/instrument-models.ts`
- **Peran:** membangun kelima instrumen secara prosedural dari satu "machine shop" bersama, memakai palet yang sama
  dengan `observatory-model.ts`: logam perak, struktur navy, kuningan terkendali, lampu amber, kaca optik.
- **Ekspor utama:** `buildInstrument(id)` → `{ object, materials, dispose }`, `DUE_ORBITS`, tipe `BuiltInstrument`.
- **Dipakai oleh:** `observatory-scene.tsx` (geometri) dan `instrument-motion.ts` (`DUE_ORBITS`: satu tabel radius,
  dua konsumen).
- **Bergantung pada:** three + `mergeGeometries`; `InstrumentId` dari `lib/instruments.ts`.
- **State / efek samping:** tiap builder memakai `shop()` — satu material per finish, satu geometri per bagian,
  helper `box/cyl/drum/ring/hoop/ball/rod/bar/lathe/cable/teeth/studs/scale` dan `plinth()` (alas bertingkat
  bersama: kanal layanan amber, 12 bay berlampu, geladak berpelat, skala terkalibrasi). `finalize(root, assemblies)`
  memanggang setiap bagian statis menjadi satu mesh per material per assembly; `assemblies` = pivot bergerak
  **dan** grup mount, sebab `cases.ts` mengakhiri leader line pada material di dalam `<id>Mount`. Mesh hasil merge
  ditaruh **sebelum** pivot anak supaya pencarian material per nama menemukan bagian milik mount, bukan milik anaknya.
- **Catatan:** kontrak yang tak boleh berubah tanpa memperbarui konsumen: nama node di atas + nama material
  `Lens1Glow..Lens3Glow`, `Amber light`, `surgeline signal`, `driftwatch ceramic` (hanya kertas grafik di mount,
  hanya drum di `RollerPivot0`), `driftwatch alarm` (hanya ujung pena), `duewatch signal/alarm/ceramic*`,
  `brandwall ceramic` (hanya tabung kolimator), `Prism blue`, `Spectrum0..3`. GLB instrumen lama masih ada di
  `web/public/models/` tetapi tidak dimuat lagi; sumber Blender tetap di `assets/blender/`.

### `web/components/instrument-motion.ts`
- **Peran:** rig gerak idle per instrumen + Saturnus; objek tambahan dibuat runtime.
- **Ekspor utama:** `rigInstrument(id, view, materials, onObserve)`, `saturn(source)`, `pointScale`, tipe `Rig`.
- **Dipakai oleh:** `observatory-scene.tsx`.
- **Bergantung pada:** kontrak node/material dari `instrument-models.ts` (lihat scene) + nama material
  `surgeline signal`, `driftwatch alarm`, `duewatch signal/alarm`, `Spectrum0..3`, `Amber light`,
  `First light / planet mineral`, `dusty rings`; `DUE_ORBITS` untuk radius/presesi lintasan.
- **State / efek samping:** CrossCheck siklus 6.6 dtk (lensa 1→2→3, lalu ketiganya hijau). SurgeLine: parameter
  yaw/pitch/periode per piringan + 2 cincin pulsa additive per piringan. DriftWatch:
  ribbon trace 150 titik dari `reading(t)` (sumbu waktu = z kertas), tick kertas bergerak, burst merah tiap 5.2 dtk.
  CrossCheck juga memutar `FocusPivot{i}` saat kanal itu membaca. DueWatch: `OrbitPivot{i}` presesi, `PlanetPivot{i}`
  berputar dengan kecepatan Kepler `1.1·(0.65/r)^1.5` dari `DUE_ORBITS`; planet merah berkedip di tanda "due". BrandWall: 64 foton/dtk
  collimator → prisma → layar; detektor off = pola interferensi cos², on (siklus 13 dtk atau tap 5 dtk) = dua pita.
  Saturnus: clone scene + shader onBeforeCompile (pita, badai, celah Cassini), 520 debu cincin (Kepler), dua bulan.
- **Catatan:** semua geometri/material buatan rig di-dispose lewat `rig.dispose()`; `frustumCulled=false` untuk objek dinamis.

### `web/lib/ambient.ts`
- **Peran:** sound design sintetis original: hum, lima klik instrumen, sweep kamera; tanpa sample/aset audio eksternal.
- **Ekspor utama:** `ObservatoryAudio.setEnabled`, `click(index)`, `transition(in|out)`, `visibilityChanged`, `dispose`.
- **Dipakai oleh:** shell; AudioContext dibuat hanya dari gesture Enter/toggle.
- **Bergantung pada:** Web Audio API, document visibility.
- **State / efek samping:** oscillator/gain di satu master; pitch klik 660/520/440/780/880 Hz, envelope 120ms; sweep dua sine 780/660ms. Rate limit klik 75ms, maksimum enam voice transien, transition mengganti voice lama. `onended` disconnect; mute/hidden langsung stop/disconnect transien + fade hum; dispose stop/close. Request generation menjaga hasil resume lama tidak membalik intent terbaru.
- **Catatan:** kualitas/volume pada speaker HP fisik tetap bahan gate pemilik.

### `web/scripts/verify_mobile.py`
- **Peran:** regresi homepage Fase 3 setelah case route Fase 4, Chromium 390×844 → 360×740 → 430×932.
- **Ekspor utama:** `run`, `position`, `menu_to`, `enter`, `difference`; `OBSERVATORY_URL` override.
- **Dipakai oleh:** `npm run verify:mobile`; CrossCheck venv Python Playwright + Pillow.
- **Bergantung pada:** server :8767, selector page/shell, Chromium ANGLE gl-egl.
- **State / efek samping:** PNG + `verification.json` ke `assets/renders/full-observatory/dev/`;
  timestamp/status running/passed/failed; error navigasi menyimpan detail + screenshot.
- **Catatan:** audio/entry/mute, satu Canvas, lima sticky/idle/orbit/readings, lima route case + return (Fase 5; hanya dialog menu tersisa), fokus,
  reverse navigation, semua skill href dan lima klik project, scan clip berbeda, About, Contact
  (`CONTACTS` href persis, tap ≥44, noopener), readout 100%, touch swipe 390px, block BrandWall →
  lima fallback + notice tidak menimpa copy (`fallback-verification.json`); nol `.draft-label`; grup "Daily work" = 3 item tanpa link.
  Sejak Fase 7 (instrumen dimuat sesudah Enter) cabang model-diblok menunggu `.observatory[data-scene="fallback"]`, bukan membaca atribut langsung setelah Enter; sama di `verify_case.py`, `verify_cases.py`, `case_files_evidence.py`.
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
- **Peran:** run/preview, handoff Fase 3–7, tabel sumber semua copy bisnis/angka dan skill-project; seluruh copy approved Fase 5, istilah DRAFT dalam tabel adalah riwayat provenance.
- **Ekspor utama:** commands build/start/verify/tunnel; status copy dan kontak; Blender node contracts.
- **Dipakai oleh:** pemilik dan harness Testing.
- **Bergantung pada:** PLAN §4–§12 relevan, lima dossier §1/§3/§5 dan batas demonstrasi masing-masing.
- **State / efek samping:** tidak ada.
- **Catatan:** fokus Automation Engineer dari klarifikasi pemilik; copy approved Fase 3; skill harian terpasang
  dinyatakan; kontak asli tercatat. Perintah paket bukti Testing ada di Verification.
  Fase 7 menambah kontrak suara/loader/transisi, perintah dua tes fokus, batas Development vs pengukuran performa Testing. Fase 6 gate sudah passed.
  2026-09-16: paragraf Enter lebih cepat (opsi B) + angka ukur sebelum/sesudah di bagian Phase 7.
  Script bukti Fase 1–2 diarsipkan, bukan acceptance Fase 3.
  2026-09-16 (7A): bagian "Phase 7A" di atas = brief personal, sumber data/bukti, tabel copy DRAFT → dossier, perintah verifikasi; judul README jadi "Personal rooms".

### `web/lib/instruments.ts`
- **Peran:** urutan lima instrumen + sumber data copy chapter (field `preview` dihapus Fase 5 bersama dialog).
- **Ekspor utama:** `instruments`, `InstrumentId`, `ChapterState` (`from?` hanya selama rantai case→case).
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
- **Ekspor utama:** `fraunces.woff2`, `inter.woff2`, `jetbrains-mono.woff2` (disajikan; 17,960 / 21,092 / 19,772 B);
  `fraunces.ttf`, `inter.ttf`, `jetbrains-mono.ttf` (sumber approved, tidak lagi dirujuk CSS; dipakai label `full_observatory_evidence.py`), masing-masing
  `*-LICENSE.txt`; `dome-fallback.png`; `draco_decoder.wasm`, `draco_wasm_wrapper.js`,
  `README.md` upstream dan `LICENSE.txt` Apache 2.0.
- **Dipakai oleh:** CSS (WOFF2) / useGLTF / preload layout (Draco).
- **Catatan WOFF2 (Fase 7):** `pyftsubset <ttf> --unicodes=U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2190-21FF,U+2212,U+2215,U+221D --layout-features='*' --name-IDs='*' --name-languages='*' --flavor=woff2`
  (lewat `uv run --no-project --with fonttools --with brotli`). Semua karakter non-ASCII situs (§²³·×–’“”…↑→↗↙−∝) tetap tercakup sama seperti TTF; fitur hilang hanya `ccmp`/`mark`/`mkmk` (tanda gabung, tak dipakai). Copyright name ID 0 tetap. Lisensi OFL tanpa Reserved Font Name. Copy baru dengan karakter di luar rentang → regenerasi subset.
- **Bergantung pada:** salinan aset style-lock/render; decoder distribusi three 0.186.0;
  teks lisensi Apache dari apache.org/licenses/LICENSE-2.0.txt.
- **State / efek samping:** hanya download/cache browser; salinan vendor tidak diedit.
- **Catatan:** fallback sama dengan dome-night.png approved, bukan pengganti diam-diam scene.

### `assets/renders/first-light/`
- **Peran:** arsip render Blender, screenshot HP, bukti alur dan environment Fase 1
  (Fase 2 output ke `crosscheck/`, sejak Fase 3 output ke `full-observatory/dev/`).
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
- **Catatan:** Fase 0 `done` 2026-09-14; Fase 1 `done` 2026-09-15; Fase 2 `done` 2026-09-15; Fase 3 `done` 2026-09-15. Fase 4 `done` 2026-09-15 (copy case approved). Fase 5 `done` 2026-09-15 (gate lolos, seluruh copy approved, DRAFT dilepas, opsi 1 DueWatch). Fase 6 (Desktop) `done` 2026-09-15 (gate dari video bukti desktop). Fase 7 `ready-for-test` (Testing 13/13; opsi B "Enter lebih cepat" dikerjakan 2026-09-16, menunggu Testing ulang + gate). `assets/` tidak dilacak git sejak 2026-09-15 (tetap lokal; riwayat commit lama masih memuatnya). Log sesi dijaga ringkas.

## 5. Aset

Ukuran byte aset Fase 0 diukur 2026-09-14; aset Fase 1 pada 2026-09-15.

| Aset | Sumber | Ekspor GLB | Ukuran | Dipakai di |
|---|---|---|---:|---|
| `crosscheck-explainer.mp4` | dossier §6 K13 / crosscheck/assets | H.264, silent English | 5002746 | case demo video |
| `crosscheck-demo-poster.jpg` | frame detik 1 video yang sama | JPEG 960×540 | 22133 | case video poster |
| `surgeline-explainer.mp4` / poster | `surgeline/assets/explainer.mp4` | H.264, silent English | 1812889 / 14675 | case SurgeLine |
| `driftwatch-explainer.mp4` / poster | `driftwatch/assets/explainer.mp4` | H.264, silent English | 2227965 / 39996 | case DriftWatch |
| `duewatch-explainer.mp4` / poster | `duewatch/assets/explainer.mp4` (poster 8 s) | H.264, silent English | 2221217 / 44319 | case DueWatch |
| `brandwall-explainer.mp4` / poster | `brandwall/assets/explainer.mp4` | H.264, silent English | 10457918 / 37244 | case BrandWall |
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
| `fraunces.ttf` | Google Fonts | — | 71580 | sumber subset (dulu heading) |
| `inter.ttf` | Google Fonts | — | 324820 | sumber subset (dulu body) |
| `jetbrains-mono.ttf` | Google Fonts | — | 112172 | sumber subset; label bukti Fase 3 |
| `fraunces.woff2` | `pyftsubset` dari TTF (2026-09-16) | — | 17960 | heading |
| `inter.woff2` | `pyftsubset` dari TTF (2026-09-16) | — | 21092 | body |
| `jetbrains-mono.woff2` | `pyftsubset` dari TTF (2026-09-16) | — | 19772 | readout |

## 6. Alur penting

Fase 7:
1. HTML preload dome/ambient/Draco + WOFF2 dari CSS + JS (termasuk three) paralel → loader subscribe drei, progres tidak mundur;
   hero render frame ke-2 + font settle → dial ready, tombol aktif → `loadInstruments` → lima GLB dimuat di belakang hero.
2. Enter gesture → resume hum + welcome sweep bila sound on; silent/remembered off tidak membuat AudioContext.
3. Hotspot/close/BrandWall tap → klik instrumen; open/return/Next → sweep; semua lewat master dan guard visibility/mute.
4. Departure timeline → route arrival; cleanup pathname membatalkan callback navigasi basi; kartu pointer WAAPI 180ms dapat diinterupsi.

Fase 5:
1. CTA chapter mana pun → `openCase(i)`: simpan home scroll/chapter, `caseView.index = i`, tween mix → push `/work/<slug>`.
2. Next (`data-case-target`) → `chainCase(j)`: mix 1→0, chapter sapuan `from`→`j`, push; arrival layout effect terbang masuk.
3. Return/menu dari case → `leaveCase`: scroll asal, atau `#<slug>` case aktif setelah rantai / direct URL; kamera mundur.
4. Scene: leader tiap komponen dari `anchor(node, part)` → SVG; fallback still per slug; BrandWall tap-to-observe juga di case.

Fase 4:
1. CrossCheck CTA → simpan home scroll/chapter → hentikan Lenis → tween `CaseView.mix` + fade → router push.
2. Root Canvas/audio/Lenis tetap hidup; trigger lama cleanup, trigger case + ResizeObserver baru.
3. Model mengikuti section instrument; Lens1–3 → world projection → SVG leaders; tap marker → kartu.
4. IntersectionObserver reading → GSAP count-up; video menunggu play, captions English asli.
5. Return/Back → kamera mundur + restore home scroll; Tools → Skills; Next → homepage SurgeLine.
6. Direct URL/reload tidak bergantung elemen homepage; model gagal → labeled still + kartu tetap tersedia.

Fase 3:
1. Page map instruments → lima section sticky; main trigger menghitung index/transisi/orbit/outro.
2. Scene membaca chapter ref → kamera + group incoming/outgoing + node idle, tetap satu Canvas.
3. Skills disclosure → ResizeObserver → refresh bounds; link → Lenis scroll + highlight + fokus heading.
4. About portrait masuk viewport → GSAP clipping + scan line; Contact → `mailto:` + tiga link eksternal tab baru.
5. Arsip Fase 3–4: CTA CrossCheck → route, empat CTA lain → dialog preview. Sejak Fase 5 kelima CTA → `openCase` (lihat Fase 5 di atas).
6. Error model baru → semua instrumen tetap tersedia sebagai still view berlabel.

Fase 2:
1. Scroll lewat hero → trigger reveal `#crosscheck` (top bottom → top top) → kamera mulai
   berputar, teleskop naik, kubah hilang, `data-chapter=crosscheck`.
2. Section sticky → trigger orbit (top top → bottom bottom) → sudut kamera; mundur = menelusur balik.
3. Idle `useFrame`: ayun `OpticsPivot`, gelombang emissive `Lens1..3Glow` bergiliran.
4. Arsip Fase 2: CTA dulu preview dialog. Sejak Fase 4 CrossCheck membuka route persisten, lalu Return memulihkan scroll/fokus.
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
