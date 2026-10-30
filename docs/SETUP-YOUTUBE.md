# Setup auto-upload YouTube (draft / private)

Sekali setup (± 20 menit), lalu:

```bash
python tools/upload_yt.py 015 --kirim          # upload sebagai PRIVATE (draft)
python tools/upload_yt.py --antrean --kirim    # upload konten berikutnya yang belum ada di YouTube
```

> Login dan izin dilakukan sendiri. File `client_secret_youtube.json` dan `token_youtube.json` **jangan** dikirim ke chat atau di-commit (sudah ada di `.gitignore`).
> Tampilan Google Cloud sering berubah — kalau nama menu beda sedikit, cari yang paling mirip.

## ⚠️ Batasan penting dari Google

Video yang di-upload lewat API dari project yang **belum diaudit** otomatis **terkunci private**: tidak bisa dijadikan publik atau dijadwalkan. Jadi ada dua tahap:

| Tahap | Hasil |
|---|---|
| **Sebelum audit** | Upload otomatis jalan, video masuk YouTube Studio sebagai **private** — berguna untuk ngecek hasil, tapi untuk tayang publik masih harus upload manual. |
| **Setelah lolos audit** | Upload otomatis bisa **dijadwalkan tayang** (`--jadwal "2026-11-02 18:00"`) atau kamu publish sendiri dari Studio. |

Audit gratis, lewat formulir (langkah 7). Prosesnya biasanya beberapa hari sampai beberapa minggu.

## 1. Bikin project Google Cloud

1. Buka **https://console.cloud.google.com** → login pakai **akun Google pemilik channel** YouTube.
2. Pojok kiri atas, pilih project → **New Project** → nama `Ngomongin Sejarah` → **Create**.

## 2. Aktifkan YouTube Data API v3

**APIs & Services → Library** → cari **YouTube Data API v3** → **Enable**.

## 3. Layar izin OAuth (Google Auth Platform)

1. **APIs & Services → OAuth consent screen** (atau **Google Auth Platform**) → **Get started**.
2. App name: `Ngomongin Sejarah Uploader`, support email: email kamu.
3. Audience: **External**.
4. Contact email: email kamu → setujui kebijakan → **Create**.
5. Menu **Audience** → klik **Publish app** → status jadi **In production**.
   *Penting:* kalau dibiarkan "Testing", izin login kedaluwarsa tiap 7 hari dan upload otomatis berhenti.

## 4. Bikin OAuth client

1. Menu **Clients** (atau **Credentials → Create credentials → OAuth client ID**).
2. Application type: **Desktop app**, nama bebas → **Create**.
3. Klik **Download JSON** → ganti nama file jadi **`client_secret_youtube.json`** → taruh di folder project `D:\Work\Ngomongin Sejarah\`.

## 5. Login pertama

```bash
python tools/upload_yt.py --cek
```

Browser terbuka:
1. Pilih akun Google pemilik channel (kalau channel-nya *brand account*, pilih channel **Ngomongin Sejarah**).
2. Muncul *"Google hasn't verified this app"* → **Advanced** → **Go to Ngomongin Sejarah Uploader (unsafe)**. Ini normal karena app-nya milik kamu sendiri.
3. Centang semua izin → **Continue**.

Terminal harus menampilkan `OK. Channel: Ngomongin Sejarah ...`.

## 6. Tes upload

```bash
python tools/upload_yt.py 001            # cek judul/deskripsi/tag dulu
python tools/upload_yt.py 001 --kirim    # upload sebagai private
```

Link YouTube Studio ditampilkan di akhir, dan tercatat di `konten/001-*/posting.json` (script menolak upload konten yang sama dua kali).

Pengaturan yang dikirim otomatis: kategori **Pendidikan**, **bukan untuk anak-anak**, **konten sintetis/AI: Ya**, bahasa Indonesia.

## 7. Ajukan audit (supaya bisa publik / terjadwal)

Formulir: **https://support.google.com/youtube/contact/yt_api_form** → pilih *audit / quota extension*.

Yang biasanya diminta & draf jawabannya:

- **Project number:** ada di Google Cloud → Dashboard project.
- **Kegunaan aplikasi:**
  > Internal tool for a single YouTube channel ("Ngomongin Sejarah", Indonesian history education). It uploads our own short videos (produced by us) with titles, descriptions and tags we wrote, using videos.insert. Only the channel owner uses it; no other users, no data collection, no third-party content.
- **API yang dipakai:** `videos.insert`, `channels.list` (mine=true).
- **Jumlah pengguna:** 1 (pemilik channel).
- **Kebijakan privasi / situs:** bisa diminta — bilang ke Claude untuk bikinkan halaman kebijakan privasi di GitHub Pages.
- Kadang diminta **video demo** cara kerja tool (rekam layar terminal saat upload).

## Kuota

Kuota gratis 10.000 unit per hari; satu upload ≈ 1.600 unit → maksimal ± 6 video per hari. Lebih dari cukup.
