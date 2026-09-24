# PROGRESS — Tracker Rayin Observatory

> Sumber kebenaran status kerja. Diupdate di akhir **setiap** sesi (lihat `PROMPT.md`).
> Status: `todo` · `in-dev` · `ready-for-test` · `in-test` · `awaiting-gate` · `done` · `deferred`
> Mulai Fase 3 (PLAN §12, Q31): tahap **Development** = Codex (utama) / Claude Code;
> tahap **Testing** = Claude Code / Antigravity, menghasilkan paket bukti video + foto untuk gate.

## Status saat ini

| Hal | Isi |
|---|---|
| Fase aktif | **Fase 8 — Launch ready** · `done` (gate 2026-09-24, "terima semua"; F1 WebKit headless diterima). Fase 9 tetap `deferred` |
| Status fase | 7F `done` (gate 2026-09-24, "saya accept semua itu lulus"). 7D `done` (gate 2026-09-18, "semuanya approved"); 7A/7B/7C `done`. 7E `done` (gate 2026-09-24, "saya sudah approve"). 7A–7E `done`. |
| Bagian PLAN.md yang relevan | §3 Q40–Q50, §7, §10–§12 (Fase 8 launch). |
| Blocker | — |
| Preview sesi ini | `http://127.0.0.1:8767/` = build 7F Development (2026-09-24, sumber `2e90c092c607038b`, memuat Q49 + fix 7F). |
| Revisi terakhir | Gate 7F lolos → `done` 2026-09-24 (Claude Code): pemilik accept semua — hint Q49 approved, kunci scroll ±50–320 ms dan header transparan diterima (PLAN §3 Q50); tanpa perubahan kode; commit + push. Sebelumnya: 7F Testing → `awaiting-gate` 2026-09-24 (Claude Code): skrip baru `observatory_evidence.py`, paket `personal-observatory/evidence/` 17/17 pass (sumber `2e90c092c607038b`; runner 18/18 skip = hijau); tanpa perubahan kode app. Sebelumnya: 7F Development → `ready-for-test` 2026-09-24 (Claude Code): walkthrough rantai lima ruang HP + desktop; fix label `data-chapter`, Replay CrossCheck di baris kicker HP, tinggi step tetap di desktop (tanpa lompatan 9 px); suite + `perf_quick` diperbarui ke Q49 (`q49.py`); runner 18/18 passed di sumber `2e90c092c607038b`. Sebelumnya: Revisi pemilik Q49 2026-09-24 (Claude Code): scroll native tanpa pin (hero, lima chapter, inspection field CrossCheck satu layar), putaran instrumen lewat geser/tap pengunjung, scan CrossCheck main saat terlihat + step/Replay; transisi = tirai berbeda per case (panggung, bilah, gulungan, lajur, lipatan spektrum) menggantikan iris/pulsa/pita/cincin/prisma. Typecheck/lint + cek Playwright dev :8768 lulus; belum `next build`/runner; skrip regresi lama basi (lihat CODEMAP "Revisi Q49"). Commit + push. Sebelumnya: Gate 7E lolos 2026-09-24 (Claude Code): copy 7E approved, DRAFT BrandWall dilepas (`cases.ts`, `page.tsx` strip → "Illustration", komentar `brandwall-room.ts`/`instruments.ts`/CSS; tes `verify_mobile.py` `DRAFTS = set()`, `verify_cases.py`, `verify_brandwall_room.py`, `brandwall_room_evidence.py` → 0 DRAFT); perbaikan atas izin pemilik: label 8 px → 10 px, crop Overflow HP `phoneView`; lint/typecheck/build, runner 11 suite + `perf-brandwall` passed, paket bukti ulang 17/17 (sumber `4bf13e4158597b83`); commit + push. Sebelumnya: 7E Testing → `awaiting-gate` 2026-09-24 (Claude Code, Q47 ringan): skrip baru `brandwall_room_evidence.py`, paket 17/17 pass di sumber `d97d12160a89721c` (runner: semua suite terkait sudah `passed` di sidik jari sama → tidak diulang); tanpa perubahan kode app. Sebelumnya: Gate 7D lolos 2026-09-18 (Claude Code): pemilik "semuanya approved" → copy 7D approved, label DRAFT DueWatch dilepas (`cases.ts`, strip `page.tsx` → "Illustration", komentar `duewatch-room.ts/.tsx`/`instruments.ts`/CSS, tes `verify_duewatch_room.py`/`verify_cases.py`/`duewatch_room_evidence.py` mengharapkan 0 DRAFT), 2 temuan diterima; lint/typecheck/build + regresi `time`, `cases`/`mobile` 390×844 passed (sumber `de8440d2274dbcd4`); commit + push. Sebelumnya: 7D Testing → `awaiting-gate` 2026-09-17 (Claude Code): lint/typecheck/build utama, runner 16/16 passed (sumber `f19aac05262f34b3`; `time` 6 viewport + edge hijau setelah fix rig, `perf-surgeline` 57–60 fps — gagal lama tidak terulang), fix tes basi `verify_cases` (judul hotspot DueWatch), paket bukti baru 22/22; tanpa perubahan kode app. Sebelumnya: 7D terintegrasi 2026-09-17 (Codex): dua modul agenda/triage, replay ledger, audit, chapter dan transisi cincin; tanpa tes ulang atas arahan pemilik. Detail verifikasi/temuan di handoff 7D. Sebelumnya: Gate 7C lolos 2026-09-17 (Claude Code): pemilik "saya approve semua untuk 7C" → copy 7C approved (termasuk Day 1–3), label DRAFT DriftWatch dilepas, jarak verdict HP diterima; build + regresi `monitor`, `cases`/`mobile` 390×844 passed (sumber `8b800e3ebedbbbb4`); commit + push. Sebelumnya 7C Testing → `awaiting-gate` 2026-09-17 (Claude Code): paket `driftwatch_room_evidence.py` 21/21 (memanggil `verify_driftwatch_room.viewport/edges`); fix gerak Compare = jendela clip (lonjakan digambar di tempat, dulu diperas `scaleX`); runner 13/13 hijau di sumber `a8336493ca0de6ca`. Sebelumnya 7C Development → `ready-for-test` 2026-09-17 (Codex → Claude Code): trace chapter seismograf, pita jarum → timeline, meja banding 5 situasi (perubahan biasa sehat; layout rusak/collector gagal/run hilang = alarm beralasan; pulih pakai baseline terakhir), arsip bukti terpisah; ilustrasi Day 1–3 (bukan tanggal soak); runner 13 suite hijau di sumber `40a56b14db159831`. Sebelumnya gate 7B lolos 2026-09-17 (Claude Code): copy approved, label DRAFT SurgeLine dilepas, Cut sebelum Form diterima; build + regresi terdampak; commit + push. Sebelumnya Testing 7B (Claude Code): paket `surgeline_room_evidence.py` 18/18; fix pulsa Return mendarat di titik antena asal (`pulseHome` di shell); runner 11 suite hijau di sumber `37a4f3e3770463fb`. Sebelumnya Development 7B (Codex → Claude Code): strip chapter 3 browser (lane 2 cut → resumed), pulsa antena masuk/kembali, papan dispatch A–F (antrean → 3 browser → Confirmed/Rejected/Dead-letter; Cut/Resume/Replay), ledger + bukti rekaman, teaser DriftWatch; fix fps var CSS root. Copy baru DRAFT |
| Langkah berikut | **Fase 8 Testing (putaran penuh)** di `https://rayin-observatory.vercel.app`: QA 3 engine × HP/tablet/desktop, lima ruang, cek preview share WhatsApp/LinkedIn, paket `assets/renders/launch/evidence/`; lalu tes HP fisik pemilik + gate. Copy share (format judul, alt, teks sosial) masih DRAFT. |
| Launch | Produksi: **https://rayin-observatory.vercel.app** (Vercel `chhrones-projects/rayin-observatory`, deploy 2026-09-24 `dpl_CFmRsnzmH2xtNJQXh7wBo2DXoBK7`, atas izin pemilik). Sambung domain: lihat "Instruksi domain" di checklist Fase 8. Riwayat: Gate 7A–7F lolos; Fase 8 aktif. `web/` ter-link sejak 2026-09-24 (`.vercel/` untracked, login CLI `chhrone`). Testing produksi mengikuti Q40 |

### Integrasi 7D (izin pemilik 2026-09-17)

Development awal di `assets/development/phase-7d/`. Pemilik kemudian menyatakan:
**"7C sudah stabil tinggal kamu integrasikan, gak perlu tes ulang cukup integrasikan aja"**.
15 berkas 7D terintegrasi ke `web/` utama; approval/perbaikan 7C dipertahankan.
Handoff dan bukti Development tetap di salinan; `INTEGRATION.json` mencatat hash hasil penggabungan.
Tanpa tes ulang/rebuild utama pada sesi integrasi. Belum gate 7D, belum commit/push 7D.

### Arahan wajib saat memakai prompt universal

- **Baca Q41 terlebih dahulu:** sumber copy/angka adalah `portfolio/CAPABILITY_*.md` di root
  **Rayin Observatory**, menggantikan path sibling pada prompt lama. Jangan berpindah sumber
  tanpa mencatat perbedaannya. Dossier adalah snapshot, bukan laporan hasil run hari ini.
- Urutan aktif: **7A CrossCheck → 7B SurgeLine → 7C DriftWatch → 7D DueWatch → 7E BrandWall →
  7F integrasi → 8 launch → 9 aksesibilitas**. Kerjakan hanya fase/tahap aktif.
- Setiap fase project: **brief personal → mobile selesai dan diuji → desktop dipoles →
  regresi mobile → Testing → gate**. Desktop tetap panggung utama; bukan pekerjaan sisa.
- Personalisasi meliputi cerita, chapter homepage, case file, komposisi bukti, hotspot,
  animasi penjelas, serta entry/return/Next. Mengganti warna/nama saja belum memenuhi gate.
- Fase 0–7 dan copy lama tetap riwayat approved; checklist baru belum dikerjakan. Copy baru
  berstatus DRAFT. Bukti lama tidak dipakai untuk meluluskan personalisasi baru.

## Ringkasan fase

| Fase | Nama | Status | Gate lolos (tanggal) |
|---|---|---|---|
| 0 | Style lock | `done` | 2026-09-14 |
| 1 | First light | `done` | 2026-09-15 |
| 2 | One instrument alive | `done` | 2026-09-15 |
| 3 | Full observatory | `done` | 2026-09-15 |
| 4 | First case file | `done` | 2026-09-15 |
| 5 | All case files | `done` | 2026-09-15 |
| 6 | Desktop | `done` | 2026-09-15 |
| 7 | Showpiece polish | `done` | 2026-09-16 |
| 7A | CrossCheck — inspection room | `done` | 2026-09-16 |
| 7B | SurgeLine — dispatch room | `done` | 2026-09-17 |
| 7C | DriftWatch — monitoring room | `done` | 2026-09-17 |
| 7D | DueWatch — time control room | `done` | 2026-09-18 |
| 7E | BrandWall — visual studio | `done` | 2026-09-24 |
| 7F | Five rooms, one observatory | `done` | 2026-09-24 |
| 8 | Launch ready | `done` | 2026-09-24 |
| 9 | Accessibility | `deferred` | — |

---

## Checklist per fase

### Fase 0 — Style lock
Target: satu render kubah, satu render instrumen, dan satu layar contoh di HP disetujui; palet,
font, dan foto final.
- [x] Buat folder `assets/blender/`, `assets/renders/`, `assets/photo/`
- [x] Crop `/home/rayin/Documents/profile foto.jpg` → tanpa logo Amazon, simpan di `assets/photo/` (crop + edit latar AI agar bahu utuh; disetujui di gate)
- [x] Stilisasi foto (duotone navy + garis scan) → `assets/photo/`
- [x] Blender: kubah observatorium (night look) → `assets/blender/dome.blend` + render `assets/renders/`
- [x] Blender: teleskop 3 lensa (CrossCheck) → `assets/blender/crosscheck.blend` + render
- [x] Layar contoh HP statis (hero atau chapter CrossCheck) memakai palet & font §8
- [x] Pemilik memilih/menyetujui palet & font → catat final di PLAN.md §8
- [x] Gate: pemilik menyatakan lolos (2026-09-14, "lolos, buat saya aman untuk lanjut")

Bahan gate: `assets/style-lock/index.html`. Jalankan dari root:
`python -m http.server 8766 --bind 0.0.0.0 --directory assets`.
Lokal: `http://127.0.0.1:8766/style-lock/`; HP satu Wi-Fi sesi ini:
`http://192.168.1.21:8766/style-lock/` (IP dapat berubah).
Screenshot: `assets/renders/mobile-390x844.png` dan `style-review-mobile.png`.
Petunjuk/sumber copy: `assets/style-lock/README.md`; bukti: `verification.json`.
Palet/font FINAL sejak gate 2026-09-14; keputusan di PLAN §8. Fase 1 dimulai sesi Codex berikutnya.

### Fase 1 — First light
- [x] Inisialisasi `web/` (Next.js + TS + R3F + GSAP + Lenis), satu Canvas persisten
- [x] Gerbang "Enter the Observatory" + loader "calibrating instruments" + "Enter without sound"
- [x] Hero: kubah terbuka, langit + planet ambient, kalimat posisi (DRAFT)
- [x] Suara ambient + toggle di header
- [x] Scroll Lenis sangat halus; header minimal + readout progres
- [x] Preview link yang bisa dibuka di HP
- [x] Gate: pemilik menyatakan lolos (2026-09-15, "lolos, buat saya aman untuk lanjut ke fase selanjutnya"; dinilai dari foto + video bukti)

Bahan gate Fase 1:
- **Preview HP:** https://geological-ones-medline-loans.trycloudflare.com/
- Lokal: `http://127.0.0.1:8767/`; jalankan `npm run start --prefix web` setelah build.
- URL publik sementara: app + container `rayin-observatory-preview-tunnel` harus hidup;
  hostname berganti saat tunnel diulang. Setup/stop: `web/README.md`. Tidak mengubah firewall/domain/DNS.
- Bukti HP emulasi: `assets/renders/first-light/verification.json` (status `passed`),
  `preview-verification.json`, PNG `gate-`, `hero-`, `dome-scroll-`, `menu-` untuk tiga ukuran;
  `preview-390x844.png` dari URL publik.
- Verifikasi produksi: build, lint, TypeScript exit 0; Chromium 390×844 → 360×740 → 430×932;
  satu Canvas, font termuat, nol overflow/error/request ≥400 pada alur normal; audio resume,
  silent entry, mute tersimpan, menu/contact, Lenis readout 100%, return dan swipe 390px.
  Fresh visitor default audio + model sengaja diblok → fallback berlabel juga lolos.
- Batas: speaker/audio, rasa scroll, fps dan 4G di HP fisik belum diuji. Target performa PLAN §11
  belum diklaim tercapai. Kubah memakai bentuk terbuka approved; gerak reveal + rotasi/zoom,
  bukan shutter mekanis baru. Work/About/Contact lengkap masih fase berikut; CTA Contact
  sementara memberi keterangan bahwa detail belum tersedia.
- **Bukti gate 2026-09-15** (`web/scripts/gate_evidence.py` ke URL publik): Chromium/WebKit/Firefox
  390×844 → preview, gate, canvas, hero, scroll, clean = pass ketiganya; sound pass Chromium+Firefox,
  `n/a` WebKit headless (tanpa perangkat audio; situs tampil pesan retry, tidak error). 4G lambat
  emulasi: Enter aktif 5.9 s, transfer 952602 byte. Folder `assets/renders/first-light/gate-evidence/`.
- Copy hero **DRAFT**: “I test. I watch.” + “I build systems that find web issues and catch
  changes in your data.” Sumber: CrossCheck §1 + DriftWatch §1; peta copy lengkap `web/README.md`.

### Fase 2 — One instrument alive
- [x] Ekspor `.glb` teleskop CrossCheck terkompresi (`crosscheck.glb`, Draco, 317336 byte)
- [x] Chapter pinned CrossCheck: kamera memutari instrumen saat scroll, gerakan idle
- [x] Copy pendek CrossCheck (pitch + 1 angka bukti) dari dossier → approve pemilik (disetujui lewat gate tanpa revisi; label DRAFT di situs dilepas bersama sign-off copy homepage Fase 3)
- [x] Tombol "Open case file" (tujuan sementara: dialog preview)
- [x] Gate: pemilik menyatakan lolos (2026-09-15, "lolos, buat saya aman utuk lnjut ke fase selanjutnya sekarang"; dinilai dari foto + video bukti emulasi)

Bahan gate Fase 2:
- **Preview HP:** https://geological-ones-medline-loans.trycloudflare.com/ (app :8767 + container
  tunnel harus hidup; hostname berganti bila tunnel restart). Enter → scroll lewat kubah → chapter.
- **Video + foto** (bila link tidak terbuka di HP): `assets/renders/crosscheck/walkthrough/`
  (`crosscheck-walkthrough.mp4`, `01-gate` … `06-orbit-end.png`), direkam lewat URL publik.
- Copy DRAFT: kicker "01 / Web QA"; pitch "I test your web app across browsers, screen sizes and
  user roles, then deliver a clear list of issues."; angka **1,080** "test combinations · On an owned
  demo app". Sumber: CrossCheck §1, meta "Proven scale", §3.2 (demo target). Tabel lengkap `web/README.md`.
- Verifikasi: lint/typecheck/build exit 0; `verify:mobile` passed 390×844 → 360×740 → 430×932
  (`assets/renders/crosscheck/verification.json`): chapter pinned, diff piksel idle ≈6.6–7.4 & orbit
  ≈50–56, dialog menahan scroll + fokus kembali, still view saat `crosscheck.glb` diblok, 0 error/≥400.
- Batas: emulasi Chromium saja; fps/rasa scroll HP fisik belum diuji; Firefox/WebKit = Fase 8.

> Fase 3–8: centang Development dulu (status → `ready-for-test`), lalu Testing. Paket bukti di
> `assets/renders/<slug-fase>/evidence/` (PNG per item, MP4, contact sheet, `evidence.json`).

### Fase 3 — Full observatory
Development (Codex / Claude Code):
- [x] Blender + `.glb`: antena array, seismograf, orrery, spektrograf prisma
- [x] Chapter SurgeLine, DriftWatch, DueWatch, BrandWall (urutan PLAN §5)
- [x] Skills: daftar PLAN §9 + tautan skill → project; Python/testing/scripting/automation jadi inti
  - [x] Konfirmasi daftar kerja harian Go, MySQL/TiDB, Redis (2026-09-15) → grup Skills "Daily work"
- [x] About: foto stilisasi + reveal scan + copy DRAFT
- [x] Contact: CTA + Email / LinkedIn / GitHub / Upwork
  - [x] Alamat/URL dari pemilik (2026-09-15); CTA `mailto:` aktif, label link "Rayina Ilham"
- [x] Copy homepage lengkap DRAFT + tabel sumber (`web/README.md`); lint/typecheck/build + tes fokus → `ready-for-test`

Testing (Claude Code / Antigravity):
- [x] Tes otomatis setiap item Development (390×844 → 360×740 → 430×932); bug diperbaiki + tes ulang
- [x] Paket bukti `assets/renders/full-observatory/evidence/` dikirim ke pemilik (16/16 pass)
- [x] Semua copy homepage di-approve (label DRAFT dilepas, 2026-09-15)
- [x] Gate: pemilik menyatakan lolos (2026-09-15, "Lolos semua gacor brok"; dinilai dari video + foto bukti)

Bahan gate Fase 3: `full-observatory-walkthrough.mp4` + `contact-sheet.jpg` (24 frame berlabel) +
`viewports/viewports-sheet.jpg` + `evidence.json` di folder bukti. Emulasi Chromium; fps/HP fisik = Fase 8.

