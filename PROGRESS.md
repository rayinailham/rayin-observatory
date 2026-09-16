# PROGRESS — Tracker Rayin Observatory

> Sumber kebenaran status kerja. Diupdate di akhir **setiap** sesi (lihat `PROMPT.md`).
> Status: `todo` · `in-dev` · `ready-for-test` · `in-test` · `awaiting-gate` · `done` · `deferred`
> Mulai Fase 3 (PLAN §12, Q31): tahap **Development** = Codex (utama) / Claude Code;
> tahap **Testing** = Claude Code / Antigravity, menghasilkan paket bukti video + foto untuk gate.

## Status saat ini

| Hal | Isi |
|---|---|
| Fase aktif | **Fase 7A — CrossCheck: inspection room** · Development |
| Status fase | `todo` |
| Bagian PLAN.md yang relevan | §3 Q41, §5.1 (CrossCheck), §7 (kontrak isi), §8.1–§8.2 (visual/motion/mobile → desktop), §10 (copy), §11 (performa), §12 (fase personalisasi) |
| Blocker | Rig tes: `verify_desktop.py` / `verify_mobile.py` di venv `crosscheck` (Playwright 1.62) gagal — canvas R3F tetap 300×150, `data-scene=loading`, Chrome for Testing 149/151, headless + headed; direproduksi pada kode lama, perlu re-provision engine |
| Preview sesi ini | Revisi planet: `http://127.0.0.1:8780/` · preview produksi lokal (`next start`) |
| Revisi terakhir | Skills deck kartu: 13 grup / 37 tool, tiap tool dijelaskan, link case file pindah ke footer kartu, grup baru "Scripting & glue". Revisi gerbang desktop sebelumnya tetap siap review |
| Langkah berikut | Development 7A: baca dossier CrossCheck lokal, susun brief personal, bangun chapter + case **mobile dulu**, lalu poles desktop sebagai tampilan utama; verifikasi → `ready-for-test`. Pulihkan rig browser sebelum mengklaim hasil visual lulus |
| Launch | Fase 8 menunggu gate 7A–7F. Catatan deployment terdahulu: Vercel CLI login 2026-09-16 (`chhrone`, scope `chhrones-projects`), `web/` belum `vercel link`; verifikasi lagi saat Fase 8. Testing produksi tetap mengikuti Q40 |

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
| 7A | CrossCheck — inspection room | `todo` | — |
| 7B | SurgeLine — dispatch room | `todo` | — |
| 7C | DriftWatch — monitoring room | `todo` | — |
| 7D | DueWatch — time control room | `todo` | — |
| 7E | BrandWall — visual studio | `todo` | — |
| 7F | Five rooms, one observatory | `todo` | — |
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

### Fase 8 — Launch ready
Prasyarat: gate 7A–7F lolos. Detail personalisasi dan bukti per project tetap wajib saat launch.

Development (Codex / Claude Code):
- [ ] Meta, share card (preview WhatsApp/LinkedIn), favicon
- [ ] Judul/deskripsi/share card lima case mengikuti cerita masing-masing, angka dan batas dossier
- [ ] Deploy Vercel (produksi); instruksi sambung domain untuk pemilik → `ready-for-test`

Testing (Claude Code / Antigravity) — **semua tes memakai URL Vercel, bukan preview lokal (Q40)**:
- [ ] QA lintas browser (Chromium/Firefox/WebKit) + viewport HP/tablet/desktop di URL Vercel
- [ ] CrossCheck: scan/matriks/temuan, entry lensa dan return tetap utuh di produksi
- [ ] SurgeLine: antrean/crash/resume, konfirmasi vs kegagalan, transisi antena tetap utuh
- [ ] DriftWatch: snapshot/diff/alarm, label tanggal dan transisi pita tetap utuh
- [ ] DueWatch: dua modul, eskalasi manusia, label simulasi/video dan transisi waktu tetap utuh
- [ ] BrandWall: specimen/tema, kontrol sebelum/sesudah dan transisi prisma tetap utuh
- [ ] Cek preview share (WhatsApp/LinkedIn) dari URL Vercel
- [ ] Paket bukti `assets/renders/launch/evidence/` dikirim
- [ ] Tes manual pemilik di HP fisik (satu-satunya; rasa scroll, fps, suara, 4G)
- [ ] Gate

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
| 2026-09-16 | Personalisasi cerita, visual, animasi dan transisi lima project dari `portfolio/` lokal; setiap fase mobile dahulu, lalu desktop sebagai tampilan utama. Sisipkan 7A–7E per project + 7F integrasi sebelum launch; fase aktif berikut 7A. Disalin ke PLAN §3 Q41 | Pemilik, chat sesi Codex |

## Log sesi

> Entri terbaru di atas. Singkat, 1–2 baris: tanggal · harness · fase — apa yang dikerjakan,
> verifikasi, berikutnya. Detail teknis taruh di CODEMAP / folder bukti, bukan di sini.

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
