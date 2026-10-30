"""Antrean posting harian: posting 1 konten berikutnya ke Instagram Reels.

Urutan: nomor konten terkecil yang belum diposting (lihat posting.json).
Konten dilewati kalau di foldernya ada file bernama TAHAN (buat nahan video
yang belum dicek / mau direvisi). Hapus file TAHAN untuk melepasnya.

    python tools/posting_otomatis.py            # lihat antrean + pratinjau berikutnya
    python tools/posting_otomatis.py --kirim    # posting 1 konten berikutnya
    python tools/posting_otomatis.py --sudah 001 002 005   # tandai yang sudah diposting manual
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # emoji di caption aman di terminal Windows
sys.path.insert(0, str(Path(__file__).parent))
from upload_ig import ROOT, baca_env, cari_konten, posting, sudah_diposting  # noqa: E402


def antrean():
    siap, ditahan = [], []
    for folder in sorted((ROOT / "konten").iterdir()):
        if not (folder / "caption.md").exists() or not list((folder / "shorts").glob("*.mp4")):
            continue
        if sudah_diposting(folder):
            continue
        (ditahan if (folder / "TAHAN").exists() else siap).append(folder)
    return siap, ditahan


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kirim", action="store_true", help="benar-benar posting 1 konten")
    ap.add_argument("--sudah", nargs="+", metavar="NNN", help="tandai konten yang sudah diposting manual di IG")
    a = ap.parse_args()

    if a.sudah:
        for no in a.sudah:
            folder = cari_konten(no)[0]
            log = folder / "posting.json"
            riwayat = json.loads(log.read_text(encoding="utf-8")) if log.exists() else {}
            riwayat.setdefault("instagram", {"manual": True, "dicatat": datetime.now().isoformat(timespec="seconds")})
            log.write_text(json.dumps(riwayat, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Ditandai sudah diposting: {folder.name}")
        return

    siap, ditahan = antrean()
    print(f"Antrean siap posting: {len(siap)} | ditahan: {len(ditahan)}")
    for f in siap[:5]:
        print("  -", f.name)
    for f in ditahan:
        print("  [TAHAN]", f.name)
    if not siap:
        print("Tidak ada yang bisa diposting hari ini.")
        return

    env = baca_env()
    no = siap[0].name.split("-")[0]
    link = posting(env, no, kirim=a.kirim)
    if link:
        print(f"Sisa antrean: {len(siap) - 1} konten")


if __name__ == "__main__":
    main()
