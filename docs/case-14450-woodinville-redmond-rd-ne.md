# Case study: 14450 Woodinville-Redmond Rd NE, Woodinville 98072

This is a multi-tenant winery building in Woodinville's Hollywood district, and the case that started this work.

## The three answers

- **DOR's Tax Rate Lookup:** 1735 Woodinville, 10.4%.
- **QuickBooks Online:** 4000 King County unincorporated, 8.9%, for the address with no suite and for the tenant's actual suite, "Ste 101-A".
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

**When the 8.9% started.** If the single-address record wins over the block record, 14450 with no suite came out 1735 every quarter until 2026-03-31:
- From 2022-04 to 2023-12 the block was already 4000, but the no-suite 14450 record still existed and won.
- The 8.9% starts on **2026-04-01**. By then the no-suite 14450 record was gone (since 2025-07-01) and the block switched to 4000 again.

All rows are in `results/2026Q4/case_14450_sst_rows.csv` (raw SST rows, line numbers included). They were extracted with `scripts/extract_sst_rows.py`.

## How each method resolves the address

| Input | DOR lookup | SST strict | SST with assumptions (= QuickBooks) | DOR sample library |
|---|---|---|---|---|
| no suite (any ZIP+4) | 1735 | 4000 | 4000 | 1735 (file order) |
| Ste 101, 108, 109 | 1735 | 1735 | 1735 | 1735 |
| Ste 101-A, 101A, 105, 9999, no ZIP+4 | 1735 | 3120 (ZIP5 default) | 4000 | 1735 |
| Ste 101-A with 98072-9051 (test T33; not entered in QuickBooks) | 1735 | 1735 (via ZIP+4 record) | 4000 | 1735 |
| "Redmond-Woodinville Rd NE", 98072 | 1735 | 3120 (ZIP5 default) | 3120 | 4200 (lowest rate in ZIP) |

## Observations, not conclusions

- **The lookup ignores the suite.** DOR's lookup returned 1735, ResultCode 4 ("corrected"), for every suite, ZIP+4 and street-name spelling we tried, including a nonexistent "Ste 9999".
- **It reports a different ZIP.** The lookup's standardized address comes back with `zip="98052"`, while USPS and both DOR files use 98072.
- **The block may straddle the city limit.** On the same block face, 14412 returned 4000 and 14498 returned 1735. That is consistent with the city limit crossing the 14412-14498 block face, but two lookups don't show where it crosses.

## What would fix it

- **The block record:** split 14412-14498 E, or re-add a 14450 record without a secondary coded 1735.
- **The tenant's suite:** add STE 101-A, or a single STE range covering the building.
