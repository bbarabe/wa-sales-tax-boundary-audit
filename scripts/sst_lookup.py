#!/usr/bin/env python3
"""Replay a lookup against Washington's SST boundary file.

The model (SSUTA sections 305 and 309, May 2026; SST Technology Guide, Oct 2022, ch. 5):
standardize the address (USPS, CASS or Board-approved software), match it to the address ("A") records;
if no address record matches, use the standardized ZIP+4 against the ZIP+4 ("4") records; if none, the
ZIP5 ("Z") record. Every address field must match exactly, secondary (suite/unit) fields included; the
guide allows the ZIP extension to be left out of the address match. See docs/sst-rules.md.

Three modes:
  strict_no_plus4    omit the ZIP extension when matching A rows.
  strict_with_plus4  retain the supplied candidate ZIP extension when matching A rows.
                     Identical to strict_no_plus4 when the input has no ZIP+4.
  In both strict modes a supplied suite must match a listed suite, and two matching records with different
  codes are reported as ambiguous (the guide says an address can only be valid for one row).
  assumptions        NOT in the rules: a suite that is not listed is dropped and the record without a suite
                     is used; where records without a suite overlap, the single-address record wins; the
                     ZIP+4 is left out of the address match. QuickBooks Online matched this mode on all 31
                     inputs we entered.

Input: a TSV of standardized addresses with header (extra columns are ignored)
  id  house  predir  name  suffix  postdir  sec_abbr  sec_value  zip5  plus4  label
Usage:
  python3 sst_lookup.py --sst WAB2026Q4AUG27.csv --date 20261120 --inputs tests/test_inputs_standardized.tsv --out out.csv
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


def fmt(level, codes):
    codes = sorted(codes)
    if not codes:
        return level, 'no match'
    if len(codes) == 1:
        return level, codes[0]
    return level, 'ambiguous ' + ' / '.join(codes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sst', required=True); ap.add_argument('--date', required=True)
    ap.add_argument('--inputs', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    tests = list(csv.DictReader(open(a.inputs, newline=''), delimiter='\t'))
    zips = {t['zip5'] for t in tests}
    A, F, Z = [], [], []
    with open(a.sst, newline='', encoding='latin-1') as f:
        for i, r in enumerate(csv.reader(f), start=1):
            if not r or not (r[1] <= a.date <= r[2]):
                continue
            r += [''] * (31 - len(r))
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

    def strict(base, sec, zip5, plus4):
        exact = [(i, r) for i, r in base if (r[10] == sec[0] and sec_in(r, sec[1]))] if sec else \
                [(i, r) for i, r in base if not r[10]]
        if exact:
            return fmt('A', {loc_code(r) for i, r in exact})
        lvl, hit = fallback(zip5, plus4)
        return fmt(lvl, {loc_code(r) for i, r in hit})

    with open(a.out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'label', 'plus4_used',
                    'strict_no_plus4_level', 'strict_no_plus4_code',
                    'strict_with_plus4_level', 'strict_with_plus4_code',
                    'assumptions_level', 'assumptions_code', 'matching_address_records'])
        for t in tests:
            n = int(t['house'])
            base = [(i, r) for i, r in A if r[15] == t['zip5'] and (r[6], r[7], r[8], r[9]) == (t['predir'], t['name'], t['suffix'], t['postdir'])
                    and (not t.get('city') or r[14] == t['city'])
                    and r[3].isdigit() and r[4].isdigit() and int(r[3]) <= n <= int(r[4]) and par_ok(r[5], n)]
            desc = ' | '.join(f"L{i}: {r[3]}-{r[4]} {r[5] or 'B'} {r[10]} {r[11]}-{r[12]} +{r[16]} -> {loc_code(r)}".replace('  ', ' ') for i, r in base)
            sec = (t['sec_abbr'], t['sec_value']) if t['sec_abbr'] else None
            p4 = t['plus4']
            s1 = strict(base, sec, t['zip5'], p4)
            s2 = strict([(i, r) for i, r in base if r[16] == p4] if p4 else base, sec, t['zip5'], p4)
            # assumptions (not in the rules)
            exact = [(i, r) for i, r in base if r[10] == sec[0] and sec_in(r, sec[1])] if sec else [(i, r) for i, r in base if not r[10]]
            pick = exact or [(i, r) for i, r in base if not r[10]]
            if pick:
                if len({loc_code(r) for i, r in pick}) > 1:
                    pick = [(i, r) for i, r in pick if r[3] == r[4]] or pick
                s3 = ('A', '/'.join(sorted({loc_code(r) for i, r in pick})))
            else:
                lvl, hit = fallback(t['zip5'], p4)
                s3 = (lvl, '/'.join(sorted({loc_code(r) for i, r in hit})))
            w.writerow([t['id'], t['label'], p4, *s1, *s2, *s3, desc])


if __name__ == '__main__':
    main()
