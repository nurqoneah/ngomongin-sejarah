"""Shorts ±90 detik: Sejarah Candu di Nusantara — dari monopoli VOC sampai candu Republik.

Pemicu: pabrik sabu ± 1,2 ton dibongkar di Pidie, Aceh (diumumkan 23 Okt 2026).
Peta Asia + peta Nusantara + ilustrasi (bunga opium, grafik pemasukan kolonial).
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

NAMA_FILE = "sejarah-candu-nusantara-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "SEJARAH CANDU"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
UNGU = (110, 50, 110)
VOC = (200, 110, 30)
BELANDA = (40, 70, 130)
COKLAT = (120, 80, 40)

MADURA = [(-6.88, 112.75), (-7.15, 112.72), (-7.25, 113.4), (-7.1, 114.05), (-6.88, 114.1), (-6.85, 113.4)]

print("  menyiapkan peta Asia...")
PETA_ASIA = Peta(60, 128, -25, 35, 55, [], [(30, 85, 4), (35, 100, 4), (27, 92, 2)], seed=41, darat=pd.SEMUA)
print("  menyiapkan peta Nusantara...")
PETA = Peta(88, 125, -18, 16, 100, [], [(-2, 114, 1.5), (0, 101, 1.2), (5, 117, 1.0), (-7.3, 110.4, 0.6),
                                        (-7.9, 112.6, 0.5)], seed=27, darat=pd.SEMUA + [MADURA])

PIDIE = (5.2, 96.0)
BATAVIA = (-6.15, 106.85)
MATARAM = (-7.85, 110.4)
MADURA_TENGAH = (-7.05, 113.4)
KEDIRI = (-7.82, 112.0)
WONOSARI = (-7.96, 110.6)
KLATEN = (-7.7, 110.6)
YOGYA = (-7.8, 110.37)
SINGAPURA = (1.3, 103.8)
BENGAL = (22.5, 88.4)
SELAT = (4.0, 99.5)


# ------------------------------------------------------------------ helper

def cam(peta, lat, lon, zoom):
    x, y = peta.px(lat, lon)
    return (x, y, zoom)


def peta(p, kamera):
    img = se.render_peta(p, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(p, kamera, ll):
    return kamera.layar(*p.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def titik(d, x, y, warna=MERAH, r=12, alpha=1.0, denyut=0.0):
    a = int(255 * alpha)
    if denyut > 0:
        rr = r + 30 * denyut
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=tuple(warna) + (int(a * (1 - denyut)),), width=5)
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=(255, 255, 255, a), width=3)


def muncul(c, a):
    """Skala 'pop' untuk kartu yang muncul di fraksi a."""
    return back_out((c.t / c.d - a) / 0.1)


def bunga(d, x, y, s=1.0, alpha=1.0, mekar=1.0, goyang=0.0):
    """Bunga opium (poppy) ilustrasi: tangkai, 4 kelopak merah, bonggol gelap."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    gx = x + math.sin(goyang) * 10 * s
    d.line((x, y + 260 * s, x + 6 * s, y + 140 * s, gx, y), fill=(70, 110, 50, a), width=max(3, int(10 * s)))
    d.ellipse((x - 70 * s, y + 150 * s, x + 10 * s, y + 185 * s), fill=(80, 125, 60, a))
    r = 85 * s * mekar
    for i in range(4):
        sud = i * math.pi / 2 + math.pi / 4 + goyang * 0.1
        cx, cy = gx + math.cos(sud) * r * 0.55, y + math.sin(sud) * r * 0.55
        d.ellipse((cx - r * 0.75, cy - r * 0.7, cx + r * 0.75, cy + r * 0.7), fill=(205, 40, 40, a),
                  outline=(120, 15, 15, a), width=max(2, int(4 * s)))
    d.ellipse((gx - 26 * s, y - 26 * s, gx + 26 * s, y + 26 * s), fill=(45, 30, 40, a))
    for i in range(10):
        sud = i * math.pi / 5
        d.line((gx, y, gx + math.cos(sud) * 36 * s, y + math.sin(sud) * 36 * s), fill=(30, 20, 25, a),
               width=max(1, int(3 * s)))


