# Rayin Observatory — Rencana Induk

> Web portofolio showpiece milik **Rayina Ilham** ("Rayin" = nama panggilan).
> Dokumen ini adalah hasil sesi grilling 2026-09-14. Semua keputusan di bawah **sudah dikunci**
> oleh pemilik; jangan diubah tanpa persetujuan eksplisit. Status kerja harian ada di
> `PROGRESS.md`, peta kode ada di `CODEMAP.md`, cara memulai sesi ada di `PROMPT.md`.
> Revisi 2026-09-16 (Q41): personalisasi lima project, mobile dahulu, desktop tetap utama.

---

## 1. Ringkasan satu paragraf

Rayin Observatory adalah web portofolio berbahasa Inggris untuk **calon klien freelance**
(automation & QA). Bentuknya halaman scroll 2D yang super smooth (Lenis) dengan aset 3D buatan
sendiri dan animasi berat. Temanya **observatorium malam**: Rayina adalah operator yang
"mengawasi sistem klien", dan kelima project-nya tampil sebagai **lima instrumen** di dalam
observatorium. Tiap instrumen punya halaman **case file** sendiri; perpindahan ke sana memakai
transisi kamera yang terbang masuk ke instrumen, jadi pengunjung tidak pernah merasa keluar dari
observatorium. Setiap project mendapat cerita, komposisi visual, animasi penjelas, dan transisi
sesuai pekerjaannya. **Mobile-first adalah urutan pengembangan; desktop tetap panggung utama**.
Fase 0–7 menjadi fondasi yang sudah lolos; fase personalisasi 7A–7F mendahului launch Fase 8.

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
| Q5 | Device | **Mobile-first**, lalu desktop sebagai panggung utama; diperjelas Q41: urutan ini berlaku di setiap fase personalisasi |
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
| Q21 | Struktur case study | Lihat §7; sejak Q41, bagian wajib adalah kontrak isi, bukan template visual seragam |
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
| Q40 | Tes Fase 8 di URL Vercel | (2026-09-16) Tahap Testing Fase 8 dijalankan terhadap **URL produksi Vercel**, bukan preview lokal: Development deploy dulu, lalu QA lintas browser + paket bukti + tes HP fisik pemilik semuanya memakai link Vercel. Vercel CLI 54.9.1 sudah terpasang di device (dicatat di `RULES.md`); `vercel login` dilakukan pemilik sendiri. Domain/DNS tetap di luar cakupan agent |
| Q38 | Commit + push akhir fase | (2026-09-16) Setiap akhir fase (gate lolos → `done`) **wajib** git commit + push ke `origin main` (akun personal). Di luar akhir fase tetap hanya atas permintaan pemilik. Aturan di `PROMPT.md` |
| Q41 | Personalisasi lima project | (2026-09-16) Pemilik meminta plan/progress mengarahkan sesi berikut ke penjelasan personal tiap project berdasarkan **`portfolio/` di root Rayin Observatory**. Cerita, visual, animasi, dan transisi boleh berbeda sesuai jenis project; jangan terasa template. Setiap fase membangun dan memverifikasi mobile dulu, kemudian memoles desktop sebagai tampilan utama. Tambahkan 7A–7E per project + 7F integrasi sebelum Fase 8; gate 0–7 tetap sebagai riwayat. Rincian §5, §7, §8, §12 |
| Q42 | Efisiensi tes | (2026-09-16, sesi Testing 7A) Pemilik tidak mau Testing selama sesi ini (regresi jalan dua kali setelah bug performa baru ketahuan di Testing). Berlaku mulai fase berikut: (1) Development wajib cek fps `perf_quick.py` sebelum `ready-for-test`; (2) regresi lewat `run_regressions.py` — suite yang sudah lolos pada sidik jari sumber yang sama dilewati, setelah fix hanya suite yang belum hijau di kode baru; (3) paket bukti Testing memanggil ulang tes dev fase aktif di dalam paketnya, bukan menjalankan suite dev terpisah lalu mengulang; (4) suite fase lama cukup 390×844 (`--phone-only`), tiga HP hanya untuk fase aktif. Detail §12.3 |
| Q43 | Gate 7A CrossCheck | (2026-09-16) Gate 7A lolos dari paket bukti Testing 16/17 ("lulus semua aman"); copy baru 7A di-approve, label DRAFT CrossCheck dilepas. Dua temuan diterima apa adanya: scrub inspection field 52–54 fps dengan 11–13% frame lambat di 4× CPU (gagal p95 ketat), crop "Expected" CC-001 sulit dibaca di HP. Fase aktif berikut 7B |
| Q44 | Gate 7B SurgeLine | (2026-09-17) Gate 7B lolos dari paket bukti Testing 18/18 ("lulus semua"); copy baru 7B di-approve, label DRAFT SurgeLine dilepas. Temuan diterima: Cut boleh ditekan sebelum B sampai Form (B beku di tengah lane, Resume normal); refresh `/work/surgeline` mengulang ilustrasi dari awal. Fase aktif berikut 7C |
| Q45 | Gate 7C DriftWatch | (2026-09-17) Gate 7C lolos dari paket bukti Testing 21/21 ("saya approve semua untuk 7C ini"); copy baru 7C di-approve termasuk ilustrasi bernomor Day 1–3, label DRAFT DriftWatch dilepas. Temuan diterima: di HP sebab/aksi/kode alarm perlu scroll sedikit sesudah Compare; fix Testing jendela clip trace menjadi motion approved. 7D berjalan paralel di salinan terpisah (Codex), integrasi setelah 7C stabil |
| Q46 | Gate 7D DueWatch | (2026-09-18) Gate 7D lolos dari paket bukti Testing 22/22 ("semuanya approved"); copy baru 7D di-approve (chapter + strip pointer, brief, 3 hotspot, ruang agenda/triage/pengingat, bukti rekaman + 7 temuan audit, teaser BrandWall), label DRAFT DueWatch dilepas; strip chapter berlabel "Illustration". Temuan diterima: cincin → rail tipis (garis rambut) dan tick dial tanpa label. Fase aktif berikut 7E |
| Q47 | Testing ringan | (2026-09-18, pasca-gate 7D) Pemilik: Testing jangan banyak dan lama, cukup fitur yang baru dibuat. Berlaku mulai 7E Testing (7F dan 8 tetap putaran penuh): (1) cakupan = item checklist fase aktif saja; fitur fase lama tidak dites ulang; (2) regresi = suite fase aktif + `cases` + `mobile` 390×844 lewat runner, suite lain hanya bila berkas bersama (shell, `globals.css`, scene, `cases.ts`) diubah fase itu; runner 16 suite penuh hanya di 7F/8; (3) viewport Testing 390×844 + 1440×900; 360/430/768/1920 cukup dari tes Development pada sidik jari sama; (4) paket bukti: 1 video HP + 1 video desktop (masing-masing ≤ ±90 dtk, alur utama fitur baru), PNG per item, satu contact sheet, `evidence.json`; tanpa reel slow-motion kecuali ada temuan motion; (5) fps: pakai hasil `perf_quick.py` Development bila sidik jari sumber sama, tidak diukur ulang; (6) edge (reduced motion, model gagal, Back saat transisi, resize) satu kali di 390×844. Target Testing ±20 menit waktu mesin. Detail §12.3 |
| Q48 | Gate 7E BrandWall | (2026-09-24) Gate 7E lolos dari paket bukti Testing ringan 17/17 ("untuk saat ini saya sudah approve"); copy baru 7E di-approve, label DRAFT BrandWall dilepas, strip chapter berlabel "Illustration". Pemilik mengizinkan perbaikan yang dinilai perlu: label mono 8 px di studio/chapter → 10 px; pasangan Overflow di HP memakai crop lebih tinggi (`phoneView` 706×599, tetangga tetap terlihat, skala 0.458 → 0.481). Header fixed yang menumpuk konten saat scroll tetap perilaku lama. Fase aktif berikut 7F |
| Q49 | Scroll native + tirai | (2026-09-24, pasca-gate 7E) Pemilik: "kalau mau scroll dia malah gerakin animasinya dulu … scroll ya scroll aja, animasi terpisah, user interaksi sendiri pas pencet modelnya" dan "animasi transisi tirai aja, setiap tirai beda-beda". Mengganti sebagian Q2/Q27 dan §5/§6: (1) wheel native (Lenis `smoothWheel: false`; Lenis tetap untuk lompatan menu + kunci scroll saat terbang); (2) tidak ada chapter/hero/field yang di-pin: hero, lima chapter, dan inspection field CrossCheck masing-masing satu layar dan ikut scroll; (3) putaran instrumen = interaksi pengunjung (geser samping = putar manual, tap = putar penuh / balik), bukan scroll; strip ilustrasi chapter ikut putaran itu; scan CrossCheck main sendiri sekali saat terlihat + klik step + Replay; (4) transisi masuk/keluar/Next = tirai per case (CrossCheck panggung terbelah, SurgeLine 8 bilah, DriftWatch gulungan kertas grafik, DueWatch 6 lajur, BrandWall 5 lipatan spektrum), menggantikan iris/pulsa/pita/cincin/prisma. Tes regresi lama yang mengasumsikan scroll-orbit/iris/flight perlu diperbarui di 7F |
| Q50 | Gate 7F integrasi | (2026-09-24) Gate 7F lolos dari paket bukti Testing putaran penuh 17/17 ("saya accept semua itu lulus"). Copy DRAFT Q49 di-approve: hint chapter "Drag or tap the instrument to turn it" (empat chapter; BrandWall tetap hint observer). Temuan diterima apa adanya: kunci scroll dilepas ±50–320 ms sebelum tirai terbuka penuh; header transparan menumpuk judul chapter/case saat scroll (perilaku lama). Fase 8 Development aktif. |

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

