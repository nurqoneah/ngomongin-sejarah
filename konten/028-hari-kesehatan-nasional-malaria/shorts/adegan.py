"""Shorts ±88 detik: Kenapa 12 November jadi Hari Kesehatan Nasional? — perang lawan malaria (1733–1964).

Tren: pencarian "12 november hari apa" / "hari ayah kapan" (Google Trends ID, 12 November 2026).
Visual: semprotan DDT ke dinding gedek, nyamuk raksasa, peta Batavia & tambak pesisir, rawa berkabut
("mal'aria" = udara buruk), mikroskop Ross 1897, peta Jawa–Bali–Lampung, kalender 12 November 1959,
angka 63 juta, stempel Hari Kesehatan Nasional.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "hari-kesehatan-nasional-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "PERANG LAWAN NYAMUK"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU = (30, 80, 150)
ABU = (60, 60, 70)
HIJAU_TUA = (30, 110, 60)
COKLAT = (120, 80, 40)
KUNING = (255, 214, 10)

print("  menyiapkan peta Jawa...")
PETA = Peta(100, 120, -16, 4, 150, [], [(-7.2, 107.6, 0.35), (-7.0, 110.4, 0.4), (-7.9, 112.6, 0.4),
                                        (-7.5, 109.2, 0.3), (-5.0, 104.5, 0.3)],
            seed=28, darat=pd.SEMUA)

BATAVIA = (-6.13, 106.82)
KALASAN = (-7.77, 110.47)
LABEL = {"JAWA": (-8.3, 110.5), "SUMATRA": (-2.6, 103.0), "KALIMANTAN": (-1.5, 113.0), "BALI": (-9.5, 114.3)}
SARANG = [(-6.3, 106.4), (-6.9, 107.5), (-7.4, 108.6), (-6.9, 109.6), (-7.6, 110.3), (-7.0, 111.2), (-7.6, 111.9),
          (-7.3, 112.7), (-8.0, 113.3), (-8.2, 114.1), (-8.4, 115.2), (-5.2, 105.2), (-4.6, 104.8), (-5.5, 104.3),
          (-6.6, 105.8), (-8.1, 112.3)]

print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 28, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (20, 14, 8), 0.6)


def _gedek(w, h, seed=4):
    """Tekstur dinding anyaman bambu (gedek)."""
    img = Image.new("RGBA", (w, h), (190, 150, 95, 255))
    d = ImageDraw.Draw(img)
    rng = random.Random(seed)
    sel = 44
    for j in range(h // sel + 1):
        for i in range(w // sel + 1):
            x0, y0 = i * sel, j * sel
            dasar = (205, 165, 105) if (i + j) % 2 else (175, 135, 82)
            k = rng.uniform(0.92, 1.05)
            dasar = tuple(int(v * k) for v in dasar)
            d.rectangle((x0, y0, x0 + sel, y0 + sel), fill=dasar + (255,))
            for n in range(1, 4):
                if (i + j) % 2:
                    yy = y0 + n * sel / 4
                    d.line((x0 + 2, yy, x0 + sel - 2, yy), fill=(140, 100, 55, 255), width=2)
                else:
                    xx = x0 + n * sel / 4
                    d.line((xx, y0 + 2, xx, y0 + sel - 2), fill=(140, 100, 55, 255), width=2)
            d.rectangle((x0, y0, x0 + sel, y0 + sel), outline=(110, 75, 40, 255), width=2)
    return img


GEDEK = _gedek(W, 520)


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


def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def skala_muncul(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


def nyamuk(d, x, y, s=1.0, alpha=1.0, t=0.0, arah=1, warna=(55, 42, 35)):
    """Nyamuk ilustrasi. arah=1 menghadap kanan, -1 kiri."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    k = 0.55 + 0.45 * abs(math.sin(t * 38 + x * 0.01))

    def P(px, py):
        return (x + arah * px * s, y + py * s)

    # kaki
    for i, (bx, ex, ey) in enumerate([(-6, -60, 70), (6, -10, 85), (16, 50, 75)]):
        mid = P(bx + (ex - bx) * 0.4, 30)
        d.line([P(bx, 8), mid, P(ex, ey)], fill=(40, 30, 25, a), width=max(2, int(3 * s)))
    # sayap
    sayap = (200, 225, 240, int(a * 0.55))
    xa, ya = P(-5, -6)
    xb, yb = P(70, -6 - 55 * k)
    d.ellipse((min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb)), fill=sayap, outline=(90, 110, 130, a), width=2)
    xa, ya = P(-15, -4)
    xb, yb = P(50, -4 - 40 * k)
    d.ellipse((min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb)), fill=sayap, outline=(90, 110, 130, a), width=2)
    # perut panjang berbintik
    xa, ya = P(-120, -10)
    xb, yb = P(-10, 12)
    d.ellipse((min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb)), fill=tuple(warna) + (a,))
    for n in range(4):
        cx, cy = P(-100 + n * 24, 0)
        r = 4 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(200, 190, 170, a))
    # dada, kepala, belalai
    xa, ya = P(-18, -18)
    xb, yb = P(28, 18)
    d.ellipse((min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb)), fill=tuple(warna) + (a,))
    xa, ya = P(26, -10)
    xb, yb = P(48, 10)
    d.ellipse((min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb)), fill=tuple(warna) + (a,))
    d.line([P(46, 2), P(110, 26)], fill=(40, 30, 25, a), width=max(2, int(4 * s)))
    d.line([P(44, -6), P(80, -40)], fill=(40, 30, 25, a), width=max(1, int(2 * s)))


