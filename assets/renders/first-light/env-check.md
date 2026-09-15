# First light browser environment

2026-09-15 · Codex. Existing CrossCheck Python environment; no install or library changes.

```sh
timeout 60 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python /home/rayin/Projects/Testing/crosscheck/scripts/verify_engines.py
```

Exit 0:

```text
chromium: 151.0.7922.34
firefox: 153.0
webkit: 26.5
```

All three engines launched headless. Website flow tests use Chromium mobile emulation.
This is not the cross-browser website QA phase, and no physical-device performance is claimed.
