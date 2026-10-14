"""Beberapa konsep logo alternatif -> branding/opsi-logo/"""

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import shorts_engine as se  # noqa: E402

OUT = Path(__file__).parent.parent / "branding" / "opsi-logo"
S = 1080
C = S / 2
EMAS = (226, 182, 92)
EMAS_TUA = (150, 110, 45)
MERAH = (196, 40, 36)


def teks_lengkung(img, isi, f, r, sudut_tengah, warna, atas=True, stroke=0, stroke_warna=(0, 0, 0)):
    """Tulis teks melengkung mengikuti lingkaran radius r."""
    lebar = [f.getlength(ch) for ch in isi]
    total = sum(lebar) / r  # radian
    a = sudut_tengah - total / 2 if atas else sudut_tengah + total / 2
    for ch, w in zip(isi, lebar):
        da = w / r
        tengah = a + da / 2 if atas else a - da / 2
        x, y = C + r * math.cos(tengah), C + r * math.sin(tengah)
        lap = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        ImageDraw.Draw(lap).text((100, 100), ch, font=f, fill=warna, anchor="mm", stroke_width=stroke, stroke_fill=stroke_warna)
        rot = -math.degrees(tengah) - 90 if atas else -math.degrees(tengah) + 90
        lap = lap.rotate(rot, resample=Image.BICUBIC)
        img.alpha_composite(lap, (int(x - 100), int(y - 100)))
        a = a + da if atas else a - da


def kertas(seed, gelap=0.0):
    img = se.latar_tekstur(S, S, seed).convert("RGBA")
    se.tint(img, (0, 0, 0), gelap)
    return img


# A — Lencana klasik: navy + emas, monogram, teks melingkar
def opsi_a():
    img = Image.new("RGBA", (S, S), (22, 32, 54, 255))
    tekstur = se.fbm(S, S, 200, 5, 5)
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] *= (0.8 + 0.35 * tekstur)[..., None]
    img = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(img)
    d.ellipse((60, 60, S - 60, S - 60), outline=EMAS, width=14)
    d.ellipse((95, 95, S - 95, S - 95), outline=EMAS_TUA, width=4)
    d.ellipse((250, 250, S - 250, S - 250), outline=EMAS, width=8)
    f = se.font("judul", 78)
    teks_lengkung(img, "NGOMONGIN", f, 345, -math.pi / 2, EMAS, atas=True)
    teks_lengkung(img, "SEJARAH", f, 345, math.pi / 2, EMAS, atas=False)
    d.text((C - 4, C + 10), "NS", font=se.font("judul", 230), fill=(245, 230, 190), anchor="mm")
    for sx in (-1, 1):
        x = C + sx * 345
        d.regular_polygon((x, C, 18), 4, rotation=45, fill=EMAS)
    return img


