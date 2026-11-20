#!/usr/bin/env python3
"""Scan Washington's Streamlined Sales Tax (SST) boundary file for records that conflict.

The SST Technology Guide (Oct 2022), chapter 5, says: "Each row on the database must be unique for the
query to return one record". This script screens Washington's published location-code assignments
on the requested effective date. The code crosswalk is not itself an SST rate calculation.

Usage:
  python3 scan_sst_conflicts.py --sst WAB2026Q4AUG27.csv --rates Rates_26Q4.csv \
      [--dor-address State_26Q4.txt] --date 20261120 --out results/2026Q4

Categories (one CSV each, all with 1-based line numbers into the SST file):
  C1_address_overlaps_no_suite      two address ("A") records without a secondary (suite/unit) cover the
                                    same house number (same city, ZIP, street, odd/even side) with different codes
  C2_zip4_duplicates                two ZIP+4 ("4") records cover the same ZIP+4 with different codes
  C3_zip5_duplicates                two ZIP5 ("Z") records cover the same ZIP with different codes
  C4_suite_vs_no_suite              a building whose listed suites carry a different code than the
                                    no-suite record covering the same house number. The outcome for an
                                    input depends on its postal candidate and matching procedure.
  C5_suite_overlaps                 two suite records for the same building overlap (same unit designator,
                                    overlapping unit range) with different codes
  C6_zip4_vs_addresses              a ZIP+4 whose "4" record is missing, or whose code is not among the
                                    codes of the address records carrying that ZIP+4, or whose rate is not
                                    the lowest of them (the guide says 9-digit rows carry the lowest rate)
  C7_sst_vs_dor_address_file        (with --dor-address) a range in DOR's own address download whose code
                                    differs from the SST records for the same ZIP+4, street and numbers
  C8_zip5_rule                      for each ZIP5 record: its rate vs the lowest and highest rates of the
                                    address and ZIP+4 records in that ZIP (informational)

Only the Python standard library is used.
"""
import argparse, csv, collections, os, sys

def loc_code(r):
    """DOR location code: the special-district 'L####' code when present, else the last 4 digits of the
    composite SER code."""
    if len(r) > 30 and r[30].startswith('L'):
        return r[30][1:]
    return r[21][-4:] if r[21] else ''

def street_key(r):
    return (r[6], r[7], r[8], r[9])

def street_str(k):
    return ' '.join(p for p in k if p)

def par_ok(oe, n):
    return oe in ('', 'B') or (oe == 'O' and n % 2 == 1) or (oe == 'E' and n % 2 == 0)


def shares_number(lo, hi, side, row):
    first = max(lo, int(row[3]))
    last = min(hi, int(row[4]))
    return any(first + offset <= last and par_ok(side, first + offset)
               and par_ok(row[5], first + offset) for offset in (0, 1))

def overlap_segments(rows, key_parity):
    """rows: list of (lo, hi, oe, payload). Yields (first, last, count, active_rows) for maximal segments of
    house numbers of the given parity (0 even, 1 odd) where the active rows carry more than one code."""
    act_rows = [x for x in rows if x[2] in ('B', '') or (x[2] == 'O') == (key_parity == 1)]
    if len(act_rows) < 2:
        return
    pts = sorted({p for x in act_rows for p in (x[0], x[1] + 1)})
    for a, b in zip(pts, pts[1:]):
        act = [x for x in act_rows if x[0] <= a and x[1] >= b - 1]
        if len({x[3]['code'] for x in act}) < 2:
            continue
        first = a if a % 2 == key_parity else a + 1
        if first > b - 1:
            continue
        last = b - 1 if (b - 1) % 2 == key_parity else b - 2
        yield first, last, (last - first) // 2 + 1, act

def sec_range(r):
    lo, hi = r[11], r[12]
    if lo.isdigit() and hi.isdigit():
        return ('n', int(lo), int(hi))
    return ('s', lo, hi or lo)