def kapal(d, x, y, s=1.0, warna=(110, 70, 35), alpha=1.0, arah=1):
    a = int(255 * alpha)
    d.polygon([(x - 40 * s, y), (x + 40 * s, y), (x + 28 * s * arah if arah > 0 else x + 28 * s, y + 16 * s),
               (x - 28 * s, y + 16 * s)], fill=tuple(warna) + (a,), outline=(30, 20, 10, a))
    d.line((x, y, x, y - 52 * s), fill=(40, 25, 10, a), width=max(2, int(4 * s)))
    d.polygon([(x + 3 * s, y - 50 * s), (x + 34 * s * arah, y - 10 * s), (x + 3 * s, y - 8 * s)],
              fill=(240, 230, 205, a), outline=(60, 45, 30, a))


def pabrik(d, x, y, s=1.0, alpha=1.0, t=0.0):
    a = int(255 * alpha)
    d.rectangle((x - 60 * s, y - 40 * s, x + 60 * s, y + 30 * s), fill=(150, 90, 60, a), outline=(40, 25, 15, a), width=3)
    d.polygon([(x - 60 * s, y - 40 * s), (x - 30 * s, y - 62 * s), (x, y - 40 * s), (x + 30 * s, y - 62 * s),
               (x + 60 * s, y - 40 * s)], fill=(120, 70, 45, a), outline=(40, 25, 15, a))
    d.rectangle((x + 34 * s, y - 110 * s, x + 50 * s, y - 50 * s), fill=(110, 65, 45, a), outline=(40, 25, 15, a))
    for i in range(4):
        f = (t * 0.5 + i * 0.25) % 1
        r = (10 + f * 26) * s
        cx, cy = x + 42 * s + f * 30 * s, y - 120 * s - f * 90 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(120, 110, 105, int(a * 0.7 * (1 - f))))


def asap_candu(d, x, y, t, s=1.0, alpha=1.0, seed=0):
    """Gumpalan asap kecil (ikon tempat mengisap candu)."""
    a = int(255 * alpha)
    for i in range(3):
        f = (t * 0.6 + i / 3 + seed * 0.37) % 1
        r = (8 + f * 18) * s
        cx, cy = x + math.sin(f * 6 + seed) * 8 * s, y - f * 60 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(235, 230, 220, int(a * 0.8 * (1 - f))))
    d.ellipse((x - 10 * s, y - 6 * s, x + 10 * s, y + 6 * s), fill=(90, 50, 30, a))


