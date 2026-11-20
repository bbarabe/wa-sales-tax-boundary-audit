# Washington sales-tax boundary data audit (Q4 2026)

Washington publishes its address-level sales-tax jurisdictions in two forms:
- **The Streamlined Sales Tax (SST) boundary file** (`WAB2026Q4AUG27.csv`). These are Washington's address, ZIP+4 and ZIP5 records in the SST format, and certified tax software is built on them. Washington's certificate says sellers must use its address-based records to get liability relief (item 305115).
- **DOR's own downloads** (address file, ZIP+4 files), plus **DOR's live AddressRates lookup**.

This repo checks the published data against the SST rules, against itself, and against DOR's live lookup. Everything is reproducible from public files with the scripts in [`scripts/`](scripts/). All results are for records effective 2026-11-20.

The rules are quoted, with page numbers, in [docs/sst-rules.md](docs/sst-rules.md). The sources are the Agreement (SSUTA), the SST Technology Guide, and Washington's own 2026 Certificate of Compliance.

## For tax generalists: what we found

**1. The rules allow two ways to look an address up, and Washington's file gives different answers depending on which one is used.**
- **The rules:** standardize the address (USPS or CASS) and match every field exactly, the suite included. The ZIP+4 may be left in the match or left out.
- **What the file does:** in **101 buildings** (75 rate-changing), the outcome depends on that choice. Leaving the ZIP+4 out matches the street's block record. Keeping the building's ZIP+4 falls through to a ZIP+4 record carrying the building's own rate. At all three buildings we checked with USPS, the building's ZIP+4 was one of its suite ZIP+4s.
- **What the Technology Guide expects:** records built so that both queries give the same result, and a range covering only addresses that share its ZIP+4.
- **What DOR's lookup does:** it gave the building's rate in all 75 rate-changing cases.
- **This is the pattern QuickBooks support described ("the address needs the suite").** It is real, but it is limited to about a hundred buildings.

**2. The two state sources disagree, and DOR's lookup follows DOR's file, not the SST file.**
- DOR's address file and the SST file give different jurisdictions for **7,002** address ranges. 5,247 of them change the rate, across 347 ZIP codes.
- In a random sample of 200, DOR's lookup returned DOR's file's code 190 times and the SST file's 8 times (2 neither).
- Software that follows the SST file will usually disagree with DOR on those ranges, with no suite or typing error involved.

**3. The file breaks its own "one record per address" rule in hundreds of places.**
- **692** stretches of street (in 167 ZIPs, 520 rate-changing) are covered by two address records with different codes, neither with a suite.
- The rules give no tie-break.
- Including the ZIP+4 separates 686 of them, but which record wins then depends on the ZIP+4 USPS assigns.
- DOR's lookup picked the narrower record in 671 (513 of the 520 rate-changing).

**4. The clearest violations: duplicate ZIP+4 records.**
- The Technology Guide says a ZIP+4 "may not be in more than one '4' record."
- **15** ZIP+4s are in two records with different codes (10 change the rate). One of them is 3058 Camp 2 Rd, split between Skagit and Whatcom counties.

**5. ZIP records don't follow Washington's declared policy.**
- Washington's Certificate of Compliance declares that ZIP+4 and 5-digit ZIP records carry the lowest rate in the area.
- In ZIPs with several rates, the 5-digit ZIP record is the *highest* rate in 110 ZIPs, the middle one in 49 and the lowest in 47.
- 4 ZIP+4 records aren't the lowest rate of their addresses, and 9 ZIP+4s used by addresses have no ZIP+4 record at all.
- The Agreement has allowed highest or blended 5-digit rates since 2024, but Washington chose lowest.

**Two specific addresses show these patterns in action:**

| Address | What happens | Kind | Write-up |
|---|---|---|---|
| 14450 Woodinville-Redmond Rd NE, Woodinville 98072 | **No suite:** the rules allow 8.9% (block record) or 10.4% (USPS ZIP+4 98072-9051); that ambiguity is a data defect (pattern 1). **Ste 101-A (the real suite):** every rule-compliant reading gives 10.4%. QuickBooks charges 8.9% for both, which for Ste 101-A requires dropping the suite | Specific record, one instance of pattern 1; plus a QuickBooks behavior the rules don't support | [case study](docs/case-14450-woodinville-redmond-rd-ne.md) |
| 3058 Camp 2 Rd, Sedro-Woolley 98284-9508 | Two address records and two ZIP+4 records for the same address, in two counties (8.7% / 8.9%), recurring since 2022 | Specific record, one instance of finding 4 | [case study](docs/case-3058-camp-2-rd.md) |

