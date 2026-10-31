#!/usr/bin/env python3
"""
07_qa.py - Quality checks for NGX-DOL. Writes data/processed/qa_report.txt and
paper/stats.json.

PLAIN-LANGUAGE NOTE: This script checks the finished data against itself and
against independent NGX reports. It counts rows, compares each stock's daily
trades with the exchange's separate Daily Summary, compares daily totals with
the exchange's weekly report, checks that prices make sense (high is not below
low, etc.), and lists a handful of named rows you can look up by hand. Read
qa_report.txt before trusting anything. Every number in the data paper comes
from stats.json, which this script writes.
"""
import json, os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from nglib import INTERIM, PROC, ROOT

out, stats = [], {}


def say(s=""):
    out.append(s); print(s)


def pct(x):
    return round(100 * float(x), 2)


def main():
    D = pd.read_csv(os.path.join(PROC, "ngxdol_daily.csv"), parse_dates=["date"], low_memory=False)
    say("NGX-DOL QA REPORT"); say("=" * 60)

    # 1. Parse logs
    say("\n1. PARSE LOGS (one row per source file)")
    for f, col in (("parse_log_pricelist.csv", "status"), ("parse_log_officiallist.csv", "status"),
                   ("parse_log_weekly.csv", "status"), ("parse_log_dailysummary.csv", "status")):
        p = os.path.join(INTERIM, f)
        if os.path.exists(p):
            l = pd.read_csv(p)
            say(f"  {f}: {len(l)} files; " + ", ".join(f"{k}={v}" for k, v in l[col].value_counts().items()))
            stats[f.replace("parse_log_", "files_").replace(".csv", "")] = int(len(l))

    # 2. Coverage
    say("\n2. COVERAGE")
    days = D.date.drop_duplicates().sort_values()
    stats.update(first_date=str(days.min().date()), last_date=str(days.max().date()), trading_days=int(len(days)),
                 rows_daily=int(len(D)), symbols=int(D.symbol.nunique()),
                 rows_traded=int(D.traded.sum()))
    say(f"  {stats['trading_days']} trading days, {stats['first_date']} to {stats['last_date']}")
    say(f"  {stats['rows_daily']:,} security-day rows; {stats['rows_traded']:,} with trading; {stats['symbols']} symbols")
    gaps = days.diff().dt.days
    big = days[gaps > 5]
    say(f"  calendar gaps > 5 days: {len(big)}")
    for d in big:
        say(f"    gap ending {d.date()} ({int(gaps[days == d].iloc[0])} days)")
    stats["gaps_gt5"] = int(len(big))
    by_year = D.groupby(D.date.dt.year).agg(days=("date", "nunique"), listed=("in_official_list", "sum"), traded=("traded", "sum"))
    say("  by year:\n" + by_year.to_string())
    stats["days_by_year"] = {int(k): int(v) for k, v in by_year.days.items()}
    only_trade = D[~D.in_official_list.astype(bool)]
    say(f"  traded rows with no Official List entry that day: {len(only_trade):,} ({pct(len(only_trade)/max(1,D.traded.sum()))}% of traded rows)")
    stats["traded_not_in_ol_pct"] = pct(len(only_trade) / max(1, D.traded.sum()))
    say("    most common such symbols: " + ", ".join(only_trade.symbol.value_counts().head(10).index))

    # 3. Range and sanity
    say("\n3. RANGE AND SANITY CHECKS")
    T = D[D.traded.astype(bool)]
    checks = {
        "close <= 0": (T.close <= 0).sum(),
        "high < low": (T.high < T.low).sum(),
        "close outside [low, high]": ((T.close < T.low * 0.999) | (T.close > T.high * 1.001)).sum(),
        "VWAP outside [0.8*low, 1.2*high]": ((T.vwap < T.low * 0.8) | (T.vwap > T.high * 1.2)).sum(),
        "|return| > 11% (flagged, excluded from Amihud)": int(D.ret_flag.sum()),
        "value == 0 on traded rows": int((T.value == 0).sum()),
    }
    for k, v in checks.items():
        say(f"  {k}: {int(v):,}")
    stats["ret_flag_rows"] = int(D.ret_flag.sum())
    stats["ret_flag_pct_traded"] = pct(D.ret_flag.sum() / max(1, len(T)))
    say("  largest flagged returns (likely corporate actions; verify):")
    say(D[D.ret_flag == 1].reindex(D[D.ret_flag == 1].ret.abs().sort_values(ascending=False).index)
        .head(10)[["date", "symbol", "pclose", "close", "ret", "close_src"]].to_string(index=False))

    # 4. Independent reconciliation: price list vs Daily Summary (per security-day)
    say("\n4. RECONCILIATION: Price List vs NGX Daily Summary (same stock, same day)")
    p = os.path.join(INTERIM, "dailysummary_trades.csv")
    if os.path.exists(p):
        S = pd.read_csv(p, parse_dates=["date"]).groupby(["date", "symbol"], as_index=False)[["deals", "volume", "value"]].sum()
        J = T.merge(S, on=["date", "symbol"], suffixes=("", "_ds"))
        n = len(J)
        m_deals = (J.deals == J.deals_ds).mean() if n else np.nan
        m_vol = (J.volume == J.volume_ds).mean() if n else np.nan
        m_val = (np.abs(J.value - J.value_ds) <= 1).mean() if n else np.nan
        say(f"  matched security-days: {n:,} (Daily Summary carries trade rows in {S.date.dt.year.min()}-{S.date.dt.year.max()})")
        say(f"  deals identical: {pct(m_deals)}%  volume identical: {pct(m_vol)}%  value within NGN 1: {pct(m_val)}%")
        stats.update(recon_ds_n=int(n), recon_ds_deals_pct=pct(m_deals), recon_ds_volume_pct=pct(m_vol), recon_ds_value_pct=pct(m_val))
        bad = J[J.volume != J.volume_ds]
        if len(bad):
            say("  examples of volume disagreement:")
            say(bad.head(8)[["date", "symbol", "volume", "volume_ds", "deals", "deals_ds"]].to_string(index=False))

    # 5. Weekly reconciliation: sum of daily price-list volume vs weekly Activity Summary
    say("\n5. RECONCILIATION: daily volumes summed by week vs NGX weekly Activity Summary")
    A = pd.read_csv(os.path.join(INTERIM, "activity_weekly.csv"), parse_dates=["week_start", "week_end"])
    A = A.groupby(["week_start", "week_end", "symbol"], as_index=False)[["deals", "volume", "value"]].sum()
    T2 = T[T.trade_source == "price_list"][["date", "symbol", "deals", "volume", "value"]]
    weeks = A[["week_start", "week_end"]].drop_duplicates()
    weeks = weeks[(weeks.week_end - weeks.week_start).dt.days.between(0, 7)]  # drop misprinted periods
    pl_days = set(T2.date)
    all_days = D.date.drop_duplicates()
    rows = []
    for ws, we in weeks.itertuples(index=False):
        w = T2[(T2.date >= ws) & (T2.date <= we)]
        if w.empty:
            continue
        wk_days = all_days[(all_days >= ws) & (all_days <= we)]
        g = w.groupby("symbol")[["deals", "volume", "value"]].sum().reset_index()
        g["week_end"] = we; g["complete"] = all(d in pl_days for d in wk_days); rows.append(g)
    W = pd.concat(rows).merge(A, on=["week_end", "symbol"], suffixes=("", "_wk"))
    rel = np.abs(W.volume - W.volume_wk) / W.volume_wk.replace(0, np.nan)
    stats.update(recon_wk_n=int(len(W)), recon_wk_vol_exact_pct=pct((W.volume == W.volume_wk).mean()),
                 recon_wk_vol_1pct=pct((rel <= 0.01).mean()))
    say(f"  all security-weeks compared: {len(W):,}; volume exact: {stats['recon_wk_vol_exact_pct']}%; within 1%: {stats['recon_wk_vol_1pct']}%")
    Wc = W[W.complete]
    stats.update(recon_wkc_n=int(len(Wc)), recon_wkc_weeks=int(Wc.week_end.nunique()),
                 recon_wkc_vol_exact_pct=pct((Wc.volume == Wc.volume_wk).mean()),
                 recon_wkc_deals_exact_pct=pct((Wc.deals == Wc.deals_wk).mean()))
    say(f"  weeks where every trading day has a full price list: {stats['recon_wkc_weeks']} weeks, {len(Wc):,} security-weeks;"
        f" volume exact {stats['recon_wkc_vol_exact_pct']}%, deals exact {stats['recon_wkc_deals_exact_pct']}%")
    bw = Wc[Wc.volume != Wc.volume_wk]
    if len(bw):
        say("  examples (complete weeks) where they differ:")
        say(bw.head(8)[["week_end", "symbol", "deals", "deals_wk", "volume", "volume_wk"]].to_string(index=False))
    say("  (Mismatch arises when a weekly file covers a holiday-shortened week or a daily file is missing.)")

    # 6. Market cap, ISIN coverage
    say("\n6. MARKET CAPITALISATION AND IDENTIFIERS")
    rep = (D.mcap_source == "reported")
    first_rep = D.loc[rep, "date"].min()
    stats.update(mcap_reported_rows=int(rep.sum()), mcap_first_reported=str(first_rep.date()) if pd.notna(first_rep) else None,
                 mcap_any_pct=pct(D.mcap_ngn.notna().mean()),
                 isin_rows_pct=pct(D["isin"].notna().mean()), isin_symbols=int(D.loc[D["isin"].notna(), "symbol"].nunique()))
    say(f"  rows with exchange-reported market cap: {rep.sum():,}; first date: {stats['mcap_first_reported']}")
    say(f"  rows with any market cap (reported or carried shares): {stats['mcap_any_pct']}%")
    say(f"  rows with ISIN: {stats['isin_rows_pct']}%  ({stats['isin_symbols']} symbols; snapshot covers currently listed issuers only)")
    Mm = pd.read_csv(os.path.join(INTERIM, "mcap_mapped.csv"))
    say("  market-cap rows symbol mapping: " + ", ".join(f"{k}={v}" for k, v in Mm.map_method.fillna("unmapped").value_counts().items()))

    # 7. Liquidity measures summary
    say("\n7. DERIVED MEASURES")
    Mo = pd.read_csv(os.path.join(PROC, "ngxdol_monthly.csv"))
    Mo["year"] = Mo.month.str[:4].astype(int)
    yr = Mo.groupby("year").agg(zero_ret=("zero_return_share", "median"), amihud=("amihud_mean", "median"))
    say(yr.round(4).to_string())
    stats["median_zero_return_share_by_year"] = {int(k): round(float(v), 4) for k, v in yr.zero_ret.items()}
    stats["median_amihud_by_year"] = {int(k): (None if pd.isna(v) else round(float(v), 6)) for k, v in yr.amihud.items()}
    stats["mean_zero_return_share_by_year"] = {int(k): round(float(v), 4) for k, v in Mo.groupby("year").zero_return_share.mean().items()}
    stats["n_securities_traded_any"] = int(D.loc[D.traded.astype(bool), "symbol"].nunique())
    stats["value_traded_total_ngn_tn"] = round(float(D.value.sum()) / 1e12, 2)
    stats["zero_return_share_all"] = round(float(D.zero_return.mean()), 4)
    C = pd.read_csv(os.path.join(PROC, "ngxdol_broker_concentration.csv"))
    say(f"  broker weeks: {C.week_end.nunique()}; CR10(value) > 1.0 in {(C[C.measure=='value'].cr10 > 1.0001).sum()} weeks (NGX % basis; see LIMITATIONS)")
    stats.update(broker_weeks=int(C.week_end.nunique()),
                 cr10_value_median=round(float(C[C.measure == "value"].cr10.median()), 4),
                 cr10_volume_median=round(float(C[C.measure == "volume"].cr10.median()), 4),
                 cr10_value_gt1_weeks=int((C[C.measure == "value"].cr10 > 1.0001).sum()))

    # 8. Named spot checks for the author
    say("\n8. SPOT CHECKS (look these up in the original PDFs; see docs/VERIFY_CHECKLIST.md)")
    picks = [("2014-06-30", "DANGCEM"), ("2014-06-30", "ACCESS"), ("2016-06-20", "NESTLE"), ("2019-06-14", "MTNN"),
             ("2020-03-23", "ZENITHBANK"), ("2023-06-14", "GTCO"), ("2026-10-23", "ARADEL"), ("2026-10-23", "CHELLARAM")]
    spot = []
    for d, s in picks:
        r = D[(D.date == d) & (D.symbol == s)]
        if len(r):
            r = r.iloc[0]
            spot.append(dict(date=d, symbol=s, close=r.close, deals=r.deals, volume=r.volume, value=r.value,
                             mcap_ngn=r.mcap_ngn, board=r.board))
            say(f"  {d} {s}: close {r.close}, deals {r.deals:.0f}, volume {r.volume:,.0f}, value {r.value:,.2f}, board {r.board}")
        else:
            say(f"  {d} {s}: not found (symbol may differ that year)")
    stats["spot_checks"] = spot
    stats["version"] = "1.0.0"

    open(os.path.join(PROC, "qa_report.txt"), "w").write("\n".join(out) + "\n")
    os.makedirs(os.path.join(ROOT, "paper"), exist_ok=True)
    json.dump(stats, open(os.path.join(ROOT, "paper", "stats.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
