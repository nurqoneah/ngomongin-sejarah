"""Shorts ±90 detik: Asal-Usul Shell, dari Sumur Minyak di Langkat (1885).

Peta Sumatra Utara + Selat Malaka, penampang sumur bor, ikon kerang ilustratif (bukan logo resmi).
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import EMAS, MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "asal-usul-shell-langkat-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "ASAL-USUL SHELL"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
MINYAK = (22, 18, 16)
ORANYE = (240, 120, 30)
BIRU = (30, 80, 150)
KUNING_KERANG = (250, 200, 40)
MERAH_KERANG = (215, 40, 30)

print("  menyiapkan peta Sumatra Utara...")
PETA = Peta(93, 106, -2, 9, 200, [], [(3.0, 98.5, 0.6), (4.4, 96.9, 0.8), (1.5, 99.5, 0.7), (0, 101, 0.9)],
            seed=85, darat=pd.SEMUA)

TELAGA_SAID = (3.98, 98.20)
BRANDAN = (4.04, 98.32)
MEDAN = (3.59, 98.67)
LAUT_EKSPOR = (4.6, 99.2)
LABEL = {"LANGKAT": (3.62, 98.05), "ACEH": (4.7, 96.8), "Selat Malaka": (4.3, 99.75), "MALAYSIA": (4.4, 101.5)}


# ------------------------------------------------------------------ helper

def cam(ll, zoom, sx=540, sy=960):
    """Kamera supaya titik ll tampil di layar (sx, sy)."""
    x, y = PETA.px(*ll)
    return (x - (sx - W / 2) / zoom, y - (sy - H / 2) / zoom, zoom)


def peta(kamera):
    img = se.render_peta(PETA, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(kamera, ll):
    return kamera.layar(*PETA.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def hdr(img, sub="1880 – 1907", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def muncul(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


def label_peta(d, kamera, alpha=1.0, skip=()):
    for nama, ll in LABEL.items():
        if nama in skip:
            continue
        x, y = layar(kamera, ll)
        warna = (200, 225, 245) if nama == "Selat Malaka" else TINTA
        if nama == "Selat Malaka":
            se.teks(d, (x, y), nama, 38, warna, nama_font="tangan", alpha=alpha * 0.9)
        else:
            label(d, (x, y), nama, 40, warna, alpha)


def titik(d, x, y, warna=MERAH, r=12, alpha=1.0):
    if alpha > 0.01:
        a = int(255 * alpha)
        d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=(255, 255, 255, a), width=3)


def denyut(d, x, y, t, warna=MERAH, alpha=1.0, r0=20, r1=90):
    for k in range(2):
        f = (t * 0.8 + k * 0.5) % 1
        r = lerp(r0, r1, f)
        d.ellipse((x - r, y - r, x + r, y + r), outline=tuple(warna) + (int(220 * (1 - f) * alpha),), width=6)


def menara_bor(d, x, y, s=1.0, alpha=1.0, warna=(55, 40, 28)):
    """Menara bor kayu sederhana, alas di (x, y)."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    w = tuple(warna) + (a,)
    tinggi, lebar = 230 * s, 60 * s
    kiri, kanan, puncak = (x - lebar, y), (x + lebar, y), (x, y - tinggi)
    tb = max(3, int(7 * s))
    d.line((kiri, puncak), fill=w, width=tb)
    d.line((kanan, puncak), fill=w, width=tb)
    for k in range(1, 5):
        f = k / 5
        y1 = y - tinggi * f
        dx = lebar * (1 - f)
        y0 = y - tinggi * (f - 0.2)
        dx0 = lebar * (1 - f + 0.2)
        d.line((x - dx, y1, x + dx, y1), fill=w, width=max(2, int(4 * s)))
        d.line((x - dx0, y0, x + dx, y1), fill=w, width=max(2, int(3 * s)))
    d.rectangle((x - 16 * s, puncak[1] - 10 * s, x + 16 * s, puncak[1] + 6 * s), fill=w)
    d.rectangle((x - lebar - 20 * s, y - 6 * s, x + lebar + 20 * s, y + 6 * s), fill=w)


