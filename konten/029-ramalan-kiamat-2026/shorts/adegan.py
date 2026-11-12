"""Shorts ±88 detik: Ramalan "kiamat" 13 November 2026 — rumus penduduk von Foerster di jurnal Science (1960).

Tren: viral "ilmuwan prediksi kiamat 13 November 2026" (detik, CNN Indonesia, Bisnis.com, November 2026).
Visual: bumi penuh titik manusia + penghitung meledak ke ∞, sampul jurnal 1960, grafik penduduk 1–1958 M,
kurva hiperbola menembak ke atas di 2026, batang prediksi vs kenyataan 1997, amplop surat protes,
grafik laju pertumbuhan (puncak 1963), penghitung 8,3 miliar + peta Indonesia, kalender ulang tahun.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "ramalan-kiamat-2026-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "RUMUS KIAMAT 1960"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU = (30, 80, 150)
ABU = (60, 60, 70)
HIJAU_TUA = (30, 110, 60)
COKLAT = (120, 80, 40)
KUNING = (255, 214, 10)
GELAP = (10, 10, 20)

print("  menyiapkan peta Indonesia...")
PETA = Peta(85, 150, -45, 35, 30, [], [(-7.2, 107.6, 0.35), (-7.0, 110.4, 0.4), (-0.5, 101.0, 0.5)],
            seed=29, darat=pd.SEMUA)

print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 29, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (20, 14, 8), 0.6)
LATAR_MALAM = Image.new("RGBA", (W, H), (0, 0, 0, 255))
_dm = ImageDraw.Draw(LATAR_MALAM)
for _y in range(H):
    _dm.line((0, _y, W, _y), fill=se.lerp_rgb((8, 10, 30), (40, 12, 18), _y / H) + (255,))
_rs = random.Random(5)
for _i in range(160):
    _x, _yy, _r = _rs.uniform(0, W), _rs.uniform(0, H), _rs.uniform(1, 3)
    _dm.ellipse((_x - _r, _yy - _r, _x + _r, _yy + _r), fill=(255, 255, 230, _rs.randint(80, 220)))


# ------------------------------------------------------------------ helper

def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def skala_muncul(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


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


def kalender(img, cx, cy, bulan, tgl, alpha=1.0, s=1.0, bawah=""):
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
    d.text((cx, cy + 30 * s), tgl, font=se.font("caption", int(150 * s)), fill=TINTA, anchor="mm")
    if bawah:
        d.text((cx, cy + h / 2 - 34 * s), bawah, font=se.font("ui", int(30 * s)), fill=(150, 30, 25), anchor="mm")
    se.tempel(img, lap, alpha)


# Benua sederhana di bola bumi: (dx, dy, rx, ry) relatif ke radius
BENUA = [(-0.35, -0.35, 0.28, 0.2), (-0.2, 0.15, 0.18, 0.32), (0.25, -0.3, 0.35, 0.22), (0.35, 0.1, 0.2, 0.2),
         (0.05, -0.05, 0.12, 0.18), (0.45, 0.45, 0.16, 0.1), (-0.5, 0.05, 0.08, 0.12)]


def bumi(img, cx, cy, r, putar=0.0):
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.ellipse((cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18), fill=(80, 140, 220, 70))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(22, 60, 120, 255), outline=(150, 200, 255, 255), width=5)
    for (dx, dy, rx, ry) in BENUA:
        x = cx + ((dx + putar + 1) % 2 - 1) * r
        y = cy + dy * r
        if (x - cx) ** 2 + (y - cy) ** 2 < (r * 0.92) ** 2:
            d.ellipse((x - rx * r, y - ry * r, x + rx * r, y + ry * r), fill=(214, 188, 138, 255),
                      outline=(150, 120, 80, 255), width=3)
    img.alpha_composite(lap)


def titik_manusia(d, cx, cy, r, n, seed=1, warna=(255, 230, 120)):
    rng = random.Random(seed)
    for i in range(n):
        a = rng.uniform(0, math.tau)
        rr = math.sqrt(rng.uniform(0, 1)) * r * 0.95
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        s = rng.uniform(3, 6)
        d.ellipse((x - s, y - s, x + s, y + s), fill=tuple(warna) + (230,))


def hiperbola(t):
    """Rumus von Foerster (disederhanakan): miliar jiwa pada tahun t."""
    return 179.0 / max(0.05, 2026.9 - t)


class Grafik:
    """Grafik di dalam panel. x = tahun, y = nilai."""

    def __init__(self, box, x0, x1, y0, y1):
        self.box, self.x0, self.x1, self.y0, self.y1 = box, x0, x1, y0, y1

    def p(self, x, y):
        bx0, by0, bx1, by1 = self.box
        return (bx0 + (x - self.x0) / (self.x1 - self.x0) * (bx1 - bx0),
                by1 - (y - self.y0) / (self.y1 - self.y0) * (by1 - by0))

    def sumbu(self, d, label_x, label_y=()):
        bx0, by0, bx1, by1 = self.box
        d.line((bx0, by0 - 20, bx0, by1, bx1 + 20, by1), fill=TINTA + (255,), width=5)
        f = se.font("ui", 30)
        for v, s in label_x:
            x, _ = self.p(v, self.y0)
            d.line((x, by1, x, by1 + 14), fill=TINTA + (255,), width=4)
            d.text((x, by1 + 38), s, font=f, fill=TINTA, anchor="mm")
        for v, s in label_y:
            _, y = self.p(self.x0, v)
            d.line((bx0 - 14, y, bx0, y), fill=TINTA + (255,), width=4)
            d.text((bx0 - 22, y), s, font=f, fill=TINTA, anchor="rm")


def kurva(d, g, fungsi, xa, xb, warna, tebal=8, n=200, ymaks=None):
    titik = []
    for i in range(n + 1):
        x = lerp(xa, xb, i / n)
        y = fungsi(x)
        if ymaks is not None and y > ymaks:
            titik.append(g.p(x, ymaks))
            break
        titik.append(g.p(x, y))
    if len(titik) > 1:
        d.line(titik, fill=tuple(warna) + (255,), width=tebal, joint="curve")
    return titik[-1] if titik else None


def amplop(d, x, y, s=1.0, sudut=0.0, alpha=1.0):
    a = int(255 * alpha)
    w, h = 150 * s, 100 * s
    c, sn = math.cos(sudut), math.sin(sudut)

    def R(px, py):
        return (x + px * c - py * sn, y + px * sn + py * c)

    kotak = [R(-w / 2, -h / 2), R(w / 2, -h / 2), R(w / 2, h / 2), R(-w / 2, h / 2)]
    d.polygon(kotak, fill=(250, 245, 230, a), outline=(90, 70, 50, a))
    d.line([R(-w / 2, -h / 2), R(0, h * 0.1), R(w / 2, -h / 2)], fill=(90, 70, 50, a), width=max(2, int(4 * s)))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_MALAM.copy()
    # bumi berdenyut, penuh titik manusia yang makin banyak
    denyut = 1 + 0.03 * math.sin(c.t * 9)
    r = int(270 * denyut)
    cx, cy = 540, 1000
    se.glow(img, cx, cy, 520, (255, 80, 40), 0.9 + 0.3 * c.p(0, 1))
    bumi(img, cx, cy, r, putar=c.t * 0.05)
    d = ImageDraw.Draw(img, "RGBA")
    n = int(250 + 1500 * c.p(0.0, 0.7))
    titik_manusia(d, cx, cy, r, n, seed=2)
    # penghitung penduduk meledak ke ∞
    k = c.p(0.0, 0.55)
    if k < 0.98:
        nilai = hiperbola(lerp(1958, 2026.85, k ** 0.35))
        isi = f"{nilai:,.1f} MILIAR".replace(",", "#").replace(".", ",").replace("#", ".")
        uk = 70
    else:
        isi, uk = "∞ ORANG", 96
    se.teks(d, (cx, 1340), isi, uk, (255, 90, 70), nama_font="caption", stroke=8, stroke_warna=GELAP)
    se.teks(d, (540, 395), "KIAMAT", 150, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 530), "HARI INI?!", 120, KUNING, nama_font="caption", stroke=10, stroke_warna=GELAP)
    stempel(img, "JUMAT, 13 NOV 2026", 540, 660, max(0.85, back_out((c.t / c.d - 0.05) / 0.08)) if c.t / c.d > 0.05
            else 0.85, uk=58, sudut=-5)
    return img


def a_jurnal(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out((c.t / c.d) / 0.15)
    # sampul jurnal / halaman artikel
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    x0, y0, x1, y1 = 200, 430, 880, 1150
    dl.rectangle((x0 + 12, y0 + 16, x1 + 12, y1 + 16), fill=(0, 0, 0, 90))
    dl.rectangle((x0, y0, x1, y1), fill=(250, 246, 236, 255), outline=(60, 50, 40, 255), width=4)
    dl.rectangle((x0, y0, x1, y0 + 120), fill=(140, 25, 25, 255))
    dl.text((540, y0 + 60), "SCIENCE", font=se.font("judul", 78), fill=PUTIH, anchor="mm")
    dl.text((540, y0 + 160), "Vol. 132 · November 1960", font=se.font("ui", 32), fill=(90, 70, 50), anchor="mm")
    for i, baris in enumerate(["DOOMSDAY:", "FRIDAY, 13 NOVEMBER,", "A.D. 2026"]):
        dl.text((540, y0 + 270 + i * 80), baris, font=se.font("judul", 58 if i != 1 else 50), fill=TINTA, anchor="mm")
    rng = random.Random(7)
    for i in range(7):
        yy = y0 + 540 + i * 26
        dl.line((x0 + 60, yy, x1 - 60 - rng.uniform(0, 160), yy), fill=(150, 140, 125, 255), width=8)
    se.tempel(img, lap, c.p(0.0, 0.08), (0, int(60 * (1 - s))))
    # sorotan stabilo di tanggal
    st = c.p(0.2, 0.32)
    if st > 0:
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle((240, 806, 240 + 600 * st, 816), fill=(200, 30, 30, 255))
    se.kartu(img, 540, 1240, "Heinz von Foerster", "fisikawan Austria · Univ. Illinois, AS", BIRU,
             alpha=c.p(0.5, 0.58), tiang=False, skala=skala_muncul(c, 0.5))
    hdr(img, "Jurnal sains, bukan ramalan dukun")
    return img


G_DATA = Grafik((180, 560, 960, 1150), 0, 2030, 0, 10)


def panel_grafik(img):
    se.panel(img, (70, 440, 1010, 1300))


def a_data(c):
    img = LATAR.copy()
    panel_grafik(img)
    d = ImageDraw.Draw(img, "RGBA")
    g = G_DATA
    g.sumbu(d, [(1, "1 M"), (1000, "1000"), (1958, "1958")], [(0, "0"), (5, "5 M"), (10, "10 M")])
    se.teks(d, (540, 495), "Penduduk dunia (miliar)", 40, TINTA, nama_font="judul")
    # titik-titik perkiraan penduduk 1 M – 1958
    tahun = [1, 200, 400, 600, 800, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1650, 1700, 1750, 1800,
             1850, 1900, 1920, 1930, 1940, 1950, 1955, 1958]
    n = int(len(tahun) * c.p(0.05, 0.7) + 0.999)
    rng = random.Random(3)
    for i, th in enumerate(tahun[:n]):
        x, y = g.p(th, hiperbola(th) * rng.uniform(0.92, 1.08))
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(200, 52, 44, 255), outline=(255, 255, 255, 255), width=3)
    se.kartu(img, 540, 760, "± 2.000 tahun data", "dari tahun 1 Masehi sampai 1958", HIJAU_TUA,
             alpha=c.p(0.3, 0.38), tiang=False, skala=skala_muncul(c, 0.3))
    a = c.p(0.72, 0.8)
    if a > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1235), "Makin banyak orang → makin cepat nambahnya", 36, (150, 30, 25),
                nama_font="caption", alpha=a)
    hdr(img, "Ngumpulin data")
    return img


def a_rumus(c):
    img = LATAR.copy()
    panel_grafik(img)
    d = ImageDraw.Draw(img, "RGBA")
    g = G_DATA
    g.sumbu(d, [(1, "1 M"), (1000, "1000"), (2026, "2026")], [(0, "0"), (5, "5 M"), (10, "10 M")])
    se.teks(d, (540, 495), "Penduduk dunia (miliar)", 40, TINTA, nama_font="judul")
    # garis asimtot 2026
    ax, _ = g.p(2026.9, 0)
    se.garis_putus(d, [(ax, 1150), (ax, 560)], c.p(0.35, 0.5), (200, 52, 44), tebal=5, panah=False)
    akhir = lerp(1958, 2026.6, c.p(0.1, 0.55) ** 0.5)
    ujung = kurva(d, g, hiperbola, 1, akhir, (30, 80, 150), tebal=9, ymaks=10.6)
    if ujung and c.p(0.45, 0.55) > 0:
        se.teks(d, (ujung[0] - 40, 600), "∞", 120, (200, 52, 44), nama_font="caption", stroke=6,
                stroke_warna=(247, 236, 208), alpha=c.p(0.45, 0.55))
    se.kartu(img, 470, 700, "Rumusnya nembak ke atas", "tak terhingga di akhir 2026", MERAH,
             alpha=c.p(0.55, 0.63), tiang=False, skala=skala_muncul(c, 0.55))
    a = c.p(0.12, 0.2)
    if a > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1235), "N ≈ 179 miliar ÷ (2026,9 − tahun)", 40, TINTA, nama_font="judul", alpha=a)
    stempel(img, "BUMI KEPENUHAN", 540, 920, skala_muncul(c, 0.78, 0.08), uk=64, sudut=-6)
    hdr(img, "Rumus 'kiamat'")
    return img


def batang(d, x, y_dasar, lebar, tinggi, warna, label_atas, label_bawah, alpha=1.0):
    a = int(255 * alpha)
    d.rectangle((x - lebar / 2, y_dasar - tinggi, x + lebar / 2, y_dasar), fill=tuple(warna) + (a,),
                outline=(30, 20, 10, a), width=4)
    d.text((x, y_dasar - tinggi - 45), label_atas, font=se.font("caption", 56), fill=TINTA + (a,), anchor="mm")
    d.text((x, y_dasar + 45), label_bawah, font=se.font("ui", 38), fill=TINTA + (a,), anchor="mm")


def a_hampir(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 430), "TAPI BAGIAN PALING GILA…", 58, (150, 30, 25), nama_font="caption", stroke=7,
            stroke_warna=(247, 236, 208), alpha=c.p(0.0, 0.05))
    se.teks(d, (540, 530), "RUMUSNYA HAMPIR BENAR", 70, TINTA, nama_font="caption", stroke=7,
            stroke_warna=(247, 236, 208), alpha=c.p(0.12, 0.18))
    se.panel(img, (130, 600, 950, 1270), alpha=c.p(0.1, 0.18))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 670), "Awal tahun 1997", 46, TINTA, nama_font="judul", alpha=c.p(0.15, 0.2))
    k1 = c.p(0.3, 0.45)
    k2 = c.p(0.5, 0.65)
    if k1 > 0:
        batang(d, 360, 1150, 220, 300 * k1, (30, 80, 150), "5,99 M" if k1 > 0.9 else "", "Rumus 1960")
    if k2 > 0:
        batang(d, 720, 1150, 220, 297 * k2, (200, 52, 44), "5,92 M" if k2 > 0.9 else "", "Kenyataan")
    se.kartu(img, 540, 1335, "Meleset cuma ± 1%", "", HIJAU_TUA, alpha=c.p(0.72, 0.8), tiang=False,
             skala=skala_muncul(c, 0.72))
    hdr(img, "Diuji 37 tahun kemudian")
    return img


def a_protes(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # tumpukan surat terbang ke jurnal
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rectangle((390, 760, 690, 1150), fill=(250, 246, 236, 255), outline=(60, 50, 40, 255), width=4)
    dl.rectangle((390, 760, 690, 820), fill=(140, 25, 25, 255))
    dl.text((540, 790), "SCIENCE", font=se.font("judul", 40), fill=PUTIH, anchor="mm")
    img.alpha_composite(lap)
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(11)
    n = int(14 * c.p(0.0, 0.6) + 0.999)
    for i in range(n):
        sx, sy = rng.choice([(-100, rng.uniform(500, 1300)), (1180, rng.uniform(500, 1300))])
        tx, ty = 540 + rng.uniform(-120, 120), 960 + rng.uniform(-120, 160)
        mulai = i / 14 * 0.6
        f = clamp((c.t / c.d - mulai) / 0.15)
        x, y = lerp(sx, tx, se.ease(f)), lerp(sy, ty, se.ease(f)) - math.sin(f * math.pi) * 120
        amplop(d, x, y, 0.9, rng.uniform(-0.5, 0.5) * (1 - f * 0.6))
    se.kartu(img, 540, 500, "Banyak ilmuwan protes", "rumusnya dibilang nggak masuk akal", MERAH,
             alpha=c.p(0.05, 0.13), tiang=False, skala=skala_muncul(c, 0.05))
    se.kartu(img, 540, 1290, "Penulisnya tetap ngotot", "malah balas suratnya", BIRU, alpha=c.p(0.6, 0.68),
             tiang=False, skala=skala_muncul(c, 0.6))
    hdr(img, "Surat-surat ke redaksi")
    return img


G_LAJU = Grafik((200, 620, 950, 1150), 1950, 2030, 0, 2.5)
LAJU = [(1950, 1.75), (1955, 1.9), (1960, 1.6), (1963, 2.2), (1966, 2.1), (1970, 2.05), (1975, 1.85), (1980, 1.75),
        (1985, 1.8), (1990, 1.65), (1995, 1.45), (2000, 1.32), (2005, 1.25), (2010, 1.2), (2015, 1.13),
        (2020, 0.95), (2026, 0.84)]


def a_belok(c):
    img = LATAR.copy()
    se.panel(img, (80, 440, 1010, 1300))
    d = ImageDraw.Draw(img, "RGBA")
    g = G_LAJU
    g.sumbu(d, [(1950, "1950"), (1963, "1963"), (2000, "2000"), (2026, "2026")], [(0, "0%"), (1, "1%"), (2, "2%")])
    se.teks(d, (545, 500), "Laju pertumbuhan penduduk dunia / tahun", 34, TINTA, nama_font="judul")
    k = c.p(0.05, 0.75)
    n = 1 + int((len(LAJU) - 1) * k)
    titik = [g.p(x, y) for x, y in LAJU[:n]]
    if len(titik) > 1:
        d.line(titik, fill=(200, 52, 44, 255), width=9, joint="curve")
    if n >= 4:
        x, y = g.p(1963, 2.2)
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=KUNING + (255,), outline=TINTA + (255,), width=4)
        se.teks(d, (x + 120, y - 20), "puncak 2,2%", 40, (150, 30, 25), nama_font="caption", stroke=5,
                stroke_warna=(247, 236, 208))
    if n == len(LAJU):
        x, y = g.p(2026, 0.84)
        d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=KUNING + (255,), outline=TINTA + (255,), width=4)
        se.teks(d, (x - 40, y - 60), "0,84%", 44, (150, 30, 25), nama_font="caption", stroke=5,
                stroke_warna=(247, 236, 208))
    se.kartu(img, 540, 1230, "Keluarga makin kecil", "termasuk lewat KB di Indonesia (BKKBN, 1970)", HIJAU_TUA,
             alpha=c.p(0.7, 0.78), tiang=False, skala=skala_muncul(c, 0.7))
    hdr(img, "Yang terjadi kemudian")
    return img


def cam(lat, lon, zoom):
    x, y = PETA.px(lat, lon)
    return (x, y, zoom)


def a_sekarang(c):
    kamera = se.kamera_antara(cam(-2.5, 118.0, 0.8), cam(-3.5, 117.0, 0.9), c.p(0.0, 1.0))
    img = se.render_peta(PETA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    # titik-titik penduduk di Indonesia
    rng = random.Random(4)
    pulau = [(-7.3, 110.0, 1.0, 3.5, 60), (-0.5, 101.5, 3.5, 2.5, 30), (-1.0, 114.0, 2.5, 2.5, 14),
             (-2.0, 120.5, 2.0, 1.2, 14), (-4.5, 138.0, 1.5, 3.0, 8), (-8.6, 116.5, 0.4, 2.5, 8)]
    jumlah = c.p(0.45, 0.75)
    for (la, lo, sla, slo, nn) in pulau:
        for i in range(int(nn * (1 + 2 * jumlah))):
            x, y = kamera.layar(*PETA.px(la + rng.gauss(0, sla * 0.4), lo + rng.gauss(0, slo * 0.4)))
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(200, 52, 44, 220), outline=(255, 255, 255, 200))
    se.panel(img, (110, 400, 970, 640), alpha=c.p(0.0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    miliar = lerp(3.0, 8.3, c.p(0.05, 0.35))
    se.teks(d, (540, 480), f"± {miliar:.1f} MILIAR".replace(".", ","), 84, (150, 30, 25), nama_font="caption",
            alpha=c.p(0.0, 0.08))
    se.teks(d, (540, 575), "penduduk dunia 2026 · bukan tak terhingga", 34, TINTA, nama_font="judul",
            alpha=c.p(0.0, 0.08))
    se.kartu(img, 330, 1250, "Sensus 1961", "± 97 juta jiwa", COKLAT, alpha=c.p(0.45, 0.53), tiang=False,
             skala=skala_muncul(c, 0.45))
    se.kartu(img, 760, 1250, "2025 (BPS)", "± 285 juta jiwa", MERAH, alpha=c.p(0.6, 0.68), tiang=False,
             skala=skala_muncul(c, 0.6))
    hdr(img, "Hari ini")
    return img


def a_jawaban(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 420), "INI JAWABANNYA", 60, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP,
            alpha=c.p(0.0, 0.05))
    se.teks(d, (540, 540), "2026,9", 130, KUNING, nama_font="caption", stroke=9, stroke_warna=GELAP,
            alpha=c.p(0.05, 0.12))
    se.teks(d, (540, 640), "= akhir tahun 2026, kata rumusnya", 42, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=GELAP, alpha=c.p(0.1, 0.18))
    kalender(img, 300, 960, "NOVEMBER", "13", c.p(0.35, 0.42), skala_muncul(c, 0.35) * 0.8, bawah="JUMAT")
    a = c.p(0.5, 0.58)
    if a > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        # kue ulang tahun
        kx, ky = 760, 1010
        dl.rounded_rectangle((kx - 150, ky - 40, kx + 150, ky + 110), 20, fill=(240, 200, 210, 255),
                             outline=(120, 60, 70, 255), width=5)
        dl.rounded_rectangle((kx - 110, ky - 130, kx + 110, ky - 40), 18, fill=(250, 230, 235, 255),
                             outline=(120, 60, 70, 255), width=5)
        for i in range(5):
            x = kx - 80 + i * 40
            dl.rectangle((x - 6, ky - 190, x + 6, ky - 130), fill=(80, 140, 220, 255))
            fl = 1 + 0.15 * math.sin(c.t * 14 + i)
            dl.ellipse((x - 9 * fl, ky - 225 * 1, x + 9 * fl, ky - 195), fill=(255, 190, 40, 255))
        se.tempel(img, lap, a)
    se.kartu(img, 540, 1270, "Ulang tahun von Foerster sendiri", "lahir 13 November 1911, Wina", BIRU,
             alpha=c.p(0.55, 0.63), tiang=False, skala=skala_muncul(c, 0.55))
    hdr(img, "Kenapa 13 November?")
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
        se.teks(d, (540, 540), "Rumus bisa pas di masa lalu…", 50, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 640), "tapi masa depan ditentukan", 46, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 710), "pilihan kita", 46, TINTA, nama_font="judul", alpha=a)
        b2 = c.p(0.25, 0.33) * a
        if b2 > 0:
            stempel(img, "BUKAN HARI KIAMAT", 540, 930, b2, uk=60, sudut=-5, warna=HIJAU_TUA)
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
    Adegan("hook", "Kiamat, katanya jatuh hari ini. Lagi rame ramalan kiamat tiga belas November? Ini ditulis ilmuwan, enam puluh enam tahun lalu. Tapi kenapa harus tanggal ini?",
           a_hook, transisi=False),
    Adegan("jurnal", "Tahun sembilan belas enam puluh, jurnal Science memuat artikel berjudul: Hari Kiamat, Jumat, tiga belas November, dua ribu dua puluh enam. Penulisnya, fisikawan Heinz von Foerster.",
           a_jurnal),
    Adegan("data", "Dia ngumpulin perkiraan penduduk dunia, dari tahun satu sampai sembilan belas lima puluh delapan. Polanya: makin banyak manusia, makin cepat nambahnya.",
           a_data),
    Adegan("rumus", "Kalau pola ini terus jalan, garisnya nembak ke atas. Akhir dua ribu dua puluh enam, jumlah manusia jadi tak terhingga. Bumi kepenuhan.",
           a_rumus),
    Adegan("hampir", "Tapi bagian paling gila-nya: rumus ini hampir benar. Tahun sembilan belas sembilan puluh tujuh, rumusnya nebak hampir enam miliar orang. Kenyataannya? Juga hampir enam miliar.",
           a_hampir),
    Adegan("protes", "Banyak ilmuwan protes, katanya nggak masuk akal. Tapi penulisnya tetap ngotot.",
           a_protes),
    Adegan("belok", "Terus, kenapa kita masih di sini? Tahun enam puluhan, pertumbuhan penduduk dunia mencapai puncak, lalu turun. Keluarga makin kecil, termasuk lewat KB di Indonesia.",
           a_belok),
    Adegan("sekarang", "Sekarang penduduk dunia sekitar delapan koma tiga miliar. Indonesia, dari sembilan puluh tujuh juta tahun enam puluh satu, jadi sekitar dua ratus delapan puluh lima juta.",
           a_sekarang),
    Adegan("jawaban", "Nah, ini jawabannya. Rumusnya cuma nunjuk akhir dua ribu dua puluh enam. Tanggal tiga belas November? Itu hari ulang tahun von Foerster sendiri.",
           a_jawaban),
    Adegan("penutup", "Rumus bisa pas buat masa lalu, tapi masa depan ditentukan pilihan kita. Santai, hari ini bukan kiamat. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
