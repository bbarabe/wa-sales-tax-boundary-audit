# Review: DOR's sample library (WaRateFileLookup 1.0.5)

DOR publishes C# source code (version 1.0.5, 2011-08-05) as "a starting point" for lookups against its download files. We compiled it unmodified on Mono 6.8, leaving out `FileMaintenance.cs` and `UnitTest/`, and ran it with `RateLookupEngine.STANDARDIZER` against the Q4 2026 files. See `scripts/wsrl/`.

## Findings

- **The ZIP+4 is never used to match an address.** `AddressNormalIndex.Locate` uses the ZIP only to choose the `ZipStreet`. The plus4 never reaches `StreetName.Locate`, so a known ZIP+4 can't break a tie between rows.
- **Ties resolve by file order.**
  - `StreetComponent.Match` gives no credit for a house number being inside a range. Outside a range it subtracts 0.1 plus a small distance term.
  - It has no preference for a narrower range.
  - `StreetName.Locate` keeps the first highest score (strict `>`), so overlapping rows resolve by file order.
  - `State_26Q4.txt` is sorted by ZIP, then PLUS4. The answer therefore depends on how ZIP+4s happen to be numbered: 14450 gets +4547 first (1735), but 18030 162nd Pl SE gets +9180 first (1700).
- **The odd/even check is one-sided.** An odd number on an even-side row gets −0.0001; an even number on an odd-side row gets nothing.
- **The Metaphone fallback matches the wrong street.**
  - "Woodinville-Redmond Rd NE" matched WOODINVILLE SNOHOMISH RD NE 17500-17598.
  - "Redmond-Woodinville Rd NE" in 98052 matched REDMOND WAY 14400-14498.
- **The ZIP5 fallback takes the lowest rate in the ZIP** (98072 → 4200, 7.9%). That matches what Washington declares in its Certificate of Compliance (items 305081 and 308041: "Lowest rate"). The SST file's ZIP5 record for 98072 is L3120 (10.5%), the *highest* rate in that ZIP, so it is the SST record that departs from the declared policy, not the library.
- **One mapping is hard-coded.** `FileRateLookup.FindRate` swaps Nooksack and Everson (3703/3706).
- **There is no secondary (suite) support, and no address standardization.** The SST procedure requires standardizing through USPS/CASS before matching (SSUTA §309.A.2(a)). The library relies on its own Metaphone fuzzy match instead.
- **Result:** the library matches DOR's live lookup on 21 of 31 test inputs (`results/2026Q4/test_inputs_comparison.csv`).
