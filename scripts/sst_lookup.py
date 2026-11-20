#!/usr/bin/env python3
"""Replay a lookup against Washington's SST boundary file, following the SST Technology Guide (Oct 2022),
chapter 5: match the address ("A") record first, leaving the ZIP extension out of the address match; if no
address record matches, use the ZIP+4 ("4") record; if none, the ZIP5 ("Z") record.

Two modes, because the guide leaves two cases open:
  strict       every address field must match, including the secondary (suite/unit). A suite that is not
               listed means no address match. If two records match, the result is reported as ambiguous.
  assumptions  the same, plus two assumptions the guide does not state:
               (1) a suite that is not listed is dropped and the record without a suite is used;
               (2) where two records without a suite overlap, the single-address record wins.
               In our tests QuickBooks Online behaved like this mode on all 31 inputs.

Input: a TSV of standardized addresses with header
  id  house  predir  name  suffix  postdir  sec_abbr  sec_value  zip5  plus4  label
Usage:
  python3 sst_lookup.py --sst WAB2026Q4AUG27.csv --date 20261120 --inputs tests/test_inputs.tsv --out results.csv
"""
import argparse, csv

def loc_code(r):
    return r[30][1:] if len(r) > 30 and r[30].startswith('L') else (r[21][-4:] if r[21] else '')

def par_ok(oe, n):
    return oe in ('', 'B') or (oe == 'O' and n % 2 == 1) or (oe == 'E' and n % 2 == 0)

def sec_in(r, val):
    lo, hi, oe = r[11], r[12], r[13]
    if lo.isdigit() and hi.isdigit() and val.isdigit():
        return int(lo) <= int(val) <= int(hi) and par_ok(oe, int(val))
    if len(lo) == len(hi) == len(val):
        return lo <= val <= hi
    return val in (lo, hi)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sst', required=True); ap.add_argument('--date', required=True)
    ap.add_argument('--inputs', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    tests = list(csv.DictReader(open(a.inputs, newline=''), delimiter='\t'))
    zips = {t['zip5'] for t in tests}
    A, F, Z = [], [], []
    with open(a.sst, newline='') as f:
        for i, r in enumerate(csv.reader(f), start=1):
            if not r or not (r[1] <= a.date <= r[2]):
                continue
            if r[0] == 'A' and r[15] in zips:
                A.append((i, r))
            elif r[0] in ('4', 'Z') and any(r[17] <= z <= (r[19] or r[17]) for z in zips):
                (F if r[0] == '4' else Z).append((i, r))

    def fallback(zip5, plus4):
        if plus4:
            hit = [(i, r) for i, r in F if r[17] <= zip5 <= (r[19] or r[17]) and r[18] <= plus4 <= (r[20] or r[18])]
            if hit:
                return '4', hit
        return 'Z', [(i, r) for i, r in Z if r[17] <= zip5 <= (r[19] or r[17])]

    with open(a.out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'label', 'strict_level', 'strict_codes', 'assumptions_level', 'assumptions_code', 'matching_address_records'])
        for t in tests:
            n = int(t['house'])
            base = [(i, r) for i, r in A if r[15] == t['zip5'] and (r[6], r[7], r[8], r[9]) == (t['predir'], t['name'], t['suffix'], t['postdir'])
                    and r[3].isdigit() and r[4].isdigit() and int(r[3]) <= n <= int(r[4]) and par_ok(r[5], n)]
            desc = ' | '.join(f"L{i}: {r[3]}-{r[4]} {r[5] or 'B'} {r[10]} {r[11]}-{r[12]} +{r[16]} -> {loc_code(r)}".replace('  ', ' ') for i, r in base)
            sec = (t['sec_abbr'], t['sec_value']) if t['sec_abbr'] else None
            if sec:
                exact = [(i, r) for i, r in base if r[10] == sec[0] and sec_in(r, sec[1])]
            else:
                exact = [(i, r) for i, r in base if not r[10]]
            nosuite = [(i, r) for i, r in base if not r[10]]
            # strict
            if exact:
                s_level, s_codes = 'A', sorted({loc_code(r) for i, r in exact})
            else:
                lvl, hit = fallback(t['zip5'], t['plus4'])
                s_level, s_codes = lvl, sorted({loc_code(r) for i, r in hit})
            # assumptions
            pick = exact or nosuite
            if pick:
                if len({loc_code(r) for i, r in pick}) > 1:
                    singles = [(i, r) for i, r in pick if r[3] == r[4]]
                    pick = singles or pick
                a_level, a_code = 'A', '/'.join(sorted({loc_code(r) for i, r in pick}))
            else:
                lvl, hit = fallback(t['zip5'], t['plus4'])
                a_level, a_code = lvl, '/'.join(sorted({loc_code(r) for i, r in hit}))
            w.writerow([t['id'], t['label'], s_level, ' / '.join(s_codes) if len(s_codes) == 1 else 'ambiguous ' + ' / '.join(s_codes),
                        a_level, a_code, desc])

if __name__ == '__main__':
    main()