def penyemprot(d, x, y, s=1.0, arah=-1, alpha=1.0):
    """Tangki semprot pompa. (x, y) = tengah tangki. Mengembalikan posisi ujung nosel."""
    a = int(255 * alpha)
    w, h = 110 * s, 220 * s
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), int(30 * s), fill=(150, 160, 150, a),
                        outline=(40, 45, 40, a), width=max(2, int(5 * s)))
    d.rectangle((x - w / 2, y - 20 * s, x + w / 2, y + 10 * s), fill=(200, 60, 40, a))
    d.text((x, y - 5 * s), "DDT", font=se.font("ui", max(10, int(26 * s))), fill=(255, 245, 230, a), anchor="mm")
    # pompa
    d.line((x, y - h / 2, x, y - h / 2 - 60 * s), fill=(40, 45, 40, a), width=max(2, int(10 * s)))
    d.line((x - 40 * s, y - h / 2 - 60 * s, x + 40 * s, y - h / 2 - 60 * s), fill=(40, 45, 40, a),
           width=max(2, int(12 * s)))
    # selang & tongkat semprot
    hx, hy = x + arah * w / 2, y + h / 2 - 30 * s
    tx, ty = x + arah * 150 * s, y + 40 * s
    d.line((hx, hy, tx, ty), fill=(30, 30, 30, a), width=max(2, int(8 * s)))
    nx, ny = x + arah * 300 * s, y - 60 * s
    d.line((tx, ty, nx, ny), fill=(90, 90, 95, a), width=max(2, int(12 * s)))
    d.polygon([(nx, ny - 10 * s), (nx + arah * 26 * s, ny - 16 * s), (nx + arah * 26 * s, ny + 16 * s), (nx, ny + 10 * s)],
              fill=(60, 60, 65, a))
    return nx + arah * 26 * s, ny


def kabut_semprot(img, nx, ny, arah, t, kuat=1.0, panjang=420, seed=1, sebar=0.55):
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    for i in range(150):
        f = (t * 0.9 + i / 150) % 1
        sudut = rng.uniform(-sebar, sebar) * f + 0.15
        jarak = f * panjang * rng.uniform(0.8, 1.1)
        x = nx + arah * jarak * math.cos(sudut)
        y = ny + jarak * math.sin(sudut)
        r = 6 + 46 * f
        d.ellipse((x - r, y - r, x + r, y + r), fill=(240, 245, 245, int(120 * (1 - f) * kuat)))
    img.alpha_composite(lap)