### Revisi desain pasca Fase 3 (2026-09-15, permintaan pemilik)
- [x] Langit: gradasi hitam pekat (atas) → biru (horizon), bintang berkelip, nebula tipis; gate ikut
- [x] Saturnus: pita + rotasi, debu cincin, dua bulan, goyang sumbu
- [x] CrossCheck: lensa bergiliran → ketiganya nyala hijau bersama
- [x] SurgeLine: tiap piringan sudut/ritme sendiri + cincin pulsa sendiri
- [x] DriftWatch: kertas bergulir, trace hidup, lonjakan merah + jarum tersentak
- [x] DueWatch: planet di jalurnya, kecepatan Kepler (makin jauh makin lambat), cincin presesi
- [x] BrandWall: foton + detektor; off = pola gelombang, tap = dua pita partikel (celah ganda)
- [x] lint/typecheck/build + `verify:mobile` 3 viewport pass; bukti 8/8 pass (MP4 + contact sheet)
- [x] Label BrandWall "Tap to observe · detector off/on …" di-approve (2026-09-15)
- [x] Pemilik menyatakan revisi oke (2026-09-15, "setuju"; langit 30% gelap di revisi 2)

### Fase 4 — First case file
Development (Codex / Claude Code):
- [x] Route `/work/crosscheck` dengan template PLAN §7
- [x] Transisi kamera terbang masuk / mundur
- [x] Hotspot instrumen + kartu komponen
- [x] Readings teranimasi, Tools used, demo video; copy DRAFT → `ready-for-test`

Testing (Claude Code / Antigravity):
- [x] Tes otomatis item di atas + transisi masuk/kembali; bug diperbaiki + tes ulang
- [x] Paket bukti `assets/renders/case-crosscheck/evidence/` dikirim (14/14 pass)
- [x] Copy case file CrossCheck di-approve (label DRAFT dilepas, 2026-09-15)
- [x] Gate: pemilik menyatakan lolos (2026-09-15, "lolos semua ini fase 4 aman"; dinilai dari video + foto bukti)

Bahan gate Fase 4 (Testing, 2026-09-15): folder `assets/renders/case-crosscheck/evidence/` —
`case-crosscheck-walkthrough.mp4` (390×844, ±62 dtk), `contact-sheet.jpg` (17 frame berlabel),
`02-flight-in.png`, `05-hotspots.png`, `11-return-flight.png`, `viewports/viewports-sheet.jpg`, `evidence.json`.
- Bug diperbaiki: tiap home → case melempar `TypeError … getBoundingClientRect` (ResizeObserver homepage lama
  refresh setelah DOM case masuk → `#skills` null). Fix guard `live()` di `observatory-shell.tsx`; lint/typecheck/build,
  `verify_case.py` + `verify:mobile` 3 viewport pass, 0 error.
- **Temuan untuk pemilik (bukan fail otomatis; diterima apa adanya di gate):** flight-in terbaca lemah — teks memudar, teleskop sedikit berputar
  tapi tidak tampak mendekat, lalu turun keluar layar; case terbuka di Brief tanpa instrumen. PLAN §7 minta kamera
  terbang masuk + instrumen jadi objek utama. Pilihan: terima, atau kembali ke Development (zoom masuk terlihat +
  instrumen tetap di layar pertama case). Return terasa baik (instrumen turun kembali ke tempatnya).
- Batas: emulasi Chromium GPU; kilatan frame kecil di MP4 = artefak screenshot rekaman Playwright. fps/HP fisik = Fase 7/8.

Bahan handoff Fase 4 Development (2026-09-15):
- Lokal: `http://127.0.0.1:8767/work/crosscheck` atau homepage → CrossCheck → Open case file.
  Server produksi aktif, tunnel tidak dinyalakan. Jalankan ulang: `npm run start --prefix web`.
- Copy case seluruhnya **DRAFT**; sumber/tabel angka di `web/README.md` (CrossCheck dossier §3–§7/§9).
  Readings: 1,080 kombinasi; 216 cek akses; 18 issue dari 881 sinyal; 12/12 bug tanam, konteks demo eksplisit.
- Verifikasi Development: lint/typecheck/build exit 0; `verify_case.py` + `verify:mobile` passed
  390×844 → 360×740 → 430×932; Canvas identik, scroll/fokus pulih, Back/Forward, direct/reload,
  kartu + endpoint lensa, count-up, lazy video/playback, Skills/Next. Nol error/HTTP ≥400 alur normal.
- Fix terakhir khusus fallback: notice tidak menutup label; `verify_case.py --fallback-only` passed
  (390×844), screenshot diperbarui. Video asli English byte-identik, H.264, 0 audio streams.
- Foto/JSON Development: `assets/renders/case-crosscheck/dev/` (`brief-`, `flight-`, `hotspot-1/2/3-`,
  `flow-`, `readings-`, `demo-`, `return-`, `fallback-`; `verification.json`, `fallback-verification.json`).
  Ini belum paket gate Testing; copy belum di-approve. Next menuju chapter SurgeLine homepage;
  rantai case-to-case Fase 5. Tes HP fisik/performa tetap fase yang sudah dijadwalkan.

### Fase 5 — All case files
Development (Codex / Claude Code):
- [x] Case file SurgeLine, DriftWatch, DueWatch, BrandWall
- [x] "Next instrument" berantai; copy DRAFT → `ready-for-test`

Bahan handoff Fase 5 Development (2026-09-15, Claude Code):
- Lokal `http://127.0.0.1:8767/work/<slug>` atau chapter mana pun → Open case file. Server produksi aktif, tunnel mati.
- Satu template untuk 5 case (`lib/cases.ts` + `components/case-file.tsx` + `/work/[slug]`); dialog preview dihapus.
  Next berantai CrossCheck → … → BrandWall → CrossCheck: kamera mundur, menyapu ke instrumen berikut, lalu terbang masuk.
- Copy 4 case baru **DRAFT** (label di halaman); sumber per angka di `web/README.md` (Phase 5). Blok Next CrossCheck ikut berubah
  ("Open the next case file" → case SurgeLine) — perlu approve juga.
- Video explainer asli 4 project disalin byte-identik (0 audio). **Keputusan pemilik:** video DueWatch memuat caption
  "Seven days in a row. Nobody had to remember." di atas tanggal simulasi (temuan self-review DueWatch); case menyebutnya di bawah video.
  Opsi: terima dengan catatan, buang video, atau potong ulang di project DueWatch.
- Verifikasi: lint/typecheck/build exit 0; `verify_cases.py` passed 390×844 → 360×740 → 430×932 (buka + Return ×5, rantai penuh + wrap,
  Back/Forward, 5 direct URL, slug asing 404, fallback, angka ada di dossier); `verify_case.py` + `verify:mobile` passed. Nol error/HTTP ≥400.
- Batas: emulasi Chromium; leader DueWatch mengikuti planet yang mengorbit (kadang melintas instrumen, sengaja). fps/HP fisik = Fase 7/8.

Testing (Claude Code / Antigravity):
- [x] Tes otomatis 5 case file + rantai Next; bug diperbaiki + tes ulang
- [x] Paket bukti `assets/renders/case-files/evidence/` dikirim (17/17 pass)
- [x] Semua copy case file di-approve (SurgeLine, DriftWatch, DueWatch, BrandWall + blok Next CrossCheck; label DRAFT dilepas, 2026-09-15)
- [x] Gate: pemilik menyatakan lolos (2026-09-15, "semuanya lulus dan approved, duewatch opsi no 1"; dinilai dari video + foto bukti)

Bahan gate Fase 5 (Testing, 2026-09-15):
- **Paket bukti:** folder `assets/renders/case-files/evidence/`
  - Video walkthrough: `case-files-walkthrough.mp4` (H.264 390×844, 130.4 s, alur penuh: Gate → CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall → CrossCheck wrap → Return → history → SurgeLine return).
  - Contact sheet: `contact-sheet.jpg` (2340×3376, 24 frame berlabel alur kunci).
  - Viewport sheet: `viewports/viewports-sheet.jpg` (1170×2532, 3 viewport × 3 segmen).
  - Data hasil uji: `evidence.json` (17/17 pass, status `passed`).
- **Verifikasi otomatis:**
  - 5 case files mengikuti template PLAN §7, 1 Canvas persisten, 0 error console/page, 0 HTTP ≥ 400, nol horizontal overflow.
  - 15 component cards (3 per instrumen) tap target ≥ 44px, card pas di viewport; leader lines terproyeksi dari 3D node tanpa memotong geometri.
  - Readings animasi count-up terverifikasi verbatim ke 5 dossier CAPABILITY; limits disclosure membuka catatan batasan.
  - Video explainer 5 project: lazy loading (hanya unduh saat play), 0 audio streams, durasi akurat (115.2s, 118.2s, 102.5s, 125.0s, 126.9s), poster custom.
  - Rantai Next instrument berputar penuh: CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall → CrossCheck (wrap).
  - Flight-in & Return: kamera terbang masuk & mundur, scroll terkunci saat terbang, scroll position & focus pulih di homepage.
  - History browser: Back/Forward navigasi antar case dan homepage aman tanpa kehilangan state Canvas.
  - Fallback: model diblokir → still view berlabel + background fallback PNG + kartu & return tetap berfungsi.
  - Viewports: lolos di 390×844, 360×740, dan 430×932.
- **Catatan temuan untuk keputusan pemilik:**
  - Video DueWatch memuat caption *"Seven days in a row. Nobody had to remember."* di atas tanggal simulasi (temuan self-review dossier §7 finding 4). Case file mencatat hal ini di bawah video. Opsi pemilik di gate: (A) terima dengan catatan yang ada, (B) lepas video, atau (C) potong ulang di project DueWatch.

### Fase 6 — Desktop
Development (Codex / Claude Code):
- [x] Layout desktop homepage + case file (komposisi lebar) → `ready-for-test`

Bahan handoff Development (2026-09-15, Codex):
- Preview produksi aktif `http://127.0.0.1:8767/`; homepage → Work atau `/work/<slug>`.
  Bila server berhenti: `npm run start --prefix web` (build sesi ini sudah dibuat).
- Desktop mulai 1024px: hero/chapter teks kiri + model besar kanan; header Work/About/Contact;
  Skills/About/Contact lebar; case brief dua kolom, hotspot + kartu samping, flow mendatar, readings/tools grid.
- Lint/typecheck/build exit 0; `verify:mobile` dan `verify_case.py` passed 390×844 → 360×740 → 430×932.
  `verify_desktop.py` passed 390×844 → 1366×768 → 1440×900 → 1920×1080; lima case + rantai Next/wrap/history,
  navigasi desktop, hotspot/leader, fallback, satu Canvas, nol overflow/error/HTTP ≥400 alur normal.
  `--breakpoints-only` passed resize 768→1024→1440→390; `--hotspots-only` memperbarui foto setelah warna marker stabil. Foto/JSON di `assets/renders/desktop/dev/`.
- Copy/angka approved tetap; PLAN tidak diubah. Peta/README basi tentang DRAFT Fase 5 dibetulkan.
  Bukti Development berupa PNG/JSON; paket MP4/contact sheet + gate tetap tahap Testing di bawah.

Testing (Claude Code / Antigravity):
- [x] Tes otomatis viewport laptop/monitor (1366×768, 1440×900, 1920×1080) + HP tidak rusak; bug diperbaiki + tes ulang
- [x] Paket bukti `assets/renders/desktop/evidence/` (video 1440×900) dikirim
- [x] Gate: pemilik menyatakan lolos (2026-09-15, "okay semuanya lolos catat"; dinilai dari video bukti)

Bahan gate Fase 6 (Testing, 2026-09-15): folder `assets/renders/desktop/evidence/` — `desktop-walkthrough.mp4`
(H.264 1440×900), `contact-sheet.jpg` (24 frame), `viewports/desktop-sheet.jpg`, `viewports/resize-sheet.jpg`,
`phones/phones-sheet.jpg`, `evidence.json` (21 item). Skrip `web/scripts/desktop_evidence.py`.
- Bug diperbaiki: About/Skills desktop — baris grid meregang setinggi portrait/accordion (paragraf About berjarak ±115px) → `grid-template-rows: auto auto auto 1fr`.
- Regresi build baru, dijalankan sendiri-sendiri: `verify_desktop` (4 ukuran + fallback), `verify:mobile`, `verify_case`, `verify_cases` pass; lint/typecheck/build exit 0.
  Saat 5 suite GPU dijalankan beruntun, `verify_desktop`/`verify:mobile` sempat timeout (timing, bukan bug), lalu lolos saat diulang.
- Temuan diterima apa adanya di gate: layar pertama case desktop = brief dua kolom, ±40% bawah kosong, instrumen di bawah lipatan.
- Batas: emulasi Chromium GPU; fps/HP fisik = Fase 7/8.

### Fase 7 — Showpiece polish
Development (Codex / Claude Code):
- [x] Sound design lengkap (klik instrumen, transisi)
- [x] Micro-interaksi, loader final, transisi dihaluskan → `ready-for-test`
- [x] **Enter aktif lebih cepat** (keputusan pemilik 2026-09-16, opsi B, PLAN §3 Q37): Enter aktif setelah hero siap
  (kubah + Saturnus + font); lima instrumen dimuat di belakang hero → `ready-for-test`

Bahan handoff "Enter aktif lebih cepat" (2026-09-16, Claude Code):
- Diukur (skrip `perf_gate` yang sama, 390×844, cache mati): DevTools Slow 4G + CPU 4× → Enter aktif **12.46 → 7.01 dtk**;
  profil 150 ms → **8.46 → 5.30 dtk**. Gate tampil tetap ±1.5 dtk. Transfer sebelum Enter 1,370,869 → 787,063 B.
- Empat langkah, masing-masing diukur: instrumen dimuat sesudah hero (9.70 dtk) → dome + planet paralel + preload GLB/Draco
  dari HTML (8.71) → Scene impor statis, chunk three ikut JS pertama (6.99) → font WOFF2 subset 253 KB → 60 KB (7.01; ukur akhir).
- Font: bentuk sama (subset Latin dari TTF approved, glyph terpakai utuh, dicek per karakter); screenshot gate sama.
- Perilaku baru: chapter/case bisa sebentar tanpa model bila di-scroll sebelum lima instrumen selesai (±2–3 dtk di slow 4G);
  model gagal sesudah Enter → still view + notice seperti biasa. Label "Instruments calibrated" tidak diubah.
- Verifikasi: lint/typecheck/build exit 0; `verify_audio` 9/9; `verify:mobile`, `verify_case`, `verify_cases`, `verify_showpiece`
  (3 HP) + `verify_desktop` (390/1366 lalu 1440/1920, dua run) passed. Tes fallback kini menunggu `data-scene=fallback`.
- Untuk Testing: teks `perfGate`/`FINDINGS` di `showpiece_evidence.py` sudah disesuaikan; logika ukur sama. Batas: emulasi Chromium, GPU host tidak di-throttle.

Spesifikasi item "Enter aktif lebih cepat" (arsip; dikerjakan 2026-09-16):
- Data ukur Testing 2026-09-15 (DevTools Slow 4G + CPU 4×, 390×844): gate tampil 1.4 dtk, **Enter aktif 12.2 dtk**
  (profil 150 ms: 8.6 dtk). Transfer sebelum Enter 1,370,869 B = 3D 523 KB, JS 514 KB, font 253 KB, Draco 64 KB, HTML/CSS 17 KB.
  Lima GLB instrumen = 546 KB mentah dari 737 KB; kubah + planet 191 KB.
- Penyebab: `World` di `observatory-scene.tsx` memanggil `useGLTF` untuk ketujuh GLB dalam satu `<Suspense>`; `onReady` (frame ke-2)
  baru jalan setelah semuanya termuat. Shell: `ready = fontsReady && (sceneReady || failed)`.
- Arah: pisahkan muat hero (dome + ambient) dari lima instrumen. Instrumen di Suspense sendiri dan baru diminta setelah hero tampil
  (tidak berebut bandwidth). `views`, tap BrandWall, `anchor`/leader dan visibilitas group harus aman selama instrumen belum ada
  (chapter/case sementara tanpa model), termasuk direct URL `/work/<slug>`.
- Model instrumen gagal kini bisa terjadi **sesudah** Enter → tetap jatuh ke still view (`failed`) + notice, seperti sekarang.
- Tes yang mengecek fallback langsung setelah Enter perlu menunggu `data-scene=fallback`: `verify_mobile.py:59`, `verify_case.py:170`,
  `verify_cases.py:191` (`verify_desktop.py:169` sudah menunggu). Label gate "Instruments calibrated" = copy approved, jangan diubah
  tanpa izin pemilik (cek `showpiece_evidence.py` item loader).
- Opsional bila masih kurang cepat, ukur dulu: font TTF → WOFF2 (253 KB), chunk JS three terbesar 710 KB mentah / 193 KB gzip.
- Ukur sebelum/sesudah dengan `showpiece_evidence.py` (item `perfGate`, `enterEnabledMs`); jangan klaim angka tanpa ukur.
- Selesai: lint/typecheck/build + suite regresi (CODEMAP §2; GPU satu per satu, foreground ≤10 menit) → `ready-for-test`.

Bahan handoff Fase 7 Development (2026-09-15, Codex + Claude Code):
- Preview produksi `http://127.0.0.1:8767/` (build ulang sesi ini). Bila mati: `npm run start --prefix web`.
- Suara sintetis (tanpa berkas audio): hum + klik 5 nada per instrumen (hotspot/close/menu/summary/BrandWall tap),
  sweep welcome/fly-in/Return/Next dua bagian. Silent entry = tanpa AudioContext; mute/tab tersembunyi = tanpa efek.
- Loader: dial SVG + beacon, progres tak mundur antar batch GLB, hijau saat siap / amber saat still view.
  Tombol press `scale`, hover hanya pointer fine, leader/kartu aktif, menu entrance, satu timeline departure yang batal saat Back.
- Verifikasi: lint/typecheck/build exit 0; `verify_audio.mjs` 9/9; `verify_showpiece.py` passed 390×844 → 360×740 → 430×932;
  regresi `verify:mobile`, `verify_case.py`, `verify_desktop.py` (HP + 1366/1440/1920) passed. Foto/JSON `assets/renders/showpiece/dev/`.
- Copy/angka tidak berubah. Batas: emulasi Chromium GPU; belum ukur fps/4G/CPU throttle (tugas Testing) dan belum dengar di speaker HP.

Testing (Claude Code / Antigravity):
- [x] Performa sesuai target PLAN §11 lewat emulasi (CPU throttle + 4G lambat, fps, ukuran aset)
- [x] Paket bukti `assets/renders/showpiece/evidence/` dikirim (13/13 pass)
- [x] Tes ulang setelah fix "Enter aktif lebih cepat" (perfGate + regresi), paket bukti diperbarui (14/14 pass)
- [x] Gate: pemilik menyatakan lolos (2026-09-16, "lolos commit dan push"; dinilai dari video + foto bukti);
  temuan jeda instrumen ±3 dtk (chapter/case sempat tanpa model, garis penunjuk case bertemu di ruang kosong) diterima apa adanya

Bahan gate Fase 7 (Testing ulang, 2026-09-16 — paket berlaku): folder `assets/renders/showpiece/evidence/` —
`showpiece-walkthrough.mp4` (H.264 + AAC 390×844, 105.9 dtk, suara asli situs), `contact-sheet.jpg` (26 frame),
`15-enter-early.png` (item baru), `01-loader.png`, `05-flight-in.png`, `11-perf-gate.png`, `12-perf-fps.png`,
`13-micro.png`, `14-sound-control.png`, `phones/phones-sheet.jpg`, `evidence.json` (14/14 pass).
- Enter lebih cepat terbukti: gate tampil 1.41 dtk, **Enter aktif 6.39 dtk** (arsip 12.2), transfer sebelum Enter
  787,063 B (arsip 1,370,869). Profil 150 ms: tampil 0.57 dtk, aktif 5.16 dtk.
