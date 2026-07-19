#!/usr/bin/env python3
"""Upload an image to one of three configured image hosts, in priority order.

Priority:
  1. freeimage.host (iili.io)  - permanent
  2. litter.catbox.moe          - 24h temporary
  3. uguu.se                    - temporary

Exit 0 with URL printed on stdout on first success.
Exit 1 with error messages on stderr if all fail.
"""
from __future__ import annotations

import argparse
import io
import json
import mimetypes
import os
import sys
import uuid
import urllib.error
import urllib.request

FREEIMAGE_KEY = "6d207e02198a847aa98d0a2a901485a5"
FREEIMAGE_URL = "https://freeimage.host/api/1/upload"
CATBOX_LITTER_URL = "https://litter.catbox.moe/user/api.php"
UGUU_URL = "https://uguu.se/upload"

USER_AGENT = "pushi-picurl/1.0 (Codex skill)"
TIMEOUT = 45  # seconds per attempt


class UploadError(Exception):
    pass


def _multipart(fields, files):
    """Build a multipart/form-data body. Returns (content_type, body_bytes)."""
    boundary = "----picurl" + uuid.uuid4().hex
    buf = io.BytesIO()
    for k, v in fields.items():
        buf.write(f"--{boundary}\r\n".encode())
        buf.write(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        buf.write(str(v).encode() + b"\r\n")
    for name, (fname, content, ctype) in files.items():
        buf.write(f"--{boundary}\r\n".encode())
        buf.write(
            f'Content-Disposition: form-data; name="{name}"; filename="{fname}"\r\n'.encode()
        )
        buf.write(f"Content-Type: {ctype}\r\n\r\n".encode())
        buf.write(content + b"\r\n")
    buf.write(f"--{boundary}--\r\n".encode())
    return f"multipart/form-data; boundary={boundary}", buf.getvalue()


def _post(url, fields, files):
    ctype, body = _multipart(fields, files)
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": ctype, "User-Agent": USER_AGENT},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", "replace")


def upload_freeimage(path, filename, data, ctype):
    resp = _post(
        FREEIMAGE_URL,
        {"key": FREEIMAGE_KEY, "action": "upload", "format": "json"},
        {"source": (filename, data, ctype)},
    )
    d = json.loads(resp)
    if d.get("status_code") == 200 and d.get("image", {}).get("url"):
        return d["image"]["url"], "freeimage.host (permanent)"
    raise UploadError(f"freeimage.host unexpected response: {resp[:300]}")


def upload_catbox_litter(path, filename, data, ctype):
    resp = _post(
        CATBOX_LITTER_URL,
        {"reqtype": "fileupload", "time": "24h"},
        {"fileToUpload": (filename, data, ctype)},
    )
    url = resp.strip()
    if url.startswith("http"):
        return url, "litter.catbox.moe (24h)"
    raise UploadError(f"litter.catbox.moe unexpected response: {resp[:300]}")


def upload_uguu(path, filename, data, ctype):
    resp = _post(UGUU_URL, {}, {"files[]": (filename, data, ctype)})
    d = json.loads(resp)
    if d.get("success") and d.get("files") and d["files"][0].get("url"):
        return d["files"][0]["url"], "uguu.se (temporary)"
    raise UploadError(f"uguu.se unexpected response: {resp[:300]}")


PROVIDERS = [
    ("freeimage.host", upload_freeimage),
    ("litter.catbox.moe", upload_catbox_litter),
    ("uguu.se", upload_uguu),
]


def upload_image(path):
    if not os.path.isfile(path):
        raise UploadError(f"file not found: {path}")
    filename = os.path.basename(path)
    ctype, _ = mimetypes.guess_type(filename)
    if not ctype or not ctype.startswith("image/"):
        ctype = "application/octet-stream"
    with open(path, "rb") as f:
        data = f.read()
    if not data:
        raise UploadError(f"file is empty: {path}")

    errors = []
    for name, fn in PROVIDERS:
        try:
            url, desc = fn(path, filename, data, ctype)
            return url, desc
        except (urllib.error.URLError, urllib.error.HTTPError, UploadError, OSError, ValueError) as e:
            msg = str(e)
            if hasattr(e, "read"):
                try:
                    body = e.read().decode("utf-8", "replace")
                    if body:
                        msg = f"{msg}: {body[:200]}"
                except Exception:
                    pass
            errors.append(f"{name}: {msg}")
            print(f"[pushi-picurl] {name} failed: {msg}", file=sys.stderr)
    raise UploadError("all providers failed:\n  " + "\n  ".join(errors))


def main():
    parser = argparse.ArgumentParser(
        description="Upload an image to a public image host with fallback."
    )
    parser.add_argument("image", help="path to the image file to upload")
    parser.add_argument(
        "--json", action="store_true", help="emit JSON on stdout instead of plain URL"
    )
    args = parser.parse_args()

    try:
        url, provider = upload_image(args.image)
    except UploadError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps({"url": url, "provider": provider}, ensure_ascii=False))
    else:
        print(url)
    print(f"[via {provider}]", file=sys.stderr)


if __name__ == "__main__":
    main()
