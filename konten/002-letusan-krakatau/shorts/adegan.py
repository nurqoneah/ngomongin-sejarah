"""Shorts ±90 detik: Letusan Krakatau 1883.

Dua peta: (1) Selat Sunda dekat, (2) Samudra Hindia untuk jangkauan suara & abu.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import shorts_engine as se
from shorts_engine import (EMAS, HIJAU_TUA, MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp,
                           lerp)

NAMA_FILE = "letusan-krakatau-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "LETUSAN KRAKATAU"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)

# ------------------------------------------------------------------ peta Selat Sunda (dekat)

JAWA_BARAT = [(-5.93, 106.0), (-6.0, 106.15), (-5.95, 106.35), (-6.05, 106.6), (-6.1, 106.8), (-6.0, 107.3),
              (-8.0, 107.3), (-7.4, 106.9), (-7.0, 106.53), (-6.95, 106.0), (-6.85, 105.55), (-6.8, 105.25),
              (-6.72, 105.2), (-6.62, 105.38), (-6.63, 105.6), (-6.48, 105.65), (-6.53, 105.72), (-6.38, 105.83),
              (-6.3, 105.83), (-6.05, 105.88)]
SUMATRA_SEL = [(-4.5, 103.6), (-5.19, 103.93), (-5.6, 104.25), (-5.92, 104.58), (-5.75, 104.72), (-5.5, 104.62),
               (-5.55, 104.85), (-5.8, 105.05), (-5.95, 105.2), (-5.75, 105.22), (-5.47, 105.27), (-5.55, 105.42),
               (-5.73, 105.6), (-5.87, 105.75), (-5.7, 105.85), (-5.3, 105.85), (-4.5, 105.9)]
PULAU_KECIL = [
    [(-5.9, 105.45), (-5.93, 105.51), (-5.97, 105.48), (-5.94, 105.43)],                       # Sebesi
    [(-5.93, 105.83), (-5.96, 105.88), (-5.98, 105.84)],                                        # Sangiang
    [(-6.55, 105.15), (-6.6, 105.27), (-6.65, 105.22), (-6.62, 105.12)],                       # Panaitan
]

print("  menyiapkan peta Selat Sunda...")
SUNDA = Peta(103.6, 107.2, -7.9, -4.6, 900, [], [(-6.5, 106.3, 0.35), (-7.0, 106.9, 0.4), (-5.2, 104.6, 0.4),
                                                 (-5.4, 105.0, 0.3), (-4.9, 105.4, 0.4)],
             seed=8, darat=[JAWA_BARAT, SUMATRA_SEL] + PULAU_KECIL)

KRAKATAU = (-6.11, 105.43)
LABEL_SUNDA = {"JAWA": (-6.55, 106.35), "SUMATRA": (-5.05, 104.75), "Selat Sunda": (-6.25, 105.2)}
KOTA_SUNDA = {"Anyer": (-6.05, 105.88), "Merak": (-5.93, 106.0), "Telukbetung": (-5.45, 105.27)}

# bentuk pulau Krakatau (sebelum & sesudah)
KRAK_LAMA = [(-6.05, 105.42), (-6.06, 105.45), (-6.1, 105.46), (-6.15, 105.455), (-6.165, 105.43), (-6.15, 105.41),
             (-6.1, 105.405)]
KRAK_SISA = [(-6.125, 105.445), (-6.15, 105.455), (-6.165, 105.43), (-6.15, 105.41), (-6.13, 105.415)]
VERLATEN = [(-6.07, 105.36), (-6.09, 105.385), (-6.11, 105.375), (-6.09, 105.355)]
LANG = [(-6.08, 105.47), (-6.1, 105.485), (-6.11, 105.475)]

# ------------------------------------------------------------------ peta Samudra Hindia (jauh)

ASIA_AFRIKA = [(-34.5, 20), (-34, 26), (-25.9, 32.6), (-19.8, 34.8), (-15, 40.7), (-10.5, 40.4), (-6.8, 39.3),
               (-4, 39.7), (-1.5, 41.6), (2, 45.3), (5, 48), (10, 50.8), (11.8, 51.2), (11.5, 47), (12, 43.4),
               (12.8, 45), (14.5, 49), (16.8, 52), (18.5, 56.5), (22.5, 59.8), (24, 57), (25.3, 60), (24.8, 67),
               (22.5, 69), (21, 72.6), (19, 72.8), (15.5, 73.8), (12.9, 74.8), (10, 76.2), (8.08, 77.55), (9.3, 79.2),
               (13.1, 80.3), (16.5, 82.2), (19.3, 84.9), (21.5, 87), (22, 88.5), (21.8, 90), (22.3, 91.8), (20, 92.9),
               (16.8, 94.4), (16.8, 97.6), (13, 98.6), (9, 98.3), (7.9, 98.3), (5.4, 100.3), (2.5, 101.8),
               (1.3, 103.8), (3.8, 103.4), (6.1, 102.3), (8.5, 100.0), (13.5, 100.5), (11.5, 102.8), (10.4, 104.5),
               (8.6, 104.7), (10.3, 107.1), (12.2, 109.2), (16, 108.2), (21, 106.7), (21.5, 108), (22.5, 114),
               (25, 119.5), (30, 122), (35, 119.5), (37.5, 122.5), (40, 121.5), (45, 125), (45, 15), (-34.5, 15)]
DARAT_JAUH = [
    ASIA_AFRIKA,
    [(5.6, 95.3), (5.2, 97.5), (3.8, 98.7), (2.0, 100.5), (0.5, 103.6), (-1, 104.4), (-2.5, 105.9), (-3.5, 106.0),
     (-5.9, 105.8), (-5.9, 104.6), (-4, 102.3), (-0.95, 100.35), (0.5, 99), (2.2, 98), (3.7, 96.5)],
    [(-5.9, 106.0), (-6.1, 107.0), (-6.2, 108.3), (-6.85, 110.4), (-6.9, 112.6), (-7.1, 113.5), (-7.7, 114.4),
     (-8.6, 114.4), (-8.3, 111.5), (-7.75, 108.9), (-7.4, 106.5), (-6.8, 105.2)],
    [(-8.1, 114.5), (-8.8, 115.2), (-8.5, 115.7), (-8.1, 115.2)],
    [(-8.3, 116), (-8.9, 116.1), (-8.8, 116.6), (-8.3, 116.6)],
    [(-8.1, 116.8), (-9.0, 117), (-8.9, 119), (-8.2, 118.6)],
    [(-8.4, 119.8), (-8.9, 120), (-8.8, 122.8), (-8.2, 122.9)],
    [(-9.2, 123.5), (-10.4, 123.5), (-9.0, 127), (-8.4, 127)],
    [(7, 116.8), (5.9, 118.3), (4.2, 117.8), (1.0, 118.9), (-1.3, 116.6), (-3.9, 116.0), (-4.1, 114.6),
     (-3.4, 111.8), (-2.9, 110.2), (-1.2, 109.9), (1.6, 109.2), (2.0, 111.2), (3.3, 113.1), (4.9, 115), (6.4, 116.1)],
    [(1.4, 125.1), (0.5, 124), (0.9, 121), (0.5, 120.2), (-0.9, 119.8), (-3.5, 118.8), (-5.6, 119.4), (-5.4, 120.4),
     (-2.6, 120.4), (-4.8, 122.0), (-5.0, 123.0), (-3.2, 122.4), (-1.5, 123.3), (-0.9, 122.5), (0.4, 121.2),
     (1.0, 124.5)],
    [(18.5, 120.6), (18.3, 122.2), (14, 124.2), (12.5, 124.5), (10, 126), (7, 126.5), (6, 125.3), (7, 122),
     (9.5, 123), (11, 122), (12.5, 120.9), (14.5, 120.6), (16.3, 119.8)],
    [(25.2, 121.5), (22, 120.7), (22.9, 121.3)],
    [(-0.8, 131.0), (-0.4, 132.8), (-2.5, 135), (-9, 135), (-8.5, 137), (-1, 140), (0, 140)],
    [(-12.4, 130.8), (-14.9, 128.4), (-14, 126), (-16.4, 123), (-18, 122.2), (-19.9, 119), (-20.5, 116.7),
     (-22, 114), (-24.9, 113.6), (-27.7, 114.1), (-31.9, 115.7), (-34.3, 115.1), (-35, 117.9), (-33.9, 123.6),
     (-31.7, 128.9), (-31.5, 131.1), (-40, 140), (-11, 140)],
    [(-12, 49.3), (-15.5, 50.2), (-20, 48.9), (-25, 47), (-25.5, 45.1), (-23.5, 43.6), (-21.5, 43.5), (-16, 44.4),
     (-15.2, 46.6), (-13.4, 48.3)],
    [(9.8, 80), (8.5, 81.3), (6.9, 81.8), (6.0, 80.6), (6.5, 79.9), (8.2, 79.8)],
]
print("  menyiapkan peta Samudra Hindia...")
HINDIA = Peta(35, 135, -47, 42, 40, [], [(25, 85, 8), (30, 100, 9), (-25, 125, 8), (5, 40, 7)], seed=13,
              darat=DARAT_JAUH)

KRAK_JAUH = (-6.1, 105.4)
RODRIGUES = (-19.7, 63.4)
PERTH = (-31.95, 115.86)
KM_PER_DERAJAT = 111.0


# ------------------------------------------------------------------ helper

def cam(peta, lat, lon, zoom):
    x, y = peta.px(lat, lon)
    return (x, y, zoom)


def peta_dgn(peta, kamera, goyang=0.0, seed=0):
    if goyang > 0:
        rng = random.Random(seed)
        kamera.x += rng.uniform(-1, 1) * goyang / kamera.zoom
        kamera.y += rng.uniform(-1, 1) * goyang / kamera.zoom
    img = se.render_peta(peta, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(peta, kamera, ll):
    return kamera.layar(*peta.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def pulau(d, kamera, poli, warna=(150, 120, 90), alpha=1.0):
    p = se.halus([layar(SUNDA, kamera, ll) for ll in poli])
    d.polygon(p, fill=tuple(warna) + (int(255 * alpha),), outline=(40, 30, 20, int(255 * alpha)))


def asap(img, x, y, t, kuat=1.0, tinggi=600, lebar=1.0, seed=1, warna=(90, 85, 80)):
    """Kolom asap/abu yang naik dari (x, y)."""
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    for i in range(46):
        fase = (rng.random() + t * rng.uniform(0.15, 0.3)) % 1.0
        yy = y - fase * tinggi
        xx = x + math.sin(fase * 6 + i) * 30 * lebar + rng.uniform(-40, 40) * lebar * fase
        r = (30 + fase * 140) * lebar * rng.uniform(0.7, 1.2)
        a = int(200 * kuat * (1 - fase * 0.7))
        g = rng.randint(-15, 15)
        c = tuple(clamp(v + g, 0, 255) for v in warna)
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=tuple(int(v) for v in c) + (a,))
    img.alpha_composite(lap)


def cincin(d, x, y, r, warna, alpha, tebal=8):
    if alpha <= 0.01 or r <= 1:
        return
    d.ellipse((x - r, y - r, x + r, y + r), outline=tuple(warna) + (int(255 * alpha),), width=tebal)


def kilat(img, kuat):
    se.tint(img, (255, 245, 220), clamp(kuat))


def hdr(img, sub="27 Agustus 1883", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def label_sunda(d, kamera, alpha=1.0):
    for nama, ll in LABEL_SUNDA.items():
        x, y = layar(SUNDA, kamera, ll)
        label(d, (x, y), nama, 46 if nama != "Selat Sunda" else 36,
              TINTA if nama != "Selat Sunda" else (30, 50, 90), alpha)


def kota_sunda(d, kamera, alpha=1.0, merah=0.0):
    for nama, ll in KOTA_SUNDA.items():
        x, y = layar(SUNDA, kamera, ll)
        warna = se.lerp_rgb((40, 30, 20), (200, 30, 20), merah)
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=warna + (int(255 * alpha),), outline=(255, 255, 255, int(255 * alpha)), width=3)
        label(d, (x + 14, y - 26), nama, 30, warna, alpha, "tangan")


# ------------------------------------------------------------------ adegan

def a_hook(c):
    kamera = Kamera(*cam(HINDIA, -12, 86, 0.6))
    img, d = peta_dgn(HINDIA, kamera)
    se.tint(img, (5, 5, 15), 0.55)
    d = ImageDraw.Draw(img, "RGBA")
    kx, ky = layar(HINDIA, kamera, KRAK_JAUH)
    for i in range(4):
        f = ((c.t * 0.55 + i * 0.25) % 1.0)
        cincin(d, kx, ky, f * 900, (255, 200, 120), (1 - f) * 0.9, 10)
    d.ellipse((kx - 16, ky - 16, kx + 16, ky + 16), fill=(255, 90, 40, 255), outline=(255, 255, 255, 255), width=4)
    s = back_out(c.t / 0.35)
    se.teks(d, (540, 700), "BOOM!", int(190 * s) + 1, (255, 120, 40), nama_font="caption", stroke=10, stroke_warna=(0, 0, 0))
    s2 = back_out((c.t / c.d - 0.3) / 0.12) if c.t / c.d > 0.3 else 0
    if s2 > 0:
        se.teks(d, (540, 900), "4.800 KM", int(150 * s2) + 1, PUTIH, nama_font="caption", stroke=10, stroke_warna=(0, 0, 0))
        se.teks(d, (540, 1010), "jauhnya suara ini terdengar", 44, (255, 220, 160), nama_font="caption", stroke=6,
                stroke_warna=(0, 0, 0), alpha=c.p(0.4, 0.5))
    se.teks(d, (540, 1150), "…dan ini terjadi di Indonesia", 46, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(0, 0, 0), alpha=c.p(0.7, 0.8))
    hdr(img, alpha=c.p(0.8, 0.95))
    return img


CAM_S2 = (cam(SUNDA, -5.9, 105.5, 0.8), cam(SUNDA, -6.1, 105.45, 2.2))


def a_lokasi(c):
    kamera = se.kamera_antara(*CAM_S2, c.p(0.0, 0.9))
    img, d = peta_dgn(SUNDA, kamera)
    label_sunda(d, kamera, 1 - c.p(0.75, 0.9))
    kota_sunda(d, kamera, 1 - c.p(0.75, 0.9))
    for poli in (VERLATEN, LANG):
        pulau(d, kamera, poli)
    pulau(d, kamera, KRAK_LAMA, (130, 105, 80))
    kx, ky = layar(SUNDA, kamera, KRAKATAU)
    label(d, (kx, ky + 90 * kamera.zoom / 2.2 + 30), "Krakatau", 44, (150, 30, 20))
    asap(img, kx, ky - 10, c.t, kuat=c.p(0.35, 0.5) * 0.8, tinggi=420, lebar=0.6)
    d = ImageDraw.Draw(img, "RGBA")
    # kapal turis
    a = c.p(0.6, 0.7)
    if a > 0:
        bx, by = kx + 210, ky + 80 + math.sin(c.t * 3) * 4
        d.polygon([(bx - 40, by), (bx + 40, by), (bx + 28, by + 18), (bx - 28, by + 18)], fill=(90, 60, 40, int(255 * a)))
        d.line((bx, by, bx, by - 50), fill=(60, 40, 30, int(255 * a)), width=4)
        d.polygon([(bx + 2, by - 48), (bx + 30, by - 10), (bx + 2, by - 10)], fill=(245, 240, 230, int(255 * a)))
        se.kartu(img, bx + 40, by - 110, "Turis datang nonton!", "Mei 1883", (60, 120, 170), alpha=a, tiang=False)
    se.kartu(img, kx - 200, ky - 260, "Mulai erupsi", "20 Mei 1883", MERAH, alpha=c.p(0.4, 0.5) * (1 - c.p(0.58, 0.62)), tiang=False)
    hdr(img, "Selat Sunda, 1883")
    return img


LEDAKAN = [0.12, 0.28, 0.45, 0.62]  # fraksi; yang ke-3 (indeks 2) paling besar


def a_ledakan(c):
    k = c.t / c.d
    goyang = 0.0
    for i, f in enumerate(LEDAKAN):
        if f <= k < f + 0.08:
            goyang = (40 if i == 2 else 18) * (1 - (k - f) / 0.08)
    kamera = Kamera(*cam(SUNDA, -6.11, 105.44, 2.4))
    img, d = peta_dgn(SUNDA, kamera, goyang, int(c.t * 30))
    for poli in (VERLATEN, LANG):
        pulau(d, kamera, poli)
    runtuh = c.p(0.66, 0.8)
    pulau(d, kamera, KRAK_LAMA, (130, 105, 80), 1 - runtuh)
    pulau(d, kamera, KRAK_SISA, (130, 105, 80), 1.0)
    kx, ky = layar(SUNDA, kamera, KRAKATAU)
    # cincin kejut
    for i, f in enumerate(LEDAKAN):
        if k >= f:
            r = (k - f) * c.d * 900
            cincin(d, kx, ky, r, (255, 240, 220), max(0, 1 - (k - f) * 5), 12 if i == 2 else 7)
    asap(img, kx, ky - 20, c.t, kuat=0.6 + 0.4 * c.p(0.1, 0.5), tinggi=900, lebar=1.4, warna=(70, 65, 62))
    d = ImageDraw.Draw(img, "RGBA")
    for i, f in enumerate(LEDAKAN):
        if f <= k < f + 0.05:
            kilat(img, (0.85 if i == 2 else 0.5) * (1 - (k - f) / 0.05))
    n = sum(1 for f in LEDAKAN if k >= f)
    d = ImageDraw.Draw(img, "RGBA")
    if n:
        se.kartu(img, 540, 1180, f"Ledakan {n} dari 4", "terbesar ± jam 10.02 pagi" if n >= 3 else "27 Agustus 1883",
                 MERAH, tiang=False)
    if runtuh > 0:
        se.kartu(img, 540, 1010, "2/3 pulau runtuh ke laut", "", (60, 60, 70), alpha=c.p(0.7, 0.78), tiang=False)
    hdr(img)
    return img


def km_ke_px(km, kamera):
    return km / KM_PER_DERAJAT * HINDIA.skala * kamera.zoom


def a_suara(c):
    kamera = se.kamera_antara(cam(HINDIA, -18, 106, 0.6), cam(HINDIA, -14, 78, 0.6), c.p(0.33, 0.5))
    img, d = peta_dgn(HINDIA, kamera)
    kx, ky = layar(HINDIA, kamera, KRAK_JAUH)
    jarak = 5200 * c.p(0.0, 0.55)
    for km in (1000, 2000, 3000, 4000):
        if jarak >= km:
            cincin(d, kx, ky, km_ke_px(km, kamera), (120, 60, 30), 0.35, 3)
    cincin(d, kx, ky, km_ke_px(jarak, kamera), (220, 70, 30), 0.9, 9)
    d.ellipse((kx - 14, ky - 14, kx + 14, ky + 14), fill=(220, 60, 30, 255), outline=(255, 255, 255, 255), width=4)
    label(d, (kx + 10, ky + 50), "Krakatau", 34, (150, 30, 20))
    if jarak >= 3100:
        x, y = layar(HINDIA, kamera, PERTH)
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(40, 30, 20, 255))
        se.kartu(img, x - 120, y - 20, "Perth, Australia", "± 3.100 km", (60, 120, 170), alpha=c.p(0.2, 0.26) * (1 - c.p(0.36, 0.42)))
    if jarak >= 4800:
        x, y = layar(HINDIA, kamera, RODRIGUES)
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(40, 30, 20, 255))
        se.kartu(img, x + 200, y - 20, "Pulau Rodrigues", "± 4.800 km · dekat Afrika", MERAH, alpha=c.p(0.47, 0.53),
                 skala=back_out((c.t / c.d - 0.47) / 0.1))
    se.kartu(img, 540, 720, "Suara terkeras dalam sejarah tercatat", "", (40, 40, 50),
             alpha=c.p(0.68, 0.75), tiang=False)
    hdr(img)
    return img


CAM_S5 = (cam(SUNDA, -6.0, 105.55, 1.0), cam(SUNDA, -5.85, 105.55, 0.95))


def a_tsunami(c):
    kamera = se.kamera_antara(*CAM_S5, c.p(0, 1))
    img, d = peta_dgn(SUNDA, kamera)
    label_sunda(d, kamera)
    pulau(d, kamera, KRAK_SISA)
    for poli in (VERLATEN, LANG):
        pulau(d, kamera, poli)
    kx, ky = layar(SUNDA, kamera, KRAKATAU)
    for i in range(3):
        f = clamp((c.t / c.d - 0.05 - i * 0.12) / 0.6)
        if f > 0:
            cincin(d, kx, ky, f * 1100, (235, 245, 255), (1 - f) * 0.95, 14 - i * 3)
            cincin(d, kx, ky, f * 1100 - 18, (80, 140, 200), (1 - f) * 0.7, 6)
    kota_sunda(d, kamera, merah=c.p(0.35, 0.5))
    se.kartu(img, 540, 1000, "Tsunami > 30 meter", "menyapu pesisir Banten & Lampung", (40, 100, 170),
             alpha=c.p(0.2, 0.3), tiang=False, skala=back_out((c.t / c.d - 0.2) / 0.1))
    a = c.p(0.62, 0.7)
    if a > 0:
        x, y = layar(SUNDA, kamera, KOTA_SUNDA["Telukbetung"])
        se.kartu(img, x + 30, y - 40, "Kapal uap Berouw", "terseret > 2 km ke daratan", (90, 60, 40), alpha=a,
                 skala=back_out((c.t / c.d - 0.62) / 0.1))
    hdr(img)
    return img


def _angka(d, x, y, teks_angka, label_, warna, a):
    se.teks(d, (x, y), teks_angka, 130, warna, nama_font="caption", stroke=9, stroke_warna=(0, 0, 0), alpha=a)
    se.teks(d, (x, y + 100), label_, 42, PUTIH, nama_font="caption", stroke=5, stroke_warna=(0, 0, 0), alpha=a)


def a_korban(c):
    kamera = Kamera(*cam(SUNDA, -5.95, 105.55, 1.0))
    img, d = peta_dgn(SUNDA, kamera)
    se.tint(img, (10, 5, 0), 0.65)
    d = ImageDraw.Draw(img, "RGBA")
    n = int(36417 * c.p(0.05, 0.5))
    _angka(d, 540, 700, f"{n:,}".replace(",", "."), "jiwa meninggal", MERAH, c.p(0.02, 0.1))
    _angka(d, 540, 1000, f"± {int(165 * c.p(0.5, 0.85))}", "desa & kota hancur", (240, 150, 50), c.p(0.48, 0.55))
    hdr(img)
    return img


def a_dunia(c):
    kamera = Kamera(*cam(HINDIA, -2, 88, 0.58))
    img, d = peta_dgn(HINDIA, kamera)
    k = c.t / c.d
    # abu menyebar ke barat sepanjang khatulistiwa lalu melebar
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    rng = random.Random(4)
    sebar = c.p(0.0, 0.6)
    for i in range(140):
        lon = 105.4 - rng.random() * 80 * sebar
        lat = -6 + rng.gauss(0, 4 + 14 * sebar)
        x, y = layar(HINDIA, kamera, (lat, lon))
        x += math.sin(c.t * 0.8 + i) * 10
        r = rng.uniform(30, 80)
        dl.ellipse((x - r, y - r, x + r, y + r), fill=(110, 105, 100, int(55 * clamp(sebar * 3))))
    img.alpha_composite(lap)
    # langit senja merah
    se.tint(img, (230, 70, 30), 0.28 * c.p(0.45, 0.6))
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 760, "Abu menyebar ke seluruh dunia", "", (70, 70, 80), alpha=c.p(0.08, 0.16) * (1 - c.p(0.4, 0.45)), tiang=False)
    se.kartu(img, 540, 760, "Suhu bumi turun", "± setahun setelahnya", (40, 100, 170), alpha=c.p(0.38, 0.45) * (1 - c.p(0.62, 0.66)), tiang=False)
    se.kartu(img, 540, 760, "Senja merah menyala", "terlihat di berbagai negara", (200, 70, 30), alpha=c.p(0.5, 0.56) * (1 - c.p(0.62, 0.66)), tiang=False, )
    a = c.p(0.66, 0.74)
    if a > 0:
        se.kartu(img, 540, 900, "Amerika: pemadam kebakaran dikerahkan", "dikira ada kebakaran besar", MERAH, alpha=a,
                 tiang=False, skala=back_out((k - 0.66) / 0.1))
    hdr(img)
    return img


TELEGRAF = [(-6.1, 106.8), (-2, 101), (1.3, 103.8), (6, 98), (8, 80), (12.8, 45), (14, 38)]


def a_telegraf(c):
    kamera = Kamera(*cam(HINDIA, 2, 78, 0.6))
    img, d = peta_dgn(HINDIA, kamera)
    titik = [layar(HINDIA, kamera, ll) for ll in TELEGRAF]
    ujung = se.garis_putus(d, titik, c.p(0.1, 0.7), (30, 60, 120), tebal=6, putus=14, celah=10)
    x0, y0 = titik[0]
    d.ellipse((x0 - 12, y0 - 12, x0 + 12, y0 + 12), fill=(30, 60, 120, 255), outline=(255, 255, 255, 255), width=3)
    label(d, (x0 + 10, y0 + 46), "Batavia", 34)
    if ujung:
        label(d, (ujung[0] + 10, ujung[1] - 50), "ke Eropa →", 34, (30, 60, 120), c.p(0.6, 0.7))
    se.kartu(img, 540, 1000, "Kabar menyebar lewat telegraf", "dibaca dunia hampir bersamaan", (30, 60, 120),
             alpha=c.p(0.35, 0.45), tiang=False, skala=back_out((c.t / c.d - 0.35) / 0.1))
    hdr(img)
    return img


def a_anak(c):
    kamera = Kamera(*cam(SUNDA, -6.11, 105.43, 2.4))
    img, d = peta_dgn(SUNDA, kamera)
    for poli in (VERLATEN, LANG, KRAK_SISA):
        pulau(d, kamera, poli)
    kx, ky = layar(SUNDA, kamera, (-6.102, 105.423))
    muncul = c.p(0.25, 0.5)
    if muncul > 0:
        r = 46 * muncul
        d.ellipse((kx - r * 1.3, ky - r, kx + r * 1.3, ky + r), fill=(70, 60, 55, 255), outline=(30, 25, 20, 255), width=4)
        d.polygon([(kx - r * 0.7, ky), (kx, ky - r * 1.4), (kx + r * 0.7, ky)], fill=(90, 75, 65, 255))
        asap(img, kx, ky - r, c.t, kuat=muncul * 0.7, tinggi=380, lebar=0.5, seed=5)
    se.kartu(img, kx + 20, ky - 230, "Anak Krakatau", "muncul dari laut · 1927", (150, 30, 20), alpha=c.p(0.35, 0.45))
    se.kartu(img, 540, 1180, "Sampai sekarang masih aktif", "", MERAH, alpha=c.p(0.75, 0.82), tiang=False,
             skala=back_out((c.t / c.d - 0.75) / 0.1))
    hdr(img, "1927 – sekarang")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(SUNDA, -6.0, 105.6, 1.0))
    img, d = peta_dgn(SUNDA, kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 440, 990, 1000), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 520), "INGAT YA!", 64, MERAH, nama_font="judul", alpha=a)
        # gelombang surut -> panah ke bukit
        for i in range(3):
            y = 640 + i * 26
            d.arc((170 + i * 10, y - 30, 330 - i * 10, y + 30), 200, 340, fill=(40, 100, 170, int(255 * a)), width=8)
        se.teks(d, (300, 760), "air laut surut", 34, TINTA, alpha=a)
        d.polygon([(700, 760), (840, 600), (980, 760)], fill=(120, 150, 90, int(255 * a)), outline=(40, 30, 20, int(255 * a)))
        se.garis_putus(d, [(420, 680), (560, 660), (760, 640)], c.p(0.15, 0.4), MERAH, tebal=8)
        se.teks(d, (840, 800), "lari ke tempat tinggi", 34, TINTA, alpha=a)
        se.teks(d, (540, 920), "Jangan nunggu, langsung lari!", 44, (150, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Ada suara ledakan yang kedengeran sampai empat ribu delapan ratus kilometer jauhnya. "
                   "Dan itu terjadi di Indonesia.", a_hook, transisi=False),
    Adegan("lokasi", "Tahun seribu delapan ratus delapan puluh tiga. Di Selat Sunda, antara Jawa dan Sumatra, "
                     "ada pulau gunung api bernama Krakatau. Sejak bulan Mei, gunung ini udah mulai erupsi. "
                     "Bahkan ada turis yang datang buat nonton.", a_lokasi),
    Adegan("ledakan", "Tanggal dua puluh tujuh Agustus pagi, terjadi empat ledakan raksasa. Yang paling besar, "
                      "sekitar jam sepuluh pagi. Dua per tiga pulaunya hancur, runtuh ke laut.", a_ledakan,
           transisi=False),
    Adegan("suara", "Suaranya kedengeran sampai Australia, bahkan sampai Pulau Rodrigues, dekat Afrika. "
                    "Ini dianggap suara terkeras dalam sejarah yang pernah tercatat.", a_suara),
    Adegan("tsunami", "Tapi yang paling mematikan, tsunami. Gelombang setinggi lebih dari tiga puluh meter menyapu "
                      "pesisir Banten dan Lampung. Kapal uap Berouw sampai terseret lebih dari dua kilometer ke daratan.",
           a_tsunami),
    Adegan("korban", "Lebih dari tiga puluh enam ribu orang meninggal. Ratusan desa hilang.", a_korban),
    Adegan("dunia", "Abunya naik ke langit, nyebar ke seluruh dunia. Suhu bumi turun. Langit senja jadi merah menyala. "
                    "Di Amerika, pemadam kebakaran sampai dikerahkan, karena orang kira ada kebakaran besar.", a_dunia),
    Adegan("telegraf", "Kabarnya nyebar cepat lewat kabel telegraf. Krakatau jadi salah satu bencana pertama "
                       "yang beritanya dibaca seluruh dunia hampir bersamaan.", a_telegraf, transisi=False),
    Adegan("anak", "Tapi ceritanya belum selesai. Tahun seribu sembilan ratus dua puluh tujuh, muncul gunung baru "
                   "dari laut. Namanya, Anak Krakatau. Dan sampai sekarang, dia masih aktif.", a_anak),
    Adegan("penutup", "Jadi inget ya. Kalau air laut tiba-tiba surut, jangan ditonton. Langsung lari ke tempat tinggi! "
                      "Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