- Item baru `enterEarly`: sebelum Enter hanya kubah + Saturnus terunduh; lima GLB instrumen mulai 6.43 dtk (sesudah Enter)
  dan selesai +3.0 dtk. Scroll ke chapter dalam jeda itu → copy kebaca, nol error, model muncul sendiri; direct
  `/work/crosscheck` → heading kebaca, leader line menyambung ke model saat tiba. Scene tetap `ready`.
- Item lain tetap lolos: loader monotonik 0→100 + hijau, suara masuk/klik 5 nada (660/520/440/780/880 Hz)/sweep/mute,
  micro-interaksi, transisi + rantai lima case, fps 4× 56–60 (min 45), 3D 737 KB (batas 8 MB), GLB terbesar 317 KB, DPR ≤1.5×,
  dua HP lain, nol error/HTTP ≥400/overflow.
- Regresi diulang di build ini, semua `passed`: `verify_audio` 9/9, `verify:mobile`, `verify_case`, `verify_cases`,
  `verify_showpiece`, `verify_desktop` (390×844+1366×768 lalu 1440×900+1920×1080; JSON memuat run terakhir). lint/typecheck exit 0.
- **Temuan untuk pemilik (bukan fail otomatis):** selama ±3 dtk sebelum instrumen tiba, chapter/case tampil tanpa model —
  di case, tiga garis penunjuk sempat bertemu di ruang kosong (frame "Case opened early"). Ini konsekuensi opsi B.
  Pilihan: terima, atau kembali ke Development (mis. sembunyikan garis sampai model ada).
- Batas: emulasi Chromium GPU; GPU host tidak di-throttle; HP fisik = Fase 8.

Bahan gate Fase 7 (Testing, 2026-09-15 — arsip; diulang setelah fix Enter): folder `assets/renders/showpiece/evidence/` — `showpiece-walkthrough.mp4`
(H.264 390×844 **dengan suara asli situs**), `contact-sheet.jpg` (24 frame), `01-loader.png`, `05-flight-in.png`,
`11-perf-gate.png`, `12-perf-fps.png` (grafik frame), `13-micro.png`, `14-sound-control.png`, `phones/phones-sheet.jpg`, `evidence.json`.
- Performa (emulasi HP, CPU 4×): gate tampil 1.4 dtk di slow 4G (target < 2.5); fps 56–60 di semua segmen (min 45);
  3D total 737 KB (batas 8 MB), GLB terbesar 317 KB (batas 1.5 MB); pixel ratio 3D maks 1.5×. Stres CPU 6×: 52–60 fps.
- Suara: nada klik beda per instrumen (660/520/440/780/880 Hz), sweep fly-in/Next/Return, mute langsung sunyi + diingat.
- **Temuan untuk pemilik (bukan fail otomatis):** tombol Enter baru bisa ditekan ±12 dtk di slow 4G (menunggu 7 model + font,
  1.37 MB). Opsi: terima, atau kembali ke Development agar Enter aktif lebih cepat. → **Pemilik pilih B (2026-09-16).**
- Bug tes diperbaiki (bukan bug situs): `verify_desktop` timeout 1440×900 karena ekor animasi Lenis menimpa `scrollTo`.
- Batas: emulasi Chromium; GPU laptop tidak di-throttle (beban GPU HP belum terwakili); HP fisik = Fase 8.

### Kontrak pengerjaan Fase 7A–7F

Fase 0–7 di atas adalah riwayat implementasi dan gate lama. Revisi Q41 dimulai di bawah;
semua checkbox baru sengaja kosong. Setiap tahap memakai aturan Development/Testing PLAN §12.

| Fase | Mobile: implementasi + verifikasi | Desktop: komposisi + polish | Regresi mobile sesudah desktop |
|---|---|---|---|
| 7A CrossCheck | lolos Testing + gate 2026-09-16 (390/360/430 + 768) | lolos Testing + gate 2026-09-16 (1440/1920) | lolos 2026-09-16 |
| 7B SurgeLine | lolos Testing + gate 2026-09-17 (390/360/430 + 768) | lolos Testing + gate 2026-09-17 (1440/1920) | lolos 2026-09-16; ulang pasca-gate 2026-09-17 |
| 7C DriftWatch | lolos Testing + gate 2026-09-17 (390/360/430 + 768) | lolos Testing + gate 2026-09-17 (1440/1920) | lolos 2026-09-17 ulang pasca-fix; ulang pasca-gate (`monitor`, `cases`/`mobile` 390×844) |
| 7D DueWatch | lolos Testing 2026-09-17 + gate 2026-09-18 (390/360/430 + 768) | lolos Testing 2026-09-17 + gate 2026-09-18 (1440/1920) | runner 16/16 passed 2026-09-17; ulang pasca-gate (`time`, `cases`/`mobile` 390×844) |
| 7E BrandWall | Development lolos 2026-09-18 (390/360/430 + 768); Testing Q47 390×844 lolos + gate 2026-09-24 | Development lolos (1440/1920, `studio`); Testing Q47 1440×900 lolos + gate 2026-09-24 | runner 2026-09-24 passed; ulang pasca-gate 11 suite + `perf-brandwall` (sumber `4bf13e4158597b83`) |
| 7F Integrasi lima project | Development 2026-09-24: 390/360/430 + 768 lolos (suite `room`/`dispatch`/`monitor`/`time`/`studio`/`mobile`/`cases`) | Development 2026-09-24: 1440/1920 lolos (suite fase + `desktop-a/-b`); fix lompatan copy CrossCheck | runner 18/18 sesudah fix desktop (sumber `2e90c092c607038b`); Testing penuh 2026-09-24: 390×844 + 1440×900 walkthrough, 6 viewport dari suite dev sidik jari sama, paket 17/17 |

**Wajib dalam setiap checklist Testing di bawah:**

1. Uji semua item Development pada mobile 390×844 → 360×740 → 430×932, kemudian tablet
   768×1024 dan desktop 1440×900/1920×1080; ulang regresi mobile sesudah perubahan desktop.
2. Uji chapter → case, direct URL/refresh, hotspot, interaksi penjelas, Next, Back/Forward,
   kembali ke posisi homepage, scroll balik, tap cepat, resize, serta model lambat/gagal.
3. Periksa keterbacaan, overflow/overlap, fokus interaksi, console/request gagal, dan performa
   terhadap PLAN §11. Laporkan angka aktual dan keterbatasan rig; jangan klaim lancar dari build.
4. Rekam walkthrough mobile **dan** desktop, PNG per item, contact sheet, `evidence.json`
   dengan pass/fail cerita/visual/animasi/transisi/mobile/desktop/sumber. Lihat motion normal
   dan lambat; bukti harus memperlihatkan ciri project aktif, bukan hanya halaman terbuka.
5. Development selesai → `ready-for-test`; Testing + paket bukti → `awaiting-gate`;
   approve copy baru + gate pemilik → `done`. Jangan meluluskan fase dari bukti lama.
6. **Efisiensi tes (Q42, mulai 7B; detail PLAN §12.3):** Development menjalankan `perf_quick.py --slug <project>`
   sebelum `ready-for-test`; regresi selalu lewat `run_regressions.py` (suite yang sudah lolos pada sumber yang sama
   dilewati; setelah fix hanya yang belum hijau); skrip bukti Testing memanggil tes dev fase aktif di dalam paket;
   suite fase lama `--phone-only` (390×844).
7. **Testing ringan (Q47, mulai 7E Testing; detail PLAN §12.3):** mengganti poin 1–4 untuk 7E: uji hanya item baru fase aktif di
   390×844 + 1440×900; regresi suite fase aktif + `cases`/`mobile` 390×844 (suite lain bila berkas bersama disentuh); paket = video HP +
   video desktop ≤ ±90 dtk, PNG per item, satu contact sheet, `evidence.json`; slow-motion hanya bila ada temuan motion; fps dari
   `perf_quick.py` Development. 7F dan Fase 8 tetap putaran penuh.

### Fase 7A — CrossCheck: inspection room

Sumber: `portfolio/CAPABILITY_CROSSCHECK.md` §1–4, §7, §9. Brief desain: PLAN §5.1.
Target: pengunjung memahami cakupan tes → sinyal → temuan yang bisa direproduksi.

Development (Codex / Claude Code), **urut mobile → desktop**:
- [x] Baca dossier + implementasi terkait dari CODEMAP; tulis brief personal dan peta sumber
  copy DRAFT: 1,080 kombinasi, 881 sinyal → 18 isu, 12/12 bug tertanam; target demo milik sendiri
- [x] Mobile: chapter teleskop dan case menjadi ruang inspeksi; matriks bertahap, kartu temuan
  dengan bukti/reproduksi; hotspot menjelaskan pemeriksaan, bukan deskripsi mesin generik
- [x] Animasi scan tiga jalur browser → kelompok sinyal → temuan; pilih temuan menyorot bukti;
  definisikan trigger, easing/durasi, state akhir, scroll balik dan interupsi
- [x] Transisi lensa → bidang inspeksi, return ke chapter asal, pengantar Next ke SurgeLine;
  fallback tidak meninggalkan hotspot menunjuk ruang kosong
- [x] Verifikasi mobile selesai sebelum desktop; catat hasil pada tabel kemajuan
- [x] Desktop: meja inspeksi lebar, matriks dan bukti berdampingan, framing teleskop/cahaya
  presisi; komposisi 1440/1920 sengaja dirancang untuk presentasi utama
- [x] Regresi mobile, lint/typecheck/build + tes fokus; catat sumber copy/bukti → `ready-for-test`


Bahan handoff 7A Development (2026-09-16, Claude Code):
- **Preview:** `http://127.0.0.1:8767/` → chapter CrossCheck → Open case file (atau `/work/crosscheck`). Server mati → `npm run build --prefix web && npm run start --prefix web`.
- **Brief + peta sumber copy DRAFT:** `web/README.md` bagian Phase 7A. Copy baru: strip lane, 3 body hotspot, readout 4 step,
  heading/intro/4 temuan (CC-003, CC-001, CC-017, CC-015), label bingkai desktop. Deck/brief/readings/tools/video/judul-body 4 step tetap approved; teaser Next memakai deck SurgeLine approved.
- **Bukti = data asli, bukan karangan:** `build_crosscheck_run.py` membaca hasil run CrossCheck dan menolak menulis bila total ≠ dossier (1,080 / 422 / 877 / 40 / 216→3 / 5→1 / 18 = 3·14·1). Screenshot temuan = crop gambar bukti proyek sendiri (V4 before/after 1–3 + screenshot flow langkah gagal).
- **Yang dibangun:** chapter → strip 3 lane × 9 sel terisi mengikuti orbit, lane menyala sinkron lensa (rig `onScan`), hijau saat ketiga lensa sepakat.
  Masuk: iris keluar dari lensa tengah (grid inspeksi + garis bidik) menutup layar, case terbuka dari titik yang sama; Return: case menutup ke lensa, dibuka lagi di lensa chapter; Back saat terbang aman.
  Case: leader hanya tampil saat model terproyeksi (fallback/jeda model tak lagi menunjuk ruang kosong); hotspot = hasil inspeksi; **Inspection field** sticky: map → scan tiga jalur (1,080 sel run asli) → sort (baris tanpa isu jadi abu, duplikat memadat) → 18 chip isu; fungsi murni progress (mundur membalik, flick tak mengantre), reduced motion = state akhir. **Finding desk:** 4 temuan, tap → strip bukti menyala (matrix 9/27 sel, access 2 dari 3 pelanggaran, flow 1/5), screenshot + toggle before/expected (HP) atau berdampingan (desktop), langkah reproduksi, expected/actual. Desktop: rail step kiri + matriks berlabel route, meja temuan dua kolom, bingkai bidik teleskop.
- **Verifikasi:** lint/typecheck/build exit 0. `verify_crosscheck_room.py` passed 390×844 → 360×740 → 430×932 → 768×1024 → 1440×900 → 1920×1080 + edge (Back saat terbang, `ambient.glb` diblok, reduced motion);
  regresi `verify_case`, `verify_cases`, `verify:mobile`, `verify_desktop` (390+1366, 1440+1920), `verify_showpiece`, `verify_audio` 9/9 passed. Foto/JSON `assets/renders/personal-crosscheck/dev/`.
- **Perbaikan rig (bukan situs):** path dossier 4 skrip → `portfolio/` root (Q41); tunggu ekor Lenis di `verify:mobile` (readout 100%) + `verify_showpiece` (origin return) — keduanya gagal identik di HEAD `ac01ca4` sebelum 7A.
- **Ukur (emulasi Chromium 390×844, scrollTo tiap frame, 6 dtk):** CPU 1× 60 fps datar; CPU 4× scrub matriks 243 frame (±40 fps rata-rata, median 16.7 ms, p95 33 ms) vs pembanding scroll bagian lain 264 frame (±44 fps) → tambahan biaya matriks ±8%. Metode ini lebih berat dari swipe CDP Fase 7; Testing mengukur ulang dengan metode Fase 7 dan mencatat selisih §11.
- **Untuk Testing/pemilik:** arsip bukti lama (`case_crosscheck_evidence.py`, `case_files_evidence.py`, `desktop_evidence.py`) masih mengharapkan `.signal-flow` / tanpa DRAFT untuk CrossCheck → perlu skrip bukti 7A baru. Still view fallback CrossCheck masih render teleskop lama (PNG approved) — marker tanpa leader. Keputusan desain terbuka: iris memakai warna ink + grid tipis (bukan warna baru).

Testing (Claude Code / Antigravity):
- [x] Jalankan seluruh kontrak Testing 7A–7F; matriks/temuan tetap jelas tanpa hover (semua interaksi diuji dengan tap/touch)
- [x] Bukti menunjukkan identitas inspeksi, scan bermakna, entry/return mulus dan desktop matang;
  paket `assets/renders/personal-crosscheck/evidence/` dikirim → `awaiting-gate` (16/17 pass; `performance` fail ketat, temuan 1)
- [x] Copy baru di-approve + gate personalisasi CrossCheck lolos (2026-09-16, "lulus semua aman"; label DRAFT dilepas; temuan 1–2 diterima apa adanya)

Bahan gate 7A (Testing 2026-09-16, Claude Code) — folder `assets/renders/personal-crosscheck/evidence/`:
- **Video:** `walkthrough-mobile.mp4` (390×844 touch, 266 dtk), `walkthrough-desktop.mp4` (1440×900 wheel + resize, 80 dtk),
  `slow-motion.mp4` (0.25×, 147 dtk: iris masuk/kembali HP + desktop, scroll balik membalik scan, tap cepat, resize 1440→390→1440).
  Tanpa suara (masuk silent; suara sudah diuji Fase 7). **Foto:** `contact-sheet-mobile.jpg` (26 frame), `contact-sheet-desktop.jpg` (16),
  strip per item `i01`…`i12`, grafik `p01-fps-4x.png`, per-viewport `viewports/`; `evidence.json` pass/fail per item + per kategori.
- **Kategori:** cerita ✔ · visual ✔ · animasi ✔ · transisi ✔ · desktop ✔ · sumber ✔ · mobile ✘ + performa ✘ (keduanya hanya karena item `performance`).
- Item lolos: story, chapterScan (0 → 27 sel ikut orbit, balik ke 12), irisEntry (disc → hole → hidden, fokus heading, HP + desktop), hotspots,
  inspectionField (maju 0→3, balik 3→1 chip 0, flick 5 lompatan tepat), findingDesk (hit 1/2/9/27, toggle HP, berdampingan desktop), returnNext (±0 px,
  fokus Open case file, Next → SurgeLine), historyDirect (Back/Forward, direct + refresh), interruptions (double tap +1 history, tap cepat → tap terakhir,
  Back saat terbang, resize lintas 1024 progres tetap), modelSlowFail (leader tak pernah tampil sebelum model terproyeksi; `ambient.glb` diblok → still view, ruang tetap terbaca),
  reducedMotion, 4 HP/tablet + 1440/1920, sources (15/15 klaim → dossier / skrip video proyek; data run ulang byte-identik), clean (1 Canvas, 0 error, 0 ≥400, 0 overflow),
  regressions (8 suite di build final).
- **Bug ditemukan + diperbaiki di Testing:** (a) **regresi fps 7A** — scene menulis `--aperture-x/y` ke `.observatory` tiap frame (lensa berayun) → style recalc seluruh halaman.
  Diukur bergantian vs build HEAD `ac01ca4` (4× CPU, swipe): 7A 31–43 fps vs HEAD 57–60. Fix: posisi lensa di objek JS `apertureScreen` (`lib/cases.ts`) → chapter/readings kembali 56–60.
  (b) Scrub matriks: chip tidak lagi `scale` (glyph dirasterisasi ulang tiap frame) — chip kini meluncur + fade; fade SVG pakai `fill-/stroke-opacity`; sel `shape-rendering: crispEdges`
  → beat hand 46 → 55 fps. Semua suite + paket bukti diulang sesudah fix.
- **Temuan untuk pemilik (keputusan):**
  1. **Performa scrub field** (4× CPU, HP emulasi): 52–54 fps rata-rata, tapi 11–13% frame > 22 ms (p95 33 ms) → gagal aturan ketat Fase 7 (p95 ≤ 22 ms); segmen lain 52–59 fps lolos.
     Pilihan: terima (rata-rata ≥ 45, setara chapter), atau kembali ke Development: pisahkan chip ke lapisan komposit + redupkan matriks lewat opacity elemen.
  2. **Crop "Expected" CC-001** = teks "Forbidden: settings require administrator privileges" ±6 px di HP → tampak kotak putih kosong (bukti asli, tidak diubah).
     Pilihan: terima (expected tertulis di bawahnya), atau crop lebih rapat ke notice.
  3. Perubahan gerak kecil dari fix: chip isu kini meluncur tanpa membesar. Still view fallback masih teleskop PNG lama (catatan Development).
- Batas: Chromium GPU emulasi lokal; GPU host tidak di-throttle; HP fisik = Fase 8.

### Fase 7B — SurgeLine: dispatch room

Sumber: `portfolio/CAPABILITY_SURGELINE.md` §1–4, §7, §9. Brief desain: PLAN §5.2.
Target: pengunjung melihat bagaimana pekerjaan lanjut setelah crash tanpa pengiriman ganda.

Development (Codex / Claude Code), **urut mobile → desktop**:
- [x] Brief dan copy personal DRAFT: 50,000 input → 49,950 unik; 48,273 terkonfirmasi,
  844 ditolak, 833 dead-letter; dua kill, nol duplikat. Nyatakan target lokal dan batas estimasi 6M
- [x] Mobile: chapter antena + alur vertikal case dari spreadsheet sampai konfirmasi;
  kontrol demonstrasi crash/resume lewat tap, hasil gagal tetap terlihat dan beralasan
- [x] Animasi record/pekerja/pulsa → satu jalur putus → resume tanpa mengulang record sukses;
  tetapkan trigger, timing, state akhir dan interupsi, tandai ilustrasi sebagai demonstrasi
- [x] Transisi mengikuti pulsa antena; return menjaga orientasi; Next memperkenalkan DriftWatch
- [x] Verifikasi mobile selesai sebelum desktop; catat hasil pada tabel kemajuan
- [x] Desktop: jalur pekerja paralel lebar, area crash/resume dan hasil berdampingan;
  ritme pengiriman tegas, bukti tetap terbaca saat aliran bergerak
- [x] Regresi mobile, lint/typecheck/build + tes fokus; sumber copy/bukti → `ready-for-test`