def kalender(img, cx, cy, bulan, tgl, alpha=1.0, s=1.0):
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    w, h = 330 * s, 350 * s
    d.rounded_rectangle((cx - w / 2 + 8, cy - h / 2 + 10, cx + w / 2 + 8, cy + h / 2 + 10), 20, fill=(0, 0, 0, 100))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 20, fill=(250, 245, 235, 255),
                        outline=(80, 60, 40, 255), width=4)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 90 * s), 20, fill=MERAH + (255,))
    d.text((cx, cy - h / 2 + 46 * s), bulan, font=se.font("ui", int(32 * s)), fill=PUTIH, anchor="mm")
    d.text((cx, cy + 50 * s), tgl, font=se.font("caption", int(160 * s)), fill=TINTA, anchor="mm")
    se.tempel(img, lap, alpha)


def stempel(img, isi, cx, cy, s, uk=76, sudut=-8, warna=(210, 30, 30), isi_penuh=False):
    if s <= 0.01:
        return
    f = se.font("caption", uk)
    lw = int(f.getlength(isi)) + 80
    lap = Image.new("RGBA", (lw, uk + 90), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    if isi_penuh:
        dl.rounded_rectangle((10, 10, lw - 10, uk + 80), 22, fill=tuple(warna) + (240,), outline=(255, 230, 160, 255),
                             width=6)
        dl.text((lw / 2, (uk + 90) / 2), isi, font=f, fill=PUTIH, anchor="mm")
    else:
        dl.rounded_rectangle((10, 10, lw - 10, uk + 80), 22, outline=tuple(warna) + (255,), width=12)
        dl.text((lw / 2, (uk + 90) / 2), isi, font=f, fill=tuple(warna) + (255,), anchor="mm")
    lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, 1.0, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


def rumah_gedek(img, cx, bawah, w, h, alpha=1.0):
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    x0, x1, y0 = int(cx - w / 2), int(cx + w / 2), int(bawah - h)
    lap.paste(GEDEK.crop((0, 0, x1 - x0, h)), (x0, y0))
    d.rectangle((x0, y0, x1, bawah), outline=(70, 45, 20, 255), width=6)
    d.polygon([(x0 - 60, y0), (cx, y0 - h * 0.55), (x1 + 60, y0)], fill=(120, 55, 35, 255), outline=(60, 30, 15, 255))
    for i in range(1, 6):
        yy = y0 - h * 0.55 * i / 6
        dx = (w / 2 + 60) * (1 - i / 6)
        d.line((cx - dx, yy, cx + dx, yy), fill=(90, 40, 25, 255), width=3)
    d.rectangle((cx - 60, bawah - 200, cx + 60, bawah), fill=(70, 45, 25, 255), outline=(40, 25, 10, 255), width=4)
    d.rectangle((x0 + 50, y0 + 60, x0 + 170, y0 + 150), fill=(40, 30, 20, 255), outline=(70, 45, 20, 255), width=5)
    se.tempel(img, lap, alpha)


# ------------------------------------------------------------------ adegan

NYAMUK_HOOK = [(200, 640, 0.0), (430, 760, 1.3), (690, 620, 2.1), (330, 880, 0.7), (560, 900, 2.9), (150, 820, 1.9)]


def a_hook(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # dinding gedek di bawah
    img.alpha_composite(GEDEK.crop((0, 0, W, 480)), (0, 860))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 1340, W, H), fill=(30, 22, 15, 255))
    # penyemprot dari kanan, kabut ke kiri
    nx, ny = penyemprot(d, 930, 1090, 1.05, arah=-1)
    kabut_semprot(img, nx, ny, -1, c.t, 1.0, panjang=640, sebar=0.7)
    d = ImageDraw.Draw(img, "RGBA")
    # nyamuk-nyamuk: terbang, lalu berjatuhan kena semprot
    for i, (x0, y0, ph) in enumerate(NYAMUK_HOOK):
        jatuh = c.p(0.25 + i * 0.06, 0.45 + i * 0.06)
        x = x0 + math.sin(c.t * 2.5 + ph) * 30
        y = y0 + math.cos(c.t * 3.1 + ph) * 20 + jatuh * 420
        nyamuk(d, x, y, 0.9, 1 - 0.7 * jatuh, c.t, 1 if i % 2 else -1)
    se.teks(d, (540, 395), "PRESIDEN NYEMPROT", 92, PUTIH, nama_font="caption", stroke=10, stroke_warna=(10, 10, 20))
    se.teks(d, (540, 505), "RUMAH WARGA?!", 116, KUNING, nama_font="caption", stroke=10,
            stroke_warna=(10, 10, 20))
    stempel(img, "12 NOVEMBER", 540, 700, back_out((c.t / c.d - 0.42) / 0.08))
    return img


