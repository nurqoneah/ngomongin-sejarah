"""Shorts 90 detik: Perang Badar.

Narasi tiap adegan dibacakan terpisah, jadi durasi adegan = durasi suaranya.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5) = progres dari 20% ke 50% adegan.
"""

import math
import random

from PIL import Image, ImageDraw

import shorts_engine as se
from shorts_engine import (EMAS, HIJAU, HIJAU_TUA, MERAH, MERAH_TUA, PUTIH, TINTA, W, H, Adegan, Kamera, Peta,
                           back_out, clamp, ease, lerp, prog)

NAMA_FILE = "perang-badar-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "PERANG BADAR"

# ------------------------------------------------------------------ peta Hijaz

LAUT = [[
    (29.55, 34.98), (29.0, 34.85), (28.4, 34.78), (28.05, 34.78),
    # pesisir Arab
    (27.9, 35.15), (27.6, 35.5), (27.35, 35.72), (26.8, 36.05), (26.2, 36.45), (25.6, 36.9), (25.0, 37.25),
    (24.6, 37.6), (24.1, 38.06), (23.6, 38.5), (23.2, 38.8), (22.8, 39.03), (22.3, 39.08), (21.8, 39.12),
    (21.5, 39.17), (21.0, 39.4), (20.5, 39.9), (20.15, 40.27), (19.6, 40.7), (18.8, 41.3),
    # pesisir Afrika
    (18.8, 37.3), (19.6, 37.25), (20.5, 37.2), (21.2, 37.0), (22.0, 36.85), (22.4, 36.4), (23.0, 35.7),
    (23.9, 35.6), (24.3, 35.2), (25.07, 34.9), (25.8, 34.5), (26.1, 34.28), (26.75, 33.94), (27.25, 33.8),
    (27.6, 33.55), (28.0, 33.3), (28.8, 32.9), (29.2, 32.9), (28.7, 33.3), (28.24, 33.62),
    # Sinai
    (27.95, 34.0), (27.73, 34.25), (28.0, 34.43), (28.5, 34.52), (29.0, 34.7), (29.5, 34.9),
]]
GUNUNG = [(28.5, 35.8, 0.8), (27.2, 36.9, 0.7), (26.0, 37.9, 0.8), (25.0, 38.8, 0.7), (24.0, 39.9, 0.6),
          (23.0, 39.9, 0.5), (22.3, 40.2, 0.6), (21.2, 40.5, 0.6), (20.2, 41.4, 0.7), (28.6, 33.9, 0.4),
          (30.3, 35.6, 0.6), (26.5, 39.5, 0.9), (29.5, 38.5, 1.0)]

print("  menyiapkan peta...")
PETA = Peta(33.5, 42.5, 19.0, 31.0, 300, LAUT, GUNUNG)
px = PETA.px

MEKKAH = (21.42, 39.83)
MADINAH = (24.47, 39.61)
BADAR = (23.78, 38.79)

RUTE_KAFILAH_A = [(30.9, 36.1), (29.3, 36.25), (28.0, 36.6), (26.8, 37.3), (25.6, 38.0), (24.7, 38.45)]
RUTE_KAFILAH_B = [(24.7, 38.45), (24.3, 38.18), (23.8, 38.5), (23.3, 38.85), (22.8, 39.15), (22.1, 39.25),
                  (21.6, 39.4), MEKKAH]
RUTE_UTUSAN = [(24.7, 38.45), (23.6, 39.05), (22.5, 39.55), MEKKAH]
RUTE_MUSLIM = [MADINAH, (24.25, 39.3), (23.98, 38.98), (23.86, 38.8)]
RUTE_QURAISY = [MEKKAH, (22.2, 39.55), (23.0, 39.2), (23.68, 38.85)]


def cam_ll(lat, lon, zoom):
    x, y = px(lat, lon)
    return (x, y, zoom)


def ke_layar(cam, rute):
    return [cam.layar(*px(*p)) for p in rute]


FORMASI_M = se.formasi(22, 110, 60, 1)
FORMASI_Q = se.formasi(64, 190, 100, 2)