def semburan(img, x, y, t, kuat=1.0, tinggi=500, seed=0, lebar=1.0):
    """Minyak menyembur ke atas dari (x, y) lalu jatuh melebar."""
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    h = tinggi * kuat
    # tiang semburan
    for k in range(26):
        f = k / 25
        r = (10 + 26 * f) * lebar
        yy = y - h * f + math.sin(t * 9 + k) * 4
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=MINYAK + (int(235 * kuat),))
    # tetesan yang jatuh
    for i in range(110):
        v = rng.uniform(0.5, 1.2)
        f = (t * 0.55 * v + rng.random()) % 1
        arah = rng.uniform(-1, 1)
        px = x + arah * f * 260 * lebar
        py = y - h + h * f * f * 1.05 - math.sin(f * math.pi) * 40
        r = rng.uniform(5, 16) * lebar * (1 - 0.4 * f)
        d.ellipse((px - r, py - r, px + r, py + r), fill=MINYAK + (int(220 * kuat * (1 - 0.6 * f)),))
    # kilap
    for k in range(6):
        yy = y - h * (0.15 + k * 0.13)
        d.ellipse((x - 5 * lebar, yy - 12, x + 3 * lebar, yy + 12), fill=(120, 110, 100, int(120 * kuat)))
    img.alpha_composite(lap)


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


def kilang(d, x, y, s=1.0, alpha=1.0, hangus=0.0):
    """Ikon kilang: tangki-tangki + cerobong. hangus 0..1 = makin gelap."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    badan = se.lerp_rgb((225, 222, 210), (45, 38, 34), hangus) + (a,)
    garis = (50, 40, 30, a)
    for i, dx in enumerate((-95, 0, 95)):
        cx = x + dx * s
        r, hh = 40 * s, (60 + 15 * (i == 1)) * s
        d.rectangle((cx - r, y - hh, cx + r, y), fill=badan, outline=garis, width=max(2, int(3 * s)))
        d.ellipse((cx - r, y - hh - 14 * s, cx + r, y - hh + 14 * s), fill=badan, outline=garis, width=max(2, int(3 * s)))
    d.rectangle((x + 150 * s, y - 170 * s, x + 168 * s, y), fill=(120, 60, 50, a) if hangus < 0.5 else badan,
                outline=garis, width=2)


def kerang(d, x, y, R=120, alpha=1.0, kuning=KUNING_KERANG, merah=MERAH_KERANG):
    """Kerang kipas ilustratif, engsel di (x, y), membuka ke atas."""
    if alpha <= 0.01 or R < 6:
        return
    a = int(255 * alpha)
    n, a0, a1 = 9, math.radians(195), math.radians(345)
    tepi = []
    for k in range(91):
        f = k / 90
        sud = lerp(a0, a1, f)
        r = R * (0.93 + 0.07 * abs(math.sin(f * n * math.pi)))
        tepi.append((x + r * math.cos(sud), y + r * math.sin(sud) * 1.05))
    d.polygon([(x, y)] + tepi, fill=tuple(kuning) + (a,), outline=tuple(merah) + (a,))
    d.line(tepi + [(x, y), tepi[0]], fill=tuple(merah) + (a,), width=max(3, int(R / 18)), joint="curve")
    for k in range(1, n):
        sud = lerp(a0, a1, k / n)
        d.line((x, y, x + R * 0.9 * math.cos(sud), y + R * 0.9 * math.sin(sud) * 1.05),
               fill=tuple(merah) + (a,), width=max(2, int(R / 24)))
    d.rectangle((x - R * 0.28, y - R * 0.04, x + R * 0.28, y + R * 0.16), fill=tuple(kuning) + (a,),
                outline=tuple(merah) + (a,), width=max(2, int(R / 24)))


def obor(d, x, y, t, s=1.0, alpha=1.0):
    """Obor bambu, ujung api di (x, y)."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    d.rectangle((x - 9 * s, y + 10 * s, x + 9 * s, y + 380 * s), fill=(150, 130, 60, a), outline=(80, 65, 30, a), width=3)
    for k in range(1, 4):
        yy = y + (10 + k * 92) * s
        d.line((x - 10 * s, yy, x + 10 * s, yy), fill=(90, 75, 35, a), width=4)
    api(d, x, y, t, 2.4 * s, alpha, 3)


