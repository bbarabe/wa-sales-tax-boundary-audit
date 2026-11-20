# 14450 Woodinville Redmond Rd NE, Woodinville

**Three independent observations matter for this venue.** DOR's street lookup returned 1735 Woodinville, 10.4%. The King County building point lies inside DOR's Q4 polygon for 1735. QuickBooks displayed 8.9% for the ship-to string containing STE 101-A, and 10.4% for STE 101. The venue publishes the reverse street-name order, “Redmond-Woodinville,” without a unit. STE 101-A is the unit reported by the business. [Venue listing](https://evergreenfamilywines.com/tasting-rooms/) · [QuickBooks test results](quickbooks-online-tests.md)

## Physical location

King County's address layer returned a single building point for 14450 WOODINVILLE REDMOND RD NE, site ID `{061D163D-D103-47A9-B78B-BCAE9F444D02}`, latitude 47.73229011, longitude -122.14063994. The county gives city Woodinville, ZIP 98072, extension 4547 and a blank unit. Requesting the point in the Q4 shapefile's native projection gives (1236641.89195337, 879095.59835768) US survey feet. The point is inside exactly one location-code polygon, 1735, about 61 feet from its boundary. This supports 1735 at the county's building point. It does not locate the tenant's floor space or establish relief on a return. [County address layer](https://gismaps.kingcounty.gov/arcgis/rest/services/Address/KingCo_AddressPoints/MapServer/0) · [DOR Q4 polygons](https://dor.wa.gov/sites/default/files/2026-08/LOCCODE_PUBLIC_26Q4.zip)

## Active SST street rows

| Street numbers (even) | Secondary | ZIP extension | Mapped code | Effective from |
|---|---|---:|---:|---|
| 14450 | STE 108–111 | 4547 | 1735 | Jan 1, 2021 |
| 14450 | STE 101B | 7100 | 1735 | Jan 1, 2025 |
| 14450 | STE 101 | 9051 | 1735 | July 1, 2025 |
| 14412–14498 | blank | 6978 | 4000 | April 1, 2026 |

The effective-dated even block in this release changed code three times since 2021: 1735, 4000 from April 2022, 1735 from January 2024, and 4000 from April 2026. The single-number blank-suite row on +9051 ended June 30, 2025. These are dates on source records. They establish no historical QuickBooks behavior. The active SST and DOR ZIP+4 downloads agree on these assignments: +4547, +7100 and +9051 map to 1735, while +6978 maps to 4000. [Source rows and dates](../results/2026Q4/case_14450_sst_rows.csv)

## What USPS actually returned

| Input on the USPS public form | Visible result | Interpretation used here |
|---|---|---|
| Building, no suite | Building entry +9051, suite alternatives +4547 and +7100, even block +6978 | +9051 is the building candidate used in the replay. |
| STE 101, 108, 109 | One entry for each. +9051 for 101, +4547 for 108 and 109 | All three have listed SST street matches. |
| STE 105 | One entry, +9051. The candidate list for the building includes STE 102–107 on +9051. | The SST file omits that range. This is the strongest single-result control. |
| STE 101-A, STE 101A, STE 9999 | 13 candidates on each five-digit lookup, including an echo of the supplied unit at +9051 | A returned string does not independently confirm occupancy, deliverability or a unique suite assignment. |
| No suite, supplied +9051, +4547 or +6978 | The results included +9051 and the other building and street extensions | Input selection affects the replay. No universal CASS correction is inferred. |

[USPS address lookup](https://tools.usps.com/zip-code-lookup.htm?byaddress) · [Input-specific notes](../tests/test_inputs_standardized.tsv)

## Why the results differ

With no suite, omitting the ZIP extension matches the even block at 8.9%. Including the selected +9051 removes that block and falls through to the ZIP+4 record at 10.4%. With STE 105 or STE 101-A retained and +9051 selected, both exact-field variants give 10.4% by ZIP+4. A different postal result, input transformation or source could change that outcome. Intuit's internal trace is unavailable.

AddressRates returned 1735 for the winery suite variants. Its XML returned ZIP 98052, with +9051 for STE 101-A and +4547 for STE 108 and 109. Those address queries returned result 4, for which DOR calls for validation. A query for 14412 on the block returned 4000, while 14498 returned 1735. Address lookup responses alone do not trace a city boundary. [Recorded state responses](../results/2026Q4/addressrates_test_inputs.csv) · [DOR interface and status codes](https://dor.wa.gov/wa-sales-tax-rate-lookup-url-interface)

DOR can confirm the reporting code for the event location and the treatment of earlier returns. A repair to the file should reconcile both the blank-suite building record and the even block. Simply adding a conflicting single-number row can create another overlap when the ZIP extension is omitted.
