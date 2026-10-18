"""Shorts ±90 detik: Resolusi Jihad 22 Oktober 1945 — kenapa Hari Santri jatuh tanggal 22 Oktober.

Peta Jawa (radius 94 km di sekitar Surabaya, rombongan ulama, laskar santri) + denah kota Surabaya 1945
(pendaratan Brigade 49, Jembatan Merah, gempuran 10 November) + kartu kalender.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Kamera, Peta, Adegan, back_out, clamp, lerp

NAMA_FILE = "resolusi-jihad-1945-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "RESOLUSI JIHAD 1945"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
HIJAU = (30, 120, 70)
BIRU = (40, 80, 150)
INGGRIS = (60, 95, 170)

# ------------------------------------------------------------------ peta Jawa (garis pantai lebih rinci dari peta_data)

JAWA_D = [(-6.75, 105.2), (-6.05, 105.9), (-6.0, 106.1), (-6.1, 106.8), (-5.93, 107.0), (-6.2, 107.6), (-6.25, 108.3),
          (-6.7, 108.55), (-6.85, 109.1), (-6.88, 109.7), (-6.95, 110.4), (-6.6, 110.65), (-6.4, 110.9),
          (-6.65, 111.15), (-6.7, 111.4), (-6.88, 112.05), (-6.88, 112.4), (-7.05, 112.6), (-7.18, 112.7),
          (-7.45, 112.83), (-7.62, 112.92), (-7.72, 113.2), (-7.7, 113.6), (-7.7, 114.0), (-7.8, 114.42),
          (-8.2, 114.4), (-8.75, 114.6), (-8.6, 114.2), (-8.45, 113.6), (-8.35, 113.2), (-8.4, 112.6),
          (-8.3, 112.1), (-8.25, 111.1), (-8.15, 110.6), (-8.0, 110.3), (-7.75, 109.0), (-7.7, 108.65),
          (-7.6, 107.8), (-7.0, 106.5), (-6.85, 106.3), (-6.8, 105.4)]
MADURA = [(-6.95, 112.78), (-7.1, 112.8), (-7.16, 112.95), (-7.2, 113.2), (-7.15, 113.5), (-7.1, 113.9),
          (-7.05, 114.1), (-6.9, 114.1), (-6.85, 113.7), (-6.88, 113.2), (-6.9, 112.95)]

print("  menyiapkan peta Jawa...")
PETA = Peta(103.0, 118.5, -17.0, 1.5, 200, [], [(-7.3, 110.4, 0.35), (-7.9, 112.9, 0.4), (-7.0, 107.6, 0.4),
                                                  (-7.5, 109.2, 0.3), (-7.9, 111.5, 0.35), (-8.0, 114.0, 0.35)],
            seed=45, darat=[JAWA_D, MADURA, pd.SUMATRA, pd.BALI, pd.LOMBOK, pd.KALIMANTAN])

SURABAYA = (-7.25, 112.74)
JAKARTA = (-6.15, 106.83)
TEBUIRENG = (-7.6, 112.24)
R94 = 94 / 111.0  # derajat
KOTA_NU = [(-6.15, 106.83), (-6.9, 107.6), (-6.72, 108.55), (-6.97, 110.42), (-7.8, 110.37), (-7.57, 110.82),
           (-7.82, 112.0), (-7.6, 112.24), (-7.98, 112.63), (-6.9, 112.05), (-7.03, 112.75), (-7.0, 113.86),
           (-8.2, 114.37), (-7.65, 112.9), (-7.17, 113.2), (-8.17, 113.7)]
PESANTREN = [(-7.6, 112.24), (-7.82, 112.0), (-7.98, 112.63), (-7.65, 112.9), (-6.9, 112.05), (-7.03, 112.75),
             (-7.4, 111.45), (-8.1, 112.15), (-7.17, 113.2), (-7.75, 113.4), (-7.5, 112.45), (-8.17, 113.7),
             (-7.0, 113.86), (-7.87, 111.47)]
LABEL_JAWA = {"JAWA": (-7.45, 109.6), "MADURA": (-6.85, 113.35), "Laut Jawa": (-5.4, 111.0),
              "Samudra Hindia": (-9.6, 110.0)}


# ------------------------------------------------------------------ helper

def cam(lat, lon, zoom):
    x, y = PETA.px(lat, lon)
    return (x, y, zoom)


def gambar_peta(kamera):
    img = se.render_peta(PETA, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(kamera, ll):
    return kamera.layar(*PETA.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def kartu(img, cx, cy, judul, sub="", warna=MERAH, **kw):
    """se.kartu, tapi digeser supaya tidak keluar layar."""
    lw = max(se.font("tangan", 34).getlength(judul), se.font("tangan_tipis", 24).getlength(sub) if sub else 0) + 56
    sk = kw.get("skala", 1.0)
    setengah = lw / 2 * max(sk, 1.0) + 30
    cx = clamp(cx, setengah, W - setengah)
    se.kartu(img, cx, cy, judul, sub, warna, **kw)


def muncul(c, a):
    k = c.t / c.d
    return back_out((k - a) / 0.1) if k > a else 0.0


def cincin(d, x, y, r, warna, alpha, tebal=8):
    if alpha <= 0.01 or r <= 1:
        return
    d.ellipse((x - r, y - r, x + r, y + r), outline=tuple(warna) + (int(255 * alpha),), width=tebal)


def denyut(d, x, y, t, alpha=1.0, warna=(200, 40, 30), skala=1.0):
    for i in range(3):
        f = (t * 0.8 + i / 3) % 1.0
        cincin(d, x, y, 14 + f * 120 * skala, warna, (1 - f) * 0.9 * alpha, 6)
    a = int(255 * alpha)
    d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=tuple(warna) + (a,), outline=(255, 255, 255, a), width=3)


def lingkaran_94(img, kamera, k, alpha=1.0, isi=True):
    """Lingkaran radius 94 km di sekitar Surabaya; k = progres membesar."""
    if alpha <= 0.01 or k <= 0:
        return
    x, y = layar(kamera, SURABAYA)
    r = R94 * PETA.skala * kamera.zoom * k
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    if isi:
        dl.ellipse((x - r, y - r, x + r, y + r), fill=(200, 52, 44, int(70 * alpha)))
    # garis putus-putus melingkar
    n = 48
    for i in range(n):
        if i % 2:
            continue
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        dl.arc((x - r, y - r, x + r, y + r), math.degrees(a0), math.degrees(a1), fill=(170, 25, 20, int(255 * alpha)),
               width=8)
    img.alpha_composite(lap)


def hdr(img, sub="Surabaya, Oktober 1945", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def kapal(d, x, y, s=1.0, alpha=1.0, warna=(85, 95, 110)):
    """Kapal perang kecil (dari samping, menghadap kanan)."""
    a = int(255 * alpha)
    d.polygon([(x - 60 * s, y - 8 * s), (x + 64 * s, y - 8 * s), (x + 48 * s, y + 14 * s), (x - 52 * s, y + 14 * s)],
              fill=tuple(warna) + (a,), outline=(25, 25, 30, a))
    d.rectangle((x - 30 * s, y - 24 * s, x + 18 * s, y - 8 * s), fill=se.lerp_rgb(warna, (255, 255, 255), 0.25) + (a,),
                outline=(25, 25, 30, a))
    d.rectangle((x - 16 * s, y - 40 * s, x - 2 * s, y - 24 * s), fill=se.lerp_rgb(warna, (0, 0, 0), 0.2) + (a,))
    d.line((x + 18 * s, y - 16 * s, x + 46 * s, y - 22 * s), fill=(25, 25, 30, a), width=max(2, int(5 * s)))


def pesawat(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    c = (35, 35, 45, a)
    d.polygon([(x - 50 * s, y), (x + 50 * s, y - 4 * s), (x + 56 * s, y + 2 * s), (x - 50 * s, y + 8 * s)], fill=c)
    d.polygon([(x - 6 * s, y), (x + 14 * s, y - 46 * s), (x + 26 * s, y - 46 * s), (x + 14 * s, y)], fill=c)
    d.polygon([(x - 6 * s, y + 6 * s), (x + 14 * s, y + 50 * s), (x + 26 * s, y + 50 * s), (x + 14 * s, y + 6 * s)], fill=c)
    d.polygon([(x - 50 * s, y + 2 * s), (x - 42 * s, y - 20 * s), (x - 34 * s, y - 20 * s), (x - 36 * s, y + 2 * s)], fill=c)


def kalender(img, cx, cy, atas, angka, bulan, bawah, alpha=1.0, skala=1.0, warna=HIJAU):
    """Lembar kalender meja."""
    if alpha <= 0.01 or skala <= 0.01:
        return
    w, h = 520, 560
    lap = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rounded_rectangle((28, 32, w + 28, h + 32), 30, fill=(0, 0, 0, 110))
    d.rounded_rectangle((20, 20, w + 20, h + 20), 30, fill=(250, 244, 228, 255), outline=(60, 45, 30, 255), width=6)
    d.rounded_rectangle((20, 20, w + 20, 150), 30, fill=tuple(warna) + (255,))
    d.rectangle((20, 110, w + 20, 150), fill=tuple(warna) + (255,))
    for rx in (130, w - 90):
        d.ellipse((rx - 14, 6, rx + 14, 34), fill=(60, 45, 30, 255))
    d.text((w / 2 + 20, 86), atas, font=se.font("caption", 46), fill=PUTIH, anchor="mm")
    d.text((w / 2 + 20, 300), angka, font=se.font("caption", 220), fill=TINTA, anchor="mm")
    d.text((w / 2 + 20, 450), bulan, font=se.font("judul", 60), fill=(150, 40, 30), anchor="mm")
    d.text((w / 2 + 20, 525), bawah, font=se.font("ui", 34), fill=(90, 70, 50), anchor="mm")
    if skala != 1.0:
        lap = lap.resize((max(1, int(lap.width * skala)), max(1, int(lap.height * skala))), Image.BICUBIC)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def _gradasi(atas, bawah):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (np.array(atas, np.float32) * (1 - g) + np.array(bawah, np.float32) * g).repeat(W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    return img, ImageDraw.Draw(img, "RGBA")


# ------------------------------------------------------------------ denah kota Surabaya 1945 (ilustrasi)

LAUT_Y = 560  # di atas garis ini = Selat Madura
KALIMAS = [(560, LAUT_Y - 10), (575, 660), (548, 760), (590, 860), (570, 960), (610, 1060), (585, 1180), (620, 1320),
           (600, 1500)]
JEMBATAN = (571, 950)
INTERNATIO = (690, 940)


@lru_cache(maxsize=1)
def _denah():
    img = se.latar_tekstur(W, H, 21, bukit=[(200, 1350, 260, 120), (900, 1250, 220, 110)]).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # laut
    tepi = [(0, LAUT_Y + 20)] + [(x, LAUT_Y + 14 * math.sin(x / 70)) for x in range(0, W + 1, 30)] + [(W, 0), (0, 0)]
    d.polygon(tepi, fill=(44, 64, 98, 255))
    d.line([(x, LAUT_Y + 14 * math.sin(x / 70)) for x in range(0, W + 1, 30)], fill=TINTA + (255,), width=5)
    # dermaga Tanjung Perak
    for x0 in (330, 640):
        d.rectangle((x0, LAUT_Y - 70, x0 + 140, LAUT_Y + 10), fill=(150, 130, 100, 255), outline=TINTA + (255,), width=4)
    # blok-blok kota
    rng = random.Random(3)
    for gy in range(640, 1340, 70):
        for gx in range(60, 1040, 90):
            if abs(gx + 35 - 590) < 70:
                continue
            if rng.random() < 0.2:
                continue
            w, h = rng.randint(50, 72), rng.randint(40, 55)
            d.rectangle((gx, gy, gx + w, gy + h), fill=(190, 160, 115, 255), outline=(120, 90, 55, 255), width=2)
    # jalan
    for gy in (700, 910, 1120):
        d.line((0, gy, W, gy + 20), fill=(235, 220, 185, 255), width=14)
    # sungai Kalimas
    d.line(KALIMAS, fill=(70, 100, 140, 255), width=34, joint="curve")
    # Jembatan Merah
    jx, jy = JEMBATAN
    d.rectangle((jx - 40, jy - 8, jx + 40, jy + 8), fill=(190, 40, 30, 255), outline=(60, 20, 10, 255), width=3)
    # Gedung Internatio
    ix, iy = INTERNATIO
    d.rectangle((ix - 45, iy - 40, ix + 45, iy + 30), fill=(235, 225, 200, 255), outline=TINTA + (255,), width=4)
    d.polygon([(ix - 45, iy - 40), (ix, iy - 70), (ix + 45, iy - 40)], fill=(160, 70, 50, 255), outline=TINTA + (255,))
    return img


def denah(c, label_alpha=1.0):
    img = _denah().copy()
    d = ImageDraw.Draw(img, "RGBA")
    label(d, (400, 615), "Tanjung Perak", 34, TINTA, label_alpha)
    label(d, (500, 1240), "Kalimas", 34, (30, 50, 90), label_alpha)
    label(d, (420, 990), "Jembatan Merah", 32, TINTA, label_alpha)
    return img, d


def ombak(d, t, alpha=1.0):
    for i in range(14):
        x = (i * 83 + t * 30) % W
        y = 400 + (i * 37) % 130
        d.arc((x - 18, y - 6, x + 18, y + 6), 200, 340, fill=(200, 220, 240, int(160 * alpha)), width=3)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    kamera = se.kamera_antara(cam(-7.5, 112.5, 0.9), cam(-7.4, 112.6, 1.35), c.p(0, 1))
    img, d = gambar_peta(kamera)
    se.tint(img, (15, 8, 0), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    lingkaran_94(img, kamera, back_out(c.p(0.05, 0.4)), 1.0)
    d = ImageDraw.Draw(img, "RGBA")
    x, y = layar(kamera, SURABAYA)
    denyut(d, x, y, c.t, c.p(0.0, 0.08))
    label(d, (x, y - 50), "Surabaya", 42, TINTA, c.p(0.02, 0.1))
    s = muncul(c, 0.0)
    se.teks(d, (540, 470), "SATU SERUAN ULAMA", int(78 * s) + 1, (255, 235, 180), nama_font="caption", stroke=8,
            stroke_warna=(40, 25, 10))
    s2 = muncul(c, 0.5)
    if s2 > 0:
        se.teks(d, (540, 1170), "94 KM", int(190 * s2) + 1, (255, 235, 180), nama_font="caption", stroke=10,
                stroke_warna=(40, 25, 10))
    hdr(img, alpha=c.p(0.8, 0.95))
    return img


def a_tren(c):
    img, d = _gradasi((20, 70, 45), (10, 35, 25))
    # pola bintang segi delapan samar
    for i in range(18):
        x, y = (i * 263) % W, 380 + (i * 397) % 1000
        r = 40
        pts = [(x + r * math.cos(k * math.pi / 4 + (k % 2) * 0.0) * (1 if k % 2 == 0 else 0.6),
                y + r * math.sin(k * math.pi / 4) * (1 if k % 2 == 0 else 0.6)) for k in range(8)]
        d.polygon(pts, outline=(230, 200, 120, 40))
    sk = muncul(c, 0.02) or 0.01
    kalender(img, 540, 780, "KAMIS", "22", "OKTOBER", "2026", alpha=c.p(0.02, 0.1), skala=sk * 0.95)
    kartu(img, 540, 1160, "Hari Santri", "diperingati tiap 22 Oktober", HIJAU, alpha=c.p(0.15, 0.25), tiang=False)
    s = muncul(c, 0.4)
    if s > 0:
        se.teks(d, (540, 430), "kok 22 Oktober?", int(76 * s) + 1, (255, 235, 180), nama_font="caption", stroke=8,
                stroke_warna=(20, 30, 15))
    if c.p(0.68, 0.78) > 0:
        se.tint(img, (20, 10, 0), 0.82 * c.p(0.68, 0.78))
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 780), "Surabaya, 1945", 86, (255, 220, 160), nama_font="caption", stroke=8,
                stroke_warna=(30, 15, 5), alpha=c.p(0.7, 0.8))
    hdr(img, "Kamis ini: Hari Santri")
    return img


def a_latar(c):
    kamera = se.kamera_antara(cam(-7.0, 109.6, 0.56), cam(-7.0, 110.2, 0.6), c.p(0, 1))
    img, d = gambar_peta(kamera)
    for nama, ll in LABEL_JAWA.items():
        x, y = layar(kamera, ll)
        if nama.isupper():
            label(d, (x, y), nama, 40, TINTA, 0.85)
        else:
            se.teks(d, (x, y), nama, 32, (215, 225, 240), nama_font="tangan", stroke=4, stroke_warna=(20, 30, 50), alpha=0.85)
    kartu(img, 540, 470, "17 Agustus 1945: merdeka", "baru dua bulan", MERAH, alpha=c.p(0.02, 0.1), tiang=False,
          skala=muncul(c, 0.02) or 0.01)
    # kapal Sekutu datang dari utara ke Jakarta
    for j in range(3):
        k = c.p(0.25 + j * 0.05, 0.6 + j * 0.05)
        if k <= 0:
            continue
        ll = (lerp(-2.5, -5.9 - j * 0.15, k), lerp(105.6 + j * 0.6, 106.6 + j * 0.3, k))
        x, y = layar(kamera, ll)
        kapal(d, x, y, 0.75, min(1.0, k * 4))
    x, y = layar(kamera, JAKARTA)
    a = c.p(0.55, 0.62)
    if a > 0:
        denyut(d, x, y, c.t, a, BIRU)
        label(d, (x + 40, y + 50), "Jakarta", 34, TINTA, a)
        kartu(img, 540, 1120, "Sekutu mendarat · akhir Sept 1945", "Belanda (NICA) ikut membonceng", BIRU, alpha=a,
              tiang=False, skala=muncul(c, 0.55) or 0.01)
    s = muncul(c, 0.8)
    if s > 0:
        se.teks(d, (540, 780), "mau balik berkuasa?", int(66 * s) + 1, (255, 235, 180), nama_font="caption", stroke=8,
                stroke_warna=(40, 25, 10))
    hdr(img, "Setelah proklamasi")
    return img


def a_rapat(c):
    kamera = se.kamera_antara(cam(-7.2, 110.0, 0.56), cam(-7.3, 111.3, 0.66), c.p(0, 0.6))
    img, d = gambar_peta(kamera)
    sx, sy = layar(kamera, SURABAYA)
    k = c.p(0.05, 0.5)
    for i, ll in enumerate(KOTA_NU):
        x, y = layar(kamera, ll)
        kk = clamp(k * 1.3 - i * 0.02)
        se.garis_putus(d, [(x, y), (sx, sy)], kk, (30, 110, 60), tebal=5, putus=14, celah=10, alpha=0.8, panah=False)
        px, py = lerp(x, sx, kk), lerp(y, sy, kk)
        if 0 < kk < 1:
            se.prajurit(d, px, py, (30, 140, 70), 1.2)
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(30, 110, 60, 220))
    denyut(d, sx, sy, c.t, 1.0, HIJAU)
    label(d, (sx + 10, sy + 55), "Surabaya", 38, TINTA)
    for nama, ll in (("JAWA", (-7.45, 109.6)), ("MADURA", (-6.85, 113.35))):
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 36, TINTA, 0.8)
    kartu(img, 540, 470, "21–22 Oktober 1945", "konsul NU se-Jawa & Madura rapat di Surabaya", HIJAU,
          alpha=c.p(0.02, 0.1), tiang=False, skala=muncul(c, 0.02) or 0.01)
    kartu(img, 540, 1050, "KH Hasyim Asy'ari", "Rais Akbar NU · pengasuh Pesantren Tebuireng", (90, 70, 50),
          alpha=c.p(0.5, 0.58), tiang=False, skala=muncul(c, 0.5) or 0.01)
    a = c.p(0.72, 0.8)
    if a > 0:
        se.panel(img, (190, 1150, 890, 1290), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1220), "RESOLUSI JIHAD", int(64 * (muncul(c, 0.72) or 0.01)) + 1, (150, 30, 20),
                nama_font="judul", alpha=a)
    hdr(img)
    return img


def a_isi(c):
    kamera = se.kamera_antara(cam(-7.6, 112.6, 1.25), cam(-7.7, 112.74, 1.4), c.p(0, 1))
    img, d = gambar_peta(kamera)
    lingkaran_94(img, kamera, back_out(c.p(0.3, 0.5)), 1.0)
    d = ImageDraw.Draw(img, "RGBA")
    x, y = layar(kamera, SURABAYA)
    denyut(d, x, y, c.t)
    label(d, (x, y - 50), "Surabaya", 38, TINTA)
    a = c.p(0.35, 0.45)
    if a > 0:
        r = R94 * PETA.skala * kamera.zoom
        d.line((x, y, x + r * 0.71, y - r * 0.71), fill=(150, 25, 20, int(255 * a)), width=6)
        se.teks(d, (x + r * 0.35 + 70, y - r * 0.35 - 20), "94 km", 46, (150, 25, 20), nama_font="caption", stroke=5,
                stroke_warna=KREM_LABEL, alpha=a)
    kartu(img, 540, 470, "Membela tanah air: WAJIB", "bagi tiap muslim", MERAH, alpha=c.p(0.02, 0.1), tiang=False,
          skala=muncul(c, 0.02) or 0.01)
    kartu(img, 540, 1090, "Dalam radius 94 km", "wajib ikut berjuang (fardu ain)", MERAH, alpha=c.p(0.5, 0.58),
          tiang=False)
    kartu(img, 540, 1220, "Di luar radius", "wajib membantu (fardu kifayah)", (90, 70, 50), alpha=c.p(0.78, 0.85),
          tiang=False)
    hdr(img, "Isi seruannya")
    return img


def a_sebar(c):
    kamera = Kamera(*cam(-7.55, 112.6, 1.05))
    img, d = gambar_peta(kamera)
    lingkaran_94(img, kamera, 1.0, 0.5, isi=False)
    d = ImageDraw.Draw(img, "RGBA")
    sx, sy = layar(kamera, SURABAYA)
    rng = random.Random(9)
    for i, ll in enumerate(PESANTREN):
        x, y = layar(kamera, ll)
        a = c.p(0.03 + i * 0.025, 0.08 + i * 0.025)
        if a <= 0:
            continue
        se.ikon_masjid(d, x, y, 0.55, a)
        # rombongan laskar (titik hijau) bergerak ke Surabaya
        for j in range(3):
            f = ((c.t * 0.18 + j / 3 + rng.random()) % 1.0) * c.p(0.4, 0.5)
            if f <= 0:
                continue
            px, py = lerp(x, sx, f), lerp(y, sy, f)
            se.prajurit(d, px + (j - 1) * 10, py, (30, 140, 70), 1.0, a)
    denyut(d, sx, sy, c.t, 1.0, (200, 40, 30))
    label(d, (sx, sy - 50), "Surabaya", 38, TINTA)
    kartu(img, 540, 470, "Dari pesantren ke pesantren", "seruan menyebar cepat", HIJAU, alpha=c.p(0.02, 0.1),
          tiang=False, skala=muncul(c, 0.02) or 0.01)
    kartu(img, 540, 1200, "Laskar Hizbullah & Sabilillah", "santri dan kiai bergerak ke Surabaya", HIJAU,
          alpha=c.p(0.4, 0.48), tiang=False, skala=muncul(c, 0.4) or 0.01)
    hdr(img, "Akhir Oktober 1945")
    return img


def a_inggris(c):
    img, d = denah(c)
    ombak(d, c.t)
    # kapal-kapal di selat
    for j, (x, y) in enumerate(((220, 470), (560, 440), (880, 480))):
        kapal(d, x + math.sin(c.t + j) * 6, y, 1.1, c.p(0.02 + j * 0.04, 0.1 + j * 0.04))
    # pasukan Inggris (biru) turun di dermaga lalu menyebar
    rng = random.Random(4)
    k = c.p(0.25, 0.85)
    for i in range(60):
        x0, y0 = rng.choice(((400, 520), (710, 520)))
        tx, ty = rng.uniform(120, 980), rng.uniform(640, 1150)
        kk = clamp(k * 1.4 - i / 60 * 0.4)
        if kk <= 0:
            continue
        se.prajurit(d, lerp(x0, tx, kk), lerp(y0, ty, kk), INGGRIS, 1.4)
    kartu(img, 540, 1150, "25 Oktober 1945", "Brigade 49 Inggris mendarat", BIRU, alpha=c.p(0.05, 0.13), tiang=False,
          skala=muncul(c, 0.05) or 0.01)
    s = muncul(c, 0.5)
    if s > 0:
        se.teks(d, (540, 1330), "± 6.000 tentara", int(80 * s) + 1, (255, 235, 180), nama_font="caption", stroke=8,
                stroke_warna=(30, 20, 10))
    hdr(img, "Surabaya, 25 Oktober 1945")
    return img


def a_tempur(c):
    img, d = denah(c)
    ombak(d, c.t)
    rng = random.Random(4)
    biru = []
    for i in range(60):
        rng.choice(((400, 520), (710, 520)))
        biru.append((rng.uniform(120, 980), rng.uniform(640, 1150)))
    rng2 = random.Random(11)
    k = c.p(0.05, 0.45)
    for i, (x, y) in enumerate(biru):
        # terdesak: merapat ke beberapa titik pertahanan
        pos = ((300, 760), (700, 900), (820, 1080))[i % 3]
        bx, by = lerp(x, pos[0] + rng2.uniform(-60, 60), k), lerp(y, pos[1] + rng2.uniform(-50, 50), k)
        se.prajurit(d, bx, by, INGGRIS, 1.4)
    # pejuang (merah) mengepung dari pinggir
    rng3 = random.Random(12)
    for i in range(90):
        sud = rng3.uniform(0, 2 * math.pi)
        x0, y0 = 540 + math.cos(sud) * 700, 980 + math.sin(sud) * 520
        pos = ((300, 760), (700, 900), (820, 1080))[i % 3]
        tx, ty = pos[0] + math.cos(sud) * rng3.uniform(110, 190), pos[1] + math.sin(sud) * rng3.uniform(90, 160)
        kk = clamp(c.p(0.0, 0.45) * 1.3 - i / 90 * 0.3)
        x, y = lerp(x0, tx, kk), lerp(y0, ty, kk)
        if LAUT_Y + 30 < y < 1350 and 0 < x < W:
            se.prajurit(d, x, y, (200, 40, 30), 1.3)
    # kilatan tembakan
    if 0.1 < c.t / c.d < 0.5:
        for j in range(4):
            if math.sin(c.t * 9 + j * 2.1) > 0.6:
                px, py = ((300, 760), (700, 900), (820, 1080), (420, 1000))[j]
                se.glow(img, px, py, 70, (255, 200, 90), 1.2)
    d = ImageDraw.Draw(img, "RGBA")
    kartu(img, 540, 1240, "28 Oktober: pertempuran pecah", "pasukan Inggris terdesak", MERAH,
          alpha=c.p(0.02, 0.1) * (1 - c.p(0.5, 0.56)),
          tiang=False, skala=muncul(c, 0.02) or 0.01)
    b = c.p(0.55, 0.62)
    if b > 0:
        ix, iy = INTERNATIO
        denyut(d, ix, iy, c.t, b, (200, 40, 30))
        kartu(img, ix + 40, iy - 90, "Brigadir A.W.S. Mallaby", "tewas 30 Okt, dekat Jembatan Merah", BIRU, alpha=b,
              skala=muncul(c, 0.55), coret=c.p(0.68, 0.8))
        kartu(img, 540, 1240, "siapa penembaknya?", "sampai sekarang masih diperdebatkan", (90, 70, 50),
              alpha=c.p(0.8, 0.88), tiang=False)
    hdr(img, "28 – 30 Oktober 1945")
    return img


def a_10nov(c):
    img, d = denah(c, label_alpha=0.6)
    se.tint(img, (60, 10, 0), 0.25 + 0.15 * c.p(0, 0.3))
    d = ImageDraw.Draw(img, "RGBA")
    for j, (x, y) in enumerate(((180, 470), (480, 450), (800, 480))):
        kapal(d, x, y, 1.2, 1.0, (70, 75, 90))
        if math.sin(c.t * 5 + j * 2) > 0.7:
            se.glow(img, x + 60, y - 20, 50, (255, 210, 120), 1.4)
            d = ImageDraw.Draw(img, "RGBA")
    # pesawat lewat
    for j in range(2):
        f = (c.t * 0.25 + j * 0.5) % 1.0
        pesawat(d, lerp(-80, W + 80, f), 650 + j * 120, 1.0, c.p(0.2, 0.3))
    # ledakan di kota
    rng = random.Random(int(c.t * 4))
    if c.t / c.d > 0.15:
        for j in range(5):
            x, y = rng.uniform(100, 980), rng.uniform(700, 1300)
            se.glow(img, x, y, rng.uniform(50, 100), (255, 150, 60), 1.6)
        d = ImageDraw.Draw(img, "RGBA")
    s = muncul(c, 0.02)
    se.teks(d, (540, 900), "10 NOVEMBER", int(118 * s) + 1, (255, 235, 180), nama_font="caption", stroke=10,
            stroke_warna=(40, 15, 5))
    se.teks(d, (540, 1020), "1945", int(96 * s) + 1, (255, 235, 180), nama_font="caption", stroke=9,
            stroke_warna=(40, 15, 5))
    kartu(img, 540, 1170, "Digempur dari darat, laut, udara", "ribuan pejuang gugur", MERAH, alpha=c.p(0.3, 0.38),
          tiang=False)
    kartu(img, 540, 1290, "HARI PAHLAWAN", "", (180, 140, 40), alpha=c.p(0.72, 0.8), tiang=False,
          skala=muncul(c, 0.72) or 0.01)
    hdr(img, "Pertempuran Surabaya")
    return img


def a_keppres(c):
    img, d = _gradasi((20, 70, 45), (10, 35, 25))
    k = c.p(0.15, 0.45)
    tahun = int(lerp(1945, 2015, k))
    kalender(img, 540, 760, "RESOLUSI JIHAD" if k < 1 else "HARI SANTRI", "22", "OKTOBER", str(tahun),
             alpha=c.p(0.02, 0.1), skala=(muncul(c, 0.02) or 0.01) * 0.95, warna=HIJAU if k < 1 else (180, 140, 40))
    s = muncul(c, 0.12)
    if s > 0 and k < 1:
        se.teks(d, (540, 430), "70 tahun kemudian…", int(64 * s) + 1, (255, 235, 180), nama_font="caption",
                stroke=7, stroke_warna=(20, 30, 15))
    kartu(img, 540, 1140, "Keppres No. 22 Tahun 2015", "22 Oktober ditetapkan sebagai Hari Santri", (180, 140, 40),
          alpha=c.p(0.5, 0.58), tiang=False, skala=muncul(c, 0.5) or 0.01)
    hdr(img, "Dari 1945 ke 2015")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(-7.3, 111.0, 0.62))
    img, d = gambar_peta(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1000), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Hari Santri bukan cuma", 48, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 635), "soal sarung dan peci", 48, TINTA, nama_font="judul", alpha=a)
        se.ikon_masjid(d, 540, 790, 1.8, a)
        se.teks(d, (540, 930), "ada keberanian yang menjaga merdeka", 40, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Satu seruan ulama, bikin para santri turun ke medan perang. Kuncinya cuma satu angka: sembilan "
                   "puluh empat kilometer.", a_hook, transisi=False),
    Adegan("tren", "Kamis ini, dua puluh dua Oktober, kita peringati Hari Santri. Tapi kok tanggal itu? "
                   "Jawabannya ada di Surabaya, tahun sembilan belas empat puluh lima.", a_tren),
    Adegan("latar", "Waktu itu Indonesia baru dua bulan merdeka. Tentara Sekutu mulai mendarat, dan Belanda lewat NICA "
                    "ikut membonceng. Mereka mau balik berkuasa.", a_latar),
    Adegan("rapat", "Tanggal dua puluh satu sampai dua puluh dua Oktober, wakil NU se-Jawa dan Madura rapat di "
                    "Surabaya. Lahirlah seruan Kiai Haji Hasyim Asy'ari: Resolusi Jihad.",
           a_rapat),
    Adegan("isi", "Isinya: membela tanah air dari penjajah itu wajib. Yang paling dikenal: muslim dalam radius "
                  "sembilan puluh empat kilometer, wajib ikut berjuang. Yang lebih jauh, "
                  "wajib membantu.", a_isi),
    Adegan("sebar", "Seruan ini menyebar dari pesantren ke pesantren. Santri dan kiai bergabung di laskar Hizbullah "
                    "dan Sabilillah, lalu bergerak ke Surabaya.", a_sebar, transisi=False),
    Adegan("inggris", "Tiga hari kemudian, sekitar enam ribu tentara Inggris dari Brigade empat puluh sembilan "
                      "mendarat di Surabaya.", a_inggris),
    Adegan("tempur", "Dua puluh delapan Oktober, pertempuran pecah, dan pasukan Inggris terdesak. Dua hari kemudian, "
                     "komandannya, Brigadir Mallaby, tewas di dekat Jembatan Merah.", a_tempur, transisi=False),
    Adegan("10nov", "Inggris membalas. Sepuluh November, Surabaya digempur dari darat, laut, dan udara. Ribuan "
                    "pejuang gugur. Itulah asal Hari Pahlawan.", a_10nov),
    Adegan("keppres", "Tujuh puluh tahun kemudian, tahun dua ribu lima belas, tanggal Resolusi Jihad ditetapkan "
                      "sebagai Hari Santri.", a_keppres),
    Adegan("penutup", "Jadi, Hari Santri bukan cuma soal sarung dan peci. Ada keberanian yang ikut menjaga kemerdekaan "
                      "kita. Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
