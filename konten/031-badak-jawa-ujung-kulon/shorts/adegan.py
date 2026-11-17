"""Shorts ±88 detik: Badak jawa — dulu diburu berhadiah, kini cuma tersisa di Ujung Kulon. Kenapa di sana?

Tren: wacana relokasi badak jawa dari Ujung Kulon ke Alas Purwo (14–17 November 2026), trending Google ID.
Visual: poster sayembara + bidikan merah, peta sebaran Asia, sawah diinjak badak, penghitung 526 badak,
peta Jawa dengan titik yang padam, sensus 1967 (25 ekor), Vietnam 2010, Krakatau 1883 + tsunami ke Ujung Kulon,
hutan tumbuh lagi, panah wacana ke Alas Purwo, penutup maskot.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Peta, back_out, clamp, lerp

NAMA_FILE = "badak-jawa-ujung-kulon-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "BADAK JAWA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KUNING = (255, 214, 10)
GELAP = (10, 10, 20)
KREM = (247, 236, 208)
KREM_LABEL = (240, 225, 190)
KULIT = (78, 72, 66)
EMAS = (235, 185, 50)
HIJAU_TUA = (30, 110, 60)
HIJAU_DAUN = (60, 130, 60)
BIRU = (30, 80, 150)
COKLAT = (120, 80, 40)
MERAH_BIDIK = (230, 30, 25)

# ------------------------------------------------------------------ peta

print("  menyiapkan peta Asia...")
ASIA = Peta(78, 122, -24, 50, 26, [], [(25, 93, 2.5), (20, 98, 3), (16, 104, 2), (0, 101, 1.2), (-7.3, 110, 0.6)],
            seed=31, darat=pd.SEMUA)

print("  menyiapkan peta Jawa...")
JAWA = Peta(103.5, 116.5, -18, 4, 100, [], [(-7.2, 107.6, 0.35), (-7.0, 110.4, 0.4), (-7.9, 112.9, 0.35),
                                              (-0.5, 101.0, 0.5), (-2, 114, 1.0)],
            seed=32, darat=pd.SEMUA)

JAWA_BARAT = [(-5.93, 106.0), (-6.0, 106.15), (-5.95, 106.35), (-6.05, 106.6), (-6.1, 106.8), (-6.0, 107.3),
              (-8.0, 107.3), (-7.4, 106.9), (-7.0, 106.53), (-6.95, 106.0), (-6.85, 105.55), (-6.8, 105.25),
              (-6.72, 105.2), (-6.62, 105.38), (-6.63, 105.6), (-6.48, 105.65), (-6.53, 105.72), (-6.38, 105.83),
              (-6.3, 105.83), (-6.05, 105.88)]
SUMATRA_SEL = [(-4.5, 103.6), (-5.19, 103.93), (-5.6, 104.25), (-5.92, 104.58), (-5.75, 104.72), (-5.5, 104.62),
               (-5.55, 104.85), (-5.8, 105.05), (-5.95, 105.2), (-5.75, 105.22), (-5.47, 105.27), (-5.55, 105.42),
               (-5.73, 105.6), (-5.87, 105.75), (-5.7, 105.85), (-5.3, 105.85), (-4.5, 105.9)]
PULAU_KECIL = [
    [(-5.9, 105.45), (-5.93, 105.51), (-5.97, 105.48), (-5.94, 105.43)],
    [(-5.93, 105.83), (-5.96, 105.88), (-5.98, 105.84)],
    [(-6.55, 105.15), (-6.6, 105.27), (-6.65, 105.22), (-6.62, 105.12)],
]
print("  menyiapkan peta Selat Sunda...")
SUNDA = Peta(103.6, 107.2, -7.9, -4.6, 900, [], [(-6.5, 106.3, 0.35), (-7.0, 106.9, 0.4), (-5.2, 104.6, 0.4),
                                                 (-5.4, 105.0, 0.3), (-4.9, 105.4, 0.4), (-6.77, 105.32, 0.06)],
             seed=8, darat=[JAWA_BARAT, SUMATRA_SEL] + PULAU_KECIL)

KRAKATAU = (-6.10, 105.42)
UJUNG_KULON = (-6.74, 105.40)
TASIK = (-7.73, 108.05)
ALAS_PURWO = (-8.62, 114.35)
CAT_TIEN = (11.43, 107.4)

print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 31, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (20, 10, 6), 0.62)


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


def stempel(img, isi, cx, cy, s, uk=76, sudut=-8, warna=(210, 30, 30)):
    if s <= 0.01:
        return
    f = se.font("caption", uk)
    lw = int(f.getlength(isi)) + 80
    lap = Image.new("RGBA", (lw, uk + 90), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((10, 10, lw - 10, uk + 80), 22, fill=(247, 236, 208, 210), outline=tuple(warna) + (255,),
                         width=12)
    dl.text((lw / 2, (uk + 90) / 2), isi, font=f, fill=tuple(warna) + (255,), anchor="mm")
    lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, 1.0, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


def kalender(img, cx, cy, bulan, tgl, tahun="", alpha=1.0, s=1.0):
    if alpha <= 0.01 or s <= 0.2:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    w, h = 300 * s, 330 * s
    d.rounded_rectangle((cx - w / 2 + 8, cy - h / 2 + 10, cx + w / 2 + 8, cy + h / 2 + 10), int(18 * s), fill=(0, 0, 0, 100))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(18 * s), fill=(250, 245, 235, 255),
                        outline=(80, 60, 40, 255), width=4)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 84 * s), int(18 * s), fill=MERAH + (255,))
    d.text((cx, cy - h / 2 + 43 * s), bulan, font=se.font("ui", int(32 * s)), fill=PUTIH, anchor="mm")
    d.text((cx, cy + 20 * s), tgl, font=se.font("caption", int(140 * s)), fill=TINTA, anchor="mm")
    if tahun:
        d.text((cx, cy + h / 2 - 34 * s), tahun, font=se.font("ui", int(34 * s)), fill=(150, 30, 25), anchor="mm")
    se.tempel(img, lap, alpha)


def badak(d, x, y, s=1.0, warna=KULIT, alpha=1.0, arah=1, langkah=0.0):
    """Siluet badak bercula satu tampak samping; (x, y) = tanah di bawah badan. arah 1 = menghadap kanan."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    gelap = tuple(max(0, v - 30) for v in warna) + (a,)

    def X(dx):
        return x + arah * dx * s

    # kaki
    for i, lx in enumerate((-85, -48, 52, 88)):
        ayun = math.sin(langkah + i * 1.7) * 9 * s
        x0, x1 = sorted((X(lx) - 15 * s + ayun, X(lx) + 15 * s + ayun))
        if s >= 0.4:
            d.rounded_rectangle((x0, y - 85 * s, x1, y), int(6 * s) + 1, fill=gelap if i % 2 else c)
        else:
            d.rectangle((x0, y - 85 * s, x1, y), fill=gelap if i % 2 else c)
    # ekor
    d.line((X(-122), y - 150 * s, X(-138), y - 105 * s), fill=c, width=max(2, int(6 * s)))
    # badan
    bx0, bx1 = sorted((X(-130), X(118)))
    d.ellipse((bx0, y - 200 * s, bx1, y - 62 * s), fill=c)
    # kepala
    pts = [(X(95), y - 178 * s), (X(160), y - 150 * s), (X(205), y - 112 * s), (X(212), y - 86 * s),
           (X(180), y - 74 * s), (X(110), y - 88 * s)]
    d.polygon(pts, fill=c)
    # cula
    d.polygon([(X(182), y - 118 * s), (X(196), y - 168 * s), (X(204), y - 112 * s)], fill=c)
    # telinga
    d.polygon([(X(112), y - 170 * s), (X(104), y - 208 * s), (X(130), y - 176 * s)], fill=c)
    # lipatan kulit ("baju zirah")
    if s > 0.3:
        for dx in (-70, 40, 98):
            d.arc((X(dx) - 30 * s, y - 196 * s, X(dx) + 30 * s, y - 70 * s), 250 if arah > 0 else -70,
                  110 if arah > 0 else 70, fill=gelap, width=max(2, int(5 * s)))
        ex = X(150)
        d.ellipse((ex - 5 * s, y - 140 * s, ex + 5 * s, y - 130 * s), fill=(20, 15, 10, a))


