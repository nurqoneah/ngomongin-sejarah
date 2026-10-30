"""Bikin file bukti untuk formulir audit YouTube API -> docs/audit-youtube/

  arsitektur.png, alur-pengguna.png      (diagram, dibuat dengan Pillow)
  screenshot-beranda.png, screenshot-privasi.png, screenshot-syarat.png
  kebijakan-privasi.pdf, syarat-layanan.pdf   (dari halaman live, via Edge headless)

    python tools/buat_bukti_audit.py
"""

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "audit-youtube"
SITUS = "https://nurqoneah.github.io/ngomongin-sejarah/"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

TINTA, GARIS, LATAR = (33, 37, 41), (90, 100, 110), (255, 255, 255)
WARNA = {"lokal": (225, 240, 250), "google": (232, 245, 233), "yt": (253, 236, 234), "web": (245, 240, 230)}


def font(uk, tebal=False):
    return ImageFont.truetype("C:/Windows/Fonts/" + ("segoeuib.ttf" if tebal else "segoeui.ttf"), uk)


def kotak(d, box, judul, baris, warna):
    d.rounded_rectangle(box, 16, fill=warna, outline=GARIS, width=3)
    x0, y0, x1, _ = box
    d.text(((x0 + x1) / 2, y0 + 30), judul, font=font(26, True), fill=TINTA, anchor="mm")
    for i, b in enumerate(baris):
        d.text(((x0 + x1) / 2, y0 + 72 + i * 32), b, font=font(20), fill=TINTA, anchor="mm")


def panah(d, a, b, label=""):
    d.line([a, b], fill=GARIS, width=4)
    import math
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for s in (2.6, -2.6):
        d.line([b, (b[0] + 18 * math.cos(ang + s), b[1] + 18 * math.sin(ang + s))], fill=GARIS, width=4)
    if label:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        w = font(18).getlength(label) + 16
        d.rectangle((mx - w / 2, my - 16, mx + w / 2, my + 16), fill=LATAR)
        d.text((mx, my), label, font=font(18), fill=TINTA, anchor="mm")


def arsitektur():
    img = Image.new("RGB", (1600, 900), LATAR)
    d = ImageDraw.Draw(img)
    d.text((800, 50), "Ngomongin Sejarah Uploader — Architecture", font=font(36, True), fill=TINTA, anchor="mm")
    d.text((800, 92), "Internal tool, single user (channel owner). No server, no database.", font=font(22), fill=GARIS, anchor="mm")
    kotak(d, (60, 160, 560, 520), "Channel owner's laptop", [
        "Python scripts (local only)", "buat_shorts.py → renders own MP4", "upload_yt.py → uploads own MP4",
        "OAuth token stored locally", "(token_youtube.json, never shared)"], WARNA["lokal"])
    kotak(d, (700, 160, 1100, 400), "Google OAuth 2.0", [
        "Owner signs in & consents", "Scopes: youtube.upload,", "youtube.readonly"], WARNA["google"])
    kotak(d, (1180, 160, 1560, 520), "YouTube Data API v3", [
        "videos.insert (privacy: private)", "channels.list (mine=true)", "videos.list (own video status)"], WARNA["yt"])
    kotak(d, (1180, 620, 1560, 840), "YouTube channel", ["\"Ngomongin Sejarah\"", "(owner's own channel)"], WARNA["yt"])
    kotak(d, (60, 620, 560, 840), "GitHub Pages website", ["Privacy Policy & Terms", "Own video previews + captions", "No YouTube API calls"], WARNA["web"])
    panah(d, (560, 280), (700, 280), "1. consent")
    panah(d, (1100, 280), (1180, 280), "2. token")
    panah(d, (560, 450), (1180, 450), "3. upload own video (private)")
    panah(d, (1370, 520), (1370, 620), "4. draft in Studio")
    img.save(OUT / "arsitektur.png")


def alur():
    img = Image.new("RGB", (1600, 1000), LATAR)
    d = ImageDraw.Draw(img)
    d.text((800, 50), "Ngomongin Sejarah Uploader — User Flow", font=font(36, True), fill=TINTA, anchor="mm")
    langkah = [
        ("1. First sign-in (once)", ["Owner runs: upload_yt.py --cek", "Google consent screen opens", "Owner approves upload + read scopes"], "google"),
        ("2. Token saved locally", ["Refresh token stored on laptop", "Never sent anywhere else"], "lokal"),
        ("3. Produce own video", ["Channel owner creates", "history education Short (MP4)", "+ title, description, tags"], "lokal"),
        ("4. Upload as PRIVATE", ["upload_yt.py NNN --kirim", "videos.insert, privacyStatus=private", "madeForKids=false, synthetic=true"], "yt"),
        ("5. Owner reviews", ["Checks the draft in", "YouTube Studio"], "yt"),
        ("6. Owner publishes", ["Owner sets Public / schedule", "manually (or publishAt)"], "yt"),
    ]
    for i, (j, b, w) in enumerate(langkah):
        kol, bar = i % 3, i // 3
        x0, y0 = 70 + kol * 520, 140 + bar * 420
        kotak(d, (x0, y0, x0 + 440, y0 + 260), j, b, WARNA[w])
        if kol < 2:
            panah(d, (x0 + 440, y0 + 130), (x0 + 520, y0 + 130))
    panah(d, (1330, 400), (1330, 470))
    d.line([(1330, 470), (290, 470)], fill=GARIS, width=4)
    panah(d, (290, 470), (290, 560))
    d.text((800, 950), "Access can be revoked at any time at myaccount.google.com/permissions; deleting the local token removes all stored data.",
           font=font(20), fill=GARIS, anchor="mm")
    img.save(OUT / "alur-pengguna.png")


def edge(*args):
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", *args],
                   check=True, capture_output=True, timeout=120)


def halaman():
    for nama, url, tinggi in (("beranda", SITUS, 1600), ("privasi", SITUS + "privasi.html", 2600),
                              ("syarat", SITUS + "syarat.html", 1800)):
        edge(f"--screenshot={OUT / f'screenshot-{nama}.png'}", f"--window-size=1000,{tinggi}", url)
    edge(f"--print-to-pdf={OUT / 'kebijakan-privasi.pdf'}", "--no-pdf-header-footer", SITUS + "privasi.html")
    edge(f"--print-to-pdf={OUT / 'syarat-layanan.pdf'}", "--no-pdf-header-footer", SITUS + "syarat.html")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    arsitektur()
    alur()
    halaman()
    for p in sorted(OUT.iterdir()):
        print(f"  {p.name:28} {p.stat().st_size / 1024:7.0f} KB")
