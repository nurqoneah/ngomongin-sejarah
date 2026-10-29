"""Shorts ±90 detik: Asal-Usul Kata Sehari-hari — bahasa kita ternyata 'gado-gado'.

Pemicu: video IShowSpeed makin lancar bahasa Indonesia viral (CNN Indonesia, 28 Okt 2026).
Peta Samudra Hindia–Nusantara (rute kapal pembawa kata) + panel ilustrasi (gelembung chat, bedah kalimat).
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp

NAMA_FILE = "asal-usul-kata-serapan-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "ASAL-USUL KATA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
SANSKERTA = (190, 110, 30)
ARAB = (30, 120, 70)
CINA = (180, 40, 40)
PORTUGIS = (40, 90, 160)
BELANDA = (220, 110, 20)
YUNANI = (60, 60, 150)
GELAP = (24, 22, 30)

print("  menyiapkan peta Samudra Hindia...")
PETA = Peta(30, 130, -40, 45, 40, [], [(30, 85, 4), (35, 100, 4), (27, 92, 2), (0, 101, 1.2), (-2, 114, 1.5)],
            seed=51, darat=pd.SEMUA)

MALAKA = (2.2, 102.25)
PALEMBANG = (-3.0, 104.7)
PASAI = (5.1, 97.3)
BATAVIA = (-6.15, 106.85)
QUANZHOU = (24.9, 118.6)
INDIA = (12.5, 80.3)

RUTE_INDIA = [(12.5, 80.6), (9, 86), (6, 94), (2, 100), (-1.5, 104.0), PALEMBANG]
RUTE_ARAB = [(17.5, 55.5), (14, 60), (10, 70), (7, 78), (6.5, 88), (5.6, 95.5), PASAI]
RUTE_CINA = [(24.5, 119.0), (21, 115), (15, 111.5), (8, 109.5), (1, 107.5), (-4.5, 107.2), BATAVIA]
RUTE_PORTUGIS = [(-30, 33), (-20, 41), (-8, 47), (5, 57), (13, 70), (15.5, 73.5), (9, 75.5), (6, 81),
                 (5.5, 92), (4.5, 98), MALAKA]
RUTE_BELANDA = [(-36, 40), (-34, 60), (-26, 85), (-14, 100), (-7.5, 104.5), (-6.0, 106.0), BATAVIA]


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


def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def muncul(c, a):
    return back_out((c.t / c.d - a) / 0.1)


def titik(d, x, y, warna=MERAH, r=12, alpha=1.0):
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=(255, 255, 255, a), width=3)


def kapal(d, x, y, s=1.0, warna=(110, 70, 35), layar_warna=(240, 230, 205), alpha=1.0):
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    d.polygon([(x - 40 * s, y), (x + 40 * s, y), (x + 28 * s, y + 16 * s), (x - 28 * s, y + 16 * s)],
              fill=tuple(warna) + (a,), outline=(30, 20, 10, a))
    d.line((x, y, x, y - 52 * s), fill=(40, 25, 10, a), width=max(2, int(4 * s)))
    d.polygon([(x + 3 * s, y - 50 * s), (x + 34 * s, y - 10 * s), (x + 3 * s, y - 8 * s)],
              fill=tuple(layar_warna) + (a,), outline=(60, 45, 30, a))


def rute(d, kamera, jalur, k, warna, kapal_warna=None):
    """Garis putus-putus rute + kapal di ujungnya."""
    titik_layar = [layar(kamera, ll) for ll in jalur]
    se.garis_putus(d, titik_layar, k, warna, tebal=7, putus=20, celah=12)
    if 0 < k < 1:
        (x, y), _ = se.titik_di_jalur(titik_layar, k)
        kapal(d, x, y - 10, 1.1, layar_warna=kapal_warna or (240, 230, 205))


def ubin(img, x, y, kata, asal, warna, alpha, skala=1.0):
    """Kartu kata serapan: kata Indonesia + bentuk aslinya."""
    se.kartu(img, x, y, kata, asal, warna, alpha=alpha, skala=1.5 * skala, tiang=False)


def deret_kata(img, c, daftar, warna, mulai, jeda, y0=640, dy=165, x=540):
    """Munculkan kartu kata satu per satu (daftar = [(kata, asal)])."""
    for i, (kata, asal) in enumerate(daftar):
        a = mulai + i * jeda
        ubin(img, x, y0 + i * dy, kata, asal, warna, c.p(a, a + 0.06), muncul(c, a))


def kotak_judul(img, d, teks_, warna, alpha, y=470):
    """Pita judul asal bahasa (mis. 'SANSKERTA')."""
    if alpha <= 0.01:
        return
    f = se.font("caption", 64)
    w2 = f.getlength(teks_) / 2 + 40
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((540 - w2, y - 52, 540 + w2, y + 52), 26, fill=tuple(warna) + (240,),
                         outline=(255, 255, 255, 255), width=4)
    dl.text((540, y), teks_, font=f, fill=PUTIH, anchor="mm")
    se.tempel(img, lap, alpha)


def gelap_bawah(img, kuat=0.45):
    """Gelapkan peta tipis supaya kartu kata lebih kebaca."""
    se.tint(img, (10, 8, 5), kuat)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    kamera = Kamera(*cam(3.0, 100.0, 0.75))
    img, d = peta(kamera)
    rute(d, kamera, RUTE_PORTUGIS, 0.82 + 0.18 * c.p(0.0, 0.9), PORTUGIS, (200, 215, 240))
    gelap_bawah(img, 0.5)
    se.glow(img, 540, 560, 360, (255, 200, 120), 0.5)
    d = ImageDraw.Draw(img, "RGBA")
    s = 0.85 + 0.15 * back_out(c.t / 0.3)
    se.teks(d, (540, 520), "SEPATU =", int(130 * s), (255, 235, 180), nama_font="caption", stroke=10,
            stroke_warna=(30, 15, 5))
    se.teks(d, (540, 670), "PORTUGIS?!", int(140 * s), (255, 120, 90), nama_font="caption", stroke=10,
            stroke_warna=(30, 15, 5))
    kata = [("sepatu", "sapato"), ("meja", "mesa"), ("jendela", "janela")]
    for i, (k, asal) in enumerate(kata):
        a = 0.0 if i == 0 else i * 0.15
        ubin(img, 540, 880 + i * 165, k, "Portugis: " + asal, PORTUGIS, 1.0 if i == 0 else c.p(a, a + 0.05),
             1.0 if i == 0 else muncul(c, a))
    hdr(img, alpha=c.p(0.8, 0.95))
    return img


def _gelembung(img, box, isi, alpha, warna=(255, 255, 255), uk=52, sorot=None):
    """Gelembung chat. sorot = {kata: warna} untuk mewarnai kata tertentu."""
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    x0, y0, x1, y1 = box
    dl.rounded_rectangle((x0 + 6, y0 + 10, x1 + 6, y1 + 10), 40, fill=(0, 0, 0, 120))
    dl.rounded_rectangle(box, 40, fill=tuple(warna) + (255,))
    dl.polygon([(x0 + 60, y1 - 2), (x0 + 30, y1 + 50), (x0 + 120, y1 - 2)], fill=tuple(warna) + (255,))
    f = se.font("caption", uk)
    baris = se.bungkus(isi, f, x1 - x0 - 80)
    y = (y0 + y1) / 2 - (len(baris) - 1) * uk * 0.62
    for b in baris:
        kata = b.split()
        spasi = f.getlength(" ")
        total = sum(f.getlength(k) for k in kata) + spasi * (len(kata) - 1)
        x = (x0 + x1) / 2 - total / 2
        for k in kata:
            wr = (sorot or {}).get(k.strip(".,!?"), (35, 30, 40))
            dl.text((x, y), k, font=f, fill=tuple(wr) + (255,), anchor="lm")
            x += f.getlength(k) + spasi
        y += uk * 1.25
    se.tempel(img, lap, alpha)


def _latar_gelap():
    img = Image.new("RGBA", (W, H), GELAP + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(4)
    for _ in range(60):
        x, y, r = rng.uniform(0, W), rng.uniform(300, 1400), rng.uniform(30, 120)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(60, 55, 80, 40))
    return img, d


def a_tren(c):
    img, d = _latar_gelap()
    se.kartu(img, 540, 470, "IShowSpeed", "streamer asal Amerika · viral Oktober 2026", (120, 60, 160),
             alpha=c.p(0.0, 0.06), tiang=False, skala=muncul(c, 0.0))
    _gelembung(img, (120, 610, 960, 860), "Aku bisa bicara bahasa Indonesia!", c.p(0.33, 0.4))
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.66, 0.74)
    if a > 0:
        goyang = math.sin(c.t * 6) * 6
        se.teks(d, (540, 1060 + goyang), "?", 220, (255, 214, 10), nama_font="caption", stroke=10,
                stroke_warna=(0, 0, 0), alpha=a)
        se.teks(d, (540, 1250), "kalimat ini nyimpen rahasia", 50, PUTIH, nama_font="caption", stroke=6,
                stroke_warna=(0, 0, 0), alpha=a)
    hdr(img, "Lagi rame")
    return img


def a_simpang(c):
    kamera = se.kamera_antara(cam(8, 100, 0.62), cam(4, 102, 0.58), c.p(0, 1))
    img, d = peta(kamera)
    rutes = [(RUTE_INDIA, SANSKERTA), (RUTE_ARAB, ARAB), (RUTE_CINA, CINA), (RUTE_PORTUGIS, PORTUGIS),
             (RUTE_BELANDA, BELANDA)]
    for i, (jalur, w) in enumerate(rutes):
        k = c.p(0.05 + i * 0.08, 0.45 + i * 0.08)
        titik_layar = [layar(kamera, ll) for ll in jalur]
        se.garis_putus(d, titik_layar, k, w, tebal=7, putus=20, celah=12)
    for nama, ll, w in [("India", (18, 78), SANSKERTA), ("Cina", (27, 112), CINA)]:
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 46, w, c.p(0.1, 0.2), "caption")
    se.teks(d, (110, 560), "← Arab", 44, ARAB, nama_font="caption", stroke=5, stroke_warna=KREM_LABEL,
            anchor="lm", alpha=c.p(0.25, 0.32))
    se.teks(d, (110, 1180), "← Eropa", 44, PORTUGIS, nama_font="caption", stroke=5, stroke_warna=KREM_LABEL,
            anchor="lm", alpha=c.p(0.4, 0.48))
    x, y = layar(kamera, (-2, 112))
    label(d, (x, y + 40), "NUSANTARA", 50, TINTA, c.p(0.0, 0.1), "caption")
    se.kartu(img, 540, 1270, "Persimpangan kapal dunia", "tiap kapal ninggalin kata", MERAH,
             alpha=c.p(0.6, 0.68), tiang=False, skala=muncul(c, 0.6))
    hdr(img)
    return img


def a_sanskerta(c):
    kamera = se.kamera_antara(cam(10, 86, 0.75), cam(2, 98, 0.7), c.p(0.0, 0.45))
    img, d = peta(kamera)
    rute(d, kamera, RUTE_INDIA, c.p(0.0, 0.45), SANSKERTA)
    x, y = layar(kamera, PALEMBANG)
    titik(d, x, y, SANSKERTA, 14, c.p(0.4, 0.45))
    gelap_bawah(img, 0.35 * c.p(0.3, 0.4))
    kotak_judul(img, d, "SANSKERTA", SANSKERTA, c.p(0.02, 0.08))
    deret_kata(img, c, [("raja", "raja"), ("negara", "nagara"), ("agama", "agama"), ("surga", "svarga")],
               SANSKERTA, 0.47, 0.085)
    hdr(img, "Dari India, yang paling tua")
    return img


def a_arab(c):
    kamera = se.kamera_antara(cam(14, 62, 0.7), cam(7, 90, 0.7), c.p(0.0, 0.5))
    img, d = peta(kamera)
    rute(d, kamera, RUTE_ARAB, c.p(0.0, 0.5), ARAB)
    gelap_bawah(img, 0.35 * c.p(0.15, 0.25))
    kotak_judul(img, d, "ARAB", ARAB, c.p(0.02, 0.08))
    deret_kata(img, c, [("kursi", "kursiy"), ("kabar", "khabar"), ("waktu", "waqt")], ARAB, 0.27, 0.12)
    a = c.p(0.68, 0.73)
    if a > 0:
        se.panel(img, (110, 1080, 970, 1370), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
        for i, h in enumerate(hari):
            b = c.p(0.7 + i * 0.03, 0.74 + i * 0.03)
            xx = 230 + (i % 3) * 310
            yy = 1165 + (i // 3) * 100
            se.teks(d, (xx, yy), h, 50, ARAB, nama_font="caption", alpha=a * b)
        se.teks(d, (540, 1335), "nama hari juga dari bahasa Arab", 30, (90, 70, 50), nama_font="tangan_tipis",
                alpha=a)
    hdr(img, "Pedagang & ulama")
    return img


def a_cina(c):
    kamera = se.kamera_antara(cam(20, 116, 0.7), cam(8, 110, 0.7), c.p(0.0, 0.5))
    img, d = peta(kamera)
    rute(d, kamera, RUTE_CINA, c.p(0.0, 0.5), CINA)
    gelap_bawah(img, 0.35 * c.p(0.1, 0.2))
    kotak_judul(img, d, "TIONGHOA", CINA, c.p(0.02, 0.08))
    deret_kata(img, c, [("teh", "Hokkien: te"), ("tahu", "Hokkien: tau-hu"), ("kecap", "Hokkien: ke-tsiap")],
               CINA, 0.2, 0.12)
    a = c.p(0.55, 0.62)
    if a > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1060), "↓", 90, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0), alpha=a)
        s = muncul(c, 0.82)
        se.teks(d, (540, 1200), "KETCHUP?", int(120 * s) + 1, (255, 90, 60), nama_font="caption", stroke=9,
                stroke_warna=(0, 0, 0), alpha=c.p(0.82, 0.88))
        se.teks(d, (540, 1300), "dugaan kuat para ahli bahasa", 32, PUTIH, nama_font="ui", stroke=4,
                stroke_warna=(0, 0, 0), alpha=c.p(0.86, 0.92))
    hdr(img, "Pedagang Tionghoa")
    return img


def a_portugis(c):
    kamera = se.kamera_antara(cam(-8, 55, 0.62), cam(5, 92, 0.66), c.p(0.12, 0.45))
    img, d = peta(kamera)
    rute(d, kamera, RUTE_PORTUGIS, c.p(0.12, 0.45), PORTUGIS, (200, 215, 240))
    a_tapi = c.p(0.0, 0.03) * (1 - c.p(0.13, 0.17))
    if a_tapi > 0:
        se.tint(img, (0, 0, 0), 0.55 * a_tapi)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 760), "TAPI…", 170, (255, 214, 10), nama_font="caption", stroke=10, stroke_warna=(0, 0, 0),
                alpha=a_tapi)
        se.teks(d, (540, 920), "yang paling kerasa di rumah kita", 46, PUTIH, nama_font="caption", stroke=6,
                stroke_warna=(0, 0, 0), alpha=a_tapi)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.24, 0.29) * (1 - c.p(0.47, 0.5))
    if a > 0:
        se.teks(d, (540, 680), "1511", int(160 * muncul(c, 0.24)) + 1, (255, 235, 180), nama_font="caption",
                stroke=10, stroke_warna=(20, 30, 60), alpha=a)
        se.kartu(img, 540, 860, "Portugis merebut Malaka", "", PORTUGIS, alpha=c.p(0.36, 0.4), tiang=False)
    gelap_bawah(img, 0.35 * c.p(0.45, 0.5))
    d = ImageDraw.Draw(img, "RGBA")
    kotak_judul(img, d, "PORTUGIS", PORTUGIS, c.p(0.47, 0.52))
    kata = [("sepatu", "sapato"), ("meja", "mesa"), ("jendela", "janela"), ("bendera", "bandeira")]
    for i, (k, asal) in enumerate(kata):
        a2 = 0.52 + i * 0.065
        x = 290 if i % 2 == 0 else 790
        ubin(img, x, 640 + (i // 2) * 175, k, asal, PORTUGIS, c.p(a2, a2 + 0.04), muncul(c, a2))
    a3 = c.p(0.84, 0.89)
    if a3 > 0:
        se.kartu(img, 540, 1010, "Minggu", "dari kata domingo", MERAH, alpha=a3, tiang=False, skala=1.4 * muncul(c, 0.84))
    hdr(img, "Datang dari Eropa")
    return img


def a_belanda(c):
    kamera = se.kamera_antara(cam(-24, 75, 0.62), cam(-5, 104, 0.7), c.p(0.0, 0.45))
    img, d = peta(kamera)
    rute(d, kamera, RUTE_BELANDA, c.p(0.0, 0.45), BELANDA, (240, 160, 90))
    gelap_bawah(img, 0.35 * c.p(0.25, 0.35))
    kotak_judul(img, d, "BELANDA", BELANDA, c.p(0.02, 0.08))
    deret_kata(img, c, [("kantor", "kantoor"), ("handuk", "handdoek"), ("kulkas", "koelkast"),
                        ("wortel", "wortel")], BELANDA, 0.52, 0.1)
    hdr(img, "Tinggal lama banget")
    return img


KATA_HUJAN = ["sepatu", "kursi", "teh", "kantor", "raja", "kabar", "meja", "handuk", "agama", "tahu", "jendela",
              "waktu", "kulkas", "negara", "kecap", "bendera", "ilmu", "roda", "keju", "dunia"]
WARNA_HUJAN = [PORTUGIS, ARAB, CINA, BELANDA, SANSKERTA, ARAB, PORTUGIS, BELANDA, SANSKERTA, CINA, PORTUGIS,
               ARAB, BELANDA, SANSKERTA, CINA, PORTUGIS, ARAB, PORTUGIS, PORTUGIS, ARAB]


def a_jumlah(c):
    img, d = _latar_gelap()
    rng = random.Random(9)
    for i in range(40):
        k = KATA_HUJAN[i % len(KATA_HUJAN)]
        w = WARNA_HUJAN[i % len(WARNA_HUJAN)]
        x = rng.uniform(80, 1000)
        y = (rng.uniform(0, 1500) + c.t * rng.uniform(80, 160)) % 950 + 400
        se.teks(d, (x, y), k, int(rng.uniform(30, 52)), w, nama_font="caption", alpha=0.55)
    se.panel(img, (110, 640, 970, 1120), alpha=c.p(0.0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    n = int(20000 * c.p(0.05, 0.4))
    se.teks(d, (540, 820), f"± {n:,}".replace(",", "."), 140, MERAH, nama_font="caption", alpha=c.p(0.05, 0.1))
    se.teks(d, (540, 950), "kata serapan dicatat", 50, TINTA, nama_font="judul", alpha=c.p(0.1, 0.16))
    se.teks(d, (540, 1040), "Loan-Words in Indonesian and Malay (KITLV)", 28, (110, 90, 70), nama_font="tangan_tipis",
            alpha=c.p(0.3, 0.4))
    hdr(img, "Totalnya?")
    return img


KALIMAT = ["Aku", "bisa", "bicara", "bahasa", "Indonesia"]


def a_bongkar(c):
    img, d = _latar_gelap()
    _gelembung(img, (90, 430, 990, 640), "Aku bisa bicara bahasa Indonesia", 1.0, uk=56,
               sorot={"bicara": SANSKERTA if c.p(0.2, 0.22) > 0 else (35, 30, 40),
                      "bahasa": SANSKERTA if c.p(0.35, 0.37) > 0 else (35, 30, 40),
                      "Indonesia": YUNANI if c.p(0.55, 0.57) > 0 else (35, 30, 40)})
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 280, 790, "bicara", "Sanskerta: vicara", SANSKERTA, alpha=c.p(0.2, 0.25), tiang=False,
             skala=1.4 * muncul(c, 0.2))
    se.kartu(img, 800, 790, "bahasa", "Sanskerta: bhasa", SANSKERTA, alpha=c.p(0.35, 0.4), tiang=False,
             skala=1.4 * muncul(c, 0.35))
    a = c.p(0.55, 0.6)
    if a > 0:
        se.panel(img, (110, 920, 970, 1320), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 990), "INDONESIA", 74, YUNANI, nama_font="caption", alpha=a)
        se.teks(d, (540, 1080), "Yunani: Indos + nesos", 46, TINTA, nama_font="judul", alpha=c.p(0.67, 0.72))
        se.teks(d, (540, 1150), "= pulau-pulau India", 44, (90, 70, 50), nama_font="tangan", alpha=c.p(0.75, 0.8))
        se.teks(d, (540, 1250), "G. W. Earl & J. R. Logan · 1850", 34, MERAH, nama_font="ui", alpha=c.p(0.86, 0.9))
    hdr(img, "Rahasianya dibongkar")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(4, 102, 0.6))
    img, d = peta(kamera)
    for jalur, w in [(RUTE_INDIA, SANSKERTA), (RUTE_ARAB, ARAB), (RUTE_CINA, CINA), (RUTE_PORTUGIS, PORTUGIS),
                     (RUTE_BELANDA, BELANDA)]:
        se.garis_putus(d, [layar(kamera, ll) for ll in jalur], 1.0, w, tebal=7, putus=20, celah=12)
    se.tint(img, (10, 6, 0), 0.55)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 520, 990, 980), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 610), "Bukan bahasa miskin", 56, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 700), "justru jago nyerap", 46, (90, 70, 50), alpha=a)
        for i, w in enumerate([SANSKERTA, ARAB, CINA, PORTUGIS, BELANDA]):
            x = 260 + i * 140
            d.ellipse((x - 40, 790, x + 40, 870), fill=tuple(w) + (int(255 * a),), outline=(255, 255, 255, int(255 * a)),
                      width=4)
        se.teks(d, (540, 930), "kayak pelabuhan yang terbuka", 40, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Sepatu, meja, jendela. Ternyata bahasa Portugis.", a_hook, transisi=False),
    Adegan("tren", "Lagi rame IShowSpeed makin lancar bahasa Indonesia? Kalimat andalannya, aku bisa bicara bahasa "
                   "Indonesia, ternyata nyimpen rahasia. Nanti kita bongkar.", a_tren),
    Adegan("simpang", "Soalnya, Nusantara dari dulu persimpangan kapal dunia. Dan tiap kapal ninggalin kata.",
           a_simpang),
    Adegan("sanskerta", "Yang paling tua, dari India. Bahasa Sanskerta. Raja, negara, agama, surga, semuanya dari "
                        "sana.", a_sanskerta),
    Adegan("arab", "Lalu dari Arab. Kursi, kabar, waktu. Bahkan nama hari Senin sampai Sabtu.", a_arab),
    Adegan("cina", "Dari Tionghoa, ada teh, tahu, dan kecap. Yang katanya nyebrang ke Inggris, jadi ketchup.", a_cina),
    Adegan("portugis", "Tapi, yang paling kerasa justru dari Eropa. Tahun lima belas sebelas, Portugis merebut "
                       "Malaka. Lahirlah sepatu, meja, jendela, bendera. Bahkan hari Minggu, dari domingo.",
           a_portugis, transisi=False),
    Adegan("belanda", "Lalu Belanda datang. Hasilnya? Kantor, handuk, kulkas, wortel.", a_belanda),
    Adegan("jumlah", "Satu kamus etimologi bahkan mencatat sekitar dua puluh ribu kata serapan.", a_jumlah),
    Adegan("bongkar", "Nah, balik ke kalimat IShowSpeed. Bicara, dari Sanskerta. Bahasa, juga Sanskerta. Dan "
                      "Indonesia? Dari bahasa Yunani, artinya pulau-pulau India. Dicetuskan tahun delapan belas lima "
                      "puluh.", a_bongkar),
    Adegan("penutup", "Jadi, bahasa kita bukan bahasa miskin. Dia jago nyerap. Follow Ngomongin Sejarah buat cerita "
                      "berikutnya!", a_penutup),
]
