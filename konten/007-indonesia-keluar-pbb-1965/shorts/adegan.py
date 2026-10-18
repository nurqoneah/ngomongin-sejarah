"""Shorts ±90 detik: Indonesia keluar dari PBB (1965) dan kembali lagi (1966).

Peta Asia Tenggara (Hambalang, konfrontasi dengan Malaysia) + adegan ilustrasi: bola dunia PBB, deretan kursi
anggota, meja Dewan Keamanan, koran & surat, cetak biru gedung CONEFO (sekarang Gedung DPR/MPR), Majelis Umum.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "indonesia-keluar-pbb-1965-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "KELUAR DARI PBB"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU_PBB = (75, 146, 219)
BIRU = (40, 80, 150)
HIJAU = (30, 120, 70)
ABU = (110, 110, 120)

print("  menyiapkan peta Asia Tenggara...")
PETA = Peta(90, 125, -12, 22, 100, [], [(-6.8, 107.3, 0.6), (0, 101, 1.2), (5, 117, 1.0), (4.5, 101.6, 1.0),
                                        (18, 101, 3), (14, 106, 2)],
            seed=33, darat=pd.SEMUA)

HAMBALANG = (-6.55, 106.93)
JAKARTA = (-6.15, 106.83)
# wilayah Malaysia (disederhanakan, untuk sorotan)
MALAYA = [(6.5, 100.1), (6.3, 101.9), (5.6, 102.6), (4.6, 103.45), (3.4, 103.45), (2.4, 103.9), (1.5, 104.25),
          (1.35, 103.5), (2.0, 102.2), (2.8, 101.3), (3.8, 100.8), (4.8, 100.4), (5.8, 100.3)]
BORNEO_MY = [(1.0, 109.6), (1.7, 110.4), (2.1, 111.3), (2.9, 113.0), (4.0, 113.9), (4.9, 115.0), (5.4, 115.6),
             (6.9, 116.8), (6.4, 117.7), (5.8, 118.3), (5.0, 119.2), (4.3, 117.6), (4.2, 116.0), (3.0, 115.5),
             (1.9, 114.6), (1.3, 113.0), (1.1, 111.6), (1.3, 110.9), (0.9, 110.4)]


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


def hdr(img, sub="1965 – 1966", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def _gradasi(atas, bawah):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (np.array(atas, np.float32) * (1 - g) + np.array(bawah, np.float32) * g).repeat(W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    return img, ImageDraw.Draw(img, "RGBA")


def cincin(d, x, y, r, warna, alpha, tebal=8):
    if alpha <= 0.01 or r <= 1:
        return
    d.ellipse((x - r, y - r, x + r, y + r), outline=tuple(warna) + (int(255 * alpha),), width=tebal)


def denyut(d, x, y, t, alpha=1.0, warna=(200, 40, 30), skala=1.0):
    for i in range(3):
        f = (t * 0.8 + i / 3) % 1.0
        cincin(d, x, y, 14 + f * 110 * skala, warna, (1 - f) * 0.9 * alpha, 6)
    a = int(255 * alpha)
    d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=tuple(warna) + (a,), outline=(255, 255, 255, a), width=3)


def bendera_ri(d, x, y, s=1.0, alpha=1.0):
    """Bendera merah putih kecil (tengah di x, y)."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    w, h = 60 * s, 40 * s
    d.rectangle((x - w / 2 + 4, y - h / 2 + 5, x + w / 2 + 4, y + h / 2 + 5), fill=(0, 0, 0, int(90 * alpha)))
    d.rectangle((x - w / 2, y - h / 2, x + w / 2, y), fill=(206, 17, 38, a))
    d.rectangle((x - w / 2, y, x + w / 2, y + h / 2), fill=(250, 250, 250, a))
    d.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), outline=(40, 30, 20, a), width=max(1, int(2 * s)))


