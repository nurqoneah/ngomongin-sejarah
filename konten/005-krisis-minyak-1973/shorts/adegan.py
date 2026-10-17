"""Shorts ±90 detik: Krisis Minyak 1973 (embargo minyak Arab) — saat dunia isi bensin pakai ganjil genap.

Peta Timur Tengah + peta Indonesia + adegan ilustrasi (antrean SPBU, jalan tol Belanda yang kosong, grafik harga).
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

NAMA_FILE = "krisis-minyak-1973-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "KRISIS MINYAK 1973"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU = (30, 80, 150)
HIJAU = (40, 130, 70)
MINYAK = (35, 30, 30)

# ------------------------------------------------------------------ peta Timur Tengah (laut digambar di atas daratan)

LAUT_TENGAH = [(40.5, 25.0), (40.0, 26.2), (39.0, 26.8), (38.2, 26.3), (37.5, 27.2), (36.7, 28.0), (36.6, 30.5),
               (36.2, 30.6), (36.8, 31.5), (36.6, 34.6), (36.9, 35.9), (36.0, 35.9), (34.5, 35.9), (33.5, 35.4),
               (32.8, 35.0), (31.5, 34.5), (31.2, 33.0), (31.5, 31.5), (31.1, 29.9), (31.0, 28.0), (31.6, 25.1),
               (32.6, 23.0), (32.1, 20.1), (30.4, 19.0), (31.0, 15.5), (32.0, 13.0), (37.5, 13.0),
               (38.0, 16.0), (39.5, 17.5), (40.0, 19.5), (40.5, 22.5)]
LAUT_HITAM = [(41.2, 29.1), (41.7, 32.0), (42.0, 35.0), (41.4, 37.5), (41.0, 39.5), (41.6, 41.6), (43.0, 41.0),
              (44.6, 37.5), (45.2, 36.5), (46.0, 34.0), (45.0, 33.0), (44.5, 33.5), (45.5, 30.0), (43.5, 28.5),
              (42.0, 28.0)]
LAUT_MERAH = [(28.0, 33.3), (27.9, 34.4), (26.0, 36.5), (24.0, 37.6), (22.0, 39.0), (20.0, 40.0), (17.0, 42.0),
              (15.0, 42.8), (12.6, 43.4), (12.0, 43.4), (11.0, 44.0), (10.5, 45.0), (11.3, 49.0), (11.8, 51.2),
              (10.0, 50.8), (5.0, 48.0), (2.0, 45.3), (-1.5, 41.6), (-4.0, 40.5), (-4.0, 66.0), (22.5, 66.0), (22.5, 59.8), (18.5, 56.5), (16.8, 52.0),
              (14.5, 49.0), (12.8, 45.0), (12.5, 43.2), (14.5, 41.0), (16.5, 39.3), (18.5, 38.0), (20.5, 37.2),
              (22.5, 36.4), (24.5, 35.3), (26.5, 34.0)]
TELUK_PERSIA = [(30.0, 48.0), (29.4, 48.0), (28.5, 48.5), (27.0, 49.6), (26.0, 50.2), (25.0, 50.8), (26.1, 51.3),
                (25.0, 51.6), (24.2, 52.5), (24.3, 54.0), (25.3, 55.5), (26.2, 56.2), (25.0, 56.4), (24.0, 57.0),
                (23.6, 58.5), (22.5, 59.8), (22.0, 66.0), (25.2, 66.0), (25.3, 61.0), (25.4, 59.0), (26.6, 57.2),
                (27.2, 56.3), (26.6, 54.5), (27.5, 52.0), (29.0, 50.6), (30.0, 49.0)]
LAUT_KASPIA = [(37.0, 50.0), (36.6, 52.0), (36.9, 54.0), (38.5, 53.8), (40.0, 53.0), (41.0, 52.8), (42.5, 52.5),
               (44.0, 51.0), (45.0, 53.0), (46.5, 53.0), (47.0, 51.0), (46.0, 49.0), (44.5, 47.5), (42.0, 48.0),
               (40.5, 49.5), (38.5, 48.8)]
GUNUNG_TT = [(37.5, 44, 2.0), (33, 49, 2.5), (36.5, 36, 1.2), (20, 42, 2.0), (39, 40, 2.0), (28, 34, 1.0)]

print("  menyiapkan peta Timur Tengah...")
PETA_TT = Peta(13, 66, -2, 50, 55, [LAUT_TENGAH, LAUT_HITAM, LAUT_MERAH, TELUK_PERSIA, LAUT_KASPIA], GUNUNG_TT,
               seed=73)
print("  menyiapkan peta Indonesia...")
PETA_ID = Peta(88, 145, -32, 22, 60, [], [(-2, 114, 1.5), (0, 101, 1.2), (-7.5, 110, 1.0), (-2, 121, 1.2)],
               seed=74, darat=pd.SEMUA)

KUWAIT = (29.37, 47.98)
MESIR = (27.0, 30.5)
SURIAH = (35.0, 38.5)
ISRAEL = (31.4, 34.9)
SINAI = (29.6, 33.8)
GOLAN = (33.0, 35.8)
NEGARA_ARAB = {"Arab Saudi": (23.5, 45.5), "Irak": (33.0, 43.5), "Kuwait": (29.37, 47.98), "Libya": (28.0, 23.0),
               "UEA": (23.6, 54.0), "Qatar": (25.3, 51.2)}
# jalur kapal tanker keluar dari Teluk Persia
RUTE_AS = [(28.5, 49.5), (26.5, 52.0), (26.3, 56.4), (24.0, 59.5), (19.0, 61.0), (12.0, 58.0), (6.0, 52.0)]
RUTE_BELANDA = [(30.5, 31.8), (33.0, 30.0), (34.5, 26.0), (35.5, 22.0), (36.0, 19.0)]
SUMUR_ID = [(1.0, 101.3), (1.6, 101.4), (-1.27, 116.8), (-0.5, 117.4), (-2.9, 104.7), (-3.2, 104.2), (2.5, 98.1)]
SD_ID = [(3.6, 98.7), (2.0, 99.5), (0.9, 100.4), (-0.9, 100.4), (-1.6, 103.6), (-3.0, 104.8), (-5.2, 105.3),
         (-6.3, 106.8), (-6.9, 107.6), (-7.0, 109.3), (-7.4, 110.4), (-7.0, 110.4), (-7.6, 111.5), (-7.3, 112.7),
         (-8.0, 113.7), (-8.5, 115.2), (-8.6, 116.2), (-8.6, 118.0), (-8.6, 121.0), (-10.0, 123.6), (-0.03, 109.3),
         (-1.8, 110.5), (-2.2, 113.9), (-3.3, 114.6), (-1.2, 116.8), (0.5, 117.1), (1.5, 124.8), (-0.9, 119.9),
         (-3.0, 120.2), (-5.1, 119.4), (-3.7, 128.2), (-2.5, 140.7), (-0.9, 131.2), (-4.0, 122.5), (5.5, 95.3),
         (-6.9, 108.6), (-7.8, 110.4), (-2.1, 106.1), (-0.5, 102.0)]
LABEL_ID = {"SUMATRA": (-0.5, 101.6), "KALIMANTAN": (0.0, 113.6), "JAWA": (-7.2, 110.0)}


# ------------------------------------------------------------------ helper

def cam(peta, lat, lon, zoom):
    x, y = peta.px(lat, lon)
    return (x, y, zoom)


def gambar_peta(peta, kamera):
    img = se.render_peta(peta, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(peta, kamera, ll):
    return kamera.layar(*peta.px(*ll))


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
    """Skala 'pop' untuk elemen yang muncul di fraksi a."""
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


def hdr(img, sub="Oktober 1973", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def ikon_tong(d, x, y, s=1.0, alpha=1.0):
    """Tong minyak (barel)."""
    a = int(255 * alpha)
    w, h = 46 * s, 64 * s
    d.rounded_rectangle((x - w, y - h, x + w, y + h), int(14 * s), fill=(40, 70, 120, a), outline=(20, 25, 40, a),
                        width=max(2, int(4 * s)))
    for yy in (y - h * 0.45, y + h * 0.45):
        d.line((x - w, yy, x + w, yy), fill=(20, 25, 40, a), width=max(2, int(5 * s)))
    d.ellipse((x - w * 0.3, y - h * 0.85, x + w * 0.3, y - h * 0.65), fill=(20, 25, 40, a))


def ikon_tanker(d, x, y, s=1.0, alpha=1.0, warna=(150, 40, 30)):
    a = int(255 * alpha)
    d.polygon([(x - 46 * s, y - 6 * s), (x + 50 * s, y - 6 * s), (x + 38 * s, y + 12 * s), (x - 40 * s, y + 12 * s)],
              fill=tuple(warna) + (a,), outline=(30, 20, 15, a))
    d.rectangle((x - 40 * s, y - 14 * s, x + 30 * s, y - 6 * s), fill=(90, 90, 95, a))
    d.rectangle((x - 40 * s, y - 30 * s, x - 22 * s, y - 14 * s), fill=(240, 240, 240, a), outline=(30, 20, 15, a))


def ikon_sekolah(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.rectangle((x - 26 * s, y - 12 * s, x + 26 * s, y + 16 * s), fill=(250, 245, 230, a), outline=(40, 30, 20, a),
                width=max(1, int(3 * s)))
    d.polygon([(x - 32 * s, y - 12 * s), (x, y - 32 * s), (x + 32 * s, y - 12 * s)], fill=(200, 52, 44, a),
              outline=(40, 30, 20, a))
    d.rectangle((x - 6 * s, y + 2 * s, x + 6 * s, y + 16 * s), fill=(120, 80, 45, a))
    d.line((x + 36 * s, y + 16 * s, x + 36 * s, y - 34 * s), fill=(60, 50, 40, a), width=max(1, int(3 * s)))
    d.rectangle((x + 37 * s, y - 34 * s, x + 56 * s, y - 27 * s), fill=(220, 30, 40, a))
    d.rectangle((x + 37 * s, y - 27 * s, x + 56 * s, y - 20 * s), fill=(250, 250, 250, a))


# ------------------------------------------------------------------ ilustrasi: antrean di SPBU

def _langit(atas, bawah):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (np.array(atas, np.float32) * (1 - g) + np.array(bawah, np.float32) * g).repeat(W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    return img, ImageDraw.Draw(img, "RGBA")


WARNA_MOBIL = [(180, 60, 40), (60, 110, 160), (220, 180, 60), (90, 140, 80), (150, 150, 155), (120, 70, 120),
               (210, 120, 40), (70, 70, 80)]


def rr(d, box, r, **kw):
    """rounded_rectangle yang aman untuk kotak sangat kecil (Pillow bisa error)."""
    x0, y0, x1, y1 = box
    r = int(min(r, (x1 - x0) / 2 - 1, (y1 - y0) / 2 - 1))
    try:
        if r < 2:
            raise ValueError
        d.rounded_rectangle(box, r, **kw)
    except ValueError:
        d.rectangle(box, **kw)


def mobil(d, x, y, s, warna, pelat, alpha=1.0, sorot=None):
    """Mobil dari belakang (antre menjauh). sorot: None / 'ok' (hijau) / 'tolak' (merah)."""
    a = int(255 * alpha)
    w, h = 150 * s, 90 * s
    d.ellipse((x - w * 1.05, y + h * 0.75, x + w * 1.05, y + h * 1.1), fill=(0, 0, 0, int(70 * alpha)))
    d.rectangle((x - w * 0.9, y + h * 0.6, x - w * 0.6, y + h * 0.95), fill=(25, 25, 25, a))
    d.rectangle((x + w * 0.6, y + h * 0.6, x + w * 0.9, y + h * 0.95), fill=(25, 25, 25, a))
    d.polygon([(x - w * 0.62, y - h * 0.15), (x - w * 0.45, y - h * 0.75), (x + w * 0.45, y - h * 0.75),
               (x + w * 0.62, y - h * 0.15)], fill=se.lerp_rgb(warna, (0, 0, 0), 0.25) + (a,), outline=(20, 15, 10, a))
    d.polygon([(x - w * 0.52, y - h * 0.2), (x - w * 0.4, y - h * 0.65), (x + w * 0.4, y - h * 0.65),
               (x + w * 0.52, y - h * 0.2)], fill=(150, 185, 205, a))
    rr(d, (x - w, y - h * 0.2, x + w, y + h * 0.75), int(18 * s), fill=tuple(warna) + (a,),
                        outline=(20, 15, 10, a), width=max(2, int(4 * s)))
    for sx in (-1, 1):
        rr(d, (x + sx * w * 0.92 - 22 * s, y + h * 0.02, x + sx * w * 0.92 + 22 * s, y + h * 0.26),
                            int(6 * s), fill=(230, 40, 30, a))
    pw, ph = 74 * s, 26 * s
    py = y + h * 0.36
    pelat_w = (250, 250, 240) if sorot is None else ((120, 220, 130) if sorot == "ok" else (240, 130, 120))
    rr(d, (x - pw, py - ph, x + pw, py + ph), int(5 * s), fill=pelat_w + (a,), outline=(20, 15, 10, a),
                        width=max(1, int(3 * s)))
    if s > 0.35:
        se.teks(d, (x, py + 1), pelat, max(8, int(34 * s)), (20, 15, 10), nama_font="ui", alpha=alpha)


def spbu(c, era="1973", sorot=0.0, maju=0.0):
    """Antrean mobil ke pom bensin. sorot 0..1 = munculkan warna ganjil/genap di pelat."""
    if era == "1973":
        img, d = _langit((235, 175, 110), (250, 225, 175))
    else:
        img, d = _langit((120, 175, 225), (215, 232, 245))
    jauh = 700
    d.rectangle((0, jauh, W, H), fill=(120, 150, 90, 255) if era == "1973" else (95, 150, 75, 255))
    # jalan menjauh
    d.polygon([(470, jauh), (610, jauh), (1020, H), (60, H)], fill=(80, 80, 85, 255))
    for i in range(10):
        f0 = ((i / 10) + c.t * 0.05) % 1
        f1 = f0 + 0.04
        y0, y1 = lerp(jauh, H, f0 ** 2), lerp(jauh, H, f1 ** 2)
        d.polygon([(540 - 2 - 8 * f0, y0), (540 + 2 + 8 * f0, y0), (540 + 2 + 8 * f1, y1), (540 - 2 - 8 * f1, y1)],
                  fill=(230, 220, 150, 255))
    # kanopi SPBU di ujung antrean
    d.rectangle((300, 500, 780, 545), fill=(200, 52, 44, 255) if era == "1973" else (230, 230, 235, 255),
                outline=(30, 20, 15, 255), width=4)
    for x in (330, 750):
        d.rectangle((x - 10, 545, x + 10, jauh + 10), fill=(200, 200, 200, 255), outline=(40, 40, 40, 255), width=2)
    for x in (470, 610):
        d.rounded_rectangle((x - 22, 620, x + 22, jauh + 10), 6, fill=(230, 60, 40, 255) if era == "1973" else (30, 120, 200, 255),
                            outline=(30, 20, 15, 255), width=3)
    se.teks(d, (540, 523), "GAS" if era == "1973" else "SPBU", 34, PUTIH if era == "1973" else (30, 80, 150),
            nama_font="caption", stroke=3, stroke_warna=(30, 20, 15))
    if era == "1973":
        d.rounded_rectangle((820, 560, 960, 640), 10, fill=(250, 245, 230, 255), outline=(30, 20, 15, 255), width=4)
        se.teks(d, (890, 600), "NO GAS", 28, (190, 30, 20), nama_font="caption")
    # mobil-mobil antre: belakang (dekat kamera) besar, depan kecil
    rng = random.Random(5 if era == "1973" else 6)
    n = 7
    for i in reversed(range(n)):
        f = i / (n - 1)  # 0 = dekat pom, 1 = dekat kamera
        f = clamp(f + maju * 0.08)
        y = lerp(jauh + 30, 1270, f ** 1.6)
        s = lerp(0.22, 1.45, f ** 1.6)
        x = 540 + math.sin(i * 1.3) * 25 * s
        angka = rng.randint(100, 9999)
        if i % 2:
            angka += 1 - angka % 2  # ganjil
        else:
            angka -= angka % 2  # genap
        pelat = f"{rng.choice('ABCDEFGHKLMN')}{rng.choice('ABCDEFGHKLMN')} {angka}" if era == "1973" else f"DK {angka}"
        st = None
        if sorot > 0.5:
            st = "ok" if angka % 2 else "tolak"
        mobil(d, x, y, s, WARNA_MOBIL[(i + (0 if era == "1973" else 3)) % len(WARNA_MOBIL)], pelat, 1.0, st)
    return img, ImageDraw.Draw(img, "RGBA")


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img, d = spbu(c, "1973", sorot=c.p(0.35, 0.4))
    s = muncul(c, 0.0)
    se.teks(d, (540, 430), "GANJIL GENAP?", int(110 * s) + 1, (255, 235, 180), nama_font="caption", stroke=9,
            stroke_warna=(40, 25, 10))
    s2 = muncul(c, 0.55)
    if s2 > 0:
        se.teks(d, (540, 820), "1973", int(200 * s2) + 1, (255, 235, 180), nama_font="caption", stroke=10,
                stroke_warna=(40, 25, 10))
        se.teks(d, (540, 960), "dunia pernah ngalamin ini", 46, PUTIH, nama_font="caption", stroke=6,
                stroke_warna=(40, 25, 10), alpha=c.p(0.62, 0.72))
    hdr(img, alpha=c.p(0.8, 0.95))
    return img


def a_tren(c):
    img, d = spbu(c, "2026", sorot=c.p(0.35, 0.4), maju=c.p(0, 1))
    kartu(img, 540, 430, "Bali · 17–19 Oktober 2026", "BBM langka, antrean panjang", MERAH, alpha=c.p(0.02, 0.1),
          tiang=False, skala=muncul(c, 0.02) or 0.01)
    kartu(img, 290, 1010, "Pelat ganjil: 17 Okt", "", HIJAU, alpha=c.p(0.3, 0.38), tiang=False)
    kartu(img, 790, 1010, "Pelat genap: 18 Okt", "", MERAH, alpha=c.p(0.38, 0.46), tiang=False)
    if c.p(0.7, 0.78) > 0:
        se.tint(img, (20, 10, 0), 0.45 * c.p(0.7, 0.78))
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 760), "53 tahun lalu…", 80, (255, 220, 160), nama_font="caption", stroke=8,
                stroke_warna=(30, 15, 5), alpha=c.p(0.72, 0.8))
        se.teks(d, (540, 870), "krisis yang jauh lebih parah", 48, PUTIH, nama_font="caption", stroke=6,
                stroke_warna=(30, 15, 5), alpha=c.p(0.78, 0.86))
    hdr(img, "Lagi rame hari ini")
    return img


def a_perang(c):
    kamera = se.kamera_antara(cam(PETA_TT, 31.5, 35, 0.95), cam(PETA_TT, 30.5, 40, 0.8), c.p(0.35, 0.65))
    img, d = gambar_peta(PETA_TT, kamera)
    a = 1 - c.p(0.45, 0.55)
    for nama, ll in (("MESIR", MESIR), ("SURIAH", SURIAH), ("ISRAEL", ISRAEL)):
        x, y = layar(PETA_TT, kamera, ll)
        label(d, (x, y), nama, 40, TINTA, c.p(0.02, 0.1) * (0.6 + 0.4 * a), "caption")
    for i, ll in enumerate((SINAI, GOLAN)):
        x, y = layar(PETA_TT, kamera, ll)
        denyut(d, x, y, c.t + i * 0.4, c.p(0.05 + i * 0.05, 0.12 + i * 0.05) * a)
    kartu(img, 540, 470, "Perang Oktober 1973", "Israel vs Mesir & Suriah · mulai 6 Okt", (90, 70, 50),
          alpha=c.p(0.05, 0.13) * a, tiang=False, skala=muncul(c, 0.05) or 0.01)
    # rapat di Kuwait
    b = c.p(0.55, 0.62)
    if b > 0:
        kx, ky = layar(PETA_TT, kamera, KUWAIT)
        d.ellipse((kx - 14, ky - 14, kx + 14, ky + 14), fill=(200, 52, 44, int(255 * b)), outline=(255, 255, 255, int(255 * b)),
                  width=4)
        label(d, (kx + 10, ky + 50), "Kuwait", 36, TINTA, b)
        kartu(img, kx, ky - 30, "17 Oktober 1973", "rapat negara Arab pengekspor minyak", MERAH, alpha=b,
              skala=muncul(c, 0.55))
    hdr(img)
    return img


def a_embargo(c):
    kamera = Kamera(*cam(PETA_TT, 26.0, 41.0, 0.67))
    img, d = gambar_peta(PETA_TT, kamera)
    for i, (nama, ll) in enumerate(NEGARA_ARAB.items()):
        x, y = layar(PETA_TT, kamera, ll)
        a = c.p(0.0 + i * 0.03, 0.06 + i * 0.03)
        if a > 0:
            ikon_tong(d, x, y - 30, 0.45, a)
            label(d, (x, y + 22), nama, 28, TINTA, a)
    # produksi dipangkas: tong mengecil (angka)
    kartu(img, 540, 470, "Produksi minyak dipangkas", "dan terus dikurangi tiap bulan", (90, 70, 50),
          alpha=c.p(0.08, 0.16), tiang=False, skala=muncul(c, 0.08) or 0.01)
    for rute, nama, f0, y_k in ((RUTE_AS, "Amerika Serikat", 0.35, 1180), (RUTE_BELANDA, "Belanda", 0.45, 1300)):
        titik = [layar(PETA_TT, kamera, ll) for ll in rute]
        k = c.p(f0, f0 + 0.15)
        ujung = se.garis_putus(d, titik, k, (30, 80, 150), tebal=8, putus=20, celah=12)
        if ujung and k > 0.05:
            ikon_tanker(d, ujung[0], ujung[1] - 10, 0.8, 1.0 - c.p(0.75, 0.85))
        x = c.p(0.68, 0.78)
        if x > 0:
            mx, my = titik[len(titik) // 2]
            r = 40
            d.line((mx - r, my - r, mx - r + 2 * r * x, my - r + 2 * r * x), fill=(200, 30, 30, 255), width=14)
            if x > 0.5:
                d.line((mx + r, my - r, mx + r - 2 * r * (x - 0.5) * 2, my - r + 2 * r * (x - 0.5) * 2),
                       fill=(200, 30, 30, 255), width=14)
        kartu(img, 540, y_k, f"→ {nama}", "kiriman minyak dihentikan", MERAH, alpha=c.p(f0 + 0.1, f0 + 0.18),
              tiang=False, coret=c.p(0.7, 0.85))
    hdr(img, "Senjata minyak")
    return img


def a_harga(c):
    img = Image.new("RGBA", (W, H), (30, 28, 34, 255))
    se.panel(img, (70, 400, 1010, 1300), alpha=c.p(0, 0.08), warna=(247, 236, 208))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 480), "HARGA MINYAK PER BAREL", 46, (150, 40, 30), nama_font="judul", alpha=c.p(0.02, 0.1))
    x0, x1, y0, y1 = 170, 930, 1180, 640
    d.line((x0, y0, x1, y0), fill=TINTA + (255,), width=4)
    d.line((x0, y0, x0, y1 - 20), fill=TINTA + (255,), width=4)
    for v in (3, 6, 9, 12):
        yy = lerp(y0, y1, v / 12)
        d.line((x0, yy, x1, yy), fill=(120, 90, 50, 70), width=2)
        se.teks(d, (x0 - 20, yy), f"${v}", 28, TINTA, anchor="rm", alpha=c.p(0.05, 0.12))
    se.teks(d, (x0 + 20, y0 + 40), "awal Okt 1973", 26, (90, 70, 50), anchor="lm", alpha=c.p(0.05, 0.12))
    se.teks(d, (x1, y0 + 40), "awal 1974", 26, (90, 70, 50), anchor="rm", alpha=c.p(0.05, 0.12))
    # garis harga: datar lalu melonjak
    titik = [(0.0, 3.0), (0.2, 3.0), (0.3, 5.1), (0.55, 5.4), (0.7, 8.0), (0.8, 11.6), (1.0, 11.65)]
    k = c.p(0.1, 0.7)
    pts = [(lerp(x0, x1, f), lerp(y0, y1, v / 12)) for f, v in titik]
    ujung = se.garis_putus(d, pts, k, (200, 40, 30), tebal=10, putus=6, celah=0, panah=False)
    harga = 3 + 8.65 * c.p(0.15, 0.7)
    if ujung:
        ikon_tong(d, ujung[0], ujung[1] - 60, 0.55)
    se.teks(d, (540, 1250), f"± ${harga:.0f}", 90, MERAH, nama_font="caption", stroke=6, stroke_warna=(255, 255, 255),
            alpha=c.p(0.1, 0.18))
    s = muncul(c, 0.72)
    if s > 0:
        se.teks(d, (700, 720), "4×", int(150 * s) + 1, (200, 40, 30), nama_font="caption", stroke=8,
                stroke_warna=(255, 255, 255))
    hdr(img, "Okt 1973 – Jan 1974")
    return img


def a_amerika(c):
    img, d = spbu(c, "1973", sorot=c.p(0.45, 0.5), maju=c.p(0, 1))
    kartu(img, 540, 430, "Amerika Serikat", "antrean panjang, banyak pom kehabisan", BIRU, alpha=c.p(0.02, 0.1),
          tiang=False, skala=muncul(c, 0.02) or 0.01)
    kartu(img, 540, 900, "Oregon: sistem ganjil genap", "negara bagian pertama yang menerapkan", MERAH,
          alpha=c.p(0.4, 0.48), tiang=False, skala=muncul(c, 0.4) or 0.01)
    kartu(img, 540, 1030, "pelat ganjil → tgl ganjil", "", HIJAU, alpha=c.p(0.55, 0.62), tiang=False)
    kartu(img, 540, 1130, "pelat genap → tgl genap", "", MERAH, alpha=c.p(0.62, 0.68), tiang=False)
    s = muncul(c, 0.85)
    if s > 0:
        se.teks(d, (540, 780), "persis kayak Bali!", int(64 * s) + 1, (255, 235, 180), nama_font="caption", stroke=7,
                stroke_warna=(40, 25, 10))
    hdr(img, "1973 – 1974")
    return img


def a_belanda(c):
    img, d = _langit((150, 185, 220), (225, 235, 240))
    jauh = 760
    d.rectangle((0, jauh, W, H), fill=(110, 160, 80, 255))
    # kincir angin di kejauhan
    for kx, ks in ((170, 1.0), (900, 0.8)):
        d.polygon([(kx - 22 * ks, jauh), (kx - 12 * ks, jauh - 120 * ks), (kx + 12 * ks, jauh - 120 * ks),
                   (kx + 22 * ks, jauh)], fill=(120, 90, 70, 255))
        for j in range(4):
            sud = c.t * 1.2 + j * math.pi / 2
            ex, ey = kx + math.cos(sud) * 80 * ks, jauh - 120 * ks + math.sin(sud) * 80 * ks
            d.line((kx, jauh - 120 * ks, ex, ey), fill=(240, 235, 220, 255), width=int(10 * ks))
    # jalan tol yang kosong
    d.polygon([(500, jauh), (580, jauh), (1060, H), (20, H)], fill=(90, 90, 95, 255))
    d.polygon([(536, jauh), (544, jauh), (560, H), (520, H)], fill=(110, 140, 80, 255))
    for i in range(12):
        f0 = (i / 12 + c.t * 0.04) % 1
        f1 = f0 + 0.03
        for sisi in (-1, 1):
            xa = lerp(540 + sisi * 20, 540 + sisi * 270, f0 ** 2)
            xb = lerp(540 + sisi * 20, 540 + sisi * 270, f1 ** 2)
            d.line((xa, lerp(jauh, H, f0 ** 2), xb, lerp(jauh, H, f1 ** 2)), fill=(240, 240, 240, 255), width=int(2 + 8 * f0))
    # orang bersepeda & bersepatu roda (siluet)
    rng = random.Random(8)
    for i in range(9):
        f = 0.15 + (i / 9) * 0.8
        s = lerp(0.3, 1.4, f ** 1.5)
        y = lerp(jauh, 1300, f ** 1.5)
        x = 540 + (rng.uniform(80, 380) * rng.choice((-1, 1))) * s / 1.4 + math.sin(c.t * 2 + i) * 20 * s
        a = int(255 * c.p(0.15 + i * 0.03, 0.22 + i * 0.03))
        if a <= 0:
            continue
        hit = (35, 30, 30, a)
        if i % 3 == 0:  # sepeda
            for dx in (-28, 28):
                d.ellipse((x + dx * s - 22 * s, y - 22 * s, x + dx * s + 22 * s, y + 22 * s), outline=hit, width=max(2, int(5 * s)))
            d.line((x - 28 * s, y, x, y - 30 * s, x + 28 * s, y), fill=hit, width=max(2, int(5 * s)))
            d.line((x, y - 30 * s, x - 4 * s, y - 75 * s), fill=hit, width=max(2, int(7 * s)))
            d.ellipse((x - 16 * s, y - 105 * s, x + 8 * s, y - 81 * s), fill=hit)
        else:  # sepatu roda
            ayun = math.sin(c.t * 5 + i) * 18 * s
            d.line((x, y - 50 * s, x - ayun, y), fill=hit, width=max(2, int(7 * s)))
            d.line((x, y - 50 * s, x + ayun, y), fill=hit, width=max(2, int(7 * s)))
            d.line((x, y - 50 * s, x, y - 100 * s), fill=hit, width=max(2, int(8 * s)))
            d.line((x, y - 90 * s, x - 30 * s, y - 60 * s + ayun), fill=hit, width=max(2, int(5 * s)))
            d.line((x, y - 90 * s, x + 30 * s, y - 60 * s - ayun), fill=hit, width=max(2, int(5 * s)))
            d.ellipse((x - 13 * s, y - 128 * s, x + 13 * s, y - 102 * s), fill=hit)
    # kereta kuda
    b = c.p(0.55, 0.65)
    if b > 0:
        a = int(255 * b)
        kx, ky, ks = 330 + c.t * 8, 1200, 1.2
        d.rectangle((kx, ky - 90 * ks, kx + 120 * ks, ky - 20 * ks), fill=(110, 60, 30, a), outline=(30, 20, 10, a), width=4)
        d.ellipse((kx + 10 * ks, ky - 40 * ks, kx + 60 * ks, ky + 10 * ks), outline=(30, 20, 10, a), width=6)
        d.ellipse((kx + 70 * ks, ky - 40 * ks, kx + 120 * ks, ky + 10 * ks), outline=(30, 20, 10, a), width=6)
        hx = kx + 150 * ks
        d.ellipse((hx, ky - 100 * ks, hx + 110 * ks, ky - 50 * ks), fill=(80, 50, 30, a))
        d.polygon([(hx + 95 * ks, ky - 90 * ks), (hx + 140 * ks, ky - 140 * ks), (hx + 155 * ks, ky - 120 * ks),
                   (hx + 115 * ks, ky - 70 * ks)], fill=(80, 50, 30, a))
        for lx in (12, 30, 80, 98):
            d.line((hx + lx * ks, ky - 60 * ks, hx + lx * ks + math.sin(c.t * 6 + lx) * 8, ky), fill=(80, 50, 30, a), width=8)
    kartu(img, 540, 470, "Belanda: Minggu tanpa mobil", "mulai 4 November 1973", (200, 110, 30), alpha=c.p(0.02, 0.1),
          tiang=False, skala=muncul(c, 0.02) or 0.01)
    kartu(img, 540, 610, "Jalan tol jadi tempat main", "sepatu roda, sepeda, kereta kuda", (60, 60, 70),
          alpha=c.p(0.4, 0.48), tiang=False)
    hdr(img, "Eropa, akhir 1973")
    return img


def a_indonesia(c):
    kamera = se.kamera_antara(cam(PETA_ID, -2.0, 112.0, 0.66), cam(PETA_ID, -1.0, 108.0, 0.72), c.p(0, 1))
    img, d = gambar_peta(PETA_ID, kamera)
    for nama, ll in LABEL_ID.items():
        x, y = layar(PETA_ID, kamera, ll)
        label(d, (x, y), nama, 36, TINTA, 0.85)
    for i, ll in enumerate(SUMUR_ID):
        x, y = layar(PETA_ID, kamera, ll)
        a = c.p(0.12 + i * 0.03, 0.18 + i * 0.03)
        if a > 0:
            ikon_tong(d, x, y - 20, 0.4, a)
    # tanker berangkat ekspor
    for j in range(3):
        f = (c.t * 0.12 + j / 3) % 1
        ll = (lerp(-1.0, 12.0, f), lerp(108.0 + j * 4, 128.0 + j * 2, f))
        x, y = layar(PETA_ID, kamera, ll)
        ikon_tanker(d, x, y, 0.8, c.p(0.3, 0.4) * (1 - f) ** 0.3, (40, 120, 70))
    kartu(img, 540, 470, "Indonesia: pengekspor minyak", "justru untung besar", HIJAU, alpha=c.p(0.2, 0.28),
          tiang=False, skala=muncul(c, 0.2) or 0.01)
    k = c.p(0.45, 0.75)
    if k > 0:
        harga = 3.70 + (12.60 - 3.70) * k
        se.teks(d, (540, 1150), f"${harga:.2f}".replace(".", ","), 110, (255, 220, 120), nama_font="caption", stroke=9,
                stroke_warna=(30, 20, 10))
        se.teks(d, (540, 1250), "harga ekspor per barel · Apr 1973 → Jul 1974", 32, PUTIH, nama_font="ui", stroke=4,
                stroke_warna=(0, 0, 0))
    s = muncul(c, 0.82)
    if s > 0:
        se.teks(d, (540, 700), "OIL BOOM", int(110 * s) + 1, (255, 235, 180), nama_font="caption", stroke=9,
                stroke_warna=(30, 20, 10))
    hdr(img, "Bagaimana dengan Indonesia?")
    return img


def a_sd(c):
    kamera = Kamera(*cam(PETA_ID, -3.0, 113.0, 0.62))
    img, d = gambar_peta(PETA_ID, kamera)
    n = int(len(SD_ID) * c.p(0.08, 0.6) + 0.999)
    for i, ll in enumerate(SD_ID[:n]):
        x, y = layar(PETA_ID, kamera, ll)
        ikon_sekolah(d, x, y, 0.75)
    jumlah = int(61000 * c.p(0.08, 0.6))
    se.teks(d, (540, 1150), f"{jumlah:,}".replace(",", ".") + ("+" if jumlah >= 61000 else ""), 120, (255, 220, 120),
            nama_font="caption", stroke=9, stroke_warna=(30, 20, 10), alpha=c.p(0.05, 0.12))
    se.teks(d, (540, 1255), "SD Inpres · 1973 – 1978", 44, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0),
            alpha=c.p(0.05, 0.12))
    kartu(img, 540, 470, "Dibiayai sebagian dari uang minyak", "", (90, 70, 50), alpha=c.p(0.02, 0.1), tiang=False)
    s = muncul(c, 0.72)
    if s > 0:
        se.teks(d, (540, 680), "SD orang tuamu?", int(80 * s) + 1, (255, 235, 180), nama_font="caption", stroke=8,
                stroke_warna=(30, 20, 10))
    hdr(img, "Dari minyak jadi sekolah")
    return img


def a_akhir(c):
    kamera = Kamera(*cam(PETA_TT, 26.0, 41.0, 0.67))
    img, d = gambar_peta(PETA_TT, kamera)
    for rute in (RUTE_AS, RUTE_BELANDA):
        titik = [layar(PETA_TT, kamera, ll) for ll in rute]
        ujung = se.garis_putus(d, titik, c.p(0.1, 0.35), HIJAU, tebal=8, putus=20, celah=12)
        if ujung and c.p(0.1, 0.35) > 0.05:
            ikon_tanker(d, ujung[0], ujung[1] - 10, 0.8)
    kartu(img, 540, 470, "Maret 1974: embargo dicabut", "untuk Amerika Serikat", HIJAU, alpha=c.p(0.02, 0.1),
          tiang=False, skala=muncul(c, 0.02) or 0.01)
    kartu(img, 540, 1180, "Tapi harga minyak", "nggak pernah balik semurah dulu", MERAH, alpha=c.p(0.45, 0.53),
          tiang=False, skala=muncul(c, 0.45) or 0.01)
    hdr(img, "Setelah krisis")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(PETA_ID, -3.0, 113.0, 0.62))
    img, d = gambar_peta(PETA_ID, kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1000), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Antre BBM bukan cerita baru", 48, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 650), "energi itu rapuh", 38, (90, 70, 50), alpha=a)
        # pompa bensin
        aa = int(255 * a)
        d.rounded_rectangle((480, 700, 590, 900), 14, fill=(200, 52, 44, aa), outline=(40, 25, 15, aa), width=5)
        d.rectangle((500, 725, 570, 785), fill=(250, 245, 230, aa))
        d.line((590, 740, 630, 760, 630, 860), fill=(40, 25, 15, aa), width=8)
        ikon_tong(d, 400, 830, 0.6, a)
        se.teks(d, (540, 950), "Pakai seperlunya, ya!", 46, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Isi bensin pakai ganjil genap? Dunia pernah ngalamin ini, lima puluh tiga tahun lalu.", a_hook,
           transisi=False),
    Adegan("tren", "Hari ini, Bali mulai pakai ganjil genap buat beli Pertalite, gara-gara BBM langka. Tapi lima "
                   "puluh tiga tahun lalu, ada krisis BBM yang jauh lebih parah.", a_tren),
    Adegan("perang", "Oktober sembilan belas tujuh puluh tiga, pecah perang Israel melawan Mesir dan Suriah. Tanggal "
                     "tujuh belas, negara-negara Arab pengekspor minyak rapat di Kuwait.", a_perang),
    Adegan("embargo", "Produksi minyak dipangkas, dan kiriman ke negara pendukung Israel dihentikan. Terutama Amerika "
                      "Serikat dan Belanda.", a_embargo, transisi=False),
    Adegan("harga", "Hasilnya, harga minyak dunia naik empat kali lipat. Dari sekitar tiga dolar, jadi hampir dua "
                    "belas dolar per barel.", a_harga),
    Adegan("amerika", "Di Amerika, antrean pom bensin mengular, banyak yang kehabisan stok. Oregon jadi negara bagian "
                      "pertama yang pakai ganjil genap. Persis kayak Bali sekarang.", a_amerika),
    Adegan("belanda", "Di Belanda, mobil pribadi dilarang jalan tiap hari Minggu. Jalan tol sepi, orang malah main "
                      "sepatu roda dan naik kereta kuda di sana.", a_belanda),
    Adegan("indonesia", "Terus, Indonesia gimana? Justru untung. Kita pengekspor minyak. Harga ekspor kita naik dari "
                        "tiga koma tujuh, jadi dua belas koma enam dolar per barel. Inilah oil boom.", a_indonesia),
    Adegan("sd", "Sebagian uangnya dipakai bangun lebih dari enam puluh satu ribu SD Inpres dalam lima tahun. Bisa "
                 "jadi, SD orang tuamu salah satunya.", a_sd, transisi=False),
    Adegan("akhir", "Embargonya dicabut Maret sembilan belas tujuh puluh empat. Tapi harga minyak, nggak pernah balik "
                    "semurah dulu.", a_akhir),
    Adegan("penutup", "Jadi, antre BBM itu bukan cerita baru. Energi itu rapuh, jadi pakai seperlunya, ya. Follow "
                      "Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
