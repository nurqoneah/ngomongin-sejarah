"""Shorts ±88 detik: Dulu bolos kerja bisa dipidana. Kuli kontrak di kebun tembakau Deli, Koeli Ordonansi 1880
dan poenale sanctie, sampai akhirnya dihapus bukan karena kasihan, tapi karena takut pasar Amerika.

Tren: penetapan UMP 2027 (batas 21 November 2026).
Visual: kontrak + cambuk + teks besar, peta Sumatra/Deli + daun tembakau, rute kuli dari Penang & Jawa (titik),
kontrak 3 tahun + jam 12 jam, dokumen ordonansi 1880, daftar pelanggaran dicoret, pamflet 1902, laporan Rhemrev
masuk laci, kapal tembakau ke Amerika dihadang, penutup maskot.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Peta, back_out, clamp, lerp

NAMA_FILE = "kuli-kontrak-deli-1880-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "KULI KONTRAK DELI"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KUNING = (255, 214, 10)
GELAP = (10, 10, 20)
KREM = (247, 236, 208)
KREM_LABEL = (240, 225, 190)
HIJAU_TUA = (30, 110, 60)
HIJAU_DAUN = (70, 120, 45)
BIRU = (30, 80, 150)
COKLAT = (120, 80, 40)
MERAH_TUA = (150, 30, 25)
TEMBAKAU = (150, 105, 50)

# ------------------------------------------------------------------ pengaman PIL

def _kotak(box):
    if len(box) == 2:
        (x0, y0), (x1, y1) = box
    else:
        x0, y0, x1, y1 = box
    x0, x1 = sorted((int(round(x0)), int(round(x1))))
    y0, y1 = sorted((int(round(y0)), int(round(y1))))
    return [x0, y0, max(x1, x0 + 1), max(y1, y0 + 1)]


_rr_asli = ImageDraw.ImageDraw.rounded_rectangle
_el_asli = ImageDraw.ImageDraw.ellipse


def _rr_aman(self, xy, radius=0, *args, **kw):
    b = _kotak(xy)
    r = int(min(radius, (b[2] - b[0]) // 2 - 1, (b[3] - b[1]) // 2 - 1))
    if r < 1:
        return self.rectangle(b, kw.get("fill", args[0] if args else None), kw.get("outline"), kw.get("width", 1))
    return _rr_asli(self, b, r, *args, **kw)


def _el_aman(self, xy, *args, **kw):
    return _el_asli(self, _kotak(xy), *args, **kw)


ImageDraw.ImageDraw.rounded_rectangle = _rr_aman
ImageDraw.ImageDraw.ellipse = _el_aman

# ------------------------------------------------------------------ peta

print("  menyiapkan peta Sumatra...")
NUSA = Peta(88, 120, -22, 18, 72, [], [(3.0, 98.5, 0.5), (0.0, 100.5, 0.6), (-3.0, 102.5, 0.5), (-7.2, 110.0, 0.4)],
            seed=35, darat=pd.SEMUA)

DELI = (3.6, 98.7)
PENANG = (5.4, 100.3)
BATAVIA = (-6.1, 106.8)
SEMARANG = (-6.95, 110.4)

print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 35, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (8, 12, 24), 0.66)


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


def titik_kota(d, x, y, nama, alpha=1.0, warna=(255, 200, 60), dy=50, uk=40, t=0.0, dx=0):
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    r = 15 + 3 * math.sin(t * 5)
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=PUTIH + (a,), width=4)
    label(d, (x + dx, y + dy), nama, uk, alpha=alpha)


def stempel(img, isi, cx, cy, s, uk=76, sudut=-8, warna=(210, 30, 30)):
    if s <= 0.01:
        return
    f = se.font("caption", uk)
    lw = int(f.getlength(isi)) + 80
    lap = Image.new("RGBA", (lw, uk + 90), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((10, 10, lw - 10, uk + 80), 22, fill=(247, 236, 208, 215), outline=tuple(warna) + (255,),
                         width=12)
    dl.text((lw / 2, (uk + 90) / 2), isi, font=f, fill=tuple(warna) + (255,), anchor="mm")
    lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, 1.0, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


def pita(img, y, isi, warna_garis=(170, 30, 20), uk=56, alpha=1.0, x0=90, x1=990, tinggi=110):
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((x0, y - tinggi / 2, x1, y + tinggi / 2), 30, fill=(247, 236, 208, 242),
                         outline=tuple(warna_garis) + (255,), width=6)
    se.tempel(img, lap, alpha)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, ((x0 + x1) / 2, y), isi, uk, warna_garis, nama_font="caption", alpha=alpha)


def kertas(img, cx, cy, w, h, judul, baris=(), s=1.0, sudut=0.0, alpha=1.0, warna_judul=MERAH_TUA, uk_judul=44,
           uk_baris=32, ttd=False):
    """Dokumen kertas tua dengan judul + baris teks (ilustrasi, bukan replika)."""
    if alpha <= 0.01 or s <= 0.05:
        return
    sw, sh = int(w * s), int(h * s)
    lap = Image.new("RGBA", (sw + 40, sh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rectangle((22, 24, sw + 22, sh + 24), fill=(0, 0, 0, 90))
    d.rectangle((12, 12, sw + 12, sh + 12), fill=(244, 232, 200, 255), outline=(110, 80, 45, 255),
                width=max(2, int(5 * s)))
    d.text((12 + sw / 2, 12 + 60 * s), judul, font=se.font("caption", int(uk_judul * s)), fill=warna_judul, anchor="mm")
    d.line((12 + 40 * s, 12 + 100 * s, 12 + sw - 40 * s, 12 + 100 * s), fill=(110, 80, 45, 255),
           width=max(1, int(3 * s)))
    y = 12 + 150 * s
    for b in baris:
        if b:
            d.text((12 + sw / 2, y), b, font=se.font("judul", int(uk_baris * s)), fill=(50, 35, 25), anchor="mm")
        else:
            for k in range(2):
                yy = y - 10 * s + k * 22 * s
                d.line((12 + 60 * s, yy, 12 + sw - 60 * s, yy), fill=(120, 95, 65, 160), width=max(1, int(3 * s)))
        y += 58 * s
    if ttd:
        yy = 12 + sh - 70 * s
        pts = [(12 + sw * 0.55 + k * 9 * s, yy + math.sin(k * 1.3) * 16 * s) for k in range(22)]
        d.line(pts, fill=(30, 40, 110, 255), width=max(2, int(4 * s)))
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def cambuk(d, x, y, s=1.0, t=0.0, alpha=1.0, ayun=0.0):
    """Cambuk: gagang + tali melengkung. (x, y) = pangkal gagang."""
    a = int(255 * alpha)
    d.line((x, y, x + 70 * s, y - 120 * s), fill=(90, 55, 25, a), width=max(3, int(22 * s)))
    d.ellipse((x - 14 * s, y - 14 * s, x + 14 * s, y + 14 * s), fill=(60, 35, 15, a))
    pts = []
    for k in range(30):
        u = k / 29
        px = x + 70 * s + u * 420 * s
        py = y - 120 * s - math.sin(u * math.pi) * (160 - ayun * 220) * s + u * u * 260 * s \
            + math.sin(u * 8 + t * 6) * 10 * s
        pts.append((px, py))
    d.line(pts, fill=(70, 40, 18, a), width=max(2, int(12 * s)), joint="curve")


def daun(d, cx, cy, s=1.0, sudut=0.0, warna=HIJAU_DAUN, alpha=1.0):
    """Daun tembakau sederhana (elips runcing + tulang daun)."""
    a = int(255 * alpha)
    rad = math.radians(sudut)
    pts = []
    for k in range(41):
        u = k / 40 * 2 * math.pi
        px = math.cos(u) * 150 * s
        py = math.sin(u) * 62 * s * (1 - 0.35 * math.cos(u))
        pts.append((cx + px * math.cos(rad) - py * math.sin(rad), cy + px * math.sin(rad) + py * math.cos(rad)))
    d.polygon(pts, fill=tuple(warna) + (a,), outline=(35, 60, 25, a))
    p0 = (cx - 150 * s * math.cos(rad), cy - 150 * s * math.sin(rad))
    p1 = (cx + 150 * s * math.cos(rad), cy + 150 * s * math.sin(rad))
    d.line((p0, p1), fill=(200, 215, 150, a), width=max(2, int(5 * s)))


def kuli(d, x, y, s=1.0, warna=(60, 45, 35), alpha=1.0, caping=True):
    """Siluet pekerja tanpa wajah, bertopi caping."""
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    d.ellipse((x - 9 * s, y - 50 * s, x + 9 * s, y - 32 * s), fill=c)
    if caping:
        d.polygon([(x - 22 * s, y - 44 * s), (x, y - 62 * s), (x + 22 * s, y - 44 * s)], fill=c)
    d.rounded_rectangle((x - 12 * s, y - 30 * s, x + 12 * s, y), int(6 * s) + 1, fill=c)


def kapal(d, x, y, s=1.0, alpha=1.0, warna=(60, 60, 70), t=0.0, muatan=True):
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    y = y + math.sin(t * 3) * 4 * s
    d.polygon([(x - 120 * s, y - 30 * s), (x + 120 * s, y - 30 * s), (x + 90 * s, y + 20 * s), (x - 95 * s, y + 20 * s)],
              fill=c)
    d.rectangle((x - 40 * s, y - 70 * s, x + 40 * s, y - 30 * s), fill=c)
    d.rectangle((x - 10 * s, y - 110 * s, x + 10 * s, y - 70 * s), fill=c)
    if muatan:
        for k in range(3):
            bx = x - 100 * s + k * 28 * s
            d.rectangle((bx, y - 58 * s, bx + 24 * s, y - 32 * s), fill=TEMBAKAU + (a,), outline=(80, 50, 20, a))
        for k in range(2):
            bx = x + 50 * s + k * 28 * s
            d.rectangle((bx, y - 58 * s, bx + 24 * s, y - 32 * s), fill=TEMBAKAU + (a,), outline=(80, 50, 20, a))


def silang(d, cx, cy, r, k, alpha=1.0, tebal=14):
    if k <= 0:
        return
    a = int(255 * alpha)
    k1, k2 = clamp(k * 2), clamp(k * 2 - 1)
    d.line((cx - r, cy - r, lerp(cx - r, cx + r, k1), lerp(cy - r, cy + r, k1)), fill=(220, 30, 25, a), width=tebal)
    if k2 > 0:
        d.line((cx + r, cy - r, lerp(cx + r, cx - r, k2), lerp(cy - r, cy + r, k2)), fill=(220, 30, 25, a), width=tebal)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 930, 540, (230, 60, 40), 1.05 + 0.3 * math.sin(c.t * 4))
    goyang = math.sin(c.t * 2.0) * 2
    kertas(img, 540, 930, 560, 600, "KONTRAK KULI", ["", "", "3 TAHUN", "", ""], 1.0, sudut=-4 + goyang, ttd=True)
    d = ImageDraw.Draw(img, "RGBA")
    ay = 0.5 + 0.5 * math.sin(c.t * 3.2)
    cambuk(d, 150, 1270, 1.0, c.t, 1.0, ayun=ay)
    se.teks(d, (540, 410), "BOLOS KERJA", 104, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 530), "BISA DIPIDANA", 112, KUNING, nama_font="caption", stroke=11, stroke_warna=GELAP)
    stempel(img, "DELI, 1880", 860, 700, 0.6, uk=56, sudut=10)
    a = c.p(0.22, 0.3)
    if a > 0:
        se.kartu(img, 230, 700, "Lagi rame:", "penetapan UMP 2027", HIJAU_TUA, alpha=a, tiang=False,
                 skala=skala_muncul(c, 0.22))
    a2 = c.p(0.62, 0.7)
    if a2 > 0:
        pita(img, 1290, "Kenapa akhirnya dihapus?", uk=58, alpha=a2)
    return img


def a_deli(c):
    kamera = se.kamera_antara(cam(NUSA, -1.0, 103.0, 0.75), cam(NUSA, 2.2, 99.2, 2.0), c.p(0.0, 0.6))
    img = se.render_peta(NUSA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    dx, dy = layar(NUSA, kamera, DELI)
    a = c.p(0.1, 0.2)
    if a > 0:
        se.glow(img, dx, dy, 160, (255, 200, 80), 1.2 * a)
        d = ImageDraw.Draw(img, "RGBA")
        titik_kota(d, dx, dy, "Deli (Medan)", a, (200, 52, 44), t=c.t, dx=-40)
    se.kartu(img, 540, 470, "Jacob Nienhuys", "pengusaha Belanda, 1863", BIRU, alpha=c.p(0.05, 0.12), tiang=False,
             skala=skala_muncul(c, 0.05))
    k = c.p(0.42, 0.62)
    if k > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        rng = random.Random(5)
        for i in range(7):
            f = clamp(k * 7 - i)
            if f <= 0:
                continue
            x = 180 + (i % 4) * 240 + rng.uniform(-30, 30)
            y = 1020 + (i // 4) * 170 + rng.uniform(-20, 20)
            daun(dl, x, y, 0.75 * back_out(f), sudut=rng.uniform(-35, 35), alpha=1.0)
        se.tempel(img, lap, 1.0)
    a2 = c.p(0.72, 0.8)
    if a2 > 0:
        pita(img, 880, "Daun pembungkus cerutu", warna_garis=HIJAU_TUA, uk=54, alpha=a2)
    hdr(img, "Sumatra Timur, 1863")
    return img


def a_kuli_datang(c):
    kamera = se.kamera_antara(cam(NUSA, -1.0, 104.5, 0.7), cam(NUSA, -1.0, 104.6, 0.74), c.p(0.0, 1.0))
    img = se.render_peta(NUSA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    dx, dy = layar(NUSA, kamera, DELI)
    titik_kota(d, dx, dy, "Deli", 1.0, (200, 52, 44), t=c.t, dx=-60, dy=-50)
    rute = [
        ([PENANG, (4.6, 99.6), DELI], "Penang", "dari Tiongkok", PENANG, 0.08, (160, 30, 30)),
        ([SEMARANG, (-5.5, 109.0), (-3.0, 107.5), (0.5, 104.8), (2.6, 101.2), DELI], "Jawa", "dari Jawa",
         SEMARANG, 0.36, (30, 80, 150)),
    ]
    for pts_ll, nama, sub, asal, mulai, warna in rute:
        a = c.p(mulai, mulai + 0.08)
        if a <= 0:
            continue
        ax, ay = layar(NUSA, kamera, asal)
        titik_kota(d, ax, ay, nama, a, t=c.t, dx=0 if nama == "Jawa" else 70, dy=55)
        pts = [layar(NUSA, kamera, ll) for ll in pts_ll]
        k = c.p(mulai + 0.04, mulai + 0.3)
        se.garis_putus(d, pts, k, warna, tebal=8)
        # titik-titik kuli bergerak di sepanjang rute
        for i in range(12):
            u = (k * 1.2 - i * 0.07)
            if 0 < u < 1:
                (px, py), _ = se.titik_di_jalur(pts, u)
                d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=tuple(warna) + (255,), outline=PUTIH + (255,), width=2)
    se.kartu(img, 540, 470, "Butuh tenaga banyak", "kebun makin luas", MERAH, alpha=c.p(0.0, 0.06), tiang=False,
             skala=skala_muncul(c, 0.0))
    a2 = c.p(0.7, 0.78)
    if a2 > 0:
        pita(img, 1280, "PULUHAN RIBU KULI", uk=64, alpha=a2)
    hdr(img, "Kuli didatangkan")
    return img


def a_kontrak(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # calo menyodorkan uang muka
    a = c.p(0.0, 0.08)
    kuli(d, 240, 1250, 5.0, (55, 40, 30), a)
    kuli(d, 820, 1250, 5.0, (95, 70, 50), a, caping=False)
    se.kartu(img, 240, 1300, "Kuli", "", HIJAU_TUA, alpha=a, tiang=False)
    se.kartu(img, 820, 1300, "Calo", "", MERAH, alpha=a, tiang=False)
    k = c.p(0.12, 0.3)
    if k > 0:
        # koin uang muka melayang ke kuli
        for i in range(4):
            f = clamp(k * 4 - i * 0.6)
            if 0 < f:
                x = lerp(760, 320, f)
                y = lerp(900, 950, f) - math.sin(f * math.pi) * 120 - i * 26
                d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=(230, 190, 60, 255), outline=(140, 100, 20, 255),
                          width=4)
        se.teks(d, (540, 800), "uang muka", 50, COKLAT, nama_font="tangan", stroke=5, stroke_warna=KREM,
                alpha=c.p(0.15, 0.22))
    a2 = c.p(0.35, 0.43)
    if a2 > 0:
        kertas(img, 540, 760, 520, 560, "KONTRAK", ["", "", "", "", ""], skala_muncul(c, 0.35) * 0.95, sudut=3,
               alpha=a2, ttd=c.t / c.d > 0.48)
        d = ImageDraw.Draw(img, "RGBA")
        stempel(img, "3 TAHUN", 540, 760, skala_muncul(c, 0.5, 0.08) * 0.95, uk=90, sudut=-8)
    a3 = c.p(0.68, 0.76)
    if a3 > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.ellipse((380, 1020, 700, 1340), fill=(250, 245, 235, 255), outline=(60, 45, 30, 255), width=8)
        sudut = c.t * 2.5
        dl.line((540, 1180, 540 + 110 * math.sin(sudut), 1180 - 110 * math.cos(sudut)), fill=(170, 30, 20, 255),
                width=8)
        dl.line((540, 1180, 540, 1100), fill=TINTA + (255,), width=10)
        se.tempel(img, lap, a3)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 450), "12 JAM SEHARI", 96, (170, 30, 20), nama_font="caption", stroke=8, stroke_warna=KREM,
                alpha=a3)
    hdr(img, "Teken kontrak")
    return img


def a_ordonansi(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 880, 520, (230, 190, 90), 0.9)
    s = skala_muncul(c, 0.04, 0.12)
    kertas(img, 540, 860, 700, 760, "KOELIE ORDONNANTIE", ["Sumatra Timur", "", "", "", "", ""], s, sudut=-2,
           alpha=c.p(0.0, 0.08), uk_judul=52, uk_baris=40)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 430), "1880", 120, KUNING, nama_font="caption", stroke=9, stroke_warna=GELAP,
            alpha=c.p(0.0, 0.06))
    stempel(img, "POENALE SANCTIE", 540, 1000, skala_muncul(c, 0.5, 0.08) * 0.9, uk=72, sudut=-7)
    a = c.p(0.66, 0.74)
    if a > 0:
        pita(img, 1270, "= sanksi PIDANA buat kuli", uk=52, alpha=a)
    hdr(img, "Aturan pemerintah kolonial")
    return img


def a_hukuman(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 900, 520, (200, 50, 40), 0.9 + 0.2 * math.sin(c.t * 5))
    se.panel(img, (110, 410, 970, 560), alpha=c.p(0.0, 0.05))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 485), "TAPI BAGIAN PALING NGERI…", 52, (170, 30, 20), nama_font="caption",
            alpha=c.p(0.0, 0.05))
    item = [("Malas", 0.1), ("Membantah", 0.18), ("Kabur dari kebun", 0.26)]
    for i, (isi, m) in enumerate(item):
        a = c.p(m, m + 0.06)
        if a <= 0:
            continue
        y = 660 + i * 120
        se.panel(img, (170, y - 48, 910, y + 48), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (500, y), isi, 52, TINTA, nama_font="judul", alpha=a)
        silang(d, 830, y, 30, c.p(m + 0.04, m + 0.1), tebal=12)
    stempel(img, "DIHUKUM!", 540, 1060, skala_muncul(c, 0.36, 0.08) * 0.9, uk=80, sudut=-6)
    a2 = c.p(0.5, 0.58)
    if a2 > 0:
        se.kartu(img, 300, 1220, "Pemilik kebun =", "polisi + hakim", MERAH, alpha=a2, tiang=False,
                 skala=skala_muncul(c, 0.5))
        d = ImageDraw.Draw(img, "RGBA")
        ay = 0.5 + 0.5 * math.sin(c.t * 4)
        cambuk(d, 620, 1300, 0.65, c.t, c.p(0.7, 0.78), ayun=ay)
    hdr(img, "Poenale sanctie")
    return img


def a_pamflet(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 470, "Mr. J. van den Brand", "pengacara di Medan", BIRU, alpha=c.p(0.0, 0.06), tiang=False,
             skala=skala_muncul(c, 0.0))
    s = skala_muncul(c, 0.12, 0.12)
    kertas(img, 540, 860, 600, 620, "1902", ["De Millioenen", "uit Deli", "", "", ""], s * 0.95, sudut=-3,
           alpha=c.p(0.1, 0.18), uk_judul=60, uk_baris=54)
    a = c.p(0.45, 0.53)
    if a > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (300, 1250), "Untung jutaan", 50, HIJAU_TUA, nama_font="caption", stroke=5, stroke_warna=KREM,
                alpha=a)
        se.teks(d, (780, 1250), "dibayar nyawa", 50, (170, 30, 20), nama_font="caption", stroke=5,
                stroke_warna=KREM, alpha=c.p(0.62, 0.7))
        se.garis_putus(d, [(470, 1250), (600, 1250)], c.p(0.55, 0.65), TINTA, tebal=6)
    stempel(img, "BIKIN HEBOH", 800, 640, skala_muncul(c, 0.3, 0.08) * 0.6, uk=60, sudut=10)
    hdr(img, "Pamflet yang bikin geger")
    return img


def a_rhemrev(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 470, "Jaksa Rhemrev", "diutus pemerintah, 1903", BIRU, alpha=c.p(0.0, 0.06), tiang=False,
             skala=skala_muncul(c, 0.0))
    # laci meja
    d.rectangle((150, 1080, 930, 1300), fill=(110, 70, 38, 255), outline=(60, 35, 18, 255), width=6)
    d.rectangle((300, 1120, 780, 1260), fill=(95, 60, 32, 255), outline=(50, 30, 15, 255), width=5)
    d.rounded_rectangle((500, 1175, 580, 1200), 10, fill=(200, 170, 90, 255))
    turun = c.p(0.7, 0.88)
    y = lerp(800, 1190, turun)
    a = c.p(0.1, 0.18) * (1 - c.p(0.86, 0.9))
    if a > 0:
        kertas(img, 540, y, 420, 460, "LAPORAN", ["Kuli di", "Sumatra Timur", "", ""], 1.0 - 0.35 * turun, alpha=a,
               uk_judul=50, uk_baris=36)
    stempel(img, "TUDUHAN TERBUKTI", 540, 720, skala_muncul(c, 0.3, 0.08) * 0.78 * (1 - c.p(0.62, 0.68)), uk=64,
            sudut=-6)
    a2 = c.p(0.86, 0.92)
    if a2 > 0:
        stempel(img, "DISIMPAN DI LACI", 540, 880, skala_muncul(c, 0.86, 0.08) * 0.8, uk=64, sudut=-5,
                warna=(60, 60, 70))
    hdr(img, "Laporan Rhemrev")
    return img


def a_payoff(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 950, 520, (90, 150, 230), 0.9)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 430), "BUKAN KARENA KASIHAN", 66, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP,
            alpha=c.p(0.0, 0.05))
    # laut + kapal tembakau menuju Amerika, dihadang
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rectangle((0, 960, W, 1320), fill=(35, 70, 120, 255))
    for k in range(8):
        yy = 990 + k * 40
        dl.line([(x, yy + math.sin(x / 40 + c.t * 3 + k) * 6) for x in range(0, W + 40, 40)],
                fill=(90, 140, 200, 160), width=3)
    se.tempel(img, lap, c.p(0.06, 0.12))
    d = ImageDraw.Draw(img, "RGBA")
    maju = c.p(0.1, 0.4)
    kapal(d, lerp(-160, 470, maju), 1010, 1.5, c.p(0.06, 0.12), (70, 60, 55), t=c.t)
    a = c.p(0.12, 0.2)
    se.kartu(img, 820, 640, "Amerika, 1930", "UU Tarif: tolak barang", BIRU, alpha=a, tiang=False,
             skala=skala_muncul(c, 0.12))
    se.teks(d, (820, 760), "hasil kerja paksa", 40, PUTIH, nama_font="tangan", stroke=5, stroke_warna=GELAP, alpha=a)
    a2 = c.p(0.32, 0.38)
    if a2 > 0:
        stempel(img, "DITOLAK MASUK", 760, 900, skala_muncul(c, 0.32, 0.08) * 0.75, uk=60, sudut=-7)
    a3 = c.p(0.55, 0.62)
    if a3 > 0:
        se.panel(img, (110, 1150, 970, 1310), alpha=a3)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1195), "± 1931: sanksi pidana dihentikan", 42, TINTA, nama_font="judul", alpha=a3)
        se.teks(d, (540, 1265), "1941: aturan kuli dicabut", 42, (170, 30, 20), nama_font="judul",
                alpha=c.p(0.78, 0.84))
    hdr(img, "Kenapa akhirnya dihapus?")
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
    se.glow(img, 540, 960, 480, (230, 190, 90), 0.9)
    a = c.p(0.0, 0.08) * (1 - c.p(0.6, 0.64))
    if a > 0:
        kertas(img, 540, 1080, 420, 420, "KONTRAK KERJA", ["", "Upah minimum", "Hak berhenti", ""], 0.9, sudut=4,
               alpha=a, warna_judul=HIJAU_TUA, uk_judul=40, uk_baris=36)
        se.panel(img, (90, 420, 990, 760), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 495), "Upah minimum, hak resign,", 44, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 590), "dulu nggak gratis", 66, (170, 30, 20), nama_font="caption", alpha=c.p(0.1, 0.16) * a)
        se.teks(d, (540, 685), "semuanya diperjuangkan.", 44, TINTA, nama_font="judul", alpha=c.p(0.2, 0.26) * a)
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
    Adegan("hook", "Dulu, bolos kerja bisa dihukum pidana. Lagi nunggu UMP dua ribu dua puluh tujuh? Buruh di Sumatra dulu punya aturan yang jauh lebih ngeri. Dan cara aturan ini hilang, bikin kaget.",
           a_hook, transisi=False),
    Adegan("deli", "Tahun delapan belas enam puluh tiga, pengusaha Belanda Jacob Nienhuys buka kebun tembakau di Deli, dekat Medan. Daunnya jadi pembungkus cerutu kelas dunia.",
           a_deli),
    Adegan("kuli", "Kebun makin luas, butuh tenaga banyak. Didatangkanlah puluhan ribu kuli, dari Tiongkok lewat Penang, lalu dari Jawa.",
           a_kuli_datang),
    Adegan("kontrak", "Banyak yang dibujuk calo, dikasih uang muka, lalu teken kontrak tiga tahun. Kerjanya bisa dua belas jam sehari.",
           a_kontrak),
    Adegan("ordonansi", "Tahun delapan belas delapan puluh, lahir Koeli Ordonansi. Isinya ada poenale sanctie: sanksi pidana buat kuli.",
           a_ordonansi),
    Adegan("hukuman", "Tapi bagian paling ngeri: malas, membantah, apalagi kabur, bisa dihukum. Pemilik kebun jadi polisi sekaligus hakim. Cambuk jadi hal biasa.",
           a_hukuman),
    Adegan("pamflet", "Tahun sembilan belas nol dua, pengacara Medan, van den Brand, nulis pamflet heboh: untung jutaan pemegang saham dibayar pakai nyawa kuli.",
           a_pamflet),
    Adegan("rhemrev", "Pemerintah kirim jaksa Rhemrev buat menyelidiki. Hasilnya, sebagian besar tuduhan terbukti. Tapi laporannya malah disimpan, nggak diumumkan.",
           a_rhemrev),
    Adegan("payoff", "Terus kenapa akhirnya dihapus? Bukan karena kasihan. Amerika bikin undang-undang: barang hasil kerja paksa dilarang masuk. Takut tembakaunya ditolak, pengusaha Deli berhenti pakai sanksi pidana sekitar tahun tiga puluh satu. Tahun empat puluh satu, aturan kuli dicabut total.",
           a_payoff),
    Adegan("penutup", "Jadi, upah minimum dan hak resign itu bukan hadiah. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
