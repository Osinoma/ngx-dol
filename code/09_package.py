#!/usr/bin/env python3
"""
09_package.py - Bundle the release files for Zenodo.

PLAIN-LANGUAGE NOTE: Compresses the finished data tables, the codebook and the
quality report into release/ so they can be uploaded to Zenodo as NGX-DOL v1.0.
Raw NGX PDFs are deliberately NOT included. You do not need to open this file.
"""
import gzip, hashlib, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from nglib import PROC, ROOT

import json
import pandas as pd

MODE = json.load(open(os.path.join(ROOT, "AUTHORS.json"))).get("release_mode", "full")
REL = os.path.join(ROOT, "release")
shutil.rmtree(REL, ignore_errors=True); os.makedirs(REL)
if MODE == "measures":
    # v1.0 without redistribution permission: derived measures and aggregates only
    stage = os.path.join(ROOT, "data", "interim", "release_stage"); os.makedirs(stage, exist_ok=True)
    m = pd.read_csv(os.path.join(PROC, "ngxdol_monthly.csv"))
    m[["symbol", "month", "board", "sector", "days_listed", "days_traded", "zero_return_share", "amihud_mean",
       "amihud_obs", "turnover"]].to_csv(os.path.join(stage, "ngxdol_liquidity_monthly.csv"), index=False, float_format="%.10g")
    for f in ["ngxdol_market_daily.csv", "ngxdol_broker_concentration.csv", "ngxdol_securities.csv"]:
        shutil.copy(os.path.join(PROC, f), stage)
    files = [(os.path.join(stage, f), f) for f in sorted(os.listdir(stage))]
else:
    files = [(os.path.join(PROC, f), f) for f in ["ngxdol_daily.csv", "ngxdol_monthly.csv", "ngxdol_market_daily.csv",
             "ngxdol_broker_weekly.csv", "ngxdol_broker_concentration.csv", "ngxdol_securities.csv"]]
lines = []
for src, f in files:
    dst = os.path.join(REL, f + ".gz")
    with open(src, "rb") as i, open(dst, "wb") as raw, \
            gzip.GzipFile(filename=f, mode="wb", fileobj=raw, compresslevel=9, mtime=0) as o:  # reproducible bytes
        shutil.copyfileobj(i, o)
for f in ["qa_report.txt"]:
    shutil.copy(os.path.join(PROC, f), REL)
for f in ["docs/CODEBOOK.md", "docs/LIMITATIONS.md", "README.md", "LICENSE-DATA.md"]:
    if os.path.exists(os.path.join(ROOT, f)):
        shutil.copy(os.path.join(ROOT, f), REL)
for f in sorted(os.listdir(REL)):
    if f == "SHA256SUMS.txt":
        continue
    h = hashlib.sha256(open(os.path.join(REL, f), "rb").read()).hexdigest()
    lines.append(f"{h}  {f}")
open(os.path.join(REL, "SHA256SUMS.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
