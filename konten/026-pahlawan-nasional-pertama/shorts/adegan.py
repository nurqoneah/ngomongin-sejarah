"""Shorts ±88 detik: Pahlawan Nasional pertama Indonesia — Abdul Muis, wartawan & penulis Salah Asuhan.

Tren: pengumuman gelar Pahlawan Nasional 2026 (Hari Pahlawan, 10 November 2026).
Visual: medali bintang, peta Nusantara (Agam → Batavia → Bandung → Yogyakarta → Garut),
tumpukan koran, meja menulis di pengasingan, sampul novel, kalender 30 Agustus 1959.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "pahlawan-nasional-pertama-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "PAHLAWAN PERTAMA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
EMAS = (240, 190, 60)
EMAS_TUA = (150, 100, 20)
BIRU = (30, 80, 150)
HIJAU_SI = (30, 120, 70)
ABU = (60, 60, 70)
KERTAS = (247, 236, 208)

print("  menyiapkan peta Nusantara...")
PETA = Peta(92, 120, -16, 8, 150, [], [(-0.4, 100.4, 0.5), (-7.2, 107.9, 0.35), (-7.0, 110.4, 0.4),
                                       (-7.5, 112.5, 0.4), (-2.0, 102.0, 0.6)],
            seed=26, darat=pd.SEMUA)

AGAM = (-0.27, 100.42)
BATAVIA = (-6.13, 106.81)
BANDUNG = (-6.91, 107.61)
YOGYA = (-7.80, 110.36)
GARUT = (-7.22, 107.90)

print("  menyiapkan latar kertas...")
LATAR = se.latar_tekstur(W, H, 26, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (30, 18, 8), 0.55)


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


def medali(img, x, y, s=1.0, alpha=1.0, kilau=0.0):
    """Medali bintang emas dengan pita merah-putih."""
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    # pita
    pw = 120 * s
    d.polygon([(x - pw, y - 260 * s), (x - 10 * s, y - 260 * s), (x + 30 * s, y - 60 * s), (x - 50 * s, y - 60 * s)],
              fill=(200, 40, 35, 255), outline=(90, 15, 10, 255))
    d.polygon([(x + 10 * s, y - 260 * s), (x + pw, y - 260 * s), (x + 50 * s, y - 60 * s), (x - 30 * s, y - 60 * s)],
              fill=(245, 245, 240, 255), outline=(120, 110, 100, 255))
    # cakram
    r = 190 * s
    d.ellipse((x - r - 10 * s, y - r - 10 * s, x + r + 10 * s, y + r + 10 * s), fill=EMAS_TUA + (255,))
    d.ellipse((x - r, y - r, x + r, y + r), fill=EMAS + (255,), outline=(255, 230, 140, 255), width=int(6 * s) + 1)
    # bintang
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = (140 if i % 2 == 0 else 58) * s
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    d.polygon(pts, fill=(255, 220, 110, 255), outline=EMAS_TUA + (255,))
    # kilau
    if kilau > 0:
        gx = x - r + 2 * r * (kilau % 1)
        d.line((gx - 40 * s, y - r * 0.7, gx + 40 * s, y + r * 0.7), fill=(255, 255, 255, 120), width=int(26 * s) + 1)
    se.tempel(img, lap, alpha)


def koran(img, cx, cy, nama, judul_berita, sudut=0.0, alpha=1.0, s=1.0):
    """Lembar koran kecil, bisa diputar."""
    if alpha <= 0.01:
        return
    w, h = int(420 * s), int(540 * s)
    lap = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rectangle((14, 16, w + 14, h + 16), fill=(0, 0, 0, 80))
    d.rectangle((6, 6, w + 6, h + 6), fill=(238, 228, 205, 255), outline=(90, 80, 60, 255), width=3)
    d.text((w / 2 + 6, 50 * s), nama, font=se.font("judul", int(46 * s)), fill=(25, 20, 15), anchor="mm")
    d.line((24, 90 * s, w - 12, 90 * s), fill=(40, 30, 20), width=3)
    d.text((w / 2 + 6, 135 * s), judul_berita, font=se.font("caption", int(34 * s)), fill=(150, 30, 25), anchor="mm")
    rng = random.Random(nama)
    for kol in range(3):
        x0 = 26 + kol * (w - 30) / 3
        for i in range(14):
            yy = 185 * s + i * 24 * s
            ll = (w - 60) / 3 * rng.uniform(0.6, 0.95)
            d.line((x0, yy, x0 + ll, yy), fill=(120, 110, 95), width=max(2, int(6 * s)))
    lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def pena(d, x, y, s=1.0, alpha=1.0, miring=-0.7):
    a = int(255 * alpha)
    dx, dy = math.cos(miring), math.sin(miring)
    px, py = -dy, dx
    L, Wd = 260 * s, 18 * s
    ujung = (x, y)
    leher = (x - dx * 50 * s, y - dy * 50 * s)
    ekor = (x - dx * L, y - dy * L)
    d.polygon([ujung, (leher[0] + px * Wd, leher[1] + py * Wd), (leher[0] - px * Wd, leher[1] - py * Wd)],
              fill=(200, 170, 80, a), outline=(60, 40, 10, a))
    d.polygon([(leher[0] + px * Wd, leher[1] + py * Wd), (ekor[0] + px * Wd, ekor[1] + py * Wd),
               (ekor[0] - px * Wd, ekor[1] - py * Wd), (leher[0] - px * Wd, leher[1] - py * Wd)],
              fill=(30, 30, 40, a), outline=(10, 10, 15, a))


def buku(img, cx, cy, s=1.0, alpha=1.0, sudut=0.0):
    """Sampul novel Salah Asuhan (ilustrasi, bukan sampul asli)."""
    if alpha <= 0.01:
        return
    w, h = int(420 * s), int(600 * s)
    lap = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rounded_rectangle((22, 24, w + 22, h + 24), 10, fill=(0, 0, 0, 100))
    d.rounded_rectangle((8, 8, w + 8, h + 8), 10, fill=(120, 35, 30, 255), outline=(60, 15, 10, 255), width=4)
    d.rectangle((8, 8, 8 + 34 * s, h + 8), fill=(90, 25, 20, 255))
    d.rectangle((60 * s, 70 * s, w - 30 * s, h - 70 * s), outline=EMAS + (255,), width=int(5 * s) + 1)
    d.text((w / 2 + 20 * s, 210 * s), "SALAH", font=se.font("judul", int(78 * s)), fill=(255, 225, 140), anchor="mm")
    d.text((w / 2 + 20 * s, 300 * s), "ASUHAN", font=se.font("judul", int(78 * s)), fill=(255, 225, 140), anchor="mm")
    d.line((w / 2 - 80 * s, 360 * s, w / 2 + 120 * s, 360 * s), fill=EMAS + (255,), width=3)
    d.text((w / 2 + 20 * s, 410 * s), "Abdoel Moeis", font=se.font("tangan", int(36 * s)), fill=(250, 235, 200), anchor="mm")
    d.text((w / 2 + 20 * s, h - 110 * s), "Balai Pustaka · 1928", font=se.font("ui", int(26 * s)), fill=(240, 210, 150), anchor="mm")
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 760, 520, (255, 200, 90), 1.4)
    goyang = math.sin(c.t * 2.2) * 6
    medali(img, 540, 860 + goyang, 1.0, 1.0, kilau=c.t * 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    # teks besar sejak frame pertama
    se.teks(d, (540, 420), "PAHLAWAN NASIONAL", 84, (255, 225, 140), nama_font="caption", stroke=9,
            stroke_warna=(30, 15, 5))
    se.teks(d, (540, 530), "PERTAMA?", 120, PUTIH, nama_font="caption", stroke=10, stroke_warna=(30, 15, 5))
    # kartu dicoret
    se.kartu(img, 290, 1150, "Diponegoro", "", ABU, alpha=1.0, tiang=False, coret=c.p(0.05, 0.22))
    se.kartu(img, 790, 1150, "Kartini", "", ABU, alpha=c.p(0.16, 0.24), tiang=False, coret=c.p(0.24, 0.38))
    se.teks(d, (540, 1270), "ternyata… seorang penulis", 54, (255, 210, 130), nama_font="caption", stroke=7,
            stroke_warna=(30, 15, 5), alpha=c.p(0.62, 0.72))
    hdr(img, "Gelar pertama, 1959", alpha=c.p(0.85, 0.97))
    return img


def a_agam(c):
    k = c.p(0.0, 0.35)
    kamera = se.kamera_antara(cam(-2.5, 104.2, 0.56), cam(-2.8, 103.6, 0.64), k)
    img, d = peta(kamera)
    x1, y1 = layar(kamera, AGAM)
    x2, y2 = layar(kamera, BATAVIA)
    label(d, layar(kamera, (-1.6, 102.2)), "SUMATRA", 40, TINTA, 0.8)
    label(d, layar(kamera, (-7.9, 109.6)), "JAWA", 40, TINTA, 0.8)
    titik_kota(d, x1, y1)
    label(d, (x1 + 10, y1 - 50), "Agam, Sumatra Barat", 38)
    se.kartu(img, 540, 560, "Abdul Muis", "lahir di Agam · 1880-an", MERAH, alpha=c.p(0.05, 0.14) * (1 - c.p(0.6, 0.66)),
             tiang=False, skala=skala_muncul(c, 0.05))
    jalur = [(x1, y1), (lerp(x1, x2, 0.5) + 60, lerp(y1, y2, 0.5) - 40), (x2, y2)]
    se.garis_putus(d, se.halus(jalur), c.p(0.4, 0.62), MERAH, tebal=6)
    a = c.p(0.58, 0.66)
    if a > 0:
        titik_kota(d, x2, y2, BIRU, a)
        label(d, (x2 - 20, y2 + 50), "Batavia", 38, TINTA, a)
    se.kartu(img, 560, 600, "STOVIA · sekolah dokter", "nggak lulus, karena sakit", ABU, alpha=c.p(0.66, 0.74),
             tiang=False, skala=skala_muncul(c, 0.66), coret=c.p(0.82, 0.95))
    hdr(img, "Siapa dia?")
    return img


def a_wartawan(c):
    img = LATAR.copy()
    koran(img, 300, 760, "Preanger Bode", "BANDOENG", -9, c.p(0.0, 0.08), 0.95)
    koran(img, 780, 820, "Kaoem Moeda", "SUARA RAKYAT", 8, c.p(0.15, 0.25), 0.95)
    koran(img, 540, 900, "KABAR", "KRITIK KERAS!", -2, c.p(0.42, 0.52), 1.05)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.55, 0.65)
    if a > 0:
        pena(d, 640 + math.sin(c.t * 9) * 10, 1080, 1.4, a)
    se.kartu(img, 540, 470, "Jadi wartawan di Bandung", "", MERAH, alpha=c.p(0.02, 0.1), tiang=False,
             skala=skala_muncul(c, 0.02))
    se.kartu(img, 540, 1260, "Penanya tajam ke Belanda", "", (150, 30, 25), alpha=c.p(0.6, 0.7), tiang=False,
             skala=skala_muncul(c, 0.6))
    hdr(img, "Senjatanya: pena")
    return img


def a_komite(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out((c.t / c.d) / 0.12)
    se.teks(d, (540, 470), "1913", int(130 * s) + 1, (150, 30, 25), nama_font="caption", stroke=7,
            stroke_warna=KERTAS)
    se.kartu(img, 540, 640, "Gabung Sarekat Islam", "", HIJAU_SI, alpha=c.p(0.04, 0.12), tiang=False,
             skala=skala_muncul(c, 0.04))
    se.kartu(img, 540, 790, "Komite Bumiputera", "bareng Ki Hajar Dewantara", MERAH, alpha=c.p(0.22, 0.3),
             tiang=False, skala=skala_muncul(c, 0.22))
    # spanduk pesta Belanda yang dicoret
    a = c.p(0.45, 0.55)
    if a > 0:
        se.panel(img, (150, 930, 930, 1240), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        for i, wr in enumerate([(200, 40, 40), (245, 245, 245), (30, 70, 160)]):
            d.rectangle((260, 975 + i * 32, 420, 1007 + i * 32), fill=wr + (int(255 * a),), outline=(40, 30, 20, int(255 * a)))
        se.teks(d, (650, 1010), "Pesta 100 tahun", 44, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (650, 1065), "Belanda merdeka", 40, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 1170), "…di negeri yang mereka jajah", 38, (150, 30, 25), nama_font="tangan", alpha=a)
        k = c.p(0.72, 0.85)
        if k > 0:
            d.line((190, 960, lerp(190, 890, k), lerp(960, 1210, k)), fill=(190, 20, 20, 230), width=14)
    hdr(img, "Melawan lewat organisasi")
    return img


def a_rehook(c):
    kamera = Kamera(*cam(-7.2, 109.2, 1.05))
    img, d = peta(kamera)
    se.tint(img, (40, 20, 10), 0.25 * c.p(0.0, 0.3))
    d = ImageDraw.Draw(img, "RGBA")
    xb, yb = layar(kamera, BANDUNG)
    xy, yy = layar(kamera, YOGYA)
    titik_kota(d, xb, yb, BIRU)
    label(d, (xb, yb - 46), "Bandung", 36)
    se.teks(d, (540, 520), "TAPI BAGIAN PALING GILA…", 60, PUTIH, nama_font="caption", stroke=8,
            stroke_warna=(30, 15, 5), alpha=c.p(0.0, 0.06) * (1 - c.p(0.25, 0.3)))
    se.kartu(img, 540, 560, "Masuk Volksraad", "dewan rakyat buatan Belanda", BIRU, alpha=c.p(0.28, 0.36),
             tiang=False, skala=skala_muncul(c, 0.28))
    a = c.p(0.55, 0.63)
    if a > 0:
        titik_kota(d, xy, yy, MERAH, a)
        rng = random.Random(4)
        for i in range(70):
            ang = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(30, 120) * a
            se.prajurit(d, xy + math.cos(ang) * rr, yy + math.sin(ang) * rr * 0.6 + math.sin(c.t * 6 + i) * 3,
                        (200, 50, 40), 0.9, a)
        se.kartu(img, xy, yy - 70, "Mogok buruh pegadaian", "Yogyakarta, awal 1920-an", MERAH, alpha=a,
                 skala=skala_muncul(c, 0.55))
    hdr(img, "Bikin Belanda gerah")
    return img


def a_buang(c):
    k = c.p(0.0, 0.4)
    kamera = se.kamera_antara(cam(-5.0, 106.5, 0.56), cam(-7.0, 108.6, 1.05), k)
    img, d = peta(kamera)
    xg, yg = layar(kamera, GARUT)
    # pagar larangan keluar Jawa
    a = c.p(0.2, 0.35)
    if a > 0:
        pts = [layar(kamera, ll) for ll in [(-5.6, 105.4), (-5.7, 108.5), (-6.4, 111.5), (-6.4, 114.8), (-8.9, 114.8),
                                             (-8.6, 108.5), (-7.4, 105.2), (-5.6, 105.4)]]
        se.garis_putus(d, pts, a, (190, 20, 20), tebal=8, putus=20, celah=12, panah=False)
    se.kartu(img, 540, 520, "Dilarang berpolitik", "", (150, 30, 25), alpha=c.p(0.05, 0.13), tiang=False,
             skala=skala_muncul(c, 0.05))
    se.kartu(img, 540, 650, "Dilarang keluar Pulau Jawa", "", (150, 30, 25), alpha=c.p(0.22, 0.3), tiang=False,
             skala=skala_muncul(c, 0.22))
    b = c.p(0.55, 0.65)
    if b > 0:
        r = 30 + 12 * math.sin(c.t * 5)
        d.ellipse((xg - r * 2, yg - r * 2, xg + r * 2, yg + r * 2), outline=(190, 20, 20, int(220 * b)), width=8)
        titik_kota(d, xg, yg, MERAH, b)
        se.kartu(img, xg, yg - 70, "Diasingkan ke Garut", "", MERAH, alpha=b, skala=skala_muncul(c, 0.55))
    hdr(img, "Dibungkam")
    return img


def a_menulis(c):
    img = Image.new("RGBA", (W, H), (25, 18, 12, 255))
    d = ImageDraw.Draw(img, "RGBA")
    # dinding & jendela malam
    d.rectangle((0, 0, W, 900), fill=(55, 40, 30, 255))
    d.rectangle((640, 420, 940, 760), fill=(20, 30, 60, 255), outline=(90, 65, 40, 255), width=14)
    d.line((790, 420, 790, 760), fill=(90, 65, 40, 255), width=10)
    d.line((640, 590, 940, 590), fill=(90, 65, 40, 255), width=10)
    d.ellipse((860, 450, 910, 500), fill=(240, 235, 200, 255))
    # meja
    d.polygon([(0, 900), (W, 900), (W, H), (0, H)], fill=(95, 60, 35, 255))
    d.line((0, 900, W, 900), fill=(60, 35, 20, 255), width=8)
    # lampu minyak
    flick = 1 + 0.08 * math.sin(c.t * 13) + 0.05 * math.sin(c.t * 7.3)
    se.glow(img, 250, 760, 420 * flick, (255, 190, 90), 1.3)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((190, 860, 310, 920), fill=(130, 90, 40, 255), outline=(60, 35, 15, 255), width=4)
    d.polygon([(215, 870), (285, 870), (270, 760), (230, 760)], fill=(230, 220, 190, 120), outline=(120, 100, 70, 200))
    d.ellipse((238, 770 - 30 * flick, 262, 810), fill=(255, 200, 80, 255))
    # kertas & tulisan yang muncul
    d.polygon([(380, 960), (900, 950), (930, 1290), (360, 1300)], fill=(240, 228, 200, 255), outline=(120, 100, 70, 255))
    baris = int(10 * c.p(0.15, 0.95))
    rng = random.Random(9)
    for i in range(baris):
        yb = 1000 + i * 28
        d.line((410, yb, 410 + rng.uniform(300, 470), yb + 2), fill=(50, 40, 30, 255), width=4)
    xp = 410 + (c.t * 300) % 450
    pena(d, xp, 1000 + max(baris - 1, 0) * 28, 1.1, 1.0, miring=-0.9)
    se.kartu(img, 540, 1210 - 820, "Mulutnya dibungkam", "", ABU, alpha=c.p(0.02, 0.1) * (1 - c.p(0.45, 0.5)),
             tiang=False)
    se.kartu(img, 540, 390, "Tangannya nggak.", "", MERAH, alpha=c.p(0.5, 0.58), tiang=False,
             skala=skala_muncul(c, 0.5))
    hdr(img, "Di Garut")
    return img


def a_novel(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 800, 480, (255, 200, 110), 1.2)
    s = 0.6 + 0.4 * back_out((c.t / c.d) / 0.15)
    buku(img, 540, 790, 1.0 * s, 1.0, sudut=math.sin(c.t * 1.5) * 2)
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 1185, "Hanafi, malu sama bangsanya sendiri", "", (120, 35, 30), alpha=c.p(0.32, 0.4),
             tiang=False, skala=skala_muncul(c, 0.32))
    se.kartu(img, 290, 420, "Bacaan sekolah", "", HIJAU_SI, alpha=c.p(0.62, 0.7), tiang=False,
             skala=skala_muncul(c, 0.62))
    se.kartu(img, 790, 420, "Film · 1972", "", BIRU, alpha=c.p(0.75, 0.83), tiang=False, skala=skala_muncul(c, 0.75))
    hdr(img, "Novel dari pengasingan", alpha=1 - c.p(0.6, 0.66))
    return img


def kalender(img, cx, cy, alpha=1.0, s=1.0):
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    w, h = 300 * s, 330 * s
    d.rounded_rectangle((cx - w / 2 + 8, cy - h / 2 + 10, cx + w / 2 + 8, cy + h / 2 + 10), 20, fill=(0, 0, 0, 100))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 20, fill=(250, 245, 235, 255),
                        outline=(80, 60, 40, 255), width=4)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 90 * s), 20, fill=MERAH + (255,))
    d.text((cx, cy - h / 2 + 46 * s), "AGUSTUS 1959", font=se.font("ui", int(34 * s)), fill=PUTIH, anchor="mm")
    d.text((cx, cy + 50 * s), "30", font=se.font("caption", int(150 * s)), fill=TINTA, anchor="mm")
    se.tempel(img, lap, alpha)


def a_gelar(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 450, "Wafat di Bandung", "Juni 1959", ABU, alpha=c.p(0.02, 0.1) * (1 - c.p(0.3, 0.35)),
             tiang=False)
    a = c.p(0.28, 0.36)
    kalender(img, 300, 760, a, skala_muncul(c, 0.28))
    b = c.p(0.36, 0.46)
    if b > 0:
        se.glow(img, 770, 760, 260, (255, 210, 110), 1.2 * b)
        medali(img, 770, 800, 0.55 * skala_muncul(c, 0.36), b, kilau=c.t * 0.7)
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 1050, "Pahlawan Nasional pertama", "ditetapkan Bung Karno", MERAH, alpha=c.p(0.4, 0.48),
             tiang=False, skala=skala_muncul(c, 0.4))
    n = int(200 * c.p(0.68, 0.92))
    se.teks(d, (540, 1225), f"sekarang: lebih dari {n} nama", 52, (255, 225, 140), nama_font="caption", stroke=7,
            stroke_warna=(30, 15, 5), alpha=c.p(0.66, 0.72))
    hdr(img, "Gelar nomor satu")
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
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1060), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 570), "Pahlawan nggak selalu", 50, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 640), "pegang senjata", 50, TINTA, nama_font="judul", alpha=a)
        pena(d, 640, 720, 1.0, a, miring=-0.8)
        se.teks(d, (540, 1000), "Kadang cuma pegang pena.", 46, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Pahlawan nasional pertama kita? Bukan Diponegoro. Bukan Kartini juga. "
                   "Lagi rame gelar pahlawan baru, kan? Ternyata, yang pertama dapat gelar ini, seorang penulis. "
                   "Dan karyanya, mungkin pernah kamu baca.", a_hook, transisi=False),
    Adegan("agam", "Namanya Abdul Muis, dari Agam, Sumatra Barat. Dia sempat sekolah dokter di Batavia, "
                   "tapi nggak lulus, karena sakit.", a_agam),
    Adegan("wartawan", "Dia lalu jadi wartawan di Bandung. Tulisannya tajam, terang-terangan mengkritik Belanda.",
           a_wartawan),
    Adegan("komite", "Tahun sembilan belas tiga belas, dia gabung Sarekat Islam. Bareng Ki Hajar Dewantara, "
                     "dia memprotes Belanda yang mau pesta seratus tahun merdeka, di negeri yang mereka jajah sendiri.",
           a_komite),
    Adegan("rehook", "Tapi bagian paling gila-nya, ini. Dia masuk Volksraad, dewan buatan Belanda, "
                     "dan malah memakainya buat melawan Belanda. Dia juga memimpin mogok buruh di Yogyakarta.",
           a_rehook),
    Adegan("buang", "Belanda kehabisan sabar. Dia dilarang berpolitik, dilarang keluar Pulau Jawa, "
                    "lalu diasingkan ke Garut.", a_buang, transisi=False),
    Adegan("menulis", "Di pengasingan, mulutnya dibungkam. Tapi tangannya nggak. Di Garut, dia menulis sebuah novel.",
           a_menulis),
    Adegan("novel", "Judulnya, Salah Asuhan. Terbit tahun sembilan belas dua puluh delapan. Kisah Hanafi, "
                    "pemuda pribumi yang malu sama bangsanya sendiri. Sampai jadi bacaan sekolah, bahkan difilmkan.",
           a_novel),
    Adegan("gelar", "Abdul Muis wafat Juni sembilan belas lima puluh sembilan. Sekitar dua bulan kemudian, "
                    "Bung Karno menetapkannya sebagai pahlawan nasional pertama. Sekarang, sudah lebih dari dua ratus nama.",
           a_gelar),
    Adegan("penutup", "Jadi, pahlawan itu nggak selalu pegang senjata. Kadang, cuma pegang pena. "
                      "Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
