"""Ubah naskah narasi jadi audio MP3 + subtitle SRT pakai suara Indonesia (Edge TTS).

Contoh:
    python tools/buat_audio.py konten/001-perang-badar
    python tools/buat_audio.py konten/001-perang-badar --suara id-ID-GadisNeural --kecepatan -5%
"""

import argparse
import asyncio
from pathlib import Path

import edge_tts

SUARA = {
    "ardi": "id-ID-ArdiNeural",   # laki-laki
    "gadis": "id-ID-GadisNeural",  # perempuan
}


async def buat(folder: Path, suara: str, kecepatan: str, nada: str) -> None:
    teks = (folder / "narasi.txt").read_text(encoding="utf-8").strip()
    keluaran = folder / "audio"
    keluaran.mkdir(exist_ok=True)
    nama = folder.name
    mp3 = keluaran / f"{nama}.mp3"
    srt = keluaran / f"{nama}.srt"

    komunikasi = edge_tts.Communicate(teks, suara, rate=kecepatan, pitch=nada)
    sub = edge_tts.SubMaker()
    with open(mp3, "wb") as f:
        async for potongan in komunikasi.stream():
            if potongan["type"] == "audio":
                f.write(potongan["data"])
            elif potongan["type"] in ("WordBoundary", "SentenceBoundary"):
                sub.feed(potongan)
    srt.write_text(sub.get_srt(), encoding="utf-8")
    print(f"Selesai: {mp3}\n         {srt}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("folder", type=Path, help="folder konten yang berisi narasi.txt")
    p.add_argument("--suara", default="ardi", help="ardi, gadis, atau nama suara Edge TTS lengkap")
    p.add_argument("--kecepatan", default="-8%", help="misal -10%%, +0%%, +5%%")
    p.add_argument("--nada", default="-2Hz", help="misal -5Hz, +0Hz")
    a = p.parse_args()
    asyncio.run(buat(a.folder, SUARA.get(a.suara, a.suara), a.kecepatan, a.nada))


if __name__ == "__main__":
    main()
