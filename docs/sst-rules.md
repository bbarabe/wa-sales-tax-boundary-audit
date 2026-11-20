# What the rules actually say

The test results in this repo depend on how strictly the Streamlined Sales Tax (SST) rules are read, so this page lists the governing texts and quotes them directly. Each statement below names its source and page. Quotes are kept short; read the originals for context.

## Sources

| Short name | Document |
|---|---|
| **SSUTA** | Streamlined Sales and Use Tax Agreement, as amended through 2024-12-20 (streamlinedsalestax.org). §305 and §309 were amended on 2024-07-18 ("sourcing without complete address"). |
| **TG** | SST Technology Guide SST160.9, 2022-10-06, chapter 5 "Rates and Boundary Databases" |
| **WA CoC** | Washington Certificate of Compliance, version 2026.0, published 2026-08-17 (sst.streamlinedsalestax.org/coc) |

## 1. The lookup procedure

**Standardize first** (SSUTA §309.A.2(a), p. 22). The address is standardized with one of:
- the USPS lookup;
- CASS-certified software;
- other Board-approved software.

**Then match in this order** (SSUTA §309.A.2(b)–(d), p. 23):
1. Match the standardized result to the **address-based records**.
2. If that fails, use the standardized result to determine the **nine-digit ZIP**.
3. If that fails, use the **five-digit ZIP** records.

**Washington requires the address records** (WA CoC):
- Item 305115 answers "Yes" to requiring sellers and certified service providers (CSPs) to use the address-based records to get liability relief.
- Items 305116 and 305117 answer "Yes" to the ZIP+4 and ZIP5 fallbacks.
- Item 306010 cites RCW 82.32.430 for relief when a seller relies on state data.

## 2. What counts as an address match

- **Exact match, every field** (TG p. 39): "To be a match at the 'A' level, the address must match all address fields exactly as in the database."
- **One stated exception** (TG p. 39): "an address level query may exclude the zip extension field." TG p. 25 says the same: "An address search may be performed using the address with only the 5-digit zip code."
- **The suite is one of the address fields.** TG p. 29 lists Address Secondary Abbreviation, Low, High and Odd/Even as fields of the address record ("If highrise or firm").
- **No exception for an unmatched suite.**
  - Neither document allows dropping a supplied suite that doesn't match.
  - Neither treats a record with a blank suite as matching an address that has one.

So both of these queries follow the rules:
- the standardized address with its ZIP+4 in the match;
- the standardized address without its ZIP+4 in the match.

Dropping the suite is not in the rules.

## 3. One record per address

- **Uniqueness** (TG p. 25): "An address, 9-digit or 5-digit zip code can only be valid for one row of the database." The only exception is the same row repeated across effective dates.
- **ZIP+4 records** (TG p. 26): "A 9-digit zip code may not be in more than one '4' record."
- **ZIP5 records** (TG p. 26): "A zip code may not be in more than one 'Z' record."
- **No tie-break rule.** Neither document says what a seller should do when two records match: not first row, not narrowest range, not lowest rate. The rule is addressed to the state: two records shouldn't match.
- **With or without the ZIP+4 should give the same answer** (TG p. 25):
  - Address records leave the ZIP-range fields blank. TG says this "will allow vendors to get the same FIPS results regardless of how they query the database."
  - "An address range is only for addresses that have same Street Name, City Name and Zip Code, Zip Extension."

## 4. Which rate a ZIP record carries

| Record | Rule | Washington's choice |
|---|---|---|
| ZIP+4 (`4`) | SSUTA §305.A.6(a), p. 18: the state "must assign the lowest combined tax rate imposed in the nine-digit zip code area." TG p. 26 also says lowest. | Lowest (WA CoC 305080, 308042) |
| ZIP5 (`Z`) | SSUTA §305.A.6(b)i, p. 18, since the 2024 amendment: the state "may assign the highest, lowest or blended rate." TG p. 26 (2022, before the amendment) says lowest. | **Lowest** (WA CoC 305081, 308041: "Lowest rate") |

The lowest-rate rules are instructions to the **state** about how to build the file. They don't tell a seller to pick the cheaper of two conflicting records.

## What this means for the findings in this repo

| Finding | Rule it breaks |
|---|---|
| 3058 Camp 2 Rd: two active `4` records for 98284-9508 (C2, 15 ZIP+4s) | TG p. 26, which has no exception. This is the clearest violation in the file. |
| Overlapping address records (C1, 692 segments) | TG p. 25, one row per address. 686 of the 692 can be separated by including the ZIP+4, a query the rules allow. |
| Buildings coded differently from their block (C4a, 101) | TG p. 25: the two permitted queries give different answers, and the block record's ZIP+4 isn't the building's ZIP+4. |
| ZIP5 records that are not the lowest rate in the ZIP (C8) | Washington's own certificate (305081, 308041). The SSUTA has allowed highest or blended since 2024, but Washington declared lowest. |
| ZIP+4 records that are not the lowest rate of their addresses (C6, 4) | SSUTA §305.A.6(a); TG p. 26; WA CoC 305080 |
| QuickBooks charging 8.9% for "Ste 101-A" | Not a data finding. Every reading that follows the rules gives 10.4% for that input; 8.9% requires dropping the suite (see [the QuickBooks tests](quickbooks-online-tests.md)). |

**What this page does not cover:** the SST rate file, or how its jurisdiction-type codes join to the boundary file. This repo maps boundary records to DOR location codes its own way: the `L####` special-district code if present, otherwise the last four digits of the composite SER code. That is our convention, not an SST requirement.