Sumber materi yang dipakai sesi berikut: **`portfolio/CAPABILITY_<NAMA>.md` di root project ini**
(`/home/rayin/Projects/Testing/Rayin Observatory/portfolio/`). Dossier adalah snapshot bukti,
bukan data live. Baca pitch, masalah klien, alur, angka, dan keterbatasan project aktif sebelum
menulis copy atau merancang adegan. Jangan hanya mengganti nama/angka pada case lain.

| Urutan | Project | Fungsi singkat | Instrumen | Gerakan idle khas |
|---|---|---|---|---|
| 1 | **CrossCheck** | Automated web QA lintas browser | **Teleskop 3 lensa** (3 engine browser, satu target) | lensa bergantian menyala, tabung sedikit mengayun |
| 2 | **SurgeLine** | Bulk form automation tahan crash | **Antena array** (banyak piringan mengirim sinyal bersamaan) | piringan berputar bergelombang, pulsa sinyal |
| 3 | **DriftWatch** | Scraping + alarm saat sumber berubah | **Seismograf** (jarum menggambar garis, ada lonjakan) | jarum bergetar, kertas bergulir, sesekali lonjakan merah |
| 4 | **DueWatch** | Expiry tracking + auto follow-up | **Orrery / jam astronomi** | cincin berotasi dengan kecepatan berbeda |
| 5 | **BrandWall** | Design QA / visual brand testing | **Spektrograf prisma** (cahaya dipecah jadi pita warna) | prisma berputar pelan, pita warna bergeser |

