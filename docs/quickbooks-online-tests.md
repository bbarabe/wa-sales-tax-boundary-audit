# QuickBooks Online: what it returned, and why

QuickBooks Online's Automated Sales Tax was tested on 2026-11-20 with 31 ship-to addresses. Each was typed on an unsaved test invoice; tabbing out triggers the recalculation, and the result was read from "See the math". The full table is `results/2026Q4/test_inputs_comparison.csv`, with each input next to DOR's lookup, the SST replays and DOR's sample library.

## Result

**On all 31 inputs, QuickBooks returned the same jurisdiction as an SST boundary-file replay that adds two assumptions** (`scripts/sst_lookup.py`, assumptions mode):

1. **Unlisted suites are dropped.** If the suite isn't listed for the building, the suite is ignored and the address record with no suite is used.
2. **Single addresses beat blocks.** Where a single-address record and a block record overlap, the single-address record wins.

This doesn't show which data QuickBooks uses internally. It shows that its answers are consistent with the SST file plus those two rules.

QuickBooks and DOR's lookup disagreed on 18 of the 31 inputs. In every one of those cases, the disagreement traces to the published records or to the SST hierarchy, not to a calculation error:

| Inputs | QuickBooks | DOR lookup | Why |
|---|---|---|---|
| 14450 Woodinville Redmond Rd NE, no suite or an unlisted suite (T02–T05, T07–T09, T12, T13) | 4000, 8.9% | 1735, 10.4% | The SST block record 14412–14498 is 4000. No 14450 record without a suite has existed since 2025-07-01. Ste 101-A isn't listed. See [the case study](case-14450-woodinville-redmond-rd-ne.md) |
| 14498 Woodinville Redmond Rd NE (T18) | 4000 | 1735 | Same block record; this address has no suite records in either file |
| 1450 S Bluff Dr, Spokane Valley (T24) | 3200 Spokane County, 8.1% | 3213 Spokane Valley, 9.0% | No suites. The SST file codes 1400–1599 as 3200, while DOR's address file codes 1401–1599 odd as 3213 (a C7 row) |
| 21806 103rd Avenue Ct E, Graham (T20, T21) | 4100, 8.2% | 2700, 9.6% | Suites 101–201 are coded 2700; the address with no suite falls in a 4100 block record (a C4a row) |
| 4212 5th Ave NW, Olympia (T27, T28) | 3400, 8.4% | 3403, 10.0% | Units 101–104 are coded 3403; the address with no suite falls in a 3400 block record (a C4a row) |
| Street name misspelled as "Redmond-Woodinville Rd NE" (T14–T16) | ZIP5 record: 3120 (10.5%) in 98072, 1716 in 98052 | 1735 | No address match, so the lookup drops to the ZIP5 record. DOR's lookup corrects the street name instead |

## Practical notes

- **Rows 2 and 3 are the counter-examples for addresses with no suite.** QuickBooks and DOR disagree there, and no suite is involved in either file: the SST file and DOR's own address file simply code the range differently. The full list of such ranges is `results/2026Q4/C7_sst_vs_dor_address_file.csv`.
- **A suite only helps when it is a listed one.** For 14450, entering Ste 101, 108, 109, 110, 111 or 101B gives 1735. Ste 101-A (the real tenant suite in this case) gives 4000, because the suite is dropped.
- **A misspelled street is costly.** The ZIP5 record for 98072 is 3120 (Bothell/Snohomish, 10.5%), which is the highest rate found in that ZIP.