def jawa_sorot(img, p, kamera, warna, alpha, poli=pd.JAWA):
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.polygon(se.halus([layar(p, kamera, ll) for ll in poli]), fill=tuple(warna) + (int(110 * alpha),))
    img.alpha_composite(lap)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = Image.new("RGBA", (W, H), (22, 18, 20, 255))
    d = ImageDraw.Draw(img, "RGBA")
    # sorot lampu
    se.glow(img, 540, 760, 520, (120, 90, 60), 0.5)
    d = ImageDraw.Draw(img, "RGBA")
    # drum-drum barang bukti
    for i in range(5):
        x = 220 + i * 160
        a = c.p(0.0 + i * 0.03, 0.08 + i * 0.03)
        if a > 0:
            aa = int(255 * a)
            d.rounded_rectangle((x - 55, 1000, x + 55, 1180), 12, fill=(40, 90, 150, aa), outline=(15, 30, 60, aa), width=4)
            for yy in (1040, 1140):
                d.line((x - 55, yy, x + 55, yy), fill=(20, 50, 90, aa), width=5)
    goyang = math.sin(c.t * 40) * 6 * (1 - c.p(0.0, 0.25))
    s = back_out(c.t / 0.35)
    ton = 1.2 * c.p(0.0, 0.2)
    se.teks(d, (540 + goyang, 720), f"{ton:.1f} TON".replace(".", ","), int(190 * s) + 1, (255, 90, 70),
            nama_font="caption", stroke=10, stroke_warna=(10, 5, 5))
    se.teks(d, (540, 880), "narkoba, dari satu pabrik di Aceh", 44, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(10, 5, 5), alpha=c.p(0.1, 0.2) * (1 - c.p(0.45, 0.5)))
    a = c.p(0.5, 0.58)
    if a > 0:
        se.tint(img, (60, 30, 10), 0.4 * a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 880), "Tapi dulu, yang jualan candu…", 52, (255, 225, 170), nama_font="caption", stroke=7,
                stroke_warna=(10, 5, 5), alpha=a)
        se.teks(d, (540, 1290), "PEMERINTAHNYA SENDIRI", 70, (255, 200, 60), nama_font="caption", stroke=8,
                stroke_warna=(10, 5, 5), alpha=c.p(0.75, 0.82))
    hdr(img, alpha=c.p(0.85, 0.95))
    return img


def a_tren(c):
    kamera = se.kamera_antara(cam(PETA, 4.5, 97.5, 1.3), cam(PETA, -1.0, 106.0, 0.62), c.p(0.5, 0.8))
    img, d = peta(PETA, kamera)
    x, y = layar(PETA, kamera, PIDIE)
    titik(d, x, y, MERAH, 14, denyut=(c.t * 0.8) % 1)
    label(d, (x + 110, y - 50), "Pidie, Aceh", 42, (120, 20, 15), 1 - c.p(0.5, 0.6), "caption")
    se.kartu(img, 560, 1050, "Pabrik sabu terbesar se-Indonesia", "Pidie, Aceh · dibongkar Oktober 2026", MERAH,
             alpha=c.p(0.05, 0.13) * (1 - c.p(0.48, 0.54)), tiang=False, skala=muncul(c, 0.05))
    se.kartu(img, 540, 760, "Candu = opium", "sejarahnya panjang di Nusantara", UNGU, alpha=c.p(0.62, 0.7),
             tiang=False, skala=muncul(c, 0.62))
    hdr(img, "Lagi rame")
    return img


RUTE_ASAL = [BENGAL, (16.0, 92.5), (9.0, 95.5), SELAT, (1.6, 102.8), (-2.5, 106.8), BATAVIA]