def a_musuh(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out((c.t / c.d) / 0.15)
    se.glow(img, 540, 850, 380, (200, 60, 40), 0.8)
    d = ImageDraw.Draw(img, "RGBA")
    nyamuk(d, 600 + math.sin(c.t * 2) * 20, 830 + math.cos(c.t * 2.6) * 14, 3.2 * s + 0.01, 1.0, c.t, 1)
    se.teks(d, (540, 450), "MUSUHNYA KECIL BANGET", 64, (150, 30, 25), nama_font="caption", stroke=7,
            stroke_warna=(247, 236, 208), alpha=c.p(0.0, 0.06))
    se.kartu(img, 540, 1130, "Nyamuk Anopheles", "pembawa parasit malaria", BIRU, alpha=c.p(0.25, 0.33), tiang=False,
             skala=skala_muncul(c, 0.25))
    se.kartu(img, 540, 1270, "Demam tinggi · menggigil · bisa mematikan", "", MERAH, alpha=c.p(0.55, 0.63),
             tiang=False, skala=skala_muncul(c, 0.55))
    hdr(img, "Malaria")
    return img


def a_batavia(c):
    kamera = se.kamera_antara(cam(-6.6, 107.4, 0.8), cam(-6.25, 106.85, 1.7), c.p(0.0, 0.35))
    img, d = peta(kamera)
    # tambak di pesisir
    tb = c.p(0.55, 0.7)
    if tb > 0:
        rng = random.Random(9)
        for i in range(22):
            lat = -6.13 + rng.uniform(-0.03, 0.02)
            lon = 106.35 + i * 0.05 + rng.uniform(-0.01, 0.01)
            x, y = layar(kamera, (lat, lon))
            w = 30 * kamera.zoom
            d.rectangle((x - w, y - w * 0.6, x + w, y + w * 0.6), fill=(90, 140, 120, int(220 * tb)),
                        outline=(60, 40, 20, int(255 * tb)), width=3)
    bx, by = layar(kamera, BATAVIA)
    d.ellipse((bx - 16, by - 16, bx + 16, by + 16), fill=MERAH + (255,), outline=(255, 255, 255, 255), width=4)
    label(d, (bx, by + 60), "Batavia", 46, TINTA)
    # kawanan nyamuk
    k = c.p(0.15, 0.4)
    if k > 0:
        rng = random.Random(4)
        for i in range(int(40 * k)):
            ox, oy = rng.uniform(-420, 420), rng.uniform(-260, 200)
            x = bx + ox + math.sin(c.t * 3 + i) * 18
            y = by + oy + math.cos(c.t * 2.4 + i * 0.7) * 14
            nyamuk(d, x, y, 0.32, 0.9, c.t + i, 1 if i % 2 else -1)
    se.kartu(img, 540, 470, "Abad ke-18 · sejak ± 1733", "wabah demam mematikan", MERAH, alpha=c.p(0.05, 0.13),
             tiang=False, skala=skala_muncul(c, 0.05))
    se.kartu(img, 540, 1280, "Salah satu dugaan: tambak ikan", "jadi sarang nyamuk", HIJAU_TUA,
             alpha=c.p(0.58, 0.66), tiang=False, skala=skala_muncul(c, 0.58))
    b = c.p(0.33, 0.41)
    if b > 0:
        stempel(img, "“KUBURAN ORANG EROPA”", 540, 640, skala_muncul(c, 0.33, 0.08), uk=50, sudut=-4,
                warna=(30, 25, 20), isi_penuh=True)
    hdr(img, "Batavia, 1700-an")
    return img


def a_rawa(c):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line((0, y, W, y), fill=se.lerp_rgb((20, 40, 30), (55, 80, 45), y / H) + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((-200, 1050, 1280, 1500), fill=(35, 60, 50, 255))
    rng = random.Random(3)
    for i in range(70):
        x = rng.uniform(0, W)
        y0 = rng.uniform(1050, 1350)
        hh = rng.uniform(120, 300)
        d.line((x, y0, x + rng.uniform(-20, 20), y0 - hh), fill=(70, 100, 40, 255), width=5)
    # kabut "udara buruk"
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    for i in range(60):
        x = (rng.uniform(-200, W + 200) + c.t * rng.uniform(15, 45)) % (W + 400) - 200
        y = rng.uniform(750, 1350)
        rr = rng.uniform(100, 220)
        dl.ellipse((x - rr, y - rr * 0.5, x + rr, y + rr * 0.5), fill=(150, 190, 110, 40))
    img.alpha_composite(lap)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 430), "TAPI BAGIAN PALING GILA…", 58, PUTIH, nama_font="caption", stroke=7,
            stroke_warna=(10, 10, 20), alpha=c.p(0.0, 0.05) * (1 - c.p(0.3, 0.35)))
    a = c.p(0.36, 0.42)
    s = back_out((c.t / c.d - 0.36) / 0.1)
    se.teks(d, (540, 560), "MAL' ARIA", int(150 * s) + 1, KUNING, nama_font="caption", stroke=10,
            stroke_warna=(10, 10, 20), alpha=a)
    se.teks(d, (540, 690), "= udara buruk (bahasa Italia)", 52, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(10, 10, 20), alpha=c.p(0.5, 0.56))
    se.kartu(img, 540, 1260, "Dikira dari bau busuk rawa", "bukan dari nyamuk", ABU, alpha=c.p(0.72, 0.8),
             tiang=False, skala=skala_muncul(c, 0.72))
    hdr(img, "Salah sangka ratusan tahun")
    return img


