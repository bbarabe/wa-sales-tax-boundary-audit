# Washington sales-tax boundary data audit (Q4 2026)

Washington publishes its address-level sales-tax jurisdictions in two ways. Software that follows the rules can still end up charging a different rate than the Department of Revenue's (DOR) own lookup, so this repo checks the published data against itself and against DOR's live lookup.

The two publications are:
- **The Streamlined Sales Tax (SST) boundary file** (`WAB2026Q4AUG27.csv`), which certified tax software is built on.
- **DOR's own downloads** (address file, ZIP+4 files) and **DOR's live AddressRates lookup**.

Everything here is reproducible from public files with the scripts in [`scripts/`](scripts/). All results are for records effective 2026-11-20.

## For tax generalists: what we found

**1. The two state sources disagree, and DOR's lookup follows DOR's file, not the SST file.**
- DOR's address file and the SST file give different jurisdictions for **7,002** address ranges.
  - 5,247 of these change the rate.
  - They are spread across 347 ZIP codes.
- In a random sample of 200 ranges, DOR's live lookup returned DOR's file's code 190 times and the SST file's 8 times (2 neither).
- Software that implements the SST file to the letter will disagree with DOR's lookup on those ranges. No suite or data-entry error is involved.

**2. Some buildings are coded differently from their own block.** In **101** buildings, every listed suite carries a different code than the street record covering the building (75 change the rate).
- **What SST-based software does:**
  - Without a suite, or with a suite the file doesn't list, it gets the street record's rate.
  - With a listed suite, it gets the suite rate.
- **What DOR's lookup does:** it ignores the suite and returned the suites' code in all 75 rate-changing cases.
- **This is the pattern QuickBooks support described ("the address needs the suite").** It is real, but it affects about a hundred buildings statewide, not Washington's data in general.