_LATAR = {}


def latar_kertas(seed=11, warna=(222, 200, 155)):
    if seed not in _LATAR:
        _LATAR[seed] = se.latar_tekstur(W, H, seed, warna).convert("RGBA")
    return _LATAR[seed].copy()


def latar_gelap(warna=(30, 26, 30)):
    img = Image.new("RGBA", (W, H), tuple(warna) + (255,))
    se.vignette(img)
    return img


# ------------------------------------------------------------------ adegan

def a_hook(c):
    kamera = se.kamera_antara(cam(TELAGA_SAID, 1.55, 540, 1180), cam(TELAGA_SAID, 1.75, 540, 1180), c.p(0, 1))
    img, d = peta(kamera)
    se.tint(img, (20, 10, 5), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    label_peta(d, kamera, 0.85, skip=("LANGKAT",))
    x, y = layar(kamera, TELAGA_SAID)
    se.glow(img, x, y - 150, 330, (255, 150, 60), 0.55)
    d = ImageDraw.Draw(img, "RGBA")
    denyut(d, x, y, c.t, MERAH, 1.0, 40, 170)
    menara_bor(d, x, y, 0.8)
    semburan(img, x, y - 180, c.t, kuat=0.75 + 0.25 * c.p(0, 0.3), tinggi=300, seed=1, lebar=0.9)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, (x - 210, y + 60), "Langkat, Sumatra Utara", 40, TINTA)
    s = 0.85 + 0.15 * back_out(c.t / 0.3)
    se.teks(d, (540, 470), "SHELL LAHIR", int(130 * s), (255, 214, 10), nama_font="caption", stroke=11,
            stroke_warna=(30, 15, 5))
    se.teks(d, (540, 610), "DI SUMATRA?", int(130 * s), PUTIH, nama_font="caption", stroke=11, stroke_warna=(30, 15, 5))
    a1 = c.p(0.3, 0.38) * (1 - c.p(0.68, 0.74))
    se.kartu(img, 540, 1330, "SPBU Shell resmi ganti pemilik", "Detik, 31 Oktober 2026", MERAH, alpha=a1, tiang=False,
             skala=muncul(c, 0.3))
    a2 = c.p(0.76, 0.84)
    se.teks(d, (540, 1330), "kilang pertamanya… dibakar habis", 52, (255, 190, 110), nama_font="caption", stroke=7,
            stroke_warna=(30, 15, 5), alpha=a2)
    hdr(img, "Sumur minyak 1885", alpha=c.p(0.85, 0.95))
    return img


