"""Shorts ±88 detik: Sandi rahasia pertama Indonesia dibikin dokter — cikal bakal BSSN.

Tren: pendaftaran CPNS BSSN dibuka 27 November 2026 (BSSN masuk Google Trends) → asal-usul lembaga sandi negara:
4 April 1946 Menhan Amir Sjarifoeddin menugasi dr. Roebiono Kertopati membentuk Dinas Kode → Buku Kode C
(± 10.000 kata jadi angka, digandakan 6 eksemplar, kode diganti tiap minggu/bulan) → Agresi Militer II 19 Des 1948,
dokumen diselamatkan → Letnan Soedijatmo & Letnan Soemarkidjo mengungsi ke Dusun Dukuh, Samigaluh, Kulon Progo
→ payoff: rumah warga (Merto Setomo) jadi kantor sandi darurat ± 6 bulan, Ponijan jadi kurir
→ Djawatan Sandi 1949 → Lembaga Sandi Negara 1972 → BSSN 2017; motto "Berani Tidak Dikenal".
Visual: peta Jawa/DIY bergaya ilustrasi, buku kode, angka sandi, rumah kayu-bambu di perbukitan Menoreh.
"""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, KUNING, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "sandi-negara-dokter-roebiono-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "SANDI NEGARA 1946"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
KERTAS = (247, 236, 208)
GELAP = (10, 18, 30)
HIJAU_KODE = (120, 230, 150)
BIRU_TUA = (25, 60, 120)
COKLAT = (120, 75, 35)
BELANDA = (230, 110, 30)

print("  menyiapkan peta Jawa...")
PETA = Peta(103.0, 117.0, -13.0, 0.0, 150, [],
            [(-7.54, 110.45, 0.25), (-7.2, 107.7, 0.3), (-7.9, 112.6, 0.35), (-7.65, 110.15, 0.2), (-3.5, 102.5, 0.6),
             (-1.0, 113.5, 0.8)],
            seed=41, darat=[pd.JAWA, pd.SUMATRA, pd.KALIMANTAN, pd.BALI, pd.LOMBOK, pd.SUMBAWA])

print("  menyiapkan peta Yogyakarta...")
PETA_DIY = Peta(109.7, 110.9, -8.6, -7.0, 1300, [],
                [(-7.54, 110.45, 0.07), (-7.45, 110.43, 0.06), (-7.66, 110.15, 0.07), (-7.72, 110.10, 0.06),
                 (-7.62, 110.21, 0.05), (-7.78, 110.13, 0.05), (-7.58, 110.10, 0.05)],
                seed=46, darat=[pd.JAWA])

YOGYA = (-7.80, 110.37)
SAMIGALUH = (-7.68, 110.17)
MERAPI = (-7.54, 110.45)
BATAVIA = (-6.13, 106.82)
LABEL_PULAU = {"JAWA": (-7.35, 109.0), "SUMATRA": (-3.2, 103.8), "KALIMANTAN": (-1.8, 113.5)}
KAPAL_BELANDA = [(-5.6, 106.6), (-6.3, 109.2), (-5.9, 111.8), (-9.0, 109.5), (-8.9, 112.5), (-4.8, 104.8)]


# ------------------------------------------------------------------ helper

def cam(lat, lon, zoom, p=PETA):
    x, y = p.px(lat, lon)
    return (x, y, zoom)


def peta(kamera, p=PETA):
    img = se.render_peta(p, kamera)
    return img, ImageDraw.Draw(img, "RGBA")


def layar(kamera, ll, p=PETA):
    return kamera.layar(*p.px(*ll))


def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


def pop(c, a, lama=0.1):
    return back_out((c.t / c.d - a) / lama)


def muncul(c, a):
    """Skala pop yang 0 sebelum fraksi a (biar stempel nggak nongol kecil duluan)."""
    return pop(c, a) * (1 if c.p(a, a + 0.02) > 0 else 0)


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
    dl.rounded_rectangle((10, 10, lw - 10, uk + 80), 22, fill=KERTAS + (225,), outline=tuple(warna) + (255,),
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
    dl.rounded_rectangle((x0, y - tinggi / 2, x1, y + tinggi / 2), 30, fill=KERTAS + (242,),
                         outline=tuple(warna_garis) + (255,), width=6)
    se.tempel(img, lap, alpha)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, ((x0 + x1) / 2, y), isi, uk, warna_garis, nama_font="caption", alpha=alpha)