def bidik(d, x, y, r, alpha=1.0, warna=MERAH_BIDIK):
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    d.ellipse((x - r, y - r, x + r, y + r), outline=c, width=max(3, int(r * 0.07)))
    d.ellipse((x - r * 0.45, y - r * 0.45, x + r * 0.45, y + r * 0.45), outline=c, width=max(2, int(r * 0.04)))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        d.line((x + dx * r * 0.25, y + dy * r * 0.25, x + dx * r * 1.3, y + dy * r * 1.3), fill=c,
               width=max(3, int(r * 0.06)))


def koin(d, x, y, r, alpha=1.0):
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=EMAS + (a,), outline=(130, 90, 10, a), width=max(2, int(r * 0.12)))
    d.ellipse((x - r * 0.65, y - r * 0.65, x + r * 0.65, y + r * 0.65), outline=(170, 120, 20, a),
              width=max(1, int(r * 0.08)))


def rumah(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.rectangle((x - 22 * s, y - 26 * s, x + 22 * s, y), fill=(150, 110, 60, a), outline=(60, 40, 20, a), width=2)
    d.polygon([(x - 32 * s, y - 24 * s), (x, y - 52 * s), (x + 32 * s, y - 24 * s)], fill=(110, 60, 30, a),
              outline=(60, 40, 20, a))


def pohon(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.rectangle((x - 4 * s, y - 18 * s, x + 4 * s, y), fill=(90, 60, 30, a))
    d.ellipse((x - 22 * s, y - 56 * s, x + 22 * s, y - 14 * s), fill=HIJAU_DAUN + (a,), outline=(25, 70, 30, a),
              width=2)


def cincin(d, x, y, r, warna, alpha, tebal=8):
    if alpha <= 0.01 or r <= 1:
        return
    d.ellipse((x - r, y - r, x + r, y + r), outline=tuple(warna) + (int(255 * alpha),), width=tebal)


def gunung_peta(img, x, y, r, kuat=1.0):
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((x - r * 1.35, y - r * 0.9, x + r * 1.35, y + r * 0.9), fill=(62, 52, 48, 255), outline=(25, 20, 18, 255),
              width=4)
    d.polygon([(x - r * 0.9, y + r * 0.2), (x, y - r * 1.25), (x + r * 0.9, y + r * 0.2)], fill=(92, 76, 66, 255),
              outline=(30, 24, 20, 255))
    for i in range(4):
        ax = x + (i - 1.5) * r * 0.22
        d.line((x, y - r * 1.15, ax, y + r * 0.1), fill=(255, 110, 30, int(200 * kuat)), width=5)
    se.glow(img, x, y - r * 1.2, r * 1.1, (255, 120, 40), 2.2 * kuat)


def asap(img, x, y, t, kuat=1.0, tinggi=500, lebar=1.0, seed=1, warna=(90, 85, 80)):
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    for i in range(40):
        fase = (rng.random() + t * rng.uniform(0.15, 0.3)) % 1.0
        yy = y - fase * tinggi
        xx = x + math.sin(fase * 6 + i) * 30 * lebar + rng.uniform(-40, 40) * lebar * fase
        r = (24 + fase * 110) * lebar * rng.uniform(0.7, 1.2)
        a = int(190 * kuat * (1 - fase * 0.7))
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=tuple(warna) + (a,))
    img.alpha_composite(lap)


def poster(img, cx, cy, s=1.0, sudut=-3, alpha=1.0, langkah=0.0):
    """Poster sayembara kertas tua dengan siluet badak."""
    if alpha <= 0.01:
        return
    pw, ph = int(760 * s), int(640 * s)
    lap = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rectangle((26, 30, pw + 26, ph + 30), fill=(0, 0, 0, 120))
    d.rectangle((14, 14, pw + 14, ph + 14), fill=(236, 214, 165, 255), outline=(110, 75, 35, 255), width=8)
    d.rectangle((34, 34, pw - 6, ph - 6), outline=(140, 100, 50, 255), width=3)
    d.text((pw / 2 + 14, 90 * s), "SAYEMBARA", font=se.font("caption", int(84 * s)), fill=(120, 30, 20), anchor="mm")
    d.line((80 * s, 145 * s, pw - 50 * s, 145 * s), fill=(120, 80, 40, 255), width=4)
    badak(d, pw / 2 - 10 * s, ph - 110 * s, 1.35 * s, (60, 50, 42), 1.0, langkah=langkah)
    d.text((pw / 2 + 14, ph - 55 * s), "HADIAH BAGI PEMBUNUHNYA", font=se.font("ui", int(36 * s)),
           fill=(90, 50, 25), anchor="mm")
    lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 900, 520, (180, 40, 20), 1.2)
    poster(img, 540, 990, 0.95, sudut=-3, langkah=c.t * 3)
    d = ImageDraw.Draw(img, "RGBA")
    # bidikan merah di badak (sudah ada di frame pertama)
    r = 120 + 10 * math.sin(c.t * 7)
    bidik(d, 645, 1030, r, 0.95)
    # koin berjatuhan
    rng = random.Random(4)
    for i in range(14):
        fase = (rng.random() + c.t * rng.uniform(0.25, 0.45)) % 1
        x = rng.uniform(90, 990)
        y = lerp(560, 1320, fase)
        koin(d, x, y, rng.uniform(18, 30), 0.9 * (1 - fase * 0.5))
    se.teks(d, (540, 410), "DULU DIBAYAR", 112, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 535), "BUAT DIBUNUH!", 118, KUNING, nama_font="caption", stroke=10, stroke_warna=GELAP)
    stempel(img, "JAWA, 1747", 850, 1225, 0.75 if c.p(0, 0.05) <= 0 else max(0.75, skala_muncul(c, 0.0, 0.08) * 0.75),
            uk=56, sudut=-9)
    se.kartu(img, 540, 1335, "Badak jawa mau dipindah?", "wacana Ujung Kulon → Alas Purwo", HIJAU_TUA,
             alpha=c.p(0.3, 0.38), tiang=False, skala=skala_muncul(c, 0.3))
    a = c.p(0.55, 0.62)
    if a > 0:
        se.panel(img, (90, 800, 990, 1010), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 870), "Kenapa cuma tersisa", 56, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 945), "di SATU ujung pulau?", 56, (170, 30, 20), nama_font="caption", alpha=c.p(0.6, 0.66))
    return img