Aset tambahan: **kubah observatorium** (hero + gerbang), **langit + planet ambient** (latar).

### 5.1 CrossCheck — ruang inspeksi, dari sinyal ke masalah yang bisa ditindak

- **Sumber:** `portfolio/CAPABILITY_CROSSCHECK.md` §1–4, §7, §9.
- **Cerita:** aplikasi tampak baik di satu layar → periksa browser, ukuran layar, dan peran
  pengguna → kelompokkan sinyal → buka satu temuan beserta bukti dan langkah reproduksi.
  Fokus klien: tahu apa yang rusak, siapa terdampak, dan apa yang harus diperbaiki dulu.
- **Visual:** teleskop tiga lensa, garis bidik presisi, matriks cakupan, lembar temuan terkurasi;
  navy/ivory dengan hijau sebagai hasil pemeriksaan dan merah hanya pada masalah.
- **Animasi penjelas:** lensa memindai tiga jalur browser; sel matriks terisi lalu sinyal
  mengelompok menjadi temuan. Sorot satu bukti saat kartu temuan dipilih; hindari efek alarm acak.
- **Transisi:** homepage → mendekati lensa → bidang inspeksi membuka case file; kembali
  menarik kamera ke teleskop dan posisi chapter semula. Scroll balik membalik urutan scan.
