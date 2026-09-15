# Browser environment · 2026-09-15

Read-only smoke launch with the existing CrossCheck venv:
`timeout 60 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python /home/rayin/Projects/Testing/crosscheck/scripts/verify_engines.py`

- Playwright 1.62.0 (existing CrossCheck venv)
- Chromium 151.0.7922.34
- Firefox 153.0
- WebKit 26.5
- Exit 0. No provisioning changes or cache removal.
- Developer UI checks use Chromium with ANGLE gl-egl, 390×844 first.
- This verifies headless engine launch; it does not establish physical-device performance.