def a_asal(c):
    kamera = Kamera(*cam(PETA_ASIA, 6.0, 97.5, 0.6))
    img, d = peta(PETA_ASIA, kamera)
    ix, iy = layar(PETA_ASIA, kamera, BENGAL)
    label(d, (ix + 150, iy - 20), "dari India", 44, TINTA, c.p(0.3, 0.4))
    nx, ny = layar(PETA_ASIA, kamera, BATAVIA)
    label(d, (nx - 160, ny - 70), "NUSANTARA", 44, TINTA, c.p(0.3, 0.4))
    pts = [layar(PETA_ASIA, kamera, ll) for ll in RUTE_ASAL]
    k = c.p(0.35, 0.95)
    se.garis_putus(d, pts, k, (120, 20, 15), tebal=7)
    if k > 0:
        (kx, ky), _ = se.titik_di_jalur(pts, k)
        kapal(d, kx, ky - 6, 0.9)
    # panel bunga opium
    a = c.p(0.0, 0.1) * (1 - c.p(0.4, 0.48))
    if a > 0:
        se.panel(img, (240, 440, 840, 1240), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        bunga(d, 540, 700, 1.3, a, mekar=back_out(c.t / 0.6), goyang=math.sin(c.t * 2) * 0.6)
        se.teks(d, (540, 1150), "getah bunga opium", 46, (150, 30, 30), nama_font="tangan", alpha=a)
    se.kartu(img, 720, 560, "Dibawa pedagang lewat laut", "jauh sebelum Belanda berkuasa", COKLAT,
             alpha=c.p(0.55, 0.62), tiang=False, skala=muncul(c, 0.55))
    hdr(img, "Asal-usul")
    return img


def a_1677(c):
    kamera = Kamera(*cam(PETA, -9.3, 108.6, 1.25))
    img, d = peta(PETA, kamera)
    label(d, layar(PETA, kamera, (-7.35, 108.9)), "JAWA", 46, TINTA, 0.8)
    bx, by = layar(PETA, kamera, BATAVIA)
    mx, my = layar(PETA, kamera, MATARAM)
    titik(d, bx, by, VOC, 14, c.p(0.0, 0.1))
    titik(d, mx, my, (90, 60, 30), 14, c.p(0.1, 0.2))
    se.garis_putus(d, [(bx, by), ((bx + mx) / 2, min(by, my) - 120), (mx, my)], c.p(0.25, 0.45), (120, 20, 15),
                   tebal=6, panah=False)
    se.kartu(img, bx + 40, by - 10, "VOC", "Batavia", VOC, alpha=c.p(0.02, 0.1), skala=muncul(c, 0.02))
    se.kartu(img, mx, my - 10, "Amangkurat II", "Raja Mataram", (90, 60, 30), alpha=c.p(0.12, 0.2),
             skala=muncul(c, 0.12))
    s = back_out((c.t / c.d) / 0.15)
    se.teks(d, (540, 1120), "1677", int(170 * s) + 1, (255, 220, 150), nama_font="caption", stroke=9,
            stroke_warna=(40, 20, 10), alpha=1 - c.p(0.45, 0.5))
    a = c.p(0.5, 0.58)
    if a > 0:
        se.panel(img, (110, 960, 970, 1300), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1030), "PERJANJIAN 1677", 44, (130, 40, 20), nama_font="judul", alpha=a)
        se.teks(d, (540, 1120), "Impor candu ke Mataram", 44, TINTA, nama_font="tangan", alpha=a)
        se.teks(d, (540, 1200), "hanya boleh lewat VOC", 50, (170, 30, 20), nama_font="caption", alpha=c.p(0.62, 0.7))
    hdr(img, "Monopoli VOC")
    return img


def a_volume(c):
    kamera = Kamera(*cam(PETA, -3.5, 107.5, 0.75))
    img, d = peta(PETA, kamera)
    rute = [layar(PETA, kamera, ll) for ll in [(6.0, 95.0), SELAT, (1.6, 102.8), (-2.5, 106.8), BATAVIA]]
    se.garis_putus(d, rute, 1.0, (120, 20, 15), tebal=5, alpha=0.6, panah=False)
    for i in range(5):
        f = (c.t * 0.22 + i * 0.2) % 1
        (kx, ky), _ = se.titik_di_jalur(rute, f)
        kapal(d, kx, ky - 6, 0.75, alpha=clamp(f * 6) * clamp((1 - f) * 6))
    se.kartu(img, 540, 560, "Puluhan ton candu", "masuk ke Jawa tiap tahun", VOC, alpha=c.p(0.05, 0.13),
             tiang=False, skala=muncul(c, 0.05))
    # tempat mengisap candu bermunculan di kota-kota Jawa
    kota = [BATAVIA, (-6.7, 108.55), (-6.97, 110.42), (-7.57, 110.82), YOGYA, (-7.25, 112.75), KEDIRI,
            (-7.63, 111.52), (-6.9, 109.67), (-7.0, 113.86), (-8.17, 113.7), (-6.6, 106.8)]
    n = int(len(kota) * c.p(0.45, 0.9) + 0.999)
    for i, ll in enumerate(kota[:n]):
        x, y = layar(PETA, kamera, ll)
        asap_candu(d, x, y, c.t, 1.3, 1.0, i)
    se.kartu(img, 540, 1230, "Tempat mengisap candu", "muncul di mana-mana", (90, 60, 40), alpha=c.p(0.5, 0.58),
             tiang=False, skala=muncul(c, 0.5))
    hdr(img, "Abad ke-18 – 19")
    return img