Bahan handoff 7B Development (2026-09-16, Codex → Claude Code):
- **Preview:** `http://127.0.0.1:8767/` → chapter SurgeLine → Open case file (atau `/work/surgeline`). Server mati → `npm run build --prefix web && npm run start --prefix web`.
- **Brief + peta sumber copy DRAFT + kontrak motion:** `web/README.md` bagian Phase 7B. Copy baru DRAFT: strip chapter, body 3 hotspot, intro/steps/label papan/narasi 5 stage/ledger, bukti rekaman, teaser DriftWatch. Record A–F dan receipt DEMO-* fiktif, dilabeli ilustrasi; angka run (50,000 → 49,950; 10,621 → 21,508 → 48,273; 844 / 833; 0 duplikat; 7 pulih; 6M estimasi 3.0/4.1 hari, tidak pernah dijalankan) dari dossier §3–4, §6 K1–K7, §7, §9.
- **Yang dibangun:** chapter → strip 3 browser × 8 record ikut orbit (amber terkirim → hijau receipt), lane 2 beku + `cut` di orbit .35–.6 lalu `resumed`, scroll balik membalik. Masuk/kembali: 3 cincin pulsa dari antena. Case: **papan dispatch** — Start (A → Confirmed, C → Rejected dengan getar di Form, B menunggu receipt), Cut (B beku merah putus-putus, lane 2 offline, A/C tetap), Resume (klaim kedaluwarsa, B kembali ke antrean, dikirim lagi `×2` → Confirmed; D/E jalan; F dicoba 5× → Dead-letter; A tidak bergerak), Replay eksplisit. Ledger per record + alasan; bukti rekaman terpisah dari ilustrasi. HP: papan + tombol dalam satu layar 390×844. Desktop: steps satu baris, papan lebar kiri→kanan, control di samping ledger 2 kolom.
- **Fix performa (shell):** var CSS scroll (`--journey`, hero, reveal/offset, orbit) pindah dari root ke elemen konsumennya. 4× CPU 390×844 (`perf_quick.py`): SurgeLine chapter 48.7 → **60.0 fps** (lambat 23% → 0%), terbang 55.7, demo crash/resume 59.8, scroll case 59.7, return 58.0; CrossCheck chapter 55.9 → 59.8. Rig: iGPU Intel headless, bukan HP fisik.
- **Verifikasi:** lint/typecheck/build exit 0. `run_regressions.py --phone-only room,mobile,case,cases,showpiece` di sumber `c78f440b40bb069d`: dispatch (6 viewport + edge back/resize saat resume/fallback/reduced), perf-surgeline, room, audio, mobile, case, cases, showpiece, desktop-a, desktop-b passed; perf-crosscheck gagal tipis sekali (return 44.7) → ulang `--force` passed (49.6). Foto/JSON `assets/renders/personal-surgeline/dev/`.
- **Untuk Testing/pemilik:** (1) arsip bukti lama (`case_files_evidence.py`, `desktop_evidence.py`) masih mengharapkan `.signal-flow` SurgeLine → paket 7B perlu skrip baru. (2) Keputusan desain terbuka: Cut boleh ditekan sebelum B sampai Form (B membeku di tengah jalur, tetap "stranded"). (3) Tanpa JS chip papan bertumpuk di pojok (halaman butuh JS untuk masuk, dampak kecil).

Testing (Claude Code / Antigravity):
- [x] Jalankan seluruh kontrak Testing 7A–7F; simulasi resume tidak menggandakan hasil visual (jejak per frame, HP tap + desktop klik)
- [x] Bukti membedakan selesai diproses dari sukses terkonfirmasi; motion antrean dan entry/return
  dinilai di dua device; paket `assets/renders/personal-surgeline/evidence/` → `awaiting-gate` (18/18 pass)
- [x] Copy baru di-approve + gate personalisasi SurgeLine lolos (2026-09-17, "lulus semua"; temuan Cut sebelum Form diterima)

Bahan gate 7B (Testing 2026-09-16, Claude Code) — folder `assets/renders/personal-surgeline/evidence/`:
- **Video:** `walkthrough-mobile.mp4` (390×844 touch, 152 dtk), `walkthrough-desktop.mp4` (1440×900 wheel/klik + resize, 80 dtk),
  `slow-motion.mp4` (0.25×, 135 dtk: pulsa masuk/kembali HP + desktop, Start → Cut, Resume tanpa kirim ulang A, Cut sebelum Form, resize saat pemulihan).
  Tanpa suara. **Foto:** `contact-sheet-mobile.jpg` (28 frame), `contact-sheet-desktop.jpg` (18), strip per item `i01`…`i13`, grafik `p01-fps-4x.png`,
  `viewports/` (6 viewport + fallback/reduced); `evidence.json` pass/fail per item + kategori + `forOwner`.
- **Kategori:** cerita ✔ · visual ✔ · animasi ✔ · transisi ✔ · mobile ✔ · desktop ✔ · sumber ✔ · performa ✔ (18/18 item).
- Item lolos (ringkas): chapterStrip (lane 2 beku 7.4 selama orbit .39–.56 + `cut`, akhir tiga lane hijau + `resumed`, balik membalik; HP swipe + desktop wheel),
  pulseEntry (3 cincin bertingkat ±680 ms dari antena, fokus heading), hotspots, dispatchDemo (C getar 3 balikan → Rejected, B menunggu dengan cincin, Cut membekukan B,
  lane 2 offline, Resume ±3.9 dtk tombol nonaktif, B kembali ke antrean ×2 → Confirmed, F ×1…×5 → Dead-letter; papan + tombol satu layar HP),
  **noDuplicate** (±237 frame HP/desktop: A bergeser 0 px, 6 chip tiap frame, confirmed 1 → 4 hanya naik, 0 frame dua chip confirmed bertumpuk, ledger 6 baris; scroll balik tetap, Replay reset, 7 tap cepat tetap 4/1/1),
  **processedVsConfirmed** (48,273 hijau vs 844/833 merah, jumlah 49,950; alasan per record), returnNext (±0 px, fokus Open case file, cincin mendarat di titik asal), historyDirect,
  interruptions (double tap +1 history, Cut ±0.8 dtk → B beku di tengah lane, Back saat pulsa → cincin 0, resize 1440→390 saat pemulihan lalu 1024/900/1920/1440 → 6 chip/4 confirmed/0 overflow),
  modelSlowFail, reducedMotion (cincin 0, chip snap 10–20 ms, pesan pemulihan 1.3 dtk), 4 HP/tablet + 1440/1920 (`verify_surgeline_room` dipanggil di paket, Q42),
  sources (20/20 klaim → dossier, 4/4 label ilustrasi/rekaman), performa 4× CPU (chapter 60.0, pulsa masuk 56.6, demo papan 60.0, scroll case 60.0, return 58.6 fps; ≤3% frame lambat),
  clean (1 Canvas, 0 error, 0 ≥400, 0 overflow), regressions (ledger 11 suite `passed` di sumber `37a4f3e3770463fb`).
- **Bug ditemukan + diperbaiki di Testing:** pulsa Return menyusut ke tepi atas layar, bukan ke antena — `lensCentre()` dibaca di halaman case saat dish sudah ter-scroll
  keluar (di-clamp `h*.14`; desktop y 126 vs antena 353). Fix: `pulseHome` menyimpan titik antena saat `openCase`, dipakai Return bila viewport sama. Build ulang → runner 11 suite → paket penuh diulang.
- **Temuan untuk pemilik (keputusan):**
  1. **Approve copy DRAFT 7B** (strip chapter, 3 hotspot, narasi papan 5 stage + label + ledger, bagian bukti rekaman, teaser DriftWatch).
  2. **Cut sebelum B sampai Form** diizinkan: B beku di tengah lane, tetap "stranded", Resume selesai normal (`m05b-cut-before-form.png`, klip slow-motion 4). Terima, atau kembali ke Development agar Cut aktif hanya saat B menunggu di Form.
  3. Info: refresh `/work/surgeline` mengulang ilustrasi dari "Start dispatch" (bukan state tersimpan) — sesuai desain.
- Batas: Chromium GPU emulasi lokal; GPU host tidak di-throttle; HP fisik = Fase 8.

### Fase 7C — DriftWatch: monitoring room

Sumber: `portfolio/CAPABILITY_DRIFTWATCH.md` §1–4, §7, §9. Brief desain: PLAN §5.3.
Target: pengunjung membedakan perubahan sumber, data hilang, dan pipeline yang rusak.

Development (Codex / Claude Code), **urut mobile → desktop**:
- [x] Brief dan copy personal DRAFT: 1,323 record/hari, empat sumber, 11/11 kegagalan uji,
  nol false positive pada uji itu, tiga hari unattended; semua label tanggal/konteks jelas
- [x] Mobile: chapter seismograf + case snapshot bertanggal ditumpuk, kontrol banding dan
  detail perubahan; hasil kosong mendapat penjelasan alarm, bukan status sehat
- [x] Trace tenang → lonjakan sesuai sebab → diff terbuka; pisahkan perubahan sumber dari
  gangguan pipeline; tentukan trigger, timing, state akhir, scroll balik dan interupsi
- [x] Transisi jarum/pita → timeline; return menggulung ke asal; Next memperkenalkan DueWatch
- [x] Verifikasi mobile selesai sebelum desktop; catat hasil pada tabel kemajuan
- [x] Desktop: timeline lebar, snapshot sejajar dan panel alarm kontekstual; cukup ruang tenang
  untuk membaca perubahan, tidak mengulang layout antrean SurgeLine
- [x] Regresi mobile, lint/typecheck/build + tes fokus; sumber copy/bukti → `ready-for-test`


Bahan handoff 7C Development (2026-09-17, Codex → Claude Code):
- **Preview:** `http://127.0.0.1:8767/` → chapter DriftWatch → Open case file (atau `/work/driftwatch`). Server mati → `npm run build --prefix web && npm run start --prefix web`.
- **Brief + peta sumber copy DRAFT + kontrak motion:** `web/README.md` bagian Phase 7C. Copy baru DRAFT: pitch/reading chapter, deck + brief + 3 hotspot, meja banding (intro, 4 langkah, 5 situasi, verdict/sebab/aksi, kode alarm), arsip bukti, teaser DueWatch.
- **Yang dibangun:** chapter → trace SVG hijau mengikuti orbit, lonjakan merah + label "Empty run → alarm" setelah .6, scroll balik membalik. Masuk: pita kertas dari jarum melebar jadi timeline; Return menggulung ke titik chapter asal. Case: **meja banding** — pilih situasi → Compare → trace tenang/lonjakan lokal (.8 s) → verdict + diff field (changed/added/removed/unchanged) atau sebab + aksi + kode alarm (`details`). Kosong/run hilang tidak pernah hijau; pulih = Day 1 tetap baseline, Day 2 gagal dicatat. Arsip: 1,323/hari per sumber, soak 01–03 Sep (01 Sep bukti tak langsung), 11/11 termasuk 3 kontrol normal, sumber publik tak berubah. HP: snapshot bertumpuk; desktop: timeline lebar, snapshot sejajar (sticky) + kolom verdict.
- **Fix sesi Claude Code:** (1) ilustrasi memakai Day 1–3 — sebelumnya 01–03 Sep 2026 = tanggal soak asli (0 alarm), sehingga "02 Sep failed" bertentangan dengan arsip; tes menolak tanggal kalender di ruang ilustrasi. (2) Snapshot desktop sticky agar tidak ada sumur kosong di samping diff panjang. (3) Tes trace chapter flaky di 1920 (baca var sebelum rAF) → tunggu sampel stabil; server lama (lebih tua dari build) di-restart.
- **Verifikasi:** lint/typecheck/build exit 0. `perf_quick.py --slug driftwatch` 4× CPU 390×844: chapter 60.0, terbang 57.8, banding 5 situasi 60.0, scroll case 60.0, return 58.8 fps (≤3% lambat). `run_regressions.py --phone-only room,dispatch,mobile,case,cases,showpiece`: 13/13 passed di sumber `40a56b14db159831` (monitor 6 viewport + edge fallback/reduced/Back saat pita). Foto/JSON `assets/renders/personal-driftwatch/dev/`. Rig: iGPU Intel headless, bukan HP fisik.
- **Untuk Testing/pemilik:** (1) Approve copy DRAFT 7C, termasuk pilihan "Day 1–3" untuk ilustrasi. (2) HP: sesudah Compare, trace + label HEALTHY/ALARM langsung di bawah tombol, verdict lengkap perlu scroll sedikit — nilai apakah cukup. (3) Refresh `/work/driftwatch` mengulang dari "Compare snapshots" (tanpa state tersimpan), sama seperti 7B.

Testing (Claude Code / Antigravity):
- [x] Jalankan seluruh kontrak Testing 7A–7F; sebab alarm terbaca dan trace tidak menyamar live
- [x] Bukti snapshot/diff/hasil kosong serta transisi pita mobile/desktop;
  paket `assets/renders/personal-driftwatch/evidence/` → `awaiting-gate` (21/21 pass)
- [x] Copy baru di-approve + gate personalisasi DriftWatch lolos (2026-09-17, "saya approve semua untuk 7C"; temuan jarak verdict HP diterima)

Bahan gate 7C (Testing 2026-09-17, Claude Code) — folder `assets/renders/personal-driftwatch/evidence/`:
- **Video:** `walkthrough-mobile.mp4` (390×844 touch, 148 dtk), `walkthrough-desktop.mp4` (1440×900 wheel/klik + resize, 103 dtk),
  `slow-motion.mp4` (0.25×, 118 dtk, 10 klip: seismograf, pita masuk, perubahan biasa sehat, layout kosong → alarm, ganti situasi saat Compare, pita kembali HP; pita masuk, run hilang, pita kembali, resize desktop).
  Tanpa suara. **Foto:** `contact-sheet-mobile.jpg` (28), `contact-sheet-desktop.jpg` (20), strip per item `i01`…`i16`, grafik `p01-fps-4x.png`, `viewports/` (6 viewport + fallback/reduced); `evidence.json` pass/fail per item + kategori + `forOwner`.
- **Kategori:** cerita ✔ · visual ✔ · animasi ✔ · transisi ✔ · mobile ✔ · desktop ✔ · sumber ✔ · performa ✔ (21/21 item).
- Item lolos (ringkas): chapterTrace (garis hijau = 1 − orbit, lonjakan merah + "Empty run → alarm" mulai orbit ±.67, balik membalik, diam saat idle; HP swipe + desktop wheel),
  ribbonEntry (pita 0.012 → lebar penuh ±800 ms dari titik jarum HP 190,367 / desktop 998,324, fokus heading), hotspots (zero rows ≠ sukses, baseline terakhir tanpa timestamp, watchdog + runner gagal),
  comparisonDesk (5 situasi HP tap + desktop klik: jendela trace 0→1 ±783 ms, verdict mulai ±600 ms, path tidak diskala; snapshot bertumpuk HP), **emptyNeverHealthy** (layout/collector/run hilang = ALARM merah
  + sebab + aksi + kode 5/5/1 di dua device; sebelum Compare "AWAITING COMPARISON", bukan hijau), sourceVsPipeline (Source comparison vs Pipeline health, recovery Day 1 tetap baseline + Day 2 gagal tercatat),
  diffDetail (changed/added/removed/unchanged, lama dicoret → baru), **notLive** (label ilustrasi di strip/meja/trace, Day 1–3 tanpa tanggal kalender, trace diam 2.1 dtk sesudah banding),
  archive (1,000 + 100 + 23 + 200 = 1,323; 01–03 Sep, 01 Sep tak langsung; 11/11 termasuk 3 kontrol normal; sumber publik tak berubah), returnNext (pita menggulung ke titik asal ±0 px, scroll ±0, fokus Open case file; Next → DueWatch),
  historyDirect, interruptions (double tap +1 history; ganti situasi 0.3 dtk saat Compare → tetap pending, tanpa verdict telat; 6 tap cepat → satu alarm; scroll balik tetap; keyboard langsung final;
  Back saat pita → pita bersih; resize 1440→390/1024/900/1920/1440 tetap alarm, overflow 0), modelSlowFail, reducedMotion (tanpa pita, trace chapter final, verdict 0 ms),
  4 HP/tablet + 1440/1920 (`verify_driftwatch_room` dipanggil di paket, Q42), desktopComposition (steps satu baris, timeline selebar meja, snapshot sejajar sticky top 130 di samping kolom verdict, ledger arsip di samping judul, 3 hari satu baris),
  sources (29/29 klaim → dossier, 5/5 label ilustrasi, "live" hanya dalam "Not a live monitor"), performa 4× CPU (chapter 59.8, pita masuk 54.3, lima banding 59.6, scroll case 58.6, pita kembali 54.3 fps; ≤3.3% lambat),
  clean (1 Canvas, 0 error, 0 ≥400, 0 overflow), regressions (ledger 13 suite `passed` di sumber `a8336493ca0de6ca`).
- **Bug ditemukan + diperbaiki di Testing:** animasi Compare memeras seluruh trace (`scaleX` pada grup path) → lonjakan bergeser dari tepi kiri dan melebar, bukan digambar di tempat
  (terlihat di slow-motion run pertama). Fix: jendela `clipPath` yang dibuka kiri → kanan (`driftwatch-room.tsx`, hapus satu baris CSS). Build ulang → runner 13 suite → paket penuh diulang.
- **Catatan rig:** percobaan fps pertama di paket penuh (host load ±11) scroll case 54.2 fps / 10.5% lambat (batas 10%); diukur ulang sendiri di sumber sama → 58.6 fps / 2.5%. Dua percobaan tersimpan di `evidence.json`.
- **Temuan untuk pemilik (keputusan):**
  1. **Approve copy DRAFT 7C** (strip chapter, klarifikasi brief, 3 hotspot, meja banding 5 situasi + verdict/sebab/aksi/kode, arsip bukti, teaser DueWatch), termasuk ilustrasi "Day 1–3" (bukan tanggal kalender).
  2. **HP sesudah Compare:** tombol di sepertiga atas → trace + label langsung terlihat (bawah trace 436 px), judul verdict mulai 489 px dari 844 (masih di layar); sebab/aksi/kode perlu scroll (sampai 854 px). Terima, atau kembali ke Development (`m04-layout-compared.png`).
  3. Info: gerak Compare berubah karena fix (lihat klip slow-motion 3–4). Refresh `/work/driftwatch` mengulang dari "Compare snapshots" — sama seperti 7B.
- Batas: Chromium GPU emulasi lokal; GPU host tidak di-throttle; HP fisik = Fase 8.

### Fase 7D — DueWatch: time control room

Sumber: `portfolio/CAPABILITY_DUEWATCH.md` §1–4, §7–8, §11. Brief desain: PLAN §5.4.
Target: pengunjung memahami agenda kontrak dan batas tindak lanjut otomatis pada pesan.

Development (Codex / Claude Code), **urut mobile → desktop**:
- [x] Brief dan copy personal DRAFT memisahkan tracker/triage: 200 kontrak/run, 18 pesan uji,
  6/6 sensitif dieskalasi, nol API eksternal; tampilkan batas audit dan tanggal simulasi video
- [x] Mobile: chapter orrery + agenda vertikal, pergantian modul via tap, status kontrak dan
  handoff manusia jelas; jangan membuat dua modul terlihat sebagai satu alur yang tidak terbukti
- [x] Animasi waktu → kategori kontrak; pesan sensitif berhenti ke manusia; replay pengingat
  tidak menambah duplikat; definisikan trigger, timing tenang, state akhir dan interupsi
- [x] Transisi cincin → agenda, return ke orrery; Next memperkenalkan studio BrandWall
- [x] Verifikasi mobile selesai sebelum desktop; catat hasil pada tabel kemajuan
- [x] Desktop: agenda kontrak dan meja triage berdampingan dengan hierarki berbeda;
  pencahayaan hangat, tempo tenang, tanpa countdown darurat palsu
- [x] Regresi mobile, lint/typecheck/build + tes fokus; sumber copy/bukti → `ready-for-test` (dituntaskan di sesi Testing 2026-09-17 pada build terintegrasi: lint/typecheck/build exit 0, runner 16/16)

Handoff Development 7D (2026-09-17):
- **Sumber utama sudah terintegrasi.** Brief/copy dan provenance: `web/README.md` bagian Phase 7D;
  rincian salinan: `assets/development/phase-7d/HANDOFF.md`, metadata `INTEGRATION.json`.
