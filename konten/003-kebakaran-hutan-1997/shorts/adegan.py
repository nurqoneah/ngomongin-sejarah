"""Shorts ±90 detik: Kebakaran Hutan & Kabut Asap 1997–1998.

Peta Asia Tenggara + dua adegan ilustrasi (langit berkabut, penampang gambut).
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

NAMA_FILE = "kebakaran-hutan-1997-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "KABUT ASAP 1997"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
ORANYE = (240, 120, 30)
ASAP = (150, 135, 110)

print("  menyiapkan peta Asia Tenggara...")
PETA = Peta(90, 125, -12, 22, 100, [], [(-2, 114, 1.5), (0, 101, 1.2), (5, 117, 1.0), (18, 101, 3), (14, 106, 2)],
            seed=21, darat=pd.SEMUA)

TITIK_API = {
    "kalimantan": [(-2.5, 114.0), (-2.2, 113.5), (-3.0, 114.5), (-1.8, 114.8), (-2.8, 112.8), (-3.3, 115.0),
                   (0.5, 116.8), (-0.5, 116.5), (1.0, 117.2), (-0.5, 110.5), (0.2, 109.8), (-1.5, 112.0),
                   (-2.0, 111.0), (-1.0, 115.8)],
    "sumatra": [(0.8, 102.0), (1.4, 101.5), (0.4, 103.0), (-1.5, 103.8), (-1.2, 104.2), (-3.0, 105.0),
                (-2.6, 104.6), (-3.4, 105.3), (-0.5, 102.5), (1.8, 100.8)],
}
SEMUA_API = TITIK_API["kalimantan"] + TITIK_API["sumatra"]
NEGARA = {"MALAYSIA": (4.2, 102.0), "SINGAPURA": (1.35, 103.82), "BRUNEI": (4.9, 114.9), "THAILAND": (8.0, 99.4),
          "Sarawak": (2.4, 112.8)}
LABEL_ID = {"SUMATRA": (-0.3, 101.3), "KALIMANTAN": (-0.8, 113.3), "JAWA": (-7.2, 110.0)}
IBU_KOTA = [(3.14, 101.69), (1.35, 103.82), (13.75, 100.5), (4.89, 114.94), (14.6, 121.0), (11.55, 104.92),
            (17.97, 102.6), (16.84, 96.17), (21.0, 105.8)]
JAKARTA = (-6.2, 106.8)
MEDAN = (3.6, 98.67)


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


def api(d, x, y, t, s=1.0, alpha=1.0, seed=0):
    """Ikon api kecil yang berkedip."""
    if alpha <= 0.01:
        return
    k = 1 + 0.15 * math.sin(t * 11 + seed * 1.7)
    s = s * k
    a = int(255 * alpha)
    luar = [(x, y - 34 * s), (x + 14 * s, y - 12 * s), (x + 16 * s, y + 6 * s), (x + 8 * s, y + 16 * s),
            (x - 8 * s, y + 16 * s), (x - 16 * s, y + 6 * s), (x - 12 * s, y - 14 * s), (x - 4 * s, y - 6 * s)]
    d.polygon(luar, fill=(225, 60, 25, a), outline=(80, 20, 10, a))
    dalam = [(x + 1 * s, y - 16 * s), (x + 8 * s, y + 2 * s), (x + 5 * s, y + 12 * s), (x - 5 * s, y + 12 * s),
             (x - 8 * s, y + 2 * s)]
    d.polygon(dalam, fill=(255, 205, 60, a))


def titik_api(d, kamera, t, alpha=1.0, munculkan=1.0, s=1.0, daftar=SEMUA_API):
    n = int(len(daftar) * clamp(munculkan) + 0.999)
    for i, ll in enumerate(daftar[:n]):
        x, y = layar(kamera, ll)
        api(d, x, y, t, s, alpha, i)


def kabut(img, kamera, t, kuat=1.0, jangkau=1.0, seed=3):
    """Partikel asap dari titik api, terbawa angin ke barat laut."""
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    for i in range(260):
        asal = SEMUA_API[i % len(SEMUA_API)]
        f = rng.random() * jangkau
        lat = asal[0] + f * rng.uniform(2, 7) + rng.gauss(0, 1.0)
        lon = asal[1] - f * rng.uniform(1, 6) + rng.gauss(0, 1.0)
        x, y = layar(kamera, (lat, lon))
        x += math.sin(t * 0.7 + i) * 12
        r = rng.uniform(40, 110) * kamera.zoom / 0.6
        d.ellipse((x - r, y - r, x + r, y + r), fill=ASAP + (int(70 * kuat),))
    img.alpha_composite(lap)
    se.tint(img, (190, 160, 100), 0.18 * kuat * jangkau)


def hdr(img, sub="1997 – 1998", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def label_id(d, kamera, alpha=1.0):
    for nama, ll in LABEL_ID.items():
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 40, TINTA, alpha)


# ------------------------------------------------------------------ adegan

def _langit(kekuningan):
    """Langit gradasi + gedung siluet (ilustrasi kota berkabut)."""
    atas = np.array(se.lerp_rgb((110, 170, 230), (190, 150, 70), kekuningan), np.float32)
    bawah = np.array(se.lerp_rgb((200, 225, 245), (225, 190, 110), kekuningan), np.float32)
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (atas * (1 - g) + bawah * g).repeat(W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    return img, ImageDraw.Draw(img, "RGBA")


GEDUNG = [(0, 1250, 130), (120, 1120, 110), (220, 1300, 90), (300, 1050, 140), (430, 1200, 100), (520, 980, 120),
          (630, 1150, 110), (730, 1080, 130), (850, 1230, 90), (930, 1000, 150)]


def a_hook(c):
    kuning = c.p(0.0, 0.5)
    img, d = _langit(kuning)
    # matahari pucat
    r = 120
    d.ellipse((540 - r, 520 - r, 540 + r, 520 + r), fill=se.lerp_rgb((255, 240, 160), (255, 230, 200), kuning) + (int(255 - 120 * kuning),))
    for x, y, w in GEDUNG:
        d.rectangle((x, y, x + w, H), fill=(60, 55, 60, 255))
        for wy in range(y + 30, H - 300, 60):
            for wx in range(x + 18, x + w - 20, 34):
                d.rectangle((wx, wy, wx + 14, wy + 22), fill=(230, 200, 120, 160))
    # kabut menebal
    rng = random.Random(1)
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    for i in range(70):
        x = (rng.uniform(-200, W + 200) + c.t * rng.uniform(10, 40)) % (W + 400) - 200
        y = rng.uniform(300, H)
        rr = rng.uniform(120, 260)
        dl.ellipse((x - rr, y - rr * 0.6, x + rr, y + rr * 0.6), fill=(200, 170, 110, int(60 * kuning)))
    img.alpha_composite(lap)
    se.tint(img, (170, 130, 60), 0.35 * kuning)
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out(c.t / 0.35)
    se.teks(d, (540, 820), "1997", int(220 * s) + 1, (255, 235, 180), nama_font="caption", stroke=10, stroke_warna=(40, 25, 10))
    se.teks(d, (540, 1000), "matahari siang kayak bulan pucat", 46, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(40, 25, 10), alpha=c.p(0.2, 0.3))
    se.teks(d, (540, 1150), "asapnya… dari Indonesia", 56, (255, 200, 120), nama_font="caption", stroke=7,
            stroke_warna=(40, 25, 10), alpha=c.p(0.72, 0.82))
    hdr(img, alpha=c.p(0.8, 0.95))
    return img


def a_penyebab(c):
    kamera = Kamera(*cam(-0.5, 108.5, 0.6))
    img, d = peta(kamera)
    se.tint(img, (230, 150, 40), 0.18 * c.p(0.1, 0.35))
    d = ImageDraw.Draw(img, "RGBA")
    label_id(d, kamera)
    se.kartu(img, 540, 720, "El Niño", "kemarau panjang, hutan & gambut kering", ORANYE,
             alpha=c.p(0.05, 0.14) * (1 - c.p(0.5, 0.56)), tiang=False, skala=back_out((c.t / c.d - 0.05) / 0.1))
    titik_api(d, kamera, c.t, munculkan=c.p(0.55, 0.9))
    se.kartu(img, 540, 720, "Buka lahan dengan cara dibakar", "cara paling murah", MERAH, alpha=c.p(0.6, 0.68),
             tiang=False, skala=back_out((c.t / c.d - 0.6) / 0.1))
    hdr(img)
    return img


def a_gambut(c):
    img = Image.new("RGBA", (W, H), (180, 205, 225, 255))
    d = ImageDraw.Draw(img, "RGBA")
    tanah_y, gambut_y, dasar_y = 760, 830, 1260
    # pohon
    rng = random.Random(2)
    for i in range(9):
        x = 60 + i * 120 + rng.uniform(-20, 20)
        h = rng.uniform(160, 260)
        d.rectangle((x - 8, tanah_y - h * 0.5, x + 8, tanah_y), fill=(90, 60, 35, 255))
        d.ellipse((x - 55, tanah_y - h, x + 55, tanah_y - h * 0.4), fill=(70, 130, 60, 255), outline=(40, 70, 30, 255), width=4)
    d.rectangle((0, tanah_y, W, gambut_y), fill=(120, 90, 55, 255))
    d.rectangle((0, gambut_y, W, dasar_y), fill=(70, 45, 28, 255))
    for i in range(160):
        x, y = rng.uniform(0, W), rng.uniform(gambut_y + 10, dasar_y - 10)
        d.line((x, y, x + rng.uniform(-30, 30), y + rng.uniform(-8, 8)), fill=(95, 65, 40, 255), width=4)
    d.rectangle((0, dasar_y, W, H), fill=(150, 140, 130, 255))
    se.teks(d, (180, gambut_y + 50), "GAMBUT", 52, (240, 210, 160), nama_font="caption", stroke=5, stroke_warna=(30, 20, 10))
    se.teks(d, (180, dasar_y + 60), "tanah mineral", 34, (60, 50, 40), nama_font="tangan")
    # bara menjalar di bawah tanah
    maju = c.p(0.3, 0.95)
    if maju > 0:
        lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        ujung = 80 + maju * 900
        for i in range(60):
            x = rng.uniform(60, ujung)
            y = rng.uniform(gambut_y + 40, dasar_y - 60)
            r = rng.uniform(20, 55) * (0.8 + 0.2 * math.sin(c.t * 7 + i))
            dl.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=(255, 120, 30, 110))
            dl.ellipse((x - r * 0.4, y - r * 0.25, x + r * 0.4, y + r * 0.25), fill=(255, 220, 90, 160))
        img.alpha_composite(lap)
        d = ImageDraw.Draw(img, "RGBA")
        for i, x in enumerate(range(140, int(ujung), 180)):
            for j in range(5):
                f = (c.t * 0.4 + j * 0.2 + i * 0.13) % 1
                r = 20 + f * 50
                d.ellipse((x - r, tanah_y - f * 320 - r, x + r, tanah_y - f * 320 + r), fill=(110, 100, 95, int(150 * (1 - f))))
    se.kartu(img, 540, 470, "Gambut = spons karbon", "", (90, 60, 35), alpha=c.p(0.05, 0.14), tiang=False,
             skala=back_out((c.t / c.d - 0.05) / 0.1))
    se.kartu(img, 540, 1360, "Api menjalar di bawah tanah", "berbulan-bulan, susah dipadamkan", MERAH,
             alpha=c.p(0.45, 0.55), tiang=False)
    hdr(img)
    return img


def a_luas(c):
    kamera = Kamera(*cam(-1.0, 108.5, 0.62))
    img, d = peta(kamera)
    label_id(d, kamera, 0.8)
    # bekas terbakar (hangus) meluas
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    rng = random.Random(6)
    k = c.p(0.0, 0.6)
    for i, (lat, lon) in enumerate(SEMUA_API):
        for j in range(6):
            x, y = layar(kamera, (lat + rng.gauss(0, 0.5), lon + rng.gauss(0, 0.6)))
            r = rng.uniform(20, 46) * k
            dl.ellipse((x - r, y - r, x + r, y + r), fill=(40, 25, 15, 200))
    img.alpha_composite(lap)
    d = ImageDraw.Draw(img, "RGBA")
    titik_api(d, kamera, c.t, alpha=1 - c.p(0.6, 0.8))
    juta = 10 * c.p(0.05, 0.6)
    se.teks(d, (540, 760), f"{juta:.1f} JUTA".replace(".", ","), 120, MERAH, nama_font="caption", stroke=9,
            stroke_warna=(0, 0, 0), alpha=c.p(0.02, 0.1))
    se.teks(d, (540, 860), "hektar terbakar", 48, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0),
            alpha=c.p(0.02, 0.1))
    se.kartu(img, 540, 1050, "≈ seluas Korea Selatan", "", (60, 60, 70), alpha=c.p(0.62, 0.7), tiang=False,
             skala=back_out((c.t / c.d - 0.62) / 0.1))
    hdr(img)
    return img


def a_kabut(c):
    kamera = se.kamera_antara(cam(-0.5, 109, 0.62), cam(3.0, 106.5, 0.66), c.p(0.0, 0.5))
    img, d = peta(kamera)
    titik_api(d, kamera, c.t, alpha=0.9)
    kabut(img, kamera, c.t, kuat=c.p(0.0, 0.2), jangkau=0.3 + 0.7 * c.p(0.0, 0.55))
    d = ImageDraw.Draw(img, "RGBA")
    for i, (nama, ll) in enumerate(NEGARA.items()):
        if nama == "Sarawak":
            continue
        a = c.p(0.25 + i * 0.07, 0.32 + i * 0.07)
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 38, (120, 20, 15), a, "caption")
    x, y = layar(kamera, NEGARA["Sarawak"])
    se.kartu(img, min(x, W - 230), y, "Sarawak: status darurat", "September 1997", MERAH, alpha=c.p(0.7, 0.78),
             skala=back_out((c.t / c.d - 0.7) / 0.1))
    hdr(img)
    return img


def _pesawat(d, x, y, s=1.0, a=255):
    d.polygon([(x - 50 * s, y), (x + 50 * s, y - 6 * s), (x + 58 * s, y), (x + 50 * s, y + 6 * s)], fill=(240, 240, 245, a), outline=(40, 40, 50, a))
    d.polygon([(x - 5 * s, y), (x + 15 * s, y - 40 * s), (x + 25 * s, y - 40 * s), (x + 15 * s, y)], fill=(220, 220, 230, a), outline=(40, 40, 50, a))
    d.polygon([(x - 5 * s, y), (x + 15 * s, y + 40 * s), (x + 25 * s, y + 40 * s), (x + 15 * s, y)], fill=(220, 220, 230, a), outline=(40, 40, 50, a))
    d.polygon([(x - 50 * s, y), (x - 40 * s, y - 20 * s), (x - 32 * s, y - 20 * s), (x - 36 * s, y)], fill=(200, 60, 40, a))


def a_korban(c):
    kamera = Kamera(*cam(2.0, 102.5, 0.7))
    img, d = peta(kamera)
    titik_api(d, kamera, c.t, alpha=0.8)
    kabut(img, kamera, c.t, kuat=1.0, jangkau=1.0)
    se.tint(img, (40, 30, 15), 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 620, "Jutaan orang sesak napas", "", (90, 70, 50), alpha=c.p(0.02, 0.1), tiang=False)
    se.kartu(img, 540, 760, "Sekolah & bandara tutup", "", (90, 70, 50), alpha=c.p(0.22, 0.3), tiang=False)
    a = c.p(0.45, 0.55)
    if a > 0:
        x, y = layar(kamera, MEDAN)
        _pesawat(d, x - 60, y - 70, 0.9, int(255 * a))
        se.kartu(img, x + 170, y + 60, "Garuda GA 152 · 26 Sep 1997", "234 jiwa · kabut ikut jadi faktor", MERAH,
                 alpha=a, tiang=False)
    hdr(img)
    return img


def a_karbon(c):
    img = Image.new("RGBA", (W, H), (30, 28, 34, 255))
    d = ImageDraw.Draw(img, "RGBA")
    se.panel(img, (80, 420, 1000, 1260), alpha=c.p(0, 0.08), warna=(247, 236, 208))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 500), "KARBON YANG LEPAS", 52, (150, 40, 30), nama_font="judul", alpha=c.p(0.02, 0.1))
    # batang perbandingan
    x0, x1 = 160, 920
    lebar = x1 - x0
    y1 = 690
    se.teks(d, (x0, y1 - 50), "Emisi BBM seluruh dunia, 1 tahun", 32, TINTA, anchor="lm", alpha=c.p(0.1, 0.18))
    d.rounded_rectangle((x0, y1, x0 + lebar * c.p(0.12, 0.3), y1 + 70), 12, fill=(70, 70, 80, 255))
    y2 = 920
    se.teks(d, (x0, y2 - 50), "Gambut Indonesia, 1997", 32, TINTA, anchor="lm", alpha=c.p(0.35, 0.42))
    k = c.p(0.4, 0.75)
    d.rounded_rectangle((x0, y2, x0 + lebar * 0.13 * k, y2 + 70), 12, fill=(200, 60, 30, 255))
    d.rounded_rectangle((x0, y2, x0 + lebar * 0.40 * k, y2 + 70), 12, outline=(200, 60, 30, 255), width=5)
    se.teks(d, (540, 1080), "13 – 40 %", 110, MERAH, nama_font="caption", stroke=6, stroke_warna=(255, 255, 255),
            alpha=c.p(0.7, 0.8))
    se.teks(d, (540, 1180), "Page dkk., Nature (2002)", 28, (110, 90, 70), nama_font="tangan_tipis", alpha=c.p(0.75, 0.85))
    hdr(img)
    return img


def a_asean(c):
    kamera = Kamera(*cam(6.0, 107.0, 0.58))
    img, d = peta(kamera)
    jx, jy = layar(kamera, JAKARTA)
    for i, ll in enumerate(IBU_KOTA):
        x, y = layar(kamera, ll)
        k = c.p(0.1 + i * 0.04, 0.3 + i * 0.04)
        se.garis_putus(d, [(jx, jy), (x, y)], k, (30, 80, 150), tebal=5, putus=12, celah=10, panah=False)
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(30, 80, 150, int(255 * k)), outline=(255, 255, 255, int(255 * k)), width=3)
    d.ellipse((jx - 12, jy - 12, jx + 12, jy + 12), fill=(200, 40, 30, 255), outline=(255, 255, 255, 255), width=3)
    se.kartu(img, 540, 1150, "Perjanjian ASEAN", "soal polusi asap lintas batas · 2002", (30, 80, 150),
             alpha=c.p(0.35, 0.45), tiang=False, skala=back_out((c.t / c.d - 0.35) / 0.1))
    se.teks(d, (540, 1300), "Tapi…", 70, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0), alpha=c.p(0.82, 0.9))
    hdr(img, "Setelah 1997")
    return img


def a_2015(c):
    kamera = Kamera(*cam(-1.0, 108.5, 0.62))
    img, d = peta(kamera)
    label_id(d, kamera, 0.8)
    titik_api(d, kamera, c.t, munculkan=c.p(0.0, 0.3))
    kabut(img, kamera, c.t, kuat=c.p(0.1, 0.4) * 0.8, jangkau=0.7)
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out((c.t / c.d) / 0.12)
    se.teks(d, (540, 640), "2015", int(150 * s) + 1, (255, 200, 120), nama_font="caption", stroke=9, stroke_warna=(40, 20, 10))
    se.kartu(img, 540, 830, "2,6 juta hektar terbakar", "", MERAH, alpha=c.p(0.3, 0.38), tiang=False)
    se.kartu(img, 540, 990, "Kerugian > Rp 200 triliun", "taksiran Bank Dunia", (60, 60, 70), alpha=c.p(0.6, 0.68),
             tiang=False, skala=back_out((c.t / c.d - 0.6) / 0.1))
    hdr(img, "Terulang lagi")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(-1.0, 108.5, 0.62))
    img, d = peta(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1000), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Bukan cuma soal pohon", 50, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 650), "ini soal udara yang kita hirup bareng", 36, (90, 70, 50), alpha=a)
        api(d, 540, 820, c.t, 3.0, a)
        d.ellipse((440, 700, 640, 900), outline=(200, 30, 30, int(255 * a)), width=16)
        d.line((470, 870, 610, 730), fill=(200, 30, 30, int(255 * a)), width=16)
        se.teks(d, (540, 950), "Jangan bakar lahan!", 48, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Tahun sembilan belas sembilan puluh tujuh. Siang hari, tapi matahari cuma kelihatan kayak bulan pucat. "
                   "Langit kuning, napas sesak. Dan asapnya, dari Indonesia.", a_hook, transisi=False),
    Adegan("penyebab", "Waktu itu, El Nino bikin kemarau panjang. Hutan dan lahan gambut di Kalimantan dan Sumatra "
                       "kering kerontang. Dan banyak lahan dibuka dengan cara paling murah. Dibakar.", a_penyebab),
    Adegan("gambut", "Masalahnya, gambut itu kayak spons berisi karbon. Sekali terbakar, apinya bisa menjalar di bawah "
                     "tanah berbulan-bulan, dan susah banget dipadamkan.", a_gambut),
    Adegan("luas", "Totalnya, sekitar sepuluh juta hektar terbakar. Kira-kira seluas Korea Selatan.", a_luas),
    Adegan("kabut", "Kabut asapnya nyebrang negara. Malaysia, Singapura, Brunei, sampai Thailand selatan. "
                    "Sarawak bahkan menetapkan status darurat.", a_kabut, transisi=False),
    Adegan("korban", "Jutaan orang kena gangguan pernapasan. Sekolah dan bandara ditutup. Kabut asap juga ikut jadi "
                     "faktor jatuhnya pesawat Garuda di dekat Medan. Dua ratus tiga puluh empat orang meninggal.",
           a_korban),
    Adegan("karbon", "Dan yang jarang orang tahu, karbon yang lepas dari gambut tahun itu, setara tiga belas sampai "
                     "empat puluh persen emisi bahan bakar fosil seluruh dunia dalam setahun.", a_karbon),
    Adegan("asean", "Setelah itu, negara-negara ASEAN bikin perjanjian khusus soal polusi asap lintas batas. Tapi,",
           a_asean),
    Adegan("2015", "tahun dua ribu lima belas, kejadian serupa terulang. Dua koma enam juta hektar terbakar, dan "
                   "kerugiannya ditaksir Bank Dunia lebih dari dua ratus triliun rupiah.", a_2015, transisi=False),
    Adegan("penutup", "Jadi, kebakaran hutan bukan cuma soal pohon. Ini soal udara yang kita hirup bareng-bareng. "
                      "Jangan bakar lahan, ya. Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
