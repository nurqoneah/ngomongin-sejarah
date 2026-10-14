"""Bikin aset profil pakai maskot anak petualang (gaya kartun).

    python tools/buat_branding.py
Hasil di folder branding/: foto-profil.png, banner-youtube.png, sampul-facebook.png, maskot.png
"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import shorts_engine as se  # noqa: E402
from logo_kartun import GARIS, KREM, KUNING, MERAH, MERAH_TUA  # noqa: E402
from logo_maskot import maskot_petualang  # noqa: E402

OUT = Path(__file__).parent.parent / "branding"
SS = 2
LANGIT, LANGIT_SINAR = (120, 200, 230), (150, 215, 240)


def latar_sinar(w, h, cx, cy):
    img = Image.new("RGBA", (w * SS, h * SS), LANGIT + (255,))
    d = ImageDraw.Draw(img)
    r = max(w, h) * 1.5 * SS
    for i in range(36):
        a0 = i * 2 * math.pi / 36
        a1 = a0 + math.pi / 36
        d.polygon([(cx * SS, cy * SS), (cx * SS + r * math.cos(a0), cy * SS + r * math.sin(a0)),
                   (cx * SS + r * math.cos(a1), cy * SS + r * math.sin(a1))], fill=LANGIT_SINAR)
    return img, d


def pita(d, cx, cy, judul, label, uk=1.0):
    """Pita merah + label kuning, ukuran mengikuti lebar teks."""
    s = SS * uk
    f = se.font("caption", int(112 * s))
    lebar = f.getlength(judul) / 2 + 60 * s
    x, y = cx * SS, cy * SS
    for arah in (-1, 1):
        x0, x1 = x + arah * (lebar - 40 * s), x + arah * (lebar + 70 * s)
        d.polygon([(x0, y - 40 * s), (x1, y - 40 * s), (x1 - arah * 40 * s, y + 30 * s), (x1, y + 100 * s), (x0, y + 100 * s)],
                  fill=MERAH_TUA, outline=GARIS, width=int(8 * s))
    d.rounded_rectangle((x - lebar, y - 70 * s, x + lebar, y + 70 * s), int(12 * s), fill=MERAH, outline=GARIS, width=int(9 * s))
    d.text((x + 6 * s, y + 10 * s), judul, font=f, fill=GARIS, anchor="mm", stroke_width=int(6 * s), stroke_fill=GARIS)
    d.text((x, y + 4 * s), judul, font=f, fill=KREM, anchor="mm", stroke_width=int(6 * s), stroke_fill=GARIS)
    fl = se.font("caption", int(48 * s))
    lw = fl.getlength(label) / 2 + 34 * s
    d.rounded_rectangle((x - lw, y - 128 * s, x + lw, y - 62 * s), int(31 * s), fill=KUNING, outline=GARIS, width=int(7 * s))
    d.text((x, y - 95 * s), label, font=fl, fill=GARIS, anchor="mm")


def banner(w, h, tinggi_aman):
    """Maskot di kiri, judul di kanan, semua di dalam area aman tengah."""
    cx, cy = w / 2, h / 2
    img, d = latar_sinar(w, h, cx - tinggi_aman * 0.9, cy)
    m = maskot_petualang(penuh=False).crop((140, 90, 940, 870))  # karakter saja
    tm = int(tinggi_aman * 1.05 * SS)
    m = m.resize((int(m.width * tm / m.height), tm), Image.LANCZOS)
    img.alpha_composite(m, (int((cx - tinggi_aman * 0.95) * SS - m.width / 2), int(cy * SS - m.height / 2)))
    uk = tinggi_aman / 423 * 0.9
    tx = cx + tinggi_aman * 0.55
    pita(d, tx, cy - 10 * uk, "SEJARAH", "NGOMONGIN", uk)
    d.text((tx * SS, (cy + 140 * uk) * SS), "Sejarah diceritain santai, kayak lagi ngobrol",
           font=se.font("caption", int(40 * uk * SS)), fill=(255, 255, 255), anchor="mm",
           stroke_width=int(6 * uk * SS), stroke_fill=GARIS)
    return img.resize((w, h), Image.LANCZOS).convert("RGB")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    maskot_petualang().save(OUT / "foto-profil.png")
    maskot_petualang(penuh=False).save(OUT / "maskot.png")
    banner(2560, 1440, 423).save(OUT / "banner-youtube.png")   # area aman YouTube 1546x423
    banner(1640, 924, 380).save(OUT / "sampul-facebook.png")
    print("Selesai:", *sorted(p.name for p in OUT.glob("*.png")))
