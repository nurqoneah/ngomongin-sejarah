# Setup auto-upload Instagram Reels

Sekali setup (± 20–30 menit), lalu tiap video cukup:

```bash
python tools/upload_ig.py 004 --kirim
```

> Semua langkah login & token dilakukan sendiri. Token **jangan** dikirim ke chat atau di-commit; simpan hanya di file `.env` di laptop.
> Tampilan situs Meta sering berubah — kalau nama tombol beda sedikit, cari yang paling mirip.

## 1. Akun Instagram Profesional + Halaman Facebook

1. Aplikasi IG → **Profil → ☰ → Jenis akun dan alat → Beralih ke akun profesional** → pilih **Kreator** (atau Bisnis).
2. Buat **Halaman Facebook** "Ngomongin Sejarah" (kalau belum).
3. Hubungkan: IG → **Edit profil → Halaman** → pilih Halaman Facebook tadi.
   (Atau dari Meta Business Suite → Pengaturan → Akun Instagram → Hubungkan.)

## 2. Bikin app di Meta for Developers

1. Buka **https://developers.facebook.com** → login pakai akun Facebook yang mengelola Halaman tadi → **My Apps → Create App**.
2. Nama app bebas, misalnya `Ngomongin Sejarah Uploader`.
3. Pilih use case yang berhubungan dengan **Instagram** / **Manage messaging & content on Instagram** (kalau ditanya tipe: **Business**).
4. Selesai — app ini cukup dalam **mode Development** karena cuma dipakai untuk akun sendiri (tidak perlu App Review).

## 3. Buat access token

1. Buka **https://developers.facebook.com/tools/explorer** (Graph API Explorer).
2. Kanan atas: pilih app tadi. **User or Page:** *User Token*.
3. Tambahkan izin (Permissions):
   `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management`
4. Klik **Generate Access Token** → login → **centang Halaman & akun Instagram** Ngomongin Sejarah → izinkan.

## 4. Cari IG_USER_ID

Masih di Graph API Explorer, isi kolom query dengan:

```
me/accounts?fields=name,instagram_business_account{id,username}
```

Klik **Submit**. Angka di `instagram_business_account.id` itulah **IG_USER_ID**.

## 5. Jadikan token jangka panjang (60 hari)

Token dari Explorer cuma berlaku ± 1 jam.

1. Klik ikon **ⓘ** di sebelah token → **Open in Access Token Tool**.
2. Klik **Extend Access Token** di bagian bawah → salin token baru (berlaku ± 60 hari).

## 6. Isi `.env`

Di folder project, salin `.env.example` jadi `.env`, lalu isi:

```
IG_USER_ID=1784xxxxxxxxxxxx
IG_ACCESS_TOKEN=EAAG...
```

## 7. Tes

```bash
python tools/upload_ig.py --cek
```

Harus muncul `Token OK. Akun: @ngomonginsejarah ...`. Kalau error, pesan dari Instagram ditampilkan apa adanya.

## Cara pakai

```bash
python tools/upload_ig.py 004           # pratinjau: cek video & caption yang akan dikirim
python tools/upload_ig.py 004 --kirim   # posting ke Reels (+ tampil di feed)
```

- Video diambil dari GitHub Pages (`/video/004.mp4`), jadi konten harus sudah di-push dan ter-deploy.
- Caption diambil dari bagian **Instagram Reels** di `caption.md`.
- Setelah tayang, link-nya dicatat di `konten/004-*/posting.json`, dan script menolak posting konten yang sama dua kali.
- Batas Instagram: ± 50 postingan lewat API per 24 jam (jauh di atas kebutuhan kita).

## Yang tidak bisa lewat API

- Musik dari library IG (yang ada cuma suara narasi di video).
- Label **"Dibuat dengan AI"** — tambahkan manual: buka Reels → ⋯ → Edit → Label AI.
- Gambar cover custom (cover diambil dari frame video).

## Perpanjang token

Token jangka panjang habis ± 60 hari. Kalau `--cek` bilang token kedaluwarsa, ulangi langkah 3 & 5, lalu ganti `IG_ACCESS_TOKEN` di `.env`.
