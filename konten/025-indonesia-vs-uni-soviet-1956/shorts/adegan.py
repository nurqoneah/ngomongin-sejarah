"""Shorts ±88 detik: Indonesia 0–0 Uni Soviet, Olimpiade Melbourne 1956 — dan kiper yang hidupnya lebih dramatis.

Visual: (1) ilustrasi stadion malam + papan skor, (2) peta Nusantara–Australia (rute Jakarta → Melbourne),
(3) lapangan tampak atas dengan pemain berupa titik, (4) papan skor & medali, (5) kartu tokoh tanpa wajah.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "indonesia-vs-uni-soviet-1956-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "TIMNAS VS UNI SOVIET"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
ORANYE = (235, 120, 25)
HIJAU_LAP = (46, 125, 60)
SOVIET = (150, 25, 25)
BIRU = (30, 80, 150)
ABU = (60, 60, 70)
EMAS_T = (255, 214, 120)
PUTIH_KAOS = (240, 240, 245)

# ------------------------------------------------------------------ peta Nusantara – Australia (disederhanakan)

AUSTRALIA_PENUH = [(-12.4, 130.8), (-14.9, 128.4), (-14, 126), (-16.4, 123), (-18, 122.2), (-19.9, 119),
                   (-20.5, 116.7), (-22, 114), (-24.9, 113.6), (-27.7, 114.1), (-31.9, 115.7), (-34.3, 115.1),
                   (-35, 117.9), (-33.9, 123.6), (-31.7, 128.9), (-31.5, 131.1), (-32.0, 133.6), (-33.0, 134.3),
                   (-34.7, 135.8), (-33.0, 137.6), (-35.6, 138.1), (-36.0, 139.6), (-37.6, 140.5), (-38.4, 142.0),
                   (-38.8, 143.5), (-38.3, 144.5), (-38.5, 145.4), (-39.1, 146.4), (-37.8, 148.0), (-37.5, 150.0),
                   (-35.0, 150.8), (-33.8, 151.3), (-32.5, 152.5), (-28.2, 153.6), (-25.0, 152.8), (-23.0, 150.8),
                   (-20.0, 148.7), (-19.2, 146.8), (-16.9, 145.8), (-14.5, 144.5), (-14.0, 143.5), (-10.7, 142.5),
                   (-12.5, 141.6), (-14.0, 141.5), (-17.5, 140.8), (-16.5, 139.2), (-15.0, 135.5), (-12.3, 136.8),
                   (-11.5, 132.6)]
TASMANIA = [(-40.8, 144.7), (-41.0, 148.3), (-43.2, 148.0), (-43.6, 146.8), (-42.5, 145.3)]
PNG = [(-1.0, 139.5), (-2.6, 141.0), (-3.3, 143.5), (-4.2, 145.8), (-5.6, 147.5), (-6.8, 147.8), (-8.0, 148.2),
       (-10.2, 150.5), (-10.5, 149.8), (-9.0, 146.5), (-7.6, 144.0), (-9.1, 143.2), (-9.2, 139.5)]
DARAT = [pd.ASIA_AFRIKA, pd.FILIPINA, AUSTRALIA_PENUH, TASMANIA, PNG] + pd.INDONESIA

print("  menyiapkan peta Nusantara–Australia...")
PETA = Peta(92, 158, -46, 12, 40, [], [(-2, 114, 1.5), (0, 101, 1.2), (-2, 121, 1.2), (-30, 148, 3),
                                        (-23, 133, 4), (-4, 138, 1.5)], seed=25, darat=DARAT)

JAKARTA = (-6.2, 106.8)
MELBOURNE = (-37.81, 144.96)
RUTE = [JAKARTA, (-8.5, 112.0), (-12.0, 120.0), (-16.0, 127.0), (-22.0, 133.0), (-29.0, 139.0), (-34.5, 143.0),
        MELBOURNE]

# lapangan tampak atas
LX0, LX1, LY0, LY1 = 120, 960, 420, 1300
GAWANG_ATAS = (540, LY0)
GAWANG_BAWAH = (540, LY1)


# ------------------------------------------------------------------ helper

def cam(lat, lon, zoom):
    x, y = PETA.px(lat, lon)
    return (x, y, zoom)


def peta(kamera):
    img = se.render_peta(PETA, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(kamera, ll):
    return kamera.layar(*PETA.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def hdr(img, sub="Olimpiade Melbourne 1956", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def pop(c, a):
    return back_out((c.t / c.d - a) / 0.1)


def bola(d, x, y, r, putar=0.0, alpha=1.0):
    """Bola kulit klasik: lingkaran krem + jahitan."""
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(205, 150, 85, a), outline=(60, 35, 15, a), width=max(2, int(r * 0.08)))
    for k in range(3):
        ang = putar + k * math.pi / 3
        dx, dy = math.cos(ang) * r * 0.92, math.sin(ang) * r * 0.92
        d.line((x - dx, y - dy, x + dx, y + dy), fill=(90, 55, 25, a), width=max(2, int(r * 0.06)))
    d.ellipse((x - r * 0.55, y - r * 0.7, x - r * 0.1, y - r * 0.35), fill=(255, 230, 190, int(90 * alpha)))


def langit_malam():
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    atas = np.array((10, 14, 30), np.float32)
    bawah = np.array((40, 45, 70), np.float32)
    arr = (atas * (1 - g) + bawah * g).repeat(W, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")


_LANGIT = None


def stadion(t, tribun_kedip=True):
    """Ilustrasi stadion malam: tribun, lampu sorot, lapangan perspektif."""
    global _LANGIT
    if _LANGIT is None:
        _LANGIT = langit_malam()
    img = _LANGIT.copy()
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(0, 700), (W, 700), (W, 1080), (0, 1080)], fill=(35, 30, 40, 255))
    rng = random.Random(4)
    for i in range(700):
        x, y = rng.uniform(0, W), rng.uniform(720, 1070)
        col = rng.choice([(200, 190, 170), (150, 140, 130), (230, 140, 60), (120, 110, 100)])
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=col + (200,))
    d.polygon([(260, 1080), (820, 1080), (W + 260, H), (-260, H)], fill=HIJAU_LAP + (255,))
    for k in range(8):
        y0 = 1080 + (H - 1080) * (k / 8) ** 1.4
        y1 = 1080 + (H - 1080) * ((k + 0.5) / 8) ** 1.4
        f0, f1 = (y0 - 1080) / (H - 1080), (y1 - 1080) / (H - 1080)
        d.polygon([(260 - 520 * f0, y0), (820 + 520 * f0, y0), (820 + 520 * f1, y1), (260 - 520 * f1, y1)],
                  fill=(56, 140, 70, 255))
    d.line((260, 1080, -260, H), fill=(240, 240, 240, 220), width=6)
    d.line((820, 1080, W + 260, H), fill=(240, 240, 240, 220), width=6)
    d.line((260, 1082, 820, 1082), fill=(240, 240, 240, 220), width=5)
    d.ellipse((540 - 300, 1380 - 70, 540 + 300, 1380 + 70), outline=(240, 240, 240, 200), width=6)
    for lx in (120, 960):
        d.rectangle((lx - 6, 420, lx + 6, 700), fill=(70, 70, 80, 255))
        d.rectangle((lx - 70, 380, lx + 70, 440), fill=(220, 220, 200, 255), outline=(60, 60, 70, 255), width=4)
        se.glow(img, lx, 410, 260, (255, 245, 200), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    if tribun_kedip:
        rk = random.Random(int(t * 8))
        for _ in range(6):
            x, y = rk.uniform(30, W - 30), rk.uniform(730, 1060)
            d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(255, 255, 255, 230))
    return img


def papan(d, y0, kiri, kanan, sk_kiri, sk_kanan, menit="", alpha=1.0, merah_kanan=True):
    """Papan skor besar: nama tim kiri/kanan + angka."""
    a = int(255 * alpha)
    d.rounded_rectangle((70, y0, 1010, y0 + 330), 26, fill=(15, 15, 18, int(245 * alpha)),
                        outline=(200, 200, 200, a), width=6)
    se.teks(d, (290, y0 + 60), kiri, 46, PUTIH, nama_font="ui", alpha=alpha)
    se.teks(d, (790, y0 + 60), kanan, 46, (255, 120, 110) if merah_kanan else PUTIH, nama_font="ui", alpha=alpha)
    se.teks(d, (290, y0 + 200), str(sk_kiri), 190, (255, 200, 60), nama_font="caption", alpha=alpha)
    se.teks(d, (540, y0 + 200), "–", 150, PUTIH, nama_font="caption", alpha=alpha)
    se.teks(d, (790, y0 + 200), str(sk_kanan), 190, (255, 200, 60), nama_font="caption", alpha=alpha)
    if menit:
        d.rounded_rectangle((430, y0 - 36, 650, y0 + 22), 16, fill=(200, 52, 44, a))
        se.teks(d, (540, y0 - 7), menit, 40, PUTIH, nama_font="ui", alpha=alpha)


def kiper_terbang(d, x, y, s=1.0, ang=-25, warna=(30, 30, 35), alpha=1.0):
    """Siluet kiper melompat (tanpa wajah): badan miring, lengan terulur, sarung tangan."""
    a = int(255 * alpha)
    r = math.radians(ang)
    ca, sa = math.cos(r), math.sin(r)

    def p(px, py):
        return (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)

    badan = [p(-90, -28), p(60, -32), p(60, 32), p(-90, 28)]
    d.polygon(badan, fill=warna + (a,), outline=(10, 10, 10, a), width=max(2, int(5 * s)))
    d.ellipse(_kotak(p(90, 0), 26 * s), fill=warna + (a,))
    for dy in (-22, 22):  # lengan
        d.line([p(110, dy * 0.6), p(200, dy)], fill=warna + (a,), width=max(4, int(22 * s)))
        gx, gy = p(212, dy)
        d.ellipse(_kotak((gx, gy), 20 * s), fill=(235, 235, 235, a), outline=(20, 20, 20, a), width=3)
    for dy in (-18, 18):  # kaki
        d.line([p(-88, dy), p(-200, dy * 2.2)], fill=warna + (a,), width=max(4, int(26 * s)))


def _kotak(c, r):
    return (c[0] - r, c[1] - r, c[0] + r, c[1] + r)


def lapangan(img, alpha=1.0):
    """Lapangan tampak atas; gawang Indonesia di atas, gawang Soviet di bawah."""
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rounded_rectangle((LX0 - 30, LY0 - 40, LX1 + 30, LY1 + 40), 20, fill=(30, 90, 45, 255))
    n = 10
    for i in range(n):
        y0 = LY0 + (LY1 - LY0) * i / n
        y1 = LY0 + (LY1 - LY0) * (i + 1) / n
        d.rectangle((LX0, y0, LX1, y1), fill=(52, 135, 66, 255) if i % 2 else (46, 122, 60, 255))
    g = (240, 240, 240, 230)
    d.rectangle((LX0, LY0, LX1, LY1), outline=g, width=5)
    my = (LY0 + LY1) / 2
    d.line((LX0, my, LX1, my), fill=g, width=5)
    d.ellipse((540 - 95, my - 95, 540 + 95, my + 95), outline=g, width=5)
    for gy, arah in ((LY0, 1), (LY1, -1)):
        d.rectangle((330, min(gy, gy + 150 * arah), 750, max(gy, gy + 150 * arah)), outline=g, width=5)
        d.rectangle((440, min(gy, gy + 55 * arah), 640, max(gy, gy + 55 * arah)), outline=g, width=5)
        d.rectangle((470, min(gy, gy - 26 * arah), 610, max(gy, gy - 26 * arah)), fill=(250, 250, 250, 255),
                    outline=(120, 120, 120, 255), width=3)
    se.tempel(img, lap, alpha)


def titik_pemain(d, x, y, warna, r=22, alpha=1.0, teks=""):
    a = int(255 * alpha)
    d.ellipse((x - r + 3, y - r + 5, x + r + 3, y + r + 5), fill=(0, 0, 0, int(80 * alpha)))
    d.ellipse((x - r, y - r, x + r, y + r), fill=warna + (a,), outline=(20, 15, 10, a), width=4)
    if teks:
        se.teks(d, (x, y - r - 26), teks, 32, PUTIH, nama_font="caption", stroke=5, stroke_warna=(0, 0, 0),
                alpha=alpha)


def medali(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.polygon([(x - 50 * s, y - 210 * s), (x - 10 * s, y - 210 * s), (x + 15 * s, y - 60 * s), (x - 25 * s, y - 60 * s)],
              fill=(190, 40, 40, a))
    d.polygon([(x + 50 * s, y - 210 * s), (x + 10 * s, y - 210 * s), (x - 15 * s, y - 60 * s), (x + 25 * s, y - 60 * s)],
              fill=(30, 70, 150, a))
    d.ellipse(_kotak((x, y), 85 * s), fill=(235, 185, 50, a), outline=(140, 95, 20, a), width=max(3, int(8 * s)))
    d.ellipse(_kotak((x, y), 58 * s), outline=(255, 225, 120, a), width=max(2, int(5 * s)))
    se.teks(d, (x, y + 4 * s), "1", int(70 * s) + 1, (140, 95, 20), nama_font="caption", alpha=alpha)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = stadion(c.t)
    se.tint(img, (8, 6, 4), 0.2)
    d = ImageDraw.Draw(img, "RGBA")
    # judul besar langsung tampil di detik 0
    s = 1 + 0.03 * math.sin(c.t * 6)
    se.teks(d, (540, 470), "SOVIET 0–0", int(150 * s), PUTIH, nama_font="caption", stroke=11,
            stroke_warna=(20, 10, 5))
    se.teks(d, (540, 620), "INDONESIA", int(150 * s), (255, 120, 100), nama_font="caption", stroke=11,
            stroke_warna=(20, 10, 5))
    # kiper melompat menepis bola
    k = clamp(c.t / c.d)
    kx = 540 + 40 * math.sin(c.t * 1.5)
    kiper_terbang(d, kx - 120, 1200 - 30 * k, 1.35, ang=-20, warna=(230, 195, 40))
    bx, by = kx + 200, 1070 - 40 * k + math.sin(c.t * 9) * 6
    bola(d, bx, by, 46, c.t * 4)
    se.glow(img, bx, by, 120, (255, 240, 200), 0.5 + 0.3 * math.sin(c.t * 10))
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.3, 0.38)
    if a > 0:
        se.kartu(img, 540, 800, "120 menit · nol gol", "lawan juara Olimpiade", MERAH, alpha=a, tiang=False,
                 skala=pop(c, 0.3))
    hdr(img, alpha=c.p(0.85, 0.97))
    return img


def a_tren(c):
    kamera = Kamera(*cam(-2.5, 114, 0.95))
    img, d = peta(kamera)
    se.tint(img, (10, 6, 0), 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    a1 = c.p(0.02, 0.1) * (1 - c.p(0.45, 0.5))
    se.kartu(img, 540, 640, "Lagi rame: naturalisasi", "Taisei Marukawa buat Timnas", ABU, alpha=a1, tiang=False,
             skala=pop(c, 0.02))
    k = c.p(0.47, 0.85)
    tahun = int(round(lerp(2026, 1956, k)))
    se.teks(d, (540, 820), str(tahun), 200, EMAS_T, nama_font="caption", stroke=12, stroke_warna=(30, 15, 5),
            alpha=c.p(0.45, 0.52))
    se.teks(d, (540, 960), "70 tahun lalu…", 56, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=c.p(0.8, 0.88))
    bola(d, 540, 1130, 60 * c.p(0.8, 0.9) + 1, c.t * 3, alpha=c.p(0.8, 0.88))
    hdr(img, "Lagi rame: Timnas")
    return img


def a_melbourne(c):
    k = c.p(0.05, 0.6)
    titik_px = [PETA.px(*ll) for ll in RUTE]
    pos, _ = se.titik_di_jalur(titik_px, k)
    kamera = Kamera(pos[0], pos[1] + 120, 0.95)
    img, d = peta(kamera)
    pts = [kamera.layar(*p) for p in titik_px]
    se.garis_putus(d, pts, k, (150, 30, 20), tebal=7, putus=16, celah=10, panah=True)
    for nama, ll in {"Jakarta": JAKARTA, "Melbourne": MELBOURNE}.items():
        x, y = layar(kamera, ll)
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(200, 40, 30, 255), outline=(255, 255, 255, 255), width=3)
        label(d, (x, y + 48), nama, 42, TINTA)
    for nama, ll in {"AUSTRALIA": (-25, 134), "INDONESIA": (-1.0, 113.5)}.items():
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 46, (90, 60, 30), 0.9)
    se.kartu(img, 540, 600, "Olimpiade Melbourne", "November 1956", EMAS_T, alpha=c.p(0.05, 0.12), tiang=False,
             skala=pop(c, 0.05))
    a = c.p(0.55, 0.62)
    if a > 0:
        se.kartu(img, 540, 1060, "Lawan pertama: Vietnam", "mundur", ABU, alpha=a, tiang=False, skala=pop(c, 0.55),
                 coret=c.p(0.62, 0.72))
        se.kartu(img, 540, 1230, "Langsung ke perempat final!", "", (30, 130, 60), alpha=c.p(0.75, 0.82),
                 tiang=False, skala=pop(c, 0.75))
    hdr(img, "Jakarta → Melbourne")
    return img


def a_lawan(c):
    img = stadion(c.t, tribun_kedip=False)
    se.tint(img, (40, 5, 5), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    sk = pop(c, 0.0)
    se.teks(d, (540, 520), "UNI SOVIET", int(140 * sk) + 1, (255, 90, 80), nama_font="caption", stroke=11,
            stroke_warna=(20, 5, 5))
    se.kartu(img, 540, 690, "Salah satu tim terkuat dunia", "", SOVIET, alpha=c.p(0.08, 0.15), tiang=False,
             skala=pop(c, 0.08))
    a = c.p(0.4, 0.48)
    if a > 0:
        # siluet kiper berdiri (tanpa wajah)
        x, y = 540, 980
        s = pop(c, 0.4)
        d.ellipse(_kotak((x, y - 150 * s), 42 * s), fill=(15, 15, 18, int(255 * a)))
        d.rounded_rectangle((x - 70 * s, y - 105 * s, x + 70 * s, y + 60 * s), int(20 * s), fill=(15, 15, 18, int(255 * a)))
        for sx in (-1, 1):
            d.line((x + 66 * sx * s, y - 90 * s, x + 150 * sx * s, y - 180 * s), fill=(15, 15, 18, int(255 * a)),
                   width=max(4, int(30 * s)))
            d.ellipse(_kotak((x + 160 * sx * s, y - 192 * s), 26 * s), fill=(235, 235, 235, int(255 * a)),
                      outline=(10, 10, 10, int(255 * a)), width=3)
        se.kartu(img, 540, 1180, "Kiper: Lev Yashin", "kiper legendaris", (20, 20, 25), alpha=c.p(0.5, 0.58),
                 tiang=False, skala=pop(c, 0.5))
    hdr(img, "Perempat final")
    return img


FORMASI_IDN = [(540, 470), (380, 560), (540, 580), (700, 560), (300, 700), (450, 690), (630, 690), (780, 700),
               (380, 880), (540, 960), (700, 880)]


def a_taktik(c):
    img = Image.new("RGBA", (W, H), (25, 30, 28, 255))
    lapangan(img)
    d = ImageDraw.Draw(img, "RGBA")
    k = c.p(0.2, 0.5)
    for i, (x, y) in enumerate(FORMASI_IDN):
        if i == 0:
            titik_pemain(d, x, y, (230, 200, 40), 24)
            continue
        # pemain bertahan ditarik ke tengah (2 bek → lini tengah)
        if i in (1, 3):
            x, y = lerp(x, 420 if i == 1 else 660, k), lerp(y, 690, k)
        if i in (4, 7):
            y = lerp(y, 640, k)
        if i == 9:
            titik_pemain(d, x, y, MERAH, 26, teks="RAMANG" if c.p(0.6, 0.68) > 0 else "",
                         alpha=1.0)
            continue
        titik_pemain(d, x, y, MERAH, 24)
    g = c.p(0.35, 0.5)
    if g > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((230, 520, 850, 760), 40, outline=(255, 220, 80, 255), width=8)
        se.tempel(img, lap, g * 0.9)
        d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.62, 0.7)
    if a > 0:
        se.garis_putus(d, [(540, 960), (560, 1100), (540, 1250)], c.p(0.65, 0.85), (255, 220, 80), tebal=8,
                       putus=18, celah=10, panah=True)
    se.kartu(img, 540, 1150, "Pelatih: Toni Pogacnik", "dari Yugoslavia", BIRU,
             alpha=c.p(0.02, 0.1) * (1 - c.p(0.33, 0.38)), tiang=False, skala=pop(c, 0.02))
    se.kartu(img, 540, 1150, "Pertahanan digembok rapat", "", MERAH, alpha=c.p(0.38, 0.45) * (1 - c.p(0.58, 0.62)), tiang=False,
             skala=pop(c, 0.38))
    hdr(img, "Rencana nekat")
    return img


TEMBAKAN = [(300, 760), (760, 720), (540, 820), (420, 700), (680, 780)]


def a_gempur(c):
    img = Image.new("RGBA", (W, H), (25, 30, 28, 255))
    lapangan(img)
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(9)
    maju = c.p(0.0, 0.3)
    # pemain Soviet bergerak naik
    for i in range(10):
        x0, y0 = rng.uniform(200, 880), rng.uniform(950, 1250)
        x1, y1 = rng.uniform(250, 830), rng.uniform(640, 900)
        x = lerp(x0, x1, maju) + math.sin(c.t * 2 + i) * 12
        y = lerp(y0, y1, maju)
        titik_pemain(d, x, y, PUTIH_KAOS, 22)
    for i, (x, y) in enumerate(FORMASI_IDN[1:9]):
        titik_pemain(d, x + math.sin(c.t * 2.5 + i) * 8, min(y, 720), MERAH, 22)
    # tembakan beruntun, kiper menepis
    n = len(TEMBAKAN)
    fase = c.p(0.15, 0.62) * n
    i = min(int(fase), n - 1)
    f = fase - int(fase) if fase < n else 1.0
    sx, sy = TEMBAKAN[i]
    tx = 540 + (sx - 540) * 0.35
    kx = lerp(540, tx, clamp(f * 1.6))
    titik_pemain(d, kx, 470, (230, 200, 40), 26)
    if 0 < c.p(0.15, 0.62) < 1:
        bx, by = lerp(sx, tx, clamp(f * 1.4)), lerp(sy, 470, clamp(f * 1.4))
        if f > 0.72:  # bola memantul keluar
            q = (f - 0.72) / 0.28
            bx, by = tx + (tx - 540) * q * 1.5 + 60 * q, 470 + 120 * q
        bola(d, bx, by, 18, c.t * 8)
        if 0.66 < f < 0.85:
            se.teks(d, (tx, 400), "TEPIS!", 64, (255, 220, 80), nama_font="caption", stroke=6, stroke_warna=(0, 0, 0))
    se.kartu(img, 540, 1060, f"Tembakan ke-{i + 1} … mentok", "", SOVIET, alpha=c.p(0.15, 0.22) * (1 - c.p(0.6, 0.64)),
             tiang=False)
    # re-hook
    a = c.p(0.66, 0.74)
    if a > 0:
        se.tint(img, (0, 0, 0), 0.45 * a)
        d = ImageDraw.Draw(img, "RGBA")
        titik_pemain(d, kx, 470, (230, 200, 40), 30)
        se.glow(img, kx, 470, 140, (255, 230, 120), 0.8 * a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 760), "Ingat kiper ini.", 80, PUTIH, nama_font="caption", stroke=8, stroke_warna=(0, 0, 0),
                alpha=a)
        se.teks(d, (540, 870), "Nanti kita balik ke dia…", 54, EMAS_T, nama_font="caption", stroke=6,
                stroke_warna=(0, 0, 0), alpha=c.p(0.78, 0.85))
    hdr(img, "Soviet menggempur")
    return img


def a_ramang(c):
    img = Image.new("RGBA", (W, H), (25, 30, 28, 255))
    lapangan(img)
    d = ImageDraw.Draw(img, "RGBA")
    jalur = [(540, 800), (600, 920), (520, 1020), (590, 1110), (560, 1170)]
    k = c.p(0.08, 0.5)
    (rx, ry), _ = se.titik_di_jalur(jalur, k)
    # dua bek Soviet yang dilewati
    for j, (bx, by, kapan) in enumerate(((560, 950, 0.25), (540, 1070, 0.42))):
        lewat = c.p(kapan, kapan + 0.08)
        titik_pemain(d, bx - 70 * lewat * (1 if j == 0 else -1), by + 10 * lewat, PUTIH_KAOS, 22)
        if lewat > 0.3:
            se.teks(d, (bx + (110 if j == 0 else -110), by), "lewat!", 36, EMAS_T, nama_font="caption", stroke=4,
                    stroke_warna=(0, 0, 0), alpha=1 - c.p(kapan + 0.12, kapan + 0.2))
    # Yashin di gawang bawah
    tembak = c.p(0.5, 0.62)
    yx = lerp(540, 600, tembak)
    titik_pemain(d, yx, 1255, (25, 25, 30), 26, teks="YASHIN" if c.p(0.5, 0.55) > 0 else "")
    titik_pemain(d, rx, ry, MERAH, 26, teks="RAMANG")
    if tembak <= 0:
        bola(d, rx + 18, ry + 20, 14, c.t * 8)
    elif tembak < 1:
        bola(d, lerp(rx, 610, tembak), lerp(ry, 1262, tembak), 14, c.t * 8)
    else:
        bola(d, 660, 1230 - 60 * c.p(0.62, 0.7), 14, c.t * 8)
        se.teks(d, (790, 1180), "ujung jari!", 46, EMAS_T, nama_font="caption", stroke=5, stroke_warna=(0, 0, 0),
                alpha=1 - c.p(0.72, 0.78))
    a = c.p(0.74, 0.8)
    if a > 0:
        se.teks(d, (540, 700), "84'", int(170 * pop(c, 0.74)) + 1, PUTIH, nama_font="caption", stroke=10,
                stroke_warna=MERAH, alpha=a)
        se.kartu(img, 540, 540, "Hampir gol!", "", MERAH, alpha=a, tiang=False, skala=pop(c, 0.76))
    hdr(img, "Serangan balik")
    return img


def a_skor(c):
    img = stadion(c.t)
    se.tint(img, (8, 6, 4), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    k1 = c.p(0.0, 0.25)
    k2 = c.p(0.3, 0.5)
    menit = int(lerp(1, 90, k1)) if k2 <= 0 else int(lerp(90, 120, k2))
    papan(d, 450, "UNI SOVIET", "INDONESIA", 0, 0, f"{menit}'")
    if 0.5 > c.t / c.d > 0.27:
        se.teks(d, (540, 870), "perpanjangan waktu", 56, EMAS_T, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0))
    se.kartu(img, 540, 1000, "Adu penalti? Belum ada", "", ABU, alpha=c.p(0.55, 0.62), tiang=False, skala=pop(c, 0.55))
    a = c.p(0.75, 0.82)
    if a > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((170, 1110, 910, 1270), 24, outline=(220, 60, 40, 255), width=12)
        dl.text((540, 1190), "LAGA DIULANG", font=se.font("caption", 70), fill=(220, 60, 40, 255), anchor="mm")
        lap = lap.rotate(-6 * pop(c, 0.75), center=(540, 1190))
        se.tempel(img, lap, a)
    hdr(img, "29 November 1956")
    return img


def a_ulang(c):
    img = stadion(c.t, tribun_kedip=False)
    se.tint(img, (8, 6, 4), 0.45)
    d = ImageDraw.Draw(img, "RGBA")
    a0 = 1 - c.p(0.5, 0.56)
    if a0 > 0:
        n = min(4, int(c.p(0.08, 0.45) * 4 + 0.0001))
        papan(d, 470, "UNI SOVIET", "INDONESIA", n, 0, "laga ulang", alpha=a0)
        se.kartu(img, 540, 970, "1 Desember 1956", "dua hari kemudian", ABU, alpha=c.p(0.02, 0.1) * a0, tiang=False)
    b = c.p(0.55, 0.63)
    if b > 0:
        medali(d, 540, 760, 1.6 * pop(c, 0.55), b)
        se.kartu(img, 540, 1050, "Uni Soviet juara Olimpiade", "medali emas 1956", SOVIET, alpha=c.p(0.62, 0.7),
                 tiang=False, skala=pop(c, 0.62))
    hdr(img, "Laga ulang")
    return img


def a_saelan(c):
    img = stadion(c.t, tribun_kedip=False)
    se.tint(img, (8, 6, 4), 0.62)
    d = ImageDraw.Draw(img, "RGBA")
    # siluet kiper + sarung tangan
    a = c.p(0.0, 0.08)
    kiper_terbang(d, 500, 560, 1.0 * pop(c, 0.0), ang=-12, warna=(230, 195, 40), alpha=a)
    se.glow(img, 540, 560, 260, (255, 220, 140), 0.35 * a)
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 760, "Maulwi Saelan", "kiper & kapten Timnas · dari Makassar", MERAH, alpha=c.p(0.08, 0.16),
             tiang=False, skala=pop(c, 0.08) * 1.15)
    fakta = [(0.28, "Seorang tentara", "Polisi Militer"),
             (0.42, "Wakil Komandan Tjakrabirawa", "pasukan pengawal Presiden Sukarno"),
             (0.68, "Ketua PSSI", "1964 – 1967")]
    for i, (t0, judul, sub) in enumerate(fakta):
        se.kartu(img, 540, 920 + i * 140, judul, sub, (60, 50, 40) if i != 1 else (150, 30, 20),
                 alpha=c.p(t0, t0 + 0.07), tiang=False, skala=pop(c, t0))
    hdr(img, "Siapa kiper itu?")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    img = stadion(c.t, tribun_kedip=False)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1000), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Raksasa dunia pernah keringetan", 44, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 650), "Soviet 0 – 0 Indonesia", 56, (170, 30, 20), nama_font="caption", alpha=a)
        bola(d, 540, 810, 90, c.t * 2, a)
        se.teks(d, (540, 950), "Semoga sejarah itu terulang!", 40, (90, 70, 50), alpha=a)
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
    Adegan("hook", "Timnas pernah bikin juara Olimpiade frustrasi. Seratus dua puluh menit, nggak kebobolan. "
                   "Dan kipernya? Hidupnya lebih dramatis lagi.", a_hook, transisi=False),
    Adegan("tren", "Lagi rame naturalisasi Taisei Marukawa? Tujuh puluh tahun lalu, Timnas udah bikin dunia melongo.",
           a_tren),
    Adegan("melbourne", "November sembilan belas lima puluh enam, Olimpiade Melbourne, Australia. Lawan pertama, "
                        "Vietnam, mundur. Kita langsung ke perempat final.", a_melbourne),
    Adegan("lawan", "Lawan berikutnya, Uni Soviet. Salah satu tim terkuat dunia, dengan kiper legendaris, Lev Yashin.",
           a_lawan),
    Adegan("taktik", "Pelatih kita, Toni Pogacnik dari Yugoslavia, nekat. Bek ditarik ke tengah, pertahanan digembok "
                     "rapat. Serangan balik, diserahkan ke Ramang.", a_taktik),
    Adegan("gempur", "Soviet menggempur terus. Tapi semua tembakan mentok di tangan kiper kita. Ingat kiper ini, ya.",
           a_gempur),
    Adegan("ramang", "Ramang juga bikin repot. Dia lewati dua pemain, sampai Yashin menepis pakai ujung jari. "
                     "Menit delapan puluh empat, hampir gol!", a_ramang),
    Adegan("skor", "Sembilan puluh menit, nol-nol. Perpanjangan waktu, tetap nol-nol. Belum ada adu penalti. "
                   "Jadi, laga diulang.", a_skor),
    Adegan("ulang", "Dua hari kemudian, Soviet menang empat-nol, lalu pulang bawa medali emas.", a_ulang),
    Adegan("saelan", "Terus, siapa kiper tadi? Maulwi Saelan, kapten tim dari Makassar, seorang tentara. Belakangan, "
                     "dia jadi wakil komandan Cakrabirawa, pengawal Presiden Sukarno. Dan sempat jadi Ketua PSSI.",
           a_saelan),
    Adegan("penutup", "Jadi, Timnas pernah bikin raksasa dunia keringetan. Siapa tahu, terulang lagi. "
                      "Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
