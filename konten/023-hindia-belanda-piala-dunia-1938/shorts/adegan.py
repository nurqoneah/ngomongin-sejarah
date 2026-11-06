"""Shorts ±88 detik: Hindia Belanda di Piala Dunia 1938 — satu-satunya pertandingan kita di Piala Dunia.

Visual: (1) ilustrasi stadion malam, (2) peta dunia lama Nusantara → Eropa (rute kapal ilustratif),
(3) peta Eropa Barat dekat (Reims), (4) papan skor & bagan sistem gugur.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "hindia-belanda-piala-dunia-1938-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "PIALA DUNIA 1938"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
ORANYE = (235, 120, 25)
HIJAU_LAP = (46, 125, 60)
MERAH_HU = (190, 40, 40)
BIRU = (30, 80, 150)
ABU = (60, 60, 70)
EMAS_T = (255, 214, 120)

# ------------------------------------------------------------------ garis pantai Afro-Eurasia (disederhanakan)

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
EROPA_UTARA = [(62.0, 125.0), (62.0, 30.0), (56.0, 21.0), (54.0, 14.0), (54.5, 10.0), (57.5, 10.5), (57.0, 8.0),
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
                + AA[_i_aden:_i_ujung + 1] + EROPA_UTARA + LAUT_TENGAH_UTARA)
BRITANIA = [(50.1, -5.7), (50.8, 0.8), (51.4, 1.4), (52.9, 1.7), (53.6, 0.0), (55.8, -2.0), (57.7, -1.8),
            (58.6, -3.0), (58.5, -5.0), (56.5, -6.2), (55.0, -4.9), (54.5, -3.4), (53.3, -3.0), (52.8, -4.7),
            (51.7, -5.2), (51.6, -3.0), (51.2, -4.2), (50.3, -5.0)]
IRLANDIA = [(55.3, -7.3), (54.3, -10.0), (51.6, -10.0), (51.8, -8.0), (52.2, -6.3), (54.0, -6.0)]
SISILIA = [(38.2, 12.4), (38.3, 15.6), (36.7, 15.1), (37.6, 12.6)]
SARDINIA = [(41.2, 9.2), (40.9, 9.8), (39.1, 9.6), (39.0, 8.4), (40.9, 8.2)]
KORSIKA = [(43.0, 9.4), (41.4, 9.2), (41.7, 8.6), (42.8, 8.6)]
KRETA = [(35.6, 23.6), (35.4, 26.3), (35.0, 26.1), (35.2, 23.5)]
DARAT = ([AFRO_EURASIA, BRITANIA, IRLANDIA, SISILIA, SARDINIA, KORSIKA, KRETA, pd.SRI_LANKA, pd.MADAGASKAR,
          pd.FILIPINA, pd.AUSTRALIA] + pd.INDONESIA)

print("  menyiapkan peta dunia lama...")
DUNIA = Peta(-20, 142, -40, 62, 30, [], [(46.3, 9.0, 1.6), (31, 82, 4), (0, 101, 1.0), (-2, 114, 1.3),
                                          (40.5, 44.0, 2.0), (31.0, -6.0, 1.5)], seed=38, darat=DARAT)
print("  menyiapkan peta Eropa Barat...")
EROPA = Peta(-6, 16, 41, 56, 130, [], [(46.3, 9.0, 1.2), (42.8, 0.5, 0.6)], seed=39, darat=DARAT)
print("  menyiapkan peta Nusantara...")
NUSA = Peta(90, 142, -16, 24, 60, [], [(-2, 114, 1.5), (0, 101, 1.2), (14, 106, 2), (-2, 121, 1.2)],
            seed=40, darat=pd.SEMUA)

PRIOK = (-6.1, 106.88)
REIMS = (49.25, 4.03)
DEN_HAAG = (52.08, 4.3)
BUDAPEST = (47.5, 19.04)
# rute kapal ilustratif: Tanjung Priok → Selat Sunda → Samudra Hindia → Suez → Laut Tengah → Belanda
RUTE_KAPAL = [PRIOK, (-6.0, 105.9), (-5.5, 104.6), (1.0, 95.0), (5.9, 80.5), (12.5, 52.0), (12.6, 43.4),
              (20.0, 38.5), (27.5, 33.8), (31.4, 32.4), (33.5, 25.0), (37.4, 11.5), (37.0, 1.0), (36.0, -5.6),
              (36.8, -9.8), (43.8, -9.4), (47.5, -6.0), (49.6, -3.0), (51.0, 1.6), (51.95, 4.05)]


# ------------------------------------------------------------------ helper

def cam(lat, lon, zoom, p=DUNIA):
    x, y = p.px(lat, lon)
    return (x, y, zoom)


def peta(kamera, p=DUNIA):
    img = se.render_peta(p, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(kamera, ll, p=DUNIA):
    return kamera.layar(*p.px(*ll))


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def hdr(img, sub="Prancis, Juni 1938", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def pop(c, a):
    return back_out((c.t / c.d - a) / 0.1)


def bola(d, x, y, r, putar=0.0, alpha=1.0):
    """Bola kulit klasik: lingkaran krem + jahitan."""
    a = int(255 * alpha)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(205, 150, 85, a), outline=(60, 35, 15, a), width=max(2, int(r * 0.08)))
    for k in range(3):
        ang = putar + k * math.pi / 3
        dx, dy = math.cos(ang) * r * 0.92, math.sin(ang) * r * 0.92
        d.line((x - dx, y - dy, x + dx, y + dy), fill=(90, 55, 25, a), width=max(2, int(r * 0.06)))
    d.ellipse((x - r * 0.55, y - r * 0.7, x - r * 0.1, y - r * 0.35), fill=(255, 230, 190, int(90 * alpha)))


def kacamata(d, x, y, s=1.0, alpha=1.0, warna=(30, 25, 20)):
    a = int(255 * alpha)
    r = 52 * s
    for cx in (x - 70 * s, x + 70 * s):
        d.ellipse((cx - r, y - r, cx + r, y + r), fill=(220, 235, 245, int(120 * alpha)), outline=warna + (a,),
                  width=max(3, int(10 * s)))
    d.arc((x - 22 * s, y - 22 * s, x + 22 * s, y + 18 * s), 200, 340, fill=warna + (a,), width=max(3, int(9 * s)))
    d.line((x - 122 * s, y - 10 * s, x - 165 * s, y - 25 * s), fill=warna + (a,), width=max(3, int(9 * s)))
    d.line((x + 122 * s, y - 10 * s, x + 165 * s, y - 25 * s), fill=warna + (a,), width=max(3, int(9 * s)))


def pemain(d, x, y, warna, s=1.0, alpha=1.0, nomor=""):
    """Pemain tanpa wajah: kaus bulat berwarna + celana."""
    a = int(255 * alpha)
    d.ellipse((x - 16 * s, y - 60 * s, x + 16 * s, y - 28 * s), fill=(70, 50, 35, a))  # kepala polos (siluet)
    d.rounded_rectangle((x - 26 * s, y - 28 * s, x + 26 * s, y + 18 * s), int(10 * s), fill=warna + (a,),
                        outline=(30, 20, 10, a), width=max(2, int(3 * s)))
    d.rectangle((x - 22 * s, y + 18 * s, x + 22 * s, y + 36 * s), fill=(245, 245, 245, a), outline=(30, 20, 10, a))
    if nomor:
        d.text((x, y - 5 * s), nomor, font=se.font("ui", int(24 * s)), fill=(255, 255, 255, a), anchor="mm")


def kapal(d, x, y, s=1.0, alpha=1.0, arah=1):
    """Kapal penumpang kecil (tampak samping) — arah 1 = hadap kanan."""
    a = int(255 * alpha)
    p = lambda px, py: (x + px * s * arah, y + py * s)
    d.polygon([p(-60, 0), p(60, 0), p(48, 22), p(-52, 22)], fill=(40, 40, 50, a), outline=(15, 15, 20, a))
    d.rectangle((min(p(-38, -18)[0], p(34, 0)[0]), y - 18 * s, max(p(-38, -18)[0], p(34, 0)[0]), y),
                fill=(240, 235, 225, a), outline=(40, 40, 50, a))
    for fx in (-12, 12):
        q0, q1 = p(fx - 6, -40), p(fx + 6, -18)
        d.rectangle((min(q0[0], q1[0]), q0[1], max(q0[0], q1[0]), q1[1]), fill=(210, 140, 40, a),
                    outline=(40, 30, 20, a))


def langit_malam():
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    atas = np.array((10, 14, 30), np.float32)
    bawah = np.array((40, 45, 70), np.float32)
    arr = (atas * (1 - g) + bawah * g).repeat(W, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")


_LANGIT = None


def stadion(t, tribun_kedip=True):
    """Ilustrasi stadion malam: tribun, lampu sorot, lapangan perspektif."""
    global _LANGIT
    if _LANGIT is None:
        _LANGIT = langit_malam()
    img = _LANGIT.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # tribun
    d.polygon([(0, 700), (W, 700), (W, 1080), (0, 1080)], fill=(35, 30, 40, 255))
    rng = random.Random(4)
    for i in range(700):
        x, y = rng.uniform(0, W), rng.uniform(720, 1070)
        col = rng.choice([(200, 190, 170), (150, 140, 130), (230, 140, 60), (120, 110, 100)])
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=col + (200,))
    # lapangan perspektif
    d.polygon([(260, 1080), (820, 1080), (W + 260, H), (-260, H)], fill=HIJAU_LAP + (255,))
    for k in range(8):
        y0 = 1080 + (H - 1080) * (k / 8) ** 1.4
        y1 = 1080 + (H - 1080) * ((k + 0.5) / 8) ** 1.4
        f0, f1 = (y0 - 1080) / (H - 1080), (y1 - 1080) / (H - 1080)
        d.polygon([(260 - 520 * f0, y0), (820 + 520 * f0, y0), (820 + 520 * f1, y1), (260 - 520 * f1, y1)],
                  fill=(56, 140, 70, 255))
    d.line((260, 1080, -260, H), fill=(240, 240, 240, 220), width=6)
    d.line((820, 1080, W + 260, H), fill=(240, 240, 240, 220), width=6)
    d.line((260, 1082, 820, 1082), fill=(240, 240, 240, 220), width=5)
    d.ellipse((540 - 300, 1380 - 70, 540 + 300, 1380 + 70), outline=(240, 240, 240, 200), width=6)
    # lampu sorot
    for lx in (120, 960):
        d.rectangle((lx - 6, 420, lx + 6, 700), fill=(70, 70, 80, 255))
        d.rectangle((lx - 70, 380, lx + 70, 440), fill=(220, 220, 200, 255), outline=(60, 60, 70, 255), width=4)
        se.glow(img, lx, 410, 260, (255, 245, 200), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    # kilatan kamera di tribun
    if tribun_kedip:
        rk = random.Random(int(t * 8))
        for _ in range(6):
            x, y = rk.uniform(30, W - 30), rk.uniform(730, 1060)
            d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(255, 255, 255, 230))
    return img


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = stadion(c.t)
    d = ImageDraw.Draw(img, "RGBA")
    # bola meluncur ke arah kamera
    k = clamp(c.t / c.d)
    bola(d, 540 + math.sin(c.t * 2) * 40, 1250 - 60 * k, 70 + 50 * k, c.t * 3)
    s = 1 + 0.04 * math.sin(c.t * 6)
    se.teks(d, (540, 470), "KITA PERNAH", int(118 * s), PUTIH, nama_font="caption", stroke=10,
            stroke_warna=(20, 10, 5))
    se.teks(d, (540, 600), "DI PIALA DUNIA", int(118 * s), EMAS_T, nama_font="caption", stroke=10,
            stroke_warna=(20, 10, 5))
    sk = back_out(c.t / 0.25)
    se.teks(d, (540, 800), "1938", int(200 * sk) + 1, (255, 180, 60), nama_font="caption", stroke=12,
            stroke_warna=(30, 15, 5))
    a = c.p(0.55, 0.65)
    if a > 0:
        se.kartu(img, 540, 990, "…dan nyimpen rekor yang belum pecah", "", MERAH, alpha=a, tiang=False,
                 skala=pop(c, 0.55))
    hdr(img, alpha=c.p(0.85, 0.97))
    return img


def a_tren(c):
    kamera = Kamera(*cam(2, 112, 0.7, NUSA))
    img, d = peta(kamera, NUSA)
    se.tint(img, (10, 6, 0), 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    a1 = c.p(0.02, 0.1) * (1 - c.p(0.42, 0.48))
    se.kartu(img, 540, 640, "FIFA Matchday Nov 2026", "Timnas vs Yordania batal", ABU, alpha=a1, tiang=False,
             skala=pop(c, 0.02), coret=c.p(0.18, 0.32))
    # hitung mundur tahun
    k = c.p(0.45, 0.85)
    tahun = int(round(lerp(2026, 1938, k)))
    a2 = c.p(0.42, 0.5)
    se.teks(d, (540, 820), str(tahun), 200, EMAS_T, nama_font="caption", stroke=12, stroke_warna=(30, 15, 5),
            alpha=a2)
    se.teks(d, (540, 960), "88 tahun lalu…", 56, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=c.p(0.8, 0.88))
    bola(d, 540, 1150, 60 * c.p(0.8, 0.9) + 1, c.t * 3, alpha=c.p(0.8, 0.88))
    hdr(img, "Lagi rame: Timnas")
    return img


def a_hindia(c):
    kamera = se.kamera_antara(cam(-1.0, 112.0, 0.72, NUSA), cam(-2.0, 114.0, 0.8, NUSA), c.p(0, 1))
    img, d = peta(kamera, NUSA)
    # label wilayah
    a = c.p(0.1, 0.2)
    se.teks(d, (540, 560), "HINDIA BELANDA", 76, (120, 30, 20), nama_font="caption", stroke=7,
            stroke_warna=KREM_LABEL, alpha=a)
    for nama, ll in {"Sumatra": (0.3, 103.2), "Kalimantan": (0.5, 113.5),
                     "Sulawesi": (-2.0, 121.0)}.items():
        x, y = layar(kamera, ll, NUSA)
        label(d, (x, y), nama, 38, TINTA, c.p(0.05, 0.15))
    se.kartu(img, 540, 1220, "Masih tanah jajahan Belanda", "nama 'Indonesia' belum jadi negara", ORANYE,
             alpha=c.p(0.45, 0.55), tiang=False, skala=pop(c, 0.45))
    hdr(img, "1938")
    return img


def a_lolos(c):
    img = stadion(c.t, tribun_kedip=False)
    se.tint(img, (8, 6, 4), 0.55)
    se.panel(img, (70, 420, 1010, 1320), alpha=c.p(0, 0.06))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 500), "KUALIFIKASI ZONA ASIA", 50, (120, 30, 20), nama_font="judul", alpha=c.p(0.02, 0.08))
    se.kartu(img, 540, 650, "Lawan: Jepang", "mundur — lagi perang dengan Tiongkok", MERAH, alpha=c.p(0.05, 0.12),
             tiang=False, skala=pop(c, 0.05), coret=c.p(0.25, 0.35))
    se.kartu(img, 540, 830, "Pengganti: Amerika Serikat", "ikut mundur", BIRU, alpha=c.p(0.4, 0.47),
             tiang=False, skala=pop(c, 0.4), coret=c.p(0.55, 0.65))
    a = c.p(0.7, 0.78)
    if a > 0:
        sk = pop(c, 0.7)
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        dl.rounded_rectangle((140, 1000, 940, 1170), 24, outline=(30, 130, 60, 255), width=12)
        dl.text((540, 1085), "LOLOS TANPA MAIN", font=se.font("caption", 60), fill=(30, 130, 60, 255), anchor="mm")
        lap = lap.rotate(-6 * sk, center=(540, 1085))
        se.tempel(img, lap, a)
    hdr(img, "Jalan menuju Prancis")
    return img


def a_kapal(c):
    k = c.p(0.05, 0.92)
    pos, _ = se.titik_di_jalur([DUNIA.px(*ll) for ll in RUTE_KAPAL], k)
    # kamera ikut kapal, sedikit tertinggal
    kamera = Kamera(pos[0], pos[1] - 100, 1.0)
    img, d = peta(kamera)
    titik = [layar(kamera, ll) for ll in RUTE_KAPAL]
    se.garis_putus(d, titik, k, (150, 30, 20), tebal=7, putus=16, celah=10, panah=False)
    for nama, ll in {"BATAVIA": PRIOK, "Belanda": DEN_HAAG}.items():
        x, y = layar(kamera, ll)
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(200, 40, 30, 255), outline=(255, 255, 255, 255), width=3)
        label(d, (x, y + 50), nama, 40, TINTA)
    for nama, ll in {"Samudra Hindia": (-2, 78), "Laut Tengah": (34.5, 18), "EROPA": (48, 15),
                     "AFRIKA": (15, 20), "ASIA": (35, 75), "Laut Merah": (20, 33)}.items():
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 38, (90, 60, 30) if nama.isupper() else (230, 230, 240), 0.9)
    x, y = kamera.layar(*pos)
    kapal(d, x, y - 10 + math.sin(c.t * 4) * 4, 1.3, arah=-1 if titik[-1][0] < x else 1)
    hari = int(1 + 27 * k)
    se.kartu(img, 540, 1260, f"Hari ke-{hari} di laut", "hampir sebulan naik kapal", BIRU, alpha=c.p(0.05, 0.12),
             tiang=False)
    hdr(img, "Tanjung Priok → Eropa")
    return img


def a_tim(c):
    img = stadion(c.t, tribun_kedip=False)
    se.tint(img, (8, 6, 4), 0.55)
    d = ImageDraw.Draw(img, "RGBA")
    grup = [("Pribumi", 700), ("Keturunan Tionghoa", 900), ("Keturunan Belanda", 1100)]
    a_grup = 1 - c.p(0.45, 0.52)
    for i, (nama, y) in enumerate(grup):
        a = c.p(0.04 + i * 0.1, 0.1 + i * 0.1) * a_grup
        if a <= 0:
            continue
        for j, dx in enumerate((-70, 0, 70)):
            pemain(d, 230 + dx, y + 20, ORANYE, 1.3, a, str(i * 3 + j + 2))
        se.kartu(img, 680, y, nama, "", ORANYE, alpha=a, tiang=False, skala=1.1)
    se.teks(d, (540, 520), "SATU TIM, CAMPURAN", 64, PUTIH, nama_font="caption", stroke=7, stroke_warna=(0, 0, 0),
            alpha=c.p(0.04, 0.1) * a_grup)
    b = c.p(0.5, 0.58)
    if b > 0:
        sk = pop(c, 0.5)
        pemain(d, 540, 760, ORANYE, 2.6 * sk, b, "C")
        kacamata(d, 540, 645, 0.45 * sk, c.p(0.75, 0.82))
        se.kartu(img, 540, 1000, "Kapten: Achmad Nawir", "seorang dokter", ORANYE, alpha=b, tiang=False, skala=sk)
        se.teks(d, (540, 1160), "main pakai KACAMATA!", 66, EMAS_T, nama_font="caption", stroke=8,
                stroke_warna=(0, 0, 0), alpha=c.p(0.75, 0.82))
    hdr(img, "Skuad Hindia Belanda")
    return img


def a_reims(c):
    kamera = se.kamera_antara(cam(49.5, 5.5, 1.0, EROPA), cam(49.0, 4.6, 1.2, EROPA), c.p(0.0, 0.6))
    img, d = peta(kamera, EROPA)
    for nama, ll in {"PRANCIS": (47.6, 3.2), "BELANDA": (52.3, 5.7), "JERMAN": (50.3, 8.6),
                     "BELGIA": (50.7, 4.9)}.items():
        x, y = layar(kamera, ll, EROPA)
        label(d, (x, y), nama, 40, (90, 60, 30), 0.85)
    x, y = layar(kamera, REIMS, EROPA)
    pulse = 1 + 0.25 * math.sin(c.t * 6)
    a = c.p(0.15, 0.25)
    d.ellipse((x - 26 * pulse, y - 26 * pulse, x + 26 * pulse, y + 26 * pulse), outline=(200, 30, 20, int(200 * a)),
              width=6)
    d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(200, 30, 20, int(255 * a)), outline=(255, 255, 255, int(255 * a)),
              width=3)
    se.kartu(img, x, y - 20, "Reims", "5 Juni 1938", MERAH, alpha=a, skala=pop(c, 0.15))
    b = c.p(0.55, 0.62)
    if b > 0:
        se.panel(img, (90, 1010, 990, 1290), alpha=b)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (290, 1110), "HINDIA", 50, (200, 100, 20), nama_font="caption", alpha=b)
        se.teks(d, (290, 1170), "BELANDA", 50, (200, 100, 20), nama_font="caption", alpha=b)
        se.teks(d, (540, 1140), "VS", 80, TINTA, nama_font="judul", alpha=b)
        se.teks(d, (790, 1140), "HUNGARIA", 56, MERAH_HU, nama_font="caption", alpha=c.p(0.7, 0.76))
        se.teks(d, (790, 1215), "tim terkuat dunia", 30, (90, 70, 50), nama_font="tangan_tipis",
                alpha=c.p(0.8, 0.86))
    hdr(img, "Babak 16 besar")
    return img


GOL = ["14'", "16'", "25'", "30'", "67'", "88'"]


def a_skor(c):
    img = stadion(c.t)
    se.tint(img, (8, 6, 4), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    # papan skor
    d.rounded_rectangle((90, 420, 990, 760), 26, fill=(15, 15, 18, 245), outline=(200, 200, 200, 255), width=6)
    n = min(6, int(c.p(0.08, 0.5) * 6 + 0.0001))
    se.teks(d, (300, 480), "HUNGARIA", 44, PUTIH, nama_font="ui")
    se.teks(d, (780, 480), "HINDIA BELANDA", 40, PUTIH, nama_font="ui")
    se.teks(d, (300, 630), str(n), 190, (255, 200, 60), nama_font="caption")
    se.teks(d, (540, 630), "–", 150, PUTIH, nama_font="caption")
    se.teks(d, (780, 630), "0", 190, (255, 200, 60), nama_font="caption")
    for i in range(n):
        se.teks(d, (180 + i * 72, 735), GOL[i], 26, (180, 180, 180), nama_font="ui")
    if n >= 1 and c.p(0.08, 0.5) < 1:
        fase = (c.p(0.08, 0.5) * 6) % 1
        if fase < 0.35:
            se.teks(d, (540, 880), "GOL!", 110, MERAH, nama_font="caption", stroke=9, stroke_warna=PUTIH,
                    alpha=1 - fase / 0.35)
    se.kartu(img, 540, 1000, "Kalah 6 – 0", "", MERAH, alpha=c.p(0.5, 0.56), tiang=False, skala=pop(c, 0.5))
    se.kartu(img, 540, 1180, "Hungaria lanjut sampai final", "akhirnya kalah dari Italia", MERAH_HU,
             alpha=c.p(0.68, 0.75), tiang=False, skala=pop(c, 0.68))
    hdr(img, "Reims, 5 Juni 1938")
    return img


def a_rekor(c):
    img = Image.new("RGBA", (W, H), (25, 24, 30, 255))
    d = ImageDraw.Draw(img, "RGBA")
    a0 = 1 - c.p(0.42, 0.48)
    # bagan sistem gugur
    if a0 > 0:
        se.teks(d, (540, 460), "SISTEM GUGUR", 70, EMAS_T, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0),
                alpha=c.p(0.02, 0.08) * a0)
        kotak = [(150, 600, "Hungaria", MERAH_HU), (150, 760, "Hindia Belanda", ORANYE)]
        for x, y, nama, w in kotak:
            d.rounded_rectangle((x, y - 45, x + 400, y + 45), 14, fill=(247, 236, 208, int(255 * a0)),
                                outline=w + (int(255 * a0),), width=6)
            d.text((x + 200, y), nama, font=se.font("tangan", 38), fill=TINTA + (int(255 * a0),), anchor="mm")
        g = c.p(0.08, 0.25)
        d.line((550, 600, 550 + 80 * g, 600), fill=(255, 255, 255, int(255 * a0)), width=8)
        d.line((550, 760, 550 + 80 * g, 760), fill=(255, 255, 255, int(255 * a0)), width=8)
        d.line((630, 600, 630, 600 + 160 * g), fill=(255, 255, 255, int(255 * a0)), width=8)
        d.line((630, 680, 630 + 150 * c.p(0.2, 0.3), 680), fill=(255, 255, 255, int(255 * a0)), width=8)
        if c.p(0.28, 0.32) > 0:
            se.teks(d, (880, 680), "lanjut", 44, PUTIH, nama_font="tangan", alpha=c.p(0.28, 0.32) * a0)
        b = c.p(0.25, 0.33) * a0
        if b > 0:
            se.teks(d, (540, 950), "Sekali kalah = pulang", 62, MERAH, nama_font="caption", stroke=6,
                    stroke_warna=PUTIH, alpha=b)
            d.line((150, 760, 550, 760), fill=(200, 30, 30, int(255 * b)), width=10)
    # rekor
    r = c.p(0.48, 0.56)
    if r > 0:
        sk = pop(c, 0.48)
        se.teks(d, (540, 520), "REKOR DUNIA", 72, EMAS_T, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0),
                alpha=r)
        se.teks(d, (540, 780), "1", int(400 * sk) + 1, PUTIH, nama_font="caption", stroke=12,
                stroke_warna=MERAH, alpha=r)
        se.teks(d, (540, 1010), "PERTANDINGAN", 84, PUTIH, nama_font="caption", stroke=8, stroke_warna=(0, 0, 0),
                alpha=r)
        se.kartu(img, 540, 1180, "Paling sedikit main di Piala Dunia", "satu-satunya, sampai hari ini", MERAH,
                 alpha=c.p(0.62, 0.7), tiang=False, skala=pop(c, 0.62))
    hdr(img, "Rekornya…")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    img = stadion(c.t, tribun_kedip=False)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1000), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Rekor yang pengin kita pecahin", 46, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 650), "1938 → ???", 60, (170, 30, 20), nama_font="caption", alpha=a)
        bola(d, 540, 810, 90, c.t * 2, a)
        se.teks(d, (540, 950), "Semoga Timnas balik ke Piala Dunia!", 38, (90, 70, 50), alpha=a)
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
    Adegan("hook", "Kita pernah main di Piala Dunia. Beneran. Tahun sembilan belas tiga puluh delapan. "
                   "Dan tim kita nyimpen satu rekor, yang sampai hari ini belum pecah.", a_hook, transisi=False),
    Adegan("tren", "Lagi rame, laga Timnas lawan Yordania di FIFA Matchday November batal? Padahal, delapan puluh "
                   "delapan tahun lalu, tim dari tanah kita udah tampil di panggung sepak bola terbesar dunia.",
           a_tren),
    Adegan("hindia", "Tapi waktu itu, namanya belum Indonesia. Masih Hindia Belanda, tanah jajahan Belanda.", a_hindia),
    Adegan("lolos", "Cara lolosnya juga unik. Lawannya di kualifikasi, Jepang, mundur karena lagi perang dengan "
                    "Tiongkok. Lawan penggantinya, Amerika Serikat, ikut mundur. Jadi mereka lolos, tanpa main "
                    "sekali pun.", a_lolos),
    Adegan("kapal", "Pemainnya berangkat dari Tanjung Priok naik kapal. Hampir sebulan di laut, menuju Eropa.",
           a_kapal),
    Adegan("tim", "Timnya campuran. Ada pemain pribumi, keturunan Tionghoa, sampai keturunan Belanda. Kaptennya, "
                  "Achmad Nawir, seorang dokter. Dan dia main pakai kacamata!", a_tim),
    Adegan("reims", "Nah, bagian paling seru baru mulai. Lima Juni sembilan belas tiga puluh delapan, di kota Reims, "
                    "Prancis. Lawannya, Hungaria. Salah satu tim terkuat dunia saat itu.", a_reims),
    Adegan("skor", "Hasilnya? Kalah enam kosong. Dan Hungaria, terus melaju sampai final.", a_skor),
    Adegan("rekor", "Waktu itu, Piala Dunia pakai sistem gugur. Sekali kalah, langsung pulang. Itulah rekornya. "
                    "Sampai hari ini, kita jadi satu-satunya negara yang cuma pernah main satu kali di Piala Dunia.",
           a_rekor),
    Adegan("penutup", "Sejak itu, kita belum pernah balik lagi. Kalau suatu hari Timnas lolos, rekor itu akhirnya "
                      "pecah. Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
