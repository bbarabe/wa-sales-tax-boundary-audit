#!/usr/bin/env python3
"""Query DOR's live address lookup (AddressRates) for rows of a results CSV and record what it returns.

Usage:
  python3 check_addressrates.py IN.csv OUT.csv --addr "{house_from} {street}" --zip "{zip}" \
      [--city ""] [--sample N --seed 7] [--delay 0.25]

--addr, --zip and --city are Python format strings over the CSV columns. Use --zip "{zip}-{plus4_from}"
with --addr "" to query a ZIP+4 on its own. Adds columns api_code, api_rate, api_result_code,
api_zip, api_plus4. Be polite: keep --delay at 0.2 s or more.

DOR documents the interface at https://dor.wa.gov/wa-sales-tax-rate-lookup-url-interface
(ResultCode 0 = address found, 1 = ZIP+4 found, 2/3/4 = updated or corrected, 5 = ZIP5 only).
"""
import argparse, csv, random, re, sys, time, urllib.parse, urllib.request

URL = 'https://webgis.dor.wa.gov/webapi/AddressRates.aspx?'

def lookup(addr, city, zip_):
    q = urllib.parse.urlencode({'output': 'xml', 'addr': addr, 'city': city, 'zip': zip_})
    for attempt in range(3):
        try:
            x = urllib.request.urlopen(URL + q, timeout=30).read().decode('utf-8', 'replace')
            break
        except Exception as e:  # network hiccup: retry
            x = ''
            time.sleep(2 * (attempt + 1))
    g = lambda p: (re.search(p, x) or [None, ''])[1]
    return {'api_code': g(r'loccode="(\d+)"'), 'api_rate': g(r'<response[^>]* rate="([.\d]+)"'),
            'api_result_code': g(r'<response[^>]* code="(\d+)"'), 'api_zip': g(r'<addressline[^>]* zip="(\d+)"'),
            'api_plus4': g(r'plus4="(\d+)"')}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--addr', required=True); ap.add_argument('--zip', required=True); ap.add_argument('--city', default='')
    ap.add_argument('--sample', type=int, default=0); ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--delay', type=float, default=0.25)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.inp, newline='')))
    if a.sample and a.sample < len(rows):
        random.seed(a.seed)
        rows = random.sample(rows, a.sample)
    with open(a.out, 'w', newline='') as f:
        w = None
        for i, r in enumerate(rows, 1):
            res = lookup(a.addr.format(**r), a.city.format(**r), a.zip.format(**r))
            r = {**r, **res}
            if w is None:
                w = csv.DictWriter(f, fieldnames=list(r.keys())); w.writeheader()
            w.writerow(r); f.flush()
            if i % 50 == 0:
                print(f'{i}/{len(rows)}', file=sys.stderr)
            time.sleep(a.delay)

if __name__ == '__main__':
    main()
