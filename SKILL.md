---
name: pushi-picurl
description: "Upload images to image hosting services (qu.ax) and generate public image links. Use when Codex needs to upload an image file to get a shareable URL, embed images in documentation/messages, or provide a direct image link. Triggers on: upload image, generate image link, get image URL, share image online, image hosting, send image link, picurl, picture url."
---

# Image Upload Skill

Upload images and get public/shareable links. Uses qu.ax as the upload service.

## Quick Start

```powershell
# Upload a local image file
python scripts/upload.py "C:\path\to\image.png"

# Upload with a custom title
python scripts/upload.py "C:\path\to\image.jpg" --title "My Photo"

# Upload multiple images at once
python scripts/upload.py "C:\path\to\img1.png" "C:\path\to\img2.png"
```

## Output

The script prints the image URL to stdout. Example:

```
https://qu.ax/4a9fP
```

## Notes

- Default service: **qu.ax** (free, no registration needed, permanent links)
- Supports PNG, JPG, GIF, BMP, WEBP formats
- Max file size: ~5 MB for qu.ax
- Links are public and accessible via the returned URL
