"""Shorts ±90 detik: Sejarah El Niño — dari nelayan Peru sampai Super El Niño 2026.

Pemicu: berita Super El Niño 2026 (BMKG: indeks Niño 3.4 +2,76 °C, BRIN: kemarau bisa sampai 2027), Okt 2026.
Peta Peru, Asia, Asia Tenggara + ilustrasi (jungkat-jungkit Walker, penampang Pasifik).
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "sejarah-el-nino-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "SEJARAH EL NIÑO"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU = (40, 100, 170)
ORANYE = (235, 110, 30)
HANGAT = (220, 70, 40)
GELAP = (25, 20, 15)
COKLAT = (120, 80, 40)


def _b(lon):
    """Bujur barat -> bujur 0..360 (peta Amerika Selatan pakai bujur timur > 180)."""
    return lon + 360


AMERIKA_SELATAN = [(12, _b(-72)), (11, _b(-75)), (9.5, _b(-76.5)), (8.5, _b(-77.5)), (7, _b(-77.8)), (4, _b(-77.4)),
                   (1.6, _b(-79)), (0.9, _b(-80.1)), (-0.5, _b(-80.5)), (-2.2, _b(-80.9)), (-3.4, _b(-80.3)),
                   (-4.3, _b(-81.3)), (-5.8, _b(-81.1)), (-7.5, _b(-79.6)), (-9.2, _b(-78.5)), (-12, _b(-77.1)),
                   (-13.7, _b(-76.3)), (-15.4, _b(-75.1)), (-16.6, _b(-72.6)), (-18.4, _b(-70.3)), (-21, _b(-70.1)),
                   (-23.6, _b(-70.4)), (-27, _b(-70.9)), (-30, _b(-71.4)), (-30, _b(-55)), (12, _b(-55))]

print("  menyiapkan peta Asia Tenggara...")
PETA = Peta(90, 125, -12, 22, 100, [], [(-2, 114, 1.5), (0, 101, 1.2), (5, 117, 1.0), (18, 101, 3), (14, 106, 2)],
            seed=21, darat=pd.SEMUA)
print("  menyiapkan peta Amerika Selatan...")
PETA_SA = Peta(_b(-95), _b(-60), -25, 10, 90, [],
               [(-1, _b(-78.5), 2.0), (-8, _b(-77.5), 2.2), (-14, _b(-72), 2.4), (-19, _b(-68), 2.6)],
               seed=31, darat=[AMERIKA_SELATAN])
print("  menyiapkan peta Asia...")
PETA_ASIA = Peta(60, 128, -12, 48, 55, [], [(30, 85, 4), (35, 100, 4), (27, 92, 2)], seed=41, darat=pd.SEMUA)

LABEL_ID = {"SUMATRA": (-0.3, 101.6), "KALIMANTAN": (-0.8, 112.6), "JAWA": (-7.2, 110.0)}
TITIK_API = [(-2.5, 114.0), (-2.2, 113.5), (-3.0, 114.5), (-1.8, 114.8), (0.5, 116.8), (-0.5, 110.5), (0.2, 109.8),
             (-1.5, 112.0), (0.8, 102.0), (1.4, 101.5), (0.4, 103.0), (-1.5, 103.8), (-3.0, 105.0), (-2.6, 104.6),
             (-0.5, 102.5), (-1.0, 115.8)]
PANTAI_PERU = [(2.0, _b(-80.5)), (-0.5, _b(-81.4)), (-3.4, _b(-81.6)), (-6.0, _b(-81.9)), (-9.0, _b(-79.6)),
               (-12.0, _b(-78.0)), (-15.0, _b(-76.0))]


# ------------------------------------------------------------------ helper

def cam(petanya, lat, lon, zoom):
    x, y = petanya.px(lat, lon)
    return (x, y, zoom)


def peta(petanya, kamera):
    img = se.render_peta(petanya, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(petanya, kamera, ll):
    return kamera.layar(*petanya.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def judul_besar(d, xy, isi, uk, warna=PUTIH, alpha=1.0, stroke=(0, 0, 0)):
    se.teks(d, xy, isi, uk, warna, nama_font="caption", stroke=max(5, uk // 14), stroke_warna=stroke, alpha=alpha)


def hdr(img, sub="dari Peru sampai 2026", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def gradasi(atas, bawah):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (np.array(atas, np.float32) * (1 - g) + np.array(bawah, np.float32) * g).repeat(W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    return img, ImageDraw.Draw(img, "RGBA")


def api(d, x, y, t, s=1.0, alpha=1.0, seed=0):
    """Ikon api kecil yang berkedip."""
    if alpha <= 0.01:
        return
    k = 1 + 0.15 * math.sin(t * 11 + seed * 1.7)
    s = s * k
    a = int(255 * alpha)
    luar = [(x, y - 34 * s), (x + 14 * s, y - 12 * s), (x + 16 * s, y + 6 * s), (x + 8 * s, y + 16 * s),
            (x - 8 * s, y + 16 * s), (x - 16 * s, y + 6 * s), (x - 12 * s, y - 14 * s), (x - 4 * s, y - 6 * s)]
    d.polygon(luar, fill=(225, 60, 25, a), outline=(80, 20, 10, a))
    dalam = [(x + 1 * s, y - 16 * s), (x + 8 * s, y + 2 * s), (x + 5 * s, y + 12 * s), (x - 5 * s, y + 12 * s),
             (x - 8 * s, y + 2 * s)]
    d.polygon(dalam, fill=(255, 205, 60, a))


def titik_api(d, kamera, t, munculkan=1.0, s=1.0, alpha=1.0):
    n = int(len(TITIK_API) * clamp(munculkan) + 0.999) if munculkan > 0 else 0
    for i, ll in enumerate(TITIK_API[:n]):
        x, y = layar(PETA, kamera, ll)
        api(d, x, y, t, s, alpha, i)


def awan(img, x, y, s=1.0, warna=(245, 245, 250), alpha=1.0, seed=0, lebar=1.0):
    """Awan kartun dari tumpukan elips."""
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    a = int(255 * alpha)
    gelap = tuple(int(v * 0.78) for v in warna)
    bola = []
    for i in range(9):
        bx = x + (i - 4) * 46 * s * lebar + rng.uniform(-10, 10) * s
        by = y - (60 - abs(i - 4) * 12) * s * rng.uniform(0.6, 1.1)
        r = (70 - abs(i - 4) * 6) * s * rng.uniform(0.85, 1.15)
        bola.append((bx, by, r))
    for bx, by, r in bola:
        d.ellipse((bx - r, by - r + 10 * s, bx + r, by + r + 10 * s), fill=gelap + (a,))
    for bx, by, r in bola:
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=tuple(warna) + (a,))
    d.rounded_rectangle((x - 200 * s * lebar, y - 30 * s, x + 200 * s * lebar, y + 40 * s), int(30 * s),
                        fill=tuple(warna) + (a,))
    img.alpha_composite(lap)


def hujan_lokal(d, x, y, lebar, tinggi, t, kuat=1.0, seed=2, n=40):
    if kuat <= 0.01:
        return
    rng = random.Random(seed)
    for i in range(n):
        f = (rng.random() + t * 1.4) % 1
        xx = x + rng.uniform(-lebar / 2, lebar / 2)
        yy = y + f * tinggi
        d.line((xx, yy, xx - 4, yy + 26), fill=(60, 110, 190, int(230 * kuat * (1 - f * 0.6))), width=4)


def matahari(img, x, y, r, t, alpha=1.0):
    if alpha <= 0.01:
        return
    se.glow(img, x, y, r * 2.4, (255, 200, 80), alpha)
    d = ImageDraw.Draw(img, "RGBA")
    a = int(255 * alpha)
    for i in range(12):
        sud = i * math.pi / 6 + t * 0.4
        d.line((x + math.cos(sud) * r * 1.2, y + math.sin(sud) * r * 1.2,
                x + math.cos(sud) * r * 1.6, y + math.sin(sud) * r * 1.6), fill=(255, 190, 40, a), width=8)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 205, 60, a), outline=(220, 130, 20, a), width=5)


def ikan(d, x, y, s=1.0, alpha=1.0, warna=(170, 190, 200)):
    a = int(255 * alpha)
    if a <= 2:
        return
    d.ellipse((x - 22 * s, y - 9 * s, x + 18 * s, y + 9 * s), fill=tuple(warna) + (a,), outline=GELAP + (a,), width=2)
    d.polygon([(x + 14 * s, y), (x + 30 * s, y - 11 * s), (x + 30 * s, y + 11 * s)], fill=tuple(warna) + (a,),
              outline=GELAP + (a,))
    d.ellipse((x - 15 * s, y - 3 * s, x - 10 * s, y + 2 * s), fill=GELAP + (a,))


def perahu(d, x, y, s=1.0, alpha=1.0, goyang=0.0):
    a = int(255 * alpha)
    if a <= 2:
        return
    y = y + goyang
    d.polygon([(x - 34 * s, y), (x + 34 * s, y), (x + 22 * s, y + 16 * s), (x - 22 * s, y + 16 * s)],
              fill=(120, 70, 35, a), outline=GELAP + (a,))
    d.line((x, y, x, y - 46 * s), fill=GELAP + (a,), width=3)
    d.polygon([(x + 2 * s, y - 44 * s), (x + 28 * s, y - 6 * s), (x + 2 * s, y - 6 * s)], fill=(245, 235, 210, a),
              outline=GELAP + (a,))


def panah_arus(d, titik, progres, warna=HANGAT, tebal=10, alpha=1.0):
    """Arus laut: garis tebal putus-putus dengan panah."""
    return se.garis_putus(d, titik, progres, warna, tebal=tebal, putus=26, celah=14, alpha=alpha)


# ------------------------------------------------------------------ adegan

def _ombak(d, y0, t, warna=(30, 50, 90), amp=18, alpha=255):
    titik = [(0, H)]
    for x in range(0, W + 20, 20):
        titik.append((x, y0 + math.sin(x / 70 + t * 2) * amp + math.sin(x / 29 - t * 3) * amp * 0.4))
    titik.append((W, H))
    d.polygon(titik, fill=tuple(warna) + (alpha,))


def a_hook(c):
    k = c.t / c.d
    panas = c.p(0.0, 0.45)
    img, d = gradasi(se.lerp_rgb((70, 120, 180), (200, 110, 50), panas), se.lerp_rgb((150, 190, 220), (240, 190, 110), panas))
    matahari(img, 820, 560, 70 + 20 * panas, c.t, 0.4 + 0.6 * panas)
    d = ImageDraw.Draw(img, "RGBA")
    _ombak(d, 1130, c.t, (40, 70, 120))
    _ombak(d, 1190, c.t + 1, (25, 45, 85), amp=12)
    # termometer
    tx, ty0, ty1 = 220, 520, 1050
    d.rounded_rectangle((tx - 34, ty0, tx + 34, ty1), 34, fill=(245, 245, 245, 255), outline=GELAP + (255,), width=5)
    d.ellipse((tx - 62, ty1 - 40, tx + 62, ty1 + 84), fill=(210, 40, 30, 255), outline=GELAP + (255,), width=5)
    tinggi = lerp(ty1 - 60, ty0 + 70, panas)
    d.rounded_rectangle((tx - 16, tinggi, tx + 16, ty1), 16, fill=(210, 40, 30, 255))
    for i in range(8):
        yy = ty0 + 60 + i * 55
        d.line((tx + 34, yy, tx + 54, yy), fill=GELAP + (255,), width=4)
    angka = 2.0 * panas
    judul_besar(d, (tx + 30, ty0 - 50), f"+{angka:.1f}°C".replace(".", ","), 60, (255, 235, 150))
    s = back_out(k / 0.12)
    judul_besar(d, (640, 720), "SUPER", int(90 * s) + 1, (255, 225, 150), 1 - c.p(0.5, 0.55))
    judul_besar(d, (640, 830), "EL NIÑO", int(120 * s) + 1, PUTIH, 1 - c.p(0.5, 0.55))
    se.kartu(img, 640, 970, "Suhu laut Pasifik", "lebih dari 2°C di atas normal", MERAH,
             alpha=c.p(0.2, 0.28) * (1 - c.p(0.5, 0.55)), tiang=False)
    s2 = back_out((k - 0.55) / 0.1) if k > 0.55 else 0
    if s2 > 0:
        d = ImageDraw.Draw(img, "RGBA")
        judul_besar(d, (640, 700), "“El Niño”", int(100 * s2) + 1, PUTIH)
        judul_besar(d, (640, 800), "artinya…", int(60 * s2) + 1, (255, 235, 190))
        se.kartu(img, 640, 940, "si bayi laki-laki?", "bahasa Spanyol", MERAH, alpha=c.p(0.72, 0.8), tiang=False,
                 skala=1.3 * back_out((k - 0.72) / 0.1))
    hdr(img, alpha=c.p(0.85, 0.95))
    return img


def a_tren(c):
    kamera = se.kamera_antara(cam(PETA, 0.0, 107.5, 0.62), cam(PETA, -1.0, 107.2, 0.75), c.p(0.0, 0.7))
    img, d = peta(PETA, kamera)
    se.tint(img, (190, 140, 70), 0.25 * c.p(0.2, 0.6))
    d = ImageDraw.Draw(img, "RGBA")
    for nama, ll in LABEL_ID.items():
        x, y = layar(PETA, kamera, ll)
        label(d, (x, y), nama, 38, TINTA, 0.85)
    titik_api(d, kamera, c.t, c.p(0.3, 0.75), 0.9)
    se.kartu(img, 540, 520, "BMKG: indeks Niño 3.4 +2,76°C", "8 Oktober 2026 · El Niño sangat kuat", MERAH,
             alpha=c.p(0.02, 0.1), tiang=False)
    se.kartu(img, 540, 1230, "BRIN: kemarau bisa sampai 2027", "risiko karhutla Sumatra & Kalimantan", ORANYE,
             alpha=c.p(0.2, 0.28) * (1 - c.p(0.66, 0.7)), tiang=False, skala=back_out((c.t / c.d - 0.2) / 0.1))
    judul_besar(d, (540, 1230), "kok namanya aneh?", 64, (255, 225, 150), c.p(0.72, 0.8))
    hdr(img, "Oktober 2026")
    return img


def _label_peru(d, kamera, alpha=1.0):
    x, y = layar(PETA_SA, kamera, (-9.5, _b(-75.5)))
    label(d, (x, y), "PERU", 46, TINTA, alpha)
    x, y = layar(PETA_SA, kamera, (-1.5, _b(-78.3)))
    label(d, (x, y), "EKUADOR", 32, TINTA, alpha * 0.9)
    x, y = layar(PETA_SA, kamera, (-9.5, _b(-83.0)))
    label(d, (x, y), "Samudra Pasifik", 36, (230, 225, 210), alpha, "tangan_tipis")


def a_peru(c):
    kamera = se.kamera_antara(cam(PETA_SA, -6.0, _b(-80.5), 0.62), cam(PETA_SA, -6.5, _b(-79.5), 0.85), c.p(0.0, 0.8))
    img, d = peta(PETA_SA, kamera)
    _label_peru(d, kamera, c.p(0.0, 0.1))
    # arus hangat dari utara menyusuri pantai
    titik = [layar(PETA_SA, kamera, ll) for ll in PANTAI_PERU]
    for j in range(3):
        geser = [(x - 70 - j * 55, y) for x, y in titik]
        panah_arus(d, geser, c.p(0.25 + j * 0.05, 0.6 + j * 0.05), HANGAT, tebal=9, alpha=0.9)
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    hangat = c.p(0.3, 0.7)
    for x, y in titik:
        dl.ellipse((x - 220, y - 160, x + 40, y + 160), fill=HANGAT + (int(60 * hangat),))
    img.alpha_composite(lap.filter(ImageFilter.GaussianBlur(45)))
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(4)
    for i, (x, y) in enumerate(titik[1:6]):
        perahu(d, x - 120 + rng.uniform(-20, 20), y + 30, 0.9, c.p(0.05, 0.15), math.sin(c.t * 2 + i) * 4)
    se.kartu(img, 540, 470, "Nelayan Peru", "abad ke-19", BIRU, alpha=c.p(0.02, 0.1), tiang=False)
    se.kartu(img, 540, 1150, "Datang menjelang Natal", "arus laut hangat", HANGAT, alpha=c.p(0.3, 0.38) * (1 - c.p(0.62, 0.66)),
             tiang=False)
    se.kartu(img, 540, 1150, "El Niño = “Sang Bayi”", "merujuk ke kelahiran Yesus", MERAH, alpha=c.p(0.66, 0.72),
             tiang=False, skala=1.15 * back_out((c.t / c.d - 0.66) / 0.1))
    hdr(img, "Pantai Peru, 1800-an")
    return img


def a_ikan(c):
    kamera = Kamera(*cam(PETA_SA, -7.0, _b(-79.5), 0.95))
    img, d = peta(PETA_SA, kamera)
    _label_peru(d, kamera)
    titik = [layar(PETA_SA, kamera, ll) for ll in PANTAI_PERU]
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    for x, y in titik:
        dl.ellipse((x - 220, y - 160, x + 40, y + 160), fill=HANGAT + (60,))
    img.alpha_composite(lap.filter(ImageFilter.GaussianBlur(45)))
    d = ImageDraw.Draw(img, "RGBA")
    # kawanan ikan teri menghilang
    hilang = c.p(0.12, 0.4)
    rng = random.Random(8)
    for i in range(36):
        bx, by = titik[2 + i % 4]
        x = bx - 160 + rng.uniform(-90, 60) + math.sin(c.t * 2 + i) * 10 - hilang * 260
        y = by + rng.uniform(-80, 80)
        ikan(d, x, y, 0.8, 1 - hilang)
    if hilang >= 1:
        x, y = titik[3]
        se.teks(d, (x - 180, y), "✕", 90, MERAH, nama_font="ui", alpha=c.p(0.4, 0.46) * (1 - c.p(0.55, 0.6)))
    se.kartu(img, 540, 470, "Ikan teri menghilang", "nelayan kehilangan tangkapan", BIRU, alpha=c.p(0.08, 0.16), tiang=False)
    # hujan deras di gurun pesisir
    hj = c.p(0.5, 0.6)
    if hj > 0:
        x, y = layar(PETA_SA, kamera, (-7.5, _b(-78.0)))
        awan(img, x, y - 230, 0.75, (150, 155, 170), hj, seed=5)
        d = ImageDraw.Draw(img, "RGBA")
        hujan_lokal(d, x, y - 200, 340, 280, c.t, hj, n=50)
        label(d, (x + 30, y + 120), "gurun pesisir banjir", 38, (30, 60, 130), hj)
    se.kartu(img, 540, 1250, "1892: dilaporkan Kapten Camilo Carrillo", "ke Masyarakat Geografi Lima", (90, 70, 50),
             alpha=c.p(0.78, 0.86), tiang=False)
    hdr(img, "Kalau arusnya kuat…")
    return img


def a_kelaparan(c):
    kamera = se.kamera_antara(cam(PETA_ASIA, 25, 93, 0.6), cam(PETA_ASIA, 25, 93, 0.63), c.p(0.0, 1.0))
    img, d = peta(PETA_ASIA, kamera)
    kering = c.p(0.15, 0.5)
    se.tint(img, (170, 110, 50), 0.35 * kering)
    d = ImageDraw.Draw(img, "RGBA")
    # retakan tanah kering
    rng = random.Random(3)
    for pusat in [(22, 80), (33, 104)]:
        px_, py_ = layar(PETA_ASIA, kamera, pusat)
        for i in range(int(14 * kering)):
            x, y = px_ + rng.uniform(-150, 150), py_ + rng.uniform(-130, 130)
            pts = [(x, y)]
            for _ in range(3):
                x += rng.uniform(-30, 30)
                y += rng.uniform(-30, 30)
                pts.append((x, y))
            d.line(pts, fill=(90, 50, 20, 200), width=4)
    for nama, ll in [("INDIA", (21, 83)), ("CINA", (31, 104))]:
        x, y = layar(PETA_ASIA, kamera, ll)
        label(d, (x, y + 70), nama, 46, TINTA)
    # awan monsun yang gagal datang
    am = 1 - c.p(0.08, 0.3)
    x, y = layar(PETA_ASIA, kamera, (10, 80))
    awan(img, x + 60, y + 40 - 120 * (1 - am), 0.6, (150, 155, 170), am * 0.9, seed=6)
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out(c.t / c.d / 0.1)
    judul_besar(d, (540, 470), "1877", int(120 * s) + 1, (255, 225, 150))
    se.kartu(img, 540, 600, "Monsun gagal datang", "kemarau & kelaparan besar", COKLAT, alpha=c.p(0.2, 0.28), tiang=False)
    a = c.p(0.66, 0.74)
    se.kartu(img, 540, 1240, "Korban di seluruh dunia", "diperkirakan puluhan juta jiwa", MERAH, alpha=a, tiang=False,
             skala=1.15 * back_out((c.t / c.d - 0.66) / 0.1))
    hdr(img, "Kemarau besar 1876 – 1878")
    return img


def _barometer(d, x, y, nilai, nama, alpha=1.0):
    """Barometer bundar; nilai -1..1 = tekanan rendah..tinggi."""
    a = int(255 * alpha)
    d.ellipse((x - 85, y - 85, x + 85, y + 85), fill=(250, 245, 230, a), outline=GELAP + (a,), width=6)
    for i in range(9):
        sud = math.pi * (0.75 + i * 1.5 / 8)
        d.line((x + math.cos(sud) * 62, y + math.sin(sud) * 62, x + math.cos(sud) * 74, y + math.sin(sud) * 74),
               fill=GELAP + (a,), width=3)
    sud = math.pi * 1.5 + nilai * math.pi * 0.7
    d.line((x, y, x + math.cos(sud) * 60, y + math.sin(sud) * 60), fill=MERAH + (a,), width=7)
    d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=GELAP + (a,))
    se.teks(d, (x, y - 125), nama, 42, TINTA, nama_font="judul", alpha=alpha)


def a_walker(c):
    img, d = gradasi((60, 75, 100), (110, 125, 150))
    se.panel(img, (70, 430, 1010, 1310), alpha=c.p(0, 0.06))
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 500, "Gilbert Walker, 1904", "kepala observatorium cuaca India", BIRU, alpha=c.p(0.02, 0.1),
             tiang=False)
    a = c.p(0.3, 0.38)
    if a > 0:
        # jungkat-jungkit: miring bolak-balik
        miring = math.sin((c.t - c.d * 0.3) * 1.6) * 0.18 * a
        cx, cy = 540, 1000
        pj = 320
        dx, dy = math.cos(miring) * pj, math.sin(miring) * pj
        d.polygon([(cx, cy), (cx - 60, cy + 110), (cx + 60, cy + 110)], fill=(120, 80, 45, int(255 * a)),
                  outline=GELAP + (int(255 * a),))
        d.line((cx - dx, cy - dy, cx + dx, cy + dy), fill=(150, 100, 55, int(255 * a)), width=26)
        nilai_kiri = -miring / 0.18
        _barometer(d, cx - dx, cy - dy - 170, nilai_kiri, "DARWIN", a)
        _barometer(d, cx + dx, cy + dy - 170, -nilai_kiri, "TAHITI", a)
        se.teks(d, (cx - dx, cy - dy + 50), "Australia", 30, (100, 80, 60), nama_font="tangan_tipis", alpha=a)
        se.teks(d, (cx + dx, cy + dy + 50), "Pasifik tengah", 30, (100, 80, 60), nama_font="tangan_tipis", alpha=a)
        se.teks(d, (540, 1170), "tekanan udara naik-turun bergantian", 38, TINTA, nama_font="tangan", alpha=a)
    s = back_out((c.t / c.d - 0.72) / 0.1) if c.t / c.d > 0.72 else 0
    if s > 0:
        d = ImageDraw.Draw(img, "RGBA")
        judul_besar(d, (540, 1250), "OSILASI SELATAN", int(70 * s) + 1, (255, 225, 150), 1.0, (60, 30, 10))
    hdr(img, "Ramalan monsun India")
    return img


def a_bjerknes(c):
    img, d = gradasi((45, 60, 95), (100, 115, 150))
    k = c.t / c.d
    nyatu = c.p(0.45, 0.62)
    xa = lerp(300, 540, nyatu)
    xb = lerp(780, 540, nyatu)
    a = c.p(0.0, 0.08) * (1 - c.p(0.6, 0.64))
    se.kartu(img, xa, 760, "El Niño", "arus hangat Peru", HANGAT, alpha=a, tiang=False)
    se.kartu(img, xb, 960, "Osilasi Selatan", "jungkat-jungkit Walker", BIRU, alpha=c.p(0.08, 0.16) * (1 - c.p(0.6, 0.64)),
             tiang=False)
    d = ImageDraw.Draw(img, "RGBA")
    if nyatu <= 0:
        se.teks(d, (540, 860), "?", 110, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0),
                alpha=c.p(0.16, 0.22))
    s = back_out((k - 0.62) / 0.1) if k > 0.62 else 0
    if s > 0:
        se.glow(img, 540, 860, 320, (255, 200, 120), 0.8)
        d = ImageDraw.Draw(img, "RGBA")
        judul_besar(d, (540, 840), "ENSO", int(170 * s) + 1, (255, 225, 150), 1.0, (60, 30, 10))
        se.teks(d, (540, 960), "El Niño – Southern Oscillation", 40, PUTIH, nama_font="ui", stroke=4,
                stroke_warna=(0, 0, 0), alpha=c.p(0.68, 0.74))
    se.kartu(img, 540, 520, "Jacob Bjerknes, 1969", "ahli meteorologi, Norwegia–AS", MERAH, alpha=c.p(0.02, 0.1),
             tiang=False)
    judul_besar(d, (540, 1200), "ternyata satu fenomena!", 56, PUTIH, c.p(0.66, 0.72), (30, 40, 80))
    hdr(img, "Dua teka-teki, satu jawaban")
    return img


def a_cara(c):
    img, d = gradasi((120, 170, 220), (190, 215, 240))
    k = c.t / c.d
    e = c.p(0.45, 0.7)  # 0 = normal, 1 = El Niño
    laut_y = 900
    # laut
    d.rectangle((0, laut_y, W, 1280), fill=(40, 70, 120, 255))
    # kolam air hangat
    kiri = lerp(230, 120, e)
    kanan = lerp(60, 120, e)
    titik = [(140, laut_y)]
    for i in range(21):
        f = i / 20
        x = lerp(140, 940, f)
        dalam = lerp(kiri, kanan, f) + math.sin(f * 6 + c.t) * 6
        titik.append((x, laut_y + dalam))
    titik.append((940, laut_y))
    d.polygon(titik, fill=(215, 85, 45, 235))
    se.teks(d, (lerp(330, 540, e), laut_y + 60), "air hangat", 38, PUTIH, nama_font="tangan", stroke=4,
            stroke_warna=(80, 20, 10))
    se.teks(d, (540, 1225), "air dingin", 34, (200, 220, 245), nama_font="tangan_tipis")
    # daratan kiri-kanan
    d.polygon([(0, 820), (110, 790), (150, laut_y), (150, 1280), (0, 1280)], fill=(200, 170, 120, 255), outline=GELAP + (255,))
    d.polygon([(W, 760), (960, 800), (930, laut_y), (930, 1280), (W, 1280)], fill=(200, 170, 120, 255), outline=GELAP + (255,))
    se.teks(d, (75, 750), "INDONESIA", 26, TINTA, nama_font="judul", stroke=3, stroke_warna=KREM_LABEL)
    se.teks(d, (1000, 715), "PERU", 28, TINTA, nama_font="judul", stroke=3, stroke_warna=KREM_LABEL)
    # awan hujan berpindah
    ax = lerp(300, 720, e)
    awan(img, ax, 620, 0.7, (150, 158, 175), seed=3)
    d = ImageDraw.Draw(img, "RGBA")
    hujan_lokal(d, ax, 660, 300, 230, c.t, 1.0, n=36)
    # angin pasat
    kuat = 1 - 0.8 * e
    geser = (c.t * 160) % 220
    for i in range(4):
        x0 = 880 - i * 220 - geser
        if x0 < 180:
            continue
        pj = 140 * kuat
        d.line((x0, 845, x0 - pj, 845), fill=(255, 255, 255, int(220 * kuat)), width=6)
        d.polygon([(x0 - pj - 18, 845), (x0 - pj + 4, 833), (x0 - pj + 4, 857)], fill=(255, 255, 255, int(220 * kuat)))
    se.teks(d, (700, 795), "angin pasat", 34, (30, 50, 90), nama_font="tangan", alpha=kuat)
    if e > 0.5:
        matahari(img, 230, 560, 50, c.t, c.p(0.6, 0.72))
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (230, 690), "kering!", 40, MERAH, nama_font="caption", stroke=4, stroke_warna=PUTIH,
                alpha=c.p(0.65, 0.72))
    judul_besar(d, (540, 470), "NORMAL", 72, PUTIH, 1 - c.p(0.4, 0.45), (30, 60, 110))
    judul_besar(d, (540, 470), "EL NIÑO", 80, (255, 220, 140), c.p(0.45, 0.5), (110, 30, 10))
    hdr(img, "Cara kerjanya")
    return img


TAHUN = [(0.12, "1997–1998", "± 10 juta ha hutan terbakar", ORANYE),
         (0.42, "2015", "dijuluki “El Niño Godzilla”", MERAH),
         (0.75, "2026", "Super El Niño lagi…", (120, 40, 140))]


def a_indonesia(c):
    kamera = se.kamera_antara(cam(PETA, 0.0, 107.3, 0.72), cam(PETA, -1.0, 107.8, 0.62), c.p(0.0, 1.0))
    img, d = peta(PETA, kamera)
    se.tint(img, (190, 140, 70), 0.3 * c.p(0.05, 0.3))
    d = ImageDraw.Draw(img, "RGBA")
    for nama, ll in LABEL_ID.items():
        x, y = layar(PETA, kamera, ll)
        label(d, (x, y), nama, 36, TINTA, 0.8)
    titik_api(d, kamera, c.t, c.p(0.05, 0.4), 0.85)
    for i, (f, th, sub, warna) in enumerate(TAHUN):
        a = c.p(f, f + 0.06)
        if i < len(TAHUN) - 1:
            a *= 1 - c.p(TAHUN[i + 1][0], TAHUN[i + 1][0] + 0.04)
        se.kartu(img, 540, 500, th, sub, warna, alpha=a, tiang=False, skala=1.1 * back_out((c.t / c.d - f) / 0.1))
    judul_besar(d, (540, 1240), "kemarau + kebakaran hutan", 52, (255, 225, 150), c.p(0.05, 0.12))
    hdr(img, "Dampaknya ke Indonesia")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(PETA, -1.0, 108.5, 0.62))
    img, d = peta(PETA, kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1060), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Namanya dari nelayan Peru", 50, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 645), "dampaknya sampai ke kita", 40, (90, 70, 50), alpha=a)
        perahu(d, 330, 820, 1.6, a, math.sin(c.t * 2) * 5)
        matahari(img, 740, 800, 60, c.t, a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1000), "hemat air, jangan bakar lahan", 42, (150, 40, 30), nama_font="caption", alpha=a)
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
    Adegan("hook", "Lagi rame Super El Nino, suhu laut Pasifik naik lebih dari dua derajat. "
                   "Tapi tahu nggak, El Nino itu artinya… si bayi laki-laki?", a_hook, transisi=False),
    Adegan("tren", "BRIN mengingatkan, kemarau bisa panjang, dan kebakaran hutan mengintai. "
                   "Terus, kenapa namanya aneh gitu?", a_tren),
    Adegan("peru", "Dari nelayan Peru, abad kesembilan belas. Tiap menjelang Natal, arus laut hangat datang "
                   "ke pantai mereka. Mereka menyebutnya El Nino, merujuk ke kelahiran Yesus.", a_peru),
    Adegan("ikan", "Kalau arusnya kuat, ikan teri menghilang, dan hujan deras mengguyur gurun pesisir.", a_ikan),
    Adegan("kelaparan", "Tapi dampaknya sampai ke Asia. Tahun delapan belas tujuh puluh tujuh, monsun gagal. "
                        "Kelaparan melanda India dan Cina. Di seluruh dunia, korbannya diperkirakan puluhan juta jiwa.",
           a_kelaparan),
    Adegan("walker", "Tahun sembilan belas nol empat, ilmuwan Inggris Gilbert Walker ditugaskan meramal monsun India. "
                     "Dia menemukan jungkat-jungkit raksasa. Tekanan udara di Darwin naik, di Tahiti turun. "
                     "Namanya, Osilasi Selatan.", a_walker),
    Adegan("bjerknes", "Tahun sembilan belas enam puluh sembilan, Jacob Bjerknes sadar. Arus hangat Peru, "
                       "dan jungkat-jungkit Walker, ternyata satu fenomena.", a_bjerknes),
    Adegan("cara", "Biasanya, angin pasat mendorong air hangat ke arah kita, jadi awan hujan numpuk di Indonesia. "
                   "Pas El Nino, anginnya melemah. Air hangat dan awan hujan pindah ke timur.", a_cara),
    Adegan("indonesia", "Makanya El Nino kuat sering bawa kemarau dan kebakaran hutan. Kayak tahun sembilan belas "
                        "sembilan puluh tujuh, dan dua ribu lima belas, si El Nino Godzilla.", a_indonesia),
    Adegan("penutup", "Jadi, nama El Nino lahir dari nelayan Peru, tapi dampaknya sampai ke kita. "
                      "Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
