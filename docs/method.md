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

The SST Technology Guide (Oct 2022), chapter 5:

- **Address first.** "Users are required to use the address data when it is provided by the state. If the query does not find the address, the user should use the 9-digit zip code (zip +4) data. If no address or 9-digit zip code record is found, the query would fall back to the 5-digit zip code."
- **Exact match.** "Each component of the address must be an exact match to that component in the table (may exclude the zip extension from the query)."
- **Uniqueness.** "Each row on the database must be unique for the query to return one record ... An address, 9-digit or 5-digit zip code can only be valid for one row of the database."
- **9-digit rows.** These carry the lowest rates for that 9-digit ZIP.

The guide leaves two cases open:
1. A suite that is not listed for the building.
2. Two overlapping records, which shouldn't exist.

`scripts/sst_lookup.py` therefore replays each input two ways:

- **strict**: nothing added to the guide.
  - An unlisted suite means no address match, so the lookup falls back to the ZIP+4 record, then the ZIP5 record.
  - When two records match, the result is reported as ambiguous.
- **assumptions**: two assumptions the guide doesn't state.
  - An unlisted suite is dropped and the record without a suite is used.
  - Where two no-suite records overlap, the single-address record wins.

  QuickBooks Online behaved like this mode on all 31 test inputs.

## Conflict scans (`scripts/scan_sst_conflicts.py`)

| ID | Check |
|---|---|
| C1 | Two no-suite address records cover the same house number (same ZIP, street, side) with different codes |
| C2 | Two ZIP+4 records cover the same ZIP+4 with different codes |
| C3 | Two ZIP5 records cover the same ZIP with different codes |
| C4 | A building whose listed suites carry a different code than a no-suite record covering its house number. The output is split afterwards (`summarize_api_checks.py`): **C4a**, no no-suite record carries the suites' code, so the result depends on the suite under any reading; **C4b**, the no-suite records overlap (a C1 situation) and the narrowest one agrees with the suites |
| C5 | Two suite records for one building overlap with different codes |
| C6 | A ZIP+4 with no `4` record, or whose `4` record code isn't used by any address on it, or isn't the lowest rate |
| C7 | A range in DOR's address download whose code differs from the SST records with the same ZIP, ZIP+4, street and overlapping numbers |
| C8 | Where each ZIP5 record's rate sits among the rates found in that ZIP (lowest, middle, highest) |

**House numbers are candidates, not verified addresses.** Counts give the numbers that fall inside conflicting ranges. Only a geocoded address list or one live lookup per number can tell which of them actually exist.

## Live checks against AddressRates (`scripts/check_addressrates.py`)

| Check | Coverage | What was queried |
|---|---|---|
| C1 | every row | first house number of each segment |
| C2 | every row | ZIP+4 alone |
| C4 | every row | building's house number with no suite |
| C7 | random sample of 200 (seed 7) | first house number of the range |

The DOR address-file scan (`results/2026Q4/dor_address_file_conflicts.csv`) was checked in full.

## Tested in QuickBooks Online

31 inputs typed as the ship-to address of an unsaved test invoice, tabbing out to recalculate. The jurisdiction and rate were read from the invoice's "See the math" panel. Ship-from was held constant. A control input (19510 144th Ave NE) confirmed that ship-to drives the calculation.

## DOR address-file scan (`scripts/scan_dor_address_file.py`)

This finds house numbers in DOR's own download that match more than one row with different codes (same ZIP, street, side). `dor_address_file_conflicts_api.csv` has the same 494 segments, with DOR's live answer for each, and records whether the most specific row agrees with it.