def mikroskop(d, x, y, s=1.0):
    c1, c2 = (50, 50, 60, 255), (20, 20, 25, 255)
    d.rounded_rectangle((x - 140 * s, y + 160 * s, x + 140 * s, y + 210 * s), 14, fill=c1, outline=c2, width=4)
    d.arc((x - 40 * s, y - 120 * s, x + 200 * s, y + 200 * s), 120, 260, fill=c1, width=int(40 * s))
    d.rectangle((x - 120 * s, y + 20 * s, x + 80 * s, y + 45 * s), fill=c1, outline=c2, width=3)
    tb = [(x - 70 * s, y - 230 * s), (x - 20 * s, y - 250 * s), (x + 10 * s, y - 40 * s), (x - 40 * s, y - 30 * s)]
    d.polygon(tb, fill=(170, 140, 70, 255), outline=c2)
    d.rectangle((x - 40 * s, y - 40 * s, x + 10 * s, y + 5 * s), fill=c1)


def a_ross(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out((c.t / c.d) / 0.12)
    se.teks(d, (540, 450), "1897", int(150 * s) + 1, (150, 30, 25), nama_font="caption", stroke=8,
            stroke_warna=(247, 236, 208))
    mikroskop(d, 300, 960, 1.2)
    # lingkaran pembesaran
    a = c.p(0.2, 0.3)
    if a > 0:
        cx, cy, r = 720, 880, 240
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.line((360, 720, cx - r * 0.8, cy - r * 0.5), fill=(80, 60, 40, 200), width=4)
        dl.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(235, 225, 200, 255), outline=(60, 45, 30, 255), width=10)
        dl.ellipse((cx - 150, cy - 80, cx + 150, cy + 100), fill=(220, 170, 150, 255), outline=(150, 90, 70, 255), width=5)
        rng = random.Random(2)
        n = int(14 * c.p(0.3, 0.6))
        for i in range(n):
            px, py = cx + rng.uniform(-110, 110), cy + rng.uniform(-50, 70)
            rr = rng.uniform(10, 18)
            dl.ellipse((px - rr, py - rr, px + rr, py + rr), fill=(190, 30, 40, 255), outline=(110, 10, 20, 255), width=3)
        se.tempel(img, lap, a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (cx, cy + r + 40), "perut nyamuk", 34, TINTA, alpha=a)
    se.kartu(img, 540, 590, "Ronald Ross · dokter Inggris", "Nobel Kedokteran 1902", BIRU, alpha=c.p(0.08, 0.16),
             tiang=False, skala=skala_muncul(c, 0.08))
    se.kartu(img, 540, 1290, "Pelakunya: gigitan nyamuk!", "", MERAH, alpha=c.p(0.68, 0.76), tiang=False,
             skala=skala_muncul(c, 0.68))
    hdr(img, "Akhirnya ketahuan")
    return img


