# Ngomongin Sejarah

Konten sejarah yang diceritain dengan gaya ngobrol santai, pakai narasi suara Bahasa Indonesia.

## Daftar konten

| No | Judul | Status |
|----|-------|--------|
| 001 | [Perang Badar](konten/001-perang-badar/naskah.md) | Naskah + audio ✅ |

## Struktur

```
konten/
  001-perang-badar/
    naskah.md      # info, alur cerita, ide visual, rujukan
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

## Bikin konten baru

1. Bikin folder `konten/00X-judul/`
2. Tulis `narasi.txt` — pakai kalimat pendek, titik dan koma buat jeda, `...` buat jeda dramatis
3. Salin `naskah.md` dari konten sebelumnya, sesuaikan
4. Jalankan `python tools/buat_audio.py konten/00X-judul`