def _gradasi(atas, bawah):
    atas = np.array(atas, np.float32)
    bawah = np.array(bawah, np.float32)
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (atas * (1 - g) + bawah * g).repeat(W, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    return img


def hujan_angka(img, t, kuat=1.0, seed=5, warna=HIJAU_KODE, uk=34):
    """Kolom angka sandi yang jatuh pelan (latar gelap)."""
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    f = se.font("ui", uk)
    rng = random.Random(seed)
    for kol in range(16):
        x = 34 + kol * 68
        v = rng.uniform(60, 160)
        off = rng.uniform(0, H)
        for j in range(22):
            y = (off + j * 90 + t * v) % (H + 200) - 100
            angka = str((kol * 7 + j * 3 + int(t * 4 + rng.random() * 9)) % 10)
            a = int(255 * kuat * rng.uniform(0.15, 0.55))
            d.text((x, y), angka, font=f, fill=tuple(warna) + (a,), anchor="mm")
    img.alpha_composite(lap)


def buku(img, cx, cy, s, judul="BUKU KODE C", buka=0.0, alpha=1.0, warna=(110, 30, 25)):
    """Buku sampul kulit. buka: 0 tertutup, 1 terbuka (halaman berisi deretan angka)."""
    if alpha <= 0.01 or s <= 0.01:
        return
    lw, lh = int(520 * s), int(380 * s)
    lap = Image.new("RGBA", (lw * 2 + 40, lh + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    ox, oy = lw + 20, 20
    if buka < 0.5:
        w = int(lw * 0.62)
        d.rounded_rectangle((ox - w // 2 + 10, oy + 12, ox + w // 2 + 10, oy + lh + 12), 14, fill=(0, 0, 0, 110))
        d.rounded_rectangle((ox - w // 2, oy, ox + w // 2, oy + lh), 14, fill=tuple(warna) + (255,),
                            outline=(40, 10, 8, 255), width=6)
        d.rectangle((ox - w // 2 + 4, oy + 4, ox - w // 2 + 26, oy + lh - 4), fill=(70, 18, 14, 255))
        d.rounded_rectangle((ox - w // 2 + 50, oy + 40, ox + w // 2 - 30, oy + lh - 40), 8,
                            outline=(230, 190, 90, 255), width=4)
        fj = se.font("judul", int(44 * s) + 1)
        for i, kata in enumerate(judul.split(" ", 1)):
            d.text((ox + 10, oy + lh * 0.38 + i * 60 * s), kata, font=fj, fill=(240, 205, 110, 255), anchor="mm")
    else:
        d.polygon([(ox, oy + 8), (ox - lw + 20, oy), (ox - lw, oy + lh), (ox, oy + lh + 10)], fill=(0, 0, 0, 0))
        d.rounded_rectangle((ox - lw - 6, oy - 6, ox + lw + 6, oy + lh + 10), 16, fill=tuple(warna) + (255,))
        d.rectangle((ox - lw + 8, oy + 6, ox - 4, oy + lh - 2), fill=KERTAS + (255,))
        d.rectangle((ox + 4, oy + 6, ox + lw - 8, oy + lh - 2), fill=(242, 230, 200, 255))
        d.line((ox, oy + 4, ox, oy + lh), fill=(120, 90, 60, 255), width=4)
        fk = se.font("tangan_tipis", int(26 * s) + 1)
        rng = random.Random(9)
        kata = ["merdeka", "pasukan", "kapal", "serang", "mundur", "kurir", "Jogja", "senjata", "radio", "besok"]
        for i in range(9):
            y = oy + 36 * s + i * 36 * s
            d.text((ox - lw + 40 * s, y), kata[i % len(kata)], font=fk, fill=TINTA + (255,), anchor="lm")
            d.text((ox - 30 * s, y), f"{rng.randint(1000, 9999)}", font=fk, fill=(150, 30, 20, 255), anchor="rm")
            d.text((ox + 40 * s, y), " ".join(f"{rng.randint(10, 99)}" for _ in range(4)), font=fk,
                   fill=TINTA + (255,), anchor="lm")
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def stetoskop(d, x, y, s, alpha=1.0, warna=(60, 60, 70)):
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    w = max(3, int(9 * s))
    d.arc((x - 70 * s, y - 120 * s, x + 70 * s, y + 20 * s), 180, 360, fill=c, width=w)
    d.line((x - 70 * s, y - 50 * s, x - 70 * s, y + 10 * s), fill=c, width=w)
    d.line((x + 70 * s, y - 50 * s, x + 70 * s, y + 10 * s), fill=c, width=w)
    d.arc((x - 70 * s, y - 40 * s, x + 70 * s, y + 100 * s), 0, 180, fill=c, width=w)
    d.line((x, y + 100 * s, x, y + 160 * s), fill=c, width=w)
    d.ellipse((x - 34 * s, y + 150 * s, x + 34 * s, y + 218 * s), fill=(190, 190, 200, a), outline=c, width=w)


def pesawat(d, x, y, s=1.0, a=255, warna=(50, 50, 60)):
    c = tuple(warna) + (a,)
    d.polygon([(x - 60 * s, y), (x + 60 * s, y - 7 * s), (x + 70 * s, y), (x + 60 * s, y + 7 * s)], fill=c)
    d.polygon([(x - 5 * s, y), (x + 18 * s, y - 50 * s), (x + 30 * s, y - 50 * s), (x + 18 * s, y)], fill=c)
    d.polygon([(x - 5 * s, y), (x + 18 * s, y + 50 * s), (x + 30 * s, y + 50 * s), (x + 18 * s, y)], fill=c)
    d.polygon([(x - 60 * s, y), (x - 48 * s, y - 24 * s), (x - 40 * s, y - 24 * s), (x - 44 * s, y)], fill=c)


def ledakan(img, x, y, f, s=1.0):
    """f: 0..1 umur ledakan."""
    if f <= 0 or f >= 1:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    r = (30 + 110 * f) * s
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 140, 40, int(200 * (1 - f))))
    r2 = r * 0.55
    d.ellipse((x - r2, y - r2, x + r2, y + r2), fill=(255, 230, 120, int(230 * (1 - f))))
    for i in range(5):
        ang = i * 1.3 + 0.4
        rr = r * (0.8 + 0.5 * f)
        d.ellipse((x + math.cos(ang) * rr - 26 * s, y - f * 60 * s + math.sin(ang) * rr * 0.6 - 26 * s,
                   x + math.cos(ang) * rr + 26 * s, y - f * 60 * s + math.sin(ang) * rr * 0.6 + 26 * s),
                  fill=(90, 80, 75, int(160 * (1 - f))))
    img.alpha_composite(lap)


def amplop(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.rectangle((x - 36 * s, y - 24 * s, x + 36 * s, y + 24 * s), fill=(245, 235, 210, a), outline=(70, 50, 30, a),
                width=max(2, int(3 * s)))
    d.line((x - 36 * s, y - 24 * s, x, y + 4 * s, x + 36 * s, y - 24 * s), fill=(70, 50, 30, a),
           width=max(2, int(3 * s)))
    d.ellipse((x - 8 * s, y - 4 * s, x + 8 * s, y + 12 * s), fill=(190, 30, 25, a))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = _gradasi((8, 14, 26), (24, 30, 46))
    hujan_angka(img, c.t, 1.0)
    se.glow(img, 540, 900, 420, (255, 200, 120), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    # buku kode + stetoskop di tengah
    goyang = math.sin(c.t * 2) * 6
    buku(img, 540, 930 + goyang, 1.0, alpha=1.0)
    d = ImageDraw.Draw(img, "RGBA")
    stetoskop(d, 780, 960, 0.9, 1.0, (200, 200, 210))
    stempel(img, "RAHASIA", 370, 1110, 0.8 * (1 + 0.05 * math.sin(c.t * 6)), uk=64, sudut=12)
    se.teks(d, (540, 430), "SANDI RAHASIA", 118, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 555), "DIBIKIN DOKTER", 118, KUNING, nama_font="caption", stroke=11, stroke_warna=GELAP)
    a2 = c.p(0.28, 0.34) * (1 - c.p(0.66, 0.7))
    if a2 > 0:
        pita(img, 1290, "Daftar CPNS BSSN dibuka 27 Nov", uk=44, alpha=a2, warna_garis=BIRU_TUA)
    stempel(img, "DIUMPETIN DI MANA?", 540, 1280, 0.8 * muncul(c, 0.72), uk=60, sudut=-4)
    hdr(img, "Asal-usul BSSN", alpha=c.p(0.88, 0.97))
    return img


def a_masalah(c):
    kamera = se.kamera_antara(cam(-7.4, 108.6, 1.0), cam(-7.5, 109.3, 1.12), c.p(0.0, 1.0))
    img, d = peta(kamera)
    for nama, ll in LABEL_PULAU.items():
        x, y = layar(kamera, ll)
        label(d, (x, y), nama, 44, alpha=0.9)
    # kapal Belanda mendekat
    k = c.p(0.0, 0.35)
    for i, ll in enumerate(KAPAL_BELANDA):
        x, y = layar(kamera, ll)
        ox = math.sin(c.t * 1.5 + i) * 10
        d.polygon([(x - 26 + ox, y), (x + 26 + ox, y), (x + 16 + ox, y + 14), (x - 16 + ox, y + 14)],
                  fill=BELANDA + (int(255 * k),), outline=(60, 25, 10, int(255 * k)), width=3)
        d.line((x + ox, y, x + ox, y - 26), fill=(60, 25, 10, int(255 * k)), width=3)
    se.kartu(img, 540, 560, "Belanda pengen balik lagi", "1946", BELANDA, alpha=c.p(0.02, 0.1) * (1 - c.p(0.4, 0.45)),
             tiang=False, skala=pop(c, 0.02))
    # kurir dengan amplop ditangkap
    xj, yj = layar(kamera, YOGYA)
    xb, yb = layar(kamera, BATAVIA)
    k2 = c.p(0.4, 0.7)
    if k2 > 0:
        se.garis_putus(d, [(xj, yj), (lerp(xj, xb, 0.5), yj - 60), (xb, yb)], k2 * 0.6, (60, 40, 25), tebal=5,
                       panah=False)
        px, py = lerp(xj, lerp(xj, xb, 0.5), clamp(k2 * 1.2)), lerp(yj, yj - 60, clamp(k2 * 1.2))
        amplop(d, px, py - 40, 1.0)
        se.prajurit(d, px, py, (200, 50, 40), 1.4)
        if c.p(0.7, 0.72) > 0:
            d.ellipse((px - 60, py - 100, px + 60, py + 20), outline=(200, 30, 30, 255), width=8)
    titik_kota(d, xj, yj, "Yogyakarta", 1.0, t=c.t, dy=50)
    stempel(img, "KEBACA!", 540, 620, 0.85 * muncul(c, 0.74), uk=70, sudut=-7)
    se.kartu(img, 540, 1290, "Tiap kementerian punya sandi sendiri", "sederhana, gampang dipecahin", (90, 70, 50),
             alpha=c.p(0.45, 0.52), tiang=False)
    hdr(img, "Ibu kota pindah ke Jogja")
    return img


def a_perintah(c):
    kamera = se.kamera_antara(cam(-7.4, 109.8, 1.0), cam(-7.75, 110.37, 2.4), c.p(0.0, 0.45))
    img, d = peta(kamera)
    x, y = layar(kamera, YOGYA)
    titik_kota(d, x, y, "Yogyakarta", 1 - c.p(0.4, 0.46), t=c.t, dy=55)
    stempel(img, "4 APRIL 1946", 540, 560, 0.9 * muncul(c, 0.05), uk=72, sudut=-5, warna=(150, 30, 20))
    se.kartu(img, 540, 800, "Amir Sjarifoeddin", "Menteri Pertahanan", (60, 80, 60), alpha=c.p(0.15, 0.22),
             tiang=False, skala=pop(c, 0.15))
    a = c.p(0.45, 0.52)
    if a > 0:
        d.line((540, 870, 540, 1010), fill=(70, 50, 30, int(255 * a)), width=6)
        d.polygon([(525, 990), (555, 990), (540, 1015)], fill=(70, 50, 30, int(255 * a)))
    se.kartu(img, 540, 1080, "dr. Roebiono Kertopati", "seorang dokter", MERAH, alpha=c.p(0.5, 0.57), tiang=False,
             skala=pop(c, 0.5))
    pita(img, 1270, "Tugas: sandi buat semua kementerian", uk=42, alpha=c.p(0.75, 0.82), warna_garis=(120, 60, 20))
    hdr(img, "Lahirnya Dinas Kode")
    return img


def a_dokter(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    stetoskop(d, 300, 560, 1.1, c.p(0.0, 0.08))
    se.kartu(img, 720, 600, "Dokter, bukan ahli sandi", "nggak pernah sekolah sandi", (90, 70, 50),
             alpha=c.p(0.03, 0.1), tiang=False, skala=pop(c, 0.03))
    # empat bahasa
    a = c.p(0.35, 0.42)
    if a > 0:
        for i, b in enumerate(["Inggris", "Jerman", "Belanda", "Prancis"]):
            k = c.p(0.35 + i * 0.05, 0.42 + i * 0.05)
            se.kartu(img, 160 + i * 253, 880, b, "", BIRU_TUA, alpha=k, tiang=False, skala=pop(c, 0.35 + i * 0.05))
        se.teks(d, (540, 790), "4 BAHASA", 70, BIRU_TUA, nama_font="caption", stroke=6, stroke_warna=KERTAS, alpha=a)
    # dua tangan nulis bareng
    b = c.p(0.65, 0.72)
    if b > 0:
        se.panel(img, (110, 1000, 970, 1300), alpha=b)
        d = ImageDraw.Draw(img, "RGBA")
        for j, x0 in enumerate((200, 580)):
            k = clamp((c.t / c.d - 0.68) / 0.3)
            d.line((x0, 1150, x0 + 300 * k, 1150 + 10 * math.sin(c.t * 20 + j)), fill=TINTA + (int(255 * b),),
                   width=6)
            hx = x0 + 300 * k
            d.polygon([(hx, 1150), (hx + 14, 1090), (hx + 30, 1096), (hx + 8, 1154)], fill=(60, 40, 25, int(255 * b)))
        se.teks(d, (540, 1060), "nulis pakai dua tangan sekaligus", 40, TINTA, nama_font="tangan", alpha=b)
        se.teks(d, (540, 1240), "kiri & kanan, barengan", 40, (150, 30, 20), nama_font="tangan", alpha=b)
    hdr(img, "Siapa dr. Roebiono?")
    return img


def a_buku(c):
    img = _gradasi((40, 30, 22), (70, 52, 36))
    d = ImageDraw.Draw(img, "RGBA")
    buka = 0.0 if c.t / c.d < 0.12 else 1.0
    s = 0.95 if buka else 1.0
    buku(img, 540, 760, s, buka=buka, alpha=c.p(0.0, 0.05))
    d = ImageDraw.Draw(img, "RGBA")
    jml = int(10000 * c.p(0.12, 0.35))
    se.teks(d, (540, 470), f"± {jml:,} KATA".replace(",", "."), 84, KUNING, nama_font="caption", stroke=8,
            stroke_warna=(30, 20, 10), alpha=c.p(0.12, 0.18))
    se.teks(d, (540, 555), "diubah jadi angka", 44, PUTIH, nama_font="caption", stroke=5, stroke_warna=(30, 20, 10),
            alpha=c.p(0.2, 0.26))
    # 6 eksemplar
    a = c.p(0.38, 0.44)
    if a > 0:
        for i in range(6):
            k = c.p(0.38 + i * 0.025, 0.42 + i * 0.025)
            x = 160 + i * 152
            d.rounded_rectangle((x - 50, 1010, x + 50, 1140), 8, fill=(110, 30, 25, int(255 * k)),
                                outline=(240, 205, 110, int(255 * k)), width=4)
            se.teks(d, (x, 1075), "C", 54, (240, 205, 110), nama_font="judul", alpha=k)
        se.teks(d, (540, 1185), "cuma 6 eksemplar", 46, PUTIH, nama_font="caption", stroke=5, stroke_warna=(30, 20, 10),
                alpha=a)
    stempel(img, "GANTI TIAP MINGGU / BULAN", 540, 1290, 0.7 * muncul(c, 0.55) * (1 - c.p(0.76, 0.78)), uk=50,
            sudut=-3, warna=(150, 30, 20))
    pita(img, 1290, "Tapi bagian paling tegangnya…", uk=46, alpha=c.p(0.8, 0.86), warna_garis=(170, 30, 20))
    hdr(img, "Buku Kode C")
    return img


def a_agresi(c):
    kamera = Kamera(*cam(-7.78, 110.37, 1.6, PETA_DIY))
    img, d = peta(kamera, PETA_DIY)
    se.tint(img, (120, 20, 10), 0.2 * c.p(0.1, 0.3))
    d = ImageDraw.Draw(img, "RGBA")
    x, y = layar(kamera, YOGYA, PETA_DIY)
    xm, ym = layar(kamera, MERAPI, PETA_DIY)
    titik_kota(d, x, y, "Yogyakarta", 1.0, t=c.t, dy=60, warna=(230, 60, 40))
    # pesawat lewat + ledakan
    for i in range(3):
        f = (c.t * 0.45 + i * 0.33) % 1
        px = lerp(-150, W + 150, f)
        py = 560 + i * 120 + math.sin(f * 6) * 10
        pesawat(d, px, py, 0.9, 230)
    rng = random.Random(4)
    for i in range(7):
        t0 = rng.uniform(0.05, 0.6) * c.d
        ex, ey = x + rng.uniform(-160, 160), y + rng.uniform(-120, 120)
        ledakan(img, ex, ey, (c.t - t0) / 1.2, 0.9)
    d = ImageDraw.Draw(img, "RGBA")
    stempel(img, "19 DES 1948", 540, 480, 0.9 * muncul(c, 0.02), uk=74, sudut=-5)
    se.kartu(img, 540, 1130, "Agresi Militer Belanda II", "Jogja dibom pagi-pagi", BELANDA, alpha=c.p(0.15, 0.22),
             tiang=False, skala=pop(c, 0.15))
    pita(img, 1290, "Perintah: selamatkan dokumen!", uk=46, alpha=c.p(0.62, 0.7), warna_garis=(170, 30, 20))
    hdr(img, "Ujian terberat")
    return img


def a_evakuasi(c):
    kamera = se.kamera_antara(cam(-7.76, 110.30, 1.7, PETA_DIY), cam(-7.74, 110.27, 2.0, PETA_DIY), c.p(0.0, 0.6))
    img, d = peta(kamera, PETA_DIY)
    xj, yj = layar(kamera, YOGYA, PETA_DIY)
    xs, ys = layar(kamera, SAMIGALUH, PETA_DIY)
    label(d, (xs - 40, ys - 170), "Perbukitan Menoreh", 40, (60, 50, 30), alpha=c.p(0.35, 0.45))
    titik_kota(d, xj, yj, "Yogyakarta", 1.0, t=c.t, dy=60, warna=(230, 60, 40))
    k = c.p(0.1, 0.7)
    jalur = [(xj, yj), (lerp(xj, xs, 0.35), yj + 40), (lerp(xj, xs, 0.7), lerp(yj, ys, 0.6) + 20), (xs, ys)]
    ujung = se.garis_putus(d, jalur, k, (150, 30, 20), tebal=8)
    if ujung and k < 1:
        se.prajurit(d, ujung[0] + 20, ujung[1] - 20, (40, 120, 70), 1.6)
        se.prajurit(d, ujung[0] + 44, ujung[1] - 6, (40, 120, 70), 1.6)
        amplop(d, ujung[0] + 30, ujung[1] - 60, 0.9)
    titik_kota(d, xs, ys, "Samigaluh, Kulon Progo", c.p(0.65, 0.72), t=c.t, dy=-55, dx=40)
    se.kartu(img, 300, 560, "Letnan Soedijatmo", "perwira sandi", (40, 120, 70), alpha=c.p(0.05, 0.12),
             tiang=False, skala=pop(c, 0.05))
    se.kartu(img, 780, 560, "Letnan Soemarkidjo", "perwira sandi", (40, 120, 70), alpha=c.p(0.12, 0.19),
             tiang=False, skala=pop(c, 0.12))
    se.kartu(img, 540, 1250, "Kabur ke barat, naik ke bukit", "", (90, 70, 50), alpha=c.p(0.4, 0.47), tiang=False)
    hdr(img, "Kode harus selamat")
    return img


def _bukit(d, t):
    rng = random.Random(3)
    # bukit belakang & depan
    for lapis, (warna, y0, amp) in enumerate([((70, 95, 70), 760, 120), ((50, 80, 50), 900, 90),
                                               ((38, 62, 40), 1180, 60)]):
        titik = [(0, H)]
        for x in range(0, W + 41, 40):
            y = y0 - amp * math.sin(x / 260 + lapis * 1.7) - 30 * math.sin(x / 90 + lapis)
            titik.append((x, y))
        titik.append((W, H))
        d.polygon(titik, fill=warna + (255,))
    # pohon kelapa/siluet kecil
    for i in range(7):
        x = 60 + i * 160 + rng.uniform(-30, 30)
        y = 900 - 90 * math.sin(x / 260 + 1.7) - 30 * math.sin(x / 90 + 1) + 10
        d.line((x, y, x + 6, y - 90), fill=(30, 45, 30, 255), width=6)
        for j in range(5):
            ang = -math.pi / 2 + (j - 2) * 0.55 + 0.05 * math.sin(t * 2 + i)
            d.line((x + 6, y - 90, x + 6 + math.cos(ang) * 55, y - 90 + math.sin(ang) * 55 + 18), fill=(30, 45, 30, 255),
                   width=5)


def rumah(img, cx, cy, s, t, alpha=1.0, lampu=1.0):
    """Rumah kayu, dinding anyaman bambu, atap limasan."""
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    w, h = 300 * s, 190 * s
    x0, y0, x1, y1 = cx - w, cy - h, cx + w, cy + h * 0.6
    d.rectangle((x0, y0, x1, y1), fill=(170, 130, 80, 255), outline=(70, 45, 25, 255), width=6)
    # anyaman bambu
    step = int(26 * s)
    for i in range(int(x0), int(x1), step):
        d.line((i, y0, i + step, y1), fill=(140, 100, 60, 255), width=2)
        d.line((i + step, y0, i, y1), fill=(140, 100, 60, 255), width=2)
    for x in (x0, cx - w * 0.5, cx + w * 0.5, x1):
        d.rectangle((x - 9 * s, y0, x + 9 * s, y1), fill=(100, 65, 35, 255))
    # atap limasan
    d.polygon([(x0 - 70 * s, y0 + 10 * s), (cx - w * 0.45, y0 - 170 * s), (cx + w * 0.45, y0 - 170 * s),
               (x1 + 70 * s, y0 + 10 * s)], fill=(120, 55, 35, 255), outline=(60, 25, 15, 255))
    for k in range(1, 6):
        yy = y0 + 10 * s - k * 30 * s
        d.line((x0 - 70 * s + k * 26 * s, yy, x1 + 70 * s - k * 26 * s, yy), fill=(90, 40, 25, 255), width=3)
    # pintu
    d.rectangle((cx - 55 * s, cy - 40 * s, cx + 55 * s, y1), fill=(80, 50, 28, 255))
    # jendela dengan cahaya lampu
    jx0, jy0, jx1, jy1 = cx + 120 * s, cy - 110 * s, cx + 250 * s, cy - 10 * s
    kedip = 0.85 + 0.15 * math.sin(t * 9)
    d.rectangle((jx0, jy0, jx1, jy1), fill=(255, 200, 90, int(255 * lampu * kedip)), outline=(70, 45, 25, 255),
                width=5)
    # siluet petugas sandi sedang menulis (tanpa wajah)
    sx, sy = jx0 + 50 * s, jy1
    d.ellipse((sx - 16 * s, sy - 78 * s, sx + 16 * s, sy - 46 * s), fill=(40, 25, 15, 255))
    d.polygon([(sx - 30 * s, sy), (sx - 22 * s, sy - 48 * s), (sx + 22 * s, sy - 48 * s), (sx + 36 * s, sy)],
              fill=(40, 25, 15, 255))
    d.line((sx + 20 * s, sy - 30 * s, sx + 60 * s, sy - 18 * s + 4 * math.sin(t * 14)), fill=(40, 25, 15, 255),
           width=int(8 * s))
    d.rectangle((jx0, jy1 - 14 * s, jx1, jy1), fill=(90, 60, 30, 255))
    se.tempel(img, lap, alpha)
    se.glow(img, (jx0 + jx1) / 2, (jy0 + jy1) / 2, 160 * s, (255, 200, 100), 0.45 * lampu * alpha)


def a_rumah(c):
    img = _gradasi((20, 24, 50), (120, 80, 70))
    d = ImageDraw.Draw(img, "RGBA")
    # bintang
    rng = random.Random(2)
    for _ in range(70):
        x, y = rng.uniform(0, W), rng.uniform(0, 700)
        r = rng.uniform(1, 3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 245, 220, int(rng.uniform(80, 220))))
    _bukit(d, c.t)
    zoom = 1.0 + 0.06 * c.p(0.0, 1.0)
    rumah(img, 540, 1000, 0.95 * zoom, c.t, alpha=1.0)
    d = ImageDraw.Draw(img, "RGBA")
    # kurir berjalan di jalan setapak
    k = c.p(0.62, 0.95)
    if k > 0:
        px, py = lerp(700, 1040, k), lerp(1210, 1300, k)
        se.prajurit(d, px, py, (40, 120, 70), 1.6)
        amplop(d, px, py - 45, 0.8)
        se.kartu(img, 330, 1270, "Ponijan, anak pemilik rumah", "jadi kurir pesan rahasia", (40, 120, 70),
                 alpha=c.p(0.62, 0.69), tiang=False)
    stempel(img, "MARKAS SANDI REPUBLIK", 540, 470, 0.75 * muncul(c, 0.03), uk=58, sudut=-4)
    se.kartu(img, 540, 610, "Rumah Pak Merto Setomo", "Dusun Dukuh, Samigaluh", COKLAT, alpha=c.p(0.15, 0.22),
             tiang=False, skala=pop(c, 0.15))
    stempel(img, "± 6 BULAN", 860, 760, 0.8 * muncul(c, 0.42), uk=60, sudut=8, warna=(150, 30, 20))
    hdr(img, "Kantor sandi darurat")
    return img


TAHAPAN = [("1946", "Dinas Kode"), ("1949", "Djawatan Sandi"), ("1972", "Lembaga Sandi Negara"), ("2017", "BSSN")]


def a_warisan(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    x = 250
    y0, y1 = 470, 1150
    k = c.p(0.0, 0.7)
    d.line((x, y0, x, lerp(y0, y1, k)), fill=(120, 90, 50, 255), width=10)
    for i, (th, nama) in enumerate(TAHAPAN):
        y = lerp(y0, y1, i / 3)
        a = c.p(i * 0.2, i * 0.2 + 0.07)
        if a <= 0:
            continue
        warna = MERAH if i == 3 else COKLAT
        d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=warna + (int(255 * a),), outline=PUTIH + (int(255 * a),),
                  width=5)
        se.teks(d, (x - 50, y), th, 50, warna, nama_font="caption", anchor="rm", alpha=a)
        se.kartu(img, 620, y, nama, "", warna, alpha=a, tiang=False, skala=pop(c, i * 0.2) * (1.15 if i == 3 else 1))
    rumah_a = c.p(0.82, 0.9)
    if rumah_a > 0:
        pita(img, 1290, "Rumah di Dukuh → sekarang museum", uk=44, alpha=rumah_a, warna_garis=(120, 60, 20))
    hdr(img, "Dari kamar sandi ke BSSN")
    return img


def a_motto(c):
    img = _gradasi((8, 14, 26), (24, 30, 46))
    hujan_angka(img, c.t, 0.6, seed=8)
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 560, "dr. Roebiono Kertopati", "memimpin persandian 1946–1984", MERAH, alpha=c.p(0.02, 0.1),
             tiang=False, skala=pop(c, 0.02) * 1.2)
    se.teks(d, (540, 760), "Bapak Persandian Negara", 48, (255, 225, 160), nama_font="caption", stroke=5,
            stroke_warna=GELAP, alpha=c.p(0.2, 0.28))
    a = c.p(0.45, 0.55)
    if a > 0:
        se.panel(img, (110, 880, 970, 1180), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 950), "Mottonya:", 40, (90, 70, 50), nama_font="tangan", alpha=a)
        se.teks(d, (540, 1060), "“BERANI TIDAK DIKENAL”", 64, (150, 30, 20), nama_font="caption", alpha=a)
    hdr(img, "Pahlawan di balik layar")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    img = _gradasi((8, 14, 26), (24, 30, 46))
    hujan_angka(img, c.t, 0.4, seed=11)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.58, 0.64))
    if a > 0:
        se.panel(img, (90, 470, 990, 1100), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 550), "Kemerdekaan kita", 52, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 620), "juga dijaga pakai angka", 52, TINTA, nama_font="judul", alpha=a)
        buku(img, 540, 830, 0.55, alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1035), "Daftar BSSN? Lewat SSCASN resmi!", 42, BIRU_TUA, nama_font="caption", alpha=a)
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


print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 41, warna=(222, 200, 155)).convert("RGBA")

