# pushi-picurl

Codex skill: upload a local image to a public image host and return a direct URL.

## Providers (priority order with failover)

1. **freeimage.host / iili.io** — permanent storage (preferred)
2. **litter.catbox.moe** — temporary (~24 hours)
3. **uguu.se** — temporary (auto-expires)

If provider N fails, automatically fall through to N+1. Only fails when all three fail.

## Requirements

- Python 3 (stdlib only, no pip dependencies)

## CLI usage

```bash
python scripts/upload.py <path/to/image.png>         # prints URL to stdout
python scripts/upload.py <path/to/image.png> --json  # prints {"url": "...", "provider": "..."}
```

Exit code `0` on success (URL on stdout), `1` if all providers fail (errors on stderr).

## Install as a Codex skill

Copy (or symlink) this folder into `~/.codex/skills/pushi-picurl/`. Codex will auto-discover it and use it when the user asks to upload/host an image or turn a local picture into a public link.

## Related

- [`pushi-videogen`](https://github.com/zhaochong/pushi-videogen) — AI video generation skill
