---
name: pushi-picurl
description: "Upload a local image to a public image host and return a direct URL. Use when Codex needs to turn a local image file into an online link, host a screenshot/PNG/JPG/GIF online, publish a generated image for sharing or embedding, or get a public URL for a local picture. Providers are tried in priority order: freeimage.host (iili.io, permanent) → litter.catbox.moe (24h temporary) → uguu.se (temporary). Returns failure only when all three fail. Triggers on: upload image, image to link, image to url, host image, image hosting, 上传图片, 图床, 图片链接, 图片转链接, 上传图床."
---

# pushi-picurl

Upload a local image to one of three free public image hosts, in fixed priority order.
Return the first URL that succeeds.

## Priority order (failover chain)

1. `freeimage.host` / `iili.io` — permanent storage (preferred)
2. `litter.catbox.moe` — temporary, ~24 hours
3. `uguu.se` — temporary, auto-expires

If provider N fails (network error, HTTP error, unexpected response, oversize),
automatically fall through to provider N+1. Only fail when all three fail.

## Usage

Run the bundled script via Python 3 (uses only stdlib, no pip dependencies):

```bash
python <skill_dir>/scripts/upload.py <path/to/image.png>
```

Stdout prints the resulting public URL on success.
Stderr logs which provider was used, plus any per-provider errors.
Exit code `0` on success, `1` if all providers fail.

### Flags

- `--json` — emit a single JSON object on stdout: `{"url": "...", "provider": "..."}`

### Examples

```bash
# plain URL
python scripts/upload.py ./screenshot.png
# → https://iili.io/xxxx.png

# JSON output
python scripts/upload.py ./diagram.jpg --json
# → {"url": "https://d.uguu.se/xxxx.png", "provider": "uguu.se (temporary)"}
```

## How to use from a task

When the user asks to upload an image / get a public link / host a picture:

1. Resolve the absolute path of the local image. Confirm the file exists and is a supported image type (PNG, JPG, GIF, BMP, WebP, etc.).
2. Invoke the script with `shell_command`, e.g.
   `python <skill_dir>/scripts/upload.py "<absolute_path>"`
   using the absolute path to this skill's `scripts/upload.py`.
3. If exit code is 0, capture stdout as the URL and report it. Note which provider was used (the `[via …]` line on stderr), especially if a temporary host was chosen instead of the permanent one — warn the user that the link is temporary.
4. If exit code is 1, report failure and surface the stderr error list. Do not fabricate URLs.

## Notes

- Pure Python 3 stdlib (`urllib`); no third-party packages required.
- Default timeout is 45 seconds per provider.
- The first provider (`freeimage.host`) is the only one that guarantees permanent links; the other two are ephemeral fallbacks. Always prefer a successful permanent URL.
- For very large images (> a few MB) some providers may reject with 413; the script will automatically fall through to the next provider.