def a_obor(c):
    # malam di Langkat: kolam berminyak + obor bambu
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    atas, bawah = np.array((20, 28, 55), np.float32), np.array((70, 60, 70), np.float32)
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (atas * (1 - g) + bawah * g).repeat(W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(4)
    for i in range(12):  # siluet pohon
        x = rng.uniform(0, W)
        hh = rng.uniform(250, 420)
        d.rectangle((x - 7, 860 - hh * 0.4, x + 7, 860), fill=(15, 20, 18, 255))
        d.ellipse((x - 80, 860 - hh, x + 80, 860 - hh * 0.35), fill=(15, 25, 20, 255))
    d.rectangle((0, 860, W, H), fill=(55, 45, 30, 255))
    # kolam berminyak
    d.ellipse((140, 960, 760, 1200), fill=(25, 22, 22, 255), outline=(20, 15, 10, 255), width=6)
    for k, warna in enumerate([(160, 60, 160), (60, 140, 170), (190, 170, 60), (60, 160, 90)]):
        r = 0.65 - k * 0.12
        ox = math.sin(c.t * 0.8 + k) * 20
        d.ellipse((450 - 300 * r + ox, 1080 - 110 * r, 450 + 300 * r + ox, 1080 + 110 * r),
                  outline=warna + (110,), width=5)
    # obor + cahaya
    se.glow(img, 870, 760, 300, (255, 170, 70), 0.75)
    d = ImageDraw.Draw(img, "RGBA")
    obor(d, 870, 760, c.t, 1.0)
    se.kartu(img, 540, 470, "Aeilko Jans Zijlker", "manajer kebun tembakau · ± 1880", (90, 60, 35),
             alpha=c.p(0.1, 0.2), tiang=False, skala=muncul(c, 0.1))
    se.teks(d, (450, 1250), "minyak merembes dari tanah", 44, (255, 225, 170), nama_font="caption", stroke=6, stroke_warna=(20, 15, 10), alpha=c.p(0.4, 0.5) * (1 - c.p(0.62, 0.68)))
    se.kartu(img, 540, 1330, "Ternyata: kaya minyak tanah", "sampel diuji di Batavia", ORANYE,
             alpha=c.p(0.7, 0.78), tiang=False, skala=muncul(c, 0.7))
    hdr(img, "Langkat, ± 1880")
    return img


def a_konsesi(c):
    kamera = Kamera(*cam(TELAGA_SAID, 1.9, 560, 900))
    img, d = peta(kamera)
    label_peta(d, kamera)
    x, y = layar(kamera, TELAGA_SAID)
    mx, my = layar(kamera, MEDAN)
    titik(d, mx, my, (60, 60, 70), 10)
    label(d, (mx + 70, my + 40), "Medan", 36)
    se.kartu(img, 540, 520, "Izin konsesi", "dari penguasa Langkat", (30, 100, 60), alpha=c.p(0.05, 0.14),
             tiang=False, skala=muncul(c, 0.05))
    a = c.p(0.35, 0.45)
    bx, by = x - 120, y + 40
    menara_bor(d, bx, by, 0.7, a)
    if a > 0.5:
        se.kartu(img, bx, by - 175, "Sumur pertama", "", (90, 60, 35), alpha=c.p(0.45, 0.55), coret=c.p(0.62, 0.8))
    se.teks(d, (540, 1300), "GAGAL", 110, MERAH, nama_font="caption", stroke=8, stroke_warna=(255, 255, 255),
            alpha=c.p(0.72, 0.8))
    hdr(img, "1884")
    return img


def a_sumur(c):
    img = Image.new("RGBA", (W, H), (160, 195, 220, 255))
    d = ImageDraw.Draw(img, "RGBA")
    tanah, dasar = 820, 1300
    d.rectangle((0, tanah, W, tanah + 70), fill=(120, 95, 60, 255))
    lapis = [(150, 120, 80), (130, 100, 70), (165, 140, 95), (115, 90, 65)]
    yy = tanah + 70
    for i, w in enumerate(lapis):
        d.rectangle((0, yy, W, yy + 85), fill=w + (255,))
        yy += 85
    d.rectangle((0, 1210, W, H), fill=(30, 25, 22, 255))
    se.teks(d, (200, 1255), "MINYAK", 40, (230, 200, 140), nama_font="caption")
    x = 540
    k = c.p(0.12, 0.45)
    ujung = tanah + k * (1235 - tanah)
    d.line((x, tanah, x, ujung), fill=(60, 60, 70, 255), width=12)
    d.polygon([(x - 14, ujung), (x + 14, ujung), (x, ujung + 26)], fill=(90, 90, 100, 255))
    meter = round(121 * k)
    se.teks(d, (790, ujung), f"{meter} m", 62, PUTIH, nama_font="caption", stroke=6, stroke_warna=(30, 20, 10),
            alpha=c.p(0.12, 0.16) * (1 - c.p(0.9, 1.0)))
    menara_bor(d, x, tanah, 1.0)
    sembur = c.p(0.45, 0.55)
    semburan(img, x, tanah - 230, c.t, kuat=sembur, tinggi=330, seed=5)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 450), "15 JUNI 1885", 110, (255, 214, 10), nama_font="caption", stroke=10,
            stroke_warna=(30, 15, 5), alpha=c.p(0.0, 0.08) * (1 - c.p(0.44, 0.5)))
    se.kartu(img, 540, 1330, "Telaga Tunggal 1", "sumur minyak komersial pertama di Indonesia", MERAH,
             alpha=c.p(0.62, 0.7), tiang=False, skala=muncul(c, 0.62))
    hdr(img, "Telaga Said, Langkat")
    return img


