"""Shorts ±88 detik: Dulu Nenek Moyang Kita Nggak Kenal Cabai.

Cabai (Capsicum) asal Amerika → Columbus 1492 → pelaut Portugis → Goa → Malaka → Nusantara abad ke-16.
Nama "cabai" aslinya milik cabya / cabe jawa (Piper retrofractum), keluarga lada.
Peta dunia ilustratif + adegan ilustrasi (cabai, rempah, label nama).
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, KUNING, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "sejarah-cabai-dari-amerika-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "SEJARAH CABAI"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
MERAH_CABAI = (205, 30, 25)
HIJAU_TANGKAI = (60, 130, 50)
COKLAT = (120, 70, 35)
BIRU = (30, 80, 150)
ABU = (60, 60, 70)
GELAP = (25, 12, 8)

# ------------------------------------------------------------------ garis pantai dunia (disederhanakan, ilustratif)

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
EROPA_UTARA = [(75.0, 140.0), (75.0, 31.0), (70.5, 31.0), (71.0, 26.0), (70.0, 19.0), (67.0, 14.0), (64.0, 10.0),
               (62.0, 5.0), (59.0, 5.2), (58.0, 6.5), (58.5, 8.0), (59.0, 10.5), (57.7, 11.8), (56.0, 12.8),
               (55.4, 13.0), (56.2, 14.5), (56.0, 16.0), (58.0, 16.7), (60.0, 18.5), (62.5, 17.5), (65.5, 22.0),
               (64.0, 24.5), (61.0, 21.5), (60.0, 22.5), (60.0, 29.0), (59.4, 28.0), (57.8, 24.3), (56.5, 21.0),
               (54.5, 19.5), (54.0, 14.0), (54.5, 10.0), (57.5, 10.5), (57.0, 8.0),
               (55.0, 8.5), (53.5, 7.0), (53.3, 5.0), (52.0, 4.2), (51.3, 3.3), (51.0, 2.0), (50.0, 1.5),
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
                + AA[_i_aden:_i_ujung + 1] + [(45, 140)] + EROPA_UTARA + LAUT_TENGAH_UTARA)
BRITANIA = [(50.1, -5.7), (50.8, 0.8), (51.4, 1.4), (52.9, 1.7), (53.6, 0.0), (55.8, -2.0), (57.7, -1.8),
            (58.6, -3.0), (58.5, -5.0), (56.5, -6.2), (55.0, -4.9), (54.5, -3.4), (53.3, -3.0), (52.8, -4.7),
            (51.7, -5.2), (51.6, -3.0), (51.2, -4.2), (50.3, -5.0)]
IRLANDIA = [(55.3, -7.3), (54.3, -10.0), (51.6, -10.0), (51.8, -8.0), (52.2, -6.3), (54.0, -6.0)]
JEPANG = [(41.5, 140.0), (40.0, 142.0), (36.0, 140.8), (34.6, 138.5), (33.5, 135.5), (34.3, 132.0), (35.5, 135.0),
          (37.5, 137.0), (39.5, 140.0)]

AMERIKA = [(75.0, -118.0), (72.0, -80.0), (66.0, -62.0), (60.0, -64.0), (55.0, -60.0), (52.0, -56.0),
           (47.5, -52.7), (46.5, -60.0), (45.0, -61.0), (44.0, -66.0), (43.5, -70.0), (41.5, -70.0),
           (40.6, -74.0), (39.0, -74.5), (37.0, -76.0), (35.2, -75.5), (33.8, -78.0), (32.0, -81.0),
           (30.0, -81.3), (27.0, -80.0), (25.2, -80.4), (25.8, -81.5), (28.0, -82.7), (30.0, -84.0),
           (30.3, -87.0), (29.5, -89.5), (29.2, -91.5), (29.7, -94.0), (28.0, -97.0), (25.9, -97.2),
           (23.0, -97.8), (21.2, -97.3), (19.2, -96.1), (18.5, -94.5), (18.6, -92.0), (20.5, -90.4),
           (21.4, -87.1), (20.0, -87.4), (18.0, -88.0), (16.0, -88.5), (15.8, -86.0), (15.9, -84.0),
           (14.0, -83.3), (11.0, -83.6), (9.5, -82.2), (9.2, -79.5), (8.5, -77.5), (10.5, -75.5),
           (11.3, -74.0), (12.3, -71.6), (11.0, -68.0), (10.6, -64.0), (10.5, -61.8), (8.5, -60.0),
           (6.8, -58.0), (5.5, -55.0), (4.5, -51.5), (1.5, -50.0), (-1.2, -48.5), (-1.5, -44.0),
           (-2.9, -40.0), (-5.0, -36.5), (-8.0, -34.9), (-13.0, -38.5), (-18.0, -39.5), (-22.9, -42.0),
           (-23.0, -44.5), (-25.5, -48.5), (-29.0, -48.8), (-32.0, -52.0), (-34.9, -56.0), (-36.5, -56.8),
           (-39.0, -62.0), (-41.0, -65.0), (-46.0, -67.0), (-46.0, -75.0), (-40.0, -73.7), (-30.0, -71.5),
           (-23.6, -70.4), (-18.4, -70.3), (-15.4, -75.1), (-12.0, -77.1), (-7.5, -79.6), (-5.8, -81.1),
           (-2.2, -80.9), (0.9, -80.1), (4.0, -77.4), (7.0, -77.8), (8.0, -79.8), (7.5, -81.0), (8.3, -83.0),
           (9.6, -85.0), (11.0, -85.7), (13.0, -87.5), (13.5, -90.0), (14.5, -92.5), (15.7, -95.5),
           (16.5, -99.0), (18.0, -102.5), (19.5, -105.3), (21.5, -105.5), (23.2, -106.5), (25.5, -109.0),
           (28.0, -111.0), (31.0, -113.5), (31.5, -118.0)]
KUBA = [(23.1, -82.4), (23.2, -80.0), (22.4, -78.0), (21.1, -75.7), (20.2, -74.2), (19.9, -77.5), (21.8, -80.5),
        (21.9, -84.9)]
HISPANIOLA = [(19.9, -72.8), (19.7, -70.0), (18.6, -68.3), (18.2, -71.0), (18.0, -74.4), (18.6, -74.4)]
GREENLAND = [(60.0, -44.0), (65.0, -40.0), (70.0, -22.0), (75.0, -20.0), (75.0, -58.0), (68.0, -53.0),
             (64.0, -51.0), (61.0, -48.0)]

DARAT = ([AFRO_EURASIA, BRITANIA, IRLANDIA, JEPANG, AMERIKA, KUBA, HISPANIOLA, GREENLAND, pd.SRI_LANKA,
          pd.MADAGASKAR, pd.FILIPINA, pd.TAIWAN, pd.AUSTRALIA] + pd.INDONESIA)

print("  menyiapkan peta dunia...")
DUNIA = Peta(-118, 140, -45, 74, 14, [], [(19, -100, 3.0), (-15, -70, 4.0), (40, -110, 4.0), (31, 82, 4),
                                          (46.3, 9.0, 1.6), (40.5, 44.0, 2.0), (0, 101, 1.0), (-2, 114, 1.3)],
             seed=37, darat=DARAT)
print("  menyiapkan peta Nusantara...")
NUSA = Peta(90, 142, -16, 24, 60, [], [(-2, 114, 1.5), (0, 101, 1.2), (14, 106, 2), (-2, 121, 1.2)],
            seed=40, darat=pd.SEMUA)
print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 37, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (30, 6, 4), 0.72)

MEKSIKO = (19.4, -99.1)
SPANYOL = (37.2, -6.9)        # Palos de la Frontera
BAHAMA = (24.0, -74.5)
HISPANIOLA_T = (19.7, -72.2)
LISBON = (38.7, -9.1)
GOA = (15.5, 73.8)
MALAKA = (2.2, 102.25)
MALUKU = (0.8, 127.4)
RUTE_COLUMBUS = [SPANYOL, (35.0, -10.0), (28.1, -15.4), (27.0, -25.0), (26.0, -40.0), (25.0, -55.0),
                 (24.4, -68.0), BAHAMA, (21.5, -74.5), HISPANIOLA_T]
RUTE_PORTUGIS = [LISBON, (33.0, -12.0), (20.0, -20.0), (8.0, -18.0), (-5.0, -8.0), (-20.0, 5.0), (-33.0, 13.0),
                 (-37.0, 20.0), (-33.0, 31.0), (-24.0, 37.0), (-15.0, 42.5), (-4.0, 44.0), (6.0, 56.0),
                 (13.0, 68.0), GOA]
RUTE_TIMUR = [GOA, (12.0, 73.5), (7.5, 76.5), (5.5, 80.5), (5.8, 92.0), (5.6, 97.5), (3.5, 100.0), MALAKA,
              (1.1, 104.0), (-3.0, 108.5), (-5.6, 113.5), (-6.5, 118.5), (-5.2, 123.0), (-3.5, 127.0), MALUKU]
SPOT_CABAI = [(-0.5, 101.5), (-2.8, 104.5), (2.8, 98.8), (-6.9, 107.6), (-7.3, 110.2), (-7.6, 112.6),
              (-8.4, 115.2), (-2.3, 113.9), (0.2, 116.8), (-1.5, 110.8), (-4.5, 120.1), (1.0, 124.6),
              (-3.7, 128.2), (-4.0, 138.5), (-8.6, 120.8), (-9.8, 124.2), (-8.6, 116.3), (4.5, 96.8)]
SABANG = (5.89, 95.32)
MERAUKE = (-8.49, 140.40)


# ------------------------------------------------------------------ helper

def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def pop(c, a, lama=0.1):
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


def _bentuk(x, y, panjang, lebar, sudut, lengkung, n=28, ujung_tumpul=False):
    """Poligon buah memanjang (cabai / cabe jawa) di sepanjang garis tengah melengkung."""
    ca, sa = math.cos(sudut), math.sin(sudut)
    kiri, kanan = [], []
    for i in range(n + 1):
        t = i / n
        cx = t * panjang
        cy = lengkung * panjang * math.sin(t * math.pi * 0.9) * t
        if ujung_tumpul:
            w = lebar * (0.55 + 0.45 * math.sin(min(1.0, t * 1.15) * math.pi * 0.5)) * (1 - max(0, t - 0.9) * 6)
        else:
            w = lebar * (1 - t) ** 0.75 * (0.75 + 0.25 * math.sin(min(1.0, t * 4) * math.pi * 0.5))
        dx, dy = 0.0, 1.0
        if 0 < i < n:
            dy_ = lengkung * panjang * (math.sin(t * math.pi * 0.9) + t * math.pi * 0.9 * math.cos(t * math.pi * 0.9))
            nl = math.hypot(panjang, dy_)
            dx, dy = -dy_ / nl, panjang / nl
        for daftar, sgn in ((kiri, 1), (kanan, -1)):
            px = cx + sgn * dx * w / 2
            py = cy + sgn * dy * w / 2
            daftar.append((x + px * ca - py * sa, y + px * sa + py * ca))
    return kiri + kanan[::-1]


def cabai(d, x, y, s=1.0, sudut=0.4, alpha=1.0, warna=MERAH_CABAI, lengkung=0.12):
    """Cabai merah ilustrasi: pangkal di (x, y), ujung ke arah `sudut` (radian)."""
    if alpha <= 0.01 or s <= 0.01:
        return
    a = int(255 * alpha)
    poli = _bentuk(x, y, 300 * s, 70 * s, sudut, lengkung)
    gelap = tuple(int(v * 0.45) for v in warna)
    d.polygon(poli, fill=tuple(warna) + (a,), outline=gelap + (a,))
    kilap = _bentuk(x + 10 * s * math.cos(sudut) - 14 * s * math.sin(sudut),
                    y + 10 * s * math.sin(sudut) - 14 * s * math.cos(sudut) * 0.6,
                    200 * s, 14 * s, sudut, lengkung, n=16)
    d.polygon(kilap, fill=(255, 170, 150, int(a * 0.6)))
    # tangkai hijau
    bx, by = x - 18 * s * math.cos(sudut), y - 18 * s * math.sin(sudut)
    d.ellipse((bx - 30 * s, by - 26 * s, bx + 30 * s, by + 26 * s), fill=HIJAU_TANGKAI + (a,), outline=(25, 60, 20, a))
    ex, ey = bx - 55 * s * math.cos(sudut - 0.6), by - 55 * s * math.sin(sudut - 0.6)
    d.line((bx, by, ex, ey), fill=(50, 105, 40, a), width=max(2, int(12 * s)))


def cabe_jawa(d, x, y, s=1.0, sudut=0.0, alpha=1.0):
    """Cabe jawa / cabya (Piper retrofractum): bulir panjang bertekstur bintil."""
    if alpha <= 0.01 or s <= 0.01:
        return
    a = int(255 * alpha)
    panjang, lebar = 260 * s, 46 * s
    poli = _bentuk(x, y, panjang, lebar, sudut, 0.03, ujung_tumpul=True)
    d.polygon(poli, fill=(165, 45, 30, a), outline=(70, 20, 10, a))
    ca, sa = math.cos(sudut), math.sin(sudut)
    for i in range(1, 14):
        t = i / 14
        for j in (-1, 0, 1):
            px, py = t * panjang, j * lebar * 0.26
            cx, cy = x + px * ca - py * sa, y + px * sa + py * ca
            r = 6 * s
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(110, 28, 18, a))
    bx, by = x - 10 * s * ca, y - 10 * s * sa
    d.line((bx, by, bx - 60 * s * ca, by - 60 * s * sa), fill=(90, 70, 40, a), width=max(2, int(8 * s)))


def lada(d, x, y, s=1.0, alpha=1.0):
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    rng = random.Random(4)
    for _ in range(26):
        px, py = x + rng.gauss(0, 42 * s), y + rng.gauss(0, 26 * s)
        r = rng.uniform(13, 18) * s
        d.ellipse((px - r, py - r, px + r, py + r), fill=(40, 30, 25, a), outline=(15, 10, 8, a))
        d.ellipse((px - r * 0.4, py - r * 0.6, px, py - r * 0.2), fill=(110, 95, 80, int(a * 0.7)))


def jahe(d, x, y, s=1.0, alpha=1.0):
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    isi, garis = (215, 175, 110, a), (130, 90, 45, a)
    for dx, dy, rx, ry in [(0, 0, 70, 38), (-70, -20, 45, 30), (65, -30, 40, 34), (40, 34, 36, 26), (-50, 30, 34, 24)]:
        d.ellipse((x + (dx - rx) * s, y + (dy - ry) * s, x + (dx + rx) * s, y + (dy + ry) * s), fill=isi, outline=garis,
                  width=max(1, int(4 * s)))
    for i in range(5):
        xx = x + (-60 + i * 30) * s
        d.arc((xx - 14 * s, y - 10 * s, xx + 14 * s, y + 10 * s), 200, 340, fill=garis, width=max(1, int(3 * s)))


def tanaman_cabai(d, x, y, s=1.0, alpha=1.0, t=0.0, seed=0):
    """Pohon cabai kecil (ikon peta) dengan beberapa buah."""
    if alpha <= 0.01 or s <= 0.01:
        return
    a = int(255 * alpha)
    goyang = math.sin(t * 3 + seed) * 2 * s
    d.line((x, y, x + goyang, y - 46 * s), fill=(50, 100, 40, a), width=max(2, int(6 * s)))
    for dx, dy in [(-18, -40), (18, -44), (0, -60), (-10, -24), (14, -26)]:
        d.ellipse((x + goyang + (dx - 14) * s, y + (dy - 9) * s, x + goyang + (dx + 14) * s, y + (dy + 9) * s),
                  fill=(60, 140, 55, a), outline=(25, 70, 20, a))
    for dx, dy, sd in [(-14, -30, 1.9), (10, -34, 1.2), (2, -50, 1.6)]:
        cabai(d, x + goyang + dx * s, y + dy * s, 0.13 * s, sd, alpha)


def kapal(d, x, y, s=1.0, alpha=1.0, arah=1, warna_layar=(245, 238, 220)):
    """Kapal layar kecil (karavel) ilustrasi."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    k = arah
    d.polygon([(x - 46 * s, y), (x + 46 * s, y), (x + 34 * s, y + 20 * s),
               (x - 34 * s, y + 20 * s)], fill=(110, 70, 35, a), outline=(40, 25, 10, a))
    d.line((x, y, x, y - 70 * s), fill=(60, 40, 20, a), width=max(2, int(5 * s)))
    d.polygon([(x + 3 * s, y - 66 * s), (x + 3 * s, y - 10 * s), (x + 40 * s * k, y - 22 * s)],
              fill=warna_layar + (a,), outline=(80, 60, 40, a))
    d.polygon([(x - 3 * s, y - 60 * s), (x - 3 * s, y - 14 * s), (x - 32 * s * k, y - 22 * s)],
              fill=warna_layar + (a,), outline=(80, 60, 40, a))
    d.line((x - 5 * s, y - 50 * s, x + 18 * s, y - 50 * s), fill=(200, 40, 40, a), width=max(2, int(4 * s)))


