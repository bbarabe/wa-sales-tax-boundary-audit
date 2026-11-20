"""Compare every explicit DOR long-file key to its covering short-file range."""
import argparse
import csv
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--short", required=True)
    parser.add_argument("--long", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    Path(args.out).parent.mkdir(exist_ok=True, parents=True)
    with open(args.short, newline="") as sf, open(args.long, newline="") as lf, open(args.out, "w", newline="") as dest:
        ranges = iter(csv.reader(sf))
        short = next(ranges, None)
        writer = csv.writer(dest)
        writer.writerow(["zip", "plus4", "long_code", "short_code", "long_rate", "short_rate"])
        for count, long_row in enumerate(csv.reader(lf), 1):
            key = tuple(long_row[:2])
            while short and (short[0], short[2]) < key:
                short = next(ranges, None)
            if not short or short[0] != key[0] or short[1] > key[1]:
                raise ValueError(f"No covering short range for {key}")
            if short[3:] != long_row[2:]:
                writer.writerow([*key, long_row[2], short[3], long_row[5], short[6]])
    print(f"Compared {count:,} long-file rows")


if __name__ == "__main__":
    main()
