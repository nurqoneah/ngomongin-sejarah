"""Shorts ±90 detik: Gempa 1834 yang Meruntuhkan Istana Bogor (Buitenzorg).

Peta Jawa bagian barat + adegan ilustrasi istana (tumbuh dua lantai, retak, ambruk, dibangun ulang).
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

NAMA_FILE = "gempa-istana-bogor-1834-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "GEMPA ISTANA BOGOR"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU = (30, 80, 150)
COKLAT = (120, 80, 45)

# ------------------------------------------------------------------ peta Jawa bagian barat

JAWA_DETAIL = [(-5.93, 106.0), (-6.0, 106.15), (-5.95, 106.35), (-6.05, 106.6), (-6.1, 106.8), (-6.02, 107.0),
               (-5.93, 107.05), (-6.1, 107.4), (-6.2, 107.8), (-6.25, 108.05), (-6.27, 108.4), (-6.45, 108.5),
               (-6.72, 108.57), (-6.8, 108.8), (-6.85, 109.0), (-6.85, 109.14), (-6.87, 109.68), (-6.9, 109.9),
               (-6.9, 110.2), (-6.95, 110.42), (-6.55, 110.67), (-6.42, 110.95), (-6.65, 111.3), (-6.7, 111.4),
               (-6.85, 111.9), (-6.88, 112.05), (-6.88, 112.6), (-7.0, 113.0), (-8.4, 113.0), (-8.3, 112.0),
               (-8.2, 111.2), (-8.1, 110.7), (-8.02, 110.33), (-7.85, 109.95), (-7.72, 109.4), (-7.73, 109.0),
               (-7.7, 108.75), (-7.7, 108.65), (-7.78, 108.3), (-7.75, 108.0), (-7.68, 107.7), (-7.5, 107.3),
               (-7.42, 106.8), (-7.38, 106.4), (-7.15, 106.45), (-7.0, 106.53), (-6.95, 106.3), (-6.88, 106.0),
               (-6.85, 105.55), (-6.8, 105.25), (-6.72, 105.2), (-6.62, 105.38), (-6.63, 105.6), (-6.48, 105.65),
               (-6.53, 105.72), (-6.38, 105.83), (-6.3, 105.83), (-6.05, 105.88)]
SUMATRA_SEL = [(-4.5, 103.6), (-5.19, 103.93), (-5.6, 104.25), (-5.92, 104.58), (-5.75, 104.72), (-5.5, 104.62),
               (-5.55, 104.85), (-5.8, 105.05), (-5.95, 105.2), (-5.75, 105.22), (-5.47, 105.27), (-5.55, 105.42),
               (-5.73, 105.6), (-5.87, 105.75), (-5.7, 105.85), (-5.3, 105.85), (-4.5, 105.9)]
GUNUNG = [(-6.72, 106.73, 0.12), (-6.78, 106.98, 0.15), (-6.73, 106.45, 0.15), (-6.89, 108.4, 0.12),
          (-7.24, 109.21, 0.15), (-6.9, 107.6, 0.3), (-7.3, 107.7, 0.3), (-7.2, 109.9, 0.2), (-7.5, 110.43, 0.15),
          (-6.27, 106.04, 0.1), (-5.0, 104.5, 0.4)]

print("  menyiapkan peta Jawa bagian barat...")
PETA = Peta(103, 112, -11.5, -2.5, 450, [], GUNUNG, seed=34,
            darat=[JAWA_DETAIL, pd.SUMATRA, SUMATRA_SEL, pd.KALIMANTAN])

BOGOR = (-6.6, 106.8)
BATAVIA = (-6.13, 106.82)
SUKABUMI = (-6.92, 106.93)
CIANJUR = (-6.82, 107.14)
SALAK = (-6.72, 106.73)
TEGAL = (-6.87, 109.14)
LAMPUNG = (-5.43, 105.26)
EPI_1834 = (-6.47, 106.96)        # pusat gempa hasil pemodelan (ilustratif)
GEMPA_2026 = [(-6.72, 106.66), (-6.78, 106.62)]  # dua gempa 15 Okt 2026 (perkiraan posisi, ilustratif)
CILIWUNG = [(-6.70, 106.76), (-6.62, 106.80), (-6.50, 106.83), (-6.38, 106.82), (-6.25, 106.85), (-6.13, 106.82)]
SESAR = [(-6.40, 106.72), (-6.44, 106.88), (-6.49, 107.02), (-6.53, 107.16)]


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


def kota(d, kamera, ll, nama, alpha=1.0, warna=TINTA, dx=16, dy=-28, uk=32):
    if alpha <= 0.01:
        return
    x, y = layar(kamera, ll)
    a = int(255 * alpha)
    d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=tuple(warna) + (a,), outline=(255, 255, 255, a), width=3)
    se.teks(d, (x + dx, y + dy), nama, uk, warna, nama_font="tangan", anchor="lm" if dx >= 0 else "rm",
            stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def cincin(d, x, y, r, warna, alpha, tebal=8):
    if alpha <= 0.01 or r <= 1:
        return
    d.ellipse((x - r, y - r, x + r, y + r), outline=tuple(warna) + (int(255 * alpha),), width=tebal)


def getar(d, x, y, t, alpha=1.0, cepat=0.8, skala=1.0, warna=(200, 40, 30), n=3):
    """Cincin gelombang gempa yang terus memancar."""
    for i in range(n):
        f = (t * cepat + i / n) % 1.0
        cincin(d, x, y, 20 + f * 220 * skala, warna, (1 - f) * 0.9 * alpha, 7)
    a = int(255 * alpha)
    d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=(220, 50, 30, a), outline=(255, 255, 255, a), width=4)


def ikon_gunung(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.polygon([(x - 60 * s, y + 25 * s), (x - 12 * s, y - 40 * s), (x + 8 * s, y - 30 * s), (x + 60 * s, y + 25 * s)],
              fill=(110, 95, 75, a), outline=(40, 30, 20, a))
    d.polygon([(x - 12 * s, y - 40 * s), (x + 8 * s, y - 30 * s), (x + 2 * s, y - 20 * s), (x - 18 * s, y - 28 * s)],
              fill=(80, 120, 70, a))


def ikon_istana(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.rectangle((x - 46 * s, y - 20 * s, x + 46 * s, y + 14 * s), fill=(245, 240, 228, a), outline=(40, 30, 20, a), width=3)
    d.polygon([(x - 20 * s, y - 20 * s), (x, y - 36 * s), (x + 20 * s, y - 20 * s)], fill=(235, 228, 212, a), outline=(40, 30, 20, a))
    for i in range(4):
        cx = x - 12 * s + i * 8 * s
        d.line((cx, y - 18 * s, cx, y + 12 * s), fill=(150, 140, 125, a), width=max(1, int(2 * s)))


def hdr(img, sub="Oktober 1834", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def goyang(img, kuat, seed):
    """Guncang seluruh layar (zoom sedikit supaya tepi tidak bolong)."""
    if kuat <= 0.5:
        return img
    rng = random.Random(seed)
    m = 40
    besar = img.resize((W + 2 * m, H + 2 * m), Image.BILINEAR)
    dx = int(clamp(rng.uniform(-1, 1) * kuat, -m, m))
    dy = int(clamp(rng.uniform(-1, 1) * kuat, -m, m))
    return besar.crop((m + dx, m + dy, m + dx + W, m + dy + H))


# ------------------------------------------------------------------ ilustrasi istana

G = 1150  # garis tanah

DINDING = (246, 241, 229)
BAYANG = (205, 196, 180)
ATAP = (125, 112, 100)
JENDELA = (70, 85, 100)


def _taman(malam=0.0):
    atas = np.array(se.lerp_rgb((120, 175, 230), (15, 20, 45), malam), np.float32)
    bawah = np.array(se.lerp_rgb((215, 232, 245), (45, 50, 80), malam), np.float32)
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (atas * (1 - g) + bawah * g).repeat(W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    if malam > 0.05:
        rng = random.Random(9)
        for _ in range(60):
            x, y = rng.uniform(0, W), rng.uniform(380, 900)
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 230, int(200 * malam)))
    # siluet Gunung Salak di belakang
    gs = se.lerp_rgb((120, 140, 165), (30, 35, 60), malam)
    d.polygon([(-50, G), (150, 860), (330, 700), (420, 660), (520, 700), (700, 820), (900, 930), (1130, G)], fill=gs + (255,))
    label_a = 1 - malam
    se.teks(d, (300, 765), "Gunung Salak", 30, se.lerp_rgb((60, 70, 90), (180, 180, 200), malam), nama_font="tangan_tipis",
            alpha=0.8 * label_a)
    # rumput
    rumput = se.lerp_rgb((95, 150, 70), (25, 45, 30), malam)
    d.rectangle((0, G, W, H), fill=rumput + (255,))
    rng = random.Random(3)
    for _ in range(140):
        x, y = rng.uniform(0, W), rng.uniform(G + 10, H)
        d.line((x, y, x + rng.uniform(-10, 10), y - rng.uniform(8, 18)), fill=se.lerp_rgb(rumput, (40, 80, 30), 0.5) + (255,), width=3)
    # pohon Kebun Raya di kiri-kanan
    for x, h in ((40, 330), (1040, 360), (150, 250), (930, 260)):
        d.rectangle((x - 12, G - h * 0.45, x + 12, G), fill=se.lerp_rgb((80, 55, 35), (25, 20, 15), malam) + (255,))
        d.ellipse((x - 95, G - h, x + 95, G - h * 0.35), fill=se.lerp_rgb((60, 115, 55), (20, 40, 25), malam) + (255,),
                  outline=se.lerp_rgb((35, 70, 30), (10, 20, 10), malam) + (255,), width=4)
    return img


def _istana(lantai2=1.0, malam=0.0, bendera=0.0, t=0.0):
    """Lapisan istana neoklasik. lantai2 0..1 = tinggi lantai atas."""
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap, "RGBA")
    din = se.lerp_rgb(DINDING, (120, 120, 140), malam * 0.6)
    bay = se.lerp_rgb(BAYANG, (70, 70, 90), malam * 0.6)
    lampu = se.lerp_rgb(JENDELA, (255, 210, 110), malam)
    h1, h2 = 170, 150 * lantai2
    top = G - h1 - h2
    # sayap kiri & kanan
    for x0, x1 in ((90, 300), (780, 990)):
        d.rectangle((x0, G - 130, x1, G), fill=din + (255,), outline=TINTA + (255,), width=4)
        d.rectangle((x0 - 6, G - 146, x1 + 6, G - 130), fill=ATAP + (255,), outline=TINTA + (255,), width=3)
        for wx in range(x0 + 22, x1 - 20, 46):
            d.rounded_rectangle((wx, G - 100, wx + 24, G - 40), 10, fill=lampu + (255,), outline=TINTA + (255,), width=2)
    # lorong penghubung
    for x0, x1 in ((300, 330), (750, 780)):
        d.rectangle((x0, G - 80, x1, G), fill=bay + (255,), outline=TINTA + (255,), width=3)
    # badan utama
    d.rectangle((330, top, 750, G), fill=din + (255,), outline=TINTA + (255,), width=5)
    d.rectangle((322, top - 18, 758, top), fill=ATAP + (255,), outline=TINTA + (255,), width=3)
    for lt in range(2):
        if lt == 1 and lantai2 < 0.6:
            continue
        y0 = G - 130 if lt == 0 else G - h1 - h2 + 30
        for wx in list(range(350, 420, 40)) + list(range(680, 740, 40)):
            d.rounded_rectangle((wx, y0, wx + 24, y0 + 70), 10, fill=lampu + (255,), outline=TINTA + (255,), width=2)
    if h2 > 4:
        d.line((330, G - h1, 750, G - h1), fill=bay + (255,), width=6)
    # serambi bertiang + segitiga atap (pediment)
    d.rectangle((410, top + 10, 670, G), fill=bay + (255,))
    for i in range(6):
        cx = 425 + i * 46
        d.rectangle((cx - 9, top + 14, cx + 9, G - 14), fill=din + (255,), outline=TINTA + (255,), width=2)
    d.rectangle((400, top - 4, 680, top + 16), fill=din + (255,), outline=TINTA + (255,), width=3)
    d.polygon([(392, top - 4), (540, top - 80), (688, top - 4)], fill=din + (255,), outline=TINTA + (255,))
    d.polygon([(420, top - 12), (540, top - 66), (660, top - 12)], outline=bay + (255,))
    d.rectangle((380, G - 14, 700, G), fill=bay + (255,), outline=TINTA + (255,), width=2)
    if bendera > 0.01:
        px, py = 540, top - 80
        tinggi = 150
        d.line((px, py, px, py - tinggi), fill=(60, 50, 40, 255), width=6)
        fy = py - tinggi + (1 - bendera) * (tinggi - 60)
        kib = math.sin(t * 6) * 6
        d.polygon([(px + 3, fy), (px + 95, fy + kib), (px + 95, fy + 26 + kib), (px + 3, fy + 26)], fill=(220, 30, 40, 255))
        d.polygon([(px + 3, fy + 26), (px + 95, fy + 26 + kib), (px + 95, fy + 52 + kib), (px + 3, fy + 52)],
                  fill=(250, 250, 250, 255), outline=(150, 150, 150, 255))
    return lap


_RNG_RETAK = random.Random(18)
RETAK = []
for _ in range(9):
    x, y = _RNG_RETAK.uniform(340, 740), _RNG_RETAK.uniform(G - 300, G - 60)
    garis = [(x, y)]
    for _ in range(6):
        x += _RNG_RETAK.uniform(-30, 30)
        y += _RNG_RETAK.uniform(10, 40)
        garis.append((x, y))
    RETAK.append(garis)
for x0 in (120, 860):
    RETAK.append([(x0, G - 140), (x0 + 15, G - 110), (x0 + 5, G - 80), (x0 + 22, G - 40)])


def _retak(lap, k):
    if k <= 0.01:
        return
    d = ImageDraw.Draw(lap, "RGBA")
    for garis in RETAK:
        n = max(2, int(len(garis) * clamp(k) + 0.999))
        d.line(garis[:n], fill=(40, 30, 25, 255), width=5)


STRIP = [80, 200, 300, 400, 470, 540, 610, 680, 760, 870, 1000]


def _runtuh(lap, k, seed=4):
    """Potong istana jadi irisan vertikal; irisan tengah (bagian depan) jatuh & miring."""
    if k <= 0.01:
        return lap
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rng = random.Random(seed)
    for i in range(len(STRIP) - 1):
        x0, x1 = STRIP[i], STRIP[i + 1]
        tengah = 330 <= x0 < 750
        a = rng.uniform(0.55, 1.0) if tengah else rng.uniform(0.04, 0.18)
        sudut = rng.uniform(-16, 16) * a * k
        turun = a * k * 300
        iris = lap.crop((x0, 0, x1, G)).rotate(sudut, resample=Image.BICUBIC, expand=True)
        px = int(x0 - (iris.width - (x1 - x0)) / 2)
        py = int(turun - (iris.height - G) / 2)
        out.paste(iris, (px, py), iris)
    out.paste((0, 0, 0, 0), (0, G, W, H))
    return out


def _puing(img, k, t, malam=0.0):
    if k <= 0.01:
        return
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(7)
    for _ in range(45):
        x = rng.uniform(330, 760)
        w, h = rng.uniform(20, 60), rng.uniform(14, 36)
        y = G - rng.uniform(0, 70) * k
        c = se.lerp_rgb((215, 205, 190), (110, 100, 95), rng.random() * 0.6 + malam * 0.3)
        d.polygon([(x, y), (x + w, y + rng.uniform(-6, 6)), (x + w * 0.8, y + h), (x - 5, y + h * 0.8)],
                  fill=c + (int(255 * clamp(k * 2)),), outline=(60, 50, 40, int(255 * clamp(k * 2))))
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    for i in range(40):
        f = (rng.random() + t * 0.15) % 1
        x = rng.uniform(260, 820) + math.sin(t + i) * 20
        y = G - 40 - f * 380
        r = 50 + f * 110
        dl.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=(190, 175, 150, int(110 * k * (1 - f))))
    img.alpha_composite(lap)


def adegan_istana(lantai2=1.0, malam=0.0, retak=0.0, runtuh=0.0, t=0.0, bendera=0.0, naik=1.0):
    img = _taman(malam)
    lap = _istana(lantai2, malam, bendera, t)
    _retak(lap, retak)
    lap = _runtuh(lap, runtuh)
    if naik < 0.999:  # istana "tumbuh" dari tanah (dibangun ulang)
        geser = int((1 - naik) * 520)
        lap2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lap2.paste(lap, (0, geser), lap)
        lap2.paste((0, 0, 0, 0), (0, G, W, H))
        lap = lap2
    img.alpha_composite(lap)
    _puing(img, runtuh, t, malam)
    return img


# ------------------------------------------------------------------ adegan

def a_hook(c):
    k = c.t / c.d
    rt = c.p(0.1, 0.5)
    rn = c.p(0.35, 0.75)
    img = adegan_istana(1.0, 0.0, rt, rn * 0.9, c.t)
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out(c.t / 0.35)
    se.teks(d, (540, 520), "1834", int(200 * s) + 1, (255, 235, 180), nama_font="caption", stroke=10,
            stroke_warna=(40, 25, 10))
    se.teks(d, (540, 660), "istana presiden ini pernah ambruk", 44, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(40, 25, 10), alpha=c.p(0.15, 0.25))
    hdr(img, alpha=c.p(0.8, 0.95))
    kuat = 26 * c.p(0.08, 0.2) * (1 - c.p(0.75, 0.9))
    return goyang(img, kuat, int(c.t * 30))


def a_tren(c):
    kamera = Kamera(*cam(-6.75, 106.8, 1.6))
    img, d = peta(kamera)
    kota(d, kamera, BATAVIA, "Jakarta")
    kota(d, kamera, BOGOR, "Bogor", dx=18, dy=-30)
    kota(d, kamera, SUKABUMI, "Sukabumi", dx=18, dy=26)
    for i, ll in enumerate(GEMPA_2026):
        a = c.p(0.04 + i * 0.12, 0.1 + i * 0.12)
        if a > 0:
            x, y = layar(kamera, ll)
            getar(d, x, y, c.t + i * 0.3, a, skala=0.8)
    kartu(img, 300, 420, "M 3,5 · 17.49 WIB", "gempa pertama", MERAH, alpha=c.p(0.05, 0.12), tiang=False)
    kartu(img, 780, 420, "M 4,1 · 17.58 WIB", "sembilan menit kemudian", MERAH, alpha=c.p(0.17, 0.24), tiang=False)
    kartu(img, 540, 1220, "Sumber: sesar aktif", "gempa dangkal · data BMKG", BIRU, alpha=c.p(0.32, 0.4), tiang=False,
          skala=back_out((c.t / c.d - 0.32) / 0.1))
    kartu(img, 540, 1330, "Tidak ada laporan kerusakan", "", (40, 120, 70), alpha=c.p(0.48, 0.55), tiang=False)
    se.teks(d, (540, 660), "…tapi daerah ini punya sejarah", 46, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(0, 0, 0), alpha=c.p(0.7, 0.78))
    hdr(img, "Kamis, 15 Oktober 2026")
    return img


def a_buitenzorg(c):
    kamera = se.kamera_antara(cam(-6.6, 106.8, 1.6), cam(-6.55, 106.8, 2.6), c.p(0.0, 0.4))
    img, d = peta(kamera)
    kota(d, kamera, BATAVIA, "Batavia", alpha=1 - c.p(0.2, 0.3))
    x, y = layar(kamera, BOGOR)
    s = back_out((c.t / c.d - 0.25) / 0.12) if c.t / c.d > 0.25 else 0
    if s > 0:
        ikon_istana(d, x, y, 2.4 * s)
    kartu(img, x, y - 100, "Gubernur Jenderal van Imhoff", "mulai dibangun 1745", BIRU, alpha=c.p(0.3, 0.38))
    s2 = back_out((c.t / c.d - 0.6) / 0.12) if c.t / c.d > 0.6 else 0
    if s2 > 0:
        se.teks(d, (540, 1110), "BUITENZORG", int(96 * s2) + 1, (255, 235, 180), nama_font="caption", stroke=8,
                stroke_warna=(30, 20, 10))
    kartu(img, 540, 1240, "artinya: tanpa kekhawatiran", "", (60, 60, 70), alpha=c.p(0.7, 0.78), tiang=False)
    hdr(img, "1745")
    return img


def a_daendels(c):
    l2 = c.p(0.25, 0.65)
    img = adegan_istana(l2, 0.0, 0.0, 0.0, c.t)
    kartu(img, 540, 470, "Masa Daendels (1808–1811)", "dirombak jadi dua lantai", BIRU, alpha=c.p(0.05, 0.14),
          tiang=False, skala=back_out((c.t / c.d - 0.05) / 0.1))
    if l2 > 0.05:
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 600), "makin megah", 48, (255, 235, 180), nama_font="caption", stroke=6,
                stroke_warna=(40, 25, 10), alpha=c.p(0.6, 0.7))
    hdr(img, "Awal 1800-an")
    return img


def a_1699(c):
    kamera = se.kamera_antara(cam(-6.55, 106.8, 2.0), cam(-6.5, 106.8, 2.1), c.p(0, 1))
    img, d = peta(kamera)
    sx, sy = layar(kamera, SALAK)
    ikon_gunung(d, sx, sy, 1.2)
    label(d, (sx - 40, sy + 60), "Gunung Salak", 34, TINTA)
    getar(d, sx, sy - 10, c.t, c.p(0.05, 0.12) * (1 - c.p(0.4, 0.5)), skala=1.2)
    # longsor
    lon = c.p(0.25, 0.45)
    if lon > 0:
        rng = random.Random(5)
        for _ in range(16):
            x = sx + rng.uniform(-70, 70)
            y = sy + rng.uniform(-30, 20)
            r = rng.uniform(10, 24) * lon
            d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=COKLAT + (220,))
    titik = [layar(kamera, ll) for ll in CILIWUNG]
    ujung = se.garis_putus(d, titik, c.p(0.4, 0.75), COKLAT, tebal=12, putus=22, celah=8)
    mx, my = layar(kamera, (-6.38, 106.82))
    label(d, (mx + 90, my), "Ciliwung", 34, COKLAT, c.p(0.45, 0.55))
    kota(d, kamera, BATAVIA, "Batavia", dx=20, dy=-32, uk=36)
    kota(d, kamera, BOGOR, "Bogor", dx=20, dy=10)
    bx, by = layar(kamera, BATAVIA)
    kartu(img, bx, by - 50, "Lumpur sampai Batavia", "puluhan bangunan batu roboh", COKLAT, alpha=c.p(0.72, 0.8))
    s = back_out(c.t / c.d / 0.12)
    se.teks(d, (540, 1310), "1699", int(130 * s) + 1, (255, 220, 160), nama_font="caption", stroke=8, stroke_warna=(40, 20, 10))
    hdr(img, "Peringatan pertama")
    return img


def a_malam(c):
    k = c.t / c.d
    malam = 1 - c.p(0.6, 0.78)
    img = adegan_istana(1.0, malam, 0.0, 0.0, c.t)
    kartu(img, 540, 470, "Oktober 1834", "malam: guncangan pendahuluan", (60, 60, 90), alpha=c.p(0.05, 0.14),
          tiang=False, skala=back_out((k - 0.05) / 0.1))
    kartu(img, 540, 620, "Paginya: gempa utama", "", MERAH, alpha=c.p(0.8, 0.86), tiang=False,
          skala=back_out((k - 0.8) / 0.1))
    kuat = 0.0
    for f in (0.3, 0.45):
        if f <= k < f + 0.06:
            kuat = 10 * (1 - (k - f) / 0.06)
    if k > 0.85:
        kuat = 30 * c.p(0.85, 0.92)
    hdr(img)
    return goyang(img, kuat, int(c.t * 30))


def a_ambruk(c):
    rt = c.p(0.0, 0.2)
    rn = c.p(0.12, 0.55)
    img = adegan_istana(1.0, 0.0, rt, rn, c.t)
    d = ImageDraw.Draw(img, "RGBA")
    kartu(img, 540, 470, "Bagian depan roboh", "dinding retak di mana-mana", MERAH, alpha=c.p(0.2, 0.28) * (1 - c.p(0.55, 0.6)),
          tiang=False)
    kartu(img, 540, 470, "Gubernur Jenderal Baud", "memerintahkan sisanya dirobohkan", (60, 60, 70),
          alpha=c.p(0.6, 0.68), tiang=False, skala=back_out((c.t / c.d - 0.6) / 0.1))
    hdr(img)
    kuat = 34 * (1 - c.p(0.4, 0.6))
    return goyang(img, kuat, int(c.t * 30))


def a_dampak(c):
    kamera = Kamera(*cam(-6.6, 107.2, 0.54))
    img, d = peta(kamera)
    ex, ey = layar(kamera, EPI_1834)
    jang = c.p(0.0, 0.8)
    for i in range(4):
        f = clamp(jang * 1.3 - i * 0.25)
        if f > 0:
            cincin(d, ex, ey, f * 950, (220, 70, 30), (1 - f) * 0.9, 8)
    d.ellipse((ex - 14, ey - 14, ex + 14, ey + 14), fill=(220, 50, 30, 255), outline=(255, 255, 255, 255), width=4)
    # jalan retak Bogor - Cianjur
    a = c.p(0.05, 0.25)
    if a > 0:
        x0, y0 = layar(kamera, BOGOR)
        x1, y1 = layar(kamera, CIANJUR)
        pts = [(lerp(x0, x1, f) + (8 if j % 2 else -8), lerp(y0, y1, f)) for j, f in enumerate(np.linspace(0, a, 8))]
        d.line(pts, fill=(170, 20, 20, 255), width=6)
    kota(d, kamera, BOGOR, "Bogor", dx=-16, dy=-24, uk=30)
    kota(d, kamera, CIANJUR, "Cianjur", dx=16, dy=24, uk=30)
    kota(d, kamera, BATAVIA, "Batavia", dx=-16, dy=-26, uk=30, alpha=c.p(0.25, 0.32))
    kota(d, kamera, TEGAL, "Tegal", dx=-16, dy=-28, uk=34, alpha=c.p(0.55, 0.62))
    kota(d, kamera, LAMPUNG, "Lampung", dx=16, dy=-28, uk=34, alpha=c.p(0.72, 0.78))
    kartu(img, 540, 1250, "Jalan Bogor–Cianjur retak", "", MERAH, alpha=c.p(0.08, 0.16), tiang=False)
    bx, by = layar(kamera, BATAVIA)
    kartu(img, bx, by - 50, "Rumah & gedung batu rusak", "Batavia", (60, 60, 70), alpha=c.p(0.3, 0.38))
    tx, ty = layar(kamera, TEGAL)
    kartu(img, tx, ty + 150, "Terasa sampai Tegal", "", BIRU, alpha=c.p(0.58, 0.65), tiang=False)
    lx, ly = layar(kamera, LAMPUNG)
    kartu(img, lx, ly - 130, "…bahkan Lampung", "", BIRU, alpha=c.p(0.75, 0.82), tiang=False)
    hdr(img)
    return img


def a_sebab(c):
    kamera = Kamera(*cam(-6.55, 106.9, 1.9))
    img, d = peta(kamera)
    sx, sy = layar(kamera, SALAK)
    ikon_gunung(d, sx, sy, 1.1)
    kota(d, kamera, BOGOR, "Bogor", dx=-18, dy=-26)
    kartu(img, sx, sy + 120, "Dulu: gara-gara Gunung Salak?", "", (110, 95, 75), alpha=c.p(0.03, 0.1),
          coret=c.p(0.35, 0.45), tiang=False)
    titik = [layar(kamera, ll) for ll in SESAR]
    se.garis_putus(d, titik, c.p(0.4, 0.6), (200, 30, 30), tebal=10, putus=26, celah=10, panah=False)
    if c.p(0.4, 0.6) > 0.5:
        x, y = titik[-1]
        label(d, (x - 40, y + 50), "sesar (ilustrasi)", 30, (170, 20, 20))
    kartu(img, 540, 620, "Kini: sesar aktif di daratan", "kajian Geoscience Australia (2015)", BIRU,
          alpha=c.p(0.45, 0.53), tiang=False, skala=back_out((c.t / c.d - 0.45) / 0.1))
    s = back_out((c.t / c.d - 0.72) / 0.12) if c.t / c.d > 0.72 else 0
    if s > 0:
        se.teks(d, (540, 1340), "± MAGNITUDO 7", int(80 * s) + 1, (255, 220, 160), nama_font="caption", stroke=8,
                stroke_warna=(40, 20, 10))
    hdr(img, "Apa penyebabnya?")
    return img


def a_bangun(c):
    naik = c.p(0.05, 0.4)
    img = adegan_istana(0.0, 0.0, 0.0, 0.0, c.t, bendera=c.p(0.7, 0.9), naik=naik)
    kartu(img, 540, 470, "Dibangun ulang 1850-an", "sengaja cuma satu lantai", (40, 120, 70), alpha=c.p(0.05, 0.14),
          tiang=False, skala=back_out((c.t / c.d - 0.05) / 0.1))
    kartu(img, 540, 1280, "Istana Bogor hari ini", "", MERAH, alpha=c.p(0.72, 0.8), tiang=False,
          skala=back_out((c.t / c.d - 0.72) / 0.1))
    hdr(img, "Setelah 1834")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(-6.6, 106.8, 1.6))
    img, d = peta(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1000), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Tanah kita masih bergerak", 50, TINTA, nama_font="judul", alpha=a)
        # garis seismograf
        pts = []
        for i in range(120):
            x = 160 + i * 6.3
            amp = 90 * math.exp(-((i - 60) / 18) ** 2) + 8
            pts.append((x, 760 + math.sin(i * 1.9 + c.t * 8) * amp))
        n = max(2, int(len(pts) * c.p(0.05, 0.3)))
        d.line(pts[:n], fill=(200, 30, 30, int(255 * a)), width=5)
        se.teks(d, (540, 940), "Kenali jalur evakuasi di sekitarmu!", 42, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Istana presiden ini pernah ambruk dihantam gempa. Lokasinya, dekat banget sama gempa "
                   "yang lagi rame.", a_hook, transisi=False),
    Adegan("tren", "Lagi rame soal gempa beruntun di Sukabumi dan Bogor? Kata BMKG, sumbernya sesar aktif. "
                   "Untungnya nggak ada kerusakan. Tapi daerah ini punya sejarah gempa yang serem.", a_tren),
    Adegan("buitenzorg", "Tahun tujuh belas empat puluh lima, Gubernur Jenderal van Imhoff mulai membangun rumah "
                         "peristirahatan di Bogor. Namanya Buitenzorg. Artinya, tanpa kekhawatiran.", a_buitenzorg,
           transisi=False),
    Adegan("daendels", "Di masa Daendels, bangunannya dirombak jadi dua lantai, makin megah.", a_daendels),
    Adegan("1699", "Padahal, alam udah ngasih peringatan. Tahun enam belas sembilan puluh sembilan, gempa besar "
                   "bikin Gunung Salak longsor. Lumpurnya hanyut lewat Ciliwung sampai Batavia.", a_1699),
    Adegan("malam", "Lalu, Oktober delapan belas tiga puluh empat. Malamnya, tanah mulai bergetar. Paginya, datang "
                    "guncangan yang jauh lebih besar.", a_malam),
    Adegan("ambruk", "Istana Buitenzorg rusak parah. Bagian depannya roboh. Saking parahnya, Gubernur Jenderal Baud "
                     "menyuruh sisanya dirobohkan sekalian.", a_ambruk, transisi=False),
    Adegan("dampak", "Jalan Bogor ke Cianjur retak. Gedung batu di Batavia ikut rusak. Getarannya kerasa sampai Tegal, "
                     "bahkan Lampung.", a_dampak),
    Adegan("sebab", "Dulu, gempa ini dikaitkan dengan Gunung Salak. Tapi peneliti sekarang menduga, sumbernya sesar "
                    "aktif di daratan. Kira-kira magnitudo tujuh.", a_sebab),
    Adegan("bangun", "Istananya lalu dibangun ulang tahun delapan belas lima puluhan. Sengaja cuma satu lantai, biar "
                     "lebih aman dari gempa. Itulah Istana Bogor sekarang.", a_bangun),
    Adegan("penutup", "Jadi, gempa kemarin itu pengingat. Tanah kita masih bergerak. Kenali jalur evakuasi di "
                      "sekitarmu, ya. Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
