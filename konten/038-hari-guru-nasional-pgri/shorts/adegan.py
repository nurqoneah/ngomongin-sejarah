"""Shorts ±88 detik: Kenapa Hari Guru Tanggal 25 November?

PGHB 1912 (guru bantu, guru desa, kepala sekolah, penilik) → organisasi guru terpecah-pecah →
1932 ganti nama jadi PGI (kata "Indonesia" bikin Belanda kaget) → Jepang 1942 (organisasi dilarang) →
merdeka 1945 → Kongres Guru Indonesia di Surakarta 24–25 Nov 1945 → PGRI lahir, tepat 100 hari setelah
proklamasi → Hari Guru Nasional (Keppres 78/1994).
Peta Jawa ilustratif + adegan ilustrasi (kalender, label nama, sekolah, timbangan).
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, KUNING, W, H, Adegan, Kamera, Peta, back_out, clamp, lerp

NAMA_FILE = "hari-guru-nasional-pgri-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "HARI GURU"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KREM_LABEL = (240, 225, 190)
COKLAT = (120, 70, 35)
BIRU = (30, 80, 150)
HIJAU_KAPUR = (40, 80, 55)
GELAP = (25, 12, 8)
ABU = (90, 90, 100)

print("  menyiapkan peta Nusantara...")
NUSA = Peta(90, 142, -16, 24, 60, [], [(-7.3, 110.4, 0.5), (-7.6, 111.5, 0.4), (-7.9, 112.9, 0.5),
                                       (-6.9, 107.7, 0.5), (0, 101, 1.2), (-2, 121, 1.2)],
            seed=38, darat=pd.SEMUA)
print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 38, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (6, 14, 30), 0.74)

JAKARTA = (-6.2, 106.85)
BANDUNG = (-6.9, 107.6)
SEMARANG = (-6.97, 110.42)
MAGELANG = (-7.47, 110.22)
SURAKARTA = (-7.57, 110.82)
SURABAYA = (-7.25, 112.75)
YOGYA = (-7.8, 110.37)
SEKOLAH_JAWA = [(-6.6, 106.8), (-6.9, 108.5), (-7.3, 109.2), (-7.0, 110.0), (-7.7, 111.6), (-7.5, 112.3),
                (-8.0, 113.6), (-6.4, 108.2), (-7.2, 107.8), (-6.9, 111.2), (-8.1, 112.6), (-7.8, 109.6)]
ORGANISASI = [("PGB", 240, 560, -8), ("PGD", 790, 540, 7), ("PGAS", 520, 690, -3), ("PNS", 250, 820, 6),
              ("HKSB", 820, 800, -7), ("COV", 520, 930, 5), ("KOB", 230, 1060, -5), ("VVM", 820, 1060, 8),
              ("NIOG", 530, 1170, -4)]
WARNA_ORG = [(200, 52, 44), (46, 120, 80), (30, 80, 150), (150, 90, 30), (120, 50, 130), (40, 110, 130),
             (170, 60, 90), (90, 100, 40), (60, 60, 70)]


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


def tag_nama(img, cx, cy, isi, s=1.0, alpha=1.0, warna=(200, 52, 44), uk=64, sudut=0, coret=0.0):
    """Label nama (tag kertas dengan lubang tali). coret: 0..1 garis coret merah."""
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
    if coret > 0:
        dl.line((30, lh / 2 + 10, 30 + (lw - 20) * coret, lh / 2 + 10), fill=(255, 220, 40, 255),
                width=max(6, uk // 7))
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, alpha, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


def kalender(img, cx, cy, s, angka, bulan, tahun="", alpha=1.0, sudut=0, lingkar=0.0):
    """Lembar kalender sobek: pita merah bulan + angka besar. lingkar: 0..1 coretan lingkaran merah."""
    if alpha <= 0.01 or s <= 0.01:
        return
    lw, lh = 420, 470
    lap = Image.new("RGBA", (lw + 80, lh + 80), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    ox, oy = 40, 40
    dl.rounded_rectangle((ox + 10, oy + 14, ox + lw + 10, oy + lh + 14), 26, fill=(0, 0, 0, 90))
    dl.rounded_rectangle((ox, oy, ox + lw, oy + lh), 26, fill=(252, 248, 238, 255), outline=(60, 40, 20, 255), width=6)
    dl.rounded_rectangle((ox, oy, ox + lw, oy + 120), 26, fill=(200, 40, 35, 255))
    dl.rectangle((ox, oy + 80, ox + lw, oy + 120), fill=(200, 40, 35, 255))
    for rx in (ox + 110, ox + lw - 110):
        dl.ellipse((rx - 14, oy - 14, rx + 14, oy + 14), fill=(70, 70, 80, 255))
    dl.text((ox + lw / 2, oy + 62), bulan, font=se.font("caption", 66), fill=PUTIH, anchor="mm")
    dl.text((ox + lw / 2, oy + 285), angka, font=se.font("caption", 230), fill=(40, 30, 25, 255), anchor="mm")
    if tahun:
        dl.text((ox + lw / 2, oy + lh - 45), tahun, font=se.font("ui", 46), fill=(120, 90, 60, 255), anchor="mm")
    if lingkar > 0:
        bbox = (ox + 30, oy + 150, ox + lw - 30, oy + lh - 40)
        dl.arc(bbox, -100, -100 + 380 * lingkar, fill=(225, 30, 25, 255), width=16)
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    lap = lap.resize((max(1, int(lap.width * s)), max(1, int(lap.height * s))))
    se.tempel(img, lap, alpha, (int(cx - lap.width // 2), int(cy - lap.height // 2)))


def guru(d, x, y, s=1.0, alpha=1.0, warna=(40, 70, 120), peci=True):
    """Ikon guru sederhana (siluet: kepala, badan, peci). Bukan tokoh tertentu."""
    if alpha <= 0.01 or s <= 0.01:
        return
    a = int(255 * alpha)
    d.polygon([(x - 48 * s, y + 120 * s), (x + 48 * s, y + 120 * s), (x + 34 * s, y + 10 * s),
               (x - 34 * s, y + 10 * s)], fill=tuple(warna) + (a,), outline=(20, 15, 10, a))
    d.line((x, y + 12 * s, x, y + 60 * s), fill=(240, 235, 220, a), width=max(2, int(5 * s)))
    d.ellipse((x - 30 * s, y - 52 * s, x + 30 * s, y + 8 * s), fill=(170, 120, 80, a), outline=(60, 35, 20, a),
              width=max(1, int(3 * s)))
    if peci:
        d.rounded_rectangle((x - 30 * s, y - 70 * s, x + 30 * s, y - 38 * s), int(6 * s), fill=(25, 25, 30, a))


def papan_tulis(d, x0, y0, x1, y1, alpha=1.0):
    a = int(255 * alpha)
    d.rectangle((x0 - 14, y0 - 14, x1 + 14, y1 + 14), fill=(120, 80, 40, a))
    d.rectangle((x0, y0, x1, y1), fill=HIJAU_KAPUR + (a,))


def sekolah(d, x, y, s=1.0, alpha=1.0, gembok=0.0):
    """Gedung sekolah kecil + bendera. gembok: 0..1 rantai silang & gembok."""
    if alpha <= 0.01 or s <= 0.01:
        return
    a = int(255 * alpha)
    d.rectangle((x - 70 * s, y - 50 * s, x + 70 * s, y + 40 * s), fill=(245, 235, 210, a), outline=(80, 50, 30, a),
                width=max(1, int(4 * s)))
    d.polygon([(x - 90 * s, y - 48 * s), (x, y - 100 * s), (x + 90 * s, y - 48 * s)], fill=(170, 60, 40, a),
              outline=(80, 30, 20, a))
    d.rectangle((x - 16 * s, y - 5 * s, x + 16 * s, y + 40 * s), fill=(110, 70, 40, a))
    for dx in (-48, 48):
        d.rectangle((x + (dx - 14) * s, y - 30 * s, x + (dx + 14) * s, y - 4 * s), fill=(120, 170, 200, a))
    if gembok > 0:
        g = int(255 * alpha * gembok)
        d.line((x - 80 * s, y - 60 * s, x + 80 * s, y + 45 * s), fill=(90, 90, 100, g), width=max(2, int(10 * s)))
        d.line((x + 80 * s, y - 60 * s, x - 80 * s, y + 45 * s), fill=(90, 90, 100, g), width=max(2, int(10 * s)))
        d.arc((x - 22 * s, y - 30 * s, x + 22 * s, y + 10 * s), 180, 360, fill=(60, 60, 70, g), width=max(2, int(8 * s)))
        d.rounded_rectangle((x - 30 * s, y - 10 * s, x + 30 * s, y + 34 * s), int(6 * s), fill=(200, 160, 40, g),
                            outline=(80, 60, 10, g))


def ikon_sekolah_peta(d, x, y, s=1.0, alpha=1.0):
    if alpha <= 0.01 or s <= 0.01:
        return
    a = int(255 * alpha)
    d.rectangle((x - 16 * s, y - 12 * s, x + 16 * s, y + 10 * s), fill=(250, 240, 215, a), outline=(80, 50, 30, a),
                width=2)
    d.polygon([(x - 22 * s, y - 11 * s), (x, y - 26 * s), (x + 22 * s, y - 11 * s)], fill=(180, 60, 40, a))
    d.line((x, y - 26 * s, x, y - 44 * s), fill=(60, 40, 20, a), width=2)
    d.polygon([(x, y - 44 * s), (x + 14 * s, y - 40 * s), (x, y - 36 * s)], fill=(220, 40, 40, a))


def timbangan(d, x, y, sudut, alpha=1.0, kiri="", kanan=""):
    """Timbangan: tiang di (x, y) atas, lengan miring `sudut` (radian)."""
    if alpha <= 0.01:
        return
    a = int(255 * alpha)
    d.polygon([(x - 90, y + 330), (x + 90, y + 330), (x + 20, y + 290), (x - 20, y + 290)], fill=(110, 70, 35, a))
    d.line((x, y, x, y + 300), fill=(110, 70, 35, a), width=16)
    d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=(200, 160, 40, a))
    L = 300
    dx, dy = L * math.cos(sudut), L * math.sin(sudut)
    pts = [(x - dx, y - dy), (x + dx, y + dy)]
    d.line((pts[0], pts[1]), fill=(80, 50, 25, a), width=14)
    for (px, py), isi in zip(pts, (kiri, kanan)):
        d.line((px, py, px - 80, py + 140), fill=(80, 50, 25, a), width=4)
        d.line((px, py, px + 80, py + 140), fill=(80, 50, 25, a), width=4)
        d.chord((px - 110, py + 90, px + 110, py + 200), 0, 180, fill=(200, 160, 40, a), outline=(110, 80, 10, a),
                width=4)
        se.teks(d, (px, py + 110), isi, 36, TINTA, nama_font="caption", stroke=4, stroke_warna=KREM_LABEL, alpha=alpha)


def ledakan(d, x, y, r, alpha=1.0, seed=0):
    if alpha <= 0.01 or r <= 1:
        return
    rng = random.Random(seed)
    n = 14
    pts = []
    for i in range(n * 2):
        ang = i * math.pi / n
        rr = r * (1.0 if i % 2 == 0 else 0.5) * rng.uniform(0.85, 1.1)
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    d.polygon(pts, fill=(255, 120, 30, int(220 * alpha)))
    d.ellipse((x - r * 0.35, y - r * 0.35, x + r * 0.35, y + r * 0.35), fill=(255, 230, 120, int(240 * alpha)))


def bendera_rp(d, x, y, s=1.0, alpha=1.0, t=0.0):
    if alpha <= 0.01 or s <= 0.01:
        return
    a = int(255 * alpha)
    d.line((x, y, x, y - 110 * s), fill=(60, 40, 20, a), width=max(2, int(5 * s)))
    k = math.sin(t * 6) * 6 * s
    d.polygon([(x, y - 110 * s), (x + 80 * s, y - 106 * s + k), (x + 80 * s, y - 86 * s + k), (x, y - 88 * s)],
              fill=(220, 30, 30, a))
    d.polygon([(x, y - 88 * s), (x + 80 * s, y - 86 * s + k), (x + 80 * s, y - 66 * s + k), (x, y - 66 * s)],
              fill=(250, 250, 250, a), outline=(150, 150, 150, a))


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 880, 520, (230, 70, 40), 1.0 + 0.25 * math.sin(c.t * 4))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 420), "KENAPA", 124, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 545), "25 NOVEMBER?", 112, KUNING, nama_font="caption", stroke=11, stroke_warna=GELAP)
    # kalender raksasa, lingkaran merah langsung tergambar sejak frame 0
    goyang = math.sin(c.t * 2.2) * 2.5
    kalender(img, 540, 900, 1.12, "25", "NOVEMBER", alpha=1.0, sudut=goyang,
             lingkar=clamp(0.45 + c.t / 0.9))
    d = ImageDraw.Draw(img, "RGBA")
    a1 = c.p(0.18, 0.24) * (1 - c.p(0.4, 0.42))
    stempel(img, "SELAMAT HARI GURU!", 540, 1250, 0.8 * pop(c, 0.18) * (1 if a1 > 0 else 0), uk=60, sudut=-5,
            warna=(30, 110, 60))
    a2 = c.p(0.42, 0.48)
    if a2 > 0:
        s = pop(c, 0.42)
        se.teks(d, (540, 1250), "ANGKA 100?", int(104 * s) + 1, KUNING, nama_font="caption", stroke=10,
                stroke_warna=GELAP, alpha=a2 * (1 - c.p(0.64, 0.67)))
    a3 = c.p(0.66, 0.72)
    if a3 > 0:
        pita(img, 1250, "Ceritanya mulai tahun 1912…", uk=54, alpha=a3)
    hdr(img, "Kenapa sih…", alpha=c.p(0.85, 0.95))
    return img


def a_pghb(c):
    kamera = se.kamera_antara(cam(NUSA, -4.0, 112.0, 0.75), cam(NUSA, -7.2, 110.0, 1.75), c.p(0.0, 0.45))
    img = se.render_peta(NUSA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, layar(NUSA, kamera, (-5.6, 110.5)), "Laut Jawa", 38, alpha=c.p(0.3, 0.4))
    for i, ll in enumerate(SEKOLAH_JAWA):
        k = c.p(0.35 + i * 0.025, 0.42 + i * 0.025)
        x, y = layar(NUSA, kamera, ll)
        ikon_sekolah_peta(d, x, y, 1.5 * back_out(k), k)
    am = c.p(0.5, 0.58)
    mx, my = layar(NUSA, kamera, MAGELANG)
    titik_kota(d, mx, my, "Magelang", am, (255, 200, 60), dy=-55, t=c.t)
    se.kartu(img, 540, 470, "1912 · zaman Hindia Belanda", "guru-guru pribumi berserikat", COKLAT,
             alpha=c.p(0.02, 0.1), tiang=False, skala=pop(c, 0.02) * 1.15)
    a = c.p(0.62, 0.7)
    if a > 0:
        tag_nama(img, 540, 1130, "PGHB", 1.15 * pop(c, 0.62), a, warna=(170, 40, 30), uk=80, sudut=-4)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1265), "Persatuan Guru Hindia Belanda", 46, TINTA, nama_font="tangan", stroke=5,
                stroke_warna=KREM_LABEL, alpha=c.p(0.7, 0.78))
    hdr(img, "Awalnya…")
    return img


def a_anggota(c):
    img = LATAR.copy()
    se.panel(img, (60, 390, 1020, 1320), alpha=c.p(0, 0.05))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 450), "Siapa anggotanya?", 56, (150, 40, 30), nama_font="judul", alpha=c.p(0.0, 0.06))
    a_fase1 = 1 - c.p(0.5, 0.56)
    isi = [("guru bantu", (40, 70, 120)), ("guru desa", (46, 120, 80)), ("kepala sekolah", (150, 70, 40)),
           ("penilik sekolah", (90, 60, 120))]
    for i, (nama, w) in enumerate(isi):
        k = c.p(0.06 + i * 0.08, 0.13 + i * 0.08)
        x = 300 + (i % 2) * 480
        y = 600 + (i // 2) * 330
        guru(d, x, y, 1.15 * back_out(k), k * a_fase1, w)
        se.teks(d, (x, y + 190), nama, 38, TINTA, nama_font="tangan", alpha=k * a_fase1)
    # fase 2: timbangan hak
    b = c.p(0.52, 0.6)
    if b > 0:
        sudut = lerp(0.32, 0.0, c.p(0.68, 0.85))
        timbangan(d, 540, 640, sudut, b, "pribumi", "Belanda")
        a2 = c.p(0.85, 0.92)
        if a2 > 0:
            stempel(img, "HAK YANG SAMA!", 540, 1180, 0.85 * pop(c, 0.85), uk=64, sudut=-6)
    hdr(img, "Isinya macam-macam")
    return img


def a_pecah(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # retakan kertas
    rng = random.Random(5)
    kr = c.p(0.55, 0.75)
    if kr > 0:
        for j in range(5):
            x, y = 540 + rng.uniform(-80, 80), 860 + rng.uniform(-80, 80)
            pts = [(x, y)]
            ang = rng.uniform(0, 2 * math.pi)
            for _ in range(7):
                ang += rng.uniform(-0.6, 0.6)
                x += 60 * math.cos(ang)
                y += 60 * math.sin(ang)
                pts.append((x, y))
            n = max(2, int(len(pts) * kr))
            d.line(pts[:n], fill=(80, 50, 30, 200), width=5)
    for i, (nama, x, y, sd) in enumerate(ORGANISASI):
        k = c.p(0.05 + i * 0.05, 0.12 + i * 0.05)
        geser = math.sin(c.t * 2 + i) * 6
        jauh = c.p(0.6, 0.8) * 30
        dx = (x - 540) / 540 * jauh
        tag_nama(img, x + dx, y + geser, nama, 0.95 * back_out(k), k, warna=WARNA_ORG[i], uk=58, sudut=sd)
    se.kartu(img, 540, 450, "Organisasi guru waktu itu", "dipisah sekolah, daerah, sampai agama", BIRU,
             alpha=c.p(0.0, 0.06), tiang=False, skala=pop(c, 0.0) * 1.1)
    a = c.p(0.66, 0.72)
    stempel(img, "TERPECAH-PECAH!", 540, 1290, 0.8 * pop(c, 0.66) * (1 if a > 0 else 0), uk=64, sudut=4)
    hdr(img, "Jalan sendiri-sendiri")
    return img


def a_pgi(c):
    img = LATAR.copy()
    se.glow(img, 540, 820, 420, (255, 210, 120), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 450, "Tahun 1932", "langkah paling berani", MERAH, alpha=c.p(0.0, 0.06), tiang=False,
             skala=pop(c, 0.0) * 1.2)
    # nama lama dicoret
    tag_nama(img, 540, 640, "Hindia Belanda", 1.0, 1.0 - 0.5 * c.p(0.5, 0.6), warna=(110, 90, 70), uk=66, sudut=-3,
             coret=c.p(0.22, 0.34))
    # nama baru turun
    a = c.p(0.32, 0.4)
    if a > 0:
        y = lerp(560, 860, back_out(c.p(0.32, 0.42)))
        tag_nama(img, 540, y, "INDONESIA", 1.25, a, warna=(205, 30, 30), uk=86, sudut=3)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1000), "PGHB  →  PGI", 64, TINTA, nama_font="caption", alpha=c.p(0.4, 0.48))
        se.teks(d, (540, 1075), "Persatuan Guru Indonesia", 46, (90, 70, 50), nama_font="tangan",
                alpha=c.p(0.44, 0.52))
    b = c.p(0.6, 0.66)
    stempel(img, "BELANDA KAGET!", 540, 1220, 0.85 * pop(c, 0.6) * (1 if b > 0 else 0), uk=66, sudut=-7)
    hdr(img, "Nah, ini dia…")
    return img


def a_jepang(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 860, 380, (180, 40, 30), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    se.kartu(img, 540, 460, "1942 · Jepang datang", "semua organisasi dilarang", MERAH, alpha=c.p(0.0, 0.06),
             tiang=False, skala=pop(c, 0.0) * 1.2)
    sekolah(d, 540, 860, 2.6, 1.0, gembok=c.p(0.35, 0.45))
    a = c.p(0.5, 0.56)
    stempel(img, "DITUTUP", 540, 1120, 0.9 * pop(c, 0.5) * (1 if a > 0 else 0), uk=76, sudut=-9)
    b = c.p(0.72, 0.78)
    if b > 0:
        tag_nama(img, 540, 1270, "PGI · berhenti", 0.9, b, warna=(80, 80, 90), uk=56, sudut=2)
    hdr(img, "Masa pendudukan")
    return img


def a_merdeka(c):
    kamera = se.kamera_antara(cam(NUSA, -6.9, 108.0, 1.7), cam(NUSA, -7.2, 110.0, 1.6), c.p(0.0, 1.0))
    img = se.render_peta(NUSA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    jx, jy = layar(NUSA, kamera, JAKARTA)
    a0 = c.p(0.02, 0.08)
    bendera_rp(d, jx, jy, 1.5 * pop(c, 0.02), a0, c.t)
    titik_kota(d, jx, jy, "Jakarta", a0, (255, 200, 60), dy=45, t=c.t)
    se.kartu(img, 540, 470, "17 Agustus 1945", "Indonesia merdeka!", MERAH, alpha=c.p(0.02, 0.1), tiang=False,
             skala=pop(c, 0.02) * 1.2)
    # pertempuran pecah
    for i, (ll, s0) in enumerate([(SURABAYA, 0.45), (BANDUNG, 0.55), (SEMARANG, 0.62), ((-7.0, 109.3), 0.7)]):
        a = c.p(s0, s0 + 0.06)
        if a > 0:
            x, y = layar(NUSA, kamera, ll)
            r = 55 + 10 * math.sin(c.t * 9 + i)
            ledakan(d, x, y, r * back_out(c.p(s0, s0 + 0.08)), a, seed=i)
    sx, sy = layar(NUSA, kamera, SURABAYA)
    label(d, (sx - 20, sy + 80), "Surabaya", 40, alpha=c.p(0.5, 0.56))
    a2 = c.p(0.32, 0.4)
    if a2 > 0:
        pita(img, 1240, "Tapi Belanda mau balik lagi", uk=54, alpha=a2)
    hdr(img, "Merdeka, tapi belum aman")
    return img


def _pos_org_peta(kamera):
    return layar(NUSA, kamera, SURAKARTA)


def a_kongres(c):
    kamera = se.kamera_antara(cam(NUSA, -7.2, 110.0, 1.6), cam(NUSA, -7.45, 110.7, 2.6), c.p(0.0, 0.4))
    img = se.render_peta(NUSA, kamera)
    se.tint(img, (10, 6, 0), 0.25 * c.p(0.45, 0.6))
    d = ImageDraw.Draw(img, "RGBA")
    kx, ky = layar(NUSA, kamera, SURAKARTA)
    a = c.p(0.1, 0.2)
    se.glow(img, kx, ky, 160, (255, 200, 80), a)
    d = ImageDraw.Draw(img, "RGBA")
    titik_kota(d, kx, ky, "Surakarta", a, (255, 200, 60), dy=-60, uk=46, t=c.t)
    se.kartu(img, 540, 470, "Kongres Guru Indonesia", "Surakarta, 24–25 November 1945", COKLAT,
             alpha=c.p(0.08, 0.16), tiang=False, skala=pop(c, 0.08) * 1.15)
    # organisasi-organisasi terbang & melebur ke Surakarta
    m = c.p(0.42, 0.68)
    hilang = 1 - c.p(0.64, 0.7)
    if c.p(0.3, 0.36) > 0 and hilang > 0:
        for i, (nama, x, y, sd) in enumerate(ORGANISASI):
            k = clamp((m - i * 0.03) / 0.75)
            tx = lerp(x, kx, k)
            ty = lerp(y + 80, ky, k) - math.sin(k * math.pi) * 80
            tag_nama(img, tx, ty, nama, 0.8 * (1 - 0.6 * k), c.p(0.3, 0.36) * hilang, warna=WARNA_ORG[i], uk=54,
                     sudut=sd * (1 - k))
    b = c.p(0.68, 0.76)
    if b > 0:
        se.glow(img, kx, ky, 260, (255, 230, 150), 1.2 * b)
        tag_nama(img, 540, 1130, "PGRI", 1.5 * pop(c, 0.68), b, warna=(205, 30, 30), uk=96, sudut=-3)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1275), "Persatuan Guru Republik Indonesia", 44, TINTA, nama_font="tangan", stroke=5,
                stroke_warna=KREM_LABEL, alpha=c.p(0.76, 0.84))
    hdr(img, "Di tengah suasana perang")
    return img


def a_seratus(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    kalender(img, 280, 640, 0.62, "17", "AGUSTUS", "1945", alpha=c.p(0.0, 0.06), sudut=-6)
    a2 = c.p(0.04, 0.1)
    kalender(img, 800, 640, 0.62, "25", "NOVEMBER", "1945", alpha=a2, sudut=6,
             lingkar=c.p(0.32, 0.42))
    d = ImageDraw.Draw(img, "RGBA")
    k = c.p(0.08, 0.32)
    se.garis_putus(d, [(420, 640), (540, 590), (660, 640)], k, (200, 40, 30), tebal=7, putus=16, celah=10)
    n = max(1, int(round(lerp(1, 100, k))))
    s = 1.0 + 0.25 * c.p(0.3, 0.34) * (1 - c.p(0.36, 0.42))
    se.teks(d, (540, 960), str(n), int(210 * s), MERAH, nama_font="caption", stroke=10, stroke_warna=PUTIH)
    se.teks(d, (540, 1090), "HARI", 70, TINTA, nama_font="caption", alpha=c.p(0.1, 0.16))
    a = c.p(0.5, 0.56)
    if a > 0:
        pita(img, 1230, "= HARI GURU NASIONAL", uk=60, alpha=a, warna_garis=(30, 110, 60))
    b = c.p(0.72, 0.8)
    if b > 0:
        se.kartu(img, 540, 450, "Keppres No. 78 Tahun 1994", "", BIRU, alpha=b, tiang=False, skala=pop(c, 0.72) * 1.2)
    hdr(img, "Ini jawabannya")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = Kamera(*cam(NUSA, -7.2, 110.0, 1.6))
    img = se.render_peta(NUSA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    for i, ll in enumerate(SEKOLAH_JAWA):
        x, y = layar(NUSA, kamera, ll)
        ikon_sekolah_peta(d, x, y, 1.4, 1.0)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.02, 0.1) * (1 - c.p(0.55, 0.62))
    if a > 0:
        se.panel(img, (90, 480, 990, 1060), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 560), "100 hari setelah merdeka,", 46, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 630), "guru-guru udah bersatu", 46, TINTA, nama_font="judul", alpha=a)
        papan_tulis(d, 260, 700, 820, 900, a)
        se.teks(d, (540, 800), "Terima kasih, Guru!", 60, (245, 245, 235), nama_font="tangan", alpha=a)
        se.teks(d, (540, 990), "25 NOVEMBER", 70, (170, 30, 20), nama_font="caption", alpha=a)
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
    Adegan("hook", "Kenapa Hari Guru tanggal dua puluh lima November? Lagi rame ucapan Hari Guru, kan? "
                   "Jawabannya ada hubungannya sama angka seratus. Dan ceritanya mulai jauh sebelum merdeka.",
           a_hook, transisi=False),
    Adegan("pghb", "Tahun sembilan belas dua belas, guru-guru pribumi di Hindia Belanda bikin perkumpulan. "
                   "Namanya PGHB, Persatuan Guru Hindia Belanda.", a_pghb),
    Adegan("anggota", "Isinya guru bantu, guru desa, kepala sekolah, sampai penilik sekolah. Mereka nuntut hak dan "
                      "posisi yang sama dengan orang Belanda.", a_anggota),
    Adegan("pecah", "Tapi guru zaman itu terpecah-pecah. Beda sekolah, beda daerah, beda agama, beda perkumpulan. "
                    "Jalan sendiri-sendiri.", a_pecah),
    Adegan("pgi", "Nah, tahun sembilan belas tiga puluh dua, mereka nekat. PGHB ganti nama jadi PGI, Persatuan "
                  "Guru Indonesia. Kata Indonesia itu bikin Belanda kaget, karena jadi lambang kebangsaan.", a_pgi),
    Adegan("jepang", "Lalu Jepang datang. Semua organisasi dilarang, sekolah ditutup. PGI terpaksa berhenti.",
           a_jepang, transisi=False),
    Adegan("merdeka", "Tahun sembilan belas empat puluh lima, Indonesia merdeka. Tapi Belanda mau balik, dan "
                      "pertempuran pecah di mana-mana.", a_merdeka),
    Adegan("kongres", "Di tengah suasana perang itu, para guru berkumpul di Surakarta, dua puluh empat sampai dua "
                      "puluh lima November. Semua organisasi guru yang terpecah dihapus, dilebur jadi satu: PGRI.",
           a_kongres),
    Adegan("seratus", "Dan dua puluh lima November itu, tepat seratus hari setelah proklamasi. Hari lahir PGRI "
                      "inilah yang sekarang kita peringati sebagai Hari Guru Nasional.", a_seratus),
    Adegan("penutup", "Jadi, baru seratus hari merdeka, guru-guru kita udah bersatu. Udah bilang terima kasih ke "
                      "gurumu? Follow Ngomongin Sejarah buat cerita berikutnya!", a_penutup),
]
