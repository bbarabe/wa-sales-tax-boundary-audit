# Method

All results are for records effective **2026-11-20** (Q4 2026). Every scan is reproducible from public files with the scripts in `scripts/` (Python 3 standard library only, plus Mono for the DOR sample library).

## Data sources

| Source | What it is | Suite/unit (secondary) data |
|---|---|---|
| **SST boundary file** `WAB2026Q4AUG27.csv` | Washington's Streamlined Sales Tax boundary file, published on streamlinedsalestax.org. Record types: `A` (address), `4` (ZIP+4), `Z` (ZIP5). This is the file certified tax software is built on. | **Yes**: 181,879 of 887,013 effective address records carry APT/STE/UNIT ranges |
| **DOR address file** `State_26Q4.txt` | DOR's own download: house-number range, side, street, ZIP, ZIP+4, location code | **No** |
| **DOR ZIP+4 files** `Zip4RatesQ42026-Short.txt` / `-Long.txt` | ZIP+4 → location code | n/a |
| **DOR wireless (MTSA) file** `StateWRLS_26Q4.txt` | National MTSA format | Fields exist, but DOR's spec lists them as "Populated in DOR's database? **no**" |
| **DOR AddressRates** | DOR's live lookup ("direct access to the Washington Department of Revenue's address based rate lookup technology platform"), `https://webgis.dor.wa.gov/webapi/AddressRates.aspx` | Accepts a suite in the street line; every suite variant we tried returned the same code |
| **DOR sample library** WaRateFileLookup 1.0.5 (2011) | C# reference code DOR publishes for its download files | No |

## SST matching rules

The rules are quoted with page references in [sst-rules.md](sst-rules.md). In short:
1. Standardize the address (USPS, CASS or Board-approved software).
2. Match it to the address records.
3. If that fails, use the standardized ZIP+4 against the ZIP+4 records.
4. If that fails, use the ZIP5 record.

Every address field must match exactly, the suite included. The only stated exception is that the ZIP extension may be left out of the address match. The rules give no tie-break, because an address may be valid for only one row.

`scripts/sst_lookup.py` replays each input three ways:
- **strict, ZIP+4 left out**: permitted by the rules.
- **strict, ZIP+4 in the match**: also permitted. It gives the same result as the first when the input has no ZIP+4.
- **assumptions**: not in the rules. An unlisted suite is dropped and the no-suite record used; where no-suite records overlap, the single-address record wins; the ZIP+4 is left out. QuickBooks Online matched this mode on all 31 inputs.

In both strict modes, an unlisted suite gets no address match, and two matching records with different codes are reported as ambiguous.

**Standardized inputs.** `tests/test_inputs_standardized.tsv` holds the 33 test addresses with the ZIP+4 the USPS ZIP Code lookup returned on 2026-11-20, with a note per address. `tests/test_inputs.tsv` holds them as typed into QuickBooks.

**Location codes.** Boundary records are mapped to DOR location codes this way: the `L####` special-district code if present, otherwise the last four digits of the composite SER code. That is this repo's convention, not an SST requirement.

## Conflict scans (`scripts/scan_sst_conflicts.py`)

| ID | Check |
|---|---|
| C1 | Two no-suite address records cover the same house number (same ZIP, street, side) with different codes |
| C2 | Two ZIP+4 records cover the same ZIP+4 with different codes |
| C3 | Two ZIP5 records cover the same ZIP with different codes |
| C4 | A building whose listed suites carry a different code than a no-suite record covering its house number. The output is split afterwards (`summarize_api_checks.py`): **C4a**, no no-suite record carries the suites' code, so the result depends on the suite under any reading; **C4b**, the no-suite records overlap (a C1 situation) and the narrowest one agrees with the suites |
| C5 | Two suite records for one building overlap with different codes |
| C6 | A ZIP+4 with no `4` record, or whose `4` record code isn't used by any address on it, or isn't the lowest rate (SSUTA §305.A.6(a); TG p. 26; WA certificate 305080) |
| C7 | A range in DOR's address download whose code differs from the SST records with the same ZIP, ZIP+4, street and overlapping numbers |
| C8 | Where each ZIP5 record's rate sits among the rates found in that ZIP (lowest, middle, highest). Washington's certificate declares "Lowest rate" for ZIP5 (items 305081, 308041), although SSUTA §305.A.6(b) has allowed highest or blended since 2024 |

**House numbers are candidates, not verified addresses.** Counts give the numbers that fall inside conflicting ranges. Only a geocoded address list or one live lookup per number can tell which of them actually exist.

## Live checks against AddressRates (`scripts/check_addressrates.py`)

| Check | Coverage | What was queried |
|---|---|---|
| C1 | every row | first house number of each segment |
| C2 | every row | ZIP+4 alone |
| C4 | every row | building's house number with no suite |
| C7 | random sample of 200 (seed 7) | first house number of the range |

The DOR address-file scan (`results/2026Q4/dor_address_file_conflicts.csv`) was checked in full.

## Would the ZIP+4 separate the conflicts? (`scripts/check_zip4_resolution.py`)

This check matters because the rules allow the standardized ZIP+4 in the address match:
- **C1:** do the overlapping records carry different ZIP+4s? They do in 686 of 692.
- **C4a:** are the suite ZIP+4s missing from the no-suite records, and do their ZIP+4 records carry the suites' code? Both hold for all 101 buildings.

The file doesn't contain the ZIP+4 USPS assigns to each house number, so the check can't say which record would win. Output: `results/2026Q4/zip4_resolution.md`.

## Tested in QuickBooks Online

31 inputs typed as the ship-to address of an unsaved test invoice, tabbing out to recalculate. The jurisdiction and rate were read from the invoice's "See the math" panel. Ship-from was held constant. A control input (19510 144th Ave NE) confirmed that ship-to drives the calculation.

## DOR address-file scan (`scripts/scan_dor_address_file.py`)

This finds house numbers in DOR's own download that match more than one row with different codes (same ZIP, street, side). `dor_address_file_conflicts_api.csv` has the same 494 segments, with DOR's live answer for each, and records whether the most specific row agrees with it.