SEBARAN = [("India", (24.5, 90.5), 2.6), ("Myanmar", (19.5, 95.5), 2.6), ("Thailand", (15.5, 100.5), 2.4),
           ("Vietnam", (13.0, 106.5), 2.4), ("Semenanjung", (5.0, 101.5), 1.8), ("Sumatra", (-1.5, 102.5), 2.2),
           ("Jawa", (-7.2, 108.5), 2.0)]


def a_sebaran(c):
    kamera = se.kamera_antara(cam(ASIA, 10.0, 99.5, 1.0), cam(ASIA, 8.0, 100.5, 1.08), c.p(0, 1))
    img = se.render_peta(ASIA, kamera)
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    for i, (nama, ll, rr) in enumerate(SEBARAN):
        a = c.p(0.05 + i * 0.07, 0.12 + i * 0.07)
        if a <= 0:
            continue
        x, y = layar(ASIA, kamera, ll)
        r = rr * ASIA.skala * kamera.zoom * back_out(a)
        dl.ellipse((x - r, y - r * 0.75, x + r, y + r * 0.75), fill=(200, 60, 40, int(110 * a)),
                   outline=(150, 30, 20, int(200 * a)), width=4)
    se.tempel(img, lap)
    d = ImageDraw.Draw(img, "RGBA")
    for i, (nama, ll, rr) in enumerate(SEBARAN):
        a = c.p(0.05 + i * 0.07, 0.12 + i * 0.07)
        if a <= 0:
            continue
        x, y = layar(ASIA, kamera, ll)
        badak(d, x, y + 20, 0.22, (50, 40, 35), a, arah=1 if i % 2 else -1, langkah=c.t * 4 + i)
        label(d, (x, y + 52), nama, 34, alpha=a)
    se.kartu(img, 540, 470, "Rumah badak jawa, dulu", "dari India sampai Pulau Jawa", MERAH, alpha=c.p(0.0, 0.08),
             tiang=False, skala=skala_muncul(c, 0.0))
    a = c.p(0.7, 0.78)
    if a > 0:
        x, y = layar(ASIA, kamera, (-7.2, 108.5))
        se.kartu(img, min(800, x + 40), y - 150, "Di Jawa: dekat kampung", "", COKLAT, alpha=a, tiang=False,
                 skala=skala_muncul(c, 0.7))
    hdr(img, "Bercula satu, menjelajah Asia")
    return img