def pasukan(d, cam, pos_ll, formasi, warna, s=0.75, alpha=1.0, tebar=1.0):
    x, y = cam.layar(*px(*pos_ll))
    for dx, dy in formasi:
        se.prajurit(d, x + dx * tebar, y + dy * tebar, warna, s, alpha)
    return x, y


def label_kota(img, d, cam, ll, nama, ikon=None, alpha=1.0, dy=50, dx=0):
    x, y = cam.layar(*px(*ll))
    if ikon:
        ikon(d, x, y, 0.9, alpha)
    se.teks(d, (min(x + dx, W - 110), y + dy), nama, 40, TINTA, stroke=5, stroke_warna=(240, 225, 190), alpha=alpha)


def label_badar(d, cam, alpha=1.0, s=1.0):
    x, y = cam.layar(*px(*BADAR))
    se.ikon_sumur(d, x, y, 0.8 * s, alpha)
    se.teks(d, (x - 34 * s, y - 30 * s), "Badar", int(46 * s), (120, 20, 15), anchor="rm", stroke=5,
            stroke_warna=(240, 225, 190), alpha=alpha)


def latar_peta(cam):
    img = se.render_peta(PETA, cam)
    return img, ImageDraw.Draw(img, "RGBA")


def syam(d, cam, alpha=1.0):
    x, y = cam.layar(*px(30.9, 36.1))
    y = max(y, 420)
    se.teks(d, (x, y), "SYAM", 52, TINTA, stroke=6, stroke_warna=(240, 225, 190), alpha=alpha)
    se.teks(d, (x, y - 52), "▲", 34, TINTA, nama_font="ui", alpha=alpha)


def kafilah(d, cam, rute, k, t, n=7, alpha=1.0):
    """Barisan unta di sepanjang rute, kepala barisan di progres k."""
    titik = ke_layar(cam, rute)
    kepala = None
    for i in range(n):
        ki = k - i * 0.018
        if ki < 0:
            continue
        (x, y), _ = se.titik_di_jalur(titik, ki)
        se.ikon_unta(d, x, y, 1.2, (75, 45, 20), alpha, t * 9 + i)
        if i == 0:
            kepala = (x, y)
    return kepala


# ------------------------------------------------------------------ latar lembah Badar

print("  menyiapkan lembah Badar...")
LEMBAH = se.latar_tekstur(W, H, 11, bukit=[(-40, 380, 380, 260), (1120, 330, 360, 280), (900, 470, 200, 140),
                                           (-80, 1640, 420, 300), (1160, 1700, 460, 320), (540, 1900, 380, 160)])

SUMUR_TUTUP = [(330, 560), (720, 520), (210, 760)]
SUMUR_JAGA = (560, 860)
ARISY = (880, 560)

POS_M = (540, 700)
POS_Q = (540, 1180)
F_M = se.formasi(44, 560, 120, 3)
F_Q = se.formasi(130, 820, 230, 4)


def latar_lembah(gelap=0.0, malam=0.0):
    img = LEMBAH.convert("RGBA")
    se.tint(img, (8, 16, 45), malam * 0.5)
    se.tint(img, (0, 0, 0), gelap)
    return img, ImageDraw.Draw(img, "RGBA")


def label_lembah(d, alpha=1.0):
    se.teks(d, (300, 430), "Pihak dekat (Madinah)", 30, TINTA, nama_font="tangan_tipis", stroke=4,
            stroke_warna=(240, 225, 190), alpha=alpha)
    se.teks(d, (760, 1360), "Pihak jauh (Mekkah)", 30, TINTA, nama_font="tangan_tipis", stroke=4,
            stroke_warna=(240, 225, 190), alpha=alpha)


def gambar_sumur(d, tutup=0.0, alpha=1.0):
    for x, y in SUMUR_TUTUP:
        se.ikon_sumur(d, x, y, 1.0, alpha, tutup)
    x, y = SUMUR_JAGA
    d.ellipse((x - 80, y - 36, x + 80, y + 36), fill=(50, 105, 150, int(230 * alpha)), outline=(40, 30, 20, int(255 * alpha)), width=5)
    se.ikon_sumur(d, x, y, 1.0, alpha)