**3. The file breaks its own uniqueness rule in hundreds of places.** The SST spec says an address can match only one record. Here, **692** stretches of street (in 167 ZIPs, 520 rate-changing) are covered by two address records with different codes, each with no suite. DOR's lookup returned the narrower record's code in 671 of them (513 of the 520 rate-changing), so software that lets the narrower record win mostly agrees with DOR (see [results](#results)).

**4. Smaller defects:**
- 15 ZIP+4s appear twice with different codes (10 change the rate).
- 13 ZIP+4 problems: 9 ZIP+4s used by addresses have no ZIP+4 record, and 4 ZIP+4 records don't carry the lowest rate of their addresses as SSUTA §305 requires.
- 5-digit ZIP fallback records are often the *highest* rate in the ZIP: 110 ZIPs highest, 49 middle, 47 lowest.

**Two specific addresses show these patterns in action:**

| Address | Problem | Kind | Write-up |
|---|---|---|---|
| 14450 Woodinville-Redmond Rd NE, Woodinville 98072 | SST-based software gives 8.9% where DOR gives 10.4%: the block record says unincorporated King County, and the building's no-suite record was dropped in 2025 | Specific record. It is one instance of pattern 2 | [case study](docs/case-14450-woodinville-redmond-rd-ne.md) |
| 3058 Camp 2 Rd, Sedro-Woolley 98284-9508 | Two records for the same address and ZIP+4, in two counties (Skagit 8.7% / Whatcom 8.9%), recurring since 2022 | Specific record. It is one instance of defect 4 | [case study](docs/case-3058-camp-2-rd.md) |

Specific problems can be fixed by editing one record. Systemic problems are patterns found across the file; each comes with a full list in `results/2026Q4/`.

## For engineers

### Repository layout

```
scripts/download_data.sh          fetch DOR + SST Q4 2026 files into ./data
scripts/scan_sst_conflicts.py     full conflict scan of the SST file (C1–C8)
scripts/scan_dor_address_file.py  overlap scan of DOR's own address file
scripts/check_addressrates.py     query DOR's live AddressRates for each row of a CSV
scripts/summarize_api_checks.py   which record DOR's lookup sided with, per check
scripts/sst_lookup.py             SST lookup replay (strict, and with two assumptions)
scripts/extract_sst_rows.py       all rows (every effective date) for an address / ZIP+4
scripts/wsrl/                     DOR's sample C# library, built unmodified, + a driver
tests/test_inputs.tsv             33 standardized test addresses
results/2026Q4/                   every output CSV
docs/                             method, case studies, sample-library review, QuickBooks tests
```

### Reproduce

```bash
scripts/download_data.sh                                   # ~450 MB unzipped, into ./data
python3 scripts/scan_sst_conflicts.py --sst data/WAB2026Q4AUG27.csv --rates data/Rates_26Q4.csv \
    --dor-address data/State_26Q4.txt --date 20261120 --out out/          # ~3 min
python3 scripts/sst_lookup.py --sst data/WAB2026Q4AUG27.csv --date 20261120 \
    --inputs tests/test_inputs.tsv --out out/sst_lookup_test_inputs.csv
python3 scripts/check_addressrates.py out/C1_address_overlaps_no_suite.csv out/C1_api.csv \
    --addr "{house_from} {street}" --zip "{zip}" --delay 0.3            # live DOR queries
python3 scripts/summarize_api_checks.py out/
scripts/wsrl/run_wsrl.sh data tests/wsrl_inputs.tsv                    # needs mono-mcs
```

Python 3.8+, standard library only.

### How a lookup should work (SST Technology Guide, ch. 5)

Address record → ZIP+4 record → ZIP5 record, using exact matches on every address component (the ZIP extension may be left out of the address match). Each address, ZIP+4 and ZIP5 may be valid for **one** row only. The guide does not say what to do with a suite the file doesn't list, or with overlapping rows, because overlapping rows shouldn't exist. `sst_lookup.py` reports both readings:
- **strict:** an unlisted suite gets no address match, and overlapping rows come out as *ambiguous*.
- **assumptions:** an unlisted suite is dropped, and in an overlap the single-address row beats the block row. QuickBooks Online matched this mode on 31 of 31 inputs.

See [docs/method.md](docs/method.md).

### Checks

| ID | Check | Rows | Rate-changing | Kind |
|---|---|---|---|---|
| C1 | No-suite address records overlap with different codes | 692 segments (3,277 house-number candidates) | 520 | systemic |
| C2 | Duplicate ZIP+4 records with different codes | 15 | 10 | systemic (incl. 3058 Camp 2 Rd) |
| C3 | Duplicate ZIP5 records | 0 | – | – |
| C4a | Listed suites carry a code no no-suite record covering the building carries | 101 buildings | 75 | systemic (incl. 14450) |
| C4b | Suites differ from a block record but agree with an overlapping single-address record (a C1 situation) | 292 buildings | 218 | systemic, resolved by narrow-wins |
| C5 | Overlapping suite records within a building | 0 | – | – |
| C6 | ZIP+4 missing, or not the lowest rate of its addresses | 13 | 4 | systemic |
| C7 | SST file vs DOR's address file, same ZIP+4/street/range | 7,002 ranges | 5,247 | systemic |
| C8 | Position of each ZIP5 record's rate within its ZIP | 715 ZIPs | – | systemic |

House-number counts are *candidates*: numbers inside a conflicting range, not verified addresses.

For C8:
- 387 ZIPs have a single rate.
- In the ZIPs with several rates, the ZIP5 record is the highest rate in 110, the middle one in 49 and the lowest in 47.
- The other 122 ZIP5 records carry only a composite `09xxx` code with no `L` location code, so this method can't map them to a DOR rate.

### Results

DOR's live AddressRates lookup was queried for every row of C1, C2 and C4, and for a random sample of 200 rows of C7 (full tables in [`results/2026Q4/api_check_summary.md`](results/2026Q4/api_check_summary.md)):

| Check | DOR's lookup sided with | Rows |
|---|---|---|
| C1 overlapping no-suite records | the narrower record | 671 of 692 (513 of 520 rate-changing) |
| C4a building suites vs. street record | the suites' code, for a query with **no** suite | 94 of 101 (75 of 75 rate-changing) |
| C4b suites vs. overlapping records | the narrowest no-suite record | 278 of 292 (214 of 218 rate-changing) |
| C7 SST file vs. DOR address file | DOR's address file | 190 of 200 (SST file: 8, neither: 2) |
| C2 duplicate ZIP+4s | one of the two duplicates (ZIP+4-only query) | 15 of 15 |

Two consequences for anyone implementing the SST file:
- **C1 and C4b are mostly harmless in practice.** "Narrowest record wins" reproduces DOR's answer in all but 7 rate-changing C1 cases.
- **C4a and C7 are not harmless.** Correct SST matching gives a different rate than DOR's own lookup, and no tie-break rule can fix it.

DOR's own address download has the same kind of overlaps: 494 segments, 368 of them rate-changing. There, DOR's lookup agreed with the most specific row in 467 of 494.

Files: `results/2026Q4/dor_address_file_conflicts.csv` (scan) and `dor_address_file_conflicts_api.csv` (same segments with DOR's live answer).

### DOR's sample library

WaRateFileLookup 1.0.5 (2011) was built unmodified and run against the Q4 2026 files. It agrees with DOR's live lookup on 21 of 31 inputs. The main reasons it differs:
- The ZIP+4 is not used to choose between rows.
- Overlapping rows resolve by file order.
- The odd/even check is one-sided.
- Its ZIP5 fallback takes the lowest rate in the ZIP.

Details: [docs/dor-sample-library.md](docs/dor-sample-library.md).

### DOR's live lookup

Observed behavior of AddressRates, which the SST spec doesn't describe:
- It ignores the suite: every variant tried for 14450 returned 1735, including "Ste 9999".
- It corrects street names instead of dropping to the ZIP5 record.
- It reported `zip="98052"` for 14450, which USPS and both DOR files put in 98072.

## Caveats

- **The live lookup is a moving target.** It reflects DOR's current data and may change at any time; every check here ran on 2026-11-20.
- **Some checks are sampled.** C7 was checked live on a random sample of 200 rows (seed 7). C1, C2 and C4 were checked on every row, using one house number per row.
- **No position on whether any address is taxable at a given rate.** This is a data-consistency audit only. Sellers relying on the state's databases have statutory relief from errors in them (RCW 82.32.430).
- **QuickBooks results are observed, not inferred.** They show what QuickBooks returned, not which data it uses.

## License

Code is MIT ([LICENSE](LICENSE)). The input data is published by Washington DOR and the Streamlined Sales Tax Governing Board. The result CSVs and docs are derived from it and may be reused freely, with attribution appreciated.
