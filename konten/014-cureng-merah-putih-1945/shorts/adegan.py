"""Shorts ±90 detik: Cureng, Pesawat Merah Putih Pertama (27 Oktober 1945).

Langit ilustrasi + pesawat Cureng tampak samping, denah lapangan Maguwo, peta Jawa Tengah
(serangan udara 29 Juli 1947 & insiden Dakota). Waktu animasi pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import EMAS, MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "cureng-merah-putih-1945-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "CURENG MERAH PUTIH"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
ORANYE = (232, 118, 38)
ORANYE_TUA = (175, 80, 25)
ABU = (120, 118, 112)
HIJAU_ZAITUN = (95, 105, 60)
BIRU = (30, 80, 150)
MERAH_BENDERA = (210, 30, 35)

# ------------------------------------------------------------------ peta Jawa Tengah

print("  menyiapkan peta Jawa...")
GUNUNG = [(-7.54, 110.45, 0.12), (-7.45, 110.43, 0.12), (-7.38, 110.07, 0.11), (-7.3, 109.99, 0.11),
          (-7.63, 111.19, 0.14), (-7.2, 110.33, 0.08), (-7.0, 107.6, 0.15), (-7.94, 112.95, 0.15)]
PETA = Peta(104.5, 116.5, -10.5, -3.5, 300, [], GUNUNG, seed=45, darat=pd.SEMUA)

MAGUWO = (-7.788, 110.432)
YOGYA = (-7.797, 110.37)
SEMARANG = (-6.97, 110.42)
SALATIGA = (-7.33, 110.508)
AMBARAWA = (-7.264, 110.404)
NGOTO = (-7.86, 110.38)

print("  menyiapkan latar lapangan...")
LAPANGAN = se.latar_tekstur(W, H, 77, warna=(176, 168, 118))


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


def hdr(img, sub="27 Oktober 1945", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def muncul(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


# ------------------------------------------------------------------ gambar pesawat

def roundel(d, x, y, r, a):
    """Tanda bulat merah putih (merah di atas)."""
    box = (x - r, y - r, x + r, y + r)
    d.pieslice(box, 180, 360, fill=MERAH_BENDERA + (a,))
    d.pieslice(box, 0, 180, fill=(250, 250, 250, a))
    d.ellipse(box, outline=(40, 25, 15, a), width=max(1, int(r * 0.15)))


def cureng(d, x, y, s=1.0, arah=1, alpha=1.0, warna=ORANYE, tanda=True, t=0.0):
    """Pesawat latih bersayap dua (Yokosuka K5Y 'Cureng') tampak samping. arah=1 menghadap kanan."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)

    def P(px, py):
        return (x + px * s * arah, y + py * s)

    col = tuple(warna) + (a,)
    gelap = tuple(int(v * 0.72) for v in warna) + (a,)
    ink = (45, 30, 20, a)
    lw = max(2, int(3 * s))
    # sayap bawah (di belakang badan)
    d.polygon([P(-30, 12), P(46, 8), P(50, 17), P(-28, 20)], fill=gelap, outline=ink)
    # roda
    d.line([P(40, 12), P(30, 40)], fill=ink, width=lw)
    d.line([P(54, 10), P(30, 40)], fill=ink, width=lw)
    rr = 10 * s
    cx, cy = P(30, 42)
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(40, 35, 30, a))
    tx, ty = P(-106, 10)
    d.ellipse((tx - 4 * s, ty - 4 * s, tx + 4 * s, ty + 4 * s), fill=(40, 35, 30, a))
    d.line([P(-104, 4), P(-106, 10)], fill=ink, width=lw)
    # badan
    d.polygon([P(70, -17), P(20, -19), P(-60, -11), P(-114, -6), P(-112, 3), P(-60, 9), P(20, 16), P(72, 14)],
              fill=col, outline=ink)
    # kokpit (dua kursi)
    for kx in (-30, 8):
        d.polygon([P(kx, -18), P(kx + 8, -30), P(kx + 18, -30), P(kx + 18, -18)], fill=(160, 200, 215, a), outline=ink)
    # sirip ekor & stabilizer
    d.polygon([P(-92, -8), P(-108, -42), P(-121, -42), P(-116, -4)], fill=col, outline=ink)
    d.polygon([P(-88, -1), P(-124, -3), P(-124, 4), P(-88, 4)], fill=gelap, outline=ink)
    # mesin
    d.polygon([P(66, -18), P(90, -13), P(90, 11), P(66, 15)], fill=(70, 62, 58, a), outline=ink)
    # sayap atas + tiang
    d.line([P(2, -46), P(-6, 12)], fill=ink, width=lw)
    d.line([P(48, -50), P(40, 9)], fill=ink, width=lw)
    d.line([P(20, -48), P(26, -18)], fill=ink, width=lw)
    d.polygon([P(-16, -52), P(64, -57), P(68, -48), P(-13, -44)], fill=col, outline=ink)
    if tanda:
        rx, ry = P(-62, -1)
        roundel(d, rx, ry, 11 * s, a)
        ux, uy = P(26, -51)
        d.ellipse((ux - 9 * s, uy - 4 * s, ux + 9 * s, uy + 4 * s), fill=MERAH_BENDERA + (a,))
    # baling-baling berputar
    bx, by = P(92, 0)
    d.ellipse((bx - 4 * s, by - 36 * s, bx + 4 * s, by + 36 * s), fill=(220, 220, 220, int(70 * alpha)))
    k = math.cos(t * 40) * 34 * s
    d.line((bx, by - k, bx, by + k), fill=(60, 50, 45, int(200 * alpha)), width=max(2, int(4 * s)))


