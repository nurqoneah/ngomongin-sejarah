"""Mesin video Shorts 9:16 (1080x1920) gaya animasi peta sejarah.

Dipakai oleh tools/buat_shorts.py. Setiap konten punya file `shorts/adegan.py`
yang berisi daftar adegan (narasi + fungsi gambar).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30

FONT_DIR = "C:/Windows/Fonts/"
FONTS = {
    "tangan": "segoeprb.ttf",   # tulisan tangan, buat label peta
    "tangan_tipis": "segoepr.ttf",
    "judul": "georgiab.ttf",
    "caption": "seguibl.ttf",   # Segoe UI Black
    "ui": "seguisb.ttf",
}

# Palet
PASIR = (214, 188, 138)
TINTA = (43, 30, 18)
HIJAU = (46, 160, 90)
HIJAU_TUA = (20, 90, 50)
MERAH = (200, 52, 44)
MERAH_TUA = (110, 20, 16)
EMAS = (240, 196, 70)
KUNING = (255, 214, 10)
PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)


# ---------------------------------------------------------------- utilitas

@lru_cache(maxsize=None)
def font(nama: str, ukuran: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_DIR + FONTS.get(nama, nama), int(ukuran))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def back_out(t):
    t = clamp(t)
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def prog(t, a, b):
    """Progress 0..1 (eased) antara waktu a..b."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return ease((t - a) / (b - a))