def bola_dunia(d, x, y, r, alpha=1.0, warna=BIRU_PBB, cabang=True):
    """Bola dunia bergaris lintang/bujur + dua ranting zaitun (lambang ala PBB, ilustrasi)."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    col = tuple(warna) + (a,)
    tebal = max(2, int(r / 28))
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(int(v * 0.3) for v in warna) + (a,), outline=col, width=tebal + 2)
    for f in (0.35, 0.7):
        d.ellipse((x - r * f, y - r, x + r * f, y + r), outline=col, width=tebal)
    d.line((x, y - r, x, y + r), fill=col, width=tebal)
    for f in (-0.55, 0, 0.55):
        yy = y + f * r
        half = r * math.sqrt(1 - f * f)
        d.line((x - half, yy, x + half, yy), fill=col, width=tebal)
    if cabang:
        for sisi in (-1, 1):
            for i in range(9):
                # daun di setengah bawah lingkaran besar
                rr = r * 1.22
                ang = math.radians(90 - sisi * (i * 13 + 18))
                lx = x + rr * math.cos(ang)
                ly = y + rr * math.sin(ang) * 0.95
                dw = r * 0.13
                d.ellipse((lx - dw, ly - dw * 0.5, lx + dw, ly + dw * 0.5), fill=col)


def kalender(img, cx, cy, atas, angka, bulan, bawah, alpha=1.0, skala=1.0, warna=BIRU):
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


def poligon_layar(img, kamera, poli, warna, alpha):
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    pts = se.halus([layar(kamera, ll) for ll in poli])
    dl.polygon(pts, fill=tuple(warna) + (int(110 * alpha),), outline=tuple(warna) + (int(255 * alpha),))
    dl.line(pts + [pts[0]], fill=tuple(warna) + (int(255 * alpha),), width=5)
    img.alpha_composite(lap)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img, d = _gradasi((22, 32, 60), (8, 12, 26))
    gx, gy, r = 540, 730, 230
    bola_dunia(d, gx, gy, r, alpha=c.p(0.0, 0.12))
    se.teks(d, (gx, gy + r + 95), "PBB", 64, (190, 215, 245), nama_font="judul", alpha=c.p(0.05, 0.15))
    # bendera RI keluar dari lingkaran
    k = c.p(0.3, 0.62)
    bx, by = lerp(gx, 900, k), lerp(gy, 560, k)
    if k > 0:
        se.garis_putus(d, [(gx, gy), (bx, by)], 1.0, (255, 210, 120), tebal=6, putus=14, celah=10)
    bendera_ri(d, bx, by, 1.6 + 0.4 * k, alpha=c.p(0.12, 0.2))
    se.teks(d, (540, 1150), "KELUAR?!", int(140 * muncul(c, 0.45)) + 1, (255, 205, 120), nama_font="caption", stroke=9,
            stroke_warna=(30, 15, 5), alpha=c.p(0.45, 0.5) * (1 - c.p(0.7, 0.75)))
    se.teks(d, (540, 1150), "INDONESIA", int(130 * muncul(c, 0.75)) + 1, (235, 60, 50), nama_font="caption", stroke=9,
            stroke_warna=(255, 255, 255), alpha=c.p(0.75, 0.8))
    se.teks(d, (540, 1270), "satu-satunya", 52, PUTIH, nama_font="caption", stroke=6, stroke_warna=(30, 15, 5),
            alpha=c.p(0.8, 0.88))
    hdr(img, alpha=c.p(0.85, 0.97))
    return img


def a_tren(c):
    kamera = se.kamera_antara(cam(-1.5, 108.0, 0.55), cam(-6.6, 106.9, 1.9), c.p(0.0, 0.4))
    img, d = peta(kamera)
    a = c.p(0.3, 0.42)
    x, y = layar(kamera, HAMBALANG)
    if a > 0:
        denyut(d, x, y, c.t, a)
        jx, jy = layar(kamera, JAKARTA)
        d.ellipse((jx - 8, jy - 8, jx + 8, jy + 8), fill=(40, 30, 20, int(255 * a)))
        label(d, (jx + 20, jy - 40), "Jakarta", 36, alpha=a)
        label(d, (x + 150, y + 30), "Hambalang", 40, MERAH, a)
    kartu(img, 540, 520, "Sekjen PBB Antonio Guterres", "berkunjung 17–19 Oktober 2026", BIRU_PBB,
          alpha=c.p(0.05, 0.13), tiang=False, skala=muncul(c, 0.05))
    kartu(img, 540, 1150, "bertemu Presiden Prabowo", "Hambalang, Bogor · 18 Oktober 2026", MERAH,
          alpha=c.p(0.35, 0.43), tiang=False, skala=muncul(c, 0.35))
    se.teks(d, (540, 1300), "dulu pernah putus?", 64, (255, 215, 140), nama_font="caption", stroke=7,
            stroke_warna=(30, 15, 5), alpha=c.p(0.72, 0.8))
    hdr(img, "Lagi rame: Sekjen PBB ke Indonesia")
    return img


def a_gabung(c):
    img, d = _gradasi((235, 222, 192), (205, 185, 145))
    kalender(img, 540, 650, "RESMI GABUNG", "28", "SEPTEMBER", "1950", alpha=c.p(0.0, 0.08), skala=0.85 * muncul(c, 0.0))
    d = ImageDraw.Draw(img, "RGBA")
    n = int(60 * c.p(0.25, 0.75))
    for i in range(60):
        baris, kol = divmod(i, 15)
        x, y = 120 + kol * 60, 1000 + baris * 62
        if i == 59:
            if n >= 60:
                bendera_ri(d, x, y, 0.85 + 0.25 * abs(math.sin(c.t * 4)))
            continue
        isi = (40, 80, 150, 255) if i < n else (190, 172, 135, 255)
        d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=isi, outline=(255, 255, 255, 255) if i < n else (170, 150, 115, 255), width=3)
    se.teks(d, (540, 1270), "Indonesia = anggota ke-60", 50, (150, 40, 30), nama_font="caption",
            alpha=c.p(0.78, 0.86))
    hdr(img, "Awalnya: masuk PBB")
    return img


def a_konfrontasi(c):
    kamera = Kamera(*cam(2.5, 109.0, 0.6))
    img, d = peta(kamera)
    kedip = 0.75 + 0.25 * math.sin(c.t * 4)
    for poli in (MALAYA, BORNEO_MY):
        poligon_layar(img, kamera, poli, (200, 52, 44), c.p(0.1, 0.25) * kedip)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.12, 0.22)
    label(d, layar(kamera, (4.6, 103.0)), "MALAYSIA", 38, (130, 20, 15), a, "caption")
    label(d, layar(kamera, (3.6, 115.0)), "MALAYSIA", 38, (130, 20, 15), a, "caption")
    label(d, layar(kamera, (-1.0, 102.3)), "SUMATRA", 36, TINTA, 0.85)
    label(d, layar(kamera, (-1.3, 113.6)), "KALIMANTAN", 36, TINTA, 0.85 * (1 - c.p(0.42, 0.46)))
    # panah konfrontasi
    for awal, akhir, mulai in (((-0.5, 104.5), (1.8, 103.4), 0.45), ((-0.3, 112.5), (1.9, 112.6), 0.5),
                               ((0.2, 115.5), (3.0, 115.8), 0.55)):
        k = c.p(mulai, mulai + 0.2)
        if k > 0:
            se.garis_putus(d, [layar(kamera, awal), layar(kamera, akhir)], k, (170, 25, 20), tebal=7)
    kartu(img, 540, 500, "Federasi Malaysia berdiri", "16 September 1963", (130, 20, 15), alpha=c.p(0.05, 0.13),
          tiang=False, skala=muncul(c, 0.05))
    kartu(img, 540, 1310, "KONFRONTASI", "Indonesia vs Malaysia · 1963–1966", MERAH, alpha=c.p(0.45, 0.53),
          tiang=False, skala=muncul(c, 0.45))
    hdr(img, "Tahun 1960-an")
    return img


def a_kursi(c):
    img, d = _gradasi((26, 40, 74), (10, 16, 34))
    cx, cy, R = 540, 1000, 330
    # meja tapal kuda
    a = c.p(0.0, 0.12)
    d.arc((cx - R, cy - R, cx + R, cy + R), 180, 360, fill=(150, 110, 70, int(255 * a)), width=60)
    d.line((cx - R + 30, cy, cx - R + 30, cy + 200), fill=(150, 110, 70, int(255 * a)), width=60)
    d.line((cx + R - 30, cy, cx + R - 30, cy + 200), fill=(150, 110, 70, int(255 * a)), width=60)
    se.teks(d, (540, 900), "DEWAN KEAMANAN PBB", 36, (190, 215, 245), nama_font="judul", alpha=a)
    kursi = []
    for i in range(7):
        ang = math.radians(180 + 15 + i * 25)
        kursi.append((cx + (R + 55) * math.cos(ang), cy + (R + 55) * math.sin(ang)))
    for yy in (cy + 60, cy + 170):
        kursi.insert(0, (cx - R - 25, yy))
        kursi.append((cx + R + 25, yy))
    MY = 6  # indeks kursi Malaysia
    for i, (x, y) in enumerate(kursi):
        k = c.p(0.04 + i * 0.015, 0.1 + i * 0.015)
        warna = (200, 52, 44) if (i == MY and c.p(0.25, 0.3) > 0.5) else (190, 200, 215)
        d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=tuple(warna) + (int(255 * k),), outline=(255, 255, 255, int(200 * k)), width=3)
    x, y = kursi[MY]
    if c.p(0.25, 0.3) > 0:
        denyut(d, x, y, c.t, c.p(0.25, 0.3))
        kartu(img, x, y - 30, "MALAYSIA", "mulai 1 Januari 1965", MERAH, alpha=c.p(0.25, 0.33), skala=muncul(c, 0.25))
    # Indonesia protes
    b = c.p(0.62, 0.7)
    bendera_ri(d, 540, 1060, 1.5, b)
    if b > 0:
        kartu(img, 540, 1250, "Indonesia protes keras", "", (130, 20, 15), alpha=b, tiang=False, skala=muncul(c, 0.62))
    hdr(img, "Januari 1965")
    return img


@lru_cache(maxsize=1)
def _koran():
    lap = Image.new("RGBA", (760, 560), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rectangle((14, 18, 754, 554), fill=(0, 0, 0, 100))
    d.rectangle((0, 0, 740, 540), fill=(238, 230, 210, 255), outline=(80, 70, 55, 255), width=4)
    d.text((370, 50), "KABAR HARIAN", font=se.font("judul", 44), fill=(40, 35, 30), anchor="mm")
    d.line((30, 85, 710, 85), fill=(40, 35, 30, 255), width=4)
    d.text((370, 108), "Januari 1965", font=se.font("ui", 24), fill=(90, 80, 70), anchor="mm")
    d.text((370, 180), "INDONESIA KELUAR", font=se.font("caption", 64), fill=(170, 25, 20), anchor="mm")
    d.text((370, 255), "DARI PBB", font=se.font("caption", 64), fill=(170, 25, 20), anchor="mm")
    for i in range(7):
        y = 320 + i * 30
        d.line((40, y, 345, y), fill=(120, 110, 95, 255), width=8)
        d.line((395, y, 700 - (i % 3) * 40, y), fill=(120, 110, 95, 255), width=8)
    return lap


def _amplop(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    w, h = 110 * s, 72 * s
    d.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=(250, 245, 230, a), outline=(60, 45, 30, a), width=3)
    d.line((x - w / 2, y - h / 2, x, y + 4 * s, x + w / 2, y - h / 2), fill=(60, 45, 30, a), width=3)
    d.ellipse((x - 10 * s, y - 6 * s, x + 10 * s, y + 14 * s), fill=(170, 25, 20, a))


def a_keluar(c):
    img, d = _gradasi((120, 95, 60), (45, 32, 20))
    k = muncul(c, 0.0)
    if k > 0:
        lap = _koran()
        sk = 0.4 + 0.6 * min(k, 1.1)
        lap2 = lap.rotate(-4 + 4 * min(k, 1), expand=True, resample=Image.BICUBIC)
        lap2 = lap2.resize((max(1, int(lap2.width * sk)), max(1, int(lap2.height * sk))), Image.BICUBIC)
        se.tempel(img, lap2, c.p(0.0, 0.06), (int(540 - lap2.width / 2), int(720 - lap2.height / 2)))
    d = ImageDraw.Draw(img, "RGBA")
    # surat resmi terbang ke markas PBB
    e = c.p(0.5, 0.85)
    if c.p(0.45, 0.5) > 0:
        bola_dunia(d, 880, 1110, 70, alpha=c.p(0.45, 0.52), cabang=False)
        se.teks(d, (880, 1215), "Markas PBB", 32, PUTIH, nama_font="tangan", alpha=c.p(0.45, 0.52))
        se.garis_putus(d, [(220, 1110), (790, 1110)], e, (255, 220, 150), tebal=5, panah=False)
        _amplop(d, lerp(220, 790, e), 1110 - math.sin(e * math.pi) * 60, 1.0, c.p(0.45, 0.5) * (1 - c.p(0.86, 0.92)))
    kartu(img, 540, 1270, "Surat resmi · 20 Januari 1965", "", (130, 20, 15), alpha=c.p(0.5, 0.58), tiang=False,
          skala=muncul(c, 0.5))
    hdr(img, "Januari 1965")
    return img


@lru_cache(maxsize=1)
def _grid_biru():
    img, d = _gradasi((22, 60, 110), (14, 38, 76))
    for x in range(0, W, 60):
        d.line((x, 0, x, H), fill=(120, 170, 230, 40), width=1)
    for y in range(0, H, 60):
        d.line((0, y, W, y), fill=(120, 170, 230, 40), width=1)
    return img


def _kubah(sisi, cx=540, dasar=1000, lebar=300, tinggi=210, celah=12, n=40):
    """Satu belahan kubah (kiri/kanan) sebagai poligon."""
    # urutan: dari tengah atas ke ujung luar, tutup di dasar
    pts = [(cx + sisi * celah, dasar - tinggi * 0.95)] + [
        (cx + sisi * (celah + lebar * math.sin(math.pi * f / 2)), dasar - tinggi * 0.95 * math.cos(math.pi * f / 2))
        for f in [i / n for i in range(1, n + 1)]]
    pts.append((cx + sisi * celah, dasar))
    return pts


def a_conefo(c):
    img = _grid_biru().copy()
    jadi = c.p(0.55, 0.7)
    if jadi > 0:
        langit, _ = _gradasi((150, 200, 235), (235, 225, 200))
        se.tempel(img, langit, jadi)
    d = ImageDraw.Draw(img, "RGBA")
    garis = se.lerp_rgb((235, 245, 255), (40, 40, 40), jadi)
    k = c.p(0.12, 0.5)
    # dasar gedung
    dasar = 1000
    if jadi > 0:
        d.rectangle((0, dasar + 80, W, H), fill=(110, 150, 80, int(255 * jadi)))
    a = int(255 * c.p(0.12, 0.18))
    d.rectangle((200, dasar, 880, dasar + 80), fill=(230, 225, 215, int(255 * jadi)), outline=garis + (a,), width=4)
    for x in range(230, 870, 44):
        d.line((x, dasar + 10, x, dasar + 72), fill=garis + (int(a * 0.8),), width=3)
    for sisi in (-1, 1):
        pts = _kubah(sisi)
        n = max(2, int(len(pts) * k))
        if jadi > 0:
            d.polygon(pts, fill=(45, 140, 95, int(255 * jadi)))
        d.line(pts[:n], fill=garis + (255,), width=6)
    se.teks(d, (540, 1150), "rencana gedung CONEFO · Senayan, 1965", 34, PUTIH, nama_font="tangan",
            alpha=c.p(0.15, 0.22) * (1 - jadi))
    kartu(img, 540, 520, "CONEFO", "tandingan PBB dari Soekarno", (130, 20, 15), alpha=c.p(0.03, 0.1) * (1 - c.p(0.5, 0.55)),
          tiang=False, skala=muncul(c, 0.03))
    kartu(img, 540, 520, "Sekarang: Gedung DPR/MPR", "Senayan, Jakarta", HIJAU, alpha=c.p(0.62, 0.7), tiang=False,
          skala=muncul(c, 0.62))
    se.teks(d, (540, 1250), "CONEFO nggak pernah terwujud", 46, (150, 30, 20), nama_font="caption",
            alpha=c.p(0.62, 0.7))
    hdr(img, "Rencana tandingan")
    return img


def _kursi_majelis():
    """Posisi kursi Majelis Umum (setengah lingkaran)."""
    cx, cy = 540, 1130
    pts = []
    for j, r in enumerate(range(190, 470, 62)):
        n = 7 + j * 3
        for i in range(n):
            ang = math.radians(180 + 8 + (164 * i / (n - 1)))
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


KURSI_MU = _kursi_majelis()
KURSI_RI = 3  # kursi Indonesia (baris depan)


def a_balik(c):
    img, d = _gradasi((30, 44, 80), (12, 18, 36))
    for i, (x, y) in enumerate(KURSI_MU):
        k = c.p(0.0, 0.12)
        if i == KURSI_RI:
            continue
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(120, 160, 210, int(230 * k)))
    x, y = KURSI_MU[KURSI_RI]
    b = c.p(0.35, 0.45)
    d.ellipse((x - 16, y - 16, x + 16, y + 16), outline=(150, 150, 160, int(255 * (1 - b))), width=3)
    if b > 0:
        se.glow(img, x, y, 70, (255, 220, 140), b)
        d = ImageDraw.Draw(img, "RGBA")
        bendera_ri(d, x, y, 0.9 * muncul(c, 0.35) + 0.01, b)
    se.teks(d, (540, 1190), "MAJELIS UMUM PBB", 40, (190, 215, 245), nama_font="judul", alpha=c.p(0.0, 0.1))
    kartu(img, 540, 500, "Telegram ke PBB", "19 September 1966 · siap kerja sama lagi", BIRU_PBB,
          alpha=c.p(0.03, 0.1) * (1 - c.p(0.68, 0.72)), tiang=False, skala=muncul(c, 0.03))
    kartu(img, 540, 500, "Pas 16 tahun setelah gabung", "28 September 1950 → 1966", HIJAU, alpha=c.p(0.74, 0.8),
          tiang=False, skala=muncul(c, 0.74))
    se.teks(d, (540, 1290), "28 SEPTEMBER 1966", 64, (255, 215, 140), nama_font="caption", stroke=7,
            stroke_warna=(30, 15, 5), alpha=c.p(0.38, 0.45))
    hdr(img, "Kembali ke PBB")
    return img


def a_unik(c):
    img, d = _gradasi((235, 222, 192), (205, 185, 145))
    kartu(img, 540, 500, "Keluar dari PBB", "", MERAH, alpha=c.p(0.0, 0.06), tiang=False, coret=c.p(0.1, 0.22),
          skala=muncul(c, 0.0))
    kartu(img, 540, 650, "cuma \"berhenti bekerja sama\"", "begitu catatan PBB", BIRU_PBB, alpha=c.p(0.22, 0.3),
          tiang=False, skala=muncul(c, 0.22))
    a = c.p(0.5, 0.58)
    bola_dunia(d, 540, 900, 110, alpha=a)
    bendera_ri(d, 540, 900, 1.3, a)
    kartu(img, 540, 1160, "Adam Malik", "Presiden Sidang Majelis Umum PBB · 1971", (130, 20, 15), alpha=c.p(0.6, 0.68),
          tiang=False, skala=muncul(c, 0.6))
    se.teks(d, (540, 1280), "orang Indonesia pertama", 44, (150, 40, 30), nama_font="caption", alpha=c.p(0.75, 0.83))
    hdr(img, "Uniknya…")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(0.5, 108.0, 0.6))
    img, d = peta(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1000), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Pernah keluar,", 50, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 635), "tapi balik lagi", 50, TINTA, nama_font="judul", alpha=a)
        bola_dunia(d, 540, 790, 85, alpha=a)
        bendera_ri(d, 540, 790, 1.1, a)
        se.teks(d, (540, 935), "dan malah makin aktif di PBB", 40, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Ada satu negara yang pernah bilang: kami keluar dari PBB! Dan satu-satunya negara "
                   "itu... Indonesia.", a_hook, transisi=False),
    Adegan("tren", "Lagi rame nih, Sekjen PBB, Antonio Guterres, datang ke Hambalang, ketemu Presiden Prabowo. "
                   "Tapi tahu nggak, hubungan kita sama PBB dulu pernah putus. Kok bisa?", a_tren),
    Adegan("gabung", "Awalnya, Indonesia resmi masuk PBB tanggal dua puluh delapan September, sembilan belas lima puluh. "
                     "Jadi anggota yang keenam puluh.", a_gabung),
    Adegan("konfrontasi", "Lalu tahun enam puluhan, Indonesia konfrontasi sama Malaysia, negara federasi yang baru "
                          "berdiri tahun sembilan belas enam puluh tiga. Soekarno menentangnya.",
           a_konfrontasi),
    Adegan("kursi", "Masalahnya, Malaysia malah dapat kursi di Dewan Keamanan PBB, mulai Januari sembilan belas enam "
                    "puluh lima. Indonesia protes keras.", a_kursi),
    Adegan("keluar", "Januari sembilan belas enam puluh lima, Soekarno mengumumkan Indonesia keluar dari PBB. "
                     "Surat resminya bertanggal dua puluh Januari, dikirim ke markas PBB.", a_keluar),
    Adegan("conefo", "Soekarno bahkan menggagas tandingannya, namanya CONEFO. Gedungnya mulai dibangun di Senayan. "
                     "CONEFO nggak pernah terwujud, tapi gedungnya sekarang kamu kenal, sebagai Gedung DPR MPR.",
           a_conefo),
    Adegan("balik", "Setelah pergantian kekuasaan, Indonesia kirim telegram ke PBB, siap kerja sama lagi. "
                    "Dua puluh delapan September sembilan belas enam puluh enam, delegasi kita duduk lagi di Majelis "
                    "Umum. Pas enam belas tahun setelah pertama gabung.", a_balik),
    Adegan("unik", "Uniknya, PBB nggak mencatatnya sebagai keluar beneran, cuma berhenti bekerja sama. Dan lima tahun "
                   "kemudian, diplomat kita, Adam Malik, malah terpilih memimpin Sidang Majelis Umum PBB.", a_unik),
    Adegan("penutup", "Jadi, Indonesia pernah keluar dari PBB, tapi balik lagi, dan malah makin aktif. "
                      "Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
