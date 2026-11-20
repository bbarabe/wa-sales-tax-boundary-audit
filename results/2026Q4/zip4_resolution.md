# Would the ZIP+4 resolve the conflicts?

## C1 overlapping no-suite records

| | rows | rate-changing |
|---|---|---|
| conflicting codes have disjoint extensions | 686 | 519 |
| different codes share an extension | 6 | 1 |

A matching extension distinguishes the codes in the disjoint group. A different extension can miss every overlapping row. The chosen postal candidate matters.

## C4a buildings whose suites are coded differently from every no-suite record

| | buildings | rate-changing |
|---|---|---|
| suite ZIP+4 records carry the suites' code | 101 | 75 |

For a no-suite query that uses one of the listed suite ZIP+4s, including that extension can change the result from a covering street row to the ZIP+4 fallback. The scan does not determine which extension a postal standardizer would select for each building.
