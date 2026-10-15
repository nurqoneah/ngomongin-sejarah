"""Bangun web app "Studio Posting" dari semua folder konten.

Membaca konten/*/caption.md + video Shorts, lalu menulis app/dist/:
  index.html        (data caption tertanam)
  video/<no>.mp4    (dikompres < 14 MB supaya bisa di-publish)
  thumb/<no>.jpg    (cover dari frame video)
  maskot.png

    python tools/buat_app.py                                  # untuk Artifact claude.ai -> app/dist
    python tools/buat_app.py --target pages --keluar _site    # untuk GitHub Pages (dipakai GitHub Actions)
"""

import argparse
import json
import re
import shutil
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


# Artifact dibungkus skeleton otomatis; GitHub Pages butuh dokumen HTML lengkap + manifest PWA.
KEPALA_PAGES = """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#7cc8e6">
<meta name="description" content="Video Shorts Ngomongin Sejarah siap upload + caption tiap platform.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="ikon-192.png">
<link rel="apple-touch-icon" href="ikon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<style>html,body{margin:0}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""

MANIFEST = {
    "name": "Studio Posting Ngomongin Sejarah",
    "short_name": "Ngomongin Sejarah",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#eef6f9",
    "theme_color": "#7cc8e6",
    "icons": [{"src": "ikon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "ikon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["artifact", "pages"], default="artifact")
    ap.add_argument("--keluar", type=Path, default=None, help="folder hasil (default app/dist)")
    a = ap.parse_args()
    global DIST
    DIST = (a.keluar or DIST).resolve()
    pages = a.target == "pages"

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
        if pages:  # GitHub Pages tidak membatasi 15 MB per file -> pakai kualitas asli
            shutil.copy2(videos[0], DIST / "video" / f"{no}.mp4")
        else:
            kompres(videos[0], DIST / "video" / f"{no}.mp4")
        cover(videos[0], data["detik_cover"], DIST / "thumb" / f"{no}.jpg")
        data.update(no=no, slug=folder.name, video=f"video/{no}.mp4", thumb=f"thumb/{no}.jpg",
                    nama_file=videos[0].name, durasi=round(durasi(videos[0])))
        semua.append(data)

    m = Image.open(ROOT / "branding" / "maskot.png").convert("RGBA").crop((140, 90, 940, 870))
    m.resize((240, int(240 * m.height / m.width)), Image.LANCZOS).save(DIST / "maskot.png", optimize=True)

    tpl = (ROOT / "app" / "template.html").read_text(encoding="utf-8")
    html = tpl.replace("/*DATA*/[]", json.dumps(semua, ensure_ascii=False))
    if pages:
        html = KEPALA_PAGES + html + "\n</body>\n</html>\n"
        (DIST / "manifest.webmanifest").write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")
        profil = Image.open(ROOT / "branding" / "foto-profil.png").convert("RGB")
        for uk in (192, 512):
            profil.resize((uk, uk), Image.LANCZOS).save(DIST / f"ikon-{uk}.png", optimize=True)
        (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "index.html").write_text(html, encoding="utf-8")
    ukuran = sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file()) / 1e6
    print(f"Selesai: {DIST} ({len(semua)} konten, {ukuran:.1f} MB)")


if __name__ == "__main__":
    main()