def tentara_lembah(d, t, m_y=0.0, q_y=0.0, q_tebar=1.0, q_gugur=0.0, alpha=1.0):
    mx, my = POS_M[0], POS_M[1] + m_y
    for dx, dy in F_M:
        se.prajurit(d, mx + dx, my + dy, HIJAU, 0.9, alpha)
    rng = random.Random(9)
    qx, qy = POS_Q[0], POS_Q[1] + q_y
    for dx, dy in F_Q:
        jatuh = rng.random() < 0.35 and q_gugur > 0
        if jatuh:
            a = alpha * (1 - q_gugur)
            x, y = qx + dx, POS_Q[1] - 140 + dy * 0.6
            if a > 0.05:
                se.prajurit(d, x, y, MERAH, 0.9, a)
            if q_gugur > 0.3:
                d.line((x - 6, y - 6, x + 6, y + 6), fill=(60, 20, 15, int(200 * alpha)), width=3)
                d.line((x + 6, y - 6, x - 6, y + 6), fill=(60, 20, 15, int(200 * alpha)), width=3)
            continue
        se.prajurit(d, qx + dx * q_tebar, qy + dy * q_tebar, MERAH, 0.9, alpha)
    se.bendera(d, mx - 300, my + 20, HIJAU_TUA, 1.0, alpha, t * 4)
    se.bendera(d, qx + 430 * q_tebar, qy - 40, MERAH_TUA, 1.0, alpha, t * 4 + 1)


def hdr(img, sub="", alpha=1.0):
    se.header(img, JUDUL, sub, alpha)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img, d = latar_lembah(gelap=0.55)
    k = c.p(0, 1)
    # siluet pasukan samar di belakang
    tentara_lembah(d, c.t, m_y=-40, q_y=20, alpha=0.35)
    se.tint(img, (0, 0, 0), 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    s1 = back_out((c.t) / 0.4)
    se.teks(d, (540, 520), "313", int(230 * s1) + 1, HIJAU, nama_font="caption", stroke=10, stroke_warna=(0, 0, 0))
    se.teks(d, (540, 660), "orang", 54, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0), alpha=c.p(0.05, 0.15))
    se.teks(d, (540, 735), "2 kuda · 70 unta", 44, (220, 220, 220), nama_font="ui", stroke=5, stroke_warna=(0, 0, 0), alpha=c.p(0.2, 0.3))
    se.teks(d, (540, 850), "VS", 90, EMAS, nama_font="judul", stroke=8, stroke_warna=(0, 0, 0), alpha=c.p(0.38, 0.45))
    s2 = back_out((c.t / c.d - 0.42) / 0.12) if c.t / c.d > 0.42 else 0
    if s2 > 0:
        se.teks(d, (540, 1010), "±1000", int(200 * s2) + 1, MERAH, nama_font="caption", stroke=10, stroke_warna=(0, 0, 0))
    se.teks(d, (540, 1140), "bersenjata lengkap", 48, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0), alpha=c.p(0.55, 0.65))
    hdr(img, "17 Ramadhan 2 H · 624 M", alpha=c.p(0.75, 0.9))
    if k > 0.75:
        se.teks(d, (900, 840), "?", int(160 * back_out((c.t / c.d - 0.75) / 0.1)) + 1, EMAS, nama_font="judul",
                stroke=8, stroke_warna=(0, 0, 0))
    return img


CAM_S2 = (cam_ll(27.6, 37.4, 0.55), cam_ll(24.6, 38.7, 0.78))
CAM_S3 = (CAM_S2[1], cam_ll(23.0, 39.1, 0.8))
CAM_S4 = (CAM_S3[1], cam_ll(22.7, 39.2, 0.95))
CAM_S5 = (CAM_S4[1], cam_ll(23.9, 39.2, 1.1), cam_ll(23.8, 38.85, 2.6))