def label_harga(img, cx, cy, s, alpha=1.0, sudut=8):
    """Label harga gantung: 'Rp100 ribu+ / kg'."""
    if alpha <= 0.01 or s <= 0.01:
        return
    lap = Image.new("RGBA", (520, 300), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.polygon([(70, 40), (500, 40), (500, 260), (70, 260), (20, 150)], fill=(255, 214, 10, 250),
               outline=(60, 40, 0, 255))
    dl.ellipse((48, 136, 76, 164), fill=(60, 40, 0, 255))
    dl.text((285, 110), "Rp100 RIBU+", font=se.font("caption", 66), fill=(150, 20, 15, 255), anchor="mm")
    dl.text((285, 195), "per kilo · Nov 2026", font=se.font("ui", 38), fill=(60, 40, 0, 255), anchor="mm")
    lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, alpha, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


def tag_nama(img, cx, cy, isi, s=1.0, alpha=1.0, warna=(200, 52, 44), uk=64, sudut=0):
    """Label nama (tag kertas dengan tali)."""
    if alpha <= 0.01 or s <= 0.01:
        return
    f = se.font("caption", uk)
    lw = int(f.getlength(isi)) + 70
    lh = uk + 50
    lap = Image.new("RGBA", (lw + 20, lh + 20), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((10, 10, lw + 10, lh + 10), 16, fill=tuple(warna) + (250,), outline=(40, 10, 5, 255), width=5)
    dl.ellipse((22, lh / 2 + 2, 38, lh / 2 + 18), fill=(247, 236, 208, 255))
    dl.text((lw / 2 + 22, lh / 2 + 10), isi, font=f, fill=PUTIH, anchor="mm")
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, alpha, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 900, 560, (230, 60, 30), 1.1 + 0.25 * math.sin(c.t * 4))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 420), "DULU NGGAK", 124, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 545), "ADA CABAI", 124, KUNING, nama_font="caption", stroke=11, stroke_warna=GELAP)
    # cabai raksasa di tengah, berayun
    ayun = math.sin(c.t * 2.0) * 0.05
    cabai(d, 330, 760, 2.05, 0.55 + ayun)
    # tanda silang merah di atas cabai (langsung dari frame 0)
    k = clamp(0.55 + c.t / 0.5)
    d.line((250, 690, lerp(250, 860, k), lerp(690, 1240, k)), fill=(255, 40, 30, 235), width=26)
    k2 = clamp(c.t / 0.5)
    if k2 > 0:
        d.line((860, 690, lerp(860, 250, k2), lerp(690, 1240, k2)), fill=(255, 40, 30, 235), width=26)
    # label harga (tren) muncul
    a = c.p(0.16, 0.22) * (1 - c.p(0.56, 0.6))
    label_harga(img, 760, 1150, 0.85 * pop(c, 0.16), alpha=a, sudut=10)
    a2 = c.p(0.4, 0.46) * (1 - c.p(0.6, 0.64))
    stempel(img, "PENDATANG!", 330, 1130, 0.8 * pop(c, 0.4) * (1 if a2 > 0 else 0), uk=70, sudut=-10)
    a3 = c.p(0.66, 0.72)
    if a3 > 0:
        pita(img, 1250, "Namanya pun… pinjaman?", uk=56, alpha=a3)
    hdr(img, "Asal-usul", alpha=c.p(0.85, 0.95))
    return img


