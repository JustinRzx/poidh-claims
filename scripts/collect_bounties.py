#!/usr/bin/env python3
"""Enumerate every poidh bounty across Base, Arbitrum and Mainnet from poidh.xyz's own data
endpoints, and save the raw record for each to JSONL.

Reproducible by anyone: no API key, no auth, no indexer of our own. Frontend ids are offset
from contract ids (Base +986, Arbitrum +180, Mainnet +0), so walking the frontend id space
walks the whole protocol history. Frontend ids are what the URLs and the MCP tools use.

Usage: python3 collect_bounties.py [out.jsonl]
"""
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

OUT = sys.argv[1] if len(sys.argv) > 1 else "/root/makefun-work/poidh-activity/bounties.jsonl"
UA = {"User-Agent": "Mozilla/5.0 (compatible; poidh-activity-census/1.0)"}

RANGES = {
    # chain: (frontend id start, end inclusive) -- contract ids 1..N plus the chain's offset
    "base": (987, 1600),
    "arbitrum": (181, 620),
    "mainnet": (1, 80),
}


def fetch(target):
    chain, fid = target
    url = f"https://poidh.xyz/{chain}/bounty/{fid}/data"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", "replace")
        if not raw.strip().startswith("{"):
            return None
        d = json.loads(raw, strict=False)
    except Exception:
        return None
    if not d.get("title"):
        return None
    return {
        "chain": chain,
        "frontend_id": fid,
        "on_chain_id": d.get("onChainId"),
        "title": d.get("title"),
        "description": d.get("description"),
        "issuer": d.get("issuer"),
        "created_at": d.get("createdAt"),
        "amount_wei": d.get("amount"),
        "status": d.get("status"),
        "is_multiplayer": d.get("isMultiplayer"),
        "is_canceled": d.get("isCanceled"),
        "claim_count": len(d.get("claims") or []),
        "claims": [
            {
                "title": c.get("title"),
                "description": c.get("description"),
                "issuer": c.get("issuer"),
                "is_accepted": c.get("isAccepted"),
                "url": c.get("url"),
            }
            for c in (d.get("claims") or [])
        ],
    }


def main():
    targets = [(c, f) for c, (a, b) in RANGES.items() for f in range(a, b + 1)]
    print(f"probing {len(targets)} bounty ids across {len(RANGES)} chains", flush=True)
    found = 0
    with open(OUT, "w") as out, ThreadPoolExecutor(max_workers=10) as ex:
        for rec in ex.map(fetch, targets):
            if rec:
                out.write(json.dumps(rec) + "\n")
                found += 1
                if found % 100 == 0:
                    print(f"  {found} found", flush=True)
    print(f"done: {found} bounties -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