ADEGAN = [
    Adegan("hook", "Sandi rahasia pertama Indonesia dibikin dokter. Lagi rame daftar CPNS BSSN? Lembaga itu lahir "
                   "dari kode ini. Pas Belanda nyerbu, kodenya diumpetin di tempat tak terduga.",
           a_hook, transisi=False),
    Adegan("masalah", "Sembilan belas empat puluh enam, Belanda mau balik lagi. Sandi tiap kementerian masih "
                      "sederhana. Kurir ketangkep, isinya langsung kebaca.", a_masalah),
    Adegan("perintah", "Empat April empat puluh enam, Menteri Pertahanan Amir Sjarifoeddin nugasin seorang dokter, "
                       "Roebiono Kertopati. Bikin sandi buat semua kementerian.", a_perintah),
    Adegan("dokter", "Dia bukan ahli sandi. Tapi nguasain empat bahasa, dan bisa nulis pakai dua tangan sekaligus.",
           a_dokter),
    Adegan("buku", "Hasilnya, Buku Kode C. Sekitar sepuluh ribu kata jadi angka, dan cuma digandakan enam. "
                   "Kodenya diganti tiap minggu atau bulan. Tapi bagian paling tegangnya baru mulai.", a_buku),
    Adegan("agresi", "Sembilan belas Desember empat puluh delapan, Belanda ngebom Jogja. Roebiono perintahkan, "
                     "selamatkan dokumen penting!", a_agresi),
    Adegan("evakuasi", "Letnan Soedijatmo dan Letnan Soemarkidjo kabur ke barat, naik ke perbukitan Menoreh, "
                       "Kulon Progo.", a_evakuasi),
    Adegan("rumah", "Markas sandi Republik ternyata cuma rumah kayu berdinding bambu, punya warga desa, Pak Merto "
                    "Setomo, di Samigaluh. Sekitar enam bulan jadi kantor sandi darurat. Anaknya, Ponijan, jadi "
                    "kurir rahasia.", a_rumah),
    Adegan("warisan", "Dinas Kode terus ganti nama, sampai tahun dua ribu tujuh belas jadi BSSN. Rumah itu sekarang "
                      "jadi museum.", a_warisan),
    Adegan("motto", "Roebiono memimpin hampir empat puluh tahun. Mottonya, berani tidak dikenal.", a_motto),
    Adegan("penutup", "Jadi, kemerdekaan kita juga dijaga pakai angka. Follow Ngomongin Sejarah buat cerita "
                      "berikutnya!", a_penutup),
]
