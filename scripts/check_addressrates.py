#!/usr/bin/env python3
"""Query DOR's live address lookup (AddressRates) for rows of a results CSV and record what it returns.

Usage:
  python3 check_addressrates.py IN.csv OUT.csv --addr "{house_from} {street}" --zip "{zip}" \
      [--city ""] [--sample N --seed 7] [--delay 0.25]

--addr, --zip and --city are Python format strings over the CSV columns. Use --zip "{zip}-{plus4_from}"
with --addr "" to query a ZIP+4 on its own. Adds columns api_code, api_rate, api_result_code,
api_zip, api_plus4, api_street, api_house_low and api_house_high.
Be polite: keep --delay at 0.2 s or more.

DOR documents the interface at https://dor.wa.gov/wa-sales-tax-rate-lookup-url-interface
(ResultCode 0 = address found, 1 = ZIP+4 found, 2/3/4 = updated or corrected, 5 = ZIP5 only).
"""
import argparse, csv, random, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

URL = 'https://webgis.dor.wa.gov/webapi/AddressRates.aspx?'

def response_fields(xml):
    root = ET.fromstring(xml)
    if root.tag != 'response' or 'code' not in root.attrib:
        raise ValueError('Unexpected AddressRates response')
    address = root.find('addressline')
    fields = {} if address is None else address.attrib
    return {'api_code': root.get('loccode', ''), 'api_rate': root.get('rate', ''),
            'api_result_code': root.get('code'), 'api_zip': fields.get('zip', ''),
            'api_plus4': fields.get('plus4', ''), 'api_street': fields.get('street', ''),
            'api_house_low': fields.get('houselow', ''), 'api_house_high': fields.get('househigh', '')}


def lookup(addr, city, zip_):
    q = urllib.parse.urlencode({'output': 'xml', 'addr': addr, 'city': city, 'zip': zip_})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(URL + q, timeout=30) as response:
                return response_fields(response.read())
        except (OSError, ET.ParseError, ValueError):
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))

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