def a_royal(c):
    kamera = Kamera(*cam(BRANDAN, 2.0, 560, 900))
    img, d = peta(kamera)
    label_peta(d, kamera)
    x, y = layar(kamera, TELAGA_SAID)
    bx, by = layar(kamera, BRANDAN)
    ex, ey = layar(kamera, LAUT_EKSPOR)
    menara_bor(d, x - 40, y + 30, 0.8)
    k = c.p(0.6, 0.75)
    se.garis_putus(d, [(x - 40, y + 30), (bx, by)], k, (25, 20, 18), tebal=7, putus=14, celah=8, panah=False)
    kilang(d, bx + 60, by + 20, 1.0, c.p(0.62, 0.7))
    k2 = c.p(0.78, 0.98)
    se.garis_putus(d, [(bx + 120, by - 20), (ex, ey)], k2, (30, 80, 150), tebal=6, putus=16, celah=12)
    if k2 > 0:
        (px, py), _ = se.titik_di_jalur([(bx + 120, by - 20), (ex, ey)], k2)
        d.ellipse((px - 22, py - 10, px + 22, py + 10), fill=(60, 60, 70, 255), outline=PUTIH, width=3)
    se.kartu(img, 540, 1330, "Kilang Pangkalan Brandan", "beroperasi 1892", (90, 60, 35),
             alpha=c.p(0.66, 0.74), tiang=False, skala=muncul(c, 0.66))
    # panel 1890 menutup peta di awal
    a = c.p(0.0, 0.05) * (1 - c.p(0.54, 0.6))
    if a > 0:
        se.tint(img, (10, 8, 5), 0.55 * a)
        se.panel(img, (110, 420, 970, 1320), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 540), "1890", 130, (150, 40, 30), nama_font="caption", alpha=a)
        se.teks(d, (540, 660), "Den Haag, Belanda", 44, (90, 70, 50), alpha=a)
        se.kartu(img, 540, 820, "Royal Dutch", "Koninklijke Nederlandsche Petroleum Mij.", (230, 110, 30),
                 alpha=a * c.p(0.1, 0.18), tiang=False, skala=muncul(c, 0.1))
        se.kartu(img, 540, 1060, "Zijlker wafat", "akhir 1890, karena sakit", (90, 90, 95),
                 alpha=a * c.p(0.3, 0.38), tiang=False)
    hdr(img, "1890 – 1892")
    return img


def a_shell(c):
    img = latar_kertas(11)
    d = ImageDraw.Draw(img, "RGBA")
    s = muncul(c, 0.0, 0.12)
    se.teks(d, (540, 470), "Shell-nya dari mana?", int(84 * max(s, 0.01)) + 1, MERAH, nama_font="caption", stroke=7,
            stroke_warna=(255, 255, 255))
    R = 230 * clamp(muncul(c, 0.17, 0.15), 0, 1.2)
    kerang(d, 540, 940, R, c.p(0.17, 0.23))
    se.kartu(img, 540, 1060, "London · toko barang hiasan kerang", "keluarga Marcus Samuel", (150, 40, 30),
             alpha=c.p(0.2, 0.28), tiang=False, skala=muncul(c, 0.2))
    se.teks(d, (540, 600), "kerang = SHELL", 70, TINTA, nama_font="caption", stroke=6, stroke_warna=(255, 240, 210),
            alpha=c.p(0.45, 0.52))
    se.kartu(img, 540, 1250, "1897: Shell Transport and Trading", "perusahaan minyak & kapal tanker, London", BIRU,
             alpha=c.p(0.68, 0.76), tiang=False, skala=muncul(c, 0.68))
    hdr(img, "Sementara itu, di London…")
    return img


