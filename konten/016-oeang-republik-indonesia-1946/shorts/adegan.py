"""Shorts ±90 detik: ORI, Uang Pertama Indonesia (30 Oktober 1946).

Uang kertas ilustratif (bukan replika desain asli), peta Jawa–Sumatra, radio malam 29 Oktober 1946.
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

NAMA_FILE = "oeang-republik-indonesia-1946-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "UANG PERTAMA RI"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
COKLAT_JEPANG = (150, 110, 70)
BIRU_DJB = (60, 95, 150)
MERAH_NICA = (190, 50, 45)
HIJAU_ORI = (60, 120, 85)
BIRU = (30, 80, 150)

print("  menyiapkan peta Jawa–Sumatra...")
PETA = Peta(93, 125, -22, 14, 110, [], [(-7.54, 110.45, 0.25), (-7.94, 112.95, 0.3), (-7.0, 107.6, 0.3),
                                       (0, 101, 1.0), (-2, 114, 1.2), (3.0, 98.5, 0.6)], seed=46, darat=pd.SEMUA)

JAKARTA = (-6.2, 106.8)
BANDUNG = (-6.9, 107.6)
CIREBON = (-6.71, 108.56)
PURWOKERTO = (-7.42, 109.23)
YOGYA = (-7.8, 110.37)
SOLO = (-7.57, 110.82)
SEMARANG = (-6.97, 110.42)
MADIUN = (-7.63, 111.52)
SURABAYA = (-7.25, 112.75)
MALANG = (-8.05, 112.63)
REL = [JAKARTA, CIREBON, PURWOKERTO, YOGYA, SOLO, MADIUN, SURABAYA, MALANG]
ORIDA = [("ORIBA", "Banda Aceh", (5.0, 96.4)), ("ORITA", "Tapanuli", (1.9, 99.2)),
         ("ORIPS", "Sumatra", (-1.2, 101.6)), ("ORIDABS", "Banten", (-6.4, 106.0))]


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


def hdr(img, sub="1945 – 1946", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def muncul(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


def titik(d, x, y, warna=MERAH, r=12, alpha=1.0):
    if alpha > 0.01:
        a = int(255 * alpha)
        d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=(255, 255, 255, a), width=3)


def uang(img, cx, cy, warna, atas, nilai, w=420, sudut=0.0, alpha=1.0, skala=1.0, stempel=None):
    """Uang kertas ilustratif (bukan replika desain asli)."""
    if alpha <= 0.01 or skala <= 0.01:
        return
    w = int(w * skala)
    if w < 40:  # terlalu kecil buat digambar (awal animasi muncul)
        return
    h = int(w * 0.5)
    lap = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    gelap = tuple(int(v * 0.55) for v in warna)
    terang = se.lerp_rgb(warna, (245, 235, 205), 0.55)
    d.rounded_rectangle((14, 16, w + 14, h + 16), 10, fill=(0, 0, 0, 90))
    d.rounded_rectangle((6, 6, w + 6, h + 6), 10, fill=terang + (255,), outline=gelap + (255,), width=max(2, w // 80))
    m = w * 0.05
    d.rounded_rectangle((6 + m, 6 + m, w + 6 - m, h + 6 - m), 6, outline=tuple(warna) + (255,), width=max(2, w // 60))
    # ornamen bulat di kiri, angka besar di kanan
    r = h * 0.28
    ox, oy = 6 + w * 0.26, 6 + h * 0.56
    d.ellipse((ox - r, oy - r, ox + r, oy + r), fill=tuple(warna) + (110,), outline=gelap + (255,), width=max(2, w // 120))
    for k in range(8):
        a = k * math.pi / 4
        d.line((ox, oy, ox + math.cos(a) * r, oy + math.sin(a) * r), fill=gelap + (160,), width=max(1, w // 200))
    d.text((6 + w / 2, 6 + h * 0.2), atas, font=se.font("judul", max(8, int(w * 0.052))), fill=gelap + (255,), anchor="mm")
    d.text((6 + w * 0.7, 6 + h * 0.6), nilai, font=se.font("judul", max(8, int(w * 0.13))), fill=gelap + (255,), anchor="mm")
    if stempel:
        k, sd = stempel
        fs = se.font("caption", max(8, int(w * 0.075)))
        tw = fs.getlength(k) + w * 0.06
        st = Image.new("RGBA", (int(tw), int(w * 0.13)), (0, 0, 0, 0))
        ds = ImageDraw.Draw(st)
        ds.rectangle((0, 0, st.width - 1, st.height - 1), outline=(200, 25, 25, 230), width=max(2, w // 90))
        ds.text((st.width / 2, st.height / 2), k, font=fs, fill=(200, 25, 25, 230), anchor="mm")
        st = st.rotate(sd, expand=True, resample=Image.BICUBIC)
        lap.alpha_composite(st, (int(6 + w / 2 - st.width / 2), int(6 + h / 2 - st.height / 2)))
    if sudut:
        lap = lap.rotate(sudut, expand=True, resample=Image.BICUBIC)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def latar_gelap(warna=(45, 30, 22)):
    img = Image.new("RGBA", (W, H), tuple(warna) + (255,))
    se.vignette(img)
    return img


HUJAN_UANG = [(random.Random(i).uniform(0, W), random.Random(i + 99).uniform(0, 1), random.Random(i + 7).uniform(-35, 35),
               random.Random(i + 3).uniform(0.45, 0.75)) for i in range(14)]


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = latar_gelap((60, 22, 18))
    for i, (x, f, sd, s) in enumerate(HUJAN_UANG):
        y = ((f + c.t * 0.12 * (0.7 + s)) % 1.2) * (H + 200) - 260
        uang(img, x, y, COKLAT_JEPANG, "UANG JEPANG", "10", 300, sd + math.sin(c.t * 2 + i) * 8, 0.85, s)
    se.tint(img, (40, 10, 5), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    # frame pertama sudah penuh: pop kecil dari 1,15 ke 1
    s = 1 + 0.15 * (1 - clamp(c.t / 0.3))
    se.teks(d, (540, 600), "MERDEKA,", int(140 * s), PUTIH, nama_font="caption", stroke=10, stroke_warna=(40, 10, 5))
    se.teks(d, (540, 760), "UANGNYA JEPANG?", int(92 * s), (255, 205, 120), nama_font="caption", stroke=10,
            stroke_warna=(40, 10, 5))
    uang(img, 540, 1000, COKLAT_JEPANG, "UANG JEPANG", "100", 520, -4 + math.sin(c.t * 1.5) * 2, 1.0, 1.0,
         stempel=("MASIH BERLAKU", 12))
    se.kartu(img, 540, 1230, "Hari Oeang ke-80", "30 Oktober 1946 – 2026", MERAH, alpha=c.p(0.38, 0.46), tiang=False,
             skala=muncul(c, 0.38))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 1330), "…dan kenapa kita bilang \"lima ribu PERAK\"?", 40, (255, 235, 190), nama_font="caption",
            stroke=6, stroke_warna=(30, 10, 5), alpha=c.p(0.7, 0.8))
    hdr(img, "30 Oktober 1946", alpha=c.p(0.85, 0.97))
    return img


def a_kacau(c):
    kamera = Kamera(*cam(-7.4, 110.0, 0.85))
    img, d = peta(kamera)
    se.tint(img, (30, 20, 10), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, layar(kamera, (-7.25, 109.6)), "JAWA", 44, TINTA, 0.6)
    tumpuk = [(COKLAT_JEPANG, "UANG JEPANG", "1", 0.04, (330, 640, -8)),
              (BIRU_DJB, "DE JAVASCHE BANK", "5", 0.22, (750, 700, 7))]
    for warna, atas, nilai, mulai, (x, y, sd) in tumpuk:
        uang(img, x, y, warna, atas, nilai, 400, sd, c.p(mulai, mulai + 0.08), muncul(c, mulai))
    se.kartu(img, 540, 920, "Habis proklamasi 1945", "rakyat masih belanja pakai uang lama", (90, 70, 50),
             alpha=c.p(0.05, 0.13), tiang=False)
    a = c.p(0.55, 0.62)
    if a > 0:
        for i, (warna, nama) in enumerate([(COKLAT_JEPANG, "JEPANG I"), (COKLAT_JEPANG, "JEPANG II"),
                                          (COKLAT_JEPANG, "DAI NIPPON"), (BIRU_DJB, "JAVASCHE BANK")]):
            k = c.p(0.55 + i * 0.05, 0.62 + i * 0.05)
            uang(img, 180 + i * 240, 1130 + (i % 2) * 40, warna, nama, "?", 250, (-1) ** i * 6, k, back_out(k))
        se.teks(ImageDraw.Draw(img, "RGBA"), (540, 1300), "4 JENIS UANG SAH SEKALIGUS", 54, PUTIH, nama_font="caption",
                stroke=7, stroke_warna=(0, 0, 0), alpha=c.p(0.75, 0.82))
    hdr(img, "Oktober 1945")
    return img


def a_nica(c):
    kamera = se.kamera_antara(cam(-7.0, 108.8, 0.85), cam(-6.6, 107.4, 1.3), c.p(0.0, 0.5))
    img, d = peta(kamera)
    jx, jy = layar(kamera, JAKARTA)
    k = c.p(0.25, 0.75)
    if k > 0:
        lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        r = 60 + 230 * k
        dl.ellipse((jx - r, jy - r * 0.6, jx + r, jy + r * 0.6), fill=MERAH_NICA + (90,), outline=MERAH_NICA + (220,), width=5)
        img.alpha_composite(lap)
        d = ImageDraw.Draw(img, "RGBA")
    titik(d, jx, jy, MERAH_NICA, 14)
    label(d, (jx, jy - 50), "Batavia", 42, TINTA)
    for i in range(5):
        kk = c.p(0.3 + i * 0.06, 0.4 + i * 0.06)
        a = i * 1.26 + 0.4
        uang(img, jx + math.cos(a) * 190 * kk, jy + 60 + math.sin(a) * 120 * kk, MERAH_NICA, "NICA", "1", 200,
             i * 13 - 20, kk, kk)
    se.kartu(img, 540, 560, "Belanda datang lagi", "membonceng Sekutu", MERAH_NICA, alpha=c.p(0.03, 0.11), tiang=False,
             skala=muncul(c, 0.03))
    se.kartu(img, 540, 1180, "\"Uang Merah\" NICA", "sah di daerah pendudukan · Maret 1946", MERAH_NICA,
             alpha=c.p(0.45, 0.53), tiang=False, skala=muncul(c, 0.45))
    se.teks(d, (540, 1310), "UANG JADI SENJATA", 60, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=c.p(0.82, 0.9))
    hdr(img, "1945 – 1946")
    return img


def mesin_cetak(d, x, y, t, s=1.0, a=255):
    d.rectangle((x - 110 * s, y - 40 * s, x + 110 * s, y + 70 * s), fill=(70, 70, 78, a), outline=(25, 25, 30, a), width=4)
    for i, ox in enumerate((-60, 60)):
        cx, cy = x + ox * s, y - 70 * s
        r = 42 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(110, 110, 120, a), outline=(25, 25, 30, a), width=4)
        sd = t * 6 * (1 if i == 0 else -1)
        d.line((cx, cy, cx + math.cos(sd) * r, cy + math.sin(sd) * r), fill=(25, 25, 30, a), width=5)
    d.rectangle((x - 130 * s, y + 70 * s, x + 130 * s, y + 90 * s), fill=(45, 40, 38, a))


def a_cetak(c):
    kamera = Kamera(*cam(-7.4, 110.3, 0.85))
    img, d = peta(kamera)
    jx, jy = layar(kamera, JAKARTA)
    titik(d, jx, jy, (120, 120, 120), 12)
    label(d, (jx + 10, jy - 46), "Jakarta", 38, TINTA)
    x = c.p(0.12, 0.22)
    if x > 0:
        d.line((jx - 30, jy - 30, jx - 30 + 60 * x, jy - 30 + 60 * x), fill=(200, 20, 20, 255), width=10)
        d.line((jx + 30, jy - 30, jx + 30 - 60 * x, jy - 30 + 60 * x), fill=(200, 20, 20, 255), width=10)
        se.teks(d, (jx + 40, jy + 70), "nggak aman", 36, (170, 20, 20), nama_font="caption", stroke=5,
                stroke_warna=KREM_LABEL, alpha=x)
    for i, (nama, ll, dx, dy) in enumerate([("Kendalpayak, Malang", MALANG, -10, 62), ("Yogyakarta", YOGYA, -120, 50),
                                            ("Solo", SOLO, 30, -45)]):
        a = c.p(0.35 + i * 0.15, 0.42 + i * 0.15)
        x, y = layar(kamera, ll)
        titik(d, x, y, HIJAU_ORI, 14, a)
        label(d, (x + dx, y + dy), nama, 38, TINTA, a)
    mx, my = layar(kamera, MALANG)
    mesin_cetak(d, 540, 650, c.t, 1.3, int(255 * c.p(0.3, 0.38)))
    if c.p(0.4, 0.45) > 0:
        for i in range(3):
            f = (c.t * 0.6 + i / 3) % 1
            uang(img, lerp(540, 540 + 260, f), 760 + f * 40, HIJAU_ORI, "OEANG REPOEBLIK", "1", 220, -10 + 20 * f,
                 c.p(0.4, 0.45) * (1 - f * 0.5))
    se.kartu(img, 540, 1230, "Republik cetak uang sendiri", "pindah-pindah demi keamanan", HIJAU_ORI,
             alpha=c.p(0.02, 0.1), tiang=False)
    hdr(img, "1945 – 1946")
    return img


def a_teken(c):
    img = latar_gelap((40, 50, 42))
    z = 1 + 0.06 * c.p(0, 1)
    uang(img, 540, 760, HIJAU_ORI, "OEANG REPOEBLIK INDONESIA", "100", int(900 * z), -2, 1.0)
    d = ImageDraw.Draw(img, "RGBA")
    # tanda tangan (coretan ilustratif) di pojok kanan bawah uang
    k = c.p(0.12, 0.3)
    if k > 0:
        x0, y0 = 650, 900
        pts = [(x0 + i * 6, y0 + math.sin(i * 0.9) * 18 - i * 0.6) for i in range(int(40 * k) + 1)]
        if len(pts) > 1:
            d.line(pts, fill=(20, 30, 70, 255), width=5, joint="curve")
    se.kartu(img, 760, 1010, "A. A. Maramis", "Menteri Keuangan", BIRU, alpha=c.p(0.15, 0.23), tiang=False,
             skala=muncul(c, 0.15), coret=0)
    se.kartu(img, 540, 520, "Padahal sudah bukan menteri", "sejak November 1945", MERAH, alpha=c.p(0.35, 0.43),
             tiang=False, skala=muncul(c, 0.35))
    a = c.p(0.62, 0.7)
    if a > 0:
        d.rounded_rectangle((180, 590, 470, 650), 10, outline=(220, 30, 30, int(255 * a)), width=6)
        se.kartu(img, 540, 1160, "Tertulis: 17 Oktober 1945", "baru beredar setahun kemudian", (90, 70, 50), alpha=a,
                 tiang=False, skala=muncul(c, 0.62))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 1310), "ADA YANG ANEH…", 64, (255, 215, 120), nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=c.p(0.0, 0.06) * (1 - c.p(0.3, 0.36)))
    hdr(img, "Uang pertama kita")
    return img


def kereta(d, x, y, s=1.0, a=255, gerbong=2):
    for g in range(gerbong):
        gx = x - (g + 1) * 70 * s
        d.rectangle((gx - 30 * s, y - 22 * s, gx + 30 * s, y + 14 * s), fill=(120, 85, 50, a), outline=(40, 25, 15, a), width=3)
        d.ellipse((gx - 14 * s, y - 32 * s, gx + 14 * s, y - 14 * s), fill=(190, 160, 110, a))  # karung goni
    d.rectangle((x - 30 * s, y - 30 * s, x + 34 * s, y + 14 * s), fill=(40, 40, 45, a), outline=(10, 10, 10, a), width=3)
    d.rectangle((x + 10 * s, y - 48 * s, x + 22 * s, y - 30 * s), fill=(40, 40, 45, a))
    for ox in (-18, 4, 24):
        d.ellipse((x + (ox - 7) * s, y + 8 * s, x + (ox + 7) * s, y + 22 * s), fill=(20, 20, 20, a))


def besek(d, x, y, s=1.0, a=255):
    d.polygon([(x - 60 * s, y - 30 * s), (x + 60 * s, y - 30 * s), (x + 50 * s, y + 30 * s), (x - 50 * s, y + 30 * s)],
              fill=(200, 165, 100, a), outline=(110, 80, 40, a))
    for i in range(-5, 6):
        d.line((x + i * 10 * s, y - 30 * s, x + i * 9 * s, y + 30 * s), fill=(150, 115, 60, a), width=2)
    for j in range(-2, 3):
        d.line((x - 55 * s, y + j * 12 * s, x + 55 * s, y + j * 12 * s), fill=(150, 115, 60, a), width=2)


def a_kirim(c):
    kamera = Kamera(*cam(-7.4, 110.0, 0.85))
    img, d = peta(kamera)
    pts = [layar(kamera, ll) for ll in REL]
    k = c.p(0.3, 0.95)
    se.garis_putus(d, pts, k, (60, 40, 25), tebal=6, putus=14, celah=8, panah=False)
    for ll in REL:
        x, y = layar(kamera, ll)
        titik(d, x, y, HIJAU_ORI, 9, c.p(0.3, 0.4))
    if k > 0:
        (x, y), _ = se.titik_di_jalur(pts, k)
        kereta(d, x, y - 26, 1.0)
    a = c.p(0.0, 0.08) * (1 - c.p(0.3, 0.36))
    if a > 0:
        uang(img, 540, 700, HIJAU_ORI, "OEANG REPOEBLIK", "5", 380, -6, a)
    b = c.p(0.1, 0.18) * (1 - c.p(0.3, 0.36))
    besek(d, 540, 900, 2.2, int(255 * b))
    se.kartu(img, 540, 560, "Dibungkus besek & karung goni", "lalu naik kereta api", (110, 80, 40),
             alpha=c.p(0.05, 0.13), tiang=False)
    se.teks(d, (540, 1270), "KE SELURUH JAWA", 64, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=c.p(0.6, 0.7))
    hdr(img, "1946")
    return img


def radio(d, x, y, s=1.0, a=255):
    d.rounded_rectangle((x - 170 * s, y - 120 * s, x + 170 * s, y + 120 * s), 40 * s, fill=(120, 75, 40, a),
                        outline=(50, 30, 15, a), width=6)
    d.pieslice((x - 150 * s, y - 100 * s, x + 30 * s, y + 80 * s), 180, 360, fill=(200, 175, 120, a))
    d.rectangle((x - 150 * s, y - 10 * s, x + 30 * s, y + 80 * s), fill=(200, 175, 120, a))
    for i in range(6):
        yy = y - 50 * s + i * 22 * s
        d.line((x - 135 * s, yy, x + 15 * s, yy), fill=(120, 90, 50, a), width=4)
    for ox in (95,):
        for oy in (-40, 40):
            d.ellipse((x + (ox - 26) * s, y + (oy - 26) * s, x + (ox + 26) * s, y + (oy + 26) * s), fill=(60, 35, 20, a))


def jam(d, x, y, r, menit, a=255):
    d.ellipse((x - r, y - r, x + r, y + r), fill=(245, 238, 215, a), outline=(40, 30, 20, a), width=6)
    for i in range(12):
        sd = i * math.pi / 6
        d.line((x + math.cos(sd) * r * 0.82, y + math.sin(sd) * r * 0.82, x + math.cos(sd) * r * 0.95,
                y + math.sin(sd) * r * 0.95), fill=(40, 30, 20, a), width=4)
    sm = menit / 60 * 2 * math.pi - math.pi / 2
    sj = (11 + menit / 60) / 12 * 2 * math.pi - math.pi / 2
    d.line((x, y, x + math.cos(sj) * r * 0.5, y + math.sin(sj) * r * 0.5), fill=(40, 30, 20, a), width=8)
    d.line((x, y, x + math.cos(sm) * r * 0.8, y + math.sin(sm) * r * 0.8), fill=(200, 40, 30, a), width=5)


def a_hatta(c):
    img = latar_gelap((18, 22, 45))
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(4)
    for i in range(60):
        x, y = rng.uniform(0, W), rng.uniform(380, 1300)
        r = 2 + (math.sin(c.t * 3 + i) + 1)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 230, 160))
    radio(d, 540, 700, 1.3)
    for i in range(3):
        f = (c.t * 0.7 + i / 3) % 1
        r = 230 + f * 260
        d.arc((540 - r, 700 - r, 540 + r, 700 + r), 290, 340, fill=(255, 220, 140, int(200 * (1 - f))), width=6)
        d.arc((540 - r, 700 - r, 540 + r, 700 + r), 200, 250, fill=(255, 220, 140, int(200 * (1 - f))), width=6)
    se.kartu(img, 540, 470, "29 Oktober 1946, malam", "Wapres Mohammad Hatta · radio, Yogyakarta", BIRU,
             alpha=c.p(0.02, 0.1), tiang=False)
    a = c.p(0.28, 0.36) * (1 - c.p(0.6, 0.66))
    if a > 0:
        jam(d, 540, 1060, 110, 60 * c.p(0.28, 0.55), int(255 * a))
        uang(img, 260, 1060, COKLAT_JEPANG, "UANG JEPANG", "10", 240, -8, a, stempel=("TIDAK LAKU", 10) if c.p(0.5, 0.52) else None)
        uang(img, 820, 1060, BIRU_DJB, "JAVASCHE BANK", "5", 240, 8, a, stempel=("TIDAK LAKU", -10) if c.p(0.5, 0.52) else None)
    b = c.p(0.64, 0.72)
    if b > 0:
        se.panel(img, (90, 960, 990, 1280), alpha=b)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1050), "\"Uang sendiri itu adalah", 52, TINTA, nama_font="judul", alpha=b)
        se.teks(d, (540, 1125), "tanda kemerdekaan negara.\"", 52, TINTA, nama_font="judul", alpha=b)
        se.teks(d, (540, 1210), "— Mohammad Hatta", 34, (110, 80, 50), alpha=b)
    hdr(img, "Malam sebelum ORI beredar")
    return img


def a_kurs(c):
    img = latar_gelap((40, 34, 28))
    se.panel(img, (70, 420, 1010, 1290), alpha=c.p(0, 0.06))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 500), "JAWA & MADURA", 50, (110, 40, 20), nama_font="judul", alpha=c.p(0.02, 0.1))
    k = c.p(0.1, 0.45)
    n = 12
    for i in range(n):
        x = 290 + (i % 4) * 16 - 24 + lerp(0, 250 - (290 + (i % 4) * 16 - 24), clamp(k * 1.4 - 0.4))
        y = 640 + (i // 4) * 90 + lerp(0, 700 - (640 + (i // 4) * 90), clamp(k * 1.4 - 0.4))
        uang(img, x, y, COKLAT_JEPANG, "UANG JEPANG", "", 260, (i % 5 - 2) * 4, 1 - clamp(k * 1.4 - 0.4) * 0.9)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (250, 900), "50 rupiah Jepang", 38, TINTA, nama_font="tangan", alpha=c.p(0.05, 0.12))
    se.teks(d, (540, 720), "=", 110, TINTA, nama_font="caption", alpha=c.p(0.3, 0.38))
    uang(img, 790, 720, HIJAU_ORI, "OEANG REPOEBLIK", "1", 330, 4, c.p(0.35, 0.43), muncul(c, 0.35))
    se.teks(d, (790, 900), "1 rupiah ORI", 38, TINTA, nama_font="tangan", alpha=c.p(0.35, 0.43))
    se.teks(d, (540, 1040), "50 : 1", 130, MERAH, nama_font="caption", stroke=6, stroke_warna=PUTIH, alpha=c.p(0.42, 0.5))
    se.kartu(img, 540, 1200, "Luar Jawa: 100 : 1", "UU No. 19 Tahun 1946", (90, 70, 50), alpha=c.p(0.7, 0.78),
             tiang=False, skala=muncul(c, 0.7))
    hdr(img, "30 Oktober 1946")
    return img


def api(d, x, y, t, s=1.0, alpha=1.0, seed=0):
    if alpha <= 0.01:
        return
    s = s * (1 + 0.15 * math.sin(t * 11 + seed * 1.7))
    a = int(255 * alpha)
    d.polygon([(x, y - 34 * s), (x + 14 * s, y - 12 * s), (x + 16 * s, y + 6 * s), (x + 8 * s, y + 16 * s),
               (x - 8 * s, y + 16 * s), (x - 16 * s, y + 6 * s), (x - 12 * s, y - 14 * s), (x - 4 * s, y - 6 * s)],
              fill=(225, 60, 25, a), outline=(80, 20, 10, a))
    d.polygon([(x + 1 * s, y - 16 * s), (x + 8 * s, y + 2 * s), (x + 5 * s, y + 12 * s), (x - 5 * s, y + 12 * s),
               (x - 8 * s, y + 2 * s)], fill=(255, 205, 60, a))


def a_orida(c):
    kamera = se.kamera_antara(cam(-7.6, 112.0, 1.1), cam(-1.5, 102.5, 0.58), c.p(0.4, 0.6))
    img, d = peta(kamera)
    a1 = 1 - c.p(0.38, 0.45)
    x, y = layar(kamera, MALANG)
    if a1 > 0:
        api(d, x, y - 10, c.t, 2.5, a1 * c.p(0.08, 0.15))
        label(d, (x - 40, y + 70), "Malang", 42, TINTA, a1)
        se.kartu(img, 540, 620, "Agresi Militer Belanda I", "21 Juli 1947", MERAH, alpha=c.p(0.02, 0.1) * a1, tiang=False,
                 skala=muncul(c, 0.02))
        se.kartu(img, 540, 1180, "Pabrik uang dibumihanguskan", "uangnya diungsikan ke Yogyakarta", MERAH,
                 alpha=c.p(0.15, 0.23) * a1, tiang=False)
    for i, (nama, daerah, ll) in enumerate(ORIDA):
        a = c.p(0.6 + i * 0.07, 0.66 + i * 0.07)
        x, y = layar(kamera, ll)
        uang(img, x, y, (120 + i * 25, 90, 60 + i * 20), nama, "", 190, (-1) ** i * 6, a, muncul(c, 0.6 + i * 0.07))
        label(d, (x, y + 75), daerah, 32, TINTA, a)
    se.kartu(img, 540, 480, "ORIDA: uang republik versi daerah", "daerah yang terputus dari pusat", HIJAU_ORI,
             alpha=c.p(0.6, 0.68), tiang=False, skala=muncul(c, 0.6))
    hdr(img, "1947 – 1949")
    return img


def koin(d, x, y, r, t, a=255):
    lebar = abs(math.cos(t * 1.6)) * 0.85 + 0.15
    d.ellipse((x - r * lebar - 6, y - r - 6, x + r * lebar + 6, y + r + 6), fill=(90, 90, 100, a))
    d.ellipse((x - r * lebar, y - r, x + r * lebar, y + r), fill=(205, 208, 215, a), outline=(120, 122, 130, a), width=6)
    d.ellipse((x - r * 0.75 * lebar, y - r * 0.75, x + r * 0.75 * lebar, y + r * 0.75), outline=(150, 152, 160, a), width=4)
    if lebar > 0.6:
        se.teks(d, (x, y), "RUPYA", int(r * 0.5 * lebar), (110, 110, 120), nama_font="ui", alpha=a / 255)


def a_perak(c):
    img = latar_gelap((32, 34, 44))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 470), "KENAPA \"LIMA RIBU PERAK\"?", 62, PUTIH, nama_font="caption", stroke=7,
            stroke_warna=(0, 0, 0), alpha=c.p(0.0, 0.05))
    se.glow(img, 540, 760, 260, (220, 225, 240), 0.6 * c.p(0.15, 0.3))
    d = ImageDraw.Draw(img, "RGBA")
    koin(d, 540, 760, 190, c.t, int(255 * c.p(0.15, 0.22)))
    se.kartu(img, 540, 1030, "rupiah ← rupya (Sanskerta)", "artinya: PERAK", (120, 122, 135), alpha=c.p(0.3, 0.38),
             tiang=False, skala=muncul(c, 0.3))
    s = muncul(c, 0.65, 0.12)
    se.teks(d, (540, 1210), "RUPIAH = PERAK", int(96 * clamp(s, 0, 1.3)) + 1, (230, 232, 245), nama_font="caption",
            stroke=8, stroke_warna=(30, 30, 40), alpha=c.p(0.65, 0.7))
    hdr(img, "Asal-usul kata")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(-7.4, 110.0, 0.85))
    img, d = peta(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1000), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 560), "Uang di dompetmu", 52, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 635), "itu tanda merdeka juga", 40, (90, 70, 50), alpha=a)
        uang(img, 540, 800, HIJAU_ORI, "OEANG REPOEBLIK INDONESIA", "1", 460, -3, a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 950), "Selamat Hari Oeang ke-80!", 42, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Indonesia sudah merdeka, tapi uangnya masih uang Jepang. Selamat Hari Oeang ke delapan puluh! "
                   "Di akhir, kamu bakal tahu kenapa kita bilang lima ribu perak.", a_hook, transisi=False),
    Adegan("kacau", "Habis proklamasi, rakyat masih pakai uang Jepang, dan uang De Javasche Bank. "
                    "Pemerintah bahkan sempat mengakui empat jenis uang sekaligus.", a_kacau),
    Adegan("nica", "Lalu Belanda datang lagi, dan mengedarkan uang NICA, si uang merah. "
                   "Uang jadi senjata perang.", a_nica),
    Adegan("cetak", "Republik butuh uang sendiri. Tapi Jakarta nggak aman, jadi dicetak di Kendalpayak, Malang, "
                    "juga di Yogyakarta dan Solo.", a_cetak),
    Adegan("teken", "Nah, ada yang aneh. Uang itu diteken A. A. Maramis, padahal dia sudah bukan menteri keuangan sejak "
                    "November empat lima. Dan tanggal di uangnya, tujuh belas Oktober empat lima. Setahun sebelum beredar.", a_teken),
    Adegan("kirim", "Uangnya dibungkus besek, masuk karung goni, lalu naik kereta api ke seluruh Jawa.", a_kirim),
    Adegan("hatta", "Dua puluh sembilan Oktober empat enam, malam, Bung Hatta bicara lewat radio. Mulai tengah malam, "
                    "uang Jepang dan Javasche Bank nggak laku lagi. Kata beliau, uang sendiri itu adalah tanda "
                    "kemerdekaan negara.", a_hatta),
    Adegan("kurs", "Di Jawa dan Madura, lima puluh rupiah Jepang, cuma jadi satu rupiah ORI. Luar Jawa, seratus "
                   "banding satu.", a_kurs),
    Adegan("orida", "Tahun empat tujuh, Belanda menyerang. Pabrik di Malang dibumihanguskan. Daerah yang terputus "
                    "sampai bikin uang sendiri, namanya ORIDA.", a_orida),
    Adegan("perak", "Terus, kenapa lima ribu perak? Nama rupiah ternyata dari bahasa Sanskerta, rupya. "
                    "Artinya, perak. Jadi bilang lima ribu perak, nggak salah-salah amat.", a_perak),
    Adegan("penutup", "Jadi, uang di dompetmu itu, tanda merdeka juga. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
