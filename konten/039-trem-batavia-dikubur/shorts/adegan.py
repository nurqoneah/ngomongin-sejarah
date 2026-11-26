"""Shorts ±88 detik: Jakarta pernah punya trem — terus relnya dikubur.

Temuan rel trem di proyek MRT Glodok–Kota (Des 2021) → trem kuda 1869 (Kota lama–Weltevreden) →
masalah kuda (mati, kotoran) → trem uap awal 1880-an → trem listrik 1899 → puncak 1934 (5 jalur, ±41 km) →
1957 jadi PPD → ±1960 dinilai tak cocok untuk Jakarta yang makin padat, ditutup bertahap & diganti bus,
rel ditimbun aspal → ketemu lagi waktu gali MRT.
Visual: penampang jalan (aspal–tanah–rel), peta lokal Batavia (jalur trem disederhanakan/ilustratif),
ilustrasi trem kuda/uap/listrik, bus. Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, KUNING, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "trem-batavia-dikubur-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "TREM BATAVIA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
COKLAT = (120, 70, 35)
BIRU = (30, 80, 150)
HIJAU_T = (46, 110, 70)
GELAP = (25, 12, 8)
ASPAL = (52, 52, 58)
TANAH = (126, 90, 54)

# ------------------------------------------------------------------ peta lokal Batavia (disederhanakan)

DARAT_JKT = [(-5.98, 106.30), (-6.00, 106.45), (-6.02, 106.56), (-6.04, 106.65), (-6.09, 106.73), (-6.11, 106.79),
             (-6.105, 106.85), (-6.10, 106.89), (-6.105, 106.95), (-6.06, 106.99), (-5.98, 107.01), (-5.93, 107.04),
             (-5.94, 107.15), (-5.97, 107.35), (-7.40, 107.35), (-7.40, 106.20), (-5.98, 106.20)]

print("  menyiapkan peta Batavia...")
BAT = Peta(106.70, 106.97, -6.32, -6.04, 7000, [], [], seed=39, darat=[DARAT_JKT])
print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 39, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (6, 14, 30), 0.78)

KOTA = (-6.137, 106.813)
GLODOK = (-6.147, 106.815)
HARMONI = (-6.166, 106.819)
WELTEVREDEN = (-6.170, 106.834)
PASARBARU = (-6.163, 106.834)
GAMBIR = (-6.177, 106.829)
SENEN = (-6.176, 106.843)
KRAMAT = (-6.188, 106.845)
SALEMBA = (-6.197, 106.851)
JATINEGARA = (-6.215, 106.870)
TANAHABANG = (-6.186, 106.812)
MENTENG = (-6.196, 106.834)
CILIWUNG = [(-6.24, 106.862), (-6.215, 106.858), (-6.20, 106.848), (-6.185, 106.838), (-6.172, 106.828),
            (-6.160, 106.818), (-6.145, 106.812), (-6.125, 106.810), (-6.108, 106.808)]
RUTE_KUDA = [KOTA, GLODOK, HARMONI, (-6.165, 106.826), WELTEVREDEN]
# jaringan 1934 — disederhanakan (ilustratif)
JALUR = [
    ([KOTA, GLODOK, HARMONI, PASARBARU, SENEN, KRAMAT, SALEMBA, (-6.206, 106.860), JATINEGARA], (200, 40, 35)),
    ([HARMONI, (-6.175, 106.817), TANAHABANG], (30, 80, 150)),
    ([KOTA, (-6.140, 106.826), (-6.152, 106.833), PASARBARU], (40, 120, 70)),
    ([HARMONI, GAMBIR, SENEN], (200, 130, 20)),
    ([TANAHABANG, (-6.193, 106.822), MENTENG, KRAMAT], (120, 50, 130)),
]


# ------------------------------------------------------------------ helper

def cam(lat, lon, zoom):
    x, y = BAT.px(lat, lon)
    return (x, y, zoom)


def layar(kamera, ll):
    return kamera.layar(*BAT.px(*ll))


def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def pop(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def titik_kota(d, x, y, nama, alpha=1.0, warna=(255, 200, 60), dy=50, uk=40, t=0.0, dx=0):
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    r = 13 + 3 * math.sin(t * 5)
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=PUTIH + (a,), width=4)
    if nama:
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


def pita(img, y, isi, warna_garis=(170, 30, 20), uk=54, alpha=1.0, x0=80, x1=1000, tinggi=110):
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((x0, y - tinggi / 2, x1, y + tinggi / 2), 30, fill=(247, 236, 208, 242),
                         outline=tuple(warna_garis) + (255,), width=6)
    se.tempel(img, lap, alpha)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, ((x0 + x1) / 2, y), isi, uk, warna_garis, nama_font="caption", alpha=alpha)


def tag_nama(img, cx, cy, isi, s=1.0, alpha=1.0, warna=(200, 52, 44), uk=64, sudut=0, coret=0.0):
    if alpha <= 0.01 or s <= 0.01:
        return
    f = se.font("caption", uk)
    lw = int(f.getlength(isi)) + 70
    lh = uk + 50
    lap = Image.new("RGBA", (lw + 20, lh + 20), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((10, 10, lw + 10, lh + 10), 16, fill=tuple(warna) + (250,), outline=(40, 10, 5, 255), width=5)
    dl.ellipse((22, lh / 2 + 2, 38, lh / 2 + 18), fill=(247, 236, 208, 255))
    dl.text((lw / 2 + 22, lh / 2 + 10), isi, font=f, fill=PUTIH, anchor="mm")
    if coret > 0:
        dl.line((30, lh / 2 + 10, 30 + (lw - 20) * coret, lh / 2 + 10), fill=(255, 220, 40, 255),
                width=max(6, uk // 7))
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, alpha, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


def ledakan(d, x, y, r, alpha=1.0, seed=0):
    if alpha <= 0.01 or r <= 1:
        return
    rng = random.Random(seed)
    n = 14
    pts = []
    for i in range(n * 2):
        ang = i * math.pi / n
        rr = r * (1.0 if i % 2 == 0 else 0.5) * rng.uniform(0.85, 1.1)
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    d.polygon(pts, fill=(255, 120, 30, int(220 * alpha)))
    d.ellipse((x - r * 0.35, y - r * 0.35, x + r * 0.35, y + r * 0.35), fill=(255, 230, 120, int(240 * alpha)))


# ------------------------------------------------------------------ ilustrasi kendaraan

def kuda(d, x, y, s=1.0, alpha=1.0, t=0.0, warna=(120, 75, 40)):
    """Kuda tampak samping menghadap kanan. (x, y) = titik tapak kaki."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    w = tuple(warna) + (a,)
    g = math.sin(t * 11) * 16 * s
    for i, kx in enumerate((-42, -28, 30, 44)):
        ayun = g if i % 2 == 0 else -g
        d.line((x + kx * s, y - 62 * s, x + kx * s + ayun, y), fill=w, width=max(2, int(9 * s)))
    d.ellipse((x - 58 * s, y - 100 * s, x + 58 * s, y - 52 * s), fill=w)
    d.polygon([(x + 36 * s, y - 92 * s), (x + 60 * s, y - 150 * s), (x + 80 * s, y - 145 * s),
               (x + 58 * s, y - 80 * s)], fill=w)
    d.polygon([(x + 58 * s, y - 152 * s), (x + 100 * s, y - 128 * s), (x + 94 * s, y - 116 * s),
               (x + 60 * s, y - 128 * s)], fill=w)
    d.line((x - 56 * s, y - 88 * s, x - 76 * s, y - 50 * s), fill=(50, 30, 15, a), width=max(2, int(7 * s)))
    d.line((x + 58 * s, y - 150 * s, x + 50 * s, y - 112 * s), fill=(50, 30, 15, a), width=max(2, int(7 * s)))


