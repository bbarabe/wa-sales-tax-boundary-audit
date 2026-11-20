#!/usr/bin/env python3
"""Print every SST boundary-file row (all effective dates) for one address and/or ZIP+4s.

Example (the two case studies):
  extract_sst_rows.py --sst data/WAB2026Q4AUG27.csv --zip 98072 --street "WOODINVILLE REDMOND" --house 14450 \
      --zip4 98072-9051 98072-6978 98072-4547 98072-7100 > case_14450_sst_rows.csv
  extract_sst_rows.py --sst data/WAB2026Q4AUG27.csv --zip 98284 --street "CAMP 2" --house 3058 \
      --zip4 98284-9508 > case_3058_camp_2_rd_sst_rows.csv
"""
import argparse, csv, re, sys

HDR = ['sst_line', 'type', 'begin', 'end', 'low', 'high', 'odd_even', 'predir', 'street', 'suffix', 'postdir',
       'sec_abbr', 'sec_low', 'sec_high', 'sec_odd_even', 'city', 'zip', 'plus4',
       'zip_low', 'ext_low', 'zip_high', 'ext_high', 'composite_ser', 'special_district_code', 'location_code']


def num(s):
    m = re.match(r'\d+', s or '')
    return int(m.group()) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sst', required=True)
    ap.add_argument('--zip'); ap.add_argument('--street'); ap.add_argument('--house', type=int)
    ap.add_argument('--zip4', nargs='*', default=[])
    a = ap.parse_args()
    z4 = {tuple(x.split('-')) for x in a.zip4}
    w = csv.writer(sys.stdout)
    w.writerow(HDR)
    for i, f in enumerate(csv.reader(open(a.sst, newline='', encoding='latin-1')), 1):
        f += [''] * (31 - len(f))
        keep = False
        if f[0] == 'A' and a.street and f[7].strip() == a.street and f[15] == a.zip:
            lo, hi = num(f[3]), num(f[4])
            keep = lo is not None and hi is not None and lo <= a.house <= hi
            keep = keep or (a.zip, f[16]) in z4
        elif f[0] == '4':
            keep = any(f[17] <= z <= f[19] and (f[17], f[18]) <= (z, p) <= (f[19], f[20]) for z, p in z4)
        if keep:
            loc = f[30][1:] if f[30].startswith('L') else f[21][-4:]
            w.writerow([i] + f[:22] + [f[30], loc])


if __name__ == '__main__':
    main()
