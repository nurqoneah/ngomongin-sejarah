"""Shorts ±88 detik: De Javasche Bank — bank sentral kita dulu milik pemegang saham Belanda, lalu DIBELI (1951–1953).

Tren: "BI Rate" ramai di Google Trends Indonesia (RDG Bank Indonesia November 2026).
Visual: gedung bank + bendera Belanda + uang gulden beterbangan, peta Jawa → Batavia, cabang Semarang & Surabaya,
1942 ditutup Jepang, uang merah vs uang putih, KMB 1949 + diagram saham, Syafruddin Prawiranegara (kartu nama),
panitia nasionalisasi (ambil paksa dicoret), sertifikat saham terbang Amsterdam → Jakarta + 99,4%,
1 Juli 1953 papan nama berganti Bank Indonesia, penutup maskot.
Waktu animasi di dalam adegan pakai fraksi durasi: ctx.p(0.2, 0.5).
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

import peta_data as pd
import shorts_engine as se
from shorts_engine import MERAH, PUTIH, TINTA, W, H, Adegan, Peta, back_out, clamp, lerp

NAMA_FILE = "de-javasche-bank-dibeli-shorts"
SUARA = "id-ID-ArdiNeural"
KECEPATAN = "+15%"
NADA = "-2Hz"
JUDUL = "BANK SENTRAL KITA"

MASKOT = Path(__file__).resolve().parents[3] / "branding" / "maskot.png"
KUNING = (255, 214, 10)
GELAP = (10, 10, 20)
KREM = (247, 236, 208)
KREM_LABEL = (240, 225, 190)
EMAS = (235, 185, 50)
HIJAU_TUA = (30, 110, 60)
BIRU = (30, 80, 150)
COKLAT = (120, 80, 40)
ORANYE = (230, 120, 30)
MERAH_TUA = (150, 30, 25)
NL_MERAH = (174, 28, 40)
NL_BIRU = (33, 70, 139)
GULDEN = (200, 175, 120)

# ------------------------------------------------------------------ pengaman PIL
# Bentuk yang sangat kecil (saat animasi skala muncul) bisa bikin rounded_rectangle/ellipse error karena
# koordinat float terbalik. Normalisasi kotak + kecilkan radius supaya selalu valid.

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
_ps_asli = ImageDraw.ImageDraw.pieslice


def _rr_aman(self, xy, radius=0, *args, **kw):
    b = _kotak(xy)
    r = int(min(radius, (b[2] - b[0]) // 2 - 1, (b[3] - b[1]) // 2 - 1))
    if r < 1:
        return self.rectangle(b, kw.get("fill", args[0] if args else None), kw.get("outline"), kw.get("width", 1))
    return _rr_asli(self, b, r, *args, **kw)


def _el_aman(self, xy, *args, **kw):
    return _el_asli(self, _kotak(xy), *args, **kw)


def _ps_aman(self, xy, *args, **kw):
    return _ps_asli(self, _kotak(xy), *args, **kw)


ImageDraw.ImageDraw.rounded_rectangle = _rr_aman
ImageDraw.ImageDraw.ellipse = _el_aman
ImageDraw.ImageDraw.pieslice = _ps_aman

# ------------------------------------------------------------------ peta

print("  menyiapkan peta Jawa...")
JAWA = Peta(103.5, 116.5, -18, 4, 100, [], [(-7.2, 107.6, 0.35), (-7.0, 110.4, 0.4), (-7.9, 112.9, 0.35),
                                              (-0.5, 101.0, 0.5), (-2, 114, 1.0)],
            seed=33, darat=pd.SEMUA)

BATAVIA = (-6.13, 106.81)
SEMARANG = (-6.97, 110.42)
SURABAYA = (-7.25, 112.75)

print("  menyiapkan latar...")
LATAR = se.latar_tekstur(W, H, 33, warna=(222, 200, 155)).convert("RGBA")
LATAR_GELAP = LATAR.copy()
se.tint(LATAR_GELAP, (8, 12, 24), 0.64)


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


def stempel(img, isi, cx, cy, s, uk=76, sudut=-8, warna=(210, 30, 30)):
    if s <= 0.01:
        return
    f = se.font("caption", uk)
    lw = int(f.getlength(isi)) + 80
    lap = Image.new("RGBA", (lw, uk + 90), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lap)
    dl.rounded_rectangle((10, 10, lw - 10, uk + 80), 22, fill=(247, 236, 208, 210), outline=tuple(warna) + (255,),
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
    d.rounded_rectangle((cx - w / 2 + 8, cy - h / 2 + 10, cx + w / 2 + 8, cy + h / 2 + 10), int(18 * s), fill=(0, 0, 0, 100))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(18 * s), fill=(250, 245, 235, 255),
                        outline=(80, 60, 40, 255), width=4)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 84 * s), int(18 * s), fill=MERAH + (255,))
    d.text((cx, cy - h / 2 + 43 * s), bulan, font=se.font("ui", int(32 * s)), fill=PUTIH, anchor="mm")
    d.text((cx, cy + 20 * s), tgl, font=se.font("caption", int(120 * s)), fill=TINTA, anchor="mm")
    if tahun:
        d.text((cx, cy + h / 2 - 34 * s), tahun, font=se.font("ui", int(34 * s)), fill=(150, 30, 25), anchor="mm")
    se.tempel(img, lap, alpha)


def bendera_nl(d, x, y, s=1.0, t=0.0, alpha=1.0, warna=None):
    """Bendera di tiang; (x, y) = pangkal tiang. warna: daftar warna garis (default Belanda)."""
    a = int(255 * alpha)
    warna = warna or [NL_MERAH, PUTIH, NL_BIRU]
    tinggi = 200 * s
    d.line((x, y, x, y - tinggi), fill=(60, 50, 40, a), width=max(3, int(7 * s)))
    bw, bh = 150 * s, 96 * s
    n = len(warna)
    for i, w in enumerate(warna):
        pts = []
        for k in range(11):
            f = k / 10
            px = x + f * bw
            gel = math.sin(f * 5 + t * 6) * 8 * s * f
            pts.append((px, y - tinggi + i * bh / n + gel))
        for k in range(10, -1, -1):
            f = k / 10
            px = x + f * bw
            gel = math.sin(f * 5 + t * 6) * 8 * s * f
            pts.append((px, y - tinggi + (i + 1) * bh / n + gel))
        d.polygon(pts, fill=tuple(w) + (a,))


def gedung(img, cx, by, s=1.0, papan="DE JAVASCHE BANK", alpha=1.0, terang=1.0):
    """Fasad gedung bank bergaya kolonial (ilustrasi). (cx, by) = dasar tengah."""
    if alpha <= 0.01 or s <= 0.05:
        return (cx, by)
    gw, gh = int(760 * s), int(470 * s)
    lap = Image.new("RGBA", (gw + 40, gh + 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    ox, oy = 20, 170
    dinding = tuple(int(v * terang) for v in (238, 228, 205))
    gar = (80, 60, 40, 255)
    d.rectangle((ox + 10, oy + 14, ox + gw + 10, oy + gh + 14), fill=(0, 0, 0, 90))
    d.rectangle((ox, oy, ox + gw, oy + gh), fill=dinding + (255,), outline=gar, width=6)
    # atap segitiga + kubah kecil
    d.polygon([(ox - 20, oy), (ox + gw / 2, oy - 150 * s), (ox + gw + 20, oy)], fill=(190, 80, 55, 255), outline=gar)
    d.ellipse((ox + gw / 2 - 40 * s, oy - 200 * s, ox + gw / 2 + 40 * s, oy - 120 * s), fill=(150, 160, 150, 255),
              outline=gar, width=4)
    # papan nama
    d.rectangle((ox + 60 * s, oy + 22 * s, ox + gw - 60 * s, oy + 88 * s), fill=(40, 40, 50, 255))
    f = se.font("caption", int(44 * s))
    d.text((ox + gw / 2, oy + 56 * s), papan, font=f, fill=(245, 215, 130), anchor="mm")
    # kolom + jendela
    for k in range(6):
        x = ox + 70 * s + k * (gw - 140 * s) / 5
        d.rectangle((x - 18 * s, oy + 110 * s, x + 18 * s, oy + gh - 10), fill=(250, 245, 230, 255), outline=gar, width=3)
    for k in range(5):
        x = ox + 70 * s + (k + 0.5) * (gw - 140 * s) / 5
        d.rounded_rectangle((x - 30 * s, oy + 150 * s, x + 30 * s, oy + 280 * s), int(28 * s),
                            fill=(255, 210, 120, 230) if terang > 0.8 else (90, 80, 70, 255), outline=gar, width=3)
    # pintu + tangga
    d.rounded_rectangle((ox + gw / 2 - 48 * s, oy + gh - 150 * s, ox + gw / 2 + 48 * s, oy + gh), int(40 * s),
                        fill=(90, 55, 30, 255), outline=gar, width=4)
    for k in range(3):
        d.rectangle((ox - 10 + k * 15, oy + gh + k * 12 * s, ox + gw + 10 - k * 15, oy + gh + (k + 1) * 12 * s),
                    fill=(200, 190, 170, 255), outline=gar, width=2)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(by - oy - gh)))
    return (cx + gw / 2 - 100 * s, by - gh - 150 * s * 0.4)  # pangkal tiang bendera di atap kanan


def uang(img, cx, cy, s=1.0, isi="10", sub="GULDEN", warna=GULDEN, sudut=0.0, alpha=1.0, tinta=(80, 50, 25)):
    """Uang kertas ilustrasi (bukan replika)."""
    if alpha <= 0.01 or s <= 0.05:
        return
    uw, uh = int(330 * s), int(170 * s)
    lap = Image.new("RGBA", (uw + 20, uh + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rounded_rectangle((10, 10, uw + 10, uh + 10), int(12 * s), fill=tuple(warna) + (255,), outline=tinta + (255,),
                        width=max(2, int(5 * s)))
    m = int(14 * s)
    d.rectangle((10 + m, 10 + m, uw + 10 - m, uh + 10 - m), outline=tinta + (150,), width=max(1, int(3 * s)))
    d.ellipse((10 + 28 * s, 10 + 35 * s, 10 + 128 * s, 10 + 135 * s), outline=tinta + (200,), width=max(1, int(4 * s)))
    d.text((10 + 78 * s, 10 + 85 * s), isi, font=se.font("caption", int(54 * s)), fill=tinta, anchor="mm")
    d.text((10 + 230 * s, 10 + 70 * s), sub, font=se.font("ui", int(30 * s)), fill=tinta, anchor="mm")
    d.text((10 + 230 * s, 10 + 115 * s), isi, font=se.font("caption", int(44 * s)), fill=tinta, anchor="mm")
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def hujan_uang(img, t, n=14, seed=1, y0=380, y1=1320, alpha=1.0, s=0.55):
    rng = random.Random(seed)
    for i in range(n):
        fase = (rng.random() + t * rng.uniform(0.12, 0.22)) % 1
        x = rng.uniform(60, 1020) + math.sin(fase * 6 + i) * 40
        y = lerp(y0, y1, fase)
        uang(img, x, y, s * rng.uniform(0.8, 1.15), "10", "GULDEN", sudut=math.sin(t * 2 + i) * 30 + rng.uniform(-40, 40),
             alpha=alpha * (1 - fase * 0.5))


def sertifikat(img, cx, cy, s=1.0, sudut=0.0, alpha=1.0):
    """Sertifikat saham ilustrasi."""
    if alpha <= 0.01 or s <= 0.05:
        return
    sw, sh = int(260 * s), int(180 * s)
    lap = Image.new("RGBA", (sw + 20, sh + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    d.rectangle((10, 10, sw + 10, sh + 10), fill=(250, 243, 222, 255), outline=(120, 80, 30, 255), width=max(2, int(5 * s)))
    d.rectangle((10 + 12 * s, 10 + 12 * s, sw + 10 - 12 * s, sh + 10 - 12 * s), outline=(180, 130, 50, 255),
                width=max(1, int(3 * s)))
    d.text((10 + sw / 2, 10 + 50 * s), "AANDEEL", font=se.font("caption", int(40 * s)), fill=(110, 50, 20), anchor="mm")
    d.text((10 + sw / 2, 10 + 95 * s), "saham DJB", font=se.font("ui", int(26 * s)), fill=(110, 80, 40), anchor="mm")
    d.ellipse((10 + sw / 2 - 22 * s, 10 + 120 * s, 10 + sw / 2 + 22 * s, 10 + 164 * s), fill=(190, 40, 30, 255))
    if sudut:
        lap = lap.rotate(sudut, Image.BICUBIC, expand=True)
    se.tempel(img, lap, alpha, (int(cx - lap.width / 2), int(cy - lap.height / 2)))


def pie(d, cx, cy, r, frak, warna, sisa=(120, 120, 130), alpha=1.0, label_tengah=None):
    a = int(255 * alpha)
    d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=(40, 30, 20, a))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tuple(sisa) + (a,))
    if frak > 0:
        d.pieslice((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * frak, fill=tuple(warna) + (a,))


def senapan(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    c = (60, 45, 35, a)
    d.polygon([(x - 160 * s, y + 10 * s), (x - 60 * s, y - 14 * s), (x + 150 * s, y - 14 * s), (x + 150 * s, y),
               (x - 40 * s, y + 4 * s), (x - 150 * s, y + 50 * s)], fill=c)
    d.rectangle((x + 150 * s, y - 10 * s, x + 220 * s, y - 2 * s), fill=(90, 90, 95, a))


def coret_besar(d, box, k, alpha=1.0):
    if k <= 0:
        return
    x0, y0, x1, y1 = box
    a = int(255 * alpha)
    k1, k2 = clamp(k * 2), clamp(k * 2 - 1)
    d.line((x0, y0, lerp(x0, x1, k1), lerp(y0, y1, k1)), fill=(220, 30, 25, a), width=18)
    if k2 > 0:
        d.line((x1, y0, lerp(x1, x0, k2), lerp(y0, y1, k2)), fill=(220, 30, 25, a), width=18)


def orang(d, x, y, s=1.0, warna=(60, 45, 35), alpha=1.0):
    """Siluet orang sederhana tanpa wajah."""
    a = int(255 * alpha)
    c = tuple(warna) + (a,)
    d.ellipse((x - 9 * s, y - 50 * s, x + 9 * s, y - 32 * s), fill=c)
    d.rounded_rectangle((x - 12 * s, y - 30 * s, x + 12 * s, y), int(6 * s) + 1, fill=c)


# ------------------------------------------------------------------ adegan

def a_hook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 1000, 560, (200, 150, 50), 1.1)
    hujan_uang(img, c.t + 3, n=12, seed=2, y0=620, y1=1330, alpha=0.95)
    tiang = gedung(img, 540, 1290, 0.95)
    d = ImageDraw.Draw(img, "RGBA")
    bendera_nl(d, tiang[0], tiang[1], 1.1, c.t)
    se.teks(d, (540, 410), "BANK SENTRAL KITA", 86, PUTIH, nama_font="caption", stroke=11, stroke_warna=GELAP)
    se.teks(d, (540, 530), "MILIK BELANDA?!", 110, KUNING, nama_font="caption", stroke=11, stroke_warna=GELAP)
    stempel(img, "BATAVIA, 1828", 240, 1240, 0.7, uk=56, sudut=8)
    se.kartu(img, 540, 1345, "Lagi rame: BI Rate", "suku bunga acuan", HIJAU_TUA,
             alpha=c.p(0.16, 0.24), tiang=False, skala=skala_muncul(c, 0.16))
    a = c.p(0.68, 0.75)
    if a > 0:
        se.panel(img, (90, 640, 990, 880), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 715), "Cara kita ngambil alihnya…", 52, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 800), "BUKAN pakai senjata", 50, TINTA, nama_font="caption", alpha=c.p(0.8, 0.86))
    return img


def a_berdiri(c):
    kamera = se.kamera_antara(cam(JAWA, -7.3, 108.8, 0.9), cam(JAWA, -6.6, 107.2, 1.7), c.p(0.0, 0.45))
    img = se.render_peta(JAWA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    bx, by = layar(JAWA, kamera, BATAVIA)
    a = c.p(0.12, 0.22)
    if a > 0:
        se.glow(img, bx, by, 110, (255, 200, 80), 1.4 * a)
        d = ImageDraw.Draw(img, "RGBA")
        r = 16 + 4 * math.sin(c.t * 5)
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=(255, 200, 60, int(255 * a)), outline=PUTIH + (int(255 * a),),
                  width=4)
        label(d, (bx + 20, by + 50), "Batavia", 44, alpha=a)
    se.kartu(img, bx + 60, by - 30, "De Javasche Bank", "berdiri 24 Januari 1828", NL_BIRU, alpha=c.p(0.25, 0.33),
             skala=skala_muncul(c, 0.25))
    stempel(img, "BANK SWASTA", 800, 560, skala_muncul(c, 0.42, 0.08) * 0.75, uk=64, sudut=-7)
    a = c.p(0.62, 0.7)
    if a > 0:
        se.panel(img, (150, 960, 930, 1320), alpha=a)
        uang(img, 540, 1110, 1.25 * skala_muncul(c, 0.62), "10", "GULDEN", sudut=-4, alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1265), "hak istimewa: cetak uang", 46, (170, 30, 20), nama_font="caption", alpha=c.p(0.7, 0.76))
    hdr(img, "Batavia, 1828")
    return img


def a_cabang(c):
    kamera = se.kamera_antara(cam(JAWA, -7.0, 109.0, 0.95), cam(JAWA, -7.0, 109.6, 1.0), c.p(0.0, 1.0))
    img = se.render_peta(JAWA, kamera)
    d = ImageDraw.Draw(img, "RGBA")
    kota = [(BATAVIA, "Batavia"), (SEMARANG, "Semarang"), (SURABAYA, "Surabaya")]
    pts = [layar(JAWA, kamera, k) for k, _ in kota]
    se.garis_putus(d, pts, c.p(0.05, 0.4), MERAH, tebal=7)
    for i, ((ll, nama), (x, y)) in enumerate(zip(kota, pts)):
        a = 1.0 if i == 0 else c.p(0.12 + i * 0.12, 0.2 + i * 0.12)
        if a <= 0:
            continue
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(255, 200, 60, int(255 * a)), outline=PUTIH + (int(255 * a),), width=4)
        label(d, (x, y + 52), nama, 40, alpha=a)
    se.kartu(img, 760, 520, "Cabang baru, 1829", "Semarang & Surabaya", NL_BIRU, alpha=c.p(0.3, 0.38), tiang=False,
             skala=skala_muncul(c, 0.3))
    a = c.p(0.45, 0.52)
    if a > 0:
        hujan_uang(img, c.t, n=10, seed=5, y0=650, y1=1330, alpha=a, s=0.5)
        d = ImageDraw.Draw(img, "RGBA")
        se.panel(img, (170, 1040, 910, 1320), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1120), "1828  →  1942", 76, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 1225), "lebih dari 100 tahun", 48, TINTA, nama_font="caption", alpha=c.p(0.55, 0.62))
    hdr(img, "Pabrik uang Hindia Belanda")
    return img


def a_perang(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    f2 = c.p(0.4, 0.47)
    a1 = 1 - f2
    if a1 > 0.01:
        gedung(img, 540, 1060, 0.85, alpha=a1, terang=0.6)
        d = ImageDraw.Draw(img, "RGBA")
        # matahari merah (bendera Jepang)
        r = 70
        d.rectangle((760, 500, 960, 630), fill=(250, 250, 250, int(255 * a1)), outline=(60, 60, 60, int(255 * a1)), width=3)
        d.ellipse((860 - 40, 565 - 40, 860 + 40, 565 + 40), fill=(200, 20, 30, int(255 * a1)))
        kalender(img, 230, 560, "MARET", "1942", "", a1 * c.p(0.0, 0.06), 0.62)
        stempel(img, "DITUTUP", 540, 930, skala_muncul(c, 0.12, 0.08) * (1.0 if a1 > 0.5 else 0.0), uk=96, sudut=-10)
        se.kartu(img, 540, 1300, "Diduduki Jepang", "bank Belanda ditutup", MERAH, alpha=a1 * c.p(0.08, 0.14),
                 tiang=False, skala=skala_muncul(c, 0.08))
    if f2 > 0:
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 440), "1945: Belanda balik lagi", 56, PUTIH, nama_font="caption", stroke=6, stroke_warna=GELAP,
                alpha=f2)
        uang(img, 290, 760, 1.05 * skala_muncul(c, 0.5), "5", "DJB / NICA", warna=(205, 80, 70), sudut=-8,
             alpha=c.p(0.5, 0.56), tinta=(70, 15, 10))
        uang(img, 790, 760, 1.05 * skala_muncul(c, 0.62), "5", "ORI", warna=(245, 242, 232), sudut=7,
             alpha=c.p(0.62, 0.68), tinta=(40, 40, 50))
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 770), "VS", 90, KUNING, nama_font="caption", stroke=8, stroke_warna=GELAP, alpha=c.p(0.6, 0.65))
        se.teks(d, (290, 930), "uang merah", 54, (255, 140, 120), nama_font="caption", stroke=6, stroke_warna=GELAP,
                alpha=c.p(0.55, 0.6))
        se.teks(d, (790, 930), "uang putih", 54, PUTIH, nama_font="caption", stroke=6, stroke_warna=GELAP,
                alpha=c.p(0.66, 0.72))
        se.kartu(img, 540, 1180, "ORI = uang Republik", "lahir 1946", HIJAU_TUA, alpha=c.p(0.78, 0.84), tiang=False,
                 skala=skala_muncul(c, 0.78))
    hdr(img, "Perang & revolusi")
    return img


def a_rehook(c):
    img = LATAR_GELAP.copy()
    se.glow(img, 540, 1000, 420, (60, 90, 170), 1.0)
    se.panel(img, (90, 410, 990, 640), alpha=c.p(0.0, 0.08))
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 480), "TAPI BAGIAN PALING ANEH…", 54, (170, 30, 20), nama_font="caption", alpha=c.p(0.0, 0.08))
    se.teks(d, (540, 570), "KMB 1949: kedaulatan diakui", 44, TINTA, nama_font="caption", alpha=c.p(0.1, 0.18))
    a = c.p(0.3, 0.38)
    if a > 0:
        tiang = gedung(img, 330, 1130, 0.55 * skala_muncul(c, 0.3), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        bendera_nl(d, tiang[0], tiang[1], 0.7, c.t, a)
        se.kartu(img, 330, 1250, "Bank sentral RI?", "tetap De Javasche Bank", NL_BIRU, alpha=c.p(0.38, 0.45),
                 tiang=False, skala=skala_muncul(c, 0.38))
    a2 = c.p(0.6, 0.68)
    if a2 > 0:
        pie(d, 800, 960, 160 * skala_muncul(c, 0.6), 1.0, ORANYE, alpha=a2)
        se.teks(d, (800, 960), "SAHAM", 46, PUTIH, nama_font="caption", stroke=5, stroke_warna=GELAP, alpha=a2)
        se.kartu(img, 800, 1250, "Pemegang saham:", "orang Belanda", ORANYE, alpha=c.p(0.68, 0.75), tiang=False,
                 skala=skala_muncul(c, 0.68))
    hdr(img, "Konferensi Meja Bundar, 1949")
    return img


def a_syafruddin(c):
    img = LATAR.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # deretan presiden sebelumnya: siluet abu-abu
    for i in range(7):
        a = c.p(0.0 + i * 0.03, 0.06 + i * 0.03)
        orang(d, 140 + i * 133, 640, 2.2, (110, 105, 100), a * 0.9)
    se.teks(d, (540, 450), "Presiden bank sebelumnya:", 46, TINTA, nama_font="caption", alpha=c.p(0.0, 0.06))
    se.teks(d, (540, 700), "semuanya orang Belanda", 44, NL_MERAH, nama_font="caption", stroke=4, stroke_warna=KREM,
            alpha=c.p(0.12, 0.18))
    a = c.p(0.32, 0.4)
    if a > 0:
        se.glow(img, 540, 960, 260, (255, 210, 90), 1.2 * a)
        d = ImageDraw.Draw(img, "RGBA")
        orang(d, 540, 1010, 4.0, (40, 30, 25), a)
        bendera_nl(d, 640, 1010, 0.9, c.t, a, warna=[(210, 30, 35), PUTIH])
        se.kartu(img, 540, 1110, "Syafruddin Prawiranegara", "Presiden DJB, mulai 15 Juli 1951", MERAH, alpha=a,
                 tiang=False, skala=skala_muncul(c, 0.32))
    stempel(img, "SATU-SATUNYA", 540, 1290, skala_muncul(c, 0.62, 0.08) * 0.85, uk=72, sudut=-6)
    hdr(img, "1951: mulai bergerak")
    return img


def a_panitia(c):
    img = LATAR.copy()
    se.kartu(img, 540, 470, "Panitia Nasionalisasi", "dibentuk 2 Juli 1951", HIJAU_TUA, alpha=c.p(0.0, 0.08),
             tiang=False, skala=skala_muncul(c, 0.0))
    d = ImageDraw.Draw(img, "RGBA")
    a = c.p(0.28, 0.36)
    if a > 0:
        se.panel(img, (120, 640, 960, 1060), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 720), "Opsi gampang:", 46, TINTA, nama_font="judul", alpha=a)
        se.teks(d, (540, 800), "AMBIL PAKSA", 84, (170, 30, 20), nama_font="caption", alpha=a)
        senapan(d, 520, 940, 1.3, a)
        coret_besar(d, (180, 680, 900, 1020), c.p(0.62, 0.78), a)
    a2 = c.p(0.8, 0.86)
    if a2 > 0:
        se.teks(d, (540, 1200), "Terus… gimana?", 80, KUNING, nama_font="caption", stroke=9, stroke_warna=GELAP, alpha=a2)
    hdr(img, "Jakarta, 1951")
    return img


def a_dibeli(c):
    img = LATAR_GELAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    se.teks(d, (540, 425), "JAWABANNYA:", 58, PUTIH, nama_font="caption", stroke=7, stroke_warna=GELAP,
            alpha=c.p(0.0, 0.04))
    se.teks(d, (540, 525), "DIBELI!", 130, KUNING, nama_font="caption", stroke=11, stroke_warna=GELAP,
            alpha=c.p(0.02, 0.07))
    f2 = c.p(0.5, 0.56)
    a1 = 1 - f2
    if a1 > 0.01:
        # fase 1: tawaran +20% dan sertifikat terbang Amsterdam → Jakarta
        se.kartu(img, 220, 720, "Amsterdam", "pedagang saham", ORANYE, alpha=a1 * c.p(0.2, 0.26), tiang=False,
                 skala=skala_muncul(c, 0.2))
        se.kartu(img, 860, 720, "Jakarta", "pemerintah RI", MERAH, alpha=a1 * c.p(0.08, 0.14), tiang=False,
                 skala=skala_muncul(c, 0.08))
        se.teks(d, (540, 900), "+20%", 120, (120, 230, 120), nama_font="caption", stroke=9, stroke_warna=GELAP,
                alpha=a1 * c.p(0.1, 0.16))
        se.teks(d, (540, 990), "di atas harga normal", 42, PUTIH, nama_font="caption", stroke=5, stroke_warna=GELAP,
                alpha=a1 * c.p(0.12, 0.18))
        k = c.p(0.24, 0.5)
        if k > 0:
            rng = random.Random(9)
            for i in range(9):
                f = clamp((k * 1.6 - i * 0.07))
                if f <= 0 or f >= 1:
                    continue
                x = lerp(240, 850, f)
                y = 1180 - math.sin(f * math.pi) * 130 + rng.uniform(-30, 30)
                sertifikat(img, x, y, 0.62, math.sin(f * 6 + i) * 18, a1)
    if f2 > 0:
        k = c.p(0.54, 0.74)
        d = ImageDraw.Draw(img, "RGBA")
        pie(d, 540, 900, 230, 0.994 * k, (210, 30, 35), sisa=(110, 110, 120), alpha=f2)
        d.pieslice((540 - 230, 900 - 230, 540 + 230, 900 + 230), -90, -90 + 360 * 0.994 * k, outline=PUTIH + (int(255 * f2),),
                   width=4)
        nilai = 99.4 * k
        se.teks(d, (540, 900), f"{nilai:.1f}%".replace(".", ","), 120, PUTIH, nama_font="caption", stroke=10,
                stroke_warna=GELAP, alpha=f2)
        se.teks(d, (540, 1180), "saham DJB terbeli", 52, PUTIH, nama_font="caption", stroke=6, stroke_warna=GELAP,
                alpha=c.p(0.6, 0.66))
        stempel(img, "MILIK NEGARA · 15 DES 1951", 540, 1310, skala_muncul(c, 0.82, 0.08) * 0.62, uk=60, sudut=-5)
    hdr(img, "Agustus–Desember 1951")
    return img


def a_bi(c):
    img = LATAR.copy()
    ganti = c.p(0.08, 0.2)
    papan = "BANK INDONESIA" if ganti > 0.5 else "DE JAVASCHE BANK"
    tiang = gedung(img, 540, 1020, 0.9, papan=papan)
    d = ImageDraw.Draw(img, "RGBA")
    if ganti < 0.5:
        bendera_nl(d, tiang[0], tiang[1], 1.0, c.t)
    else:
        bendera_nl(d, tiang[0], tiang[1], 1.0, c.t, warna=[(210, 30, 35), PUTIH])
    if 0.3 < ganti < 0.7:
        se.glow(img, 540, 690, 300, (255, 230, 140), 2.0)
    kalender(img, 190, 520, "JULI", "1", "1953", c.p(0.0, 0.06), 0.62)
    a = c.p(0.36, 0.44) * (1 - c.p(0.62, 0.68))
    if a > 0:
        se.kartu(img, 540, 1150, "Gedungnya di Kota Tua", "kini: Museum Bank Indonesia", COKLAT, alpha=a, tiang=False,
                 skala=skala_muncul(c, 0.36))
    a2 = c.p(0.66, 0.72)
    if a2 > 0:
        se.panel(img, (150, 1070, 930, 1320), alpha=a2)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 1140), "Yang nentuin", 44, TINTA, nama_font="judul", alpha=a2)
        naik = math.sin(c.t * 4) * 10
        se.teks(d, (540, 1235), "BI RATE", 84, (170, 30, 20), nama_font="caption", alpha=a2)
        se.teks(d, (790, 1225 + naik), "▲", 50, HIJAU_TUA, nama_font="ui", alpha=a2)
        se.teks(d, (290, 1235 - naik), "▼", 50, MERAH_TUA, nama_font="ui", alpha=a2)
    hdr(img, "Lahirnya Bank Indonesia")
    return img


_MASKOT = None


def maskot():
    global _MASKOT
    if _MASKOT is None and MASKOT.exists():
        m = Image.open(MASKOT).convert("RGBA").crop((140, 90, 940, 870))
        _MASKOT = m.resize((380, int(380 * m.height / m.width)), Image.LANCZOS)
    return _MASKOT


def a_penutup(c):
    kamera = se.kamera_antara(cam(JAWA, -6.4, 106.9, 2.4), cam(JAWA, -6.25, 106.82, 2.7), c.p(0.0, 1.0))
    img = se.render_peta(JAWA, kamera)
    bx, by = layar(JAWA, kamera, BATAVIA)
    se.glow(img, bx, by, 120, (255, 200, 80), 1.2)
    se.tint(img, (10, 6, 0), 0.2 + 0.4 * c.p(0.58, 0.66))
    a = c.p(0.02, 0.1) * (1 - c.p(0.54, 0.58))
    if a > 0:
        se.panel(img, (90, 420, 990, 720), alpha=a)
        d = ImageDraw.Draw(img, "RGBA")
        se.teks(d, (540, 495), "Kedaulatan nggak selalu", 52, (170, 30, 20), nama_font="caption", alpha=a)
        se.teks(d, (540, 580), "direbut pakai senjata.", 46, TINTA, nama_font="judul", alpha=c.p(0.12, 0.18) * a)
        se.teks(d, (540, 655), "Kadang, dibeli lewat saham.", 46, TINTA, nama_font="judul", alpha=c.p(0.28, 0.34) * a)
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
    Adegan("hook", "Bank sentral kita dulu milik Belanda. Lagi rame soal BI Rate? Lembaga penentu bunga itu, dulu sahamnya dipegang Belanda. Dan cara kita ngambil alihnya, bukan pakai senjata.",
           a_hook, transisi=False),
    Adegan("berdiri", "Batavia, tahun delapan belas dua puluh delapan. Berdiri De Javasche Bank, bank swasta. Tapi punya hak istimewa: mencetak uang gulden Hindia Belanda.",
           a_berdiri),
    Adegan("cabang", "Setahun kemudian, cabangnya buka di Semarang dan Surabaya. Lebih dari seratus tahun, bank ini jadi pabrik uang Hindia Belanda.",
           a_cabang),
    Adegan("perang", "Tahun empat puluh dua, Jepang datang dan menutupnya. Kita merdeka, Belanda balik, bank ini buka lagi. Uangnya disebut uang merah, lawan uang putih, ORI.",
           a_perang),
    Adegan("rehook", "Tapi bagian paling aneh: tahun empat sembilan, kedaulatan kita diakui. Bank sentralnya? Tetap De Javasche Bank. Sahamnya masih punya Belanda.",
           a_rehook),
    Adegan("syafruddin", "Tahun lima puluh satu, pemerintah bergerak. Syafruddin Prawiranegara diangkat jadi presiden bank ini, satu-satunya orang Indonesia yang pernah memimpinnya.",
           a_syafruddin),
    Adegan("panitia", "Lalu dibentuk panitia nasionalisasi. Jalan paling gampang: ambil paksa. Tapi itu justru nggak dipilih.",
           a_panitia),
    Adegan("dibeli", "Jawabannya: dibeli! Pemerintah menawar sahamnya dua puluh persen di atas harga normal, sampai melobi pedagang saham di Amsterdam. Hasilnya, sembilan puluh sembilan koma empat persen saham terbeli.",
           a_dibeli),
    Adegan("bi", "Satu Juli lima puluh tiga, namanya berganti jadi Bank Indonesia. Gedung lamanya di Kota Tua kini jadi museum. Dan lembaga inilah yang sekarang nentuin BI Rate.",
           a_bi),
    Adegan("penutup", "Kedaulatan nggak selalu direbut pakai senjata. Kadang, dibeli lewat saham. Follow Ngomongin Sejarah buat cerita berikutnya!",
           a_penutup),
]