def trem(d, x, y, s=1.0, jenis="listrik", alpha=1.0, t=0.0, kabel_y=None, siluet=False):
    """Trem tampak samping menghadap kanan. (x, y) = tengah gerbong di permukaan rel."""
    if alpha <= 0.01 or s <= 0.01:
        return
    a = int(255 * alpha)
    warna = {"kuda": HIJAU_T, "uap": (110, 62, 36), "listrik": (190, 48, 40)}[jenis]
    if siluet:
        warna = (230, 220, 190)
    gelap = (35, 25, 18, a)
    L = 300 * s
    x0, x1 = x - L / 2, x + L / 2
    # tiang listrik (trolley pole)
    if jenis == "listrik":
        ky = kabel_y if kabel_y is not None else y - 300 * s
        d.line((x - 30 * s, y - 172 * s, x + 70 * s, ky), fill=gelap, width=max(2, int(6 * s)))
        d.ellipse((x + 62 * s, ky - 8 * s, x + 78 * s, ky + 8 * s), fill=gelap)
    d.polygon([(x0 - 12 * s, y - 150 * s), (x1 + 12 * s, y - 150 * s), (x1 - 10 * s, y - 174 * s),
               (x0 + 10 * s, y - 174 * s)], fill=(70, 60, 55, a) if not siluet else (240, 235, 215, a))
    d.rounded_rectangle((x0, y - 152 * s, x1, y - 34 * s), int(12 * s), fill=tuple(warna) + (a,),
                        outline=gelap, width=max(2, int(4 * s)))
    d.rectangle((x0 + 4 * s, y - 82 * s, x1 - 4 * s, y - 68 * s), fill=(240, 225, 185, a))
    for i in range(5):
        wx = x0 + 22 * s + i * 54 * s
        d.rectangle((wx, y - 138 * s, wx + 40 * s, y - 94 * s),
                    fill=(200, 225, 235, a) if not siluet else (255, 250, 230, a))
    rot = t * 6
    for wx in (x0 + 62 * s, x1 - 62 * s):
        r = 21 * s
        d.ellipse((wx - r, y - 21 * s - r, wx + r, y - 21 * s + r), fill=(40, 40, 45, a))
        for k in range(3):
            ang = rot + k * math.pi / 3
            d.line((wx - r * math.cos(ang), y - 21 * s - r * math.sin(ang), wx + r * math.cos(ang),
                    y - 21 * s + r * math.sin(ang)), fill=(150, 150, 150, a), width=max(1, int(3 * s)))
    if jenis == "uap":
        d.rounded_rectangle((x1 + 8 * s, y - 130 * s, x1 + 120 * s, y - 34 * s), int(8 * s), fill=(50, 45, 45, a),
                            outline=gelap, width=max(2, int(3 * s)))
        d.rectangle((x1 + 84 * s, y - 190 * s, x1 + 106 * s, y - 130 * s), fill=(40, 35, 35, a))
        d.rectangle((x1 + 78 * s, y - 198 * s, x1 + 112 * s, y - 188 * s), fill=(40, 35, 35, a))
        for wx in (x1 + 40 * s, x1 + 92 * s):
            r = 17 * s
            d.ellipse((wx - r, y - 18 * s - r, wx + r, y - 18 * s + r), fill=(40, 40, 45, a))
    if jenis == "kuda":
        d.line((x1, y - 70 * s, x1 + 110 * s, y - 100 * s), fill=gelap, width=max(2, int(4 * s)))
        kuda(d, x1 + 150 * s, y, 0.95 * s, alpha, t + 0.4, (95, 58, 30))
        kuda(d, x1 + 118 * s, y, 0.95 * s, alpha, t, (130, 82, 45))