- **Mobile → desktop:** matriks bertahap dan bukti dalam satu kolom yang bisa di-tap; kemudian
  desktop menjadi meja inspeksi lebar dengan matriks dan detail bukti berdampingan.
- **Bukti & batas:** 1,080 kombinasi, 881 sinyal → 18 isu, 12/12 bug tertanam tertangkap.
  Jelaskan target demo milik sendiri; bukan hasil aplikasi klien. Jangan menyiratkan semua
  pengurangan sinyal adalah false positive; dossier mencatat 562 false positive terpisah.

### 5.2 SurgeLine — ruang pengiriman, pekerjaan tetap lanjut setelah putus

- **Sumber:** `portfolio/CAPABILITY_SURGELINE.md` §1–4, §7, §9.
- **Cerita:** spreadsheet besar → antrean → pekerja paralel → pengiriman terputus → lanjut
  dari posisi tersimpan → hasil terkonfirmasi atau gagal dengan alasan. Fokus: tidak hilang,
  tidak terkirim dua kali, dan estimasi waktu yang jujur.
- **Visual:** antena array, jalur pengiriman, blok record dan tanda konfirmasi; susunan memanjang
  dengan ritme tegas, amber sebagai aktivitas dan hijau khusus hasil terkonfirmasi.
- **Animasi penjelas:** record mengalir ke pekerja, satu jalur berhenti saat demonstrasi crash,
  pekerjaan tertunda kembali mengalir saat resume; record sukses tidak mengulang pengiriman.
  Pisahkan hasil confirmed, rejected, dan dead-letter secara terbaca.
- **Transisi:** kamera mengikuti pulsa menuju antena → jalur antrean menjadi pengantar case;
  saat kembali, aliran menyusut ke antena, tanpa animasi reset seolah data hilang.
- **Mobile → desktop:** alur vertikal bertahap dengan kontrol crash/resume yang bisa di-tap;
  desktop memperlihatkan beberapa jalur pekerja dan ringkasan hasil serentak.
- **Bukti & batas:** 50,000 baris input → 49,950 unik; 48,273 terkonfirmasi, 844 ditolak,
  833 dead-letter; dua kali kill, nol duplikat. Selesai diproses bukan berarti semua sukses.
  Target lokal sintetis; 6 juta record adalah estimasi, bukan volume yang pernah dijalankan.

### 5.3 DriftWatch — ruang pemantauan, perubahan tidak lewat diam-diam

- **Sumber:** `portfolio/CAPABILITY_DRIFTWATCH.md` §1–4, §7, §9.
- **Cerita:** snapshot kemarin → pengambilan hari ini → bedakan data baru/berubah/hilang →
  bedakan perubahan sumber dari pipeline rusak → alarm yang bisa ditelusuri.
  Fokus: tahu kapan data sudah tidak dapat dipercaya.
- **Visual:** seismograf, pita waktu, dua snapshot, anotasi perubahan; ruang lebih tenang,
  trace hijau dan lonjakan merah bermakna dengan label sebab.
- **Animasi penjelas:** trace berjalan stabil, perubahan memicu lonjakan lokal, detail diff
  terbuka; contoh hasil kosong masuk ke alarm, tidak berubah menjadi indikator sukses.
- **Transisi:** ikuti jarum ke pita rekaman; pita melebar menjadi timeline case file.
  Kembali menggulung ke titik asal; beda snapshot tetap mudah dipahami saat scroll balik.
- **Mobile → desktop:** pasangan snapshot ditumpuk dengan penanda tanggal dan tombol banding;
  desktop menampilkan timeline lebar serta snapshot/diff sejajar.
- **Bukti & batas:** 1,323 record/hari dari empat sumber; 11/11 kegagalan tertanam tertangkap,
  nol false positive pada pengujian itu; tiga hari unattended yang dibuktikan.
  Jangan mengubah bukti tiga hari menjadi klaim monitoring berbulan-bulan atau status live.

