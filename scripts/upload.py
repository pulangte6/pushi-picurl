import os
import sys
import json
import argparse
import requests

def upload_image_quax(file_path, title=None):
    """Upload image to qu.ax and get URL."""
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
        data = {}
        if title:
            data['title'] = title

        resp = requests.post('https://qu.ax/upload', files=files, data=data, timeout=60)

    if resp.status_code != 200:
        print(f"ERROR: HTTP {resp.status_code}", file=sys.stderr)
        print(resp.text, file=sys.stderr)
        sys.exit(1)

    result = resp.json()
    if not result.get('success'):
        print(f"ERROR: {result}", file=sys.stderr)
        sys.exit(1)

    return result['files'][0]['url']


def main():
    parser = argparse.ArgumentParser(description='Upload images to qu.ax')
    parser.add_argument('files', nargs='+', help='Image file paths to upload')
    parser.add_argument('--title', default=None, help='Title for the image')
    args = parser.parse_args()

    urls = []
    for file_path in args.files:
        print(f"Uploading: {file_path}")
        url = upload_image_quax(file_path, args.title)
        print(f"  -> {url}")
        urls.append(url)

    print("\nDone!")
    for u in urls:
        print(u)


if __name__ == '__main__':
    main()