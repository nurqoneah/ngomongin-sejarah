"""Shorts ±88 detik: Sejarah banjir Batavia–Jakarta (1621 – sekarang).

Dua jenis visual: (1) peta Teluk Jakarta dekat dengan 13 sungai (jalur sungai disederhanakan),
(2) ilustrasi denah kota tua Batavia bergaya peta kuno + skema/penampang.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "sejarah-banjir-jakarta-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "BANJIR JAKARTA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
AIR = (55, 105, 160)
AIR_MUDA = (120, 170, 215)
BIRU = (30, 80, 150)
LUMPUR = (120, 95, 60)

# ------------------------------------------------------------------ peta Teluk Jakarta (dekat)

DARAT = [(-5.98, 106.45), (-6.0, 106.55), (-6.01, 106.67), (-6.06, 106.72), (-6.105, 106.77), (-6.11, 106.79),
         (-6.122, 106.808), (-6.123, 106.84), (-6.1, 106.885), (-6.1, 106.93), (-6.095, 106.96), (-6.03, 107.0),
         (-5.93, 107.03), (-5.95, 107.25), (-6.65, 107.25), (-6.65, 106.45)]

print("  menyiapkan peta Teluk Jakarta...")
TELUK = Peta(106.45, 107.25, -6.65, -5.85, 2400, [], [(-6.6, 106.8, 0.08), (-6.62, 106.95, 0.07)],
             seed=19, darat=[DARAT])

# 13 sungai (disederhanakan, ilustratif)
CILIWUNG = [(-6.6, 106.82), (-6.45, 106.83), (-6.33, 106.85), (-6.27, 106.86), (-6.225, 106.866), (-6.21, 106.85),
            (-6.18, 106.835), (-6.163, 106.833), (-6.145, 106.818), (-6.122, 106.81)]
SUNGAI = [
    CILIWUNG,
    [(-6.6, 106.66), (-6.4, 106.69), (-6.25, 106.72), (-6.17, 106.75), (-6.12, 106.765), (-6.105, 106.77)],
    [(-6.6, 106.74), (-6.4, 106.76), (-6.27, 106.76), (-6.19, 106.77), (-6.15, 106.765), (-6.115, 106.768)],
    [(-6.6, 106.79), (-6.4, 106.8), (-6.28, 106.81), (-6.21, 106.81), (-6.18, 106.815), (-6.15, 106.815)],
    [(-6.3, 106.78), (-6.22, 106.79), (-6.16, 106.79), (-6.112, 106.79)],
    [(-6.4, 106.89), (-6.3, 106.885), (-6.23, 106.88), (-6.17, 106.875), (-6.12, 106.87)],
    [(-6.6, 106.92), (-6.4, 106.9), (-6.27, 106.9), (-6.18, 106.89), (-6.12, 106.895), (-6.1, 106.9)],
    [(-6.3, 106.92), (-6.22, 106.93), (-6.15, 106.925), (-6.1, 106.925)],
    [(-6.6, 106.98), (-6.4, 106.97), (-6.25, 106.95), (-6.15, 106.95), (-6.096, 106.945)],
    [(-6.32, 106.95), (-6.23, 106.94), (-6.16, 106.938)],
    [(-6.21, 106.66), (-6.18, 106.71), (-6.16, 106.74), (-6.13, 106.758)],
    [(-6.2, 106.815), (-6.17, 106.808), (-6.14, 106.802), (-6.115, 106.8)],
    [(-6.35, 106.87), (-6.27, 106.875), (-6.22, 106.872), (-6.19, 106.86), (-6.15, 106.855), (-6.124, 106.85)],
]
KANAL_BARAT = [(-6.209, 106.85), (-6.206, 106.83), (-6.205, 106.815), (-6.19, 106.806), (-6.17, 106.797),
               (-6.145, 106.79), (-6.125, 106.78), (-6.105, 106.772)]
KANAL_TIMUR = [(-6.235, 106.885), (-6.215, 106.905), (-6.19, 106.925), (-6.16, 106.945), (-6.12, 106.955),
               (-6.098, 106.962)]
TEMPAT = {"Manggarai": (-6.209, 106.85), "Karet": (-6.205, 106.815), "Muara Angke": (-6.105, 106.772),
          "Pasar Baru": (-6.163, 106.835), "Kota Tua": (-6.135, 106.813), "Marunda": (-6.098, 106.962)}


def _titik_banjir():
    rng = random.Random(4)
    hasil = []
    for s in SUNGAI:
        for (a0, b0), (a1, b1) in zip(s, s[1:]):
            for k in range(6):
                f = k / 6
                lat, lon = lerp(a0, a1, f), lerp(b0, b1, f)
                if lat > -6.3:
                    hasil.append((lat + rng.gauss(0, 0.004), lon + rng.gauss(0, 0.004), rng.uniform(0.6, 1.3),
                                  (lat + 6.3) / 0.2))
    for i in range(60):
        lon = rng.uniform(106.7, 106.98)
        lat = rng.uniform(-6.15, -6.105)
        hasil.append((lat, lon, rng.uniform(0.8, 1.4), 1.0))
    return hasil


TITIK_BANJIR = _titik_banjir()


# ------------------------------------------------------------------ helper

def cam(lat, lon, zoom):
    x, y = TELUK.px(lat, lon)
    return (x, y, zoom)


def peta(kamera):
    img = se.render_peta(TELUK, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(kamera, ll):
    return kamera.layar(*TELUK.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def hdr(img, sub="1621 – sekarang", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def berkelok(poli, seed):
    """Sisipkan kelokan kecil biar sungai tidak lurus kaku (lat, lon)."""
    rng = random.Random(seed)
    hasil = []
    for (a0, b0), (a1, b1) in zip(poli, poli[1:]):
        dl, db = a1 - a0, b1 - b0
        n = math.hypot(dl, db) or 1
        for k in range(5):
            f = k / 5
            geser = math.sin(f * math.pi) * rng.uniform(-0.25, 0.25) * n * 0.35
            hasil.append((a0 + dl * f - db / n * geser, b0 + db * f + dl / n * geser))
    hasil.append(poli[-1])
    return hasil


SUNGAI = [berkelok(s, i) for i, s in enumerate(SUNGAI)]
CILIWUNG = SUNGAI[0]


def sungai(d, kamera, daftar=SUNGAI, progres=1.0, alpha=1.0, tebal=7, warna=AIR):
    for i, s in enumerate(daftar):
        pts = se.halus([layar(kamera, ll) for ll in s], 2)
        pts = pts[:max(2, int(len(pts) * clamp(progres)))] if progres < 1 else pts
        d.line(pts, fill=tuple(warna) + (int(230 * alpha),), width=tebal, joint="curve")


def banjir(img, kamera, level, t, seed=0, warna=AIR):
    """Genangan meluas dari sungai & pesisir. level 0..1+ (1 = parah)."""
    if level <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    skala = TELUK.skala * kamera.zoom
    for i, (lat, lon, r, urut) in enumerate(TITIK_BANJIR):
        k = clamp(level * 1.6 - urut * 0.5)
        if k <= 0:
            continue
        x, y = layar(kamera, (lat, lon))
        rr = r * 0.012 * skala * k * (1 + 0.04 * math.sin(t * 2 + i))
        if -rr < x < W + rr and -rr < y < H + rr:
            d.ellipse((x - rr, y - rr * 0.8, x + rr, y + rr * 0.8), fill=tuple(warna) + (255,))
    for s_ in SUNGAI:
        pts = [layar(kamera, ll) for ll in s_ if ll[0] > -6.24]
        if len(pts) > 1:
            d.line(pts, fill=tuple(warna) + (255,), width=max(1, int(0.014 * skala * clamp(level * 1.3))),
                   joint="curve")
    se.tempel(img, lap, 0.62)
    # kilau riak
    d2 = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed)
    for i in range(int(50 * clamp(level))):
        lat, lon, _, urut = TITIK_BANJIR[rng.randrange(len(TITIK_BANJIR))]
        if clamp(level * 1.6 - urut * 0.5) < 0.5:
            continue
        x, y = layar(kamera, (lat, lon))
        x += math.sin(t * 1.5 + i) * 14
        d2.line((x - 22, y, x + 22, y), fill=(220, 235, 250, 150), width=3)


def pin(d, x, y, warna=MERAH, alpha=1.0, s=1.0):
    a = int(255 * alpha)
    d.ellipse((x - 16 * s, y - 52 * s, x + 16 * s, y - 20 * s), fill=tuple(warna) + (a,), outline=(40, 10, 10, a), width=3)
    d.polygon([(x - 12 * s, y - 30 * s), (x + 12 * s, y - 30 * s), (x, y)], fill=tuple(warna) + (a,))
    d.ellipse((x - 6 * s, y - 42 * s, x + 6 * s, y - 30 * s), fill=(255, 255, 255, a))


def angka_besar(d, xy, isi, uk, warna=PUTIH, alpha=1.0, stroke_warna=(10, 20, 40)):
    se.teks(d, xy, isi, uk, warna, nama_font="caption", stroke=10, stroke_warna=stroke_warna, alpha=alpha)


# ------------------------------------------------------------------ denah kuno Batavia (ilustrasi)

print("  menyiapkan latar denah kuno...")
_KERTAS = se.latar_tekstur(W, H, 33, warna=(226, 208, 166)).convert("RGBA")
LAUT_Y = 520   # garis pantai di denah
KOTA = (300, 640, 840, 1080)  # kotak kota bertembok


def denah(c, banjir_k=0.0, lumpur=0.0, kanal=1.0):
    img = _KERTAS.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # laut di atas
    d.rectangle((0, 0, W, LAUT_Y), fill=(60, 85, 120, 255))
    for i in range(14):
        y = 330 + (i % 7) * 28
        x = (i * 173 + c.t * 30) % (W + 200) - 100
        d.arc((x - 40, y - 10, x + 40, y + 10), 200, 340, fill=(160, 190, 215, 200), width=3)
    se.teks(d, (180, 470), "Laut Jawa", 38, (220, 230, 240), nama_font="tangan")
    # sungai Ciliwung lurus menembus kota
    cx = 570
    d.rectangle((cx - 24, LAUT_Y, cx + 24, H), fill=AIR + (255,))
    # tembok kota
    x0, y0, x1, y1 = KOTA
    d.rectangle((x0, y0, x1, y1), outline=(90, 60, 35, 255), width=10)
    for bx, by in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        d.polygon([(bx, by - 34), (bx + 34, by), (bx, by + 34), (bx - 34, by)], fill=(120, 85, 50, 255),
                  outline=(60, 40, 20, 255))
    # kanal-kanal (grid)
    wk = se.lerp_rgb(AIR, LUMPUR, lumpur)
    k = clamp(kanal)
    for i, y in enumerate((720, 820, 920, 1020)):
        L = (x1 - x0 - 40) * clamp(k * 4 - i)
        if L > 2:
            d.line((x0 + 20, y, x0 + 20 + L, y), fill=wk + (255,), width=14)
    for i, x in enumerate((380, 470, 670, 760)):
        L = (y1 - y0 - 40) * clamp(k * 4 - i)
        if L > 2:
            d.line((x, y0 + 20, x, y0 + 20 + L), fill=wk + (255,), width=14)
    # blok rumah
    rng = random.Random(5)
    for gx in (380, 470, 670, 760):
        for gy in (720, 820, 920):
            for _ in range(3):
                bx = gx + rng.uniform(16, 70)
                by = gy + rng.uniform(16, 70)
                d.rectangle((bx, by, bx + 18, by + 14), fill=(150, 70, 45, 255), outline=(70, 35, 20, 255))
    if lumpur > 0.05:
        for i in range(40):
            gx = rng.choice((380, 470, 670, 760))
            gy = rng.uniform(y0 + 30, y1 - 30)
            r = rng.uniform(6, 14) * lumpur
            d.ellipse((gx - r, gy - r, gx + r, gy + r), fill=(80, 60, 35, 230))
            d.ellipse((gx + 30 - r, gy - r, gx + 30 + r, gy + r), fill=(60, 55, 40, 200))
    # genangan banjir
    if banjir_k > 0.01:
        lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        rng2 = random.Random(9)
        for i in range(70):
            x = rng2.uniform(120, 960)
            y = rng2.uniform(LAUT_Y + 20, 1260)
            jarak = abs(x - cx) / 450 + (y - LAUT_Y) / 1400
            kk = clamp(banjir_k * 1.8 - jarak)
            r = rng2.uniform(60, 130) * kk
            if r > 2:
                dl.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=AIR + (255,))
        se.tempel(img, lap, 0.55)
    return img


# ------------------------------------------------------------------ adegan

def a_hook(c):
    kamera = se.kamera_antara(cam(-6.16, 106.835, 1.55), cam(-6.15, 106.83, 1.8), c.p(0.0, 1.0))
    img, d = peta(kamera)
    sungai(d, kamera)
    banjir(img, kamera, 0.75 + 0.25 * c.p(0.0, 0.5), c.t, 1)
    se.tint(img, (20, 30, 50), 0.28)
    se.hujan(img, c.t, 1.0, 3)
    d = ImageDraw.Draw(img, "RGBA")
    for i, nama in enumerate(("Kota Tua", "Pasar Baru", "Manggarai")):
        x, y = layar(kamera, TEMPAT[nama])
        pin(d, x, y, alpha=c.p(0.05 + i * 0.05, 0.1 + i * 0.05))
    s = 0.88 + 0.12 * back_out(c.t / 0.4)
    angka_besar(d, (540, 520), "BANJIR SEJAK", int(104 * s), PUTIH)
    angka_besar(d, (540, 690), "1621", int(240 * s), (150, 210, 255))
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    a = c.p(0.32, 0.42)
    dl.rounded_rectangle((170, 1000, 910, 1100), 26, fill=(240, 140, 20, 240), outline=(60, 30, 10, 255), width=5)
    dl.text((540, 1050), "Musim hujan 2026: siaga banjir", font=se.font("caption", 40), fill=PUTIH, anchor="mm",
            stroke_width=4, stroke_fill=(60, 30, 10))
    se.tempel(img, lap, a * (1 - c.p(0.68, 0.74)))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 1060), "kenapa nggak pernah menang?", 52, (255, 220, 120), nama_font="caption", stroke=7,
            stroke_warna=(20, 15, 10), alpha=c.p(0.76, 0.84))
    hdr(img, alpha=c.p(0.55, 0.7))
    return img


def a_coen(c):
    img = denah(c, kanal=c.p(0.3, 0.75))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (570, 610), "BATAVIA", 50, TINTA, nama_font="judul", alpha=c.p(0.02, 0.1))
    se.kartu(img, 540, 1190, "Jan Pieterszoon Coen · VOC", "rebut Jayakarta, 1619", MERAH, alpha=c.p(0.05, 0.14),
             tiang=False, skala=back_out((c.t / c.d - 0.05) / 0.1))
    a = c.p(0.62, 0.7)
    if a > 0:
        se.kartu(img, 760, 450, "“kayak Amsterdam”", "penuh kanal", BIRU, alpha=a, tiang=False,
                 skala=back_out((c.t / c.d - 0.62) / 0.1))
    hdr(img, "1619")
    return img


def a_1621(c):
    img = denah(c, banjir_k=c.p(0.25, 0.65), lumpur=c.p(0.6, 0.85))
    d = ImageDraw.Draw(img, "RGBA")
    # panah sungai-sungai turun ke kota (dataran rendah)
    for i, x in enumerate((150, 360, 790, 960)):
        k = c.p(0.02 + i * 0.04, 0.2 + i * 0.04)
        se.garis_putus(d, [(x, 1290), (lerp(x, 570, 0.35), 1150), (lerp(x, 570, 0.55), 1100)], k, BIRU, tebal=7)
    se.kartu(img, 540, 1190, "Dataran rendah, muara sungai", "", (90, 70, 50), alpha=c.p(0.04, 0.12) * (1 - c.p(0.36, 0.42)),
             tiang=False)
    s = back_out((c.t / c.d - 0.36) / 0.1)
    if c.t / c.d > 0.36:
        angka_besar(d, (540, 880), "1621", int(190 * s) + 1, (150, 210, 255))
        se.teks(d, (540, 1000), "banjir besar pertama tercatat", 46, PUTIH, nama_font="caption", stroke=6,
                stroke_warna=(10, 20, 40), alpha=c.p(0.4, 0.48))
    se.kartu(img, 540, 1190, "Kanal tersumbat lumpur & sampah", "", LUMPUR, alpha=c.p(0.68, 0.76), tiang=False,
             skala=back_out((c.t / c.d - 0.68) / 0.1))
    hdr(img, "1621")
    return img


def a_berulang(c):
    img = _KERTAS.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # air naik dari bawah
    naik = c.p(0.0, 0.95)
    y_air = int(1300 - 620 * naik)
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    gel = [(x, y_air + math.sin(x / 70 + c.t * 3) * 14) for x in range(0, W + 20, 20)]
    dl.polygon(gel + [(W, H), (0, H)], fill=AIR + (215,))
    for j in range(3):
        yy = y_air + 70 + j * 90
        dl.line([(x, yy + math.sin(x / 50 + c.t * 2 + j) * 8) for x in range(0, W + 20, 20)], fill=AIR_MUDA + (160,),
                width=4)
    img.alpha_composite(lap)
    d = ImageDraw.Draw(img, "RGBA")
    tahun = [("1621", 0.02), ("1654", 0.18), ("1870-an", 0.42)]
    for i, (th, t0) in enumerate(tahun):
        a = c.p(t0, t0 + 0.06)
        if a > 0:
            angka_besar(d, (540, 500 + i * 170), th, int(130 * back_out((c.t / c.d - t0) / 0.1)) + 1,
                        (40, 70, 120), alpha=a, stroke_warna=PUTIH)
    se.teks(d, (540, 1060), "lagi… dan lagi", 70, PUTIH, nama_font="caption", stroke=8, stroke_warna=(10, 20, 40),
            alpha=c.p(0.72, 0.8))
    hdr(img, "Abad demi abad")
    return img


def a_1918(c):
    kamera = se.kamera_antara(cam(-6.17, 106.84, 1.4), cam(-6.17, 106.835, 1.75), c.p(0.0, 1.0))
    img, d = peta(kamera)
    sungai(d, kamera, [CILIWUNG], tebal=12)
    sungai(d, kamera, SUNGAI[1:], tebal=6, alpha=0.6)
    banjir(img, kamera, 0.4 + 0.6 * c.p(0.1, 0.5), c.t, 2)
    se.hujan(img, c.t, 0.8, 5)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 590), "Ciliwung meluap", 52, PUTIH, nama_font="caption", stroke=6, stroke_warna=(10, 20, 40),
            alpha=c.p(0.28, 0.34))
    s = back_out((c.t / c.d) / 0.12)
    angka_besar(d, (540, 470), "FEBRUARI 1918", int(100 * s) + 1, (255, 220, 120), stroke_warna=(40, 20, 10))
    kartu = [("Kampung terendam ± 1 meter", "", 0.42), ("Trem berhenti", "", 0.56),
             ("Kolera menyebar", "", 0.78)]
    for i, (j, sub, t0) in enumerate(kartu):
        warna = MERAH if i == 2 else (60, 60, 70)
        se.kartu(img, 540, 760 + i * 130, j, sub, warna, alpha=c.p(t0, t0 + 0.06), tiang=False,
                 skala=back_out((c.t / c.d - t0) / 0.08))
    hdr(img, "Banjir terbesar zaman kolonial")
    return img


def a_breen(c):
    img = _KERTAS.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # skema: laut atas, kota di tengah, air dari selatan dibelokkan
    d.rectangle((0, 330, W, 470), fill=(60, 85, 120, 255))
    se.teks(d, (540, 400), "LAUT", 40, (220, 230, 240), nama_font="tangan")
    d.rounded_rectangle((420, 600, 840, 820), 20, fill=(150, 70, 45, 255), outline=(70, 35, 20, 255), width=6)
    se.teks(d, (630, 710), "KOTA", 54, PUTIH, nama_font="judul")
    se.teks(d, (540, 1250), "air dari selatan (hulu)", 38, TINTA, nama_font="tangan", alpha=c.p(0.25, 0.32))
    belok = c.p(0.55, 0.85)
    for i, x in enumerate((520, 630, 740)):
        k = c.p(0.28 + i * 0.03, 0.45 + i * 0.03)
        if belok < 0.05:
            se.garis_putus(d, [(x, 1200), (x, 840)], k, BIRU, tebal=9)
        else:
            se.garis_putus(d, [(x, 1200), (x, 990), (230, 990), (230, 480)], belok, BIRU, tebal=9)
    if belok > 0.05:
        d.line([(230, 990), (900, 990)], fill=AIR + (int(255 * belok),), width=26)
        d.line([(230, 990), (230, 470)], fill=AIR + (int(255 * belok),), width=26)
        se.teks(d, (270, 760), "kanal", 40, (20, 50, 110), nama_font="tangan", anchor="lm", alpha=belok)
    se.kartu(img, 540, 540, "Herman van Breen", "insinyur pengairan Belanda", BIRU, alpha=c.p(0.03, 0.12),
             tiang=False, skala=back_out((c.t / c.d - 0.03) / 0.1))
    se.teks(d, (540, 1130), "Belokin aja!", 64, MERAH, nama_font="caption", stroke=6, stroke_warna=PUTIH,
            alpha=c.p(0.82, 0.9))
    hdr(img, "Idenya sederhana")
    return img


def a_kanal(c):
    kamera = Kamera(*cam(-6.155, 106.81, 2.6))
    img, d = peta(kamera)
    sungai(d, kamera, [CILIWUNG], tebal=10)
    pts = se.halus([layar(kamera, ll) for ll in KANAL_BARAT], 2)
    k = c.p(0.05, 0.6)
    n = max(2, int(len(pts) * k))
    if k > 0:
        d.line(pts[:n], fill=(30, 90, 170, 255), width=22, joint="curve")
        se.garis_putus(d, pts, k, (240, 240, 250), tebal=5, putus=14, celah=12)
    for i, nama in enumerate(("Manggarai", "Karet", "Muara Angke")):
        x, y = layar(kamera, TEMPAT[nama])
        a = c.p(0.05 + i * 0.22, 0.12 + i * 0.22)
        pin(d, x, y, BIRU, a)
        label(d, (x + (130 if i != 1 else -90), y + 30), nama, 40, TINTA, a)
    se.kartu(img, 540, 470, "Banjir Kanal Barat", "rampung sekitar 1919", BIRU, alpha=c.p(0.02, 0.1), tiang=False,
             skala=back_out((c.t / c.d - 0.02) / 0.1))
    se.kartu(img, 540, 1230, "Digali pakai tangan", "", (90, 70, 50), alpha=c.p(0.66, 0.74), tiang=False,
             skala=back_out((c.t / c.d - 0.66) / 0.1))
    hdr(img, "Banjir Kanal Barat")
    return img


def a_2007(c):
    kamera = Kamera(*cam(-6.17, 106.86, 1.35))
    img, d = peta(kamera)
    sungai(d, kamera)
    pts = se.halus([layar(kamera, ll) for ll in KANAL_BARAT], 2)
    d.line(pts, fill=(30, 90, 170, 255), width=14, joint="curve")
    banjir(img, kamera, c.p(0.0, 0.25) * (1 - 0.6 * c.p(0.6, 0.75)), c.t, 3)
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out((c.t / c.d) / 0.12)
    angka_besar(d, (540, 520), "2007", int(170 * s) + 1, (150, 210, 255))
    a = c.p(0.12, 0.2) * (1 - c.p(0.62, 0.66))
    se.kartu(img, 540, 760, "± 79 orang meninggal", "Jabodetabek · data Bappenas", MERAH, alpha=a, tiang=False)
    se.kartu(img, 540, 910, "Ratusan ribu mengungsi", "", (60, 60, 70), alpha=c.p(0.4, 0.47) * (1 - c.p(0.62, 0.66)),
             tiang=False)
    k = c.p(0.64, 0.92)
    if k > 0:
        pts = se.halus([layar(kamera, ll) for ll in KANAL_TIMUR], 2)
        n = max(2, int(len(pts) * k))
        d.line(pts[:n], fill=(30, 90, 170, 255), width=22, joint="curve")
        se.garis_putus(d, pts, k, (240, 240, 250), tebal=5, putus=14, celah=12)
        se.kartu(img, 540, 1180, "Banjir Kanal Timur", "ide yang sama, abad ke-21", BIRU, alpha=c.p(0.66, 0.74),
                 tiang=False, skala=back_out((c.t / c.d - 0.66) / 0.1))
    hdr(img, "Banjir tetap datang")
    return img


def a_jawaban(c):
    k = c.t / c.d
    if k < 0.42:
        kamera = Kamera(*cam(-6.3, 106.84, 0.95))
        img, d = peta(kamera)
        sungai(d, kamera, progres=c.p(0.0, 0.25), tebal=8)
        n = max(1, int(13 * c.p(0.0, 0.25) + 0.5))
        angka_besar(d, (540, 560), f"{n} SUNGAI", 130, (150, 210, 255))
        se.teks(d, (540, 690), "mengalir ke kota ini", 50, PUTIH, nama_font="caption", stroke=6,
                stroke_warna=(10, 20, 40), alpha=c.p(0.1, 0.18))
        se.teks(d, (540, 470), "Jawabannya:", 50, (255, 220, 120), nama_font="caption", stroke=6,
                stroke_warna=(40, 20, 10), alpha=c.p(0.0, 0.05))
        hdr(img, "Kenapa nggak pernah menang?")
        return img
    # penampang: tanah turun di bawah permukaan laut
    img = _KERTAS.copy()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 300, W, 1320), fill=(185, 210, 230, 255))
    laut_y = 860
    turun = c.p(0.6, 0.95) * 70
    # laut di kanan (utara)
    d.rectangle((640, laut_y, W, 1320), fill=(60, 85, 120, 255))
    for i in range(6):
        x = 680 + i * 70 + math.sin(c.t * 2 + i) * 10
        d.arc((x - 30, laut_y - 8, x + 30, laut_y + 8), 200, 340, fill=(200, 220, 235, 220), width=3)
    # profil tanah: dari selatan (kiri, tinggi) ke utara (kanan, di bawah laut)
    prof = [(0, 700), (200, 760), (380, 830), (520, laut_y + 20 + turun), (700, laut_y + 40 + turun),
            (760, laut_y + 70 + turun)]
    d.polygon(prof + [(760, 1320), (0, 1320)], fill=(150, 115, 75, 255), outline=(60, 40, 20, 255))
    d.line([(0, laut_y), (W, laut_y)], fill=(20, 50, 110, 255), width=4)
    se.teks(d, (180, laut_y - 26), "permukaan laut", 32, (20, 50, 110), nama_font="tangan", anchor="lm")
    # tanggul
    d.rectangle((740, laut_y - 60, 790, 1320), fill=(120, 120, 125, 255), outline=(50, 50, 55, 255), width=3)
    # rumah di bawah permukaan laut
    for x in (560, 640):
        y = laut_y + 30 + turun
        d.rectangle((x - 28, y - 40, x + 28, y), fill=(200, 90, 60, 255), outline=(70, 30, 20, 255), width=3)
        d.polygon([(x - 36, y - 40), (x, y - 72), (x + 36, y - 40)], fill=(130, 50, 35, 255))
    se.teks(d, (150, 1250), "selatan", 34, TINTA, anchor="lm")
    se.teks(d, (930, 1250), "utara", 34, PUTIH, anchor="rm")
    se.kartu(img, 540, 450, "Sebagian kota di bawah laut", "", BIRU, alpha=c.p(0.44, 0.52), tiang=False,
             skala=back_out((k - 0.44) / 0.08))
    a = c.p(0.62, 0.7)
    if a > 0:
        se.garis_putus(d, [(600, 600), (600, 770)], a, MERAH, tebal=10)
        se.kartu(img, 540, 1100, "Tanah turun terus", "Jakarta Utara: beberapa cm / tahun", MERAH, alpha=a,
                 tiang=False, skala=back_out((k - 0.62) / 0.08))
    hdr(img, "Kenapa nggak pernah menang?")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def ikon_sampah(d, x, y, a):
    al = int(255 * a)
    d.rectangle((x - 60, y - 70, x + 60, y + 80), fill=(90, 110, 90, al), outline=(30, 40, 30, al), width=5)
    d.rectangle((x - 75, y - 95, x + 75, y - 70), fill=(70, 90, 70, al), outline=(30, 40, 30, al), width=5)
    for dx in (-30, 0, 30):
        d.line((x + dx, y - 50, x + dx, y + 60), fill=(40, 55, 40, al), width=6)


def a_penutup(c):
    kamera = Kamera(*cam(-6.17, 106.84, 1.05))
    img, d = peta(kamera)
    sungai(d, kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 450, 990, 1060), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 540), "Bukan cuma soal hujan", 54, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 615), "kota ini dibangun di jalur air", 38, (90, 70, 50), alpha=a)
        b = a * c.p(0.3, 0.38)
        ikon_sampah(d, 540, 820, b)
        d.ellipse((420, 700, 660, 940), outline=(200, 30, 30, int(255 * b)), width=16)
        d.line((455, 905, 625, 735), fill=(200, 30, 30, int(255 * b)), width=16)
        se.teks(d, (540, 1000), "Jangan buang sampah ke kali!", 46, (170, 30, 20), nama_font="caption", alpha=b)
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
    Adegan("hook", "Jakarta banjir sejak tahun enam belas dua puluh satu. Musim hujan baru mulai, BNPB udah minta "
                   "siaga. Tapi ada satu alasan, kenapa kota ini nggak pernah menang lawan air.", a_hook,
           transisi=False),
    Adegan("coen", "Tahun enam belas sembilan belas, VOC membangun Batavia. Coen pengin kota ini mirip Amsterdam. "
                   "Penuh kanal.", a_coen),
    Adegan("1621", "Masalahnya, Batavia ada di dataran rendah, tempat sungai bermuara. Tahun enam belas dua puluh "
                   "satu, banjir besar pertama tercatat. Kanalnya pun gampang tersumbat lumpur.", a_1621,
           transisi=False),
    Adegan("berulang", "Banjir terus balik. Enam belas lima puluh empat. Delapan belas tujuh puluhan. Lagi, dan lagi.",
           a_berulang),
    Adegan("1918", "Nah, yang paling parah, Februari sembilan belas delapan belas. Ciliwung meluap, kampung "
                   "terendam semeter, trem berhenti. Lalu, kolera menyebar.", a_1918),
    Adegan("breen", "Lalu muncul insinyur pengairan, Herman van Breen. Idenya simpel. Air dari selatan jangan masuk "
                    "kota. Belokin aja.", a_breen),
    Adegan("kanal", "Lahirlah Banjir Kanal Barat, dari Manggarai sampai Muara Angke. Digali pakai tangan, rampung "
                    "sekitar sembilan belas sembilan belas.", a_kanal),
    Adegan("2007", "Tahun dua ribu tujuh, banjir lagi. Hampir delapan puluh orang meninggal, ratusan "
                   "ribu mengungsi. Lalu dibangun Banjir Kanal Timur, idenya sama.", a_2007),
    Adegan("jawaban", "Kenapa nggak pernah menang? Tiga belas sungai mengalir ke kota ini. Sebagian wilayahnya "
                      "di bawah permukaan laut. Dan tanahnya terus turun, di Jakarta Utara bisa beberapa senti "
                      "tiap tahun.", a_jawaban),
    Adegan("penutup", "Banjir Jakarta bukan cuma soal hujan, tapi soal kota di jalur air. Jangan buang sampah "
                      "ke kali. Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
