#!/usr/bin/env python3
"""Find house numbers in DOR's address download (State_YYQn.txt) that match more than one row with
different location codes (same ZIP, street and odd/even side).

Usage:
  python3 scan_dor_address_file.py --address State_26Q4.txt --rates Rates_26Q4.csv --out results/2026Q4/dor_address_file_conflicts.csv

Each output row is a segment of consecutive house numbers (of one parity) covered by the same set of
conflicting rows. 'pattern' is:
  single-address row inside block row   one row covers exactly this house number, another a range
  overlapping block rows                only range rows overlap
  same ZIP+4, different codes           two rows share a ZIP+4 yet carry different codes

The address file has no suite/unit field, so suite-level records published elsewhere (the SST boundary
file) show up here as duplicate single-address rows.
"""
import argparse, collections, csv

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--address', required=True); ap.add_argument('--rates', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    rate = {x['Code']: (x['Name'], round(float(x['Rate']), 4)) for x in csv.DictReader(open(a.rates, encoding='utf-8-sig'))}
    groups = collections.defaultdict(list)
    with open(a.address, newline='') as f:
        for i, x in enumerate(csv.DictReader(f), start=2):
            groups[(x['ZIP'], x['STREET'], x['ODD_EVEN'])].append((int(x['ADDR_LOW']), int(x['ADDR_HIGH']), x['PLUS4'], x['CODE'], i))
    out = []
    for (z, street, side), rows in groups.items():
        if len(rows) < 2 or len({r[3] for r in rows}) < 2:
            continue
        par = 0 if side == 'E' else 1
        pts = sorted({p for lo, hi, *_ in rows for p in (lo, hi + 1)})
        for s, e in zip(pts, pts[1:]):
            act = [r for r in rows if r[0] <= s and r[1] >= e - 1]
            if len({r[3] for r in act}) < 2:
                continue
            first = s if s % 2 == par else s + 1
            if first > e - 1:
                continue
            last = e - 1 if (e - 1) % 2 == par else e - 2
            by4 = collections.defaultdict(set)
            for r in act:
                by4[r[2]].add(r[3])
            if any(len(v) > 1 for v in by4.values()):
                pattern = 'same ZIP+4, different codes'
            elif any(r[0] == r[1] for r in act) and any(r[0] != r[1] for r in act):
                pattern = 'single-address row inside block row'
            elif all(r[0] == r[1] for r in act):
                pattern = 'single-address rows only'
            else:
                pattern = 'overlapping block rows'
            rates = {rate.get(r[3], ('?', None))[1] for r in act}
            out.append([z, street, side, first, last, (last - first) // 2 + 1, pattern, len(rates) > 1,
                        ' | '.join(f"L{r[4]}: {r[0]}-{r[1]} +{r[2]} -> {r[3]} ({rate.get(r[3], ('?', None))[0]} {rate.get(r[3], ('?', None))[1]})" for r in sorted(act))])
    with open(a.out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['zip', 'street', 'side', 'house_from', 'house_to', 'house_number_candidates', 'pattern', 'rate_differs', 'rows'])
        w.writerows(out)
    print(len(out), 'segments;', sum(r[5] for r in out), 'house-number candidates')

if __name__ == '__main__':
    main()