def a_regie(c):
    kamera = se.kamera_antara(cam(PETA, -7.2, 112.0, 1.25), cam(PETA, -6.9, 108.8, 1.15), c.p(0.55, 0.7))
    img, d = peta(PETA, kamera)
    jawa_sorot(img, PETA, kamera, BELANDA, c.p(0.1, 0.18), MADURA)
    jawa_sorot(img, PETA, kamera, BELANDA, c.p(0.3, 0.45))
    d = ImageDraw.Draw(img, "RGBA")
    x, y = layar(PETA, kamera, MADURA_TENGAH)
    label(d, (x, y - 60), "Madura", 40, (20, 40, 90), c.p(0.1, 0.18) * (1 - c.p(0.55, 0.62)), "caption")
    s = back_out((c.t / c.d) / 0.15)
    keluar = 1 - c.p(0.62, 0.68)
    se.teks(d, (540, 520), "1894", int(150 * s) + 1, (210, 225, 255), nama_font="caption", stroke=9,
            stroke_warna=(15, 20, 40), alpha=keluar)
    se.kartu(img, 540, 690, "Opium Regie", "negara jadi penjual candu", BELANDA, alpha=c.p(0.04, 0.12) * keluar,
             tiang=False, skala=muncul(c, 0.04))
    a = c.p(0.68, 0.75)
    if a > 0:
        bx, by = layar(PETA, kamera, BATAVIA)
        pabrik(d, bx, by - 10, 1.2, a, c.t)
        se.kartu(img, clamp(bx + 120, 300, W - 300), by + 200, "Pabrik candu Salemba", "kini kawasan kampus UI",
                 MERAH, alpha=a, tiang=False, skala=muncul(c, 0.68))
    hdr(img, "Pemerintah Hindia Belanda")
    return img


