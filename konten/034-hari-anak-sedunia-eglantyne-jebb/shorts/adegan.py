"""Shorts ±88 detik: Kenapa Hari Anak Sedunia 20 November? Berawal dari Eglantyne Jebb yang DITANGKAP gara-gara
selebaran foto anak kelaparan (London, 1919).

Tren: "hari anak sedunia" #1 di Google Trends Indonesia (20 November 2026).
Visual: selebaran foto anak kurus + borgol, peta Eropa + blokade kapal, Trafalgar Square + selebaran beterbangan,
palu sidang + denda £5, uang £5 terbang ke kotak "Save the Children", kapal bantuan 600 ton, gulungan deklarasi
Jenewa 1924, kalender 20 NOV 1959 & 1989, peta Nusantara + 1990, penutup maskot.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Peta, back_out, clamp, lerp

NAMA_FILE = "hari-anak-sedunia-eglantyne-jebb-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "HARI ANAK SEDUNIA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KUNING = (255, 214, 10)
GELAP = (10, 10, 20)
KREM = (247, 236, 208)
KREM_LABEL = (240, 225, 190)
HIJAU_TUA = (30, 110, 60)
BIRU = (30, 80, 150)
BIRU_PBB = (70, 140, 210)
COKLAT = (120, 80, 40)
ORANYE = (230, 120, 30)
MERAH_TUA = (150, 30, 25)
SEPIA = (200, 178, 140)
POLISI = (25, 30, 55)

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

# ------------------------------------------------------------------ garis pantai Eropa (disederhanakan, dari 023)

AA = pd.ASIA_AFRIKA
_i_djibouti = AA.index((12, 43.4))
_i_aden = AA.index((12.8, 45))
_i_ujung = AA.index((45, 125))
AFRIKA_BARAT = [(35.8, -5.9), (34.0, -6.8), (31.5, -9.8), (28.0, -13.0), (24.0, -15.9), (21.0, -17.0),
                (15.0, -17.4), (10.0, -14.8), (7.5, -13.0), (5.0, -7.5), (5.0, -4.0), (6.0, 1.0), (6.4, 3.4),
                (4.3, 6.0), (4.0, 9.0), (1.0, 9.5), (-5.0, 12.0), (-17.0, 11.8), (-22.0, 14.4), (-29.0, 16.5),
                (-34.5, 18.5)]
LAUT_MERAH_BARAT = [(15.5, 39.5), (18.0, 38.5), (22.0, 36.8), (26.0, 34.3), (29.9, 32.5)]
LAUT_MERAH_TIMUR = [(28.0, 34.6), (24.0, 37.5), (20.0, 40.0), (16.0, 42.7), (12.7, 43.6)]
EROPA_UTARA = [(66.0, 125.0), (66.0, 40.0), (64.5, 40.0), (60.5, 30.0), (59.5, 28.0), (59.4, 24.0), (57.5, 24.2),
               (57.0, 21.5), (56.0, 21.0), (54.4, 19.6), (54.6, 18.0), (54.0, 14.0), (54.5, 10.0), (57.5, 10.5),
               (57.0, 8.0), (55.0, 8.5), (53.5, 7.0), (53.3, 5.0), (52.0, 4.2), (51.3, 3.3), (51.0, 2.0), (50.0, 1.5),
               (49.6, 0.0), (49.3, -1.3), (48.7, -1.6), (48.6, -4.7), (47.5, -2.5), (46.0, -1.2), (43.5, -1.5),
               (43.4, -8.2), (42.0, -8.9), (38.7, -9.5), (37.0, -9.0), (37.0, -7.4), (36.15, -5.4)]
LAUT_TENGAH_UTARA = [(36.7, -4.4), (36.7, -2.2), (38.5, -0.4), (41.5, 2.2), (43.0, 3.3), (43.3, 5.4), (43.5, 7.0),
                     (44.4, 8.9), (44.0, 10.2), (41.9, 12.3), (40.8, 14.2), (38.9, 16.1), (38.0, 15.7),
                     (38.0, 16.3), (39.0, 17.1), (40.5, 17.0), (40.6, 18.5), (41.9, 16.0), (43.6, 13.5),
                     (45.4, 12.3), (45.7, 13.7), (42.6, 18.0), (40.0, 19.8), (38.3, 21.2), (36.8, 22.5),
                     (38.0, 24.0), (40.6, 22.9), (40.9, 26.0), (38.5, 26.6), (37.0, 27.4), (36.6, 30.5),
                     (36.8, 34.5), (36.5, 36.0), (35.0, 35.9), (33.0, 35.1), (31.5, 34.4), (31.2, 32.3),
                     (31.5, 30.0), (30.9, 28.5), (32.5, 23.0), (30.3, 19.7), (32.4, 15.3), (33.5, 11.2),
                     (36.8, 11.0), (37.2, 9.8), (36.9, 7.0), (36.8, 3.0), (35.6, -0.6), (35.2, -2.9), (35.9, -5.3)]
AFRO_EURASIA = (AFRIKA_BARAT + AA[:_i_djibouti + 1] + LAUT_MERAH_BARAT + LAUT_MERAH_TIMUR
                + AA[_i_aden:_i_ujung + 1] + EROPA_UTARA + LAUT_TENGAH_UTARA)
BRITANIA = [(50.1, -5.7), (50.8, 0.8), (51.4, 1.4), (52.9, 1.7), (53.6, 0.0), (55.8, -2.0), (57.7, -1.8),
            (58.6, -3.0), (58.5, -5.0), (56.5, -6.2), (55.0, -4.9), (54.5, -3.4), (53.3, -3.0), (52.8, -4.7),
            (51.7, -5.2), (51.6, -3.0), (51.2, -4.2), (50.3, -5.0)]
IRLANDIA = [(55.3, -7.3), (54.3, -10.0), (51.6, -10.0), (51.8, -8.0), (52.2, -6.3), (54.0, -6.0)]
SKANDINAVIA = [(58.0, 7.0), (59.0, 10.5), (57.7, 11.8), (55.4, 13.0), (56.2, 16.0), (58.0, 16.7), (60.5, 17.5),
               (62.5, 17.8), (63.5, 20.0), (65.8, 22.5), (66.0, 26.0), (66.0, 13.0), (64.0, 10.0), (62.0, 5.0),
               (60.0, 5.0)]
SISILIA = [(38.2, 12.4), (38.3, 15.6), (36.7, 15.1), (37.6, 12.6)]
SARDINIA = [(41.2, 9.2), (40.9, 9.8), (39.1, 9.6), (39.0, 8.4), (40.9, 8.2)]
KORSIKA = [(43.0, 9.4), (41.4, 9.2), (41.7, 8.6), (42.8, 8.6)]
DARAT = [AFRO_EURASIA, BRITANIA, IRLANDIA, SKANDINAVIA, SISILIA, SARDINIA, KORSIKA]

print("  menyiapkan peta Eropa...")
EROPA = Peta(-12, 34, 30, 68, 110, [], [(46.5, 9.5, 1.5), (47.0, 13.5, 1.0), (42.8, 0.5, 0.7)], seed=34, darat=DARAT)
print("  menyiapkan peta Nusantara...")
NUSA = Peta(92, 142, -20, 14, 90, [], [(-7.2, 107.6, 0.35), (-7.0, 110.4, 0.4), (-0.5, 101.0, 0.5),
                                        (-2, 114, 1.0)], seed=35, darat=pd.SEMUA)

LONDON = (51.5, -0.12)
BERLIN = (52.52, 13.4)
WINA = (48.2, 16.37)
JENEWA = (46.2, 6.15)
JAKARTA = (-6.2, 106.8)

print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 34, warna=(222, 200, 155)).convert("RGBA")
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


def kalender(img, cx, cy, bulan, tgl, tahun="", alpha=1.0, s=1.0):
    if alpha <= 0.01 or s <= 0.2:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    w, h = 300 * s, 330 * s
    d.rounded_rectangle((cx - w / 2 + 8, cy - h / 2 + 10, cx + w / 2 + 8, cy + h / 2 + 10), int(18 * s),
                        fill=(0, 0, 0, 100))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(18 * s), fill=(250, 245, 235, 255),
                        outline=(80, 60, 40, 255), width=4)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 84 * s), int(18 * s), fill=MERAH + (255,))
    d.text((cx, cy - h / 2 + 43 * s), bulan, font=se.font("ui", int(34 * s)), fill=PUTIH, anchor="mm")
    d.text((cx, cy + 20 * s), tgl, font=se.font("caption", int(120 * s)), fill=TINTA, anchor="mm")
    if tahun:
        d.text((cx, cy + h / 2 - 34 * s), tahun, font=se.font("ui", int(38 * s)), fill=(150, 30, 25), anchor="mm")
    se.tempel(img, lap, alpha)


def anak_kurus(d, x, y, s=1.0, warna=(70, 50, 35), alpha=1.0):
    """Siluet anak kurus sederhana tanpa wajah. (x, y) = telapak kaki tengah."""
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    lw = max(2, int(7 * s))
    d.ellipse((x - 26 * s, y - 250 * s, x + 26 * s, y - 196 * s), fill=c)          # kepala
    d.line((x, y - 196 * s, x, y - 185 * s), fill=c, width=lw)                       # leher
    d.rounded_rectangle((x - 22 * s, y - 188 * s, x + 22 * s, y - 95 * s), int(10 * s) + 1, fill=c)  # badan
    d.line((x - 22 * s, y - 180 * s, x - 42 * s, y - 110 * s), fill=c, width=lw)   # lengan
    d.line((x + 22 * s, y - 180 * s, x + 42 * s, y - 110 * s), fill=c, width=lw)
    d.line((x - 10 * s, y - 95 * s, x - 14 * s, y), fill=c, width=lw)              # kaki kurus
    d.line((x + 10 * s, y - 95 * s, x + 14 * s, y), fill=c, width=lw)


def selebaran(img, cx, cy, s=1.0, sudut=0.0, alpha=1.0, teks_atas=True):
    """Selebaran ilustrasi: 'foto' sepia anak kurus + tulisan Inggris asli."""
    if alpha <= 0.01 or s <= 0.05:
        return
    sw, sh = int(420 * s), int(560 * s)
    lap = Image.new("RGBA", (sw + 30, sh + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rectangle((18, 20, sw + 18, sh + 20), fill=(0, 0, 0, 90))
    d.rectangle((10, 10, sw + 10, sh + 10), fill=(246, 240, 225, 255), outline=(90, 70, 50, 255),
                width=max(2, int(4 * s)))
    if teks_atas:
        d.text((10 + sw / 2, 10 + 48 * s), "A STARVING BABY", font=se.font("caption", int(38 * s)), fill=(40, 30, 25),
               anchor="mm")
    fx0, fy0, fx1, fy1 = 10 + 40 * s, 10 + 85 * s, 10 + sw - 40 * s, 10 + 420 * s
    d.rectangle((fx0, fy0, fx1, fy1), fill=SEPIA + (255,), outline=(60, 45, 30, 255), width=max(2, int(4 * s)))
    anak_kurus(d, (fx0 + fx1) / 2, fy1 - 18 * s, 1.15 * s, (85, 62, 42))
    d.text((10 + sw / 2, 10 + 465 * s), "Our blockade", font=se.font("judul", int(34 * s)), fill=(150, 25, 20),
           anchor="mm")
    d.text((10 + sw / 2, 10 + 510 * s), "has caused this", font=se.font("judul", int(34 * s)), fill=(150, 25, 20),
           anchor="mm")
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def borgol(d, cx, cy, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    c = (200, 205, 215, a)
    w = max(3, int(16 * s))
    d.ellipse((cx - 150 * s, cy - 60 * s, cx - 30 * s, cy + 60 * s), outline=c, width=w)
    d.ellipse((cx + 30 * s, cy - 60 * s, cx + 150 * s, cy + 60 * s), outline=c, width=w)
    for k in range(3):
        x = cx - 30 * s + k * 30 * s
        d.ellipse((x - 14 * s, cy - 9 * s, x + 14 * s, cy + 9 * s), outline=c, width=max(2, int(7 * s)))


def polisi(d, x, y, s=1.0, alpha=1.0):
    """Siluet polisi London (helm tinggi), tanpa wajah."""
    a = int(255 * alpha)
    c = POLISI + (a,)
    d.ellipse((x - 11 * s, y - 62 * s, x + 11 * s, y - 40 * s), fill=c)
    d.polygon([(x - 13 * s, y - 56 * s), (x - 8 * s, y - 84 * s), (x + 8 * s, y - 84 * s), (x + 13 * s, y - 56 * s)],
              fill=c)
    d.ellipse((x - 4 * s, y - 90 * s, x + 4 * s, y - 82 * s), fill=(200, 190, 120, a))
    d.rounded_rectangle((x - 15 * s, y - 40 * s, x + 15 * s, y), int(6 * s) + 1, fill=c)


def orang(d, x, y, s=1.0, warna=(60, 45, 35), alpha=1.0, rok=False):
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    d.ellipse((x - 9 * s, y - 50 * s, x + 9 * s, y - 32 * s), fill=c)
    if rok:
        d.polygon([(x - 8 * s, y - 32 * s), (x + 8 * s, y - 32 * s), (x + 18 * s, y), (x - 18 * s, y)], fill=c)
    else:
        d.rounded_rectangle((x - 12 * s, y - 30 * s, x + 12 * s, y), int(6 * s) + 1, fill=c)


def kolom_nelson(d, x, y, s=1.0, alpha=1.0, warna=(40, 40, 55)):
    """Siluet tugu di Trafalgar Square. (x, y) = dasar."""
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    d.rectangle((x - 70 * s, y - 60 * s, x + 70 * s, y), fill=c)
    d.rectangle((x - 45 * s, y - 120 * s, x + 45 * s, y - 60 * s), fill=c)
    d.rectangle((x - 18 * s, y - 520 * s, x + 18 * s, y - 120 * s), fill=c)
    d.rectangle((x - 30 * s, y - 545 * s, x + 30 * s, y - 520 * s), fill=c)
    d.ellipse((x - 12 * s, y - 590 * s, x + 12 * s, y - 545 * s), fill=c)
    # singa
    for sx in (-1, 1):
        bx = x + sx * 200 * s
        d.rectangle((bx - 60 * s, y - 40 * s, bx + 60 * s, y), fill=c)
        d.ellipse((bx - 50 * s, y - 85 * s, bx + 50 * s, y - 35 * s), fill=c)


def palu(d, cx, cy, s=1.0, sudut=0.0, alpha=1.0):
    """Palu sidang. sudut dalam derajat (rotasi di sekitar pangkal gagang)."""
    a = int(255 * alpha)
    rad = math.radians(sudut)

    def rot(px, py):
        return (cx + px * math.cos(rad) - py * math.sin(rad), cy + px * math.sin(rad) + py * math.cos(rad))

    gagang = [rot(-8 * s, 0), rot(8 * s, 0), rot(8 * s, -230 * s), rot(-8 * s, -230 * s)]
    d.polygon(gagang, fill=(120, 75, 40, a))
    kepala = [rot(-80 * s, -210 * s), rot(80 * s, -210 * s), rot(80 * s, -290 * s), rot(-80 * s, -290 * s)]
    d.polygon(kepala, fill=(95, 55, 28, a), outline=(50, 30, 15, a))


def uang_pound(img, cx, cy, s=1.0, sudut=0.0, alpha=1.0):
    """Uang kertas £5 ilustrasi (bukan replika)."""
    if alpha <= 0.01 or s <= 0.05:
        return
    uw, uh = int(340 * s), int(180 * s)
    lap = Image.new("RGBA", (uw + 20, uh + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    tinta = (40, 40, 45)
    d.rounded_rectangle((10, 10, uw + 10, uh + 10), int(10 * s), fill=(248, 246, 238, 255), outline=tinta + (255,),
                        width=max(2, int(5 * s)))
    m = int(14 * s)
    d.rectangle((10 + m, 10 + m, uw + 10 - m, uh + 10 - m), outline=tinta + (140,), width=max(1, int(3 * s)))
    d.text((10 + uw / 2, 10 + 70 * s), "£5", font=se.font("caption", int(80 * s)), fill=tinta, anchor="mm")
    d.text((10 + uw / 2, 10 + 140 * s), "FIVE POUNDS", font=se.font("ui", int(28 * s)), fill=tinta, anchor="mm")
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def kapal(d, x, y, s=1.0, alpha=1.0, warna=(60, 60, 70), muatan=False, t=0.0):
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    goyang = math.sin(t * 3) * 4 * s
    y = y + goyang
    d.polygon([(x - 120 * s, y - 30 * s), (x + 120 * s, y - 30 * s), (x + 90 * s, y + 20 * s), (x - 95 * s, y + 20 * s)],
              fill=c)
    d.rectangle((x - 40 * s, y - 70 * s, x + 40 * s, y - 30 * s), fill=c)
    d.rectangle((x - 10 * s, y - 110 * s, x + 10 * s, y - 70 * s), fill=c)
    if muatan:
        for k in range(3):
            bx = x - 95 * s + k * 26 * s
            d.rectangle((bx, y - 58 * s, bx + 22 * s, y - 32 * s), fill=(190, 140, 70, a), outline=(90, 60, 30, a))
        for k in range(3):
            bx = x + 48 * s + k * 22 * s
            d.rectangle((bx, y - 54 * s, bx + 18 * s, y - 32 * s), fill=(235, 235, 235, a), outline=(200, 30, 30, a))


def coret_besar(d, box, k, alpha=1.0):
    if k <= 0:
        return
    x0, y0, x1, y1 = box
    a = int(255 * alpha)
    k1, k2 = clamp(k * 2), clamp(k * 2 - 1)
    d.line((x0, y0, lerp(x0, x1, k1), lerp(y0, y1, k1)), fill=(220, 30, 25, a), width=16)
    if k2 > 0:
        d.line((x1, y0, lerp(x1, x0, k2), lerp(y0, y1, k2)), fill=(220, 30, 25, a), width=16)


def selebaran_terbang(img, t, n=10, seed=3, y0=380, y1=1320, alpha=1.0, s=0.26):
    rng = random.Random(seed)
    for i in range(n):
        fase = (rng.random() + t * rng.uniform(0.1, 0.2)) % 1
        x = rng.uniform(70, 1010) + math.sin(fase * 6 + i) * 50
        y = lerp(y0, y1, fase)
        selebaran(img, x, y, s * rng.uniform(0.8, 1.15), sudut=math.sin(t * 2 + i) * 25 + rng.uniform(-30, 30),
                  alpha=alpha * (1 - fase * 0.4))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 960, 520, (230, 60, 40), 1.0 + 0.3 * math.sin(c.t * 4))
    selebaran_terbang(img, c.t + 2, n=7, seed=4, y0=700, y1=1330, alpha=0.55, s=0.22)
    goyang = math.sin(c.t * 2.2) * 3
    selebaran(img, 540, 900, 1.0, sudut=-4 + goyang, alpha=1.0)
    d = ImageDraw.Draw(img, "RGBA")
    borgol(d, 790, 1160, 0.75)
    se.teks(d, (540, 410), "DITANGKAP GARA-GARA", 78, PUTIH, nama_font="caption", stroke=10, stroke_warna=GELAP)
    se.teks(d, (540, 520), "FOTO ANAK", 120, KUNING, nama_font="caption", stroke=11, stroke_warna=GELAP)
    stempel(img, "LONDON, 1919", 880, 690, 0.55, uk=56, sudut=10)
    a = c.p(0.3, 0.38)
    if a > 0:
        se.kartu(img, 190, 700, "Lagi rame:", "Hari Anak Sedunia", HIJAU_TUA, alpha=a, tiang=False,
                 skala=skala_muncul(c, 0.3))
    a2 = c.p(0.52, 0.6)
    if a2 > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((120, 1240, 960, 1350), 30, fill=(247, 236, 208, 240), outline=(170, 30, 20, 255), width=6)
        se.tempel(img, lap, a2)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1295), "Kenapa 20 November?", 60, (170, 30, 20), nama_font="caption", alpha=a2)
    return img


def a_blokade(c):
    kamera = se.kamera_antara(cam(EROPA, 50.5, 7.2, 0.47), cam(EROPA, 50.5, 7.6, 0.5), c.p(0.0, 1.0))
    img = se.render_peta(EROPA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    lx, ly = layar(EROPA, kamera, LONDON)
    titik_kota(d, lx, ly, "London", c.p(0.02, 0.1), (200, 52, 44), t=c.t)
    a = c.p(0.12, 0.22)
    bx, by = layar(EROPA, kamera, BERLIN)
    wx, wy = layar(EROPA, kamera, WINA)
    if a > 0:
        se.glow(img, bx, by, 150, (230, 60, 40), 1.2 * a)
        se.glow(img, wx, wy, 130, (230, 60, 40), 1.1 * a)
        d = ImageDraw.Draw(img, "RGBA")
        titik_kota(d, bx, by, "Jerman", a, t=c.t)
        titik_kota(d, wx, wy, "Austria", a, t=c.t, dx=-70)
    # deretan kapal blokade di Laut Utara
    k = c.p(0.28, 0.5)
    titik_blok = [(56.5, 4.0), (55.0, 5.0), (53.8, 4.6), (52.6, 3.6), (51.6, 2.6)]
    for i, ll in enumerate(titik_blok):
        f = clamp(k * 5 - i)
        if f <= 0:
            continue
        x, y = layar(EROPA, kamera, ll)
        kapal(d, x, y, 0.6 * back_out(f), 1.0, (50, 55, 70), t=c.t + i)
    if k > 0:
        pts = [layar(EROPA, kamera, ll) for ll in titik_blok]
        se.garis_putus(d, pts, k, MERAH, tebal=8, panah=False)
    a2 = c.p(0.58, 0.66)
    if a2 > 0:
        cx, cy = (bx + wx) / 2 + 40, (by + wy) / 2 - 10
        stempel(img, "MAKANAN DIHADANG", 540, 1240, skala_muncul(c, 0.58, 0.08) * 0.72, uk=60, sudut=-5)
    se.kartu(img, 540, 470, "Perang Dunia I baru usai", "tapi blokade jalan terus", MERAH, alpha=c.p(0.05, 0.12),
             tiang=False, skala=skala_muncul(c, 0.05))
    hdr(img, "Eropa, 1918–1919")
    return img


def a_selebaran(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.0, 0.08)
    se.glow(img, 300, 820, 260, (255, 210, 120), 1.0 * a)
    d = ImageDraw.Draw(img, "RGBA")
    orang(d, 300, 1000, 5.0, (55, 40, 30), a, rok=True)
    se.kartu(img, 300, 1110, "Eglantyne Jebb", "aktivis sosial, Inggris", BIRU, alpha=c.p(0.05, 0.12), tiang=False,
             skala=skala_muncul(c, 0.05))
    stempel(img, "NGGAK TERIMA!", 300, 520, skala_muncul(c, 0.18, 0.08) * 0.7, uk=60, sudut=-8)
    # mesin cetak: selebaran bertumpuk keluar
    k = c.p(0.35, 0.65)
    for i in range(5):
        f = clamp(k * 5 - i)
        if f <= 0:
            continue
        selebaran(img, 770 + i * 6, lerp(1300, 860 - i * 10, back_out(f) if f < 1 else 1), 0.82, sudut=6 - i * 3,
                  alpha=min(1, f * 2))
    a2 = c.p(0.72, 0.8)
    if a2 > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((90, 1180, 990, 1320), 30, fill=(247, 236, 208, 245), outline=(170, 30, 20, 255), width=6)
        se.tempel(img, lap, a2)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1250), "“Blokade kita yang bikin ini”", 52, (170, 30, 20), nama_font="caption",
                alpha=a2)
    hdr(img, "Selebaran, 1919")
    return img


def a_ditangkap(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 1000, 480, (90, 110, 160), 0.9)
    d = ImageDraw.Draw(img, "RGBA")
    kolom_nelson(d, 540, 1150, 1.15, 1.0, (30, 32, 48))
    selebaran_terbang(img, c.t, n=9, seed=6, y0=420, y1=1300, alpha=0.9 * c.p(0.0, 0.1), s=0.24)
    d = ImageDraw.Draw(img, "RGBA")
    # kerumunan
    rng = random.Random(8)
    for i in range(16):
        x = 60 + i * 64 + rng.uniform(-10, 10)
        orang(d, x, 1300 + rng.uniform(-10, 10), 2.2, (20, 20, 28), 1.0)
    se.kartu(img, 540, 470, "Trafalgar Square", "London, 1919", BIRU, alpha=c.p(0.0, 0.06), tiang=False,
             skala=skala_muncul(c, 0.0))
    a = c.p(0.18, 0.26)
    if a > 0:
        maju = c.p(0.18, 0.4)
        polisi(d, lerp(-40, 300, maju), 1290, 2.6, a)
        polisi(d, lerp(1120, 780, maju), 1290, 2.6, a)
        stempel(img, "DITANGKAP!", 540, 700, skala_muncul(c, 0.3, 0.08) * 0.9, uk=86, sudut=-9)
    a2 = c.p(0.45, 0.53)
    if a2 > 0:
        se.panel(img, (110, 820, 970, 1060), alpha=a2)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 890), "Nolong anak-anak", 50, TINTA, nama_font="judul", alpha=a2)
        se.teks(d, (540, 985), "NEGARA MUSUH", 76, (170, 30, 20), nama_font="caption", alpha=c.p(0.52, 0.58))
    hdr(img, "Ditangkap di jalanan")
    return img


def a_sidang(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # meja hakim
    d.rectangle((140, 980, 940, 1080), fill=(110, 70, 38, 255), outline=(60, 35, 18, 255), width=5)
    d.rectangle((160, 1080, 920, 1300), fill=(95, 60, 32, 255), outline=(60, 35, 18, 255), width=5)
    ketuk = c.p(0.2, 0.26)
    sudut = -35 + 35 * ketuk if c.t / c.d < 0.26 else -35 * c.p(0.3, 0.45)
    palu(d, 800, 990, 0.9, sudut)
    if 0.24 < c.t / c.d < 0.34:
        se.glow(img, 760, 980, 160, (255, 230, 150), 1.4)
        d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 470, "Diadili", "UU darurat masa perang", MERAH, alpha=c.p(0.0, 0.06), tiang=False,
             skala=skala_muncul(c, 0.0))
    stempel(img, "BERSALAH", 540, 700, skala_muncul(c, 0.24, 0.08) * 0.95, uk=96, sudut=-7)
    a = c.p(0.5, 0.58)
    if a > 0:
        uang_pound(img, 540, 1180, 1.1 * skala_muncul(c, 0.5), sudut=-5, alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 880), "Denda: lima pound", 58, (170, 30, 20), nama_font="caption", stroke=5,
                stroke_warna=KREM, alpha=c.p(0.55, 0.62))
    hdr(img, "Ruang sidang, 1919")
    return img


def a_rehook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 1000, 440, (230, 190, 90), 1.0)
    se.panel(img, (90, 410, 990, 600), alpha=c.p(0.0, 0.06))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 470), "TAPI BAGIAN PALING ANEH…", 52, (170, 30, 20), nama_font="caption", alpha=c.p(0.0, 0.06))
    se.teks(d, (540, 550), "siapa yang bayar dendanya?", 44, TINTA, nama_font="judul", alpha=c.p(0.06, 0.12))
    # kartu dua kemungkinan
    se.kartu(img, 290, 720, "Jaksanya?", "versi banyak sumber", BIRU, alpha=c.p(0.22, 0.28), tiang=False,
             skala=skala_muncul(c, 0.22))
    se.kartu(img, 790, 720, "Hakimnya?", "versi Save the Children", BIRU, alpha=c.p(0.3, 0.36), tiang=False,
             skala=skala_muncul(c, 0.3))
    # uang terbang ke kotak donasi
    k = c.p(0.5, 0.75)
    kx, ky = 540, 1180
    if c.p(0.45, 0.5) > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rectangle((kx - 230, ky - 90, kx + 230, ky + 110), fill=(200, 40, 35, 255), outline=(90, 15, 10, 255),
                     width=6)
        dl.rectangle((kx - 90, ky - 100, kx + 90, ky - 80), fill=(40, 20, 15, 255))
        dl.text((kx, ky + 10), "SAVE THE", font=se.font("caption", 50), fill=PUTIH, anchor="mm")
        dl.text((kx, ky + 66), "CHILDREN", font=se.font("caption", 50), fill=PUTIH, anchor="mm")
        se.tempel(img, lap, c.p(0.45, 0.5))
    if 0 < k < 1:
        x = lerp(540, kx, k)
        y = lerp(880, ky - 100, k) - math.sin(k * math.pi) * 90
        uang_pound(img, x, y, lerp(0.8, 0.35, k), sudut=k * 200)
    elif k <= 0:
        uang_pound(img, 540, 900, 0.8 * c.p(0.38, 0.44), alpha=c.p(0.38, 0.44))
    stempel(img, "DONASI PERTAMA", 540, 930, skala_muncul(c, 0.78, 0.08) * 0.8, uk=64, sudut=-6)
    hdr(img, "Lahirnya Save the Children")
    return img


def a_bantuan(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # Royal Albert Hall (kubah)
    a1 = 1 - c.p(0.4, 0.46)
    if a1 > 0.01:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.pieslice((220, 620, 860, 1100), 180, 360, fill=(170, 95, 70, 255), outline=(80, 40, 25, 255), width=6)
        dl.rectangle((220, 860, 860, 1150), fill=(185, 105, 75, 255), outline=(80, 40, 25, 255), width=6)
        for k in range(8):
            x = 260 + k * 80
            dl.rounded_rectangle((x, 920, x + 40, 1050), 18, fill=(250, 225, 150, 255))
        se.tempel(img, lap, a1)
        se.kartu(img, 540, 1250, "Royal Albert Hall", "Save the Children Fund, Mei 1919", BIRU, alpha=a1 * c.p(0.04, 0.1),
                 tiang=False, skala=skala_muncul(c, 0.04))
        stempel(img, "DONASI MENGALIR", 540, 500, skala_muncul(c, 0.16, 0.08) * 0.75 * (1 if a1 > 0.5 else 0),
                uk=60, sudut=-6, warna=(30, 110, 60))
    f2 = c.p(0.42, 0.48)
    if f2 > 0:
        # laut + kapal bantuan
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rectangle((0, 1000, W, 1320), fill=(35, 70, 120, 255))
        for k in range(8):
            yy = 1030 + k * 38
            dl.line([(x, yy + math.sin(x / 40 + c.t * 3 + k) * 6) for x in range(0, W + 40, 40)],
                    fill=(90, 140, 200, 160), width=3)
        se.tempel(img, lap, f2)
        d = ImageDraw.Draw(img, "RGBA")
        kapal(d, lerp(-200, 560, c.p(0.42, 0.8)), 1040, 1.7, f2, (70, 60, 55), muatan=True, t=c.t)
        se.kartu(img, 540, 470, "1921: kelaparan Rusia", "kapal bantuan dikirim", MERAH, alpha=c.p(0.5, 0.56),
                 tiang=False, skala=skala_muncul(c, 0.5))
        se.teks(d, (540, 700), "600 TON", 130, (170, 30, 20), nama_font="caption", stroke=8, stroke_warna=KREM,
                alpha=c.p(0.62, 0.68))
        se.teks(d, (540, 820), "makanan & obat", 52, TINTA, nama_font="caption", stroke=5, stroke_warna=KREM,
                alpha=c.p(0.66, 0.72))
    hdr(img, "Dari London ke dunia")
    return img


def a_deklarasi(c):
    kamera = se.kamera_antara(cam(EROPA, 47.5, 6.5, 1.1), cam(EROPA, 46.6, 6.3, 1.5), c.p(0.0, 0.5))
    img = se.render_peta(EROPA, kamera)
    se.tint(img, (10, 6, 0), 0.25 * c.p(0.3, 0.4))
    d = ImageDraw.Draw(img, "RGBA")
    jx, jy = layar(EROPA, kamera, JENEWA)
    titik_kota(d, jx, jy, "Jenewa", 1.0 - c.p(0.3, 0.38), t=c.t)
    a = c.p(0.3, 0.38)
    if a > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        y0, y1 = 520, lerp(560, 1290, c.p(0.3, 0.45))
        dl.rectangle((150, y0, 930, y1), fill=(248, 240, 220, 255), outline=(110, 80, 45, 255), width=5)
        dl.rounded_rectangle((130, y0 - 30, 950, y0 + 10), 18, fill=(200, 170, 120, 255), outline=(110, 80, 45, 255),
                             width=4)
        dl.rounded_rectangle((130, y1 - 10, 950, y1 + 30), 18, fill=(200, 170, 120, 255), outline=(110, 80, 45, 255),
                             width=4)
        se.tempel(img, lap, a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 590), "HAK ANAK", 70, (150, 30, 25), nama_font="caption", alpha=c.p(0.36, 0.42))
        baris = [("Yang lapar", "harus diberi makan"), ("Yang sakit", "harus dirawat"),
                 ("Yang yatim", "harus dilindungi")]
        for i, (b1, b2) in enumerate(baris):
            ai = c.p(0.42 + i * 0.08, 0.48 + i * 0.08)
            y = 720 + i * 150
            se.teks(d, (540, y), b1, 50, TINTA, nama_font="judul", alpha=ai)
            se.teks(d, (540, y + 58), b2, 44, (110, 80, 50), nama_font="tangan", alpha=ai)
    stempel(img, "DISAHKAN 1924", 700, 1230, skala_muncul(c, 0.76, 0.08) * 0.72, uk=60, sudut=-7, warna=(30, 80, 150))
    se.kartu(img, 540, 470, "1923: ditulis Eglantyne", "Liga Bangsa-Bangsa, Jenewa", BIRU,
             alpha=c.p(0.05, 0.12) * (1 - c.p(0.28, 0.32)), tiang=False, skala=skala_muncul(c, 0.05))
    hdr(img, "Deklarasi Jenewa")
    return img


def a_20nov(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 900, 500, (90, 150, 230), 1.0)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 430), "INI JAWABANNYA:", 60, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP,
            alpha=c.p(0.0, 0.05))
    kalender(img, 300, 780, "NOVEMBER", "20", "1959", c.p(0.06, 0.12), 0.95 * skala_muncul(c, 0.06))
    se.kartu(img, 300, 1030, "PBB sahkan", "Deklarasi Hak Anak", BIRU_PBB, alpha=c.p(0.14, 0.2), tiang=False,
             skala=skala_muncul(c, 0.14))
    kalender(img, 780, 780, "NOVEMBER", "20", "1989", c.p(0.46, 0.52), 0.95 * skala_muncul(c, 0.46))
    se.kartu(img, 780, 1030, "Konvensi", "Hak-Hak Anak", BIRU_PBB, alpha=c.p(0.54, 0.6), tiang=False,
             skala=skala_muncul(c, 0.54))
    a = c.p(0.3, 0.4)
    if a > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.garis_putus(d, [(420, 640), (540, 590), (660, 640)], c.p(0.3, 0.46), KUNING, tebal=7)
        se.teks(d, (540, 540), "+30 tahun", 44, KUNING, nama_font="caption", stroke=5, stroke_warna=GELAP, alpha=a)
    stempel(img, "TANGGAL YANG SAMA!", 540, 1230, skala_muncul(c, 0.72, 0.08) * 0.82, uk=64, sudut=-5,
            warna=(200, 40, 35))
    hdr(img, "Kenapa 20 November?")
    return img


def a_indonesia(c):
    kamera = se.kamera_antara(cam(NUSA, -3.0, 116.0, 0.65), cam(NUSA, -5.0, 111.0, 0.8), c.p(0.0, 1.0))
    img = se.render_peta(NUSA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    a0 = 1 - c.p(0.32, 0.38)
    if a0 > 0.01:
        se.panel(img, (110, 470, 970, 720), alpha=a0 * c.p(0.0, 0.06))
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 545), "Perjanjian HAM yang paling", 46, TINTA, nama_font="judul", alpha=a0 * c.p(0.0, 0.06))
        se.teks(d, (540, 640), "BANYAK DIRATIFIKASI", 64, (170, 30, 20), nama_font="caption",
                alpha=a0 * c.p(0.04, 0.1))
    jx, jy = layar(NUSA, kamera, JAKARTA)
    a = c.p(0.36, 0.44)
    if a > 0:
        se.glow(img, jx, jy, 150, (255, 200, 80), 1.3 * a)
        d = ImageDraw.Draw(img, "RGBA")
        titik_kota(d, jx, jy, "Jakarta", a, (200, 52, 44), t=c.t)
        kalender(img, 540, 640, "INDONESIA", "1990", "ikut meratifikasi", a, 0.9 * skala_muncul(c, 0.36))
        se.kartu(img, 760, 900, "Keppres No. 36/1990", "Konvensi Hak Anak", MERAH, alpha=c.p(0.5, 0.56), tiang=False,
                 skala=skala_muncul(c, 0.5))
    a2 = c.p(0.66, 0.72)
    if a2 > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((90, 1200, 990, 1300), 30, fill=(247, 236, 208, 240), outline=(30, 110, 60, 255), width=6)
        se.tempel(img, lap, a2)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1250), "Hak anak = kewajiban negara", 50, (30, 110, 60), nama_font="caption", alpha=a2)
    hdr(img, "Sampai ke Indonesia")
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
    a = c.p(0.0, 0.08) * (1 - c.p(0.54, 0.58))
    if a > 0:
        selebaran(img, 540, 1050, 0.62, sudut=4, alpha=a)
        se.panel(img, (90, 420, 990, 720), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 495), "Semua berawal dari", 46, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 575), "selembar foto", 62, (170, 30, 20), nama_font="caption", alpha=c.p(0.08, 0.14) * a)
        se.teks(d, (540, 655), "& satu orang yang nggak mau diam.", 40, TINTA, nama_font="judul",
                alpha=c.p(0.2, 0.26) * a)
    b = c.p(0.56, 0.64)
    if b > 0:
        m = maskot()
        if m is not None:
            loncat = abs(math.sin(c.t * 5)) * 18
            se.tempel(img, m, b, (540 - m.width // 2, int(560 - loncat)))
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        sk = back_out((c.t / c.d - 0.56) / 0.1)
        w2 = 380 * sk
        dl.rounded_rectangle((540 - w2, 960, 540 + w2, 1090), 40, fill=(200, 52, 44, 245))
        dl.text((540, 1025), "NGOMONGIN SEJARAH", font=se.font("caption", int(56 * sk) + 1), fill=PUTIH, anchor="mm")
        dl.text((540, 1160), "Follow buat cerita berikutnya", font=se.font("ui", 42), fill=PUTIH, anchor="mm",
                stroke_width=4, stroke_fill=(0, 0, 0))
        se.tempel(img, lap, b)
    return img


ADEGAN = [
    Adegan("hook", "Dia ditangkap gara-gara foto anak. Lagi rame Hari Anak Sedunia? Kenapa sih tanggalnya dua puluh November? Jawabannya berawal dari perempuan ini.",
           a_hook, transisi=False),
    Adegan("blokade", "Tahun sembilan belas sembilan belas. Perang Dunia Pertama baru usai, tapi Jerman dan Austria masih diblokade. Makanan susah masuk. Anak-anak kelaparan.",
           a_blokade),
    Adegan("selebaran", "Eglantyne Jebb dari Inggris nggak terima. Dia bikin selebaran foto anak kurus kering, tulisannya: blokade kita yang bikin ini.",
           a_selebaran),
    Adegan("ditangkap", "Dia bagikan di Trafalgar Square, London. Langsung ditangkap. Bayangin, nolong anak negara musuh, waktu suasana masih perang.",
           a_ditangkap),
    Adegan("sidang", "Di pengadilan, dia dinyatakan bersalah. Hukumannya: denda lima pound.",
           a_sidang),
    Adegan("rehook", "Tapi bagian paling aneh: dendanya justru dibayar orang dari ruang sidang itu sendiri, banyak sumber bilang jaksanya. Itulah donasi pertama Save the Children.",
           a_rehook),
    Adegan("bantuan", "Donasi mengalir deras. Tahun dua puluh satu, mereka kirim kapal berisi enam ratus ton makanan dan obat ke Rusia yang dilanda kelaparan.",
           a_bantuan),
    Adegan("deklarasi", "Tahun dua puluh tiga, Eglantyne menulis deklarasi hak anak: yang lapar harus diberi makan, yang sakit harus dirawat. Setahun kemudian, disahkan di Jenewa.",
           a_deklarasi),
    Adegan("20nov", "Nah, ini jawabannya. Dua puluh November, sembilan belas lima sembilan, PBB mengesahkan Deklarasi Hak Anak. Tiga puluh tahun kemudian, di tanggal yang sama, lahir Konvensi Hak Anak.",
           a_20nov),
    Adegan("indonesia", "Konvensi ini jadi perjanjian hak asasi paling banyak diratifikasi di dunia. Indonesia ikut meratifikasinya tahun sembilan puluh.",
           a_indonesia),
    Adegan("penutup", "Semua berawal dari selembar foto, dan satu orang yang nggak mau diam. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
