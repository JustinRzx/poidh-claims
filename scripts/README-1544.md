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
