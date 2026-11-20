"""Join Washington's Q4 boundary rows to its SST general intrastate rate file.

Technology Guide chapter 5: type 45 for state, 00 for county, 01 for place,
63 for a special district. The composite SER code is for reporting.
Outputs use decimal fractions and effective dates inclusive at both ends.
"""
import argparse
import csv
from collections import Counter, defaultdict
from decimal import Decimal
from functools import lru_cache
from pathlib import Path


def classify(value, observed):
    lo, hi = min(observed), max(observed)
    if value < lo or value > hi:
        return "outside range"
    if lo == hi:
        return "only rate"
    if value == lo:
        return "lowest"
    return "highest" if value == hi else "middle"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("sst", "sst-rates", "rates", "date", "out"):
        parser.add_argument("--" + field, required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rates = {}
    with open(args.sst_rates, newline="") as source:
        for state, kind, code, general, _, _, _, start, end in csv.reader(source):
            if start <= args.date <= end:
                key = (state, kind, code)
                if key in rates:
                    raise ValueError(f"Duplicate effective rate for {key}")
                rates[key] = Decimal(general)
    with open(args.rates, encoding="utf-8-sig", newline="") as source:
        dor = {r["Code"]: Decimal(r["Rate"]) for r in csv.DictReader(source)}

    @lru_cache(maxsize=None)
    def total(fields):
        state, indicator, county, place = fields[:4]
        components = [("45", indicator), ("00", county), ("01", place)]
        # Washington uses state-assigned special district codes in triplets.
        for idx in range(7, len(fields), 3):
            spec, code, qualifier = fields[idx:idx+3]
            if code and (spec, qualifier) != ("ST", "45"):
                raise ValueError(f"Unrecognized special district {spec, code, qualifier}")
            components.append(("63", code))
        return sum(rates[state, kind, code] for kind, code in components if code)

    observed = defaultdict(set)
    zrows = {}
    crosswalk = Counter()
    a4 = defaultdict(set)
    f4 = defaultdict(set)
    with open(args.sst, newline="", encoding="ascii") as source:
        for line, r in enumerate(csv.reader(source), 1):
            if not r[1] <= args.date <= r[2]:
                continue
            # The three fields preceding the district triplets are empty in this release.
            if len(r) == 90 and not r[-1]:
                r.pop()  # WA includes a trailing comma after the 20th district.
            if any(r[26:29]) or (len(r)-29) % 3:
                raise ValueError(f"Unrecognized boundary layout at line {line}")
            value = total(tuple(r[22:]))
            code = r[30][1:] if r[30].startswith("L") else r[21][-4:]
            crosswalk[(r[0], code, value, dor.get(code))] += 1
            if r[0] == "A":
                observed[r[15]].add(value)
                if r[16]:
                    a4[r[15], r[16]].add(value)
            elif r[0] == "4":
                if r[17] != r[19]:
                    raise ValueError(f"Cross-ZIP range at line {line}")
                observed[r[17]].add(value)
                for p4 in range(int(r[18]), int(r[20])+1):
                    f4[r[17], f"{p4:04d}"].add(value)
            elif r[0] == "Z":
                if r[17] != r[19] or r[17] in zrows:
                    raise ValueError(f"Expected one ZIP per active Z row at line {line}")
                zrows[r[17]] = (line, r[21], code, value)

    with (out/"sst_zip5_rates.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["zip","sst_line","composite_ser","mapped_code","sst_rate","min_A_or_4","max_A_or_4","position"])
        for z,(line,ser,code,v) in sorted(zrows.items()):
            vals = observed[z]
            w.writerow([z,line,ser,code,v,min(vals),max(vals),classify(v, vals)])
    with (out/"sst_rate_crosswalk.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_type","mapped_code","sst_rate","dor_rate","row_count"])
        for (typ,code,v,d), count in sorted(crosswalk.items()):
            w.writerow([typ,code,v,d,count])
    with (out/"sst_zip4_rate_checks.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["zip","plus4","min_A_rate","record_4_rates","finding"])
        for key, vals in sorted(a4.items()):
            choices = f4.get(key, set())
            if not choices or choices != {min(vals)}:
                issue = "missing" if not choices else "multiple rates" if len(choices)>1 else "differs from A minimum"
                w.writerow([*key,min(vals)," | ".join(map(str,sorted(choices))),issue])


if __name__ == "__main__":
    main()