def asap(d, x, y, t, alpha=1.0, s=1.0, n=7):
    for i in range(n):
        k = ((t * 0.9 + i / n) % 1.0)
        r = (18 + 60 * k) * s
        px = x - 90 * k * s * 2 + math.sin(i * 3 + t) * 10
        py = y - 260 * k * s
        a = int(170 * (1 - k) * alpha)
        d.ellipse((px - r, py - r, px + r, py + r), fill=(90, 85, 85, a))


def bus(d, x, y, s=1.0, alpha=1.0, warna=(40, 90, 160)):
    if alpha <= 0.01 or s <= 0.01:
        return
    a = int(255 * alpha)
    d.rounded_rectangle((x - 150 * s, y - 140 * s, x + 150 * s, y - 32 * s), int(22 * s), fill=tuple(warna) + (a,),
                        outline=(25, 25, 35, a), width=max(2, int(4 * s)))
    for i in range(5):
        wx = x - 130 * s + i * 50 * s
        d.rectangle((wx, y - 125 * s, wx + 38 * s, y - 88 * s), fill=(210, 230, 240, a))
    d.rectangle((x + 118 * s, y - 125 * s, x + 142 * s, y - 60 * s), fill=(210, 230, 240, a))
    d.rectangle((x - 146 * s, y - 76 * s, x + 146 * s, y - 66 * s), fill=(245, 240, 225, a))
    for wx in (x - 90 * s, x + 90 * s):
        r = 22 * s
        d.ellipse((wx - r, y - 30 * s - r, wx + r, y - 30 * s + r), fill=(30, 30, 35, a))


# ------------------------------------------------------------------ latar jalan & penampang

def gedung_kolonial(d, alpha=1.0, y_dasar=860, warna=(200, 175, 130)):
    a = int(255 * alpha)
    rng = random.Random(4)
    x = -20
    while x < W:
        lw = rng.randint(130, 200)
        tg = rng.randint(170, 280)
        d.rectangle((x, y_dasar - tg, x + lw, y_dasar), fill=tuple(warna) + (a,), outline=(110, 85, 55, a), width=3)
        d.polygon([(x - 8, y_dasar - tg), (x + lw / 2, y_dasar - tg - 50), (x + lw + 8, y_dasar - tg)],
                  fill=(170, 80, 50, a))
        for wx in range(x + 22, x + lw - 30, 46):
            d.rectangle((wx, y_dasar - tg + 40, wx + 24, y_dasar - tg + 90), fill=(90, 70, 50, a))
            if tg > 210:
                d.rectangle((wx, y_dasar - tg + 120, wx + 24, y_dasar - tg + 170), fill=(90, 70, 50, a))
        x += lw + rng.randint(10, 40)


