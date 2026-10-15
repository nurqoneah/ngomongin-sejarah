"""Bangun web app "Studio Posting" dari semua folder konten.

Membaca konten/*/caption.md + video Shorts, lalu menulis app/dist/:
  index.html        (data caption tertanam)
  video/<no>.mp4    (dikompres < 14 MB supaya bisa di-publish)
  thumb/<no>.jpg    (cover dari frame video)
  maskot.png

    python tools/buat_app.py
"""

import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "app" / "dist"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
BATAS_MB = 14

BATAS_KARAKTER = {  # (kata kunci platform, label) -> batas
    ("YouTube", "Judul"): 100,
    ("YouTube", "Deskripsi"): 5000,
    ("YouTube", "Tag"): 500,
    ("TikTok", "Caption"): 4000,
    ("Instagram", "Caption"): 2200,
    ("Threads", "Teks"): 280,
}


def parse_caption(md: str) -> dict:
    data = {"judul": "", "cover": "", "detik_cover": 1.5, "platform": []}
    sekarang, label, kode = None, None, None
    for baris in md.splitlines():
        if kode is not None:
            if baris.strip() == "```":
                sekarang["isian"].append({"label": label or "Teks", "teks": "\n".join(kode).strip()})
                kode, label = None, None
            else:
                kode.append(baris)
            continue
        if baris.startswith("# "):
            data["judul"] = re.sub(r"^Caption\s*[—-]\s*\d+\s*", "", baris[2:]).strip()
        elif baris.startswith("Teks cover"):
            m = re.search(r"\*\*(.+?)\*\*", baris)
            data["cover"] = m.group(1) if m else ""
            m = re.search(r"detik ke-(\d+)", baris)
            if m:
                data["detik_cover"] = float(m.group(1)) + 0.5
        elif baris.startswith("## "):
            sekarang = {"nama": baris[3:].strip(), "isian": [], "catatan": []}
            data["platform"].append(sekarang)
        elif sekarang is not None and baris.strip() == "```":
            kode = []
        elif sekarang is not None and baris.startswith("**"):
            m = re.match(r"\*\*(.+?)\*\*:?\s*(.*)", baris)
            if not m:
                continue
            kunci, sisa = m.group(1).rstrip(":"), m.group(2).strip()
            if sisa and not sisa.startswith("("):
                sekarang["catatan"].append({"label": kunci, "teks": sisa.replace("`", "").replace("**", "")})
            else:
                label = kunci
    for p in data["platform"]:
        for isi in p["isian"]:
            for (kata, lbl), batas in BATAS_KARAKTER.items():
                if kata in p["nama"] and lbl == isi["label"]:
                    isi["batas"] = batas
    return data


def durasi(mp4: Path) -> float:
    out = subprocess.run([FFMPEG, "-i", str(mp4)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0


def kompres(src: Path, dst: Path):
    if dst.exists() and dst.stat().st_mtime > src.stat().st_mtime:
        return
    for crf in (26, 29, 32):
        subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(src), "-c:v", "libx264", "-preset", "slow",
                        "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                        "-movflags", "+faststart", str(dst)], check=True)
        if dst.stat().st_size < BATAS_MB * 1024 * 1024:
            return
    raise SystemExit(f"{dst.name} masih di atas {BATAS_MB} MB")


def cover(src: Path, detik: float, dst: Path):
    subprocess.run([FFMPEG, "-y", "-v", "error", "-ss", str(detik), "-i", str(src), "-frames:v", "1",
                    "-vf", "scale=540:-2", "-q:v", "4", str(dst)], check=True)


def main():
    (DIST / "video").mkdir(parents=True, exist_ok=True)
    (DIST / "thumb").mkdir(parents=True, exist_ok=True)
    semua = []
    for folder in sorted((ROOT / "konten").iterdir()):
        cap = folder / "caption.md"
        videos = sorted((folder / "shorts").glob("*.mp4"))
        if not cap.exists() or not videos:
            continue
        no = folder.name.split("-")[0]
        data = parse_caption(cap.read_text(encoding="utf-8"))
        print(f"  {no} {data['judul']}")
        kompres(videos[0], DIST / "video" / f"{no}.mp4")
        cover(videos[0], data["detik_cover"], DIST / "thumb" / f"{no}.jpg")
        data.update(no=no, slug=folder.name, video=f"video/{no}.mp4", thumb=f"thumb/{no}.jpg",
                    nama_file=videos[0].name, durasi=round(durasi(videos[0])))
        semua.append(data)

    m = Image.open(ROOT / "branding" / "maskot.png").convert("RGBA").crop((140, 90, 940, 870))
    m.resize((240, int(240 * m.height / m.width)), Image.LANCZOS).save(DIST / "maskot.png", optimize=True)

    tpl = (ROOT / "app" / "template.html").read_text(encoding="utf-8")
    html = tpl.replace("/*DATA*/[]", json.dumps(semua, ensure_ascii=False))
    (DIST / "index.html").write_text(html, encoding="utf-8")
    ukuran = sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file()) / 1e6
    print(f"Selesai: {DIST} ({len(semua)} konten, {ukuran:.1f} MB)")


if __name__ == "__main__":
    main()
