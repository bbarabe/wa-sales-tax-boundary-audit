# Washington sales-tax boundary audit · Q4 2026

For November 20, 2026, Washington's published SST records, state downloads and live lookup can yield different jurisdictions for the same supplied location. The most useful evidence is a duplicate within the SST file itself, a geographic cross-check for the Woodinville venue, and a full rate-file comparison for all 715 ZIP5 records. [Verification report](docs/verification-report.md) · [Rules and official sources](docs/sst-rules.md)

| Question | Verified result |
|---|---|
| Where is the Woodinville building? | King County's building point lies inside DOR's 1735 Woodinville polygon. AddressRates also returned 1735, 10.4%. QuickBooks displayed 8.9% for STE 101-A and 10.4% for STE 101. USPS returned several candidates for 101-A. STE 105 produced a single postal result and the same QuickBooks discrepancy. [Case study](docs/case-14450-woodinville-redmond-rd-ne.md) |
| Is there an unequivocal duplicate? | At 3058 Camp 2 Rd, two active street records cover the address and two active ZIP+4 rows cover 98284-9508. The records identify different counties and rates, 8.7% and 8.9%. [Source lines and state comparisons](docs/case-3058-camp-2-rd.md) |
| Does the five-digit fallback reflect Washington's declared minimum? | Among 287 ZIPs with multiple rates present on SST A or 4 rows, the ZIP5 row carries the highest observed rate in 127, an intermediate rate in 57 and the lowest in 103. The other 428 have a single observed rate. [All 715 ZIPs](results/2026Q4/sst_zip5_rates.csv) · [Washington certificate](https://sst.streamlinedsalestax.org/CC/form/14955) |
| Do the two street downloads agree? | 7,002 DOR rows passed the different-code screen, across 347 ZIPs. 5,247 were rate-changing, across 251 ZIPs. In a seeded sample of 200 flagged rows, the live query agreed with the DOR download in 190, the SST candidate in 8 and neither in 2. [Full list](results/2026Q4/C7_sst_vs_dor_address_file.csv) |
| How closely did QuickBooks and DOR agree? | The 31 nonrandom ship-to variants reproduced on the existing test invoice. The observed jurisdiction and DOR's code agreed on 13. A replay with extension omitted, blank-suite fallback and a single-number preference fit all 31. Only Intuit can identify the actual source and selected record. [Tests](docs/quickbooks-online-tests.md) |

## Statewide file checks

| Check | Count | Rate-changing | Meaning |
|---|---:|---:|---|
| C1 | 692 segments in 167 ZIPs | 520 | Blank-suite street ranges overlap when extension is omitted. There are 3,277 house-number candidates. Disjoint extensions distinguish the conflicting codes in 686 segments. |
| C2 | 15 ZIP+4s | 10 | Different-code ZIP+4 fallbacks overlap on the same date. |
| C3 | 0 | — | Different-code duplicate ZIP5 records. |
| C4a | 101 building groups | 75 | Listed suite codes differ from every covering blank-suite code. The result for a no-suite address depends on the postal candidate chosen. |
| C4b | 292 building groups | 218 | A narrower blank-suite row agrees with the listed suite code, while another covering row differs. |
| C5 | 0 | — | Different-code overlaps detected by the suite-range test. |
| C6 | 9 missing ZIP+4 fallbacks and 4 above the address minimum | 4 | Based on extensions carried by active address rows. C2 covers conflicting fallbacks separately. |
| C7 | 7,002 DOR street rows | 5,247 | State publications differ on the parity-compatible matched range. |
| C8 | 715 ZIP5 totals | 184 above the observed minimum | Sum the dated SST rate components, including rows without an identifiable DOR location code. |

DOR's separate address download contains 494 conflict segments, 368 rate-changing. Counts across checks can overlap. A segment, building group or queried address string is a different unit of observation. None measures the number of taxpayers charged incorrectly. [Methods](docs/method.md) · [Machine-readable results](results/2026Q4/)

## Reproduction

Run from the repository root. The scans use Python's standard library. The shell download script needs curl and unzip. Public feeds can change; compare the [archive hashes](docs/verification-report.md#source-archives).

```bash
bash scripts/download_data.sh
python scripts/scan_sst_conflicts.py --sst data/WAB2026Q4AUG27.csv --rates data/Rates_26Q4.csv --dor-address data/State_26Q4.txt --date 20261120 --out out
python scripts/check_sst_rates.py --sst data/WAB2026Q4AUG27.csv --sst-rates data/WAR2026Q4AUG27.csv --rates data/Rates_26Q4.csv --date 20261120 --out out
python scripts/compare_dor_zip4.py --short data/Zip4RatesQ42026-Short.txt --long data/Zip4RatesQ42026-Long.txt --out out/dor_zip4_format_differences.csv
python scripts/scan_dor_address_file.py --address data/State_26Q4.txt --rates data/Rates_26Q4.csv --out out/dor_address_file_conflicts.csv
python scripts/sst_lookup.py --sst data/WAB2026Q4AUG27.csv --date 20261120 --inputs tests/test_inputs_standardized.tsv --out out/sst_lookup_standardized.csv
python scripts/check_zip4_resolution.py --sst data/WAB2026Q4AUG27.csv --date 20261120 --results out
python scripts/summarize_api_checks.py results/2026Q4
```

The stored API tables are dated observations. The live recheck contains the query and the returned street, range, ZIP and result status. The summary of the original run and the differences on repeat are documented separately. [Original API summary](results/2026Q4/api_check_summary.md) · [Repeat requests](results/2026Q4/addressrates_recheck.csv) · [Named address queries](results/2026Q4/addressrates_test_inputs.csv)

To reproduce a dated case extract, use the commands in [extract_sst_rows.py](scripts/extract_sst_rows.py). The sample-library driver takes DOR downloads and the 31 invoice strings. Its build script requires Mono and a matching current quarter. [Sample library](docs/dor-sample-library.md) · [Build script](scripts/wsrl/run_wsrl.sh)

Code is under the [MIT license](LICENSE). The publishers are the sources for the underlying data.
