#!/usr/bin/env python3
"""How would the conflicts resolve if the standardized ZIP+4 is part of the address match?

The SST Technology Guide allows an address query with or without the ZIP extension. This reports, for the
C1 and C4a conflicts, whether including the ZIP+4 would separate the conflicting records:
  C1   do the overlapping no-suite records carry different ZIP+4s?
  C4a  are the building's suite ZIP+4s absent from the no-suite records, and do the ZIP+4 ("4") records
       for those ZIP+4s carry the suites' code? (Then a no-suite or unlisted-suite address whose
       standardized ZIP+4 is one of them falls through to a ZIP+4 record with the suites' code.)

Usage: check_zip4_resolution.py --sst WAB2026Q4AUG27.csv --date 20261120 --results results/2026Q4 > zip4_resolution.md
"""
import argparse, csv, os, re
from collections import Counter

C1REC = re.compile(r'L\d+: (\d+)-(\d+) \S+ (\d{5})-(\d{4}) -> (\d+)')
C4REC = re.compile(r'L\d+: \S+ \S+(?: [A-Z]+ \S+)? (\d{5})-(\d{4}) -> (\d+)')


def codes(s):
    return {x.strip().lstrip('0') for x in s.split('|') if x.strip()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sst', required=True); ap.add_argument('--date', required=True); ap.add_argument('--results', required=True)
    a = ap.parse_args()
    out = ['# Would the ZIP+4 resolve the conflicts?', '']

    c1 = list(csv.DictReader(open(os.path.join(a.results, 'C1_address_overlaps_no_suite.csv'))))
    t = Counter()
    for r in c1:
        by4 = {}
        for lo, hi, z, p, code in C1REC.findall(r['records']):
            by4.setdefault(p, set()).add(code)
        k = 'two records share a ZIP+4' if any(len(v) > 1 for v in by4.values()) else 'each record has its own ZIP+4'
        t[(k, r['rate_differs'] == 'True')] += 1
    out += ['## C1 overlapping no-suite records', '', '| | rows | rate-changing |', '|---|---|---|']
    for k in ('each record has its own ZIP+4', 'two records share a ZIP+4'):
        out.append(f'| {k} | {t[(k, True)] + t[(k, False)]} | {t[(k, True)]} |')
    out += ['', 'Where each record has its own ZIP+4, including the standardized ZIP+4 picks the record that carries it. '
            'Which one that is depends on the ZIP+4 USPS assigns, which the file does not contain.', '']

    c4 = list(csv.DictReader(open(os.path.join(a.results, 'C4_suite_vs_no_suite.csv'))))
    c4a, need = [], set()
    for r in c4:
        s, n = codes(r['listed_suite_codes']), codes(r['no_suite_codes'])
        if s & n:
            continue
        sz = {(z, p) for z, p, c in C4REC.findall(r['suite_records_detail'])}
        nz = {(z, p) for z, p, c in C4REC.findall(r['no_suite_records_detail'])}
        c4a.append((r, s, sz, nz)); need |= sz
    F = {}
    for f in csv.reader(open(a.sst, newline='', encoding='latin-1')):
        if f[0] != '4' or not (f[1] <= a.date <= f[2]):
            continue
        f += [''] * (31 - len(f))
        code = (f[30][1:] if f[30].startswith('L') else f[21][-4:]).lstrip('0')
        for z, p in need:
            if (f[17], f[18]) <= (z, p) <= (f[19], f[20]):
                F.setdefault((z, p), set()).add(code)
    t = Counter()
    for r, s, sz, nz in c4a:
        got = set().union(*[F.get(k, set()) for k in sz]) if sz else set()
        if sz & nz:
            k = 'a suite ZIP+4 also appears on a no-suite record'
        elif not got:
            k = 'no ZIP+4 record for the suite ZIP+4s'
        elif got <= s:
            k = "suite ZIP+4 records carry the suites' code"
        else:
            k = 'suite ZIP+4 records carry another code'
        t[(k, r['rate_differs'] == 'True')] += 1
    out += ['## C4a buildings whose suites are coded differently from every no-suite record', '',
            '| | buildings | rate-changing |', '|---|---|---|']
    for k in sorted({k for k, _ in t}):
        out.append(f'| {k} | {t[(k, True)] + t[(k, False)]} | {t[(k, True)]} |')
    out += ['', 'For these buildings the two permitted ways of querying disagree: leaving the ZIP+4 out matches the '
            'block record; including a suite ZIP+4 (USPS gives the building default, which was a suite ZIP+4 at '
            '14450, 21806 and 4212) falls through to a ZIP+4 record with the suites\' code.']
    print('\n'.join(out))


if __name__ == '__main__':
    main()
