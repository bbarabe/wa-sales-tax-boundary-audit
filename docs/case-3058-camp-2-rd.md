# Case study: 3058 Camp 2 Rd, Sedro-Woolley 98284-9508

A reproducible defect in the SST boundary file. One address has two records on the same ZIP+4, in two different counties, and the ZIP+4 itself appears twice.

| SST line | Type | Range / ZIP+4 | Code | County FIPS | Effective |
|---|---|---|---|---|---|
| 1546893 | A | 3000-3058 B, 98284-9508 | L2929 Skagit PTBA, 8.7% | 057 | 2024-01-01 on |
| 1547127 | A | 3058-3058 B, 98284-9508 | L3737 Whatcom PTBA, 8.9% | 073 | 2021-01-01 on |
| 307014 | 4 | 98284-9508 | L2929 | 057 | 2026-10-01 on |
| 307015 | 4 | 98284-9508 | L3737 | 073 | 2026-10-01 on |

- **Other sources disagree too:**
  - DOR's live lookup returns 3737 (ResultCode 2) for "3058 Camp 2 Rd, 98284" but 2929 (ResultCode 1) for 98284-9508 on its own.
  - DOR's address download (`State_26Q4.txt`) codes both 3000-3058 and 3058 as 3737.
- **Not a one-off:** duplicate ZIP+4 pairs for 98284-9508 appear in most quarters back to 2022.
- **No input can resolve it:** both address records and both ZIP+4 records share the same ZIP+4, so no suite and no ZIP+4 settles which one applies.

All rows: `results/2026Q4/case_3058_camp_2_rd_sst_rows.csv`. The same pattern exists for 14 other ZIP+4s: `results/2026Q4/C2_zip4_duplicates.csv`.
