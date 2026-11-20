# Case study: 14450 Woodinville-Redmond Rd NE, Woodinville 98072

This is a multi-tenant winery building in Woodinville's Hollywood district, and the case that started this work.

## The three answers

- **DOR's Tax Rate Lookup:** 1735 Woodinville, 10.4%.
- **QuickBooks Online:** 4000 King County unincorporated, 8.9%, both for the address with no suite and for the tenant's actual suite, "Ste 101-A". For Ste 101-A, that is not what the rules give (see below).
- **QuickBooks support:** said Washington's records for the building are tied to individual suites, and that adding a suite fixes it.

## SST boundary file records (effective 2026-11-20)

| House range | Side | Secondary | ZIP+4 | Code | Effective |
|---|---|---|---|---|---|
| 14450-14450 | E | STE 108-111 (B) | 98072-4547 | 01735 | since 2021-01-01 |
| 14450-14450 | E | STE 101B | 98072-7100 | 01735 | since 2025-01-01 |
| 14450-14450 | E | STE 101 | 98072-9051 | 01735 | since 2025-07-01 |
| **14412-14498** | E | (none) | 98072-6978 | **L4000** | since 2026-04-01 |

- **ZIP+4 records:** 98072-9051 → 01735 (since 2016-10-01); 98072-6978 → L4000 (since 2026-04-01).
- **The block record has changed code three times:** 1735 (2021-01-01 to 2022-03-31), 4000 (2022-04-01 to 2023-12-31), 1735 (2024-01-01 to 2026-03-31), 4000 (2026-04-01 on).
- **The no-suite 14450 record was dropped:** until 2025-06-30 there was a 14450 record without a secondary on 98072-9051, coded 1735. From 2025-07-01 that ZIP+4 carries STE 101 only.

**When the 8.9% started.** Take the reading where the ZIP+4 is left out of the match and the single-address record wins over the block record. Under it, 14450 with no suite came out 1735 every quarter until 2026-03-31:
- From 2022-04 to 2023-12 the block was already 4000, but the no-suite 14450 record still existed and won.
- The 8.9% starts on **2026-04-01**. By then the no-suite 14450 record was gone (since 2025-07-01) and the block switched to 4000 again.

All rows are in `results/2026Q4/case_14450_sst_rows.csv` (raw SST rows, line numbers included). They were extracted with `scripts/extract_sst_rows.py`.

## What USPS has for the building

These are USPS ZIP Code lookup results from 2026-11-20. USPS standardization is the first step the rules require (SSUTA §309.A.2(a)).

| USPS record | ZIP+4 | In the SST file? |
|---|---|---|
| 14450, no suite (building default) | 98072-9051 | No. A no-suite record existed until 2025-06-30 |
| STE 101 | 98072-9051 | Yes, 1735 |
| STE 102–107 | 98072-9051 | **No** |
| STE 101B | 98072-7100 | Yes, 1735 |
| STE 108–111 | 98072-4547 | Yes, 1735 |
| Street range 14412–14498 even (street default) | 98072-6978 | Yes, the block record, 4000 |

- **Unconfirmed suites:** "Ste 101-A" and "Ste 9999" both come back echoed with the building default 98072-9051, among 13 candidates. USPS does not confirm either suite.
- **"Ste 105"** is a single exact match inside STE 102–107.

## How each method resolves the address

| Input (USPS-standardized ZIP+4) | DOR lookup | Rules, ZIP+4 left out | Rules, ZIP+4 in the match | Assumptions (= QuickBooks) | DOR sample library |
|---|---|---|---|---|---|
| no suite (9051) | 1735 | 4000 (block record) | 1735 (ZIP+4 record 9051) | 4000 | 1735 (file order) |
| Ste 101 (9051); Ste 108, 109 (4547) | 1735 | 1735 | 1735 | 1735 | 1735 |
| Ste 101-A, 101A, 105, 9999 (9051) | 1735 | 1735 (ZIP+4 record) | 1735 (ZIP+4 record) | 4000 | 1735 |
| "Redmond-Woodinville Rd NE" (USPS: not found) | 1735 | 3120 (ZIP5 record) | 3120 (ZIP5 record) | 3120 | 4200 (lowest rate in ZIP) |

**What the table shows:**
- **Ste 101-A:** every reading that follows the rules gives 10.4%. QuickBooks' 8.9% requires dropping the suite, which the rules don't allow.
- **No suite:** the rules allow both 8.9% and 10.4%. That is a data defect. TG p. 25 says a query should give the same result with or without the ZIP+4, and that a range covers only addresses sharing its ZIP+4. The block record 14412–14498 carries 6978, but 14450's ZIP+4 is 9051.
- **The supplied ZIP+4 doesn't matter.** CASS/USPS standardization replaces a mistyped ZIP+4, so inputs typed with 4547 or 6978 standardize to 9051. Before standardization, the replay of the as-typed inputs is in `results/2026Q4/sst_lookup_test_inputs.csv`.

## Observations, not conclusions

- **The lookup ignores the suite.** DOR's lookup returned 1735, ResultCode 4 ("corrected"), for every suite, ZIP+4 and street-name spelling we tried, including a nonexistent "Ste 9999".
- **It reports a different ZIP.** The lookup's standardized address comes back with `zip="98052"`, while USPS and both DOR files use 98072.
- **The block may straddle the city limit.** On the same block face, 14412 returned 4000 and 14498 returned 1735. That is consistent with the city limit crossing the 14412-14498 block face, but two lookups don't show where it crosses.

## What would fix it

- **The building:** re-add a 14450 record with no suite on 98072-9051, coded 1735. Alternatively, take 14450 out of the 14412–14498 block record, whose ZIP+4 (6978) isn't the building's.
- **The suites:** add USPS's STE 102–107 range. If 101-A is a real suite, add it too, or one STE range covering the building.
