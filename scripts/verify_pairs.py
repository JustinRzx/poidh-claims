#!/usr/bin/env python3
"""Verify the two $12.5M pairs are real contributions and not amendment double-counts.

FEC bulk files include amended records. If a contribution was amended, the original and the
amendment can both appear, so an aggregation that ignores AMNDT_IND and SUB_ID can double a
number. This prints every field of every record whose donor surname is Andreessen or Horowitz
with the a16z employer, so the four records can be inspected directly.
"""
import zipfile

TARGETS = ("ANDREESSEN, MARC", "HOROWITZ, BENJAMIN")
with zipfile.ZipFile("/root/makefun-work/fec/indiv26.zip") as z:
    with z.open(z.namelist()[0]) as fh:
        for raw in fh:
            line = raw.decode("latin-1").rstrip("\n")
            if "ANDREESSEN HOROWITZ" not in line:
                continue
            f = line.split("|")
            if len(f) < 21 or not f[7].upper().startswith(TARGETS):
                continue
            print(f"amndt={f[1]} type={f[5]} entity={f[6]} subid={f[20]} file={f[17]}")
            print(f"   {f[7]:<28} emp={f[11]:<24} date={f[13]} amt={float(f[14]):>14,.0f} cmte={f[0]} tran={f[16]}")
