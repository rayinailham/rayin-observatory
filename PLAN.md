# Rayin Observatory — Rencana Induk

> Web portofolio showpiece milik **Rayina Ilham** ("Rayin" = nama panggilan).
> Dokumen ini adalah hasil sesi grilling 2026-09-14. Semua keputusan di bawah **sudah dikunci**
> oleh pemilik; jangan diubah tanpa persetujuan eksplisit. Status kerja harian ada di
> `PROGRESS.md`, peta kode ada di `CODEMAP.md`, cara memulai sesi ada di `PROMPT.md`.

---

## 1. Ringkasan satu paragraf

Rayin Observatory adalah web portofolio berbahasa Inggris untuk **calon klien freelance**
(automation & QA). Bentuknya halaman scroll 2D yang super smooth (Lenis) dengan aset 3D buatan
sendiri dan animasi berat. Temanya **observatorium malam**: Rayina adalah operator yang
"mengawasi sistem klien", dan kelima project-nya tampil sebagai **lima instrumen** di dalam
observatorium. Tiap instrumen punya halaman **case file** sendiri; perpindahan ke sana memakai
transisi kamera yang terbang masuk ke instrumen, jadi pengunjung tidak pernah merasa keluar dari
observatorium. Dikerjakan **mobile-first**, desktop menyusul, dalam 10 fase bertarget non-teknis.

---

## 2. Tujuan dan penonton

| Hal | Keputusan |
|---|---|
| Penonton utama | Calon klien freelance (Upwork, DM, referral) yang butuh automation / QA |
| Aksi yang diinginkan | Klien menghubungi Rayina: **Book a call** / **Email me** |
| Ujian 30 detik | Dalam 30 detik klien harus paham: siapa Rayina, masalah apa yang bisa dibereskan, dan ada bukti angka |
| Bahasa konten | **Full English**. Tidak ada versi Indonesia |
| Nama di web | Brand: **Rayin Observatory**. Nama lengkap (About, meta): **Rayina Ilham** |
| Domain | Diurus sendiri oleh pemilik — **bukan tugas agen** |

---

## 3. Log keputusan grilling (dikunci)

