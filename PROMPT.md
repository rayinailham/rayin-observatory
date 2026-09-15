# PROMPT — Prompt universal sesi kerja Rayin Observatory

> Tempel isi blok di bawah ke harness mana pun (Claude Code, Codex, OpenCode, Kiro, Antigravity) untuk
> memulai atau melanjutkan sesi. Prompt ini sama untuk setiap sesi dan setiap fase —
> semua konteks yang berubah hidup di `PROGRESS.md` dan `CODEMAP.md`.

---

```text
Kamu melanjutkan project "Rayin Observatory" di:
/home/rayin/Projects/Testing/Rayin Observatory/

URUTAN BACA (wajib, jangan dilompati):
1. PROGRESS.md  — fase aktif, checklist, blocker, log sesi terakhir.
2. CODEMAP.md   — peta kode. Ini PENGGANTI membaca kode. Jangan scan/grep seluruh `web/`.
                  Buka hanya berkas yang CODEMAP tunjuk DAN yang akan kamu ubah.
3. PLAN.md      — hanya bagian yang relevan dengan fase aktif (lihat pointer di PROGRESS.md).
                  Keputusan di PLAN.md sudah dikunci pemilik; jangan diubah tanpa izin eksplisit.

TAHAP FASE (mulai Fase 3; lihat PLAN §12 dan kolom tahap di PROGRESS.md):
- Development (Codex utama / Claude Code): bangun item checklist Development. Verifikasi
  sendiri: lint, typecheck, build, tes fokus. Selesai → status `ready-for-test`.
  JANGAN menanyakan gate.
- Testing (Claude Code / Antigravity): tes otomatis SETIAP item checklist fase dengan
  Playwright (390×844 dulu, lalu 360×740 dan 430×932; engine/viewport lain bila fase
  meminta). Perbaiki bug yang ditemukan lalu tes ulang; bila butuh kerja besar, kembalikan
  fase ke Development dengan daftar bug di PROGRESS.md. Susun paket bukti di
  assets/renders/<slug-fase>/evidence/: PNG per item, video MP4 alur utama, contact sheet
  JPG berlabel, evidence.json pass/fail per item. Kirim ke pemilik → status `awaiting-gate`.
- Pemilik TIDAK diminta tes manual di HP sampai Fase 8.

CARA KERJA:
- Kerjakan HANYA fase aktif (dan tahap aktif) di PROGRESS.md. Jangan mencicil fase berikutnya.
- Sebelum mengubah apa pun, tulis rencana singkat (item checklist mana yang dikerjakan sesi ini).
- Mobile-first: setiap hasil visual diverifikasi dulu di viewport HP (mis. 390×844),
  baru desktop bila fase aktif memang meminta.
- Bahasa konten web: full English. Nama lengkap: "Rayina Ilham". Brand: "Rayin Observatory".
- Copy dan angka: ambil dari /home/rayin/Projects/Testing/portfolio/CAPABILITY_*.md.
  Tidak ada angka karangan, tidak ada klaim afiliasi. Copy baru = status DRAFT sampai
  pemilik approve.
- Aset 3D: buat di Blender lewat Blender MCP. Syarat: Blender GUI terbuka
  (`setsid -f ~/.local/bin/blender >/dev/null 2>&1 < /dev/null`), bridge localhost:9876.
  Simpan .blend ke assets/blender/, render review ke assets/renders/, ekspor .glb ke
  web/public/models/. Save .blend sebelum operasi destruktif.
- Jangan git commit/push/branch kecuali pemilik minta eksplisit.
- Jangan pernah menyentuh domain/DNS (urusan pemilik).

GATE:
- Fase selesai hanya jika pemilik sendiri menyatakan lolos setelah melihat paket bukti
  (video + foto) dari tahap Testing.
- Hanya tahap Testing yang menanyakan gate. Jangan tandai fase "done" tanpa kata lolos
  dari pemilik.

WAJIB SEBELUM MENUTUP SESI:
1. Update CODEMAP.md untuk SETIAP berkas yang kamu buat, ubah, pindah, atau hapus
   (ikuti format di CODEMAP.md). CODEMAP yang basi = bug. Jika kamu menemukan entri yang
   tidak cocok dengan kode, perbaiki sekarang.
2. Update PROGRESS.md: centang checklist, status fase, blocker, dan tambahkan satu entri
   di "Log sesi" (tanggal, harness, apa yang dikerjakan, cara verifikasi, langkah berikut).
3. Laporkan ke pemilik: apa yang berubah, bukti verifikasi, dan apa yang perlu dia lakukan
   (Development: "siap dites, buka sesi Testing"; Testing: kirim video + foto, lalu minta gate).
```

---

## Catatan untuk pemilik

- Cukup kirim prompt di atas setiap memulai sesi; tidak perlu menjelaskan ulang konteks.
- Tahap Development → buka sesi di Codex (atau Claude Code). Tahap Testing → buka sesi di
  Claude Code atau Antigravity. Prompt sama; agen membaca tahap dari PROGRESS.md.
- Untuk menilai gate, lihat video + foto bukti dari tahap Testing lalu balas "lolos" atau
  sebutkan apa yang kurang. Tes manual di HP baru diminta di Fase 8.
- Mengubah keputusan di `PLAN.md` (misal warna, urutan instrumen): katakan ke agen secara
  eksplisit, dan agen mencatat perubahannya di log keputusan PLAN.md.
