"""Shorts ±88 detik: Lampu lalu lintas pertama di dunia (London, 1868) yang meledak, dan asal warna merah-kuning-hijau.

Tren: Operasi Zebra 2026 dimulai hari ini, 16–29 November 2026 (Korlantas Polri).
Visual: tiang sinyal gas Westminster meledak di malam hari, jalanan London penuh kereta kuda, sinyal rel
dipindah ke jalan raya, peta perempatan dekat Parlemen, kalender 9 Des → 2 Jan, lampu listrik Cleveland 1914
& Detroit 1920, sinyal kereta api merah/hijau/putih, kaca merah pecah, peta Indonesia + Operasi Zebra.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Peta, back_out, clamp, lerp

NAMA_FILE = "lampu-merah-pertama-1868-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "LAMPU MERAH PERTAMA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
BIRU = (30, 80, 150)
BIRU_POLISI = (25, 35, 70)
HIJAU_TUA = (30, 110, 60)
COKLAT = (120, 80, 40)
KUNING = (255, 214, 10)
GELAP = (10, 10, 20)
L_MERAH = (240, 40, 30)
L_HIJAU = (40, 220, 110)
L_KUNING = (255, 190, 20)
L_PUTIH = (255, 250, 230)
MATI = (55, 50, 45)
BESI = (40, 70, 55)
KREM = (247, 236, 208)

print("  menyiapkan peta Indonesia...")
PETA = Peta(85, 150, -45, 35, 30, [], [(-7.2, 107.6, 0.35), (-7.0, 110.4, 0.4), (-0.5, 101.0, 0.5)],
            seed=30, darat=pd.SEMUA)

print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 30, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (20, 14, 8), 0.6)


def _latar_malam(seed=5):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line((0, y, W, y), fill=se.lerp_rgb((8, 12, 32), (45, 28, 30), y / H) + (255,))
    rs = random.Random(seed)
    for _ in range(90):
        x, yy, r = rs.uniform(0, W), rs.uniform(0, 700), rs.uniform(1, 3)
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=(255, 255, 230, rs.randint(60, 200)))
    # siluet gedung parlemen (menara jam + atap runcing) & jalan berbatu
    sil = (14, 14, 26, 255)
    d.rectangle((0, 1050, W, 1180), fill=sil)
    for x0, w, h in [(-20, 160, 120), (140, 120, 200), (260, 200, 150), (700, 140, 180), (840, 260, 140)]:
        d.rectangle((x0, 1050 - h, x0 + w, 1050), fill=sil)
        for i in range(int(w // 30)):
            px = x0 + 15 + i * 30
            d.polygon([(px - 10, 1050 - h), (px, 1050 - h - 40), (px + 10, 1050 - h)], fill=sil)
    d.rectangle((880, 640, 960, 1050), fill=sil)  # menara jam
    d.polygon([(870, 640), (920, 540), (970, 640)], fill=sil)
    d.ellipse((895, 680, 945, 730), fill=(230, 200, 120, 255))
    d.rectangle((0, 1180, W, H), fill=(30, 26, 30, 255))
    for i in range(40):
        y = 1190 + (i // 8) * 40
        x = (i % 8) * 140 + ((i // 8) % 2) * 70
        d.rounded_rectangle((x, y, x + 120, y + 30), 8, fill=(42, 38, 42, 255))
    return img


LATAR_MALAM = _latar_malam()


# ------------------------------------------------------------------ helper

def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def skala_muncul(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


def stempel(img, isi, cx, cy, s, uk=76, sudut=-8, warna=(210, 30, 30)):
    if s <= 0.01:
        return
    f = se.font("caption", uk)
    lw = int(f.getlength(isi)) + 80
    lap = Image.new("RGBA", (lw, uk + 90), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((10, 10, lw - 10, uk + 80), 22, fill=(247, 236, 208, 200), outline=tuple(warna) + (255,),
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
    d.text((cx, cy + 20 * s), tgl, font=se.font("caption", int(140 * s)), fill=TINTA, anchor="mm")
    if tahun:
        d.text((cx, cy + h / 2 - 34 * s), tahun, font=se.font("ui", int(34 * s)), fill=(150, 30, 25), anchor="mm")
    se.tempel(img, lap, alpha)


def rot(cx, cy, x, y, a):
    c, s = math.cos(a), math.sin(a)
    return (cx + x * c - y * s, cy + x * s + y * c)


def tiang_knight(img, x, y_dasar, s=1.0, lengan=0.0, lampu=None, alpha=1.0, rusak=0.0):
    """Tiang sinyal Westminster 1868: tiang besi, dua lengan semafor, lentera gas di puncak.
    lengan: 0 = mendatar (berhenti), 1 = turun 45° (hati-hati). lampu: warna RGB lentera atau None."""
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    tinggi = 620 * s
    top = y_dasar - tinggi
    # dasar & tiang
    d.polygon([(x - 60 * s, y_dasar), (x + 60 * s, y_dasar), (x + 36 * s, y_dasar - 90 * s),
               (x - 36 * s, y_dasar - 90 * s)], fill=BESI + (255,), outline=(15, 25, 20, 255))
    d.rectangle((x - 20 * s, top + 120 * s, x + 20 * s, y_dasar - 90 * s), fill=BESI + (255,),
                outline=(15, 25, 20, 255), width=3)
    for k in (0.35, 0.6):
        yy = lerp(top + 120 * s, y_dasar - 90 * s, k)
        d.rectangle((x - 28 * s, yy - 8 * s, x + 28 * s, yy + 8 * s), fill=(70, 100, 80, 255))
    # lengan semafor (kiri & kanan)
    a = math.radians(45) * lengan
    py = top + 150 * s
    for arah in (-1, 1):
        pts = [rot(x, py, 0, -12 * s, 0), rot(x, py, arah * 230 * s, -12 * s, arah * a),
               rot(x, py, arah * 230 * s, 12 * s, arah * a), rot(x, py, 0, 12 * s, 0)]
        pts = [rot(x, py, arah * 18 * s, -14 * s, arah * a), rot(x, py, arah * 240 * s, -14 * s, arah * a),
               rot(x, py, arah * 240 * s, 14 * s, arah * a), rot(x, py, arah * 18 * s, 14 * s, arah * a)]
        d.polygon(pts, fill=(200, 40, 35, 255), outline=(60, 10, 10, 255))
        bx, by = rot(x, py, arah * 200 * s, 0, arah * a)
        d.ellipse((bx - 8 * s, by - 8 * s, bx + 8 * s, by + 8 * s), fill=PUTIH + (255,))
    # lentera gas
    lx0, ly0, lx1, ly1 = x - 45 * s, top + 20 * s, x + 45 * s, top + 110 * s
    if rusak < 1:
        d.polygon([(x - 55 * s, top + 20 * s), (x, top - 30 * s), (x + 55 * s, top + 20 * s)], fill=BESI + (255,))
        d.rectangle((lx0, ly0, lx1, ly1), fill=(25, 35, 30, 255), outline=(15, 20, 15, 255), width=3)
        warna = lampu if lampu else MATI
        d.ellipse((x - 32 * s, top + 33 * s, x + 32 * s, top + 97 * s), fill=tuple(warna) + (255,))
    se.tempel(img, lap, alpha)
    if lampu and rusak < 1 and alpha > 0.3:
        se.glow(img, x, top + 65 * s, 150 * s, lampu, 1.4 * alpha)


def ledakan(img, x, y, r, k, seed=1):
    """k: 0..1 progres ledakan (besar → pudar)."""
    if k <= 0 or k >= 1:
        return
    rng = random.Random(seed)
    besar = back_out(min(1.0, k * 3)) * r
    pudar = 1 - clamp((k - 0.6) / 0.4)
    se.glow(img, x, y, besar * 2.2, (255, 140, 40), 2.5 * pudar)
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    for lapis, (warna, skl) in enumerate([((150, 20, 10), 1.0), ((240, 90, 20), 0.78), ((255, 190, 40), 0.55),
                                          ((255, 250, 210), 0.28)]):
        pts = []
        n = 18
        for i in range(n * 2):
            a = i / (n * 2) * math.tau + lapis * 0.3
            rr = besar * skl * (1.0 if i % 2 == 0 else rng.uniform(0.45, 0.65))
            pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
        d.polygon(pts, fill=warna + (int(255 * pudar),))
    # serpihan
    for i in range(26):
        a = rng.uniform(0, math.tau)
        v = rng.uniform(0.6, 1.4) * r * 1.8
        jx = x + math.cos(a) * v * k
        jy = y + math.sin(a) * v * k + 400 * k * k
        sz = rng.uniform(5, 13)
        d.rectangle((jx - sz, jy - sz, jx + sz, jy + sz), fill=(255, rng.randint(120, 220), 40, int(255 * pudar)))
    se.tempel(img, lap)


def polisi(d, x, y, s=1.0, alpha=1.0, tuas=0.0):
    """Siluet polisi London (helm kubah) berdiri di (x, y = kaki)."""
    a = int(255 * alpha)
    c = BIRU_POLISI + (a,)
    d.rectangle((x - 30 * s, y - 150 * s, x + 30 * s, y - 40 * s), fill=c)
    d.rectangle((x - 26 * s, y - 40 * s, x - 6 * s, y), fill=c)
    d.rectangle((x + 6 * s, y - 40 * s, x + 26 * s, y), fill=c)
    d.ellipse((x - 22 * s, y - 200 * s, x + 22 * s, y - 150 * s), fill=(225, 195, 160, a))
    d.ellipse((x - 26 * s, y - 240 * s, x + 26 * s, y - 175 * s), fill=c)
    d.rectangle((x - 30 * s, y - 182 * s, x + 30 * s, y - 172 * s), fill=c)
    d.ellipse((x - 5 * s, y - 230 * s, x + 5 * s, y - 220 * s), fill=(220, 200, 120, a))
    # lengan memegang tuas
    ang = math.radians(-60 + 50 * tuas)
    hx, hy = x + 30 * s + math.cos(ang) * 70 * s, y - 135 * s + math.sin(ang) * 70 * s
    d.line((x + 25 * s, y - 135 * s, hx, hy), fill=c, width=int(18 * s))


def kereta_kuda(d, x, y, s=1.0, sudut=0.0, warna=(90, 50, 30), alpha=1.0):
    """Tampak atas: kereta + kuda di depannya."""
    a = int(255 * alpha)
    body = [rot(x, y, -26 * s, -16 * s, sudut), rot(x, y, 26 * s, -16 * s, sudut), rot(x, y, 26 * s, 16 * s, sudut),
            rot(x, y, -26 * s, 16 * s, sudut)]
    d.polygon(body, fill=tuple(warna) + (a,), outline=(30, 20, 10, a))
    kx, ky = rot(x, y, 48 * s, 0, sudut)
    d.ellipse((kx - 14 * s, ky - 8 * s, kx + 14 * s, ky + 8 * s), fill=(60, 40, 25, a))


def kereta_api(d, x, y, s=1.0, alpha=1.0, warna=(40, 40, 50)):
    """Siluet lokomotif uap, menghadap kanan, (x, y) = rel di bawah roda belakang."""
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    d.rectangle((x, y - 150 * s, x + 90 * s, y - 40 * s), fill=c)               # kabin
    d.rectangle((x + 90 * s, y - 110 * s, x + 260 * s, y - 40 * s), fill=c)     # ketel
    d.rectangle((x + 200 * s, y - 175 * s, x + 230 * s, y - 110 * s), fill=c)   # cerobong
    d.polygon([(x + 260 * s, y - 40 * s), (x + 300 * s, y - 10 * s), (x + 250 * s, y - 10 * s)], fill=c)
    d.rectangle((x + 15 * s, y - 135 * s, x + 70 * s, y - 95 * s), fill=(255, 220, 120, a))
    for wx, wr in [(40, 30), (130, 30), (210, 22)]:
        d.ellipse((x + (wx - wr) * s, y - 2 * wr * s, x + (wx + wr) * s, y), fill=(20, 20, 25, a),
                  outline=(150, 150, 160, a), width=3)


def rel(d, x0, x1, y, alpha=1.0):
    a = int(255 * alpha)
    for xx in range(int(x0), int(x1), 50):
        d.rectangle((xx, y + 2, xx + 26, y + 22), fill=(110, 75, 45, a))
    d.line((x0, y + 4, x1, y + 4), fill=(80, 80, 90, a), width=6)


def lampu_tiang(img, x, y, s, warna_lampu, nyala, alpha=1.0, label=None):
    """Lampu lalu lintas vertikal. warna_lampu: daftar RGB (atas→bawah); nyala: set indeks yang menyala."""
    if alpha <= 0.01:
        return
    n = len(warna_lampu)
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    w, step = 150 * s, 140 * s
    h = step * n + 30 * s
    d.rectangle((x - 14 * s, y + h / 2, x + 14 * s, y + h / 2 + 260 * s), fill=(45, 45, 50, 255))
    d.rounded_rectangle((x - w / 2 + 8, y - h / 2 + 10, x + w / 2 + 8, y + h / 2 + 10), 26 * s, fill=(0, 0, 0, 110))
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), 26 * s, fill=(35, 35, 40, 255),
                        outline=(10, 10, 10, 255), width=4)
    pusat = []
    for i, wl in enumerate(warna_lampu):
        cy = y - h / 2 + 15 * s + step * (i + 0.5)
        r = 52 * s
        on = i in nyala
        warna = wl if on else tuple(int(v * 0.25) for v in wl)
        d.ellipse((x - r, cy - r, x + r, cy + r), fill=tuple(warna) + (255,), outline=(10, 10, 10, 255), width=3)
        if label:
            d.text((x + w / 2 + 20, cy), label[i], font=se.font("caption", int(40 * s)), fill=TINTA, anchor="lm",
                   stroke_width=5, stroke_fill=KREM)
        pusat.append((cy, on, wl))
    se.tempel(img, lap, alpha)
    for cy, on, wl in pusat:
        if on:
            se.glow(img, x, cy, 110 * s, wl, 1.2 * alpha)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_MALAM.copy()
    goyang = math.sin(c.t * 40) * 6 * (1 - c.p(0, 0.3))
    tiang_knight(img, 540 + goyang, 1250, 1.05, lengan=0.0, lampu=None, rusak=1.0)
    # ledakan berulang di lentera (sudah besar di frame pertama)
    ly = 1250 - 620 * 1.05 + 65
    k = 0.12 + 0.48 * ((c.t / 1.3) % 1.0)
    ledakan(img, 540 + goyang, ly, 230, k, seed=int(c.t / 1.3) + 3)
    se.glow(img, 540, ly, 380, (255, 120, 30), 1.0)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 400), "LAMPU MERAH", 118, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 535), "MELEDAK!", 130, KUNING, nama_font="caption", stroke=10, stroke_warna=GELAP)
    stempel(img, "LONDON, 1869", 790, 1110, 0.8 if c.p(0, 0.05) <= 0 else max(0.8, skala_muncul(c, 0.0, 0.08)),
            uk=50, sudut=-7)
    se.kartu(img, 540, 1290, "Operasi Zebra mulai hari ini", "16 – 29 November 2026", HIJAU_TUA,
             alpha=c.p(0.3, 0.38), tiang=False, skala=skala_muncul(c, 0.3))
    a = c.p(0.45, 0.52)
    if a > 0:
        se.panel(img, (110, 720, 970, 900), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 780), "Kenapa MERAH = berhenti?", 52, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 850), "dan dulu HIJAU bukan berarti jalan?", 38, TINTA, nama_font="judul",
                alpha=c.p(0.65, 0.7))
    return img


def a_london(c):
    img = LATAR.copy()
    se.panel(img, (70, 420, 1010, 1300))
    d = ImageDraw.Draw(img, "RGBA")
    # perempatan tampak atas
    jalan = (150, 140, 125, 255)
    d.rectangle((90, 760, 990, 960), fill=jalan)
    d.rectangle((440, 440, 640, 1280), fill=jalan)
    se.garis_putus(d, [(100, 860), (980, 860)], 1.0, (240, 230, 200), tebal=5, panah=False)
    se.garis_putus(d, [(540, 450), (540, 1270)], 1.0, (240, 230, 200), tebal=5, panah=False)
    # kereta kuda bergerak dari segala arah, berantakan
    rng = random.Random(8)
    n = int(18 * c.p(0.0, 0.4)) + 4
    for i in range(n):
        arah = i % 4
        fase = (rng.uniform(0, 1) + c.t * rng.uniform(0.08, 0.16)) % 1
        jit = rng.uniform(-70, 70)
        if arah == 0:
            x, y, sd = lerp(80, 1000, fase), 860 + jit, 0
        elif arah == 1:
            x, y, sd = lerp(1000, 80, fase), 860 + jit, math.pi
        elif arah == 2:
            x, y, sd = 540 + jit, lerp(450, 1280, fase), math.pi / 2
        else:
            x, y, sd = 540 + jit, lerp(1280, 450, fase), -math.pi / 2
        kereta_kuda(d, x, y, 1.1, sd + rng.uniform(-0.3, 0.3),
                    rng.choice([(90, 50, 30), (40, 40, 60), (120, 30, 30), (30, 70, 40)]))
    # tanda tabrakan
    for i, (bx, by) in enumerate([(500, 820), (600, 900), (250, 870), (560, 600)]):
        a = c.p(0.35 + i * 0.08, 0.42 + i * 0.08)
        if a > 0:
            for (dx, dy) in ((1, 1), (1, -1)):
                d.line((bx - 26 * dx, by - 26 * dy, bx + 26 * dx, by + 26 * dy), fill=(200, 30, 25, int(255 * a)),
                       width=12)
    se.kartu(img, 540, 560, "Jalanan London, 1860-an", "kereta kuda, pejalan kaki, tanpa lampu", COKLAT,
             alpha=c.p(0.0, 0.08), tiang=False, skala=skala_muncul(c, 0.0))
    a = c.p(0.6, 0.68)
    if a > 0:
        se.panel(img, (170, 1050, 910, 1270), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1125), "1.102 tewas", 84, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 1210), "di jalanan London, tahun 1866 saja", 36, TINTA, nama_font="judul", alpha=a)
    hdr(img, "Jalanan tanpa aturan")
    return img


def a_knight(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # kiri: rel kereta + sinyal; kanan: jalan raya
    rel(d, 40, 520, 1180)
    kereta_api(d, lerp(-320, 60, c.p(0.0, 0.4)), 1176, 0.8)
    tiang_knight(img, 330, 1180, 0.7, lengan=0.5 + 0.5 * math.sin(c.t * 2.5), lampu=None)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((600, 1100, 1060, 1260), fill=(150, 140, 125, 255))
    se.garis_putus(d, [(610, 1180), (1050, 1180)], 1.0, (240, 230, 200), tebal=5, panah=False)
    for i in range(3):
        fase = (c.t * 0.18 + i / 3) % 1
        kereta_kuda(d, lerp(620, 1040, fase), 1150 if i % 2 else 1215, 1.0, 0 if i % 2 else math.pi)
    se.teks(d, (330, 1290), "rel kereta", 40, TINTA, nama_font="tangan")
    se.teks(d, (830, 1290), "jalan raya", 40, TINTA, nama_font="tangan")
    # panah ide
    a = c.p(0.5, 0.75)
    se.garis_putus(d, [(380, 560), (600, 470), (820, 600), (830, 1060)], a, (200, 52, 44), tebal=8)
    if c.p(0.75, 0.82) > 0:
        tiang_knight(img, 830, 1100, 0.55, lengan=0, lampu=None, alpha=c.p(0.75, 0.82))
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (830, 450), "?!", 100, (200, 52, 44), nama_font="caption", stroke=6, stroke_warna=KREM,
                alpha=c.p(0.78, 0.84))
    se.kartu(img, 330, 470, "John Peake Knight", "manajer kereta api Inggris", BIRU,
             alpha=c.p(0.05, 0.13), tiang=False, skala=skala_muncul(c, 0.05))
    hdr(img, "Ide dari rel kereta")
    return img


def a_pasang(c):
    img = LATAR.copy()
    if c.t / c.d < 0.42:
        # peta Westminster sederhana
        se.panel(img, (70, 420, 1010, 1300))
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle((830, 440, 990, 1280), fill=(35, 75, 130, 255))  # Sungai Thames
        se.teks(d, (910, 860), "Thames", 40, (220, 235, 255), nama_font="tangan")
        jalan = (150, 140, 125, 255)
        d.rectangle((300, 700, 1000, 780), fill=jalan)       # Bridge St → jembatan
        d.rectangle((90, 760, 520, 830), fill=jalan)         # Great George St
        d.rectangle((420, 700, 520, 1280), fill=jalan)
        d.rectangle((830, 705, 990, 775), fill=(170, 160, 140, 255))
        se.teks(d, (900, 615), "Jembatan", 28, TINTA, nama_font="tangan", stroke=4, stroke_warna=KREM)
        se.teks(d, (900, 655), "Westminster", 28, TINTA, nama_font="tangan", stroke=4, stroke_warna=KREM)
        d.rectangle((560, 860, 800, 1220), fill=(190, 160, 110, 255), outline=(90, 60, 30, 255), width=4)
        se.teks(d, (680, 1000), "Gedung", 40, TINTA, nama_font="tangan")
        se.teks(d, (680, 1050), "Parlemen", 40, TINTA, nama_font="tangan")
        se.teks(d, (230, 870), "Great George St", 30, TINTA, nama_font="tangan")
        se.teks(d, (640, 680), "Bridge St", 30, TINTA, nama_font="tangan")
        pin = skala_muncul(c, 0.08)
        if pin > 0.01:
            r = 26 * pin
            se.glow(img, 470, 765, 120, (255, 60, 40), 1.5)
            d = ImageDraw.Draw(img, "RGBA")
            d.ellipse((470 - r, 765 - r, 470 + r, 765 + r), fill=(220, 30, 25, 255), outline=PUTIH + (255,), width=5)
        kalender(img, 230, 560, "DESEMBER", "9", "1868", c.p(0.12, 0.18), skala_muncul(c, 0.12) * 0.7)
        hdr(img, "Westminster, London")
        return img
    # siang vs malam
    k = c.p(0.42, 0.5)
    img = LATAR.copy()
    malam = LATAR_MALAM.crop((540, 0, 1080, H))
    img.alpha_composite(malam, (540, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.line((540, 380, 540, 1320), fill=TINTA + (255,), width=6)
    tiang_knight(img, 270, 1250, 0.85, lengan=0.5 + 0.5 * math.sin(c.t * 2.2), lampu=None, alpha=k)
    warna = L_MERAH if int(c.t * 0.9) % 2 == 0 else L_HIJAU
    tiang_knight(img, 810, 1250, 0.85, lengan=0, lampu=warna, alpha=k)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (270, 450), "SIANG", 64, TINTA, nama_font="caption", stroke=6, stroke_warna=KREM, alpha=k)
    se.teks(d, (270, 515), "lengan sinyal", 38, TINTA, nama_font="judul", alpha=k)
    se.teks(d, (810, 450), "MALAM", 64, PUTIH, nama_font="caption", stroke=6, stroke_warna=GELAP, alpha=k)
    se.teks(d, (810, 515), "lampu gas merah / hijau", 34, PUTIH, nama_font="judul", alpha=k)
    a = c.p(0.78, 0.86)
    if a > 0:
        polisi(d, 470, 1290, 0.9, a, tuas=0.5 + 0.5 * math.sin(c.t * 3))
        se.kartu(img, 540, 1330, "Dijalankan polisi, pakai tuas", "", BIRU_POLISI, alpha=a, tiang=False,
                 skala=skala_muncul(c, 0.78))
    hdr(img, "Siang & malam")
    return img


def a_meledak(c):
    img = LATAR_MALAM.copy()
    se.tint(img, (0, 0, 0), 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 420), "TAPI BAGIAN PALING GILA…", 56, KUNING, nama_font="caption", stroke=7, stroke_warna=GELAP,
            alpha=c.p(0.0, 0.05))
    if c.t / c.d < 0.5:
        kalender(img, 300, 760, "DESEMBER", "9", "1868", c.p(0.08, 0.14), skala_muncul(c, 0.08) * 0.75)
        kalender(img, 780, 760, "JANUARI", "2", "1869", c.p(0.22, 0.28), skala_muncul(c, 0.22) * 0.75)
        d = ImageDraw.Draw(img, "RGBA")
        se.garis_putus(d, [(430, 760), (650, 760)], c.p(0.14, 0.22), (255, 200, 120), tebal=7)
        a = c.p(0.3, 0.36)
        if a > 0:
            se.teks(d, (540, 1010), "cuma 24 hari", 92, (255, 90, 70), nama_font="caption", stroke=8,
                    stroke_warna=GELAP, alpha=a)
    else:
        k = c.p(0.5, 0.85)
        goyang = math.sin(c.t * 50) * 10 * (1 - k)
        tiang_knight(img, 540 + goyang, 1260, 1.0, lengan=0, lampu=None if k > 0.05 else L_MERAH,
                     rusak=1.0 if k > 0.05 else 0.0)
        ly = 1260 - 620 + 65
        ledakan(img, 540, ly, 260, k, seed=7)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 520), "GAS BOCOR", 90, PUTIH, nama_font="caption", stroke=9, stroke_warna=GELAP,
                alpha=c.p(0.52, 0.56))
        se.kartu(img, 540, 1330, "Polisi penjaganya luka parah", "", MERAH, alpha=c.p(0.78, 0.85), tiang=False,
                 skala=skala_muncul(c, 0.78))
    hdr(img, "Umurnya nggak sampai sebulan")
    return img


def a_hilang(c):
    img = LATAR.copy()
    se.panel(img, (70, 440, 1010, 1260))
    d = ImageDraw.Draw(img, "RGBA")
    tiang_knight(img, 300, 1180, 0.85, lengan=0, lampu=None, alpha=1 - 0.6 * c.p(0.3, 0.5))
    se.kartu(img, 300, 560, "Sinyal Westminster", "dibongkar, 1869", MERAH, alpha=c.p(0.0, 0.08), tiang=False,
             skala=skala_muncul(c, 0.0), coret=c.p(0.15, 0.35))
    # garis waktu kosong puluhan tahun
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (750, 640), "London tanpa", 46, TINTA, nama_font="caption", alpha=c.p(0.4, 0.48))
    se.teks(d, (750, 700), "lampu lalu lintas", 46, TINTA, nama_font="caption", alpha=c.p(0.4, 0.48))
    n = int(50 * c.p(0.5, 0.85))
    isi = "50+ tahun" if c.p(0.5, 0.85) >= 1 else f"{n} tahun"
    a = c.p(0.5, 0.55)
    if a > 0:
        se.teks(d, (750, 880), isi, 100, (170, 30, 20), nama_font="caption", stroke=7, stroke_warna=KREM,
                alpha=a)
        se.garis_putus(d, [(600, 1000), (900, 1000)], c.p(0.5, 0.9), TINTA, tebal=6)
        se.teks(d, (750, 1080), "puluhan tahun…", 48, TINTA, nama_font="judul", alpha=c.p(0.7, 0.78))
    hdr(img, "Dibongkar")
    return img


def a_amerika(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 420), "Yang nerusin: Amerika", 60, TINTA, nama_font="caption", stroke=6, stroke_warna=KREM,
            alpha=c.p(0.0, 0.06))
    a1 = c.p(0.12, 0.2)
    kedip = {0} if int(c.t * 1.2) % 2 == 0 else {1}
    lampu_tiang(img, 290, 760, 1.0, [L_MERAH, L_HIJAU], kedip, alpha=a1)
    se.kartu(img, 290, 1200, "Cleveland, 1914", "lampu lalu lintas listrik", BIRU, alpha=a1, tiang=False,
             skala=skala_muncul(c, 0.12))
    a2 = c.p(0.5, 0.58)
    fase = int(c.t * 1.4) % 3
    lampu_tiang(img, 790, 760, 1.0, [L_MERAH, L_KUNING, L_HIJAU], {fase} if c.p(0.7, 0.75) < 1 else {1}, alpha=a2)
    se.kartu(img, 790, 1200, "Detroit, 1920", "William Potts, kepolisian Detroit", HIJAU_TUA, alpha=a2, tiang=False,
             skala=skala_muncul(c, 0.5))
    a3 = c.p(0.75, 0.82)
    if a3 > 0:
        stempel(img, "+ KUNING", 790, 560, skala_muncul(c, 0.75, 0.08) * 0.9, uk=60, sudut=-8, warna=(190, 120, 0))
    hdr(img, "Lampu listrik")
    return img


def a_jawaban(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 420), "INI JAWABANNYA", 70, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP,
            alpha=c.p(0.0, 0.05))
    se.teks(d, (540, 510), "warnanya dari sinyal kereta api", 42, KUNING, nama_font="caption", stroke=6,
            stroke_warna=GELAP, alpha=c.p(0.1, 0.18))
    rel(d, 0, W, 1250)
    kereta_api(d, lerp(-340, 40, c.p(0.0, 0.5)), 1246, 0.9, warna=(20, 20, 28))
    nyala = set()
    if c.p(0.38, 0.4) > 0:
        nyala.add(0)
    if c.p(0.55, 0.57) > 0:
        nyala.add(1)
    if c.p(0.75, 0.77) > 0:
        nyala.add(2)
    se.panel(img, (560, 590, 1030, 1150), alpha=c.p(0.25, 0.32), warna=(60, 55, 50), garis=(20, 20, 20))
    lampu_tiang(img, 680, 860, 0.95, [L_MERAH, L_HIJAU, L_PUTIH], nyala, alpha=c.p(0.25, 0.32))
    d = ImageDraw.Draw(img, "RGBA")
    for i, (isi, a0) in enumerate([("BERHENTI", 0.38), ("HATI-HATI", 0.55), ("JALAN", 0.75)]):
        cy = 860 - (140 * 0.95 * 3 + 30 * 0.95) / 2 + 15 * 0.95 + 140 * 0.95 * (i + 0.5)
        se.teks(d, (880, cy), isi, 44, PUTIH, nama_font="caption", stroke=6, stroke_warna=GELAP,
                alpha=c.p(a0, a0 + 0.05))
    hdr(img, "Sinyal kereta, abad ke-19")
    return img


def a_kaca(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    if c.t / c.d < 0.66:
        # kaca merah pecah → tampak putih
        pecah = c.p(0.08, 0.2)
        x, y, r = 540, 800, 180
        warna = se.lerp_rgb(L_MERAH, L_PUTIH, c.p(0.2, 0.3))
        se.glow(img, x, y, 340, warna, 1.4)
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse((x - r - 30, y - r - 30, x + r + 30, y + r + 30), fill=(35, 35, 40, 255), outline=(10, 10, 10, 255),
                  width=6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (255,))
        rng = random.Random(4)
        if pecah > 0:
            for i in range(9):
                a = i / 9 * math.tau + rng.uniform(-0.2, 0.2)
                d.line((x, y, x + math.cos(a) * r * pecah, y + math.sin(a) * r * pecah), fill=(60, 10, 10, 255),
                       width=6)
            jatuh = c.p(0.2, 0.45)
            for i in range(14):
                sx, sy = x + rng.uniform(-r, r) * 0.7, y + rng.uniform(-r, r) * 0.7
                yy = sy + 600 * jatuh * jatuh * rng.uniform(0.6, 1.2)
                if yy < 1300:
                    sz = rng.uniform(10, 24)
                    d.polygon([(sx - sz, yy), (sx, yy - sz * 1.4), (sx + sz, yy + sz * 0.3)], fill=(220, 40, 30, 230))
        se.teks(d, (540, 470), "Kaca merah pecah…", 66, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP,
                alpha=c.p(0.02, 0.08))
        a = c.p(0.3, 0.36)
        if a > 0:
            se.teks(d, (540, 1080), "= tampak PUTIH = \"jalan\"", 54, KUNING, nama_font="caption", stroke=7,
                    stroke_warna=GELAP, alpha=a)
        a2 = c.p(0.48, 0.55)
        if a2 > 0:
            stempel(img, "TABRAKAN", 540, 1240, skala_muncul(c, 0.48, 0.08), uk=66, sudut=-6)
        hdr(img, "Ceritanya…")
        return img
    # sistem baru
    lampu_tiang(img, 400, 820, 1.15, [L_MERAH, L_KUNING, L_HIJAU], {int(c.t * 1.3) % 3},
                alpha=c.p(0.66, 0.7), label=["BERHENTI", "HATI-HATI", "JALAN"])
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 430), "Sejak itu:", 60, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP,
            alpha=c.p(0.66, 0.7))
    se.kartu(img, 540, 1330, "Hijau = jalan · Kuning = hati-hati", "", HIJAU_TUA, alpha=c.p(0.74, 0.8), tiang=False,
             skala=skala_muncul(c, 0.74))
    hdr(img, "Aturan warna yang baru")
    return img


def cam(lat, lon, zoom):
    x, y = PETA.px(lat, lon)
    return (x, y, zoom)


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = se.kamera_antara(cam(-2.5, 118.0, 0.8), cam(-3.5, 117.0, 0.88), c.p(0.0, 1.0))
    img = se.render_peta(PETA, kamera)
    se.tint(img, (10, 6, 0), 0.25 + 0.35 * c.p(0.6, 0.68))
    d = ImageDraw.Draw(img, "RGBA")
    # titik-titik razia di kota-kota besar
    kota = [(-6.2, 106.8), (-6.9, 107.6), (-7.0, 110.4), (-7.25, 112.75), (3.6, 98.7), (-5.15, 119.4),
            (-8.65, 115.2), (-0.95, 100.35), (-3.0, 104.75), (-1.25, 116.85), (0.5, 101.45), (-2.5, 140.7)]
    a = c.p(0.0, 0.5) * (1 - c.p(0.6, 0.66))
    for i, (la, lo) in enumerate(kota[:int(len(kota) * c.p(0.0, 0.4)) + 1]):
        x, y = kamera.layar(*PETA.px(la, lo))
        r = 12 + 4 * math.sin(c.t * 6 + i)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(240, 40, 30, int(230 * a)), outline=(255, 255, 255, int(220 * a)),
                  width=3)
    a = c.p(0.02, 0.1) * (1 - c.p(0.6, 0.66))
    if a > 0:
        se.panel(img, (90, 420, 990, 700), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 500), "Aturan di lampu merah", 52, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 580), "lahir dari kecelakaan", 52, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 650), "patuhi lampunya, ya", 38, TINTA, nama_font="judul", alpha=a)
        b2 = c.p(0.25, 0.33) * a
        if b2 > 0:
            stempel(img, "OPERASI ZEBRA 16–29 NOV", 540, 1180, b2 * 0.85, uk=56, sudut=-5, warna=HIJAU_TUA)
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
    Adegan("hook", "Lampu merah pertama di dunia, meledak. Operasi Zebra mulai hari ini. Tapi kenapa sih, merah artinya berhenti? Dan kenapa dulu, hijau bukan artinya jalan?",
           a_hook, transisi=False),
    Adegan("london", "London, tahun delapan belas enam puluhan. Jalanan penuh kereta kuda. Tahun delapan belas enam puluh enam saja, lebih dari seribu orang tewas di jalan.",
           a_london),
    Adegan("knight", "Lalu ahli kereta api, John Peake Knight, punya ide: pindahin sinyal rel kereta ke jalan raya.",
           a_knight),
    Adegan("pasang", "Sembilan Desember delapan belas enam puluh delapan, sinyal itu berdiri dekat gedung parlemen Inggris. Siang pakai lengan sinyal, malam pakai lampu gas merah dan hijau. Yang narik tuasnya, polisi.",
           a_pasang),
    Adegan("meledak", "Tapi bagian paling gila-nya: umurnya nggak sampai sebulan. Dua Januari delapan belas enam puluh sembilan, gasnya bocor, dan meledak. Polisi penjaganya luka parah.",
           a_meledak),
    Adegan("hilang", "Sinyal itu dibongkar. London nggak punya lampu lalu lintas lagi, sampai puluhan tahun kemudian.",
           a_hilang),
    Adegan("amerika", "Yang nerusin malah Amerika. Sembilan belas empat belas, lampu listrik dipasang di Cleveland. Sembilan belas dua puluh, polisi Detroit William Potts nambahin warna ketiga: kuning.",
           a_amerika),
    Adegan("jawaban", "Nah, ini jawabannya. Warnanya dipinjam dari kereta api. Dulu, merah artinya berhenti, hijau hati-hati, dan putih, jalan.",
           a_jawaban),
    Adegan("kaca", "Masalahnya, kalau kaca merahnya pecah, yang kelihatan putih. Ceritanya, masinis ngira aman, lalu tabrakan. Sejak itu, hijau jadi jalan, kuning jadi hati-hati.",
           a_kaca),
    Adegan("penutup", "Jadi, aturan lampu merah lahir dari kecelakaan. Patuhi lampunya ya. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
