"""Shorts ±88 detik: Bandara Kemayoran (1940–1985), landasan yang sekarang jadi jalan raya.

Tiga jenis visual: (1) peta Teluk Jakarta dekat (Soetta, Kemayoran, Halim),
(2) peta Asia Tenggara (rute ilustratif), (3) ilustrasi tampak atas landasan/jalan + menara ATC.
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

NAMA_FILE = "bandara-kemayoran-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "BANDARA KEMAYORAN"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU = (30, 80, 150)
ASPAL = (70, 72, 78)
ABU = (60, 60, 70)
EMAS_T = (255, 214, 120)

# ------------------------------------------------------------------ peta Teluk Jakarta (dekat)

DARAT = [(-5.98, 106.45), (-6.0, 106.55), (-6.01, 106.67), (-6.06, 106.72), (-6.105, 106.77), (-6.11, 106.79),
         (-6.122, 106.808), (-6.123, 106.84), (-6.1, 106.885), (-6.1, 106.93), (-6.095, 106.96), (-6.03, 107.0),
         (-5.93, 107.03), (-5.95, 107.25), (-6.65, 107.25), (-6.65, 106.45)]

print("  menyiapkan peta Teluk Jakarta...")
TELUK = Peta(106.45, 107.25, -6.65, -5.85, 2400, [], [(-6.6, 106.8, 0.08), (-6.62, 106.95, 0.07)],
             seed=22, darat=[DARAT])

SOETTA = (-6.1256, 106.6559)
KEMAYORAN = (-6.150, 106.848)
HALIM = (-6.2666, 106.8909)
MONAS = (-6.1754, 106.8272)

print("  menyiapkan peta Asia Tenggara...")
ASIA = Peta(92, 128, -30, 25, 90, [], [(-2, 114, 1.5), (0, 101, 1.2), (14, 106, 2), (-7.5, 110, 0.6)],
            seed=8, darat=pd.SEMUA)
JKT = (-6.15, 106.85)
TUJUAN = {"Singapura": (1.35, 103.82), "Medan": (3.6, 98.67), "Bangkok": (13.75, 100.5),
          "Denpasar": (-8.7, 115.2), "Makassar": (-5.1, 119.4)}


# ------------------------------------------------------------------ helper

def cam(lat, lon, zoom, p=TELUK):
    x, y = p.px(lat, lon)
    return (x, y, zoom)


def peta(kamera, p=TELUK):
    img = se.render_peta(p, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(kamera, ll, p=TELUK):
    return kamera.layar(*p.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def hdr(img, sub="1940 – 1985", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def angka_besar(d, xy, isi, uk, warna=PUTIH, alpha=1.0, stroke_warna=(10, 20, 40)):
    se.teks(d, xy, isi, uk, warna, nama_font="caption", stroke=10, stroke_warna=stroke_warna, alpha=alpha)


def pesawat(d, x, y, s=1.0, sudut=0.0, a=1.0, warna=(240, 240, 245), garis=(40, 40, 50)):
    """Pesawat tampak atas, hidung ke arah `sudut` (radian, 0 = kanan)."""
    if a <= 0.01:
        return
    A = int(255 * a)
    ca, sa = math.cos(sudut), math.sin(sudut)

    def r(px, py):
        return (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)

    badan = [(-50, -6), (40, -7), (56, 0), (40, 7), (-50, 6), (-56, 0)]
    sayap = [(-2, -6), (14, -6), (-10, -52), (-20, -52)]
    sayap2 = [(-2, 6), (14, 6), (-10, 52), (-20, 52)]
    ekor = [(-46, -5), (-38, -5), (-52, -20), (-58, -20)]
    ekor2 = [(-46, 5), (-38, 5), (-52, 20), (-58, 20)]
    for poli in (sayap, sayap2, ekor, ekor2, badan):
        d.polygon([r(*p) for p in poli], fill=tuple(warna) + (A,), outline=tuple(garis) + (A,))


def pin(d, x, y, warna=MERAH, alpha=1.0, s=1.0):
    a = int(255 * alpha)
    if a <= 2:
        return
    d.ellipse((x - 16 * s, y - 52 * s, x + 16 * s, y - 20 * s), fill=tuple(warna) + (a,), outline=(40, 10, 10, a), width=3)
    d.polygon([(x - 12 * s, y - 30 * s), (x + 12 * s, y - 30 * s), (x, y)], fill=tuple(warna) + (a,))
    d.ellipse((x - 6 * s, y - 42 * s, x + 6 * s, y - 30 * s), fill=(255, 255, 255, a))


def ikon_bandara(d, x, y, alpha=1.0, warna=BIRU, s=1.0):
    a = int(255 * alpha)
    if a <= 2:
        return
    r = 30 * s
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=(255, 255, 255, a), width=4)
    pesawat(d, x, y, 0.42 * s, -math.pi / 2, alpha, (255, 255, 255), (255, 255, 255))


def rute(d, kamera, a_ll, b_ll, k, warna=BIRU, p=TELUK, lengkung=0.18, pesawat_ikut=True, tebal=6, s=0.7):
    """Rute melengkung bergaris putus + pesawat di ujungnya."""
    if k <= 0:
        return
    ax, ay = layar(kamera, a_ll, p)
    bx, by = layar(kamera, b_ll, p)
    mx, my = (ax + bx) / 2, (ay + by) / 2
    dx, dy = bx - ax, by - ay
    cx, cy = mx - dy * lengkung, my + dx * lengkung
    pts = []
    for i in range(41):
        f = i / 40
        pts.append(((1 - f) ** 2 * ax + 2 * (1 - f) * f * cx + f * f * bx,
                    (1 - f) ** 2 * ay + 2 * (1 - f) * f * cy + f * f * by))
    se.garis_putus(d, pts, k, warna, tebal=tebal, putus=16, celah=11, panah=False)
    if pesawat_ikut and k < 0.999:
        n = max(1, int(40 * k))
        x0, y0 = pts[n - 1]
        x1, y1 = pts[n]
        pesawat(d, x1, y1, s, math.atan2(y1 - y0, x1 - x0))


# ------------------------------------------------------------------ ilustrasi tampak atas: landasan / jalan

print("  menyiapkan latar tampak atas...")
_RUMPUT = se.latar_tekstur(W, H, 44, warna=(150, 160, 105)).convert("RGBA")
_KOTA = se.latar_tekstur(W, H, 45, warna=(196, 178, 140)).convert("RGBA")
X0, X1 = 360, 720  # tepi landasan
CX = (X0 + X1) // 2


def _landasan(d):
    d.rectangle((X0, 0, X1, H), fill=ASPAL + (255,))
    d.rectangle((X0 + 10, 0, X0 + 16, H), fill=(235, 235, 235, 255))
    d.rectangle((X1 - 16, 0, X1 - 10, H), fill=(235, 235, 235, 255))
    for y in range(0, H, 140):
        d.rectangle((CX - 5, y, CX + 5, y + 80), fill=(240, 240, 240, 255))
    # piano keys + nomor landasan (17 di atas, 35 di bawah — kebalik arah baca)
    for i in range(8):
        x = X0 + 30 + i * 40
        d.rectangle((x, 1250, x + 22, 1370), fill=(240, 240, 240, 255))
    se.teks(d, (CX, 1180), "35", 90, (240, 240, 240), nama_font="judul")


def _jalan(d, t, mobil=True):
    d.rectangle((X0, 0, X1, H), fill=(58, 60, 66, 255))
    d.rectangle((CX - 22, 0, CX + 22, H), fill=(90, 140, 70, 255))  # median hijau
    for i in range(0, H, 90):
        d.ellipse((CX - 18, i, CX + 18, i + 36), fill=(60, 115, 50, 255))
    for xl in ((X0 + CX) // 2, (CX + X1) // 2):
        for y in range(0, H, 100):
            d.rectangle((xl - 4, y, xl + 4, y + 50), fill=(235, 235, 235, 255))
    if not mobil:
        return
    rng = random.Random(7)
    warna = [(200, 52, 44), (240, 240, 240), (40, 90, 160), (230, 190, 40), (30, 30, 35), (150, 150, 160)]
    for jalur, arah in (((X0 + 45), 1), ((X0 + 135), 1), ((CX + 45), -1), ((CX + 135), -1)):
        for j in range(5):
            v = rng.uniform(170, 260)
            y = (rng.uniform(0, H + 300) + arah * t * v) % (H + 300) - 150
            w = rng.choice(warna)
            d.rounded_rectangle((jalur - 26, y - 46, jalur + 26, y + 46), 10, fill=w + (255,), outline=(20, 20, 20, 255),
                                width=3)
            d.rectangle((jalur - 20, y - 26 * arah - 10, jalur + 20, y - 26 * arah + 10), fill=(120, 170, 200, 255))


def tampak_atas(t, jalan_k=0.0, kota=0.0, mobil=True):
    """jalan_k 0 = landasan pesawat (rumput), 1 = jalan raya (kota). kota 0..1 = rumah mengepung."""
    a = _RUMPUT.copy()
    _landasan(ImageDraw.Draw(a, "RGBA"))
    if kota > 0.01:
        d = ImageDraw.Draw(a, "RGBA")
        rng = random.Random(3)
        for i in range(260):
            x = rng.uniform(-20, W + 20)
            if X0 - 30 < x < X1 + 30:
                continue
            y = rng.uniform(-20, H + 20)
            jarak = min(abs(x - X0), abs(x - X1)) / 360  # 0 dekat landasan
            if clamp(kota * 1.6 - (1 - jarak) * 0.9) <= 0:
                continue
            w, h = rng.uniform(26, 50), rng.uniform(22, 40)
            atap = rng.choice([(170, 80, 50), (150, 70, 45), (120, 110, 100), (180, 100, 60)])
            d.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=atap + (255,), outline=(60, 35, 20, 255))
            d.line((x - w / 2, y, x + w / 2, y), fill=(90, 50, 30, 200), width=2)
    if jalan_k <= 0.01:
        return a
    b = _KOTA.copy()
    db = ImageDraw.Draw(b, "RGBA")
    rng = random.Random(11)
    for i in range(70):  # gedung di kiri-kanan jalan
        sisi = rng.choice((0, 1))
        x = rng.uniform(20, X0 - 60) if sisi == 0 else rng.uniform(X1 + 60, W - 20)
        y = rng.uniform(0, H)
        w, h = rng.uniform(60, 130), rng.uniform(60, 140)
        g = rng.choice([(150, 150, 160), (175, 165, 150), (120, 130, 145), (200, 190, 175)])
        db.rectangle((x - w / 2 + 8, y - h / 2 + 10, x + w / 2 + 8, y + h / 2 + 10), fill=(0, 0, 0, 70))
        db.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=g + (255,), outline=(70, 70, 75, 255), width=3)
    _jalan(db, t, mobil)
    if jalan_k >= 0.99:
        return b
    return Image.blend(a, b, jalan_k)


def bayangan_pesawat(img, x, y, s, alpha=1.0):
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pesawat(ImageDraw.Draw(lap), x + 60, y + 90, s, -math.pi / 2, 1.0, (0, 0, 0), (0, 0, 0))
    se.tempel(img, lap, 0.35 * alpha)
    d = ImageDraw.Draw(img, "RGBA")
    pesawat(d, x, y, s, -math.pi / 2, alpha)


# ------------------------------------------------------------------ menara ATC

def _langit(atas=(110, 160, 215), bawah=(235, 215, 175)):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (np.array(atas, np.float32) * (1 - g) + np.array(bawah, np.float32) * g).repeat(W, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")


def menara(img, x, dasar, tinggi, a=1.0):
    d = ImageDraw.Draw(img, "RGBA")
    A = int(255 * a)
    top = dasar - tinggi
    d.polygon([(x - 70, dasar), (x + 70, dasar), (x + 45, top + 150), (x - 45, top + 150)], fill=(225, 220, 205, A),
              outline=(70, 60, 50, A))
    for yy in range(int(top + 200), dasar - 40, 70):
        d.rectangle((x - 12, yy, x + 12, yy + 30), fill=(70, 90, 110, A))
    # kabin kaca
    d.rectangle((x - 80, top + 140, x + 80, top + 160), fill=(200, 195, 180, A), outline=(70, 60, 50, A))
    d.polygon([(x - 95, top + 40), (x + 95, top + 40), (x + 80, top + 140), (x - 80, top + 140)], fill=(60, 110, 140, A),
              outline=(40, 40, 50, A))
    for i in range(-3, 4):
        d.line((x + i * 26, top + 42, x + i * 22, top + 138), fill=(30, 40, 50, A), width=4)
    d.rectangle((x - 100, top + 20, x + 100, top + 42), fill=(215, 210, 195, A), outline=(70, 60, 50, A))
    d.line((x, top + 20, x, top - 50), fill=(60, 60, 60, A), width=5)
    d.ellipse((x - 7, top - 58, x + 7, top - 44), fill=(220, 40, 30, A))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = tampak_atas(c.t, 1.0)
    se.tint(img, (15, 20, 35), 0.25)
    # pesawat raksasa "hantu" melintas di atas jalan
    py = lerp(1500, 520, c.p(0.0, 0.9))
    bayangan_pesawat(img, CX, py, 4.2, 0.85)
    d = ImageDraw.Draw(img, "RGBA")
    s = 0.88 + 0.12 * back_out(c.t / 0.35)
    angka_besar(d, (540, 470), "BANDARA", int(130 * s), EMAS_T, stroke_warna=(20, 15, 10))
    angka_besar(d, (540, 610), "JADI JALAN RAYA", int(100 * s), PUTIH, stroke_warna=(20, 15, 10))
    a = c.p(0.45, 0.55)
    if a > 0:
        se.kartu(img, 540, 1250, "1940 – 1985", "pesawat mendarat di sini", MERAH, alpha=a, tiang=False,
                 skala=back_out((c.t / c.d - 0.45) / 0.1))
    se.teks(d, (540, 1110), "dan menaranya… masuk komik dunia?", 46, (255, 225, 140), nama_font="caption", stroke=7,
            stroke_warna=(20, 15, 10), alpha=c.p(0.72, 0.8))
    hdr(img, alpha=c.p(0.85, 0.97))
    return img


def a_tren(c):
    kamera = se.kamera_antara(cam(-6.14, 106.72, 1.35), cam(-6.16, 106.84, 1.9), c.p(0.45, 0.8))
    img, d = peta(kamera)
    label(d, (540, 470), "Laut Jawa", 40, (220, 230, 240), c.p(0, 0.1) * (1 - c.p(0.45, 0.6)), "tangan")
    x, y = layar(kamera, SOETTA)
    ikon_bandara(d, x, y, c.p(0.02, 0.1))
    se.kartu(img, clamp(x, 280, 800), y - 50, "Soekarno-Hatta", "tersibuk ke-2 Asia Tenggara · 2026", BIRU,
             alpha=c.p(0.05, 0.13) * (1 - c.p(0.42, 0.5)), skala=back_out((c.t / c.d - 0.05) / 0.1))
    x, y = layar(kamera, MONAS)
    label(d, (x, y + 40), "Monas", 34, TINTA, c.p(0.6, 0.7))
    d.polygon([(x - 8, y), (x + 8, y), (x + 3, y - 40), (x - 3, y - 40)], fill=(240, 240, 240, int(255 * c.p(0.6, 0.7))),
              outline=(40, 30, 20, int(255 * c.p(0.6, 0.7))))
    x, y = layar(kamera, KEMAYORAN)
    a = c.p(0.62, 0.72)
    if a > 0:
        r = 50 + 12 * math.sin(c.t * 5)
        d.ellipse((x - r, y - r, x + r, y + r), outline=(200, 40, 30, int(255 * a)), width=7)
        ikon_bandara(d, x, y, a, MERAH)
        se.kartu(img, 540, y - 90, "KEMAYORAN", "di tengah kota", MERAH, alpha=a, tiang=False,
                 skala=back_out((c.t / c.d - 0.62) / 0.1))
    hdr(img, "Sebelum ada Soetta")
    return img


def a_1940(c):
    kamera = Kamera(*cam(-6.208, 106.87, 1.9))
    img, d = peta(kamera)
    kx, ky = layar(kamera, KEMAYORAN)
    hx, hy = layar(kamera, HALIM)
    # landasan dibangun
    k = c.p(0.05, 0.35)
    if k > 0:
        L = 230 * k
        d.line((kx, ky - 115, kx, ky - 115 + L), fill=ASPAL + (255,), width=26)
    ikon_bandara(d, kx, ky, c.p(0.3, 0.4), MERAH)
    label(d, (kx + 150, ky), "Kemayoran", 40, TINTA, c.p(0.05, 0.15))
    ikon_bandara(d, hx, hy, c.p(0.4, 0.5))
    label(d, (hx + 150, hy + 10), "Tjililitan", 40, TINTA, c.p(0.4, 0.5))
    se.teks(d, (hx + 150, hy + 52), "(sekarang Halim)", 28, (90, 70, 50), nama_font="tangan_tipis", alpha=c.p(0.45, 0.55))
    rute(d, kamera, HALIM, KEMAYORAN, c.p(0.55, 0.9), MERAH, lengkung=-0.25, s=0.9)
    s = back_out((c.t / c.d) / 0.12)
    angka_besar(d, (540, 470), "1934", int(110 * s) + 1, EMAS_T, alpha=1 - c.p(0.36, 0.42), stroke_warna=(30, 20, 10))
    se.teks(d, (540, 570), "mulai dibangun Belanda", 44, PUTIH, nama_font="caption", stroke=6, stroke_warna=(30, 20, 10),
            alpha=c.p(0.05, 0.12) * (1 - c.p(0.36, 0.42)))
    s2 = back_out((c.t / c.d - 0.4) / 0.12)
    if c.t / c.d > 0.4:
        angka_besar(d, (540, 470), "JULI 1940", int(110 * s2) + 1, EMAS_T, stroke_warna=(30, 20, 10))
    se.kartu(img, 540, 590, "DC-3 milik KNILM", "pesawat pertama yang mendarat", BIRU, alpha=c.p(0.6, 0.68),
             tiang=False, skala=back_out((c.t / c.d - 0.6) / 0.1))
    hdr(img, "1934 – 1940")
    return img


def a_internasional(c):
    kamera = se.kamera_antara(cam(2, 108.5, 0.52, ASIA), cam(2, 108.5, 0.48, ASIA), c.p(0.0, 1.0))
    img, d = peta(kamera, ASIA)
    jx, jy = layar(kamera, JKT, ASIA)
    for i, (nama, ll) in enumerate(TUJUAN.items()):
        k = c.p(0.12 + i * 0.07, 0.35 + i * 0.07)
        rute(d, kamera, JKT, ll, k, BIRU, ASIA, lengkung=0.12 if i % 2 else -0.12, s=0.55, tebal=5)
        x, y = layar(kamera, ll, ASIA)
        if k > 0.95:
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=BIRU + (255,), outline=(255, 255, 255, 255), width=3)
            label(d, (min(x, W - 90), y - 36), nama, 32, TINTA, c.p(0.3 + i * 0.07, 0.36 + i * 0.07))
    ikon_bandara(d, jx, jy, 1.0, MERAH)
    label(d, (jx, jy + 56), "Jakarta", 38, (120, 20, 15), 1.0, "caption")
    se.kartu(img, 540, 640, "Bandara internasional pertama", "di Hindia Belanda", MERAH, alpha=c.p(0.02, 0.1),
             tiang=False, skala=back_out((c.t / c.d - 0.02) / 0.1))
    se.kartu(img, 540, 800, "Pintu udara utama Jakarta", "selama puluhan tahun", BIRU, alpha=c.p(0.62, 0.7),
             tiang=False, skala=back_out((c.t / c.d - 0.62) / 0.1))
    se.teks(d, (900, 1330), "rute ilustratif", 26, (230, 230, 230), nama_font="tangan_tipis", alpha=0.8)
    hdr(img, "Gerbang ke dunia")
    return img


def a_padat(c):
    img = tampak_atas(c.t, 0.0, kota=c.p(0.05, 0.85))
    d = ImageDraw.Draw(img, "RGBA")
    # pesawat antre di landasan
    for i in range(4):
        y = lerp(1500, 420, ((c.t * 0.12 + i * 0.25) % 1))
        pesawat(d, CX, y, 1.2, -math.pi / 2, c.p(0.2 + i * 0.05, 0.3 + i * 0.05))
    a = c.p(0.55, 0.65)
    if a > 0:
        for sisi in (X0 - 30, X1 + 30):
            se.garis_putus(d, [(sisi, 1320), (sisi, 420)], a, MERAH, tebal=8, panah=False)
    angka_besar(d, (540, 470), "TAPI…", 120, PUTIH, alpha=c.p(0.0, 0.08) * (1 - c.p(0.3, 0.36)),
                stroke_warna=(20, 15, 10))
    se.kartu(img, 540, 760, "Penerbangan makin padat", "", ABU, alpha=c.p(0.25, 0.33), tiang=False,
             skala=back_out((c.t / c.d - 0.25) / 0.1))
    se.kartu(img, 540, 900, "Kota mengepung bandara", "", (120, 70, 40), alpha=c.p(0.45, 0.53), tiang=False,
             skala=back_out((c.t / c.d - 0.45) / 0.1))
    se.kartu(img, 540, 1040, "Landasan mentok, nggak bisa diperpanjang", "", MERAH, alpha=c.p(0.68, 0.76), tiang=False,
             skala=back_out((c.t / c.d - 0.68) / 0.1))
    hdr(img, "Makin rame, makin masalah")
    return img


def a_halim(c):
    kamera = Kamera(*cam(-6.208, 106.87, 1.9))
    img, d = peta(kamera)
    kx, ky = layar(kamera, KEMAYORAN)
    hx, hy = layar(kamera, HALIM)
    ikon_bandara(d, kx, ky, 1.0, MERAH)
    label(d, (kx + 150, ky), "Kemayoran", 40)
    ikon_bandara(d, hx, hy, 1.0)
    label(d, (hx + 130, hy + 10), "Halim", 40)
    for i in range(3):
        k = c.p(0.25 + i * 0.1, 0.6 + i * 0.1)
        rute(d, kamera, KEMAYORAN, HALIM, k, BIRU, lengkung=0.15 + i * 0.1, s=0.75)
    s = back_out((c.t / c.d) / 0.12)
    angka_besar(d, (540, 470), "1974", int(130 * s) + 1, EMAS_T, stroke_warna=(30, 20, 10))
    se.kartu(img, 540, 590, "Penerbangan internasional", "dipindah ke Halim", BIRU, alpha=c.p(0.15, 0.23),
             tiang=False, skala=back_out((c.t / c.d - 0.15) / 0.1))
    hdr(img, "Mulai dipindah")
    return img


def a_1985(c):
    kamera = se.kamera_antara(cam(-6.15, 106.84, 1.9), cam(-6.15, 106.75, 1.35), c.p(0.2, 0.55))
    img, d = peta(kamera)
    kx, ky = layar(kamera, KEMAYORAN)
    sx, sy = layar(kamera, SOETTA)
    ikon_bandara(d, kx, ky, 1.0, MERAH)
    rute(d, kamera, KEMAYORAN, SOETTA, c.p(0.25, 0.6), BIRU, lengkung=-0.2, s=0.9)
    ikon_bandara(d, sx, sy, c.p(0.5, 0.6))
    label(d, (sx, sy + 60), "Cengkareng", 38, TINTA, c.p(0.5, 0.6))
    se.kartu(img, clamp(kx, 200, 880), ky - 50, "Kemayoran", "", MERAH, alpha=1.0, coret=c.p(0.15, 0.3), skala=0.9)
    s = back_out((c.t / c.d) / 0.12)
    angka_besar(d, (540, 450), "31 MARET 1985", int(96 * s) + 1, EMAS_T, stroke_warna=(30, 20, 10))
    se.teks(d, (540, 545), "resmi berhenti beroperasi", 44, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(30, 20, 10), alpha=c.p(0.06, 0.14))
    se.kartu(img, 540, 1240, "Bandara Soekarno-Hatta", "rancangan arsitek Prancis Paul Andreu", BIRU,
             alpha=c.p(0.65, 0.73), tiang=False, skala=back_out((c.t / c.d - 0.65) / 0.1))
    hdr(img, "Akhir sebuah era")
    return img


def a_sekarang(c):
    k = c.p(0.05, 0.35)
    img = tampak_atas(c.t, k)
    d = ImageDraw.Draw(img, "RGBA")
    # papan nama jalan hijau
    a = c.p(0.3, 0.4)
    if a > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        sk = back_out((c.t / c.d - 0.3) / 0.1)
        w2 = 330 * sk
        dl.rounded_rectangle((540 - w2, 600, 540 + w2, 720), 16, fill=(20, 110, 60, 250), outline=PUTIH + (255,), width=6)
        dl.text((540, 660), "Jl. Benyamin Sueb", font=se.font("caption", int(58 * sk) + 1), fill=PUTIH, anchor="mm")
        se.tempel(img, lap, a)
        d = ImageDraw.Draw(img, "RGBA")
    # penggaris panjang
    b = c.p(0.5, 0.6)
    if b > 0:
        d.line((X1 + 70, 760, X1 + 70, 1300), fill=(255, 220, 120, int(255 * b)), width=6)
        for yy in (760, 1300):
            d.line((X1 + 50, yy, X1 + 90, yy), fill=(255, 220, 120, int(255 * b)), width=6)
        se.kartu(img, 540, 1030, "± 2,5 km", "bekas landasan pacu", MERAH, alpha=b, tiang=False,
                 skala=back_out((c.t / c.d - 0.5) / 0.1))
    se.kartu(img, 540, 1250, "Jakarta Fair & kawasan Kemayoran", "bekas area bandara", BIRU, alpha=c.p(0.72, 0.8),
             tiang=False, skala=back_out((c.t / c.d - 0.72) / 0.1))
    angka_besar(d, (540, 470), "SEKARANG?", 110, PUTIH, alpha=c.p(0.0, 0.06) * (1 - c.p(0.28, 0.33)),
                stroke_warna=(20, 15, 10))
    hdr(img, "Nasibnya sekarang")
    return img


def a_tintin(c):
    img = _langit()
    d = ImageDraw.Draw(img, "RGBA")
    # tanah & semak
    d.rectangle((0, 1240, W, H), fill=(120, 140, 80, 255))
    rng = random.Random(5)
    for i in range(30):
        x = rng.uniform(-40, W + 40)
        r = rng.uniform(40, 90)
        d.ellipse((x - r, 1240 - r * 0.7, x + r, 1240 + r * 0.7), fill=(70, 110, 55, 255), outline=(40, 70, 30, 255))
    naik = back_out(c.p(0.0, 0.2) * 1.0)
    menara(img, 300, 1250, int(620 * naik + 1))
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 300, 560, "Menara pengawas", "cagar budaya", (90, 60, 35), alpha=c.p(0.08, 0.16) * (1 - c.p(0.4, 0.45)),
             tiang=False)
    angka_besar(d, (720, 470), "“MENARA", 76, EMAS_T, alpha=c.p(0.3, 0.38), stroke_warna=(30, 20, 10))
    angka_besar(d, (720, 560), "TINTIN”", 96, EMAS_T, alpha=c.p(0.3, 0.38), stroke_warna=(30, 20, 10))
    # panel komik
    a = c.p(0.5, 0.58)
    if a > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        sk = back_out((c.t / c.d - 0.5) / 0.1)
        x0, y0, x1, y1 = 470, 700, 1030, 1200
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        x0, x1 = cx - (cx - x0) * sk, cx + (x1 - cx) * sk
        y0, y1 = cy - (cy - y0) * sk, cy + (y1 - cy) * sk
        dl.rectangle((x0 + 10, y0 + 12, x1 + 10, y1 + 12), fill=(0, 0, 0, 110))
        dl.rectangle((x0, y0, x1, y1), fill=(250, 245, 225, 255), outline=(20, 20, 20, 255), width=8)
        # titik halftone
        for yy in range(int(y0 + 20), int(y1 - 20), 26):
            for xx in range(int(x0 + 20), int(x1 - 20), 26):
                dl.ellipse((xx - 3, yy - 3, xx + 3, yy + 3), fill=(230, 200, 170, 255))
        if sk > 0.6:
            dl.text((cx, y0 + 70), "KOMIK TINTIN", font=se.font("caption", 50), fill=(200, 40, 30), anchor="mm",
                    stroke_width=4, stroke_fill=PUTIH)
            dl.text((cx, y0 + 140), "Penerbangan 714", font=se.font("judul", 44), fill=TINTA, anchor="mm")
            dl.text((cx, y0 + 190), "(terbit 1968)", font=se.font("tangan_tipis", 30), fill=(90, 70, 50), anchor="mm")
            pesawat(dl, cx + math.sin(c.t * 1.5) * 60, y0 + 300, 1.8, 0.0, 1.0)
            dl.text((cx, y1 - 70), "transit di Kemayoran", font=se.font("tangan", 38), fill=TINTA, anchor="mm")
        se.tempel(img, lap, a)
    hdr(img, "Masih berdiri sampai sekarang")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    img = tampak_atas(c.t, 1.0)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 450, 990, 1100), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 540), "Lewat Jalan Benyamin Sueb?", 50, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 615), "kamu lagi di atas landasan pesawat", 38, (90, 70, 50), alpha=a)
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rectangle((440, 680, 640, 1000), fill=ASPAL + (255,))
        for yy in range(690, 1000, 60):
            dl.rectangle((535, yy, 545, yy + 30), fill=(240, 240, 240, 255))
        pesawat(dl, 540, 840 - math.sin(c.t * 2) * 20, 2.2, -math.pi / 2, 1.0)
        se.tempel(img, lap, a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1050), "Bandara Kemayoran 1940 – 1985", 40, (170, 30, 20), nama_font="caption", alpha=a)
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
        dl.rounded_rectangle((540 - w2, 960, 540 + w2, 1090), int(clamp(w2, 1, 40)), fill=(200, 52, 44, 245))
        dl.text((540, 1025), "NGOMONGIN SEJARAH", font=se.font("caption", int(56 * sk) + 1), fill=PUTIH, anchor="mm")
        dl.text((540, 1160), "Follow buat cerita berikutnya", font=se.font("ui", 42), fill=PUTIH, anchor="mm",
                stroke_width=4, stroke_fill=(0, 0, 0))
        se.tempel(img, lap, b)
    return img


ADEGAN = [
    Adegan("hook", "Dulu, pesawat mendarat di jalan ini. Sekarang, tiap hari mobil lewat di atasnya. "
                   "Dan menara tuanya, ternyata pernah masuk komik terkenal dunia.", a_hook, transisi=False),
    Adegan("tren", "Lagi rame, Soekarno-Hatta jadi bandara tersibuk kedua di Asia Tenggara. Tapi sebelum Soetta ada, "
                   "pintu udara Jakarta itu di tengah kota. Namanya, Kemayoran.", a_tren),
    Adegan("1940", "Belanda mulai membangunnya tahun sembilan belas tiga puluh empat. Juli sembilan belas empat puluh, "
                   "pesawat pertama mendarat. Sebuah D C tiga milik maskapai K N I L M, terbang dari Cililitan.",
           a_1940),
    Adegan("internasional", "Kemayoran jadi bandara pertama di Hindia Belanda yang melayani penerbangan internasional "
                            "terjadwal. Dan selama puluhan tahun, inilah pintu udara utama Jakarta.", a_internasional),
    Adegan("padat", "Tapi makin lama, masalahnya makin gawat. Penerbangan makin padat. Rumah dan gedung tumbuh "
                    "mengepung bandara. Landasannya mentok, nggak bisa diperpanjang.", a_padat),
    Adegan("halim", "Tahun sembilan belas tujuh puluh empat, penerbangan internasional terpaksa dipindah ke Halim.",
           a_halim),
    Adegan("1985", "Lalu tiga puluh satu Maret sembilan belas delapan puluh lima, Kemayoran resmi berhenti beroperasi. "
                   "Semua pindah ke bandara baru di Cengkareng, rancangan arsitek Prancis, Paul Andreu.", a_1985),
    Adegan("sekarang", "Bekas landasannya, sekarang jadi Jalan Benyamin Sueb. Panjangnya hampir dua setengah kilometer. "
                       "Area bandaranya jadi arena Jakarta Fair dan kawasan Kemayoran.", a_sekarang),
    Adegan("tintin", "Nah, menara pengawasnya masih berdiri, dan jadi cagar budaya. Orang menyebutnya menara Tintin. "
                     "Soalnya, di komik Tintin, Penerbangan tujuh satu empat, Tintin transit di Bandara Kemayoran!",
           a_tintin),
    Adegan("penutup", "Jadi, kalau kamu lewat Jalan Benyamin Sueb, kamu lagi jalan di atas landasan pesawat. "
                      "Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
