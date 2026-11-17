#!/usr/bin/env python3
"""Collect every claim's proof URI for every poidh bounty, via poidh.xyz's own tRPC endpoint.

Why: an agent that submits a claim usually serves its proof from a machine endpoint it
controls (a worker, a static host, a script-generated PNG path), while a person posts a
photo to a social or image host. The proof URI host is therefore a behavioural fingerprint
that does not depend on the claimant describing itself in words.

Input:  /root/makefun-work/poidh-activity/bounties.jsonl  (from collect_bounties.py)
Output: /root/makefun-work/poidh-activity/claims.jsonl

Usage: python3 collect_claims.py
"""
import json
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

SRC = "/root/makefun-work/poidh-activity/bounties.jsonl"
OUT = "/root/makefun-work/poidh-activity/claims.jsonl"
UA = ["-A", "Mozilla/5.0 (compatible; poidh-activity-census/1.0)"]
CHAIN_ID = {"base": 8453, "arbitrum": 42161, "mainnet": 1}


def fetch(rec):
    chain = rec["chain"]
    bid = rec.get("on_chain_id")
    if not bid:
        return []
    rows = []
    cursor = None
    for _ in range(60):  # tRPC paginates 10 per page
        obj = {"bountyId": bid, "chainId": CHAIN_ID[chain]}
        if cursor:
            obj["cursor"] = cursor
        inp = urllib.parse.quote(json.dumps({"json": obj}))
        url = f"https://poidh.xyz/api/trpc/claims.fetchBountyClaims?input={inp}"
        out = subprocess.run(["curl", "-s", "-m", "30", *UA, url], capture_output=True, text=True).stdout
        try:
            d = json.loads(out)
        except Exception:
            break
        j = (((d.get("result") or {}).get("data") or {}).get("json") or {})
        items = j.get("items") or []
        for c in items:
            rows.append({
                "chain": chain,
                "bounty_frontend_id": rec["frontend_id"],
                "bounty_on_chain_id": bid,
                "bounty_title": rec.get("title"),
                "bounty_created_at": rec.get("created_at"),
                "claim_id": c.get("id"),
                "claim_title": c.get("title"),
                "claim_description": c.get("description"),
                "claim_uri": c.get("url"),
                "claim_issuer": c.get("issuer"),
                "is_accepted": c.get("isAccepted"),
            })
        cursor = j.get("nextCursor")
        if not cursor or not items:
            break
    return rows


def main():
    recs = [json.loads(l) for l in open(SRC)]
    print(f"fetching claims for {len(recs)} bounties", flush=True)
    n = 0
    with open(OUT, "w") as out, ThreadPoolExecutor(max_workers=6) as ex:
        for rows in ex.map(fetch, recs):
            for r in rows:
                out.write(json.dumps(r) + "\n")
                n += 1
            if n and n % 500 < len(rows):
                print(f"  {n} claims", flush=True)
    print(f"done: {n} claims -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