def jalan(img, y_rel=1010):
    d = ImageDraw.Draw(img, "RGBA")
    gedung_kolonial(d)
    d.rectangle((0, 860, W, 1130), fill=(160, 132, 95, 255))
    d.line((0, 860, W, 860), fill=(110, 85, 55, 255), width=4)
    for yy in (y_rel - 2, y_rel + 10):
        d.line((0, yy, W, yy), fill=(95, 95, 105, 255), width=6)
    return d


def rel_samping(d, x0, x1, y, alpha=1.0, emas=0.0):
    a = int(255 * alpha)
    for sx in range(int(x0) - (int(x0) % 64), int(x1), 64):
        if x0 <= sx <= x1 - 20:
            d.rectangle((sx, y + 12, sx + 30, y + 44), fill=(110, 72, 38, a), outline=(60, 38, 18, a), width=2)
    warna = tuple(int(lerp(c1, c2, emas)) for c1, c2 in zip((120, 120, 130), (255, 205, 80)))
    d.rectangle((x0, y - 10, x1, y + 12), fill=warna + (a,), outline=(40, 40, 45, a), width=3)
    d.line((x0 + 4, y - 4, x1 - 4, y - 4), fill=(235, 235, 240, int(a * 0.6)), width=3)


def penampang(t, gali=0.0, timbun=0.0, emas=0.0, gelap=True, hantu=0.0):
    """Penampang jalan: kota di atas, aspal, tanah, rel trem di dalam tanah.
    gali: 0..1 lebar lubang galian (rel kelihatan di dalamnya). timbun: 0..1 aspal menutup rel dari kiri."""
    img = (LATAR_GELAP if gelap else LATAR).copy()
    d = ImageDraw.Draw(img, "RGBA")
    gedung_kolonial(d, 1.0, 760, (60, 70, 95) if gelap else (200, 175, 130))
    if hantu > 0:
        trem(d, 540 + math.sin(t * 1.5) * 20, 760, 0.9, "listrik", 0.42 * hantu, t, kabel_y=625, siluet=True)
        d.line((0, 625, W, 625), fill=(230, 220, 190, int(110 * hantu)), width=3)
    y_rel = 930
    d.rectangle((0, 820, W, 1330), fill=TANAH + (255,))
    rng = random.Random(9)
    for _ in range(260):
        x, y = rng.uniform(0, W), rng.uniform(830, 1320)
        r = rng.uniform(2, 7)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(95, 66, 38, 255))
    d.rectangle((0, 760, W, 822), fill=ASPAL + (255,))
    for xx in range(30, W, 140):
        d.rectangle((xx, 786, xx + 70, 796), fill=(230, 230, 220, 200))
    if gali > 0:
        lw = 860 * gali
        gx0, gx1 = 540 - lw / 2, 540 + lw / 2
        d.polygon([(gx0 - 30, 760), (gx1 + 30, 760), (gx1, 1010), (gx0, 1010)], fill=(62, 42, 24, 255))
        se.glow(img, 540, y_rel, int(80 + 340 * gali), (255, 200, 90), 0.8 * emas)
        d = ImageDraw.Draw(img, "RGBA")
        rel_samping(d, gx0 + 10, gx1 - 10, y_rel, 1.0, emas)
    if timbun > 0 or (gali == 0 and timbun == 0):
        pass
    if timbun > 0:
        rel_samping(d, 0, W, y_rel, 1.0, emas)
        xt = W * timbun
        d.rectangle((0, 860, xt, 1010), fill=(70, 55, 40, 255))
        rel_samping(d, 0, xt, 930, 0.75, emas)
        d.rectangle((0, 760, xt, 860), fill=ASPAL + (255,))
        for xx in range(30, int(xt) - 60, 140):
            d.rectangle((xx, 786, xx + 70, 796), fill=(230, 230, 220, 200))
        # truk aspal kecil di ujung timbunan
        if timbun < 1:
            d.rounded_rectangle((xt - 20, 640, xt + 170, 760), 14, fill=(230, 170, 30, 255), outline=(40, 30, 20, 255),
                                width=4)
            d.rectangle((xt + 110, 660, xt + 160, 710), fill=(200, 225, 235, 255))
            for wx in (xt + 20, xt + 130):
                d.ellipse((wx - 24, 716, wx + 24, 764), fill=(30, 30, 35, 255))
    return img, ImageDraw.Draw(img, "RGBA")


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img, d = penampang(c.t, gali=1.0, emas=0.75 + 0.25 * math.sin(c.t * 4), hantu=1.0)
    se.teks(d, (540, 405), "JAKARTA PERNAH", 112, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 520), "PUNYA TREM!", 124, KUNING, nama_font="caption", stroke=11, stroke_warna=GELAP)
    a1 = c.p(0.16, 0.22)
    stempel(img, "DIKUBUR!", 540, 1095, 0.95 * pop(c, 0.16) * (1 if a1 > 0 else 0), uk=86, sudut=-7)
    a2 = c.p(0.4, 0.46)
    if a2 > 0:
        pita(img, 1250, "26 Nov · Hari Transportasi Berkelanjutan", uk=42, alpha=a2, warna_garis=(30, 110, 60))
    d = ImageDraw.Draw(img, "RGBA")
    label(d, (540, 1060), "rel trem", 44, alpha=1 - c.p(0.12, 0.16))
    hdr(img, "Jakarta tempo doeloe", alpha=c.p(0.85, 0.95))
    return img


