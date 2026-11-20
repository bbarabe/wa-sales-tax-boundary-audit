# DOR AddressRates vs. the conflicting records

### C1: overlapping no-suite address records

692 rows checked. Query: first house number of the overlap, street, ZIP5.

| DOR lookup returned | rows | rate-changing rows |
|---|---|---|
| narrower record's code | 671 | 513 |
| wider record's code | 21 | 7 |

### C2: duplicate ZIP+4 records

15 rows checked. Query: ZIP+4 only, no street.

| DOR lookup returned | rows | rate-changing rows |
|---|---|---|
| one of the duplicate records' codes | 15 | 10 |

### C4: building suites vs. the no-suite records

393 rows checked. Query: house number and street with no suite, ZIP5. C4a = no no-suite record carries the suites' code; C4b = no-suite records overlap and the narrowest one agrees with the suites.

| DOR lookup returned | rows | rate-changing rows |
|---|---|---|
| C4b: narrowest no-suite record's code | 278 | 214 |
| C4a: listed suites' code | 94 | 75 |
| C4b: a wider no-suite record's code | 13 | 3 |
| C4a: no-suite record's code | 7 | 0 |
| C4b: neither | 1 | 1 |

### C7: SST file vs. DOR address file (random sample)

200 rows checked. Query: first house number of the DOR range, street, ZIP5.

| DOR lookup returned | rows | rate-changing rows |
|---|---|---|
| DOR address file's code | 190 | 132 |
| SST file's code | 8 | 5 |
| neither | 2 | 2 |