- Semua fitur Development terpasang. Checklist verifikasi penuh di atas sengaja belum dicentang;
  `ready-for-test` memakai pengecualian pemilik: integrasikan saja, tanpa tes ulang. Bukan gate lolos.
- Verifikasi sebelum integrasi (salinan, sumber `9be3fc9f6ae78f2d`): lint/typecheck/build passed;
  enam viewport 390/360/430/768/1440/1920 passed pada hasil `viewport`; tes state passed;
  gate fps DueWatch 52.1–59.1 fps / 1.5–7.3% frame lambat, CPU 4×, GPU Intel.
  Suite `monitor`, `perf-driftwatch`, `dispatch`, `room`, `audio` passed. Regresi penuh dihentikan
  atas instruksi pemilik; **bukan 16/16 passed**. `time` terakhir failed pada assertion error model
  yang sengaja diblok; rig sudah diperbaiki (hanya error ambient yang disengaja diizinkan),
  tetapi belum dijalankan ulang. `perf-surgeline` failed: chapter 18.9% dan case scroll 21.6%
  frame lambat (batas 10%); belum diatribusi dengan baseline. Tidak ada klaim regresi tertentu sebagai penyebab.
  Setelah integrasi: cek penggabungan per berkas/hash saja; **tanpa tes ulang dan tanpa rebuild utama**
  sesuai instruksi pemilik. Bukti salinan tidak dilabeli sebagai hasil build terintegrasi.
  
- Bukti: `assets/development/phase-7d/assets/renders/personal-duewatch/dev/verification.json`,
  `mobile-before-desktop.json`, `assets/renders/perf-quick/duewatch.json`, `regression-ledger.json`
  (dua path terakhir juga di dalam salinan). Preview utama perlu build baru pada sesi Testing.

Testing (Claude Code / Antigravity):
- [x] Jalankan seluruh kontrak Testing 7A–7F; dua modul dan simulasi terlabel, tanpa pengiriman nyata
- [x] Bukti pergantian status/handoff/replay, catatan video dan batas audit tetap terlihat;
  paket `assets/renders/personal-duewatch/evidence/` mobile/desktop → `awaiting-gate` (22/22 pass)
- [x] Copy baru di-approve + gate personalisasi DueWatch lolos (2026-09-18, "semuanya approved"; temuan cincin → rail tipis dan tick dial tanpa label diterima)

Bahan gate 7D (Testing 2026-09-17, Claude Code) — folder `assets/renders/personal-duewatch/evidence/`:
- **Video:** `walkthrough-mobile.mp4` (390×844 touch, 172 dtk), `walkthrough-desktop.mp4` (1440×900 wheel/klik + resize, 116 dtk),
  `slow-motion.mp4` (0.25×, 188 dtk, 12 klip: pointer chapter, cincin → rail, jarum ke tiap batas, tanggal tak jelas, teks disetujui vs berhenti di manusia, replay tanpa pengingat baru, tap cepat, rail kembali HP; cincin masuk, dua meja, cincin kembali, resize desktop).
  Tanpa suara. **Foto:** `contact-sheet-mobile.jpg` (28), `contact-sheet-desktop.jpg` (20), strip per item `i01`…`i17`, grafik `p01-fps-4x.png`, `viewports/` (6 viewport + fallback/reduced/slow); `evidence.json` pass/fail per item + kategori + `forOwner`.
- **Kategori:** cerita ✔ · visual ✔ · animasi ✔ · transisi ✔ · mobile ✔ · desktop ✔ · sumber ✔ · performa ✔ (22/22 item).
- Item lolos (ringkas): chapterPointer (pointer = orbit, galat maks 0, balik membalik, diam saat idle; HP swipe + desktop wheel), ringEntry (cincin .65 −28° dari orrery → rail 342 px HP / 1000 px desktop ±830 ms, fokus heading),
  hotspots (cek harian + tanggal tak jelas ke manusia / 6 fixture + celah mixed-intent / ledger sama + batas re-import), agendaDesk (61/60/8/7/0/lewat → Active/Due soon/Due soon/Needs renewal/Needs renewal/Expired; jarum monoton tanpa overshoot, diam ±550–620 ms, kartu ±150 ms; satu baris "Example here"),
  badData (Bad data + "Keep checking the others", baris sendiri, hari dipilih membersihkan), humanHandoff (harga/stok/status → teks disetujui + log mock lokal; komplain/pembayaran/tak jelas → berhenti ke manusia tanpa draf; sinyal 0→24 px ±250 ms; celah mixed-intent tertulis),
  **reminderReplay** (24 jam tepat 0 pending → >24 jam 1 → 6 replay tetap 1 "adds no duplicate" → dibalas tetap 1 → reset 0 → dibalas dulu tetap 0; HP + desktop), **twoModules** (HP satu meja per tap A/B, state bertahan dua arah, tombol ≥44 px; desktop berdampingan, langkah A/ dan B/),
  **notLive** (label simulasi, dial "BUSINESS TIME / ILLUSTRATION", tanpa countdown, semua state diam 2.1 dtk), evidenceAudit (200/run, 18 pesan + 6/6 + 0 API, 12 tetap 12 + batasnya; tanggal simulasi vs 8 firing/9 hari; 7 temuan 4 High/3 Medium bisa dibuka, A9/A10 terbuka),
  returnNext (rail melipat ke titik asal ±0 px, scroll ±0, fokus Open case file; Next → BrandWall), historyDirect, interruptions (double tap +1 history; 12 tap hari cepat → satu posisi akhir, animasi ≤1; ganti modul saat jarum berputar → final; 12 tap pesan → rute terakhir; scroll balik tetap; keyboard langsung final; Back saat cincin → bersih; resize 1440→390/1024/900/1920/1440 state tetap, overflow 0),
  modelSlowFail, reducedMotion (tanpa cincin, pointer final, jarum/sinyal tanpa animasi), 4 HP/tablet + 1440/1920 (`verify_duewatch_room` dipanggil di paket, Q42), desktopComposition (meja agenda 643 px di samping triage 613 px, modul terpilih bergaris amber, gradien hangat, langkah/bukti satu baris, catatan tanggal dua kolom, audit ≤900 px rata kanan),
  sources (42/42 klaim → dossier, 6/6 label simulasi/rekaman, "live"/"production-ready" hanya negasi), performa 4× CPU (chapter 60.0, cincin masuk 57.9, tap agenda+triage+pengingat 60.0, scroll case 60.0, cincin kembali 58.7 fps; ≤2.2% lambat),
  clean (1 Canvas, 0 error, 0 ≥400, 0 overflow), regressions (ledger 16 suite `passed` di sumber `f19aac05262f34b3`).
- **Temuan Development yang ditutup:** `time` kini hijau 6 viewport + edge (fallback hanya mengizinkan error model ambient yang sengaja diblok); `perf-surgeline` di build utama 57.0–60.0 fps ≤3% lambat — 18.9%/21.6% dulu diukur di salinan saat rig sibuk, tidak terulang.
- **Bug ditemukan + diperbaiki di Testing:** tes basi `verify_cases.py` (fallback DueWatch mengharapkan judul hotspot lama "Safe message triage" → "Message decisions"). Tanpa bug app; kode app tidak diubah.
- **Temuan untuk pemilik (keputusan):**
  1. **Approve copy DRAFT 7D** (pitch + strip pointer chapter, deck/brief/heading instrumen, 3 hotspot, ruang kendali waktu: intro, disclosure, agenda A, triage B + catatan celah, contoh pengingat terpisah + batas; 4 langkah; bukti rekaman 3 kolom, catatan tanggal, 7 temuan audit; teaser BrandWall).
  2. **Cincin → rail tipis:** cincin = garis 1 px, saat dipipihkan (scaleY .13; rail 1000 px desktop) jadi garis rambut di atas orrery yang ikut bergerak; rail pudar sebelum case muncul di Brief (meja agenda jauh di bawah). Timing/pendaratan lolos. Terima, atau kembali ke Development untuk garis/rail lebih tegas (`m02a-ring-rail.png`, `d02a-ring-rail.png`, klip slow-motion 2 dan 9).
  3. **Tick dial tanpa label:** kategori terbaca dari tombol hari, kartu hasil dan baris "Example here". Terima, atau tambah label (`m04-agenda-7.png`).
  4. Info: refresh `/work/duewatch` mengulang ke 61 hari, modul A, 0 pengingat — sama seperti 7B/7C.
- Batas: Chromium GPU emulasi lokal; GPU host tidak di-throttle; HP fisik = Fase 8.

### Fase 7E — BrandWall: visual studio

Sumber: `portfolio/CAPABILITY_BRANDWALL.md` §1–4, §6 K2–K8, §7, §9. Brief desain: PLAN §5.5.
Target: pengunjung melihat kelas kerusakan, titik patah, dan efek aturan pada aset brand.

Development (Codex / Claude Code), **urut mobile → desktop**:
- [x] Brief dan copy personal DRAFT: 30 aset sintetis × 5 surface × 2 tema = 300 screenshot/run,
  11 titik patah, tujuh aturan CSS; catat A8 parsial dan aset rusak yang harus ditolak
- [x] Mobile: chapter prisma + specimen terang/gelap, anotasi ukur, pasangan sebelum/sesudah
  besar dan terbaca; tombol pembanding tersedia selain slider opsional
- [x] Animasi spektrum → specimen → garis titik rusak → reveal hasil; observer lama sekunder
  terhadap cerita QA; tetapkan trigger, timing, state akhir dan perilaku interupsi
- [x] Transisi berkas prisma → galeri, return merapat; Next kembali memperkenalkan CrossCheck
- [x] Verifikasi mobile selesai sebelum desktop; catat hasil pada tabel kemajuan
- [x] Desktop: galeri editorial lebar, contact sheet, pembanding besar dan anotasi sejajar;
  detail logo/teks tetap tajam, spektrum tidak mengacaukan makna warna status
- [x] Regresi mobile, lint/typecheck/build + tes fokus; sumber copy/bukti → `ready-for-test` (2026-09-24, Claude Code)

Handoff Development 7E (2026-09-24, Codex → Claude Code):
- Fitur + brief/provenance: `web/README.md` bagian Phase 7E; modul di CODEMAP entri 7E.
- Sumber `d97d12160a89721c`, build utama :8767. lint/typecheck/build exit 0. `studio` 6 viewport + 4 edge passed
  (Codex 2026-09-18, sumber sama). `perf-brandwall` passed di GPU Intel: chapter 60.0, flight 55.5 (3.3% lambat),
  pembanding 60.0, case scroll 58.9, return 57.1 fps. Gagal Codex sebelumnya (14.8–39 fps) = rig llvmpipe (GPU software, :8785), bukan kode.
- Regresi runner passed: `mobile`, `case`, `cases`, `room`, `dispatch`, `monitor`, `time`, `showpiece` (390×844) + `desktop-b` (1440/1920).
- Fix tes basi (bukan app): `verify_mobile.py` mengharapkan 0 `.draft-label` di homepage → daftar `DRAFTS = {'brandwall'}`;
  `verify_case.py` cek DRAFT dicakup ke `.case-page`. Saat gate 7E lolos: kosongkan `DRAFTS`.
- Catatan untuk Testing: header fixed menumpuk judul case saat scroll di 390 (perilaku header lama; `contrast-split-390x844.png`) — nilai, jangan anggap baru tanpa bandingkan fase lama.

Testing (Claude Code / Antigravity):
- [x] Testing ringan Q47 (fitur baru 7E saja, 390×844 + 1440×900); pembanding terpakai dengan tap tanpa drag presisi
- [x] Bukti crop/kontras/rasio/overflow dan perbandingan terbaca, efek tidak menutupi spesimen;
  paket `assets/renders/personal-brandwall/evidence/` mobile/desktop → `awaiting-gate` (17/17 pass)
- [x] Copy baru di-approve + gate personalisasi BrandWall lolos (2026-09-24, "untuk saat ini saya sudah approve"; perbaikan pasca-gate: label 10 px, crop Overflow HP)

Bahan gate 7E (Testing 2026-09-24, Claude Code, aturan ringan Q47) — folder `assets/renders/personal-brandwall/evidence/`:
- **Video (tanpa suara):** `walkthrough-mobile.mp4` (390×844 touch, 45 dtk: spektrum chapter → prisma → galeri → 3 specimen × Before/Compare/After → 3 batas → tema gelap → aturan → batas bukti → Return), `walkthrough-desktop.mp4` (1440×900 wheel/klik, 27 dtk). Hotspot, tap cepat, loading gate dan ekor history dites + difoto tapi tidak difilmkan (detik tersimpan di `evidence.json.filmed`). Tanpa slow-motion (tidak ada temuan motion).
- **Foto:** `contact-sheet.jpg` (20 frame berlabel), strip `i01`…`i12`, PNG `m*`/`d*`, `dev-checks/`; `evidence.json` pass/fail per item + 8 kategori.
- **Kategori:** cerita ✔ · visual ✔ · animasi ✔ · transisi ✔ · mobile ✔ · desktop ✔ · sumber ✔ · performa ✔ (17/17).
- Item lolos (ringkas): story (7 bagian urut, langkah Specimen → Surface + theme → Measure → Compare, 1 label DRAFT); chapterSpectrum (beam scaleX .08 → 1 maju, balik .68 → .24, tanda specimen 0 → 1, diam saat idle; HP swipe + desktop wheel);
  prismEntry (bidang tampak ±780 ms: ray di titik prisma → bidang galeri penuh, tumbuh monoton, hilang ke 0; fokus heading case; Canvas sama); hotspots (Test matrix/Measurement/Fix rules);
  **comparator** (tap saja, tanpa drag: 3 specimen × 3 mode, clip 100%/50%/0%, viewBox + frame dua capture identik, tombol ≥44 px; pasangan 342×290 px HP, 1000×461 px desktop);
  defectClasses (crop BW-C1/C6, kontras BW-C3, overflow BW-C7 dengan measure + rule; C4 = 0 tanpa pasangan karangan); **effectsClear** (bidang prisma opacity 0 di case, seam hanya di Compare, 5 titik hit-test di 18 state mengenai pasangan);
  boundaries (1.00→1.25, 0.30→0.35, 28→32; tema gelap tidak mengubah angka); rulesLimits (7 disclosure, C4/C5, 186 → 18 / galeri 182 → 18, 18 aset hilang/kosong ditolak, A8 parsial);
  interruptions (5 specimen + 5 mode dalam satu frame → pilihan terakhir; state bertahan saat scroll pergi/kembali; edge 390×844 reduced/model diblok/model lambat/Back saat flight + resize passed);
  returnNext (bidang merapat ke titik asal tepat ±0 px HP + desktop, ±783 ms, scroll ±0, fokus Open case file; Next → CrossCheck; Back/Forward; refresh → portrait/before);
  desktopComposition (contact sheet kiri 276 px, pembanding 1000 px; meja batas + probe berdampingan; aturan 2 kolom; 3 kartu record sebaris); devChecks (`verify_brandwall_room.viewport` 390×844 + 1440×900 passed);
  sources (18/18 angka → dossier, label ilustrasi/arsip, tanpa klaim live/afiliasi); performa (Development `perf_quick`, sidik jari sama: chapter 60.0, flight 55.5 / 3.3% lambat, pembanding 60.0, scroll case 58.9, return 57.1 fps); clean (1 Canvas, 0 error, 0 ≥400, overflow 0); regresi (11 suite terkait `passed` di `d97d12160a89721c`).
- **Bug ditemukan di Testing:** tidak ada bug app. Yang diperbaiki hanya skrip bukti baru sendiri (clip computed `inset(0px 0% 0px 0px)`, teks sumber via `textContent`, pemotongan video).
- **Temuan untuk pemilik (keputusan):**
  1. **Approve copy DRAFT 7E** (pitch + konteks chapter, strip "Specimen → measure → compare", brief/deck/hotspot case, studio: intro, 3 judul specimen + before/after + measure/rule, catatan sumber; batas: intro + 3 konteks/catatan; 7 aturan; 3 kartu record/limits; teaser CrossCheck).
  2. **Specimen Overflow di HP kecil:** capture nama panjang tampil skala 0.455 (teks dalam screenshot ±5–6 px); efek "kartu melebar vs membungkus" terbaca, detail teks tidak. Link "Full before/after ↗" tersedia. Terima, atau Development: crop lebih sempit/zoom khusus HP (`m05-name-before.png`, `m05-name-after.png`).
  3. **Teks kecil 8 px** di strip chapter, label seam "AFTER / BEFORE" dan kepala probe (mono, mengikuti gaya label fase lama). Terima, atau naikkan ke 10 px.
  4. Info (perilaku lama, bukan baru): header fixed transparan menumpuk baris konten saat scroll di 390 (terlihat di `m05-*`, `m07-rules.png`), sama seperti catatan handoff Development dan fase sebelumnya.
- Batas: Chromium GPU emulasi lokal; fps dari Development (GPU Intel, CPU 4×); HP fisik = Fase 8.
- **Gate 2026-09-24:** pemilik approve + izinkan perbaikan. Temuan 2 → `phoneView` `134 92 706 599` (bidang HP terisi, kartu tetangga tetap terlihat; skala 0.458 → 0.481 — naik sedikit karena bukti tetangga wajib tampil; link full view tetap). Temuan 3 → label mono 8 px → 10 px. Temuan 4 perilaku lama, tidak diubah. Paket bukti di folder yang sama sudah diganti hasil build pasca-gate (17/17, sumber `4bf13e4158597b83`; fps chapter 60.0, flight 56.8, pembanding 60.0, scroll 59.9, return 58.8).

### Fase 7F — Five rooms, one observatory

Prasyarat: gate 7A–7E lolos. Referensi: PLAN §5.1–§5.5, §7, §8, §11–§12.
Target: lima pengalaman khas menyatu; desktop menjadi presentasi utama yang sudah matang.

Development (Codex / Claude Code), **mobile dahulu, kemudian desktop**:
- [x] CrossCheck: scan → temuan tetap terbaca; entry lensa dan sambungan ke SurgeLine konsisten
- [x] SurgeLine: aliran → crash/resume tetap jelas; sambungan ke DriftWatch menjaga state kamera
- [x] DriftWatch: snapshot → diff/alarm tetap tenang; sambungan ke DueWatch punya ritme tepat
- [x] DueWatch: agenda dan triage tetap terpisah; sambungan ke BrandWall menjaga label simulasi
- [x] BrandWall: perbandingan visual tetap utama; sambungan kembali CrossCheck menutup rantai
- [x] Homepage, Skills, header, audio, CTA dan About/Contact tetap satu observatorium;
  perbedaan layout/bukti/motion kelima project terlihat, tidak hanya beda warna dan nama
- [x] Verifikasi mobile seluruh perjalanan → poles tempo, kamera, lighting dan komposisi desktop
  → regresi mobile; tidak ada lompatan framing, ruang kosong tanpa fallback, atau scroll terkunci
- [x] Lint/typecheck/build + regresi fokus dan pengukuran performa lima project → `ready-for-test`

Testing (Claude Code / Antigravity):
- [x] Kontrak Testing 7A–7F pada kelima project, hasil terpisah per project/device;
  seluruh rantai Next, entry/return, refresh, Back/Forward dan interupsi lulus
- [x] Rekaman memperlihatkan lima komposisi, lima cara menjelaskan, dan transisi yang sesuai;
  desktop dinilai sebagai showpiece, mobile tetap utuh; selisih target performa dicatat
- [x] Paket `assets/renders/personal-observatory/evidence/` dikirim → `awaiting-gate` (2026-09-24, 17/17)
- [x] Gate integrasi lolos (2026-09-24, "saya accept semua itu lulus"; hint Q49 approved, temuan 2–3 diterima, PLAN §3 Q50) → Fase 8 Development aktif

