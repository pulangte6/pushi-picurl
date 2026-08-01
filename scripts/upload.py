import os, sys, json, argparse, requests

SERVICES = []

def register(name):
    def deco(fn):
        fn.__service_name__ = name
        SERVICES.append((name, fn))
        return fn
    return deco


@register('uguu')
def upload_uguu(file_path):
    """Upload to uguu.se. Returns a direct image URL.

    Note: uguu.se links are temporary (files expire after a few hours).
    """
    url = 'https://uguu.se/upload?output=json'
    with open(file_path, 'rb') as f:
        files = {'files[]': (os.path.basename(file_path), f, 'application/octet-stream')}
        resp = requests.post(url, files=files, headers={'User-Agent': _UA}, timeout=60)

    data = resp.json()
    if not data.get('success'):
        raise RuntimeError(f"uguu.se: {data}")
    files_info = data.get('files', [])
    if not files_info:
        raise RuntimeError(f"uguu.se: no file in response {data}")
    return files_info[0]['url']


@register('litterbox')
def upload_litterbox(file_path):
    """Upload to litterbox.catbox.moe. Returns a direct image URL.

    Note: litterbox links are temporary (default expiry 72h).
    """
    url = 'https://litterbox.catbox.moe/resources/internals/api.php'
    with open(file_path, 'rb') as f:
        files = {'fileToUpload': (os.path.basename(file_path), f, 'application/octet-stream')}
        data = {'reqtype': 'fileupload', 'time': '72h'}
        resp = requests.post(url, files=files, data=data, headers={'User-Agent': _UA}, timeout=60)

    result = resp.text.strip()
    if not result or not result.startswith('http'):
        raise RuntimeError(f"litterbox: unexpected response: {result!r}")
    return result


@register('freeimage')
def upload_freeimage(file_path):
    """Upload to freeimage.host / iili.io. Returns a permanent direct image URL."""
    url = 'https://freeimage.host/api/1/upload'
    with open(file_path, 'rb') as f:
        files = {'source': (os.path.basename(file_path), f, 'application/octet-stream')}
        data = {'key': '6d207e02198a847aa98d0a2a901485a5', 'action': 'upload', 'format': 'json'}
        resp = requests.post(url, files=files, data=data, headers={'User-Agent': _UA}, timeout=60)

    d = resp.json()
    if d.get('status_code') == 200 and d.get('image', {}).get('url'):
        return d['image']['url']
    raise RuntimeError(f"freeimage.host: unexpected response: {resp.text[:300]}")


@register('tucang')
def upload_tucang(file_path):
    """Upload to tucang.cc. Returns a permanent direct image URL (domestic China)."""
    url = 'https://tucang.cc/api/v1/upload'
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
        data = {'token': '1785592303364d851211522244dcabcf9e42e79e397e3'}
        resp = requests.post(url, files=files, data=data, headers={'User-Agent': _UA, 'Referer': 'https://tucang.cc/'}, timeout=60)

    d = resp.json()
    if d.get('success') and d.get('data', {}).get('url'):
        return d['data']['url']
    raise RuntimeError(f"tucang.cc: unexpected response: {resp.text[:300]}")


@register('quax')
def upload_quax(file_path):
    """Upload to qu.ax. Returns a shareable viewer URL (HTML page, not direct image)."""
    url = 'https://qu.ax/upload'
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
        resp = requests.post(url, files=files, headers={'User-Agent': _UA}, timeout=60)

    data = resp.json()
    if not data.get('success'):
        raise RuntimeError(f"qu.ax: {data}")
    files_info = data.get('files', [])
    if not files_info:
        raise RuntimeError(f"qu.ax: no file in response {data}")
    return files_info[0]['url']


_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

DEFAULT_ORDER = ['tucang', 'uguu', 'litterbox', 'freeimage', 'quax']


def upload_image(file_path, service=None):
    """Upload an image and return its public URL.

    service: service id to force. If None, tries services in DEFAULT_ORDER until one succeeds.
    """
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    by_id = {sid: fn for sid, fn in SERVICES}
    order = [service] if service else DEFAULT_ORDER

    last_err = None
    for sid in order:
        if sid not in by_id:
            print(f"ERROR: Unknown service '{sid}'. Available: {list(by_id)}", file=sys.stderr)
            sys.exit(1)
        try:
            url = by_id[sid](file_path)
            if url:
                return sid, url
        except Exception as e:
            last_err = e
            print(f"[{sid}] failed: {e}; trying next...", file=sys.stderr)

    print(f"ERROR: All upload services failed. Last error: {last_err}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Upload images to a free image host')
    parser.add_argument('files', nargs='+', help='Image file paths to upload')
    parser.add_argument('--service', default=None,
                        help='Service id to force ({0}). Default: try in order until one succeeds.'.format(', '.join(DEFAULT_ORDER)))
    parser.add_argument('--json', action='store_true', help='emit JSON on stdout')
    args = parser.parse_args()

    results = []
    for file_path in args.files:
        print(f"Uploading: {file_path}", file=sys.stderr)
        sid, url = upload_image(file_path, args.service)
        print(f"  [{sid}] -> {url}", file=sys.stderr)
        results.append((sid, url))

    if args.json:
        if len(results) == 1:
            print(json.dumps({'url': results[0][1], 'provider': results[0][0]}, ensure_ascii=False))
        else:
            print(json.dumps([{'url': u, 'provider': s} for s, u in results], ensure_ascii=False))
    else:
        for s, u in results:
            print(u)
    print(f"[via {results[-1][0]}]", file=sys.stderr)


if __name__ == '__main__':
    main()