def a_dinas(c):
    kamera = Kamera(*cam(-6.8, 109.6, 0.6))
    img, d = peta(kamera)
    for nama, ll in LABEL.items():
        if nama in ("KALIMANTAN",):
            continue
        label(d, layar(kamera, ll), nama, 38, TINTA, 0.85)
    k = c.p(0.0, 0.3)
    for i, ll in enumerate(SARANG[:int(len(SARANG) * k + 0.999)]):
        x, y = layar(kamera, ll)
        nyamuk(d, x + math.sin(c.t * 3 + i) * 8, y, 0.45, 0.95, c.t + i, 1 if i % 2 else -1)
    se.kartu(img, 540, 470, "1959 · Dinas Pembasmian Malaria", "dibantu WHO & Amerika (USAID)", HIJAU_TUA,
             alpha=c.p(0.05, 0.13), tiang=False, skala=skala_muncul(c, 0.05))
    b = c.p(0.75, 0.82)
    if b > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((250, 1060, 830, 1330), 30, fill=(247, 236, 208, 240), outline=(200, 60, 40, 255), width=6)
        nx, ny = penyemprot(dl, 380, 1210, 0.6, arah=1)
        dl.text((640, 1195), "DDT", font=se.font("caption", 110), fill=(200, 40, 30, 255), anchor="mm")
        se.tempel(img, lap, b)
        kabut_semprot(img, nx, ny, 1, c.t, b * 0.8, panjang=160, sebar=0.4)
    hdr(img, "Setelah merdeka")
    return img


def a_kalasan(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    kalender(img, 270, 560, "NOVEMBER 1959", "12", c.p(0.0, 0.06), skala_muncul(c, 0.0) * 0.72)
    se.kartu(img, 740, 520, "Kalasan, Yogyakarta", "rumah seorang guru SD", COKLAT, alpha=c.p(0.18, 0.26),
             tiang=False, skala=skala_muncul(c, 0.18))
    rumah_gedek(img, 540, 1310, 700, 380, alpha=c.p(0.1, 0.2))
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.55, 0.62)
    if a > 0:
        nx, ny = penyemprot(d, 960, 1150, 0.9, arah=-1, alpha=a)
        kabut_semprot(img, nx, ny, -1, c.t, a, panjang=420, sebar=0.5)
        se.kartu(img, 760, 680, "Presiden Sukarno", "nyemprot DDT sendiri", MERAH, alpha=a, tiang=False,
                 skala=skala_muncul(c, 0.55))
    hdr(img, "Hari itu")
    return img


