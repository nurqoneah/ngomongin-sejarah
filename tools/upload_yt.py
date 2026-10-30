"""Upload video Shorts ke YouTube lewat YouTube Data API v3 (resmi Google).

Default-nya PRIVATE (jadi "draft" yang bisa dicek dulu di YouTube Studio).
Judul, deskripsi, dan tag diambil dari bagian "## YouTube Shorts" di caption.md.

Setup sekali: docs/SETUP-YOUTUBE.md (file client_secret_youtube.json + login pertama).

    python tools/upload_yt.py --cek                   # login / tes akses channel
    python tools/upload_yt.py 015                     # pratinjau metadata, tidak upload
    python tools/upload_yt.py 015 --kirim             # upload sebagai PRIVATE
    python tools/upload_yt.py 015 --kirim --jadwal "2026-11-02 18:00"
                                                      # terjadwal tayang (butuh project lolos audit)
    python tools/upload_yt.py --antrean --kirim       # upload 1 konten berikutnya yang belum ada di YouTube
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # emoji di caption aman di terminal Windows
sys.path.insert(0, str(Path(__file__).parent))
from buat_app import parse_caption  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAHASIA = ROOT / "client_secret_youtube.json"
TOKEN = ROOT / "token_youtube.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
WIB = timezone(timedelta(hours=7))


def layanan():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    if not RAHASIA.exists():
        raise SystemExit(f"{RAHASIA.name} belum ada. Ikuti docs/SETUP-YOUTUBE.md langkah 1–4.")
    cred = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if cred and cred.expired and cred.refresh_token:
        try:
            cred.refresh(Request())
        except Exception:
            cred = None  # refresh token kedaluwarsa/dicabut -> login ulang
    if not cred or not cred.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(RAHASIA), SCOPES)
        print("Browser akan terbuka: login pakai akun Google pemilik channel, lalu izinkan.")
        cred = flow.run_local_server(port=0, prompt="consent")
    TOKEN.write_text(cred.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=cred, cache_discovery=False)


def metadata(folder):
    data = parse_caption((folder / "caption.md").read_text(encoding="utf-8"))
    yt = next((p for p in data["platform"] if p["nama"].startswith("YouTube")), None)
    if not yt:
        raise SystemExit(f"Bagian YouTube tidak ada di {folder.name}/caption.md")
    isi = {f["label"]: f["teks"] for f in yt["isian"]}
    judul = isi.get("Judul", data["judul"]).strip()
    if "#shorts" not in judul.lower() and len(judul) <= 92:
        judul += " #Shorts"
    tag = [t.strip() for t in isi.get("Tag", "").split(",") if t.strip()]
    return judul[:100], isi.get("Deskripsi", "").strip(), tag


def cari_folder(no):
    cocok = sorted((ROOT / "konten").glob(f"{no}-*"))
    if not cocok:
        raise SystemExit(f"Folder konten {no}-* tidak ditemukan")
    return cocok[0]


def riwayat(folder):
    log = folder / "posting.json"
    return json.loads(log.read_text(encoding="utf-8")) if log.exists() else {}


def antrean_berikutnya():
    for folder in sorted((ROOT / "konten").iterdir()):
        if not (folder / "caption.md").exists() or not list((folder / "shorts").glob("*.mp4")):
            continue
        if (folder / "TAHAN").exists() or "youtube" in riwayat(folder):
            continue
        return folder
    return None


def upload(folder, kirim, jadwal=None):
    from googleapiclient.http import MediaFileUpload

    if "youtube" in riwayat(folder):
        raise SystemExit(f"{folder.name} sudah ada di YouTube: {riwayat(folder)['youtube'].get('url')}")
    video = sorted((folder / "shorts").glob("*.mp4"))[0]
    judul, deskripsi, tag = metadata(folder)
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}
    if jadwal:
        waktu = datetime.strptime(jadwal, "%Y-%m-%d %H:%M").replace(tzinfo=WIB)
        status["publishAt"] = waktu.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    print(f"Konten   : {folder.name}")
    print(f"Video    : {video.name} ({video.stat().st_size / 1e6:.1f} MB)")
    print(f"Judul    : {judul} ({len(judul)}/100)")
    print(f"Tag      : {', '.join(tag)}")
    print(f"Status   : private" + (f", tayang otomatis {jadwal} WIB" if jadwal else " (draft)"))
    print(f"Deskripsi:\n{deskripsi}\n")
    if not kirim:
        print("Pratinjau saja. Tambahkan --kirim untuk upload.")
        return

    yt = layanan()
    body = {"snippet": {"title": judul, "description": deskripsi, "tags": tag, "categoryId": "27",
                        "defaultLanguage": "id", "defaultAudioLanguage": "id"},
            "status": status}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(video), chunksize=8 * 1024 * 1024, resumable=True))
    hasil = None
    while hasil is None:
        prog, hasil = req.next_chunk()
        if prog:
            print(f"\r  upload {prog.progress() * 100:5.1f}%", end="", flush=True)
    vid = hasil["id"]
    url = f"https://youtube.com/shorts/{vid}"
    r = riwayat(folder)
    r["youtube"] = {"video_id": vid, "url": url, "status": "private", "jadwal": jadwal,
                    "waktu_upload": datetime.now(WIB).isoformat(timespec="seconds")}
    (folder / "posting.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nTer-upload (private): {url}")
    print(f"Edit / publikasikan: https://studio.youtube.com/video/{vid}/edit")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("no", nargs="?", help="nomor konten, mis. 015")
    ap.add_argument("--kirim", action="store_true", help="benar-benar upload (tanpa ini cuma pratinjau)")
    ap.add_argument("--cek", action="store_true", help="login & tampilkan channel")
    ap.add_argument("--antrean", action="store_true", help="ambil konten berikutnya yang belum ada di YouTube")
    ap.add_argument("--jadwal", help='waktu tayang WIB "YYYY-MM-DD HH:MM" (butuh project lolos audit)')
    a = ap.parse_args()

    if a.cek:
        ch = layanan().channels().list(part="snippet,statistics", mine=True).execute().get("items", [])
        if not ch:
            raise SystemExit("Akun ini belum punya channel YouTube.")
        s = ch[0]
        print(f"OK. Channel: {s['snippet']['title']} · {s['statistics'].get('videoCount', 0)} video")
        return
    if a.antrean:
        folder = antrean_berikutnya()
        if not folder:
            print("Semua konten sudah ada di YouTube.")
            return
    elif a.no:
        folder = cari_folder(a.no)
    else:
        ap.print_help()
        return
    upload(folder, a.kirim, a.jadwal)


if __name__ == "__main__":
    main()
