"""Shorts ±88 detik: Dua klub ini lebih tua dari Indonesia. PSM Makassar (1915) dan Persija/VIJ (1928),
lapangan VIJ dibantu M.H. Thamrin, Soeratin keluar dari perusahaan Belanda, PSSI 19 April 1930,
dan nama "Voetbalbond Indonesia Jacatra" yang diam-diam melawan: pakai "Indonesia" dan "Jacatra", bukan Batavia.

Tren: PSM Makassar vs Persija 1-1 (Super League, 21 November 2026).
Visual: dua perisai klub + tahun vs 1945, peta Sulawesi/Makassar, bond Belanda vs pemuda pribumi (titik),
peta Jawa + Batavia, lapangan + koin gulden, Soeratin (siluet) + kantor Belanda, tujuh kota di Jawa terhubung,
piala 1931, papan nama VIJ dengan kata yang disorot, stempel ganti nama zaman Jepang, penutup maskot.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Peta, back_out, clamp, lerp

NAMA_FILE = "klub-bola-lebih-tua-dari-indonesia-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "LEBIH TUA DARI INDONESIA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KUNING = (255, 214, 10)
GELAP = (10, 10, 20)
KREM = (247, 236, 208)
KREM_LABEL = (240, 225, 190)
HIJAU_TUA = (30, 110, 60)
HIJAU_LAP = (60, 135, 60)
BIRU = (30, 80, 150)
COKLAT = (120, 80, 40)
MERAH_TUA = (150, 30, 25)
MERAH_PSM = (175, 25, 30)
ORANYE = (235, 110, 20)
ORANYE_BELANDA = (230, 120, 20)

# ------------------------------------------------------------------ pengaman PIL

def _kotak(box):
    if len(box) == 2:
        (x0, y0), (x1, y1) = box
    else:
        x0, y0, x1, y1 = box
    x0, x1 = sorted((int(round(x0)), int(round(x1))))
    y0, y1 = sorted((int(round(y0)), int(round(y1))))
    return [x0, y0, max(x1, x0 + 1), max(y1, y0 + 1)]


_rr_asli = ImageDraw.ImageDraw.rounded_rectangle
_el_asli = ImageDraw.ImageDraw.ellipse


def _rr_aman(self, xy, radius=0, *args, **kw):
    b = _kotak(xy)
    r = int(min(radius, (b[2] - b[0]) // 2 - 1, (b[3] - b[1]) // 2 - 1))
    if r < 1:
        return self.rectangle(b, kw.get("fill", args[0] if args else None), kw.get("outline"), kw.get("width", 1))
    return _rr_asli(self, b, r, *args, **kw)


def _el_aman(self, xy, *args, **kw):
    return _el_asli(self, _kotak(xy), *args, **kw)


ImageDraw.ImageDraw.rounded_rectangle = _rr_aman
ImageDraw.ImageDraw.ellipse = _el_aman

# ------------------------------------------------------------------ peta

print("  menyiapkan peta Jawa & Sulawesi...")
NUSA = Peta(98, 128, -20, 6, 72, [], [(-7.2, 110.0, 0.4), (-7.6, 112.6, 0.4), (-2.0, 120.2, 0.6), (-4.5, 120.0, 0.4)],
            seed=36, darat=pd.SEMUA)

MAKASSAR = (-5.14, 119.42)
BATAVIA = (-6.17, 106.83)
KOTA_PSSI = [  # (nama, lat, lon, dx label, dy label)
    ("Batavia", -6.17, 106.83, 0, -50),
    ("Bandung", -6.91, 107.61, 0, 52),
    ("Magelang", -7.47, 110.22, -70, -48),
    ("Yogyakarta", -7.80, 110.36, 0, 52),
    ("Solo", -7.57, 110.82, 40, -50),
    ("Madiun", -7.63, 111.52, 30, 52),
    ("Surabaya", -7.25, 112.75, 0, -50),
]

print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 36, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (8, 12, 24), 0.66)


# ------------------------------------------------------------------ helper

def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def skala_muncul(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


def cam(peta, lat, lon, zoom):
    x, y = peta.px(lat, lon)
    return (x, y, zoom)


def layar(peta, kamera, ll):
    return kamera.layar(*peta.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def titik_kota(d, x, y, nama, alpha=1.0, warna=(255, 200, 60), dy=50, uk=40, t=0.0, dx=0):
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    r = 15 + 3 * math.sin(t * 5)
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=PUTIH + (a,), width=4)
    label(d, (x + dx, y + dy), nama, uk, alpha=alpha)


def stempel(img, isi, cx, cy, s, uk=76, sudut=-8, warna=(210, 30, 30)):
    if s <= 0.01:
        return
    f = se.font("caption", uk)
    lw = int(f.getlength(isi)) + 80
    lap = Image.new("RGBA", (lw, uk + 90), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((10, 10, lw - 10, uk + 80), 22, fill=(247, 236, 208, 215), outline=tuple(warna) + (255,),
                         width=12)
    dl.text((lw / 2, (uk + 90) / 2), isi, font=f, fill=tuple(warna) + (255,), anchor="mm")
    lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, 1.0, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


def pita(img, y, isi, warna_garis=(170, 30, 20), uk=56, alpha=1.0, x0=90, x1=990, tinggi=110):
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((x0, y - tinggi / 2, x1, y + tinggi / 2), 30, fill=(247, 236, 208, 242),
                         outline=tuple(warna_garis) + (255,), width=6)
    se.tempel(img, lap, alpha)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, ((x0 + x1) / 2, y), isi, uk, warna_garis, nama_font="caption", alpha=alpha)


def perisai(img, cx, cy, s, warna, inisial, tahun, alpha=1.0, sudut=0.0):
    """Perisai klub generik (bukan logo asli): inisial + tahun berdiri."""
    if alpha <= 0.01 or s <= 0.05:
        return
    w, h = 360, 430
    lap = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)

    def bentuk(ox, oy, k=1.0):
        pts = []
        for i in range(21):
            u = i / 20
            pts.append((ox + 20 + (w - 40) * u, oy + 20 + 18 * math.sin(u * math.pi * 2) * 0))
        pts = [(ox + 20, oy + 20), (ox + w - 20, oy + 20), (ox + w - 20, oy + h * 0.55)]
        for i in range(1, 16):
            u = i / 15
            pts.append((ox + (w - 20) - (w / 2 - 20) * u, oy + h * 0.55 + (h * 0.42) * math.sin(u * math.pi / 2)))
        for i in range(1, 16):
            u = i / 15
            pts.append((ox + w / 2 - (w / 2 - 20) * u, oy + h * 0.97 - (h * 0.42) * (1 - math.cos(u * math.pi / 2))))
        return pts

    d.polygon(bentuk(14, 16), fill=(0, 0, 0, 110))
    d.polygon(bentuk(0, 0), fill=tuple(warna) + (255,), outline=(250, 240, 215, 255))
    d.line(bentuk(0, 0) + [bentuk(0, 0)[0]], fill=(250, 240, 215, 255), width=12)
    d.rectangle((40, 150, w - 40, 165), fill=(250, 240, 215, 200))
    d.text((w / 2, 95), inisial, font=se.font("caption", 92), fill=PUTIH, anchor="mm", stroke_width=5,
           stroke_fill=(30, 20, 10))
    d.text((w / 2, 250), tahun, font=se.font("caption", 104), fill=KUNING, anchor="mm", stroke_width=6,
           stroke_fill=(30, 20, 10))
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))), Image.BICUBIC)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def bola(d, x, y, r, putar=0.0, alpha=1.0):
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 250, 245, a), outline=(30, 30, 30, a), width=max(2, int(r / 12)))
    for k in range(5):
        u = putar + k * 2 * math.pi / 5
        px, py = x + math.cos(u) * r * 0.55, y + math.sin(u) * r * 0.55
        rr = r * 0.22
        d.ellipse((px - rr, py - rr, px + rr, py + rr), fill=(30, 30, 30, a))
    rr = r * 0.25
    d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(30, 30, 30, a))


def orang(d, x, y, s=1.0, warna=(60, 45, 35), alpha=1.0, topi=None):
    """Siluet orang tanpa wajah. topi: None | 'peci' | 'helm'."""
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    d.ellipse((x - 10 * s, y - 52 * s, x + 10 * s, y - 32 * s), fill=c)
    if topi == "peci":
        d.rectangle((x - 10 * s, y - 58 * s, x + 10 * s, y - 47 * s), fill=(20, 20, 20, a))
    elif topi == "helm":
        d.pieslice((x - 14 * s, y - 62 * s, x + 14 * s, y - 38 * s), 180, 360, fill=(240, 240, 230, a))
    d.rounded_rectangle((x - 13 * s, y - 30 * s, x + 13 * s, y), int(6 * s) + 1, fill=c)


def lapangan(img, box, alpha=1.0, garis=1.0):
    x0, y0, x1, y1 = box
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rounded_rectangle((x0 + 8, y0 + 12, x1 + 8, y1 + 12), 18, fill=(0, 0, 0, 100))
    d.rounded_rectangle(box, 18, fill=HIJAU_LAP + (255,))
    for k in range(6):
        if k % 2 == 0:
            yy0 = y0 + (y1 - y0) * k / 6
            d.rectangle((x0 + 4, yy0, x1 - 4, yy0 + (y1 - y0) / 6), fill=(70, 150, 70, 255))
    g = int(255 * garis)
    p = 24
    d.rectangle((x0 + p, y0 + p, x1 - p, y1 - p), outline=(250, 250, 240, g), width=6)
    cy = (y0 + y1) / 2
    d.line((x0 + p, cy, x1 - p, cy), fill=(250, 250, 240, g), width=6)
    cx = (x0 + x1) / 2
    r = (x1 - x0) * 0.14
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(250, 250, 240, g), width=6)
    bw = (x1 - x0) * 0.22
    d.rectangle((cx - bw, y0 + p, cx + bw, y0 + p + (y1 - y0) * 0.12), outline=(250, 250, 240, g), width=6)
    d.rectangle((cx - bw, y1 - p - (y1 - y0) * 0.12, cx + bw, y1 - p), outline=(250, 250, 240, g), width=6)
    se.tempel(img, lap, alpha)


def koin(d, x, y, r=30, alpha=1.0):
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(230, 190, 60, a), outline=(140, 100, 20, a), width=4)
    d.text((x, y), "ƒ", font=se.font("judul", int(r * 1.2)), fill=(140, 100, 20, a), anchor="mm")


def bendera_mp(d, x, y, s=1.0, alpha=1.0, t=0.0):
    a = int(255 * alpha)
    d.line((x, y, x, y - 300 * s), fill=(70, 50, 30, a), width=max(3, int(10 * s)))
    pts_m, pts_p = [], []
    for i in range(21):
        u = i / 20
        gel = math.sin(u * 4 + t * 5) * 10 * s * u
        pts_m.append((x + u * 220 * s, y - 300 * s + gel))
        pts_p.append((x + u * 220 * s, y - 230 * s + gel))
    pts_b = [(x + u * 220 * s, y - 160 * s + math.sin(u * 4 + t * 5) * 10 * s * u) for u in [i / 20 for i in range(21)]]
    d.polygon(pts_m + pts_p[::-1], fill=(210, 30, 35, a))
    d.polygon(pts_p + pts_b[::-1], fill=(250, 250, 245, a))


def piala(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    emas = (235, 190, 60, a)
    gelap = (150, 110, 30, a)
    d.pieslice((x - 110 * s, y - 260 * s, x + 110 * s, y - 40 * s), 0, 180, fill=emas, outline=gelap, width=5)
    d.rectangle((x - 110 * s, y - 150 * s, x + 110 * s, y - 148 * s), fill=gelap)
    d.rectangle((x - 110 * s, y - 220 * s, x + 110 * s, y - 150 * s), fill=emas)
    d.arc((x - 170 * s, y - 210 * s, x - 70 * s, y - 110 * s), 90, 270, fill=gelap, width=max(3, int(14 * s)))
    d.arc((x + 70 * s, y - 210 * s, x + 170 * s, y - 110 * s), 270, 90, fill=gelap, width=max(3, int(14 * s)))
    d.rectangle((x - 18 * s, y - 45 * s, x + 18 * s, y + 20 * s), fill=emas)
    d.rounded_rectangle((x - 80 * s, y + 20 * s, x + 80 * s, y + 70 * s), int(8 * s) + 1, fill=gelap)


def gedung(d, x, y, s=1.0, alpha=1.0, warna=(170, 150, 120)):
    """Kantor kolonial sederhana."""
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    d.rectangle((x - 220 * s, y - 220 * s, x + 220 * s, y), fill=c, outline=(90, 70, 50, a), width=4)
    d.polygon([(x - 250 * s, y - 220 * s), (x, y - 330 * s), (x + 250 * s, y - 220 * s)], fill=(150, 60, 40, a))
    for k in range(4):
        wx = x - 165 * s + k * 110 * s
        d.rectangle((wx - 25 * s, y - 180 * s, wx + 25 * s, y - 110 * s), fill=(60, 70, 90, a))
    d.rectangle((x - 35 * s, y - 90 * s, x + 35 * s, y), fill=(80, 55, 35, a))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 930, 560, (230, 90, 40), 1.1 + 0.25 * math.sin(c.t * 4))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 410), "LEBIH TUA", 116, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 530), "DARI INDONESIA", 104, KUNING, nama_font="caption", stroke=11, stroke_warna=GELAP)
    goyang = math.sin(c.t * 2.2) * 3
    perisai(img, 290, 870, 0.92, MERAH_PSM, "PSM", "1915", sudut=6 + goyang)
    perisai(img, 790, 870, 0.92, ORANYE, "VIJ", "1928", sudut=-6 - goyang)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 880), "VS", 88, PUTIH, nama_font="caption", stroke=9, stroke_warna=MERAH_TUA)
    bola(d, 540, 1120 + abs(math.sin(c.t * 4)) * -40, 46, putar=c.t * 3)
    # kartu tren + bendera 1945 kecil
    a = c.p(0.2, 0.28)
    if a > 0:
        se.kartu(img, 540, 1260, "Sabtu kemarin: PSM 1-1 Persija", "Super League, 21 Nov 2026", HIJAU_TUA,
                 alpha=a * (1 - c.p(0.6, 0.64)), tiang=False, skala=skala_muncul(c, 0.2) * 1.25)
    a1 = c.p(0.0, 0.0001)
    stempel(img, "Indonesia: 1945", 540, 1270, 0.62 * a1 * (1 - c.p(0.18, 0.21)), uk=60, sudut=-4, warna=(60, 60, 70))
    a2 = c.p(0.64, 0.72)
    if a2 > 0:
        pita(img, 1270, "Nama yang melawan Belanda?", uk=54, alpha=a2)
    return img


def a_psm(c):
    kamera = se.kamera_antara(cam(NUSA, -4.0, 113.0, 0.62), cam(NUSA, -3.9, 119.0, 1.7), c.p(0.0, 0.55))
    img = se.render_peta(NUSA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    mx, my = layar(NUSA, kamera, MAKASSAR)
    a = c.p(0.12, 0.22)
    if a > 0:
        se.glow(img, mx, my, 170, (255, 200, 80), 1.2 * a)
        d = ImageDraw.Draw(img, "RGBA")
        titik_kota(d, mx, my, "Makassar", a, (200, 52, 44), t=c.t, dx=-90, dy=55)
    se.kartu(img, 540, 470, "2 November 1915", "Makassar, Hindia Belanda", BIRU, alpha=c.p(0.05, 0.12), tiang=False,
             skala=skala_muncul(c, 0.05))
    a2 = c.p(0.3, 0.38)
    if a2 > 0:
        se.panel(img, (90, 600, 990, 770), alpha=a2)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 660), "Makassaarsche", 56, MERAH_TUA, nama_font="caption", alpha=a2)
        se.teks(d, (540, 725), "Voetbalbond", 50, TINTA, nama_font="judul", alpha=a2)
        stempel(img, "NAMA BELANDA", 820, 810, skala_muncul(c, 0.45, 0.08) * 0.55, uk=56, sudut=8)
    a3 = c.p(0.68, 0.76)
    if a3 > 0:
        pita(img, 1280, "Klub tertua yang masih ada", warna_garis=HIJAU_TUA, uk=54, alpha=a3)
    hdr(img, "Cikal bakal PSM Makassar")
    return img


def a_belanda(c):
    img = LATAR.copy()
    lapangan(img, (140, 600, 940, 1130), c.p(0.0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    # pemain Belanda (oranye) menguasai lapangan
    rng = random.Random(8)
    for i in range(8):
        a = c.p(0.05 + i * 0.02, 0.1 + i * 0.02)
        x = 240 + (i % 4) * 200 + rng.uniform(-30, 30)
        y = 740 + (i // 4) * 230 + rng.uniform(-30, 30) + math.sin(c.t * 3 + i) * 8
        orang(d, x, y, 2.0, ORANYE_BELANDA, a, topi="helm")
    bola(d, 540 + math.sin(c.t * 2) * 120, 865, 22, putar=c.t * 4)
    se.kartu(img, 540, 470, "Bond milik orang Belanda", "mengatur liga resmi", ORANYE_BELANDA, alpha=c.p(0.0, 0.08),
             tiang=False, skala=skala_muncul(c, 0.0))
    # pemuda pribumi di pinggir lapangan
    a2 = c.p(0.45, 0.53)
    if a2 > 0:
        for i in range(5):
            orang(d, 230 + i * 150, 1235, 1.8, (55, 40, 30), a2, topi="peci")
        se.kartu(img, 540, 1320, "Pemuda pribumi", "merasa dianaktirikan", MERAH, alpha=a2, tiang=False,
                 skala=skala_muncul(c, 0.45))
    hdr(img, "Zaman Hindia Belanda")
    return img


def a_vij(c):
    kamera = se.kamera_antara(cam(NUSA, -6.6, 108.5, 1.0), cam(NUSA, -6.4, 106.9, 2.3), c.p(0.0, 0.3))
    img = se.render_peta(NUSA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    bx, by = layar(NUSA, kamera, BATAVIA)
    titik_kota(d, bx, by, "Batavia", c.p(0.04, 0.1), (200, 52, 44), t=c.t, dy=-55)
    a = c.p(0.0, 0.08)
    se.panel(img, (110, 410, 970, 600), alpha=a)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 465), "28 Oktober 1928: Sumpah Pemuda", 42, TINTA, nama_font="judul", alpha=a)
    se.teks(d, (540, 540), "28 November 1928: klub sendiri!", 46, MERAH_TUA, nama_font="caption",
            alpha=c.p(0.16, 0.22))
    # lapangan sendiri + koin gulden
    a2 = c.p(0.5, 0.58)
    if a2 > 0:
        se.tint(img, (8, 12, 24), 0.45 * a2)
        lapangan(img, (230, 760, 850, 1180), a2, garis=c.p(0.55, 0.7))
        d = ImageDraw.Draw(img, "RGBA")
        for i in range(5):
            f = clamp(c.p(0.62, 0.85) * 5 - i * 0.8)
            if f > 0:
                koin(d, 300 + i * 120, lerp(700, 1230, back_out(f) * 0.0 + f) if f < 1 else 1230, 34)
        se.kartu(img, 540, 1330, "Dibantu M.H. Thamrin", "biaya ± 2.000 gulden", BIRU, alpha=c.p(0.62, 0.7),
                 tiang=False, skala=skala_muncul(c, 0.62))
    hdr(img, "Batavia, 1928")
    return img


def a_soeratin(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 900, 520, (230, 190, 90), 0.8)
    se.panel(img, (110, 410, 970, 540), alpha=c.p(0.0, 0.05))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 475), "TAPI INI BELUM SEBERAPA…", 54, (170, 30, 20), nama_font="caption", alpha=c.p(0.0, 0.05))
    a = c.p(0.15, 0.23)
    gedung(d, 540, 1120, 1.15, a)
    if a > 0:
        label(d, (540, 1160), "perusahaan konstruksi Belanda", 38, alpha=a)
    # siluet Soeratin keluar dari kantor
    k = c.p(0.45, 0.85)
    if c.p(0.25, 0.3) > 0:
        x = lerp(540, 860, k)
        orang(d, x, 1115 + math.sin(k * 30) * 3 * (k > 0), 3.2, (25, 20, 15), c.p(0.25, 0.3), topi="peci")
        se.kartu(img, 330, 640, "Soeratin", "insinyur lulusan Jerman", BIRU, alpha=c.p(0.25, 0.32), tiang=False,
                 skala=skala_muncul(c, 0.25))
    a2 = c.p(0.55, 0.62)
    if a2 > 0:
        stempel(img, "KELUAR!", 800, 700, skala_muncul(c, 0.55, 0.08) * 0.8, uk=76, sudut=8)
    a3 = c.p(0.78, 0.85)
    if a3 > 0:
        pita(img, 1290, "Demi menyatukan klub pribumi", warna_garis=HIJAU_TUA, uk=54, alpha=a3)
    hdr(img, "Yogyakarta, 1930")
    return img


def a_pssi(c):
    kamera = se.kamera_antara(cam(NUSA, -8.5, 109.8, 1.35), cam(NUSA, -8.5, 109.8, 1.45), c.p(0.0, 1.0))
    img = se.render_peta(NUSA, kamera)
    a0 = c.p(0.0, 0.06) * (1 - c.p(0.78, 0.82))
    se.tint(img, (8, 12, 24), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 470), "Rapat diam-diam", 62, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP, alpha=a0)
    se.teks(d, (540, 545), "biar nggak dicurigai polisi Belanda", 38, KREM, nama_font="tangan", stroke=5,
            stroke_warna=GELAP, alpha=c.p(0.05, 0.11) * (1 - c.p(0.78, 0.82)))
    titik = [layar(NUSA, kamera, (lat, lon)) for _, lat, lon, _, _ in KOTA_PSSI]
    yk = titik[3]
    for i, ((nama, _, _, dx, dy), (x, y)) in enumerate(zip(KOTA_PSSI, titik)):
        m = 0.28 + i * 0.035
        a = c.p(m, m + 0.05)
        if a <= 0:
            continue
        if i != 3:
            se.garis_putus(d, [(x, y), yk], c.p(m + 0.02, m + 0.12), (200, 52, 44), tebal=6, panah=False)
        titik_kota(d, x, y, nama, a, (255, 200, 60) if i != 0 else (200, 52, 44), t=c.t, dx=dx, dy=dy, uk=34)
    a2 = c.p(0.58, 0.64)
    if a2 > 0:
        stempel(img, "PSSI", 540, 1130, skala_muncul(c, 0.58, 0.08) * 1.1, uk=110, sudut=-6, warna=MERAH_TUA)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1290), "19 April 1930 · 7 bond", 50, PUTIH, nama_font="caption", stroke=6,
                stroke_warna=GELAP, alpha=a2)
    a3 = c.p(0.82, 0.88)
    if a3 > 0:
        se.kartu(img, 540, 500, "Salah satunya:", "klub dari Batavia", MERAH, alpha=a3, tiang=False,
                 skala=skala_muncul(c, 0.82) * 1.4)
    hdr(img, "Persatoean Sepakraga Seloeroeh Indonesia")
    return img


def a_juara(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 900, 520, (255, 200, 80), 1.0 + 0.2 * math.sin(c.t * 5))
    d = ImageDraw.Draw(img, "RGBA")
    s = skala_muncul(c, 0.0, 0.14)
    piala(d, 540, 1060, 1.3 * s)
    se.teks(d, (540, 470), "1931", 130, KUNING, nama_font="caption", stroke=10, stroke_warna=GELAP, alpha=c.p(0.0, 0.06))
    se.teks(d, (540, 590), "Juara kompetisi PSSI pertama", 50, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=GELAP, alpha=c.p(0.08, 0.14))
    rng = random.Random(3)
    for i in range(40):
        u = (c.t * 0.5 + rng.random()) % 1
        x = rng.uniform(120, 960)
        y = 650 + u * 700
        d.rectangle((x, y, x + 12, y + 18), fill=rng.choice([(255, 214, 10), (230, 60, 50), (250, 250, 240)]) + (200,))
    a2 = c.p(0.55, 0.62)
    if a2 > 0:
        pita(img, 1280, "Terus, apa yang berani dari namanya?", uk=46, alpha=a2)
    hdr(img, "Klub Batavia jadi juara")
    return img


def a_nama(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 850, 560, (90, 150, 230), 0.9)
    a = c.p(0.0, 0.06)
    se.panel(img, (70, 560, 1010, 1060), alpha=a)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 470), "VIJ", 140, ORANYE, nama_font="caption", stroke=10, stroke_warna=GELAP, alpha=a)
    hl_ind = c.p(0.25, 0.33)
    hl_jac = c.p(0.55, 0.63)
    baris = [("Voetbalbond", 640, 0.0, TINTA), ("Indonesia", 790, hl_ind, MERAH_TUA), ("Jacatra", 940, hl_jac, MERAH_TUA)]
    for isi, y, hl, warna in baris:
        if hl > 0:
            f = se.font("caption", 92)
            lw = f.getlength(isi) / 2 + 30
            d.rounded_rectangle((540 - lw * hl, y - 60, 540 + lw * hl, y + 60), 20, fill=(255, 214, 10, 230))
        se.teks(d, (540, y), isi, 92 if hl > 0 else 82, warna if hl > 0 else TINTA, nama_font="caption", alpha=a)
    a2 = c.p(0.33, 0.4)
    if a2 > 0:
        se.kartu(img, 300, 1160, "Negaranya", "belum ada!", MERAH, alpha=a2, tiang=False, skala=skala_muncul(c, 0.33))
    a3 = c.p(0.66, 0.72)
    if a3 > 0:
        se.kartu(img, 760, 1160, "Bukan \"Batavia\"", "nama dari Belanda", BIRU, alpha=a3, tiang=False,
                 skala=skala_muncul(c, 0.66), coret=0.0)
        stempel(img, "BATAVIA", 760, 1300, skala_muncul(c, 0.72, 0.08) * 0.55, uk=60, sudut=-6, warna=(60, 60, 70))
        d = ImageDraw.Draw(img, "RGBA")
        k = c.p(0.76, 0.84)
        if k > 0:
            d.line((620, 1300, lerp(620, 900, k), 1300), fill=(220, 30, 25, 255), width=14)
    hdr(img, "Nama yang melawan")
    return img


def a_jepang(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 470, "Zaman Jepang, 1942", "nama berbau Belanda dilarang", MERAH, alpha=c.p(0.0, 0.08),
             tiang=False, skala=skala_muncul(c, 0.0))
    # papan nama lama dicoret -> nama baru
    a = c.p(0.08, 0.16)
    se.panel(img, (110, 620, 970, 800), alpha=a)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 710), "Makassaarsche Voetbalbond", 52, TINTA, nama_font="judul", alpha=a)
    k = c.p(0.22, 0.32)
    if k > 0:
        d.line((150, 710, lerp(150, 930, k), 710), fill=(220, 30, 25, 255), width=12)
    perisai(img, 300, 1040, 0.62 * skala_muncul(c, 0.32, 0.1), MERAH_PSM, "PSM", "1915", sudut=5)
    a2 = c.p(0.55, 0.62)
    if a2 > 0:
        perisai(img, 780, 1040, 0.62 * skala_muncul(c, 0.55, 0.1), ORANYE, "VIJ", "1928", sudut=-5)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (780, 1270), "→ PERSIJA", 60, MERAH_TUA, nama_font="caption", stroke=5, stroke_warna=KREM,
                alpha=c.p(0.7, 0.76))
    hdr(img, "Ganti nama")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 960, 480, (230, 190, 90), 0.9)
    a = c.p(0.0, 0.08) * (1 - c.p(0.6, 0.64))
    if a > 0:
        perisai(img, 300, 1080, 0.6, MERAH_PSM, "PSM", "1915", alpha=a, sudut=5)
        perisai(img, 780, 1080, 0.6, ORANYE, "VIJ", "1928", alpha=a, sudut=-5)
        se.panel(img, (90, 420, 990, 760), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 495), "Tiap PSM lawan Persija,", 46, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 590), "dua klub", 70, (170, 30, 20), nama_font="caption", alpha=c.p(0.1, 0.16) * a)
        se.teks(d, (540, 685), "yang lebih tua dari negaranya", 42, TINTA, nama_font="judul",
                alpha=c.p(0.2, 0.26) * a)
        bola(d, 540, 1100, 40, putar=c.t * 3, alpha=a)
    b = c.p(0.62, 0.7)
    if b > 0:
        m = maskot()
        if m is not None:
            loncat = abs(math.sin(c.t * 5)) * 18
            se.tempel(img, m, b, (540 - m.width // 2, int(560 - loncat)))
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        sk = back_out((c.t / c.d - 0.62) / 0.1)
        w2 = 380 * sk
        dl.rounded_rectangle((540 - w2, 960, 540 + w2, 1090), 40, fill=(200, 52, 44, 245))
        dl.text((540, 1025), "NGOMONGIN SEJARAH", font=se.font("caption", int(56 * sk) + 1), fill=PUTIH, anchor="mm")
        dl.text((540, 1160), "Follow buat cerita berikutnya", font=se.font("ui", 42), fill=PUTIH, anchor="mm",
                stroke_width=4, stroke_fill=(0, 0, 0))
        se.tempel(img, lap, b)
    return img


ADEGAN = [
    Adegan("hook", "Dua klub ini lebih tua dari Indonesia. Sabtu kemarin, PSM Makassar lawan Persija, imbang satu-satu. Tapi salah satunya punya nama yang diam-diam melawan Belanda.",
           a_hook, transisi=False),
    Adegan("psm", "Mulai dari Makassar. Dua November sembilan belas lima belas, lahir Makassaarsche Voetbalbond. Namanya masih Belanda. Inilah cikal bakal PSM, yang dianggap klub tertua yang masih ada.",
           a_psm),
    Adegan("belanda", "Zaman itu, liga resmi di Hindia Belanda diatur bond milik orang Belanda. Pemuda pribumi merasa dianaktirikan.",
           a_belanda),
    Adegan("vij", "Di Batavia, sebulan setelah Sumpah Pemuda, dua puluh delapan November sembilan belas dua puluh delapan, mereka bikin klub sendiri. Lapangannya dibangun sendiri, dibantu Husni Thamrin, habis dua ribu gulden.",
           a_vij),
    Adegan("soeratin", "Tapi ini belum seberapa. Di Yogyakarta, insinyur lulusan Jerman, Soeratin, rela keluar dari perusahaan Belanda, demi menyatukan klub pribumi.",
           a_soeratin),
    Adegan("pssi", "Rapatnya diam-diam, biar nggak dicurigai polisi Belanda. Sembilan belas April sembilan belas tiga puluh, tujuh bond di Jawa mendirikan PSSI. Salah satunya, klub Batavia tadi.",
           a_pssi),
    Adegan("juara", "Setahun kemudian, klub ini juara kompetisi PSSI pertama. Terus, apa yang berani dari namanya?",
           a_juara),
    Adegan("nama", "Namanya, Voetbalbond Indonesia Jacatra. Pakai kata Indonesia, padahal negaranya belum ada. Dan pakai Jacatra, bukan Batavia, nama yang dikasih Belanda.",
           a_nama),
    Adegan("jepang", "Zaman Jepang, nama berbau Belanda dilarang. Makassaarsche Voetbalbond jadi PSM. Klub Batavia itu, belakangan jadi Persija.",
           a_jepang),
    Adegan("penutup", "Jadi tiap PSM lawan Persija, yang main itu dua klub yang lebih tua dari negaranya. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
