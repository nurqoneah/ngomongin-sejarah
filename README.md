# Ngomongin Sejarah

Konten sejarah yang diceritain dengan gaya ngobrol santai, pakai narasi suara Bahasa Indonesia.

## Daftar konten

| No | Judul | Status |
|----|-------|--------|
| 001 | [Perang Badar](konten/001-perang-badar/naskah.md) | Naskah + audio panjang ✅ · Shorts 9:16 ✅ |
| 002 | [Letusan Krakatau 1883](konten/002-letusan-krakatau/naskah.md) | Shorts 9:16 ✅ |
| 003 | [Kebakaran Hutan & Kabut Asap 1997](konten/003-kebakaran-hutan-1997/naskah.md) | Shorts 9:16 ✅ |
| 004 | [Gempa 1834 yang Meruntuhkan Istana Bogor](konten/004-gempa-istana-bogor-1834/naskah.md) | Shorts 9:16 ✅ |
| 005 | [Krisis Minyak 1973: Ganjil Genap Isi Bensin](konten/005-krisis-minyak-1973/naskah.md) | Shorts 9:16 ✅ |
| 006 | [Resolusi Jihad 1945: Kenapa Hari Santri 22 Oktober?](konten/006-resolusi-jihad-1945/naskah.md) | Shorts 9:16 ✅ |
| 007 | [Indonesia Pernah Keluar dari PBB (1965–1966)](konten/007-indonesia-keluar-pbb-1965/naskah.md) | Shorts 9:16 ✅ |
| 008 | [Krisis Moneter 1997–1998](konten/008-krisis-moneter-1998/naskah.md) | Shorts 9:16 ✅ |
| 009 | [Candi Borobudur yang Pernah Hilang](konten/009-candi-borobudur/naskah.md) | Shorts 9:16 ✅ |
| 010 | [Sejarah Hujan Buatan (1946 – sekarang)](konten/010-sejarah-hujan-buatan/naskah.md) | Shorts 9:16 ✅ |
| 011 | [Sejarah El Niño: dari Nelayan Peru sampai Super El Niño](konten/011-sejarah-el-nino/naskah.md) | Shorts 9:16 ✅ |
| 012 | [Sejarah Candu di Nusantara: dari VOC sampai Revolusi](konten/012-sejarah-candu-nusantara/naskah.md) | Shorts 9:16 ✅ |
| 013 | [Sumpah Pemuda 1928: Kok Bisa Lahir Bahasa Persatuan?](konten/013-sumpah-pemuda-1928/naskah.md) | Shorts 9:16 ✅ |
| 014 | [Cureng, Pesawat Merah Putih Pertama (27 Oktober 1945)](konten/014-cureng-merah-putih-1945/naskah.md) | Shorts 9:16 ✅ |
| 015 | [Asal-Usul Kata Sehari-hari: Sepatu Itu Bahasa Portugis?](konten/015-asal-usul-kata-serapan/naskah.md) | Shorts 9:16 ✅ |

## Struktur

```
konten/
  001-perang-badar/
    naskah.md      # info, alur cerita, ide visual, rujukan
    caption.md     # caption siap posting: YouTube, TikTok, IG, FB, Threads/X
    narasi.txt     # teks yang dibacakan (yang diubah jadi suara)
    audio/         # hasil MP3 + subtitle SRT
tools/
  buat_audio.py    # narasi.txt -> MP3 + SRT
```

## Cara bikin audio

```bash
pip install -r requirements.txt
python tools/buat_audio.py konten/001-perang-badar
```

Opsi:
- `--suara ardi` (laki-laki, default) atau `--suara gadis` (perempuan)
- `--kecepatan -8%` — makin minus makin pelan
- `--nada -2Hz` — makin minus makin berat

## Video Shorts 9:16 (TikTok, Reels FB, YouTube Shorts)

Gaya animasi peta: peta bertekstur, rute bergerak, pasukan berupa titik, kartu nama tokoh (tanpa wajah), caption kata-per-kata.

```bash
pip install -r requirements.txt
python tools/buat_shorts.py konten/001-perang-badar
```

Hasil di `konten/001-perang-badar/shorts/`: `perang-badar-shorts.mp4` (1080x1920, 30fps) + `.srt`.

- Narasi & visual per adegan ada di `shorts/adegan.py` — durasi tiap adegan otomatis ikut panjang suaranya.
- `--kecepatan +20%` → lebih cepat/pendek (default di `adegan.py`: `+15%`, ± 86 detik)
- `--musik file.mp3 --volume-musik 0.12` → tambah musik latar
- `--pratinjau 5 20 40` → cuma simpan frame PNG di detik tsb (cepat, buat ngecek layout)

## Studio Posting (web app)

👉 **https://nurqoneah.github.io/ngomongin-sejarah/**

App buat posting dari HP: daftar video, putar & simpan video, tombol salin caption tiap platform, tanda "sudah diposting". Bisa dipasang di layar utama HP ("Tambahkan ke Layar Utama").

Setiap push ke `main` yang mengubah `konten/`, `app/`, atau `branding/` otomatis membangun ulang dan men-deploy app ini (GitHub Actions: `.github/workflows/pages.yml`).

```bash
python tools/buat_app.py
```

Membaca semua `konten/*/caption.md` + video Shorts, lalu menulis `app/dist/` (tidak di-commit; video dikompres < 14 MB untuk versi claude.ai). Versi GitHub Pages: `python tools/buat_app.py --target pages --keluar _site` (video kualitas asli). Tampilan ada di `app/template.html`.

## Upload otomatis ke Instagram Reels

```bash
python tools/upload_ig.py 004           # pratinjau
python tools/upload_ig.py 004 --kirim   # posting ke Reels
```

Pakai Instagram Graph API resmi; video diambil dari GitHub Pages, caption dari `caption.md`. Setup sekali: [docs/SETUP-INSTAGRAM.md](docs/SETUP-INSTAGRAM.md) (token disimpan di `.env`, tidak di-commit).

Antrean harian (1 konten per hari, nomor terkecil yang belum diposting; taruh file `TAHAN` di folder konten untuk menahan):

```bash
python tools/posting_otomatis.py                 # lihat antrean
python tools/posting_otomatis.py --kirim         # posting 1 konten berikutnya
python tools/posting_otomatis.py --sudah 001 002 # tandai yang sudah diposting manual
```

Panduan hook & sudut topik: [docs/PANDUAN-HOOK.md](docs/PANDUAN-HOOK.md).

## Bikin konten baru

1. Bikin folder `konten/00X-judul/`
2. Tulis `narasi.txt` — pakai kalimat pendek, titik dan koma buat jeda, `...` buat jeda dramatis
3. Salin `naskah.md` dari konten sebelumnya, sesuaikan
4. Jalankan `python tools/buat_audio.py konten/00X-judul`
