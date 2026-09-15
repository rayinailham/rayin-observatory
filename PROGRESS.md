# PROGRESS — Tracker Rayin Observatory

> Sumber kebenaran status kerja. Diupdate di akhir **setiap** sesi (lihat `PROMPT.md`).
> Status: `todo` · `in-dev` · `ready-for-test` · `in-test` · `awaiting-gate` · `done` · `deferred`
> Mulai Fase 3 (PLAN §12, Q31): tahap **Development** = Codex (utama) / Claude Code;
> tahap **Testing** = Claude Code / Antigravity, menghasilkan paket bukti video + foto untuk gate.

## Status saat ini

| Hal | Isi |
|---|---|
| Fase aktif | **Fase 5 — All case files** · Development belum mulai |
| Status fase | `todo` |
| Bagian PLAN.md yang relevan | §4 (peta situs), §5 (lima instrumen + urutan), §6 (alur scroll), §7 (template case + transisi), §8 (identitas FINAL), §9 (skills), §10 (aturan copy), §11 (arsitektur), §12 (target fase) |
| Blocker | Tidak ada |
| Preview sesi ini | Lokal `http://127.0.0.1:8767/work/crosscheck`; tunnel tidak dinyalakan. Bukti Testing `assets/renders/case-crosscheck/evidence/` |
| Revisi terakhir | Revisi 3 (bintang jarang hanya 30% atas + leader 01/03 ditukar lens) diterima pemilik ("okay push and commit"); bukti `assets/renders/revision-sky-lines/evidence/` |
| Langkah berikut | Codex / Claude Code: Fase 5 Development (case SurgeLine, DriftWatch, DueWatch, BrandWall + Next berantai), pola template case CrossCheck |

## Ringkasan fase

| Fase | Nama | Status | Gate lolos (tanggal) |
|---|---|---|---|
| 0 | Style lock | `done` | 2026-09-14 |
| 1 | First light | `done` | 2026-09-15 |
| 2 | One instrument alive | `done` | 2026-09-15 |
| 3 | Full observatory | `done` | 2026-09-15 |
| 4 | First case file | `done` | 2026-09-15 |
| 5 | All case files | `todo` | — |
| 6 | Desktop | `todo` | — |
| 7 | Showpiece polish | `todo` | — |
| 8 | Launch ready | `todo` | — |
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
- [ ] Case file SurgeLine, DriftWatch, DueWatch, BrandWall
- [ ] "Next instrument" berantai; copy DRAFT → `ready-for-test`

Testing (Claude Code / Antigravity):
- [ ] Tes otomatis 5 case file + rantai Next; bug diperbaiki + tes ulang
- [ ] Paket bukti `assets/renders/case-files/evidence/` dikirim
- [ ] Semua copy case file di-approve
- [ ] Gate

### Fase 6 — Desktop
Development (Codex / Claude Code):
- [ ] Layout desktop homepage + case file (komposisi lebar) → `ready-for-test`

Testing (Claude Code / Antigravity):
- [ ] Tes otomatis viewport laptop/monitor (mis. 1366×768, 1440×900, 1920×1080) + HP tidak rusak
- [ ] Paket bukti `assets/renders/desktop/evidence/` (video di viewport desktop) dikirim
- [ ] Gate

### Fase 7 — Showpiece polish
Development (Codex / Claude Code):
- [ ] Sound design lengkap (klik instrumen, transisi)
- [ ] Micro-interaksi, loader final, transisi dihaluskan → `ready-for-test`

Testing (Claude Code / Antigravity):
- [ ] Performa sesuai target PLAN §11 lewat emulasi (CPU throttle + 4G lambat, fps, ukuran aset)
- [ ] Paket bukti `assets/renders/showpiece/evidence/` dikirim
- [ ] Gate

### Fase 8 — Launch ready
Development (Codex / Claude Code):
- [ ] Meta, share card (preview WhatsApp/LinkedIn), favicon
- [ ] Deploy Vercel; instruksi sambung domain untuk pemilik → `ready-for-test`

Testing (Claude Code / Antigravity):
- [ ] QA lintas browser (Chromium/Firefox/WebKit) + viewport HP/tablet/desktop
- [ ] Paket bukti `assets/renders/launch/evidence/` dikirim
- [ ] Tes manual pemilik di HP fisik (satu-satunya; rasa scroll, fps, suara, 4G)
- [ ] Gate

### Fase 9 — Accessibility (ditunda)
- [ ] Mode gerak minimal, keyboard, screen reader

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

## Log sesi

> Entri terbaru di atas. Singkat, 1–2 baris: tanggal · harness · fase — apa yang dikerjakan,
> verifikasi, berikutnya. Detail teknis taruh di CODEMAP / folder bukti, bukan di sini.

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