# B — Bold modern: hitam, tipografi besar, aksen merah (paling kebaca di HP)
def opsi_b():
    img = Image.new("RGBA", (S, S), (16, 14, 12, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((230, 640, S - 230, 656), fill=MERAH)
    d.text((C, 430), "NGOMONGIN", font=se.font("caption", 112), fill=(255, 255, 255), anchor="mm")
    d.text((C, 555), "SEJARAH", font=se.font("judul", 150), fill=MERAH, anchor="mm")
    # jam pasir kecil
    x, y = C, 790
    d.line((x - 60, y - 80, x + 60, y - 80), fill=(235, 220, 190), width=12)
    d.line((x - 60, y + 80, x + 60, y + 80), fill=(235, 220, 190), width=12)
    d.polygon([(x - 48, y - 72), (x + 48, y - 72), (x, y), (x + 48, y + 72), (x - 48, y + 72), (x, y)],
              outline=(235, 220, 190), width=8)
    d.polygon([(x - 30, y + 70), (x + 30, y + 70), (x, y + 30)], fill=EMAS)
    d.polygon([(x - 18, y - 30), (x + 18, y - 30), (x, y - 4)], fill=EMAS)
    return img


# C — Stempel lilin merah di atas kertas tua
def opsi_c():
    img = kertas(41)
    lilin = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lilin)
    pts = []
    for i in range(72):
        a = i / 72 * 2 * math.pi
        r = 400 + 22 * math.sin(i * 1.7) + 14 * math.sin(i * 4.3)
        pts.append((C + r * math.cos(a), C + r * math.sin(a)))
    d.polygon(pts, fill=(150, 22, 22, 255))
    lilin = lilin.filter(ImageFilter.GaussianBlur(2))
    bayang = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bayang.paste((0, 0, 0, 120), (14, 20), lilin.getchannel("A").point(lambda v: v))
    img.alpha_composite(bayang.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(lilin)
    d = ImageDraw.Draw(img)
    d.ellipse((C - 320, C - 320, C + 320, C + 320), fill=(176, 32, 30), outline=(110, 12, 12), width=12)
    d.ellipse((C - 280, C - 280, C + 280, C + 280), outline=(215, 80, 70), width=4)
    f = se.font("judul", 54)
    teks_lengkung(img, "NGOMONGIN", f, 235, -math.pi / 2, (250, 205, 190), atas=True)
    teks_lengkung(img, "SEJARAH", f, 235, math.pi / 2, (250, 205, 190), atas=False)
    d.text((C, C + 6), "NS", font=se.font("judul", 190), fill=(120, 12, 12), anchor="mm")
    d.text((C - 6, C), "NS", font=se.font("judul", 190), fill=(240, 150, 130), anchor="mm")
    return img


# D — Gulungan naskah + pena, nuansa bercerita
def opsi_d():
    img = Image.new("RGBA", (S, S), (54, 36, 24, 255))
    tekstur = se.fbm(S, S, 160, 8, 5)
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] *= (0.75 + 0.45 * tekstur)[..., None]
    img = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(img)
    # gulungan
    kertas_g = se.latar_tekstur(860, 420, 77).convert("RGBA")
    m = Image.new("L", (860, 420), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, 860, 420), 20, fill=255)
    img.paste(kertas_g, (110, 330), m)
    for x in (110, 970):
        d.rounded_rectangle((x - 40, 300, x + 40, 780), 40, fill=(200, 170, 120), outline=(70, 45, 25), width=8)
        d.ellipse((x - 40, 290, x + 40, 330), fill=(120, 80, 45), outline=(70, 45, 25), width=6)
        d.ellipse((x - 40, 750, x + 40, 790), fill=(120, 80, 45), outline=(70, 45, 25), width=6)
    d.text((C, 480), "Ngomongin", font=se.font("tangan", 120), fill=(45, 28, 15), anchor="mm")
    d.text((C, 630), "SEJARAH", font=se.font("judul", 140), fill=MERAH, anchor="mm")
    d.text((C, 880), "cerita masa lalu", font=se.font("tangan", 64), fill=(235, 210, 160), anchor="mm")
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    opsi = {"A-lencana": opsi_a, "B-modern": opsi_b, "C-stempel": opsi_c, "D-gulungan": opsi_d}
    gambar = []
    for nama, fn in opsi.items():
        im = fn().convert("RGB")
        im.save(OUT / f"{nama}.png")
        gambar.append((nama, im))
    # lembar perbandingan, lengkap dengan pratinjau bulat (seperti di aplikasi)
    lembar = Image.new("RGB", (4 * 420, 640), (245, 245, 245))
    d = ImageDraw.Draw(lembar)
    for i, (nama, im) in enumerate(gambar):
        x = i * 420 + 10
        lembar.paste(im.resize((400, 400)), (x, 10))
        kecil = im.resize((150, 150))
        mask = Image.new("L", (150, 150), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 150, 150), fill=255)
        lembar.paste(kecil, (x + 125, 430), mask)
        d.text((x + 200, 610), nama, font=se.font("ui", 30), fill=(30, 30, 30), anchor="mm")
    lembar.save(OUT / "perbandingan.png")
    print("Selesai:", OUT)
