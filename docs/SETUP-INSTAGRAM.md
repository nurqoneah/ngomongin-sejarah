# Setup auto-upload Instagram Reels & Facebook Reels

Sekali setup, lalu:

```bash
python tools/upload_fb.py 023 --kirim   # Facebook Reels sebagai DRAFT (tidak tayang)
python tools/upload_ig.py 023 --kirim   # Instagram Reels (langsung tayang — API IG tidak punya draft)
```

> Semua login dilakukan sendiri di browser. Token & App secret **jangan** dikirim ke chat atau di-commit; semuanya cuma ada di file `.env` di laptop.

## Yang sudah disiapkan (November 2026)

- Akun Facebook pribadi + Halaman **Ngomongin Sejarahh**, terhubung ke IG **@ngomonginnsejarah** (akun Profesional).
- App Meta **Ngomongin Sejarah Uploader** (ID `1775932743518649`, mode Development, business portfolio "Ngomongin Sejarah").
  - Use case: *Manage messaging & content on Instagram* + *Manage everything on your Page*.
  - Izin aktif (Ready for testing): `instagram_basic`, `instagram_content_publish`, `pages_show_list`,
    `pages_read_engagement`, `pages_manage_posts`, `business_management`.
  - Mode Development cukup karena cuma dipakai untuk akun sendiri — tidak perlu App Review.

## Login / ambil token

1. `.env` → isi `META_APP_ID` dan `META_APP_SECRET`
   (developers.facebook.com → app → **App settings → Basic → App secret → Show**).
2. Jalankan:

   ```bash
   python tools/login_meta.py
   ```

   Browser membuka halaman izin Facebook → **Lanjutkan** → centang Halaman & akun IG → Simpan.
   Script menukar login jadi token jangka panjang dan mengisi `IG_ACCESS_TOKEN`, `FB_PAGE_ID`,
   `FB_PAGE_TOKEN`, `IG_USER_ID` di `.env` (token tidak pernah dicetak).
3. Tes (tidak memposting apa pun):

   ```bash
   python tools/upload_ig.py --cek
   python tools/upload_fb.py --cek
   ```

> Graph API Explorer tidak dipakai: di app model baru tombol *Generate Access Token* sering mati.
> Izin harus ditambahkan dulu di **Use cases → Customize → Permissions and features → Add**.

## Cara pakai

```bash
python tools/upload_fb.py 023                 # pratinjau
python tools/upload_fb.py 023 --kirim         # draft Reels di Halaman
python tools/upload_fb.py --antrean --kirim   # konten terbaru yang belum ada di Facebook

python tools/upload_ig.py 023                 # pratinjau
python tools/upload_ig.py 023 --kirim         # LANGSUNG TAYANG di Reels
```

- Video diambil dari GitHub Pages (`/video/NNN.mp4`), jadi konten harus sudah di-push dan ter-deploy.
- Caption dari bagian **Facebook Reels** / **Instagram Reels** di `caption.md`.
- Hasilnya dicatat di `konten/NNN-*/posting.json`; script menolak upload konten yang sama dua kali.
- Draft Facebook: **Meta Business Suite → Konten → Draf**, cek lalu publikasikan manual.

## Yang tidak bisa lewat API

- Draft Instagram (API IG hanya bisa langsung publish).
- Musik dari library IG/FB.
- Label **"Dibuat dengan AI"** — tambahkan manual saat publish.
- Gambar cover custom (cover diambil dari frame video).

## Token kedaluwarsa

`FB_PAGE_TOKEN` dibuat dari token jangka panjang, jadi tidak kedaluwarsa (kecuali password FB diganti
atau izin app dicabut). Kalau `--cek` gagal, cukup jalankan lagi `python tools/login_meta.py`.
