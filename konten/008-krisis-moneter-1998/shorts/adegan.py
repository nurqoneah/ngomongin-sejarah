"""Shorts ±90 detik: Krisis Moneter 1997–1998.

Peta Asia Tenggara (penularan krisis) + adegan ilustrasi (papan kurs, timbangan utang, antrean bank, grafik).
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import EMAS, HIJAU, MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "krisis-moneter-1998-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "KRISMON 1998"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
KERTAS = (247, 236, 208)
BIRU = (30, 80, 150)
GELAP = (28, 26, 32)

print("  menyiapkan peta Asia Tenggara...")
PETA = Peta(90, 125, -12, 22, 100, [], [(-2, 114, 1.5), (0, 101, 1.2), (5, 117, 1.0), (18, 101, 3), (14, 106, 2)],
            seed=31, darat=pd.SEMUA)
print("  menyiapkan latar kertas...")
LATAR = se.latar_tekstur(W, H, 44, warna=(225, 205, 160)).convert("RGBA")

BANGKOK = (13.75, 100.5)
KOTA = {"Kuala Lumpur": (3.14, 101.69), "Jakarta": (-6.2, 106.8), "Manila": (14.6, 121.0)}


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


def kertas(gelap=0.0):
    img = LATAR.copy()
    se.tint(img, (15, 10, 5), gelap)
    return img, ImageDraw.Draw(img, "RGBA")


def hdr(img, sub="1997 – 1998", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def rp(n):
    return "Rp " + f"{int(n):,}".replace(",", ".")


def cincin(d, x, y, r, warna, alpha, tebal=8):
    if alpha <= 0.01 or r <= 1:
        return
    d.ellipse((x - r, y - r, x + r, y + r), outline=tuple(warna) + (int(255 * alpha),), width=tebal)


def uang(d, x, y, s=1.0, warna=(110, 160, 90), simbol="$", a=255):
    """Lembar uang kertas kecil."""
    if s < 0.15:
        return
    w, h = 120 * s, 58 * s
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), int(8 * s), fill=tuple(warna) + (a,),
                        outline=(40, 50, 30, a), width=max(2, int(3 * s)))
    d.ellipse((x - 18 * s, y - 18 * s, x + 18 * s, y + 18 * s), outline=(40, 50, 30, a), width=max(2, int(3 * s)))
    d.text((x, y), simbol, font=se.font("caption", int(26 * s) + 1), fill=(30, 40, 20, a), anchor="mm")


def grafik(img, box, data, progres, warna, label_x=(), judul="", alpha=1.0, tebal=10):
    """Grafik garis sederhana di atas panel. data: list (fraksi_x, nilai); nilai dinormalisasi otomatis."""
    se.panel(img, box, alpha=alpha)
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    gx0, gx1, gy0, gy1 = x0 + 80, x1 - 60, y0 + 120, y1 - 110
    a = int(255 * alpha)
    d.line((gx0, gy1, gx1, gy1), fill=(120, 90, 50, a), width=4)
    d.line((gx0, gy0, gx0, gy1), fill=(120, 90, 50, a), width=4)
    if judul:
        se.teks(d, ((x0 + x1) / 2, y0 + 60), judul, 40, (110, 30, 20), nama_font="judul", alpha=alpha)
    for fx, isi in label_x:
        se.teks(d, (lerp(gx0, gx1, fx), gy1 + 40), isi, 28, (90, 70, 50), nama_font="tangan_tipis", alpha=alpha)
    vmin = min(v for _, v in data)
    vmax = max(v for _, v in data)
    titik = [(lerp(gx0, gx1, fx), lerp(gy1 - 20, gy0 + 20, (v - vmin) / (vmax - vmin or 1))) for fx, v in data]
    if progres <= 0:
        return titik, None
    ujung, _ = se.titik_di_jalur(titik, progres)
    # potong polyline sampai ujung
    panjang = [0.0]
    for (ax, ay), (bx, by) in zip(titik, titik[1:]):
        panjang.append(panjang[-1] + math.hypot(bx - ax, by - ay))
    batas = panjang[-1] * clamp(progres)
    jalur = [titik[0]] + [p for p, L in zip(titik[1:], panjang[1:]) if L < batas] + [ujung]
    d.line(jalur, fill=tuple(warna) + (a,), width=tebal, joint="curve")
    d.ellipse((ujung[0] - 14, ujung[1] - 14, ujung[0] + 14, ujung[1] + 14), fill=tuple(warna) + (a,),
              outline=(255, 255, 255, a), width=4)
    return titik, ujung


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img, d = kertas(0.55)
    s = back_out(c.t / 0.3)
    uang(d, 540, 560, 2.6 * s + 0.01)
    se.teks(d, (540, 700), "1 DOLAR =", 64, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=c.p(0.02, 0.1))
    k = c.p(0.5, 0.85)
    nilai = lerp(2380, 16800, k)
    warna = se.lerp_rgb((255, 235, 180), (255, 80, 60), k)
    se.teks(d, (540, 840), rp(round(nilai, -1) if 0 < k < 1 else nilai), 128, warna, nama_font="caption", stroke=10,
            stroke_warna=(0, 0, 0), alpha=c.p(0.05, 0.12))
    th = "Juni 1997" if k < 0.5 else "Juni 1998"
    se.teks(d, (540, 970), th, 54, (255, 220, 160), nama_font="caption", stroke=6, stroke_warna=(0, 0, 0),
            alpha=c.p(0.05, 0.12))
    if k > 0.3:
        sk = back_out((c.t / c.d - 0.62) / 0.1)
        se.teks(d, (540, 1130), "cuma dalam setahun!", int(60 * clamp(sk, 0, 1.3)) + 1, PUTIH, nama_font="caption",
                stroke=7, stroke_warna=(150, 20, 10))
    hdr(img, alpha=c.p(0.8, 0.95))
    return img


def _papan_bursa(img, d, t, merah=1.0):
    """Papan bursa elektronik dengan baris-baris angka merah."""
    d.rounded_rectangle((70, 400, 1010, 1300), 30, fill=(18, 20, 26, 255), outline=(80, 80, 90, 255), width=6)
    rng = random.Random(5)
    for i in range(11):
        y = 450 + i * 76
        kode = "".join(rng.choice("ABCDEGIKLMNPRSTUW") for _ in range(4))
        turun = rng.uniform(1.5, 9.9)
        kedip = 0.6 + 0.4 * abs(math.sin(t * 3 + i))
        se.teks(d, (130, y), kode, 40, (200, 200, 210), nama_font="ui", anchor="lm", alpha=0.35)
        se.teks(d, (950, y), f"▼ {turun:.2f}%".replace(".", ","), 40, (230, 60, 50), nama_font="ui", anchor="rm",
                alpha=0.35 * kedip * merah)


def a_tren(c):
    img = Image.new("RGBA", (W, H), GELAP + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    _papan_bursa(img, d, c.t)
    se.tint(img, (0, 0, 0), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.6, 0.66))
    if a > 0:
        # panah turun besar
        y = 450 + 100 * c.p(0.02, 0.3)
        d.polygon([(540, y + 200), (430, y + 60), (500, y + 60), (500, y - 60), (580, y - 60), (580, y + 60),
                   (650, y + 60)], fill=(220, 50, 40, int(255 * a)), outline=(255, 255, 255, int(255 * a)))
        se.teks(d, (540, 1010), "IHSG < 5.000", 110, (255, 90, 70), nama_font="caption", stroke=9,
                stroke_warna=(0, 0, 0), alpha=a)
        se.kartu(img, 540, 1180, "Rupiah tembus Rp 18.000 / $", "19 Oktober 2026", MERAH,
                 alpha=c.p(0.2, 0.28) * (1 - c.p(0.6, 0.66)), tiang=False)
    b = c.p(0.64, 0.72)
    if b > 0:
        sk = back_out((c.t / c.d - 0.64) / 0.12)
        se.teks(d, (540, 800), "Keinget…", 64, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0), alpha=b)
        se.teks(d, (540, 950), "KRISMON 98", int(140 * clamp(sk, 0, 1.3)) + 1, EMAS, nama_font="caption", stroke=10,
                stroke_warna=(60, 20, 10), alpha=b)
        se.teks(d, (540, 1100), "separah apa sih?", 56, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0),
                alpha=c.p(0.8, 0.88))
    hdr(img, "Lagi rame: Oktober 2026", alpha=c.p(0.0, 0.1))
    return img


def a_thailand(c):
    kamera = Kamera(*cam(5.0, 108.5, 0.57))
    img, d = peta(kamera)
    bx, by = layar(kamera, BANGKOK)
    for i in range(3):
        f = (c.t * 0.5 + i / 3) % 1.0
        if c.t / c.d > 0.15:
            cincin(d, bx, by, 30 + f * 260, (220, 60, 40), (1 - f) * 0.8, 6)
    d.ellipse((bx - 14, by - 14, bx + 14, by + 14), fill=(220, 60, 40, 255), outline=(255, 255, 255, 255), width=4)
    label(d, (bx + 95, by + 45), "Bangkok", 38, (150, 30, 20))
    se.kartu(img, 540, 1250, "2 Juli 1997: Thailand melepas baht", "baht langsung ambruk", MERAH,
             alpha=c.p(0.05, 0.14), tiang=False, skala=back_out((c.t / c.d - 0.05) / 0.1))
    for i, (nama, ll) in enumerate(KOTA.items()):
        k = c.p(0.5 + i * 0.08, 0.66 + i * 0.08)
        x, y = layar(kamera, ll)
        se.garis_putus(d, [(bx, by), ((bx + x) / 2 + 40, (by + y) / 2), (x, y)], k, (200, 50, 40), tebal=6)
        if k >= 1:
            d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(200, 50, 40, 255), outline=(255, 255, 255, 255), width=3)
            if x > W - 40:
                label(d, (W - 110, y + 45), nama + " →", 34, (150, 30, 20))
            else:
                label(d, (x, y + 44), nama, 34, (150, 30, 20))
    k = c.p(0.72, 0.84)
    se.garis_putus(d, [(bx + 40, by - 20), (1010, 385)], k, (200, 50, 40), tebal=6)
    if k >= 1:
        label(d, (790, 400), "ke Korea Selatan", 34, (150, 30, 20), font="tangan")
    hdr(img, "Juli 1997")
    return img


def _timbangan(d, x, y, miring, a=255):
    """Timbangan: kiri = utang dolar, kanan = rupiah. miring > 0 = kiri turun."""
    d.polygon([(x - 70, y + 330), (x + 70, y + 330), (x + 20, y + 280), (x - 20, y + 280)], fill=(90, 60, 35, a))
    d.rectangle((x - 10, y, x + 10, y + 290), fill=(90, 60, 35, a))
    L = 330
    dy = math.sin(miring) * L
    ki, ka = (x - L, y + dy), (x + L, y - dy)
    d.line((ki, ka), fill=(70, 45, 25, a), width=12)
    d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=(200, 160, 60, a), outline=(70, 45, 25, a), width=4)
    for px, py in (ki, ka):
        d.line((px, py, px - 80, py + 140), fill=(70, 45, 25, a), width=4)
        d.line((px, py, px + 80, py + 140), fill=(70, 45, 25, a), width=4)
        d.chord((px - 120, py + 90, px + 120, py + 190), 0, 180, fill=(200, 160, 60, a), outline=(70, 45, 25, a), width=4)
    return ki, ka


def a_utang(c):
    img, d = kertas()
    se.kartu(img, 540, 450, "Utang swasta dalam dolar", "banyak yang jangka pendek", (90, 60, 35),
             alpha=c.p(0.03, 0.12), tiang=False, skala=back_out((c.t / c.d - 0.03) / 0.1))
    tumpuk = int(2 + 7 * c.p(0.25, 0.6))
    miring = 0.08 + 0.32 * c.p(0.25, 0.6)
    ki, ka = _timbangan(d, 540, 760, miring, int(255 * c.p(0.0, 0.08)))
    if c.t / c.d > 0.05:
        for i in range(tumpuk):
            uang(d, ki[0] + (i % 2) * 14 - 7, ki[1] + 125 - i * 30, 0.9)
        uang(d, ka[0], ka[1] + 125, 0.9, (190, 120, 110), "Rp")
        label(d, (ki[0], ki[1] + 230), "utang $", 36, (110, 30, 20))
        label(d, (ka[0], ka[1] + 230), "rupiah", 36, TINTA)
        se.teks(d, (ki[0] + 30, ki[1] - 120), "MEMBENGKAK!", 44, MERAH, nama_font="caption", stroke=5,
                stroke_warna=PUTIH, alpha=c.p(0.45, 0.52) * (1 - c.p(0.62, 0.66)))
    se.kartu(img, 540, 1260, "14 Agustus 1997", "BI melepas rupiah ke kurs mengambang bebas", BIRU,
             alpha=c.p(0.66, 0.74), tiang=False, skala=back_out((c.t / c.d - 0.66) / 0.1))
    hdr(img, "Kenapa Indonesia paling parah?")
    return img


def _bank(d, x, y, s=1.0, tutup=0.0, a=255):
    w = 300 * s
    d.polygon([(x - w / 2 - 20, y - 160 * s), (x, y - 250 * s), (x + w / 2 + 20, y - 160 * s)], fill=(235, 225, 200, a),
              outline=(70, 55, 40, a))
    d.rectangle((x - w / 2, y - 160 * s, x + w / 2, y), fill=(225, 212, 185, a), outline=(70, 55, 40, a), width=4)
    for i in range(4):
        cx = x - w / 2 + 40 * s + i * (w - 80 * s) / 3
        d.rectangle((cx - 12 * s, y - 145 * s, cx + 12 * s, y - 10 * s), fill=(245, 238, 220, a), outline=(110, 90, 70, a))
    d.text((x, y - 195 * s), "BANK", font=se.font("judul", int(34 * s) + 1), fill=(70, 55, 40, a), anchor="mm")
    if tutup > 0:
        k = clamp(tutup)
        d.line((x - w / 2, y - 160 * s, x - w / 2 + w * k, y - 160 * s + 160 * s * k), fill=(200, 30, 30, a), width=int(14 * s))
        d.line((x + w / 2, y - 160 * s, x + w / 2 - w * k, y - 160 * s + 160 * s * k), fill=(200, 30, 30, a), width=int(14 * s))


def a_bank(c):
    img, d = kertas()
    # IMF
    se.kartu(img, 540, 450, "Oktober 1997: minta bantuan IMF", "", BIRU,
             alpha=c.p(0.02, 0.1) * (1 - c.p(0.3, 0.35)), tiang=False, skala=back_out((c.t / c.d - 0.02) / 0.1))
    # 16 bank ditutup
    a = c.p(0.28, 0.36)
    if a > 0:
        for i in range(16):
            x = 135 + (i % 8) * 116
            y = 560 + (i // 8) * 130
            _bank(d, x, y, 0.32, tutup=c.p(0.32 + i * 0.012, 0.4 + i * 0.012), a=int(255 * a))
        se.kartu(img, 540, 760, "1 Nov 1997: 16 bank swasta ditutup", "", MERAH, alpha=a, tiang=False)
    # rush: antrean orang (titik) ke bank lain
    b = c.p(0.62, 0.7)
    if b > 0:
        _bank(d, 840, 1260, 0.9, a=int(255 * b))
        n = int(40 * c.p(0.62, 0.95))
        rng = random.Random(9)
        for i in range(n):
            x = 660 - (i % 20) * 30 + rng.uniform(-5, 5)
            y = 1225 - (i // 20) * 34 + rng.uniform(-4, 4) + math.sin(c.t * 6 + i) * 2
            d.ellipse((x - 11, y - 30, x + 11, y - 8), fill=(60, 45, 35, int(255 * b)))
            d.rounded_rectangle((x - 13, y - 8, x + 13, y + 24), 8, fill=(90, 70, 55, int(255 * b)))
        se.teks(d, (340, 1060), "RUSH!", 90, MERAH, nama_font="caption", stroke=7, stroke_warna=PUTIH,
                alpha=c.p(0.7, 0.76))
    hdr(img, "Akhir 1997")
    return img


KURS = [(0.0, 2380), (0.25, 3000), (0.45, 4850), (0.6, 16800), (0.62, 17000), (0.75, 9000), (0.85, 11000),
        (1.0, 16800)]


def a_kurs(c):
    img, d = kertas(0.15)
    titik, ujung = grafik(img, (60, 420, 1020, 1240), KURS, c.p(0.05, 0.7), MERAH,
                          label_x=((0.0, "Jun 97"), (0.45, "Des 97"), (0.62, "Jan 98"), (1.0, "Jun 98")),
                          judul="Rupiah per 1 dolar", alpha=c.p(0.0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    if titik:
        se.teks(d, (titik[0][0] + 20, titik[0][1] - 50), "2.380", 40, TINTA, nama_font="caption", anchor="lm",
                alpha=c.p(0.05, 0.1))
        se.teks(d, (titik[4][0] + 30, titik[4][1] + 10), "± 17.000", 40, MERAH, nama_font="caption", anchor="lm",
                alpha=c.p(0.45, 0.52))
        se.teks(d, (titik[-1][0] - 10, titik[-1][1] + 60), "16.800", 40, MERAH, nama_font="caption", anchor="rm",
                alpha=c.p(0.68, 0.74))
    se.kartu(img, 540, 1330, "Nilai rupiah hilang > 80%", "", (60, 60, 70), alpha=c.p(0.78, 0.85), tiang=False,
             skala=back_out((c.t / c.d - 0.78) / 0.1))
    hdr(img, "Rupiah terjun bebas")
    return img


IHSG = [(0.0, 740), (0.12, 700), (0.3, 340), (0.45, 550), (0.6, 420), (0.75, 400), (1.0, 256)]


def a_ihsg(c):
    img = Image.new("RGBA", (W, H), GELAP + (255,))
    titik, ujung = grafik(img, (60, 420, 1020, 1240), IHSG, c.p(0.08, 0.75), MERAH,
                          label_x=((0.0, "Jul 97"), (0.5, "1998"), (1.0, "21 Sep 98")),
                          judul="IHSG (Bursa Efek Jakarta)", alpha=c.p(0.0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    if titik:
        se.teks(d, (titik[0][0] + 30, titik[0][1] - 45), "740", 44, TINTA, nama_font="caption", anchor="lm",
                alpha=c.p(0.08, 0.14))
        se.teks(d, (titik[-1][0] - 10, titik[-1][1] - 60), "256", 52, MERAH, nama_font="caption", anchor="rm",
                alpha=c.p(0.72, 0.78))
    sk = back_out((c.t / c.d - 0.8) / 0.1)
    se.teks(d, (540, 1340), "− 65%", int(120 * clamp(sk, 0, 1.3)) + 1, (255, 90, 70), nama_font="caption", stroke=9,
            stroke_warna=(0, 0, 0), alpha=c.p(0.8, 0.84))
    hdr(img, "Bursa saham ambruk")
    return img


def _angka(d, y, besar, kecil, warna, a):
    se.teks(d, (540, y), besar, 110, warna, nama_font="caption", stroke=9, stroke_warna=(0, 0, 0), alpha=a)
    se.teks(d, (540, y + 90), kecil, 40, PUTIH, nama_font="caption", stroke=5, stroke_warna=(0, 0, 0), alpha=a)


def a_rakyat(c):
    img, d = kertas(0.6)
    # keranjang belanja dengan label harga naik
    a0 = c.p(0.0, 0.08)
    rng = random.Random(3)
    for i in range(26):
        x = 80 + i * 36 + rng.uniform(-6, 6)
        y = 1300 + rng.uniform(-10, 10) + math.sin(c.t * 4 + i) * 2
        al = int(255 * c.p(0.0 + i * 0.004, 0.06 + i * 0.004))
        d.ellipse((x - 13, y - 36, x + 13, y - 10), fill=(235, 215, 175, al))
        d.rounded_rectangle((x - 16, y - 10, x + 16, y + 30), 9, fill=(235, 215, 175, al))
    _angka(d, 470, f"− {int(13 * c.p(0.12, 0.3))}%", "ekonomi menyusut (1998)", (255, 120, 80), c.p(0.1, 0.16))
    _angka(d, 740, "> 50%", "inflasi · harga melonjak", EMAS, c.p(0.38, 0.45))
    juta = 49.5 * c.p(0.65, 0.85)
    _angka(d, 1010, f"{juta:.1f} JUTA".replace(".", ","), "penduduk miskin (BPS, 1998)", (255, 90, 70), c.p(0.62, 0.68))
    hdr(img, "Yang paling kena: rakyat", alpha=a0)
    return img


def a_reformasi(c):
    kamera = se.kamera_antara(cam(-3.0, 110.0, 0.62), cam(-6.0, 107.5, 1.1), c.p(0.0, 0.5))
    img, d = peta(kamera)
    jx, jy = layar(kamera, KOTA["Jakarta"])
    d.ellipse((jx - 14, jy - 14, jx + 14, jy + 14), fill=(200, 40, 30, 255), outline=(255, 255, 255, 255), width=4)
    label(d, (jx, jy + 50), "Jakarta", 40, (150, 30, 20))
    se.kartu(img, 540, 560, "Krisis ekonomi → krisis politik", "", (60, 60, 70),
             alpha=c.p(0.03, 0.12), tiang=False)
    se.kartu(img, 540, 720, "21 Mei 1998: Presiden Soeharto mundur", "", MERAH,
             alpha=c.p(0.3, 0.38), tiang=False, skala=back_out((c.t / c.d - 0.3) / 0.1))
    se.kartu(img, 540, 1160, "Era Reformasi", "", HIJAU, alpha=c.p(0.78, 0.85), tiang=False,
             skala=back_out((c.t / c.d - 0.78) / 0.1))
    hdr(img, "Mei 1998")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    img, d = kertas(0.6)
    a = c.p(0.02, 0.1) * (1 - c.p(0.58, 0.64))
    if a > 0:
        se.panel(img, (90, 450, 990, 1080), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 540), "Pelajaran dari 98", 54, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 630), "kepanikan bikin krisis makin dalam", 36, (90, 70, 50), alpha=a)
        _bank(d, 540, 900, 0.75, a=int(255 * a))
        d.rounded_rectangle((640, 720, 860, 800), 16, fill=(46, 160, 90, int(255 * a)))
        d.text((750, 760), "LPS", font=se.font("caption", 40), fill=(255, 255, 255, int(255 * a)), anchor="mm")
        se.teks(d, (540, 970), "Simpanan dijamin s.d. Rp 2 miliar", 40, (20, 90, 50), nama_font="caption", alpha=a)
        se.teks(d, (540, 1030), "per nasabah per bank", 32, (90, 70, 50), alpha=a)
    b = c.p(0.62, 0.7)
    if b > 0:
        m = maskot()
        if m is not None:
            loncat = abs(math.sin(c.t * 5)) * 18
            se.tempel(img, m, b, (540 - m.width // 2, int(560 - loncat)))
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        sk = back_out((c.t / c.d - 0.62) / 0.1)
        w2 = 380 * sk
        dl.rounded_rectangle((540 - w2, 960, 540 + w2, 1090), 40, fill=(200, 52, 44, 245))
        dl.text((540, 1025), "NGOMONGIN SEJARAH", font=se.font("caption", int(56 * sk) + 1), fill=PUTIH, anchor="mm")
        dl.text((540, 1160), "Follow buat cerita berikutnya", font=se.font("ui", 42), fill=PUTIH, anchor="mm",
                stroke_width=4, stroke_fill=(0, 0, 0))
        se.tempel(img, lap, b)
    return img


ADEGAN = [
    Adegan("hook", "Tahun sembilan tujuh, satu dolar cuma dua ribu tiga ratusan rupiah. Setahun kemudian? "
                   "Enam belas ribu delapan ratus!", a_hook, transisi=False),
    Adegan("tren", "Lagi rame IHSG jebol di bawah lima ribu, dan rupiah tembus delapan belas ribu? Langsung "
                   "keinget krismon sembilan delapan. Separah apa sih?", a_tren),
    Adegan("thailand", "Awalnya dari Thailand. Juli sembilan tujuh, baht dilepas, langsung ambruk. "
                       "Paniknya menular. Malaysia, Indonesia, Filipina, sampai Korea Selatan.", a_thailand),
    Adegan("utang", "Indonesia paling parah. Banyak perusahaan punya utang dolar jangka pendek. Rupiah melemah, "
                    "utangnya membengkak. Agustus, rupiah dilepas ke kurs mengambang bebas.", a_utang),
    Adegan("bank", "Indonesia minta bantuan IMF. November, enam belas bank swasta ditutup. Orang panik, "
                   "rame-rame narik uang. Rush.", a_bank),
    Adegan("kurs", "Rupiah terjun bebas. Januari sembilan delapan, sempat nyentuh tujuh belas ribuan. "
                   "Lebih dari delapan puluh persen nilainya hilang.", a_kurs),
    Adegan("ihsg", "IHSG ikut ambruk, dari tujuh ratus empat puluhan, tinggal dua ratus lima puluh enam. "
                   "Anjlok sekitar enam puluh lima persen.", a_ihsg, transisi=False),
    Adegan("rakyat", "Rakyat paling kena. Ekonomi menyusut sekitar tiga belas persen. Inflasi lebih dari "
                     "lima puluh persen. Penduduk miskin, hampir lima puluh juta orang.", a_rakyat),
    Adegan("reformasi", "Krisisnya merembet ke politik. Dua puluh satu Mei sembilan delapan, "
                        "Presiden "
                        "Soeharto mundur. Era Reformasi dimulai.", a_reformasi),
    Adegan("penutup", "Pelajarannya, panik bikin krisis makin dalam. Sekarang, simpanan bank dijamin LPS sampai "
                      "dua miliar rupiah. Jadi, jangan gampang panik. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