def a_massal(c):
    kamera = Kamera(*cam(-6.8, 109.6, 0.6))
    img, d = peta(kamera)
    for nama, ll in LABEL.items():
        if nama in ("KALIMANTAN",):
            continue
        label(d, layar(kamera, ll), nama, 38, TINTA, 0.85)
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    rng = random.Random(12)
    titik = []
    for ll in SARANG:
        for j in range(4):
            titik.append((ll[0] + rng.gauss(0, 0.25), ll[1] + rng.gauss(0, 0.35)))
    titik.sort(key=lambda p: p[1] if p[1] > 106 else 106 + (106 - p[1]) * 0.1 + 9)
    n = int(len(titik) * c.p(0.05, 0.85))
    for i, ll in enumerate(titik[:n]):
        x, y = layar(kamera, ll)
        r = 18 + 6 * math.sin(c.t * 4 + i)
        dl.ellipse((x - r, y - r, x + r, y + r), fill=(245, 250, 250, 150))
        dl.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(30, 110, 60, 230))
    img.alpha_composite(lap)
    d = ImageDraw.Draw(img, "RGBA")
    for i, ll in enumerate(SARANG):
        a = 1 - c.p(0.1 + i * 0.04, 0.2 + i * 0.04)
        x, y = layar(kamera, ll)
        nyamuk(d, x, y - 30, 0.3, a * 0.9, c.t + i)
    label(d, layar(kamera, (-3.9, 105.3)), "Lampung", 36, (120, 20, 15), c.p(0.6, 0.7), "caption")
    se.kartu(img, 540, 470, "Ribuan petugas", "rumah demi rumah disemprot", HIJAU_TUA, alpha=c.p(0.02, 0.1),
             tiang=False, skala=skala_muncul(c, 0.02))
    se.kartu(img, 540, 1280, "Jawa · Bali · Lampung", "", BIRU, alpha=c.p(0.45, 0.53), tiang=False,
             skala=skala_muncul(c, 0.45))
    hdr(img, "1959 – 1964")
    return img