### 5.4 DueWatch — ruang kendali waktu, tahu kapan menindak dan kapan berhenti

- **Sumber:** `portfolio/CAPABILITY_DUEWATCH.md` §1–4, §7–8, §11.
- **Cerita:** kontrak dihitung ulang → tenggat diprioritaskan → pesan dipilah → tindak lanjut
  aman atau eskalasi manusia. Jelaskan dua modul yang berbeda: tracker kontrak dan triage pesan.
- **Visual:** orrery/jam astronomi, kalender berbentuk lintasan, kartu status dan jalur handoff;
  ivory/amber dominan, tempo tenang, status memakai label selain warna.
- **Animasi penjelas:** penunjuk waktu melewati batas status kontrak, kartu pindah kategori;
  pesan sensitif berhenti di manusia, replay tidak menambah pengingat ganda. Adegan berlabel
  simulasi; tidak menyerupai inbox atau pengiriman pesan live.
- **Transisi:** kamera mengikuti cincin waktu → lintasan membuka agenda case file;
  kembali ke orrery dengan ritme halus, tanpa hitung mundur yang memberi kesan darurat palsu.
- **Mobile → desktop:** agenda vertikal dan pilihan modul lewat tap; desktop memakai agenda
  kontrak serta meja triage berdampingan, tetap jelas bahwa keduanya punya alur berbeda.
- **Bukti & batas:** 200 kontrak/run, 18 pesan uji, 6/6 pesan sensitif dieskalasi, nol panggilan
  API eksternal. Pertahankan catatan tanggal simulasi video Q35 dan temuan audit mandiri
  (tujuh cacat; A9/A10 terbuka pada dossier); jangan menjanjikan sistem bebas cacat/siap produksi.

### 5.5 BrandWall — studio visual, tunjukkan tepat di mana brand rusak

- **Sumber:** `portfolio/CAPABILITY_BRANDWALL.md` §1–4, §6 K2–K8, §7, §9.
- **Cerita:** aset ekstrem → coba pada surface dan tema → lihat crop/kontras/rasio/overflow →
  temukan titik patah → bandingkan hasil aturan CSS. Fokus pada bukti visual dan kelas kerusakan.
- **Visual:** spektrograf prisma, bidang spesimen terang/gelap, contact sheet dan overlay ukur;
  komposisi seperti studio editorial. Spektrum warna menjadi aksen identitas khusus project ini.
- **Animasi penjelas:** berkas cahaya memisah menjadi surface/tema, specimen berganti ukuran,
  garis ukur menandai titik rusak, reveal sebelum/sesudah menunjukkan efek aturan.
  Animasi observer/celah ganda yang sudah ada boleh tetap sebagai aksen; cerita QA harus utama.
- **Transisi:** kamera mengikuti berkas melalui prisma → bidang cahaya membuka galeri;
  kembali merapat ke prisma. Reveal gambar menjaga pasangan pembanding tetap sejajar.
- **Mobile → desktop:** satu pasangan gambar terbaca, tombol sebelum/sesudah serta slider
  opsional; desktop memperluas menjadi galeri dan perbandingan besar dengan anotasi.
- **Bukti & batas:** 30 aset sintetis × 5 surface × 2 tema = 300 screenshot/run;
  11 titik patah dan tujuh aturan CSS. Bukan logo klien asli; aset 404/kosong tidak diklaim
  selesai lewat CSS. A8 pemahaman oleh pengguna non-teknis masih parsial pada dossier.

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
   **Open case file**. Sesudah personalisasi, komposisi dan ritme setiap chapter mengikuti
   §5.1–§5.5: scan, aliran antrean, trace perubahan, agenda waktu, lalu studio spesimen.
   Gaya pinned dan CTA tetap dikenali; jangan mengulang koreografi yang sama lima kali.
4. **Skills** — dikelompokkan (lihat §9). Tap skill → sorot project yang membuktikannya.
5. **About** — foto ter-crop dengan reveal "scan", paragraf singkat orang pertama.
6. **Contact** — CTA utama besar, lalu tautan sekunder.

Header tetap: logo "Rayin Observatory" + Work / About / Contact + toggle suara. Readout progres
scroll bergaya instrumen (angka/koordinat berubah saat scroll). Mobile: logo + menu + toggle
suara; menu = overlay full-screen bergaya panel kontrol.

