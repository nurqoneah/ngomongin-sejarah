"""Shorts ±90 detik: Sejarah Hujan Buatan (1946 – sekarang).

Pemicu: video viral bongkahan es (diduga dry ice OMC) merusak atap rumah di Palembang, Okt 2026.
Ilustrasi langit (pesawat, awan, lab) + peta Asia Tenggara.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import EMAS, MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "sejarah-hujan-buatan-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "HUJAN BUATAN"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU = (40, 100, 170)
BIRU_ES = (200, 230, 255)
ABU = (90, 95, 105)
GELAP = (25, 20, 15)

print("  menyiapkan peta Asia Tenggara...")
PETA = Peta(90, 125, -12, 22, 100, [], [(-2, 114, 1.5), (0, 101, 1.2), (5, 117, 1.0), (18, 101, 3), (14, 106, 2)],
            seed=21, darat=pd.SEMUA)

PALEMBANG = (-2.99, 104.76)
JAKARTA = (-6.2, 106.8)
BANGKOK = (13.75, 100.5)
JATILUHUR = (-6.52, 107.38)
LABEL_ID = {"SUMATRA": (-0.3, 101.3), "KALIMANTAN": (-0.8, 113.3), "JAWA": (-7.2, 110.0)}


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


def judul_besar(d, xy, isi, uk, warna=PUTIH, alpha=1.0, stroke=(0, 0, 0)):
    se.teks(d, xy, isi, uk, warna, nama_font="caption", stroke=max(5, uk // 14), stroke_warna=stroke, alpha=alpha)


def hdr(img, sub="1946 – sekarang", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def langit(atas=(95, 150, 210), bawah=(200, 220, 240)):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (np.array(atas, np.float32) * (1 - g) + np.array(bawah, np.float32) * g).repeat(W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    return img, ImageDraw.Draw(img, "RGBA")


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


def pesawat(d, x, y, s=1.0, a=1.0, putar=0.0):
    """Pesawat baling-baling tampak samping, menghadap kanan."""
    aa = int(255 * a)
    if aa <= 2:
        return
    badan = (235, 238, 242, aa)
    garis = (40, 45, 55, aa)
    d.rounded_rectangle((x - 95 * s, y - 18 * s, x + 80 * s, y + 18 * s), int(17 * s), fill=badan, outline=garis, width=3)
    d.polygon([(x - 95 * s, y - 10 * s), (x - 125 * s, y - 62 * s), (x - 100 * s, y - 62 * s), (x - 60 * s, y - 14 * s)],
              fill=(200, 52, 44, aa), outline=garis)
    d.polygon([(x - 20 * s, y), (x + 30 * s, y), (x + 5 * s, y + 34 * s), (x - 40 * s, y + 34 * s)],
              fill=(215, 220, 228, aa), outline=garis)
    for i in range(4):
        d.ellipse((x + (30 - i * 26) * s - 8 * s, y - 12 * s, x + (30 - i * 26) * s + 8 * s, y - 2 * s),
                  fill=(90, 140, 190, aa))
    d.ellipse((x + 74 * s, y - 8 * s, x + 92 * s, y + 8 * s), fill=garis)
    h = 34 * s * abs(math.cos(putar))
    d.line((x + 92 * s, y - h, x + 92 * s, y + h), fill=(60, 60, 70, aa), width=max(2, int(5 * s)))


def pesawat_atas(d, x, y, s=1.0, a=255):
    """Pesawat tampak atas (buat di peta)."""
    d.polygon([(x - 50 * s, y), (x + 50 * s, y - 6 * s), (x + 58 * s, y), (x + 50 * s, y + 6 * s)], fill=(240, 240, 245, a), outline=(40, 40, 50, a))
    d.polygon([(x - 5 * s, y), (x + 15 * s, y - 40 * s), (x + 25 * s, y - 40 * s), (x + 15 * s, y)], fill=(220, 220, 230, a), outline=(40, 40, 50, a))
    d.polygon([(x - 5 * s, y), (x + 15 * s, y + 40 * s), (x + 25 * s, y + 40 * s), (x + 15 * s, y)], fill=(220, 220, 230, a), outline=(40, 40, 50, a))
    d.polygon([(x - 50 * s, y), (x - 40 * s, y - 20 * s), (x - 32 * s, y - 20 * s), (x - 36 * s, y)], fill=(200, 60, 40, a))


def kristal(d, x, y, r, a=1.0, warna=PUTIH):
    """Bintang kristal es (6 lengan)."""
    aa = int(255 * a)
    if aa <= 2 or r < 1:
        return
    for k in range(3):
        sud = k * math.pi / 3
        dx, dy = math.cos(sud) * r, math.sin(sud) * r
        d.line((x - dx, y - dy, x + dx, y + dy), fill=tuple(warna) + (aa,), width=max(1, int(r / 4)))


def es_kering(d, x, y, s=1.0, a=1.0):
    aa = int(255 * a)
    d.polygon([(x - 40 * s, y - 20 * s), (x, y - 40 * s), (x + 40 * s, y - 20 * s), (x, y)], fill=(250, 252, 255, aa),
              outline=(120, 140, 160, aa))
    d.polygon([(x - 40 * s, y - 20 * s), (x, y), (x, y + 40 * s), (x - 40 * s, y + 20 * s)], fill=(215, 228, 240, aa),
              outline=(120, 140, 160, aa))
    d.polygon([(x + 40 * s, y - 20 * s), (x, y), (x, y + 40 * s), (x + 40 * s, y + 20 * s)], fill=(185, 205, 225, aa),
              outline=(120, 140, 160, aa))


def uap(img, x, y, t, kuat=1.0, seed=2, lebar=1.0, warna=(235, 245, 255)):
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    for i in range(24):
        f = (rng.random() + t * 0.35) % 1
        xx = x + rng.uniform(-60, 60) * lebar + math.sin(t * 2 + i) * 14
        yy = y - f * 160
        r = 20 + f * 50
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=tuple(warna) + (int(90 * kuat * (1 - f)),))
    img.alpha_composite(lap)


# ------------------------------------------------------------------ adegan

RUMAH = (360, 1020, 720, 1240)  # dinding rumah (x0, y0, x1, y1)


def _rumah(d, bolong=0.0, goyang=0.0):
    x0, y0, x1, y1 = RUMAH
    gx = goyang
    d.rectangle((x0 + gx, y0, x1 + gx, y1), fill=(225, 205, 170, 255), outline=GELAP + (255,), width=4)
    d.rectangle((x0 + 140 + gx, y0 + 90, x0 + 220 + gx, y1), fill=(120, 80, 50, 255), outline=GELAP + (255,), width=3)
    d.rectangle((x0 + 30 + gx, y0 + 60, x0 + 110 + gx, y0 + 130), fill=(150, 190, 220, 255), outline=GELAP + (255,), width=3)
    d.rectangle((x1 - 110 + gx, y0 + 60, x1 - 30 + gx, y0 + 130), fill=(150, 190, 220, 255), outline=GELAP + (255,), width=3)
    atap = [(x0 - 60 + gx, y0 + 5), (x0 + 60 + gx, y0 - 140), (x1 - 60 + gx, y0 - 140), (x1 + 60 + gx, y0 + 5)]
    d.polygon(atap, fill=(165, 172, 180, 255), outline=GELAP + (255,))
    for i in range(1, 14):
        f = i / 14
        xa = lerp(x0 - 60, x1 + 60, f) + gx
        xb = lerp(x0 + 60, x1 - 60, f) + gx
        d.line((xa, y0 + 5, xb, y0 - 140), fill=(120, 126, 135, 255), width=3)
    if bolong > 0:
        cx, cy = 560 + gx, y0 - 70
        r = 46 * bolong
        lubang = [(cx - r, cy - r * 0.3), (cx - r * 0.4, cy - r * 0.7), (cx + r * 0.5, cy - r * 0.5), (cx + r, cy + r * 0.1),
                  (cx + r * 0.3, cy + r * 0.6), (cx - r * 0.6, cy + r * 0.5)]
        d.polygon(lubang, fill=(30, 25, 22, 255), outline=(230, 230, 235, 255))


def a_hook(c):
    img, d = langit((150, 160, 170), (215, 205, 185))
    # tanah
    d.rectangle((0, 1240, W, H), fill=(110, 125, 70, 255))
    for i in range(12):
        x = i * 100 + 20
        d.ellipse((x - 70, 1180, x + 70, 1300), fill=(80, 110, 55, 255))
    awan(img, 220, 480, 0.8, (225, 225, 230), seed=1)
    awan(img, 860, 430, 0.7, (225, 225, 230), seed=2)
    d = ImageDraw.Draw(img, "RGBA")
    # pesawat lewat
    px = lerp(-150, W + 200, c.p(0.0, 0.7))
    pesawat(d, px, 560, 1.1, 1.0, c.t * 30)
    # bongkahan es jatuh
    k = c.t / c.d
    jatuh = c.p(0.03, 0.16)
    kena = k >= 0.16
    goyang = 0.0
    if kena and k < 0.24:
        goyang = math.sin(c.t * 70) * 14 * (1 - (k - 0.16) / 0.08)
    _rumah(d, bolong=1.0 if kena else 0.0, goyang=goyang)
    if not kena and k > 0.03:
        ex, ey = lerp(380, 560, jatuh), lerp(600, 940, jatuh * jatuh)
        es_kering(d, ex, ey, 0.6)
        for j in range(4):
            d.line((ex - 20 + j * 13, ey - 40, ex - 30 + j * 13, ey - 90), fill=(255, 255, 255, 120), width=3)
    if kena:
        rng = random.Random(4)
        f = c.p(0.16, 0.3)
        for i in range(10):
            sud = rng.uniform(-math.pi, 0)
            jx = 560 + math.cos(sud) * 160 * f
            jy = RUMAH[1] - 70 + math.sin(sud) * 120 * f + 200 * f * f
            kristal(d, jx, jy, 10, 1 - f, BIRU_ES)
        s = back_out((k - 0.16) / 0.1)
        if k < 0.42:
            judul_besar(d, (540, 820), "BRAK!", int(150 * s) + 1, (255, 230, 120), 1 - c.p(0.36, 0.42))
    s2 = back_out((k - 0.4) / 0.1) if k > 0.4 else 0
    if s2 > 0:
        judul_besar(d, (540, 760), "ES DARI LANGIT?", int(96 * s2) + 1, PUTIH)
        se.kartu(img, 540, 900, "Lagi viral di Palembang", "Oktober 2026", MERAH, alpha=c.p(0.45, 0.52), tiang=False)
    d = ImageDraw.Draw(img, "RGBA")
    judul_besar(d, (540, 1340), "kok bisa manusia bikin hujan?", 50, (255, 225, 150), c.p(0.8, 0.88))
    hdr(img, alpha=c.p(0.85, 0.95))
    return img


def a_tren(c):
    kamera = se.kamera_antara(cam(-2.5, 104.5, 1.0), cam(-3.0, 104.7, 1.6), c.p(0.0, 0.6))
    img, d = peta(kamera)
    se.tint(img, (190, 160, 100), 0.18)
    d = ImageDraw.Draw(img, "RGBA")
    x, y = layar(kamera, PALEMBANG)
    d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=MERAH + (255,), outline=(255, 255, 255, 255), width=4)
    label(d, (x + 10, y + 52), "Palembang", 44, (150, 30, 20))
    label(d, (x - 230, y - 330), "SUMATRA SELATAN", 40, TINTA, c.p(0.05, 0.15))
    # rute pesawat penabur
    rute = [(x - 420, y - 200), (x - 120, y - 260), (x + 120, y - 160), (x + 380, y - 230)]
    ujung = se.garis_putus(d, rute, c.p(0.1, 0.55), (30, 60, 120), tebal=6)
    if ujung:
        pesawat_atas(d, ujung[0], ujung[1], 1.0, 255)
        rng = random.Random(3)
        n = int(60 * c.p(0.1, 0.55))
        for i in range(n):
            q = se.titik_di_jalur(rute, (i + 1) / 61)[0]
            kristal(d, q[0] + rng.uniform(-30, 30), q[1] + rng.uniform(10, 70), 7, 0.9, PUTIH)
    se.kartu(img, 540, 1240, "Operasi Modifikasi Cuaca", "bantu lawan karhutla & kabut asap", BIRU,
             alpha=c.p(0.25, 0.33) * (1 - c.p(0.62, 0.66)), tiang=False, skala=back_out((c.t / c.d - 0.25) / 0.1))
    se.kartu(img, 540, 1240, "BMKG: masih dievaluasi", "ukuran dry ice & keamanan warga", MERAH,
             alpha=c.p(0.66, 0.72), tiang=False, skala=back_out((c.t / c.d - 0.66) / 0.1))
    hdr(img, "Palembang, Oktober 2026")
    return img


def _lab(d):
    d.rectangle((0, 0, W, H), fill=(70, 58, 48, 255))
    for x in range(0, W, 90):
        d.line((x, 0, x, 1150), fill=(80, 67, 56, 255), width=3)
    d.rectangle((0, 1150, W, H), fill=(105, 80, 55, 255))
    d.rectangle((0, 1150, W, 1170), fill=(130, 100, 70, 255))


KOTAK = (300, 820, 780, 1150)


def a_lab(c):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img, "RGBA")
    _lab(d)
    x0, y0, x1, y1 = KOTAK
    # kotak pendingin (tutup terbuka)
    d.rectangle((x0, y0, x1, y1), fill=(215, 220, 225, 255), outline=GELAP + (255,), width=5)
    d.rectangle((x0 + 30, y0 + 20, x1 - 30, y0 + 230), fill=(25, 30, 40, 255))
    d.polygon([(x0, y0), (x1, y0), (x1 - 30, y0 - 150), (x0 + 30, y0 - 150)], fill=(190, 196, 202, 255), outline=GELAP + (255,))
    se.teks(d, (540, y1 - 45), "KOTAK PENDINGIN", 30, (80, 80, 90), nama_font="ui")
    # awan mini (uap napas)
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    rng = random.Random(5)
    kabut = c.p(0.15, 0.35) * (1 - 0.7 * c.p(0.7, 0.8))
    for i in range(30):
        xx = rng.uniform(x0 + 60, x1 - 60) + math.sin(c.t + i) * 10
        yy = rng.uniform(y0 + 50, y0 + 210)
        r = rng.uniform(30, 60)
        dl.ellipse((xx - r, yy - r * 0.6, xx + r, yy + r * 0.6), fill=(170, 185, 205, int(80 * kabut)))
    img.alpha_composite(lap)
    d = ImageDraw.Draw(img, "RGBA")
    # es kering dimasukkan
    jatuh = c.p(0.55, 0.68)
    if 0.5 < c.t / c.d:
        es_kering(d, 540, lerp(560, y0 + 170, jatuh), 0.8)
        if jatuh >= 1:
            uap(img, 540, y0 + 150, c.t, 0.8, lebar=1.2)
            d = ImageDraw.Draw(img, "RGBA")
    # jutaan kristal es berkilau
    kilau = c.p(0.72, 0.85)
    if kilau > 0:
        se.glow(img, 540, y0 + 120, 300, BIRU_ES, kilau)
        d = ImageDraw.Draw(img, "RGBA")
        rng = random.Random(9)
        for i in range(int(90 * kilau)):
            xx = rng.uniform(x0 + 40, x1 - 40)
            yy = rng.uniform(y0 - 120, y0 + 220)
            r = rng.uniform(5, 13) * (0.6 + 0.4 * math.sin(c.t * 9 + i))
            kristal(d, xx, yy, r, 0.95)
        judul_besar(d, (540, 1260), "jutaan kristal es!", 64, BIRU_ES, kilau)
    s = back_out(c.t / c.d / 0.1)
    judul_besar(d, (540, 450), "1946", int(130 * s) + 1, (255, 225, 150))
    se.kartu(img, 540, 590, "Vincent Schaefer", "ilmuwan General Electric, AS", BIRU, alpha=c.p(0.12, 0.2), tiang=False)
    hdr(img, "Amerika Serikat, 1946")
    return img


def a_terbang(c):
    img, d = langit((80, 140, 210), (190, 215, 240))
    # gunung Greylock
    d.polygon([(0, 1320), (180, 1180), (380, 1060), (520, 1000), (660, 1050), (860, 1150), (W, 1230), (W, H), (0, H)],
              fill=(85, 105, 75, 255))
    d.polygon([(0, 1400), (300, 1300), (600, 1340), (900, 1280), (W, 1330), (W, H), (0, H)], fill=(60, 80, 55, 255))
    label(d, (540, 1090), "Gunung Greylock", 38)
    # lapisan awan super dingin
    for i, x in enumerate(range(80, 1100, 230)):
        awan(img, x, 760, 0.75, (238, 240, 246), seed=10 + i, lebar=0.9)
    d = ImageDraw.Draw(img, "RGBA")
    # pesawat menabur es kering di atas awan
    maju = c.p(0.05, 0.5)
    px = lerp(-120, W + 150, maju)
    rng = random.Random(6)
    for i in range(int(70 * maju)):
        f = (i + 1) / 70
        xx = lerp(-120, W + 150, f) - 100 + rng.uniform(-10, 10)
        if xx < px - 90:
            kristal(d, xx, 660 + rng.uniform(-10, 30), 6, 0.9)
    pesawat(d, px, 620, 0.9, 1.0, c.t * 30)
    # salju turun dari awan lalu menguap
    salju = c.p(0.45, 0.7)
    if salju > 0:
        rng = random.Random(8)
        for i in range(140):
            xx = rng.uniform(40, W - 40)
            if xx > px - 100:
                continue
            f = (rng.random() + c.t * 0.5) % 1
            yy = 800 + f * 260
            a = salju * (1 - f) * 0.95
            kristal(d, xx + math.sin(c.t * 2 + i) * 8, yy, 7, a)
    se.kartu(img, 540, 450, "13 November 1946", "Massachusetts, Amerika Serikat", BIRU, alpha=c.p(0.02, 0.1), tiang=False)
    judul_besar(d, (540, 1000), "SALJU TURUN!", 76, PUTIH, c.p(0.5, 0.56) * (1 - c.p(0.74, 0.78)), (30, 60, 110))
    se.kartu(img, 540, 1000, "…tapi menguap sebelum sampai tanah", "", (60, 60, 70), alpha=c.p(0.78, 0.84), tiang=False)
    hdr(img, "Uji coba di udara")
    return img


def _flare(d, x, y, t, s=1.0, a=1.0):
    aa = int(255 * a)
    d.rounded_rectangle((x - 20 * s, y - 70 * s, x + 20 * s, y + 70 * s), int(18 * s), fill=(200, 60, 40, aa), outline=GELAP + (aa,), width=4)
    for i in range(7):
        f = (t * 0.6 + i / 7) % 1
        r = (16 + f * 40) * s
        d.ellipse((x - r + f * 30, y - 80 * s - f * 120 * s - r, x + r + f * 30, y - 80 * s - f * 120 * s + r),
                  fill=(200, 200, 205, int(aa * 0.7 * (1 - f))))


def a_bahan(c):
    img, d = langit((60, 75, 100), (110, 125, 150))
    se.panel(img, (90, 440, 990, 1280), alpha=c.p(0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 530), "BAHAN PENYEMAI AWAN", 50, (150, 40, 30), nama_font="judul", alpha=c.p(0.02, 0.1))
    a1 = c.p(0.02, 0.12)
    es_kering(d, 310, 760, 1.6, a1)
    se.teks(d, (310, 920), "Es kering", 44, TINTA, nama_font="tangan", alpha=a1)
    se.teks(d, (310, 970), "karbon dioksida beku", 28, (100, 80, 60), nama_font="tangan_tipis", alpha=a1)
    a2 = c.p(0.3, 0.4)
    _flare(d, 770, 800, c.t, 0.9, a2)
    se.teks(d, (770, 920), "Perak iodida", 44, TINTA, nama_font="tangan", alpha=a2)
    se.teks(d, (770, 970), "ditemukan Bernard Vonnegut", 28, (100, 80, 60), nama_font="tangan_tipis", alpha=a2)
    se.kartu(img, 540, 1150, "Dunia mulai mencoba atur cuaca", "", BIRU, alpha=c.p(0.62, 0.7), tiang=False,
             skala=back_out((c.t / c.d - 0.62) / 0.1))
    hdr(img, "Setelah 1946")
    return img


def a_cara(c):
    img, d = langit((95, 150, 210), (200, 220, 240))
    k = c.t / c.d
    # bagian 1: cuma bantu awan yang sudah ada
    a0 = 1 - c.p(0.28, 0.33)
    if a0 > 0.01:
        awan(img, 540, 800, 1.3, alpha=a0, seed=3)
        d = ImageDraw.Draw(img, "RGBA")
        judul_besar(d, (540, 560), "nggak bikin awan dari nol", 60, PUTIH, c.p(0.02, 0.1) * a0, (30, 60, 110))
        se.kartu(img, 540, 1050, "cuma bantu awan yang sudah ada", "", BIRU, alpha=c.p(0.12, 0.2) * a0, tiang=False)
    # bagian 2: dua jenis awan
    b = c.p(0.3, 0.36)
    if b > 0.01:
        awan(img, 280, 720, 0.62, (225, 235, 250), b, seed=4, lebar=0.9)
        awan(img, 800, 720, 0.62, (250, 248, 240), b, seed=5, lebar=0.9)
        d = ImageDraw.Draw(img, "RGBA")
        judul_besar(d, (280, 540), "AWAN DINGIN", 46, (200, 230, 255), b, (20, 40, 80))
        judul_besar(d, (800, 540), "AWAN HANGAT", 46, (255, 225, 160), b, (80, 40, 10))
        # kiri: kristal es -> salju
        ki = c.p(0.36, 0.5)
        rng = random.Random(11)
        for i in range(int(18 * ki)):
            kristal(d, 280 + rng.uniform(-140, 140), 700 + rng.uniform(-50, 40), 9, 1.0)
        if ki >= 1:
            for i in range(30):
                f = (rng.random() + c.t * 0.5) % 1
                kristal(d, 280 + rng.uniform(-150, 150), 790 + f * 300, 7, 1 - f)
        se.teks(d, (280, 1150), "es kering / perak iodida", 30, TINTA, nama_font="tangan", stroke=4,
                stroke_warna=KREM_LABEL, alpha=c.p(0.36, 0.44))
        # kanan: garam -> tetes membesar -> hujan
        ka = c.p(0.55, 0.65)
        rng = random.Random(12)
        tumbuh = c.p(0.65, 0.82)
        for i in range(int(14 * ka)):
            gx, gy = 800 + rng.uniform(-130, 130), 700 + rng.uniform(-40, 40)
            d.rectangle((gx - 5, gy - 5, gx + 5, gy + 5), fill=(255, 255, 255, 255), outline=(120, 120, 130, 255))
            r = 4 + 14 * tumbuh
            if tumbuh > 0:
                d.ellipse((gx - r, gy - r, gx + r, gy + r), outline=BIRU + (200,), width=3)
        if k > 0.8:
            for i in range(40):
                f = (rng.random() + c.t * 1.4) % 1
                xx = 800 + rng.uniform(-150, 150)
                yy = 790 + f * 320
                d.line((xx, yy, xx - 4, yy + 28), fill=(60, 110, 190, int(230 * (1 - f * 0.6))), width=4)
        se.teks(d, (800, 1150), "garam halus (NaCl)", 30, TINTA, nama_font="tangan", stroke=4,
                stroke_warna=KREM_LABEL, alpha=c.p(0.55, 0.63))
        se.kartu(img, 540, 1270, "paling sering di Indonesia", "", MERAH, alpha=c.p(0.62, 0.7), tiang=False)
    hdr(img, "Cara kerjanya")
    return img


def a_indonesia(c):
    kamera = se.kamera_antara(cam(4.0, 103.5, 0.57), cam(-5.0, 106.5, 1.4), c.p(0.6, 0.85))
    img, d = peta(kamera)
    for nama, ll in LABEL_ID.items():
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 38, TINTA, 0.8)
    jx, jy = layar(kamera, JAKARTA)
    bx, by = layar(kamera, BANGKOK)
    d.ellipse((jx - 11, jy - 11, jx + 11, jy + 11), fill=MERAH + (255,), outline=(255, 255, 255, 255), width=3)
    d.ellipse((bx - 11, by - 11, bx + 11, by + 11), fill=BIRU + (255,), outline=(255, 255, 255, 255), width=3)
    label(d, (bx + 10, by - 40), "Bangkok", 34, BIRU)
    se.garis_putus(d, [(jx, jy), (jx - 120, (jy + by) / 2), (bx, by)], c.p(0.25, 0.5), MERAH, tebal=6)
    s = back_out(c.t / c.d / 0.1)
    judul_besar(d, (540, 760), "1977", int(120 * s) + 1, (255, 225, 150), 1 - c.p(0.56, 0.6))
    se.kartu(img, min(bx + 230, W - 230), by + 110, "Thailand", "pertaniannya bikin Soeharto kagum", BIRU,
             alpha=c.p(0.1, 0.18) * (1 - c.p(0.56, 0.6)), tiang=False)
    se.kartu(img, 540, 960, "Habibie diutus belajar ke sana", "", MERAH, alpha=c.p(0.3, 0.38) * (1 - c.p(0.56, 0.6)),
             tiang=False)
    a = c.p(0.72, 0.8)
    if a > 0:
        x, y = layar(kamera, JATILUHUR)
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(30, 110, 180, int(255 * a)), outline=(255, 255, 255, int(255 * a)), width=3)
        se.kartu(img, x, y - 10, "Waduk Jatiluhur", "uji coba buat ngairin sawah", (30, 110, 180), alpha=a,
                 skala=back_out((c.t / c.d - 0.72) / 0.1))
    hdr(img, "Indonesia ikut mencoba")
    return img


LINIMASA = [
    (0.02, "1978", "BPPT berdiri", ""),
    (0.08, "1985", "UPT Hujan Buatan", "unit khusus di BPPT"),
    (0.22, "1997", "Bantu padamkan karhutla", ""),
    (0.42, "2011", "SEA Games Palembang", "justru buat ngurangin hujan"),
    (0.75, "2021", "Kini dikelola BRIN", ""),
]


def a_linimasa(c):
    img, d = langit((60, 75, 100), (110, 125, 150))
    se.panel(img, (80, 420, 1000, 1310), alpha=c.p(0, 0.06))
    d = ImageDraw.Draw(img, "RGBA")
    xg = 250
    d.line((xg, 480, xg, 480 + 760 * c.p(0, 0.8)), fill=(120, 90, 50, 255), width=6)
    for i, (f, th, judul, sub) in enumerate(LINIMASA):
        a = c.p(f, f + 0.06)
        if a <= 0:
            continue
        y = 530 + i * 170
        d.ellipse((xg - 16, y - 16, xg + 16, y + 16), fill=MERAH + (int(255 * a),), outline=(255, 255, 255, int(255 * a)), width=4)
        se.teks(d, (xg - 40, y), th, 40, (150, 40, 30), nama_font="judul", anchor="rm", alpha=a)
        se.teks(d, (xg + 40, y - (16 if sub else 0)), judul, 40, TINTA, nama_font="tangan", anchor="lm", alpha=a)
        if sub:
            se.teks(d, (xg + 40, y + 30), sub, 28, (100, 80, 60), nama_font="tangan_tipis", anchor="lm", alpha=a)
    hdr(img, "Hujan buatan di Indonesia")
    return img


def a_bongkahan(c):
    img, d = langit((95, 150, 210), (200, 220, 240))
    se.panel(img, (90, 440, 990, 1130), alpha=c.p(0, 0.06))
    d = ImageDraw.Draw(img, "RGBA")
    k = c.t / c.d
    rng = random.Random(21)
    butir = [(rng.uniform(220, 860), rng.uniform(600, 880)) for _ in range(40)]
    nyatu = c.p(0.42, 0.62)
    pecah = c.p(0.78, 0.92)
    for i, (bx, by) in enumerate(butir):
        tx, ty = 540 + (bx - 540) * 0.18, 760 + (by - 740) * 0.18
        x = lerp(bx, tx, nyatu)
        y = lerp(by, ty, nyatu)
        if pecah > 0:
            x = lerp(x, bx, pecah)
            y = lerp(y, by, pecah) + pecah * 120
        r = 11
        d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 252, 255, 255), outline=(120, 140, 160, 255), width=2)
    if 0.55 < k < 0.82:
        es_kering(d, 540, 760, 1.5 * c.p(0.55, 0.62), 1.0 - c.p(0.78, 0.82))
    se.teks(d, (540, 520), "butiran ideal ± 3 mm", 48, TINTA, nama_font="tangan", alpha=c.p(0.15, 0.22) * (1 - c.p(0.4, 0.44)))
    se.teks(d, (540, 520), "kedinginan → nyatu!", 48, MERAH, nama_font="tangan", alpha=c.p(0.44, 0.5) * (1 - c.p(0.72, 0.76)))
    se.teks(d, (540, 520), "dipecah & disaring", 48, (30, 110, 60), nama_font="tangan", alpha=c.p(0.76, 0.82))
    # saringan
    sa = c.p(0.74, 0.8)
    if sa > 0:
        aa = int(200 * sa)
        for xx in range(200, 900, 40):
            d.line((xx, 940, xx, 1060), fill=(80, 80, 90, aa), width=3)
        for yy in range(940, 1070, 40):
            d.line((200, yy, 880, yy), fill=(80, 80, 90, aa), width=3)
    judul_besar(d, (540, 1250), "Kata BMKG", 56, PUTIH, c.p(0.08, 0.15), (30, 60, 110))
    hdr(img, "Kenapa bisa jadi bongkahan?")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(-1.0, 108.5, 0.62))
    img, d = peta(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1060), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Bukan sihir, tapi sains", 54, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 650), "umurnya udah 80 tahun", 38, (90, 70, 50), alpha=a)
        awan(img, 540, 820, 0.8, (235, 238, 245), a, seed=7)
        d = ImageDraw.Draw(img, "RGBA")
        rng = random.Random(2)
        for i in range(24):
            f = (rng.random() + c.t * 1.2) % 1
            xx = 540 + rng.uniform(-150, 150)
            yy = 880 + f * 110
            d.line((xx, yy, xx - 3, yy + 22), fill=(60, 110, 190, int(230 * a * (1 - f * 0.5))), width=4)
        se.teks(d, (540, 1010), "dan masih terus diperbaiki", 44, (30, 80, 150), nama_font="caption", alpha=a)
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
    Adegan("hook", "Es jatuh dari langit, atap rumah bolong? Lagi viral di Palembang. Diduga dari pesawat hujan buatan. "
                   "Kok bisa manusia bikin hujan?", a_hook, transisi=False),
    Adegan("tren", "Pesawat itu lagi menabur es kering ke awan, buat lawan kebakaran hutan dan kabut asap. "
                   "Kata BMKG, kasusnya masih dievaluasi.", a_tren),
    Adegan("lab", "Ceritanya mulai tahun sembilan belas empat puluh enam. Ilmuwan Amerika, Vincent Schaefer, bikin "
                  "awan mini di kotak pendingin. Dia masukin es kering, dan tiba-tiba, muncul jutaan kristal es.", a_lab),
    Adegan("terbang", "Lalu dia terbang, dan menabur es kering ke awan. Hasilnya, salju turun! "
                      "Walau menguap sebelum sampai tanah.", a_terbang),
    Adegan("bahan", "Rekannya, Bernard Vonnegut, lalu nemu bahan lain. Perak iodida.", a_bahan),
    Adegan("cara", "Manusia nggak bikin awan dari nol. Cuma bantu awan yang udah ada. "
                   "Es kering buat awan dingin. Di awan hangat kayak di Indonesia, biasanya pakai garam halus, "
                   "biar tetes airnya cepat besar jadi hujan.", a_cara),
    Adegan("indonesia", "Indonesia mulai tahun sembilan belas tujuh puluh tujuh. Soeharto kagum sama pertanian Thailand, "
                        "lalu mengutus Habibie belajar ke sana. Uji cobanya buat sawah, di Jatiluhur.",
           a_indonesia),
    Adegan("linimasa", "Setelah itu, hujan buatan dipakai buat isi waduk, lawan kebakaran hutan, sampai ngurangin hujan "
                       "pas SEA Games dua ribu sebelas di Palembang. Sekarang, dikelola BRIN.", a_linimasa),
    Adegan("bongkahan", "Terus, soal bongkahannya? Kata BMKG, butiran es kering idealnya sekitar tiga milimeter. "
                        "Kalau kedinginan, bisa nyatu. Sekarang, pesawatnya dipasang saringan dan pemecah.", a_bongkahan),
    Adegan("penutup", "Jadi, hujan buatan bukan sihir, tapi sains umur delapan puluh tahun. "
                      "Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
