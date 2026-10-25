"""Shorts ±90 detik: Sumpah Pemuda 1928 (Kongres Pemuda II).

Peta Nusantara + denah Batavia ilustrasi + adegan kertas rumusan, biola, dan peta bahasa.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import EMAS, MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "sumpah-pemuda-1928-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "SUMPAH PEMUDA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU = (30, 80, 150)
COKLAT = (110, 80, 50)

print("  menyiapkan peta Nusantara...")
PETA = Peta(92, 142, -45, 35, 60, [], [(-2, 114, 1.5), (0, 101, 1.2), (-4, 138, 1.5), (-2, 121, 1.0), (-7.5, 110, 0.8)],
            seed=28, darat=pd.SEMUA)

BATAVIA = (-6.15, 106.82)
PERKUMPULAN = [
    ("Jong Java", (-7.3, 110.3)),
    ("Jong Sumatranen Bond", (0.6, 101.6)),
    ("Jong Bataks Bond", (2.6, 98.9)),
    ("Jong Celebes", (-2.4, 120.3)),
    ("Jong Ambon", (-3.7, 128.2)),
    ("Jong Islamieten Bond", (-6.9, 107.6)),
    ("Pemuda Kaum Betawi", (-6.2, 106.8)),
]
# titik bahasa daerah (ilustratif), makin rapat di timur
_rng = random.Random(718)
TITIK_BAHASA = []
for _lat0, _lat1, _lon0, _lon1, _n in [(-5, 4, 96, 105, 18), (-8.3, -6.4, 106, 114, 12), (-3.5, 3, 110, 117, 14),
                                         (-5, 1, 119.5, 123, 14), (-9.5, -8, 115, 125, 18), (-8, 1, 125, 131, 26),
                                         (-8, -1, 131, 141, 60)]:
    for _ in range(_n):
        TITIK_BAHASA.append((_rng.uniform(_lat0, _lat1), _rng.uniform(_lon0, _lon1)))


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


def hdr(img, sub="27 – 28 Oktober 1928", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def muncul(c, a):
    """Skala pop-in kartu mulai fraksi a."""
    return back_out((c.t / c.d - a) / 0.1)


_KERTAS = None


def kertas_latar():
    """Latar kertas tua (dibuat sekali)."""
    global _KERTAS
    if _KERTAS is None:
        _KERTAS = se.latar_tekstur(W, H, 41, warna=(225, 205, 160)).convert("RGBA")
    return _KERTAS.copy()


def gelembung(d, x, y, w, h, isi, uk=40, alpha=1.0, warna=(250, 245, 230), tinta=TINTA, ekor=1):
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), 30, fill=warna + (a,),
                        outline=(40, 30, 20, a), width=5)
    ex = x + ekor * w * 0.25
    d.polygon([(ex - 25, y + h / 2 - 3), (ex + 25, y + h / 2 - 3), (ex + ekor * 50, y + h / 2 + 50)],
              fill=warna + (a,), outline=(40, 30, 20, a))
    d.line((ex - 22, y + h / 2 - 3, ex + 22, y + h / 2 - 3), fill=warna + (a,), width=7)
    se.teks(d, (x, y), isi, uk, tinta, nama_font="tangan", alpha=alpha)


def orang(d, x, y, s=1.0, warna=(60, 50, 45), alpha=1.0):
    """Siluet orang sederhana tanpa wajah (titik kepala + badan)."""
    a = int(255 * alpha)
    d.ellipse((x - 16 * s, y - 70 * s, x + 16 * s, y - 38 * s), fill=warna + (a,))
    d.rounded_rectangle((x - 26 * s, y - 34 * s, x + 26 * s, y + 30 * s), int(16 * s), fill=warna + (a,))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = kertas_latar()
    se.tint(img, (20, 14, 8), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out(c.t / 0.35)
    se.teks(d, (540, 520), "1928", int(200 * s) + 1, (255, 230, 170), nama_font="caption", stroke=10,
            stroke_warna=(40, 25, 10))
    # deretan pemuda (siluet)
    for i in range(7):
        orang(d, 150 + i * 130, 1250, 1.3, (50 + i * 6, 40, 35), c.p(0.05 + i * 0.02, 0.15 + i * 0.02))
    a1 = c.p(0.12, 0.2) * (1 - c.p(0.55, 0.62))
    gelembung(d, 330, 820, 460, 130, "Dames en heren…", 44, a1, ekor=1)
    gelembung(d, 760, 960, 420, 120, "Vergadering…", 42, a1 * c.p(0.25, 0.32), ekor=-1)
    a2 = c.p(0.62, 0.7)
    if a2 > 0:
        gelembung(d, 540, 880, 760, 170, "Bahasa Indonesia!", 70, a2, warna=(255, 240, 200), tinta=(170, 30, 20))
    se.teks(d, (540, 660), "rapat pemuda umumnya pakai bahasa Belanda", 38, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(30, 20, 10), alpha=c.p(0.15, 0.25) * (1 - c.p(0.55, 0.62)))
    hdr(img, alpha=c.p(0.75, 0.9))
    return img


def a_tren(c):
    img = kertas_latar()
    se.tint(img, (120, 20, 15), 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    # kalender sobek
    s = muncul(c, 0.02)
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    x0, y0, x1, y1 = 300, 470, 780, 960
    dl.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), 30, fill=(0, 0, 0, 110))
    dl.rounded_rectangle((x0, y0, x1, y1), 30, fill=(250, 245, 235, 255), outline=(60, 40, 30, 255), width=6)
    dl.rounded_rectangle((x0, y0, x1, y0 + 120), 30, fill=MERAH + (255,))
    dl.rectangle((x0, y0 + 80, x1, y0 + 120), fill=MERAH + (255,))
    dl.text((540, y0 + 62), "OKTOBER 2026", font=se.font("ui", 48), fill=PUTIH, anchor="mm")
    dl.text((540, y0 + 290), "28", font=se.font("caption", 230), fill=TINTA, anchor="mm")
    dl.text((540, y0 + 440), "Rabu", font=se.font("tangan", 48), fill=(120, 90, 60), anchor="mm")
    for i in range(5):
        dl.ellipse((x0 + 70 + i * 85, y0 - 18, x0 + 100 + i * 85, y0 + 12), fill=(80, 80, 90, 255))
    if s < 0.999:
        lap = lap.resize((max(1, int(W * s)), max(1, int(H * s))), Image.BICUBIC)
        lap2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lap2.alpha_composite(lap, (int(540 - 540 * s), int(715 - 715 * s)))
        lap = lap2
    se.tempel(img, lap, c.p(0.0, 0.06))
    se.kartu(img, 540, 1090, "Hari Sumpah Pemuda ke-98", "", MERAH, alpha=c.p(0.25, 0.33), tiang=False,
             skala=muncul(c, 0.25))
    se.kartu(img, 540, 1230, "Logonya lagi rame dicari", "", (60, 60, 70), alpha=c.p(0.45, 0.53), tiang=False,
             skala=muncul(c, 0.45))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 1340), "awal ceritanya gimana?", 50, PUTIH, nama_font="caption", stroke=6,
            stroke_warna=(30, 20, 10), alpha=c.p(0.75, 0.83))
    hdr(img, "Lagi rame minggu ini")
    return img


URUT_JONG = ["Jong Java", "Jong Sumatranen Bond", "Jong Bataks Bond", "Jong Celebes", "Jong Ambon",
             "Jong Islamieten Bond"]
POS_JONG = {"Jong Bataks Bond": (260, 560), "Jong Sumatranen Bond": (330, 690), "Jong Celebes": (800, 560),
            "Jong Ambon": (820, 690), "Jong Java": (780, 1250), "Jong Islamieten Bond": (300, 1250)}
WARNA_JONG = [BIRU, MERAH, COKLAT, (46, 140, 90), (150, 60, 140), (20, 110, 60)]


def a_terpecah(c):
    kamera = Kamera(*cam(-2.5, 113.5, 0.5))
    img, d = peta(kamera)
    se.tint(img, (40, 25, 10), 0.15)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, (540, 450), "Hindia Belanda", 46, (120, 20, 15), c.p(0.0, 0.1), "caption")
    lokasi = dict(PERKUMPULAN)
    for i, nama in enumerate(URUT_JONG):
        a = c.p(0.25 + i * 0.08, 0.32 + i * 0.08)
        if a <= 0:
            continue
        x, y = layar(kamera, lokasi[nama])
        kx, ky = POS_JONG[nama]
        se.garis_putus(d, [(kx, ky), (x, y)], a, WARNA_JONG[i], tebal=4, putus=10, celah=8, panah=False)
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=WARNA_JONG[i] + (int(255 * a),), outline=(255, 255, 255, 255),
                  width=3)
        se.kartu(img, kx, ky, nama, "", WARNA_JONG[i], alpha=a, tiang=False, skala=muncul(c, 0.25 + i * 0.08) * 0.9)
    hdr(img, "Pemuda masih terpecah")
    return img


def a_kongres(c):
    kamera = se.kamera_antara(cam(-2.5, 117.5, 0.4), cam(-3.0, 110.0, 0.62), c.p(0.0, 0.3))
    img, d = peta(kamera)
    bx, by = layar(kamera, BATAVIA)
    for i, (nama, ll) in enumerate(PERKUMPULAN):
        if nama.startswith("Pemuda Kaum"):
            continue
        x, y = layar(kamera, ll)
        k = c.p(0.05 + i * 0.03, 0.4 + i * 0.03)
        se.garis_putus(d, [(x, y), ((x + bx) / 2, min(y, by) - 60), (bx, by)], k, MERAH, tebal=5, putus=14, celah=10)
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=MERAH + (255,), outline=(255, 255, 255, 255), width=3)
        # titik-titik pemuda berjalan
        for j in range(4):
            f = clamp(k - j * 0.06)
            if 0 < f < 1:
                (px, py), _ = se.titik_di_jalur([(x, y), ((x + bx) / 2, min(y, by) - 60), (bx, by)], f)
                d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=(255, 235, 180, 255), outline=TINTA + (255,), width=2)
    r = 18 + 4 * math.sin(c.t * 6)
    d.ellipse((bx - r, by - r, bx + r, by + r), fill=EMAS + (255,), outline=TINTA + (255,), width=4)
    label(d, (bx - 150, by - 40), "Batavia", 44, TINTA, c.p(0.1, 0.2))
    se.kartu(img, 540, 560, "Kongres Pemuda II", "Batavia, 27–28 Oktober 1928", MERAH, alpha=c.p(0.2, 0.3),
             tiang=False, skala=muncul(c, 0.2))
    se.kartu(img, 300, 1290, "Soegondo Djojopoespito", "ketua kongres", BIRU, alpha=c.p(0.55, 0.62), tiang=False,
             skala=muncul(c, 0.55))
    se.kartu(img, 800, 1290, "Muhammad Yamin", "sekretaris", (46, 140, 90), alpha=c.p(0.72, 0.8), tiang=False,
             skala=muncul(c, 0.72))
    hdr(img)
    return img


# denah Batavia ilustrasi (posisi skematis, bukan skala sebenarnya)
GEDUNG = [
    ((695, 800), "1", "Gedung KJB", "Waterlooplein · 27 Okt malam"),
    ((330, 820), "2", "Oost-Java Bioscoop", "Koningsplein Noord · 28 Okt pagi"),
    ((680, 1050), "3", "Kramat 106", "28 Okt malam"),
]


def a_tiga_gedung(c):
    img = kertas_latar()
    d = ImageDraw.Draw(img, "RGBA")
    # jalan & lapangan skematis
    jalan = (170, 145, 105, 255)
    d.line((60, 760, 1020, 760), fill=jalan, width=26)
    d.line((560, 420, 560, 1350), fill=jalan, width=26)
    d.line((560, 900, 900, 1350), fill=jalan, width=26)
    d.line((100, 1000, 560, 1000), fill=jalan, width=20)
    d.rectangle((200, 520, 460, 720), fill=(150, 175, 110, 255), outline=(80, 90, 50, 255), width=4)
    d.rectangle((600, 540, 790, 660), fill=(150, 175, 110, 255), outline=(80, 90, 50, 255), width=4)
    d.line((60, 470, 1020, 430), fill=(70, 110, 150, 255), width=14)  # sungai/kanal
    se.teks(d, (330, 620), "Koningsplein", 32, (60, 70, 40), nama_font="tangan")
    se.teks(d, (695, 585), "Waterloo-", 28, (60, 70, 40), nama_font="tangan")
    se.teks(d, (695, 620), "plein", 28, (60, 70, 40), nama_font="tangan")
    se.teks(d, (820, 1110), "Kramat", 34, COKLAT, nama_font="tangan")
    # rute antar-gedung
    titik = [g[0] for g in GEDUNG]
    se.garis_putus(d, titik, c.p(0.15, 0.6), MERAH, tebal=7, putus=20, celah=12)
    for i, ((x, y), no, nama, sub) in enumerate(GEDUNG):
        a = c.p(0.08 + i * 0.2, 0.16 + i * 0.2)
        if a <= 0:
            continue
        aa = int(255 * a)
        d.polygon([(x - 36, y), (x, y - 34), (x + 36, y)], fill=(150, 50, 40, aa), outline=TINTA + (aa,))
        d.rectangle((x - 30, y, x + 30, y + 40), fill=(240, 225, 190, aa), outline=TINTA + (aa,), width=3)
        d.ellipse((x - 22, y - 92, x + 22, y - 48), fill=MERAH + (aa,), outline=PUTIH + (aa,), width=3)
        se.teks(d, (x, y - 70), no, 32, PUTIH, nama_font="caption", alpha=a)
    se.kartu(img, 540, 1200, "Kramat Raya 106", "rumah milik Sie Kong Liong", MERAH, alpha=c.p(0.62, 0.7),
             tiang=False, skala=muncul(c, 0.62))
    se.kartu(img, 540, 1320, "Sekarang: Museum Sumpah Pemuda", "", (46, 140, 90), alpha=c.p(0.8, 0.87),
             tiang=False, skala=muncul(c, 0.8) * 0.9)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 400), "3 rapat · 3 gedung", 54, TINTA, nama_font="caption", stroke=5, stroke_warna=KREM_LABEL,
            alpha=c.p(0.02, 0.1))
    hdr(img, "Batavia, 1928")
    return img


def a_kertas(c):
    img = kertas_latar()
    se.tint(img, (30, 20, 10), 0.45)
    d = ImageDraw.Draw(img, "RGBA")
    # podium & pembicara (siluet)
    d.rectangle((140, 1000, 340, 1300), fill=(90, 60, 40, 255), outline=(40, 25, 15, 255), width=4)
    orang(d, 240, 950, 1.6, (40, 32, 28))
    se.teks(d, (240, 1340), "Sunario berpidato", 32, KREM_LABEL, nama_font="tangan", alpha=c.p(0.0, 0.1))
    # meja pimpinan
    d.rectangle((560, 1080, 1000, 1140), fill=(110, 75, 45, 255), outline=(40, 25, 15, 255), width=4)
    orang(d, 680, 1060, 1.3, (50, 40, 35))
    orang(d, 880, 1060, 1.3, (50, 40, 35))
    se.teks(d, (680, 1190), "Soegondo", 30, KREM_LABEL, nama_font="tangan")
    se.teks(d, (880, 1190), "Yamin", 30, KREM_LABEL, nama_font="tangan")
    # kertas bergeser dari Yamin ke Soegondo lalu membesar
    k = c.p(0.15, 0.4)
    besar = c.p(0.5, 0.65)
    x = lerp(860, 700, k)
    y = lerp(1060, 1060, k)
    x, y = lerp(x, 540, besar), lerp(y, 720, besar)
    w, h = lerp(70, 640, besar), lerp(50, 420, besar)
    a = c.p(0.08, 0.15)
    if a > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rectangle((x - w / 2 + 8, y - h / 2 + 10, x + w / 2 + 8, y + h / 2 + 10), fill=(0, 0, 0, 100))
        dl.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=(250, 244, 225, 255), outline=(90, 70, 50, 255),
                     width=3)
        tulis = c.p(0.65, 0.95)
        if besar > 0.95:
            for i in range(3):
                kk = clamp(tulis * 3 - i)
                if kk <= 0:
                    continue
                yy = y - h / 2 + 110 + i * 110
                dl.text((x - w / 2 + 50, yy), f"{i + 1}.", font=se.font("tangan", 48), fill=TINTA, anchor="lm")
                x0 = x - w / 2 + 110
                for j in range(int(kk * 9)):
                    dl.line((x0 + j * 50, yy + 4 + (j % 2) * 3, x0 + j * 50 + 38, yy + 2), fill=(40, 40, 90, 255),
                            width=6)
        se.tempel(img, lap, a)
    se.kartu(img, 720, 1300, "Rumusan 3 kalimat", "ditulis Yamin di secarik kertas", MERAH,
             alpha=c.p(0.6, 0.68), tiang=False)
    hdr(img, "Rapat terakhir, 28 Oktober")
    return img


ISI = [("Pertama", "Satu tanah air", "tanah Indonesia"),
       ("Kedua", "Satu bangsa", "bangsa Indonesia"),
       ("Ketiga", "Menjunjung bahasa persatuan", "bahasa Indonesia")]


def a_isi(c):
    img = kertas_latar()
    d = ImageDraw.Draw(img, "RGBA")
    for i, (no, judul, sub) in enumerate(ISI):
        a = c.p(0.02 + i * 0.18, 0.1 + i * 0.18)
        if a <= 0:
            continue
        y0 = 440 + i * 230
        sk = muncul(c, 0.02 + i * 0.18)
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        tebal = i == 2 and c.p(0.62, 0.7) > 0
        garis = (190, 40, 30, 255) if tebal else (90, 70, 50, 255)
        dl.rounded_rectangle((100 + 8, y0 + 10, 980 + 8, y0 + 200 + 10), 24, fill=(0, 0, 0, 90))
        dl.rounded_rectangle((100, y0, 980, y0 + 200), 24, fill=(250, 244, 225, 255), outline=garis,
                             width=10 if tebal else 5)
        dl.text((140, y0 + 40), no.upper(), font=se.font("ui", 30), fill=MERAH, anchor="lm")
        dl.text((540, y0 + 100), judul, font=se.font("judul", 50 if i < 2 else 44), fill=TINTA, anchor="mm")
        dl.text((540, y0 + 160), sub, font=se.font("tangan", 38), fill=(110, 80, 50), anchor="mm")
        if sk < 0.999:
            lap = lap.resize((max(1, int(W * sk)), max(1, int(H * sk))), Image.BICUBIC)
            l2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            l2.alpha_composite(lap, (int(540 - 540 * sk), int((y0 + 100) * (1 - sk))))
            lap = l2
        se.tempel(img, lap, a)
    a = c.p(0.7, 0.78)
    if a > 0:
        se.kartu(img, 540, 1200, "Bukan \"berbahasa satu\"", "bahasa daerah tetap boleh hidup", (46, 140, 90),
                 alpha=a, tiang=False, skala=muncul(c, 0.7))
    hdr(img, "Isi putusan kongres")
    return img


def biola(d, x, y, s=1.0, a=255):
    cokelat = (150, 75, 30, a)
    d.ellipse((x - 70 * s, y + 10 * s, x + 70 * s, y + 150 * s), fill=cokelat, outline=(60, 30, 10, a), width=4)
    d.ellipse((x - 55 * s, y - 110 * s, x + 55 * s, y + 20 * s), fill=cokelat, outline=(60, 30, 10, a), width=4)
    d.rectangle((x - 30 * s, y - 10 * s, x + 30 * s, y + 40 * s), fill=cokelat)
    d.rectangle((x - 9 * s, y - 330 * s, x + 9 * s, y - 60 * s), fill=(40, 25, 15, a))
    d.ellipse((x - 22 * s, y - 370 * s, x + 22 * s, y - 320 * s), fill=(60, 35, 20, a))
    for dx in (-5, 0, 5):
        d.line((x + dx * s, y - 330 * s, x + dx * s, y + 120 * s), fill=(230, 220, 190, a), width=2)
    d.arc((x - 50 * s, y - 10 * s, x - 10 * s, y + 50 * s), 100, 260, fill=(30, 15, 5, a), width=5)
    d.arc((x + 10 * s, y - 10 * s, x + 50 * s, y + 50 * s), -80, 80, fill=(30, 15, 5, a), width=5)


def a_biola(c):
    img = kertas_latar()
    se.tint(img, (15, 10, 25), 0.55)
    d = ImageDraw.Draw(img, "RGBA")
    se.glow(img, 540, 850, 380, (255, 210, 130), 0.6 * c.p(0.0, 0.15))
    d = ImageDraw.Draw(img, "RGBA")
    goyang = math.sin(c.t * 4) * 0.05
    biola(d, 540, 950 + math.sin(c.t * 3) * 6, 1.1)
    # busur
    bx = 540 + math.sin(c.t * 5) * 120
    d.line((bx - 260, 860 - 200 * goyang, bx + 260, 860 + 200 * goyang), fill=(70, 45, 25, 255), width=8)
    # not balok
    for i in range(6):
        f = (c.t * 0.35 + i / 6) % 1
        x = 540 + math.sin(i * 2.1 + f * 4) * 260
        y = 820 - f * 380
        a = int(255 * (1 - f) * c.p(0.05, 0.15))
        d.ellipse((x - 18, y - 12, x + 18, y + 12), fill=(255, 235, 180, a))
        d.line((x + 16, y, x + 16, y - 60), fill=(255, 235, 180, a), width=5)
    se.kartu(img, 540, 1240, "W.R. Supratman", "memainkan Indonesia Raya", BIRU, alpha=c.p(0.05, 0.13), tiang=False,
             skala=muncul(c, 0.05))
    a = c.p(0.55, 0.63)
    if a > 0:
        se.kartu(img, 540, 450, "Tanpa syair", "kongres diawasi polisi Belanda", MERAH, alpha=a, tiang=False,
                 skala=muncul(c, 0.55))
    hdr(img, "Malam penutupan, 28 Oktober 1928")
    return img


def a_nama(c):
    img = kertas_latar()
    d = ImageDraw.Draw(img, "RGBA")
    se.panel(img, (110, 470, 970, 820), alpha=c.p(0.0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 570), "1928", 70, TINTA, nama_font="judul", alpha=c.p(0.02, 0.1))
    se.teks(d, (540, 670), "\"Sumpah Pemuda\"", 66, (150, 40, 30), nama_font="caption", alpha=c.p(0.08, 0.15))
    se.teks(d, (540, 760), "belum dipakai sebagai nama", 38, (110, 80, 50), alpha=c.p(0.12, 0.2))
    if c.p(0.25, 0.4) > 0:
        k = c.p(0.25, 0.4)
        d.line((250, 670, lerp(250, 830, k), 670), fill=(190, 30, 20, 230), width=10)
    se.kartu(img, 540, 1020, "Istilahnya populer belakangan", "", MERAH, alpha=c.p(0.5, 0.58), tiang=False,
             skala=muncul(c, 0.5))
    hdr(img, "Fakta yang jarang tahu")
    return img


def a_bahasa(c):
    kamera = Kamera(*cam(-2.5, 117.5, 0.4))
    img, d = peta(kamera)
    n = int(len(TITIK_BAHASA) * c.p(0.0, 0.5))
    rng = random.Random(5)
    for i, ll in enumerate(TITIK_BAHASA[:n]):
        x, y = layar(kamera, ll)
        r = 9 + 2 * math.sin(c.t * 4 + i)
        warna = [(200, 52, 44), (30, 80, 150), (46, 140, 90), (150, 60, 140), (230, 150, 30)][rng.randrange(5)]
        d.ellipse((x - r, y - r, x + r, y + r), fill=warna + (230,), outline=(255, 255, 255, 200), width=2)
    se.teks(d, (540, 520), "> 700", int(120 * back_out(c.t / 0.4)) + 1, MERAH, nama_font="caption", stroke=9,
            stroke_warna=PUTIH, alpha=c.p(0.0, 0.08))
    se.teks(d, (540, 625), "bahasa daerah", 50, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0),
            alpha=c.p(0.0, 0.08))
    a = c.p(0.55, 0.65)
    if a > 0:
        gelembung(d, 540, 1170, 700, 150, "Satu bahasa persatuan", 54, a, warna=(255, 240, 200), tinta=(170, 30, 20))
    hdr(img, "Sekarang")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(-2.5, 117.5, 0.4))
    img, d = peta(kamera)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.5, 0.57))
    if a > 0:
        se.panel(img, (90, 520, 990, 960), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 620), "Persatuan itu bukan hadiah", 50, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 720), "tapi pilihan", 60, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 820), "yang diambil anak muda, 1928", 40, (90, 70, 50), alpha=a)
        for i in range(5):
            orang(d, 380 + i * 80, 940, 0.7, (60, 45, 35), a)
    b = c.p(0.55, 0.63)
    if b > 0:
        m = maskot()
        if m is not None:
            loncat = abs(math.sin(c.t * 5)) * 18
            se.tempel(img, m, b, (540 - m.width // 2, int(560 - loncat)))
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        sk = back_out((c.t / c.d - 0.55) / 0.1)
        w2 = 380 * sk
        dl.rounded_rectangle((540 - w2, 960, 540 + w2, 1090), 40, fill=(200, 52, 44, 245))
        dl.text((540, 1025), "NGOMONGIN SEJARAH", font=se.font("caption", int(56 * sk) + 1), fill=PUTIH, anchor="mm")
        dl.text((540, 1160), "Follow buat cerita berikutnya", font=se.font("ui", 42), fill=PUTIH, anchor="mm",
                stroke_width=4, stroke_fill=(0, 0, 0))
        se.tempel(img, lap, b)
    return img


ADEGAN = [
    Adegan("hook", "Sebelum tahun sembilan belas dua puluh delapan, rapat pemuda kita umumnya pakai bahasa Belanda. "
                   "Kok bisa lahir bahasa persatuan?", a_hook, transisi=False),
    Adegan("tren", "Rabu ini, kita peringati Hari Sumpah Pemuda ke sembilan puluh delapan. Logonya lagi rame dicari. "
                   "Tapi, awal ceritanya gimana?", a_tren),
    Adegan("terpecah", "Waktu itu, pemuda masih terpecah dalam perkumpulan daerah. Jong Java, Jong Sumatranen Bond, "
                       "Jong Celebes, Jong Ambon, dan banyak lagi.", a_terpecah),
    Adegan("kongres", "Dua puluh tujuh dan dua puluh delapan Oktober, mereka kumpul di Batavia, dalam Kongres Pemuda "
                      "Kedua. Ketuanya Soegondo, sekretarisnya Muhammad Yamin.",
           a_kongres, transisi=False),
    Adegan("gedung", "Rapatnya pindah-pindah, tiga kali di tiga gedung. Yang terakhir di Kramat Raya seratus enam, "
                     "yang sekarang jadi Museum Sumpah Pemuda.", a_tiga_gedung),
    Adegan("kertas", "Di rapat terakhir, waktu Sunario lagi pidato, Yamin nyodorin secarik kertas ke Soegondo. "
                     "Isinya, rumusan tiga kalimat.", a_kertas),
    Adegan("isi", "Satu tanah air, tanah Indonesia. Satu bangsa, bangsa Indonesia. Dan menjunjung bahasa persatuan, "
                  "bahasa Indonesia. Perhatiin, bukan berbahasa satu. Bahasa daerah tetap boleh hidup.", a_isi),
    Adegan("biola", "Malam itu juga, Wage Rudolf Supratman memainkan lagu Indonesia Raya pakai biola. Tanpa syair, "
                    "karena kongres diawasi polisi Belanda.", a_biola),
    Adegan("nama", "Uniknya, waktu itu namanya belum Sumpah Pemuda. Istilah itu baru populer belakangan.", a_nama),
    Adegan("bahasa", "Sekarang, ada lebih dari tujuh ratus bahasa daerah di Indonesia. Tapi kita tetap bisa ngobrol "
                     "pakai satu bahasa.", a_bahasa),
    Adegan("penutup", "Persatuan itu bukan hadiah. Tapi pilihan, yang diambil anak muda. Follow Ngomongin Sejarah buat "
                      "cerita berikutnya!", a_penutup),
]
