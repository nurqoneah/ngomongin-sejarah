"""Maskot anak cowok pencerita (chibi) -> branding/opsi-logo/4-*.png"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import shorts_engine as se  # noqa: E402
from logo_kartun import C, GARIS, KUNING, OUT, Kartun  # noqa: E402

KULIT = (255, 216, 178)
RAMBUT = (58, 40, 32)


def mata_imut(k, x, y):
    k.elips((x - 36, y - 48, x + 36, y + 48), (45, 30, 25), 0)
    k.elips((x - 20, y - 36, x + 12, y - 4), (255, 255, 255), 0)
    k.elips((x + 8, y + 14, x + 22, y + 28), (255, 255, 255), 0)


def kepala(k, rambut=True, ekspresi="cerita"):
    # rambut belakang + telinga
    if rambut:
        k.elips((C - 222, 150, C + 222, 480), RAMBUT, 9)
    k.elips((C - 232, 370, C - 168, 450), KULIT, 8)
    k.elips((C + 168, 370, C + 232, 450), KULIT, 8)
    k.elips((C - 205, 200, C + 205, 590), KULIT, 9)
    if rambut:
        k.poli([(C - 212, 380), (C - 205, 260), (C - 130, 185), (C, 165), (C + 135, 185), (C + 208, 265),
                (C + 212, 370), (C + 165, 300), (C + 100, 320), (C + 50, 270), (C - 10, 310), (C - 75, 265),
                (C - 140, 315)], RAMBUT, 9)
    mata_imut(k, C - 80, 405)
    mata_imut(k, C + 80, 405)
    k.busur((C - 125, 320, C - 40, 360), 200, 330, 8)
    k.busur((C + 40, 320, C + 125, 360), 210, 340, 8)
    k.elips((C - 170, 455, C - 105, 495), (255, 160, 150), 0)
    k.elips((C + 105, 455, C + 170, 495), (255, 160, 150), 0)
    if ekspresi == "cerita":
        k.d.chord(k._b((C - 52, 470, C + 52, 560)), 0, 180, fill=(140, 40, 40), outline=GARIS, width=8 * 3)
        k.d.chord(k._b((C - 30, 520, C + 30, 562)), 180, 360, fill=(250, 120, 120))
    else:
        k.busur((C - 50, 450, C + 50, 530), 20, 160, 9)


def badan(k, baju, kerah=None):
    k.kotak((C - 165, 560, C + 165, 860), 70, baju, 9)
    k.kotak((C - 40, 545, C + 40, 600), 10, KULIT, 0)
    if kerah:
        k.poli([(C - 60, 575), (C, 640), (C + 60, 575)], kerah, 7)


def tangan(k, dari, ke, baju):
    k.garis([dari, ke], 44, GARIS)
    k.garis([dari, ke], 30, baju)
    x, y = ke
    k.elips((x - 34, y - 34, x + 34, y + 34), KULIT, 8)


def gelembung_kiri(k, isi):
    k.gelembung((C - 395, 170, C - 165, 270), [(C - 230, 260), (C - 180, 260), (C - 160, 320)], isi, 40)


def latar(k, warna_lencana):
    k.elips((C - 400, 80, C + 400, 880), warna_lencana, 14)


# 1 — Peci & baju koko, pegang gulungan
def maskot_peci():
    k = Kartun((255, 214, 92))
    k.sinar(C, 470, 24, 760, (255, 228, 140))
    latar(k, (90, 180, 140))
    hijau = (40, 140, 100)
    badan(k, hijau, (255, 255, 255))
    for y in (680, 740):
        k.elips((C - 9, y - 9, C + 9, y + 9), KUNING, 4)
    tangan(k, (C + 130, 640), (C + 250, 560), hijau)
    # gulungan di tangan kanan
    k.kotak((C + 225, 470, C + 345, 600), 8, (250, 236, 200), 7)
    k.kotak((C + 210, 455, C + 240, 615), 15, (222, 186, 130), 7)
    k.kotak((C + 330, 455, C + 360, 615), 15, (222, 186, 130), 7)
    for y in (505, 535, 565):
        k.garis([(C + 255, y), (C + 315, y)], 5, (190, 160, 120))
    tangan(k, (C - 130, 640), (C - 260, 520), hijau)
    kepala(k)
    # peci
    k.kotak((C - 165, 150, C + 165, 278), 24, (30, 30, 36), 9)
    k.garis([(C - 145, 250), (C + 145, 250)], 6, (200, 160, 60))
    gelembung_kiri(k, "Jadi gini...")
    k.pita(880)
    return k.hasil()


# 2 — Petualang: topi safari + peta
def maskot_petualang():
    k = Kartun((120, 200, 230))
    k.sinar(C, 470, 24, 760, (150, 215, 240))
    latar(k, (255, 200, 110))
    khaki, tali = (200, 170, 110), (120, 80, 45)
    badan(k, khaki, (230, 210, 160))
    k.garis([(C - 110, 575), (C - 70, 850)], 16, tali)
    k.garis([(C + 110, 575), (C + 70, 850)], 16, tali)
    # peta terbuka di tangan kanan
    tangan(k, (C + 130, 640), (C + 240, 600), khaki)
    k.poli([(C + 190, 470), (C + 260, 490), (C + 330, 465), (C + 390, 485), (C + 390, 620), (C + 330, 600),
            (C + 260, 625), (C + 190, 605)], (250, 236, 200), 7)
    se.garis_putus(k.d, [((C + 215) * 3, 580 * 3), ((C + 280) * 3, 520 * 3), ((C + 350) * 3, 560 * 3)], 1.0,
                   (200, 50, 40), tebal=15, putus=40, celah=30, panah=False)
    k.teks((C + 352, 552), "x", 40, (200, 50, 40))
    tangan(k, (C - 130, 640), (C - 240, 490), khaki)
    kepala(k)
    # topi safari
    k.elips((C - 265, 215, C + 265, 300), khaki, 9)
    k.kotak((C - 170, 110, C + 170, 265), 70, khaki, 9)
    k.kotak((C - 172, 205, C + 172, 245), 6, tali, 7)
    k.pita(880)
    return k.hasil()


# 3 — Kacamata + hoodie, pegang mikrofon
def maskot_hoodie():
    k = Kartun((255, 236, 214))
    k.sinar(C, 470, 24, 760, (255, 222, 190))
    latar(k, (110, 90, 200))
    oranye = (245, 140, 50)
    k.elips((C - 250, 520, C + 250, 640), oranye, 9)  # tudung di punggung
    badan(k, oranye)
    k.garis([(C - 35, 600), (C - 45, 700)], 7, (255, 255, 255))
    k.garis([(C + 35, 600), (C + 45, 700)], 7, (255, 255, 255))
    k.kotak((C - 90, 730, C + 90, 820), 20, (225, 120, 40), 7)
    tangan(k, (C - 130, 640), (C - 250, 520), oranye)
    kepala(k)
    # kacamata bulat
    for x in (C - 80, C + 80):
        k.elips((x - 62, 345, x + 62, 465), None, 9)
    k.garis([(C - 18, 400), (C + 18, 400)], 9)
    # mikrofon
    tangan(k, (C + 130, 650), (C + 225, 560), oranye)
    k.kotak((C + 205, 430, C + 255, 560), 25, (70, 70, 80), 8)
    k.elips((C + 190, 360, C + 270, 450), (200, 200, 215), 8)
    gelembung_kiri(k, "Tau gak?")
    k.pita(880)
    return k.hasil()


if __name__ == "__main__":
    opsi = {"peci": maskot_peci, "petualang": maskot_petualang, "hoodie": maskot_hoodie}
    gambar = []
    for nama, fn in opsi.items():
        im = fn()
        im.save(OUT / f"4-maskot-{nama}.png")
        gambar.append((nama, im))
    L = Image.new("RGB", (3 * 440, 680), (245, 245, 245))
    d = ImageDraw.Draw(L)
    for i, (nama, im) in enumerate(gambar):
        x = i * 440 + 10
        L.paste(im.resize((420, 420), Image.LANCZOS), (x, 10))
        m = Image.new("L", (170, 170), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 170, 170), fill=255)
        L.paste(im.resize((170, 170), Image.LANCZOS), (x + 125, 445), m)
        d.text((x + 210, 650), nama, font=se.font("ui", 30), fill=(30, 30, 30), anchor="mm")
    L.save(OUT / "perbandingan-maskot.png")
    print("Selesai")
