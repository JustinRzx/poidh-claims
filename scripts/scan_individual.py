#!/usr/bin/env python3
"""Stream the FEC 2026 individual-contribution bulk file and pull out donations made by people
who work at crypto companies.

Why this angle: every headline and every other poidh claim on this bounty is about PAC
spending. The employer field lets us ask a different question, what the industry's own
employees gave out of their own pockets.

indiv26 format (pipe-delimited, no header):
 0 CMTE_ID  1 AMNDT_IND  2 RPT_TP  3 TRANSACTION_PGI  4 IMAGE_NUM  5 TRANSACTION_TP
 6 ENTITY_TP  7 NAME  8 CITY  9 STATE  10 ZIP  11 EMPLOYER  12 OCCUPATION
 13 TRANSACTION_DT  14 TRANSACTION_AMT  15 OTHER_ID  16 TRAN_ID  17 FILE_NUM
 18 MEMO_CD  19 MEMO_TEXT  20 SUB_ID
"""
import collections
import csv
import json
import re
import sys
import zipfile

ZIP = "/root/makefun-work/fec/indiv26.zip"
OUT = "/root/makefun-work/fec/crypto-employees.json"

# Employers that make the donation a crypto-industry one. Kept tight on purpose: a loose
# match on "BLOCKCHAIN" or "CRYPTO" alone would sweep in unrelated firms that happen to
# have the word in their name, so the specific companies are listed too.
FIRMS = [
    "COINBASE", "RIPPLE", "CIRCLE INTERNET", "CIRCLE FINANCIAL", "BINANCE", "KRAKEN",
    "GEMINI TRUST", "GEMINI.COM", "CHAINALYSIS", "BLOCKCHAIN.COM", "BITGO", "ANCHORAGE",
    "FIREBLOCKS", "GRAYSCALE", "MICROSTRATEGY", "MARATHON DIGITAL", "RIOT PLATFORMS",
    "PARADIGM OPERATIONS", "ANDREESSEN", "A16Z", "PANTERA", "POLYCHAIN", "DRAGONFLY",
    "MULTICOIN", "ELECTRIC CAPITAL", "BLOCKCHAIN CAPITAL", "GALAXY DIGITAL", "CONSENSYS",
    "LEDGER", "TREZOR", "CHAINLINK", "AVA LABS", "DFINITY", "SOLANA FOUNDATION",
    "SOLANA LABS", "POLYGON", "UNISWAP", "OPENSEA", "AAVE", "TETHER", "BITWISE",
    "BITSTAMP", "BLOCKCHAIN ASSOCIATION", "CRYPTO COUNCIL", "CUSTODIA", "BAKKT",
    "BITFINEX", "HUOBI", "OKCOIN", "WINTERMUTE", "AMBER GROUP", "PRIME TRUST",
]
PAT = re.compile("|".join(re.escape(f) for f in FIRMS))

by_employer = collections.Counter()
by_employer_n = collections.Counter()
by_committee = collections.Counter()
by_state = collections.Counter()
rows = []
total = 0
scanned = 0
other_party = collections.Counter()

with zipfile.ZipFile(ZIP) as z:
    name = z.namelist()[0]
    with z.open(name) as fh:
        for raw in fh:
            scanned += 1
            if scanned % 2_000_000 == 0:
                print(f"  scanned {scanned:,} rows, {len(rows):,} crypto hits", flush=True)
            line = raw.decode("latin-1").rstrip("\n")
            f = line.split("|")
            if len(f) < 15:
                continue
            emp = f[11].upper().strip()
            if not emp or not PAT.search(emp):
                continue
            try:
                amt = float(f[14])
            except ValueError:
                continue
            dt = f[13]
            # FEC transaction dates are DDMMYYYY, so the year is the last four characters.
            if len(dt) != 8 or dt[4:] not in ("2025", "2026"):
                continue
            total += amt
            by_employer[emp] += amt
            by_employer_n[emp] += 1
            by_committee[f[0]] += amt
            by_state[f[9]] += amt
            rows.append({
                "employer": emp, "occupation": f[12], "name": f[7], "state": f[9],
                "date": dt, "amount": amt, "committee": f[0],
            })

json.dump({
    "scanned_rows": scanned,
    "hits": len(rows),
    "total_usd": total,
    "by_employer": by_employer.most_common(40),
    "by_committee": by_committee.most_common(40),
    "by_state": by_state.most_common(20),
    "rows": rows,
}, open(OUT, "w"), indent=1)
print(f"scanned {scanned:,} rows | crypto-employer donations: {len(rows):,} | total ${total:,.0f}")
print(f"saved {OUT}")
for e, v in by_employer.most_common(15):
    print(f"   ${v:>12,.0f}  {by_employer_n[e]:>5} gifts  {e[:46]}")
