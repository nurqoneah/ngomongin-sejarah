"""Upload video Shorts ke Facebook Reels sebagai DRAFT (tidak tayang) lewat Graph API resmi.

Video diambil dari GitHub Pages, caption dari bagian "## Facebook Reels" di caption.md.
Draft muncul di Meta Business Suite → Konten → Draf; tinggal dicek lalu dipublikasikan manual.
Setup sekali: python tools/login_meta.py (mengisi FB_PAGE_ID & FB_PAGE_TOKEN di .env).

    python tools/upload_fb.py 023            # pratinjau
    python tools/upload_fb.py 023 --kirim    # upload sebagai draft
    python tools/upload_fb.py --antrean --kirim   # konten terbaru yang belum ada di Facebook
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).parent))
from buat_app import parse_caption  # noqa: E402
from setup_meta import baca_env_mentah  # noqa: E402
from upload_ig import PAGES, ROOT, cek_video  # noqa: E402


def env_fb():
    env = baca_env_mentah()
    for k in ("FB_PAGE_ID", "FB_PAGE_TOKEN"):
        if not env.get(k):
            raise SystemExit(f"{k} kosong di .env — jalankan dulu: python tools/login_meta.py")
    return env


def panggil(url, data=None, headers=None):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data is not None else None,
                                 headers=headers or {}, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        isi = e.read()
        try:
            err = json.loads(isi)
            pesan = err.get("error", {}).get("message") or err.get("debug_info", {}).get("message") or isi[:300]
        except Exception:
            pesan = isi[:300] or e.reason
        raise SystemExit(f"API Facebook menolak ({e.code}): {pesan}") from None


def graph(env, path, **data):
    url = f"https://graph.facebook.com/{env['GRAPH_VERSION']}/{path}"
    if data.pop("_get", False):
        return panggil(url + "?" + urllib.parse.urlencode({**data, "access_token": env["FB_PAGE_TOKEN"]}))
    return panggil(url, {**data, "access_token": env["FB_PAGE_TOKEN"]})


def cari_konten(no):
    cocok = sorted((ROOT / "konten").glob(f"{no}-*"))
    if not cocok:
        raise SystemExit(f"Folder konten {no}-* tidak ditemukan")
    folder = cocok[0]
    data = parse_caption((folder / "caption.md").read_text(encoding="utf-8"))
    fb = next((p for p in data["platform"] if p["nama"].startswith("Facebook")), None)
    if not fb or not fb["isian"]:
        raise SystemExit(f"Caption Facebook tidak ada di {folder.name}/caption.md")
    return folder, data["judul"], fb["isian"][0]["teks"]


def riwayat(folder):
    log = folder / "posting.json"
    return json.loads(log.read_text(encoding="utf-8")) if log.exists() else {}


def antrean():
    """Konten terbaru (nomor terbesar) yang sudah punya video tapi belum ada di Facebook."""
    for folder in sorted((ROOT / "konten").glob("[0-9][0-9][0-9]-*"), reverse=True):
        if list((folder / "shorts").glob("*.mp4")) and "facebook" not in riwayat(folder):
            return folder.name[:3]
    raise SystemExit("Semua konten sudah ada di Facebook.")


def upload(env, no, kirim=False):
    folder, judul, caption = cari_konten(no)
    hist = riwayat(folder)
    if "facebook" in hist:
        raise SystemExit(f"{folder.name} sudah pernah diupload ke Facebook ({hist['facebook'].get('status')}).")
    video_url = f"{PAGES}/video/{no}.mp4"
    ukuran = cek_video(video_url)
    print(f"Konten : {folder.name} — {judul}")
    print(f"Video  : {video_url} ({ukuran / 1e6:.1f} MB)")
    print(f"Caption ({len(caption)} karakter):\n{'-' * 40}\n{caption}\n{'-' * 40}")
    if not kirim:
        print("Pratinjau saja. Tambahkan --kirim untuk upload sebagai draft.")
        return

    page = env["FB_PAGE_ID"]
    print("1/4 Menyiapkan upload Reels…")
    video_id = graph(env, f"{page}/video_reels", upload_phase="start")["video_id"]
    print("2/4 Facebook mengambil video dari GitHub Pages…")
    panggil(f"https://rupload.facebook.com/video-upload/{env['GRAPH_VERSION']}/{video_id}", {},
            {"Authorization": f"OAuth {env['FB_PAGE_TOKEN']}", "file_url": video_url})
    print("3/4 Menunggu video diproses…")
    for _ in range(60):
        st = graph(env, video_id, fields="status", _get=True).get("status", {})
        if st.get("uploading_phase", {}).get("status") == "error":
            raise SystemExit(f"Upload gagal: {st}")
        if st.get("uploading_phase", {}).get("status") == "complete":
            break
        time.sleep(5)
    else:
        raise SystemExit("Upload lebih dari 5 menit. Coba lagi nanti.")
    print("4/4 Menyimpan sebagai DRAFT…")
    graph(env, f"{page}/video_reels", upload_phase="finish", video_id=video_id,
          video_state="DRAFT", description=caption, title=judul[:250])
    hist["facebook"] = {"video_id": video_id, "status": "draft",
                        "waktu": datetime.now().isoformat(timespec="seconds"),
                        "studio": "https://business.facebook.com/latest/content_management"}
    (folder / "posting.json").write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ Draft Reels tersimpan (video {video_id}). Cek di Meta Business Suite → Konten → Draf.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("no", nargs="?", help="nomor konten, mis. 023")
    ap.add_argument("--kirim", action="store_true", help="benar-benar upload (sebagai draft)")
    ap.add_argument("--antrean", action="store_true", help="pilih konten terbaru yang belum ada di Facebook")
    ap.add_argument("--cek", action="store_true", help="tes token Halaman saja")
    a = ap.parse_args()
    env = env_fb()
    if a.cek or not (a.no or a.antrean):
        info = graph(env, env["FB_PAGE_ID"], fields="name,followers_count", _get=True)
        print(f"Token Halaman OK: {info.get('name')} ({info.get('followers_count', 0)} pengikut)")
        return
    upload(env, antrean() if a.antrean else a.no, a.kirim)


if __name__ == "__main__":
    main()