Bahan gate 7F (Testing 2026-09-24, Claude Code, putaran penuh) — folder `assets/renders/personal-observatory/evidence/`:
- **Video (tanpa suara):** `walkthrough-mobile.mp4` (390×844 touch, 130 dtk: lima chapter → geser + tap instrumen → tirai masuk → interaksi ruang → Return; rantai Next 5 hop; Back/Forward; Return dari rantai), `walkthrough-desktop.mp4` (1440×900 wheel/klik, 113 dtk, alur sama), `slow-motion.mp4` (10 hop tirai HP + desktop, 0.25×, 92 dtk).
- **Foto:** `contact-sheet-mobile.jpg`, `contact-sheet-desktop.jpg` (chapter / tirai / ruang / return per project); strip `i01`–`i05` per project, `i06` rantai, `i07` history, `i08` interupsi, `i09` lima ruang, `i10` header/menu/Skills/About/Contact, `i11` desktop, `i12` 6 viewport × 5 project, `i13` model diblok; `evidence.json` (`perProjectDevice` phone/desktop × chapter/entry/room/return).
- **Kategori:** cerita ✔ · visual ✔ · animasi ✔ · transisi ✔ · mobile ✔ · desktop ✔ · sumber ✔ · performa ✔ (17/17).
- **Per project (HP + desktop lulus semua):** CrossCheck tirai `stage` (buka ±1.56 dtk), scan main sendiri + step + Replay + temuan; SurgeLine `blinds` (±2.17 dtk), Start → Cut → Resume → 4 confirmed / C rejected / F dead-letter, B "sent 2×, same receipt"; DriftWatch `roller` (±1.55 dtk), layout rusak = alarm + 5 kode, perubahan biasa = sehat; DueWatch `louvre` (±2.04 dtk), 7 hari → renew, keluhan → handoff manusia, triage terpisah (HP tersembunyi sampai dipilih), label simulasi ada; BrandWall `prism` (±1.75 dtk), Before/Compare/After clip 100/50/0%. Chapter: geser sentuh → 0.35, tap → 1.0 (±2.1 dtk); scroll 220 px menggeser stage 205–220 px tanpa memutar; Return scroll ±0 px + fokus Open case file.
- **Rantai + history:** 5 hop tiap device menutup tirai asal lalu membuka tirai tujuan (stage→blinds→roller→louvre→prism→stage), mendarat di atas brief, Canvas sama, scroll terkunci saat tirai menutup. Back ×2 / Forward ×2 benar; Return dari rantai → chapter CrossCheck top 0; direct URL + refresh lima case benar di kedua device.
- **Interupsi (HP + desktop, per project):** 5 tap cepat instrumen → berhenti di 1.0; Back saat tirai tujuan masih bergerak → kembali ke `/`, tirai open, scroll bebas; double Open → satu case, satu Back ke `/`; double Next → SurgeLine (tidak lompat dua); resize 390↔1440 di case → overflow 0. Model diblok: lima case tampil still berlabel + kartu hotspot.
- **Performa:** perf_quick Development (HP 4× CPU, sidik jari sama) 53.0–60 fps, ≤4.8% frame lambat (terendah = tirai masuk case ±53 fps). Rantai diukur di Testing: HP 4× CPU 56.2–59.4 fps (≤4.8% lambat), desktop 60 fps semua hop; wheel homepage 60 fps. Target §11 (≥45) terpenuhi di emulasi.
- **Sumber:** 20 angka reading → dossier; 0 label DRAFT di homepage + lima case; kata klaim hanya dalam negasi/copy approved lama; Upwork = link kontak milik pemilik.
- **Bug ditemukan di Testing:** tidak ada bug app. Yang diperbaiki hanya skrip bukti baru sendiri (5 jebakan pengukuran, dicatat di CODEMAP entri 7F Testing); `--redo-interruptions`/`--redo-fps` mengulang dua bagian itu pada sidik jari sama.
- **Temuan untuk pemilik (keputusan):**
  1. **Approve copy antarmuka DRAFT Q49:** hint chapter "Drag or tap the instrument to turn it" (empat chapter; BrandWall memakai hint observer lama).
  2. **Kunci scroll dilepas ±50–320 ms sebelum tirai benar-benar terbuka** (diukur: `stage` ±50 ms, `louvre` ±320 ms, pengunjung bisa mulai scroll saat bilah terakhir masih bergerak). Terima, atau Development: lepas kunci tepat saat `open`.
  3. Info (perilaku lama, bukan baru): header transparan menumpuk judul chapter/case saat scroll (terlihat di frame desktop SurgeLine dan HP DueWatch), sama seperti catatan 7E.
- Batas: Chromium GPU emulasi lokal; Firefox/WebKit + HP fisik = Fase 8.

### Fase 8 — Launch ready
Prasyarat: gate 7A–7F lolos. Detail personalisasi dan bukti per project tetap wajib saat launch.

Development (Codex / Claude Code):
- [x] Meta, share card (preview WhatsApp/LinkedIn), favicon — `lib/site.ts`, `layout.tsx`, `robots.ts`/`sitemap.ts`, ikon `app/`, card `public/og/home.jpg` (2026-09-24)
- [x] Judul/deskripsi/share card lima case mengikuti cerita masing-masing, angka dan batas dossier — `generateMetadata` + `public/og/<slug>.jpg`: deck + angka chapter + batasnya (mis. "1,080 test combinations · On an owned demo app"); semua angka = copy approved `instruments.ts`. Format judul/alt/teks sosial = **DRAFT**
- [x] Deploy Vercel (produksi); instruksi sambung domain untuk pemilik → `ready-for-test` — https://rayin-observatory.vercel.app (2026-09-24)

Instruksi domain (untuk pemilik; agent tidak menyentuh domain/DNS):
1. Vercel dashboard → project `rayin-observatory` → Settings → Domains → Add → ketik domain (mis. `rayin.my.id` atau subdomain).
2. Pasang record DNS yang ditampilkan Vercel di pengelola domain (apex: `A`; subdomain: `CNAME` ke nilai yang Vercel tunjukkan). Tunggu status "Valid Configuration".
3. Jadikan domain itu domain produksi utama (Vercel memakai domain produksi terpendek/utama sebagai `VERCEL_PROJECT_PRODUCTION_URL`).
4. Minta agent **redeploy** (`vercel deploy --prod`): canonical, `og:url`, `og:image`, sitemap dibakar saat build, jadi tanpa redeploy share card masih menunjuk `*.vercel.app` (tetap jalan, hanya bukan domain sendiri).

Bahan Development Fase 8 (2026-09-24): lint/typecheck/build exit 0; build simulasi env Vercel produksi → head memuat canonical/og/twitter absolut + `index, follow`, build lokal → `noindex` + robots `Disallow: /`; runner `mobile,cases` 390×844 passed (sumber `fc3373987c815ca1`); produksi: `/`, lima case, `/og/*`, ikon, GLB, video, robots, sitemap 200, slug asing 404; smoke Playwright Chromium 390×844 + 1440×900 di URL Vercel: Enter → chapter → case CrossCheck, judul per case, 1 Canvas, 0 error, 0 respons ≥400. `.gitignore` root/web diperketat (`.vercel/`, log, cache, editor, kunci) — 0 berkas terlacak yang kini ter-ignore; `web/.vercelignore` mengecualikan `scripts/` + catatan agen dari upload.

Testing (Claude Code / Antigravity) — **semua tes memakai URL Vercel, bukan preview lokal (Q40)**:
- [x] QA lintas browser (Chromium/Firefox/WebKit) + viewport HP/tablet/desktop di URL Vercel — Chromium 3/3 + Firefox 3/3 lolos; WebKit headless crash di case file (temuan F1) **diterima pemilik apa adanya**; cek iPhone Safari = tindak lanjut pemilik
- [x] CrossCheck: scan/matriks/temuan, entry lensa dan return tetap utuh di produksi (Chromium HP + desktop)
- [x] SurgeLine: antrean/crash/resume, konfirmasi vs kegagalan, transisi antena tetap utuh
- [x] DriftWatch: snapshot/diff/alarm, label tanggal dan transisi pita tetap utuh
- [x] DueWatch: dua modul, eskalasi manusia, label simulasi/video dan transisi waktu tetap utuh
- [x] BrandWall: specimen/tema, kontrol sebelum/sesudah dan transisi prisma tetap utuh
- [x] Cek preview share (WhatsApp/LinkedIn/Facebook sebagai crawler) dari URL Vercel — 6 halaman, kartu 1200×630 ≤77 KB, `share-previews.jpg`
- [x] Paket bukti `assets/renders/launch/evidence/` dikirim (evidence.json: 17 pass / 1 fail)
- [ ] Tes manual pemilik di HP fisik (rasa scroll, fps, suara, 4G; sekaligus buka case file di iPhone Safari untuk F1) — tindak lanjut pemilik, tidak menahan gate
- [x] Fix F1 pasca-gate (2026-09-24, atas permintaan pemilik): video demo tanpa `<source>` di markup, src dipasang saat play → WebKit headless case file 0/10 crash (sebelumnya 10/10). Commit `d52db2c`, sudah di-deploy produksi
- [x] Gate: pemilik menyatakan "terima semua" (2026-09-24) → Fase 8 `done`; temuan F1 diterima; commit + push + redeploy produksi atas permintaan pemilik

### Fase 9 — Accessibility (ditunda)
- [ ] Mode gerak minimal, keyboard, screen reader
- [ ] CrossCheck: matriks dan temuan tetap dipahami tanpa scan; detail bukti terjangkau keyboard
- [ ] SurgeLine: urutan/crash/resume dan hasil tersedia sebagai teks; perubahan status diumumkan
- [ ] DriftWatch: diff/alarm terbaca tanpa gerak/warna; pasangan snapshot berlabel jelas
- [ ] DueWatch: tanggal, kategori dan handoff manusia terbaca berurutan; fokus antar modul jelas
- [ ] BrandWall: pembanding berlabel, alternatif tombol untuk slider, anotasi tidak hanya warna
- [ ] Regresi mobile dahulu lalu desktop; bukti terpisah per project + gate setelah Testing

---

## Keputusan baru setelah grilling

> Catat di sini setiap keputusan pemilik yang muncul setelah 2026-09-14, lalu salin ke log
> keputusan PLAN.md §3.

| Tanggal | Keputusan | Sumber |
|---|---|---|
| 2026-09-14 | Gate Fase 0 lolos: palet §8 (+ `muted`/`line` bantu), Fraunces/Inter/JetBrains Mono, kubah, teleskop 3 lensa, foto duotone final. Disalin ke PLAN §3 Q26 + §8. Copy chapter CrossCheck belum di-approve terpisah → tetap DRAFT sampai item Fase 2 | Pemilik, chat sesi Claude Code |
| 2026-09-15 | Gate Fase 1 lolos (dinilai dari foto + video bukti emulasi). Log sesi PROGRESS dibuat ringkas | Pemilik, chat sesi Claude Code |
| 2026-09-15 | Gate Fase 2 lolos (dinilai dari foto + video bukti emulasi); copy CrossCheck (pitch + 1,080 "On an owned demo app") diterima tanpa revisi | Pemilik, chat sesi Claude Code |
| 2026-09-15 | Skill kerja harian Go, MySQL/TiDB, Redis dikonfirmasi → grup Skills "Daily work". Disalin ke PLAN §3 Q33 | Pemilik, chat sesi Claude Code |
| 2026-09-15 | Revisi pasca Fase 3 disetujui: langit gelap hanya 30% atas + bintang lebih jarang, animasi baru 5 instrumen + Saturnus, label BrandWall observer. Repo GitHub personal public | Pemilik, chat sesi Claude Code |
| 2026-09-15 | Gate Fase 3 lolos + seluruh copy homepage di-approve (DRAFT dilepas); kontak asli dipasang. Disalin ke PLAN §3 Q32 | Pemilik, chat sesi Claude Code |
| 2026-09-15 | Mulai Fase 3 tiap fase = Development (Codex utama / Claude Code) → Testing (Claude Code / Antigravity, context ±1M) + paket bukti video/foto; gate dari bukti; tes manual HP fisik ditunda ke Fase 8. Disalin ke PLAN §3 Q31 + §12 | Pemilik, chat sesi Claude Code |
| 2026-09-15 | Gate Fase 4 lolos; copy case CrossCheck di-approve (DRAFT dilepas); flight-in diterima apa adanya; `assets/` keluar dari git (lokal saja). Disalin ke PLAN §3 Q34 | Pemilik, chat sesi Claude Code |
| 2026-09-15 | Gate Fase 5 lolos; copy 4 case baru di-approve (DRAFT dilepas); video DueWatch opsi 1 (catatan tanggal simulasi di bawah video dipertahankan). Disalin ke PLAN §3 Q35 | Pemilik, chat sesi Antigravity |
| 2026-09-15 | Gate Fase 6 lolos (dari video bukti desktop); layar pertama case desktop tanpa instrumen diterima apa adanya. Disalin ke PLAN §3 Q36 | Pemilik, chat sesi Claude Code |
| 2026-09-16 | Temuan Testing Fase 7: pemilik pilih opsi B ("B dong buat lebih cepat") — Enter aktif setelah hero siap, instrumen dimuat di belakang. Fase 7 kembali ke Development; dikerjakan sesi berikut, bukan sesi ini. Disalin ke PLAN §3 Q37 | Pemilik, chat sesi Claude Code |
| 2026-09-16 | Setiap akhir fase (gate lolos) wajib git commit + push ke `origin main`; ditulis di `PROMPT.md` (langkah tutup sesi no. 4). Disalin ke PLAN §3 Q38 | Pemilik, chat sesi Claude Code |
| 2026-09-16 | Gate Fase 7 lolos dari paket bukti Testing ulang 14/14 ("lolos commit dan push"); jeda instrumen ±3 dtk diterima apa adanya. Disalin ke PLAN §3 Q39 | Pemilik, chat sesi Claude Code |
| 2026-09-16 | Testing Fase 8 dijalankan di **URL produksi Vercel** (deploy dulu, baru tes), bukan preview lokal. Vercel CLI 54.9.1 terpasang + dicatat di `RULES.md` agar semua harness pakai. Disalin ke PLAN §3 Q40 | Pemilik, chat sesi Claude Code |
| 2026-09-24 | Gate 7E lolos ("untuk saat ini saya sudah approve", izin memperbaiki yang perlu): copy 7E approved, DRAFT BrandWall dilepas; label mono 10 px; crop Overflow HP. Fase aktif berikut 7F. Disalin ke PLAN §3 Q48 | Pemilik, chat sesi Claude Code |
| 2026-09-18 | Testing ringan mulai 7E ("testingnya jangan banyak banyak dan lama ... fitur yang baru dibuat aja"): uji hanya fitur baru di 390×844 + 1440×900, regresi terbatas, paket 2 video pendek tanpa slow-motion wajib, fps dari Development; 7F/8 tetap penuh. Disalin ke PLAN §3 Q47 + §12.3 | Pemilik, chat sesi Claude Code |
| 2026-09-18 | Gate 7D lolos ("semuanya approved"): copy 7D approved, DRAFT DueWatch dilepas (strip chapter jadi "Illustration"); temuan cincin → rail tipis dan tick dial tanpa label diterima. Fase aktif berikut 7E. Disalin ke PLAN §3 Q46 | Pemilik, chat sesi Claude Code |
| 2026-09-17 | Gate 7C lolos ("saya approve semua untuk 7C ini"): copy 7C approved termasuk ilustrasi Day 1–3, DRAFT DriftWatch dilepas; jarak verdict HP sesudah Compare diterima; fix jendela clip trace bagian dari motion approved. Commit + push tanpa mengganggu Development 7D paralel. Disalin ke PLAN §3 Q45 | Pemilik, chat sesi Claude Code |
| 2026-09-17 | Gate 7B lolos ("7b sudah saya cek dan lulus semua"): copy 7B approved, DRAFT SurgeLine dilepas; Cut sebelum B sampai Form diterima; refresh mengulang ilustrasi sesuai desain. Fase aktif berikut 7C. Disalin ke PLAN §3 Q44 | Pemilik, chat sesi Claude Code |
| 2026-09-16 | Gate 7A lolos ("lulus semua aman"): copy 7A approved, DRAFT dilepas; performa scrub (11–13% frame lambat) dan crop CC-001 diterima apa adanya. Disalin ke PLAN §3 Q43 | Pemilik, chat sesi Claude Code |
| 2026-09-16 | Testing jangan lama lagi: mulai 7B Development wajib `perf_quick.py`; regresi lewat `run_regressions.py` (skip suite yang sudah lolos di sumber sama, setelah fix hanya yang belum hijau); paket bukti memanggil tes dev fase aktif; suite fase lama 390×844 saja. Disalin ke PLAN §3 Q42 + §12.3 | Pemilik, chat sesi Claude Code (Testing 7A) |
| 2026-09-16 | Personalisasi cerita, visual, animasi dan transisi lima project dari `portfolio/` lokal; setiap fase mobile dahulu, lalu desktop sebagai tampilan utama. Sisipkan 7A–7E per project + 7F integrasi sebelum launch; fase aktif berikut 7A. Disalin ke PLAN §3 Q41 | Pemilik, chat sesi Codex |

## Log sesi

- **2026-09-24 · Claude Code · Fix F1 (Safari/WebKit case file crash)** — Permintaan pemilik "perbaiki masalah di safarinya". `case-file.tsx`: komponen `DemoVideo` — `<video>` tanpa `<source>`/`src`, tombol ▶ di atas poster; src dipasang saat tap (atau event `play`), baru kontrol native muncul. CSS `.case-video-frame`/`.case-video-play` di `globals.css`. Verifikasi: lint/typecheck/build exit 0; build lokal :8767 — WebKit headless 5 case × 390×844 + 1440×900: sebelum fix 10/10 "Page crashed", sesudah 0/10; alur Enter → 5 case WebKit 390×844 3/3 lolos (tanpa workaround harness); tap ▶ di Chromium 390/1440 + Firefox 1440: 0 request video sebelum play, video jalan, `v.play()` langsung (jalur tes lama) tetap jalan. Sisa: WebKit headless crash saat **memutar** mp4 — juga di halaman kosong tanpa kode situs (batas codec build WPE di mesin ini, bukan bug situs); pemutaran di iPhone Safari tetap dicek pemilik. Atas perintah pemilik: commit `d52db2c` + push + `vercel deploy --prod` (Ready); produksi: 5 case tanpa `<source>`, WebKit headless 10/10 halaman lolos. Berikutnya: pemilik buka case file di iPhone Safari, tap ▶.
- **2026-09-24 · Claude Code · Fase 8 Testing (putaran penuh, URL Vercel)** — Skrip baru `web/scripts/launch_evidence.py` (memakai ulang mesin 7F lewat `OBSERVATORY_URL`, keluaran `assets/renders/launch/evidence/`; `--redo-browsers` ulang bagian browser saja). Hasil: lima project × HP+desktop Chromium, rantai Next 5 hop, history/direct+refresh, interupsi, model diblok, share (3 crawler × 6 halaman), robots/sitemap/ikon/404, fps (HP 4× CPU 56.7–59.5, desktop 60), 0 error/0 ≥400 → pass. Transfer sebelum Enter di produksi 2,388,027 B (Development lokal 787 KB tidak setara: cache mati + semua aset). **FAIL: `browsers`** — headless WebKit (Playwright WPE) crash "Page crashed" di setiap case file, juga di build lokal; bisect: JS mati tetap crash, membuang `<source type="video/mp4">` menghentikan crash, halaman kosong dengan `<video><source>` sama tidak crash. Dengan workaround harness (buang `<source>`) WebKit masih tidak stabil (390×844 gagal 2×, 768/1440 lolos). Tidak bisa dibedakan bug situs vs keterbatasan build WPE; iPhone Safari belum dites. Tanpa perubahan kode app, tanpa deploy/commit. Langkah berikut: keputusan pemilik (lihat laporan): perbaikan defensif video (buat `<source>` saat play) + redeploy, atau terima dan cek di iPhone.
- **2026-09-24 · Claude Code · Fix parallax HP (pasca-gate 7F, di luar checklist Fase 8)** — Laporan pemilik dari deploy di HP: artefak goyang/glitch saat scroll dan menimpa teks. Penyebab: model WebGL di canvas `fixed` digeser dari `scrollY` (main thread) sedangkan teks digeser compositor → tertinggal 1–2 frame; canvas `inset:0` juga resize saat URL bar HP naik-turun. Fix revisi 2 (revisi 1 = tukar-skala, ditolak pemilik: artefak lenyap saat scroll sedikit): HP tetap meluncur bareng teks, tapi jarak diukur dalam tinggi section (svh) bukan canvas; ukuran home HP `.37`→`.33`; `.scene-layer` tinggi `100lvh`. Desktop tidak berubah. Verifikasi: typecheck/lint, foto 390×844 5 titik scroll (tanpa tumpang tindih), build, `run_regressions --suites mobile,cases --phone-only` passed (sumber `df2db954c24eb457`). Belum diuji di HP fisik/deploy; belum di-deploy/commit. Langkah berikut: pemilik cek di HP setelah deploy.
- **2026-09-24 · Claude Code · Fase 8 Development → ready-for-test** — Meta/OG/Twitter + canonical (`lib/site.ts`, `layout.tsx`, `generateMetadata` case), `robots.ts`/`sitemap.ts` (index hanya produksi Vercel), ikon kubah (`app/icon.svg`, `apple-icon.png`, `favicon.ico`), 6 share card 1200×630 70–77 KB dari skrip baru `web/scripts/build_share_cards.py` (copy approved dibaca dari source, bukan diketik ulang). `.gitignore` root/web diperketat atas permintaan pemilik; `web/.vercelignore` baru. Pemilik izinkan deploy → `vercel link` project baru `chhrones-projects/rayin-observatory` + `vercel deploy --prod`: https://rayin-observatory.vercel.app. Verifikasi: lint/typecheck/build exit 0; head HTML dicek di build env Vercel simulasi + lokal; runner `mobile,cases` 390×844 passed (sumber `fc3373987c815ca1`); curl produksi semua aset 200; smoke Playwright 390×844 + 1440×900 di produksi 0 error. DRAFT: format judul/alt/teks sosial share. Berikutnya: Fase 8 Testing putaran penuh di URL Vercel (Q40).

