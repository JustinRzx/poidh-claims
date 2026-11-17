# Reproduction, poidh claim 1544

No API key and no account. The FEC publishes the same data as bulk files:

    curl -sLO https://www.fec.gov/files/bulk-downloads/2026/indiv26.zip   # 2.5 GB, individual contributions
    curl -sLO https://www.fec.gov/files/bulk-downloads/2026/pas226.zip    # committee-to-committee
    curl -sLO https://www.fec.gov/files/bulk-downloads/2026/cm26.zip      # committee master
    curl -sLO https://www.fec.gov/files/bulk-downloads/2026/cn26.zip      # candidate master

- `scan_individual.py` streams indiv26, keeps gifts whose EMPLOYER matches a crypto firm, and
  writes the rows plus aggregates. 37,858,961 records scanned, 5,225 kept, $89,444,235 total.
- `verify_pairs.py` prints every field of the four largest records so the $12.5M pairs can be
  checked against amendment double-counting. All four carry AMNDT_IND=N with distinct SUB_IDs.

Two traps worth knowing, both of which produced wrong numbers here before being caught:

1. `TRANSACTION_DT` is MMDDYYYY, not YYYYMMDD. Filtering on the first four characters silently
   drops every row (it reported zero crypto donations across 8,000,000 records).
2. Employer names are not normalised by the FEC. Ripple appears as RIPPLE, RIPPLE INC.,
   RIPPLE, INC. and RIPPLE INC; Andreessen Horowitz as ANDREESSEN HOROWITZ and A16Z. Without
   folding those together about $17.8M disappears from the totals.

For the committee side: independent expenditure-style spending never appears in `pas226` as a
payment to a candidate. Filtering that file for the three crypto super PACs as the donor gives
362 transactions totalling $97,912,015, all to media vendors.

## Second claim: the vendor route

    curl -sLO https://www.fec.gov/files/bulk-downloads/2026/pas226.zip

`scan_vendors.py` filters pas226 for the three crypto super PACs as the donor. 362 payments,
$97,912,015, to 11 vendors and no candidate committee. Main Street Media Group $51,722,969
(44 tx, 89% to Republican-designated races), Targeted Platform Media $34,760,272 across two
spellings (100% Democratic), Kinetic Campaigns $5,595,895 (100% Democratic), RBC Media LLC
$4,702,347 (100% Republican), Dockside Strategies $901,543, other five vendors $228,989.

The OTHER_ID column in pas226 is a candidate id, not a committee id, which is what allows the
spending to be attributed to a race. Join it to cn26 (candidate master) for the name and party.