def a_gabung(c):
    img = latar_gelap((28, 30, 40))
    se.panel(img, (80, 420, 1000, 1310), alpha=c.p(0, 0.06))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 510), "1907: BERGABUNG", 64, (150, 40, 30), nama_font="judul", alpha=c.p(0.02, 0.1))
    k = c.p(0.05, 0.3)
    se.kartu(img, lerp(250, 330, k), 650, "Royal Dutch", "Belanda", (230, 110, 30), alpha=c.p(0.04, 0.12), tiang=False)
    se.kartu(img, lerp(830, 750, k), 650, "Shell", "Inggris", BIRU, alpha=c.p(0.04, 0.12), tiang=False)
    x0, x1, yb = 150, 930, 790
    p = c.p(0.3, 0.55)
    bagi = x0 + (x1 - x0) * 0.6
    if p > 0.05:
        d.rounded_rectangle((x0, yb, lerp(x0, bagi, p), yb + 90), 14, fill=(230, 110, 30, 255))
    if p > 0.6:
        d.rounded_rectangle((bagi + 6, yb, lerp(bagi + 6, x1, (p - 0.6) / 0.4), yb + 90), 14, fill=BIRU + (255,))
    se.teks(d, ((x0 + bagi) / 2, yb + 45), "60%", 56, PUTIH, nama_font="caption", alpha=c.p(0.4, 0.48))
    se.teks(d, ((bagi + x1) / 2, yb + 45), "40%", 56, PUTIH, nama_font="caption", alpha=c.p(0.52, 0.58))
    a = c.p(0.62, 0.7)
    kerang(d, 540, 1150, 150 * clamp(muncul(c, 0.62, 0.12), 0, 1.2), a)
    se.teks(d, (540, 970), "ROYAL DUTCH SHELL", 76, TINTA, nama_font="caption", alpha=a)
    hdr(img, "1907")
    return img


def a_hangus(c):
    kamera = Kamera(*cam(BRANDAN, 2.1, 540, 1000))
    img, d = peta(kamera)
    se.tint(img, (5, 10, 35), 0.55 * (1 - c.p(0.45, 0.6) * 0.5))
    d = ImageDraw.Draw(img, "RGBA")
    bx, by = layar(kamera, BRANDAN)
    ledak = c.p(0.42, 0.55)
    if ledak > 0:
        se.tint(img, (200, 70, 10), 0.25 * ledak)
        se.glow(img, bx, by - 80, 420 * ledak + 1, (255, 140, 40), 0.9 * ledak)
        d = ImageDraw.Draw(img, "RGBA")
    kilang(d, bx, by, 1.0, 1.0, hangus=c.p(0.5, 0.9))
    if ledak > 0:
        lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        rng = random.Random(9)
        for i in range(40):  # asap tebal
            f = (c.t * 0.25 + rng.random()) % 1
            sx = bx + rng.uniform(-150, 230) + f * 120
            sy = by - 60 - f * 520
            r = 40 + f * 110
            dl.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(35, 30, 30, int(150 * (1 - f) * ledak)))
        img.alpha_composite(lap)
        d = ImageDraw.Draw(img, "RGBA")
        for i, (dx, dy, s) in enumerate([(-95, -90, 2.2), (0, -110, 2.6), (95, -90, 2.2), (160, -190, 1.6),
                                         (-200, -20, 1.4), (230, 10, 1.5)]):
            api(d, bx + dx, by + dy, c.t, s * ledak, 1.0, i)
    se.teks(d, (540, 470), "13 AGUSTUS 1947", 96, (255, 214, 10), nama_font="caption", stroke=9,
            stroke_warna=(30, 15, 5), alpha=c.p(0.0, 0.08))
    se.kartu(img, 540, 620, "Belanda mau merebut kilang", "Agresi Militer I", (90, 90, 95),
             alpha=c.p(0.15, 0.23) * (1 - c.p(0.45, 0.5)), tiang=False, skala=muncul(c, 0.15))
    se.kartu(img, 540, 620, "Jam 3 pagi: dibumihanguskan", "oleh pejuang Republik", MERAH,
             alpha=c.p(0.5, 0.58), tiang=False, skala=muncul(c, 0.5))
    se.teks(d, (540, 1320), "lebih baik hangus…", 64, PUTIH, nama_font="caption", stroke=7, stroke_warna=(30, 10, 5),
            alpha=c.p(0.8, 0.88))
    hdr(img, "Pangkalan Brandan")
    return img


