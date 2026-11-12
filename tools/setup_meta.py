"""Lengkapi .env untuk Instagram & Facebook setelah IG_ACCESS_TOKEN diisi.

Cukup tempel token dari Graph API Explorer ke IG_ACCESS_TOKEN di .env, lalu:

    python tools/setup_meta.py

Script ini (tanpa memposting apa pun):
  - cek masa berlaku token & izinnya,
  - kalau META_APP_ID + META_APP_SECRET terisi dan token masih jangka pendek,
    tukar jadi token jangka panjang (± 60 hari) dan simpan ke .env,
  - cari Halaman Facebook + akun Instagram yang terhubung, isi FB_PAGE_ID & IG_USER_ID.
Token tidak pernah dicetak ke layar.
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"
PERLU = {"instagram_basic", "instagram_content_publish", "pages_show_list",
         "pages_read_engagement", "pages_manage_posts"}


def baca_env_mentah():
    if not ENV.exists():
        raise SystemExit("File .env belum ada. Salin .env.example jadi .env dulu.")
    env = {}
    for b in ENV.read_text(encoding="utf-8").splitlines():
        b = b.strip()
        if b and not b.startswith("#") and "=" in b:
            k, v = b.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    env.setdefault("GRAPH_VERSION", "v23.0")
    return env


def baca():
    env = baca_env_mentah()
    if not env.get("IG_ACCESS_TOKEN"):
        raise SystemExit("IG_ACCESS_TOKEN masih kosong di .env — tempel token dari Graph API Explorer dulu.")
    return env


def tulis(kunci, nilai):
    """Ganti/ tambah satu baris KUNCI=nilai di .env, baris lain tetap."""
    baris = ENV.read_text(encoding="utf-8").splitlines()
    for i, b in enumerate(baris):
        if b.split("=", 1)[0].strip() == kunci:
            baris[i] = f"{kunci}={nilai}"
            break
    else:
        baris.append(f"{kunci}={nilai}")
    ENV.write_text("\n".join(baris) + "\n", encoding="utf-8")


def get(env, path, **params):
    params.setdefault("access_token", env["IG_ACCESS_TOKEN"])
    if not params["access_token"]:
        del params["access_token"]
    url = f"https://graph.facebook.com/{env['GRAPH_VERSION']}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            pesan = json.loads(e.read()).get("error", {}).get("message", e.reason)
        except Exception:
            pesan = e.reason
        raise SystemExit(f"API Meta menolak ({e.code}): {pesan}") from None


def main():
    env = baca()
    info = get(env, "debug_token", input_token=env["IG_ACCESS_TOKEN"])["data"]
    if not info.get("is_valid"):
        raise SystemExit("Token tidak valid / sudah kedaluwarsa. Generate ulang di Graph API Explorer.")
    izin = set(info.get("scopes", []))
    habis = info.get("expires_at") or 0
    print(f"Token valid untuk app {info.get('application')}.")

    if habis and habis - datetime.now().timestamp() < 3 * 86400:
        if env.get("META_APP_ID") and env.get("META_APP_SECRET"):
            baru = get(env, "oauth/access_token", grant_type="fb_exchange_token",
                       client_id=env["META_APP_ID"], client_secret=env["META_APP_SECRET"],
                       fb_exchange_token=env["IG_ACCESS_TOKEN"], access_token="")
            tulis("IG_ACCESS_TOKEN", baru["access_token"])
            env["IG_ACCESS_TOKEN"] = baru["access_token"]
            habis = get(env, "debug_token", input_token=baru["access_token"])["data"].get("expires_at") or 0
            print("Token ditukar jadi jangka panjang dan disimpan ke .env.")
        else:
            print("⚠ Token ini jangka pendek (± 1 jam). Klik ⓘ → Open in Access Token Tool → "
                  "Extend Access Token, lalu tempel token barunya ke .env.")
    print("Berlaku sampai:", datetime.fromtimestamp(habis).strftime("%d %b %Y %H:%M") if habis else "tidak kedaluwarsa")

    kurang = PERLU - izin
    if kurang:
        print("⚠ Izin yang belum dicentang:", ", ".join(sorted(kurang)))

    halaman = get(env, "me/accounts", fields="id,name,instagram_business_account{id,username}").get("data", [])
    if not halaman:
        raise SystemExit("Tidak ada Halaman Facebook yang diizinkan untuk token ini. Saat Generate Access Token, "
                         "centang Halaman Ngomongin Sejarah & akun Instagram-nya.")
    for h in halaman:
        print(f"  Halaman: {h['name']} ({h['id']})  IG: {h.get('instagram_business_account', {}).get('username', '-')}")
    pilih = next((h for h in halaman if h.get("instagram_business_account")), halaman[0])
    tulis("FB_PAGE_ID", pilih["id"])
    ig = pilih.get("instagram_business_account")
    if ig:
        tulis("IG_USER_ID", ig["id"])
        print(f"✓ .env diisi: FB_PAGE_ID ({pilih['name']}) & IG_USER_ID (@{ig['username']})")
    else:
        print(f"✓ FB_PAGE_ID diisi ({pilih['name']}), tapi Halaman ini belum terhubung ke akun Instagram "
              "Profesional. Hubungkan dulu di IG → Edit profil → Halaman, lalu jalankan lagi.")


if __name__ == "__main__":
    main()