| # | Topik | Keputusan |
|---|---|---|
| Q1 | Penonton | Calon klien freelance |
| Q2 | Bentuk web | **2D scroll + aset 3D**, animasi & transisi banyak. **Lenis wajib**, scroll harus sangat halus |
| Q3 | Metafora | **Observatorium** |
| Q4 | Konten non-project | **About**, **Skills & Tools** (hanya yang legit dicari perusahaan), **Contact** |
| Q5 | Device | **Mobile-first**, desktop belakangan |
| Q6 | Bahasa | Full English |
| Q7 | Ambisi | **Showpiece**, banyak fase, pelan-pelan; fase ditarget secara non-teknis |
| Q8 | Foto | Foto `/home/rayin/Documents/profile foto.jpg` **di-crop tanpa logo Amazon** (tidak ada afiliasi) + stilisasi duotone navy + garis scan |
| Q9 | Klik project | **Halaman case study sendiri** per project (`/work/<slug>`) |
| Q10 | Gaya visual | **Night observatory**: navy tinta, cahaya amber, sinyal hijau (OK) / merah (alarm), 3D stylized-realistic |
| Q11 | Peran 3D | **Instrumen = project**, planet & langit = latar ambient |
| Q12 | Animasi | Full animasi untuk semua. Aksesibilitas **ditunda** ke Fase 9 |
| Q13 | Skills | Terbukti di 5 project **+** skill kerja harian **+** "AI-assisted engineering". Tiap skill ditautkan ke project pembuktinya |
| Q14 | Suara | Ada, **default on** (nyala saat tap tombol Enter), toggle selalu tersedia |
| Q15 | Contact | Email + LinkedIn + GitHub personal + Upwork, CTA utama "Book a call" / "Email me". **Tanpa WhatsApp publik** |
| Q16 | Brand | **Rayin Observatory**; nama lengkap **Rayina Ilham** |
| Q17 | Mapping instrumen | Lihat §5 |
| Q18 | Urutan homepage | Hero → Work → Skills → About → Contact |
| Q19 | Intro | Gerbang **"Enter the Observatory"** dengan loader "calibrating instruments", plus "Enter without sound" |
| Q20 | Tampilan instrumen | Chapter full-screen yang **di-pin**; kamera memutari instrumen |
| Q21 | Template case study | Lihat §7 |
| Q22 | Navigasi | Header minimal + readout progres scroll; mobile: menu overlay bergaya panel kontrol |
| Q23 | Copy | Agen yang draft dari dossier, pemilik approve. Orang pertama, bahasa klien |
| Q24 | Aset 3D | Custom di Blender (via Blender MCP) untuk kubah + 5 instrumen; CC0 hanya untuk HDRI/tekstur |
| Q25 | Foto | Hanya di About |
| Q26 | Palet & font | Lihat §8 — **final**, disetujui pemilik di gate Fase 0 (2026-09-14) |
| Q27 | Transisi | **Kamera terbang masuk ke instrumen** saat buka case file; mundur saat kembali |
| Q28 | Stack | Next.js + React Three Fiber + GSAP ScrollTrigger + Lenis + TypeScript; hosting Vercel |
| Q29 | Urutan instrumen | CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall |
| Q30 | Fase | Lihat §12 |
| Q31 | Tahap fase & gate | (2026-09-15, setelah gate Fase 2) Mulai Fase 3 tiap fase = **Development** (Codex utama / Claude Code) → **Testing** (Claude Code / Antigravity) dengan paket bukti video + foto. Gate dinilai dari bukti; tes manual pemilik di HP fisik ditunda ke Fase 8. Lihat §12 |
| Q32 | Gate Fase 3 + copy homepage | (2026-09-15) Gate Fase 3 lolos dari paket bukti; seluruh copy homepage di-approve, label DRAFT dilepas. Kontak: rayinailham9@gmail.com, LinkedIn `in/rayinailham`, GitHub `rayinailham`, Upwork; label link menampilkan "Rayina Ilham". Skill kerja harian Go/MySQL/TiDB/Redis masih menunggu konfirmasi |
| Q33 | Skill kerja harian | (2026-09-15) Pemilik konfirmasi **Go, MySQL/TiDB, Redis** → dipasang di Skills sebagai grup "Daily work", tanpa tautan project dan tanpa nama pemberi kerja |
| Q34 | Gate Fase 4 + copy case CrossCheck | (2026-09-15) Gate Fase 4 lolos dari paket bukti ("lolos semua ini fase 4 aman"); copy case CrossCheck di-approve, label DRAFT dilepas; transisi flight-in diterima apa adanya. Folder `assets/` tidak lagi dilacak git (lokal saja) |
| Q35 | Gate Fase 5 + copy 4 case baru | (2026-09-15) Gate Fase 5 lolos dari paket bukti ("semuanya lulus dan approved, duewatch opsi no 1"); copy 4 case baru (SurgeLine, DriftWatch, DueWatch, BrandWall) dan blok Next CrossCheck di-approve, seluruh label DRAFT dilepas. Video DueWatch diterima dengan opsi 1 (catatan tanggal simulasi di bawah video dipertahankan) |
| Q36 | Gate Fase 6 (Desktop) | (2026-09-15) Gate Fase 6 lolos dari video bukti desktop ("okay semuanya lolos catat"); layar pertama case file desktop (brief dua kolom, instrumen di bawah lipatan) diterima apa adanya |
| Q37 | Enter lebih cepat | (2026-09-16) Temuan Testing Fase 7 (Enter baru aktif ±12 dtk di slow 4G): pemilik pilih opsi B — Enter aktif setelah hero siap (kubah + planet + font), lima instrumen dimuat di belakang hero. Fase 7 kembali ke Development; dikerjakan sesi berikut (spesifikasi di PROGRESS Fase 7) |
| Q39 | Gate Fase 7 (Showpiece) | (2026-09-16) Gate Fase 7 lolos dari paket bukti Testing ulang 14/14 ("lolos commit dan push"); Enter aktif 6.39 dtk di slow 4G. Temuan jeda ±3 dtk (chapter/case tampil tanpa model, garis penunjuk case sempat bertemu di ruang kosong) **diterima apa adanya**. Berikutnya Fase 8 Launch ready |
| Q38 | Commit + push akhir fase | (2026-09-16) Setiap akhir fase (gate lolos → `done`) **wajib** git commit + push ke `origin main` (akun personal). Di luar akhir fase tetap hanya atas permintaan pemilik. Aturan di `PROMPT.md` |