def a_dulu(c):
    img = LATAR.copy()
    se.panel(img, (70, 400, 1010, 1310), alpha=c.p(0, 0.06))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 470), "Pedasnya dulu dari mana?", 54, (150, 40, 30), nama_font="judul", alpha=c.p(0.0, 0.08))
    # tiga bumbu muncul bergantian
    a1, a2, a3 = c.p(0.2, 0.27), c.p(0.28, 0.35), c.p(0.36, 0.43)
    lada(d, 230, 630, 1.4, a1)
    se.teks(d, (230, 760), "lada", 50, TINTA, alpha=a1)
    jahe(d, 520, 630, 1.25, a2)
    se.teks(d, (520, 760), "jahe", 50, TINTA, alpha=a2)
    cabe_jawa(d, 700, 690, 1.05, -0.5, a3)
    se.teks(d, (860, 760), "cabya", 54, (150, 30, 20), nama_font="tangan", alpha=a3)
    # kartu prasasti
    a4 = c.p(0.55, 0.62)
    if a4 > 0:
        se.kartu(img, 540, 930, "\"cabya\" tercatat di prasasti", "dan naskah Jawa Kuno", COKLAT, alpha=a4, tiang=False,
                 skala=pop(c, 0.55) * 1.2)
        d = ImageDraw.Draw(img, "RGBA")
    a5 = c.p(0.72, 0.8)
    if a5 > 0:
        s = pop(c, 0.72)
        se.teks(d, (540, 1130), "ABAD KE-10", int(110 * s) + 1, MERAH, nama_font="caption", stroke=8,
                stroke_warna=PUTIH, alpha=a5)
    hdr(img, "Sebelum abad ke-16")
    return img