def a_temuan(c):
    g = 0.15 + 0.85 * c.p(0.08, 0.45)
    img, d = penampang(c.t, gali=g, emas=c.p(0.35, 0.5), gelap=False)
    # tanah beterbangan selama digali
    if c.p(0.08, 0.45) < 1:
        rng = random.Random(int(c.t * 12))
        for _ in range(14):
            x = 540 + rng.uniform(-400, 400) * g
            y = 760 - rng.uniform(0, 160)
            r = rng.uniform(5, 12)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(95, 66, 38, 230))
    se.kartu(img, 540, 450, "Desember 2021 · proyek MRT", "galian Glodok – Kota, Jakarta", BIRU,
             alpha=c.p(0.0, 0.06), tiang=False, skala=pop(c, 0.0) * 1.15)
    a = c.p(0.42, 0.5)
    if a > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.garis_putus(d, [(300, 1120), (380, 1010), (420, 960)], c.p(0.42, 0.52), (200, 40, 30), tebal=7)
        label(d, (300, 1160), "rel trem zaman Belanda!", 46, alpha=a)
    b = c.p(0.72, 0.78)
    if b > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1265), "KOK DIKUBUR?", int(100 * pop(c, 0.72)) + 1, KUNING, nama_font="caption", stroke=10,
                stroke_warna=GELAP, alpha=b)
    hdr(img, "Ditemukan di bawah aspal")
    return img


