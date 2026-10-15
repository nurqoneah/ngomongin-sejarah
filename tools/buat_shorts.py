"""Bikin video Shorts 9:16 (TikTok / Reels FB / YouTube Shorts) dari `shorts/adegan.py`.

Contoh:
    python tools/buat_shorts.py konten/001-perang-badar
    python tools/buat_shorts.py konten/001-perang-badar --kecepatan +20% --musik musik/latar.mp3
    python tools/buat_shorts.py konten/001-perang-badar --pratinjau 12.5   # simpan 1 frame PNG di detik 12.5
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import subprocess
import sys
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import shorts_engine as se  # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SR = 24000
JEDA = 0.12  # detik hening antar adegan


def muat_adegan(folder: Path):
    spec = importlib.util.spec_from_file_location("adegan", folder / "shorts" / "adegan.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


async def tts(teks, suara, kecepatan, nada, mp3: Path):
    kom = edge_tts.Communicate(teks, suara, rate=kecepatan, pitch=nada, boundary="WordBoundary")
    kata = []
    with open(mp3, "wb") as f:
        async for p in kom.stream():
            if p["type"] == "audio":
                f.write(p["data"])
            elif p["type"] == "WordBoundary":
                m = p["offset"] / 1e7
                kata.append({"teks": p["text"], "mulai": m, "selesai": m + p["duration"] / 1e7})
    return kata


def ke_pcm(mp3: Path) -> np.ndarray:
    out = subprocess.run([FFMPEG, "-v", "error", "-i", str(mp3), "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.int16)


def potong_hening(pcm: np.ndarray, ambang=300):
    """Buang hening di ujung belakang (edge-tts suka kasih ekor panjang)."""
    keras = np.nonzero(np.abs(pcm) > ambang)[0]
    if len(keras) == 0:
        return pcm
    akhir = min(len(pcm), keras[-1] + int(0.08 * SR))
    return pcm[:akhir]


def srt_waktu(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path)
    ap.add_argument("--suara", default=None)
    ap.add_argument("--kecepatan", default=None, help="misal +15%%")
    ap.add_argument("--nada", default=None)
    ap.add_argument("--musik", type=Path, default=None, help="file musik latar (opsional)")
    ap.add_argument("--volume-musik", type=float, default=0.12)
    ap.add_argument("--pratinjau", type=float, nargs="*", default=None, help="detik-detik untuk disimpan sebagai PNG saja")
    a = ap.parse_args()

    mod = muat_adegan(a.folder)
    adegan: list[se.Adegan] = mod.ADEGAN
    suara = a.suara or getattr(mod, "SUARA", "id-ID-ArdiNeural")
    kecepatan = a.kecepatan or getattr(mod, "KECEPATAN", "+15%")
    nada = a.nada or getattr(mod, "NADA", "-2Hz")
    nama = getattr(mod, "NAMA_FILE", a.folder.name)

    out = a.folder / "shorts"
    cache = out / "_cache"
    cache.mkdir(parents=True, exist_ok=True)

    # 1. Suara per adegan (di-cache berdasarkan teks + setelan)
    semua_kata: list[se.Kata] = []
    potongan = []
    t = 0.0
    for i, ad in enumerate(adegan):
        kunci = f"{i:02}-{ad.nama}"
        mp3, js = cache / f"{kunci}.mp3", cache / f"{kunci}.json"
        sidik = json.dumps([ad.narasi, suara, kecepatan, nada])
        lama = json.loads(js.read_text(encoding="utf-8")) if js.exists() else {}
        if lama.get("sidik") != sidik or not mp3.exists():
            print(f"  TTS  {kunci}")
            kata = asyncio.run(tts(ad.narasi, suara, kecepatan, nada, mp3))
            js.write_text(json.dumps({"sidik": sidik, "kata": kata}, ensure_ascii=False), encoding="utf-8")
        else:
            kata = lama["kata"]
        pcm = potong_hening(ke_pcm(mp3))
        ad.mulai = t
        ad.durasi = len(pcm) / SR + JEDA
        potongan += [pcm, np.zeros(int(JEDA * SR), np.int16)]
        semua_kata += [se.Kata(k["teks"], t + k["mulai"], t + k["selesai"]) for k in kata]
        t += ad.durasi
    ekor = 0.6
    potongan.append(np.zeros(int(ekor * SR), np.int16))
    adegan[-1].durasi += ekor
    total = t + ekor
    print(f"Durasi total: {total:.1f} detik")

    wav = cache / "narasi.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.concatenate(potongan).tobytes())

    grup = se.kelompok_caption(semua_kata)

    def frame(T):
        idx = max(i for i, ad in enumerate(adegan) if ad.mulai <= T or i == 0)
        ad = adegan[idx]
        img = ad.gambar(se.Ctx(T - ad.mulai, ad.durasi, T, ad))
        if ad.transisi and idx > 0 and T - ad.mulai < 0.35:
            sebelum = adegan[idx - 1]
            lama = sebelum.gambar(se.Ctx(sebelum.durasi, sebelum.durasi, T, sebelum))
            img = Image.blend(lama, img, se.ease((T - ad.mulai) / 0.35))
        se.vignette(img)
        se.gambar_caption(img, grup, T)
        return img.convert("RGB")

    if a.pratinjau is not None:
        for s in a.pratinjau:
            p = out / f"pratinjau-{s:05.1f}.png"
            frame(s).save(p)
            print("  ", p)
        return

    # 2. SRT
    with open(out / f"{nama}.srt", "w", encoding="utf-8") as f:
        for i, g in enumerate(grup, 1):
            f.write(f"{i}\n{srt_waktu(g[0].mulai)} --> {srt_waktu(g[-1].selesai)}\n{' '.join(k.teks for k in g)}\n\n")

    # 3. Render video
    mp4 = out / f"{nama}.mp4"
    cmd = [FFMPEG, "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{se.W}x{se.H}", "-r", str(se.FPS), "-i", "-",
           "-i", str(wav)]
    if a.musik:
        cmd += ["-stream_loop", "-1", "-i", str(a.musik),
                "-filter_complex", f"[2:a]volume={a.volume_musik},afade=t=out:st={total - 2:.2f}:d=2[m];"
                                   f"[1:a][m]amix=inputs=2:duration=first:normalize=0[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{total:.3f}", "-movflags", "+faststart", str(mp4)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(total * se.FPS)
    try:
        for i in range(n):
            proc.stdin.write(frame(i / se.FPS).tobytes())
            if i % se.FPS == 0:
                print(f"\r  render {i / se.FPS:5.1f}/{total:.1f} dtk", end="", flush=True)
    except BaseException:
        # jangan tinggalkan video setengah jadi yang kelihatan "selesai"
        proc.kill()
        proc.wait()
        mp4.unlink(missing_ok=True)
        print(f"\nGAGAL di detik {i / se.FPS:.1f} — video dihapus.")
        raise
    proc.stdin.close()
    proc.wait()
    print(f"\nSelesai: {mp4}")


if __name__ == "__main__":
    main()