def a_amerika(c):
    kamera = se.kamera_antara(cam(DUNIA, 20.0, -20.0, 1.25), cam(DUNIA, 12.0, -88.0, 1.6), c.p(0.0, 0.45))
    img = se.render_peta(DUNIA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.2, 0.3)
    for nama, ll in {"AMERIKA": (35.0, -98.0), "Samudra Atlantik": (28.0, -52.0)}.items():
        x, y = layar(DUNIA, kamera, ll)
        label(d, (x, y), nama, 48 if nama == "AMERIKA" else 36, alpha=a)
    mx, my = layar(DUNIA, kamera, MEKSIKO)
    a2 = c.p(0.45, 0.55)
    if a2 > 0:
        se.glow(img, mx, my, 200, (255, 120, 60), 1.2 * a2)
        d = ImageDraw.Draw(img, "RGBA")
        rng = random.Random(9)
        for i in range(9):
            k = c.p(0.5 + i * 0.03, 0.58 + i * 0.03)
            px, py = mx + rng.uniform(-150, 150), my + rng.uniform(-90, 110)
            tanaman_cabai(d, px, py, 1.3 * back_out(k), k, c.t, i)
        titik_kota(d, mx, my, "MEKSIKO", a2, MERAH_CABAI, dy=-70, uk=46, t=c.t)
    se.kartu(img, 540, 1190, "Ditanam sejak ribuan tahun lalu", "Meksiko, Benua Amerika", HIJAU_TANGKAI,
             alpha=c.p(0.7, 0.78), tiang=False, skala=pop(c, 0.7) * 1.15)
    hdr(img, "Asalnya dari jauh")
    return img