def lerp_rgb(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def noise(h: int, w: int, skala: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    kecil = rng.random((max(2, h // skala + 2), max(2, w // skala + 2))).astype(np.float32)
    img = Image.fromarray((kecil * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32) / 255.0


def fbm(h, w, skala, seed, oktaf=5):
    total = np.zeros((h, w), np.float32)
    amp, norm = 1.0, 0.0
    for i in range(oktaf):
        total += noise(h, w, max(1, skala >> i), seed + i) * amp
        norm += amp
        amp *= 0.5
    return total / norm


# ---------------------------------------------------------------- teks

def teks(draw, xy, isi, ukuran, warna=TINTA, nama_font="tangan", anchor="mm",
         stroke=0, stroke_warna=PUTIH, alpha=1.0):
    if alpha <= 0.01:
        return
    f = font(nama_font, ukuran)
    w = tuple(warna) + (int(255 * alpha),)
    s = tuple(stroke_warna) + (int(255 * alpha),)
    draw.text(xy, isi, font=f, fill=w, anchor=anchor, stroke_width=stroke, stroke_fill=s)


def bungkus(isi: str, f: ImageFont.FreeTypeFont, lebar: int) -> list[str]:
    baris, sekarang = [], ""
    for kata in isi.split():
        coba = (sekarang + " " + kata).strip()
        if f.getlength(coba) <= lebar:
            sekarang = coba
        else:
            if sekarang:
                baris.append(sekarang)
            sekarang = kata
    if sekarang:
        baris.append(sekarang)
    return baris


def tempel(dasar: Image.Image, lapisan: Image.Image, alpha=1.0, pos=(0, 0)):
    if alpha <= 0.01:
        return
    if alpha < 0.999:
        a = lapisan.getchannel("A").point(lambda v: int(v * alpha))
        lapisan = lapisan.copy()
        lapisan.putalpha(a)
    dasar.alpha_composite(lapisan, pos)


# ---------------------------------------------------------------- elemen

def kartu(img, cx, cy, judul, sub="", warna=HIJAU, alpha=1.0, skala=1.0, coret=0.0,
          lebar=None, tiang=True):
    """Kartu nama berbingkai ala papan di peta. coret: 0..1 progres tanda silang."""
    if alpha <= 0.01 or skala <= 0.01:
        return
    fj = font("tangan", 34)
    fs = font("tangan_tipis", 24)
    lw = lebar or int(max(fj.getlength(judul), fs.getlength(sub) if sub else 0) + 56)
    lh = 64 + (34 if sub else 0)
    pad = 30
    lap = Image.new("RGBA", (lw + pad * 2, lh + pad * 2 + (70 if tiang else 0)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    x0, y0 = pad, pad
    d.rounded_rectangle((x0 + 6, y0 + 8, x0 + lw + 6, y0 + lh + 8), 14, fill=(0, 0, 0, 90))
    d.rounded_rectangle((x0, y0, x0 + lw, y0 + lh), 14, fill=(247, 236, 208, 255),
                        outline=tuple(warna) + (255,), width=6)
    d.rectangle((x0 + 6, y0 + 6, x0 + 22, y0 + lh - 6), fill=tuple(warna) + (255,))
    d.text((x0 + lw / 2 + 8, y0 + 36), judul, font=fj, fill=TINTA, anchor="mm")
    if sub:
        d.text((x0 + lw / 2 + 8, y0 + 76), sub, font=fs, fill=(90, 70, 50), anchor="mm")
    if tiang:
        tx = x0 + lw // 2
        d.line((tx, y0 + lh, tx, y0 + lh + 60), fill=(70, 50, 30, 255), width=6)
        d.ellipse((tx - 9, y0 + lh + 52, tx + 9, y0 + lh + 70), fill=tuple(warna) + (255,),
                  outline=(40, 30, 20, 255), width=3)
    if coret > 0:
        k = clamp(coret * 2)
        k2 = clamp(coret * 2 - 1)
        a, b = (x0 + 14, y0 + 10), (x0 + lw - 14, y0 + lh - 10)
        d.line((a[0], a[1], lerp(a[0], b[0], k), lerp(a[1], b[1], k)), fill=(190, 20, 20, 255), width=10)
        if k2 > 0:
            c, e = (x0 + lw - 14, y0 + 10), (x0 + 14, y0 + lh - 10)
            d.line((c[0], c[1], lerp(c[0], e[0], k2), lerp(c[1], e[1], k2)), fill=(190, 20, 20, 255), width=10)
    if skala != 1.0:
        lap = lap.resize((max(1, int(lap.width * skala)), max(1, int(lap.height * skala))), Image.BICUBIC)
    # titik jangkar = ujung tiang (kalau ada) atau tengah kartu
    ax = lap.width // 2
    ay = lap.height - int(pad * skala) if tiang else int((pad + lh / 2) * skala)
    tempel(img, lap, alpha, (int(cx - ax), int(cy - ay)))


def panel(img, box, alpha=1.0, warna=(247, 236, 208), garis=(120, 90, 50)):
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + 8, y0 + 12, x1 + 8, y1 + 12), 28, fill=(0, 0, 0, 110))
    d.rounded_rectangle(box, 28, fill=tuple(warna) + (240,), outline=tuple(garis) + (255,), width=5)
    d.rounded_rectangle((x0 + 14, y0 + 14, x1 - 14, y1 - 14), 20, outline=tuple(garis) + (120,), width=2)
    tempel(img, lap, alpha)


def ikon_kabah(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    w = 46 * s
    d.polygon([(x - w / 2, y - w * 0.35), (x, y - w * 0.6), (x + w / 2, y - w * 0.35),
               (x + w / 2, y + w * 0.45), (x, y + w * 0.65), (x - w / 2, y + w * 0.45)],
              fill=(15, 15, 15, a), outline=(255, 255, 255, a))
    d.line((x - w / 2, y - w * 0.12, x, y + w * 0.08, x + w / 2, y - w * 0.12), fill=(230, 180, 60, a), width=max(2, int(6 * s)))
    d.line((x, y - w * 0.6 + w * 0.47, x, y + w * 0.65), fill=(60, 60, 60, a), width=max(1, int(2 * s)))


def ikon_masjid(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    c = (20, 20, 20, a)
    d.rectangle((x - 30 * s, y - 8 * s, x + 30 * s, y + 26 * s), fill=c)
    d.pieslice((x - 22 * s, y - 38 * s, x + 22 * s, y + 6 * s), 180, 360, fill=c)
    d.rectangle((x + 34 * s, y - 50 * s, x + 44 * s, y + 26 * s), fill=c)
    d.polygon([(x + 32 * s, y - 50 * s), (x + 39 * s, y - 66 * s), (x + 46 * s, y - 50 * s)], fill=c)
    d.line((x, y - 38 * s, x, y - 50 * s), fill=c, width=max(2, int(4 * s)))
    d.rectangle((x - 8 * s, y + 6 * s, x + 8 * s, y + 26 * s), fill=(230, 200, 120, a))


def ikon_sumur(d, x, y, s=1.0, alpha=1.0, tutup=0.0):
    a = int(255 * alpha)
    r = 26 * s
    d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=(120, 100, 80, a), outline=(60, 45, 30, a), width=max(2, int(5 * s)))
    if tutup < 1:
        ri = r * 0.62 * (1 - tutup)
        d.ellipse((x - ri, y - ri * 0.7, x + ri, y + ri * 0.7), fill=(40, 90, 140, a))
    if tutup > 0:
        k = clamp(tutup)
        d.line((x - r, y - r, lerp(x - r, x + r, k), lerp(y - r, y + r, k)), fill=(200, 20, 20, a), width=max(3, int(8 * s)))
        d.line((x + r, y - r, lerp(x + r, x - r, k), lerp(y - r, y + r, k)), fill=(200, 20, 20, a), width=max(3, int(8 * s)))


def ikon_unta(d, x, y, s=1.0, warna=(70, 45, 25), alpha=1.0, langkah=0.0):
    """Siluet unta kecil menghadap kanan. langkah: fase animasi kaki."""
    c = tuple(warna) + (int(255 * alpha),)
    ox = math.sin(langkah) * 3 * s
    for kx in (-12, 10):
        d.line((x + kx * s, y + 4 * s, x + kx * s + ox, y + 22 * s), fill=c, width=max(2, int(4 * s)))
        ox = -ox
    d.ellipse((x - 18 * s, y - 10 * s, x + 16 * s, y + 8 * s), fill=c)
    d.ellipse((x - 9 * s, y - 20 * s, x + 7 * s, y - 2 * s), fill=c)
    d.line((x + 12 * s, y - 2 * s, x + 20 * s, y - 18 * s), fill=c, width=max(2, int(6 * s)))
    d.ellipse((x + 16 * s, y - 24 * s, x + 28 * s, y - 15 * s), fill=c)


def ikon_tenda(d, x, y, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    d.polygon([(x - 34 * s, y + 20 * s), (x, y - 30 * s), (x + 34 * s, y + 20 * s)], fill=(235, 225, 200, a), outline=(80, 60, 40, a))
    d.polygon([(x - 8 * s, y + 20 * s), (x, y), (x + 8 * s, y + 20 * s)], fill=(60, 45, 30, a))


def glow(img, x, y, r, warna=(255, 220, 120), kuat=1.0):
    lap = Image.new("RGBA", (int(r * 2), int(r * 2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    for i in range(12, 0, -1):
        rr = r * i / 12
        d.ellipse((r - rr, r - rr, r + rr, r + rr), fill=tuple(warna) + (int(18 * kuat),))
    img.alpha_composite(lap, (int(x - r), int(y - r)))


def prajurit(d, x, y, warna, s=1.0, alpha=1.0):
    a = int(255 * alpha)
    r = 10 * s
    d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(warna) + (a,), outline=(20, 15, 10, a), width=max(1, int(3 * s)))
    d.ellipse((x - r * 0.45, y - r * 0.55, x + r * 0.05, y - r * 0.05), fill=(255, 255, 255, int(a * 0.45)))


def bendera(d, x, y, warna, s=1.0, alpha=1.0, kibar=0.0):
    a = int(255 * alpha)
    d.line((x, y, x, y - 70 * s), fill=(60, 40, 25, a), width=max(2, int(5 * s)))
    w = 4 * math.sin(kibar) * s
    d.polygon([(x, y - 70 * s), (x + 44 * s, y - 60 * s + w), (x, y - 46 * s)], fill=tuple(warna) + (a,), outline=(30, 20, 10, a))


def garis_putus(d, titik, progres, warna, tebal=6, putus=18, celah=12, alpha=1.0, panah=True):
    """Gambar polyline putus-putus sampai `progres` (0..1) dari panjang total."""
    if progres <= 0 or len(titik) < 2:
        return None
    panjang = [0.0]
    for (x0, y0), (x1, y1) in zip(titik, titik[1:]):
        panjang.append(panjang[-1] + math.hypot(x1 - x0, y1 - y0))
    total = panjang[-1] * clamp(progres)
    c = tuple(warna) + (int(255 * alpha),)
    s = 0.0
    ujung, arah = titik[0], (1, 0)
    while s < total:
        e = min(s + putus, total)
        p0, _ = _titik_di(titik, panjang, s)
        p1, arah = _titik_di(titik, panjang, e)
        d.line((p0[0], p0[1], p1[0], p1[1]), fill=c, width=tebal)
        ujung = p1
        s += putus + celah
    ujung, arah = _titik_di(titik, panjang, total)
    if panah:
        ax, ay = arah
        n = math.hypot(ax, ay) or 1
        ax, ay = ax / n, ay / n
        L = tebal * 3.2
        px, py = -ay, ax
        d.polygon([(ujung[0] + ax * L, ujung[1] + ay * L),
                   (ujung[0] - ax * L * 0.4 + px * L * 0.8, ujung[1] - ay * L * 0.4 + py * L * 0.8),
                   (ujung[0] - ax * L * 0.4 - px * L * 0.8, ujung[1] - ay * L * 0.4 - py * L * 0.8)], fill=c)
    return ujung


def _titik_di(titik, panjang, s):
    for i in range(1, len(panjang)):
        if panjang[i] >= s or i == len(panjang) - 1:
            seg = panjang[i] - panjang[i - 1] or 1
            k = clamp((s - panjang[i - 1]) / seg)
            (x0, y0), (x1, y1) = titik[i - 1], titik[i]
            return (lerp(x0, x1, k), lerp(y0, y1, k)), (x1 - x0, y1 - y0)
    return titik[-1], (1, 0)


def titik_di_jalur(titik, progres):
    panjang = [0.0]
    for (x0, y0), (x1, y1) in zip(titik, titik[1:]):
        panjang.append(panjang[-1] + math.hypot(x1 - x0, y1 - y0))
    return _titik_di(titik, panjang, panjang[-1] * clamp(progres))


def formasi(n, lebar, tinggi, seed, jitter=0.25):
    """Posisi relatif (-0.5..0.5) untuk n prajurit dalam blok."""
    rng = random.Random(seed)
    kol = max(1, int(round(math.sqrt(n * lebar / tinggi))))
    bar = math.ceil(n / kol)
    out = []
    for i in range(n):
        cx, cy = i % kol, i // kol
        x = (cx + 0.5) / kol - 0.5 + rng.uniform(-jitter, jitter) / kol
        y = (cy + 0.5) / bar - 0.5 + rng.uniform(-jitter, jitter) / bar
        out.append((x * lebar, y * tinggi))
    return out


def hujan(img, t, kuat=1.0, seed=7):
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    rng = random.Random(seed)
    for _ in range(int(220 * kuat)):
        x0 = rng.uniform(-200, W + 200)
        v = rng.uniform(1400, 2200)
        y0 = (rng.uniform(0, H) + t * v) % (H + 200) - 100
        L = rng.uniform(30, 60)
        d.line((x0, y0, x0 - L * 0.25, y0 + L), fill=(200, 215, 235, int(rng.uniform(70, 150) * kuat)), width=2)
    img.alpha_composite(lap)


def tint(img, warna, kuat):
    if kuat <= 0.01:
        return
    lap = Image.new("RGBA", img.size, tuple(warna) + (int(255 * clamp(kuat)),))
    img.alpha_composite(lap)


@lru_cache(maxsize=1)
def _vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (xx - W / 2) / (W / 2)
    dy = (yy - H / 2) / (H / 2)
    r = np.sqrt(dx * dx * 0.9 + dy * dy * 0.75)
    a = np.clip((r - 0.55) / 0.75, 0, 1) ** 1.6 * 200
    lap = np.zeros((H, W, 4), np.uint8)
    lap[..., 3] = a.astype(np.uint8)
    return Image.fromarray(lap, "RGBA")


def vignette(img):
    img.alpha_composite(_vignette())


# ---------------------------------------------------------------- peta dunia

@dataclass
class Peta:
    """Peta raster besar (koordinat lintang/bujur) + kamera yang bisa geser & zoom."""
    lon0: float
    lon1: float
    lat0: float
    lat1: float
    skala: float  # px per derajat
    laut: list[list[tuple[float, float]]]  # poligon laut, daftar (lat, lon)
    gunung: list[tuple[float, float, float]] = field(default_factory=list)  # (lat, lon, radius_deg)
    seed: int = 3

    def __post_init__(self):
        self.lebar = int((self.lon1 - self.lon0) * self.skala)
        self.tinggi = int((self.lat1 - self.lat0) * self.skala)
        self.gambar = self._render()

    def px(self, lat, lon):
        return ((lon - self.lon0) * self.skala, (self.lat1 - lat) * self.skala)

    def _render(self) -> Image.Image:
        w, h = self.lebar, self.tinggi
        mask_img = Image.new("L", (w, h), 0)
        md = ImageDraw.Draw(mask_img)
        for poli in self.laut:
            md.polygon([self.px(a, b) for a, b in poli], fill=255)
        # garis pantai dibuat sedikit bergerigi
        mask = np.asarray(mask_img.filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
        mask = (mask + (fbm(h, w, 64, self.seed + 50, 4) - 0.5) * 0.25) > 0.5
        laut = mask.astype(np.float32)

        n1 = fbm(h, w, 512, self.seed, 6)
        n2 = fbm(h, w, 96, self.seed + 10, 4)
        kertas = fbm(h, w, 24, self.seed + 20, 3)

        # daratan: pasir + bayangan gunung
        gunung = np.zeros((h, w), np.float32)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        for lat, lon, r in self.gunung:
            gx, gy = self.px(lat, lon)
            rr = r * self.skala
            gunung += np.exp(-(((xx - gx) / (rr * 0.6)) ** 2 + ((yy - gy) / rr) ** 2))
        gunung = np.clip(gunung, 0, 1) * (0.55 + 0.9 * n2)
        ridge = np.abs(n2 - 0.5) * 2
        ridge = np.clip(1 - ridge * 3, 0, 1) * gunung

        darat = np.zeros((h, w, 3), np.float32)
        base = np.array(PASIR, np.float32)
        terang = (n1 - 0.5) * 50 + (kertas - 0.5) * 18
        darat[:] = base
        darat += terang[..., None]
        darat -= (gunung * 55)[..., None] * np.array([1.0, 1.1, 1.3], np.float32)
        darat -= (ridge * 35)[..., None]

        # laut: biru gelap + gradasi dangkal di pantai
        blur_laut = np.asarray(Image.fromarray((laut * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28)), np.float32) / 255
        dangkal = np.clip((1 - blur_laut) * 2.2, 0, 1) * laut
        air = np.zeros((h, w, 3), np.float32)
        air[:] = np.array((40, 58, 92), np.float32)
        air += ((n1 - 0.5) * 30 + (kertas - 0.5) * 16)[..., None]
        air = air * (1 - dangkal[..., None] * 0.6) + np.array((92, 130, 150), np.float32) * dangkal[..., None] * 0.6

        rgb = darat * (1 - laut[..., None]) + air * laut[..., None]

        # garis pantai gelap
        tepi = np.asarray(Image.fromarray((laut * 255).astype(np.uint8)).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5)), np.float32) / 255
        rgb = rgb * (1 - tepi[..., None] * 0.75) + np.array(TINTA, np.float32) * tepi[..., None] * 0.75

        # noda/grunge kertas
        noda = fbm(h, w, 160, self.seed + 30, 5)
        rgb *= (0.86 + 0.22 * noda)[..., None]
        return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")


class Kamera:
    def __init__(self, x, y, zoom):
        self.x, self.y, self.zoom = x, y, zoom

    def layar(self, wx, wy):
        return ((wx - self.x) * self.zoom + W / 2, (wy - self.y) * self.zoom + H / 2)


def render_peta(peta: Peta, cam: Kamera) -> Image.Image:
    """Potong peta sesuai kamera. Kamera digeser (in-place) supaya tidak keluar peta."""
    cam.zoom = max(cam.zoom, W / peta.lebar, H / peta.tinggi)
    vw, vh = W / cam.zoom, H / cam.zoom
    cam.x = clamp(cam.x, vw / 2, peta.lebar - vw / 2)
    cam.y = clamp(cam.y, vh / 2, peta.tinggi - vh / 2)
    x0, y0 = cam.x - vw / 2, cam.y - vh / 2
    crop = peta.gambar.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + vw, y0 + vh))
    return crop.convert("RGBA")


def kamera_antara(a, b, k):
    """a, b = (x, y, zoom). Interpolasi zoom secara logaritmik biar halus."""
    z = math.exp(lerp(math.log(a[2]), math.log(b[2]), k))
    return Kamera(lerp(a[0], b[0], k), lerp(a[1], b[1], k), z)


# ---------------------------------------------------------------- latar lembah (zoom-in medan perang)

def latar_tekstur(lebar, tinggi, seed, warna=PASIR, bukit=()):
    """Tekstur pasir + bukit. bukit: list (x, y, rx, ry) dalam px."""
    n1 = fbm(tinggi, lebar, 300, seed, 6)
    n2 = fbm(tinggi, lebar, 40, seed + 5, 3)
    rgb = np.zeros((tinggi, lebar, 3), np.float32)
    rgb[:] = np.array(warna, np.float32)
    rgb += ((n1 - 0.5) * 60 + (n2 - 0.5) * 20)[..., None]
    yy, xx = np.mgrid[0:tinggi, 0:lebar].astype(np.float32)
    for bx, by, rx, ry in bukit:
        g = np.exp(-(((xx - bx) / rx) ** 2 + ((yy - by) / ry) ** 2))
        g = g * (0.6 + 0.8 * n1)
        rgb -= (np.clip(g, 0, 1) * 70)[..., None] * np.array([1.0, 1.15, 1.35], np.float32)
        # sisi terang
        g2 = np.exp(-(((xx - bx + rx * 0.25) / rx) ** 2 + ((yy - by + ry * 0.25) / ry) ** 2))
        rgb += (np.clip(g2 - g, 0, 1) * 30)[..., None]
    noda = fbm(tinggi, lebar, 120, seed + 9, 4)
    rgb *= (0.85 + 0.25 * noda)[..., None]
    # garis kontur tipis
    kontur = (np.abs(((n1 * 14) % 1) - 0.5) < 0.03).astype(np.float32) * 0.25
    rgb = rgb * (1 - kontur[..., None]) + np.array(TINTA, np.float32) * kontur[..., None]
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")


# ---------------------------------------------------------------- header

def header(img, judul, sub="", alpha=1.0, seri="NGOMONGIN SEJARAH"):
    """Label seri + judul di atas (di bawah area tab TikTok)."""
    if alpha <= 0.01:
        return
    lap = Image.new("RGBA", (W, 360), (0, 0, 0, 0))
    d = ImageDraw.Draw(lap)
    fs = font("ui", 30)
    lw = fs.getlength(seri) + 44
    d.rounded_rectangle((W / 2 - lw / 2, 180, W / 2 + lw / 2, 228), 24, fill=(200, 52, 44, 235))
    d.text((W / 2, 204), seri, font=fs, fill=PUTIH, anchor="mm")
    d.text((W / 2, 262), judul, font=font("judul", 56), fill=PUTIH, anchor="mm", stroke_width=6, stroke_fill=(25, 15, 5))
    if sub:
        d.text((W / 2, 322), sub, font=font("ui", 30), fill=(255, 235, 190), anchor="mm", stroke_width=4, stroke_fill=(25, 15, 5))
    tempel(img, lap, alpha)


# ---------------------------------------------------------------- caption ala TikTok

@dataclass
class Kata:
    teks: str
    mulai: float
    selesai: float


def kelompok_caption(kata: list[Kata], maks_kata=3, maks_huruf=20) -> list[list[Kata]]:
    grup, cur = [], []
    for i, k in enumerate(kata):
        jeda = (k.mulai - kata[i - 1].selesai) if i else 0
        panjang = sum(len(x.teks) + 1 for x in cur) + len(k.teks)
        if cur and (len(cur) >= maks_kata or panjang > maks_huruf or jeda > 0.22):
            grup.append(cur)
            cur = []
        cur.append(k)
    if cur:
        grup.append(cur)
    return grup


def gambar_caption(img, grup: list[list[Kata]], t, y=1440):
    aktif = None
    for g in grup:
        if g[0].mulai - 0.05 <= t <= g[-1].selesai + 0.25:
            aktif = g
    if not aktif:
        return
    d = ImageDraw.Draw(img)
    ukuran = 84
    f = font("caption", ukuran)
    kata = [k.teks.upper() for k in aktif]
    spasi = f.getlength(" ")
    total = sum(f.getlength(k) for k in kata) + spasi * (len(kata) - 1)
    while total > 900 and ukuran > 50:
        ukuran -= 4
        f = font("caption", ukuran)
        spasi = f.getlength(" ")
        total = sum(f.getlength(k) for k in kata) + spasi * (len(kata) - 1)
    muncul = back_out((t - aktif[0].mulai + 0.05) / 0.18)
    yy = y + (1 - muncul) * 30
    x = W / 2 - total / 2
    for k, isi in zip(aktif, kata):
        lw = f.getlength(isi)
        sedang = k.mulai - 0.02 <= t < k.selesai + 0.08
        warna = KUNING if sedang else PUTIH
        d.text((x + 5, yy + 7), isi, font=f, fill=(0, 0, 0, 150), anchor="lm")
        d.text((x, yy), isi, font=f, fill=warna + (255,), anchor="lm", stroke_width=9, stroke_fill=(0, 0, 0, 255))
        x += lw + spasi


# ---------------------------------------------------------------- adegan

@dataclass
class Adegan:
    nama: str
    narasi: str
    gambar: Callable  # fungsi(ctx) -> Image RGBA (W x H)
    transisi: bool = True  # fade dari adegan sebelumnya
    durasi: float = 0.0    # diisi otomatis dari audio
    mulai: float = 0.0


@dataclass
class Ctx:
    t: float          # waktu lokal (detik) di adegan
    d: float          # durasi adegan
    T: float          # waktu global
    adegan: Adegan

    def p(self, a, b):
        """Progres eased antara fraksi durasi a..b."""
        return prog(self.t / self.d if self.d else 1, a, b)
