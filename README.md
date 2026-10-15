# Ngomongin Sejarah

Konten sejarah yang diceritain dengan gaya ngobrol santai, pakai narasi suara Bahasa Indonesia.

## Daftar konten

| No | Judul | Status |
|----|-------|--------|
| 001 | [Perang Badar](konten/001-perang-badar/naskah.md) | Naskah + audio panjang ✅ · Shorts 9:16 ✅ |
| 002 | [Letusan Krakatau 1883](konten/002-letusan-krakatau/naskah.md) | Shorts 9:16 ✅ |
| 003 | [Kebakaran Hutan & Kabut Asap 1997](konten/003-kebakaran-hutan-1997/naskah.md) | Shorts 9:16 ✅ |

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

## Bikin konten baru

1. Bikin folder `konten/00X-judul/`
2. Tulis `narasi.txt` — pakai kalimat pendek, titik dan koma buat jeda, `...` buat jeda dramatis
3. Salin `naskah.md` dari konten sebelumnya, sesuaikan
4. Jalankan `python tools/buat_audio.py konten/00X-judul`