---

## 7. Kontrak isi halaman case file — penyajian personal

Bagian wajib di bawah menjaga kelengkapan informasi. Urutan setelah Brief, proporsi,
komposisi, bentuk diagram, cara membuka bukti, dan koreografi **boleh berbeda per project**
mengikuti §5.1–§5.5. Struktur lama menjadi baseline, bukan template visual yang wajib disalin.

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

**Kontrak personalisasi setiap project:** pitch homepage, pembuka case, masalah klien,
alur penjelas, hotspot, Readings, demo, batas bukti, dan pengantar Next harus sesuai dossier
project itu. Setiap hotspot menjawab fungsi komponen bagi klien. Readings menyebut konteks
ukur; animasi ilustratif diberi label dan tidak menyamar sebagai hasil run langsung.
Minimal ada satu komposisi bukti dan satu interaksi penjelas yang khas tiap project.

**Next instrument:** tutup adegan asal, pindah fokus, buka adegan tujuan sesuai karakternya.
Uji seluruh rantai CrossCheck → SurgeLine → DriftWatch → DueWatch → BrandWall → CrossCheck,
direct URL, refresh, Back/Forward, dan kembali ke homepage. Copy baru tetap DRAFT sampai
approve; persetujuan copy lama tidak otomatis meliputi narasi baru.

---

## 8. Identitas visual (FINAL — dikunci di gate Fase 0, 2026-09-14)

> Disetujui pemilik setelah review `assets/style-lock/` (render kubah, teleskop CrossCheck,
> foto, layar HP 390×844). Token dan font di bawah tetap fondasi bersama. Q41 mengizinkan
> variasi komposisi, pencahayaan, aksen lokal, dan motion per project sesuai §5.

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

### 8.1 Variasi yang tetap terasa satu observatorium

Header, navigasi, font, CTA utama, dan makna warna status konsisten. Setiap ruang boleh punya
proporsi bidang, kepadatan informasi, aksen, material/cahaya, framing kamera, dan ritme berbeda.
CrossCheck presisi; SurgeLine bertenaga dan teratur; DriftWatch tenang lalu tajam saat perubahan;
DueWatch terukur; BrandWall kaya pembanding visual. Mengganti warna dan judul saja belum cukup.

### 8.2 Standar animasi, transisi, dan dua ukuran layar

- **Urutan wajib tiap fase:** rancang cerita mobile → implementasi dan verifikasi mobile →
  komposisi/polish desktop → regresi mobile. Desktop tetap presentasi utama: ruang, hierarki,
  detail cahaya, kamera, dan bukti dimanfaatkan sengaja, bukan sekadar memperbesar versi HP.
- Uji mobile 390×844 → 360×740 → 430×932; tablet 768×1024; desktop 1440×900 dan 1920×1080.
  Q47: keenamnya diverifikasi di Development; Testing 7E cukup 390×844 + 1440×900; putaran penuh di 7F/8.
  Konten utama dan bukti setara; mobile boleh menyederhanakan partikel, lapisan, dan orbit.
  Fungsi penjelas tidak boleh hanya tersedia lewat hover atau drag presisi.
- Setiap animasi punya tujuan: menjelaskan proses, memberi feedback, atau menjaga orientasi.
  Tetapkan trigger, objek yang bergerak, kondisi akhir, easing/durasi, serta perilaku balik
  dan interupsi. Idle tetap sekunder terhadap teks; teks tidak ikut bergerak terus saat dibaca.
- Feedback UI ditargetkan 100–250 ms; adegan penjelas boleh lebih lama dengan kontrol pengguna.
  Kamera dan reveal sinkron; hindari lompatan pose, kedipan, teks bertumpuk, CTA tertahan,
  atau animasi antre saat tap cepat. Nilai durasi final dipilih lewat rekaman, bukan angka saja.
- Model terlambat/gagal: tampilkan poster/fallback berlabel; hotspot tidak menunjuk ruang
  kosong. Penerimaan jeda lama Q39 adalah riwayat, bukan target kualitas personalisasi baru.