def a_hama(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # sawah / kebun
    d.rectangle((60, 780, 1020, 1290), fill=(120, 150, 70, 255), outline=(70, 90, 40, 255), width=5)
    for row in range(8):
        y = 820 + row * 60
        for k in range(18):
            x = 90 + k * 52 + (row % 2) * 26
            d.line((x, y, x - 8, y - 26), fill=(40, 110, 40, 255), width=4)
            d.line((x, y, x + 8, y - 26), fill=(40, 110, 40, 255), width=4)
    # badak berjalan dan menginjak tanaman
    bx = lerp(-150, 760, c.p(0.0, 0.55))
    d.rectangle((60, 1010, max(60, bx - 60), 1110), fill=(140, 110, 70, 255))
    badak(d, bx, 1150, 1.15, KULIT, 1.0, langkah=c.t * 6)
    a = c.p(0.2, 0.26)
    if a > 0:
        se.teks(d, (540, 690), "HAMA?!", 120, (190, 30, 20), nama_font="caption", stroke=8, stroke_warna=KREM, alpha=a)
    a2 = c.p(0.55, 0.63)
    if a2 > 0:
        poster(img, 540, 900, 0.82 * skala_muncul(c, 0.55), sudut=4, alpha=a2, langkah=c.t * 3)
        d = ImageDraw.Draw(img, "RGBA")
        for i in range(5):
            koin(d, 250 + i * 145, 1250 - 10 * math.sin(c.t * 5 + i), 34, c.p(0.68 + i * 0.03, 0.72 + i * 0.03))
        se.kartu(img, 540, 470, "Sayembara pemerintah kolonial", "bunuh badak = dapat hadiah", (110, 30, 20),
                 alpha=c.p(0.6, 0.68), tiang=False, skala=skala_muncul(c, 0.6))
    hdr(img, "Dianggap hama")
    return img


def a_angka(c):
    img = LATAR_GELAP.copy()
    kalender(img, 270, 560, "SEPTEMBER", "1", "1747", c.p(0.0, 0.06), skala_muncul(c, 0.0) * 0.62)
    kalender(img, 810, 560, "JANUARI", "14", "1749", c.p(0.12, 0.18), skala_muncul(c, 0.12) * 0.62)
    d = ImageDraw.Draw(img, "RGBA")
    se.garis_putus(d, [(390, 560), (690, 560)], c.p(0.05, 0.15), (255, 200, 120), tebal=7)
    se.teks(d, (540, 500), "501 hari", 40, KUNING, nama_font="caption", stroke=5, stroke_warna=GELAP,
            alpha=c.p(0.15, 0.2))
    k = c.p(0.2, 0.8)
    n = int(round(526 * k))
    se.teks(d, (540, 840), f"{n}", 190, (255, 80, 60), nama_font="caption", stroke=10, stroke_warna=GELAP,
            alpha=c.p(0.2, 0.24))
    se.teks(d, (540, 960), "badak dibunuh", 60, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP,
            alpha=c.p(0.22, 0.28))
    # ikon badak kecil, 1 ikon ≈ 10 badak
    total = 53
    tampil = int(total * k)
    for i in range(tampil):
        col, row = i % 11, i // 11
        x, y = 110 + col * 86, 1060 + row * 52
        badak(d, x, y, 0.17, (200, 190, 175), 1.0)
        d.line((x - 30, y - 30, x + 30, y), fill=(230, 40, 30, 255), width=4)
    se.teks(d, (540, 1340 - 20), "kurang dari dua tahun", 42, KUNING, nama_font="caption", stroke=5, stroke_warna=GELAP,
            alpha=c.p(0.82, 0.88))
    hdr(img, "Catatan sayembara")
    return img


JEJAK_JAWA = [(-6.6, 106.6), (-6.9, 107.1), (-7.1, 107.6), (-6.9, 108.2), (-7.4, 108.6), (-7.3, 109.2), (-7.2, 109.9),
              (-7.5, 110.4), (-7.7, 111.0), (-7.6, 111.8), (-7.9, 112.6), (-8.0, 113.3), (-8.2, 114.0), (-6.9, 106.3),
              (-7.2, 106.9), (-7.6, 107.9), (-7.0, 110.8), (-7.3, 112.2), (-8.4, 113.8), (-7.1, 106.2)]


def a_terakhir(c):
    kamera = se.kamera_antara(cam(JAWA, -7.3, 109.9, 0.9), cam(JAWA, -7.2, 108.4, 1.15), c.p(0.0, 0.6))
    img = se.render_peta(JAWA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, layar(JAWA, kamera, (-5.2, 110.2)), "Laut Jawa", 36, (220, 235, 255), alpha=0.8)
    # titik badak padam satu per satu (timur → barat)
    urut = sorted(JEJAK_JAWA, key=lambda ll: -ll[1])
    for i, ll in enumerate(urut):
        padam = c.p(0.05 + i * 0.022, 0.1 + i * 0.022)
        x, y = layar(JAWA, kamera, ll)
        a = 1 - padam
        if a > 0.02:
            r = 13
            d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 50, 35, int(230 * a)), outline=(255, 255, 255, int(200 * a)),
                      width=3)
    # Ujung Kulon tetap menyala
    x, y = layar(JAWA, kamera, UJUNG_KULON)
    r = 16 + 4 * math.sin(c.t * 5)
    se.glow(img, x, y, 90, (255, 200, 80), 1.3)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 200, 60, 255), outline=PUTIH + (255,), width=4)
    label(d, (x + 20, y + 52), "Ujung Kulon", 36)
    # Tasikmalaya 1934
    a = c.p(0.42, 0.48)
    if a > 0:
        tx, ty = layar(JAWA, kamera, TASIK)
        bidik(d, tx, ty, 50, a)
        se.kartu(img, min(820, tx + 40), ty + 60, "Tasikmalaya, 1934", "badak terakhir di luar Ujung Kulon",
                 MERAH, alpha=a, tiang=False, skala=skala_muncul(c, 0.42), coret=c.p(0.55, 0.65))
    a = c.p(0.72, 0.78)
    if a > 0:
        se.panel(img, (90, 430, 990, 650), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 495), "TAPI ANEHNYA…", 58, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 580), "kenapa selamat di Ujung Kulon?", 44, TINTA, nama_font="caption", alpha=c.p(0.78, 0.84))
    hdr(img, "Lenyap dari Jawa")
    return img


