"""Shorts ±88 detik: Sejarah air ledeng Batavia — dari minum air Ciliwung sampai pipa mata air Ciburial 1922.

Visual: (1) ilustrasi kali keruh + gelas air, (2) peta lokal Batavia–Bogor (darat custom),
(3) pancuran kayu Pancoran, (4) penampang sumur bor 1843, (5) jalur pipa Ciburial → Batavia,
(6) permainan kata waterleiding → ledeng.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "sejarah-air-ledeng-batavia-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "AIR LEDENG BATAVIA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
ORANYE = (235, 120, 25)
BIRU = (30, 80, 150)
BIRU_AIR = (70, 150, 210)
COKLAT_AIR = (120, 92, 48)
ABU = (60, 60, 70)
EMAS_T = (255, 214, 120)

# ------------------------------------------------------------------ peta lokal Teluk Jakarta – Bogor (disederhanakan)

DARAT_JKT = [(-5.98, 106.30), (-6.00, 106.45), (-6.02, 106.56), (-6.04, 106.65), (-6.09, 106.73), (-6.11, 106.79),
             (-6.105, 106.85), (-6.10, 106.89), (-6.105, 106.95), (-6.06, 106.99), (-5.98, 107.01), (-5.93, 107.04),
             (-5.94, 107.15), (-5.97, 107.35), (-7.40, 107.35), (-7.40, 106.20), (-5.98, 106.20)]
PULAU = [[(-6.00, 106.74), (-5.99, 106.76), (-6.01, 106.765), (-6.02, 106.745)],
         [(-5.95, 106.62), (-5.94, 106.64), (-5.96, 106.645), (-5.965, 106.625)]]

print("  menyiapkan peta Batavia–Bogor...")
LOKAL = Peta(106.35, 107.25, -7.30, -5.80, 2200, [], [(-6.72, 106.73, 0.09), (-6.75, 106.95, 0.1),
                                                     (-6.70, 106.85, 0.06)], seed=24, darat=[DARAT_JKT] + PULAU)

BATAVIA = (-6.135, 106.81)        # kota lama (Kota Tua)
BANTENG = (-6.170, 106.835)       # Lapangan Banteng, titik tiba air 1922
ISTIQLAL = (-6.170, 106.831)
BOGOR = (-6.597, 106.799)
CIBURIAL = (-6.600, 106.755)      # mata air Ciburial, Ciomas
PASAR_REBO = (-6.310, 106.863)
CILIWUNG = [(-6.68, 106.85), (-6.62, 106.82), (-6.55, 106.83), (-6.47, 106.835), (-6.40, 106.84),
            (-6.33, 106.855), (-6.27, 106.86), (-6.22, 106.85), (-6.18, 106.83), (-6.15, 106.815), (-6.112, 106.81)]
PIPA = [CIBURIAL, (-6.585, 106.78), (-6.55, 106.81), (-6.48, 106.835), (-6.40, 106.85), PASAR_REBO,
        (-6.25, 106.865), (-6.20, 106.85), BANTENG]


# ------------------------------------------------------------------ helper

def cam(lat, lon, zoom, p=LOKAL):
    x, y = p.px(lat, lon)
    return (x, y, zoom)


def peta(kamera, p=LOKAL):
    img = se.render_peta(p, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(kamera, ll, p=LOKAL):
    return kamera.layar(*p.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def hdr(img, sub="Batavia", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def pop(c, a):
    return back_out((c.t / c.d - a) / 0.1)


def sungai(d, kamera, k=1.0, warna=COKLAT_AIR, tebal=14, alpha=1.0):
    titik = [layar(kamera, ll) for ll in CILIWUNG]
    n = max(2, int(len(titik) * k + 0.999))
    pts = titik[:n]
    a = int(255 * alpha)
    d.line(pts, fill=(60, 45, 25, a), width=tebal + 8, joint="curve")
    d.line(pts, fill=warna + (a,), width=tebal, joint="curve")


def titik_kota(d, x, y, alpha=1.0, warna=(200, 40, 30)):
    a = int(255 * alpha)
    d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=warna + (a,), outline=(255, 255, 255, a), width=3)


def gelas(img, x, y, s=1.0, warna_air=COKLAT_AIR, level=0.75, t=0.0, alpha=1.0):
    """Gelas bening berisi air (tampak depan)."""
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    wt, wb, h = 150 * s, 115 * s, 330 * s
    atas = y - h / 2
    bawah = y + h / 2
    # air
    ya = bawah - h * level
    kiri = lambda yy: x - lerp(wb, wt, (bawah - yy) / h)
    kanan = lambda yy: x + lerp(wb, wt, (bawah - yy) / h)
    gel = [(kiri(ya) + 6, ya + math.sin(t * 3) * 5), (x, ya + math.sin(t * 3 + 1) * 7),
           (kanan(ya) - 6, ya + math.sin(t * 3 + 2) * 5), (kanan(bawah) - 8, bawah - 8), (kiri(bawah) + 8, bawah - 8)]
    d.polygon(gel, fill=warna_air + (235,))
    # kotoran melayang
    rng = random.Random(5)
    for i in range(14):
        fx, fy = rng.uniform(-0.75, 0.75), rng.uniform(0.1, 0.95)
        yy = lerp(ya + 20, bawah - 20, fy) + math.sin(t * 1.5 + i) * 10
        xx = x + fx * lerp(wb, wt, (bawah - yy) / h) * 0.8 + math.cos(t + i) * 6
        r = rng.uniform(4, 10) * s
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=(70, 50, 25, 220))
    # badan gelas
    d.polygon([(x - wt, atas), (x + wt, atas), (x + wb, bawah), (x - wb, bawah)], outline=(230, 240, 250, 255),
              width=max(4, int(9 * s)))
    d.ellipse((x - wt, atas - 18 * s, x + wt, atas + 18 * s), outline=(230, 240, 250, 255), width=max(3, int(7 * s)))
    d.line((x - wt * 0.7, atas + 40 * s, x - wb * 0.7, bawah - 40 * s), fill=(255, 255, 255, 120), width=int(14 * s))
    se.tempel(img, lap, alpha)


def keran(d, x, y, s=1.0, alpha=1.0, alir=0.0, t=0.0, warna_air=BIRU_AIR):
    """Keran air logam + kucuran."""
    a = int(255 * alpha)
    logam, gelap = (190, 195, 205, a), (70, 75, 85, a)
    d.rounded_rectangle((x - 200 * s, y - 40 * s, x + 30 * s, y + 40 * s), int(18 * s), fill=logam, outline=gelap,
                        width=max(3, int(6 * s)))
    d.rounded_rectangle((x - 10 * s, y - 40 * s, x + 70 * s, y + 110 * s), int(26 * s), fill=logam, outline=gelap,
                        width=max(3, int(6 * s)))
    d.rectangle((x - 70 * s, y - 100 * s, x - 40 * s, y - 40 * s), fill=logam, outline=gelap, width=max(2, int(4 * s)))
    d.rounded_rectangle((x - 130 * s, y - 125 * s, x + 20 * s, y - 95 * s), int(14 * s), fill=(200, 52, 44, a),
                        outline=gelap, width=max(2, int(4 * s)))
    if alir > 0:
        panjang = 380 * s * alir
        x0 = x + 30 * s
        for i in range(5):
            dx = (i - 2) * 9 * s + math.sin(t * 9 + i) * 3
            d.line((x0 + dx, y + 110 * s, x0 + dx, y + 110 * s + panjang), fill=warna_air + (int(a * 0.85),),
                   width=max(3, int(9 * s)))
        d.line((x0, y + 110 * s, x0, y + 110 * s + panjang), fill=(220, 240, 255, int(a * 0.8)), width=max(2, int(4 * s)))


def nisan(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.rounded_rectangle((x - 22 * s, y - 50 * s, x + 22 * s, y + 10 * s), int(18 * s), fill=(150, 150, 150, a),
                        outline=(40, 40, 45, a), width=max(2, int(4 * s)))
    d.line((x, y - 38 * s, x, y - 6 * s), fill=(60, 60, 65, a), width=max(2, int(4 * s)))
    d.line((x - 11 * s, y - 28 * s, x + 11 * s, y - 28 * s), fill=(60, 60, 65, a), width=max(2, int(4 * s)))
    d.ellipse((x - 30 * s, y + 4 * s, x + 30 * s, y + 18 * s), fill=(80, 60, 35, int(a * 0.6)))


def orang(d, x, y, s=1.0, alpha=1.0, warna=(70, 50, 35), kendi=True):
    """Siluet orang tanpa wajah membawa kendi."""
    a = int(255 * alpha)
    d.ellipse((x - 14 * s, y - 92 * s, x + 14 * s, y - 64 * s), fill=warna + (a,))
    d.polygon([(x - 22 * s, y - 60 * s), (x + 22 * s, y - 60 * s), (x + 30 * s, y), (x - 30 * s, y)], fill=warna + (a,))
    if kendi:
        d.ellipse((x + 18 * s, y - 50 * s, x + 50 * s, y - 16 * s), fill=(170, 90, 50, a), outline=(60, 30, 15, a))


def latar_kali(t):
    """Ilustrasi kali keruh: tepian pasir atas-bawah, arus coklat bergelombang."""
    img = Image.new("RGBA", (W, H), (20, 18, 16, 255))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 380, W, 620), fill=(176, 150, 104, 255))
    d.rectangle((0, 620, W, 1380), fill=COKLAT_AIR + (255,))
    d.rectangle((0, 1380, W, H), fill=(166, 140, 96, 255))
    for k in range(18):
        yy = 650 + k * 42
        off = (t * 60 + k * 37) % 160
        for x0 in range(-160, W + 160, 160):
            xx = x0 + off
            d.arc((xx, yy, xx + 120, yy + 30), 200, 340, fill=(150, 118, 70, 200), width=5)
    rng = random.Random(9)
    for i in range(10):  # sampah hanyut
        x = (rng.uniform(0, W) + t * rng.uniform(40, 90)) % (W + 100) - 50
        yy = rng.uniform(680, 1340)
        d.rounded_rectangle((x - 18, yy - 8, x + 18, yy + 8), 6, fill=(80, 65, 40, 230))
    return img


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = latar_kali(c.t)
    se.tint(img, (10, 5, 0), 0.35)
    gelas(img, 540, 1000, 1.25, COKLAT_AIR, 0.8, c.t)
    d = ImageDraw.Draw(img, "RGBA")
    s = 1 + 0.03 * math.sin(c.t * 6)
    se.teks(d, (540, 470), "DULU MINUM", int(124 * s), PUTIH, nama_font="caption", stroke=10,
            stroke_warna=(20, 10, 5))
    se.teks(d, (540, 610), "AIR KALI?!", int(150 * s), EMAS_T, nama_font="caption", stroke=11,
            stroke_warna=(20, 10, 5))
    a = c.p(0.22, 0.3)
    if a > 0:
        sk = pop(c, 0.22)
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((640, 1150, 1000, 1270), 20, outline=(200, 30, 30, 255), width=10)
        dl.text((820, 1210), "MENTAH!", font=se.font("caption", 64), fill=(200, 30, 30, 255), anchor="mm")
        lap = lap.rotate(-10 * sk, center=(820, 1210))
        se.tempel(img, lap, a)
    se.kartu(img, 540, 760, "…dan lahir satu kata yang kamu pakai", "", MERAH, alpha=c.p(0.55, 0.63), tiang=False,
             skala=pop(c, 0.55))
    hdr(img, "Batavia, abad ke-17", alpha=c.p(0.85, 0.97))
    return img


def a_tren(c):
    kamera = Kamera(*cam(-6.2, 106.83, 0.75))
    img, d = peta(kamera)
    se.tint(img, (10, 6, 0), 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    a1 = c.p(0.02, 0.1) * (1 - c.p(0.45, 0.5))
    se.kartu(img, 540, 620, "PAM Jaya diminta naikin layanan", "air bersih Jakarta · Nov 2026", BIRU, alpha=a1,
             tiang=False, skala=pop(c, 0.02))
    keran(d, 560, 830, 0.9, a1, alir=c.p(0.1, 0.3) * 0.6, t=c.t)
    k = c.p(0.5, 0.88)
    tahun = int(round(lerp(2026, 1670, k)))
    a2 = c.p(0.47, 0.53)
    se.teks(d, (540, 820), str(tahun), 200, EMAS_T, nama_font="caption", stroke=12, stroke_warna=(30, 15, 5),
            alpha=a2)
    se.teks(d, (540, 970), "ratusan tahun lalu…", 58, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=c.p(0.82, 0.9))
    hdr(img, "Lagi rame: air bersih")
    return img


def a_ciliwung(c):
    kamera = se.kamera_antara(cam(-6.25, 106.83, 0.9), cam(-6.16, 106.82, 1.15), c.p(0, 0.8))
    img, d = peta(kamera)
    sungai(d, kamera, c.p(0.0, 0.35))
    x, y = layar(kamera, BATAVIA)
    titik_kota(d, x, y)
    label(d, (x - 150, y - 10), "BATAVIA", 46, (120, 30, 20))
    xs, ys = layar(kamera, (-6.30, 106.86))
    label(d, (xs - 190, ys - 120), "Kali Ciliwung", 40, (70, 50, 25), c.p(0.2, 0.3))
    label(d, (540, 470), "Laut Jawa", 40, (230, 230, 240), 0.9)
    se.kartu(img, 540, 1000, "Diminum cuma disaring", "nggak dimasak", ORANYE, alpha=c.p(0.35, 0.42), tiang=False,
             skala=pop(c, 0.35))
    b = c.p(0.68, 0.75)
    se.kartu(img, 540, 1200, "Juga tempat buang sampah & kotoran", "", MERAH, alpha=b, tiang=False, skala=pop(c, 0.68))
    if b > 0:
        rng = random.Random(3)
        for i in range(12):
            ll = CILIWUNG[rng.randrange(4, len(CILIWUNG))]
            px, py = layar(kamera, ll)
            px += rng.uniform(-25, 25)
            py += rng.uniform(-25, 25) + math.sin(c.t * 2 + i) * 6
            d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=(60, 45, 20, int(230 * b)))
    hdr(img, "Zaman VOC")
    return img


def a_pancoran(c):
    img = se.latar_tekstur(W, H, 41).convert("RGBA")
    se.tint(img, (20, 10, 0), 0.15)
    d = ImageDraw.Draw(img, "RGBA")
    # bak penampung di atas tiang kayu
    kayu, gelap = (130, 85, 45, 255), (60, 35, 15, 255)
    d.rectangle((150, 560, 470, 720), fill=kayu, outline=gelap, width=6)
    d.rectangle((160, 575, 460, 610), fill=COKLAT_AIR + (255,))
    for tx in (180, 440):
        d.rectangle((tx - 12, 720, tx + 12, 1250), fill=kayu, outline=gelap, width=4)
    # talang kayu
    d.polygon([(460, 640), (760, 690), (760, 720), (460, 670)], fill=kayu, outline=gelap)
    # kucuran
    a = c.p(0.08, 0.2)
    for i in range(4):
        dx = i * 8 + math.sin(c.t * 10 + i) * 3
        d.line((752 + dx, 720, 760 + dx, 720 + 480 * a), fill=(150, 125, 80, int(230 * a)), width=8)
    d.ellipse((660, 1170, 880, 1240), fill=(150, 125, 80, int(200 * a)))
    # orang antre (siluet tanpa wajah)
    for i, ox in enumerate((600, 900, 980)):
        orang(d, ox, 1260 + (i % 2) * 8, 1.4, c.p(0.15 + i * 0.05, 0.22 + i * 0.05))
    se.kartu(img, 540, 470, "± 1670", "air kali ditampung, dikucurkan", ORANYE, alpha=c.p(0.02, 0.1), tiang=False,
             skala=pop(c, 0.02))
    b = c.p(0.55, 0.62)
    if b > 0:
        sk = pop(c, 0.55)
        se.teks(d, (540, 900), "PANCURAN", int(110 * sk) + 1, PUTIH, nama_font="caption", stroke=9,
                stroke_warna=(30, 15, 5), alpha=b)
        se.teks(d, (540, 1020), "→ PANCORAN", int(90 * sk) + 1, EMAS_T, nama_font="caption", stroke=8,
                stroke_warna=(30, 15, 5), alpha=c.p(0.68, 0.75))
    hdr(img, "Pancoran, Glodok")
    return img


_rn = random.Random(17)
NISAN_POS = [(_rn.uniform(150, 930), _rn.uniform(600, 1000)) for _ in range(22)]


def a_kuburan(c):
    kamera = se.kamera_antara(cam(-6.15, 106.82, 1.6), cam(-6.145, 106.82, 1.9), c.p(0, 1))
    img, d = peta(kamera)
    se.tint(img, (10, 5, 10), 0.45 + 0.15 * c.p(0.5, 0.8))
    d = ImageDraw.Draw(img, "RGBA")
    n = int(c.p(0.1, 0.65) * len(NISAN_POS) + 0.0001)
    for i in range(n):
        x, y = NISAN_POS[i]
        sk = back_out(clamp((c.t / c.d - 0.1 - i * 0.55 / len(NISAN_POS)) / 0.06))
        if sk > 0.15:
            nisan(d, x, y, 1.2 * sk)
    se.kartu(img, 540, 480, "+ wabah malaria", "", MERAH, alpha=c.p(0.1, 0.17), tiang=False, skala=pop(c, 0.1))
    a = c.p(0.35, 0.42)
    if a > 0:
        se.panel(img, (140, 1040, 940, 1250), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1110), "2.000 – 3.000", 84, (150, 25, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 1195), "meninggal per tahun (setelah 1733)", 34, (90, 70, 50), nama_font="tangan_tipis",
                alpha=a)
    b = c.p(0.72, 0.8)
    if b > 0:
        sk = pop(c, 0.72)
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((90, 720, 990, 920), 24, fill=(20, 10, 10, 200), outline=(220, 40, 30, 255), width=10)
        dl.text((540, 790), "KUBURAN", font=se.font("caption", 80), fill=(235, 60, 45, 255), anchor="mm")
        dl.text((540, 870), "ORANG BELANDA", font=se.font("caption", 60), fill=PUTIH, anchor="mm")
        lap = lap.rotate(-5 * sk, center=(540, 820))
        se.tempel(img, lap, b)
    hdr(img, "Batavia, abad ke-18")
    return img


def a_sumur(c):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img, "RGBA")
    # langit + tanah berlapis
    d.rectangle((0, 380, W, 560), fill=(150, 190, 220, 255))
    lapis = [(560, 700, (150, 110, 60)), (700, 860, (125, 90, 50)), (860, 1030, (165, 140, 95)),
             (1030, 1200, (105, 80, 55)), (1200, 1380, (85, 70, 60))]
    for y0, y1, w in lapis:
        d.rectangle((0, y0, W, y1), fill=w + (255,))
        rng = random.Random(y0)
        for _ in range(40):
            x, y = rng.uniform(0, W), rng.uniform(y0 + 5, y1 - 5)
            d.ellipse((x - 5, y - 4, x + 5, y + 4), fill=(0, 0, 0, 40))
    # menara bor
    d.polygon([(470, 560), (610, 560), (560, 420), (520, 420)], outline=(60, 40, 20, 255), width=8)
    d.line((490, 500, 590, 500), fill=(60, 40, 20, 255), width=6)
    k = c.p(0.2, 0.6)
    ujung = 560 + 790 * k
    d.rectangle((528, 560, 552, ujung), fill=(90, 90, 100, 255), outline=(30, 30, 35, 255), width=3)
    d.polygon([(528, ujung), (552, ujung), (540, ujung + 30)], fill=(60, 60, 70, 255))
    meter = int(round(83 * k))
    se.teks(d, (800, min(ujung, 1330)), f"{meter} m", 72, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=c.p(0.2, 0.25))
    a0 = c.p(0.0, 0.06) * (1 - c.p(0.18, 0.22))
    if a0 > 0:
        se.teks(d, (540, 900), "TAPI INI", 120, PUTIH, nama_font="caption", stroke=10, stroke_warna=(0, 0, 0), alpha=a0)
        se.teks(d, (540, 1040), "BELUM SEBERAPA…", 100, EMAS_T, nama_font="caption", stroke=9,
                stroke_warna=(0, 0, 0), alpha=a0)
    se.kartu(img, 270, 470, "1843: sumur bor", "Benteng Prins Frederik", BIRU, alpha=c.p(0.22, 0.3), tiang=False,
             skala=pop(c, 0.22) * 0.95)
    se.kartu(img, 800, 640, "kini Masjid Istiqlal", "", ABU, alpha=c.p(0.5, 0.58), tiang=False, skala=pop(c, 0.5))
    b = c.p(0.8, 0.87)
    if b > 0:
        se.kartu(img, 300, 1000, "Kurang disukai", "sebagian ada yang asin", MERAH, alpha=b, tiang=False,
                 skala=pop(c, 0.8))
    hdr(img, "Batavia, 1843")
    return img


def a_ciburial(c):
    kamera = se.kamera_antara(cam(-6.25, 106.82, 0.8), cam(-6.52, 106.79, 1.0), c.p(0.0, 0.5))
    img, d = peta(kamera)
    sungai(d, kamera, 1.0, alpha=0.6)
    for nama, ll in {"BATAVIA": BANTENG, "Bogor": BOGOR}.items():
        x, y = layar(kamera, ll)
        if y < 420:
            continue
        titik_kota(d, x, y, 1.0 if nama == "BATAVIA" else 0.9, (200, 40, 30) if nama == "BATAVIA" else (120, 80, 40))
        label(d, (x + 110, y - 30), nama, 44 if nama == "BATAVIA" else 38, (120, 30, 20) if nama == "BATAVIA" else TINTA)
    x, y = layar(kamera, CIBURIAL)
    a = c.p(0.35, 0.45)
    if a > 0:
        pulse = 1 + 0.2 * math.sin(c.t * 6)
        se.glow(img, x, y, 140 * pulse, (140, 210, 255), 1.4 * a)
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=BIRU_AIR + (int(255 * a),), outline=(255, 255, 255, int(255 * a)),
                  width=4)
        se.kartu(img, x + 60, y - 30, "Mata air Ciburial", "Ciomas, Bogor · 484 liter/detik", BIRU, alpha=a,
                 skala=pop(c, 0.35))
    se.kartu(img, 540, 480, "1918: proyek pipa disetujui", "", ORANYE, alpha=c.p(0.7, 0.77), tiang=False,
             skala=pop(c, 0.7))
    hdr(img, "Bogor, 1918")
    return img


def a_pipa(c):
    k = c.p(0.05, 0.5)
    kamera = se.kamera_antara(cam(-6.48, 106.80, 1.0), cam(-6.385, 106.82, 0.65), c.p(0.0, 0.5))
    img, d = peta(kamera)
    titik = [layar(kamera, ll) for ll in PIPA]
    garis_bawah = [(x, y) for x, y in titik]
    se.garis_putus(d, garis_bawah, k, (30, 70, 140), tebal=12, putus=26, celah=8, panah=True)
    pos, _ = se.titik_di_jalur(titik, k)
    if 0 < k < 1:
        se.glow(img, pos[0], pos[1], 70, (140, 210, 255), 1.2)
        d = ImageDraw.Draw(img, "RGBA")
    for nama, ll in {"BATAVIA": BANTENG, "Ciburial": CIBURIAL, "Pasar Rebo": PASAR_REBO}.items():
        x, y = layar(kamera, ll)
        titik_kota(d, x, y, 1.0, (200, 40, 30) if nama == "BATAVIA" else BIRU)
        label(d, (x - 140, y) if nama == "Ciburial" else ((x - 170, y + 30) if nama == "BATAVIA" else (x + 150, y)), nama, 42 if nama == "BATAVIA" else 36,
              (120, 30, 20) if nama == "BATAVIA" else TINTA)
    km = int(round(53 * k))
    se.teks(d, (540, 470), f"± {km} km pipa", 84, PUTIH, nama_font="caption", stroke=8, stroke_warna=(10, 20, 40),
            alpha=c.p(0.05, 0.1) * (1 - c.p(0.5, 0.55)))
    a = c.p(0.5, 0.57)
    if a > 0:
        se.panel(img, (110, 395, 970, 590), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 460), "23 DESEMBER 1922", 70, BIRU, nama_font="caption", alpha=a)
        se.teks(d, (540, 540), "air pertama tiba di Batavia", 38, (90, 70, 50), nama_font="tangan", alpha=a)
    se.kartu(img, 760, 1000, "Hari jadi PAM Jaya", "sampai sekarang", MERAH, alpha=c.p(0.78, 0.85), tiang=False,
             skala=pop(c, 0.78))
    hdr(img, "Ciburial → Batavia")
    return img


def a_ledeng(c):
    img = Image.new("RGBA", (W, H), (22, 26, 36, 255))
    d = ImageDraw.Draw(img, "RGBA")
    se.glow(img, 540, 850, 520, (60, 110, 170), 0.8)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 470), "bahasa Belanda:", 54, (200, 210, 230), nama_font="tangan", alpha=c.p(0.12, 0.2))
    a = c.p(0.18, 0.26)
    fw = se.font("caption", 120)
    water, leiding = "WATER", "LEIDING"
    lw1, lw2 = fw.getlength(water), fw.getlength(leiding)
    x0 = 540 - (lw1 + lw2) / 2
    redup = 1 - 0.65 * c.p(0.45, 0.52)
    se.teks(d, (x0, 620), water, 120, PUTIH, nama_font="caption", anchor="lm", stroke=8, stroke_warna=(0, 0, 0),
            alpha=a * redup)
    se.teks(d, (x0 + lw1, 620), leiding, 120, EMAS_T, nama_font="caption", anchor="lm", stroke=8,
            stroke_warna=(0, 0, 0), alpha=a)
    se.teks(d, (540, 720), "(saluran / pipa air)", 40, (200, 210, 230), nama_font="tangan_tipis", alpha=a)
    g = c.p(0.45, 0.55)
    if g > 0:
        xl = x0 + lw1
        d.line((xl, 690, xl + lw2 * g, 690), fill=(235, 60, 45, 255), width=10)
        d.line((540, 760, 540, 760 + 120 * g), fill=(255, 255, 255, int(220 * g)), width=8)
        d.polygon([(515, 760 + 120 * g), (565, 760 + 120 * g), (540, 800 + 120 * g)], fill=(255, 255, 255, int(220 * g)))
    b = c.p(0.6, 0.66)
    if b > 0:
        sk = pop(c, 0.6)
        se.teks(d, (540, 1010), "LEDENG", int(220 * sk) + 1, (120, 200, 255), nama_font="caption", stroke=14,
                stroke_warna=(10, 20, 40), alpha=b)
        keran(d, 650, 1200, 0.5, c.p(0.7, 0.78), alir=c.p(0.78, 0.9) * 0.35, t=c.t)
    hdr(img, "Jawabannya…")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(-6.35, 106.82, 0.75))
    img, d = peta(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1080), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Air dari keran kamu", 54, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 650), "1922 → 2026", 64, (30, 80, 150), nama_font="caption", alpha=a)
        keran(d, 520, 790, 0.6, a, alir=0.5, t=c.t)
        se.teks(d, (540, 1020), "ceritanya lebih dari 100 tahun", 40, (90, 70, 50), alpha=a)
    b = c.p(0.6, 0.68)
    if b > 0:
        m = maskot()
        if m is not None:
            loncat = abs(math.sin(c.t * 5)) * 18
            se.tempel(img, m, b, (540 - m.width // 2, int(560 - loncat)))
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        sk = back_out((c.t / c.d - 0.6) / 0.1)
        w2 = 380 * sk
        dl.rounded_rectangle((540 - w2, 960, 540 + w2, 1090), 40, fill=(200, 52, 44, 245))
        dl.text((540, 1025), "NGOMONGIN SEJARAH", font=se.font("caption", int(56 * sk) + 1), fill=PUTIH, anchor="mm")
        dl.text((540, 1160), "Follow buat cerita berikutnya", font=se.font("ui", 42), fill=PUTIH, anchor="mm",
                stroke_width=4, stroke_fill=(0, 0, 0))
        se.tempel(img, lap, b)
    return img


ADEGAN = [
    Adegan("hook", "Dulu, orang Belanda minum air kali. Mentah-mentah. Dan dari sini, lahir satu kata yang masih "
                   "kamu pakai sampai sekarang.", a_hook, transisi=False),
    Adegan("tren", "Lagi rame PAM Jaya diminta ningkatin layanan air bersih? Urusan air Jakarta, ternyata udah bikin "
                   "pusing dari ratusan tahun lalu.", a_tren),
    Adegan("ciliwung", "Zaman VOC, air minum Batavia diambil dari Kali Ciliwung. Cuma disaring, nggak dimasak. "
                       "Padahal, kali itu juga tempat buang sampah dan kotoran.", a_ciliwung),
    Adegan("pancoran", "Sekitar tahun seribu enam ratus tujuh puluh, air kali ditampung, lalu dikucurkan lewat "
                       "pancuran kayu. Konon, dari situlah nama Pancoran di Glodok.", a_pancoran),
    Adegan("kuburan", "Hasilnya? Penyakit di mana-mana, ditambah wabah malaria. Setelah tahun seribu tujuh ratus tiga "
                      "puluh tiga, dua sampai tiga ribu orang meninggal tiap tahun. Batavia dijuluki, kuburan orang "
                      "Belanda.", a_kuburan),
    Adegan("sumur", "Tapi ini belum seberapa. Tahun seribu delapan ratus empat puluh tiga, Belanda ngebor sumur "
                    "delapan puluh tiga meter, di lokasi yang kini jadi Masjid Istiqlal. Airnya kurang disukai, "
                    "sebagian malah asin.", a_sumur),
    Adegan("ciburial", "Akhirnya, mereka nemu mata air jernih di Ciburial, Ciomas, Bogor. Tahun seribu sembilan ratus "
                       "delapan belas, proyek pipanya disetujui.", a_ciburial),
    Adegan("pipa", "Pipanya sekitar lima puluh tiga kilometer. Dua puluh tiga Desember seribu sembilan ratus dua puluh "
                   "dua, airnya pertama sampai di Batavia. Tanggal itu kini jadi hari jadi PAM Jaya.", a_pipa),
    Adegan("ledeng", "Nah, ini jawabannya. Saluran air dalam bahasa Belanda, waterleiding. Kata leiding itulah, yang "
                     "di lidah kita jadi... ledeng!", a_ledeng),
    Adegan("penutup", "Jadi, air dari keran kamu, ceritanya udah lebih dari seratus tahun. Follow Ngomongin Sejarah "
                      "buat cerita berikutnya!", a_penutup),
]
