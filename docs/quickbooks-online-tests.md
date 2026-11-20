# QuickBooks Online invoice checks

On November 20, 2026 the 31 ship-to strings T01–T31 were re-entered on the existing test invoice for a $100 taxable workshop. The invoice date was November 5, 2026. Customer, item, amount, ship-from and automatic calculation were held fixed. For each input the reviewer left the ship-to field, opened **See the math**, and read the shipping destination, agency labels and combined rate. The original ship-to address was restored and the invoice reloaded without saving the test changes.

All 31 displayed jurisdiction labels and rates reproduced the earlier worksheet. The panel names agencies; the numeric DOR location codes in the comparison are a crosswalk. There are repeated inputs for a single building. T32 and T33 are additional replay and DOR checks only. [Repeated invoice observations](../results/2026Q4/quickbooks_recheck.csv) · [Per-input results](../results/2026Q4/test_inputs_comparison.csv) · [Intuit's description of automatic sales tax](https://quickbooks.intuit.com/learn-support/en-us/help-article/sales-taxes/learn-quickbooks-online-calculates-sales-tax/L8VWCLobK_US_en_US)

| Jurisdiction-code comparison across 31 inputs | Matches QuickBooks | Matches DOR live | Ambiguous |
|---|---:|---:|---:|
| Retain a supplied suite, omit extension during street match | 19 | 9 | 8 |
| Retain suite and selected postal extension during street match | 14 | 22 | 0 |
| Omit extension, try a blank-suite row if necessary, prefer a single-number row if codes conflict | 31 | 13 | 0 |
| QuickBooks itself | 31 | 13 | 0 |
| DOR sample library, full address engine | 10 | 21 | 0 |

At **14450 Woodinville Redmond Rd NE**, blank suite, STE 101-A, STE 101A, STE 105 and STE 9999 each displayed Washington State 6.5% plus King County Uninc Non-Rta District 2.4%, totaling **8.90%**. STE 101, 108 and 109 each displayed Washington State 6.5% plus Woodinville City 3.9%, totaling **10.40%**. These were invoice previews. No test charge was made.

STE 105 is the cleaner postal control. USPS displayed one entry with +9051 for that suite, but the SST street records omit 105. With that extension, both exact-field replays fall through to the 1735 ZIP+4 row. STE 101-A returned 13 postal candidates, including an echoed unit at +9051. Its replay result depends on the selected candidate. Intuit support suggested entering STE 101 and said it had asked Washington to correct its records. That correspondence did not identify a source file, standardizer or selected row.

The reversed street name used by the venue's website gave Bothell in Snohomish County at 10.50% in T14/T15. T16, entered with Redmond 98052, gave Kirkland District at 10.40%. T17, T19, T30 and T31 selected the block in the extension-included replay and the single-number code in QuickBooks. T18 and T24 had a street match with no postal extension. Their DOR and SST codes differed. Each is a test result on the supplied inputs.

The 31/31 fit is an explanation to test with Intuit. It establishes neither the vendor's algorithm nor its legal obligations for this venue. A trace should identify the normalized street and secondary, confidence or fallback status, data vintage, record level and jurisdiction selected. [Winery evidence](case-14450-woodinville-redmond-rd-ne.md)
