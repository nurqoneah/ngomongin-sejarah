"""Shorts ±88 detik: Pertempuran Surabaya 1945 — kita kalah, kok jadi Hari Pahlawan?

Dua jenis visual: (1) peta dekat Surabaya–Madura (kapal perang, pendaratan, pasukan titik, ledakan),
(2) ilustrasi: Hotel Yamato & bendera, malam di Jembatan Merah, selebaran ultimatum + jam, papan jawaban.
Tokoh hanya berupa kartu nama, orang berupa titik. Waktu animasi pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import shorts_engine as se
from shorts_engine import EMAS, MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "pertempuran-surabaya-1945-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "PERTEMPURAN SURABAYA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU = (40, 90, 170)
ORANYE = (240, 120, 30)
BAJA = (85, 92, 100)
ZAITUN = (95, 100, 60)

# ------------------------------------------------------------------ peta dekat Surabaya – Madura

JAWA_TIMUR = [(-6.85, 111.9), (-6.88, 112.1), (-6.9, 112.35), (-6.87, 112.55), (-6.95, 112.6), (-7.08, 112.62),
              (-7.15, 112.66), (-7.19, 112.72), (-7.21, 112.78), (-7.25, 112.8), (-7.3, 112.83), (-7.38, 112.84),
              (-7.45, 112.86), (-7.53, 112.89), (-7.6, 112.85), (-7.63, 112.92), (-7.68, 113.05), (-7.72, 113.2),
              (-7.72, 113.4), (-7.7, 113.8), (-9.0, 113.8), (-9.0, 111.9)]
MADURA = [(-6.97, 112.71), (-6.88, 112.85), (-6.87, 113.1), (-6.88, 113.5), (-6.9, 113.8), (-7.0, 113.9),
          (-7.1, 113.85), (-7.18, 113.6), (-7.21, 113.3), (-7.19, 113.0), (-7.15, 112.82), (-7.11, 112.75),
          (-7.04, 112.71)]
print("  menyiapkan peta Surabaya...")
PETA = Peta(111.9, 113.7, -8.3, -6.1, 1200, [], [(-7.76, 112.59, 0.09), (-7.62, 112.62, 0.05), (-7.8, 112.4, 0.08)],
            seed=45, darat=[JAWA_TIMUR, MADURA])

SURABAYA = (-7.255, 112.745)
PERAK = (-7.205, 112.733)
JEMBATAN_MERAH = (-7.236, 112.738)
KALIMAS = [(-7.30, 112.735), (-7.27, 112.741), (-7.245, 112.738), (-7.225, 112.737), (-7.205, 112.735)]
POS_INGGRIS = [(-7.236, 112.742), (-7.212, 112.728), (-7.29, 112.728), (-7.265, 112.752), (-7.25, 112.72)]
KAPAL_UTARA = [(-6.75, 112.55), (-6.72, 112.75), (-6.78, 112.95)]
KAPAL_TIMUR = [(-7.3, 113.0), (-7.4, 113.05)]
LABEL = {"MADURA": (-7.0, 113.25), "JAWA": (-7.55, 112.45), "Laut Jawa": (-6.6, 112.8), "Gresik": (-7.12, 112.55),
         "Sidoarjo": (-7.45, 112.7)}


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


def hdr(img, sub="1945", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def angka_besar(d, xy, isi, uk, warna=PUTIH, alpha=1.0, stroke_warna=(10, 10, 20)):
    se.teks(d, xy, isi, uk, warna, nama_font="caption", stroke=10, stroke_warna=stroke_warna, alpha=alpha)


def kota(d, kamera, alpha=1.0, nama=True):
    """Kali Mas + titik kota Surabaya."""
    a = int(255 * alpha)
    p = [layar(kamera, ll) for ll in KALIMAS]
    d.line(p, fill=(60, 105, 150, a), width=max(3, int(5 * kamera.zoom)), joint="curve")
    x, y = layar(kamera, SURABAYA)
    if nama:
        label(d, (x - 150, y + 40), "SURABAYA", 46, TINTA, alpha, "caption")


def label_peta(d, kamera, alpha=1.0):
    for nama, ll in LABEL.items():
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 38, TINTA if nama != "Laut Jawa" else (200, 215, 235), alpha)


def kapal(d, x, y, s=1.0, alpha=1.0, arah=1):
    """Kapal perang tampak samping (siluet)."""
    a = int(255 * alpha)
    if a <= 2:
        return
    k = arah
    d.polygon([(x - 70 * s * k, y - 6 * s), (x + 80 * s * k, y - 6 * s), (x + 60 * s * k, y + 14 * s),
               (x - 60 * s * k, y + 14 * s)], fill=BAJA + (a,), outline=(25, 28, 32, a))
    d.rectangle((min(x - 30 * s * k, x + 20 * s * k), y - 26 * s, max(x - 30 * s * k, x + 20 * s * k), y - 6 * s),
                fill=(70, 76, 84, a), outline=(25, 28, 32, a))
    d.rectangle((min(x - 8 * s * k, x + 4 * s * k), y - 44 * s, max(x - 8 * s * k, x + 4 * s * k), y - 26 * s),
                fill=(60, 66, 74, a))
    d.line((x + 30 * s * k, y - 14 * s, x + 70 * s * k, y - 22 * s), fill=(30, 32, 36, a), width=max(2, int(5 * s)))
    d.line((x - 70 * s * k, y + 16 * s, x + 70 * s * k, y + 16 * s), fill=(230, 240, 250, int(a * 0.5)), width=2)


def tank(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    if a <= 2:
        return
    d.rounded_rectangle((x - 30 * s, y - 10 * s, x + 30 * s, y + 12 * s), int(6 * s) + 1, fill=ZAITUN + (a,),
                        outline=(30, 32, 20, a), width=2)
    d.ellipse((x - 14 * s, y - 22 * s, x + 14 * s, y - 2 * s), fill=(80, 85, 50, a), outline=(30, 32, 20, a))
    d.line((x + 10 * s, y - 12 * s, x + 44 * s, y - 14 * s), fill=(30, 32, 20, a), width=max(2, int(5 * s)))


def pesawat(d, x, y, s=1.0, alpha=1.0):
    """Pesawat tampak atas, menghadap kanan."""
    a = int(255 * alpha)
    if a <= 2:
        return
    c, o = (70, 78, 88, a), (20, 22, 26, a)
    d.polygon([(x - 50 * s, y - 5 * s), (x + 48 * s, y - 5 * s), (x + 60 * s, y), (x + 48 * s, y + 5 * s),
               (x - 50 * s, y + 5 * s)], fill=c, outline=o)
    d.polygon([(x - 2 * s, y - 4 * s), (x + 14 * s, y - 60 * s), (x + 26 * s, y - 60 * s), (x + 22 * s, y - 4 * s)],
              fill=c, outline=o)
    d.polygon([(x - 2 * s, y + 4 * s), (x + 14 * s, y + 60 * s), (x + 26 * s, y + 60 * s), (x + 22 * s, y + 4 * s)],
              fill=c, outline=o)
    d.polygon([(x - 50 * s, y - 4 * s), (x - 42 * s, y - 22 * s), (x - 34 * s, y - 22 * s), (x - 38 * s, y)], fill=c,
              outline=o)
    d.polygon([(x - 50 * s, y + 4 * s), (x - 42 * s, y + 22 * s), (x - 34 * s, y + 22 * s), (x - 38 * s, y)], fill=c,
              outline=o)


def selebaran(d, x, y, sudut, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    if a <= 2:
        return
    w, h = 26 * s, 18 * s
    cs, sn = math.cos(sudut), math.sin(sudut)
    p = [(x + dx * cs - dy * sn, y + dx * sn + dy * cs) for dx, dy in ((-w, -h), (w, -h), (w, h), (-w, h))]
    d.polygon(p, fill=(245, 238, 220, a), outline=(90, 80, 60, a))
    d.line((p[0][0] * 0.7 + p[2][0] * 0.3, p[0][1] * 0.7 + p[2][1] * 0.3, p[1][0] * 0.7 + p[3][0] * 0.3,
            p[1][1] * 0.7 + p[3][1] * 0.3), fill=(60, 50, 40, a), width=2)


def hujan_selebaran(d, t, kuat=1.0, seed=4, y0=380, y1=1320):
    rng = random.Random(seed)
    for i in range(46):
        x0 = rng.uniform(40, W - 40)
        v = rng.uniform(90, 170)
        fase = rng.uniform(0, 1)
        tinggi = y1 - y0
        y = y0 + ((fase * tinggi + t * v) % tinggi)
        x = x0 + math.sin(t * 2 + i) * 40
        selebaran(d, x, y, t * rng.uniform(1.5, 3.5) + i, rng.uniform(0.8, 1.3), kuat)


def ledakan(img, x, y, k, s=1.0):
    """k: 0..1 umur ledakan."""
    if k <= 0 or k >= 1:
        return
    r = (40 + 120 * k) * s
    se.glow(img, x, y, r * 1.6, (255, 170, 60), 2.2 * (1 - k))
    d = ImageDraw.Draw(img, "RGBA")
    a = int(255 * (1 - k))
    d.ellipse((x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6), fill=(255, 210, 90, a))
    d.ellipse((x - r * 0.3, y - r * 0.3, x + r * 0.3, y + r * 0.3), fill=(255, 250, 220, a))
    for j in range(5):
        rr = r * (0.3 + 0.15 * j)
        oy = -k * 90 * s - j * 10
        d.ellipse((x - rr + j * 9, y + oy - rr * 0.7, x + rr + j * 9, y + oy + rr * 0.7),
                  fill=(70, 60, 55, int(120 * (1 - k))))


def ledakan_kota(img, kamera, t, kuat=1.0, n=7, seed=9, periode=1.6):
    rng = random.Random(seed)
    for i in range(n):
        ll = (SURABAYA[0] + rng.uniform(-0.06, 0.06), SURABAYA[1] + rng.uniform(-0.04, 0.05))
        off = rng.uniform(0, periode)
        k = ((t + off) % periode) / periode * 1.6
        if kuat > 0.05 and k < 1:
            x, y = layar(kamera, ll)
            ledakan(img, x, y, k, kamera.zoom / 1.8 * kuat)


def pasukan(d, kamera, pusat, n, warna, sebar=0.012, seed=1, alpha=1.0, s=1.0, t=0.0, goyang=0.0):
    rng = random.Random(seed)
    for i in range(n):
        ll = (pusat[0] + rng.gauss(0, sebar), pusat[1] + rng.gauss(0, sebar))
        x, y = layar(kamera, ll)
        x += math.sin(t * 3 + i) * goyang
        se.prajurit(d, x, y, warna, s, alpha)


_LATAR = {}


def latar_kertas(seed=33):
    if seed not in _LATAR:
        _LATAR[seed] = se.latar_tekstur(W, H, seed, warna=(222, 200, 155)).convert("RGBA")
    return _LATAR[seed].copy()


def gradasi(atas, bawah):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (np.array(atas, np.float32) * (1 - g) + np.array(bawah, np.float32) * g).repeat(W, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")


# ------------------------------------------------------------------ adegan

def a_hook(c):
    kamera = se.kamera_antara(cam(-7.1, 112.78, 1.25), cam(-7.13, 112.76, 1.4), c.p(0.0, 1.0))
    img, d = peta(kamera)
    se.tint(img, (60, 10, 5), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    kota(d, kamera, nama=False)
    for i, ll in enumerate(KAPAL_UTARA):
        x, y = layar(kamera, ll)
        kapal(d, x, y + math.sin(c.t * 2 + i) * 3, 1.0)
    # sasaran merah berdenyut di kota
    x, y = layar(kamera, SURABAYA)
    se.glow(img, x, y, 200, (255, 60, 40), 1.3)
    d = ImageDraw.Draw(img, "RGBA")
    den = (c.t * 0.9) % 1
    for r in (60, 110):
        d.ellipse((x - r, y - r, x + r, y + r), outline=(230, 40, 30, 230), width=8)
    rr = 60 + 140 * den
    d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(255, 80, 60, int(220 * (1 - den))), width=6)
    d.line((x - 150, y, x + 150, y), fill=(230, 40, 30, 200), width=5)
    d.line((x, y - 150, x, y + 150), fill=(230, 40, 30, 200), width=5)
    # pesawat lewat + hujan selebaran
    px = -150 + (c.t * 230) % (W + 300)
    pesawat(d, px, 420, 1.3)
    hujan_selebaran(d, c.t, 1.0 - 0.6 * c.p(0.5, 0.6))
    a1 = 1 - c.p(0.5, 0.56)
    s = 0.9 + 0.1 * back_out(c.t / 0.35)
    angka_besar(d, (540, 560), "SERAHKAN SENJATA", int(86 * s), EMAS, alpha=a1, stroke_warna=(40, 10, 5))
    angka_besar(d, (540, 690), "ATAU DIHANCURKAN", int(86 * s), PUTIH, alpha=a1, stroke_warna=(120, 10, 5))
    se.kartu(img, 540, 1290, "Ultimatum Inggris untuk Surabaya", "9 November 1945", MERAH,
             alpha=c.p(0.18, 0.26) * a1, tiang=False)
    b = c.p(0.56, 0.62)
    if b > 0:
        sk = back_out((c.t / c.d - 0.56) / 0.1)
        angka_besar(d, (540, 580), "KITA KALAH…", int(130 * sk) + 1, (255, 90, 70), alpha=b, stroke_warna=(20, 5, 5))
        b2 = c.p(0.8, 0.86)
        if b2 > 0:
            sk2 = back_out((c.t / c.d - 0.8) / 0.1)
            angka_besar(d, (540, 720), "KOK JADI", int(84 * sk2) + 1, PUTIH, alpha=b2)
            angka_besar(d, (540, 830), "HARI PAHLAWAN?", int(100 * sk2) + 1, EMAS, alpha=b2, stroke_warna=(40, 10, 5))
    hdr(img, "10 November 1945", alpha=c.p(0.45, 0.56))
    return img


def bendera_kibar(d, x, y, lebar, tinggi_garis, t, warna_garis, alpha=1.0, lepas=None):
    """Bendera bergaris horizontal yang berkibar. lepas: (indeks, k) garis yang jatuh."""
    a = int(255 * alpha)
    n = 16
    for gi, warna in enumerate(warna_garis):
        dy = 0.0
        rot_a = a
        if lepas and lepas[0] == gi:
            k = lepas[1]
            dy = k * k * 900
            rot_a = int(a * (1 - clamp(k * 1.3)))
            if rot_a <= 2:
                continue
        atas, bawah = [], []
        for i in range(n + 1):
            f = i / n
            xx = x + f * lebar
            w = math.sin(t * 4 - f * 5) * 10 * f
            if lepas and lepas[0] == gi:
                w += lepas[1] * 120 * f
            atas.append((xx, y + gi * tinggi_garis + w + dy))
            bawah.append((xx, y + (gi + 1) * tinggi_garis + w + dy))
        d.polygon(atas + bawah[::-1], fill=tuple(warna) + (rot_a,), outline=(40, 30, 20, rot_a))


def a_yamato(c):
    img = gradasi((235, 170, 110), (250, 220, 170))
    d = ImageDraw.Draw(img, "RGBA")
    # gedung hotel
    d.rectangle((90, 820, 990, 1330), fill=(238, 226, 200, 255), outline=(90, 70, 50, 255), width=5)
    d.rectangle((400, 640, 680, 820), fill=(232, 218, 190, 255), outline=(90, 70, 50, 255), width=5)
    d.polygon([(380, 640), (540, 560), (700, 640)], fill=(170, 80, 50, 255), outline=(90, 50, 30, 255))
    for baris in range(3):
        for kol in range(9):
            wx = 130 + kol * 96
            wy = 870 + baris * 140
            d.rectangle((wx, wy, wx + 50, wy + 80), fill=(90, 110, 130, 255), outline=(70, 55, 40, 255), width=3)
    for kol in range(3):
        d.rectangle((430 + kol * 85, 680, 470 + kol * 85, 760), fill=(90, 110, 130, 255))
    se.teks(d, (540, 845), "HOTEL YAMATO", 34, (90, 60, 40), nama_font="judul")
    # tiang bendera
    tiang_x, puncak = 540, 380
    d.line((tiang_x, 560, tiang_x, puncak), fill=(60, 45, 30, 255), width=8)
    k = c.p(0.55, 0.85)
    lepas = (2, k) if k > 0 else None
    bendera_kibar(d, tiang_x + 4, puncak + 8, 230, 42, c.t, [(200, 30, 30), (250, 250, 250), (30, 70, 160)],
                  lepas=lepas)
    # pemuda memanjat (titik merah)
    for i in range(7):
        f = clamp(c.p(0.25, 0.55) * 1.2 - i * 0.08)
        if f <= 0:
            continue
        yy = lerp(1320, 600 + i * 6, f)
        xx = 700 + i * 26 - f * 120
        se.prajurit(d, xx, yy, MERAH, 1.4)
    se.kartu(img, 540, 470, "September 1945", "Bendera Belanda dikibarkan", BIRU, alpha=c.p(0.05, 0.12) *
             (1 - c.p(0.5, 0.56)), tiang=False, lebar=440)
    if c.p(0.78, 0.86) > 0:
        angka_besar(d, (540, 1080), "TINGGAL MERAH PUTIH", int(76 * back_out((c.t / c.d - 0.78) / 0.1)) + 1,
                    PUTIH, alpha=c.p(0.78, 0.86), stroke_warna=(150, 20, 20))
    hdr(img, "Surabaya, 1945")
    return img


def a_mendarat(c):
    kamera = se.kamera_antara(cam(-7.05, 112.75, 1.0), cam(-7.2, 112.74, 1.7), c.p(0.0, 0.7))
    img, d = peta(kamera)
    label_peta(d, kamera, 1 - c.p(0.4, 0.6))
    kota(d, kamera)
    m = c.p(0.0, 0.55)
    tuju = [(-7.19, 112.71), (-7.18, 112.735), (-7.2, 112.705)]
    for i, (asal, ke) in enumerate(zip([(-6.7, 112.6), (-6.65, 112.72), (-6.72, 112.5)], tuju)):
        ll = (lerp(asal[0], ke[0], m), lerp(asal[1], ke[1], m))
        x, y = layar(kamera, ll)
        kapal(d, x, y, 0.8 + 0.3 * kamera.zoom / 1.7)
    turun = c.p(0.5, 0.8)
    if turun > 0:
        for j, pos in enumerate(POS_INGGRIS):
            ll = (lerp(PERAK[0], pos[0], turun), lerp(PERAK[1], pos[1], turun))
            pasukan(d, kamera, ll, 9, BIRU, 0.004, seed=j, s=1.1)
    se.kartu(img, 540, 1180, "± 6.000 tentara Inggris-India", "mendarat 25 Oktober 1945", BIRU, alpha=c.p(0.2, 0.3),
             tiang=False, skala=back_out((c.t / c.d - 0.2) / 0.1))
    se.kartu(img, 540, 520, "Tugas: melucuti tentara Jepang", "", (90, 70, 50), alpha=c.p(0.65, 0.73), tiang=False)
    hdr(img, "Oktober 1945")
    return img


def a_bentrok(c):
    kamera = Kamera(*cam(-7.245, 112.74, 2.1))
    img, d = peta(kamera)
    kota(d, kamera)
    for j, pos in enumerate(POS_INGGRIS):
        pasukan(d, kamera, pos, 9, BIRU, 0.004, seed=j, s=1.1)
    # selebaran 27 Oktober
    a_sel = c.p(0.2, 0.28) * (1 - c.p(0.5, 0.55))
    if a_sel > 0:
        hujan_selebaran(d, c.t, a_sel, seed=8)
        se.kartu(img, 540, 520, "Selebaran: serahkan semua senjata!", "27 Oktober 1945", BIRU, alpha=a_sel,
                 tiang=False)
    se.kartu(img, 540, 520, "Belanda ikut membonceng?", "rakyat curiga", (110, 80, 50),
             alpha=c.p(0.02, 0.1) * (1 - c.p(0.18, 0.22)), tiang=False)
    # rakyat mengepung pos-pos Inggris
    k = c.p(0.42, 0.75)
    if k > 0:
        rng = random.Random(5)
        for j, pos in enumerate(POS_INGGRIS):
            for i in range(int(22 * k)):
                sud = rng.uniform(0, math.tau)
                jr = rng.uniform(0.008, 0.016)
                ll = (pos[0] + math.sin(sud) * jr, pos[1] + math.cos(sud) * jr)
                x, y = layar(kamera, ll)
                se.prajurit(d, x + math.sin(c.t * 4 + i) * 3, y, MERAH, 1.0)
        if c.p(0.5, 0.55) > 0:
            se.kartu(img, 540, 520, "Pasukan Inggris terkepung", "", MERAH, alpha=c.p(0.52, 0.6) *
                     (1 - c.p(0.76, 0.8)), tiang=False)
    se.kartu(img, 540, 520, "Bung Karno didatangkan", "untuk gencatan senjata", (60, 60, 70), alpha=c.p(0.8, 0.88),
             tiang=False, skala=back_out((c.t / c.d - 0.8) / 0.1))
    hdr(img, "Akhir Oktober 1945")
    return img


def mobil(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.rounded_rectangle((x - 110 * s, y - 40 * s, x + 110 * s, y + 10 * s), int(14 * s), fill=(35, 38, 40, a))
    d.polygon([(x - 60 * s, y - 40 * s), (x - 35 * s, y - 80 * s), (x + 45 * s, y - 80 * s), (x + 70 * s, y - 40 * s)],
              fill=(30, 33, 36, a))
    d.polygon([(x - 45 * s, y - 42 * s), (x - 28 * s, y - 72 * s), (x + 5 * s, y - 72 * s), (x + 5 * s, y - 42 * s)],
              fill=(80, 95, 110, a))
    for wx in (-65, 65):
        d.ellipse((x + wx * s - 24 * s, y - 14 * s, x + wx * s + 24 * s, y + 34 * s), fill=(15, 15, 15, a),
                  outline=(90, 90, 90, a), width=3)
    d.ellipse((x + 100 * s, y - 30 * s, x + 116 * s, y - 16 * s), fill=(255, 230, 150, a))


def a_mallaby(c):
    img = gradasi((12, 16, 35), (40, 42, 62))
    d = ImageDraw.Draw(img, "RGBA")
    # gedung Internatio
    d.rectangle((560, 640, 1040, 1100), fill=(70, 68, 72, 255), outline=(30, 28, 32, 255), width=4)
    d.polygon([(540, 640), (800, 560), (1060, 640)], fill=(60, 58, 62, 255))
    for baris in range(3):
        for kol in range(5):
            wx, wy = 600 + kol * 88, 690 + baris * 130
            d.rectangle((wx, wy, wx + 44, wy + 76), fill=(230, 190, 110, 200 if (kol + baris) % 3 else 90))
    se.teks(d, (800, 665), "INTERNATIO", 26, (200, 190, 170), nama_font="judul")
    # jalan, sungai, Jembatan Merah
    d.rectangle((0, 1100, W, 1160), fill=(50, 50, 55, 255))
    d.rectangle((0, 1160, W, 1330), fill=(25, 40, 70, 255))
    for i in range(10):
        yy = 1180 + i * 15
        d.line((40 + (i * 70 + c.t * 30) % 400, yy, 120 + (i * 70 + c.t * 30) % 400, yy), fill=(80, 110, 150, 140),
               width=3)
    d.rectangle((0, 1060, 520, 1100), fill=(170, 40, 30, 255), outline=(80, 15, 10, 255), width=3)
    for bx in range(10, 520, 46):
        d.line((bx, 1060, bx, 1020), fill=(170, 40, 30, 255), width=8)
    d.line((0, 1020, 520, 1020), fill=(170, 40, 30, 255), width=10)
    se.teks(d, (260, 960), "Jembatan Merah", 40, (250, 210, 180), nama_font="tangan", stroke=5, stroke_warna=(20, 15, 30))
    # mobil dikepung massa
    mx = lerp(-150, 560, c.p(0.05, 0.3))
    mobil(d, mx, 1110, 1.0)
    k = c.p(0.28, 0.5)
    rng = random.Random(3)
    for i in range(int(40 * k)):
        sud = rng.uniform(math.pi * 0.95, math.tau * 1.02)
        r = rng.uniform(150, 260)
        x = 560 + math.cos(sud) * r
        y = 1110 + math.sin(sud) * r * 0.45
        se.prajurit(d, x + math.sin(c.t * 5 + i) * 4, y, (150, 60, 50), 1.2)
    # kilatan
    f = c.p(0.5, 0.53) * (1 - c.p(0.53, 0.62))
    if f > 0:
        se.glow(img, 560, 1060, 300, (255, 230, 160), 3.0 * f)
        se.tint(img, (255, 250, 230), 0.4 * f)
    se.kartu(img, 540, 480, "Brigjen A.W.S. Mallaby", "30 Oktober 1945 · malam", BIRU, alpha=c.p(0.12, 0.2),
             tiang=False, coret=c.p(0.55, 0.65))
    d = ImageDraw.Draw(img, "RGBA")
    if c.p(0.75, 0.8) > 0:
        sk = back_out((c.t / c.d - 0.75) / 0.12)
        angka_besar(d, (300, 760), "?", int(260 * sk) + 1, EMAS, alpha=c.p(0.75, 0.8), stroke_warna=(20, 10, 5))
        se.kartu(img, 540, 1290, "Siapa penembaknya? Masih misteri", "", (110, 80, 50), alpha=c.p(0.8, 0.86),
                 tiang=False)
    angka_besar(d, (540, 640), "SEMUANYA BERUBAH", 76, PUTIH, alpha=c.p(0.0, 0.05) * (1 - c.p(0.15, 0.2)),
                stroke_warna=(150, 20, 20))
    hdr(img, "Titik balik")
    return img


def a_balasan(c):
    kamera = se.kamera_antara(cam(-6.95, 112.8, 0.92), cam(-7.0, 112.8, 1.0), c.p(0.0, 1.0))
    img, d = peta(kamera)
    label_peta(d, kamera, 0.8)
    kota(d, kamera)
    m = c.p(0.1, 0.55)
    for i, ll in enumerate(KAPAL_UTARA):
        x, y = layar(kamera, (ll[0] + 0.3 * (1 - m), ll[1]))
        kapal(d, x, y + math.sin(c.t * 2 + i) * 3, 0.9, c.p(0.05, 0.15))
    for i, ll in enumerate(KAPAL_TIMUR):
        x, y = layar(kamera, (ll[0], ll[1] + 0.4 * (1 - m)))
        kapal(d, x, y, 0.9, c.p(0.05, 0.15), arah=-1)
    kt = c.p(0.4, 0.6)
    rng = random.Random(2)
    for i in range(10):
        ll = (PERAK[0] + rng.uniform(-0.03, 0.01) - 0.02 * (1 - kt), PERAK[1] + rng.uniform(-0.07, 0.03))
        x, y = layar(kamera, ll)
        tank(d, x, y, 0.9, kt)
    for i in range(4):
        px = -200 + ((c.t * 260 + i * 330) % (W + 400))
        pesawat(d, px, 760 + i * 70 - (px * 0.12), 0.8, c.p(0.55, 0.65))
    jumlah = int(24000 * c.p(0.05, 0.45))
    angka_besar(d, (540, 520), f"{jumlah:,}".replace(",", "."), 150, EMAS, alpha=c.p(0.02, 0.08),
                stroke_warna=(40, 10, 5))
    angka_besar(d, (540, 640), "TENTARA", 70, PUTIH, alpha=c.p(0.02, 0.08))
    se.kartu(img, 540, 790, "Mayjen Mansergh · Divisi India ke-5", "tank, pesawat tempur, kapal perang", BIRU,
             alpha=c.p(0.3, 0.38), tiang=False)
    hdr(img, "Inggris datang lagi")
    return img


def jam(d, x, y, r, menit_total, alpha=1.0):
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 244, 228, a), outline=(40, 30, 20, a), width=8)
    for i in range(12):
        s = i / 12 * math.tau
        d.line((x + math.sin(s) * r * 0.82, y - math.cos(s) * r * 0.82, x + math.sin(s) * r * 0.94,
                y - math.cos(s) * r * 0.94), fill=(40, 30, 20, a), width=5)
    sj = (menit_total / 720) * math.tau
    sm = (menit_total % 60) / 60 * math.tau
    d.line((x, y, x + math.sin(sj) * r * 0.5, y - math.cos(sj) * r * 0.5), fill=(40, 30, 20, a), width=10)
    d.line((x, y, x + math.sin(sm) * r * 0.78, y - math.cos(sm) * r * 0.78), fill=(180, 30, 20, a), width=6)
    d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(40, 30, 20, a))


def cap_ditolak(img, k):
    if k <= 0:
        return
    lap = Image.new("RGBA", (620, 200), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((10, 10, 610, 190), 20, outline=(200, 30, 25, 255), width=12)
    dl.text((310, 100), "DITOLAK!", font=se.font("caption", 120), fill=(200, 30, 25, 255), anchor="mm")
    sk = 1.6 - 0.6 * back_out(k)
    lap = lap.rotate(14, expand=True, resample=Image.BICUBIC)
    lap = lap.resize((int(lap.width * sk), int(lap.height * sk)), Image.BICUBIC)
    se.tempel(img, lap, clamp(k * 2), (540 - lap.width // 2, 720 - lap.height // 2))


def a_ultimatum(c):
    img = gradasi((30, 28, 34), (50, 40, 40))
    se.panel(img, (130, 400, 950, 990), alpha=c.p(0, 0.06))
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.0, 0.06)
    se.teks(d, (540, 490), "ULTIMATUM", 80, (150, 30, 20), nama_font="judul", alpha=a)
    se.teks(d, (540, 560), "Surabaya, 9 November 1945", 34, (90, 70, 50), nama_font="tangan_tipis", alpha=a)
    se.teks(d, (540, 670), "Semua senjata", 58, TINTA, alpha=c.p(0.08, 0.15))
    se.teks(d, (540, 740), "harus diserahkan", 58, TINTA, alpha=c.p(0.08, 0.15))
    se.teks(d, (540, 860), "Batas: 10 November, jam 06.00 pagi", 36, (150, 30, 20), alpha=c.p(0.25, 0.32))
    menit = lerp(4 * 60 + 15, 6 * 60, c.p(0.3, 0.62))
    jam(d, 540, 1160, 120, menit, c.p(0.28, 0.34))
    cap_ditolak(img, c.p(0.72, 0.82))
    hdr(img, "Ultimatum")
    return img


def radio(d, x, y, s=1.0, alpha=1.0, t=0.0):
    a = int(255 * alpha)
    d.rounded_rectangle((x - 70 * s, y - 45 * s, x + 70 * s, y + 45 * s), int(14 * s), fill=(120, 80, 45, a),
                        outline=(50, 30, 15, a), width=4)
    d.ellipse((x - 55 * s, y - 32 * s, x - 5 * s, y + 18 * s), fill=(60, 40, 25, a))
    d.rectangle((x + 10 * s, y - 28 * s, x + 58 * s, y - 8 * s), fill=(240, 220, 160, a))
    for i in range(3):
        f = (t * 1.2 + i / 3) % 1
        r = (60 + f * 70) * s
        d.arc((x - r, y - 45 * s - r, x + r, y - 45 * s + r), 220, 320, fill=(255, 220, 120, int(a * (1 - f))),
              width=5)


def a_pertempuran(c):
    kamera = se.kamera_antara(cam(-7.18, 112.78, 1.35), cam(-7.22, 112.77, 1.55), c.p(0.0, 1.0))
    img, d = peta(kamera)
    kota(d, kamera)
    for i, ll in enumerate(KAPAL_UTARA[:2] + KAPAL_TIMUR[:1]):
        x, y = layar(kamera, ll)
        kapal(d, x, y + math.sin(c.t * 2 + i) * 3, 0.9, arah=-1 if ll in KAPAL_TIMUR else 1)
        # peluru meriam ke kota
        f = ((c.t * 0.7 + i * 0.33) % 1)
        tx, ty = layar(kamera, (SURABAYA[0] + 0.02 * (i - 1), SURABAYA[1] + 0.01 * i))
        bx = lerp(x, tx, f)
        by = lerp(y, ty, f) - math.sin(f * math.pi) * 180
        d.ellipse((bx - 7, by - 7, bx + 7, by + 7), fill=(255, 230, 150, 255))
    rng = random.Random(7)
    for i in range(60):
        ll = (SURABAYA[0] + rng.uniform(-0.05, 0.05), SURABAYA[1] + rng.uniform(-0.04, 0.03))
        x, y = layar(kamera, ll)
        se.prajurit(d, x + math.sin(c.t * 4 + i) * 4, y, MERAH, 1.0)
    ledakan_kota(img, kamera, c.t, 1.0, n=8)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(3):
        px = -200 + ((c.t * 300 + i * 420) % (W + 400))
        pesawat(d, px, 520 + i * 90, 0.9)
    a1 = 1 - c.p(0.22, 0.27)
    angka_besar(d, (540, 600), "06.00", int(170 * (0.9 + 0.1 * back_out(c.t / 0.3))), EMAS, alpha=a1,
                stroke_warna=(40, 10, 5))
    angka_besar(d, (540, 730), "laut · darat · udara", 60, PUTIH, alpha=c.p(0.08, 0.14) * a1)
    b = c.p(0.3, 0.37) * (1 - c.p(0.6, 0.65))
    if b > 0:
        radio(d, 540, 540, 1.2, b, c.t)
        se.kartu(img, 540, 690, "Bung Tomo", "membakar semangat lewat radio", MERAH, alpha=b, tiang=False)
    se.kartu(img, 540, 600, "Pemuda & santri ikut melawan", "", MERAH, alpha=c.p(0.62, 0.68) * (1 - c.p(0.8, 0.84)),
             tiang=False)
    se.kartu(img, 540, 600, "± 3 minggu bertempur", "", (60, 60, 70), alpha=c.p(0.82, 0.88), tiang=False,
             skala=back_out((c.t / c.d - 0.82) / 0.1))
    hdr(img, "10 November 1945")
    return img


def a_korban(c):
    kamera = Kamera(*cam(-7.35, 112.74, 1.3))
    img, d = peta(kamera)
    kota(d, kamera)
    ledakan_kota(img, kamera, c.t, 0.6 * (1 - c.p(0.5, 0.8)), n=4, periode=2.2)
    se.tint(img, (15, 10, 8), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    # pengungsi mengalir ke selatan
    k = c.p(0.35, 1.0)
    if k > 0:
        rng = random.Random(11)
        for i in range(90):
            f = (rng.random() + c.t * 0.12) % 1 * k
            ll = (lerp(SURABAYA[0], -7.65, f) + rng.gauss(0, 0.01), lerp(SURABAYA[1], 112.7, f) + rng.gauss(0, 0.03))
            x, y = layar(kamera, ll)
            se.prajurit(d, x, y, (230, 220, 200), 0.8, 0.9 * c.p(0.35, 0.42))
    a1 = 1 - c.p(0.36, 0.42)
    angka_besar(d, (540, 520), "RIBUAN GUGUR", 110, (255, 90, 70), alpha=c.p(0.0, 0.06) * a1, stroke_warna=(20, 5, 5))
    se.kartu(img, 540, 680, "perkiraan: ± 6.000 – belasan ribu jiwa", "", (60, 60, 70), alpha=c.p(0.12, 0.2) * a1,
             tiang=False)
    jumlah = int(200000 * c.p(0.4, 0.7))
    angka_besar(d, (540, 520), f"± {jumlah:,}".replace(",", "."), 120, PUTIH, alpha=c.p(0.4, 0.46))
    angka_besar(d, (540, 640), "warga mengungsi", 60, PUTIH, alpha=c.p(0.4, 0.46))
    se.kartu(img, 540, 1290, "Surabaya akhirnya jatuh", "", BIRU, alpha=c.p(0.8, 0.86), tiang=False,
             skala=back_out((c.t / c.d - 0.8) / 0.1))
    hdr(img, "Harga yang dibayar")
    return img


def a_jawaban(c):
    img = latar_kertas()
    d = ImageDraw.Draw(img, "RGBA")
    sk = back_out(c.t / c.d / 0.1)
    angka_besar(d, (540, 440), "KENAPA JADI", int(70 * sk) + 1, PUTIH, stroke_warna=(60, 30, 10))
    angka_besar(d, (540, 530), "HARI PAHLAWAN?", int(90 * sk) + 1, EMAS, stroke_warna=(60, 30, 10))
    kartu = [
        (0.1, "Dunia sadar: Republik didukung rakyat", MERAH),
        (0.33, "Inggris memilih netral", BIRU),
        (0.47, "Kelak mendukung Indonesia di PBB", BIRU),
    ]
    for i, (mulai, isi, warna) in enumerate(kartu):
        se.kartu(img, 540, 680 + i * 130, isi, "", warna, alpha=c.p(mulai, mulai + 0.07), tiang=False,
                 skala=back_out((c.t / c.d - mulai) / 0.1))
    b = c.p(0.7, 0.78)
    if b > 0:
        s2 = back_out((c.t / c.d - 0.7) / 0.1)
        se.panel(img, (150, 1060, 930, 1300), alpha=b, warna=(200, 52, 44), garis=(110, 20, 16))
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1130), "Keppres 316 / 1959", int(40 * s2) + 1, (255, 235, 200), nama_font="tangan", alpha=b)
        se.teks(d, (540, 1215), "10 NOVEMBER = HARI PAHLAWAN", int(42 * s2) + 1, PUTIH, nama_font="caption", alpha=b)
    hdr(img, "Jawabannya")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(-7.22, 112.76, 1.5))
    img, _ = peta(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 450, 990, 1100), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 540), "Kalah di medan perang,", 54, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 620), "menang di mata dunia", 54, (170, 30, 20), nama_font="judul", alpha=a)
        d.line((380, 700, 380, 960), fill=(60, 45, 30, int(255 * a)), width=8)
        bendera_kibar(d, 384, 710, 320, 90, c.t, [(200, 30, 30), (250, 250, 250)], alpha=a)
        se.teks(d, (540, 1030), "Selamat Hari Pahlawan!", 48, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Serahkan senjata, atau kota kalian dihancurkan. Ancaman Inggris buat Surabaya. Sebentar lagi "
                   "Hari Pahlawan. Padahal di pertempuran ini, kita kalah. Kok malah jadi Hari Pahlawan?",
           a_hook, transisi=False),
    Adegan("yamato", "September empat lima, Hotel Yamato. Bendera Belanda berkibar. Arek-arek Suroboyo naik, "
                     "merobek birunya. Tinggal merah putih.", a_yamato),
    Adegan("mendarat", "Bulan berikutnya, enam ribuan tentara Inggris-India mendarat. Tugasnya, melucuti Jepang.",
           a_mendarat),
    Adegan("bentrok", "Tapi rakyat curiga Belanda ikut membonceng. Pertempuran pecah, Inggris terkepung, sampai "
                      "Bung Karno didatangkan buat damai.", a_bentrok, transisi=False),
    Adegan("mallaby", "Nah, di sinilah semuanya berubah. Tiga puluh Oktober malam, Brigadir "
                      "Mallaby tewas. Siapa penembaknya? Masih misteri.", a_mallaby),
    Adegan("balasan", "Inggris murka. Datang dua puluh empat ribu tentara, plus tank, pesawat, dan kapal perang.",
           a_balasan),
    Adegan("ultimatum", "Ultimatumnya: serahkan senjata sebelum jam enam pagi, sepuluh November. Jawaban "
                        "arek Suroboyo? Nggak.", a_ultimatum),
    Adegan("pertempuran", "Jam enam tepat, Surabaya digempur dari laut, darat, dan udara. Bung Tomo membakar semangat "
                          "lewat radio. Pemuda dan santri melawan, sekitar tiga minggu.", a_pertempuran),
    Adegan("korban", "Ribuan orang gugur. Dua ratus ribuan warga mengungsi. Surabaya jatuh.", a_korban,
           transisi=False),
    Adegan("jawaban", "Kenapa jadi Hari Pahlawan? Karena dunia sadar, Republik didukung rakyatnya. "
                      "Inggris pun memilih netral, dan kelak mendukung Indonesia di PBB. Tahun lima sembilan, "
                      "sepuluh November resmi jadi Hari Pahlawan.", a_jawaban),
    Adegan("penutup", "Kalah di medan perang, menang di mata dunia. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