---

## 4. Peta situs

```
/                     Homepage (satu scroll story)
  ├─ Gate             "Enter the Observatory" (loader + Enter / Enter without sound)
  ├─ Hero             kubah terbuka, langit, satu kalimat siapa Rayina
  ├─ Work             5 chapter instrumen (di-pin), tiap chapter → "Open case file"
  ├─ Skills           daftar skill & tools, tiap item tertaut ke project pembuktinya
  ├─ About            foto (reveal "scan"), cerita singkat Rayina Ilham
  └─ Contact          CTA Book a call / Email me + LinkedIn, GitHub, Upwork
/work/crosscheck      Case file CrossCheck
/work/surgeline       Case file SurgeLine
/work/driftwatch      Case file DriftWatch
/work/duewatch        Case file DueWatch
/work/brandwall       Case file BrandWall
```

---

## 5. Lima instrumen

Sumber materi tiap project: `/home/rayin/Projects/Testing/portfolio/CAPABILITY_<NAMA>.md`.
Detail isi project **belum dibahas**; dibahas saat fase copy (Fase 2–5).

| Urutan | Project | Fungsi singkat | Instrumen | Gerakan idle khas |
|---|---|---|---|---|
| 1 | **CrossCheck** | Automated web QA lintas browser | **Teleskop 3 lensa** (3 engine browser, satu target) | lensa bergantian menyala, tabung sedikit mengayun |
| 2 | **SurgeLine** | Bulk form automation tahan crash | **Antena array** (banyak piringan mengirim sinyal bersamaan) | piringan berputar bergelombang, pulsa sinyal |
| 3 | **DriftWatch** | Scraping + alarm saat sumber berubah | **Seismograf** (jarum menggambar garis, ada lonjakan) | jarum bergetar, kertas bergulir, sesekali lonjakan merah |
| 4 | **DueWatch** | Expiry tracking + auto follow-up | **Orrery / jam astronomi** | cincin berotasi dengan kecepatan berbeda |
| 5 | **BrandWall** | Design QA / visual brand testing | **Spektrograf prisma** (cahaya dipecah jadi pita warna) | prisma berputar pelan, pita warna bergeser |

Aset tambahan: **kubah observatorium** (hero + gerbang), **langit + planet ambient** (latar).

---

## 6. Alur scroll homepage (mobile-first)

1. **Gate** — layar navy, readout "Calibrating instruments… 87%" mengikuti progres loading
   aset. Selesai → tombol **Enter the Observatory** + tautan kecil **Enter without sound**.
   Tap Enter = suara ambient nyala (aturan browser: audio butuh interaksi pertama).
2. **Hero** — kubah terbuka, langit dan planet bergerak lambat. Satu kalimat posisi
   (draft awal: *"Rayina Ilham — I watch your systems so you don't have to."*), satu CTA sekunder
   ke Contact.
3. **Work** — lima chapter full-screen yang di-pin. Tiap chapter: kamera memutari instrumen
   mengikuti scroll, muncul **pitch 1 kalimat**, **1 angka bukti** (gaya readout), dan tombol
   **Open case file**.