def a_kuda(c):
    kamera = se.kamera_antara(cam(-6.175, 106.835, 1.0), cam(-6.158, 106.824, 1.6), c.p(0.0, 0.4))
    img = se.render_peta(BAT, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    sung = [layar(kamera, ll) for ll in CILIWUNG]
    d.line(sung, fill=(70, 120, 170, 200), width=10, joint="curve")
    label(d, layar(kamera, (-6.118, 106.86)), "Teluk Jakarta", 38, alpha=c.p(0.05, 0.15))
    titik = [layar(kamera, ll) for ll in RUTE_KUDA]
    k = c.p(0.25, 0.7)
    se.garis_putus(d, titik, k, (46, 110, 70), tebal=8, putus=18, celah=10, panah=False)
    kx, ky = layar(kamera, KOTA)
    titik_kota(d, kx, ky, "Kota lama", c.p(0.2, 0.28), dy=-52, t=c.t)
    wx, wy = layar(kamera, WELTEVREDEN)
    titik_kota(d, wx, wy, "Weltevreden", c.p(0.6, 0.68), dy=52, dx=40, t=c.t)
    if k > 0.02:
        (px, py), _ = se.titik_di_jalur(titik, k)
        trem(d, px, py + 10, 0.5, "kuda", 1.0, c.t)
    se.kartu(img, 540, 450, "20 April 1869", "trem pertama Batavia", HIJAU_T, alpha=c.p(0.0, 0.06), tiang=False,
             skala=pop(c, 0.0) * 1.2)
    a = c.p(0.55, 0.62)
    if a > 0:
        pita(img, 1265, "3–4 ekor kuda · ± 40 penumpang", uk=48, alpha=a, warna_garis=(46, 110, 70))
    hdr(img, "Ditarik kuda!")
    return img


def a_masalah(c):
    img = LATAR.copy()
    d = jalan(img)
    x = lerp(-150, 760, c.p(0.0, 1.0))
    # kotoran berceceran di belakang trem
    rng = random.Random(3)
    for i in range(26):
        tx = rng.uniform(-100, 980)
        if tx < x - 280:
            ty = 1040 + rng.uniform(0, 60)
            r = rng.uniform(7, 12)
            d.ellipse((tx - r, ty - r * 0.7, tx + r, ty + r * 0.7), fill=(90, 60, 25, 255))
    trem(d, x, 1010, 1.0, "kuda", 1.0, c.t)
    n = int(round(lerp(0, 200, c.p(0.15, 0.45))))
    a = c.p(0.12, 0.18)
    if a > 0:
        se.teks(d, (540, 450), f"± {n}", 130, MERAH, nama_font="caption", stroke=10, stroke_warna=PUTIH, alpha=a)
        se.teks(d, (540, 555), "kuda mati tiap tahun", 52, TINTA, nama_font="judul", alpha=c.p(0.2, 0.26))
    b = c.p(0.62, 0.68)
    stempel(img, "BATAVIA BAU!", 540, 1250, 0.85 * pop(c, 0.62) * (1 if b > 0 else 0), uk=70, sudut=-6,
            warna=(120, 70, 20))
    hdr(img, "Masalahnya…")
    return img


def a_uap(c):
    img = LATAR.copy()
    d = jalan(img)
    x = lerp(-120, 640, c.p(0.0, 1.0))
    trem(d, x, 1010, 1.0, "uap", 1.0, c.t)
    asap(d, x + 150 + 95, 1010 - 200, c.t, 1.0, 1.0)
    se.kartu(img, 540, 450, "Awal 1880-an", "kuda diganti mesin uap", (110, 62, 36), alpha=c.p(0.0, 0.06),
             tiang=False, skala=pop(c, 0.0) * 1.2)
    d = ImageDraw.Draw(img, "RGBA")
    for i, (isi, s0) in enumerate([("berisik", 0.42), ("berasap", 0.52)]):
        a = c.p(s0, s0 + 0.06)
        if a > 0:
            tag_nama(img, 300 + i * 480, 600, isi, 0.9 * pop(c, s0), a, warna=(90, 80, 75), uk=54,
                     sudut=-5 + i * 9)
    b = c.p(0.66, 0.72)
    if b > 0:
        d = ImageDraw.Draw(img, "RGBA")
        ledakan(d, x + 245, 810, (90 + 12 * math.sin(c.t * 12)) * back_out(c.p(0.66, 0.76)), b, seed=2)
        pita(img, 1250, "Ketelnya bisa meledak!", uk=58, alpha=b)
    hdr(img, "Ganti tenaga uap")
    return img


def a_listrik(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    gedung_kolonial(d, 1.0, 1000, (60, 70, 95))
    d.rectangle((0, 1000, W, 1130), fill=(70, 70, 80, 255))
    for yy in (1000, 1012):
        d.line((0, yy, W, yy), fill=(140, 140, 150, 255), width=6)
    ky = 600
    d.line((0, ky, W, ky), fill=(200, 200, 210, 255), width=4)
    for tx in (120, 960):
        d.line((tx, ky - 20, tx, 1000), fill=(50, 50, 60, 255), width=12)
    x = lerp(220, 600, c.p(0.0, 1.0))
    on = c.p(0.28, 0.34)
    if on > 0:
        se.glow(img, x + 70 * 1.0, ky, 140, (150, 200, 255), on * (0.8 + 0.4 * math.sin(c.t * 25)))
        d = ImageDraw.Draw(img, "RGBA")
        rng = random.Random(int(c.t * 20))
        for _ in range(5):
            ang = rng.uniform(0, 2 * math.pi)
            r = rng.uniform(20, 55)
            d.line((x + 70, ky, x + 70 + r * math.cos(ang), ky + r * math.sin(ang)), fill=(220, 240, 255, int(255 * on)),
                   width=3)
    trem(d, x, 1000, 1.05, "listrik", 1.0, c.t, kabel_y=ky)
    a = c.p(0.0, 0.05) * (1 - c.p(0.26, 0.29))
    if a > 0:
        pita(img, 1250, "Tapi ini belum seberapa…", uk=56, alpha=a)
    b = c.p(0.3, 0.36)
    if b > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 450), "1899", int(150 * pop(c, 0.3)) + 1, KUNING, nama_font="caption", stroke=11,
                stroke_warna=GELAP, alpha=b)
        pita(img, 1250, "TREM LISTRIK!", uk=70, alpha=c.p(0.36, 0.42), warna_garis=BIRU)
    c2 = c.p(0.66, 0.72)
    if c2 > 0:
        tag_nama(img, 300, 1150, "tanpa kuda", 0.75, c2, warna=HIJAU_T, uk=50, sudut=-5)
        tag_nama(img, 790, 1150, "tanpa asap", 0.75, c.p(0.74, 0.8), warna=(90, 80, 75), uk=50, sudut=5)
    hdr(img, "Masih zaman Belanda")
    return img