def a_hkn(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 420), "INI JAWABANNYA", 60, PUTIH, nama_font="caption", stroke=7, stroke_warna=(10, 10, 20),
            alpha=c.p(0.0, 0.05))
    juta = int(round(63 * c.p(0.05, 0.3)))
    se.teks(d, (540, 560), f"± {juta} JUTA", 130, KUNING, nama_font="caption", stroke=9, stroke_warna=(10, 10, 20),
            alpha=c.p(0.03, 0.1))
    se.teks(d, (540, 670), "penduduk terlindungi dari malaria", 44, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(10, 10, 20), alpha=c.p(0.1, 0.18))
    stempel(img, "HARI KESEHATAN NASIONAL", 540, 860, skala_muncul(c, 0.5, 0.08), uk=56, sudut=-4,
            warna=(200, 52, 44), isi_penuh=True)
    kalender(img, 330, 1150, "NOVEMBER 1964", "12", c.p(0.62, 0.7), skala_muncul(c, 0.62) * 0.7)
    se.kartu(img, 760, 1150, "Peringatan pertama", "sejak 1964", HIJAU_TUA, alpha=c.p(0.66, 0.74), tiang=False,
             skala=skala_muncul(c, 0.66))
    hdr(img, "Kenapa 12 November")
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
    se.tint(img, (10, 6, 0), 0.3)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.6, 0.66))
    if a > 0:
        se.panel(img, (90, 440, 990, 1180), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 530), "Nyamuknya belum kalah", 54, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 610), "± 706 ribu kasus malaria (2025)", 40, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 670), "lebih dari 95% di Papua", 36, (90, 70, 50), alpha=a)
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        nyamuk(dl, 560, 820, 1.4, 1.0, c.t)
        se.tempel(img, lap, a)
        b2 = c.p(0.3, 0.38) * a
        if b2 > 0:
            d = ImageDraw.Draw(img, "RGBA")
            se.teks(d, (540, 1000), "12 November =", 46, TINTA, nama_font="judul", alpha=b2)
            se.teks(d, (540, 1075), "hari mulai perang lawan nyamuk", 46, (170, 30, 20), nama_font="caption",
                    alpha=b2)
    b = c.p(0.64, 0.72)
    if b > 0:
        m = maskot()
        if m is not None:
            loncat = abs(math.sin(c.t * 5)) * 18
            se.tempel(img, m, b, (540 - m.width // 2, int(560 - loncat)))
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        sk = back_out((c.t / c.d - 0.64) / 0.1)
        w2 = 380 * sk
        dl.rounded_rectangle((540 - w2, 960, 540 + w2, 1090), 40, fill=(200, 52, 44, 245))
        dl.text((540, 1025), "NGOMONGIN SEJARAH", font=se.font("caption", int(56 * sk) + 1), fill=PUTIH, anchor="mm")
        dl.text((540, 1160), "Follow buat cerita berikutnya", font=se.font("ui", 42), fill=PUTIH, anchor="mm",
                stroke_width=4, stroke_fill=(0, 0, 0))
        se.tempel(img, lap, b)
    return img


ADEGAN = [
    Adegan("hook", "Presiden pernah nyemprot rumah warga. Beneran. Lagi rame nyari, dua belas November hari apa? "
                   "Jawabannya, berawal dari semprotan ini. Kok bisa?", a_hook, transisi=False),
    Adegan("musuh", "Musuhnya kecil banget. Nyamuk, pembawa malaria. Demam, menggigil, bisa bikin mati.", a_musuh),
    Adegan("batavia", "Abad kedelapan belas, wabah demam mematikan menyerang Batavia. "
                      "Kota ini sampai dijuluki kuburan orang Eropa. "
                      "Salah satu dugaannya, tambak di pesisir jadi sarang nyamuk.", a_batavia),
    Adegan("rawa", "Tapi bagian paling gila-nya: dulu, nggak ada yang tahu ini dari nyamuk. "
                   "Malaria itu artinya udara buruk. Orang kira, sumbernya bau rawa.", a_rawa),
    Adegan("ross", "Tahun delapan belas sembilan puluh tujuh, dokter Ronald Ross nemu parasit malaria "
                   "di perut nyamuk. Ketahuan deh, pelakunya.", a_ross),
    Adegan("dinas", "Setelah merdeka, pemerintah bentuk Dinas Pembasmian Malaria, "
                    "dibantu WHO dan Amerika. Senjatanya, DDT.", a_dinas),
    Adegan("kalasan", "Dua belas November sembilan belas lima puluh sembilan, di Kalasan, Yogyakarta. "
                      "Bung Karno mampir ke rumah guru SD, lalu nyemprot DDT sendiri ke dinding bambunya.",
           a_kalasan),
    Adegan("massal", "Habis itu, ribuan petugas nyemprot rumah demi rumah. Jawa, Bali, sampai Lampung.", a_massal),
    Adegan("hkn", "Nah, ini jawabannya. Lima tahun kemudian, sekitar enam puluh tiga juta penduduk terlindungi. "
                  "Keberhasilan itu diperingati tiap dua belas November, sebagai Hari Kesehatan Nasional.", a_hkn),
    Adegan("penutup", "Tapi nyamuknya belum kalah. Tahun lalu masih ada ratusan ribu kasus, kebanyakan di Papua. "
                      "Dua belas November itu, hari kita mulai perang lawan nyamuk. "
                      "Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
