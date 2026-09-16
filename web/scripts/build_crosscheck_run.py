"""Phase 7A: turn CrossCheck's recorded result files into the inspection room's data + evidence crops.

Reads the CrossCheck project read-only and refuses to write anything unless the totals match the
dossier (portfolio/CAPABILITY_CROSSCHECK.md §3.1, §6 K2/K5/K6/K7, §7):
1,080 cells · 422 flagged · 877 sweep findings · 40 pages · 216 access checks → 3 violations ·
5 flows → 1 data loss · 18 issues = 3 High / 14 Medium / 1 Low.

Outputs
- web/lib/crosscheck-run.ts           generated; never edit by hand
- web/public/images/crosscheck/*.png  crops of the project's own evidence images (no retouching)

Run: /home/rayin/Projects/Testing/crosscheck/.venv/bin/python web/scripts/build_crosscheck_run.py
"""
import csv
import json
from collections import Counter
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('/home/rayin/Projects/Testing/crosscheck')
RESULTS = SOURCE / 'qa/out'
OUT_TS = ROOT / 'web/lib/crosscheck-run.ts'
OUT_IMAGES = ROOT / 'web/public/images/crosscheck'

BROWSERS = ['chromium', 'firefox', 'webkit']
VIEWPORTS = ['desktop', 'tablet', 'mobile']
ROLES = ['admin', 'editor', 'viewer']

# (source file, box incl. the coloured annotation border, output name). Boxes were measured from
# the border pixels of each image; the panels themselves are untouched.
CROPS = [
    ('assets/v4_before_after_1_en.png', (218, 130, 601, 954), 'cc-017-before.png'),
    ('assets/v4_before_after_1_en.png', (880, 130, 1499, 954), 'cc-017-expected.png'),
    ('assets/v4_before_after_2_en.png', (218, 130, 601, 954), 'cc-015-before.png'),
    ('assets/v4_before_after_2_en.png', (998, 130, 1381, 954), 'cc-015-expected.png'),
    ('assets/v4_before_after_3_en.png', (38, 130, 782, 550), 'cc-001-before.png'),
    ('assets/v4_before_after_3_en.png', (818, 130, 1562, 550), 'cc-001-expected.png'),
    # Raw flow screenshot at the failed step: the title band where the lost field reappears.
    ('qa/out/shots/flow_update_post_and_crm_owner_step5.png', (0, 0, 1280, 440), 'cc-003-actual.png'),
]


def main():
    rows = [json.loads(line) for line in (RESULTS / 'results.jsonl').read_text().splitlines() if line.strip()]
    summary = json.loads((RESULTS / 'run_summary.json').read_text())
    routes = sorted({row['route'] for row in rows})
    assert len(rows) == 1080 and summary['combinations_total'] == 1080, len(rows)
    assert len(routes) == 40, len(routes)
    flagged_total = sum(1 for row in rows if not row['ok'])
    assert flagged_total == 422 == summary['combinations_failed'], flagged_total
    findings = sum(len(row['findings']) for row in rows)
    assert findings == 877 == summary['findings_total'], findings

    cell = {(r['route'], r['browser'], r['viewport'], r['role']): r for r in rows}
    columns = [(b, v, role) for b in BROWSERS for v in VIEWPORTS for role in ROLES]
    matrix = [''.join('0' if cell[(route, *col)]['ok'] else '1' for col in columns) for route in routes]
    assert sum(line.count('1') for line in matrix) == 422

    issues = json.loads((RESULTS / 'issues.json').read_text())
    assert len(issues) == 18
    assert Counter(i['priority'] for i in issues) == {'High': 3, 'Medium': 14, 'Low': 1}
    sources = {'permissions': 'access', 'flows': 'flow'}

    def issue_row(issue):
        return routes.index(issue['route']) if issue['route'] in routes and sources.get(issue['source']) is None else None

    def cells_with(route, kind):
        return [c for c, col in enumerate(columns) if any(f['kind'] == kind for f in cell[(route, *col)]['findings'])]

    permissions = list(csv.DictReader((RESULTS / 'permissions.csv').open()))
    assert len(permissions) == 216 and Counter(p['verdict'] for p in permissions) == {'OK': 213, 'VIOLATION': 3}
    pages = list(dict.fromkeys(p['route'] for p in permissions))
    assert len(pages) == 72
    violations = [[pages.index(p['route']), ROLES.index(p['role'])] for p in permissions if p['verdict'] == 'VIOLATION']

    flows = json.loads((RESULTS / 'flows_results.json').read_text())
    assert len(flows) == 5 and [f['status'] for f in flows].count('failed') == 1

    OUT_IMAGES.mkdir(parents=True, exist_ok=True)
    for source, box, name in CROPS:
        Image.open(SOURCE / source).convert('RGB').crop(box).save(OUT_IMAGES / name, optimize=True)

    data = {
        'routes': routes,
        'columns': [f'{b} · {v} · {role}' for b, v, role in columns],
        'matrix': matrix,
        'issues': [{'id': i['id'], 'priority': i['priority'], 'source': sources.get(i['source'], 'sweep'), 'row': issue_row(i)} for i in issues],
        'accessPages': len(pages),
        'violations': violations,
        'flows': [{'name': f['name'], 'passed': f['status'] == 'passed'} for f in flows],
        'evidenceCells': {'CC-017': cells_with('/wide-report/', 'layout_overflow'), 'CC-015': cells_with('/overlap-toolbar/', 'element_overlap')},
    }
    body = ',\n'.join(f'  {key}: {json.dumps(value, ensure_ascii=False, separators=(", ", ": "))}' for key, value in data.items())
    OUT_TS.write_text(
        '// GENERATED by web/scripts/build_crosscheck_run.py from the recorded CrossCheck demo run\n'
        f"// (run {summary['run_id']}). Do not edit by hand; totals are asserted against the dossier.\n"
        '// Columns: browser → screen size → role. Matrix rows: routes; 1 = combination flagged by a detector.\n'
        f'export const crosscheckRun = {{\n{body},\n}} as const;\n'
    )
    print('wrote', OUT_TS.relative_to(ROOT), 'and', len(CROPS), 'crops')


if __name__ == '__main__':
    main()