def gambar_jaringan(d, kamera, k_list, alpha=1.0, mati=0.0):
    for i, (pts, w) in enumerate(JALUR):
        k = k_list[i] if isinstance(k_list, list) else k_list
        if k <= 0:
            continue
        titik = [layar(kamera, ll) for ll in pts]
        warna = tuple(int(lerp(a, b, mati)) for a, b in zip(w, (110, 100, 90)))
        se.garis_putus(d, titik, k, warna, tebal=11, putus=1000, celah=1, panah=False, alpha=alpha)


KAM_JARINGAN = cam(-6.181, 106.838, 1.3)


def label_halte(d, kamera, alpha=1.0, t=0.0):
    for nama, ll, dy, dx in [("Kota", KOTA, 4, 80), ("Harmoni", HARMONI, 0, -120), ("Senen", SENEN, -8, 108),
                             ("Tanah Abang", TANAHABANG, 48, -40), ("Jatinegara", JATINEGARA, 52, 0)]:
        x, y = layar(kamera, ll)
        titik_kota(d, x, y, "", alpha, t=t)
        label(d, (x + dx, y + dy), nama, 40, alpha=alpha)


def a_jaringan(c):
    kamera = Kamera(*KAM_JARINGAN)
    img = se.render_peta(BAT, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    sung = [layar(kamera, ll) for ll in CILIWUNG]
    d.line(sung, fill=(70, 120, 170, 170), width=9, joint="curve")
    ks = [c.p(0.12 + i * 0.1, 0.3 + i * 0.1) for i in range(5)]
    gambar_jaringan(d, kamera, ks)
    label_halte(d, kamera, c.p(0.1, 0.2), c.t)
    se.kartu(img, 540, 450, "1934 · paling luas", "5 jalur trem listrik", MERAH, alpha=c.p(0.0, 0.06),
             tiang=False, skala=pop(c, 0.0) * 1.2)
    km = int(round(lerp(0, 41, c.p(0.3, 0.75))))
    a = c.p(0.28, 0.34)
    if a > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (250, 1215), f"± {km} km", 92, MERAH, nama_font="caption", stroke=9, stroke_warna=PUTIH, alpha=a)
    hdr(img, "Puncak kejayaan", alpha=1.0)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, (850, 640), "jalur disederhanakan", 30, (90, 70, 50), alpha=c.p(0.2, 0.3))
    return img


def a_ppd(c):
    img = LATAR.copy()
    se.glow(img, 540, 820, 420, (255, 210, 120), 0.5)
    se.kartu(img, 540, 450, "Setelah merdeka", "trem diambil alih Indonesia", MERAH, alpha=c.p(0.0, 0.06),
             tiang=False, skala=pop(c, 0.0) * 1.2)
    tag_nama(img, 540, 640, "BVM · perusahaan Belanda", 0.9, 1.0 - 0.5 * c.p(0.45, 0.55), warna=(110, 90, 70),
             uk=56, sudut=-3, coret=c.p(0.2, 0.32))
    a = c.p(0.3, 0.38)
    if a > 0:
        y = lerp(560, 840, back_out(c.p(0.3, 0.4)))
        tag_nama(img, 540, y, "PPD · 1957", 1.2, a, warna=(205, 30, 30), uk=86, sudut=3)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 960), "Pengangkutan Penumpang Djakarta", 44, TINTA, nama_font="tangan", alpha=c.p(0.38, 0.46))
    b = c.p(0.62, 0.7)
    if b > 0:
        d = ImageDraw.Draw(img, "RGBA")
        bus(d, lerp(1250, 540, back_out(c.p(0.62, 0.74))), 1200, 0.85, b, warna=(40, 90, 160))
        se.teks(d, (540, 1270), "masih ada sampai sekarang!", 44, (150, 40, 30), nama_font="judul",
                alpha=c.p(0.72, 0.78))
    hdr(img, "Ganti pemilik")
    return img


