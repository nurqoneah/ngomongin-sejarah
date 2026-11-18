"""Shorts ±88 detik: Kretek — rokok yang dulu dijual sebagai "obat" sesak napas (Kudus, ± 1880-an).

Tren: wacana larangan total vape (industri vape minta perlindungan, MUI, kajian pemerintah; 14–18 November 2026).
Visual: botol apotek + rokok kretek berasap, peta Jawa → Kudus, racikan minyak cengkeh, apotek "rokok cengkeh",
bunyi "kretek-kretek", Nitisemito & Bal Tiga, pabrik 10.000 pekerja, rahasia eugenol (tenggorokan kebas, paru),
larangan rokok cengkeh di AS 2009 + wacana larangan vape, penutup maskot.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Peta, back_out, clamp, lerp

NAMA_FILE = "kretek-obat-sesak-napas-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "SEJARAH KRETEK"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KUNING = (255, 214, 10)
GELAP = (10, 10, 20)
KREM = (247, 236, 208)
KREM_LABEL = (240, 225, 190)
EMAS = (235, 185, 50)
HIJAU_TUA = (30, 110, 60)
BIRU = (30, 80, 150)
COKLAT = (120, 80, 40)
CENGKEH = (92, 45, 25)
TEMBAKAU = (150, 100, 45)
KERTAS = (240, 232, 215)
MERAH_TUA = (150, 30, 25)

# ------------------------------------------------------------------ peta

print("  menyiapkan peta Jawa...")
JAWA = Peta(103.5, 116.5, -18, 4, 100, [], [(-7.2, 107.6, 0.35), (-7.0, 110.4, 0.4), (-7.9, 112.9, 0.35),
                                              (-6.6, 110.9, 0.25), (-0.5, 101.0, 0.5), (-2, 114, 1.0)],
            seed=32, darat=pd.SEMUA)

KUDUS = (-6.80, 110.84)

print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 32, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (20, 10, 6), 0.62)


# ------------------------------------------------------------------ helper

def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def skala_muncul(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


def cam(peta, lat, lon, zoom):
    x, y = peta.px(lat, lon)
    return (x, y, zoom)


def layar(peta, kamera, ll):
    return kamera.layar(*peta.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def stempel(img, isi, cx, cy, s, uk=76, sudut=-8, warna=(210, 30, 30)):
    if s <= 0.01:
        return
    f = se.font("caption", uk)
    lw = int(f.getlength(isi)) + 80
    lap = Image.new("RGBA", (lw, uk + 90), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((10, 10, lw - 10, uk + 80), 22, fill=(247, 236, 208, 210), outline=tuple(warna) + (255,),
                         width=12)
    dl.text((lw / 2, (uk + 90) / 2), isi, font=f, fill=tuple(warna) + (255,), anchor="mm")
    lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, 1.0, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


def kalender(img, cx, cy, bulan, tgl, tahun="", alpha=1.0, s=1.0):
    if alpha <= 0.01 or s <= 0.2:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    w, h = 300 * s, 330 * s
    d.rounded_rectangle((cx - w / 2 + 8, cy - h / 2 + 10, cx + w / 2 + 8, cy + h / 2 + 10), int(18 * s), fill=(0, 0, 0, 100))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(18 * s), fill=(250, 245, 235, 255),
                        outline=(80, 60, 40, 255), width=4)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 84 * s), int(18 * s), fill=MERAH + (255,))
    d.text((cx, cy - h / 2 + 43 * s), bulan, font=se.font("ui", int(32 * s)), fill=PUTIH, anchor="mm")
    d.text((cx, cy + 20 * s), tgl, font=se.font("caption", int(120 * s)), fill=TINTA, anchor="mm")
    if tahun:
        d.text((cx, cy + h / 2 - 34 * s), tahun, font=se.font("ui", int(34 * s)), fill=(150, 30, 25), anchor="mm")
    se.tempel(img, lap, alpha)


def koin(d, x, y, r, alpha=1.0):
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=EMAS + (a,), outline=(130, 90, 10, a), width=max(2, int(r * 0.12)))
    d.ellipse((x - r * 0.65, y - r * 0.65, x + r * 0.65, y + r * 0.65), outline=(170, 120, 20, a),
              width=max(1, int(r * 0.08)))


def asap(img, x, y, t, kuat=1.0, tinggi=500, lebar=1.0, seed=1, warna=(200, 200, 205)):
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    for i in range(26):
        fase = (rng.random() + t * rng.uniform(0.12, 0.22)) % 1.0
        yy = y - fase * tinggi
        xx = x + math.sin(fase * 7 + i) * 26 * lebar + rng.uniform(-30, 30) * lebar * fase
        r = (10 + fase * 70) * lebar * rng.uniform(0.7, 1.2)
        a = int(120 * kuat * (1 - fase))
        d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=tuple(warna) + (a,))
    img.alpha_composite(lap)


def cengkeh(d, x, y, s=1.0, sudut=0.0, alpha=1.0):
    """Sebutir cengkeh: tangkai + kepala 4 kelopak."""
    a = int(255 * alpha)
    c = CENGKEH + (a,)
    ca, sa = math.cos(sudut), math.sin(sudut)

    def P(dx, dy):
        return (x + (dx * ca - dy * sa) * s, y + (dx * sa + dy * ca) * s)

    d.polygon([P(-4, 0), P(4, 0), P(2.5, 46), P(-2.5, 46)], fill=c)
    d.ellipse((P(0, -6)[0] - 9 * s, P(0, -6)[1] - 9 * s, P(0, -6)[0] + 9 * s, P(0, -6)[1] + 9 * s), fill=c)
    for k in (-1, 1):
        px, py = P(k * 10, -2)
        d.ellipse((px - 5 * s, py - 6 * s, px + 5 * s, py + 6 * s), fill=(110, 55, 30, a))


def rokok(img, x0, y0, x1, y1, tebal=36, bara=1.0, t=0.0, alpha=1.0):
    """Rokok kretek lintingan dari (x0,y0) pangkal ke (x1,y1) ujung menyala."""
    if alpha <= 0.01:
        return
    d = ImageDraw.Draw(img, "RGBA")
    a = int(255 * alpha)
    d.line((x0, y0, x1, y1), fill=(60, 40, 25, a), width=tebal + 8)
    d.line((x0, y0, x1, y1), fill=KERTAS + (a,), width=tebal)
    # pangkal cokelat
    k = 0.18
    d.line((x0, y0, lerp(x0, x1, k), lerp(y0, y1, k)), fill=(196, 150, 95, a), width=tebal)
    # bintik cengkeh di kertas
    rng = random.Random(3)
    for i in range(14):
        f = rng.uniform(0.22, 0.92)
        px, py = lerp(x0, x1, f), lerp(y0, y1, f)
        px += rng.uniform(-tebal * 0.3, tebal * 0.3)
        py += rng.uniform(-tebal * 0.3, tebal * 0.3)
        d.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(150, 110, 70, int(a * 0.7)))
    # ujung bara
    d.ellipse((x1 - tebal * 0.55, y1 - tebal * 0.55, x1 + tebal * 0.55, y1 + tebal * 0.55),
              fill=(70, 60, 55, a))
    if bara > 0:
        kedip = 0.8 + 0.2 * math.sin(t * 9)
        se.glow(img, x1, y1, tebal * 1.6, (255, 120, 30), 2.0 * bara * kedip * alpha)
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse((x1 - tebal * 0.38, y1 - tebal * 0.38, x1 + tebal * 0.38, y1 + tebal * 0.38),
                  fill=(255, 140 + int(60 * kedip), 40, int(a * bara)))


def botol(img, cx, by, s=1.0, isi="OBAT", sub="", alpha=1.0, sudut=0):
    """Botol apotek kuno; (cx, by) = dasar botol."""
    if alpha <= 0.01:
        return
    bw, bh = int(220 * s), int(330 * s)
    lap = Image.new("RGBA", (bw + 60, bh + 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    ox = 30
    leher = bw * 0.32
    d.rounded_rectangle((ox + 8, 120 + 10, ox + bw + 8, 120 + bh + 10), int(40 * s), fill=(0, 0, 0, 90))
    d.rounded_rectangle((ox, 120, ox + bw, 120 + bh), int(40 * s), fill=(120, 70, 35, 235), outline=(50, 30, 15, 255),
                        width=5)
    d.rectangle((ox + bw / 2 - leher / 2, 50, ox + bw / 2 + leher / 2, 130), fill=(120, 70, 35, 235),
                outline=(50, 30, 15, 255), width=5)
    d.rounded_rectangle((ox + bw / 2 - leher / 2 - 10, 10, ox + bw / 2 + leher / 2 + 10, 60), 10,
                        fill=(170, 120, 70, 255), outline=(60, 40, 20, 255), width=4)
    # kilau
    d.rounded_rectangle((ox + 22 * s, 150, ox + 44 * s, 120 + bh - 40), 10, fill=(255, 255, 255, 60))
    # label
    lx0, ly0, lx1, ly1 = ox + 22 * s, 120 + bh * 0.3, ox + bw - 22 * s, 120 + bh * 0.78
    d.rectangle((lx0, ly0, lx1, ly1), fill=(245, 232, 200, 255), outline=(110, 30, 25, 255), width=4)
    f1 = se.font("caption", int(44 * s))
    d.text((ox + bw / 2, (ly0 + ly1) / 2 - (18 * s if sub else 0)), isi, font=f1, fill=(140, 25, 20), anchor="mm")
    if sub:
        d.text((ox + bw / 2, (ly0 + ly1) / 2 + 30 * s), sub, font=se.font("ui", int(24 * s)), fill=(90, 50, 25),
               anchor="mm")
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(by - lap.height + 10)))


def paru(d, cx, cy, s=1.0, kelabu=0.0, alpha=1.0, kebas=0.0):
    """Diagram tenggorokan + paru-paru sederhana. (cx, cy) = pusat paru."""
    a = int(255 * alpha)
    sehat = (226, 120, 120)
    abu = (95, 90, 90)
    c = tuple(int(lerp(sehat[i], abu[i], kelabu)) for i in range(3))
    garis = (90, 30, 30, a)
    # trakea
    tw = 34 * s
    top = cy - 430 * s
    tr = (110, 160, 230) if kebas > 0 else (235, 170, 160)
    trc = tuple(int(lerp(235 if i == 0 else (170 if i == 1 else 160), tr[i], kebas)) for i in range(3))
    d.rounded_rectangle((cx - tw, top, cx + tw, cy - 110 * s), int(14 * s), fill=trc + (a,), outline=garis, width=5)
    for k in range(7):
        yy = top + 30 * s + k * 40 * s
        d.line((cx - tw + 6, yy, cx + tw - 6, yy), fill=(150, 80, 80, int(a * 0.6)), width=4)
    # cabang
    d.line((cx, cy - 115 * s, cx - 110 * s, cy - 40 * s), fill=garis, width=int(22 * s))
    d.line((cx, cy - 115 * s, cx + 110 * s, cy - 40 * s), fill=garis, width=int(22 * s))
    # dua lobus
    for k in (-1, 1):
        x0 = cx + k * 40 * s
        x1 = cx + k * 300 * s
        bx0, bx1 = sorted((x0, x1))
        d.ellipse((bx0, cy - 190 * s, bx1, cy + 250 * s), fill=c + (a,), outline=garis, width=6)
        for j in range(4):
            yy = cy - 60 * s + j * 70 * s
            d.arc((bx0 + 40 * s, yy - 40 * s, bx1 - 40 * s, yy + 40 * s), 20, 160, fill=(150, 70, 70, int(a * 0.5)),
                  width=4)


def gigi(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.polygon([(x - 50 * s, y - 60 * s), (x - 30 * s, y - 80 * s), (x, y - 70 * s), (x + 30 * s, y - 80 * s),
               (x + 50 * s, y - 60 * s), (x + 42 * s, y), (x + 28 * s, y + 70 * s), (x + 12 * s, y + 70 * s),
               (x, y + 10 * s), (x - 12 * s, y + 70 * s), (x - 28 * s, y + 70 * s), (x - 42 * s, y)],
              fill=(250, 250, 245, a), outline=(90, 90, 100, a))


def jam_dinding(d, x, y, r, t=0.0, alpha=1.0):
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 245, 230, a), outline=(110, 70, 30, a), width=max(4, int(r * 0.12)))
    for k in range(12):
        ang = k * math.pi / 6
        d.line((x + math.cos(ang) * r * 0.75, y + math.sin(ang) * r * 0.75, x + math.cos(ang) * r * 0.88,
                y + math.sin(ang) * r * 0.88), fill=(60, 40, 20, a), width=3)
    ang = t * 2
    d.line((x, y, x + math.cos(ang) * r * 0.7, y + math.sin(ang) * r * 0.7), fill=(30, 20, 10, a), width=5)
    d.line((x, y, x + math.cos(ang / 12 - 1) * r * 0.45, y + math.sin(ang / 12 - 1) * r * 0.45), fill=(30, 20, 10, a),
           width=7)


def sepeda(d, x, y, s=1.0, t=0.0, alpha=1.0):
    a = int(255 * alpha)
    c = (40, 40, 45, a)
    r = 55 * s
    for wx in (x - 80 * s, x + 80 * s):
        d.ellipse((wx - r, y - r, wx + r, y + r), outline=c, width=max(3, int(7 * s)))
        for k in range(4):
            ang = t * 4 + k * math.pi / 4
            d.line((wx - math.cos(ang) * r, y - math.sin(ang) * r, wx + math.cos(ang) * r, y + math.sin(ang) * r),
                   fill=(90, 90, 95, a), width=2)
    pts = [(x - 80 * s, y), (x - 10 * s, y - 70 * s), (x + 55 * s, y - 70 * s), (x + 80 * s, y), (x, y),
           (x - 10 * s, y - 70 * s)]
    d.line(pts, fill=(170, 30, 25, a), width=max(3, int(8 * s)), joint="curve")
    d.line((x, y, x + 55 * s, y - 70 * s), fill=(170, 30, 25, a), width=max(3, int(8 * s)))
    d.line((x - 18 * s, y - 92 * s, x + 8 * s, y - 92 * s), fill=c, width=max(3, int(9 * s)))
    d.line((x + 55 * s, y - 70 * s, x + 62 * s, y - 100 * s, x + 82 * s, y - 104 * s), fill=c, width=max(3, int(6 * s)))


def bungkus_baltiga(img, cx, cy, s=1.0, alpha=1.0, sudut=-4):
    """Bungkus rokok ilustrasi 'BAL TIGA' (bukan replika logo asli)."""
    if alpha <= 0.01:
        return
    pw, ph = int(360 * s), int(440 * s)
    lap = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rounded_rectangle((26, 30, pw + 26, ph + 30), 18, fill=(0, 0, 0, 110))
    d.rounded_rectangle((14, 14, pw + 14, ph + 14), 18, fill=(200, 45, 35, 255), outline=(90, 20, 15, 255), width=7)
    d.rounded_rectangle((34, 34, pw - 6, ph - 6), 12, outline=(245, 215, 120, 255), width=4)
    for i, (dx, dy) in enumerate(((-0.22, 0.06), (0.22, 0.06), (0.0, -0.16))):
        bx, by = pw / 2 + 14 + dx * pw, ph * 0.46 + dy * ph
        r = 48 * s
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=(245, 225, 160, 255), outline=(90, 20, 15, 255), width=5)
    d.text((pw / 2 + 14, ph * 0.8), "BAL TIGA", font=se.font("caption", int(64 * s)), fill=(255, 240, 200),
           anchor="mm", stroke_width=4, stroke_fill=(90, 20, 15))
    d.text((pw / 2 + 14, 60 * s), "KRETEK · KOEDOES", font=se.font("ui", int(26 * s)), fill=(255, 235, 190), anchor="mm")
    lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def orang(d, x, y, s=1.0, warna=(60, 45, 35), alpha=1.0):
    """Siluet orang sederhana tanpa wajah (titik kepala + badan)."""
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    d.ellipse((x - 9 * s, y - 50 * s, x + 9 * s, y - 32 * s), fill=c)
    d.rounded_rectangle((x - 12 * s, y - 30 * s, x + 12 * s, y), int(6 * s) + 1, fill=c)


def vape(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.rounded_rectangle((x - 45 * s, y - 120 * s, x + 45 * s, y + 120 * s), int(22 * s), fill=(60, 70, 90, a),
                        outline=(20, 25, 35, a), width=5)
    d.rounded_rectangle((x - 22 * s, y - 175 * s, x + 22 * s, y - 115 * s), int(10 * s), fill=(150, 170, 200, a),
                        outline=(20, 25, 35, a), width=4)
    d.ellipse((x - 14 * s, y - 20 * s, x + 14 * s, y + 8 * s), fill=(90, 200, 255, a))
    d.rounded_rectangle((x - 30 * s, y + 40 * s, x + 30 * s, y + 90 * s), 8, fill=(40, 45, 60, a))


def coret_besar(d, box, k, alpha=1.0):
    if k <= 0:
        return
    x0, y0, x1, y1 = box
    a = int(255 * alpha)
    k1, k2 = clamp(k * 2), clamp(k * 2 - 1)
    d.line((x0, y0, lerp(x0, x1, k1), lerp(y0, y1, k1)), fill=(220, 30, 25, a), width=16)
    if k2 > 0:
        d.line((x1, y0, lerp(x1, x0, k2), lerp(y0, y1, k2)), fill=(220, 30, 25, a), width=16)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 950, 520, (170, 70, 20), 1.2)
    # botol obat + rokok kretek berasap (sudah tampil di frame 0)
    botol(img, 300, 1250, 1.25, "OBAT", "sesak napas", sudut=6)
    asap(img, 840, 830, c.t + 2, 1.0, tinggi=330, lebar=1.0, seed=2)
    rokok(img, 470, 1180, 830, 850, tebal=46, bara=1.0, t=c.t)
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(4)
    for i in range(11):
        fase = (rng.random() + c.t * rng.uniform(0.2, 0.35)) % 1
        x = rng.uniform(80, 1000)
        y = lerp(620, 1300, fase)
        cengkeh(d, x, y, rng.uniform(1.0, 1.5), c.t * rng.uniform(1, 2) + i, 0.9 * (1 - fase * 0.4))
    se.teks(d, (540, 410), "DULU DIJUAL", 118, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 535), "SEBAGAI OBAT!", 120, KUNING, nama_font="caption", stroke=10, stroke_warna=GELAP)
    stempel(img, "KUDUS, 1880-an", 790, 1240, 0.72, uk=56, sudut=-9)
    se.kartu(img, 540, 1335, "Vape mau dilarang total?", "lagi rame dikaji", HIJAU_TUA,
             alpha=c.p(0.17, 0.25), tiang=False, skala=skala_muncul(c, 0.17))
    a = c.p(0.66, 0.73)
    if a > 0:
        se.panel(img, (90, 760, 990, 990), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 835), "Rahasia cengkeh", 60, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 920), "yang bikin \"obat\" ini menipu", 46, TINTA, nama_font="caption", alpha=c.p(0.72, 0.78))
    return img


def a_kudus(c):
    kamera = se.kamera_antara(cam(JAWA, -7.3, 109.9, 0.9), cam(JAWA, -7.05, 110.6, 1.6), c.p(0.0, 0.5))
    img = se.render_peta(JAWA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, layar(JAWA, kamera, (-5.6, 110.6)), "Laut Jawa", 38, (220, 235, 255), alpha=0.85)
    kx, ky = layar(JAWA, kamera, KUDUS)
    a = c.p(0.2, 0.3)
    if a > 0:
        se.glow(img, kx, ky, 110, (255, 200, 80), 1.4 * a)
        d = ImageDraw.Draw(img, "RGBA")
        r = 16 + 4 * math.sin(c.t * 5)
        d.ellipse((kx - r, ky - r, kx + r, ky + r), fill=(255, 200, 60, int(255 * a)), outline=PUTIH + (int(255 * a),),
                  width=4)
        label(d, (kx + 10, ky + 50), "Kudus", 44, alpha=a)
    se.kartu(img, kx, ky - 30, "Haji Djamhari", "warga Kudus, ± 1880-an", COKLAT, alpha=c.p(0.42, 0.5),
             skala=skala_muncul(c, 0.42))
    a = c.p(0.66, 0.74)
    if a > 0:
        se.panel(img, (240, 920, 840, 1310), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        denyut = 1 + 0.05 * math.sin(c.t * 9)
        paru(d, 540, 1150, 0.33 * denyut, 0.0, a)
        se.teks(d, (700, 1000), "SESAK!", 50, (190, 30, 20), nama_font="caption", stroke=4, stroke_warna=KREM,
                alpha=a * (0.6 + 0.4 * abs(math.sin(c.t * 4))))
    hdr(img, "Jawa Tengah, akhir abad ke-19")
    return img


LANGKAH = [("rajang", 0.42), ("campur", 0.54), ("linting", 0.66), ("isap", 0.78)]


def a_racik(c):
    img = LATAR.copy()
    # bagian atas: minyak cengkeh dioles ke dada
    a_atas = 1 - c.p(0.36, 0.42) * 0.55
    botol(img, 330, 860, 0.9, "MINYAK", "cengkeh", alpha=a_atas, sudut=-28)
    d = ImageDraw.Draw(img, "RGBA")
    # dada (siluet sederhana)
    kul, gar = (205, 160, 120, int(255 * a_atas)), (110, 70, 40, int(255 * a_atas))
    d.polygon([(560, 600), (640, 545), (820, 545), (900, 600), (870, 880), (590, 880)], fill=kul, outline=gar)
    d.rectangle((700, 490, 760, 550), fill=kul)
    d.ellipse((665, 400, 795, 520), fill=kul, outline=gar, width=5)
    d.arc((620, 590, 720, 660), 200, 340, fill=gar, width=4)
    d.arc((740, 590, 840, 660), 200, 340, fill=gar, width=4)
    # tetesan
    for i in range(5):
        f = ((c.t * 0.9 + i * 0.2) % 1.0)
        if c.p(0.03, 0.08) > 0 and c.t / c.d < 0.38:
            x = lerp(430, 650, f)
            y = lerp(650, 700, f) - math.sin(f * math.pi) * 90
            d.ellipse((x - 9, y - 12, x + 9, y + 12), fill=(200, 140, 40, 230))
    oles = c.p(0.08, 0.3)
    if oles > 0:
        d.ellipse((620, 600, 620 + 220 * oles, 740), fill=(220, 160, 60, int(110 * a_atas)))
    if c.p(0.22, 0.28) > 0:
        se.teks(d, (730, 940), "LEGA…", 70, HIJAU_TUA, nama_font="caption", stroke=6, stroke_warna=KREM,
                alpha=c.p(0.22, 0.28) * a_atas)
    # bagian bawah: 4 langkah
    for i, (nama, t0) in enumerate(LANGKAH):
        a = c.p(t0, t0 + 0.06)
        if a <= 0:
            continue
        cx = 150 + i * 260
        cy = 1170
        s = skala_muncul(c, t0)
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((cx - 115 * s, cy - 150 * s, cx + 115 * s, cy + 150 * s), 24, fill=(247, 236, 208, 240),
                             outline=(120, 90, 50, 255), width=5)
        se.tempel(img, lap, a)
        d = ImageDraw.Draw(img, "RGBA")
        if nama == "rajang":
            for k in range(5):
                cengkeh(d, cx - 60 + k * 30, cy - 40 + (k % 2) * 30, 0.9, 0.6 + k, a)
            d.polygon([(cx - 70, cy + 60), (cx + 80, cy + 20), (cx + 85, cy + 40), (cx - 65, cy + 75)],
                      fill=(180, 185, 195, int(255 * a)), outline=(60, 60, 70, int(255 * a)))
        elif nama == "campur":
            d.pieslice((cx - 90, cy - 40, cx + 90, cy + 110), 180, 360, fill=TEMBAKAU + (int(255 * a),))
            for k in range(6):
                cengkeh(d, cx - 60 + k * 24, cy - 10 - (k % 3) * 14, 0.6, k, a)
        elif nama == "linting":
            d.rectangle((cx - 85, cy - 20, cx + 85, cy + 50), fill=KERTAS + (int(255 * a),), outline=(120, 90, 50, int(255 * a)),
                        width=3)
            d.rectangle((cx - 85, cy - 20, cx + 85, cy + 8), fill=TEMBAKAU + (int(255 * a),))
            d.arc((cx - 85, cy - 40, cx + 85, cy + 20), 180, 360, fill=(120, 90, 50, int(255 * a)), width=4)
        else:
            asap(img, cx + 70, cy - 30, c.t, a, tinggi=110, lebar=0.5, seed=7)
            rokok(img, cx - 80, cy + 40, cx + 70, cy - 20, tebal=26, bara=a, t=c.t, alpha=a)
            d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (cx, cy + 120 * s), nama, 40, TINTA, nama_font="caption", alpha=a)
        if i > 0:
            se.teks(d, (cx - 130, cy), "→", 50, MERAH_TUA, nama_font="ui", alpha=a)
    hdr(img, "Racikan Haji Djamhari")
    return img


def a_apotek(c):
    img = LATAR.copy()
    fase_b = c.p(0.5, 0.58)
    a_a = 1 - fase_b
    if a_a > 0.01:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lap)
        # toko apotek
        d.rectangle((140, 560, 940, 1180), fill=(235, 220, 185, 255), outline=(90, 60, 30, 255), width=8)
        d.polygon([(110, 560), (540, 440), (970, 560)], fill=(140, 60, 35, 255), outline=(80, 35, 20, 255))
        d.rectangle((300, 590, 780, 670), fill=(40, 90, 70, 255), outline=(20, 50, 40, 255), width=5)
        d.text((540, 630), "APOTEK", font=se.font("caption", 60), fill=(250, 240, 210), anchor="mm")
        # rak + bungkus "rokok cengkeh"
        for row in range(2):
            y = 790 + row * 170
            d.rectangle((200, y + 70, 880, y + 84), fill=(110, 70, 35, 255))
            for k in range(6):
                x = 240 + k * 110
                d.rectangle((x, y - 30, x + 80, y + 70), fill=(200, 160, 100, 255), outline=(90, 60, 30, 255), width=3)
                d.text((x + 40, y + 20), "rokok\ncengkeh", font=se.font("ui", 17), fill=(90, 30, 20), anchor="mm",
                       align="center")
        se.tempel(img, lap, a_a)
        d = ImageDraw.Draw(img, "RGBA")
        # tetangga berdatangan
        rng = random.Random(6)
        for i in range(12):
            t0 = 0.05 + i * 0.025
            k = c.p(t0, t0 + 0.15)
            if k <= 0:
                continue
            kiri = i % 2 == 0
            x = lerp(-40 if kiri else 1120, 380 + rng.uniform(-80, 320), k)
            orang(d, x, 1260 + rng.uniform(-20, 30), 1.6, (60 + i * 6, 45, 35), a_a)
        se.kartu(img, 540, 1335, "Dijual sebagai \"rokok cengkeh\"", "", COKLAT, alpha=c.p(0.28, 0.34) * a_a,
                 tiang=False, skala=skala_muncul(c, 0.28))
    if fase_b > 0:
        lap = LATAR_GELAP.copy()
        se.tempel(img, lap, fase_b)
        se.glow(img, 760, 900, 300, (200, 80, 20), 1.0 * fase_b)
        asap(img, 780, 880, c.t, fase_b, tinggi=380, lebar=1.0, seed=3)
        rokok(img, 140, 1000, 780, 880, tebal=70, bara=fase_b, t=c.t, alpha=fase_b)
        d = ImageDraw.Draw(img, "RGBA")
        # percikan
        rng = random.Random(int(c.t * 12))
        for i in range(10):
            ang = rng.uniform(-math.pi, 0)
            r = rng.uniform(40, 130)
            x, y = 780 + math.cos(ang) * r, 880 + math.sin(ang) * r
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 200, 80, int(230 * fase_b)))
        for j, (t0, xy, uk, sud) in enumerate(((0.6, (720, 600), 96, -8), (0.7, (420, 700), 80, 6))):
            a = c.p(t0, t0 + 0.04)
            if a > 0:
                goyang = 6 * math.sin(c.t * 25 + j)
                se.teks(d, (xy[0] + goyang, xy[1]), "KRETEK!", uk, KUNING, nama_font="caption", stroke=9,
                        stroke_warna=GELAP, alpha=a)
        a = c.p(0.82, 0.88)
        if a > 0:
            se.panel(img, (140, 1130, 940, 1310), alpha=a)
            d = ImageDraw.Draw(img, "RGBA")
            se.teks(d, (540, 1195), "Lahirlah nama:", 44, TINTA, nama_font="judul", alpha=a)
            se.teks(d, (540, 1260), "KRETEK", 64, (170, 30, 20), nama_font="caption", alpha=a)
    hdr(img, "Dari mulut ke mulut")
    return img


def a_rehook(c):
    kamera = se.kamera_antara(cam(JAWA, -6.95, 110.8, 2.2), cam(JAWA, -6.85, 110.84, 2.8), c.p(0.0, 1.0))
    img = se.render_peta(JAWA, kamera)
    kx, ky = layar(JAWA, kamera, KUDUS)
    se.glow(img, kx, ky, 220, (255, 200, 70), 1.6 + 0.3 * math.sin(c.t * 5))
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(8)
    for i in range(22):
        fase = (rng.random() + c.t * rng.uniform(0.3, 0.5)) % 1
        x = kx + rng.uniform(-260, 260)
        y = lerp(ky - 420, ky + 60, fase)
        koin(d, x, y, rng.uniform(18, 30), 0.95 * (1 - fase * 0.3))
    d.ellipse((kx - 18, ky - 18, kx + 18, ky + 18), fill=(255, 200, 60, 255), outline=PUTIH + (255,), width=4)
    label(d, (kx, ky + 60), "Kudus", 48)
    se.panel(img, (90, 420, 990, 650), alpha=c.p(0.0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 490), "TAPI BAGIAN PALING GILA…", 54, (170, 30, 20), nama_font="caption", alpha=c.p(0.0, 0.08))
    se.teks(d, (540, 580), "\"obat\" ini bikin satu kota kaya raya", 42, TINTA, nama_font="caption",
            alpha=c.p(0.35, 0.45))
    hdr(img, "Kota di pesisir utara Jawa")
    return img


def a_nitisemito(c):
    img = LATAR.copy()
    se.kartu(img, 540, 470, "Nitisemito", "pengusaha Kudus", MERAH, alpha=c.p(0.0, 0.08), tiang=False,
             skala=skala_muncul(c, 0.0))
    kalender(img, 260, 760, "MULAI", "1906", "", c.p(0.05, 0.12), skala_muncul(c, 0.05) * 0.68)
    bungkus_baltiga(img, 720, 800, 0.95 * skala_muncul(c, 0.2), alpha=c.p(0.2, 0.28), sudut=-5)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.52, 0.58)
    if a > 0:
        se.teks(d, (540, 1060), "HADIAH!", 70, (190, 30, 20), nama_font="caption", stroke=6, stroke_warna=KREM, alpha=a)
        jam_dinding(d, 290, 1210, 90 * skala_muncul(c, 0.52), c.t, a)
    a2 = c.p(0.66, 0.72)
    if a2 > 0:
        sepeda(d, 760, 1270, 1.1 * skala_muncul(c, 0.66), c.t, a2)
    hdr(img, "Raja kretek dari Kudus")
    return img


def a_raja(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # pabrik
    asap(img, 300, 430, c.t, 0.9, tinggi=150, lebar=0.6, seed=4, warna=(170, 165, 160))
    asap(img, 780, 430, c.t + 1, 0.9, tinggi=150, lebar=0.6, seed=5, warna=(170, 165, 160))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((280, 430, 320, 560), fill=(110, 60, 40, 255), outline=(40, 20, 10, 255), width=4)
    d.rectangle((760, 430, 800, 560), fill=(110, 60, 40, 255), outline=(40, 20, 10, 255), width=4)
    d.rectangle((150, 540, 930, 720), fill=(150, 80, 50, 255), outline=(50, 25, 15, 255), width=6)
    for k in range(4):
        x = 150 + k * 195
        d.polygon([(x, 540), (x + 98, 480), (x + 195, 540)], fill=(120, 60, 40, 255), outline=(50, 25, 15, 255))
    for k in range(8):
        d.rectangle((190 + k * 92, 590, 240 + k * 92, 650), fill=(255, 210, 120, 220))
    d.text((540, 690), "PABRIK KRETEK", font=se.font("ui", 30), fill=(255, 235, 200), anchor="mm")
    k = c.p(0.0, 0.4)
    n = int(round(10000 * k / 100.0)) * 100
    se.teks(d, (540, 830), f"{n:,}".replace(",", "."), 150, (255, 200, 80), nama_font="caption", stroke=10,
            stroke_warna=GELAP, alpha=c.p(0.0, 0.05))
    se.teks(d, (540, 935), "pekerja (± 1938)", 50, PUTIH, nama_font="caption", stroke=6, stroke_warna=GELAP,
            alpha=c.p(0.03, 0.09))
    tampil = int(60 * k)
    for i in range(tampil):
        col, row = i % 15, i // 15
        orang(d, 100 + col * 63, 1060 + row * 62, 1.0, (215, 200, 180), 1.0)
    se.kartu(img, 540, 1340, "Dijuluki: Raja Kretek", "", MERAH, alpha=c.p(0.42, 0.5), tiang=False,
             skala=skala_muncul(c, 0.42))
    stempel(img, "KOTA KRETEK", 540, 1130, skala_muncul(c, 0.72, 0.08) * 0.95, uk=80, sudut=-6)
    hdr(img, "Kudus, tahun 1930-an")
    return img


def a_rahasia(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 425), "INI RAHASIANYA:", 58, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP,
            alpha=c.p(0.0, 0.05))
    se.teks(d, (540, 510), "EUGENOL", 100, KUNING, nama_font="caption", stroke=9, stroke_warna=GELAP,
            alpha=c.p(0.03, 0.08))
    # fase 1: cengkeh → bius dokter gigi
    a1 = c.p(0.05, 0.12) * (1 - c.p(0.34, 0.4))
    if a1 > 0:
        for k in range(5):
            cengkeh(d, 200 + k * 40, 780 + (k % 2) * 30, 1.6, 0.4 * k - 0.6, a1)
        se.teks(d, (540, 820), "→", 90, MERAH_TUA, nama_font="ui", alpha=a1)
        gigi(d, 820, 800, 1.5, a1 * c.p(0.14, 0.2))
        se.kartu(img, 540, 1080, "Bahan bius dokter gigi", "terkandung di cengkeh", BIRU, alpha=a1 * c.p(0.16, 0.22),
                 tiang=False, skala=skala_muncul(c, 0.16))
    # fase 2: tenggorokan kebas, asap masuk dalam
    a2 = c.p(0.38, 0.45)
    if a2 > 0:
        kebas = c.p(0.45, 0.55)
        kelabu = c.p(0.66, 0.85) * 0.75
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        paru(dl, 540, 1020, 0.95, kelabu, 1.0, kebas)
        se.tempel(img, lap, a2)
        d = ImageDraw.Draw(img, "RGBA")
        if kebas > 0:
            se.teks(d, (790, 700), "KEBAS", 56, BIRU, nama_font="caption", stroke=6, stroke_warna=KREM, alpha=kebas)
            d.line((690, 700, 580, 720), fill=BIRU + (int(255 * kebas),), width=6)
        # partikel asap turun ke paru
        k = c.p(0.52, 0.9)
        if k > 0:
            rng = random.Random(12)
            for i in range(40):
                f = (rng.random() + c.t * 0.5) % 1.0
                if f > k + 0.1:
                    continue
                if f < 0.45:
                    x = 540 + rng.uniform(-18, 18)
                    y = lerp(620, 905, f / 0.45)
                else:
                    sisi = -1 if i % 2 else 1
                    g = (f - 0.45) / 0.55
                    x = 540 + sisi * lerp(30, rng.uniform(90, 230), g)
                    y = lerp(905, rng.uniform(900, 1230), g)
                r = rng.uniform(8, 16)
                d.ellipse((x - r, y - r, x + r, y + r), fill=(120, 115, 110, 170))
            se.teks(d, (540, 600), "asap masuk lebih dalam", 40, TINTA, nama_font="caption", stroke=5,
                    stroke_warna=KREM, alpha=c.p(0.55, 0.62))
    se.kartu(img, 540, 1340, "Terasa lega ≠ sembuh", "", MERAH, alpha=c.p(0.8, 0.86), tiang=False,
             skala=skala_muncul(c, 0.8))
    hdr(img, "Kenapa terasa \"lega\"?")
    return img


def a_tren(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # Amerika 2009: rokok cengkeh dilarang
    a1 = c.p(0.0, 0.08)
    rokok(img, 170, 700, 560, 610, tebal=40, bara=0.0, t=c.t, alpha=a1)
    d = ImageDraw.Draw(img, "RGBA")
    coret_besar(d, (180, 540, 570, 760), c.p(0.15, 0.3), a1)
    se.kartu(img, 790, 650, "Amerika, 2009", "rokok cengkeh dilarang", MERAH, alpha=a1, tiang=False,
             skala=skala_muncul(c, 0.0))
    # Indonesia 2026: vape dikaji
    a2 = c.p(0.36, 0.44)
    if a2 > 0:
        vape(d, 280, 1020, 1.05 * skala_muncul(c, 0.36), a2)
        se.kartu(img, 680, 980, "Sekarang: vape", "dikaji untuk dilarang total", HIJAU_TUA, alpha=a2, tiang=False,
                 skala=skala_muncul(c, 0.36))
    a3 = c.p(0.74, 0.8)
    if a3 > 0:
        stempel(img, "DUKUNG", 330, 1260, skala_muncul(c, 0.74, 0.08) * 0.7, uk=54, sudut=-6, warna=HIJAU_TUA)
        stempel(img, "MENOLAK", 760, 1260, skala_muncul(c, 0.8, 0.08) * 0.7, uk=54, sudut=5)
    hdr(img, "Rokok cengkeh & vape")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = se.kamera_antara(cam(JAWA, -6.9, 110.8, 2.4), cam(JAWA, -6.85, 110.84, 2.7), c.p(0.0, 1.0))
    img = se.render_peta(JAWA, kamera)
    kx, ky = layar(JAWA, kamera, KUDUS)
    se.glow(img, kx, ky, 120, (255, 200, 80), 1.2)
    se.tint(img, (10, 6, 0), 0.2 + 0.4 * c.p(0.58, 0.66))
    a = c.p(0.02, 0.1) * (1 - c.p(0.58, 0.64))
    if a > 0:
        se.panel(img, (90, 420, 990, 720), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 495), "Dulu dijual sebagai obat", 54, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 590), "sekarang kita tahu bahayanya.", 44, TINTA, nama_font="judul", alpha=c.p(0.16, 0.22) * a)
        se.teks(d, (540, 655), "Lega, belum tentu sehat.", 44, TINTA, nama_font="judul", alpha=c.p(0.3, 0.36) * a)
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
    Adegan("hook", "Rokok ini dulu dijual sebagai obat. Lagi rame vape mau dilarang total? Rokok kretek justru lahir sebagai obat sesak napas. Tapi ada satu rahasia cengkeh yang bikin obat ini menipu.",
           a_hook, transisi=False),
    Adegan("kudus", "Kudus, Jawa Tengah, sekitar tahun delapan belas delapan puluhan. Ada warga bernama Haji Jamhari yang sering sesak di dada.",
           a_kudus),
    Adegan("racik", "Dia coba oles minyak cengkeh ke dada. Rasanya lega. Lalu muncul ide: cengkeh dirajang, dicampur tembakau, dilinting, terus diisap.",
           a_racik),
    Adegan("apotek", "Katanya, sesaknya berkurang. Kabarnya menyebar, tetangga ikut pesan, sampai dijual di apotek sebagai rokok cengkeh. Waktu dibakar, cengkehnya bunyi kretek, kretek. Lahirlah nama kretek.",
           a_apotek),
    Adegan("rehook", "Tapi bagian paling gila-nya: obat ini malah bikin satu kota kaya raya.",
           a_rehook),
    Adegan("nitisemito", "Tahun sembilan belas nol enam, pengusaha Kudus bernama Nitisemito mulai bikin kretek merek Bal Tiga. Promosinya pakai hadiah, dari jam dinding sampai sepeda.",
           a_nitisemito),
    Adegan("raja", "Akhir tahun tiga puluhan, pabriknya punya sekitar sepuluh ribu pekerja. Dia dijuluki Raja Kretek, dan Kudus dikenal sebagai Kota Kretek.",
           a_raja),
    Adegan("rahasia", "Nah, ini rahasia cengkehnya. Cengkeh mengandung eugenol, bahan bius yang dipakai dokter gigi. Peneliti menduga, eugenol bikin tenggorokan kebas, jadi asapnya bisa diisap lebih dalam. Terasa lega, padahal paru-paru tetap kena.",
           a_rahasia),
    Adegan("tren", "Tahun dua ribu sembilan, Amerika melarang rokok cengkeh. Sekarang, giliran vape yang lagi dikaji buat dilarang total. Ada yang dukung, ada yang menolak.",
           a_tren),
    Adegan("penutup", "Dulu dijual sebagai obat, sekarang kita tahu bahayanya. Lega, belum tentu sehat. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
