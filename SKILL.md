---
name: pushi-picurl
description: "Upload images to image hosting services and generate public image links. Uses tucang.cc (direct image URL, permanent, CN) by default, with uguu.se, litterbox, qu.ax as fallbacks. Use when Codex needs to upload an image file to get a shareable URL, embed images in documentation/messages, or provide a direct image link. Triggers on: upload image, generate image link, get image URL, share image online, image hosting, send image link, picurl, picture url."
---

# Image Upload Skill

Upload images and get public/shareable links. Multiple free hosting services are
supported, tried in priority order until one succeeds.

## Supported Services

| Service   | Priority | Returns               | Persistence        |
|-----------|----------|-----------------------|--------------------|
| tucang.cc | primary  | direct image URL      | permanent (CN)     |
| uguu.se   | 2nd      | direct image URL      | temporary (~hours)  |
| litterbox | 3rd      | direct image URL      | temporary (72h)    |
| qu.ax     | fallback | viewer page URL       | permanent           |

- **tucang.cc**: returns a permanent direct image URL (国内图床). Best choice for CN users.
- **uguu.se**: returns a direct link to the image bytes (e.g. `https://n.uguu.se/abc.png`), best for embedding via Markdown image syntax. Links expire after a few hours.
- **litterbox** (litterbox.catbox.moe): returns a direct link to the image bytes (e.g. `https://litter.catbox.moe/abc.png`). Links expire after 72 hours.
- **qu.ax**: returns a permanent viewer page (HTML). Good for long-lived sharing; for direct embedding, prefer tucang or uguu.

## Quick Start

```bash
# Upload a local image file (uses tucang.cc first, then uguu, then litterbox, then qu.ax)
python3 scripts/upload.py "/path/to/image.png"

# Force a specific service
python3 scripts/upload.py "/path/to/image.jpg" --service uguu

# Upload multiple images at once
python3 scripts/upload.py "/path/to/img1.png" "/path/to/img2.png"
```

## Output

The script prints the chosen service and the image URL to stdout, one per line at the end:

```
Uploading: /path/to/image.png
  [tucang] -> https://tucang.cc/abc.png

Done!
https://tucang.cc/abc.png
```

## Notes

- Default order: **tucang** → **uguu** → **litterbox** → **quax** (first success wins). Override with `--service`.
- Supports PNG, JPG, GIF, BMP, WEBP formats.
- uguu.se and litterbox links are **temporary**; use `--service tucang` for permanent links (CN).
- Max file size: ~5 MB for qu.ax; ~128 MB for uguu.se; ~1 GB for litterbox; varies for tucang.cc.
- All returned links are public.

## Adding More Services

Edit `scripts/upload.py` and register a new function with `@register('id')`. It should
take a file path and return the public URL (raise an exception on failure). Then add the
new id to `DEFAULT_ORDER`.
