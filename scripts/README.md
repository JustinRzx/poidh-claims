# Reproduction

Two scripts, no API key, no auth, nothing but poidh.xyz's own public endpoints.

- `collect_bounties.py` walks the frontend id space of Base, Arbitrum and mainnet
  (frontend ids are offset from contract ids: Base +986, Arbitrum +180, mainnet +0) and
  writes one record per bounty, claims included, to `bounties.jsonl`.
- `collect_claims.py` follows the `nextCursor` of the `claims.fetchBountyClaims` tRPC call
  for each bounty and writes every claim's title, description, proof URI and issuer to
  `claims.jsonl`.

Coverage note: 151 busy bounties return no claims through that endpoint, so `claims.jsonl`
holds 2,948 of the 5,186 claims the bounty pages report (57%).