def a_columbus(c):
    k = c.p(0.12, 0.62)
    pos, _ = se.titik_di_jalur([DUNIA.px(*ll) for ll in RUTE_COLUMBUS], k)
    k0 = cam(DUNIA, 32.0, -18.0, 1.5)
    k1 = cam(DUNIA, 23.0, -66.0, 1.7)
    kamera = se.kamera_antara(k0, k1, c.p(0.1, 0.65))
    img = se.render_peta(DUNIA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    titik = [layar(DUNIA, kamera, ll) for ll in RUTE_COLUMBUS]
    se.garis_putus(d, titik, k, (200, 40, 30), tebal=7, putus=18, celah=12)
    sx, sy = kamera.layar(*pos)
    sx0, sy0 = layar(DUNIA, kamera, SPANYOL)
    titik_kota(d, sx0, sy0, "Spanyol", 1.0, BIRU, dy=-55, t=c.t, dx=40)
    kapal(d, sx, sy - 10, 1.3, 1.0, arah=-1)
    se.kartu(img, 540, 470, "1492 · Columbus", "cari jalan laut ke India, negeri lada", BIRU,
             alpha=c.p(0.02, 0.1) * (1 - c.p(0.62, 0.66)), tiang=False, skala=pop(c, 0.02) * 1.15)
    a = c.p(0.6, 0.68)
    if a > 0:
        hx, hy = layar(DUNIA, kamera, HISPANIOLA_T)
        label(d, (hx + 10, hy + 60), "Karibia", 42, alpha=a)
        cabai(d, hx - 120, hy - 230, 0.6, 0.4, a)
        se.kartu(img, 540, 1180, "\"Ini sejenis lada!\"", "dinamai pimiento = lada", MERAH, alpha=c.p(0.72, 0.8),
                 tiang=False, skala=pop(c, 0.72) * 1.2)
    hdr(img, "Nyasar ke Amerika")
    return img


def a_portugis(c):
    k = c.p(0.1, 0.7)
    pos, _ = se.titik_di_jalur([DUNIA.px(*ll) for ll in RUTE_PORTUGIS], k)
    kamera = se.kamera_antara(cam(DUNIA, 5.0, 14.0, 1.22), cam(DUNIA, 5.0, 56.0, 1.22), c.p(0.15, 0.72))
    img = se.render_peta(DUNIA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    titik = [layar(DUNIA, kamera, ll) for ll in RUTE_PORTUGIS]
    se.garis_putus(d, titik, k, (30, 90, 40), tebal=7, putus=18, celah=12)
    lx, ly = layar(DUNIA, kamera, LISBON)
    titik_kota(d, lx, ly, "Portugal", 1.0, BIRU, dy=-55, t=c.t)
    sx, sy = kamera.layar(*pos)
    kapal(d, sx, sy - 10, 1.2, 1.0, arah=1, warna_layar=(250, 245, 230))
    cabai(d, sx + 30, sy - 70, 0.22, 0.6)
    a = c.p(0.68, 0.76)
    if a > 0:
        gx, gy = layar(DUNIA, kamera, GOA)
        se.glow(img, gx, gy, 140, (255, 200, 80), a)
        d = ImageDraw.Draw(img, "RGBA")
        for i, (dx, dy) in enumerate([(-30, 40), (20, 60), (50, 20)]):
            tanaman_cabai(d, gx + dx, gy + dy, 1.2 * back_out(c.p(0.7 + i * 0.03, 0.78 + i * 0.03)), a, c.t, i)
        titik_kota(d, gx, gy, "Goa, India", a, MERAH_CABAI, dy=-60, t=c.t)
    se.kartu(img, 540, 470, "Pelaut Portugis", "bawa cabai keliling dunia", (30, 90, 40),
             alpha=c.p(0.02, 0.1), tiang=False, skala=pop(c, 0.02) * 1.15)
    se.kartu(img, 540, 1220, "< 30 tahun setelah Columbus", "cabai sudah tumbuh di Goa", MERAH,
             alpha=c.p(0.76, 0.84), tiang=False, skala=pop(c, 0.76) * 1.15)
    hdr(img, "Abad ke-16")
    return img


def a_nusantara(c):
    kamera = se.kamera_antara(cam(DUNIA, 8.0, 86.0, 1.6), cam(DUNIA, 0.0, 112.0, 2.0), c.p(0.0, 0.7))
    img = se.render_peta(DUNIA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    k = c.p(0.08, 0.72)
    titik = [layar(DUNIA, kamera, ll) for ll in RUTE_TIMUR]
    se.garis_putus(d, titik, k, (30, 90, 40), tebal=7, putus=18, celah=12)
    pos, _ = se.titik_di_jalur([DUNIA.px(*ll) for ll in RUTE_TIMUR], k)
    gx, gy = layar(DUNIA, kamera, GOA)
    titik_kota(d, gx, gy, "Goa", 1.0, MERAH_CABAI, dy=-55, t=c.t)
    am = c.p(0.3, 0.38)
    mx, my = layar(DUNIA, kamera, MALAKA)
    titik_kota(d, mx, my, "Malaka", am, BIRU, dy=-55, t=c.t, dx=-30)
    au = c.p(0.62, 0.7)
    ux, uy = layar(DUNIA, kamera, MALUKU)
    titik_kota(d, ux, uy, "Maluku", au, (240, 160, 40), dy=-55, t=c.t)
    sx, sy = kamera.layar(*pos)
    kapal(d, sx, sy - 10, 1.2, 1.0, arah=1)
    cabai(d, sx + 30, sy - 70, 0.22, 0.6)
    label(d, (540, 1000), "jalur rempah", 44, (30, 70, 30), alpha=c.p(0.15, 0.25))
    se.kartu(img, 540, 470, "Malaka direbut Portugis", "tahun 1511", BIRU, alpha=c.p(0.32, 0.4) * (1 - c.p(0.7, 0.74)),
             tiang=False, skala=pop(c, 0.32) * 1.15)
    a = c.p(0.76, 0.84)
    if a > 0:
        pita(img, 1250, "Abad ke-16: cabai sampai Nusantara", uk=50, alpha=a, warna_garis=(30, 90, 40))
    hdr(img, "Ikut kapal dagang")
    return img


def a_tumbuh(c):
    kamera = se.kamera_antara(cam(NUSA, -2.5, 113.0, 0.62), cam(NUSA, -3.5, 113.0, 0.68), c.p(0.0, 1.0))
    img = se.render_peta(NUSA, kamera)
    se.tint(img, (255, 200, 120), 0.08)
    d = ImageDraw.Draw(img, "RGBA")
    for i, ll in enumerate(SPOT_CABAI):
        k = c.p(0.12 + i * 0.022, 0.2 + i * 0.022)
        x, y = layar(NUSA, kamera, ll)
        tanaman_cabai(d, x, y, 1.25 * back_out(k), k, c.t, i)
    se.kartu(img, 540, 470, "Cocok sama iklim tropis", "sampai ke seluruh Nusantara", HIJAU_TANGKAI,
             alpha=c.p(0.05, 0.12), tiang=False, skala=pop(c, 0.05) * 1.15)
    a = c.p(0.6, 0.68)
    if a > 0:
        se.panel(img, (110, 1010, 970, 1290), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1075), "SAMBAL", 60, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (330, 1190), "hangat", 54, (150, 110, 60), nama_font="tangan", alpha=a)
        se.garis_putus(d, [(440, 1190), (620, 1190)], c.p(0.66, 0.74), (180, 40, 30), tebal=7, putus=14, celah=8)
        b = c.p(0.72, 0.8)
        se.teks(d, (770, 1190), "PEDAS!", int(64 * pop(c, 0.72)) + 1, MERAH_CABAI, nama_font="caption", alpha=b)
    hdr(img, "Pelan-pelan jadi wajib")
    return img


def a_nama(c):
    img = LATAR.copy()
    se.panel(img, (60, 390, 1020, 1320), alpha=c.p(0, 0.05))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 460), "Soal namanya…", 58, (150, 40, 30), nama_font="judul", alpha=c.p(0.0, 0.06))
    # kiri: cabe jawa (pemilik asli), kanan: cabai Amerika
    cabe_jawa(d, 140, 760, 1.15, 0.0)
    a_cabai = c.p(0.3, 0.38)
    cabai(d, 640, 690, 1.1 * pop(c, 0.3), 0.75, a_cabai)
    se.teks(d, (280, 850), "Piper retrofractum", 34, (90, 70, 50), nama_font="tangan_tipis", alpha=c.p(0.05, 0.12))
    se.teks(d, (290, 900), "keluarga lada", 38, (90, 70, 50), nama_font="tangan", alpha=c.p(0.1, 0.16))
    se.teks(d, (790, 1010), "dari Amerika", 38, (90, 70, 50), nama_font="tangan", alpha=a_cabai)
    # tag "CABAI" pindah dari kiri ke kanan
    m = c.p(0.42, 0.58)
    tx = lerp(290, 760, m)
    ty = lerp(620, 560, m) - math.sin(m * math.pi) * 120
    tag_nama(img, tx, ty, "CABAI", 1.0, 1.0, sudut=lerp(-6, 8, m))
    # kiri dapat nama baru
    a2 = c.p(0.64, 0.72)
    tag_nama(img, 290, 620, "cabe jawa", 0.85 * pop(c, 0.64), a2, warna=(110, 80, 50), uk=56, sudut=-6)
    a3 = c.p(0.8, 0.88)
    if a3 > 0:
        se.kartu(img, 540, 1150, "Sekarang lebih sering jadi bahan jamu", "", COKLAT, alpha=a3, tiang=False,
                 skala=pop(c, 0.8) * 1.15)
    stempel(img, "DIAMBIL ALIH!", 760, 860, 0.75 * pop(c, 0.56) * (1 if c.p(0.56, 0.57) > 0 else 0), uk=64, sudut=8)
    hdr(img, "Pemilik asli nama \"cabai\"")
    return img


