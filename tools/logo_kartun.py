"""Konsep logo gaya kartun (garis tebal, warna flat, pita judul) -> branding/opsi-logo/3-*.png"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import shorts_engine as se  # noqa: E402

OUT = Path(__file__).parent.parent / "branding" / "opsi-logo"
S, SS = 1080, 3          # digambar 3x lalu diperkecil biar halus
C = S / 2
GARIS = (45, 30, 25)
MERAH = (214, 58, 48)
MERAH_TUA = (150, 34, 30)
KUNING = (255, 205, 60)
KREM = (252, 242, 218)


class Kartun:
    def __init__(self, latar):
        self.img = Image.new("RGBA", (S * SS, S * SS), latar + (255,))
        self.d = ImageDraw.Draw(self.img)

    def _b(self, box):
        return [v * SS for v in box]

    def elips(self, box, isi, w=8, garis=GARIS):
        self.d.ellipse(self._b(box), fill=isi, outline=garis if w else None, width=int(w * SS))

    def kotak(self, box, r, isi, w=8, garis=GARIS):
        self.d.rounded_rectangle(self._b(box), int(r * SS), fill=isi, outline=garis if w else None, width=int(w * SS))

    def poli(self, pts, isi, w=8, garis=GARIS):
        p = [(x * SS, y * SS) for x, y in pts]
        self.d.polygon(p, fill=isi)
        if w:
            self.d.line(p + [p[0]], fill=garis, width=int(w * SS), joint="curve")
            for x, y in p:
                r = w * SS / 2
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=garis)

    def garis(self, pts, w=8, warna=GARIS):
        p = [(x * SS, y * SS) for x, y in pts]
        self.d.line(p, fill=warna, width=int(w * SS), joint="curve")
        for x, y in (p[0], p[-1]):
            r = w * SS / 2
            self.d.ellipse((x - r, y - r, x + r, y + r), fill=warna)

    def busur(self, box, a0, a1, w=8, warna=GARIS):
        self.d.arc(self._b(box), a0, a1, fill=warna, width=int(w * SS))

    def teks(self, xy, isi, ukuran, isi_warna, font="caption", stroke=0, stroke_warna=GARIS, bayang=0):
        f = se.font(font, ukuran * SS)
        x, y = xy[0] * SS, xy[1] * SS
        if bayang:
            self.d.text((x + bayang * SS, y + bayang * SS), isi, font=f, fill=GARIS, anchor="mm",
                        stroke_width=int(stroke * SS), stroke_fill=GARIS)
        self.d.text((x, y), isi, font=f, fill=isi_warna, anchor="mm", stroke_width=int(stroke * SS), stroke_fill=stroke_warna)

    def sinar(self, cx, cy, n, r, warna):
        for i in range(n):
            a0 = i * 2 * math.pi / n
            a1 = a0 + math.pi / n
            self.d.polygon([(cx * SS, cy * SS), ((cx + r * math.cos(a0)) * SS, (cy + r * math.sin(a0)) * SS),
                            ((cx + r * math.cos(a1)) * SS, (cy + r * math.sin(a1)) * SS)], fill=warna)

    def kilau(self, x, y, r, warna=(255, 255, 255)):
        self.poli([(x, y - r), (x + r * 0.25, y - r * 0.25), (x + r, y), (x + r * 0.25, y + r * 0.25),
                   (x, y + r), (x - r * 0.25, y + r * 0.25), (x - r, y), (x - r * 0.25, y - r * 0.25)], warna, 4)

    def pita(self, y, judul="SEJARAH", label="NGOMONGIN", lebar=360):
        # ujung pita (di belakang)
        for s in (-1, 1):
            x0 = C + s * (lebar - 40)
            x1 = C + s * (lebar + 70)
            self.poli([(x0, y - 40), (x1, y - 40), (x1 - s * 40, y + 30), (x1, y + 100), (x0, y + 100)], MERAH_TUA, 8)
            self.poli([(C + s * lebar, y + 70), (C + s * (lebar - 40), y + 100), (C + s * (lebar - 40), y + 70)], (100, 20, 18), 6)
        self.kotak((C - lebar, y - 70, C + lebar, y + 70), 12, MERAH, 9)
        self.teks((C, y + 4), judul, 112, KREM, stroke=6, bayang=6)
        # label kecil di atas pita
        f = se.font("caption", 48)
        lw = f.getlength(label) / 2 + 34
        self.kotak((C - lw, y - 128, C + lw, y - 62), 33, KUNING, 7)
        self.teks((C, y - 95), label, 48, GARIS)

    def gelembung(self, box, ekor, isi, ukuran=56):
        x0, y0, x1, y1 = box
        self.poli(ekor, (255, 255, 255), 8)
        self.kotak(box, 50, (255, 255, 255), 8)
        # tutup sambungan ekor
        ex = sum(p[0] for p in ekor[:2]) / 2
        self.d.rectangle(((ex - 30) * SS, (y1 - 12) * SS, (ex + 30) * SS, (y1 - 3) * SS), fill=(255, 255, 255))
        self.teks(((x0 + x1) / 2, (y0 + y1) / 2), isi, ukuran, GARIS)

    def hasil(self):
        return self.img.resize((S, S), Image.LANCZOS).convert("RGB")


def mata(k: Kartun, x, y, r=48, lirik=(8, 6), kelopak=True, warna_kulit=None):
    k.elips((x - r, y - r * 1.15, x + r, y + r * 1.15), (255, 255, 255), 7)
    px, py = x + lirik[0], y + lirik[1]
    k.elips((px - r * 0.55, py - r * 0.65, px + r * 0.55, py + r * 0.65), (35, 25, 20), 0)
    k.elips((px - r * 0.05, py - r * 0.5, px + r * 0.3, py - r * 0.15), (255, 255, 255), 0)
    if kelopak and warna_kulit:
        k.d.chord(k._b((x - r - 4, y - r * 1.15 - 4, x + r + 4, y + r * 1.15)), 180, 360, fill=warna_kulit)
        k.d.line(k._b((x - r - 2, y - r * 0.08, x + r + 2, y - r * 0.08)), fill=GARIS, width=7 * SS)


# K — Maskot unta yang lagi cerita
def opsi_unta():
    k = Kartun((255, 241, 214))
    k.sinar(C, 470, 24, 760, (255, 230, 190))
    # lencana latar: langit senja + bukit pasir
    k.elips((C - 400, 70, C + 400, 870), (255, 196, 92), 14)
    k.elips((C - 140, 160, C + 0, 300), (255, 226, 150), 0)
    k.d.chord(k._b((C - 393, 77, C + 393, 863)), 30, 150, fill=(226, 150, 70))
    k.d.chord(k._b((C - 393, 77, C + 393, 863)), 50, 130, fill=(204, 126, 54))
    kulit, moncong = (214, 160, 98), (238, 200, 146)
    # leher + syal
    k.kotak((C - 105, 470, C + 105, 900), 40, kulit, 9)
    k.kotak((C - 125, 640, C + 125, 710), 30, MERAH, 8)
    k.poli([(C + 60, 690), (C + 140, 790), (C + 80, 800), (C + 30, 700)], MERAH, 8)
    # telinga
    k.elips((C - 215, 210, C - 120, 290), kulit, 8)
    k.elips((C + 120, 210, C + 215, 290), kulit, 8)
    # kepala & moncong
    k.elips((C - 160, 150, C + 160, 520), kulit, 9)
    for dx in (-50, -15, 20, 55):
        k.elips((C + dx - 40, 120, C + dx + 40, 195), (150, 100, 55), 7)
    k.elips((C - 185, 390, C + 185, 610), moncong, 9)
    k.elips((C - 80, 430, C - 45, 465), (90, 55, 35), 0)
    k.elips((C + 45, 430, C + 80, 465), (90, 55, 35), 0)
    # mulut lagi ngomong
    k.elips((C - 60, 495, C + 60, 580), (120, 30, 30), 8)
    k.d.chord(k._b((C - 40, 535, C + 40, 590)), 180, 360, fill=(240, 110, 110))
    # pipi
    k.elips((C - 165, 470, C - 115, 510), (240, 150, 120), 0)
    k.elips((C + 115, 470, C + 165, 510), (240, 150, 120), 0)
    mata(k, C - 72, 315, 50, (6, 4))
    mata(k, C + 72, 315, 50, (6, 4))
    k.busur((C - 130, 230, C - 20, 280), 200, 330, 8)
    k.busur((C + 20, 230, C + 130, 280), 210, 340, 8)
    k.gelembung((C + 140, 150, C + 390, 270), [(C + 170, 260), (C + 230, 260), (C + 165, 330)], "Tau gak?", 46)
    k.kilau(C - 330, 200, 34)
    k.kilau(C - 280, 640, 22)
    k.pita(905)
    return k.hasil()


# L — Buku ajaib yang memunculkan sejarah
def opsi_buku():
    k = Kartun((40, 120, 160))
    k.sinar(C, 470, 24, 760, (54, 138, 178))
    # yang keluar dari buku
    k.poli([(C - 330, 520), (C - 200, 270), (C - 70, 520)], (246, 196, 84), 8)
    k.poli([(C - 200, 270), (C - 70, 520), (C - 160, 520)], (214, 160, 60), 0)
    k.kotak((C + 90, 230, C + 140, 520), 6, (240, 236, 224), 8)
    k.poli([(C + 82, 232), (C + 115, 170), (C + 148, 232)], (60, 170, 110), 8)
    k.kotak((C + 150, 380, C + 330, 520), 6, (240, 236, 224), 8)
    k.d.pieslice(k._b((C + 160, 300, C + 320, 460)), 180, 360, fill=(60, 170, 110), outline=GARIS, width=8 * SS)
    k.kotak((C - 60, 300, C + 60, 520), 4, (170, 170, 180), 8)
    for i in range(3):
        k.kotak((C - 60 + i * 44, 270, C - 30 + i * 44, 305), 3, (170, 170, 180), 7)
    k.kotak((C - 18, 440, C + 18, 520), 18, (70, 60, 60), 0)
    # buku
    k.poli([(C - 400, 560), (C, 610), (C + 400, 560), (C + 400, 660), (C, 720), (C - 400, 660)], MERAH_TUA, 9)
    k.poli([(C - 380, 500), (C - 10, 560), (C - 10, 680), (C - 380, 630)], KREM, 9)
    k.poli([(C + 380, 500), (C + 10, 560), (C + 10, 680), (C + 380, 630)], KREM, 9)
    for i in range(4):
        y = 560 + i * 26
        k.garis([(C - 330, y - 30 + i * 2), (C - 60, y + 10)], 5, (190, 170, 140))
        k.garis([(C + 330, y - 30 + i * 2), (C + 60, y + 10)], 5, (190, 170, 140))
    k.kilau(C - 380, 300, 40, KUNING)
    k.kilau(C + 400, 260, 30, KUNING)
    k.kilau(C + 330, 160, 20)
    k.kilau(C - 260, 170, 22)
    k.pita(860)
    return k.hasil()


# M — Gulungan naskah yang bisa ngomong
def opsi_gulungan():
    k = Kartun((255, 214, 92))
    k.sinar(C, 460, 24, 760, (255, 226, 130))
    kertas = (250, 236, 200)
    # tangan
    k.garis([(C - 250, 500), (C - 360, 380), (C - 380, 300)], 14)
    k.elips((C - 420, 250, C - 340, 320), (255, 255, 255), 8)
    k.garis([(C + 250, 520), (C + 350, 600)], 14)
    k.elips((C + 330, 570, C + 410, 640), (255, 255, 255), 8)
    # badan gulungan
    k.kotak((C - 260, 230, C + 260, 720), 10, kertas, 9)
    for x in (C - 260, C + 260):
        k.kotak((x - 50, 190, x + 50, 760), 50, (222, 186, 130), 9)
        k.elips((x - 50, 172, x + 50, 228), (190, 140, 90), 8)
        k.elips((x - 20, 188, x + 20, 212), (150, 100, 60), 0)
    # wajah
    mata(k, C - 85, 380, 52, (6, 4))
    mata(k, C + 85, 380, 52, (6, 4))
    k.garis([(C - 140, 300), (C - 40, 290)], 9)
    k.garis([(C + 40, 290), (C + 140, 300)], 9)
    k.d.chord(k._b((C - 90, 450, C + 90, 610)), 0, 180, fill=(120, 30, 30), outline=GARIS, width=8 * SS)
    k.d.chord(k._b((C - 50, 520, C + 50, 610)), 180, 360, fill=(240, 110, 110))
    k.elips((C - 190, 460, C - 130, 500), (245, 170, 140), 0)
    k.elips((C + 130, 460, C + 190, 500), (245, 170, 140), 0)
    k.kilau(C - 400, 150, 32, (255, 255, 255))
    k.pita(870)
    return k.hasil()


# N — Jam pasir lucu pegang mikrofon
def opsi_jampasir():
    k = Kartun((86, 60, 140))
    k.sinar(C, 460, 24, 760, (100, 74, 158))
    kayu, kaca = (176, 112, 62), (210, 240, 250)
    # badan kaca
    k.poli([(C - 190, 200), (C + 190, 200), (C + 30, 420), (C + 190, 650), (C - 190, 650), (C - 30, 420)], kaca, 9)
    k.poli([(C - 120, 280), (C + 120, 280), (C + 20, 410), (C - 20, 410)], (250, 200, 90), 6)
    k.poli([(C - 150, 640), (C, 540), (C + 150, 640)], (250, 200, 90), 6)
    k.garis([(C, 420), (C, 560)], 6, (230, 170, 60))
    # tiang & tutup
    for x in (C - 230, C + 230):
        k.kotak((x - 18, 190, x + 18, 670), 10, kayu, 8)
    k.kotak((C - 260, 150, C + 260, 210), 20, kayu, 9)
    k.kotak((C - 260, 640, C + 260, 700), 20, kayu, 9)
    # wajah di bagian atas
    mata(k, C - 55, 255, 34, (5, 3))
    mata(k, C + 55, 255, 34, (5, 3))
    k.busur((C - 40, 290, C + 40, 345), 20, 160, 8)
    # tangan + mikrofon
    k.garis([(C + 180, 520), (C + 300, 450)], 12)
    k.kotak((C + 270, 330, C + 350, 470), 40, (90, 90, 100), 8)
    k.kotak((C + 278, 300, C + 342, 380), 32, (200, 200, 210), 8)
    k.garis([(C - 180, 520), (C - 290, 430)], 12)
    k.elips((C - 330, 390, C - 260, 455), (255, 255, 255), 8)
    k.kilau(C - 380, 230, 34, KUNING)
    k.kilau(C + 400, 600, 26, KUNING)
    k.pita(860)
    return k.hasil()


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    opsi = {"K-unta": opsi_unta, "L-buku": opsi_buku, "M-gulungan": opsi_gulungan, "N-jampasir": opsi_jampasir}
    gambar = []
    for nama, fn in opsi.items():
        im = fn()
        im.save(OUT / f"3-{nama}.png")
        gambar.append((nama, im))
    L = Image.new("RGB", (4 * 440, 680), (245, 245, 245))
    d = ImageDraw.Draw(L)
    for i, (nama, im) in enumerate(gambar):
        x = i * 440 + 10
        L.paste(im.resize((420, 420), Image.LANCZOS), (x, 10))
        m = Image.new("L", (170, 170), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 170, 170), fill=255)
        L.paste(im.resize((170, 170), Image.LANCZOS), (x + 125, 445), m)
        d.text((x + 210, 650), nama, font=se.font("ui", 30), fill=(30, 30, 30), anchor="mm")
    L.save(OUT / "perbandingan-3.png")
    print("Selesai")