- **2026-09-24 · Claude Code · Gate 7F lolos → done** — Pemilik "saya accept semua itu lulus" dari paket `personal-observatory/evidence/` 17/17: hint chapter Q49 approved (tidak ada label DRAFT di kode untuk hint itu), kunci scroll dilepas ±50–320 ms sebelum tirai terbuka diterima, header transparan (perilaku lama) diterima. Keputusan di PLAN §3 Q50. Tanpa perubahan kode app; commit + push semua perubahan 7F. Berikutnya: Fase 8 Development.

- **2026-09-24 · Claude Code · Fase 7F Testing → awaiting-gate** — Putaran penuh. Runner 18/18 skip (sudah hijau di sumber `2e90c092c607038b`). Skrip bukti baru `web/scripts/observatory_evidence.py`: lima project × HP 390×844 touch + desktop 1440×900 (chapter geser/tap, tirai masuk/kembali, interaksi ruang, Return), rantai Next 5 hop, Back/Forward, direct+refresh, interupsi per project, model diblok, fps rantai; 6 viewport/edge/perf_quick dibaca dari ledger sidik jari sama. Paket `assets/renders/personal-observatory/evidence/` 17/17 pass, 3 MP4 + 2 contact sheet. Tanpa perubahan app; 5 jebakan ukur di skrip sendiri diperbaiki (interupsi + fps diulang lewat `--redo-*`). Berikutnya: gate pemilik + approve hint Q49 + keputusan kunci scroll.

- **2026-09-24 · Claude Code · Fase 7F Development → ready-for-test** — Build Q49 + walkthrough Playwright 390×844 dan 1440×900: lima chapter diputar lewat tap; rantai Next 5 hop (tirai asal tutup → tirai tujuan buka: stage→blinds→roller→louvre→prism→stage), Return ke chapter asal, Back/Forward, scroll tidak terkunci, 0 error. Fix app: `observatory-shell.tsx` label `data-chapter` = chapter yang mengisi layar; `globals.css` Replay CrossCheck di baris kicker HP (matriks 360×740 276 → 325 px) + tinggi step aktif tetap di desktop (1440: scroll anchoring menggeser halaman 9 px saat scan). Tes: helper `web/scripts/q49.py`; suite `room`/`dispatch`/`monitor`/`time`/`studio`/`mobile`/`cases` + `perf_quick.py` (segmen putar-tap) diperbarui ke Q49; `verify_cases.py` cek tirai tiap hop. Verifikasi: lint/typecheck/build exit 0; runner 18/18 passed (sumber `2e90c092c607038b`); perf lima project 390×844 CPU 4×: semua segmen 53–60 fps, ≤4.8% frame lambat (terendah = tirai masuk case ±53 fps). Batas: emulasi Chromium, GPU host tidak di-throttle. Berikutnya: 7F Testing putaran penuh + paket `personal-observatory`.

- **2026-09-24 · Claude Code · Revisi pemilik Q49 — scroll native + tirai** — Keluhan pemilik: scroll menjalankan animasi dulu. Dilepas pin 178/270/380svh (hero, chapter, inspection field); Lenis `smoothWheel: false`; putaran instrumen via geser/tap (`orbits` di shell, kamera serah terima dari sudut terakhir `lead`); scan CrossCheck autoplay sekali + step/Replay. Transisi: `.curtain` lima gaya per case (`cases.ts` `curtain`), menggantikan iris + 4 flight. Berkas: `observatory-shell.tsx`, `observatory-scene.tsx`, `crosscheck-room.tsx`, `globals.css`, `page.tsx`, `cases.ts`, `instruments.ts`. Verifikasi: typecheck/lint bersih; Playwright dev :8768 (1440×900, 390×844) scroll/putar/5 tirai/scan lulus, 0 error. Belum: build + runner; skrip regresi lama basi → 7F. PLAN §3 Q49. Commit + push.

- **2026-09-24 · Claude Code · Gate 7E lolos → done** — Pemilik approve + izinkan perbaikan. Dilepas DRAFT BrandWall (app + 4 tes). Perbaikan: label mono 8 → 10 px (`globals.css` blok 7E), crop Overflow HP `phoneView` + hook `useWide` (`brandwall-room.tsx`/`.ts`). Verifikasi: lint/typecheck/build exit 0; runner `studio,cases,mobile,case,room,dispatch,monitor,time,showpiece,desktop-b,perf-brandwall` passed (sumber `4bf13e4158597b83`); paket bukti 17/17. Keputusan disalin ke PLAN §3 Q48. Commit + push. Berikutnya: 7F Development.

- **2026-09-24 · Claude Code · Fase 7E Testing → awaiting-gate** — Aturan ringan Q47. Runner: `studio`/`cases`/`mobile` + suite berkas bersama sudah `passed` di sidik jari `d97d12160a89721c` → tidak diulang. Skrip baru `web/scripts/brandwall_room_evidence.py` (impor `verify_brandwall_room.viewport` 390×844 + 1440×900 dan `edges`, fps dari `perf-quick/brandwall.json`): paket `assets/renders/personal-brandwall/evidence/` 17/17 pass, video 45 + 27 dtk, contact sheet. Tanpa perubahan kode app; CODEMAP pohon berkas dilengkapi berkas 7E. Berikutnya: gate 7E oleh pemilik (approve copy + 2 temuan keterbacaan).

- **2026-09-24 · Claude Code · Fase 7E Development → ready-for-test** — Lanjutkan verifikasi final Codex: lint/typecheck/build exit 0; `perf-brandwall` passed di GPU Intel (55.5–60 fps, ≤3.3% lambat; gagal lama = rig llvmpipe); fix 2 tes basi DRAFT (`verify_mobile.py`, `verify_case.py`); runner passed `mobile`/`case`/`cases`/`room`/`dispatch`/`monitor`/`time`/`showpiece` 390×844 + `desktop-b` (sumber `d97d12160a89721c`). Tanpa perubahan kode app. Berikutnya: 7E Testing (Q47).

- **2026-09-18 · Claude Code · aturan Testing ringan (Q47)** — Atas permintaan pemilik: Testing mulai 7E hanya fitur baru fase aktif (390×844 + 1440×900, regresi suite fase + `cases`/`mobile`, 2 video pendek, fps dari Development); 7F/8 tetap penuh. Diubah: PLAN §3 Q47 + §8.2 + §12.3, PROGRESS kontrak + checklist 7E, PROMPT. Tanpa perubahan kode; belum commit (ikut commit akhir 7E). Berikutnya: 7E Development.

- **2026-09-18 · Claude Code · Gate 7D lolos → done** — Pemilik "semuanya approved": copy 7D approved + 2 temuan diterima (Q46). DRAFT DueWatch dilepas (`cases.ts`, strip `page.tsx` → "Illustration", komentar kode, 3 tes mengharapkan 0 DRAFT). Verifikasi: lint/typecheck/build exit 0; `run_regressions.py --suites time,cases,mobile --phone-only cases,mobile` passed (sumber `de8440d2274dbcd4`). Commit + push. Berikutnya: 7E Development.

- **2026-09-17 · Claude Code · Fase 7D Testing → awaiting-gate** — Build utama terintegrasi (lint/typecheck/build exit 0). Runner 16/16 passed di sumber `f19aac05262f34b3` (`time` hijau setelah fix rig; `perf-surgeline` 57–60 fps, gagal salinan tidak terulang; fix tes basi `verify_cases`). Skrip bukti baru `duewatch_room_evidence.py` (22 item: walkthrough HP touch + desktop, jejak per frame pointer/cincin/jarum/sinyal, urutan pengingat, interupsi, slow-motion 0.25×, fps 4×, sumber; memanggil `verify_duewatch_room.viewport/edges`) → 22/22 (item desktopComposition dihitung ulang dari ukuran tersimpan setelah fix cek tepi audit). Tanpa perubahan kode app. Berikutnya: gate pemilik + approve copy DRAFT 7D + 2 keputusan temuan; belum commit/push.

- **2026-09-17 · Codex · 7D Development → ready-for-test, integrasi** — Agenda/triage, replay ledger, audit dan cincin; mobile → desktop di salinan. Lint/typecheck/build, enam viewport dan fps DueWatch passed.
  Pemilik minta integrasi setelah 7C stabil tanpa tes ulang; 15 berkas digabung, 7C dipertahankan. Regresi penuh belum selesai, edge rig dan fps SurgeLine tercatat untuk Testing; belum gate 7D.

- **2026-09-17 · Claude Code · Gate 7C lolos → done** — Pemilik "saya approve semua untuk 7C": copy 7C approved, DRAFT DriftWatch dilepas (`cases.ts`, strip `page.tsx`, komentar `driftwatch-room.ts`/`instruments.ts`, tes `verify_driftwatch_room.py`/`verify_cases.py`/`driftwatch_room_evidence.py` mengharapkan 0 DRAFT), README 7C = gate passed (Q45). Verifikasi: lint/typecheck/build exit 0; `run_regressions.py --suites monitor,cases,mobile --phone-only cases,mobile` passed (sumber `8b800e3ebedbbbb4`). Commit + push; `assets/development/phase-7d/` (Codex) tidak disentuh (tak dilacak git). Berikutnya: 7D Development/integrasi (Codex).

- **2026-09-17 · Claude Code · Fase 7C Testing → awaiting-gate** — Skrip bukti baru `driftwatch_room_evidence.py` (21 item: walkthrough HP touch + desktop, jejak per frame seismograf/pita/Compare, interupsi, slow-motion 0.25×, fps 4×, sumber; memanggil `verify_driftwatch_room.viewport/edges`). Bug: Compare memeras trace (lonjakan bergeser) → fix jendela `clipPath`. Verifikasi: lint/typecheck/build, runner 13/13 passed (sumber `a8336493ca0de6ca`), paket 21/21 (fps diukur ulang sendiri setelah percobaan pertama 10.5% lambat saat host sibuk). Codex paralel membuat salinan 7D (`assets/development/phase-7d/`, 19:35, sudah memuat fix). Berikutnya: gate pemilik + approve copy DRAFT 7C; belum commit/push.

- **2026-09-17 · Codex · handoff 7C tetap ready-for-test** — Baca PROGRESS → CODEMAP → PLAN terkait; tahap aktif Testing ditugaskan ke Claude Code / Antigravity (PLAN §12.2). Betulkan catatan CODEMAP yang masih menyebut 7C `todo`. Verifikasi sesi ini hanya membaca JSON tersimpan: ledger 13/13 `passed` pada sumber `40a56b14db159831`, monitor enam viewport + fallback/reduced `passed`, perf DriftWatch `passed`. Skrip `driftwatch_room_evidence.py` dan `personal-driftwatch/evidence/evidence.json` belum ada. Tidak menjalankan ulang tes atau mengubah aplikasi/PLAN. Berikutnya: buka sesi Testing Claude Code / Antigravity, buat paket bukti 7C sesuai Q42; belum gate, belum commit/push.

- **2026-09-17 · Codex → Claude Code · Fase 7C → ready-for-test** — Codex: ruang banding DriftWatch, trace chapter, pita jarum, arsip bukti, `verify_driftwatch_room.py` (terputus sebelum 1920/edge). Claude Code: ilustrasi Day 1–3 (tanggal kalender bentrok dengan soak asli), snapshot desktop sticky, tes trace stabil. Verifikasi: lint/typecheck/build, `perf_quick` driftwatch ≥57.8 fps, runner 13/13 passed (sumber `40a56b14db159831`). Berikutnya: Testing 7C + approve copy DRAFT.

- **2026-09-17 · Claude Code · Gate 7B lolos → done** — Pemilik "lulus semua": copy 7B approved, DRAFT SurgeLine dilepas, Cut sebelum Form diterima (Q44).
  Verifikasi: lint/typecheck/build exit 0; `run_regressions.py --suites dispatch,cases,mobile --phone-only cases,mobile` passed (sumber `1c556e5b73edefd6`). Commit + push. Berikutnya: 7C Development.

- **2026-09-17 · Codex · handoff 7B** — Cek hasil Testing tersimpan: 18/18 pass; berkas video/foto bukti tersedia.
  Rapikan catatan status CODEMAP; tanpa perubahan aplikasi atau tes ulang. Berikutnya: keputusan pemilik atas paket Testing 7B; 7C belum dimulai.

> Entri terbaru di atas. Singkat, 1–2 baris: tanggal · harness · fase — apa yang dikerjakan,
> verifikasi, berikutnya. Detail teknis taruh di CODEMAP / folder bukti, bukan di sini.

- **2026-09-16 · Claude Code · Fase 7B Testing → awaiting-gate** — Skrip bukti baru `surgeline_room_evidence.py` (18 item: walkthrough HP touch + desktop, jejak papan per frame untuk no-duplicate, pulsa, slow-motion 0.25×, fps 4×, sumber; memanggil `verify_surgeline_room.viewport/edges`). Bug: pulsa Return mendarat di tepi atas → fix `pulseHome` di shell. Verifikasi: lint/typecheck/build, runner 11 suite passed (sumber `37a4f3e3770463fb`), paket 18/18 pass. Berikutnya: gate pemilik + approve copy DRAFT + keputusan Cut sebelum Form.

- **2026-09-16 · Codex → Claude Code · Fase 7B → ready-for-test** — Codex: reducer/ledger/bukti rekaman, pulsa antena, `verify_surgeline_room.py`. Claude Code: papan dispatch A–F (GSAP transform, Cut/Resume/Replay, pose per stage), strip chapter 3 browser, layout desktop; fps gagal ternyata akar var CSS di root tiap frame (sama di HEAD) → dipindah ke elemen konsumen, chapter 48.7 → 60 fps. Verifikasi: lint/typecheck/build + runner 11 suite passed (perf-crosscheck setelah ulang). Berikutnya: Testing 7B + approve copy DRAFT.

- **2026-09-16 · Claude Code · Gate 7A lolos → done** — Pemilik "lulus semua aman": label DRAFT CrossCheck dilepas (`cases.ts` + 3 tes), build, `run_regressions.py --suites case,cases --phone-only case,cases` passed (34 + 88 dtk). Commit + push (Q38). Berikutnya: Development 7B dengan aturan Q42.

- **2026-09-16 · Claude Code · Fase 7A Testing → awaiting-gate** — Skrip bukti baru `crosscheck_room_evidence.py` (walkthrough HP touch + desktop wheel, slow-motion 0.25×,
  6 viewport + edge, fps 4× CPU, audit sumber). Temuan: regresi fps 7A (CSS akar tiap frame) + biaya scrub SVG → diperbaiki, diukur vs build HEAD. 8 suite regresi + paket diulang di build final:
  16/17 pass (`performance` gagal p95 ketat di scrub 52–54 fps). Keputusan pemilik Q42 (efisiensi tes) dicatat + diterapkan: `run_regressions.py` (ledger, skip, `--phone-only`),
  `perf_quick.py` (gerbang fps dev), hook `OBSERVATORY_PHONES` di 4 suite. Berikutnya: gate pemilik + 2 keputusan temuan + approve copy DRAFT.

- **2026-09-16 · Claude Code · Fase 7A → ready-for-test** — Ruang inspeksi CrossCheck mobile → desktop: strip lane chapter sinkron lensa,
  iris lensa masuk/kembali, inspection field dari run asli (generator ber-assert dossier), finding desk 4 temuan berbukti, leader hanya saat model ada,
  teaser Next. Copy baru DRAFT. Verifikasi: lint/typecheck/build + `verify_crosscheck_room` 6 viewport + edge, 7 suite regresi passed; rig pulih,
  2 timing tes Lenis + path dossier diperbaiki. Berikutnya: Testing 7A + approve copy.

- **2026-09-16 · Claude Code · isi kartu Skills dijelaskan** — Permintaan pemilik lanjutan: tiap tool dijelaskan
  "itu apa dan gimana pakainya" (n8n, unittest, Playwright, dst), link project **tidak lagi per tool** tapi satu baris
  footer per kartu (`PROVEN IN`), dan tambah tools scripting yang gampang dipakai AI. Hasil: `lib/skills.ts` jadi 13 grup /
  37 tool; grup baru **Scripting & glue** (requests, BeautifulSoup, pandas, Typer/argparse, python-dotenv, rich) plus
  PyAutoGUI di Workflow automation dan pdfplumber di Reporting — tool baru ini **belum punya case file**, jadi kartunya
  sengaja tanpa baris `PROVEN IN` (sama seperti Daily work). Setiap `note` ditulis ulang jadi penjelasan 15–25 kata.
  Komponen: `proofOf(group)` menggabungkan project seluruh grup, dirender di footer sebagai link `data-skill-project`.
  Cek bukti `full_observatory_evidence.py` diubah dari per-item ke per-kartu (link nyasar, grup tanpa case file,
  tool tanpa deskripsi); `UNCONFIRMED` dikosongkan karena Go/MySQL/TiDB/Redis sudah dikonfirmasi pemilik 2026-09-15.
  Diukur di Chrome 149: 13 kartu / 37 tool, 0 tool tanpa deskripsi, 0 link nyasar, 0 link tersisa di dalam daftar tool,
  klik link footer → `#crosscheck` top 0 + highlight + heading fokus, 0 kartu terpotong, overflow 0 (1440×900 & 390×844).
  lint/typecheck/build pass. Berikutnya: review pemilik.

