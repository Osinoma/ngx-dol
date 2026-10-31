#!/usr/bin/env python3
"""
10_docs.py - Fill the documentation templates from paper/stats.json.

PLAIN-LANGUAGE NOTE: The README, limitations, data paper, talk track, citation
file and your verification checklist all quote numbers. None of those numbers
are typed by hand: this script copies them from the stats file that the quality
check writes, so the text can never disagree with the data. It also builds a
Word version of the data paper. You do not need to open this file.
"""
import datetime as dt, json, os, re, subprocess, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from nglib import ROOT, PROC, INTERIM, RAW

FINAL = "--final" in sys.argv


def fmt(n):
    return f"{int(n):,}"


def main():
    s = json.load(open(os.path.join(ROOT, "paper", "stats.json")))
    a = json.load(open(os.path.join(ROOT, "AUTHORS.json")))
    au = a["authors"][0]
    zr = s["mean_zero_return_share_by_year"]
    last_year = max(zr)
    v = dict(s)
    v.update(
        author_name=au["name"], family=au["family"], given=au["given"], orcid=au["orcid"], email=au["email"],
        affiliation=au["affiliation"], github=a["github"], competing_interests=a["competing_interests"],
        rows_daily_fmt=fmt(s["rows_daily"]), recon_ds_n_fmt=fmt(s["recon_ds_n"]), recon_wkc_n_fmt=fmt(s["recon_wkc_n"]),
        files_total_fmt=fmt(s["files_pricelist"] + s["files_officiallist"] + s["files_dailysummary"] + s["files_weekly"] + 1),
        zr_2015_pct=round(100 * zr["2015"]), zr_last_pct=round(100 * zr[last_year]), last_year=last_year,
        first_year=s["first_date"][:4], cr10_value_pct=round(100 * s["cr10_value_median"]),
        cr10_volume_pct=round(100 * s["cr10_volume_median"]), year=s["last_date"][:4],
        build_date=dt.date.today().isoformat(), doi=a.get("doi", ""), release_date=a.get("release_date", ""),
        trading_days_fmt=fmt(s["trading_days"]), recon_ds_deals_pct_int=round(s["recon_ds_deals_pct"]),
        first_month_year=dt.date.fromisoformat(s["first_date"]).strftime("%B %Y"),
        last_month_year=dt.date.fromisoformat(s["last_date"]).strftime("%B %Y"),
        snapshot_date=pd.read_csv(os.path.join(PROC, "ngxdol_securities.csv")).snapshot_date.iloc[0],
    )
    mode = a.get("release_mode", "full")
    if mode == "measures":
        v["release_scope"] = ("Version 1.0 publishes the open parser and the derived measures only: a security-month "
            "liquidity panel (Amihud illiquidity, zero-return share, turnover, days traded), daily market totals, weekly "
            "broker-concentration indices (CR5, CR10, HHI of the top 10), and a securities reference table. The full "
            "security-day panel of prices and trades is not redistributed in v1.0; anyone can rebuild it from NGX's public "
            "reports with `run_all.sh`. A request to NGX for permission to redistribute the full panel is pending; if granted, "
            "it will be added as v1.1 under the same DOI.")
        v["files_table"] = "\n".join([
            "| File | One row is |", "|---|---|",
            "| `ngxdol_liquidity_monthly.csv.gz` | one security in one month: Amihud, zero-return share, turnover, days listed and traded |",
            f"| `ngxdol_market_daily.csv.gz` | one trading day: securities listed and traded, total deals, volume, value ({s['trading_days']} rows) |",
            "| `ngxdol_broker_concentration.csv.gz` | one week and measure: CR5, CR10, HHI of the published top 10 |",
            f"| `ngxdol_securities.csv.gz` | one security: name, ISIN, board, sector, first and last date ({s['symbols']} rows) |",
            "| `qa_report.txt` | the quality report |"])
        v["permission_text"] = ("NGX-DOL v1.0 does not redistribute NGX's security-level daily prices or broker tables; it publishes "
            "derived measures and market aggregates, and code that downloads the original reports directly from NGX. Raw NGX PDFs are not mirrored.")
    else:
        v["release_scope"] = "The full security-day panel, monthly liquidity panel, market totals, weekly broker tables and concentration measures, and securities table."
        v["files_table"] = "\n".join(["| File | One row is |", "|---|---|",
            "| `ngxdol_daily.csv.gz` | one security on one trading day |", "| `ngxdol_monthly.csv.gz` | one security in one month |",
            "| `ngxdol_market_daily.csv.gz` | one trading day |", "| `ngxdol_broker_weekly.csv.gz` | one broker rank in one week |",
            "| `ngxdol_broker_concentration.csv.gz` | one week and measure |", "| `ngxdol_securities.csv.gz` | one security |",
            "| `qa_report.txt` | the quality report |"])
        v["permission_text"] = f"Redistribution of the derived dataset is made under written permission from NGX: {a['data_permission']}. Raw NGX PDFs are not mirrored."
    targets = {"LICENSE-DATA.md": "LICENSE-DATA.md", "README.md": "README.md", "LIMITATIONS.md": "docs/LIMITATIONS.md", "paper.md": "paper/ngxdol_data_paper.md",
               "TALK_TRACK.md": "docs/TALK_TRACK.md", "CITATION.cff": "CITATION.cff"}
    for src, dst in targets.items():
        t = open(os.path.join(ROOT, "templates", src)).read()
        missing = set(re.findall(r"{{(\w+)}}", t)) - set(v)
        if missing:
            raise SystemExit(f"{src}: no stats value for {missing}")
        t = re.sub(r"{{(\w+)}}", lambda m: str(v[m.group(1)]), t)
        if FINAL:
            t = t.replace("**Status: DRAFT, not yet verified by the author.** Version {0}. Do not cite until released with a DOI.".format(v["version"]),
                          "**Status: released {0}.** Version {1}. DOI: https://doi.org/{2}".format(v["release_date"], v["version"], v["doi"]))
            t = re.sub(r"\*\*DRAFT\. Not verified.*?\*\*\n", "", t)
            t = t.replace('date: "DRAFT ', 'date: "')
        open(os.path.join(ROOT, dst), "w").write(t)
    # Word version of the paper (figures resolved relative to paper/)
    subprocess.run(["pandoc", "ngxdol_data_paper.md", "-o", "ngxdol_data_paper.docx", "--resource-path=."],
                   cwd=os.path.join(ROOT, "paper"), check=True)
    write_checklist(s)
    print("docs rendered", "(final)" if FINAL else "(DRAFT)")