def a_kafilah(c):
    cam = se.kamera_antara(*CAM_S2, c.p(0.0, 0.95))
    img, d = latar_peta(cam)
    syam(d, cam)
    label_kota(img, d, cam, MADINAH, "Madinah", se.ikon_masjid, dy=0, dx=150)
    label_kota(img, d, cam, MEKKAH, "Mekkah", se.ikon_kabah, dy=58)
    label_badar(d, cam)
    kafilah_titik = ke_layar(cam, RUTE_KAFILAH_A)
    se.garis_putus(d, kafilah_titik, c.p(0, 0.85), (90, 55, 25), tebal=5, alpha=0.8, panah=False)
    kepala = kafilah(d, cam, RUTE_KAFILAH_A, c.p(0.0, 0.85), c.t)
    if kepala:
        se.kartu(img, kepala[0] + 40, kepala[1] - 30, "Kafilah Abu Sufyan", "± 1000 unta penuh harta",
                 (150, 100, 30), alpha=c.p(0.08, 0.2))
    # kaum Muslimin keluar dari Madinah
    if c.p(0.6, 0.65) > 0:
        rute = ke_layar(cam, RUTE_MUSLIM)
        k = c.p(0.65, 1.0) * 0.3
        se.garis_putus(d, rute, k, HIJAU_TUA, tebal=6, alpha=c.p(0.6, 0.65))
        (x, y), _ = se.titik_di_jalur(rute, k)
        for dx, dy in FORMASI_M:
            se.prajurit(d, x + dx, y + dy, HIJAU, 0.75, c.p(0.6, 0.66))
        se.kartu(img, x + 120, y + 140, "Kaum Muslimin", "± 313 orang", HIJAU, alpha=c.p(0.65, 0.75), tiang=False)
    hdr(img, "Tahun 2 Hijriah")
    return img


def _muslim_menunggu(img, d, cam, k=0.3, kartu=True, alpha=1.0):
    rute = ke_layar(cam, RUTE_MUSLIM)
    se.garis_putus(d, rute, k, HIJAU_TUA, tebal=6, alpha=alpha)
    (x, y), _ = se.titik_di_jalur(rute, k)
    for dx, dy in FORMASI_M:
        se.prajurit(d, x + dx, y + dy, HIJAU, 0.75, alpha)
    return x, y


def a_lolos(c):
    cam = se.kamera_antara(*CAM_S3, c.p(0, 1))
    img, d = latar_peta(cam)
    label_kota(img, d, cam, MADINAH, "Madinah", se.ikon_masjid, dy=0, dx=150)
    label_kota(img, d, cam, MEKKAH, "Mekkah", se.ikon_kabah, dy=58)
    label_badar(d, cam)
    se.garis_putus(d, ke_layar(cam, RUTE_KAFILAH_A), 1.0, (90, 55, 25), tebal=5, alpha=0.5, panah=False)
    _muslim_menunggu(img, d, cam)
    # utusan ke Mekkah
    ut = ke_layar(cam, RUTE_UTUSAN)
    ujung = se.garis_putus(d, ut, c.p(0.05, 0.4), MERAH, tebal=5, putus=10, celah=10)
    if ujung:
        (ux, uy), _ = se.titik_di_jalur(ut, 0.3)
        se.kartu(img, min(ux + 190, W - 170), uy, "Minta bantuan!", "", MERAH, alpha=c.p(0.1, 0.2) * (1 - c.p(0.6, 0.7)), tiang=False)
    # kafilah belok ke pesisir
    k = c.p(0.35, 0.92)
    se.garis_putus(d, ke_layar(cam, RUTE_KAFILAH_B), k, (90, 55, 25), tebal=5, alpha=0.85)
    kepala = kafilah(d, cam, RUTE_KAFILAH_B, max(k, 0.06), c.t)
    if c.p(0.4, 0.5) > 0 and kepala:
        se.teks(d, (kepala[0] - 170, kepala[1] - 40), "jalur pantai", 34, (40, 30, 80), nama_font="tangan",
                stroke=4, stroke_warna=(220, 230, 240), alpha=c.p(0.4, 0.5) * (1 - c.p(0.85, 0.95)))
    if c.p(0.85, 0.95) > 0:
        x, y = cam.layar(*px(*MEKKAH))
        se.kartu(img, x - 120, y - 110, "LOLOS!", "", (60, 120, 60), alpha=c.p(0.85, 0.92),
                 skala=back_out((c.t / c.d - 0.85) / 0.1), tiang=False)
    hdr(img, "Kafilah berbelok")
    return img