4. **Skills** — dikelompokkan (lihat §9). Tap skill → sorot project yang membuktikannya.
5. **About** — foto ter-crop dengan reveal "scan", paragraf singkat orang pertama.
6. **Contact** — CTA utama besar, lalu tautan sekunder.

Header tetap: logo "Rayin Observatory" + Work / About / Contact + toggle suara. Readout progres
scroll bergaya instrumen (angka/koordinat berubah saat scroll). Mobile: logo + menu + toggle
suara; menu = overlay full-screen bergaya panel kontrol.

---

## 7. Template halaman case file

Urutan bagian (isi ditulis per project nanti):

1. **Brief** — masalah klien dalam bahasa klien.
2. **The instrument** — instrumen 3D besar dengan **hotspot** yang bisa di-tap; tiap hotspot
   membuka kartu penjelasan satu komponen (ini "item yang bisa diklik lalu muncul modul").
3. **How it works** — alur kerja digambar sebagai sinyal yang mengalir antar komponen.
4. **Readings** — angka bukti, dianimasikan seperti display instrumen (hanya angka yang ada di
   dossier; tidak ada angka karangan).
5. **Tools used** — tertaut balik ke Skills.
6. **Demo video** — video bisu bertakarir yang sudah ada di tiap project (jika tersedia).
7. **Next instrument** — transisi berantai ke case file berikutnya.

Transisi masuk: tap **Open case file** → kamera terbang masuk ke instrumen, instrumen menjadi
objek utama halaman case file, teks homepage memudar. Kembali = kamera mundur. Satu kanvas 3D
tetap hidup lintas halaman supaya transisi ini mulus.

---

## 8. Identitas visual (FINAL — dikunci di gate Fase 0, 2026-09-14)

> Disetujui pemilik setelah review `assets/style-lock/` (render kubah, teleskop CrossCheck,
> foto, layar HP 390×844). Token dan font di bawah dipakai apa adanya mulai Fase 1.

| Token | Nilai | Pakai untuk |
|---|---|---|
| `ink` | `#0B1020` | latar utama |
| `panel` | `#141B2E` | panel, kartu, header |
| `amber` | `#F2A541` | cahaya instrumen, CTA, sorotan |
| `signal-ok` | `#5BE49B` | status OK, angka baik |
| `signal-alarm` | `#FF5A5F` | alarm, lonjakan |
| `ivory` | `#EDE8DC` | teks utama |
| `muted` | `#A5AEC2` | bantu: teks redup, label kecil (kontras 8.5:1 di `ink`) |
| `line` | `#303A50` | bantu: garis pemisah, border |

| Peran | Font | Catatan |
|---|---|---|
| Judul | **Fraunces** | serif display, nuansa buku astronomi |
| Isi | **Inter** | sans bersih |
| Angka / readout | **JetBrains Mono** | gaya display instrumen |

Font di-self-host (TTF + lisensi OFL di `assets/style-lock/fonts/`), bukan request Google.

Foto: crop setengah badan **tanpa logo Amazon**, treatment duotone navy + garis scan halus,
muncul lewat animasi scan. Final: `assets/photo/rayina-duotone.png` (sumber bersih
`rayina-crop.png`).

Suara: ambient hum observatorium + bunyi klik instrumen halus. Default on setelah Enter,
toggle selalu terlihat, pilihan diingat per pengunjung.

---

## 9. Skills & Tools (bahan awal, tautan ke project)

Aturan: hanya tool/skill yang legit dicari perusahaan. Nama skill internal agen
(mis. `drift-alarm`, `qa-sweep`) **tidak boleh** muncul di web.

