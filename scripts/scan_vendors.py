#!/usr/bin/env python3
"""Where the three crypto super PACs' money actually went, from the FEC 2026 bulk files.

pas226 is committee-to-committee money (Schedule A filed by committees). Filtering it for the
three crypto super PACs as the DONOR shows what left them. The OTHER_ID column is not a
committee id: it is the candidate id the money was designated to, which is what lets the
spending be attributed to a race.

Outputs a summary JSON plus a per-race table.
"""
import collections
import json
import zipfile

PAC = {"C00835959": "FAIRSHAKE", "C00848440": "PROTECT PROGRESS", "C00836221": "DEFEND AMERICAN JOBS"}
FEC = "/root/makefun-work/fec"


def candidates():
    out = {}
    with zipfile.ZipFile(f"{FEC}/cn26.zip") as z:
        with z.open(z.namelist()[0]) as fh:
            for raw in fh:
                f = raw.decode("latin-1").rstrip("\n").split("|")
                if len(f) > 4:
                    out[f[0]] = {"name": f[1], "party": f[2], "state": f[4]}
    return out


def main():
    cand = candidates()
    vendor = collections.Counter()
    vendor_n = collections.Counter()
    race = collections.Counter()
    rows = 0
    with zipfile.ZipFile(f"{FEC}/pas226.zip") as z:
        with z.open(z.namelist()[0]) as fh:
            for raw in fh:
                f = raw.decode("latin-1").rstrip("\n").split("|")
                if len(f) < 16 or f[0] not in PAC:
                    continue
                try:
                    amt = float(f[14])
                except ValueError:
                    continue
                rows += 1
                v = (f[7] or "?").strip().upper()
                vendor[v] += amt
                vendor_n[v] += 1
                race[(f[15], v)] += amt

    total = sum(vendor.values())
    top = vendor.most_common(12)
    print(f"transactions out of the three crypto super PACs: {rows}")
    print(f"total: ${total:,.0f}")
    print(f"distinct vendors paid: {len(vendor)}")
    print(f"share through the single largest vendor: {100*top[0][1]/total:.1f}%")
    print(f"share through the two largest: {100*(top[0][1]+top[1][1])/total:.1f}%")
    print("\nper vendor:")
    for v, a in top:
        print(f"   ${a:>13,.0f}  {vendor_n[v]:>4} tx  {v[:40]}")
    print("\ntop races by designated candidate:")
    races = []
    for (cid, v), a in race.most_common(20):
        c = cand.get(cid, {})
        races.append({"candidate_id": cid, "name": c.get("name"), "party": c.get("party"),
                      "state": c.get("state"), "vendor": v, "amount": a})
        print(f"   ${a:>12,.0f}  {cid}  {str(c.get('name'))[:26]:<26} {c.get('party')} {c.get('state')}  {v[:24]}")
    # honest caveat: does any row pay a candidate committee directly?
    print("\nrecipients that look like a candidate committee:")
    direct = [v for v in vendor if v.startswith(("FRIENDS", "COMMITTEE TO", "CITIZENS FOR", "ELECT"))]
    print("  ", direct if direct else "none: every recipient is a vendor, not a campaign")
    json.dump({"rows": rows, "total": total, "vendor": top, "vendor_n": dict(vendor_n),
               "races": races, "distinct_vendors": len(vendor)},
              open(f"{FEC}/vendor-summary.json", "w"), indent=1)
    print(f"\nsaved {FEC}/vendor-summary.json")


if __name__ == "__main__":
    main()
