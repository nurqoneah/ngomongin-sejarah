"""Shorts ±88 detik: Anak Krakatau, gunung yang lahir dari laut (1927) dan runtuh separuh (2018).

Dua jenis visual: (1) peta Selat Sunda dekat (garis pantai sama dengan 002), (2) penampang samping
gunung di atas laut (tinggi digambar sesuai skala meter).
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import shorts_engine as se
from shorts_engine import (EMAS, KUNING, MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp,
                           lerp)

NAMA_FILE = "anak-krakatau-lahir-1927-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "ANAK KRAKATAU"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)

# ------------------------------------------------------------------ peta Selat Sunda (dekat)

JAWA_BARAT = [(-5.93, 106.0), (-6.0, 106.15), (-5.95, 106.35), (-6.05, 106.6), (-6.1, 106.8), (-6.0, 107.3),
              (-8.0, 107.3), (-7.4, 106.9), (-7.0, 106.53), (-6.95, 106.0), (-6.85, 105.55), (-6.8, 105.25),
              (-6.72, 105.2), (-6.62, 105.38), (-6.63, 105.6), (-6.48, 105.65), (-6.53, 105.72), (-6.38, 105.83),
              (-6.3, 105.83), (-6.05, 105.88)]
SUMATRA_SEL = [(-4.5, 103.6), (-5.19, 103.93), (-5.6, 104.25), (-5.92, 104.58), (-5.75, 104.72), (-5.5, 104.62),
               (-5.55, 104.85), (-5.8, 105.05), (-5.95, 105.2), (-5.75, 105.22), (-5.47, 105.27), (-5.55, 105.42),
               (-5.73, 105.6), (-5.87, 105.75), (-5.7, 105.85), (-5.3, 105.85), (-4.5, 105.9)]
PULAU_KECIL = [
    [(-5.9, 105.45), (-5.93, 105.51), (-5.97, 105.48), (-5.94, 105.43)],                       # Sebesi
    [(-5.93, 105.83), (-5.96, 105.88), (-5.98, 105.84)],                                        # Sangiang
    [(-6.55, 105.15), (-6.6, 105.27), (-6.65, 105.22), (-6.62, 105.12)],                       # Panaitan
]

print("  menyiapkan peta Selat Sunda...")
SUNDA = Peta(103.6, 107.2, -7.9, -4.6, 900, [], [(-6.5, 106.3, 0.35), (-7.0, 106.9, 0.4), (-5.2, 104.6, 0.4),
                                                 (-5.4, 105.0, 0.3), (-4.9, 105.4, 0.4)],
             seed=8, darat=[JAWA_BARAT, SUMATRA_SEL] + PULAU_KECIL)

LABEL_SUNDA = {"JAWA": (-6.55, 106.35), "SUMATRA": (-5.05, 104.75), "Selat Sunda": (-6.25, 105.2)}
KOTA_TSUNAMI = {"Anyer": (-6.05, 105.88), "Tanjung Lesung": (-6.48, 105.65), "Kalianda": (-5.73, 105.6)}

# Krakatau sebelum 1883, sisa Rakata, dua pulau tepi kaldera
KRAK_LAMA = [(-6.05, 105.42), (-6.06, 105.45), (-6.1, 105.46), (-6.15, 105.455), (-6.165, 105.43), (-6.15, 105.41),
             (-6.1, 105.405)]
KRAK_SISA = [(-6.125, 105.445), (-6.15, 105.455), (-6.165, 105.43), (-6.15, 105.41), (-6.13, 105.415)]
VERLATEN = [(-6.07, 105.36), (-6.09, 105.385), (-6.11, 105.375), (-6.09, 105.355)]
LANG = [(-6.08, 105.47), (-6.1, 105.485), (-6.11, 105.475)]
ANAK = (-6.102, 105.423)
KM_PER_DERAJAT = 111.0

# ------------------------------------------------------------------ penampang samping

LAUT_Y = 1090        # garis permukaan laut (px)
DASAR_Y = 1300       # dasar kaldera (px)
SK = 1.6             # px per meter di atas laut
GX = 400             # posisi tengah gunung

print("  menyiapkan latar penampang...")
_LATAR = se.latar_tekstur(W, H, 21, warna=(226, 208, 166)).convert("RGBA")


# ------------------------------------------------------------------ helper

def cam(peta, lat, lon, zoom):
    x, y = peta.px(lat, lon)
    return (x, y, zoom)


def peta_dgn(kamera, goyang=0.0, seed=0):
    if goyang > 0:
        rng = random.Random(seed)
        kamera.x += rng.uniform(-1, 1) * goyang / kamera.zoom
        kamera.y += rng.uniform(-1, 1) * goyang / kamera.zoom
    img = se.render_peta(SUNDA, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(kamera, ll):
    return kamera.layar(*SUNDA.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def pulau(d, kamera, poli, warna=(150, 120, 90), alpha=1.0):
    p = se.halus([layar(kamera, ll) for ll in poli])
    d.polygon(p, fill=tuple(warna) + (int(255 * alpha),), outline=(40, 30, 20, int(255 * alpha)))


def tepi_kaldera(d, kamera, alpha=1.0):
    for poli in (VERLATEN, LANG, KRAK_SISA):
        pulau(d, kamera, poli, alpha=alpha)


def asap(img, x, y, t, kuat=1.0, tinggi=600, lebar=1.0, seed=1, warna=(90, 85, 80)):
    """Kolom asap/abu yang naik dari (x, y)."""
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    for i in range(46):
        fase = (rng.random() + t * rng.uniform(0.15, 0.3)) % 1.0
        yy = y - fase * tinggi
        xx = x + math.sin(fase * 6 + i) * 30 * lebar + rng.uniform(-40, 40) * lebar * fase
        r = (30 + fase * 140) * lebar * rng.uniform(0.7, 1.2)
        a = int(200 * kuat * (1 - fase * 0.7))
        g = rng.randint(-15, 15)
        c = tuple(clamp(v + g, 0, 255) for v in warna)
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=tuple(int(v) for v in c) + (a,))
    img.alpha_composite(lap)


def lontaran(img, x, y, t, kuat=1.0, tinggi=260, seed=3):
    """Pijar lava yang terlempar dari kawah."""
    if kuat <= 0.01:
        return
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed)
    for i in range(26):
        fase = (rng.random() + t * rng.uniform(0.5, 0.9)) % 1.0
        vx = rng.uniform(-1, 1) * 160
        xx = x + vx * fase
        yy = y - tinggi * (fase * 2 - fase * fase * 1.6) * rng.uniform(0.6, 1.1)
        r = rng.uniform(4, 9)
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=(255, int(120 + 100 * (1 - fase)), 40, int(255 * kuat * (1 - fase * 0.6))))


def cincin(d, x, y, r, warna, alpha, tebal=8):
    if alpha <= 0.01 or r <= 1:
        return
    d.ellipse((x - r, y - r, x + r, y + r), outline=tuple(warna) + (int(255 * alpha),), width=tebal)


def kilat(img, kuat):
    se.tint(img, (255, 245, 220), clamp(kuat))


def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def gunung_peta(img, x, y, r, t, kuat=1.0):
    """Pulau gunung dilihat dari atas peta: pulau gelap + kerucut + kawah membara."""
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((x - r * 1.35, y - r * 0.9, x + r * 1.35, y + r * 0.9), fill=(62, 52, 48, 255), outline=(25, 20, 18, 255),
              width=4)
    d.polygon([(x - r * 0.9, y + r * 0.2), (x, y - r * 1.25), (x + r * 0.9, y + r * 0.2)], fill=(92, 76, 66, 255),
              outline=(30, 24, 20, 255))
    for i in range(4):  # aliran lava
        ax = x + (i - 1.5) * r * 0.22
        d.line((x, y - r * 1.15, ax, y + r * 0.1), fill=(255, 110, 30, int(200 * kuat)), width=5)
    se.glow(img, x, y - r * 1.2, r * 1.1, (255, 120, 40), 2.2 * kuat)


def tinggi_px(m):
    return m * SK


def kerucut(img, tinggi_m, kiri_hilang=0.0, alpha=1.0, malam=0.0):
    """Gunung penampang samping. kiri_hilang: 0..1 bagian sisi barat daya (kiri) yang runtuh."""
    d = ImageDraw.Draw(img, "RGBA")
    py = LAUT_Y - tinggi_px(tinggi_m)
    total = DASAR_Y - py
    lb = total * 0.62
    puncak = 26
    kiri_atas = (GX - puncak, py + 6)
    kanan_atas = (GX + puncak, py + 6)
    if kiri_hilang > 0:
        # bidang longsor: dari puncak kiri turun miring ke bawah laut
        kiri_atas = (GX - puncak * (1 - kiri_hilang), py + 6 + 40 * kiri_hilang)
    poli = [(GX - lb, DASAR_Y), kiri_atas, (GX - 8, py + 18), (GX + 8, py + 18), kanan_atas, (GX + lb, DASAR_Y)]
    warna = se.lerp_rgb((112, 92, 78), (60, 50, 50), malam)
    d.polygon(poli, fill=warna + (int(255 * alpha),), outline=(40, 30, 22, int(255 * alpha)))
    # garis lereng
    for i in range(1, 5):
        f = i / 5
        d.line((lerp(GX - 10, GX - lb, f), lerp(py + 20, DASAR_Y, f), lerp(GX - 4, GX - lb * 0.7, f),
                lerp(py + 40, DASAR_Y, f)), fill=(60, 45, 35, int(90 * alpha)), width=3)
    return GX, py


def laut_penampang(img, t, malam=0.0, gelombang=0.0, gx=None):
    """Lapisan laut transparan + garis ombak. gelombang: tinggi gelombang tsunami (px) yang menyebar dari gx."""
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    titik = []
    for x in range(0, W + 20, 20):
        y = LAUT_Y + math.sin(x * 0.03 + t * 2.4) * 5
        if gelombang > 0 and gx is not None:
            for arah in (-1, 1):
                pusat = gx + arah * (120 + gelombang * 4)
                y -= gelombang * math.exp(-((x - pusat) / 70) ** 2)
        titik.append((x, y))
    biru = se.lerp_rgb((40, 70, 110), (14, 24, 48), malam)
    d.polygon(titik + [(W, H), (0, H)], fill=biru + (175,))
    d.line(titik, fill=(220, 235, 245, 230), width=5)
    d.rectangle((0, DASAR_Y, W, H), fill=(70, 55, 40, 255))
    img.alpha_composite(lap)


def latar_penampang(malam=0.0):
    img = _LATAR.copy()
    if malam > 0:
        se.tint(img, (8, 10, 30), 0.55 * malam)
    return img


def angka_meter(d, x, y, m, warna=PUTIH, uk=64, alpha=1.0):
    se.teks(d, (x, y), f"{int(round(m))} m", uk, warna, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=alpha)


def monas(d, x, alpha=1.0):
    """Siluet Monas sederhana, tinggi ± 132 m di skala yang sama."""
    a = int(255 * alpha)
    t = tinggi_px(132)
    top = LAUT_Y - t
    d.rectangle((x - 70, LAUT_Y - 18, x + 70, LAUT_Y), fill=(230, 225, 210, a), outline=(40, 30, 20, a), width=3)
    d.polygon([(x - 22, LAUT_Y - 18), (x - 9, top + 30), (x + 9, top + 30), (x + 22, LAUT_Y - 18)],
              fill=(245, 242, 232, a), outline=(40, 30, 20, a))
    d.ellipse((x - 18, top + 14, x + 18, top + 34), fill=(245, 242, 232, a), outline=(40, 30, 20, a), width=2)
    d.polygon([(x - 10, top + 16), (x, top - 6), (x + 10, top + 16)], fill=(240, 196, 70, a), outline=(120, 90, 20, a))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    kamera = Kamera(*cam(SUNDA, -6.072, 105.423, 2.6))
    k = c.t / c.d
    img, d = peta_dgn(kamera, 10 * (0.5 + 0.5 * math.sin(c.t * 9)), int(c.t * 30))
    tepi_kaldera(d, kamera)
    se.tint(img, (10, 4, 2), 0.5)
    d = ImageDraw.Draw(img, "RGBA")
    gx, gy = layar(kamera, ANAK)
    for i in range(3):
        f = (c.t * 0.7 + i / 3) % 1.0
        cincin(d, gx, gy, 60 + f * 520, (230, 60, 30), (1 - f) * 0.8, 8)
    gunung_peta(img, gx, gy, 100, c.t)
    asap(img, gx, gy - 125, c.t, kuat=0.85, tinggi=560, lebar=1.0, warna=(70, 64, 60))
    lontaran(img, gx, gy - 125, c.t, 1.0, 320)
    d = ImageDraw.Draw(img, "RGBA")
    s = 0.86 + 0.14 * back_out(c.t / 0.3)
    se.teks(d, (540, 520), "GUNUNG INI", int(112 * s), PUTIH, nama_font="caption", stroke=10, stroke_warna=(0, 0, 0))
    se.teks(d, (540, 660), "LAHIR 1927", int(150 * s), (255, 120, 40), nama_font="caption", stroke=11,
            stroke_warna=(0, 0, 0))
    se.kartu(img, 540, 1250, "Sabtu malam: erupsi 14 kali", "31 Oktober 2026 · status Siaga", MERAH,
             alpha=c.p(0.28, 0.36) * (1 - c.p(0.62, 0.68)), tiang=False, skala=back_out((k - 0.28) / 0.1))
    a = c.p(0.72, 0.8)
    if a > 0:
        se.teks(d, (540, 1250), "Kenapa dia ditakuti?", 72, KUNING, nama_font="caption", stroke=8,
                stroke_warna=(0, 0, 0), alpha=a)
    hdr(img, "Selat Sunda", alpha=c.p(0.85, 0.95))
    return img


CAM_S2 = (cam(SUNDA, -5.95, 105.5, 0.8), cam(SUNDA, -6.1, 105.42, 2.6))


def a_kaldera(c):
    kamera = se.kamera_antara(*CAM_S2, c.p(0.0, 0.55))
    img, d = peta_dgn(kamera)
    lbl = 1 - c.p(0.35, 0.5)
    for nama, ll in LABEL_SUNDA.items():
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 46 if nama != "Selat Sunda" else 36,
              TINTA if nama != "Selat Sunda" else (30, 50, 90), lbl)
    for poli in (VERLATEN, LANG):
        pulau(d, kamera, poli)
    hancur = c.p(0.4, 0.62)
    pulau(d, kamera, KRAK_LAMA, (130, 105, 80), 1 - hancur)
    pulau(d, kamera, KRAK_SISA, (130, 105, 80))
    gx, gy = layar(kamera, ANAK)
    if hancur > 0.2:
        kilat(img, 0.4 * (1 - c.p(0.45, 0.55)))
        d = ImageDraw.Draw(img, "RGBA")
    # kawah raksasa di bawah laut
    a = c.p(0.62, 0.72)
    if a > 0:
        r = 0.035 * SUNDA.skala * kamera.zoom
        se.garis_putus(d, [(gx + r * math.cos(u / 40 * 2 * math.pi), gy + r * 0.85 * math.sin(u / 40 * 2 * math.pi))
                           for u in range(41)], c.p(0.62, 0.85), (230, 235, 245), tebal=6, panah=False, alpha=a)
        label(d, (gx, gy + 30), "kawah di bawah laut", 40, (30, 50, 90), a)
    se.kartu(img, 540, 1240, "1883: Krakatau meledak", "2/3 pulau hilang ke laut", MERAH,
             alpha=c.p(0.35, 0.45), tiang=False, skala=back_out((c.t / c.d - 0.35) / 0.1))
    hdr(img, "1883")
    return img


def a_lahir(c):
    kamera = Kamera(*cam(SUNDA, -6.09, 105.423, 3.4))
    k = c.t / c.d
    img, d = peta_dgn(kamera, 6 * c.p(0.5, 0.6) * (1 - c.p(0.9, 1)), int(c.t * 30))
    tepi_kaldera(d, kamera)
    gx, gy = layar(kamera, ANAK)
    golak = c.p(0.25, 0.45)
    rng = random.Random(2)
    for i in range(18):  # gelembung
        f = (c.t * rng.uniform(0.6, 1.2) + rng.random()) % 1.0
        bx = gx + rng.uniform(-110, 110)
        by = gy + rng.uniform(-70, 70)
        cincin(d, bx, by, 6 + f * 26, (230, 240, 250), golak * (1 - f), 3)
    for i in range(3):
        f = (c.t * 0.8 + i / 3) % 1.0
        cincin(d, gx, gy, 30 + f * 240, (235, 245, 255), golak * (1 - f) * 0.8, 6)
    sembur = c.p(0.55, 0.65)
    if sembur > 0:
        # semburan air + abu hitam dari dasar laut
        asap(img, gx, gy - 10, c.t, kuat=sembur * 0.9, tinggi=560, lebar=0.75, seed=5, warna=(55, 52, 50))
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        rr = random.Random(9)
        for i in range(60):
            f = (rr.random() + c.t * rr.uniform(0.7, 1.1)) % 1.0
            vx = rr.uniform(-1, 1) * 120
            x = gx + vx * f
            y = gy - 420 * (f * 2 - f * f * 1.4) * rr.uniform(0.6, 1)
            r = rr.uniform(5, 11)
            dl.ellipse((x - r, y - r, x + r, y + r), fill=(225, 240, 250, int(220 * sembur * (1 - f * 0.7))))
        img.alpha_composite(lap)
        d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 520), "1927", 150, (255, 235, 190), nama_font="caption", stroke=10, stroke_warna=(0, 0, 0),
            alpha=c.p(0.05, 0.15))
    se.kartu(img, 540, 1250, "Letusan dari dasar laut!", "44 tahun setelah 1883", MERAH, alpha=c.p(0.6, 0.68),
             tiang=False, skala=back_out((k - 0.6) / 0.1))
    hdr(img, "1927")
    return img


# fase pulau: (mulai, puncak, hilang) dalam fraksi durasi
SIKLUS = [(0.0, 0.1, 0.22), (0.26, 0.34, 0.46)]


def a_timbul(c):
    kamera = Kamera(*cam(SUNDA, -6.095, 105.423, 3.4))
    k = c.t / c.d
    img, d = peta_dgn(kamera)
    tepi_kaldera(d, kamera)
    gx, gy = layar(kamera, ANAK)
    besar, status = 0.0, ""
    for m, p, h in SIKLUS:
        if m <= k < h:
            besar = clamp((k - m) / (p - m)) * (1 - clamp((k - p) / (h - p)))
            status = "muncul…" if k < p else "hilang digerus ombak"
    if k >= 0.52:
        besar = clamp((k - 0.52) / 0.18)
        status = "bertahan!"
    for i in range(3):  # ombak menggerus
        f = (c.t * 0.9 + i / 3) % 1.0
        cincin(d, gx, gy, 140 - f * 90, (235, 245, 255), 0.6 * f, 5)
    if besar > 0.02:
        gunung_peta(img, gx, gy, 18 + 52 * besar, c.t, 0.4 + 0.6 * besar)
        asap(img, gx, gy - 50 * besar, c.t, kuat=0.6 * besar, tinggi=360, lebar=0.55, seed=6)
    d = ImageDraw.Draw(img, "RGBA")
    if status and k < 0.7:
        se.teks(d, (540, 1250), status, 70, PUTIH, nama_font="caption", stroke=8, stroke_warna=(0, 0, 0))
    se.kartu(img, 540, 560, "Anak Krakatau", "pulau permanen · Agustus 1930", (150, 30, 20), alpha=c.p(0.72, 0.8),
             tiang=False, skala=back_out((k - 0.72) / 0.1))
    hdr(img, "1928 – 1930")
    return img


def a_tumbuh(c):
    img = latar_penampang()
    k = c.p(0.12, 0.92)
    tahun = int(lerp(1930, 2018, k))
    m = lerp(15, 338, k)
    _, py = kerucut(img, m)
    asap(img, GX, py, c.t, kuat=0.5, tinggi=260, lebar=0.5, seed=7)
    laut_penampang(img, c.t)
    d = ImageDraw.Draw(img, "RGBA")
    # mistar tinggi
    d.line((GX + 120, LAUT_Y, GX + 120, py), fill=(150, 30, 20, 255), width=5)
    d.line((GX + 105, py, GX + 135, py), fill=(150, 30, 20, 255), width=5)
    angka_meter(d, GX + 260, py + 10, m, (255, 220, 160))
    se.teks(d, (800, 450), str(tahun), 120, PUTIH, nama_font="caption", stroke=9, stroke_warna=(0, 0, 0))
    se.kartu(img, 540, 1200, "Tumbuh ± 4 meter per tahun", "", (60, 120, 170), alpha=c.p(0.45, 0.55), tiang=False,
             skala=back_out((c.t / c.d - 0.45) / 0.1))
    label(d, (140, LAUT_Y - 30), "permukaan laut", 30, (30, 50, 90))
    hdr(img, "1930 – 2018")
    return img


def a_monas(c):
    img = latar_penampang()
    _, py = kerucut(img, 338)
    asap(img, GX, py, c.t, kuat=0.5, tinggi=260, lebar=0.5, seed=7)
    a = c.p(0.35, 0.45)
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.polygon([(820, LAUT_Y), (840, LAUT_Y - 14), (1080, LAUT_Y - 14), (1080, LAUT_Y)], fill=(160, 140, 100, 255))
    monas(dl, 950)
    se.tempel(img, lap, a)
    laut_penampang(img, c.t)
    d = ImageDraw.Draw(img, "RGBA")
    angka_meter(d, GX, py - 70, 338, (255, 220, 160), 84)
    if a > 0:
        mt = LAUT_Y - tinggi_px(132)
        se.teks(d, (950, mt - 60), "Monas", 44, TINTA, alpha=a)
        se.teks(d, (950, mt - 20), "± 132 m", 34, (90, 70, 50), alpha=a)
        d.line((0, mt, W, mt), fill=(150, 30, 20, int(150 * a)), width=3)
    se.kartu(img, 540, 1215, "Lebih dari 2× tinggi Monas", "", (150, 30, 20), alpha=c.p(0.6, 0.68), tiang=False,
             skala=back_out((c.t / c.d - 0.6) / 0.1))
    hdr(img, "2018")
    return img


def a_malam(c):
    k = c.t / c.d
    malam = c.p(0.0, 0.3)
    img = latar_penampang(malam)
    _, py = kerucut(img, 338, malam=malam)
    se.glow(img, GX, py, 150, (255, 120, 40), 1.6 + math.sin(c.t * 8) * 0.4)
    asap(img, GX, py, c.t, kuat=0.8, tinggi=420, lebar=0.8, seed=8, warna=(60, 56, 54))
    lontaran(img, GX, py, c.t, 1.0, 240)
    laut_penampang(img, c.t, malam)
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 540, "22 Desember 2018", "Sabtu malam", (40, 40, 60), alpha=c.p(0.05, 0.15), tiang=False)
    a = c.p(0.6, 0.7)
    if a > 0:
        # seismograf datar: tidak ada gempa
        x0, y0, x1, y1 = 640, 1140, 1010, 1280
        se.panel(img, (x0, y0, x1, y1), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        n = int((x1 - x0 - 40) * clamp((k - 0.6) / 0.3))
        pts = [(x0 + 20 + i, (y0 + y1) / 2 + 22 + math.sin(i * 0.9) * 1.5) for i in range(0, max(2, n), 4)]
        if len(pts) > 1:
            d.line(pts, fill=(150, 30, 20, int(255 * a)), width=4)
        se.teks(d, ((x0 + x1) / 2, y0 + 38), "Gempa? Nggak ada", 34, TINTA, nama_font="caption", alpha=a)
    hdr(img, "22 Desember 2018")
    return img


def a_runtuh(c):
    k = c.t / c.d
    if k < 0.32:
        # penampang: sisi barat daya runtuh ke laut
        f = clamp(k / 0.26)
        img = latar_penampang(1.0)
        m = lerp(338, 110, f)
        _, py = kerucut(img, m, kiri_hilang=f, malam=1.0)
        # bongkahan longsor meluncur ke kiri bawah
        d = ImageDraw.Draw(img, "RGBA")
        bx = GX - 120 - f * 300
        by = LAUT_Y - 260 + f * 380
        d.polygon([(bx - 90, by), (bx + 40, by - 70), (bx + 110, by + 20), (bx - 20, by + 90)],
                  fill=(80, 66, 60, int(255 * (1 - f * 0.4))), outline=(30, 24, 20, 255))
        laut_penampang(img, c.t, 1.0, gelombang=90 * clamp(f * 1.5), gx=GX)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 520), "RUNTUH KE LAUT", 92, (255, 120, 40), nama_font="caption", stroke=9,
                stroke_warna=(0, 0, 0), alpha=c.p(0.02, 0.08))
        if k > 0.27:
            kilat(img, (k - 0.27) / 0.05 * 0.9)
        hdr(img, "22 Desember 2018")
        return img
    kamera = Kamera(*cam(SUNDA, -6.2, 105.62, 1.25))
    img, d = peta_dgn(kamera)
    se.tint(img, (8, 10, 30), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    tepi_kaldera(d, kamera)
    gx, gy = layar(kamera, ANAK)
    gunung_peta(img, gx, gy, 18, c.t, 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(3):
        f = clamp((k - 0.33 - i * 0.07) / 0.4)
        if f > 0:
            cincin(d, gx, gy, f * 900, (235, 245, 255), (1 - f) * 0.95, 14 - i * 3)
            cincin(d, gx, gy, f * 900 - 18, (80, 140, 200), (1 - f) * 0.7, 6)
    merah = c.p(0.45, 0.55)
    for nama, ll in KOTA_TSUNAMI.items():
        x, y = layar(kamera, ll)
        warna = se.lerp_rgb((40, 30, 20), (200, 30, 20), merah)
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=warna + (255,), outline=(255, 255, 255, 255), width=3)
        dx = -150 if nama == "Tanjung Lesung" else 0
        label(d, (x + dx, y - 34), nama, 32, warna)
    label(d, (layar(kamera, (-6.42, 105.88))), "BANTEN", 44, TINTA)
    label(d, (layar(kamera, (-5.75, 105.3))), "LAMPUNG", 44, TINTA)
    se.kartu(img, 540, 560, "Lebih dari 400 jiwa", "meninggal · pesisir Banten & Lampung", MERAH,
             alpha=c.p(0.5, 0.58), tiang=False, skala=back_out((k - 0.5) / 0.1))
    se.kartu(img, 540, 1100, "Tinggi: 338 m → 110 m", "hilang lebih dari separuh", (40, 40, 60),
             alpha=c.p(0.84, 0.9), tiang=False, skala=back_out((k - 0.84) / 0.08))
    hdr(img, "Tsunami Selat Sunda 2018")
    return img


def a_kini(c):
    k = c.t / c.d
    if k < 0.55:
        img = latar_penampang()
        m = lerp(110, 190, c.p(0.0, 0.45))
        _, py = kerucut(img, m)
        asap(img, GX, py, c.t, kuat=0.7, tinggi=360, lebar=0.7, seed=10, warna=(70, 66, 62))
        lontaran(img, GX, py, c.t, 0.8, 200)
        laut_penampang(img, c.t)
        d = ImageDraw.Draw(img, "RGBA")
        angka_meter(d, GX + 250, py, m, (255, 220, 160))
        se.teks(d, (GX + 250, py + 55), "tumbuh lagi", 34, TINTA, alpha=c.p(0.1, 0.2))
        hdr(img, "2018 – sekarang")
        lencana_siaga(img, c.p(0.3, 0.4))
        return img
    kamera = Kamera(*cam(SUNDA, -6.11, 105.42, 3.6))
    img, d = peta_dgn(kamera)
    tepi_kaldera(d, kamera)
    gx, gy = layar(kamera, ANAK)
    gunung_peta(img, gx, gy, 30, c.t, 0.8)
    asap(img, gx, gy - 40, c.t, kuat=0.5, tinggi=300, lebar=0.5, seed=11)
    d = ImageDraw.Draw(img, "RGBA")
    r = 5 / KM_PER_DERAJAT * SUNDA.skala * kamera.zoom
    titik = [(gx + r * math.cos(u / 60 * 2 * math.pi), gy + r * math.sin(u / 60 * 2 * math.pi)) for u in range(61)]
    se.garis_putus(d, titik, c.p(0.58, 0.8), MERAH, tebal=8, panah=False)
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lap).ellipse((gx - r, gy - r, gx + r, gy + r), fill=(200, 52, 44, int(60 * c.p(0.75, 0.85))))
    img.alpha_composite(lap)
    se.kartu(img, 540, 1260, "Radius 5 km: dilarang mendekat", "", MERAH, alpha=c.p(0.7, 0.78), tiang=False,
             skala=back_out((k - 0.7) / 0.08))
    hdr(img, "Sekarang")
    lencana_siaga(img, 1.0)
    return img


def lencana_siaga(img, a):
    if a <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rounded_rectangle((300, 410, 780, 500), 24, fill=(240, 140, 20, 245), outline=(60, 30, 10, 255), width=5)
    d.text((540, 455), "SIAGA · LEVEL III", font=se.font("caption", 48), fill=PUTIH, anchor="mm",
           stroke_width=4, stroke_fill=(60, 30, 10))
    se.tempel(img, lap, a)


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def kerucut_mini(d, x, y, h, a, potong=False):
    al = int(255 * a)
    if potong:
        d.polygon([(x - 80, y), (x - 20, y - h * 0.55), (x + 10, y - h * 0.6), (x + 80, y)], fill=(112, 92, 78, al),
                  outline=(40, 30, 22, al))
    else:
        d.polygon([(x - 80, y), (x, y - h), (x + 80, y)], fill=(112, 92, 78, al), outline=(40, 30, 22, al))
    d.line((x - 100, y, x + 100, y), fill=(40, 70, 110, al), width=6)


def a_penutup(c):
    kamera = Kamera(*cam(SUNDA, -6.0, 105.6, 1.0))
    img, d = peta_dgn(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 450, 990, 1060), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 540), "Gunung pun bisa…", 54, TINTA, nama_font="judul", alpha=a)
        for i, (judul, h, potong) in enumerate((("lahir", 50, False), ("tumbuh", 150, False), ("runtuh", 150, True))):
            x = 240 + i * 300
            ai = a * c.p(0.08 + i * 0.1, 0.14 + i * 0.1)
            kerucut_mini(d, x, 860, h, ai, potong)
            se.teks(d, (x, 930), judul, 48, (150, 30, 20), nama_font="caption", alpha=ai)
        se.teks(d, (540, 1005), "1927 · 2018 · sekarang", 34, (90, 70, 50), alpha=a)
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
    Adegan("hook", "Gunung ini umurnya belum seratus tahun. Sabtu malam kemarin, dia erupsi empat belas kali. "
                   "Tapi yang bikin dia ditakuti, bukan letusannya. Terus apa?", a_hook, transisi=False),
    Adegan("kaldera", "Tahun delapan belas delapan puluh tiga, Krakatau meledak. Dua per tiga pulaunya hilang ke laut. "
                      "Yang tersisa, kawah raksasa di bawah air.", a_kaldera),
    Adegan("lahir", "Empat puluh empat tahun kemudian, tahun sembilan belas dua puluh tujuh, laut di tengah kawah itu "
                    "mulai bergolak. Ada letusan dari dasar laut!", a_lahir),
    Adegan("timbul", "Pulau kecil muncul, lalu hilang digerus ombak. Muncul lagi, hilang lagi. Baru Agustus "
                     "sembilan belas tiga puluh, dia bertahan jadi pulau. Namanya, Anak Krakatau.", a_timbul),
    Adegan("tumbuh", "Nah, ini bagian paling gila. Gunung ini tumbuh, kayak anak kecil. Rata-rata sekitar empat meter "
                     "per tahun.", a_tumbuh),
    Adegan("monas", "Tahun dua ribu delapan belas, tingginya udah tiga ratus tiga puluh delapan meter. Lebih dari dua "
                    "kali tinggi Monas.", a_monas),
    Adegan("malam", "Dua puluh dua Desember dua ribu delapan belas, malam hari. Dia lagi erupsi, kayak biasa. "
                    "Nggak ada gempa.", a_malam),
    Adegan("runtuh", "Ternyata, sebagian tubuhnya runtuh ke laut. Longsoran raksasa itu bikin tsunami, menyapu pesisir "
                     "Banten dan Lampung. Lebih dari empat ratus orang meninggal. Tingginya, tinggal seratus sepuluh "
                     "meter.", a_runtuh),
    Adegan("kini", "Dan sekarang, dia tumbuh lagi. Statusnya Siaga, level tiga. Radius lima kilometer dari kawah, "
                   "dilarang didekati.", a_kini),
    Adegan("penutup", "Jadi, gunung pun bisa lahir, tumbuh, dan runtuh, di depan mata kita. Follow Ngomongin Sejarah "
                      "buat cerita berikutnya!", a_penutup),
]
