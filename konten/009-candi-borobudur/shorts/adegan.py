"""Shorts ±90 detik: Candi Borobudur, yang pernah "hilang" berabad-abad.

Peta Jawa (lokasi, Merapi, pindahnya pusat kerajaan) + ilustrasi candi tampak samping
(dibangun bertahap, tertimbun abu & hutan, digali lagi, dipugar).
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import EMAS, HIJAU_TUA, MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "candi-borobudur-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "CANDI BOROBUDUR"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BATU = (128, 122, 112)
BATU_GELAP = (62, 58, 54)
ABU = (150, 148, 145)
BIRU = (40, 90, 150)

# ------------------------------------------------------------------ peta Jawa

print("  menyiapkan peta Jawa...")
GUNUNG = [(-7.54, 110.45, 0.12), (-7.45, 110.43, 0.12), (-7.38, 110.07, 0.11), (-7.3, 109.99, 0.11),
          (-7.63, 111.19, 0.14), (-7.94, 112.95, 0.15), (-7.2, 109.9, 0.1), (-7.92, 112.45, 0.12),
          (-7.81, 112.31, 0.1), (-8.1, 113.5, 0.12), (-7.0, 107.6, 0.15), (-6.8, 106.9, 0.12)]
PETA = Peta(104.5, 116.5, -10.5, -3.5, 300, [], GUNUNG, seed=33, darat=pd.SEMUA)

BOROBUDUR = (-7.608, 110.204)
MERAPI = (-7.54, 110.45)
JATIM = (-7.55, 112.25)      # perkiraan wilayah pusat kerajaan baru (Jawa Timur)
SEMARANG = (-6.97, 110.42)
LABEL_PETA = {"JAWA TENGAH": (-7.25, 109.6), "JAWA TIMUR": (-7.45, 112.4), "Laut Jawa": (-5.6, 110.4)}


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


def hdr(img, sub="Magelang, Jawa Tengah", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def titik(d, x, y, warna=MERAH, r=12, alpha=1.0):
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=(255, 255, 255, a), width=4)


def asap(img, x, y, t, kuat=1.0, tinggi=500, lebar=1.0, seed=1, warna=(95, 90, 86)):
    """Kolom asap/abu yang naik dari (x, y)."""
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    for i in range(40):
        fase = (rng.random() + t * rng.uniform(0.15, 0.3)) % 1.0
        yy = y - fase * tinggi
        xx = x + math.sin(fase * 6 + i) * 25 * lebar + rng.uniform(-40, 40) * lebar * fase
        r = (24 + fase * 110) * lebar * rng.uniform(0.7, 1.2)
        a = int(190 * kuat * (1 - fase * 0.7))
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=tuple(warna) + (a,))
    img.alpha_composite(lap)


# ------------------------------------------------------------------ lanskap & candi (ilustrasi)

HORISON = 1180


def _lanskap():
    """Langit senja + siluet gunung + tanah bertekstur. Dihitung sekali."""
    tanah = se.latar_tekstur(W, H, 9, warna=(150, 160, 95))
    img = tanah.convert("RGBA")
    atas = np.array((60, 80, 120), np.float32)
    bawah = np.array((235, 190, 140), np.float32)
    g = np.linspace(0, 1, HORISON, dtype=np.float32)[:, None, None]
    langit = (atas * (1 - g) + bawah * g).repeat(W, axis=1)
    img.paste(Image.fromarray(langit.astype(np.uint8), "RGB").convert("RGBA"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # Merapi & Merbabu di kejauhan
    d.polygon([(-100, HORISON), (180, 820), (260, 800), (520, HORISON)], fill=(95, 100, 125, 255))
    d.polygon([(560, HORISON), (860, 860), (930, 850), (1200, HORISON)], fill=(110, 115, 135, 255))
    d.rectangle((0, HORISON - 4, W, HORISON + 4), fill=(80, 95, 60, 255))
    return img


LANSKAP = _lanskap()

# 6 teras persegi (kaki + 5 lorong) lalu 3 teras bundar: (lebar relatif, tinggi px)
TERAS = [(1.0, 46), (0.9, 44), (0.81, 42), (0.72, 40), (0.63, 38), (0.55, 36),
         (0.45, 22), (0.37, 22), (0.29, 22)]
STUPA_KECIL = [9, 7, 5]  # yang kelihatan dari samping per teras bundar


def stupa(d, x, y, r, warna=BATU, alpha=1.0, garis=BATU_GELAP):
    """Stupa lonceng kecil; (x, y) = alas."""
    if alpha <= 0.01 or r < 2:
        return
    a = int(255 * alpha)
    d.rectangle((x - r * 1.05, y - r * 0.25, x + r * 1.05, y), fill=tuple(warna) + (a,), outline=garis + (a,), width=2)
    d.chord((x - r, y - r * 1.9, x + r, y - r * 0.1), 180, 360, fill=tuple(warna) + (a,), outline=garis + (a,), width=2)
    d.rectangle((x - r * 0.95, y - r * 1.0, x + r * 0.95, y - r * 0.25), fill=tuple(warna) + (a,))
    d.line((x - r * 0.95, y - r * 1.0, x - r * 0.95, y - r * 0.25), fill=garis + (a,), width=2)
    d.line((x + r * 0.95, y - r * 1.0, x + r * 0.95, y - r * 0.25), fill=garis + (a,), width=2)
    d.rectangle((x - r * 0.18, y - r * 2.5, x + r * 0.18, y - r * 1.85), fill=tuple(warna) + (a,), outline=garis + (a,), width=1)


def candi(img, cx=540, dasar=HORISON, lebar=780, bangun=1.0, alpha=1.0, warna=BATU, sorot=None):
    """Borobudur tampak samping. bangun: 0..1 teras muncul satu per satu (+ stupa induk di akhir).
    sorot: set indeks teras yang diberi warna emas. Mengembalikan y puncak stupa induk."""
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    n = len(TERAS) + 1
    y = dasar
    for i, (f, h) in enumerate(TERAS):
        k = clamp(bangun * n - i)
        if k <= 0:
            break
        w2 = lebar * f / 2
        hh = h * k
        c = EMAS if sorot and i in sorot else warna
        if i < 6:
            d.rectangle((cx - w2, y - hh, cx + w2, y), fill=tuple(c) + (255,), outline=BATU_GELAP + (255,), width=3)
            # pita relief
            if hh > 20:
                for xx in range(int(cx - w2 + 14), int(cx + w2 - 14), 34):
                    d.rectangle((xx, y - hh + 10, xx + 24, y - 8), outline=BATU_GELAP + (150,), width=2)
            # ujung teras (pagar langkan)
            for xx in range(int(cx - w2 + 6), int(cx + w2), 46):
                d.rectangle((xx, y - hh - 8 * k, xx + 12, y - hh), fill=tuple(c) + (255,), outline=BATU_GELAP + (255,), width=1)
        elif hh >= 18:  # rounded_rectangle error kalau lebih pendek dari sudutnya
            d.rounded_rectangle((cx - w2, y - hh, cx + w2, y), 8, fill=tuple(c) + (255,), outline=BATU_GELAP + (255,), width=3)
        else:
            d.rectangle((cx - w2, y - hh, cx + w2, y), fill=tuple(c) + (255,), outline=BATU_GELAP + (255,), width=1)
        y -= hh
        if i >= 6 and k >= 1:
            m = STUPA_KECIL[i - 6]
            for j in range(m):
                sx = cx - w2 + 22 + j * (2 * w2 - 44) / (m - 1)
                stupa(d, sx, y, 19, c)
    # tangga tengah
    if bangun > 0:
        tinggi_tangga = dasar - max(y, dasar - 270)
        d.rectangle((cx - 26, dasar - tinggi_tangga, cx + 26, dasar), fill=(150, 144, 132, 255), outline=BATU_GELAP + (255,), width=2)
        for yy in range(int(dasar - tinggi_tangga) + 8, int(dasar), 12):
            d.line((cx - 26, yy, cx + 26, yy), fill=BATU_GELAP + (140,), width=2)
    k = clamp(bangun * n - (n - 1))
    puncak = y
    if k > 0:
        r = 62 * k
        stupa(d, cx, y, r, EMAS if sorot and 9 in sorot else warna)
        puncak = y - r * 2.5
    tempel_alpha(img, lap, alpha)
    return puncak


def tempel_alpha(img, lap, alpha):
    se.tempel(img, lap, alpha)


def hutan(img, kuat, t, seed=4, cx=540, lebar=900, dasar=HORISON, tinggi=560):
    """Pohon & semak menutupi candi. kuat 0..1."""
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    n = int(110 * kuat)
    for i in range(110):
        x = cx + rng.uniform(-0.5, 0.5) * lebar
        # makin ke tengah makin tinggi (mengikuti bentuk bukit)
        puncak = dasar - tinggi * (1 - abs(x - cx) / (lebar / 2)) ** 0.8
        y = rng.uniform(puncak, dasar + 20)
        r = rng.uniform(34, 80)
        g = rng.randint(-20, 20)
        warna = (50 + g, 105 + g, 45 + g // 2)
        if i < n:
            goyang = math.sin(t * 1.5 + i) * 3
            d.ellipse((x - r + goyang, y - r * 0.8, x + r + goyang, y + r * 0.8), fill=warna + (235,),
                      outline=(25, 55, 25, 235), width=3)
    se.tempel(img, lap, 1.0)


def timbunan(img, kuat, cx=540, lebar=980, dasar=HORISON, tinggi=520):
    """Gundukan abu/tanah yang menimbun candi (bentuk bukit)."""
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    pts = [(cx - lebar / 2, dasar + 10)]
    for i in range(41):
        f = i / 40
        x = cx - lebar / 2 + f * lebar
        y = dasar - tinggi * kuat * math.sin(math.pi * f) ** 1.3
        pts.append((x, y))
    pts.append((cx + lebar / 2, dasar + 10))
    d.polygon(pts, fill=(120, 105, 85, 245), outline=(70, 55, 40, 255))
    se.tempel(img, lap, 1.0)


def lanskap(gelap=0.0):
    img = LANSKAP.copy()
    if gelap > 0:
        se.tint(img, (10, 10, 25), gelap)
    return img, ImageDraw.Draw(img, "RGBA")


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img, d = lanskap(0.45)
    candi(img, warna=(95, 92, 88))
    hutan(img, 1.0, c.t)
    se.tint(img, (10, 10, 25), 0.3)
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out(c.t / 0.3)
    se.teks(d, (540, 520), "CANDI BUDDHA", int(96 * s) + 1, PUTIH, nama_font="caption", stroke=9, stroke_warna=(0, 0, 0))
    se.teks(d, (540, 620), "TERBESAR DI DUNIA", int(80 * s) + 1, EMAS, nama_font="caption", stroke=9, stroke_warna=(0, 0, 0))
    s2 = back_out((c.t / c.d - 0.18) / 0.12) if c.t / c.d > 0.18 else 0
    if s2 > 0:
        se.teks(d, (540, 760), "pernah HILANG", int(110 * s2) + 1, (255, 110, 70), nama_font="caption", stroke=10,
                stroke_warna=(0, 0, 0))
        se.teks(d, (540, 860), "berabad-abad", 52, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0),
                alpha=c.p(0.25, 0.32))
    se.kartu(img, 540, 1290, "Lagi rame: rencana konser di Borobudur", "yuk kenalan dulu sama sejarahnya", BIRU,
             alpha=c.p(0.5, 0.58), tiang=False, skala=back_out((c.t / c.d - 0.5) / 0.1))
    hdr(img, "yang pernah hilang", alpha=c.p(0.8, 0.95))
    return img


def a_lokasi(c):
    kamera = se.kamera_antara(cam(-7.2, 110.5, 0.36), cam(-7.55, 110.3, 1.25), c.p(0.0, 0.6))
    img, d = peta(kamera)
    a_lbl = 1 - c.p(0.45, 0.6)
    for nama, ll in LABEL_PETA.items():
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 40 if nama != "Laut Jawa" else 36, TINTA if nama != "Laut Jawa" else (200, 215, 235), a_lbl)
    x, y = layar(kamera, MERAPI)
    label(d, (x + 30, y - 60), "Merapi", 40, (130, 40, 20), c.p(0.5, 0.6))
    d.polygon([(x - 18, y + 10), (x, y - 18), (x + 18, y + 10)], fill=(130, 40, 20, int(255 * c.p(0.5, 0.6))))
    bx, by = layar(kamera, BOROBUDUR)
    titik(d, bx, by, MERAH, 14)
    label(d, (bx - 20, by + 56), "Borobudur", 44, (150, 30, 20))
    se.kartu(img, 540, 620, "Wangsa Syailendra", "dibangun ± abad ke-8 – 9", (150, 110, 40),
             alpha=c.p(0.35, 0.45), tiang=False, skala=back_out((c.t / c.d - 0.35) / 0.1))
    hdr(img, "Abad ke-8 – 9")
    return img


def a_struktur(c):
    img, d = lanskap()
    bangun = c.p(0.0, 0.62)
    sorot = None
    if 0.68 <= c.t / c.d < 0.8:
        sorot = set(range(6))
    elif c.t / c.d >= 0.8:
        sorot = {6, 7, 8, 9}
    puncak = candi(img, bangun=bangun, sorot=sorot)
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 230, 610, "6 teras persegi", "", (150, 110, 40), alpha=c.p(0.66, 0.72), tiang=False)
    se.kartu(img, 850, 610, "3 teras bundar", "+ stupa induk", (150, 110, 40), alpha=c.p(0.78, 0.84), tiang=False)
    se.kartu(img, 540, 1300, "Batu andesit · disusun tanpa semen", "", BATU_GELAP, alpha=c.p(0.88, 0.94),
             tiang=False, skala=back_out((c.t / c.d - 0.88) / 0.08))
    hdr(img, "Kayak gunung bertingkat")
    return img


def _panel_relief(d, x, y, w, h, a):
    """Panel relief ilustratif: bingkai + pola (tanpa figur)."""
    aa = int(255 * a)
    d.rectangle((x, y, x + w, y + h), fill=(150, 142, 128, aa), outline=BATU_GELAP + (aa,), width=4)
    d.rectangle((x + 10, y + 10, x + w - 10, y + h - 10), outline=BATU_GELAP + (int(140 * a),), width=2)
    d.arc((x + 20, y + 20, x + w * 0.5, y + h - 20), 180, 360, fill=BATU_GELAP + (int(170 * a),), width=4)
    d.arc((x + w * 0.45, y + 30, x + w - 20, y + h - 10), 180, 360, fill=BATU_GELAP + (int(170 * a),), width=4)
    for i in range(3):
        xx = x + 30 + i * (w - 60) / 2
        d.line((xx, y + h - 20, xx, y + h * 0.45), fill=BATU_GELAP + (int(150 * a),), width=5)


def a_relief(c):
    img = Image.new("RGBA", (W, H), (32, 30, 34, 255))
    se.panel(img, (70, 420, 1010, 1300), alpha=c.p(0, 0.08), warna=(235, 226, 205))
    d = ImageDraw.Draw(img, "RGBA")
    # deretan panel relief muncul satu per satu
    for i in range(4):
        _panel_relief(d, 115 + i * 218, 470, 196, 150, c.p(0.02 + i * 0.04, 0.1 + i * 0.04))
    n = int(2672 * c.p(0.08, 0.45))
    se.teks(d, (540, 740), f"{n:,}".replace(",", "."), 140, MERAH, nama_font="caption", stroke=8,
            stroke_warna=PUTIH, alpha=c.p(0.05, 0.12))
    se.teks(d, (540, 845), "panel relief", 50, TINTA, nama_font="judul", alpha=c.p(0.05, 0.12))
    # stupa kecil berjajar
    a = c.p(0.5, 0.58)
    if a > 0:
        for i in range(9):
            stupa(d, 170 + i * 92, 1060, 26, BATU, a)
        m = int(504 * c.p(0.52, 0.8))
        se.teks(d, (540, 1140), f"{m}", 120, (150, 110, 40), nama_font="caption", stroke=8, stroke_warna=PUTIH, alpha=a)
        se.teks(d, (540, 1235), "arca Buddha", 46, TINTA, nama_font="judul", alpha=a)
    hdr(img, "Dinding penuh cerita")
    return img


def a_ditinggal(c):
    kamera = se.kamera_antara(cam(-7.5, 110.4, 0.9), cam(-7.45, 111.3, 0.55), c.p(0.35, 0.6))
    img, d = peta(kamera)
    mx, my = layar(kamera, MERAPI)
    letus = c.p(0.3, 0.42)
    asap(img, mx, my - 10, c.t, kuat=letus, tinggi=520, lebar=0.9 * kamera.zoom / 0.7)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(mx - 20, my + 10), (mx, my - 20), (mx + 20, my + 10)], fill=(130, 40, 20, 255))
    label(d, (mx + 95, my - 10), "Merapi", 38, (130, 40, 20))
    bx, by = layar(kamera, BOROBUDUR)
    titik(d, bx, by, MERAH, 12)
    label(d, (bx - 60, by + 55), "Borobudur", 36, (150, 30, 20))
    jx, jy = layar(kamera, JATIM)
    k = c.p(0.62, 0.85)
    se.garis_putus(d, [(bx + 40, by - 30), ((bx + jx) / 2, by - 120), (jx, jy)], k, (30, 60, 120), tebal=8)
    if k >= 1:
        titik(d, jx, jy, (30, 60, 120), 14)
    se.kartu(img, 540, 560, "Kok bisa ditinggalkan?", "nggak ada yang tahu pasti", MERAH,
             alpha=c.p(0.05, 0.13), tiang=False, skala=back_out((c.t / c.d - 0.05) / 0.1))
    se.kartu(img, 540, 1260, "Pusat kerajaan pindah ke Jawa Timur", "abad ke-10", (30, 60, 120),
             alpha=c.p(0.7, 0.78), tiang=False)
    hdr(img, "Dugaan para ahli")
    return img


def a_tertimbun(c):
    img, d = lanskap(0.15 * c.p(0, 1))
    candi(img)
    # abu turun
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    rng = random.Random(8)
    hujan_abu = c.p(0.0, 0.15) * (1 - c.p(0.55, 0.75))
    for i in range(160):
        x = rng.uniform(0, W)
        y = (rng.uniform(0, HORISON) + c.t * rng.uniform(120, 220)) % HORISON
        dl.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(200, 200, 200, int(200 * hujan_abu)))
    img.alpha_composite(lap)
    timbunan(img, c.p(0.1, 0.55))
    hutan(img, c.p(0.4, 0.85), c.t, tinggi=560 * c.p(0.1, 0.55) + 40)
    d = ImageDraw.Draw(img, "RGBA")
    abad = int(lerp(10, 19, c.p(0.05, 0.9)))
    se.teks(d, (540, 520), f"abad ke-{abad}", 72, PUTIH, nama_font="caption", stroke=8, stroke_warna=(0, 0, 0),
            alpha=c.p(0.03, 0.1))
    se.kartu(img, 540, 1300, "Tertutup abu, tanah & hutan", "dunia luar hampir lupa", (70, 55, 40),
             alpha=c.p(0.6, 0.68), tiang=False)
    hdr(img, "Berabad-abad")
    return img


def a_1814(c):
    img, d = lanskap()
    candi(img)
    gali = c.p(0.35, 0.95)
    timbunan(img, 1 - gali * 0.75)
    hutan(img, 1 - gali, c.t, tinggi=600)
    d = ImageDraw.Draw(img, "RGBA")
    # ± 200 pekerja (titik) di sekeliling bukit
    a = c.p(0.3, 0.38)
    if a > 0:
        rng = random.Random(14)
        for i in range(200):
            f = rng.random()
            x = 540 + (f - 0.5) * 960
            y = HORISON - 470 * (1 - gali * 0.75) * math.sin(math.pi * f) ** 1.3 + rng.uniform(-10, 40)
            x += math.sin(c.t * 4 + i) * 4
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(180, 40, 30, int(255 * a)), outline=(255, 240, 220, int(200 * a)), width=2)
    se.kartu(img, 540, 540, "1814 · Thomas Stamford Raffles", "penguasa Inggris di Jawa", (40, 60, 130),
             alpha=c.p(0.03, 0.11), tiang=False, skala=back_out((c.t / c.d - 0.03) / 0.1))
    se.kartu(img, 540, 680, "± 200 orang · 2 bulan", "dipimpin H.C. Cornelius", MERAH, alpha=c.p(0.4, 0.48), tiang=False,
             skala=back_out((c.t / c.d - 0.4) / 0.1))
    se.kartu(img, 540, 1300, "1835: seluruh candi akhirnya terbuka", "", HIJAU_TUA, alpha=c.p(0.84, 0.9), tiang=False)
    hdr(img, "Ditemukan lagi")
    return img


def a_pugar(c):
    img, d = lanskap()
    candi(img, warna=se.lerp_rgb((110, 100, 85), BATU, c.p(0.5, 0.95)))
    d = ImageDraw.Draw(img, "RGBA")
    # batu-batu bernomor dibongkar lalu dipasang lagi
    rng = random.Random(21)
    k = c.t / c.d
    for i in range(36):
        f0 = rng.uniform(0.15, 0.55)
        x0 = 540 + rng.uniform(-330, 330)
        y0 = HORISON - rng.uniform(40, 300)
        x1 = rng.choice([rng.uniform(60, 200), rng.uniform(880, 1020)])
        y1 = HORISON + rng.uniform(40, 220)
        if k < f0:
            continue
        # keluar (f0..f0+0.12), diam, lalu kembali (0.7..0.85)
        keluar = clamp((k - f0) / 0.12)
        balik = clamp((k - 0.7 - i * 0.003) / 0.15)
        f = se.ease(keluar) * (1 - se.ease(balik))
        x = lerp(x0, x1, f)
        y = lerp(y0, y1, f) - math.sin(math.pi * f) * 120
        d.rectangle((x - 20, y - 14, x + 20, y + 14), fill=(140, 132, 118, 255), outline=BATU_GELAP + (255,), width=3)
        se.teks(d, (x, y), str(100 + i * 7), 16, TINTA, nama_font="ui")
    n = int(1_000_000 * c.p(0.2, 0.65))
    se.teks(d, (540, 560), "± " + f"{n:,}".replace(",", "."), 100, MERAH, nama_font="caption", stroke=8,
            stroke_warna=PUTIH, alpha=c.p(0.18, 0.25))
    se.teks(d, (540, 650), "batu dibongkar, dipasang lagi", 44, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(0, 0, 0), alpha=c.p(0.2, 0.28))
    se.kartu(img, 540, 1300, "Pemugaran 1973 – 1983", "Indonesia + UNESCO", BIRU, alpha=c.p(0.05, 0.13),
             tiang=False, skala=back_out((c.t / c.d - 0.05) / 0.1))
    hdr(img, "Dipugar besar-besaran")
    return img


def _sandal(d, x, y, s=1.0, a=1.0):
    aa = int(255 * a)
    d.rounded_rectangle((x - 40 * s, y - 95 * s, x + 40 * s, y + 95 * s), int(38 * s), fill=(190, 160, 105, aa),
                        outline=(90, 65, 35, aa), width=5)
    for i in range(6):
        yy = y - 70 * s + i * 28 * s
        d.line((x - 30 * s, yy, x + 30 * s, yy), fill=(140, 110, 65, aa), width=3)
    d.arc((x - 42 * s, y - 70 * s, x + 42 * s, y + 10 * s), 180, 360, fill=(110, 75, 40, aa), width=int(10 * s))


def a_warisan(c):
    img, d = lanskap()
    candi(img)
    se.tint(img, (15, 12, 8), 0.45 * c.p(0.45, 0.55))
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 560, "Warisan Dunia UNESCO", "sejak 1991", BIRU, alpha=c.p(0.03, 0.11) * (1 - c.p(0.45, 0.5)),
             tiang=False, skala=back_out((c.t / c.d - 0.03) / 0.1))
    a = c.p(0.5, 0.58)
    if a > 0:
        se.panel(img, (150, 470, 930, 1060), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 550), "Mau naik ke candi?", 50, TINTA, nama_font="judul", alpha=a)
        _sandal(d, 430, 780, 1.0, a)
        _sandal(d, 560, 800, 1.0, a)
        se.teks(d, (760, 730), "kuota", 40, (150, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (760, 780), "dibatasi", 40, (150, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (760, 850), "sandal khusus", 32, TINTA, alpha=a)
        se.teks(d, (540, 990), "biar batunya nggak makin aus", 40, (90, 70, 50), alpha=a)
    hdr(img, "Sekarang")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    img, d = lanskap(0.55)
    candi(img, warna=(105, 100, 95))
    se.tint(img, (10, 6, 0), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 470, 990, 960), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 560), "Selamat dari abu, hutan,", 46, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 625), "dan waktu", 46, TINTA, nama_font="judul", alpha=a)
        stupa(d, 540, 830, 70, EMAS, a)
        se.teks(d, (540, 900), "Sekarang giliran kita yang jaga", 42, (150, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Candi Buddha terbesar di dunia, pernah hilang, berabad-abad. Lagi rame soal rencana konser "
                   "di Borobudur? Yuk, kenalan dulu sama sejarahnya.", a_hook, transisi=False),
    Adegan("lokasi", "Borobudur dibangun di Jawa Tengah, nggak jauh dari Gunung Merapi. Kira-kira abad kedelapan "
                     "sampai kesembilan, di zaman Wangsa Syailendra.", a_lokasi),
    Adegan("struktur", "Bentuknya kayak gunung bertingkat. Enam teras persegi, tiga teras bundar, dan satu stupa "
                       "besar di puncak. Semuanya batu andesit, disusun tanpa semen.", a_struktur),
    Adegan("relief", "Dindingnya penuh cerita. Ada dua ribu enam ratus tujuh puluh dua panel relief, "
                     "dan lima ratus empat arca Buddha.", a_relief),
    Adegan("ditinggal", "Tapi, kok bisa candi sebesar ini ditinggalkan? Nggak ada yang tahu pasti. Dugaan yang "
                        "sering disebut: letusan Merapi, dan pusat kerajaan yang pindah ke Jawa Timur.", a_ditinggal),
    Adegan("tertimbun", "Pelan-pelan, Borobudur tertutup abu, tanah, dan hutan lebat. Dunia luar hampir lupa, "
                        "ada candi raksasa di sini.", a_tertimbun),
    Adegan("1814", "Tahun seribu delapan ratus empat belas, Raffles, penguasa Inggris di Jawa, dapat kabar soal "
                   "bukit penuh batu berukir. Sekitar dua ratus orang dikerahkan, dua bulan nebang pohon dan buang "
                   "tanah.", a_1814),
    Adegan("pugar", "Tapi candinya udah rusak dan kemasukan air. Tahun tujuh puluhan, Indonesia dan UNESCO "
                    "memugarnya. Sekitar satu juta batu dibongkar, lalu dipasang lagi, satu per satu.", a_pugar),
    Adegan("warisan", "Tahun sembilan belas sembilan puluh satu, Borobudur resmi jadi Warisan Dunia UNESCO. Sekarang, "
                      "pengunjung yang naik dibatasi, dan wajib pakai sandal khusus, biar batunya nggak makin aus.",
           a_warisan),
    Adegan("penutup", "Borobudur udah selamat dari abu, hutan, dan waktu. Sekarang giliran kita yang jaga. "
                      "Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