- Pakai stack yang ada (§11); utamakan transform/opacity untuk DOM, ukur beban shader/blur/
  partikel sebelum menambah efek. Budget mobile §11 tetap berlaku; catat hasil aktual dan
  selisih target, jangan menyamakan lulus build dengan animasi mulus.
- Testing menilai video kecepatan normal + potongan lambat untuk masuk/keluar, scroll balik,
  perpindahan chapter, tap cepat, dan perubahan viewport. Foto saja tidak membuktikan motion.
  Audit aksesibilitas penuh tetap Fase 9; fallback statis harus menjaga cerita tetap terbaca.

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
- Tiap project mengikuti konflik, proses, dan bukti khas §5; hindari pembuka, urutan reveal,
  dan paragraf manfaat yang bisa ditukar antar project hanya dengan mengganti nama.

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

### 12.1 Aturan sesi berikut dan urutan revisi

**Q41 berlaku saat prompt universal lama dipakai:** baca fase aktif di PROGRESS, lalu §5
khusus project itu, §7, §8.1–§8.2, dan §12 ini. Gunakan dossier di `portfolio/` dalam root
Rayin Observatory; rujukan folder sibling `/home/rayin/Projects/Testing/portfolio/` pada
prompt lama sudah digantikan oleh Q41. Tidak perlu mengganti prompt untuk melanjutkan.

Fase aktif berikut **7A**, lalu **7B → 7C → 7D → 7E → 7F → 8 → 9**. Fase 0–7 tetap `done`
sebagai fondasi historis. Tambahan ini bukan klaim bahwa revisi personalisasi sudah selesai.
Tiap fase 7A–7E mengerjakan chapter homepage **dan** case file satu project, mobile dahulu,
desktop dalam fase yang sama. Jangan menunda desktop semuanya ke akhir atau menyelesaikan
lima project sekaligus dalam satu template. Fase 7F menyatukan perjalanan dan regresi kelimanya.
Fase 8 menunggu gate 7F. Penambahan fase dalam revisi dokumen Q41 belum merupakan implementasi.

Awal Development: baca dossier → tulis brief personal singkat (klien/masalah/cerita/bukti/
visual/motion/mobile/desktop) → bangun checklist project aktif. Akhir sesi: catat kemajuan
mobile dan desktop secara terpisah, sumber copy, serta item yang belum lolos.

### 12.2 Development, Testing, dan gate

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

Untuk fase personalisasi, paket bukti memuat walkthrough **mobile dan desktop**, foto per
item, serta pass/fail terpisah untuk cerita, visual, animasi, transisi, mobile, desktop,
dan sumber bukti. Tiap fase 7A–7E harus menunjukkan alasan desainnya cocok dengan project itu;
7F/8/9 melaporkan kelima project satu per satu, bukan hanya satu hasil umum.

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
| 7A | **CrossCheck — inspection room** | Scan tiga browser → matriks cakupan → temuan berbukti; entry lewat lensa; mobile dulu, lalu meja inspeksi desktop. | chapter + case CrossCheck personal, bukti dua device |
| 7B | **SurgeLine — dispatch room** | Antrean → paralel → crash/resume → konfirmasi tanpa duplikat; pulsa antena; mobile dulu, lalu jalur desktop. | chapter + case SurgeLine personal, bukti dua device |
| 7C | **DriftWatch — monitoring room** | Snapshot → diff → alarm bermakna; trace seismograf; mobile dulu, lalu timeline desktop. | chapter + case DriftWatch personal, bukti dua device |
| 7D | **DueWatch — time control room** | Agenda kontrak + triage pesan dengan eskalasi; cincin waktu; mobile dulu, lalu dua modul desktop. | chapter + case DueWatch personal, bukti dua device |
| 7E | **BrandWall — visual studio** | Specimen → kerusakan → batas ukur → sebelum/sesudah; prisma; mobile dulu, lalu galeri desktop. | chapter + case BrandWall personal, bukti dua device |
| 7F | **Five rooms, one observatory** | Kelima cerita tetap beda; seluruh entry/return/Next menyambung, navigasi konsisten, motion dan performa diverifikasi mobile lalu desktop. | perjalanan lengkap + bukti per project |
| 8 | **Launch ready** | Lolos QA di Chrome/Firefox/Safari + viewport HP/tablet/desktop; preview link rapi saat dibagikan ke WhatsApp/LinkedIn; siap disambung domain. Satu-satunya tes manual: pemilik mencoba di HP fisik (rasa scroll, fps, suara, 4G). | kandidat rilis |
| 9 | **Accessibility** (ditunda) | Mode gerak minimal, navigasi keyboard, screen reader. | versi aksesibel |