## For engineers

### Repository layout

```
scripts/download_data.sh            fetch DOR + SST Q4 2026 files into ./data
scripts/scan_sst_conflicts.py       full conflict scan of the SST file (C1–C8)
scripts/scan_dor_address_file.py    overlap scan of DOR's own address file
scripts/check_addressrates.py       query DOR's live AddressRates for each row of a CSV
scripts/summarize_api_checks.py     which record DOR's lookup sided with, per check
scripts/check_zip4_resolution.py    would including the ZIP+4 separate the C1 / C4a conflicts?
scripts/sst_lookup.py               SST lookup replay: two rule-compliant modes + one with assumptions
scripts/extract_sst_rows.py         all rows (every effective date) for an address / ZIP+4
scripts/wsrl/                       DOR's sample C# library, built unmodified, + a driver
tests/test_inputs.tsv               33 test addresses as typed
tests/test_inputs_standardized.tsv  the same with the USPS-standardized ZIP+4 (2026-11-20)
results/2026Q4/                     every output CSV / summary
docs/                               rules, method, case studies, sample-library review, QuickBooks tests
```

### Reproduce

```bash
scripts/download_data.sh                                   # ~450 MB unzipped, into ./data
python3 scripts/scan_sst_conflicts.py --sst data/WAB2026Q4AUG27.csv --rates data/Rates_26Q4.csv \
    --dor-address data/State_26Q4.txt --date 20261120 --out out/          # ~3 min
python3 scripts/sst_lookup.py --sst data/WAB2026Q4AUG27.csv --date 20261120 \
    --inputs tests/test_inputs_standardized.tsv --out out/sst_lookup_standardized.csv
python3 scripts/check_zip4_resolution.py --sst data/WAB2026Q4AUG27.csv --date 20261120 --results out/
python3 scripts/check_addressrates.py out/C1_address_overlaps_no_suite.csv out/C1_api.csv \
    --addr "{house_from} {street}" --zip "{zip}" --delay 0.3            # live DOR queries
python3 scripts/summarize_api_checks.py out/
scripts/wsrl/run_wsrl.sh data tests/wsrl_inputs.tsv                    # needs mono-mcs
```

Python 3.8+, standard library only. The USPS ZIP+4s in `tests/test_inputs_standardized.tsv` were looked up by hand on tools.usps.com.

### Lookup rules and replay modes

The procedure (SSUTA §309.A.2; TG ch. 5):
1. Standardize the address.
2. Match it to the address (`A`) records.
3. If that fails, match the standardized ZIP+4 to the `4` records.
4. If that fails, use the `Z` record.

Every address field must match exactly, the suite included. The only stated exception is that the ZIP extension may be left out of the address match. There is no tie-break rule, because an address may be valid for one row only.

`sst_lookup.py` reports:

| Mode | In the rules? | On the 31 QuickBooks inputs (standardized) |
|---|---|---|
| strict, ZIP+4 left out of the address match | yes | = QuickBooks 19, = DOR 9, ambiguous 8 |
| strict, ZIP+4 in the address match | yes | = QuickBooks 14, = DOR **22**, ambiguous 0 |
| assumptions: unlisted suite dropped, single address beats block, ZIP+4 left out | **no** | = QuickBooks **31**, = DOR 13 |

QuickBooks and DOR's lookup agreed on 13 of the 31. The full per-input table is [`results/2026Q4/test_inputs_comparison.csv`](results/2026Q4/test_inputs_comparison.csv); the discussion is in [docs/quickbooks-online-tests.md](docs/quickbooks-online-tests.md).

### Checks