def sec_overlap(a, b):
    if a[0] == 'n' and b[0] == 'n':
        return a[1] <= b[2] and b[1] <= a[2]
    if a[0] == 's' and b[0] == 's' and len(a[1]) == len(a[2]) == len(b[1]) == len(b[2]):
        return a[1] <= b[2] and b[1] <= a[2]
    return a[1:] == b[1:]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sst', required=True)
    ap.add_argument('--rates', required=True, help='DOR rate file (Rates_YYQn.csv)')
    ap.add_argument('--dor-address', help="DOR address download (State_YYQn.txt), for C7")
    ap.add_argument('--date', required=True, help='effective date YYYYMMDD')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    rate = {}
    with open(a.rates, encoding='utf-8-sig', newline='') as f:
        for x in csv.DictReader(f):
            rate[x['Code']] = (x['Name'], round(float(x['Rate']), 4))
    R = lambda c: rate.get(c, ('?', None))

    A, F, Z = [], [], []
    with open(a.sst, newline='') as f:
        for i, r in enumerate(csv.reader(f), start=1):
            if not r or not (r[1] <= a.date <= r[2]):
                continue
            rec = {'line': i, 'code': loc_code(r), 'r': r}
            if r[0] == 'A':
                A.append(rec)
            elif r[0] == '4':
                F.append(rec)
            elif r[0] == 'Z':
                Z.append(rec)
    print(f'effective {a.date}: A={len(A)} 4={len(F)} Z={len(Z)}', file=sys.stderr)

    def desc(rec):
        r = rec['r']
        if r[0] == 'A':
            sec = f" {r[10]} {r[11]}-{r[12]}{('/' + r[13]) if r[13] else ''}" if r[10] else ''
            return f"L{rec['line']}: {r[3]}-{r[4]} {r[5] or 'B'}{sec} {r[15]}-{r[16]} -> {rec['code']} ({R(rec['code'])[0]} {R(rec['code'])[1]})"
        return f"L{rec['line']}: {r[17]}-{r[18]}..{r[19]}-{r[20]} -> {rec['code']} ({R(rec['code'])[0]} {R(rec['code'])[1]})"

    def rates_of(recs):
        return sorted({R(x['code'])[1] for x in recs if R(x['code'])[1] is not None})

    summary = []
    def write(name, header, rows, definition, scope, example=''):
        with open(os.path.join(a.out, name + '.csv'), 'w', newline='') as f:
            w = csv.writer(f); w.writerow(header); w.writerows(rows)
        print(f'{name}: {len(rows)} rows', file=sys.stderr)
        return rows

    # index address records by street
    nosuite = collections.defaultdict(list)
    suites = collections.defaultdict(list)
    for rec in A:
        r = rec['r']
        if not (r[3].isdigit() and r[4].isdigit()):
            continue
        key = (r[15], r[14]) + street_key(r)
        (suites if r[10] else nosuite)[key].append((int(r[3]), int(r[4]), r[5], rec))

    # C1
    c1 = []
    for key, rows in nosuite.items():
        if len(rows) < 2 or len({x[3]['code'] for x in rows}) < 2:
            continue
        for par in (0, 1):
            for first, last, n, act in overlap_segments(rows, par):
                recs = [x[3] for x in act]
                rs = rates_of(recs)
                c1.append([key[0], street_str(key[2:]), 'even' if par == 0 else 'odd', first, last, n,
                           len(rs) > 1, ' | '.join(sorted({x['code'] for x in recs})), ' | '.join(desc(x) for x in recs)])
    write('C1_address_overlaps_no_suite',
          ['zip', 'street', 'side', 'house_from', 'house_to', 'house_number_candidates', 'rate_differs', 'codes', 'records'], c1, '', '')

    # C2: ZIP+4 records
    by_zip = collections.defaultdict(list)
    for rec in F:
        r = rec['r']
        zl, zh = r[17], r[19] or r[17]
        if not (zl.isdigit() and zh.isdigit()):
            continue
        for z in range(int(zl), int(zh) + 1) if int(zh) - int(zl) < 200 else [int(zl)]:
            el, eh = r[18], r[20] or r[18]
            if el.isdigit() and eh.isdigit():
                by_zip[str(z).zfill(5)].append((int(el), int(eh), '', rec))
    c2 = []
    for z, rows in by_zip.items():
        if len({x[3]['code'] for x in rows}) < 2:
            continue
        pts = sorted({p for x in rows for p in (x[0], x[1] + 1)})
        for lo, hi in zip(pts, pts[1:]):
            act = [x for x in rows if x[0] <= lo and x[1] >= hi - 1]
            if len({x[3]['code'] for x in act}) < 2:
                continue
            recs = [x[3] for x in act]
            c2.append([z, str(lo).zfill(4), str(hi - 1).zfill(4), hi - lo, len(rates_of(recs)) > 1,
                       ' | '.join(sorted({x['code'] for x in recs})), ' | '.join(desc(x) for x in recs)])
    write('C2_zip4_duplicates', ['zip', 'plus4_from', 'plus4_to', 'zip4_count', 'rate_differs', 'codes', 'records'], c2, '', '')

    # C3: ZIP5 records
    z5 = collections.defaultdict(list)
    for rec in Z:
        r = rec['r']
        zl, zh = r[17], r[19] or r[17]
        if zl.isdigit() and zh.isdigit():
            for z in range(int(zl), int(zh) + 1) if int(zh) - int(zl) < 2000 else [int(zl)]:
                z5[str(z).zfill(5)].append(rec)
    c3 = [[z, len(rates_of(recs)) > 1, ' | '.join(sorted({x['code'] for x in recs})), ' | '.join(desc(x) for x in recs)]
          for z, recs in sorted(z5.items()) if len({x['code'] for x in recs}) > 1]
    write('C3_zip5_duplicates', ['zip', 'rate_differs', 'codes', 'records'], c3, '', '')

    # C4 and C5: suites
    c4, c5 = [], []
    for key, srows in suites.items():
        ns = nosuite.get(key, [])
        # group suite rows by building (house range + side)
        bld = collections.defaultdict(list)
        for x in srows:
            bld[(x[0], x[1], x[2])].append(x[3])
        for (lo, hi, oe), recs in bld.items():
            n = lo  # buildings are almost always a single house number
            cover = [y[3] for y in ns if y[0] <= n <= y[1] and par_ok(y[2], n) and par_ok(oe, n)]
            scodes = {x['code'] for x in recs}
            ncodes = {x['code'] for x in cover}
            if cover and (ncodes - scodes or scodes - ncodes):
                rs = rates_of(recs + cover)
                c4.append([key[0], street_str(key[2:]), f'{lo}-{hi}' if lo != hi else str(lo),
                           ' | '.join(sorted(scodes)), ' | '.join(sorted(ncodes)), len(rs) > 1, len(recs),
                           ' | '.join(desc(x) for x in recs), ' | '.join(desc(x) for x in cover)])
            # C5: overlapping suite ranges with different codes
            byabbr = collections.defaultdict(list)
            for x in recs:
                byabbr[x['r'][10]].append(x)
            for abbr, xs in byabbr.items():
                for i in range(len(xs)):
                    for j in range(i + 1, len(xs)):
                        p, q = xs[i], xs[j]
                        if p['code'] != q['code'] and sec_overlap(sec_range(p['r']), sec_range(q['r'])):
                            c5.append([key[0], street_str(key[2:]), f'{lo}-{hi}' if lo != hi else str(lo), abbr,
                                       len(rates_of([p, q])) > 1, f"{p['code']} | {q['code']}", f"{desc(p)} | {desc(q)}"])
    write('C4_suite_vs_no_suite', ['zip', 'street', 'house', 'listed_suite_codes', 'no_suite_codes', 'rate_differs',
                                   'suite_records', 'suite_records_detail', 'no_suite_records_detail'], c4, '', '')
    write('C5_suite_overlaps', ['zip', 'street', 'house', 'unit_designator', 'rate_differs', 'codes', 'records'], c5, '', '')

    # C6: ZIP+4 records vs the address records that carry the ZIP+4
    a_by_p4 = collections.defaultdict(list)
    for rec in A:
        r = rec['r']
        if r[16].isdigit():
            a_by_p4[(r[15], int(r[16]))].append(rec)
    f_index = {z: rows for z, rows in by_zip.items()}
    c6 = []
    for (z, p4), recs in a_by_p4.items():
        frecs = [x[3] for x in f_index.get(z, []) if x[0] <= p4 <= x[1]]
        acodes = {x['code'] for x in recs}
        fcodes = {x['code'] for x in frecs}
        arates = rates_of(recs)
        if not frecs:
            kind = 'no ZIP+4 record'
        elif len(fcodes) > 1:
            continue  # reported in C2
        else:
            fc = next(iter(fcodes))
            fr = R(fc)[1]
            if fc not in acodes:
                kind = 'ZIP+4 code not used by any address on it'
            elif arates and fr is not None and fr > min(arates):
                kind = 'ZIP+4 rate not the lowest of its addresses'
            else:
                continue
        c6.append([z, str(p4).zfill(4), kind, ' | '.join(sorted(acodes)), ' | '.join(sorted(fcodes)),
                   len(set(arates) | set(rates_of(frecs))) > 1, len(recs),
                   ' | '.join(desc(x) for x in recs[:6]) + (' | ...' if len(recs) > 6 else ''),
                   ' | '.join(desc(x) for x in frecs)])
    write('C6_zip4_vs_addresses', ['zip', 'plus4', 'issue', 'address_codes', 'zip4_codes', 'rate_differs',
                                   'address_records', 'address_records_detail', 'zip4_records_detail'], c6, '', '')

    # C7: DOR address download vs SST
    if a.dor_address:
        sst_idx = collections.defaultdict(list)
        for rec in A:
            r = rec['r']
            if r[3].isdigit() and r[4].isdigit() and r[16].isdigit():
                sst_idx[(r[15], r[16], street_str(street_key(r)))].append(rec)
        c7, missing = [], 0
        with open(a.dor_address, newline='') as f:
            for i, x in enumerate(csv.DictReader(f), start=2):
                lo, hi = int(x['ADDR_LOW']), int(x['ADDR_HIGH'])
                cands = [rec for rec in sst_idx.get((x['ZIP'], x['PLUS4'], x['STREET']), [])
                         if shares_number(lo, hi, x['ODD_EVEN'], rec['r'])]
                if not cands:
                    missing += 1
                    continue
                scodes = {rec['code'] for rec in cands}
                if x['CODE'] not in scodes:
                    c7.append([i, x['ZIP'], x['PLUS4'], x['STREET'], lo, hi, x['ODD_EVEN'], x['CODE'],
                               ' | '.join(sorted(scodes)), (R(x['CODE'])[1] not in rates_of(cands)),
                               ' | '.join(desc(rec) for rec in cands[:6])])
        write('C7_sst_vs_dor_address_file', ['dor_file_line', 'zip', 'plus4', 'street', 'house_from', 'house_to', 'side',
                                              'dor_file_code', 'sst_codes', 'rate_differs', 'sst_records'], c7, '', '')
        print(f'C7: {missing} DOR address-file rows had no SST record with the same ZIP+4/street/range', file=sys.stderr)

    # C8: ZIP5 rule
    zip_rates = collections.defaultdict(set)
    for rec in A:
        rr = R(rec['code'])[1]
        if rr is not None:
            zip_rates[rec['r'][15]].add(rr)
    for z, rows in by_zip.items():
        for x in rows:
            rr = R(x[3]['code'])[1]
            if rr is not None:
                zip_rates[z].add(rr)
    c8 = []
    for z, recs in sorted(z5.items()):
        if len({x['code'] for x in recs}) > 1 or not zip_rates.get(z):
            continue
        zr = R(recs[0]['code'])[1]
        lo, hi = min(zip_rates[z]), max(zip_rates[z])
        if zr is None:
            pos = 'no location code on Z record'
        else:
            pos = 'only rate' if lo == hi else ('lowest' if zr == lo else ('highest' if zr == hi else ('middle' if lo < zr < hi else 'outside range')))
        c8.append([z, recs[0]['code'], R(recs[0]['code'])[0], zr, lo, hi, pos, recs[0]['line']])
    write('C8_zip5_rule', ['zip', 'z_code', 'z_name', 'z_rate', 'lowest_rate_in_zip', 'highest_rate_in_zip', 'z_position', 'sst_line'], c8, '', '')

if __name__ == '__main__':
    main()