### 12.3 Efisiensi tes (Q42, berlaku mulai Fase 7B)

Tujuan: Testing tidak mengulang pekerjaan yang sudah terbukti pada kode yang sama, dan regresi performa
ketahuan di Development. Alat ada di `web/scripts/` (perintah lengkap CODEMAP §2).

1. **Development — gerbang fps sebelum `ready-for-test`.** Jalankan
   `perf_quick.py --slug <project>` (390×844 DPR 2, suara nyala, CPU 4×, swipe chapter → terbang → scroll case → Return).
   Lolos bila tiap segmen ≥ 45 fps dan ≤ 10% frame lebih lambat dari 45 fps. Bila turun, ukur pembanding
   `--baseline <url build HEAD>` untuk atribusi sebelum menyerahkan. Tetap alarm regresi, bukan klaim fps HP fisik.
2. **Regresi lewat runner.** `run_regressions.py` menjalankan suite berurutan (satu GPU) dan mencatat
   `assets/renders/regression-ledger.json` per suite dengan sidik jari sumber `web/app|components|lib|public` + lockfile.
   Suite yang sudah `passed` pada sidik jari yang sama **dilewati** (Development → Testing tanpa ulang).
   Setelah fix, runner hanya menjalankan suite yang belum hijau di kode baru; satu putaran penuh cukup di akhir.
   Runner menolak jalan bila build lebih tua dari sumber. `--force` hanya bila ada alasan (rig berubah, hasil diragukan).
3. **Paket bukti = tes fase.** Skrip bukti Testing mengimpor fungsi tes Development fase aktif dan menyimpan
   hasil + foto ke paket (contoh `crosscheck_room_evidence.py` → `verify_crosscheck_room`). Jangan menjalankan
   suite dev fase aktif terpisah lalu mengulangnya lagi di paket.
4. **Cakupan viewport.** Fase aktif: 390×844 → 360×740 → 430×932 → 768 → 1440/1920 (tetap §8.2).
   Suite fase lama: `--phone-only mobile,case,cases,showpiece` (390×844 saja, `OBSERVATORY_PHONES`);
   `desktop-a/-b` tetap. Hasil phone-only tidak menggantikan putaran penuh sebelum Fase 8.
5. **Urutan sesi Testing:** runner (skip yang sudah hijau) → skrip bukti → cek visual → fix kecil →
   runner lagi (hanya suite terdampak) → skrip bukti. Bug besar → kembali ke Development, jangan diperbaiki di Testing.
6. **Testing ringan (Q47, mulai 7E Testing; 7F dan 8 tetap penuh):** uji hanya fitur baru fase aktif.
   Regresi = suite fase aktif + `cases` + `mobile` (`--phone-only`); suite lain hanya bila fase menyentuh berkas bersama
   (shell, `globals.css`, scene, `cases.ts`). Viewport Testing 390×844 + 1440×900 (sisanya dari tes Development pada sidik jari
   sama). Paket: 1 video HP + 1 video desktop ≤ ±90 dtk, PNG per item, satu contact sheet, `evidence.json`; slow-motion hanya
   bila ada temuan motion. fps memakai hasil `perf_quick.py` Development bila sidik jari sama. Edge sekali di 390×844.
   Target ±20 menit waktu mesin.

---

## 13. Di luar cakupan / belum dibahas

- Copy final dan koreografi detail tiap project diselesaikan di 7A–7E dari brief §5; copy baru
  memerlukan approval. Batas bukti dalam dossier tetap ditampilkan.
- Domain (urusan pemilik).
- Aksesibilitas penuh (Fase 9).
- Versi bahasa Indonesia (tidak dibuat).
- Blog, testimoni, CV download (tidak dibuat saat ini).