def a_quraisy(c):
    cam = se.kamera_antara(*CAM_S4, c.p(0, 1))
    img, d = latar_peta(cam)
    label_kota(img, d, cam, MADINAH, "Madinah", se.ikon_masjid, dy=0, dx=150)
    label_kota(img, d, cam, MEKKAH, "Mekkah", se.ikon_kabah, dy=58)
    label_badar(d, cam)
    se.garis_putus(d, ke_layar(cam, RUTE_KAFILAH_B), 1.0, (90, 55, 25), tebal=4, alpha=0.35, panah=False)
    _muslim_menunggu(img, d, cam)
    # Abu Jahal ngotot
    x0, y0 = cam.layar(*px(*MEKKAH))
    se.kartu(img, x0 + 170, y0 - 70, "Abu Jahal", "\"Kita tetap ke Badar!\"", MERAH,
             alpha=c.p(0.1, 0.22) * (1 - c.p(0.5, 0.6)), skala=back_out((c.t / c.d - 0.1) / 0.12))
    rute = ke_layar(cam, RUTE_QURAISY)
    k = c.p(0.4, 1.0)
    se.garis_putus(d, rute, k, MERAH_TUA, tebal=7, alpha=c.p(0.35, 0.42))
    (x, y), _ = se.titik_di_jalur(rute, k)
    for dx, dy in FORMASI_Q:
        se.prajurit(d, x + dx, y + dy, MERAH, 0.75, c.p(0.35, 0.45))
    se.kartu(img, x + 140, y + 10, "Pasukan Quraisy", "± 1000 orang · 100 kuda", MERAH, alpha=c.p(0.5, 0.6), tiang=False)
    hdr(img, "Quraisy berangkat")
    return img


def a_musyawarah(c):
    k_cam = c.p(0, 0.55)
    if c.t / c.d < 0.7:
        cam = se.kamera_antara(CAM_S5[0], CAM_S5[1], k_cam)
    else:
        cam = se.kamera_antara(CAM_S5[1], CAM_S5[2], c.p(0.7, 1.0))
    img, d = latar_peta(cam)
    label_kota(img, d, cam, MADINAH, "Madinah", se.ikon_masjid, dy=0, dx=150)
    label_kota(img, d, cam, MEKKAH, "Mekkah", se.ikon_kabah, dy=58)
    label_badar(d, cam)
    # Quraisy sudah di selatan Badar
    rq = ke_layar(cam, RUTE_QURAISY)
    se.garis_putus(d, rq, 1.0, MERAH_TUA, tebal=7)
    (x, y), _ = se.titik_di_jalur(rq, 1.0)
    for dx, dy in FORMASI_Q:
        se.prajurit(d, x + dx * 0.8, y + 40 + dy * 0.8, MERAH, 0.75)
    # Muslim lanjut ke Badar
    _muslim_menunggu(img, d, cam, 0.3 + 0.7 * c.p(0.45, 0.95))
    # kutipan Anshar
    a = c.p(0.12, 0.22) * (1 - c.p(0.88, 0.97))
    if a > 0:
        se.panel(img, (70, 400, 1010, 800), alpha=a)
        d2 = ImageDraw.Draw(img, "RGBA")
        se.teks(d2, (540, 455), "Musyawarah", 40, HIJAU_TUA, nama_font="judul", alpha=a)
        f = se.font("tangan", 44)
        baris = se.bungkus("“Seandainya engkau ajak kami menyeberangi lautan, kami pasti ikut!”", f, 830)
        for i, b in enumerate(baris):
            se.teks(d2, (540, 540 + i * 64), b, 44, TINTA, alpha=a)
        se.teks(d2, (540, 750), "— Sa'ad bin Mu'adz, pemimpin Anshar", 30, (100, 70, 40),
                nama_font="tangan_tipis", alpha=a * c.p(0.3, 0.4))
    hdr(img, "Maju ke Badar")
    return img


