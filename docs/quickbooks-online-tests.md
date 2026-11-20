# QuickBooks Online: what it returned, compared with the rules

QuickBooks Online's Automated Sales Tax was tested on 2026-11-20 with 31 ship-to addresses:
- **How:** each address was typed on an unsaved test invoice, and the result was read from "See the math".
- **USPS:** each input was also run through the USPS ZIP Code lookup to get the standardized form the rules call for (see [sst-rules.md](sst-rules.md)).
- **Full table:** `results/2026Q4/test_inputs_comparison.csv` lists every input with DOR's lookup, QuickBooks, three SST replays and DOR's sample library.

## How often each method agreed (31 inputs)

| Method | Same as QuickBooks | Same as DOR's lookup | Ambiguous |
|---|---|---|---|
| SST rules, ZIP+4 left out of the address match | 19 | 9 | 8 |
| SST rules, standardized ZIP+4 in the address match | 14 | 22 | 0 |
| SST file + two assumptions that are **not** in the rules: an unlisted suite is dropped, and a single address beats a block | **31** | 13 | 0 |
| QuickBooks itself | – | 13 | – |

QuickBooks' answers match the SST file plus those two assumptions. That shows its answers are *consistent* with them; it doesn't show what QuickBooks does internally.

## Where QuickBooks departs from the rules

**Ste 101-A (T07, T08) and other unlisted suites (T09, T12).**
- USPS standardizes "Ste 101-A" to 98072-9051. USPS echoes any suite it can't confirm with the building's default ZIP+4; it did the same for "Ste 9999".
- The SST file lists no STE 101-A, so the address match fails under either permitted reading.
- The rules then fall back to the ZIP+4 record 98072-9051, which is 1735 Woodinville, **10.4%**.
- QuickBooks charged **8.9%**. The only way to get that is to drop the suite and match the block record 14412–14498, and the rules don't allow that.

**14450 with no suite (T02–T05, T13).** The rules allow two answers here:
- Leaving the ZIP+4 out matches the block record: 8.9%.
- Keeping USPS's ZIP+4 (98072-9051) skips the block record, whose ZIP+4 is 6978, and falls back to the ZIP+4 record: 10.4%.

QuickBooks chose the first. The state's data is at fault for allowing two answers: TG p. 25 says records should give the same result however they are queried.

## Where QuickBooks' answer matches a reading the rules allow

| Inputs | QuickBooks | DOR lookup | Explanation |
|---|---|---|---|
| 21806 103rd Avenue Ct E (T20, T21); 4212 5th Ave NW (T27, T28) | block code (8.2%; 8.4%) | suite code (9.6%; 10.0%) | Same pattern as 14450 with no suite. Leaving the ZIP+4 out gives QuickBooks' answer; including USPS's building ZIP+4 gives DOR's |
| 14498 Woodinville Redmond Rd NE (T18); 1450 S Bluff Dr (T24) | 4000; 3200 | 1735; 3213 | No suites. USPS returns no ZIP+4. The only matching SST record is the block record, so every reading agrees with QuickBooks; DOR's lookup follows DOR's own address file instead (a C7 row) |
| Misspelled "Redmond-Woodinville Rd NE" (T14–T16) | ZIP5 record: 3120 (10.5%) or 1716 | 1735 | USPS can't standardize the street name, so the address and ZIP+4 lookups both fail and the rules fall back to ZIP5. DOR's lookup corrects the name instead |
| Overlapping no-suite records (T17, T19, T22, T23, T26, T29, T30, T31) | single-address record | single-address record (8 of 8) | The rules give no tie-break (strict result: ambiguous). With USPS's ZIP+4 in the match, the block record wins in 4 of the 8, because the single-address record carries a ZIP+4 that USPS doesn't assign to that address |

## Practical notes

- **Which suites work:** for 14450, Ste 101, 108 and 109 were entered in QuickBooks and each gave 1735. By the replay, 110, 111 and 101B would too. Ste 101-A gives 8.9%.
- **The question for a QuickBooks trace:** what QuickBooks standardized "Ste 101-A" to, and which record it then selected.
- **A misspelled street is expensive:** it drops to the ZIP5 record. In 98072 that record is 3120 (10.5%), the highest rate in the ZIP, even though Washington's certificate says ZIP5 records carry the lowest.