def write_checklist(s):
    D = pd.read_csv(os.path.join(PROC, "ngxdol_daily.csv"), low_memory=False)
    T = D[D.traded & (D.trade_source == "price_list")]
    # map content date -> source URL via parse log (file) and provenance (file -> url)
    log = pd.read_csv(os.path.join(INTERIM, "parse_log_pricelist.csv"))
    prov = {}
    for l in open(os.path.join(RAW, "PROVENANCE.txt"), encoding="utf-8"):
        p = l.rstrip("\n").split(" | ")
        if len(p) >= 5:
            prov[p[1]] = p[4]
    url = {r.date: prov.get(r.file, "") for r in log[log.status == "ok"].itertuples()}

    def line(r, why):
        return (f"- [ ] **{why}**: `ngxdol_daily.csv`, date {r.date}, symbol **{r.symbol}**: close {r.close:,.2f}, "
                f"deals {r.deals:,.0f}, volume {r.volume:,.0f}, value {r.value:,.2f}. Open the zip at <{url.get(r.date, 'see catalogue_pricelist.tsv')}>, "
                f"open PRICES1.pdf (or the 'PRICES' file), find {r.symbol}. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___")

    named = [(c["date"], c["symbol"]) for c in s["spot_checks"]]
    rows = [T[(T.date == d) & (T.symbol == sy)] for d, sy in named]
    known = [line(r.iloc[0], "Well-known stock") for r in rows if len(r)]
    ext = [line(T.loc[T.value.idxmax()], "Largest value traded in the dataset"),
           line(T.loc[T.volume.idxmax()], "Largest volume"),
           line(T.loc[T.close.idxmax()], "Highest price"),
           line(T.loc[T.deals.idxmax()], "Most deals in one day"),
           line(T[T.value > 0].loc[T[T.value > 0].value.idxmin()], "Smallest value traded")]
    rnd = [line(r, "Random row (seed 2026)") for r in T.sample(5, random_state=2026).itertuples()]
    flagged = D[D.ret_flag == 1].reindex(D[D.ret_flag == 1].ret.abs().sort_values(ascending=False).index).head(3)
    fl = "\n".join(f"  - {r.date} {r.symbol}: previous {r.pclose if pd.notna(r.pclose) else 'n/a'}, close {r.close}, return {r.ret:+.0%}" for r in flagged.itertuples())

    text = f"""# Your verification checklist: NGX-DOL v1.0

*Plain-language version: before anything goes public under your name, you check it. Total time: about 1.5 to 2 hours, in one sitting. Tick each box. The publish check (`publish_gate.py`) handles the mechanical items; these are yours.*

## Part 1: Make sure the results can be rebuilt (20 to 45 min, mostly waiting)

Pick one:
- [ ] **Option A, run it yourself.** On a Mac or Linux computer with Python installed, open Terminal in the project folder and paste:
  ```
  pip install -r requirements.txt
  bash run_all.sh
  ```
  The download takes about 40 minutes. At the end the screen should show `daily rows {s['rows_daily']} symbols {s['symbols']} days {s['trading_days']}`.
- [ ] **Option B, ask Claude.** In a new chat (Opus 5.5 or Fable 5), share the GitHub repository and say: "Re-run this pipeline from scratch and give me the headline numbers." Compare: {s['trading_days']} trading days, {s['rows_daily']:,} rows, {s['symbols']} symbols, Daily Summary volume match {s['recon_ds_volume_pct']}%.

Then:
- [ ] Open `paper/ngxdol_data_paper.docx`. Spot-check three numbers against `paper/stats.json`. They should be identical.

## Part 2: Check the sources (15 min)

- [ ] Open https://ngxgroup.com/exchange/data/data-library/. Expand "Daily Official List (Equities)" and "Weekly Summary Statistics". Recent files should be listed.
- [ ] Open https://ngxgroup.com/terms-and-conditions/. It restricts republishing NGX content without written permission. **Confirm your NGX permission covers redistributing this derived dataset under CC BY 4.0.** If it does not, choose option 3 in Part 4.

## Part 3: Check rows by hand against the original NGX PDFs (40 min)

Each link downloads a small zip from NGX. Open it, open the PDF named `PRICES1` (or similar), and find the symbol.

**Well-known stocks**
{chr(10).join(known)}

**Extreme values (most likely to be errors)**
{chr(10).join(ext)}

**Random rows**
{chr(10).join(rnd)}

## Part 4: Your decisions (15 min)

- [ ] **NGX permission.** Option 1: paste the real reference (letter date, number, signatory) into `AUTHORS.json`. Option 2: Claude drafts a request to NGX Market Data and the release waits. Option 3: release v1.0 as code plus monthly, market and broker files only, with no stock-day prices, and say so in the README. Your choice: ___
- [ ] **Large returns.** {s['ret_flag_rows']} rows have daily returns above 11% and are excluded from Amihud. The largest are:
{fl}
  Option A: keep flagged as is (recommended). Option B: drop them from the daily file. Your choice: ___
- [ ] **2017-2018 step in Amihud illiquidity** (Figure 2b). Do you know of an NGX rule change, such as the minimum quantity needed to move a price, that explains it? If so, give the rule or notice so it can be cited in LIMITATIONS item 8. Your note: ___
- [ ] **Competing-interests wording** in `AUTHORS.json`: "{json.load(open(os.path.join(ROOT, 'AUTHORS.json')))['competing_interests']}". Edit to name your firm if appropriate. ___
- [ ] **"No open dataset exists" claim.** Search Google Scholar, Kaggle and GitHub for "Nigerian Stock Exchange daily data". Keep the claim only if nothing comparable turns up. ___

## Part 5: Before it goes public (20 min)

- [ ] Rewrite the README opening paragraph and the paper abstract in your own words (Claude can do it with you line by line).
- [ ] Name, ORCID {json.load(open(os.path.join(ROOT, 'AUTHORS.json')))['authors'][0]['orcid']}, affiliation and email are correct in `AUTHORS.json`.
- [ ] You have read `docs/LIMITATIONS.md` and agree with it.
- [ ] Claude re-runs with `--final` and `publish_gate.py` passes.
- [ ] Evidence log row written on release day.

**When every box is ticked, tell Claude in your own words that you have checked the package and approve publishing.**
"""
    open(os.path.join(ROOT, "docs", "VERIFY_CHECKLIST.md"), "w").write(text)


if __name__ == "__main__":
    main()
