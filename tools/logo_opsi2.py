"""Konsep logo putaran 2 -> branding/opsi-logo/2-*.png"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import shorts_engine as se  # noqa: E402

OUT = Path(__file__).parent.parent / "branding" / "opsi-logo"
S = 1080
C = S / 2


def kanvas(warna):
    img = Image.new("RGBA", (S, S), warna + (255,))
    return img, ImageDraw.Draw(img)


def bintang8(d, cx, cy, r, warna, outline=None, w=0):
    for rot in (0, 45):
        d.regular_polygon((cx, cy, r), 4, rotation=rot, fill=warna, outline=outline, width=w)


# E — Mikrofon + gulungan (vibe podcast / ngobrol), flat teal-oranye
def opsi_e(latar=(18, 82, 92), aksen=(242, 140, 56), terang=(250, 240, 220), garis=(30, 40, 45), teks1=None):
    img, d = kanvas(latar)
    d.ellipse((C - 260, 120, C + 260, 640), fill=aksen)
    # mikrofon
    d.rounded_rectangle((C - 85, 190, C + 85, 470), 85, fill=terang, outline=garis, width=12)
    for y in (260, 310, 360, 410):
        d.line((C - 60, y, C + 60, y), fill=garis, width=8)
    d.arc((C - 150, 300, C + 150, 560), 0, 180, fill=garis, width=16)
    d.line((C, 560, C, 610), fill=garis, width=16)
    d.line((C - 70, 612, C + 70, 612), fill=garis, width=16)
    d.text((C, 760), "ngomongin", font=se.font("caption", 120), fill=teks1 or terang, anchor="mm")
    d.text((C, 885), "SEJARAH", font=se.font("caption", 120), fill=aksen, anchor="mm")
    return img


# F — Geometri Islami: bintang 8 sudut emas, nuansa hijau zamrud
def opsi_f():
    img, d = kanvas((12, 64, 52))
    for i in range(-1, 6):
        for j in range(-1, 6):
            bintang8(d, i * 240 + (j % 2) * 120, j * 240, 70, None, (30, 92, 76), 4)
    d.ellipse((C - 330, C - 400, C + 330, C + 260), fill=(12, 64, 52))
    bintang8(d, C, C - 70, 300, (212, 172, 84))
    bintang8(d, C, C - 70, 262, (12, 64, 52))
    d.text((C, C - 70), "NS", font=se.font("judul", 210), fill=(240, 214, 150), anchor="mm")
    d.text((C, 800), "NGOMONGIN SEJARAH", font=se.font("judul", 58), fill=(240, 214, 150), anchor="mm")
    return img


# G — Playful: gelembung obrolan + jam pasir, kuning cerah
def opsi_g():
    img, d = kanvas((255, 205, 40))
    d.rounded_rectangle((150, 150, 930, 760), 140, fill=(35, 30, 60))
    d.polygon([(330, 740), (260, 920), (480, 750)], fill=(35, 30, 60))
    x, y = C, 360
    d.rectangle((x - 80, y - 130, x + 80, y - 110), fill=(255, 205, 40))
    d.rectangle((x - 80, y + 110, x + 80, y + 130), fill=(255, 205, 40))
    d.polygon([(x - 65, y - 110), (x + 65, y - 110), (x + 8, y), (x + 65, y + 110), (x - 65, y + 110), (x - 8, y)],
              fill=(255, 250, 235))
    d.polygon([(x - 50, y + 105), (x + 50, y + 105), (x, y + 45)], fill=(242, 120, 60))
    d.polygon([(x - 35, y - 60), (x + 35, y - 60), (x, y - 15)], fill=(242, 120, 60))
    d.text((C, 590), "NGOMONGIN", font=se.font("caption", 110), fill=(255, 250, 235), anchor="mm")
    d.text((C, 690), "SEJARAH", font=se.font("caption", 90), fill=(255, 205, 40), anchor="mm")
    return img


# H — Lengkung mihrab minimalis, krem & terakota
def opsi_h():
    img, d = kanvas((246, 236, 216))
    tera = (176, 82, 52)
    # lengkung runcing (pointed arch)
    d.rectangle((C - 230, 420, C + 230, 830), fill=tera)
    d.pieslice((C - 230, 190, C + 230, 650), 180, 360, fill=tera)
    d.polygon([(C - 40, 200), (C, 120), (C + 40, 200)], fill=tera)
    d.ellipse((C - 16, 92, C + 16, 124), fill=tera)
    d.text((C, 560), "NS", font=se.font("judul", 230), fill=(246, 236, 216), anchor="mm")
    d.text((C, 920), "ngomongin sejarah", font=se.font("judul", 70), fill=(60, 40, 30), anchor="mm")
    return img


# I — Kompas flat modern
def opsi_i():
    img, d = kanvas((236, 228, 210))
    navy, merah = (28, 40, 70), (214, 64, 50)
    d.ellipse((C - 330, 90, C + 330, 750), outline=navy, width=22)
    cy = 420
    d.polygon([(C, cy - 270), (C + 60, cy), (C, cy + 270), (C - 60, cy)], fill=navy)
    d.polygon([(C, cy - 270), (C + 60, cy), (C - 60, cy)], fill=merah)
    d.polygon([(C - 270, cy), (C, cy - 50), (C + 270, cy), (C, cy + 50)], fill=navy)
    d.ellipse((C - 26, cy - 26, C + 26, cy + 26), fill=(236, 228, 210), outline=navy, width=8)
    d.text((C, 850), "NGOMONGIN", font=se.font("caption", 96), fill=navy, anchor="mm")
    d.text((C, 950), "SEJARAH", font=se.font("caption", 96), fill=merah, anchor="mm")
    return img


# J — Stiker bold: tumpuk + bayangan, merah-kuning
def opsi_j():
    img, d = kanvas((210, 40, 40))
    for i in range(0, S * 2, 70):
        d.line((i, 0, i - S, S), fill=(196, 34, 34), width=30)
    f1, f2 = se.font("caption", 140), se.font("caption", 150)
    for dy, txt, f in ((370, "NGOMONG", f1), (530, "-IN", f1), (710, "SEJARAH", f2)):
        d.text((C + 14, dy + 16), txt, font=f, fill=(60, 10, 10), anchor="mm")
        d.text((C, dy), txt, font=f, fill=(255, 214, 60), anchor="mm", stroke_width=10, stroke_fill=(40, 10, 10))
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    opsi = {"E-podcast": opsi_e, "F-geometri": opsi_f, "G-playful": opsi_g,
            "H-mihrab": opsi_h, "I-kompas": opsi_i, "J-stiker": opsi_j}
    gambar = []
    for nama, fn in opsi.items():
        im = fn().convert("RGB")
        im.save(OUT / f"2-{nama}.png")
        gambar.append((nama, im))
    lembar = Image.new("RGB", (3 * 420, 2 * 620), (245, 245, 245))
    d = ImageDraw.Draw(lembar)
    for i, (nama, im) in enumerate(gambar):
        x, y = (i % 3) * 420 + 10, (i // 3) * 620 + 10
        lembar.paste(im.resize((400, 400)), (x, y))
        kecil = im.resize((140, 140))
        m = Image.new("L", (140, 140), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 140, 140), fill=255)
        lembar.paste(kecil, (x + 130, y + 415), m)
        d.text((x + 200, y + 582), nama, font=se.font("ui", 30), fill=(30, 30, 30), anchor="mm")
    lembar.save(OUT / "perbandingan-2.png")
    print("Selesai")