def a_uang(c):
    img = Image.new("RGBA", (W, H), (30, 28, 34, 255))
    se.panel(img, (80, 420, 1000, 1280), alpha=c.p(0, 0.08), warna=(247, 236, 208))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 500), "UNTUNG CANDU · 1905", 48, (120, 40, 30), nama_font="judul", alpha=c.p(0.02, 0.1))
    juta = 20 * c.p(0.1, 0.4)
    se.teks(d, (540, 620), f"± {juta:.0f} JUTA", 100, (150, 100, 20), nama_font="caption", stroke=6,
            stroke_warna=(255, 255, 255), alpha=c.p(0.08, 0.15))
    se.teks(d, (540, 710), "gulden", 44, TINTA, nama_font="tangan", alpha=c.p(0.08, 0.15))
    # pie: 15% dari pemasukan kolonial
    cx, cy, r = 540, 960, 170
    a = c.p(0.45, 0.52)
    if a > 0:
        aa = int(255 * a)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(120, 115, 105, aa), outline=(40, 30, 20, aa), width=5)
        k = c.p(0.5, 0.75)
        if k > 0:
            d.pieslice((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * 0.15 * k, fill=(200, 45, 40, aa),
                       outline=(40, 30, 20, aa), width=5)
        se.teks(d, (cx + 250, cy - 120), "15 %", 80, MERAH, nama_font="caption", stroke=5,
                stroke_warna=(255, 255, 255), alpha=c.p(0.7, 0.78))
        se.teks(d, (540, 1200), "± 15% pemasukan pemerintah kolonial", 38, TINTA, nama_font="tangan", alpha=a)
    hdr(img, "Kas kolonial")
    return img


def a_revolusi(c):
    kamera = Kamera(*cam(PETA, -3.5, 106.0, 0.7))
    img, d = peta(PETA, kamera)
    # kapal blokade Belanda mengepung Jawa & Sumatra
    keliling = [(5.8, 94.0), (2.5, 97.5), (2.2, 102.0), (-1.5, 107.5), (-4.5, 110.5), (-5.5, 114.8), (-9.2, 114.5),
                (-9.0, 110.0), (-8.3, 106.0), (-5.5, 101.5), (-2.0, 98.5), (2.0, 95.0)]
    k = c.p(0.35, 0.6)
    for i, ll in enumerate(keliling):
        if i / len(keliling) < k:
            x, y = layar(PETA, kamera, ll)
            kapal(d, x, y, 0.8, BELANDA, arah=1 if i % 2 else -1)
    x, y = layar(PETA, kamera, YOGYA)
    titik(d, x, y, MERAH, 14)
    se.bendera(d, x, y - 10, MERAH, 1.2, 1.0, c.t)
    label(d, (x - 10, y + 50), "Yogyakarta", 36, TINTA, c.p(0.05, 0.12), "caption")
    s = back_out((c.t / c.d) / 0.15)
    se.teks(d, (540, 520), "1945 – 1949", int(110 * s) + 1, (255, 225, 170), nama_font="caption", stroke=9,
            stroke_warna=(40, 20, 10))
    se.kartu(img, 540, 690, "Republik baru: kas kosong", "", MERAH, alpha=c.p(0.08, 0.16), tiang=False,
             skala=muncul(c, 0.08))
    se.kartu(img, 540, 830, "Laut diblokade Belanda", "", BELANDA, alpha=c.p(0.38, 0.46), tiang=False,
             skala=muncul(c, 0.38))
    se.kartu(img, 540, 1250, "Candu di gudang pemerintah ikut dijual", "", UNGU, alpha=c.p(0.7, 0.78), tiang=False,
             skala=muncul(c, 0.7))
    hdr(img, "Plot twist")
    return img


def a_selundup(c):
    kamera = se.kamera_antara(cam(PETA, -7.6, 111.3, 1.5), cam(PETA, -3.0, 106.8, 0.72), c.p(0.3, 0.45))
    img, d = peta(PETA, kamera)
    kx, ky = layar(PETA, kamera, KEDIRI)
    wx, wy = layar(PETA, kamera, WONOSARI)
    lx, ly = layar(PETA, kamera, KLATEN)
    a1 = c.p(0.0, 0.08)
    a2 = c.p(0.1, 0.18)
    titik(d, kx, ky, UNGU, 13, a1)
    titik(d, wx, wy, COKLAT, 12, a2)
    titik(d, lx, ly, COKLAT, 12, a2)
    zoom_dekat = 1 - c.p(0.3, 0.4)
    if zoom_dekat > 0:
        label(d, (kx + 10, ky + 55), "Kediri · gudang", 36, (80, 20, 80), a1 * zoom_dekat, "caption")
        label(d, (wx - 20, wy + 55), "Wonosari", 34, TINTA, a2 * zoom_dekat, "caption")
        label(d, (lx - 20, ly - 50), "Klaten", 34, TINTA, a2 * zoom_dekat, "caption")
        se.kartu(img, 540, 620, "Disimpan, lalu diolah", "gudang Kediri · pabrik Wonosari & Klaten", UNGU,
                 alpha=a1 * zoom_dekat, tiang=False, skala=muncul(c, 0.0))
    # jalur selundup ke Singapura
    rute = [layar(PETA, kamera, ll) for ll in [(-6.9, 110.4), (-5.5, 108.5), (-2.5, 106.2), (0.2, 104.6), SINGAPURA]]
    k = c.p(0.4, 0.6)
    se.garis_putus(d, rute, k, (120, 20, 15), tebal=7)
    if 0 < k < 1:
        (bx, by), _ = se.titik_di_jalur(rute, k)
        kapal(d, bx, by - 6, 0.9, arah=-1)
    sx, sy = layar(PETA, kamera, SINGAPURA)
    titik(d, sx, sy, MERAH, 13, c.p(0.55, 0.6))
    label(d, (sx + 20, sy - 50), "SINGAPURA", 40, (120, 20, 15), c.p(0.55, 0.62), "caption")
    for i, (judul, sub) in enumerate([("Gaji pegawai", ""), ("Perwakilan di luar negeri", ""),
                                      ("Beli senjata", "")]):
        a0 = 0.66 + i * 0.09
        se.kartu(img, 540, 940 + i * 120, judul, sub, (60, 110, 60), alpha=c.p(a0, a0 + 0.06), tiang=False,
                 skala=muncul(c, a0))
    hdr(img, "Candu buat revolusi")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(PETA, -3.5, 106.0, 0.7))
    img, d = peta(PETA, kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1080), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Dulu dilegalkan penjajah", 48, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 645), "candu tetap bikin orang ketagihan & rusak", 34, (90, 70, 50), alpha=a)
        bunga(d, 540, 790, 0.75, a, goyang=math.sin(c.t * 2) * 0.5)
        d.ellipse((420, 690, 660, 930), outline=(200, 30, 30, int(255 * a)), width=16)
        d.line((455, 895, 625, 725), fill=(200, 30, 30, int(255 * a)), width=16)
        se.teks(d, (540, 1010), "Jauhi narkoba!", 52, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Satu koma dua ton narkoba, dari satu pabrik rahasia di Aceh. Tapi dulu, yang jualan candu di "
                   "negeri ini justru, pemerintahnya sendiri.", a_hook, transisi=False),
    Adegan("tren", "Lagi rame soal pabrik sabu terbesar se-Indonesia di Pidie? Ternyata, Nusantara punya sejarah "
                   "panjang sama candu, alias opium.", a_tren),
    Adegan("asal", "Candu itu dari getah bunga opium. Pedagang asing membawanya ke Nusantara lewat laut, jauh "
                   "sebelum Belanda berkuasa.", a_asal),
    Adegan("1677", "Lalu tahun enam belas tujuh puluh tujuh, VOC bikin perjanjian dengan Raja Mataram, Amangkurat "
                   "Kedua. Isinya, cuma VOC yang boleh memasukkan candu ke Mataram.", a_1677),
    Adegan("volume", "Kapal-kapal VOC pun membawa candu ke Jawa, puluhan ton tiap tahun. Tempat mengisap candu "
                     "muncul di mana-mana.", a_volume, transisi=False),
    Adegan("regie", "Tahun delapan belas sembilan puluh empat, pemerintah Hindia Belanda mengambil alih langsung. "
                    "Namanya Opium Regie. Dicoba dulu di Madura, lalu meluas ke seluruh Jawa. Pabrik candunya ada "
                    "di Salemba, kawasan yang sekarang jadi kampus UI.", a_regie, transisi=False),
    Adegan("uang", "Untungnya gede banget. Tahun sembilan belas nol lima, sekitar dua puluh juta gulden. Kira-kira "
                   "lima belas persen pemasukan pemerintah kolonial.", a_uang),
    Adegan("revolusi", "Plot twist-nya, setelah merdeka, Republik nggak punya uang, dan lautnya diblokade Belanda. "
                       "Akhirnya, candu di gudang pemerintah ikut diperdagangkan.", a_revolusi),
    Adegan("selundup", "Candu disimpan di Kediri, diolah di Wonosari dan Klaten, lalu sebagian diselundupkan ke "
                       "Singapura. Hasilnya buat bayar gaji pegawai, perwakilan di luar negeri, sampai beli senjata.",
           a_selundup, transisi=False),
    Adegan("penutup", "Sekarang, narkoba dilarang keras. Sejarahnya ngingetin kita, candu itu bisnis gede yang bikin "
                      "orang ketagihan dan rusak. Jauhi narkoba, ya. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