def kawanan(d, kamera, n, t, alpha=1.0, seed=3, s=0.16):
    rng = random.Random(seed)
    for i in range(n):
        la = UJUNG_KULON[0] + rng.uniform(-0.07, 0.07)
        lo = UJUNG_KULON[1] + rng.uniform(-0.15, 0.12)
        x, y = layar(SUNDA, kamera, (la, lo))
        x += math.sin(t * 0.8 + i) * 6
        badak(d, x, y, s, (45, 38, 32), alpha, arah=1 if rng.random() > 0.5 else -1, langkah=t * 3 + i)


def a_sisa(c):
    kamera = se.kamera_antara(cam(SUNDA, -6.6, 105.45, 0.95), cam(SUNDA, -6.73, 105.42, 1.45), c.p(0.0, 0.5))
    img = se.render_peta(SUNDA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    n = int(25 * c.p(0.35, 0.75))
    kawanan(d, kamera, n, c.t, 1.0, s=0.2)
    kalender(img, 260, 560, "SENSUS", "1967", "", c.p(0.05, 0.12), skala_muncul(c, 0.05) * 0.6)
    a = c.p(0.35, 0.4)
    if a > 0:
        se.panel(img, (420, 450, 1000, 680), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (710, 535), f"CUMA {n}" if n < 25 else "CUMA 25", 84, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (710, 625), "ekor", 44, TINTA, nama_font="judul", alpha=a)
    label(d, layar(SUNDA, kamera, (-6.9, 105.75)), "Samudra Hindia", 34, (220, 235, 255), alpha=c.p(0.5, 0.6))
    hdr(img, "Ujung Kulon, 1967")
    return img


def a_vietnam(c):
    kamera = se.kamera_antara(cam(ASIA, 5.0, 104.0, 1.5), cam(ASIA, 2.5, 104.5, 1.55), c.p(0.0, 1.0))
    img = se.render_peta(ASIA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    vx, vy = layar(ASIA, kamera, CAT_TIEN)
    ux, uy = layar(ASIA, kamera, (-6.75, 105.4))
    bidik(d, vx, vy, 55, c.p(0.05, 0.12))
    se.kartu(img, vx, vy - 90, "Vietnam, 2010", "badak terakhir ditembak pemburu", MERAH, alpha=c.p(0.08, 0.15),
             tiang=False, skala=skala_muncul(c, 0.08), coret=c.p(0.3, 0.42))
    se.garis_putus(d, [(vx, vy + 30), (vx + 60, (vy + uy) / 2), (ux + 10, uy - 40)], c.p(0.5, 0.7), (255, 200, 80),
                   tebal=8)
    a = c.p(0.6, 0.7)
    if a > 0:
        se.glow(img, ux, uy, 110, (255, 200, 80), 1.5 * a)
        d = ImageDraw.Draw(img, "RGBA")
        badak(d, ux, uy + 10, 0.35, (45, 38, 32), a)
        stempel(img, "SATU-SATUNYA DI DUNIA", 540, min(1250, uy + 140), skala_muncul(c, 0.68, 0.08) * 0.8, uk=56,
                sudut=-5)
    hdr(img, "Rumah terakhir")
    return img


KAMPUNG = [(-6.66, 105.30), (-6.80, 105.30), (-6.84, 105.48), (-6.64, 105.55), (-6.70, 105.22)]


def a_jawaban(c):
    kamera = se.Kamera(*cam(SUNDA, -6.42, 105.42, 0.95))
    goyang = 8 * (1 - c.p(0.1, 0.4))
    rng = random.Random(int(c.t * 20))
    kamera.x += rng.uniform(-1, 1) * goyang
    kamera.y += rng.uniform(-1, 1) * goyang
    img = se.render_peta(SUNDA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    kx, ky = layar(SUNDA, kamera, KRAKATAU)
    ux, uy = layar(SUNDA, kamera, UJUNG_KULON)
    kuat = 1 - c.p(0.45, 0.6) * 0.7
    asap(img, kx, ky - 30, c.t, kuat, tinggi=380, lebar=0.9)
    gunung_peta(img, kx, ky, 46, kuat)
    d = ImageDraw.Draw(img, "RGBA")
    # tsunami
    for i in range(3):
        f = clamp((c.t / c.d - 0.12 - i * 0.08) / 0.35)
        if 0 < f < 1:
            cincin(d, kx, ky, f * 620, (235, 245, 255), (1 - f) * 0.95, 14 - i * 3)
            cincin(d, kx, ky, f * 620 - 18, (80, 140, 200), (1 - f) * 0.7, 6)
    # kampung hancur → hutan tumbuh
    hancur = c.p(0.3, 0.4)
    tumbuh = c.p(0.58, 0.8)
    for i, ll in enumerate(KAMPUNG):
        x, y = layar(SUNDA, kamera, ll)
        if tumbuh < 0.3:
            rumah(d, x, y, 1.0, 1.0 - 0.6 * tumbuh / 0.3)
            if hancur > 0:
                d.line((x - 26 * hancur, y - 50 * hancur, x + 26 * hancur, y), fill=(220, 30, 25, 255), width=7)
                d.line((x + 26 * hancur, y - 50 * hancur, x - 26 * hancur, y), fill=(220, 30, 25, 255), width=7)
    if tumbuh > 0:
        rng2 = random.Random(9)
        for i in range(int(40 * tumbuh)):
            la = UJUNG_KULON[0] + rng2.uniform(-0.09, 0.09)
            lo = UJUNG_KULON[1] + rng2.uniform(-0.18, 0.15)
            x, y = layar(SUNDA, kamera, (la, lo))
            pohon(d, x, y, 0.9, 0.95)
    if c.p(0.78, 0.84) > 0:
        kawanan(d, kamera, 8, c.t, c.p(0.78, 0.84), seed=5, s=0.18)
    se.teks(d, (540, 430), "INI JAWABANNYA:", 60, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP,
            alpha=c.p(0.0, 0.05))
    se.teks(d, (540, 515), "KRAKATAU", 96, KUNING, nama_font="caption", stroke=9, stroke_warna=GELAP,
            alpha=c.p(0.03, 0.08))
    se.kartu(img, 540, 1330, "1883: tsunami ± 15 m", "menyapu Ujung Kulon", BIRU, alpha=c.p(0.15, 0.22) * (1 - c.p(0.33, 0.36)),
             tiang=False, skala=skala_muncul(c, 0.15))
    a = c.p(0.36, 0.42) * (1 - c.p(0.55, 0.6))
    if a > 0:
        se.kartu(img, 540, 1330, "Kampung hancur, manusia jarang balik", "", MERAH, alpha=a, tiang=False,
                 skala=skala_muncul(c, 0.36))
    a = c.p(0.62, 0.68)
    if a > 0:
        se.kartu(img, 540, 1330, "Hutan tumbuh lagi = tempat sembunyi badak", "", HIJAU_TUA, alpha=a, tiang=False,
                 skala=skala_muncul(c, 0.62))
    hdr(img, "Selat Sunda, 1883")
    return img


def a_ironi(c):
    kamera = se.kamera_antara(cam(JAWA, -7.3, 109.9, 0.9), cam(JAWA, -7.4, 109.9, 0.93), c.p(0, 1))
    img = se.render_peta(JAWA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    kx, ky = layar(JAWA, kamera, KRAKATAU)
    ux, uy = layar(JAWA, kamera, UJUNG_KULON)
    px_, py_ = layar(JAWA, kamera, ALAS_PURWO)
    se.glow(img, kx, ky, 70 + 15 * math.sin(c.t * 6), (255, 110, 30), 1.8)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(kx - 14, ky + 8), (kx, ky - 16), (kx + 14, ky + 8)], fill=(80, 60, 50, 255))
    for i in range(2):
        f = ((c.t * 0.6 + i * 0.5) % 1.0)
        cincin(d, kx, ky, 20 + f * 120, (235, 245, 255), (1 - f) * 0.8 * c.p(0.05, 0.1), 5)
    se.glow(img, ux, uy, 60, (255, 200, 80), 1.2)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((ux - 13, uy - 13, ux + 13, uy + 13), fill=(255, 200, 60, 255), outline=PUTIH + (255,), width=3)
    label(d, (kx - 10, ky - 50), "Krakatau", 34)
    a = c.p(0.12, 0.2)
    if a > 0:
        se.panel(img, (90, 430, 990, 640), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 500), "Satu tsunami =", 54, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 580), "bisa habis semua", 54, (170, 30, 20), nama_font="caption", alpha=a)
    # panah wacana ke Alas Purwo
    se.garis_putus(d, [(ux + 10, uy + 30), ((ux + px_) / 2, uy + 260), (px_ - 10, py_ - 20)], c.p(0.4, 0.62),
                   (255, 220, 120), tebal=8)
    a = c.p(0.6, 0.66)
    if a > 0:
        se.glow(img, px_, py_, 70, (120, 255, 150), 1.2 * a)
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse((px_ - 13, py_ - 13, px_ + 13, py_ + 13), fill=(60, 200, 110, int(255 * a)), outline=PUTIH + (int(255 * a),),
                  width=3)
        se.kartu(img, min(820, px_ - 40), py_ + 130, "Alas Purwo?", "wacana habitat kedua", HIJAU_TUA, alpha=a,
                 tiang=False, skala=skala_muncul(c, 0.6))
    a = c.p(0.8, 0.86)
    if a > 0:
        stempel(img, "SETUJU", 330, 770, skala_muncul(c, 0.8, 0.08) * 0.7, uk=54, sudut=-6, warna=HIJAU_TUA)
        stempel(img, "MENOLAK", 760, 770, skala_muncul(c, 0.86, 0.08) * 0.7, uk=54, sudut=5)
    hdr(img, "Ancaman di tempat yang sama")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = se.kamera_antara(cam(SUNDA, -6.72, 105.42, 1.3), cam(SUNDA, -6.74, 105.42, 1.45), c.p(0.0, 1.0))
    img = se.render_peta(SUNDA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    kawanan(d, kamera, 14, c.t, 1.0 - c.p(0.6, 0.66), seed=11, s=0.2)
    se.tint(img, (10, 6, 0), 0.2 + 0.4 * c.p(0.6, 0.68))
    a = c.p(0.02, 0.1) * (1 - c.p(0.6, 0.66))
    if a > 0:
        se.panel(img, (90, 420, 990, 720), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 495), "Kini < 100 ekor", 60, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 590), "dulu dihargai mati,", 44, TINTA, nama_font="judul", alpha=c.p(0.2, 0.26) * a)
        se.teks(d, (540, 655), "sekarang nggak ternilai", 44, TINTA, nama_font="judul", alpha=c.p(0.28, 0.34) * a)
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
    Adegan("hook", "Badak ini dulu dibayar buat dibunuh. Lagi rame badak jawa mau dipindah? Kenapa sih, badak jawa cuma tersisa di satu ujung pulau?",
           a_hook, transisi=False),
    Adegan("sebaran", "Dulu, badak bercula satu ini hidup dari India sampai Jawa. Di Jawa, mereka berkeliaran dekat kampung.",
           a_sebaran),
    Adegan("hama", "Masalahnya, badak dianggap hama. Kebun dan sawah dirusak. Jadi pemerintah kolonial bikin sayembara: bunuh badak, dapat hadiah.",
           a_hama),
    Adegan("angka", "Dari tahun tujuh belas empat puluh tujuh sampai tujuh belas empat puluh sembilan, lima ratus dua puluh enam badak dibunuh. Kurang dari dua tahun.",
           a_angka),
    Adegan("terakhir", "Satu per satu, badak lenyap dari Jawa. Yang terakhir di luar Ujung Kulon ditembak tahun sembilan belas tiga puluh empat. Tapi bagian paling aneh-nya: kenapa yang selamat justru di Ujung Kulon?",
           a_terakhir),
    Adegan("sisa", "Tahun sembilan belas enam puluh tujuh, badak di sana dihitung. Cuma dua puluh lima ekor.",
           a_sisa),
    Adegan("vietnam", "Di Vietnam, badak jawa terakhir ditembak pemburu tahun dua ribu sepuluh. Ujung Kulon jadi satu-satunya rumah mereka.",
           a_vietnam),
    Adegan("jawaban", "Nah, ini jawabannya: Krakatau. Tahun delapan belas delapan puluh tiga, tsunami sekitar lima belas meter menyapu Ujung Kulon. Kampung hancur, manusia nggak banyak yang balik. Hutannya tumbuh lagi, jadi tempat sembunyi badak.",
           a_jawaban),
    Adegan("ironi", "Ironisnya, ancamannya juga di situ. Satu tsunami bisa menghapus semuanya. Makanya muncul ide habitat kedua, seperti Alas Purwo. Ada yang setuju, ada yang menolak.",
           a_ironi),
    Adegan("penutup", "Sekarang jumlahnya kurang dari seratus. Dulu dihargai mati, sekarang nggak ternilai. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