def a_kini(c):
    kamera = Kamera(*cam(BRANDAN, 1.5, 540, 1000))
    img, d = peta(kamera)
    label_peta(d, kamera)
    bx, by = layar(kamera, BRANDAN)
    kilang(d, bx, by, 0.7, 1.0, hangus=1.0 - 0.6 * c.p(0.05, 0.3))
    se.kartu(img, 540, 560, "1957: diambil alih Permina", "cikal bakal Pertamina", (180, 30, 30),
             alpha=c.p(0.03, 0.11) * (1 - c.p(0.42, 0.48)), tiang=False, skala=muncul(c, 0.03))
    a = c.p(0.45, 0.53)
    se.teks(d, (540, 520), "2026", int(120 * max(muncul(c, 0.45), 0.01)) + 1, (255, 214, 10), nama_font="caption",
            stroke=10, stroke_warna=(30, 15, 5), alpha=a)
    se.kartu(img, 540, 690, "SPBU Shell pindah ke pemilik baru", "30 Oktober 2026 · merek tetap Shell", BIRU,
             alpha=c.p(0.5, 0.58), tiang=False)
    se.teks(d, (540, 1320), "lebih dari 140 tahun sejak 1885", 52, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(30, 15, 5), alpha=c.p(0.72, 0.8))
    hdr(img, "Setelah merdeka")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(TELAGA_SAID, 1.5, 540, 960))
    img, d = peta(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 450, 990, 1080), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 540), "Logo kerang di SPBU itu…", 48, TINTA, nama_font="judul", alpha=a)
        kerang(d, 380, 860, 120, a)
        se.teks(d, (540, 820), "→", 80, TINTA, nama_font="caption", alpha=a)
        obor(d, 700, 700, c.t, 0.55, a)
        se.teks(d, (540, 1000), "ceritanya mulai dari obor di Langkat", 38, (150, 40, 30), nama_font="caption", alpha=a)
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
    Adegan("hook", "Raksasa minyak dunia ini lahir di Sumatra. Kemarin, SPBU Shell resmi pindah pemilik. "
                   "Dan kilang pertamanya, dibakar habis. Sama siapa?", a_hook, transisi=False),
    Adegan("obor", "Sekitar tahun delapan belas delapan puluh, Aeilko Zijlker, manajer kebun tembakau, lihat "
                   "warga Langkat bikin obor dari minyak rembesan tanah. Ternyata, kaya minyak tanah.", a_obor),
    Adegan("konsesi", "Dia dapat izin dari penguasa Langkat, lalu ngebor. Sumur pertama, gagal.", a_konsesi),
    Adegan("sumur", "Lima belas Juni delapan belas delapan puluh lima, bor tembus seratus dua puluh satu meter, dan "
                    "minyaknya nyembur! Telaga Tunggal Satu, sumur minyak komersial pertama Indonesia.", a_sumur),
    Adegan("royal", "Dari sumur ini, lahir raksasa. Tahun delapan belas sembilan puluh, Zijlker mendirikan "
                    "Royal Dutch di Den Haag, tapi meninggal akhir tahun itu. Lalu, kilang "
                    "Pangkalan Brandan dibangun.", a_royal),
    Adegan("shell", "Tapi, Shell-nya dari mana? Di London, keluarga Marcus Samuel dulu jualan hiasan kulit kerang. "
                    "Kerang itu, shell. Anaknya lalu bikin perusahaan minyak, Shell.", a_shell),
    Adegan("gabung", "Sembilan belas nol tujuh, keduanya bergabung. Enam puluh persen Belanda, empat puluh "
                     "Inggris. Lahirlah Royal Dutch Shell.", a_gabung),
    Adegan("hangus", "Nah, kilang pertama tadi? Tiga belas Agustus sembilan belas empat puluh tujuh, Belanda mau "
                     "merebutnya. Jam tiga pagi, pejuang kita membakar habis seluruh kilang. Lebih baik "
                     "hangus, daripada dipakai penjajah.", a_hangus),
    Adegan("kini", "Sisanya diambil alih Permina, cikal bakal Pertamina. Dan sekarang, Shell melepas SPBU-nya di "
                   "negeri tempat kisahnya dimulai.", a_kini),
    Adegan("penutup", "Jadi, logo kerang itu, ceritanya mulai dari obor di Langkat. Follow Ngomongin Sejarah "
                      "buat cerita berikutnya!", a_penutup),
]