def a_sumur(c):
    malam = c.p(0.42, 0.55)
    img, d = latar_lembah(malam=malam)
    label_lembah(d, 1 - malam * 0.6)
    gambar_sumur(d, tutup=c.p(0.18, 0.3))
    # pasukan Muslim berkemah di sumur terdekat musuh
    for dx, dy in F_M:
        se.prajurit(d, POS_M[0] + dx, POS_M[1] + 60 + dy * 0.8, HIJAU, 0.9)
    # Quraisy di sisi jauh, samar
    for dx, dy in F_Q:
        se.prajurit(d, POS_Q[0] + dx, POS_Q[1] + 40 + dy, MERAH, 0.9, 0.85)
    se.kartu(img, 540, 990, "Usul Hubab bin Mundzir", "kuasai sumur, tutup yang lain",
             (60, 110, 160), alpha=c.p(0.05, 0.14) * (1 - c.p(0.4, 0.46)), tiang=False)
    se.hujan(img, c.t, kuat=c.p(0.45, 0.55) * (1 - c.p(0.92, 1.0) * 0.6))
    # doa semalaman di 'arisy
    a = c.p(0.68, 0.78)
    if a > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.glow(img, ARISY[0], ARISY[1], 150 + 15 * math.sin(c.t * 4), kuat=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.ikon_tenda(d, ARISY[0], ARISY[1], 1.1, a)
        se.kartu(img, ARISY[0] - 170, ARISY[1] + 130, "Doa sepanjang malam", "", EMAS, alpha=a, tiang=False)
    hdr(img, "Malam 17 Ramadhan")
    return img


DUEL_M = [("Hamzah", "bin Abdul Muthalib"), ("Ali", "bin Abi Thalib"), ("Ubaidah", "bin Al-Harits")]
DUEL_Q = [("Utbah", "bin Rabi'ah"), ("Syaibah", "bin Rabi'ah"), ("Walid", "bin Utbah")]


def a_duel(c):
    img, d = latar_lembah(malam=1 - c.p(0, 0.2))
    gambar_sumur(d, tutup=1.0)
    tentara_lembah(d, c.t)
    a = c.p(0.2, 0.3)
    se.tint(img, (0, 0, 0), 0.45 * a)
    for i, (n, s) in enumerate(DUEL_M):
        mulai = 0.35 + i * 0.05
        se.kartu(img, 280, 700 + i * 170, n, s, HIJAU, alpha=c.p(mulai, mulai + 0.06), tiang=False, lebar=380,
                 skala=back_out((c.t / c.d - mulai) / 0.08))
    for i, (n, s) in enumerate(DUEL_Q):
        mulai = 0.55 + i * 0.05
        se.kartu(img, 800, 700 + i * 170, n, s, MERAH, alpha=c.p(mulai, mulai + 0.06), tiang=False, lebar=380,
                 coret=c.p(0.82 + i * 0.04, 0.88 + i * 0.04), skala=back_out((c.t / c.d - mulai) / 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 870), "VS", 80, EMAS, nama_font="judul", stroke=7, stroke_warna=(0, 0, 0), alpha=c.p(0.45, 0.55))
    se.teks(d, (540, 560), "DUEL PEMBUKA", 52, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0), alpha=a)
    hdr(img, "17 Ramadhan 2 H")
    return img


