"""Shorts ±88 detik: Pranata Mangsa — "BMKG"-nya petani Jawa, dan cikal bakal BMKG beneran.

Tren: BMKG umumkan puncak musim hujan Desember 2026 – Februari 2027 → kalender tani Jawa Pranata Mangsa
(dibakukan Pakubuwana VII, 22 Juni 1855; 12 mangsa 23–43 hari; ilmu titen; Lintang Waluku = Orion)
→ mangsa Kanem (9 Nov–21 Des) & Kapitu (22 Des–2 Feb) cocok dengan puncak hujan versi BMKG
→ pengamatan cuaca Dr. Onnen di Bogor 1841 → observatorium Batavia 1866 → 74 penakar hujan 1879
→ payoff: kenapa sekarang sering meleset (tanggal tetap, musim bergeser; tahun ini mundur 20–30 hari).
Visual: langit malam + sawah, roda 12 mangsa, peta Jawa, rasi Orion. Waktu animasi pakai fraksi durasi.
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, KUNING, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "pranata-mangsa-kalender-hujan-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "PRANATA MANGSA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
GELAP = (12, 16, 34)
BIRU = (40, 110, 190)
BIRU_TUA = (25, 60, 120)
ORANYE = (225, 130, 40)
HIJAU_T = (46, 120, 70)

# (nama, mulai, jumlah hari) — total 365
MANGSA = [("Kasa", "22 Jun", 41), ("Karo", "2 Agu", 23), ("Katelu", "25 Agu", 24), ("Kapat", "18 Sep", 25),
          ("Kalima", "13 Okt", 27), ("Kanem", "9 Nov", 43), ("Kapitu", "22 Des", 43), ("Kawolu", "3 Feb", 26),
          ("Kasanga", "1 Mar", 25), ("Kasadasa", "26 Mar", 24), ("Dhesta", "19 Apr", 23), ("Sadha", "12 Mei", 41)]
BASAH = {4, 5, 6, 7, 8}  # Kalima..Kasanga: musim hujan (disederhanakan untuk warna)
KANEM, KAPITU = 5, 6
HARI_INI = sum(m[2] for m in MANGSA[:KANEM]) + 18  # 27 November = hari ke-19 mangsa Kanem

print("  menyiapkan peta Jawa...")
PETA = Peta(103.0, 117.0, -15.0, 1.5, 120, [],
            [(-6.8, 107.0, 0.35), (-7.24, 109.2, 0.3), (-7.54, 110.45, 0.3), (-7.9, 112.6, 0.35), (-8.1, 112.9, 0.3),
             (-7.2, 107.7, 0.3)],
            seed=40, darat=[pd.JAWA, pd.SUMATRA, pd.KALIMANTAN, pd.BALI, pd.LOMBOK, pd.SUMBAWA])

SURAKARTA = (-7.57, 110.82)
BOGOR = (-6.6, 106.8)
BATAVIA = (-6.13, 106.82)
LABEL_PULAU = {"JAWA": (-7.35, 110.0), "SUMATRA": (-3.2, 104.2), "KALIMANTAN": (-2.0, 113.5)}


def _dalam_poligon(lat, lon, poli):
    dalam = False
    n = len(poli)
    for i in range(n):
        (y0, x0), (y1, x1) = poli[i], poli[(i + 1) % n]
        if (y0 > lat) != (y1 > lat):
            xp = x0 + (lat - y0) * (x1 - x0) / (y1 - y0)
            if lon < xp:
                dalam = not dalam
    return dalam


def _stasiun(n=74, seed=79):
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        lat, lon = rng.uniform(-8.5, -6.0), rng.uniform(105.5, 114.3)
        if _dalam_poligon(lat, lon, pd.JAWA) and _dalam_poligon(lat + 0.12, lon, pd.JAWA) and \
                _dalam_poligon(lat - 0.12, lon, pd.JAWA):
            out.append((lat, lon))
    out.sort(key=lambda p: p[1])
    return out


STASIUN = _stasiun()


# ------------------------------------------------------------------ helper

def cam(lat, lon, zoom):
    x, y = PETA.px(lat, lon)
    return (x, y, zoom)


def peta(kamera):
    img = se.render_peta(PETA, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(kamera, ll):
    return kamera.layar(*PETA.px(*ll))


def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def pop(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


def label(d, xy, isi, uk=40, warna=TINTA, alpha=1.0, font="tangan"):
    se.teks(d, xy, isi, uk, warna, nama_font=font, stroke=5, stroke_warna=KREM_LABEL, alpha=alpha)


def titik_kota(d, x, y, nama, alpha=1.0, warna=(255, 200, 60), dy=50, uk=40, t=0.0, dx=0):
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    r = 13 + 3 * math.sin(t * 5)
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=PUTIH + (a,), width=4)
    if nama:
        label(d, (x + dx, y + dy), nama, uk, alpha=alpha)


def stempel(img, isi, cx, cy, s, uk=76, sudut=-8, warna=(210, 30, 30)):
    if s <= 0.01:
        return
    f = se.font("caption", uk)
    lw = int(f.getlength(isi)) + 80
    lap = Image.new("RGBA", (lw, uk + 90), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((10, 10, lw - 10, uk + 80), 22, fill=(247, 236, 208, 225), outline=tuple(warna) + (255,),
                         width=12)
    dl.text((lw / 2, (uk + 90) / 2), isi, font=f, fill=tuple(warna) + (255,), anchor="mm")
    lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, 1.0, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


def pita(img, y, isi, warna_garis=(170, 30, 20), uk=54, alpha=1.0, x0=80, x1=1000, tinggi=110):
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((x0, y - tinggi / 2, x1, y + tinggi / 2), 30, fill=(247, 236, 208, 242),
                         outline=tuple(warna_garis) + (255,), width=6)
    se.tempel(img, lap, alpha)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, ((x0 + x1) / 2, y), isi, uk, warna_garis, nama_font="caption", alpha=alpha)


# ------------------------------------------------------------------ latar langit + sawah

def _daftar_bintang():
    rng = random.Random(11)
    return [(rng.uniform(0, W), rng.uniform(0, 1250), rng.uniform(1.2, 3.6), rng.uniform(0, 6.28)) for _ in range(170)]


BINTANG = _daftar_bintang()


def _gradasi(atas, bawah):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (np.array(atas, np.float32) * (1 - g) + np.array(bawah, np.float32) * g).repeat(W, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")


LANGIT_MALAM = _gradasi((8, 12, 32), (40, 52, 90))
LANGIT_BADAI = _gradasi((22, 26, 38), (70, 78, 96))


def sawah(d, y0=1270, alpha=1.0, warna=(18, 30, 22)):
    """Siluet bukit + petak sawah + gubuk + pohon kelapa di bawah."""
    a = int(255 * alpha)
    d.polygon([(0, y0 - 40), (180, y0 - 110), (360, y0 - 60), (560, y0 - 130), (760, y0 - 70), (930, y0 - 120),
               (W, y0 - 80), (W, H), (0, H)], fill=(28, 40, 34, a))
    d.rectangle((0, y0, W, H), fill=tuple(warna) + (a,))
    for i, yy in enumerate(range(y0 + 30, H, 70)):
        d.line((0, yy, W, yy + (12 if i % 2 else -12)), fill=(60, 90, 70, int(a * 0.6)), width=3)
    # gubuk
    gx, gy = 820, y0 + 10
    d.polygon([(gx - 70, gy - 40), (gx, gy - 100), (gx + 70, gy - 40)], fill=(10, 14, 12, a))
    d.rectangle((gx - 50, gy - 40, gx + 50, gy + 20), fill=(10, 14, 12, a))
    # kelapa
    for kx, tinggi in ((150, 260), (240, 200)):
        d.line((kx, y0 + 10, kx + 25, y0 - tinggi), fill=(10, 14, 12, a), width=10)
        for ang in range(0, 360, 45):
            r = math.radians(ang)
            d.line((kx + 25, y0 - tinggi, kx + 25 + 80 * math.cos(r), y0 - tinggi + 40 * math.sin(r) + 25),
                   fill=(10, 14, 12, a), width=8)


def langit(t, badai=0.0, bintang=1.0):
    img = Image.blend(LANGIT_MALAM, LANGIT_BADAI, clamp(badai))
    d = ImageDraw.Draw(img, "RGBA")
    if bintang > 0.01:
        for x, y, r, f in BINTANG:
            k = 0.55 + 0.45 * math.sin(t * 2.2 + f)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 250, 225, int(220 * k * bintang)))
    return img, d


def kilat(d, x, y, t, alpha=1.0, seed=0):
    if alpha <= 0.01:
        return
    rng = random.Random(seed)
    pts = [(x, y)]
    for _ in range(7):
        x += rng.uniform(-50, 50)
        y += rng.uniform(50, 90)
        pts.append((x, y))
    d.line(pts, fill=(255, 250, 210, int(255 * alpha)), width=7)
    d.line(pts, fill=(255, 255, 255, int(255 * alpha)), width=3)


# ------------------------------------------------------------------ roda 12 mangsa

def _sudut_mangsa():
    out, a = [], -90.0
    for _, _, n in MANGSA:
        b = a + 360 * n / 365
        out.append((a, b))
        a = b
    return out


SUDUT = _sudut_mangsa()


def roda(img, cx, cy, r, t, muncul=1.0, sorot=None, alpha=1.0, jarum=0.0, putar=0.0, label_uk=30,
         tanggal=False, redup=0.0):
    """Roda kalender 12 mangsa. sorot: set indeks yang disorot. jarum: 0..1 alpha jarum 'hari ini'."""
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.ellipse((cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18), fill=(247, 236, 208, 245), outline=(90, 60, 30, 255),
              width=8)
    n_muncul = muncul * 12
    for i, (a0, a1) in enumerate(SUDUT):
        k = clamp(n_muncul - i)
        if k <= 0:
            continue
        basah = i in BASAH
        warna = BIRU if basah else ORANYE
        if sorot is not None and i not in sorot:
            warna = se.lerp_rgb(warna, (200, 190, 170), 0.65 * redup)
        rr = r * (1.06 if sorot is not None and i in sorot else 1.0)
        a0p, a1p = a0 + putar, a0 + putar + (a1 - a0) * k
        d.pieslice((cx - rr, cy - rr, cx + rr, cy + rr), a0p, a1p, fill=tuple(warna) + (255,),
                   outline=(250, 240, 215, 255), width=5)
    d.ellipse((cx - r * 0.34, cy - r * 0.34, cx + r * 0.34, cy + r * 0.34), fill=(247, 236, 208, 255),
              outline=(90, 60, 30, 255), width=6)
    se.tempel(img, lap, alpha)
    d = ImageDraw.Draw(img, "RGBA")
    for i, (a0, a1) in enumerate(SUDUT):
        if clamp(n_muncul - i) < 0.6:
            continue
        m = math.radians((a0 + a1) / 2 + putar)
        x, y = cx + r * 0.68 * math.cos(m), cy + r * 0.68 * math.sin(m)
        uk = label_uk + (6 if sorot is not None and i in sorot else 0)
        se.teks(d, (x, y - (12 if tanggal else 0)), MANGSA[i][0], uk, PUTIH, nama_font="caption", stroke=4,
                stroke_warna=(30, 20, 10), alpha=alpha)
        if tanggal:
            se.teks(d, (x, y + uk * 0.6), MANGSA[i][1], int(uk * 0.62), (255, 240, 200), nama_font="ui", stroke=3,
                    stroke_warna=(30, 20, 10), alpha=alpha)
    if jarum > 0.01:
        m = math.radians(-90 + 360 * HARI_INI / 365 + putar)
        a = int(255 * alpha * jarum)
        x1, y1 = cx + (r + 40) * math.cos(m), cy + (r + 40) * math.sin(m)
        d.line((cx, cy, x1, y1), fill=(200, 30, 30, a), width=10)
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=(200, 30, 30, a), outline=(255, 255, 255, a), width=4)
        se.teks(d, (x1 + 70 * math.cos(m), y1 + 40 * math.sin(m)), "HARI INI", 34, (200, 30, 30), nama_font="caption",
                stroke=5, stroke_warna=PUTIH, alpha=alpha * jarum)
    se.teks(d, (cx, cy), "12", int(r * 0.24), (110, 70, 30), nama_font="caption", alpha=alpha * (1 - jarum))


# ------------------------------------------------------------------ ikon

def matahari(d, x, y, r, t, alpha=1.0):
    a = int(255 * alpha)
    for i in range(12):
        m = i * math.pi / 6 + t * 0.6
        d.line((x + r * 1.25 * math.cos(m), y + r * 1.25 * math.sin(m), x + r * 1.7 * math.cos(m),
                y + r * 1.7 * math.sin(m)), fill=(240, 170, 30, a), width=8)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 205, 60, a), outline=(200, 120, 20, a), width=5)


def bintang_ikon(d, x, y, r, alpha=1.0, warna=(255, 225, 120)):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        m = -math.pi / 2 + i * math.pi / 5
        pts.append((x + rr * math.cos(m), y + rr * math.sin(m)))
    d.polygon(pts, fill=tuple(warna) + (int(255 * alpha),), outline=(120, 80, 20, int(255 * alpha)))


def burung(d, x, y, s, alpha=1.0, t=0.0):
    a = int(255 * alpha)
    k = math.sin(t * 8) * 14 * s
    d.line((x - 50 * s, y - 10 * s + k, x - 20 * s, y, x, y + 6 * s, x + 20 * s, y, x + 50 * s, y - 10 * s + k),
           fill=(40, 30, 20, a), width=max(3, int(8 * s)), joint="curve")


def pohon_bunga(d, x, y, s, alpha=1.0):
    a = int(255 * alpha)
    d.rectangle((x - 10 * s, y - 20 * s, x + 10 * s, y + 70 * s), fill=(100, 65, 35, a))
    d.ellipse((x - 70 * s, y - 110 * s, x + 70 * s, y + 10 * s), fill=(70, 140, 70, a), outline=(40, 80, 40, a), width=4)
    rng = random.Random(3)
    for _ in range(9):
        bx, by = x + rng.uniform(-50, 50) * s, y + rng.uniform(-90, -10) * s
        d.ellipse((bx - 9 * s, by - 9 * s, bx + 9 * s, by + 9 * s), fill=(240, 110, 140, a))


def luku(d, x, y, s, alpha=1.0, warna=(110, 70, 35)):
    """Bajak sawah (luku) tampak samping, menghadap kiri."""
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    d.line((x - 150 * s, y - 40 * s, x + 60 * s, y - 10 * s), fill=c, width=max(4, int(14 * s)))  # tuas ke kerbau
    d.line((x + 40 * s, y - 120 * s, x + 60 * s, y + 40 * s), fill=c, width=max(4, int(14 * s)))  # gagang
    d.line((x + 40 * s, y - 120 * s, x + 90 * s, y - 130 * s), fill=c, width=max(4, int(12 * s)))
    d.polygon([(x + 60 * s, y + 40 * s), (x - 20 * s, y + 60 * s), (x + 70 * s, y + 70 * s)],
              fill=(80, 80, 90, a))  # mata bajak


# ------------------------------------------------------------------ rasi Orion (posisi kira-kira, ilustratif)

ORION = {"Betelgeuse": (-150, -230), "Bellatrix": (120, -200), "Alnitak": (-50, 0), "Alnilam": (0, -12),
         "Mintaka": (50, -24), "Saiph": (-110, 230), "Rigel": (140, 210), "pedang1": (-10, 70),
         "pedang2": (-5, 115), "kepala": (-20, -300)}
GARIS_ORION = [("Betelgeuse", "Alnitak"), ("Bellatrix", "Mintaka"), ("Alnitak", "Alnilam"), ("Alnilam", "Mintaka"),
               ("Alnitak", "Saiph"), ("Mintaka", "Rigel"), ("Betelgeuse", "kepala"), ("Bellatrix", "kepala")]
GARIS_LUKU = [("Mintaka", "Alnilam"), ("Alnilam", "Alnitak"), ("Alnilam", "pedang1"), ("pedang1", "pedang2")]


def orion(d, cx, cy, s, t, alpha=1.0, garis=1.0, luku_k=0.0, miring=0.0):
    a = int(255 * alpha)
    m = math.radians(miring)

    def pos(n):
        x, y = ORION[n]
        x, y = x * s, y * s
        return cx + x * math.cos(m) - y * math.sin(m), cy + x * math.sin(m) + y * math.cos(m)

    for i, (p, q) in enumerate(GARIS_ORION):
        k = clamp(garis * len(GARIS_ORION) - i)
        if k > 0:
            (x0, y0), (x1, y1) = pos(p), pos(q)
            d.line((x0, y0, lerp(x0, x1, k), lerp(y0, y1, k)), fill=(160, 190, 255, int(a * 0.55)), width=3)
    for i, (p, q) in enumerate(GARIS_LUKU):
        k = clamp(luku_k * len(GARIS_LUKU) - i)
        if k > 0:
            (x0, y0), (x1, y1) = pos(p), pos(q)
            d.line((x0, y0, lerp(x0, x1, k), lerp(y0, y1, k)), fill=(255, 200, 70, a), width=8)
    for n in ORION:
        x, y = pos(n)
        r = (11 if n in ("Betelgeuse", "Rigel") else 8) * s + 2 * math.sin(t * 3 + len(n))
        warna = (255, 170, 120) if n == "Betelgeuse" else (220, 235, 255)
        d.ellipse((x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2), fill=warna + (int(a * 0.18),))
        d.ellipse((x - r, y - r, x + r, y + r), fill=warna + (a,))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img, d = langit(c.t, badai=1.0, bintang=0.25)
    se.hujan(img, c.t, kuat=1.0, seed=3)
    d = ImageDraw.Draw(img, "RGBA")
    if (c.t % 2.6) < 0.18:
        se.tint(img, (255, 255, 255), 0.25)
        d = ImageDraw.Draw(img, "RGBA")
        kilat(d, 860, 330, c.t, 1.0, seed=int(c.t / 2.6))
    sawah(d)
    roda(img, 540, 940, 285 + 10 * math.sin(c.t * 2), c.t, muncul=1.0, putar=-c.t * 6, sorot={KANEM, KAPITU},
         redup=c.p(0.15, 0.3), label_uk=28)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 420), "RAMALAN HUJAN", 110, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 535), "TANPA SATELIT", 116, KUNING, nama_font="caption", stroke=11, stroke_warna=GELAP)
    a2 = c.p(0.3, 0.36)
    if a2 > 0:
        pita(img, 1290, "BMKG: puncak hujan Des – Feb", uk=46, alpha=a2, warna_garis=BIRU_TUA)
    stempel(img, "MELESET?", 820, 1150, 0.8 * pop(c, 0.72) * (1 if c.p(0.72, 0.74) > 0 else 0), uk=64, sudut=-10)
    hdr(img, "Kalender hujan petani Jawa", alpha=c.p(0.88, 0.97))
    return img


def a_nama(c):
    kamera = se.kamera_antara(cam(-7.0, 109.8, 1.5), cam(-7.4, 110.6, 2.2), c.p(0.3, 0.7))
    img, d = peta(kamera)
    for nama, ll in LABEL_PULAU.items():
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 44, alpha=1 - c.p(0.3, 0.5))
    pita(img, 640, "PRANATA = aturan · MANGSA = musim", uk=44, alpha=c.p(0.02, 0.1) * (1 - c.p(0.4, 0.46)),
         warna_garis=(120, 70, 30))
    x, y = layar(kamera, SURAKARTA)
    titik_kota(d, x, y, "Surakarta", c.p(0.4, 0.48), t=c.t, dy=-50)
    se.kartu(img, 540, y + 250, "Sunan Pakubuwana VII", "Raja Surakarta", (150, 100, 30), alpha=c.p(0.5, 0.58),
             tiang=False, skala=pop(c, 0.5))
    stempel(img, "22 JUNI 1855", 540, 600, 0.9 * pop(c, 0.72) * (1 if c.p(0.72, 0.74) > 0 else 0), uk=70, sudut=-6,
            warna=(150, 30, 20))
    hdr(img, "Dibakukan di Surakarta")
    return img


def a_roda(c):
    img = LATAR.copy()
    roda(img, 540, 870, 360, c.t, muncul=c.p(0.02, 0.45), label_uk=30, tanggal=c.p(0.7, 0.75) > 0,
         sorot={0} if c.p(0.7, 0.75) > 0 else None, redup=c.p(0.7, 0.8))
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.4, 0.48) * (1 - c.p(0.68, 0.72))
    se.kartu(img, 540, 1330, "23 sampai 43 hari", "panjang tiap mangsa beda-beda", (120, 70, 30), alpha=a,
             tiang=False, skala=pop(c, 0.4))
    se.kartu(img, 540, 1330, "Mangsa 1: Kasa", "mulai 22 Juni", ORANYE, alpha=c.p(0.74, 0.8), tiang=False,
             skala=pop(c, 0.74))
    hdr(img, "Setahun = 12 mangsa")
    return img


def a_titen(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    pita(img, 450, "ILMU TITEN = rajin ngamatin alam", uk=44, alpha=c.p(0.02, 0.1), warna_garis=HIJAU_T)
    kotak = [(300, 720), (780, 720), (300, 1110), (780, 1110)]
    nama = ["matahari", "bintang", "hewan", "tumbuhan"]
    for i, (x, y) in enumerate(kotak):
        a = c.p(0.3 + i * 0.12, 0.38 + i * 0.12)
        if a <= 0:
            continue
        s = max(0.3, pop(c, 0.3 + i * 0.12))
        se.panel(img, (x - 200 * s, y - 170 * s, x + 200 * s, y + 170 * s), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        if i == 0:
            matahari(d, x, y - 20, 60 * s, c.t, a)
        elif i == 1:
            for j, (dx, dy) in enumerate(((-60, -50), (40, -70), (10, 10), (-40, 60), (70, 40))):
                bintang_ikon(d, x + dx * s, y - 20 + dy * s, (22 if j != 2 else 34) * s, a)
        elif i == 2:
            burung(d, x - 40, y - 40, 1.0 * s, a, c.t)
            burung(d, x + 60, y + 10, 0.7 * s, a, c.t + 1)
        else:
            pohon_bunga(d, x, y + 10, 0.95 * s, a)
        se.teks(d, (x, y + 125 * s), nama[i], 40, TINTA, nama_font="tangan", alpha=a)
    stempel(img, "BUKAN SATELIT", 540, 915, 0.75 * pop(c, 0.12) * (1 - c.p(0.28, 0.3)), uk=60, sudut=-5)
    hdr(img, "Patokannya alam")
    return img


def a_waluku(c):
    img, d = langit(c.t, 0.0, 1.0)
    sawah(d, y0=1300)
    miring = 30 * c.p(0.6, 0.85)
    orion(d, 540, 880, 1.0, c.t, garis=c.p(0.02, 0.25), luku_k=c.p(0.3, 0.5), miring=miring)
    a = c.p(0.35, 0.45)
    luku(d, 330, 1110, 1.1, a * (1 - c.p(0.6, 0.65)), warna=(230, 190, 120))
    se.teks(d, (540, 430), "LINTANG WALUKU", 80, KUNING, nama_font="caption", stroke=8, stroke_warna=GELAP,
            alpha=c.p(0.02, 0.1))
    se.teks(d, (540, 515), "= rasi Orion", 50, PUTIH, nama_font="caption", stroke=6, stroke_warna=GELAP,
            alpha=c.p(0.08, 0.16))
    label(d, (330, 1240), "mirip luku (bajak)", 40, alpha=a * (1 - c.p(0.6, 0.65)))
    b = c.p(0.66, 0.74)
    if b > 0:
        se.teks(d, (230, 1130), "← barat", 44, PUTIH, nama_font="caption", stroke=5, stroke_warna=GELAP, alpha=b)
        se.kartu(img, 540, 1230, "Jam 3 pagi miring ke barat", "= saatnya tanam padi", HIJAU_T, alpha=b, tiang=False,
                 skala=pop(c, 0.66))
    hdr(img, "Jam alam di langit")
    return img


def a_kanem(c):
    img = LATAR.copy()
    se.hujan(img, c.t, kuat=0.35 * c.p(0.3, 0.6), seed=9)
    roda(img, 540, 830, 330, c.t, sorot={KANEM}, redup=c.p(0.2, 0.35), jarum=c.p(0.3, 0.4), label_uk=28)
    d = ImageDraw.Draw(img, "RGBA")
    pita(img, 440, "Bagian paling pas…", uk=52, alpha=c.p(0.0, 0.06) * (1 - c.p(0.25, 0.3)), warna_garis=MERAH)
    se.kartu(img, 540, 1270, "Mangsa Kanem · 9 Nov – 21 Des", "hujan makin deras · buah matang · semai benih",
             BIRU, alpha=c.p(0.42, 0.5), tiang=False, skala=pop(c, 0.42))
    hdr(img, "Sekarang: mangsa Kanem")
    return img


def a_kapitu(c):
    img, d = langit(c.t, badai=1.0, bintang=0.0)
    se.hujan(img, c.t, kuat=1.0, seed=4)
    d = ImageDraw.Draw(img, "RGBA")
    # sungai meluap di bawah
    naik = c.p(0.1, 0.45)
    sawah(d, y0=1300)
    yair = 1330 - 90 * naik
    d.polygon([(0, yair), (W, yair - 20), (W, H), (0, H)], fill=(60, 110, 160, 200))
    for i in range(8):
        xx = (i * 160 + c.t * 120) % (W + 100) - 50
        d.arc((xx, yair - 10, xx + 90, yair + 20), 180, 360, fill=(200, 225, 245, 200), width=4)
    roda(img, 540, 760, 250, c.t, sorot={KAPITU}, redup=1.0, label_uk=24, alpha=1 - c.p(0.45, 0.52))
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 1110, "Mangsa Kapitu · 22 Des – 2 Feb", "hujan lebat · sungai banyak yang banjir", BIRU,
             alpha=c.p(0.08, 0.16) * (1 - c.p(0.45, 0.52)), tiang=False, skala=pop(c, 0.08))
    b = c.p(0.5, 0.58)
    if b > 0:
        se.panel(img, (90, 560, 990, 1180), alpha=b)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 640), "PRANATA MANGSA", 46, (120, 70, 30), nama_font="caption", alpha=b)
        se.teks(d, (540, 720), "Kanem & Kapitu: hujan, banjir", 42, TINTA, nama_font="judul", alpha=b)
        d.line((180, 800, 900, 800), fill=(120, 90, 50, int(180 * b)), width=3)
        se.teks(d, (540, 870), "BMKG 2026", 46, BIRU_TUA, nama_font="caption", alpha=c.p(0.6, 0.66))
        se.teks(d, (540, 950), "Puncak hujan: Des – Feb", 46, TINTA, nama_font="judul", alpha=c.p(0.6, 0.66))
        stempel(img, "MIRIP BANGET!", 540, 1080, 0.8 * pop(c, 0.78) * (1 if c.p(0.78, 0.8) > 0 else 0), uk=60,
                sudut=-5, warna=(30, 110, 60))
    hdr(img, "Puncak musim hujan")
    return img


def a_onnen(c):
    kamera = se.kamera_antara(cam(-6.9, 107.6, 1.0), cam(-6.45, 106.9, 2.6), c.p(0.15, 0.45))
    img, d = peta(kamera)
    xb, yb = layar(kamera, BOGOR)
    xt, yt = layar(kamera, BATAVIA)
    pita(img, 460, "Belanda nyatet cuaca pakai alat", uk=44, alpha=c.p(0.0, 0.08) * (1 - c.p(0.25, 0.3)),
         warna_garis=(120, 70, 30))
    a1 = c.p(0.3, 0.36)
    titik_kota(d, xb, yb, "Bogor", a1, t=c.t, dy=60)
    if a1 > 0:
        se.kartu(img, xb, yb - 30, "Dr. Onnen · 1841", "kepala rumah sakit, catat cuaca di rumah", (150, 100, 30),
                 alpha=a1 * (1 - c.p(0.6, 0.65)), skala=pop(c, 0.3))
    k = c.p(0.6, 0.72)
    d = ImageDraw.Draw(img, "RGBA")
    se.garis_putus(d, [(xb, yb), (xt, yt)], k, (200, 52, 44), tebal=8)
    a2 = c.p(0.7, 0.76)
    titik_kota(d, xt, yt, "Batavia", a2, t=c.t, dy=-50)
    if a2 > 0:
        se.kartu(img, 540, yb + 180, "Observatorium resmi · 1866", "Batavia", BIRU_TUA, alpha=a2, tiang=False,
                 skala=pop(c, 0.7))
    stempel(img, "CIKAL BAKAL BMKG", 540, 1300, 0.75 * pop(c, 0.84) * (1 if c.p(0.84, 0.86) > 0 else 0), uk=60,
            sudut=-5, warna=BIRU_TUA)
    hdr(img, "Sementara itu…")
    return img


def a_stasiun(c):
    kamera = Kamera(*cam(-7.6, 110.0, 1.0))
    img, d = peta(kamera)
    n = int(len(STASIUN) * c.p(0.05, 0.75))
    for i, ll in enumerate(STASIUN[:n]):
        x, y = layar(kamera, ll)
        d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(40, 110, 190, 255), outline=PUTIH + (255,), width=3)
        d.line((x, y - 8, x, y - 22), fill=(40, 110, 190, 255), width=3)
    label(d, layar(kamera, (-6.0, 110.0)), "Laut Jawa", 40, (230, 230, 240), font="tangan_tipis")
    s = back_out((c.t / c.d) / 0.12)
    se.teks(d, (540, 560), f"{n}", int(170 * s) + 1, KUNING, nama_font="caption", stroke=10, stroke_warna=GELAP)
    se.teks(d, (540, 680), "stasiun penakar hujan", 50, PUTIH, nama_font="caption", stroke=6, stroke_warna=GELAP)
    se.kartu(img, 540, 1180, "Tahun 1879", "di seluruh Jawa", BIRU_TUA, alpha=c.p(0.2, 0.3), tiang=False,
             skala=pop(c, 0.2))
    hdr(img, "Data hujan mulai dikumpulkan")
    return img


def a_meleset(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 440), "KENAPA SEKARANG MELESET?", 62, MERAH, nama_font="caption", stroke=6, stroke_warna=PUTIH,
            alpha=c.p(0.0, 0.06))
    # dua garis waktu: kalender tetap vs musim nyata yang bergeser
    x0, x1 = 120, 960
    y1, y2 = 700, 940
    se.teks(d, (x0, y1 - 60), "Kalender: tanggal tetap", 38, TINTA, anchor="lm", alpha=c.p(0.1, 0.18))
    d.rounded_rectangle((x0, y1, x1, y1 + 70), 14, fill=(200, 190, 170, int(255 * c.p(0.1, 0.18))))
    xa = lerp(x0, x1, 0.35)
    d.rounded_rectangle((xa, y1, x1, y1 + 70), 14, fill=BIRU + (int(255 * c.p(0.12, 0.2)),))
    se.teks(d, ((xa + x1) / 2, y1 + 35), "hujan", 36, PUTIH, nama_font="caption", alpha=c.p(0.12, 0.2))
    b = c.p(0.32, 0.4)
    se.teks(d, (x0, y2 - 60), "Musim nyata: bergeser", 38, TINTA, anchor="lm", alpha=b)
    geser = 0.12 * c.p(0.42, 0.62)
    xb = lerp(x0, x1, 0.35 + geser)
    d.rounded_rectangle((x0, y2, x1, y2 + 70), 14, fill=(200, 190, 170, int(255 * b)))
    d.rounded_rectangle((xb, y2, x1, y2 + 70), 14, fill=BIRU + (int(255 * b),))
    se.teks(d, ((xb + x1) / 2, y2 + 35), "hujan", 36, PUTIH, nama_font="caption", alpha=b)
    if geser > 0.01:
        se.garis_putus(d, [(xa, y2 + 110), (xb, y2 + 110)], 1.0, MERAH, tebal=7, putus=14, celah=8)
    stempel(img, "MUNDUR 20–30 HARI", 540, 1170, 0.85 * pop(c, 0.55) * (1 if c.p(0.55, 0.57) > 0 else 0), uk=62,
            sudut=-5)
    se.teks(d, (540, 1290), "kata BMKG, musim hujan 2026/2027", 34, (90, 70, 50), nama_font="tangan_tipis",
            alpha=c.p(0.6, 0.68))
    hdr(img, "Jawaban dari awal video")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    img, d = langit(c.t, 0.0, 1.0)
    sawah(d, y0=1300)
    se.tint(img, (10, 6, 0), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.6, 0.66))
    if a > 0:
        se.panel(img, (90, 470, 990, 1100), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 550), "Nenek moyang kita", 50, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 620), "pengamat alam yang jeli", 50, TINTA, nama_font="judul", alpha=a)
        roda(img, 540, 830, 150, c.t, label_uk=16, alpha=a, putar=c.t * 8)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1035), "Info banjir? Cek BMKG!", 48, BIRU_TUA, nama_font="caption", alpha=a)
    b = c.p(0.66, 0.74)
    if b > 0:
        m = maskot()
        if m is not None:
            loncat = abs(math.sin(c.t * 5)) * 18
            se.tempel(img, m, b, (540 - m.width // 2, int(560 - loncat)))
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        sk = back_out((c.t / c.d - 0.66) / 0.1)
        w2 = 380 * sk
        dl.rounded_rectangle((540 - w2, 960, 540 + w2, 1090), 40, fill=(200, 52, 44, 245))
        dl.text((540, 1025), "NGOMONGIN SEJARAH", font=se.font("caption", int(56 * sk) + 1), fill=PUTIH, anchor="mm")
        dl.text((540, 1160), "Follow buat cerita berikutnya", font=se.font("ui", 42), fill=PUTIH, anchor="mm",
                stroke_width=4, stroke_fill=(0, 0, 0))
        se.tempel(img, lap, b)
    return img


print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 40, warna=(222, 200, 155)).convert("RGBA")

ADEGAN = [
    Adegan("hook", "Petani Jawa dulu bisa nebak musim hujan. Tanpa satelit. BMKG bilang puncak hujan Desember sampai "
                   "Februari? Kalender kuno ini udah tahu duluan. Tapi sekarang sering meleset. Kenapa?",
           a_hook, transisi=False),
    Adegan("nama", "Namanya Pranata Mangsa, aturan musim. Dibakukan Sunan Pakubuwana ketujuh dari Surakarta, "
                   "tahun delapan belas lima puluh lima.", a_nama),
    Adegan("roda", "Setahun dibagi dua belas mangsa. Panjangnya dua puluh tiga sampai empat puluh tiga hari.",
           a_roda),
    Adegan("titen", "Patokannya ilmu titen, rajin ngamatin alam. Matahari, bintang, hewan, sampai pohon berbunga.",
           a_titen),
    Adegan("waluku", "Misalnya Lintang Waluku, rasi Orion yang mirip luku, bajak sawah. Jam tiga pagi udah miring "
                     "ke barat? Waktunya tanam padi.", a_waluku),
    Adegan("kanem", "Nah, bagian paling pas sama berita hari ini. Sekarang kita di mangsa Kanem. Hujan makin deras, "
                    "petani nyemai benih.", a_kanem),
    Adegan("kapitu", "Habis itu Kapitu, sampai awal Februari. Hujan lebat, sungai banjir. Mirip banget sama puncak "
                     "hujan versi BMKG!", a_kapitu),
    Adegan("onnen", "Sementara itu, tahun delapan belas empat puluh satu, Dokter Onnen di Bogor mulai nyatet cuaca "
                    "dari rumahnya. Delapan belas enam puluh enam, jadi observatorium resmi di Batavia. Cikal bakal "
                    "BMKG.", a_onnen),
    Adegan("stasiun", "Delapan belas tujuh puluh sembilan, sudah ada tujuh puluh empat penakar hujan di Jawa.",
           a_stasiun),
    Adegan("meleset", "Terus, kenapa Pranata Mangsa sering meleset? Tanggalnya tetap, musimnya bergeser. Tahun ini "
                      "aja, musim hujan mundur dua puluh sampai tiga puluh hari.", a_meleset),
    Adegan("penutup", "Nenek moyang kita pengamat alam yang jeli. Tapi info banjir, tetap cek BMKG ya. Follow "
                      "Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