def a_dikubur(c):
    fase_b = c.p(0.7, 0.75)
    if fase_b < 1:
        kamera = Kamera(*KAM_JARINGAN)
        img = se.render_peta(BAT, kamera)
        d = ImageDraw.Draw(img, "RGBA")
        # kota makin padat: titik-titik rumah & kendaraan
        rng = random.Random(11)
        n = int(lerp(20, 420, c.p(0.05, 0.35)))
        for i in range(n):
            x, y = rng.uniform(40, 1040), rng.uniform(560, 1320)
            r = rng.uniform(4, 9)
            d.rectangle((x - r, y - r, x + r, y + r), fill=(110, 90, 70, 200))
        mati = c.p(0.45, 0.6)
        gambar_jaringan(d, kamera, 1.0, alpha=1.0 - 0.6 * mati, mati=mati)
        label_halte(d, kamera, 1.0, c.t)
        se.kartu(img, 540, 450, "± 1960 · Jakarta makin padat", "trem dinilai nggak cocok lagi", MERAH,
                 alpha=c.p(0.0, 0.06), tiang=False, skala=pop(c, 0.0) * 1.15)
        a = c.p(0.47, 0.55)
        if a > 0:
            d = ImageDraw.Draw(img, "RGBA")
            for i, ll in enumerate([SENEN, HARMONI, KRAMAT]):
                x, y = layar(kamera, ll)
                bus(d, x + 40, y + 40, 0.38 * back_out(c.p(0.47 + i * 0.04, 0.57 + i * 0.04)), a)
            pita(img, 1250, "Ditutup bertahap, diganti bus", uk=50, alpha=a)
        if fase_b > 0:
            hitam = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fase_b)))
            img.alpha_composite(hitam)
        hdr(img, "Kenapa hilang?")
        return img
    img, d = penampang(c.t, timbun=0.05 + 0.95 * c.p(0.76, 0.9), emas=0.4, gelap=False)
    se.kartu(img, 540, 450, "Relnya nggak dibongkar", "cukup ditimbun aspal", COKLAT, alpha=c.p(0.75, 0.8),
             tiang=False, skala=pop(c, 0.75) * 1.15)
    b = c.p(0.9, 0.94)
    stempel(img, "BIAR HEMAT!", 540, 1200, 0.9 * pop(c, 0.9, 0.06) * (1 if b > 0 else 0), uk=78, sudut=-6)
    hdr(img, "Kenapa hilang?")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    img, d = penampang(c.t, gali=1.0, emas=0.8, hantu=1.0)
    se.tint(img, (10, 6, 0), 0.55)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 470, 990, 1080), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 550), "Rel di bawah galian MRT itu", 46, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 620), "sisa trem yang dikubur", 46, TINTA, nama_font="judul", alpha=a)
        trem(d, 540, 900, 0.95, "listrik", a, c.t, kabel_y=700)
        d.line((140, 700, 940, 700), fill=(60, 60, 70, int(255 * a)), width=3)
        se.teks(d, (540, 1000), "1869 – ± 1962", 64, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Jakarta pernah punya trem. Terus relnya dikubur. Pas banget buat Hari Transportasi "
                   "Berkelanjutan Sedunia hari ini.",
           a_hook, transisi=False),
    Adegan("temuan", "Desember dua ribu dua puluh satu, proyek MRT menggali di Glodok. Di bawah aspal, nongol rel "
                     "trem zaman Belanda. Kok bisa dikubur?", a_temuan),
    Adegan("kuda", "Mundur ke delapan belas enam puluh sembilan. Trem pertama Batavia ditarik kuda! Tiga "
                   "sampai empat ekor, bawa sekitar empat puluh penumpang.", a_kuda),
    Adegan("masalah", "Masalahnya, kuda gampang capek. Kabarnya, sekitar dua ratus kuda mati tiap tahun. "
                      "Kotorannya? Berceceran di jalan.", a_masalah),
    Adegan("uap", "Awal delapan belas delapan puluhan, kuda diganti mesin uap. Lebih kuat, tapi berisik, "
                  "berasap, dan ketelnya bisa meledak.", a_uap),
    Adegan("listrik", "Tapi ini belum seberapa. Tahun delapan belas sembilan puluh sembilan, trem listrik mulai "
                      "jalan di Batavia. Tanpa kuda, tanpa asap.", a_listrik, transisi=False),
    Adegan("jaringan", "Puncaknya tahun sembilan belas tiga puluh empat. Lima jalur trem listrik, sekitar empat "
                       "puluh satu kilometer. Dari Kota sampai Jatinegara.", a_jaringan),
    Adegan("ppd", "Setelah merdeka, trem diambil alih. Tahun sembilan belas lima puluh tujuh, pengelolanya jadi "
                  "PPD. Iya, PPD yang busnya masih ada sampai sekarang.", a_ppd),
    Adegan("dikubur", "Terus kenapa dikubur? Jakarta makin padat. Sekitar tahun sembilan belas enam puluh, Bung "
                      "Karno menilai trem nggak cocok lagi buat Jakarta. Jalurnya ditutup bertahap, diganti bus. "
                      "Relnya nggak dibongkar, cukup ditimbun aspal. Biar hemat.", a_dikubur),
    Adegan("penutup", "Jadi, rel di galian MRT itu sisa trem yang dulu dikubur. Kamu mau trem balik "
                      "lagi? Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
