"""Upload video Shorts ke Instagram Reels lewat Instagram Graph API (resmi Meta).

Video diambil dari GitHub Pages (harus sudah ter-deploy), caption dari bagian
"## Instagram Reels" di konten/<NNN>-*/caption.md.

Setup sekali: lihat docs/SETUP-INSTAGRAM.md, lalu isi .env (contoh: .env.example).

    python tools/upload_ig.py --cek          # tes token & akun, tidak memposting apa pun
    python tools/upload_ig.py 004            # pratinjau: tampilkan yang akan diposting
    python tools/upload_ig.py 004 --kirim    # benar-benar posting ke Reels
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

sys.path.insert(0, str(Path(__file__).parent))
from buat_app import parse_caption  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAGES = "https://nurqoneah.github.io/ngomongin-sejarah"


def baca_env():
    env = {}
    f = ROOT / ".env"
    if not f.exists():
        raise SystemExit("File .env belum ada. Salin .env.example jadi .env lalu isi IG_USER_ID & IG_ACCESS_TOKEN.")
    for baris in f.read_text(encoding="utf-8").splitlines():
        baris = baris.strip()
        if baris and not baris.startswith("#") and "=" in baris:
            k, v = baris.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("IG_USER_ID", "IG_ACCESS_TOKEN"):
        if not env.get(k):
            raise SystemExit(f"{k} kosong di .env")
    env.setdefault("GRAPH_VERSION", "v23.0")
    return env


def graph(env, metode, path, **params):
    params["access_token"] = env["IG_ACCESS_TOKEN"]
    url = f"https://graph.facebook.com/{env['GRAPH_VERSION']}/{path}"
    data = urllib.parse.urlencode(params).encode()
    if metode == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read()).get("error", {})
        except Exception:
            err = {}
        raise SystemExit(f"API Instagram menolak ({e.code}): {err.get('message', e.reason)}") from None


def cari_konten(no):
    cocok = sorted((ROOT / "konten").glob(f"{no}-*"))
    if not cocok:
        raise SystemExit(f"Folder konten {no}-* tidak ditemukan")
    folder = cocok[0]
    data = parse_caption((folder / "caption.md").read_text(encoding="utf-8"))
    ig = next((p for p in data["platform"] if p["nama"].startswith("Instagram")), None)
    if not ig or not ig["isian"]:
        raise SystemExit(f"Caption Instagram tidak ada di {folder.name}/caption.md")
    return folder, data["judul"], ig["isian"][0]["teks"]


def cek_video(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
            return int(r.headers.get("Content-Length", 0))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Video belum ada di GitHub Pages ({e.code}): {url}\n"
                         "Pastikan sudah di-push dan workflow Pages selesai.") from None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("no", nargs="?", help="nomor konten, mis. 004")
    ap.add_argument("--kirim", action="store_true", help="benar-benar posting (tanpa ini cuma pratinjau)")
    ap.add_argument("--cek", action="store_true", help="tes token & akun saja")
    ap.add_argument("--tanpa-feed", action="store_true", help="jangan tampilkan juga di grid feed")
    a = ap.parse_args()
    env = baca_env()

    if a.cek or not a.no:
        akun = graph(env, "GET", env["IG_USER_ID"], fields="username,name,media_count")
        print(f"Token OK. Akun: @{akun.get('username')} ({akun.get('media_count', 0)} postingan)")
        return

    folder, judul, caption = cari_konten(a.no)
    video_url = f"{PAGES}/video/{a.no}.mp4"
    log = folder / "posting.json"
    riwayat = json.loads(log.read_text(encoding="utf-8")) if log.exists() else {}
    if "instagram" in riwayat:
        raise SystemExit(f"{folder.name} sudah pernah diposting ke Instagram: {riwayat['instagram'].get('permalink')}")

    ukuran = cek_video(video_url)
    print(f"Konten : {folder.name} — {judul}")
    print(f"Video  : {video_url} ({ukuran / 1e6:.1f} MB)")
    print(f"Caption ({len(caption)} karakter):\n{'-' * 40}\n{caption}\n{'-' * 40}")
    if len(caption) > 2200:
        raise SystemExit("Caption lebih dari 2200 karakter, potong dulu di caption.md")
    if not a.kirim:
        print("Pratinjau saja. Tambahkan --kirim untuk posting.")
        return

    print("1/3 Mengirim video ke Instagram…")
    wadah = graph(env, "POST", f"{env['IG_USER_ID']}/media", media_type="REELS", video_url=video_url,
                  caption=caption, share_to_feed="false" if a.tanpa_feed else "true")["id"]
    print("2/3 Menunggu Instagram memproses video…")
    for _ in range(60):
        st = graph(env, "GET", wadah, fields="status_code,status")
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Instagram gagal memproses video: {st.get('status')}")
        time.sleep(10)
    else:
        raise SystemExit("Proses video lebih dari 10 menit. Coba lagi nanti (belum diposting).")
    print("3/3 Mempublikasikan…")
    media_id = graph(env, "POST", f"{env['IG_USER_ID']}/media_publish", creation_id=wadah)["id"]
    info = graph(env, "GET", media_id, fields="permalink,timestamp")
    riwayat["instagram"] = {"media_id": media_id, "permalink": info.get("permalink"),
                            "waktu": info.get("timestamp") or datetime.now().isoformat(timespec="seconds")}
    log.write_text(json.dumps(riwayat, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Tayang! {info.get('permalink')}")
    print("Jangan lupa: tambahkan label 'Dibuat dengan AI' manual di aplikasi IG (tidak tersedia lewat API).")


if __name__ == "__main__":
    main()
