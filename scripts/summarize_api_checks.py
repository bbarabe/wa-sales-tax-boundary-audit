#!/usr/bin/env python3
"""Summarize which record DOR's live AddressRates lookup agrees with, per conflict check.

Usage: summarize_api_checks.py RESULTS_DIR > summary.md

Reads (if present) C1_api.csv, C2_api.csv, C4_api.csv, C7_api_sample200.csv in RESULTS_DIR.
Codes are compared as integers (DOR returns '0501', SST carries '501' or 'L0501').
"""
import csv, os, re, sys
from collections import Counter

REC = re.compile(r'L\d+: (\d+)-(\d+) .*?-> (\d+)')


def norm(c):
    c = (c or '').strip().lstrip('L')
    return int(c) if c.isdigit() else None


def codes(s):
    return {norm(x) for x in (s or '').split('|') if norm(x) is not None}


def load(d, name):
    p = os.path.join(d, name)
    return list(csv.DictReader(open(p, newline=''))) if os.path.exists(p) else None


def table(title, counter, total, note=''):
    out = [f'### {title}', '', f'{total} rows checked. {note}'.rstrip(), '', '| DOR lookup returned | rows | rate-changing rows |', '|---|---|---|']
    for k, (n, nr) in counter.items():
        out.append(f'| {k} | {n} | {nr} |')
    return '\n'.join(out) + '\n'


def tally(rows, classify):
    c = {}
    for r in rows:
        k = classify(r)
        n, nr = c.get(k, (0, 0))
        c[k] = (n + 1, nr + (r.get('rate_differs') == 'True'))
    return dict(sorted(c.items(), key=lambda kv: -kv[1][0]))


def main():
    d = sys.argv[1]
    parts = ['# Original DOR AddressRates observations', '']

    rows = load(d, 'C1_api.csv')
    if rows:
        def k1(r):
            a = norm(r['api_code'])
            if a is None:
                return 'no result'
            recs = [(int(h) - int(l), norm(c)) for l, h, c in REC.findall(r['records'])]
            if not recs:
                return 'unparsed'
            recs.sort()
            narrow, wide = recs[0], recs[-1]
            if narrow[0] == wide[0]:
                return 'a code from equal-width records' if a in {c for _, c in recs} else 'neither record\'s code'
            if a == narrow[1] and a != wide[1]:
                return 'narrower record\'s code'
            if a == wide[1] and a != narrow[1]:
                return 'wider record\'s code'
            if a in {c for _, c in recs}:
                return 'a code from one of 3+ records'
            return 'neither record\'s code'
        parts.append(table('C1: overlapping no-suite address records', tally(rows, k1), len(rows),
                           'Query: first house number of the overlap, street, ZIP5.'))

    rows = load(d, 'C2_api.csv')
    if rows:
        def k2(r):
            a = norm(r['api_code'])
            if a is None:
                return 'no result'
            return 'one of the duplicate records\' codes' if a in codes(r['codes']) else 'neither record\'s code'
        parts.append(table('C2: duplicate ZIP+4 records', tally(rows, k2), len(rows), 'Query: ZIP+4 only, no street.'))

    rows = load(d, 'C4_api.csv')
    if rows:
        def k4(r):
            a = norm(r['api_code'])
            s, n = codes(r['listed_suite_codes']), codes(r['no_suite_codes'])
            if not (s & n):
                kind = 'C4a'
            else:
                recs = sorted((int(h) - int(l), norm(c)) for l, h, c in REC.findall(r['no_suite_records_detail']))
                kind = 'C4b' if recs and recs[0][1] in s else 'C4c'
            if a is None:
                return f'{kind}: no result'
            if kind == 'C4a':
                if a in s:
                    return 'C4a: listed suites\' code'
                if a in n:
                    return 'C4a: no-suite record\'s code'
                return 'C4a: neither'
            narrow = sorted((int(h) - int(l), norm(c)) for l, h, c in REC.findall(r['no_suite_records_detail']))[0][1]
            if a == narrow:
                return f'{kind}: narrowest no-suite record\'s code'
            if a in n:
                return f'{kind}: a wider no-suite record\'s code'
            return f'{kind}: neither'
        parts.append(table('C4: building suites vs. the no-suite records', tally(rows, k4), len(rows),
                           'Query: house number and street with no suite, ZIP5. '
                           'C4a = no no-suite record carries the suites\' code; '
                           'C4b = no-suite records overlap and the narrowest one agrees with the suites.'))

    rows = load(d, 'C7_api_sample200.csv')
    if rows:
        def k7(r):
            a = norm(r['api_code'])
            if a is None:
                return 'no result'
            f, s = norm(r['dor_file_code']), codes(r['sst_codes'])
            if a == f and a not in s:
                return 'DOR address file\'s code'
            if a in s and a != f:
                return 'SST file\'s code'
            if a == f and a in s:
                return 'code shared by both'
            return 'neither'
        parts.append(table('C7: SST file vs. DOR address file (random sample)', tally(rows, k7), len(rows),
                           'Query: first house number of the DOR range, street, ZIP5.'))

    print('\n'.join(parts))


if __name__ == '__main__':
    main()