def a_perang(c):
    img, d = latar_lembah()
    gambar_sumur(d, tutup=1.0)
    maju = c.p(0.0, 0.25)
    mundur = c.p(0.45, 0.75)
    q_y = -200 * maju + 180 * mundur
    m_y = 60 * maju + 80 * mundur
    tentara_lembah(d, c.t, m_y=m_y, q_y=q_y, q_tebar=1 + 0.5 * mundur, q_gugur=c.p(0.35, 0.7))
    # percikan di garis depan
    bentrok = c.p(0.18, 0.25) * (1 - c.p(0.6, 0.7))
    if bentrok > 0:
        rng = random.Random(int(c.t * 12))
        for _ in range(14):
            x = rng.uniform(260, 820)
            y = (POS_M[1] + m_y + POS_Q[1] + q_y) / 2 + rng.uniform(-60, 40)
            r = rng.uniform(10, 26)
            d.line((x - r, y, x + r, y), fill=(255, 230, 120, int(230 * bentrok)), width=4)
            d.line((x, y - r, x, y + r), fill=(255, 230, 120, int(230 * bentrok)), width=4)
            d.line((x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6), fill=(255, 255, 255, int(200 * bentrok)), width=3)
        # debu
        se.tint(img, (230, 200, 150), 0.12 * bentrok)
    se.kartu(img, 560, 1000, "Pasukan kecil bertahan", "", HIJAU, alpha=c.p(0.25, 0.33) * (1 - c.p(0.5, 0.55)), tiang=False)
    se.kartu(img, 560, 1000, "Quraisy kocar-kacir", "", MERAH, alpha=c.p(0.5, 0.56) * (1 - c.p(0.66, 0.7)), tiang=False)
    a = c.p(0.7, 0.78)
    if a > 0:
        se.kartu(img, 540, 1080, "Abu Jahal", "oleh Mu'adz & Mu'awwidz, dua pemuda Anshar", MERAH, alpha=a,
                 tiang=False, coret=c.p(0.82, 0.95), skala=back_out((c.t / c.d - 0.7) / 0.08))
    hdr(img, "Perang pecah")
    return img


def _angka(d, x, y, nilai, k, warna, label, a):
    se.teks(d, (x, y), str(int(round(nilai * clamp(k)))), 150, warna, nama_font="caption", stroke=9,
            stroke_warna=(0, 0, 0), alpha=a)
    se.teks(d, (x, y + 110), label, 40, PUTIH, nama_font="caption", stroke=5, stroke_warna=(0, 0, 0), alpha=a)


def a_hasil(c):
    img, d = latar_lembah(gelap=0.25)
    tentara_lembah(d, c.t, m_y=140, q_y=-20, q_tebar=1.5, q_gugur=1.0, alpha=0.6)
    se.tint(img, (10, 5, 0), 0.5)
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 470), "HASIL PERANG", 58, EMAS, nama_font="judul", stroke=6, stroke_warna=(0, 0, 0))
    _angka(d, 290, 680, 70, c.p(0.08, 0.3), MERAH, "Quraisy tewas", c.p(0.05, 0.12))
    _angka(d, 790, 680, 70, c.p(0.35, 0.55), (240, 150, 50), "jadi tawanan", c.p(0.32, 0.4))
    _angka(d, 540, 1010, 14, c.p(0.62, 0.85), HIJAU, "sahabat gugur syahid", c.p(0.6, 0.68))
    hdr(img, "17 Ramadhan 2 H")
    return img


def _anak(d, x, y, a):
    c = (250, 235, 200, int(255 * a))
    d.ellipse((x - 16, y - 50, x + 16, y - 18), fill=c, outline=(40, 30, 20, int(255 * a)), width=3)
    d.rounded_rectangle((x - 22, y - 14, x + 22, y + 36), 12, fill=(60, 140, 90, int(255 * a)), outline=(40, 30, 20, int(255 * a)), width=3)