| ID | Check | Rows | Rate-changing | Rule |
|---|---|---|---|---|
| C1 | No-suite address records overlap with different codes | 692 segments (3,277 house-number candidates) | 520 | TG p. 25, one row per address |
| C2 | Duplicate ZIP+4 records with different codes | 15 | 10 | TG p. 26 (explicit) |
| C3 | Duplicate ZIP5 records | 0 | – | TG p. 26 |
| C4a | Listed suites carry a code that no no-suite record covering the building carries | 101 buildings | 75 | TG p. 25, same result with or without ZIP+4 |
| C4b | Suites differ from a block record but agree with an overlapping single-address record (a C1 situation) | 292 buildings | 218 | TG p. 25 |
| C5 | Overlapping suite records within a building | 0 | – | TG p. 25 |
| C6 | ZIP+4 missing, or not the lowest rate of its addresses | 13 | 4 | SSUTA §305.A.6(a); WA CoC 305080 |
| C7 | SST file vs DOR's address file, same ZIP+4/street/range | 7,002 ranges | 5,247 | consistency between the state's two publications |
| C8 | Position of each ZIP5 record's rate within its ZIP | 715 ZIPs | – | WA CoC 305081/308041 ("Lowest rate") |

- **House numbers are candidates:** the counts are numbers inside a conflicting range, not verified addresses.
- **C8 coverage:** 387 ZIPs have a single rate. 122 ZIP5 records carry only a composite `09xxx` code with no `L` location code, so this method can't map them to a DOR rate.
- **Would the ZIP+4 separate the conflicts?** It would for 686 of the 692 C1 segments: each record carries its own ZIP+4. For all 101 C4a buildings, the suite ZIP+4s appear on no no-suite record, and their `4` records carry the suites' code. See [`results/2026Q4/zip4_resolution.md`](results/2026Q4/zip4_resolution.md).

### Results against DOR's live lookup

DOR's AddressRates was queried for every row of C1, C2 and C4, and for a random sample of 200 rows of C7. Full tables: [`results/2026Q4/api_check_summary.md`](results/2026Q4/api_check_summary.md).

| Check | DOR's lookup sided with | Rows |
|---|---|---|
| C1 overlapping no-suite records | the narrower record | 671 of 692 (513 of 520 rate-changing) |
| C4a building suites vs. street record | the suites' code, for a query with **no** suite | 94 of 101 (75 of 75 rate-changing) |
| C4b suites vs. overlapping records | the narrowest no-suite record | 278 of 292 (214 of 218 rate-changing) |
| C7 SST file vs. DOR address file | DOR's address file | 190 of 200 (SST file: 8, neither: 2) |
| C2 duplicate ZIP+4s | one of the two duplicates (ZIP+4-only query) | 15 of 15 |

**DOR's own address download** has overlaps of the same kind: 494 segments, 368 of them rate-changing. There, DOR's lookup agreed with the most specific row in 467 of 494. Files: `results/2026Q4/dor_address_file_conflicts.csv` (scan) and `dor_address_file_conflicts_api.csv` (same segments with DOR's live answer).

### DOR's sample library

WaRateFileLookup 1.0.5 (2011) was built unmodified and run against the Q4 2026 files. It agrees with DOR's live lookup on 21 of 31 inputs. How it works:
- **No standardization:** it uses Metaphone fuzzy matching instead, and has no suite support.
- **ZIP+4 ignored:** the ZIP+4 is never used to choose between rows.
- **File-order ties:** overlapping rows resolve by file order.
- **Odd/even:** the check is one-sided.
- **ZIP5 fallback:** it takes the lowest rate in the ZIP, which does match Washington's declared ZIP5 policy.

Details: [docs/dor-sample-library.md](docs/dor-sample-library.md).

### DOR's live lookup

How AddressRates behaves compared with the SST procedure:
- **It ignores the suite.** Every variant tried for 14450 returned 1735, including "Ste 9999".
- **It corrects street names.** Where USPS couldn't standardize a misspelled name, it corrected it instead of dropping to the ZIP5 record.
- **It reported a different ZIP.** It gave `zip="98052"` for 14450, which USPS and both DOR files put in 98072.

## Caveats

- **The live lookups are a moving target.** DOR's and USPS's data can change at any time; every check here ran on 2026-11-20.
- **Some checks are sampled.** C7 was checked live on a random sample of 200 rows (seed 7). C1, C2 and C4 were checked on every row, using one house number per row.
- **No position on whether any address is taxable at a given rate.** This is a data-consistency audit. Washington relieves sellers who rely on its databases from errors in them (RCW 82.32.430; WA CoC 306010).
- **QuickBooks results are observed, not inferred.** They show what QuickBooks returned. They don't show how QuickBooks standardized the address or which data it uses.

## License

Code is MIT ([LICENSE](LICENSE)). The input data is published by Washington DOR and the Streamlined Sales Tax Governing Board. The result CSVs and docs are derived from it and may be reused freely, with attribution appreciated.