| Kelompok | Item | Dibuktikan di |
|---|---|---|
| Bahasa & runtime | Python | semua 5 |
| Test automation & QA | Playwright; cross-browser Chromium / Firefox / WebKit | CrossCheck, SurgeLine, BrandWall |
| | Visual regression / design QA (Pillow, NumPy) | BrandWall |
| | pytest, unittest | DueWatch; CrossCheck, SurgeLine, DriftWatch, BrandWall |
| Web scraping & data | httpx, selectolax, tenacity, pydantic | DriftWatch (httpx & tenacity juga CrossCheck) |
| Backend & web | FastAPI, HTMX, WordPress/PHP (target uji) | BrandWall, SurgeLine; CrossCheck |
| Data & storage | SQLite | SurgeLine, DriftWatch, DueWatch, CrossCheck |
| Workflow automation | n8n | DueWatch |
| Scheduling & ops | systemd timers, cron, Linux | DriftWatch, DueWatch |
| DevOps | Docker, Docker Compose, GNU Make, uv | BrandWall, SurgeLine, DueWatch, CrossCheck |
| Reporting | Excel reporting (openpyxl), matplotlib | BrandWall, SurgeLine, DriftWatch, CrossCheck |
| Media | ffmpeg (video demo bertakarir) | semua 5 |
| AI | Anthropic Claude API; AI-assisted engineering (Claude Code, MCP) | DriftWatch; semua 5 |
| Kerja harian | Go, MySQL/TiDB, Redis | kerja harian — **daftar persisnya dikonfirmasi pemilik di Fase 3** |

---

## 10. Aturan copy

- Orang pertama ("I build…"), percaya diri, tanpa jargon kecuali di bagian Tools.
- Pola tiap project: **masalah klien → apa yang dibangun → angka bukti**.
- Metafora observatorium hanya di label/judul (Readings, Case file, Instrument), isi tetap jelas.
- Setiap angka wajib tertelusur ke dossier sumbernya. Tidak ada klaim afiliasi (termasuk Amazon).
- Agen menulis draft; pemilik approve sebelum dianggap final.

---

## 11. Arsitektur teknis (untuk agen)

| Lapisan | Pilihan |
|---|---|
| Framework | Next.js (App Router), TypeScript, halaman di-render statis |
| 3D | React Three Fiber + drei, satu `<Canvas>` persisten di root layout |
| Scroll & animasi | Lenis (wajib) + GSAP ScrollTrigger, disinkronkan ke satu ticker |
| Aset 3D | Blender 5.2 (`~/.local/bin/blender`) via Blender MCP → `.glb` terkompresi (Draco/meshopt, tekstur KTX2) |
| Audio | Web Audio, dimulai di handler tap Enter |
| Hosting | Vercel; domain disambung sendiri oleh pemilik |

Lokasi berkas (rencana, dibuat bertahap mulai Fase 0/1):

```
Rayin Observatory/
├── PLAN.md  PROMPT.md  PROGRESS.md  CODEMAP.md
├── assets/
│   ├── blender/     sumber .blend (kubah, 5 instrumen, langit)
│   ├── renders/     render PNG untuk review pemilik
│   └── photo/       foto ter-crop + versi stilisasi
└── web/             aplikasi Next.js (belum dibuat)
    └── public/models/   ekspor .glb
```

Target performa mobile (acuan; tahap Testing mengukur lewat emulasi — CPU throttle + 4G lambat;
konfirmasi di HP Android kelas menengah fisik saat Fase 8):
- Gerbang Enter tampil < 2,5 detik.
- Total aset 3D homepage ≤ 8 MB terkompresi; satu `.glb` ≤ 1,5 MB.
- Scroll dan animasi terasa mulus (target ~60 fps, minimum stabil ≥ 45 fps); pixel ratio 3D
  dibatasi di mobile.

Catatan Blender MCP: tool hanya jalan bila **Blender GUI terbuka** (bridge `localhost:9876`,
Online Access menyala). Detail di `RULES.md` bagian Blender dan memory
`blender-mcp-jebakan-setup`.

---

## 12. Fase dan target

Mulai Fase 3, setiap fase dikerjakan dalam **dua tahap** (keputusan pemilik 2026-09-15, Q31):

