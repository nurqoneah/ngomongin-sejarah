"""Shorts ±88 detik: Kenapa orang Minang merantau? (asal-usul tradisi merantau).

Tiga jenis visual: (1) peta Nusantara–Semenanjung Malaya dengan rute rantau,
(2) peta dekat Sumatra Barat (darek / Luhak nan Tigo, gunung, danau, sungai ke timur),
(3) ilustrasi rumah gadang + surau, dokumen sensus, papan pepatah.
Tokoh hanya berupa kartu nama, orang berupa titik. Waktu animasi pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import EMAS, MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "tradisi-merantau-minang-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "MERANTAU"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
BIRU = (30, 80, 150)
AIR = (55, 105, 160)
COKLAT = (120, 80, 40)
IJUK = (45, 32, 24)
MERAH_GADANG = (150, 40, 30)
HIJAU_SAWAH = (90, 140, 60)
PINK = (225, 95, 130)

# ------------------------------------------------------------------ peta lebar (Sumatra – Malaya – Jawa)

# Semenanjung Malaya lebih rinci (garis pantai bawaan terlalu kasar di skala ini)
MALAYA = [(9.5, 98.4), (8.0, 98.3), (6.6, 99.9), (5.4, 100.35), (4.2, 100.6), (3.0, 101.3), (2.4, 101.85),
          (1.6, 102.9), (1.3, 103.5), (1.4, 104.25), (2.1, 103.9), (3.0, 103.4), (4.2, 103.45), (5.3, 103.1),
          (6.2, 102.2), (6.9, 101.6), (8.2, 100.4), (9.5, 99.8)]
print("  menyiapkan peta Nusantara barat...")
LEBAR = Peta(92, 118, -9, 9, 110, [], [(-0.4, 100.4, 0.9), (-2.5, 102, 0.8), (3, 98, 0.7), (4.5, 102, 0.7),
                                      (-7.2, 108, 0.6), (0, 113.5, 1.2)], seed=20, darat=pd.SEMUA + [MALAYA])

# ------------------------------------------------------------------ peta dekat Sumatra Barat

PANTAI_BARAT = [(1.4, 98.75), (0.9, 98.95), (0.55, 99.1), (0.2, 99.35), (-0.1, 99.65), (-0.35, 99.9), (-0.63, 100.12),
                (-0.95, 100.35), (-1.2, 100.42), (-1.35, 100.57), (-1.7, 100.8), (-2.05, 100.95), (-2.4, 101.15)]
DARAT_DEKAT = PANTAI_BARAT + [(-2.4, 102.4), (1.4, 102.4)]
GUNUNG_DEKAT = [(-0.38, 100.47, 0.09), (-0.39, 100.33, 0.08), (-0.48, 100.38, 0.06), (-0.31, 100.66, 0.06),
                (0.08, 99.98, 0.09), (-1.7, 101.26, 0.12), (-0.9, 100.75, 0.2), (0.0, 100.3, 0.25)]
print("  menyiapkan peta Sumatra Barat...")
DEKAT = Peta(98.8, 102.2, -2.2, 1.2, 650, [], GUNUNG_DEKAT, seed=21, darat=[DARAT_DEKAT])

MARAPI = (-0.38, 100.47)
PAGARUYUNG = (-0.47, 100.62)
MINANG = (-0.4, 100.5)
LUHAK = [("Tanah Datar", (-0.52, 100.6), (200, 52, 44)), ("Agam", (-0.25, 100.28), (230, 170, 40)),
         ("Lima Puluh Kota", (-0.16, 100.68), (40, 110, 70))]
DANAU = [((-0.31, 100.2), 0.045, 0.035), ((-0.62, 100.53), 0.06, 0.025)]
SUNGAI_TIMUR = [
    ("Kampar", [(-0.12, 100.65), (0.0, 100.85), (0.15, 101.05), (0.3, 101.3), (0.35, 101.7), (0.3, 102.4)]),
    ("Kuantan", [(-0.6, 100.75), (-0.55, 101.0), (-0.5, 101.3), (-0.45, 101.6), (-0.4, 102.0), (-0.38, 102.4)]),
    ("Batanghari", [(-1.0, 100.85), (-1.15, 101.1), (-1.25, 101.4), (-1.35, 101.8), (-1.45, 102.4)]),
]
PESISIR = [("Pariaman", (-0.63, 100.12)), ("Padang", (-0.95, 100.35)), ("Air Bangis", (0.2, 99.38))]

KOTA_RANTAU = {"Medan": (3.6, 98.67), "Aceh": (5.55, 95.32), "Pekanbaru": (0.51, 101.45), "Jambi": (-1.6, 103.6),
               "Palembang": (-2.98, 104.75), "Bengkulu": (-3.8, 102.27), "Jakarta": (-6.2, 106.82),
               "Bandung": (-6.9, 107.6), "Seremban": (2.8, 102.15), "Singapura": (1.3, 103.85),
               "Pontianak": (-0.03, 109.33), "Lampung": (-5.43, 105.26), "Tanjung Pinang": (0.92, 104.45),
               "Sibolga": (1.74, 98.78)}
KOTA_RM = list(KOTA_RANTAU.values()) + [(-7.0, 110.42), (-7.8, 110.37), (-7.25, 112.75), (-1.27, 116.83),
                                         (-3.32, 114.6), (-6.55, 106.8), (-6.6, 110.67), (-7.55, 110.82), (3.15, 101.7)]


# ------------------------------------------------------------------ helper

def cam(p, lat, lon, zoom):
    x, y = p.px(lat, lon)
    return (x, y, zoom)


def peta(p, kamera):
    img = se.render_peta(p, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(p, kamera, ll):
    return kamera.layar(*p.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def hdr(img, sub="Tradisi orang Minang", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def angka_besar(d, xy, isi, uk, warna=PUTIH, alpha=1.0, stroke_warna=(10, 20, 40)):
    se.teks(d, xy, isi, uk, warna, nama_font="caption", stroke=10, stroke_warna=stroke_warna, alpha=alpha)


def titik(d, x, y, warna=MERAH, r=12, alpha=1.0, denyut=0.0):
    a = int(255 * alpha)
    if a <= 2:
        return
    if denyut > 0:
        rr = r + 34 * denyut
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=tuple(warna) + (int(a * (1 - denyut)),), width=4)
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=(30, 15, 10, a), width=3)


def lengkung(a, b, tekuk=0.18, n=24):
    """Titik-titik kurva kuadratik dari a ke b (layar), ditekuk ke samping."""
    (x0, y0), (x1, y1) = a, b
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * tekuk, my + dx * tekuk
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1,
                    (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1))
    return out


def rute_rantau(img, kamera, k, t, warna=MERAH, alpha=1.0, kota=None):
    """Rute putus-putus dari ranah Minang ke kota-kota rantau. k: progres 0..1."""
    d = ImageDraw.Draw(img, "RGBA")
    asal = layar(LEBAR, kamera, MINANG)
    for i, (nama, ll) in enumerate(KOTA_RANTAU.items()):
        if kota and nama not in kota:
            continue
        kk = clamp(k * 1.6 - i * 0.04)
        if kk <= 0:
            continue
        ujung = layar(LEBAR, kamera, ll)
        pts = lengkung(asal, ujung, 0.15 if i % 2 else -0.15)
        se.garis_putus(d, pts, kk, warna, tebal=6, putus=16, celah=11, alpha=alpha)
        if kk >= 1:
            titik(d, *ujung, warna=EMAS, r=10, alpha=alpha, denyut=(t * 0.8 + i * 0.13) % 1)
    titik(d, *asal, warna=MERAH, r=16, alpha=alpha)


def rumah_gadang(d, cx, lantai, w, alpha=1.0, gonjong=4, pintu=True):
    """Rumah gadang ilustrasi: tiang, badan berukir, atap ijuk melengkung dengan gonjong."""
    a = int(255 * alpha)
    if a <= 2:
        return
    x0, x1 = cx - w / 2, cx + w / 2
    tb = w * 0.26  # tinggi badan
    # tiang
    for i in range(7):
        x = lerp(x0 + 20, x1 - 20, i / 6)
        d.rectangle((x - 7, lantai, x + 7, lantai + w * 0.12), fill=(90, 60, 35, a))
    # badan (sedikit melebar ke atas)
    badan = [(x0 + 10, lantai), (x1 - 10, lantai), (x1 + 14, lantai - tb), (x0 - 14, lantai - tb)]
    d.polygon(badan, fill=(170, 95, 50, a), outline=(60, 35, 20, a))
    d.rectangle((x0 - 6, lantai - tb, x1 + 6, lantai - tb + 22), fill=MERAH_GADANG + (a,))
    for i in range(int(w / 26)):
        x = x0 + 4 + i * 26
        d.polygon([(x, lantai - tb + 22), (x + 13, lantai - tb + 4), (x + 26, lantai - tb + 22)],
                  fill=EMAS + (a,))
    d.rectangle((x0 + 10, lantai - 18, x1 - 10, lantai), fill=MERAH_GADANG + (a,))
    if pintu:
        for i in range(4):
            px = lerp(x0 + w * 0.14, x1 - w * 0.14, i / 3)
            d.rectangle((px - 22, lantai - tb + 40, px + 22, lantai - 26), fill=(95, 50, 25, a),
                        outline=(50, 25, 10, a), width=3)
    # atap melengkung dengan gonjong
    atas = lantai - tb
    xs = [lerp(x0 - 60, x1 + 60, i / (gonjong - 1)) for i in range(gonjong)]
    tinggi_ujung = w * 0.36
    lengkung_pts = []
    for j in range(gonjong - 1):
        xa, xb = xs[j], xs[j + 1]
        for s in range(13):
            f = s / 12
            x = lerp(xa, xb, f)
            y = atas - tinggi_ujung + math.sin(f * math.pi) * tinggi_ujung * 0.55
            lengkung_pts.append((x, y))
    bawah_kanan = [(x1 + 30, atas + 6), (x0 - 30, atas + 6)]
    d.polygon(lengkung_pts + bawah_kanan, fill=IJUK + (a,), outline=(20, 12, 8, a))
    for x in xs:
        d.line((x, atas - tinggi_ujung, x + (8 if x > cx else -8), atas - tinggi_ujung - 34), fill=(30, 20, 12, a),
               width=7)
        d.ellipse((x - 5, atas - tinggi_ujung - 6, x + 5, atas - tinggi_ujung + 4), fill=EMAS + (a,))


def surau(d, cx, lantai, s=1.0, alpha=1.0):
    """Surau kayu kecil dengan atap tumpang."""
    a = int(255 * alpha)
    if a <= 2:
        return
    w = 200 * s
    d.rectangle((cx - w / 2, lantai - 110 * s, cx + w / 2, lantai), fill=(160, 120, 70, a), outline=(60, 40, 20, a),
                width=4)
    d.rectangle((cx - 26 * s, lantai - 80 * s, cx + 26 * s, lantai), fill=(90, 55, 30, a))
    for i, (lb, tg) in enumerate(((1.25, 60), (0.9, 55), (0.5, 50))):
        y = lantai - 110 * s - i * 50 * s
        d.polygon([(cx - w / 2 * lb - 20, y), (cx + w / 2 * lb + 20, y), (cx + w / 2 * lb * 0.55, y - tg * s),
                   (cx - w / 2 * lb * 0.55, y - tg * s)], fill=(70, 50, 35, a), outline=(30, 20, 10, a))
    d.line((cx, lantai - 260 * s, cx, lantai - 300 * s), fill=(40, 30, 20, a), width=5)


def latar_kertas(seed=33):
    return se.latar_tekstur(W, H, seed, warna=(226, 208, 166)).convert("RGBA")


print("  menyiapkan latar kertas...")
_KERTAS = latar_kertas()


# ------------------------------------------------------------------ adegan

def a_hook(c):
    kamera = se.kamera_antara(cam(LEBAR, -0.5, 101.5, 1.05), cam(LEBAR, -0.4, 101.0, 1.2), c.p(0.0, 1.0))
    img, _ = peta(LEBAR, kamera)
    se.tint(img, (15, 10, 5), 0.25)
    x, y = layar(LEBAR, kamera, MINANG)
    se.glow(img, x, y, 170, (255, 140, 60), 1.4)
    rute_rantau(img, kamera, 0.45 + 0.55 * c.p(0.0, 0.35), c.t)
    d = ImageDraw.Draw(img, "RGBA")
    a1 = 1 - c.p(0.62, 0.68)
    s = 0.9 + 0.1 * back_out(c.t / 0.35)
    angka_besar(d, (540, 520), "Rp 20 TRILIUN", int(132 * s), EMAS, alpha=a1, stroke_warna=(40, 20, 5))
    angka_besar(d, (540, 660), "DARI PERANTAU", int(92 * s), PUTIH, alpha=a1)
    se.kartu(img, 540, 1180, "Wamendagri: potensi dana rantau Minang", "Kompas, 3 November 2026", MERAH,
             alpha=c.p(0.22, 0.3) * (1 - c.p(0.62, 0.68)), tiang=False)
    b = c.p(0.66, 0.74)
    if b > 0:
        sk = back_out((c.t / c.d - 0.66) / 0.1)
        angka_besar(d, (540, 560), "KENAPA ORANG MINANG", int(68 * sk) + 1, PUTIH, alpha=b)
        angka_besar(d, (540, 690), "MERANTAU?", int(140 * sk) + 1, EMAS, alpha=b, stroke_warna=(40, 20, 5))
        se.kartu(img, 540, 1180, "Jawabannya ada di rumahnya sendiri", "", (90, 60, 35), alpha=c.p(0.84, 0.9),
                 tiang=False)
    hdr(img, alpha=c.p(0.5, 0.62))
    return img


def gunung_ikon(d, x, y, s=1.0, asap=0.0, t=0.0):
    d.polygon([(x - 70 * s, y + 40 * s), (x - 14 * s, y - 50 * s), (x + 14 * s, y - 50 * s), (x + 70 * s, y + 40 * s)],
              fill=(110, 90, 70, 235), outline=(50, 35, 20, 255))
    if asap > 0:
        for i in range(4):
            r = (16 + i * 9) * s
            yy = y - 60 * s - i * 26 * s - (t * 10 % 26)
            d.ellipse((x - r + i * 8, yy - r, x + r + i * 8, yy + r), fill=(235, 230, 225, int(150 * asap)))


def danau(d, kamera):
    for (lat, lon), rlon, rlat in DANAU:
        x, y = layar(DEKAT, kamera, (lat, lon))
        rx, ry = rlon * DEKAT.skala * kamera.zoom, rlat * DEKAT.skala * kamera.zoom
        d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(60, 100, 150, 255), outline=(30, 40, 60, 255), width=3)


def a_darek(c):
    kamera = se.kamera_antara(cam(DEKAT, -0.36, 100.47, 1.9), cam(DEKAT, -0.37, 100.48, 2.2), c.p(0.0, 1.0))
    img, d = peta(DEKAT, kamera)
    danau(d, kamera)
    k = c.t / c.d
    for i, (nama, ll, warna) in enumerate(LUHAK):
        a = c.p(0.42 + i * 0.14, 0.5 + i * 0.14)
        if a <= 0:
            continue
        x, y = layar(DEKAT, kamera, ll)
        r = 120 * back_out((k - 0.42 - i * 0.14) / 0.1)
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=tuple(warna) + (90,), outline=tuple(warna) + (255,),
                   width=6)
        se.tempel(img, lap, a)
        d = ImageDraw.Draw(img, "RGBA")
        label(d, (x, y), nama, 44, TINTA, a)
    x, y = layar(DEKAT, kamera, MARAPI)
    gunung_ikon(d, x, y, 1.0, c.p(0.05, 0.15), c.t)
    label(d, (x, y + 75), "Gn. Marapi", 38, TINTA, c.p(0.1, 0.18))
    se.kartu(img, 540, 470, "DAREK", "ranah asal orang Minang", MERAH, alpha=c.p(0.18, 0.26), tiang=False,
             skala=back_out((k - 0.18) / 0.1))
    se.kartu(img, 540, 600, "Luhak nan Tigo", "tiga luhak inti", (90, 60, 35), alpha=c.p(0.4, 0.48), tiang=False)
    hdr(img, "Kampung asal")
    return img


def a_rantau(c):
    kamera = se.kamera_antara(cam(DEKAT, -0.4, 100.55, 1.3), cam(DEKAT, -0.4, 100.75, 0.9), c.p(0.0, 0.3))
    img, d = peta(DEKAT, kamera)
    danau(d, kamera)
    # darek disorot, sisanya diberi warna rantau
    x, y = layar(DEKAT, kamera, (-0.35, 100.5))
    r = 0.33 * DEKAT.skala * kamera.zoom
    lap = Image.new("RGBA", (W, H), (230, 170, 40, 70))
    dl = ImageDraw.Draw(lap)
    dl.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=(0, 0, 0, 0), outline=(200, 52, 44, 255), width=6)
    se.tempel(img, lap, c.p(0.05, 0.15))
    d = ImageDraw.Draw(img, "RGBA")
    label(d, (x, y), "DAREK", 50, MERAH, c.p(0.05, 0.15), font="judul")
    # ke pesisir barat
    for i, (nama, ll) in enumerate(PESISIR):
        k = c.p(0.28 + i * 0.05, 0.48 + i * 0.05)
        ujung = layar(DEKAT, kamera, ll)
        se.garis_putus(d, lengkung((x, y), ujung, 0.1), k, MERAH, tebal=7)
        if k >= 1:
            titik(d, *ujung, EMAS, 11, 1.0)
            label(d, (ujung[0] + 90, ujung[1] + 6), nama, 36, TINTA)
    # menyusuri sungai ke timur
    for i, (nama, s_) in enumerate(SUNGAI_TIMUR):
        pts = se.halus([layar(DEKAT, kamera, ll) for ll in s_], 2)
        k = c.p(0.5 + i * 0.05, 0.8 + i * 0.05)
        d.line(pts, fill=AIR + (230,), width=8, joint="curve")
        se.garis_putus(d, pts, k, MERAH, tebal=7)
        lx, ly = layar(DEKAT, kamera, s_[2])
        label(d, (lx, ly - 40), nama, 34, BIRU, c.p(0.55 + i * 0.05, 0.62 + i * 0.05))
    label(d, (230, 1000), "pesisir barat", 40, TINTA, c.p(0.34, 0.42))
    se.kartu(img, 540, 470, "RANTAU", "tanah di luar darek", (200, 130, 30), alpha=c.p(0.12, 0.2), tiang=False,
             skala=back_out((c.t / c.d - 0.12) / 0.1))
    se.kartu(img, 540, 1270, "Awalnya: membuka kampung baru", "", (90, 60, 35), alpha=c.p(0.22, 0.3), tiang=False)
    hdr(img, "Darek & rantau")
    return img


def a_malaya(c):
    kamera = se.kamera_antara(cam(LEBAR, 0.2, 100.8, 1.4), cam(LEBAR, 1.4, 101.4, 1.75), c.p(0.0, 0.5))
    img, d = peta(LEBAR, kamera)
    asal = layar(LEBAR, kamera, PAGARUYUNG)
    tuju = layar(LEBAR, kamera, KOTA_RANTAU["Seremban"])
    label(d, layar(LEBAR, kamera, (3.3, 100.9)), "Selat Malaka", 40, (220, 230, 240), c.p(0.1, 0.2), font="tangan")
    k = c.p(0.12, 0.5)
    pts = lengkung(asal, tuju, -0.2)
    se.garis_putus(d, pts, k, MERAH, tebal=9)
    titik(d, *asal, MERAH, 15)
    label(d, (asal[0] + 10, asal[1] + 50), "Pagaruyung", 40, TINTA)
    if k >= 1:
        titik(d, *tuju, EMAS, 14, 1.0, (c.t * 0.8) % 1)
    se.kartu(img, 540, 450, "Raja Melewar · tahun 1773", "didatangkan dari Pagaruyung", MERAH, alpha=c.p(0.45, 0.53),
             tiang=False, skala=back_out((c.t / c.d - 0.45) / 0.1))
    a = c.p(0.68, 0.76)
    if a > 0:
        lx, ly = tuju
        se.kartu(img, clamp(lx, 300, 780), ly - 30, "NEGERI SEMBILAN", "kini negara bagian Malaysia", (40, 110, 70),
                 alpha=a, skala=back_out((c.t / c.d - 0.68) / 0.1))
    hdr(img, "Sampai nyeberang laut")
    return img


def dokumen(img, x0, y0, x1, y1, alpha=1.0):
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), fill=(0, 0, 0, 90))
    d.rectangle((x0, y0, x1, y1), fill=(245, 238, 215, 255), outline=(110, 90, 60, 255), width=4)
    d.text(((x0 + x1) / 2, y0 + 60), "VOLKSTELLING 1930", font=se.font("judul", 52), fill=TINTA, anchor="mm")
    d.text(((x0 + x1) / 2, y0 + 112), "sensus penduduk Hindia Belanda", font=se.font("tangan_tipis", 32),
           fill=(90, 70, 50), anchor="mm")
    for i in range(7):
        y = y0 + 170 + i * 42
        d.line((x0 + 50, y, x1 - 50, y), fill=(150, 130, 100, 160), width=3)
        d.line((x0 + 50 + 330, y - 20, x0 + 50 + 330, y + 20), fill=(150, 130, 100, 120), width=2)
    se.tempel(img, lap, alpha)


def a_sensus(c):
    img = _KERTAS.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 430), "Nah, ini yang bikin kaget…", 52, MERAH, nama_font="caption", stroke=6,
            stroke_warna=PUTIH, alpha=c.p(0.0, 0.05) * (1 - c.p(0.12, 0.16)))
    dokumen(img, 140, 480, 940, 820, c.p(0.1, 0.18))
    d = ImageDraw.Draw(img, "RGBA")
    # titik-titik orang menyebar keluar kampung
    rng = random.Random(7)
    n = int(160 * c.p(0.3, 0.7))
    for i in range(n):
        ang = rng.uniform(0, math.pi * 2)
        jarak = rng.uniform(60, 420) * clamp((c.t / c.d - 0.35 - i * 0.001) * 3)
        x = 540 + math.cos(ang) * jarak * 1.1
        y = 1080 + math.sin(ang) * jarak * 0.35
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(200, 52, 44, 230))
    rumah_gadang(d, 540, 1110, 220, c.p(0.3, 0.38), pintu=False)
    jml = int(200000 * c.p(0.4, 0.62))
    if c.p(0.4, 0.45) > 0:
        angka_besar(d, (540, 900), "> " + f"{jml:,}".replace(",", "."), 120, MERAH, c.p(0.4, 0.45), PUTIH)
    se.kartu(img, 540, 1280, "orang Minang di luar Sumatra Barat", "", (90, 60, 35), alpha=c.p(0.66, 0.74),
             tiang=False, skala=back_out((c.t / c.d - 0.66) / 0.1))
    hdr(img, "Di luar kampungnya")
    return img


TOKOH = [("Haji Agus Salim", "Koto Gadang"), ("Mohammad Hatta", "Bukittinggi"), ("Tan Malaka", "Lima Puluh Kota"),
         ("Sutan Sjahrir", "Padang Panjang"), ("Buya Hamka", "Maninjau")]


def a_tokoh(c):
    kamera = Kamera(*cam(LEBAR, -1.0, 102.5, 1.0))
    img, _ = peta(LEBAR, kamera)
    rute_rantau(img, kamera, 1.0, c.t, alpha=0.55)
    se.tint(img, (15, 10, 5), 0.45)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 440), "Lahir di ranah, besar di rantau", 50, EMAS, nama_font="caption", stroke=6,
            stroke_warna=(30, 15, 5), alpha=c.p(0.0, 0.08))
    for i, (nama, asal) in enumerate(TOKOH):
        t0 = 0.14 + i * 0.1
        se.kartu(img, 540, 580 + i * 140, nama, asal, MERAH if i % 2 else (40, 110, 70), alpha=c.p(t0, t0 + 0.05),
                 tiang=False, skala=back_out((c.t / c.d - t0) / 0.08), lebar=560)
    hdr(img, "Tokoh bangsa dari rantau")
    return img


def papan_rm(d, cx, cy, alpha=1.0, s=1.0):
    a = int(255 * alpha)
    if a <= 2:
        return
    w, h = 720 * s, 130 * s
    # atap gonjong kecil di atas papan
    pts = []
    for j in range(3):
        xa, xb = lerp(cx - w / 2 - 20, cx + w / 2 + 20, j / 3), lerp(cx - w / 2 - 20, cx + w / 2 + 20, (j + 1) / 3)
        for k in range(11):
            f = k / 10
            pts.append((lerp(xa, xb, f), cy - h / 2 - 90 * s + math.sin(f * math.pi) * 50 * s))
    d.polygon(pts + [(cx + w / 2, cy - h / 2), (cx - w / 2, cy - h / 2)], fill=IJUK + (a,))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 16, fill=(200, 52, 44, a),
                        outline=(250, 200, 80, a), width=6)
    d.text((cx, cy), "RUMAH MAKAN PADANG", font=se.font("caption", int(56 * s)), fill=(255, 235, 150, a), anchor="mm")


def a_rumahmakan(c):
    kamera = se.kamera_antara(cam(LEBAR, -2.0, 103.5, 1.0), cam(LEBAR, -2.5, 104.5, 0.97), c.p(0.0, 1.0))
    img, d = peta(LEBAR, kamera)
    rng = random.Random(3)
    for i, ll in enumerate(KOTA_RM):
        a = c.p(0.12 + i * 0.022, 0.16 + i * 0.022)
        x, y = layar(LEBAR, kamera, ll)
        if a > 0 and 0 < x < W and 380 < y < 1350:
            r = 16 * back_out((c.t / c.d - 0.12 - i * 0.022) / 0.05)
            if r < 4:
                continue
            d.rounded_rectangle((x - r * 1.4, y - r, x + r * 1.4, y + r), 3, fill=(200, 52, 44, int(255 * a)),
                                outline=(250, 200, 80, int(255 * a)), width=3)
            rng.random()
    papan_rm(d, 540, 520, c.p(0.05, 0.13), 0.9 + 0.1 * back_out((c.t / c.d - 0.05) / 0.1))
    se.kartu(img, 540, 1240, "Tempat singgah perantau baru", "", (90, 60, 35), alpha=c.p(0.6, 0.68), tiang=False,
             skala=back_out((c.t / c.d - 0.6) / 0.1))
    hdr(img, "Jejak paling enak")
    return img


def orang(d, x, y, warna, alpha=1.0, r=13):
    a = int(255 * alpha)
    d.ellipse((x - r, y - r * 2.6, x + r, y - r * 0.6), fill=tuple(warna) + (a,))
    d.rounded_rectangle((x - r * 1.1, y - r * 0.4, x + r * 1.1, y + r * 1.8), 8, fill=tuple(warna) + (a,))


def a_jawaban(c):
    img = _KERTAS.copy()
    d = ImageDraw.Draw(img, "RGBA")
    k = c.t / c.d
    d.rectangle((0, 1150, W, 1320), fill=HIJAU_SAWAH + (160,))
    for i in range(10):
        d.line((i * 120, 1150, i * 120 - 60, 1320), fill=(60, 100, 40, 120), width=3)
    angka_besar(d, (540, 430), "JAWABANNYA:", 80, EMAS, c.p(0.0, 0.06), (40, 20, 5))
    cx, lantai = 430, 1010
    rumah_gadang(d, cx, lantai, 560, c.p(0.0, 0.08))
    label(d, (cx, lantai + 105), "rumah gadang", 40, TINTA, c.p(0.06, 0.14))
    # bilik untuk perempuan
    b = c.p(0.3, 0.38)
    if b > 0:
        for i in range(4):
            px = lerp(cx - 560 * 0.36, cx + 560 * 0.36, i / 3)
            orang(d, px, lantai - 50, PINK, b, 11)
    se.kartu(img, 540, 560, "Garis keturunan ibu", "rumah & sawah pusaka ke anak perempuan", PINK, alpha=c.p(0.16, 0.24)
             * (1 - c.p(0.6, 0.65)), tiang=False, skala=back_out((k - 0.16) / 0.1))
    # anak laki-laki pindah ke surau
    s = c.p(0.58, 0.66)
    surau(d, 900, 1130, 0.85, s)
    label(d, (900, 1170), "surau", 40, TINTA, s)
    jalan = c.p(0.7, 0.92)
    if s > 0:
        for i in range(3):
            x = lerp(cx + 120 + i * 40, 860 + i * 30, jalan)
            y = lerp(lantai - 50, 1120, jalan) - abs(math.sin(c.t * 8 + i)) * 10 * (0 < jalan < 1)
            orang(d, x, y, BIRU, s, 11)
    se.kartu(img, 540, 560, "Anak laki-laki remaja", "tidurnya di surau", BIRU, alpha=c.p(0.66, 0.72), tiang=False,
             skala=back_out((k - 0.66) / 0.1))
    hdr(img, "Kenapa merantau?")
    return img


PEPATAH = ["Karatau madang di hulu,", "babuah babungo balun.", "Marantau bujang dahulu,", "di rumah baguno balun."]


def a_pepatah(c):
    kamera = Kamera(*cam(LEBAR, -0.6, 101.5, 1.1))
    img, _ = peta(LEBAR, kamera)
    rute_rantau(img, kamera, c.p(0.0, 1.0), c.t, alpha=0.8)
    se.tint(img, (10, 6, 0), 0.35)
    se.panel(img, (80, 430, 1000, 1150), alpha=c.p(0.0, 0.06))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 500), "Pepatah Minang", 44, (150, 40, 30), nama_font="judul", alpha=c.p(0.02, 0.08))
    for i, baris in enumerate(PEPATAH):
        t0 = 0.06 + i * 0.13
        se.teks(d, (540, 600 + i * 92), baris, 52, TINTA, nama_font="tangan", alpha=c.p(t0, t0 + 0.06))
    a = c.p(0.68, 0.76)
    se.teks(d, (540, 1000), "Di kampung belum berguna,", 42, (90, 70, 50), nama_font="tangan_tipis", alpha=a)
    se.teks(d, (540, 1060), "merantaulah dulu.", 50, MERAH, nama_font="caption", alpha=a)
    hdr(img, "Kata pepatah")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(LEBAR, -1.0, 102.5, 1.0))
    img, _ = peta(LEBAR, kamera)
    rute_rantau(img, kamera, 1.0, c.t, alpha=0.6)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 450, 990, 1080), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 540), "Merantau bukan kabur", 56, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 615), "dari kampung", 40, (90, 70, 50), alpha=a)
        b = a * c.p(0.25, 0.33)
        rumah_gadang(d, 540, 900, 360, b, pintu=False)
        se.teks(d, (540, 1020), "Pulang bawa ilmu & rezeki", 46, (170, 30, 20), nama_font="caption", alpha=b)
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
    Adegan("hook", "Dua puluh triliun rupiah, dari para perantau. Segitu dana rantau Minang, kata Wamendagri. "
                   "Tapi kenapa sih orang Minang suka merantau? Jawabannya, ada di rumahnya sendiri.", a_hook,
           transisi=False),
    Adegan("darek", "Kampung asalnya di kaki Gunung Marapi, namanya darek. Ada tiga luhak: Tanah Datar, Agam, "
                    "dan Lima Puluh Kota.", a_darek),
    Adegan("rantau", "Di luar darek, itulah rantau. Awalnya, merantau berarti membuka kampung baru, di pesisir dan "
                     "tepi sungai.", a_rantau, transisi=False),
    Adegan("malaya", "Lama-lama, rantaunya nyeberang Selat Malaka. Tahun tujuh belas tujuh puluh tiga, perantau di "
                     "sana mengangkat raja dari Pagaruyung. Lahirlah Negeri Sembilan, di Malaysia.", a_malaya),
    Adegan("sensus", "Nah, ini yang bikin kaget. Sensus tahun sembilan belas tiga puluh mencatat, lebih dari dua "
                     "ratus ribu orang Minang hidup di luar kampungnya.", a_sensus),
    Adegan("tokoh", "Dari rantau, lahir tokoh bangsa. Agus Salim, Hatta, Tan Malaka, Syahrir, Hamka. Semuanya "
                    "perantau.", a_tokoh),
    Adegan("rumahmakan", "Dan jejak paling enaknya? Rumah makan Padang. Ikut menyebar bareng perantau, dan sering jadi "
                         "tempat singgah perantau baru.", a_rumahmakan),
    Adegan("jawaban", "Terus, kenapa merantau? Jawabannya di rumah gadang. Garis keturunannya dari ibu. Rumah dan "
                      "sawah pusaka, buat anak perempuan. Anak laki-laki yang beranjak remaja, tidurnya di surau.",
           a_jawaban),
    Adegan("pepatah", "Makanya ada pepatah. Karatau madang di hulu, babuah babungo balun. Marantau bujang dahulu, di "
                      "rumah baguno balun. Di kampung belum berguna, merantaulah dulu.", a_pepatah),
    Adegan("penutup", "Merantau bukan kabur dari kampung. Pulangnya bawa ilmu, dan rezeki. Follow Ngomongin Sejarah "
                      "buat cerita berikutnya!", a_penutup),
]