def a_sekarang(c):
    kamera = se.kamera_antara(cam(NUSA, -2.5, 116.0, 0.56), cam(NUSA, -2.5, 116.0, 0.6), c.p(0.0, 1.0))
    img = se.render_peta(NUSA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    for i, ll in enumerate(SPOT_CABAI):
        x, y = layar(NUSA, kamera, ll)
        tanaman_cabai(d, x, y, 1.1, 1.0, c.t, i)
    a = c.p(0.05, 0.25)
    sx, sy = layar(NUSA, kamera, SABANG)
    mx, my = layar(NUSA, kamera, MERAUKE)
    se.garis_putus(d, [(sx, sy), (mx, my)], a, (200, 40, 30), tebal=6, putus=16, celah=10, panah=False)
    titik_kota(d, sx, sy, "Sabang", c.p(0.05, 0.12), MERAH_CABAI, dy=-50, t=c.t, dx=60)
    titik_kota(d, mx, my, "Merauke", c.p(0.2, 0.27), MERAH_CABAI, dy=50, t=c.t, dx=-60)
    se.kartu(img, 540, 470, "Bumbu wajib se-Indonesia", "", MERAH, alpha=c.p(0.05, 0.12), tiang=False,
             skala=pop(c, 0.05) * 1.2)
    label_harga(img, 540, 1130, 1.0 * pop(c, 0.5), alpha=c.p(0.5, 0.56), sudut=-6)
    a2 = c.p(0.72, 0.78)
    stempel(img, "HEBOH!", 820, 1000, 0.8 * pop(c, 0.72) * (1 if a2 > 0 else 0), uk=70, sudut=12)
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
    kamera = Kamera(*cam(DUNIA, 10.0, 10.0, 1.22))
    img = se.render_peta(DUNIA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    titik = [layar(DUNIA, kamera, ll) for ll in RUTE_COLUMBUS[::-1]] + \
        [layar(DUNIA, kamera, ll) for ll in RUTE_PORTUGIS] + [layar(DUNIA, kamera, ll) for ll in RUTE_TIMUR]
    se.garis_putus(d, titik, 1.0, (200, 40, 30), tebal=6, putus=16, celah=10, panah=False)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1040), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Sambal di piringmu", 54, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 650), "= perjalanan keliling dunia", 42, (90, 70, 50), alpha=a)
        cabai(d, 400, 760, 0.9, 0.35 + math.sin(c.t * 2) * 0.05, a)
        se.teks(d, (540, 970), "± 500 TAHUN", 70, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Dulu, nenek moyang kita nggak kenal cabai. Lagi rame harga cabai rawit tembus seratus ribu "
                   "sekilo? Padahal cabai itu pendatang. Bahkan namanya, ngambil punya tanaman lain.",
           a_hook, transisi=False),
    Adegan("dulu", "Terus, dulu pedasnya dari mana? Dari lada, jahe, dan buah panjang bernama cabya. "
                   "Cabya udah tercatat di prasasti dan naskah Jawa Kuno, abad kesepuluh.", a_dulu),
    Adegan("amerika", "Cabai yang kita kenal sekarang asalnya dari Benua Amerika. Di Meksiko, cabai udah "
                      "ditanam sejak ribuan tahun lalu.", a_amerika),
    Adegan("columbus", "Tahun empat belas sembilan puluh dua, Columbus nyari jalan ke India, negerinya lada. "
                       "Dia malah nyasar ke Karibia, ketemu buah merah yang pedas, dan dikira sejenis lada.",
           a_columbus, transisi=False),
    Adegan("portugis", "Tapi yang bikin cabai keliling dunia, justru pelaut Portugis. Kurang dari tiga puluh tahun "
                       "setelah Columbus, cabai udah tumbuh di Goa, India.", a_portugis),
    Adegan("nusantara", "Dari situ, cabai ikut kapal dagang ke timur, lewat Malaka yang direbut Portugis tahun lima "
                        "belas sebelas. Di abad keenam belas, cabai akhirnya sampai di Nusantara.",
           a_nusantara, transisi=False),
    Adegan("tumbuh", "Ternyata, cabai cocok banget sama iklim tropis kita. Pelan-pelan, sambal yang tadinya cuma "
                     "hangat, jadi pedas kayak sekarang.", a_tumbuh),
    Adegan("nama", "Nah, soal namanya. Kata cabai itu aslinya milik si cabya, keluarga lada. Begitu cabai Amerika "
                   "datang, namanya diambil alih. Yang asli malah jadi cabe jawa, dan sekarang lebih sering buat "
                   "jamu.", a_nama),
    Adegan("sekarang", "Sekarang, cabai jadi bumbu wajib dari Sabang sampai Merauke. Harganya naik dikit aja, satu "
                       "negara langsung heboh.", a_sekarang),
    Adegan("penutup", "Jadi, sambal di piringmu itu hasil perjalanan keliling dunia, sekitar lima ratus tahun. "
                      "Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
