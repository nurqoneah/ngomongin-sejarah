"""Shorts ±88 detik: Sejarah listrik di Indonesia — dari lampu gas Batavia sampai direbut dari Jepang (1945).

Tren: pencarian "mati lampu hari ini" + kabar ± 11 ribu desa belum berlistrik (November 2026).
Visual: bohlam raksasa di kota malam, jalan Batavia berlampu gas, pembangkit uap Gambir 1897,
trem listrik 1899, rumah terang vs kampung gelap, peta Jawa yang mulai menyala, pembangkit diambil Jepang,
massa pemuda & buruh merebut kantor listrik, kalender 27 Oktober 1945.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "sejarah-listrik-indonesia-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "LISTRIK DIREBUT"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
EMAS = (240, 190, 60)
KUNING_LAMPU = (255, 214, 120)
BIRU = (30, 80, 150)
ABU = (60, 60, 70)
HIJAU_TUA = (30, 110, 60)
MALAM_ATAS = (8, 12, 30)
MALAM_BAWAH = (28, 30, 55)

print("  menyiapkan peta Jawa...")
PETA = Peta(100, 120, -16, 4, 150, [], [(-7.2, 107.6, 0.35), (-7.0, 110.4, 0.4), (-7.9, 112.6, 0.4),
                                        (-7.5, 109.2, 0.3)],
            seed=27, darat=pd.SEMUA)

BATAVIA = (-6.15, 106.83)
BANDUNG = (-6.91, 107.61)
SEMARANG = (-6.97, 110.42)
SURABAYA = (-7.25, 112.75)
YOGYA = (-7.80, 110.36)

print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 27, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (20, 14, 8), 0.6)


def _langit():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line((0, y, W, y), fill=se.lerp_rgb(MALAM_ATAS, MALAM_BAWAH, y / H) + (255,))
    rng = random.Random(5)
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(150, 900)
        r = rng.choice([1.5, 2, 2.5])
        d.ellipse((x - r, y - r, x + r, y + r), fill=(230, 230, 255, rng.randint(80, 200)))
    return img


LANGIT = _langit()


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


def skala_muncul(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


def titik_kota(d, x, y, warna=MERAH, alpha=1.0, r=12):
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=(255, 255, 255, a), width=4)


def kilat(d, x, y, s=1.0, alpha=1.0, warna=(255, 230, 90)):
    """Ikon petir kecil."""
    a = int(255 * alpha)
    pts = [(0, -40), (-18, 4), (-2, 4), (-12, 40), (20, -8), (4, -8), (14, -40)]
    d.polygon([(x + px * s, y + py * s) for px, py in pts], fill=tuple(warna) + (a,), outline=(60, 40, 0, a))


def bohlam(img, x, y, s=1.0, nyala=1.0, alpha=1.0):
    """Bohlam pijar besar, nyala 0..1."""
    if alpha <= 0.01:
        return
    if nyala > 0.05:
        se.glow(img, x, y, 330 * s, (255, 210, 110), 1.6 * nyala * alpha)
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    r = 150 * s
    kaca = se.lerp_rgb((70, 70, 85), (255, 236, 160), nyala)
    d.ellipse((x - r, y - r, x + r, y + r), fill=kaca + (235,), outline=(230, 230, 230, 255), width=int(5 * s) + 1)
    d.polygon([(x - 70 * s, y + 120 * s), (x + 70 * s, y + 120 * s), (x + 55 * s, y + 190 * s), (x - 55 * s, y + 190 * s)],
              fill=kaca + (235,))
    # filamen
    fw = se.lerp_rgb((120, 90, 60), (255, 255, 230), nyala)
    d.line((x - 40 * s, y + 150 * s, x - 30 * s, y - 10 * s), fill=(150, 150, 150, 255), width=int(4 * s) + 1)
    d.line((x + 40 * s, y + 150 * s, x + 30 * s, y - 10 * s), fill=(150, 150, 150, 255), width=int(4 * s) + 1)
    zig = [(x - 30 * s + i * 10 * s, y - 10 * s + (12 * s if i % 2 else -12 * s)) for i in range(7)]
    d.line(zig, fill=fw + (255,), width=int(6 * s) + 1)
    # fitting
    for i in range(4):
        yy = y + (195 + i * 26) * s
        d.rounded_rectangle((x - 60 * s, yy, x + 60 * s, yy + 22 * s), 8, fill=(150, 150, 160, 255),
                            outline=(70, 70, 80, 255), width=3)
    d.ellipse((x - 25 * s, y + 295 * s, x + 25 * s, y + 325 * s), fill=(50, 50, 55, 255))
    # kilau
    d.arc((x - r * 0.75, y - r * 0.75, x + r * 0.75, y + r * 0.75), 200, 250, fill=(255, 255, 255, 170),
          width=int(12 * s) + 1)
    se.tempel(img, lap, alpha)


def rumah(d, x, y, w, h, jenis="kampung", nyala=0.0, alpha=1.0):
    """Siluet rumah. (x, y) = titik tengah bawah."""
    a = int(255 * alpha)
    if jenis == "eropa":
        dinding, atap = (235, 228, 210), (150, 60, 45)
    elif jenis == "kantor":
        dinding, atap = (240, 238, 228), (110, 110, 120)
    elif jenis == "pabrik":
        dinding, atap = (150, 110, 85), (90, 60, 45)
    else:
        dinding, atap = (120, 90, 60), (70, 50, 30)
    gelap = 0.35 + 0.65 * clamp(nyala * 0.6 + (0.4 if jenis != "kampung" else 0.15))
    dc = tuple(int(v * gelap) for v in dinding)
    ac = tuple(int(v * gelap) for v in atap)
    d.rectangle((x - w / 2, y - h, x + w / 2, y), fill=dc + (a,), outline=(10, 10, 15, a), width=3)
    if jenis == "kantor":
        d.rectangle((x - w / 2 - 10, y - h - 30, x + w / 2 + 10, y - h), fill=ac + (a,))
        d.polygon([(x - w / 2 - 10, y - h - 30), (x, y - h - 80), (x + w / 2 + 10, y - h - 30)], fill=ac + (a,))
        for i in range(5):
            cx = x - w / 2 + 20 + i * (w - 40) / 4
            d.line((cx, y - h + 10, cx, y), fill=(200, 200, 205, int(a * gelap)), width=8)
    elif jenis == "pabrik":
        d.polygon([(x - w / 2, y - h), (x - w / 4, y - h - 50), (x, y - h), (x + w / 4, y - h - 50), (x + w / 2, y - h)],
                  fill=ac + (a,))
        d.rectangle((x + w / 2 - 50, y - h - 170, x + w / 2 - 20, y - h), fill=(110, 70, 50, a))
    else:
        d.polygon([(x - w / 2 - 20, y - h), (x, y - h - h * 0.6), (x + w / 2 + 20, y - h)], fill=ac + (a,),
                  outline=(10, 10, 15, a))
    # jendela
    n = 3 if w > 200 else 2
    for i in range(n):
        jx = x - w / 2 + (i + 0.5) * w / n
        jy = y - h * 0.62
        jw, jh = min(40, w / n * 0.4), h * 0.28
        if nyala > 0.05:
            warna = se.lerp_rgb((25, 25, 35), (255, 220, 120), nyala)
        else:
            warna = (20, 20, 28)
        d.rectangle((jx - jw / 2, jy - jh / 2, jx + jw / 2, jy + jh / 2), fill=warna + (a,), outline=(10, 10, 15, a))


def cahaya_jendela(img, x, y, w, h, nyala, kuat=0.7):
    if nyala > 0.05:
        se.glow(img, x, y - h * 0.62, max(w, 140) * 0.8, (255, 200, 100), kuat * nyala)


def lampu_gas(img, d, x, y, nyala=1.0, flick=0.0):
    se.glow(img, x, y - 230, 110 * (1 + 0.05 * math.sin(flick)), (255, 200, 110), 1.2 * nyala)
    d = ImageDraw.Draw(img, "RGBA")
    d.line((x, y, x, y - 210), fill=(30, 30, 35, 255), width=10)
    d.rectangle((x - 22, y - 260, x + 22, y - 210), fill=(255, 220, 140, int(200 * nyala) + 40), outline=(20, 20, 25, 255), width=4)
    d.polygon([(x - 30, y - 260), (x, y - 285), (x + 30, y - 260)], fill=(30, 30, 35, 255))
    return d


def pembangkit(img, x, y, s=1.0, asap_t=0.0, alpha=1.0, bendera_jepang=0.0):
    """Gedung pembangkit uap dengan cerobong & asap. (x, y) = tengah bawah."""
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    w, h = 460 * s, 230 * s
    d.rectangle((x - w / 2, y - h, x + w / 2, y), fill=(165, 120, 90, 255), outline=(60, 40, 25, 255), width=5)
    d.polygon([(x - w / 2 - 15, y - h), (x, y - h - 90 * s), (x + w / 2 + 15, y - h)], fill=(110, 70, 50, 255),
              outline=(60, 40, 25, 255))
    for i in range(4):
        jx = x - w / 2 + 60 * s + i * 110 * s
        d.rounded_rectangle((jx - 22 * s, y - h + 50 * s, jx + 22 * s, y - 60 * s), 20, fill=(255, 215, 120, 255),
                            outline=(60, 40, 25, 255), width=3)
    # cerobong
    cx = x + w / 2 - 70 * s
    d.rectangle((cx - 28 * s, y - h - 260 * s, cx + 28 * s, y - h), fill=(130, 80, 60, 255), outline=(60, 40, 25, 255),
                width=4)
    rng = random.Random(3)
    for i in range(8):
        f = ((asap_t * 0.4 + i / 8) % 1)
        rr = (20 + 60 * f) * s
        ax = cx + 70 * f * s + rng.uniform(-10, 10)
        ay = y - h - 270 * s - 260 * f * s
        d.ellipse((ax - rr, ay - rr, ax + rr, ay + rr), fill=(200, 200, 205, int(150 * (1 - f))))
    if bendera_jepang > 0.01:
        bx, by = x - w / 2 + 40 * s, y - h - 30 * s
        a = int(255 * bendera_jepang)
        d.line((bx, by, bx, by - 150 * s), fill=(40, 30, 20, a), width=6)
        d.rectangle((bx, by - 150 * s, bx + 120 * s, by - 70 * s), fill=(250, 250, 250, a), outline=(40, 30, 20, a), width=3)
        d.ellipse((bx + 60 * s - 25 * s, by - 110 * s - 25 * s, bx + 60 * s + 25 * s, by - 110 * s + 25 * s),
                  fill=(200, 30, 30, a))
    se.tempel(img, lap, alpha)


def kabel(d, titik, alpha=1.0, warna=(20, 20, 25)):
    a = int(255 * alpha)
    for (x0, y0), (x1, y1) in zip(titik, titik[1:]):
        pts = []
        for i in range(13):
            t = i / 12
            pts.append((lerp(x0, x1, t), lerp(y0, y1, t) + 30 * math.sin(math.pi * t)))
        d.line(pts, fill=tuple(warna) + (a,), width=4)


def tiang(d, x, y, tinggi=300):
    d.line((x, y, x, y - tinggi), fill=(60, 45, 30, 255), width=12)
    d.line((x - 50, y - tinggi + 30, x + 50, y - tinggi + 30), fill=(60, 45, 30, 255), width=10)
    return (x, y - tinggi + 30)


def trem(img, x, y, s=1.0, alpha=1.0):
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    w, h = 520 * s, 210 * s
    d.rounded_rectangle((x - w / 2, y - h, x + w / 2, y - 30 * s), 30, fill=(200, 160, 60, 255),
                        outline=(60, 40, 20, 255), width=5)
    d.rectangle((x - w / 2, y - 90 * s, x + w / 2, y - 30 * s), fill=(120, 50, 35, 255))
    for i in range(6):
        jx = x - w / 2 + 50 * s + i * 84 * s
        d.rectangle((jx - 28 * s, y - h + 30 * s, jx + 28 * s, y - 110 * s), fill=(255, 225, 140, 255),
                    outline=(60, 40, 20, 255), width=3)
    for ox in (-w / 3, w / 3):
        d.ellipse((x + ox - 32 * s, y - 60 * s, x + ox + 32 * s, y + 4 * s), fill=(40, 35, 30, 255))
    # pantograf ke kabel atas
    d.line((x, y - h, x - 50 * s, y - h - 90 * s, x + 30 * s, y - h - 130 * s), fill=(30, 30, 35, 255), width=6)
    d.text((x, y - 60 * s), "BETM", font=se.font("ui", int(30 * s)), fill=(255, 230, 170), anchor="mm")
    se.tempel(img, lap, alpha)


def kalender(img, cx, cy, bulan, tgl, alpha=1.0, s=1.0):
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    w, h = 330 * s, 350 * s
    d.rounded_rectangle((cx - w / 2 + 8, cy - h / 2 + 10, cx + w / 2 + 8, cy + h / 2 + 10), 20, fill=(0, 0, 0, 100))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 20, fill=(250, 245, 235, 255),
                        outline=(80, 60, 40, 255), width=4)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 90 * s), 20, fill=MERAH + (255,))
    d.text((cx, cy - h / 2 + 46 * s), bulan, font=se.font("ui", int(34 * s)), fill=PUTIH, anchor="mm")
    d.text((cx, cy + 50 * s), tgl, font=se.font("caption", int(160 * s)), fill=TINTA, anchor="mm")
    se.tempel(img, lap, alpha)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LANGIT.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # kota gelap di bawah
    rng = random.Random(11)
    x = -40
    while x < W + 40:
        w = rng.uniform(90, 160)
        h = rng.uniform(90, 200)
        rumah(d, x + w / 2, 1330, w, h, "kampung", 0.0)
        x += w + rng.uniform(10, 30)
    d.rectangle((0, 1330, W, H), fill=(10, 10, 16, 255))
    # bohlam berkedip lalu menyala
    kedip = 1.0 if c.t > 0.9 else (0.35 if int(c.t * 9) % 2 else 1.0)
    bohlam(img, 540, 760 + math.sin(c.t * 2) * 6, 1.05, kedip)
    d = ImageDraw.Draw(img, "RGBA")
    rng2 = random.Random(int(c.t * 8))
    for _ in range(6):
        ang = rng2.uniform(0, 2 * math.pi)
        r0, r1 = 210, rng2.uniform(250, 330)
        d.line((540 + math.cos(ang) * r0, 760 + math.sin(ang) * r0, 540 + math.cos(ang) * r1, 760 + math.sin(ang) * r1),
               fill=(255, 240, 150, 220), width=6)
    se.teks(d, (540, 400), "LISTRIK INI", 104, PUTIH, nama_font="caption", stroke=10, stroke_warna=(10, 10, 20))
    se.teks(d, (540, 515), "DULU DIREBUT!", 112, (255, 214, 10), nama_font="caption", stroke=10,
            stroke_warna=(10, 10, 20))
    # stempel merah
    s = back_out((c.t / c.d - 0.55) / 0.08)
    if s > 0.01:
        lap = Image.new("RGBA", (520, 180), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((10, 10, 510, 170), 20, outline=(210, 30, 30, 255), width=12)
        dl.text((260, 90), "DARI SIAPA?", font=se.font("caption", 76), fill=(210, 30, 30, 255), anchor="mm")
        lap = lap.rotate(-8, Image.BICUBIC, expand=True)
        lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
        se.tempel(img, lap, 1.0, (540 - lap.width // 2, 1180 - lap.height // 2))
    return img


def a_gelap(c):
    img = LANGIT.copy()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 1150, W, H), fill=(40, 35, 30, 255))
    d.polygon([(330, 1150), (750, 1150), (1080, 1600), (0, 1600)], fill=(70, 60, 45, 255))
    # rumah-rumah dengan lampu minyak redup
    for i, (x, w, h) in enumerate([(120, 200, 180), (930, 220, 200)]):
        rumah(d, x, 1150, w, h, "kampung", 0.25)
        se.glow(img, x, 1150 - h * 0.62, 70, (255, 170, 70), 0.8)
        d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.12, 0.22)
    if a > 0:
        for i, x in enumerate([330, 750]):
            if c.p(0.12 + i * 0.06, 0.2 + i * 0.06) > 0:
                d = lampu_gas(img, d, x, 1180 + i * 0, c.p(0.12 + i * 0.06, 0.2 + i * 0.06), c.t * 7 + i)
    se.kartu(img, 540, 520, "Abad ke-19 · Batavia", "malam = gelap", ABU, alpha=c.p(0.0, 0.08), tiang=False,
             skala=skala_muncul(c, 0.0))
    se.kartu(img, 540, 660, "Jalan besar: lampu gas", "", BIRU, alpha=c.p(0.25, 0.33), tiang=False,
             skala=skala_muncul(c, 0.25))
    se.kartu(img, 540, 790, "Rumah: lampu minyak", "", (150, 90, 30), alpha=c.p(0.6, 0.68), tiang=False,
             skala=skala_muncul(c, 0.6))
    hdr(img, "Sebelum ada listrik")
    return img


def a_1897(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out((c.t / c.d) / 0.12)
    se.teks(d, (540, 470), "1897", int(150 * s) + 1, (150, 30, 25), nama_font="caption", stroke=8,
            stroke_warna=(247, 236, 208))
    pembangkit(img, 540, 1190, 1.05, asap_t=c.t, alpha=c.p(0.0, 0.1))
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.3, 0.4)
    if a > 0:
        for i in range(3):
            ph = (c.t * 1.5 + i * 0.33) % 1
            kilat(d, 540 + (ph - 0.5) * 700, 1260, 0.9, a * (1 - abs(ph - 0.5) * 2))
    se.kartu(img, 540, 600, "Listrik pertama di Batavia", "", MERAH, alpha=c.p(0.05, 0.13), tiang=False,
             skala=skala_muncul(c, 0.05))
    se.kartu(img, 540, 1290, "Pembangkit tenaga uap · Gambir", "punya perusahaan Belanda", BIRU,
             alpha=c.p(0.4, 0.48), tiang=False, skala=skala_muncul(c, 0.4))
    hdr(img, "Lampu pertama menyala")
    return img


def a_trem(c):
    img = LANGIT.copy()
    se.tint(img, (60, 50, 90), 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 1180, W, H), fill=(60, 55, 50, 255))
    d.line((0, 1190, W, 1190), fill=(150, 150, 150, 255), width=6)
    d.line((0, 1215, W, 1215), fill=(150, 150, 150, 255), width=6)
    # tiang & kabel atas
    ujung = []
    for x in (80, 540, 1000):
        ujung.append(tiang(d, x, 1180, 420))
    kabel(d, ujung)
    for x in (80, 540, 1000):
        se.glow(img, x, 760, 90, (255, 210, 120), 1.0)
    d = ImageDraw.Draw(img, "RGBA")
    tx = lerp(1000, 80, clamp(c.t / c.d))
    trem(img, tx, 1185, 1.0)
    se.kartu(img, 540, 470, "10 April 1899", "trem listrik Batavia", MERAH, alpha=c.p(0.05, 0.13), tiang=False,
             skala=skala_muncul(c, 0.05))
    se.kartu(img, 540, 610, "Kota mulai terang…", "", (150, 110, 20), alpha=c.p(0.55, 0.63), tiang=False,
             skala=skala_muncul(c, 0.55))
    hdr(img, "Dua tahun kemudian")
    return img


def a_rehook(c):
    img = LANGIT.copy()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 1200, W, H), fill=(20, 20, 26, 255))
    se.teks(d, (540, 430), "TAPI… TERANGNYA", 74, PUTIH, nama_font="caption", stroke=8, stroke_warna=(10, 10, 20),
            alpha=c.p(0.0, 0.05))
    se.teks(d, (540, 520), "BUAT SIAPA?", 92, (255, 214, 10), nama_font="caption", stroke=9,
            stroke_warna=(10, 10, 20), alpha=c.p(0.05, 0.12))
    # kiri: bangunan terang
    terang = [("kantor", 150, 1200, 230, 190, 0.22, "Kantor pemerintah"),
              ("pabrik", 440, 1200, 230, 170, 0.32, "Pabrik gula"),
              ("eropa", 760, 1200, 220, 200, 0.42, "Rumah orang Eropa & orang kaya")]
    for jenis, x, y, w, h, t0, nama in terang:
        n = c.p(t0, t0 + 0.06)
        cahaya_jendela(img, x, y, w, h, n)
        d = ImageDraw.Draw(img, "RGBA")
        rumah(d, x, y, w, h, jenis, n)
    # kampung gelap di depan
    a = c.p(0.62, 0.7)
    if a > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        rng = random.Random(7)
        x = -20
        while x < W + 40:
            w = rng.uniform(100, 150)
            rumah(dl, x + w / 2, 1330, w, rng.uniform(80, 120), "kampung", 0.0)
            x += w + 15
        dl.rectangle((0, 1330, W, H), fill=(10, 10, 14, 255))
        se.tempel(img, lap, a)
    # label bergantian
    nama_aktif = None
    for _, _, _, _, _, t0, nama in terang:
        if c.p(t0, t0 + 0.02) > 0:
            nama_aktif = (nama, t0)
    if nama_aktif and c.p(0.62, 0.66) < 1:
        se.kartu(img, 540, 680, nama_aktif[0], "", (150, 110, 20), alpha=1 - c.p(0.6, 0.64), tiang=False,
                 skala=skala_muncul(c, nama_aktif[1], 0.06))
    se.kartu(img, 540, 680, "Kampung? Tetap gelap.", "", ABU, alpha=c.p(0.66, 0.73), tiang=False,
             skala=skala_muncul(c, 0.66))
    hdr(img, "Bagian paling nyesek", alpha=c.p(0.0, 0.08))
    return img


def a_menyebar(c):
    k = c.p(0.0, 0.3)
    kamera = se.kamera_antara(cam(-6.9, 109.9, 0.78), cam(-7.0, 110.3, 0.68), k)
    img, d = peta(kamera)
    se.tint(img, (10, 10, 30), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, layar(kamera, (-9.4, 108.2)), "JAWA", 46, TINTA, 0.85)
    kota = [(BATAVIA, "Batavia · 1897", 0.0, (90, -60)), (SURABAYA, "Surabaya · 1909", 0.14, (40, -60)),
            (BANDUNG, "PLTA sekitar Bandung", 0.36, (40, 70)), (SEMARANG, "Semarang", 0.5, (-60, -60)),
            (YOGYA, "Yogyakarta", 0.56, (0, 60))]
    for ll, nama, t0, (ox, oy) in kota:
        a = c.p(t0, t0 + 0.08)
        if a <= 0:
            continue
        x, y = layar(kamera, ll)
        se.glow(img, x, y, 90 * a, (255, 210, 110), 1.4)
        d = ImageDraw.Draw(img, "RGBA")
        kilat(d, x, y, 0.8 + 0.1 * math.sin(c.t * 6 + t0 * 10), a)
        label(d, (x + ox, y + oy), nama, 34, TINTA, a)
    se.kartu(img, 540, 470, "Listrik mulai menyebar", "", MERAH, alpha=c.p(0.02, 0.1), tiang=False,
             skala=skala_muncul(c, 0.02))
    b = c.p(0.68, 0.76)
    if b > 0:
        se.kartu(img, 540, 1280, "Tapi semuanya milik Belanda", "", (150, 30, 25), alpha=b, tiang=False,
                 skala=skala_muncul(c, 0.68))
    hdr(img, "1900-an sampai 1930-an")
    return img


def a_jepang(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    pembangkit(img, 540, 1180, 1.05, asap_t=c.t, alpha=1.0, bendera_jepang=c.p(0.3, 0.42))
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out((c.t / c.d) / 0.12)
    se.teks(d, (540, 450), "1942", int(140 * s) + 1, (255, 214, 120), nama_font="caption", stroke=8,
            stroke_warna=(20, 10, 5))
    se.kartu(img, 540, 590, "Jepang datang", "", (180, 30, 30), alpha=c.p(0.05, 0.13), tiang=False,
              skala=skala_muncul(c, 0.05))
    se.kartu(img, 540, 1280, "Semua pembangkit diambil alih", "", ABU, alpha=c.p(0.45, 0.53), tiang=False,
             skala=skala_muncul(c, 0.45))
    hdr(img, "Ganti penguasa")
    return img


def a_rebut(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # gedung kantor listrik & gas
    gx, gy = 540, 1120
    d.rectangle((gx - 300, gy - 260, gx + 300, gy), fill=(240, 236, 225, 255), outline=(60, 50, 40, 255), width=6)
    d.polygon([(gx - 330, gy - 260), (gx, gy - 360), (gx + 330, gy - 260)], fill=(120, 110, 105, 255),
              outline=(60, 50, 40, 255))
    for i in range(6):
        cx = gx - 250 + i * 100
        d.line((cx, gy - 240, cx, gy), fill=(205, 200, 190, 255), width=16)
    d.rectangle((gx - 220, gy - 220, gx + 220, gy - 170), fill=(60, 50, 40, 255))
    d.text((gx, gy - 195), "KANTOR LISTRIK & GAS", font=se.font("ui", 32), fill=PUTIH, anchor="mm")
    # bendera: Jepang turun, merah putih naik
    tx, ty = gx, gy - 360
    d.line((tx, ty, tx, ty - 200), fill=(50, 40, 30, 255), width=8)
    turun = c.p(0.25, 0.4)
    naik = c.p(0.42, 0.6)
    if naik <= 0:
        yb = ty - 200 + turun * 150
        a = int(255 * (1 - turun))
        d.rectangle((tx, yb, tx + 130, yb + 85), fill=(250, 250, 250, a), outline=(40, 30, 20, a), width=3)
        d.ellipse((tx + 45, yb + 22, tx + 85, yb + 62), fill=(200, 30, 30, a))
    else:
        yb = ty - 50 - naik * 150
        kib = math.sin(c.t * 5) * 6
        d.polygon([(tx, yb), (tx + 140, yb + kib), (tx + 140, yb + 42 + kib), (tx, yb + 42)], fill=(210, 30, 30, 255))
        d.polygon([(tx, yb + 42), (tx + 140, yb + 42 + kib), (tx + 140, yb + 84 + kib), (tx, yb + 84)],
                  fill=(250, 250, 250, 255), outline=(60, 50, 40, 255))
    # massa pemuda & buruh
    m = c.p(0.0, 0.3)
    rng = random.Random(8)
    for i in range(90):
        sx = rng.uniform(40, 1040)
        sy = rng.uniform(1150, 1330)
        x = lerp(sx, gx + (sx - 540) * 0.5, m * 0.6)
        y = lerp(sy + 120, sy, m) + math.sin(c.t * 8 + i) * 4
        warna = (200, 50, 40) if i % 3 else (245, 245, 240)
        se.prajurit(d, x, y, warna, 1.2)
    se.teks(d, (540, 400), "DIREBUT!", 100, (200, 30, 25), nama_font="caption", stroke=9,
            stroke_warna=(247, 236, 208), alpha=c.p(0.0, 0.05))
    se.kartu(img, 540, 505, "Pemuda & buruh listrik", "habis Proklamasi 1945", MERAH, alpha=c.p(0.1, 0.18),
             tiang=False, skala=skala_muncul(c, 0.1))
    b = c.p(0.7, 0.78)
    if b > 0:
        se.kartu(img, 540, 1240, "September 1945", "diserahkan ke Presiden Sukarno", HIJAU_TUA, alpha=b, tiang=False,
                 skala=skala_muncul(c, 0.7))
    hdr(img, "Ini jawabannya")
    return img


def a_harilistrik(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 300, 760, 300, (255, 200, 100), 1.0)
    kalender(img, 300, 760, "OKTOBER 1945", "27", c.p(0.0, 0.08), skala_muncul(c, 0.0))
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.1, 0.18)
    if a > 0:
        kilat(d, 780, 700, 2.4, a)
    se.kartu(img, 760, 900, "Jawatan Listrik", "dan Gas", BIRU, alpha=c.p(0.12, 0.2), tiang=False,
             skala=skala_muncul(c, 0.12))
    # stempel hari listrik nasional
    s = back_out((c.t / c.d - 0.42) / 0.08)
    if s > 0.01:
        lap = Image.new("RGBA", (860, 170), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((10, 10, 850, 160), 24, fill=(200, 52, 44, 240), outline=(255, 230, 160, 255), width=6)
        dl.text((430, 85), "HARI LISTRIK NASIONAL", font=se.font("caption", 66), fill=PUTIH, anchor="mm")
        lap = lap.rotate(-4, Image.BICUBIC, expand=True)
        lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
        se.tempel(img, lap, 1.0, (540 - lap.width // 2, 1080 - lap.height // 2))
    se.kartu(img, 540, 1250, "Belakangan → PLN", "", HIJAU_TUA, alpha=c.p(0.75, 0.83), tiang=False,
             skala=skala_muncul(c, 0.75))
    hdr(img, "Milik kita sendiri")
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
    a = c.p(0.02, 0.1) * (1 - c.p(0.58, 0.64))
    if a > 0:
        se.panel(img, (90, 440, 990, 1180), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 530), "± 11 ribu desa", 62, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 605), "masih nunggu listrik", 46, TINTA, nama_font="judul", alpha=a)
        b2 = c.p(0.2, 0.28) * a
        if b2 > 0:
            lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            bohlam(lap, 540, 760, 0.42, 1.0)
            se.tempel(img, lap, b2)
            d = ImageDraw.Draw(img, "RGBA")
            se.teks(d, (540, 1000), "Lain kali mati lampu, inget:", 42, TINTA, nama_font="judul", alpha=b2)
            se.teks(d, (540, 1075), "listrik ini dulu direbut.", 50, (170, 30, 20), nama_font="caption", alpha=b2)
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
    Adegan("hook", "Listrik di rumahmu ini, dulu direbut. Lagi rame mati lampu, kan? Kesel, pasti. "
                   "Tapi, direbut dari siapa? Dan siapa yang berani?",
           a_hook, transisi=False),
    Adegan("gelap", "Abad kesembilan belas, malam di Batavia itu gelap. Jalan besar pakai lampu gas. "
                    "Rumah-rumah, cuma pakai lampu minyak.", a_gelap),
    Adegan("1897", "Tahun delapan belas sembilan puluh tujuh, listrik pertama menyala di Batavia. "
                   "Pembangkitnya tenaga uap, di Gambir, punya perusahaan Belanda.", a_1897),
    Adegan("trem", "Dua tahun kemudian, trem listrik mulai jalan di Batavia. Kota ini mulai terang.", a_trem),
    Adegan("rehook", "Tapi bagian paling nyesek-nya, ini. Terangnya buat siapa? Kantor pemerintah, pabrik gula, "
                     "rumah orang Eropa dan orang kaya. Kampung? Tetap gelap.", a_rehook),
    Adegan("menyebar", "Listrik lalu menyebar. Surabaya, tahun sembilan belas sembilan. Lalu, "
                       "pembangkit tenaga air di sekitar Bandung. Tapi semuanya, milik Belanda.", a_menyebar),
    Adegan("jepang", "Lalu tahun sembilan belas empat puluh dua, Jepang datang. "
                     "Semua pembangkit listrik diambil alih Jepang.", a_jepang),
    Adegan("rebut", "Nah, ini jawabannya. Habis proklamasi, para pemuda dan buruh listrik bergerak. "
                    "Kantor-kantor listrik dan gas, mereka rebut dari Jepang. Bulan September, "
                    "semuanya diserahkan ke Presiden Sukarno.", a_rebut),
    Adegan("harilistrik", "Dua puluh tujuh Oktober sembilan belas empat puluh lima, dibentuk Jawatan Listrik dan Gas. "
                          "Tanggal itu sekarang jadi Hari Listrik Nasional. Belakangan, namanya jadi PLN.",
           a_harilistrik),
    Adegan("penutup", "Sekarang pun, masih sekitar sebelas ribu desa nunggu listrik. Jadi, lain kali mati lampu, "
                      "inget: listrik ini dulu direbut. Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