def a_tawanan(c):
    img, d = latar_lembah(gelap=0.4)
    se.panel(img, (70, 400, 1010, 1260), alpha=c.p(0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 480), "TEBUSAN UNIK", 58, (150, 40, 30), nama_font="judul", alpha=c.p(0.02, 0.1))
    se.teks(d, (540, 600), "1 tawanan yang bisa baca tulis", 42, TINTA, alpha=c.p(0.1, 0.2))
    se.teks(d, (540, 670), "= bebas, asal ngajarin", 42, TINTA, alpha=c.p(0.25, 0.35))
    for i in range(10):
        mulai = 0.4 + i * 0.04
        a = c.p(mulai, mulai + 0.05)
        x = 220 + (i % 5) * 160
        y = 830 + (i // 5) * 160
        s = back_out((c.t / c.d - mulai) / 0.08)
        if a > 0:
            _anak(d, x, y + (1 - s) * 30, a)
    se.teks(d, (540, 1170), "10 anak Madinah", 56, HIJAU_TUA, nama_font="caption", alpha=c.p(0.8, 0.9))
    hdr(img, "Setelah perang")
    return img


def a_penutup(c):
    cam = se.Kamera(*cam_ll(23.4, 39.1, 0.7))
    img, d = latar_peta(cam)
    se.tint(img, (10, 6, 0), 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    s = back_out((c.t / c.d - 0.15) / 0.12) if c.t / c.d > 0.15 else 0
    if s > 0:
        se.teks(d, (540, 600), "YAUMUL FURQAN", int(100 * s) + 1, EMAS, nama_font="judul", stroke=8, stroke_warna=(0, 0, 0))
    se.teks(d, (540, 710), "Hari Pembeda", 56, PUTIH, nama_font="caption", stroke=6, stroke_warna=(0, 0, 0), alpha=c.p(0.3, 0.38))
    se.teks(d, (540, 780), "QS Al-Anfal: 41", 34, (220, 210, 180), nama_font="ui", stroke=4, stroke_warna=(0, 0, 0), alpha=c.p(0.32, 0.4))
    a = c.p(0.6, 0.68)
    if a > 0:
        lap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lap)
        sk = back_out((c.t / c.d - 0.6) / 0.1)
        w2 = 380 * sk
        dl.rounded_rectangle((540 - w2, 950, 540 + w2, 1080), 40, fill=(200, 52, 44, 245))
        dl.text((540, 1015), "NGOMONGIN SEJARAH", font=se.font("caption", int(56 * sk) + 1), fill=PUTIH, anchor="mm")
        dl.text((540, 1150), "Follow buat cerita berikutnya", font=se.font("ui", 42), fill=PUTIH, anchor="mm",
                stroke_width=4, stroke_fill=(0, 0, 0))
        se.tempel(img, lap, a)
    return img


ADEGAN = [
    Adegan("hook", "Tiga ratus tiga belas orang. Cuma dua ekor kuda. Ngelawan seribu pasukan bersenjata lengkap. "
                   "Siapa yang menang?", a_hook, transisi=False),
    Adegan("kafilah", "Tahun dua Hijriah. Kafilah dagang Quraisy pimpinan Abu Sufyan pulang dari Syam, bawa seribu unta "
                      "penuh harta. Rasulullah dan para sahabat keluar dari Madinah buat menghadangnya.", a_kafilah),
    Adegan("lolos", "Tapi Abu Sufyan cerdik. Dia kirim utusan minta bantuan ke Mekkah, lalu belok lewat jalur pantai. "
                    "Kafilahnya lolos.", a_lolos, transisi=False),
    Adegan("quraisy", "Harusnya selesai, kan? Tapi Abu Jahal ngotot. Seribu pasukan Quraisy tetap berangkat ke Badar.",
           a_quraisy, transisi=False),
    Adegan("musyawarah", "Rasulullah pun bermusyawarah. Dan kaum Anshar menjawab, seandainya engkau ajak kami "
                         "menyeberangi lautan, kami pasti ikut!", a_musyawarah, transisi=False),
    Adegan("sumur", "Sampai di Badar, atas usul Hubab bin Mundzir, kaum Muslimin menguasai sumur air. "
                    "Malamnya, hujan turun. Dan Rasulullah berdoa semalaman.", a_sumur),
    Adegan("duel", "Tujuh belas Ramadhan. Perang dibuka dengan duel. Hamzah, Ali, dan Ubaidah, melawan Utbah, "
                   "Syaibah, dan Walid. Pihak Muslim menang.", a_duel),
    Adegan("perang", "Perang pun pecah. Pasukan kecil itu bertahan, sampai Quraisy kocar-kacir. Abu Jahal sendiri, "
                     "jatuh di tangan dua pemuda Anshar.", a_perang),
    Adegan("hasil", "Hasilnya, tujuh puluh orang Quraisy tewas, tujuh puluh jadi tawanan. Empat belas sahabat gugur "
                    "sebagai syahid.", a_hasil),
    Adegan("tawanan", "Uniknya, tawanan yang bisa baca tulis boleh bebas, asal mau ngajarin sepuluh anak Madinah.",
           a_tawanan),
    Adegan("penutup", "Karena itu, Al-Qur'an menyebut hari ini Yaumul Furqan. Hari pembeda. Follow Ngomongin Sejarah "
                      "buat cerita berikutnya!", a_penutup),
]
