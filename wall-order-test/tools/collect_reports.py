"""Collect the print reports of the wall order test and summarise them by tester (see EVIDENCE.md).

Uses the GitHub CLI (gh), logged in. Reports count when the maintainer has added the label "verified" after
checking the attached G-code with wallorder-check.html; reports labelled "incomplete" are listed separately.

  python collect_reports.py OWNER/REPO [--out DIR]

Writes reports.csv (one row per report) and SUMMARY.md (counts by tester) into DIR (default: current folder).
"""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
import subprocess

FIELDS = {  # issue form label (English part) -> column
    'Test build': 'build', 'Operating system': 'os', 'Printer': 'printer', 'Printer type': 'printer_family',
    'Firmware': 'firmware', 'Nozzle diameter (mm)': 'nozzle', 'Material': 'material', 'Layer height (mm)': 'layer_height',
    'Wall generator': 'wall_generator', 'Wall order of A and C': 'base_order', 'Model': 'model',
    'Settings of print C': 'feature_settings', 'Overhang underside, C compared with A': 'underside_vs_a',
    'Overhang underside, C compared with B': 'underside_vs_b', 'Visible line where the order switches, on C': 'switch_line',
    'Vertical walls away from the overhang, C compared with A': 'vertical_walls', 'Which print would you keep?': 'keep',
    'Was the ranking blind?': 'blind', 'Observations': 'observations',
}
SCORES = ['underside_vs_a', 'underside_vs_b', 'switch_line', 'vertical_walls', 'keep']


def gh_issues(repo, label):
    out = subprocess.run(['gh', 'issue', 'list', '--repo', repo, '--label', label, '--state', 'all', '--limit', '1000',
                          '--json', 'number,title,body,author,labels,url,createdAt,state'],
                         capture_output=True, text=True, encoding='utf-8', check=True).stdout
    return json.loads(out)


def parse_body(body):
    """Issue forms render as '### Label / 中文\\n\\nvalue' sections."""
    row = {}
    for title, value in re.findall(r'^### (.+?)\s*\n(.*?)(?=^### |\Z)', body or '', flags=re.M | re.S):
        label = title.split(' / ')[0].strip()
        value = value.strip()
        if label in FIELDS:
            value = '' if value == '_No response_' else value
            # dropdown answers are bilingual ("Better / 較好"): keep the English part
            row[FIELDS[label]] = value.split(' / ')[0].strip() if FIELDS[label] not in ('feature_settings', 'observations', 'printer', 'material') else value
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('repo')
    ap.add_argument('--out', type=Path, default=Path('.'))
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    rows = []
    for issue in gh_issues(a.repo, 'print-report'):
        labels = {l['name'] for l in issue['labels']}
        r = parse_body(issue['body'])
        r.update(number=issue['number'], url=issue['url'], tester=issue['author']['login'], created=issue['createdAt'][:10],
                 status='counted' if 'verified' in labels else 'incomplete' if 'incomplete' in labels else 'unchecked')
        rows.append(r)
    cols = ['number', 'created', 'tester', 'status'] + list(dict.fromkeys(FIELDS.values())) + ['url']
    with open(a.out / 'reports.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

    counted = [r for r in rows if r['status'] == 'counted']
    by_tester = defaultdict(list)
    for r in counted:
        by_tester[r['tester']].append(r)

    def tester_answer(reports, key):
        """One answer per tester: their most common answer; a tie between different answers counts as 'mixed'."""
        c = Counter(r.get(key, '') for r in reports).most_common()
        return c[0][0] if len(c) == 1 or c[0][1] > c[1][1] else 'mixed'

    lines = [f'# Wall order test – summary', '',
             f'Reports: {len(rows)} (counted {len(counted)}, incomplete {sum(r["status"] == "incomplete" for r in rows)}, '
             f'not yet checked {sum(r["status"] == "unchecked" for r in rows)})', '',
             f'Independent testers with counted reports: **{len(by_tester)}**', '']
    for key, title in (('printer_family', 'Printer types'), ('firmware', 'Firmware'), ('os', 'Operating systems'),
                       ('wall_generator', 'Wall generator'), ('model', 'Models')):
        c = Counter(v for reps in by_tester.values() for v in {r.get(key, '') for r in reps})
        lines.append(f'- {title}: ' + ', '.join(f'{k or "?"} {n}' for k, n in c.most_common()))
    materials = Counter(m for reps in by_tester.values() for m in {r.get('material', '').split(',')[0].strip().upper() for r in reps})
    lines += [f'- Materials: ' + ', '.join(f'{k or "?"} {n}' for k, n in materials.most_common()), '']
    lines += ['## Scores, one answer per tester', '']
    for key in SCORES:
        c = Counter(tester_answer(reps, key) for reps in by_tester.values())
        lines.append(f'- **{key}**: ' + ', '.join(f'{k or "?"} {n}' for k, n in c.most_common()))
    blind = sum(any(r.get('blind') == 'Yes' for r in reps) for reps in by_tester.values())
    lines += ['', f'Testers with a blind ranking: {blind}', '', '## All reports', '',
              '| # | tester | status | printer | material | model | C vs A | C vs B | switch line | keep |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in sorted(rows, key=lambda r: r['number']):
        lines.append(f"| [{r['number']}]({r['url']}) | {r['tester']} | {r['status']} | {r.get('printer', '')} | "
                     f"{r.get('material', '')} | {r.get('model', '')} | {r.get('underside_vs_a', '')} | "
                     f"{r.get('underside_vs_b', '')} | {r.get('switch_line', '')} | {r.get('keep', '')} |")
    problems = gh_issues(a.repo, 'problem')
    lines += ['', '## Problem reports', '']
    lines += [f"- [#{p['number']}]({p['url']}) {p['state'].lower()}: {p['title']}" for p in problems] or ['- none']
    (a.out / 'SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{len(rows)} reports, {len(by_tester)} testers counted -> {a.out / "SUMMARY.md"}')


if __name__ == '__main__':
    main()
