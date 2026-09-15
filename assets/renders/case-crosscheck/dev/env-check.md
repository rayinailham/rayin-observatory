# Browser environment — 2026-09-15

Skill: arch-playwright-provision. Existing CrossCheck Python Playwright environment reused.
`timeout 60 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python /home/rayin/Projects/Testing/crosscheck/scripts/verify_engines.py` → exit 0:

- Chromium 151.0.7922.34
- Firefox 153.0
- WebKit 26.5

No packages or browser revisions changed; no additional library patches needed. Case development
checks use headless Chromium with ANGLE gl-egl. Engine launch is not cross-browser site acceptance.
