"""Bikin aset profil: foto profil (logo) + banner YouTube/Facebook, gaya peta yang sama dengan Shorts.

    python tools/buat_branding.py
Hasil di folder branding/.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import shorts_engine as se  # noqa: E402

OUT = Path(__file__).parent.parent / "branding"
MERAH = (200, 52, 44)


def kertas(w, h, seed):
    img = se.latar_tekstur(w, h, seed, bukit=[(w * 0.1, h * 0.2, w * 0.3, h * 0.3), (w * 0.9, h * 0.85, w * 0.35, h * 0.3)])
    return img.convert("RGBA")


def gelapkan_tepi(img, kuat=170):
    import numpy as np
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype("float32")
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a = (np.clip((r - 0.6) / 0.6, 0, 1) ** 1.5 * kuat).astype("uint8")
    lap = np.zeros((h, w, 4), "uint8")
    lap[..., 3] = a
    img.alpha_composite(Image.fromarray(lap, "RGBA"))


def logo(ukuran=1080):
    s = ukuran / 1080
    img = kertas(ukuran, ukuran, 21)
    gelapkan_tepi(img)
    d = ImageDraw.Draw(img, "RGBA")
    c = ukuran / 2
    # cincin kompas
    d.ellipse((c - 430 * s, c - 430 * s, c + 430 * s, c + 430 * s), outline=(60, 40, 20, 255), width=int(10 * s))
    d.ellipse((c - 400 * s, c - 400 * s, c + 400 * s, c + 400 * s), outline=(60, 40, 20, 140), width=int(3 * s))
    for i in range(16):
        import math
        a = i * math.pi / 8
        r0, r1 = (380 if i % 2 else 360) * s, 400 * s
        d.line((c + r0 * math.cos(a), c + r0 * math.sin(a), c + r1 * math.cos(a), c + r1 * math.sin(a)),
               fill=(60, 40, 20, 255), width=int(6 * s))
    # gelembung obrolan (= "ngomongin")
    d.rounded_rectangle((c - 330 * s, c - 250 * s, c + 330 * s, c + 150 * s), int(90 * s), fill=MERAH + (255,),
                        outline=(40, 20, 10, 255), width=int(10 * s))
    d.polygon([(c - 120 * s, c + 140 * s), (c - 200 * s, c + 280 * s), (c - 20 * s, c + 145 * s)],
              fill=MERAH + (255,), outline=(40, 20, 10, 255))
    d.line((c - 118 * s, c + 145 * s, c - 25 * s, c + 145 * s), fill=MERAH + (255,), width=int(12 * s))
    d.text((c, c - 120 * s), "NGOMONGIN", font=se.font("caption", int(80 * s)), fill=(255, 255, 255), anchor="mm")
    d.text((c, c + 10 * s), "SEJARAH", font=se.font("judul", int(106 * s)), fill=(255, 225, 150), anchor="mm",
           stroke_width=int(4 * s), stroke_fill=(90, 20, 15))
    d.text((c + 150 * s, c + 260 * s), "cerita masa lalu", font=se.font("tangan", int(44 * s)), fill=(50, 30, 15), anchor="mm")
    return img.convert("RGB")


def banner(w=2560, h=1440):
    img = kertas(w, h, 33)
    gelapkan_tepi(img, 120)
    d = ImageDraw.Draw(img, "RGBA")
    # area aman YouTube: 1546x423 di tengah
    cx, cy = w / 2, h / 2
    k = w / 2560
    f = se.font("caption", 104)
    tw = f.getlength("NGOMONGIN SEJARAH") / 2 + 60
    d.rounded_rectangle((cx - tw, cy - 120, cx + tw, cy + 30), 40, fill=MERAH + (245,), outline=(40, 20, 10, 255), width=8)
    d.text((cx, cy - 45), "NGOMONGIN SEJARAH", font=f, fill=(255, 255, 255), anchor="mm")
    d.text((cx, cy + 95), "Sejarah diceritain santai, kayak lagi ngobrol", font=se.font("tangan", 56), fill=(45, 30, 15),
           anchor="mm", stroke_width=4, stroke_fill=(240, 225, 190))
    # ornamen: rute putus-putus + unta
    se.garis_putus(d, [(cx - 1100 * k, cy + 300), (cx - 800 * k, cy + 230), (cx - 600 * k, cy + 290)], 1.0, (90, 55, 25), tebal=8, panah=False)
    for i in range(4):
        se.ikon_unta(d, cx - 1000 * k + i * 70, cy + 250 + (i % 2) * 6, 1.8, (75, 45, 20))
    se.ikon_masjid(d, cx + 820 * k - 40, cy + 260, 2.2)
    se.ikon_kabah(d, cx + 1000 * k - 40, cy + 270, 2.0)
    return img.convert("RGB")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    logo().save(OUT / "foto-profil.png")
    banner().save(OUT / "banner-youtube.png")
    banner(1640, 924).save(OUT / "sampul-facebook.png")
    print("Selesai:", *sorted(p.name for p in OUT.glob("*.png")))
