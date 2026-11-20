# Would the ZIP+4 resolve the conflicts?

## C1 overlapping no-suite records

| | rows | rate-changing |
|---|---|---|
| each record has its own ZIP+4 | 686 | 519 |
| two records share a ZIP+4 | 6 | 1 |

Where each record has its own ZIP+4, including the standardized ZIP+4 picks the record that carries it. Which one that is depends on the ZIP+4 USPS assigns, which the file does not contain.

## C4a buildings whose suites are coded differently from every no-suite record

| | buildings | rate-changing |
|---|---|---|
| suite ZIP+4 records carry the suites' code | 101 | 75 |

For these buildings the two permitted ways of querying disagree: leaving the ZIP+4 out matches the block record; including a suite ZIP+4 (USPS gives the building default, which was a suite ZIP+4 at 14450, 21806 and 4212) falls through to a ZIP+4 record with the suites' code.