| Tahap | Harness | Isi | Selesai bila |
|---|---|---|---|
| **Development** | Codex (utama) atau Claude Code | Membangun item fase. Verifikasi sendiri: lint, typecheck, build, tes fokus. | Status `ready-for-test`; tidak menanyakan gate |
| **Testing** | Claude Code atau Antigravity (context ±1M) | Mengetes otomatis **setiap** item checklist fase (Playwright; viewport HP 390×844 dulu, lalu 360×740 dan 430×932; engine/viewport lain bila fase meminta). Bug diperbaiki lalu dites ulang; bila perlu kerja besar, fase kembali ke Development dengan daftar bug di PROGRESS. Menyusun **paket bukti**. | Paket bukti terkirim; status `awaiting-gate` |

**Paket bukti** (`assets/renders/<slug-fase>/evidence/`): satu PNG per item checklist, video MP4
alur utama (H.264, 390×844 kecuali fase desktop), contact sheet JPG berlabel, dan `evidence.json`
berisi pass/fail per item. Direkam lewat URL preview publik bila tersedia, lokal bila tidak.

**Gate**: pemilik menilai dari paket bukti (video + foto) dan menyatakan lolos. Pemilik **tidak**
diminta tes manual di HP sampai Fase 8. Tanpa gate lolos, fase berikut tidak dimulai.
Gate lolos → fase `done` → **wajib commit + push** ke `origin main` (Q38).
Fase 0–2 selesai dengan aturan lama (pemilik membuka hasil sendiri).

| Fase | Nama | Target — yang terlihat di paket bukti | Hasil nyata |
|---|---|---|---|
| 0 | **Style lock** | Satu render kubah, satu render instrumen (CrossCheck), dan satu layar contoh di HP disetujui. Palet dan font final. Foto sudah ter-crop tanpa logo dan terstilisasi. | render PNG, foto olahan, token warna/font final |
| 1 | **First light** | Buka link di HP → gerbang Enter → kubah terbuka + suara → langit bergerak, scroll sangat halus. | link preview yang bisa dibuka di HP |
| 2 | **One instrument alive** | Chapter CrossCheck di homepage: kamera memutari teleskop saat scroll, muncul pitch, angka bukti, tombol Open case file. Copy CrossCheck versi pendek disetujui. | chapter pertama hidup |
| 3 | **Full observatory** | Homepage lengkap di viewport HP: 5 instrumen, Skills yang tertaut ke project, About + foto, Contact. Semua copy homepage disetujui. | homepage selesai (mobile) |
| 4 | **First case file** | Tap Open case file → kamera terbang masuk → case file CrossCheck lengkap: hotspot, Readings, video. Kembali terasa mulus. | case file pertama + transisi |
| 5 | **All case files** | Empat case file lain selesai, tombol Next instrument berantai. | 5 case file |
| 6 | **Desktop** | Semua halaman tampil megah di laptop/monitor lebar, bukan versi HP yang diperbesar. | layout desktop |
| 7 | **Showpiece polish** | Sound design, micro-interaksi, loader, dan transisi terasa premium; tetap lancar di emulasi HP menengah (CPU throttle + 4G lambat). | versi showpiece |
| 8 | **Launch ready** | Lolos QA di Chrome/Firefox/Safari + viewport HP/tablet/desktop; preview link rapi saat dibagikan ke WhatsApp/LinkedIn; siap disambung domain. Satu-satunya tes manual: pemilik mencoba di HP fisik (rasa scroll, fps, suara, 4G). | kandidat rilis |
| 9 | **Accessibility** (ditunda) | Mode gerak minimal, navigasi keyboard, screen reader. | versi aksesibel |

---

## 13. Di luar cakupan / belum dibahas

- Detail isi masing-masing project (dibahas saat fase copy).
- Domain (urusan pemilik).
- Aksesibilitas penuh (Fase 9).
- Versi bahasa Indonesia (tidak dibuat).
- Blog, testimoni, CV download (tidak dibuat saat ini).
