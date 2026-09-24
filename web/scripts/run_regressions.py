"""Q42 regression runner: one GPU, suites in sequence, nothing re-run without a reason.

Each suite that passes is recorded in assets/renders/regression-ledger.json with a fingerprint of the site
source (web/app, web/components, web/lib, web/public, package-lock, next config). A suite that already passed
on the same fingerprint is skipped — so Testing does not repeat what Development proved on the same code,
and after a fix only the suites not yet green on the new code run. --force re-runs anyway.
--phone-only runs the listed older-phase suites on 390x844 only (OBSERVATORY_PHONES); a phone-only pass
does not satisfy a later full run. Refuses to start when the production build is older than the source.

Run from the project root with the production preview on :8767:
  /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/run_regressions.py [--suites room,case] [--phone-only mobile,case,cases,showpiece] [--force] [--list]
Exit 1 when a suite fails.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / 'web'
SCRIPTS = WEB / 'scripts'
PY = '/home/rayin/Projects/Testing/crosscheck/.venv/bin/python'
LEDGER = ROOT / 'assets/renders/regression-ledger.json'
URL = os.environ.get('OBSERVATORY_URL', 'http://127.0.0.1:8767').rstrip('/')
SOURCES = [WEB / 'app', WEB / 'components', WEB / 'lib', WEB / 'public', WEB / 'package-lock.json', WEB / 'next.config.ts']
BIG = 5_000_000  # videos: size + mtime instead of reading every byte

# name: (command, cwd, timeout s, result JSON relative to ROOT or None, phones env honoured, copy JSON to)
SUITES = {
    'studio': ([PY, 'verify_brandwall_room.py'], SCRIPTS, 900, 'assets/renders/personal-brandwall/dev/verification.json', True, None),
    'perf-brandwall': ([PY, 'perf_quick.py', '--slug', 'brandwall'], SCRIPTS, 600, 'assets/renders/perf-quick/brandwall.json', False, None),
    'time': ([PY, 'verify_duewatch_room.py'], SCRIPTS, 900, 'assets/renders/personal-duewatch/dev/verification.json', True, None),
    'time-state': (['node', 'verify_duewatch_state.mjs'], SCRIPTS, 60, None, False, None),
    'perf-duewatch': ([PY, 'perf_quick.py', '--slug', 'duewatch'], SCRIPTS, 600, 'assets/renders/perf-quick/duewatch.json', False, None),
    'monitor': ([PY, 'verify_driftwatch_room.py'], SCRIPTS, 900, 'assets/renders/personal-driftwatch/dev/verification.json', True, None),
    'perf-driftwatch': ([PY, 'perf_quick.py', '--slug', 'driftwatch'], SCRIPTS, 600, 'assets/renders/perf-quick/driftwatch.json', False, None),
    'dispatch': ([PY, 'verify_surgeline_room.py'], SCRIPTS, 900, 'assets/renders/personal-surgeline/dev/verification.json', True, None),
    'perf-surgeline': ([PY, 'perf_quick.py', '--slug', 'surgeline'], SCRIPTS, 600, 'assets/renders/perf-quick/surgeline.json', False, None),
    'room': ([PY, 'verify_crosscheck_room.py'], SCRIPTS, 900, 'assets/renders/personal-crosscheck/dev/verification.json', True, None),
    'audio': (['node', 'verify_audio.mjs'], SCRIPTS, 300, 'assets/renders/showpiece/dev/audio-verification.json', False, None),
    'mobile': ([PY, 'verify_mobile.py'], SCRIPTS, 420, 'assets/renders/full-observatory/dev/verification.json', True, None),
    'case': ([PY, 'verify_case.py'], SCRIPTS, 300, 'assets/renders/case-crosscheck/dev/verification.json', True, None),
    'cases': ([PY, 'verify_cases.py'], SCRIPTS, 900, 'assets/renders/case-files/dev/verification.json', True, None),
    'showpiece': ([PY, 'verify_showpiece.py'], SCRIPTS, 600, 'assets/renders/showpiece/dev/verification.json', True, None),
    'desktop-a': ([PY, 'verify_desktop.py', '--sizes', '390x844,1366x768'], SCRIPTS, 900, 'assets/renders/desktop/dev/verification.json', False,
                  'assets/renders/desktop/dev/verification-390-1366.json'),
    'desktop-b': ([PY, 'verify_desktop.py', '--sizes', '1440x900,1920x1080'], SCRIPTS, 900, 'assets/renders/desktop/dev/verification.json', False, None),
    'perf-crosscheck': ([PY, 'perf_quick.py', '--slug', 'crosscheck'], SCRIPTS, 600, 'assets/renders/perf-quick/crosscheck.json', False, None),
}


def files():
    for source in SOURCES:
        if source.is_file():
            yield source
        elif source.is_dir():
            yield from sorted(p for p in source.rglob('*') if p.is_file())


def fingerprint():
    digest = hashlib.sha256()
    newest = 0.0
    for path in files():
        stat = path.stat()
        newest = max(newest, stat.st_mtime)
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(f'{stat.st_size}:{stat.st_mtime_ns}'.encode() if stat.st_size > BIG else path.read_bytes())
    return digest.hexdigest()[:16], newest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--suites', default=','.join(SUITES))
    parser.add_argument('--phone-only', default='')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args()
    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
    print_, now = fingerprint()
    build = WEB / '.next/BUILD_ID'
    names = [n for n in args.suites.split(',') if n]
    phone_only = {n for n in args.phone_only.split(',') if n}
    unknown = [n for n in names + sorted(phone_only) if n not in SUITES]
    if unknown:
        sys.exit(f'unknown suites: {unknown}; known: {list(SUITES)}')
    if args.list:
        for name in SUITES:
            entry = ledger.get(name, {})
            state = 'current' if entry.get('fingerprint') == print_ and entry.get('status') == 'passed' else 'stale'
            print(f"{name:16} {state:8} {entry.get('status', '-'):7} {entry.get('phones', '-'):5} {entry.get('finishedAt', '-')}")
        return 0
    if not build.exists() or build.stat().st_mtime < now:
        sys.exit('build is older than the source: run `npm run build --prefix web` and restart the preview first')
    try:
        urllib.request.urlopen(URL, timeout=10)
    except OSError as error:
        sys.exit(f'preview not reachable at {URL}: {error}')

    results = []
    for name in names:
        command, cwd, timeout, report, phones_env, copy_to = SUITES[name]
        phones = 'one' if name in phone_only and phones_env else 'full'
        entry = ledger.get(name, {})
        if not args.force and entry.get('status') == 'passed' and entry.get('fingerprint') == print_ and (entry.get('phones') == 'full' or phones == 'one'):
            print(f'SKIP {name}: already passed on source {print_} ({entry.get("finishedAt")})', flush=True)
            results.append((name, 'skipped'))
            continue
        env = dict(os.environ, OBSERVATORY_URL=URL)
        if phones == 'one':
            env['OBSERVATORY_PHONES'] = '390x844'
            if name == 'room':
                command = [*command, '--sizes', '390x844']
        print(f'RUN  {name} ({phones} phones)', flush=True)
        started = time.time()
        try:
            code = subprocess.run(['timeout', str(timeout), *command], cwd=cwd, env=env).returncode
        except OSError as error:
            print(error)
            code = 127
        status = 'passed' if code == 0 else 'failed'
        if report and (ROOT / report).exists():
            data = json.loads((ROOT / report).read_text())
            if isinstance(data, dict) and data.get('status') not in (None, 'passed'):
                status = 'failed'
            if copy_to and status == 'passed':
                shutil.copy(ROOT / report, ROOT / copy_to)
        ledger[name] = {'fingerprint': print_, 'status': status, 'phones': phones, 'exit': code, 'seconds': round(time.time() - started),
                        'finishedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'report': copy_to or report}
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(json.dumps(ledger, indent=2) + '\n')
        print(f'{status.upper()} {name} in {ledger[name]["seconds"]} s', flush=True)
        results.append((name, status))
    print('summary:', ', '.join(f'{n}={s}' for n, s in results), f'(source {print_})')
    return 1 if any(s == 'failed' for _, s in results) else 0


if __name__ == '__main__':
    sys.exit(main())