def _putar(titik, x, y, sudut, s):
    c, sn = math.cos(sudut), math.sin(sudut)
    return [(x + (px * c - py * sn) * s, y + (px * sn + py * c) * s) for px, py in titik]


def pesawat_atas(d, x, y, sudut, s=1.0, warna=ORANYE, alpha=1.0, jenis="cureng", tanda=True):
    """Ikon pesawat tampak atas, hidung ke arah `sudut` (radian, koordinat layar)."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    col = tuple(warna) + (a,)
    ink = (35, 25, 15, a)
    if jenis == "dakota":
        sayap = [(4, -52), (14, -52), (12, 52), (2, 52)]
        badan = [(36, 0), (28, -6), (-34, -3), (-34, 3), (28, 6)]
        ekor = [(-28, -16), (-22, -16), (-22, 16), (-28, 16)]
        mesin = [[(18, -26), (4, -26), (4, -18), (18, -18)], [(18, 26), (4, 26), (4, 18), (18, 18)]]
    elif jenis == "tempur":
        sayap = [(2, -30), (12, -30), (10, 30), (0, 30)]
        badan = [(30, 0), (22, -5), (-26, -3), (-26, 3), (22, 5)]
        ekor = [(-24, -12), (-18, -12), (-18, 12), (-24, 12)]
        mesin = []
    else:
        sayap = [(-2, -36), (12, -36), (12, 36), (-2, 36)]
        badan = [(28, 0), (22, -5), (-28, -3), (-28, 3), (22, 5)]
        ekor = [(-28, -13), (-21, -13), (-21, 13), (-28, 13)]
        mesin = []
    for poli in [sayap, ekor] + mesin + [badan]:
        d.polygon(_putar(poli, x, y, sudut, s), fill=col, outline=ink)
    if jenis == "cureng" and tanda:
        for py in (-24, 24):
            (rx, ry), = _putar([(5, py)], x, y, sudut, s)
            roundel(d, rx, ry, 5 * s, a)


def jalur(kamera, daftar):
    return [layar(kamera, ll) for ll in daftar]


def terbang_di(titik, k):
    (x, y), (dx, dy) = se.titik_di_jalur(titik, k)
    return x, y, math.atan2(dy, dx)


# ------------------------------------------------------------------ latar

def _langit(atas=(110, 170, 230), bawah=(225, 235, 240)):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (np.array(atas, np.float32) * (1 - g) + np.array(bawah, np.float32) * g).repeat(W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    return img, ImageDraw.Draw(img, "RGBA")


AWAN = [(140, 520, 1.0), (820, 600, 1.3), (420, 1000, 0.9), (960, 1150, 1.1), (60, 1250, 1.2), (700, 420, 0.8)]


def awan(d, t, kecepatan=18, alpha=1.0):
    for i, (x, y, s) in enumerate(AWAN):
        x = (x - t * kecepatan * s) % (W + 400) - 200
        a = int(220 * alpha)
        for dx, dy, r in [(-60, 10, 50), (0, -10, 65), (60, 8, 48), (110, 18, 34), (-105, 22, 32)]:
            d.ellipse((x + (dx - r) * s, y + (dy - r * 0.7) * s, x + (dx + r) * s, y + (dy + r * 0.7) * s),
                      fill=(255, 255, 255, a))


def tanah(d, y0=1130):
    d.rectangle((0, y0, W, H), fill=(125, 140, 80, 255))
    d.rectangle((0, y0, W, y0 + 14), fill=(95, 110, 60, 255))
    d.rectangle((0, y0 + 70, W, y0 + 150), fill=(105, 102, 96, 255))
    for x in range(20, W, 90):
        d.rectangle((x, y0 + 106, x + 50, y0 + 114), fill=(230, 225, 210, 255))


def hanggar(d, x, y, w=220, h=110, a=255):
    d.rectangle((x, y, x + w, y + h), fill=(140, 120, 95, a), outline=(60, 45, 30, a), width=4)
    d.pieslice((x - 6, y - h * 0.7, x + w + 6, y + h * 0.7), 180, 360, fill=(110, 95, 80, a), outline=(60, 45, 30, a), width=4)
    d.rectangle((x + w * 0.25, y + h * 0.35, x + w * 0.75, y + h), fill=(55, 45, 38, a))


def orang(d, x, y, s=1.0, warna=(60, 70, 110), a=255):
    """Penonton/teknisi berupa siluet bulat sederhana (tanpa wajah)."""
    d.ellipse((x - 7 * s, y - 30 * s, x + 7 * s, y - 16 * s), fill=(50, 38, 28, a))
    d.rounded_rectangle((x - 9 * s, y - 15 * s, x + 9 * s, y + 10 * s), int(6 * s), fill=tuple(warna) + (a,))


def lencana(d, x, y, s=1.0, a=255):
    """Lencana sayap penerbang dengan roundel merah putih di tengah."""
    emas = EMAS + (a,)
    for sisi in (-1, 1):
        for k in range(5):
            y0 = y - 26 * s + k * 13 * s
            panjang = (150 - k * 24) * s
            d.polygon([(x + sisi * 40 * s, y0), (x + sisi * (40 * s + panjang), y0 - 10 * s + k * 3 * s),
                       (x + sisi * (40 * s + panjang * 0.92), y0 + 9 * s), (x + sisi * 40 * s, y0 + 11 * s)],
                      fill=emas, outline=(120, 85, 20, a))
    d.ellipse((x - 46 * s, y - 46 * s, x + 46 * s, y + 46 * s), fill=EMAS + (a,), outline=(120, 85, 20, a), width=4)
    roundel(d, x, y, 34 * s, a)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img, d = _langit()
    awan(d, c.t, alpha=0.9)
    k = se.ease_out(c.p(0.0, 0.3))
    x = lerp(-300, 560, k) + math.sin(c.t * 1.4) * 10
    y = 950 + math.sin(c.t * 2.2) * 14
    cureng(d, x, y, 2.6, 1, t=c.t)
    s = back_out(c.t / 0.35)
    se.teks(d, (540, 520), "27 OKTOBER 1945", int(110 * s) + 1, (255, 240, 200), nama_font="caption", stroke=9,
            stroke_warna=(30, 20, 10))
    se.teks(d, (540, 1130), "pesawat bekas Jepang…", 50, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(30, 20, 10), alpha=c.p(0.15, 0.25))
    se.teks(d, (540, 1220), "tandanya MERAH PUTIH", 62, (255, 215, 200), nama_font="caption", stroke=7,
            stroke_warna=(120, 10, 10), alpha=c.p(0.38, 0.46))
    se.kartu(img, 540, 680, "Hari Penerbangan Nasional", "diperingati tiap 27 Oktober", MERAH,
             alpha=c.p(0.7, 0.78), tiang=False, skala=muncul(c, 0.7))
    hdr(img, alpha=c.p(0.85, 0.97))
    return img


AWAL_RUSAK = random.Random(5)
SEBARAN = [((kx - 1.5) * 170 + AWAL_RUSAK.uniform(-30, 30), ky * 90 - 40 + AWAL_RUSAK.uniform(-15, 15),
            AWAL_RUSAK.uniform(0, 6.28)) for ky in range(3) for kx in range(4)]


def a_maguwo(c):
    kamera = se.kamera_antara(cam(-7.35, 110.3, 0.95), cam(-7.788, 110.432, 1.7), c.p(0.0, 0.4))
    img, d = peta(kamera)
    a_luas = 1 - c.p(0.3, 0.4)
    for nama, ll in {"JAWA TENGAH": (-7.25, 109.7), "Laut Jawa": (-6.3, 110.3)}.items():
        label(d, layar(kamera, ll), nama, 42, TINTA, a_luas)
    x, y = layar(kamera, YOGYA)
    label(d, (x - 120, y + 50), "Yogyakarta", 40, TINTA, a_luas)
    mx, my = layar(kamera, MAGUWO)
    d.ellipse((mx - 12, my - 12, mx + 12, my + 12), fill=MERAH + (255,), outline=(255, 255, 255, 255), width=3)
    se.kartu(img, mx, my + 110, "Pangkalan Udara Maguwo", "diserahkan Jepang · Oktober 1945", MERAH,
             alpha=c.p(0.35, 0.43), tiang=False, skala=muncul(c, 0.35))
    # puluhan pesawat bekas (ilustratif) di sekitar pangkalan
    n = int(len(SEBARAN) * c.p(0.5, 0.7) + 0.999) if c.p(0.5, 0.7) > 0 else 0
    rusak = c.p(0.8, 0.88)
    for i, (dx, dy, sd) in enumerate(SEBARAN[:n]):
        warna = se.lerp_rgb(ORANYE, ABU, rusak if i % 3 != 0 else 0)
        px, py = 540 + dx * 1.15, my - 330 + dy
        pesawat_atas(d, px, py, sd, 1.7, warna, tanda=False)
        if i % 3 != 0 and rusak > 0:
            d.line((px - 24, py - 24, px + 24, py + 24), fill=(170, 20, 20, int(255 * rusak)), width=6)
            d.line((px + 24, py - 24, px - 24, py + 24), fill=(170, 20, 20, int(255 * rusak)), width=6)
    se.teks(d, (540, 1255), "PULUHAN PESAWAT BEKAS", 64, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=c.p(0.55, 0.65))
    se.teks(d, (540, 1335), "…banyak yang rusak", 48, (255, 190, 170), nama_font="caption", stroke=6,
            stroke_warna=(0, 0, 0), alpha=rusak)
    hdr(img, "Oktober 1945")
    return img


POS_BENGKEL = [(x, y) for y in (640, 790, 940) for x in (230, 540, 850)]


def a_bengkel(c):
    img = LAPANGAN.copy().convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    for hx in (60, 420, 780):
        hanggar(d, hx, 420, 240, 100)
    d.rectangle((0, 1030, W, 1130), fill=(92, 90, 86, 255))
    for x in range(0, W, 80):
        d.rectangle((x + 10, 1076, x + 50, 1084), fill=(235, 230, 215, 255))
    for i, (x, y) in enumerate(POS_BENGKEL):
        k = c.p(0.2 + i * 0.07, 0.26 + i * 0.07)
        pesawat_atas(d, x, y, -math.pi / 2, 2.2, se.lerp_rgb(ABU, ORANYE, k), tanda=False)
        if k < 1:
            a = int(255 * (1 - k))
            d.line((x - 30, y - 22, x + 30, y + 22), fill=(150, 20, 20, a), width=7)
            d.line((x + 30, y - 22, x - 30, y + 22), fill=(150, 20, 20, a), width=7)
        if 0 < k < 1:
            se.glow(img, x, y, 70, (255, 230, 140), 1.5)
            d = ImageDraw.Draw(img, "RGBA")
    # teknisi bolak-balik antar pesawat
    rng = random.Random(9)
    for i in range(14):
        a, b = rng.choice(POS_BENGKEL), rng.choice(POS_BENGKEL)
        f = (math.sin(c.t * rng.uniform(0.5, 1.0) + i) + 1) / 2
        orang(d, lerp(a[0], b[0], f) + 60, lerp(a[1], b[1], f) + 40, 1.1, BIRU)
    se.kartu(img, 540, 1225, "Sekitar 30 orang turun tangan", "memperbaiki pesawat satu per satu", BIRU,
             alpha=c.p(0.03, 0.12), tiang=False, skala=muncul(c, 0.03))
    hdr(img, "Bengkel darurat di Maguwo")
    return img


def a_cureng(c):
    img, d = _langit((150, 190, 225), (230, 225, 205))
    se.panel(img, (60, 420, 1020, 1300), alpha=c.p(0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    k = se.ease_out(c.p(0.02, 0.25))
    x = lerp(1400, 560, k)
    cureng(d, x, 830, 3.0, 1, tanda=False, t=c.t)
    a = c.p(0.15, 0.23)
    if a > 0:
        d.line((250, 620, 420, 685), fill=(90, 60, 30, int(255 * a)), width=4)
        se.teks(d, (240, 595), "sayap dobel", 40, TINTA, alpha=a)
        d.line((800, 640, 600, 735), fill=(90, 60, 30, int(255 * a)), width=4)
        se.teks(d, (820, 615), "2 kursi", 40, TINTA, alpha=a)
        se.teks(d, (300, 1010), "oranye, khas pesawat latih", 32, (90, 60, 30), nama_font="tangan_tipis", alpha=a)
    se.kartu(img, 540, 500, "Yokosuka K5Y", "pesawat latih buatan Jepang", ORANYE_TUA, alpha=c.p(0.05, 0.13),
             tiang=False)
    b = c.p(0.45, 0.53)
    se.teks(d, (330, 1150), "“curen”", 58, (90, 70, 50), nama_font="tangan", alpha=b)
    se.garis_putus(d, [(470, 1150), (600, 1150)], b, (120, 90, 50), tebal=6, putus=14, celah=8, alpha=b)
    se.teks(d, (790, 1150), "CURENG", int(80 * muncul(c, 0.72)) + 1, MERAH, nama_font="caption", stroke=6,
            stroke_warna=PUTIH, alpha=c.p(0.72, 0.78))
    se.teks(d, (540, 1235), "curen = pesawat latih tingkat menengah", 30, (110, 90, 70), nama_font="tangan_tipis",
            alpha=b)
    hdr(img, "Pesawatnya")
    return img


def a_pilot(c):
    img, d = _langit((60, 100, 160), (170, 195, 220))
    awan(d, c.t, 10, 0.5)
    cureng(d, lerp(-200, 1300, c.p(0, 1)), 1150, 1.1, 1, t=c.t, alpha=0.8)
    s = muncul(c, 0.02, 0.15)
    lencana(d, 540, 680, 1.4 * s + 0.01, int(255 * c.p(0.02, 0.1)))
    se.kartu(img, 540, 900, "Agustinus Adisutjipto", "penerbang, mantan ML-KNIL (militer Hindia Belanda)", BIRU,
             alpha=c.p(0.12, 0.2), tiang=False, skala=muncul(c, 0.12))
    se.kartu(img, 540, 1040, "Memilih membela Republik", "", MERAH, alpha=c.p(0.68, 0.75), tiang=False,
             skala=muncul(c, 0.68))
    hdr(img, "Pilotnya")
    return img


def a_terbang(c):
    img, d = _langit((95, 160, 225), (235, 230, 210))
    awan(d, c.t, 14, 0.8)
    tanah(d, 1130)
    hanggar(d, 760, 1020, 230, 110)
    # penonton di pinggir landasan
    rng = random.Random(4)
    for i in range(26):
        ox = 40 + i * 26 + rng.uniform(-6, 6)
        loncat = abs(math.sin(c.t * 4 + i)) * 8 * c.p(0.3, 0.4)
        orang(d, ox, 1300 - loncat, 1.3, rng.choice([(60, 70, 110), (140, 60, 50), (90, 90, 80), (200, 190, 170)]))
    t1 = c.d * 0.25
    if c.t < t1:
        k = se.ease(c.t / t1)
        x, y, s, arah = lerp(120, 880, k), lerp(1170, 760, k ** 1.6), lerp(0.9, 1.3, k), 1
    else:
        ang = -(c.t - t1) * 1.3
        x, y = 540 + 340 * math.cos(ang), 760 + 120 * math.sin(ang)
        s = 1.15 + 0.25 * math.sin(ang)
        arah = 1 if math.sin(ang) > 0 else -1
    cureng(d, x, y, s, arah, t=c.t)
    sk = back_out(c.t / 0.35)
    se.teks(d, (540, 450), "27 OKTOBER 1945", int(84 * sk) + 1, PUTIH, nama_font="caption", stroke=8,
            stroke_warna=(30, 20, 10), alpha=1 - c.p(0.5, 0.55))
    se.kartu(img, 540, 470, "Penerbangan pertama", "pesawat bertanda merah putih", MERAH, alpha=c.p(0.55, 0.62),
             tiang=False, skala=muncul(c, 0.55))
    se.kartu(img, 540, 1000, "Sehari sebelum peringatan Sumpah Pemuda", "", (110, 80, 50), alpha=c.p(0.76, 0.82),
             tiang=False, skala=muncul(c, 0.76))
    hdr(img, "Di atas Maguwo")
    return img


def a_sekolah(c):
    img = LAPANGAN.copy().convert("RGBA")
    se.panel(img, (70, 420, 1010, 1290), alpha=c.p(0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    d.line((170, 560, 170, 1010), fill=(120, 90, 50, int(255 * c.p(0.05, 0.6))), width=6)
    for y, a0 in ((600, 0.05), (860, 0.45)):
        a = c.p(a0, a0 + 0.08)
        d.ellipse((150, y - 20, 190, y + 20), fill=MERAH + (int(255 * a),), outline=(255, 255, 255, int(255 * a)), width=4)
    se.kartu(img, 590, 600, "15 November 1945", "sekolah penerbang dibuka di Maguwo", BIRU, alpha=c.p(0.05, 0.13),
             tiang=False, skala=muncul(c, 0.05))
    se.kartu(img, 590, 860, "9 April 1946", "Angkatan Udara Republik Indonesia berdiri", MERAH, alpha=c.p(0.45, 0.53),
             tiang=False, skala=muncul(c, 0.45))
    lencana(d, 540, 1070, 0.75, int(255 * c.p(0.6, 0.7)))
    # barisan kadet
    for i in range(12):
        x = (120 + i * 70 + c.t * 40) % 900 + 90
        orang(d, x, 1230, 1.2, BIRU, int(255 * c.p(0.1, 0.2)))
    hdr(img, "Sesudahnya")
    return img


RUTE_SERANG = {
    "Semarang": [MAGUWO, (-7.45, 110.25), (-7.15, 110.3), SEMARANG],
    "Ambarawa": [MAGUWO, (-7.55, 110.3), AMBARAWA],
    "Salatiga": [MAGUWO, (-7.55, 110.58), SALATIGA],
}
WARNA_SERANG = {"Semarang": HIJAU_ZAITUN, "Ambarawa": ORANYE, "Salatiga": ORANYE}


def a_serangan(c):
    kamera = Kamera(*cam(-7.42, 110.42, 2.2))
    img, d = peta(kamera)
    se.tint(img, (10, 20, 60), 0.4 * (1 - c.p(0.75, 1.0)))
    d = ImageDraw.Draw(img, "RGBA")
    mx, my = layar(kamera, MAGUWO)
    d.ellipse((mx - 12, my - 12, mx + 12, my + 12), fill=MERAH + (255,), outline=(255, 255, 255, 255), width=3)
    label(d, (mx + 110, my + 30), "Maguwo", 40)
    posisi_label = {"Semarang": (0, -55), "Ambarawa": (-150, 0), "Salatiga": (145, 10)}
    for i, (nama, rute) in enumerate(RUTE_SERANG.items()):
        tx, ty = layar(kamera, rute[-1])
        a = c.p(0.2 + i * 0.05, 0.3 + i * 0.05)
        d.rectangle((tx - 12, ty - 12, tx + 12, ty + 12), fill=(30, 60, 140, int(255 * a)), outline=(255, 255, 255, int(255 * a)), width=3)
        ox, oy = posisi_label[nama]
        label(d, (tx + ox, ty + oy), nama, 40, (20, 40, 110), a, "caption")
        titik = jalur(kamera, rute)
        k = c.p(0.42 + i * 0.03, 0.78)
        se.garis_putus(d, titik, k, (200, 40, 30), tebal=5, putus=14, celah=10, panah=False)
        if 0 < k:
            x, y, sd = terbang_di(titik, k)
            pesawat_atas(d, x, y, sd, 1.3, WARNA_SERANG[nama], jenis="tempur" if nama == "Semarang" else "cureng")
        if k >= 1:
            f = c.p(0.78, 0.9)
            se.glow(img, tx, ty, 50 + 90 * f, (255, 200, 90), 2.5 * (1 - f) + 0.3)
            d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 450, "29 Juli 1947 · subuh", "saat Agresi Militer Belanda I", MERAH,
             alpha=c.p(0.02, 0.1) * (1 - c.p(0.3, 0.35)), tiang=False, skala=muncul(c, 0.02))
    se.kartu(img, 540, 450, "2 Cureng + 1 Guntei", "diterbangkan para kadet", ORANYE_TUA,
             alpha=c.p(0.35, 0.41) * (1 - c.p(0.84, 0.88)), tiang=False, skala=muncul(c, 0.35))
    se.kartu(img, 540, 450, "Ketiganya pulang selamat", "", (40, 120, 70), alpha=c.p(0.88, 0.93), tiang=False,
             skala=muncul(c, 0.88))
    hdr(img, "Serangan udara pertama")
    return img


def a_dakota(c):
    kamera = Kamera(*cam(-7.66, 110.4, 2.2))
    img, d = peta(kamera)
    se.tint(img, (20, 10, 5), 0.2 * c.p(0.4, 0.6))
    d = ImageDraw.Draw(img, "RGBA")
    mx, my = layar(kamera, MAGUWO)
    d.ellipse((mx - 12, my - 12, mx + 12, my + 12), fill=MERAH + (255,), outline=(255, 255, 255, 255), width=3)
    label(d, (mx + 110, my - 10), "Maguwo", 40)
    datang = jalur(kamera, [(-7.15, 109.75), (-7.55, 110.1), (-7.76, 110.3)])
    jatuh_ll = layar(kamera, NGOTO)
    kena = 0.42
    k = c.p(0.0, kena)
    if c.t / c.d < kena:
        x, y, sd = terbang_di(datang, k)
        pesawat_atas(d, x, y, sd, 1.5, (215, 215, 210), jenis="dakota")
    else:
        f = c.p(kena, 0.6)
        x0, y0 = datang[-1]
        x, y = lerp(x0, jatuh_ll[0], f), lerp(y0, jatuh_ll[1], f)
        if f < 1:
            for j in range(10):
                g = j / 10 * f
                sx, sy = lerp(x0, jatuh_ll[0], g), lerp(y0, jatuh_ll[1], g)
                d.ellipse((sx - 14 - j, sy - 14 - j, sx + 14 + j, sy + 14 + j), fill=(70, 65, 60, 120))
            pesawat_atas(d, x, y, 1.0 + c.t * 6, 1.5 * (1 - 0.4 * f), (215, 215, 210), jenis="dakota")
        else:
            se.glow(img, x, y, 90, (255, 150, 60), 2.0 * (1 - c.p(0.6, 0.8)) + 0.4)
            d = ImageDraw.Draw(img, "RGBA")
            d.line((x - 18, y - 18, x + 18, y + 18), fill=(170, 20, 20, 255), width=8)
            d.line((x + 18, y - 18, x - 18, y + 18), fill=(170, 20, 20, 255), width=8)
            label(d, (x - 40, y + 60), "Ngoto, Bantul", 38, (120, 20, 15), c.p(0.62, 0.7))
    # dua pesawat tempur Belanda
    for j in range(2):
        rute = jalur(kamera, [(-7.3 + j * 0.15, 111.0), (-7.6 + j * 0.05, 110.6), (-7.72 + j * 0.06, 110.35)])
        kf = c.p(0.15, kena + 0.02)
        if 0 < kf and c.t / c.d < 0.6:
            fx, fy, sd = terbang_di(rute, kf)
            pesawat_atas(d, fx, fy, sd, 1.1, (90, 100, 120), 1 - c.p(0.5, 0.6), jenis="tempur")
    se.kartu(img, 540, 450, "Dakota VT-CLA", "bawa obat dari Palang Merah Malaya", (120, 120, 130),
             alpha=c.p(0.03, 0.1) * (1 - c.p(0.5, 0.55)), tiang=False, skala=muncul(c, 0.03))
    se.kartu(img, 540, 450, "Ditembak 2 pesawat tempur Belanda", "29 Juli 1947", MERAH, alpha=c.p(0.55, 0.6),
             tiang=False, skala=muncul(c, 0.55))
    se.kartu(img, 540, 1230, "8 orang meninggal, termasuk", "Adisutjipto & Abdulrachman Saleh", (60, 60, 70),
             alpha=c.p(0.6, 0.68), tiang=False, skala=muncul(c, 0.6))
    hdr(img, "Di hari yang sama")
    return img


def a_warisan(c):
    img, d = _langit((120, 170, 220), (235, 230, 215))
    awan(d, c.t, 10, 0.6)
    d.rectangle((0, 1240, W, H), fill=(150, 140, 125, 255))
    d.rectangle((300, 1180, 780, 1240), fill=(110, 100, 90, 255), outline=(60, 50, 40, 255), width=4)
    cureng(d, 540, 1110, 1.6, 1, t=0.0)
    se.kartu(img, 540, 500, "Bandara Adisutjipto", "Maguwo berganti nama, 1952", BIRU, alpha=c.p(0.03, 0.1),
             tiang=False, skala=muncul(c, 0.03))
    se.kartu(img, 540, 760, "Museum Dirgantara Mandala", "Cureng-nya masih dipajang, Yogyakarta", ORANYE_TUA,
             alpha=c.p(0.45, 0.52), tiang=False, skala=muncul(c, 0.45))
    hdr(img, "Sampai sekarang")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    img, d = _langit((40, 70, 130), (150, 170, 200))
    awan(d, c.t, 10, 0.4)
    se.tint(img, (10, 6, 0), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1000), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Langit kita dulu dijaga", 50, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 645), "pakai pesawat bekas & nyali besar", 38, (90, 70, 50), alpha=a)
        cureng(d, 540, 790, 1.5, 1, alpha=a, t=c.t)
        se.teks(d, (540, 935), "Selamat Hari Penerbangan Nasional!", 40, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Dua puluh tujuh Oktober, empat lima. Pesawat bekas Jepang terbang di langit Yogyakarta. "
                   "Tapi tandanya, merah putih! Inilah asal Hari Penerbangan Nasional.", a_hook, transisi=False),
    Adegan("maguwo", "Jepang baru kalah perang. Pangkalan udara Maguwo di Yogyakarta diserahkan ke Indonesia, "
                     "dengan puluhan pesawat bekas. Tapi banyak yang rusak.", a_maguwo),
    Adegan("bengkel", "Sekitar tiga puluh orang turun tangan. Pesawat-pesawat itu dibongkar dan diperbaiki, satu per "
                      "satu.", a_bengkel),
    Adegan("cureng", "Salah satunya pesawat latih bersayap dua. Orang Jepang menyebutnya curen. Lidah kita, Cureng.",
           a_cureng),
    Adegan("pilot", "Pilotnya, Agustinus Adisutjipto, mantan penerbang militer Hindia Belanda yang memilih membela "
                    "republik.", a_pilot),
    Adegan("terbang", "Dua puluh tujuh Oktober, Cureng bertanda merah putih itu lepas landas, dan berputar di atas "
                      "Maguwo. Pesawat merah putih pertama, sehari sebelum peringatan Sumpah Pemuda.", a_terbang),
    Adegan("sekolah", "Sebulan kemudian, dia membuka sekolah penerbang. Dan April empat puluh enam, Angkatan Udara "
                      "Republik Indonesia resmi berdiri.", a_sekolah),
    Adegan("serangan", "Dua puluh sembilan Juli empat puluh tujuh, saat agresi militer Belanda. Subuh-subuh, dua Cureng "
                       "dan satu Guntei, dipiloti para kadet, menyerang pos Belanda di Semarang, Salatiga, dan Ambarawa. "
                       "Semua pulang selamat.", a_serangan),
    Adegan("dakota", "Tapi hari itu juga, Dakota pembawa obat dari Palang Merah Malaya ditembak jatuh Belanda. Delapan "
                     "orang meninggal, termasuk Adisutjipto dan Abdulrachman Saleh.", a_dakota),
    Adegan("warisan", "Kini namanya jadi nama bandara di Yogyakarta. Dan Cureng-nya, masih dipajang di Museum "
                      "Dirgantara Mandala.", a_warisan),
    Adegan("penutup", "Jadi, langit kita dulu dijaga pakai pesawat bekas, dan nyali besar. Selamat Hari Penerbangan "
                      "Nasional! Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
