"""Login Facebook/Instagram sekali, token langsung tersimpan di .env (tanpa copy-paste token).

Syarat: META_APP_ID dan META_APP_SECRET sudah terisi di .env
(App secret: developers.facebook.com → app → App settings → Basic → App secret → Show).

    python tools/login_meta.py

Browser terbuka ke halaman izin Facebook → klik Lanjutkan, pilih Halaman & akun IG
Ngomongin Sejarah → selesai. Script lalu:
  - menukar kode login jadi token jangka panjang (± 60 hari),
  - menyimpan IG_ACCESS_TOKEN, FB_PAGE_ID, FB_PAGE_TOKEN, IG_USER_ID ke .env.
Token tidak pernah dicetak ke layar.
"""

import http.server
import json
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).parent))
from setup_meta import baca_env_mentah, tulis  # noqa: E402

PORT = 8765
REDIRECT = f"http://localhost:{PORT}/"
IZIN = ["instagram_basic", "instagram_content_publish", "pages_show_list",
        "pages_read_engagement", "pages_manage_posts", "business_management"]


def graph(versi, path, **params):
    url = f"https://graph.facebook.com/{versi}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            pesan = json.loads(e.read()).get("error", {}).get("message", e.reason)
        except Exception:
            pesan = e.reason
        raise SystemExit(f"API Meta menolak ({e.code}): {pesan}") from None


def tunggu_kode(state):
    hasil = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" not in q and "error" not in q:
                self.send_response(404)
                self.end_headers()
                return
            hasil.update({k: v[0] for k, v in q.items()})
            ok = "code" in q and q.get("state", [""])[0] == state
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            pesan = ("✅ Login berhasil. Tab ini boleh ditutup, kembali ke Claude." if ok
                     else "❌ Login gagal / dibatalkan. Tab ini boleh ditutup.")
            self.wfile.write(f"<h2 style='font-family:sans-serif'>{pesan}</h2>".encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("localhost", PORT), H)
    while not hasil:
        srv.handle_request()
    srv.server_close()
    return hasil


def main():
    env = baca_env_mentah()
    versi = env.get("GRAPH_VERSION", "v23.0")
    app_id, secret = env.get("META_APP_ID"), env.get("META_APP_SECRET")
    if not app_id or not secret:
        raise SystemExit("Isi dulu META_APP_ID dan META_APP_SECRET di .env "
                         "(App settings → Basic → App secret → Show).")

    state = secrets.token_urlsafe(16)
    url = f"https://www.facebook.com/{versi}/dialog/oauth?" + urllib.parse.urlencode({
        "client_id": app_id, "redirect_uri": REDIRECT, "state": state,
        "response_type": "code", "scope": ",".join(IZIN)})
    print("Membuka browser untuk login Facebook…\nKalau tidak terbuka, buka link ini manual:\n" + url)
    webbrowser.open(url)

    q = tunggu_kode(state)
    if q.get("state") != state or "code" not in q:
        raise SystemExit(f"Login dibatalkan / gagal: {q.get('error_description') or q.get('error') or 'state tidak cocok'}")

    pendek = graph(versi, "oauth/access_token", client_id=app_id, client_secret=secret,
                   redirect_uri=REDIRECT, code=q["code"])["access_token"]
    panjang = graph(versi, "oauth/access_token", grant_type="fb_exchange_token", client_id=app_id,
                    client_secret=secret, fb_exchange_token=pendek)["access_token"]
    tulis("IG_ACCESS_TOKEN", panjang)
    print("✓ Token jangka panjang disimpan ke .env")

    halaman = graph(versi, "me/accounts", access_token=panjang,
                    fields="id,name,access_token,instagram_business_account{id,username}").get("data", [])
    if not halaman:
        raise SystemExit("Tidak ada Halaman yang diizinkan. Ulangi login dan centang Halaman Ngomongin Sejarah.")
    pilih = next((h for h in halaman if h.get("instagram_business_account")), halaman[0])
    tulis("FB_PAGE_ID", pilih["id"])
    tulis("FB_PAGE_TOKEN", pilih["access_token"])  # dari token jangka panjang → tidak kedaluwarsa
    print(f"✓ Halaman Facebook: {pilih['name']}")
    ig = pilih.get("instagram_business_account")
    if ig:
        tulis("IG_USER_ID", ig["id"])
        print(f"✓ Akun Instagram: @{ig['username']}")
    else:
        print("⚠ Halaman ini belum terhubung ke akun Instagram Profesional "
              "(IG → Edit profil → Halaman), lalu jalankan lagi.")


if __name__ == "__main__":
    main()