- **2026-09-16 · Claude Code · Skills jadi deck kartu** — Atas permintaan pemilik (dropdown dinilai berat sebelah ke kanan):
  `#skills` tidak lagi accordion `<details>` dua kolom. Komponen baru `web/components/skill-deck.tsx` menampilkan 12 grup
  sebagai kartu bertumpuk yang bisa di-drag/swipe, melingkar (kartu selalu ada di kiri dan kanan), plus tombol panah, titik
  per grup (aria-label = nama grup) dan readout. Geometri kipas (`--deck-spread/-drop/-tilt/-scale/-step`) hidup di CSS per
  breakpoint, JS hanya membacanya. Dua kartu tiap sisi tetap terbaca (opacity 75% lalu 50%, blur 0,5 px/jarak), kartu ketiga
  nol tepat di batas clamp supaya wrap tak berkelebat. Isi kartu mengikuti permintaan kedua pemilik: kategori → deskripsi
  singkat (`blurb`) → daftar tools, tiap tool dengan satu baris keterangan (`note`) + link project → footer
  "Same job, other tools" (`swaps`; padanan di lapangan, **bukan** klaim pengalaman). `blurb`, `note`, `swaps`
  adalah field baru di `lib/skills.ts`; copy-nya **di-approve pemilik 2026-09-16** ("lulus semua approved"). Tanpa JS kartu tampil
  sebagai tumpukan biasa (`data-enhanced=false`), reduced-motion mematikan transisi lewat aturan global.
  Diukur di Chrome 149 (1440×900 + 390×844): klik link project → `#crosscheck` top 0 + `skill-highlight` + heading fokus;
  drag melewati link tidak ikut navigasi; panah/panah-kiri-kanan/dot/klik kartu tetangga semua memindah kartu; wrap 01 → 12
  jalan; overflow horizontal 0; tak ada kartu terpotong. Skrip bukti (`desktop_evidence.py`, `full_observatory_evidence.py`,
  `verify_desktop.py`, `verify_mobile.py`) diperbarui ke selector deck (`h3` grup, `h4` skill). lint/typecheck/build pass.
  Pemilik menyatakan lulus + approve, lalu minta commit + push.

- **2026-09-16 · Codex · revisi rencana personalisasi** — PLAN/PROGRESS: brief lima project, fase 7A–7F,
  mobile dulu → desktop utama. Cek sumber dossier dan konsistensi tracker; berikutnya 7A Development.

- **2026-09-16 · Claude Code · fix cincin gerbang lompat** — Laporan pemilik: line art di loading screen "teleport ke kanan
  bawah" saat Enter diklik. Sebab terukur: GSAP melipat transform dan membuang `translate` milik lapisan parallax
  (`translate: none` di inline style). Saat pointer pernah bergerak, `translate` bernilai `calc(-50% + …px)` yang tak bisa
  diurai GSAP, jadi centring −50%/−50% hilang → pusat cincin lompat **+465 px kanan, +465 px bawah** (separuh lebarnya,
  mendarat di area observatorium). Kalau pointer belum digerakkan nilainya pas `-50% -50%` dan lolos — itu sebabnya
  luput di uji pertama. Perbaikan: tiap lapisan dipecah jadi pembungkus (posisi + parallax lewat `translate`, tak
  disentuh GSAP) dan `<i>` di dalamnya (yang di-scale GSAP); timeline menyasar `.gate-rings i` / `.gate-stars i`.
  Diukur ulang: selama tween, drift pusat cincin **7,4 px konstan** (sisa easing parallax, bukan lompatan) sementara
  lebarnya 940 → 1402 px; frame-diff canvas 34 → 6,5 tanpa nol/lonjakan. lint/typecheck/build pass. Berikutnya: review pemilik.
- **2026-09-16 · Claude Code · revisi gerbang desktop** — Atas permintaan pemilik: gerbang ≥1024px jadi satu kolom di tengah
  (dial → kicker → judul → status → track → Enter → tanpa suara), tombol Enter di sumbu tengah, bukan lagi rail kanan.
  Ditambah field parallax berlapis (`.gate-field`: bintang, cincin orbit, horizon) yang digerakkan pointer lewat
  `--gate-px/--gate-py` (lerp di `gsap.ticker`, hanya desktop + pointer halus), arrival stagger CSS (`gate-arrive`,
  `animation-fill-mode: backwards` supaya timeline GSAP tetap boleh ambil alih transform), exit berlapis saat Enter
  (kontrol terangkat dari bawah ke atas, cincin + bintang mengembang, gerbang memudar). HP tidak disentuh.
  Diukur di Chrome 149 (Playwright MCP, 1440×900 + 1280×720 + 390×844): Enter di sumbu 715,8 px = sumbu gerbang
  (selisih 0 px; `innerWidth/2` = 720 px karena scrollbar), lapisan cincin +25,8 px vs `.gate-main` −16,9 px pada
  pointer sama (parallax nyata), exit 0→hidden ±1,05 dtk dengan judul −34 px dan cincin 1,0→1,49, Lenis aktif
  (`html.lenis-smooth`, wheel 600 → 549 px lalu 1193 px), gerbang muat tanpa scroll dalam di 1280×720 dan 1440×900.
  **Revisi 2 (serah-terima gerbang → hero):** pemilik menilai transisi masih kasar. Adegan 3D kini ikut bergerak
  menembus fade — `revealed` di `observatory-scene.tsx` didamp lebih lambat (1,6 desktop, 2,2 HP tak berubah) dan
  dipakai sebagai `arrival` (desktop saja) untuk sudut kamera +0,2 rad, elevasi +0,07, zoom −5,5%, kubah turun 0,7
  unit + kecil 5%, semuanya mereda ke nol; langit ikut bergeser karena offset bintang mengikuti sudut kamera.
  `ScrollTrigger.refresh()` dipindah ke awal Enter (saat gerbang masih menutup) supaya tak menggeser hero di
  tengah fade; gerbang memudar 0,16→0,96 dtk (`sine.inOut`), chrome situs mulai 0,3 dtk (`.site-content` desktop),
  hero copy 0,5→1,65 dtk. Diukur dari piksel canvas (32×20, `drawImage` tiap frame): perubahan antar-frame
  23,8 → 22 → 19 → 13 → 9 → 5 → 3 → 1,3 (idle) tanpa nol dan tanpa lonjakan = gerak menyambung, bukan potong;
  overlap opacity gerbang 1→0 (1,08 dtk) vs konten 0→1 (1,2 dtk) vs hero 0→1 (1,5 dtk) bertindih tanpa celah.
  `desktop_evidence.py` item `gate` diperbarui ke layout tengah + cek parallax. lint/typecheck/build pass (2×).
  **Blocker tes:** `verify_desktop.py`/`verify_mobile.py` (venv `crosscheck`, Playwright 1.62) gagal karena canvas R3F
  tak pernah di-resize (tetap 300×150, `data-scene=loading`) di Chrome for Testing 149 dan 151, headless maupun headed —
  direproduksi juga pada kode sebelum revisi (git stash), jadi bukan akibat revisi ini. Berikutnya: review pemilik + perbaiki rig tes.
- **2026-09-16 · Codex · revisi planet → ready-for-test** — Delapan planet berurutan, satu tiap tahap, orbit idle berulang; reset chapter dan fade shader dibenahi.
  Build/lint/typecheck, uji jalur, dan 19 cek browser lulus (0 error); foto/video di `assets/renders/planetary-motion/dev/`, preview :8780.
- **2026-09-16 · Codex · singularity dihapus** — Shader dibuang; prompt upgrade lima instrumen disiapkan, belum dieksekusi.
  Build/TypeScript/lint lulus; preview tetap :8769.
- **2026-09-16 · Codex · revisi observatorium → ready-for-test** — Kubah detail bergerak, planet/parallax desktop, horizon, reduced motion.
  Build/lint/typecheck + regresi desktop/mobile + 8 cek motion lulus; preview :8769, foto/video di `assets/renders/observatory-motion/dev/`. Berikutnya: review visual revisi.
- **2026-09-16 · Claude Code · Fase 7 → done** — Pemilik nyatakan lolos; jeda instrumen ±3 dtk diterima. Commit + push ke `origin main`.
  Berikutnya: Fase 8 Development (meta/share card/favicon, deploy Vercel).
- **2026-09-16 · Claude Code · Fase 7 → awaiting-gate** — Testing ulang: item bukti baru `enterEarly`, paket bukti 14/14 pass
  (Enter aktif 6.39 dtk), 6 suite regresi + lint/typecheck diulang pass. Berikutnya: gate pemilik.
- **2026-09-16 · Claude Code · Fase 7 → ready-for-test** — Enter lebih cepat: instrumen dimuat di belakang hero, preload, font WOFF2.
  Diukur: slow 4G 12.46 → 7.01 dtk; lint/typecheck/build + 6 suite regresi pass. Berikutnya: Testing ulang + gate.
- **2026-09-16 · Claude Code · revisi lima instrumen** — Atas permintaan pemilik: kelima instrumen dibangun ulang
  secara prosedural di `web/components/instrument-models.ts` memakai kit/palet yang sama dengan observatorium
  (perak, navy, kuningan terkendali, lampu amber, kaca optik). Bentuk baru: CrossCheck tiga kanal berbafel + kolar
  fokus berputar; SurgeLine empat reflektor parabola bersegmen + feed horn di tiga strut, bearing dan penggerak;
  DriftWatch sasis termesin dengan jalur kertas nyata (gulungan suplai, rol penggerak bergigi, pemandu tegangan);
  DueWatch tiga lintasan bergigi di bidang berbeda + rangkaian roda gigi terlihat; BrandWall bangku optik berel
  bergraduasi (lampu, kolimator, panggung prisma berputar, cincin detektor, layar penerima). Anchor `cases.ts` dan
  nama material rig dipertahankan; rig DueWatch memakai `PlanetPivot{i}`, CrossCheck memakai `FocusPivot{i}`.
  Bug ditemukan+diperbaiki: geometri statis hasil merge sempat mendarat di root sehingga leader line `*Mount`
  diam-diam gagal — sekarang tiap mount jadi target merge sendiri dan geometri mount diurut sebelum pivot anaknya.
  Delapan skrip verifikasi yang memicu fallback dengan memblokir GLB instrumen dialihkan ke `ambient.glb`
  (satu-satunya model yang masih diunduh). Ukur: model 580 KB → 34 KB; segitiga CrossCheck 118k → 50k, SurgeLine
  34k → 51k, DueWatch 30k → 41k; draw call naik (mis. SurgeLine 39 → 70); frame 16,70 ms median / 16,8 ms p95
  sebelum dan sesudah (tanpa regresi terukur); waktu sampai gerbang Enter tertutup ±1,74 dtk → ±1,89 dtk (+150 ms,
  JS +24 KB). lint/typecheck/build + `verify_instruments` (baru, before+after) + `verify_observatory_motion` +
  `verify_cases`/`verify_case`/`verify_mobile`/`verify_desktop`/`verify_showpiece`/`verify_audio` semua pass.
  Bukti: `assets/renders/instrument-detail/` (before/after, `compare-*.jpg`, `walkthrough.webm`, `frame-cost-*.json`).
  Berikutnya: Fase 8 Development.
- **2026-09-16 · Claude Code · Fase 7 → in-dev** — Pemilik pilih opsi B (Enter lebih cepat). Belum dikerjakan atas permintaan pemilik;
  spesifikasi + data ukur ditulis di checklist Fase 7 Development. Aturan baru: commit + push wajib tiap akhir fase (PROMPT).
  Commit + push kerja Fase 7 atas permintaan pemilik. Berikutnya: sesi Development khusus item itu.
- **2026-09-15 · Claude Code · Fase 7 → awaiting-gate** — Testing: paket bukti 13/13 pass (MP4 bersuara, performa §11 lewat emulasi),
  fix tes `verify_desktop`; 6 suite regresi pass. Temuan Enter ±12 dtk di slow 4G diajukan. Berikutnya: gate pemilik.
- **2026-09-15 · Codex + Claude Code · Fase 7 → ready-for-test** — Codex: suara klik/sweep, loader dial, micro-interaksi, timeline transisi + 2 tes fokus.
  Claude Code menutup: build ulang, lint/typecheck/build + `verify_audio` 9/9 + `verify_showpiece`/`verify:mobile`/`verify_case`/`verify_desktop` pass. Berikutnya: Testing (performa §11, paket bukti), gate.
- **2026-09-15 · Claude Code · Fase 6 → done** — Testing desktop: fix grid About/Skills, skrip + paket bukti (MP4 1440×900, 21 item), regresi HP + desktop pass.
  Pemilik nyatakan lolos. Berikutnya: Fase 7 Development.
- **2026-09-15 · Codex · Fase 6 → ready-for-test** — Layout desktop homepage + lima case, header nav, kamera/hotspot responsif.
  lint/typecheck/build + regresi tiga HP + tiga desktop/resize/fallback pass; berikutnya: Claude Code/Antigravity Testing, paket video/foto, gate pemilik.
- **2026-09-15 · Antigravity · Fase 5 → done** — Pemilik nyatakan lolos + approve copy ("semuanya lulus dan approved, duewatch opsi no 1"). Label DRAFT 4 case dilepas (`lib/cases.ts`), `verify_cases` + `case_files_evidence` (17/17 pass) + `verify:mobile` + build/typecheck/lint diulang dan lolos. Fase 5 selesai. Berikutnya: Fase 6 Development.
- **2026-09-15 · Antigravity · Fase 5 → awaiting-gate** — Testing: paket bukti 17 item (`case_files_evidence.py`), MP4 walkthrough 390×844 rantai penuh (130 s), contact sheet 24 frame, viewports sheet, `evidence.json` (17/17 pass). Catatan video DueWatch diajukan. Berikutnya: approve copy 4 case + keputusan video DueWatch, lalu gate.
- **2026-09-15 · Claude Code · Fase 5 → ready-for-test** — 4 case file baru (copy DRAFT, video asli) di satu template + Next berantai.
  lint/typecheck/build + `verify_cases`/`verify_case`/`verify:mobile` 3 viewport pass. Berikutnya: Testing, paket bukti, approve copy + gate.

- **2026-09-15 · Claude Code · revisi 3 (langit + leader)** — Atas permintaan pemilik: bintang setara gate, hanya 30% atas
  (70% bawah sangat jarang); marker 01→tabung atas, 03→lens kiri, garis tak lagi memotong instrumen. lint/typecheck/build +
  `verify_case` 3 viewport + bukti 3/3 pass (jarak ≥58px) + video walkthrough. Pemilik oke → commit + push. Berikutnya: Fase 5 Development.
- **2026-09-15 · Claude Code · Fase 4 → done** — Pemilik nyatakan lolos + approve copy. Label DRAFT case dilepas, `verify_case` disesuaikan;
  `assets/` di-ignore + untrack (file lokal utuh). Build + `verify_case` diulang; commit + push. Berikutnya: Fase 5 Development.
- **2026-09-15 · Claude Code · Fase 4 → awaiting-gate** — Testing: fix TypeError home→case (guard trigger homepage basi),
  `case_crosscheck_evidence.py` 14/14 pass + MP4/contact sheet; temuan flight-in lemah diajukan ke pemilik. Berikutnya: approve copy + gate.
- **2026-09-15 · Codex · Fase 4 → ready-for-test** — Route CrossCheck, kamera persisten, 3 hotspot, alur, Readings, tools, video English; copy DRAFT.
  lint/typecheck/build + case/homepage 3 viewport + fallback fix pass. Berikutnya: Claude Code/Antigravity Testing, paket bukti, approval copy + gate.
- **2026-09-15 · Claude Code · revisi langit (2)** — Atas permintaan pemilik: gelap hanya 30% atas, bintang dikurangi.
  Bukti 8/8 pass diperbarui. Berikutnya: approve label BrandWall, lalu Fase 4.
- **2026-09-15 · Claude Code · revisi langit + animasi** — Langit berbintang, Saturnus hidup, animasi baru 5 instrumen.
  `verify:mobile` + bukti 8/8 pass. Berikutnya: review pemilik, lalu Fase 4.
- **2026-09-15 · Claude Code · repo git** — Repo `main` dibuat + snapshot Fase 3 (`ad65a06`), push ke
  github.com/rayinailham/rayin-observatory (public, akun personal). Berikutnya: revisi langit/planet/animasi instrumen.
- **2026-09-15 · Claude Code · Fase 3 susulan** — Go, MySQL/TiDB, Redis dipasang (grup "Daily work").
  Build + `verify:mobile` diulang. Berikutnya: Fase 4 Development.
- **2026-09-15 · Claude Code · Fase 3 → done** — Pemilik nyatakan lolos + approve copy. Label DRAFT dilepas,
  tes disesuaikan; build + `verify:mobile` diulang. Berikutnya: Fase 4 Development.
- **2026-09-15 · Claude Code · Fase 3 → awaiting-gate** — Lanjut kerja Codex: fix notice still view menimpa copy,
  pasang kontak asli dari pemilik, skrip bukti Testing. lint/typecheck/build + `verify:mobile` 3 viewport pass;
  paket bukti 16/16 pass, video + contact sheet dikirim. Berikutnya: gate + approve copy.
- **2026-09-15 · Codex · Fase 3 dev (kuota habis)** — Empat instrumen Blender/GLB, lima chapter, Skills, About,
  Contact placeholder. Verifikasi final belum selesai saat berhenti.
- **2026-09-15 · Claude Code · rencana** — Atas permintaan pemilik: fase dipecah Development/Testing, gate dari paket
  bukti, tes HP manual → Fase 8. Diubah: PLAN §3/§11/§12, PROMPT, PROGRESS, README, CODEMAP. Berikutnya: Codex Fase 3 dev.
- **2026-09-15 · Claude Code · Fase 2 → done** — Pemilik nyatakan lolos. PROGRESS/README/CODEMAP diset ke Fase 3
  (`todo`). Server :8767 + tunnel masih hidup. Berikutnya: Fase 3.
- **2026-09-15 · Claude Code · Fase 2 bukti ulang** — Link tak terbuka di HP pemilik; dari sini publik 200,
  emulasi iPhone WebKit + Android Pixel 7 lewat link: siap <4 dtk, 0 error. Fix flaky `verify_mobile.py`
  (tunggu posisi, bukan jeda); passed 3 viewport via URL publik. Video + `00-contact-sheet.jpg` dikirim. Tetap awaiting-gate.
- **2026-09-15 · Claude Code · Fase 2 → awaiting-gate** — Lanjut kerja Codex: fix Menu → Work (Lenis
  `start()` membatalkan `scrollTo`), planet ditambat ke kamera (tak lagi menabrak teleskop), README/CODEMAP,
  `chapter_walkthrough.py`. `verify:mobile` passed 3 viewport; video via URL publik. Berikutnya: approve copy + gate.
- **2026-09-15 · Codex · Fase 2 (kuota habis)** — `export_crosscheck.py` → `crosscheck.glb`; chapter sticky,
  orbit kamera, idle lensa/ayun, dialog case preview, `verify_mobile.py` Fase 2. Belum diverifikasi saat berhenti.
- **2026-09-15 · Claude Code · Fase 1 → done** — Tes bukti gate 3 browser (`web/scripts/gate_evidence.py`),
  semua lolos; foto + video dikirim. Pemilik nyatakan lolos. Berikutnya: Fase 2.
- **2026-09-15 · Codex · Fase 1** — Bangun `web/` (Next.js + R3F + GSAP/Lenis): gerbang, hero kubah, suara,
  scroll; GLB dari Blender. Build/lint/typecheck + `verify_mobile.py` lolos; preview via tunnel.
- **2026-09-14 · Claude Code · Fase 0 → done** — Pemilik nyatakan lolos; palet/font final di PLAN §8.
  Preview LAN diblok ufw: `sudo ufw allow from 192.168.1.0/24 to any port 8766 proto tcp`.
- **2026-09-14 · Codex · Fase 0** — Foto, kubah, teleskop, layar contoh HP dibuat; audit 3 browser lolos.
- **2026-09-14 · Claude Code · pra-Fase 0** — Blender + MCP terpasang; grilling selesai; PLAN/PROMPT/PROGRESS/CODEMAP dibuat.
