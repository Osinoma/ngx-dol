#!/usr/bin/env python3
"""
06_build.py - Join the parsed reports into the NGX-DOL panel and compute measures.

PLAIN-LANGUAGE NOTE: This is the step that turns several separate report tables
into the finished dataset. For each trading day it takes every listed stock
(from the Official List), attaches that day's trading (from the Price List),
fills in market value where the exchange printed it, and then computes the
liquidity measures (how costly or easy each stock was to trade). It also builds
the weekly broker table and daily market totals. You do not need to open it;
the column definitions are in docs/CODEBOOK.md.

Outputs (data/processed/):
  ngxdol_daily.csv          security-day panel (main file)
  ngxdol_monthly.csv        security-month liquidity panel
  ngxdol_broker_weekly.csv  weekly top-10 broker tables + concentration
  ngxdol_market_daily.csv   daily market totals
  ngxdol_securities.csv     one row per symbol: names, first/last date, ISIN
"""
import glob, json, os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from nglib import RAW, INTERIM, PROC

VERSION = "1.0.0"
PRICE_LIMIT = 0.11   # NGX daily price band is +/-10% for most of the sample; beyond this flag
FFILL_SHARES_LIMIT = 20  # trading days to carry an implied share count across untraded days


def board_std(b):
    if not isinstance(b, str):
        return None
    u = b.upper()
    if "PREMIUM" in u: return "Premium"
    if "GROWTH" in u or "ASEM" in u: return "Growth/ASeM"
    if "REIT" in u or "REAL ESTATE INVESTMENT" in u or "CLOSE" in u: return "REIT/CEF"
    if "NON-INTEREST" in u or "NON INTEREST" in u: return "Non-Interest"
    if "MAIN" in u or u == "EQTY": return "Main"
    if "ETF" in u or "ETP" in u: return "ETP"
    return b.strip()


def load():
    P = pd.read_csv(os.path.join(INTERIM, "pricelist_daily.csv"))
    O = pd.read_csv(os.path.join(INTERIM, "officiallist_daily.csv"))
    M = pd.concat([pd.read_csv(os.path.join(INTERIM, f)).assign(src=s) for f, s in
                   (("pricelist_mcap.csv", "pricelist"), ("dailysummary_mcap.csv", "dailysummary"))
                   if os.path.exists(os.path.join(INTERIM, f))], ignore_index=True)
    return P, O, M


def map_mcap(P, M):
    """Attach a symbol to each market-cap row by matching (date, deals, volume) to the price list."""
    M = M.dropna(subset=["deals", "volume"]).drop_duplicates(["date", "name", "deals", "volume"])
    key = P[["date", "symbol", "deals", "volume"]].drop_duplicates()
    k = key.groupby(["date", "deals", "volume"]).symbol.agg(lambda s: s.iloc[0] if len(s) == 1 else None).reset_index()
    M = M.merge(k, on=["date", "deals", "volume"], how="left")
    # name -> symbol dictionary learned from unambiguous matches, used where no price row exists
    learned = (M.dropna(subset=["symbol"]).groupby("name").symbol
               .agg(lambda s: s.value_counts().index[0]))
    M["map_method"] = np.where(M.symbol.notna(), "deals_volume_match", None)
    miss = M.symbol.isna()
    M.loc[miss, "symbol"] = M.loc[miss, "name"].map(learned)
    M.loc[miss & M.symbol.notna(), "map_method"] = "name_dictionary"
    return M


def main():
    os.makedirs(PROC, exist_ok=True)
    P, O, M = load()
    P = P.drop_duplicates(["date", "symbol"])
    O = O.drop_duplicates(["date", "symbol"])
    M = map_mcap(P, M)
    Mq = M.dropna(subset=["symbol"]).sort_values("src").drop_duplicates(["date", "symbol"])

    # Days where the price list bundle had no per-security price table: rebuild trade rows
    # (close, deals, volume) from the market-cap list. Value and OHLC are unavailable there.
    p_days = set(P.date)
    fill = Mq[~Mq.date.isin(p_days)].rename(columns={"price": "close"})[["date", "symbol", "close", "deals", "volume"]]
    fill["trade_source"] = "mcap_list"
    P["trade_source"] = "price_list"
    T = pd.concat([P, fill], ignore_index=True)

    # ---- universe: listed (official list) union traded (price list) ----
    O = O.rename(columns={"board": "board_raw", "market_price": "ol_price", "name": "ol_name"})
    D = O.merge(T, on=["date", "symbol"], how="outer", indicator=True)
    D["in_official_list"] = D._merge.isin(["both", "left_only"])
    D["traded"] = D._merge.isin(["both", "right_only"]) & (D.volume.fillna(0) > 0)
    D = D.drop(columns="_merge")
    # scope: equities only. A symbol that never appears on any Daily Official List (Equities)
    # is an ETF, bond or other product that the price list also carries; exclude and log it.
    eq_boards = Mq.board.map(board_std).isin(["Premium", "Main", "Growth/ASeM", "REIT/CEF", "Non-Interest"])
    # equities only: a market-cap row on an equity board whose name is a company or trust
    # (the Non-Interest board also lists sukuk bonds and ETFs, e.g. "11.200% FGN JUN 2027")
    is_co = Mq.name.fillna("").str.contains(r"\bPLC\b|TRUST|REIT|LIMITED|FUND$", regex=True) & \
        ~Mq.name.fillna("").str.contains(r"%|SUKUK|ETF|ETP", regex=True)
    mc_eq = set(Mq.loc[eq_boards & is_co, "symbol"])
    ever = set(D.loc[D.in_official_list, "symbol"]) | mc_eq
    # board for rows with no Official List entry: take it from the market-cap list that day
    mb = Mq[eq_boards].assign(board_mc=Mq.board).set_index(["date", "symbol"]).board_mc
    D = D.join(mb, on=["date", "symbol"])
    D["board_raw"] = D.board_raw.fillna(D.board_mc)
    D = D.drop(columns="board_mc")
    ex = D[~D.symbol.isin(ever)]
    ex.groupby("symbol").agg(rows=("date", "size"), first=("date", "min"), last=("date", "max")) \
      .to_csv(os.path.join(INTERIM, "excluded_symbols.csv"))
    D = D[D.symbol.isin(ever)].copy()

    # Days with trading but no Official List file: rebuild the listed-but-untraded universe from
    # the Official List days either side (a symbol listed on both neighbours is assumed listed).
    ol_days = sorted(O.date.unique()); all_days = sorted(D.date.unique())
    ol_sets = O.groupby("date").symbol.agg(set).to_dict()
    add = []
    for d in sorted(set(all_days) - set(ol_days)):
        i = np.searchsorted(ol_days, d)
        if 0 < i < len(ol_days):
            listed = ol_sets[ol_days[i - 1]] & ol_sets[ol_days[i]]
            have = set(D.loc[D.date == d, "symbol"])
            add += [{"date": d, "symbol": s} for s in listed - have]
    A = pd.DataFrame(add)
    A["in_official_list"] = False; A["traded"] = False; A["universe_imputed"] = True
    D["universe_imputed"] = False
    D = pd.concat([D, A], ignore_index=True)
    # Days with an Official List but no price list: trading is unknown, not zero.
    trade_days = set(T.date)
    D["day_trades_missing"] = ~D.date.isin(trade_days)
    D["date"] = pd.to_datetime(D.date, format="%Y-%m-%d")
    D = D.sort_values(["symbol", "date"]).reset_index(drop=True)

    # static-ish attributes: carry within symbol
    for c in ["board_raw", "sector", "subsector", "par", "ol_name"]:
        D[c] = D.groupby("symbol")[c].transform(lambda s: s.ffill().bfill())
    D["board"] = D.board_raw.map(board_std)
    junk = D.board.isna() & ~D.traded  # heading words mis-read as symbols (logged in QA)
    D[junk].to_csv(os.path.join(INTERIM, "dropped_junk_rows.csv"), index=False)
    D = D[~junk].copy()

    for c in ["deals", "volume", "value"]:
        D.loc[~D.traded & D[c].isna() & ~D.day_trades_missing, c] = 0.0
    D["close_src"] = np.where(D.close.notna(), "price_list", np.where(D.ol_price.notna(), "official_list", None))
    D["close"] = D.close.fillna(D.ol_price)
    carried = D.close.isna()
    D["close"] = D.groupby("symbol").close.ffill()
    D.loc[carried & D.close.notna(), "close_src"] = "carried_forward"

    # returns: exchange PCLOSE as base on traded days (it is NGX's adjusted reference price);
    # otherwise the panel's own previous close.
    prev = D.groupby("symbol").close.shift(1)
    gap = D.groupby("symbol").date.diff().dt.days
    base = D.pclose.where(D.pclose.notna() & (D.trade_source == "price_list"), prev)
    D["ret"] = D.close / base - 1
    D.loc[gap > 10, "ret"] = np.where(D.pclose.notna(), D.close / D.pclose - 1, np.nan)[gap > 10]
    D["ret_flag"] = (D.ret.abs() > PRICE_LIMIT).astype(int)

    # market capitalisation and implied shares outstanding
    D = D.merge(Mq[["date", "symbol", "mcap_ngn_m", "src"]].assign(date=lambda x: pd.to_datetime(x.date)),
                on=["date", "symbol"], how="left").rename(columns={"src": "mcap_src"})
    D["mcap_ngn"] = D.mcap_ngn_m * 1e6
    D["shares_out_implied"] = (D.mcap_ngn / D.close).round(-3)
    D.loc[~(D.shares_out_implied > 0), "shares_out_implied"] = np.nan
    sh = D.groupby("symbol").shares_out_implied.transform(lambda s: s.ffill(limit=FFILL_SHARES_LIMIT))
    D["mcap_source"] = np.where(D.mcap_ngn.notna(), "reported", np.where(sh.notna(), "shares_carried", None))
    D["shares_out"] = D.shares_out_implied.fillna(sh)
    D["mcap_ngn"] = D.mcap_ngn.fillna(sh * D.close)

    # ISIN and current shares outstanding from the issuer-directory snapshot
    snap = sorted(glob.glob(os.path.join(RAW, "issuers", "companydirectory_*.json")))[-1]
    dirj = pd.DataFrame(json.load(open(snap)))
    dirj["Symbol"] = dirj.Symbol.str.strip()
    dirj = dirj.drop_duplicates("Symbol")  # NGX directory repeats a few issuers verbatim
    isin = dirj.set_index("Symbol").InternationSecIN
    D["isin"] = D.symbol.map(isin)

    # ---- liquidity measures (daily) ----
    D["vwap"] = np.where(D.volume > 0, D.value / D.volume, np.nan)
    D["turnover"] = D.volume / D.shares_out
    clean = D.traded & (D.value > 0) & (D.ret_flag == 0) & D.ret.notna()
    D["amihud"] = np.where(clean, D.ret.abs() / (D.value / 1e6), np.nan)  # |r| per NGN million
    D["zero_return"] = ((D.ret == 0) | ~D.traded).astype(float)
    D.loc[D.day_trades_missing, "zero_return"] = np.nan  # traded stays False but is flagged

    cols = ["date", "symbol", "isin", "ol_name", "board", "board_raw", "sector", "subsector", "par",
            "in_official_list", "traded", "pclose", "open", "high", "low", "close", "close_src",
            "deals", "volume", "value", "vwap", "ret", "ret_flag", "mcap_ngn", "mcap_source",
            "shares_out", "turnover", "amihud", "zero_return", "trade_source", "universe_imputed",
            "day_trades_missing"]
    D = D.rename(columns={"ol_name": "ol_name"})[cols].rename(columns={"ol_name": "name"})
    D = D.sort_values(["date", "symbol"])
    D.to_csv(os.path.join(PROC, "ngxdol_daily.csv"), index=False, date_format="%Y-%m-%d", float_format="%.15g")

    # ---- monthly panel ----
    D["month"] = D.date.dt.to_period("M").astype(str)
    g = D.groupby(["symbol", "month"])
    Mo = pd.DataFrame({
        "board": g.board.last(), "sector": g.sector.last(),
        "days_listed": g.size(), "days_traded": g.traded.sum(),
        "zero_return_share": g.zero_return.mean(),
        "amihud_mean": g.amihud.mean(), "amihud_obs": g.amihud.count(),
        "volume": g.volume.sum(), "value_ngn": g.value.sum(), "deals": g.deals.sum(),
        "turnover": g.turnover.sum(min_count=1),
        "close_last": g.close.last(), "mcap_ngn_last": g.mcap_ngn.last(),
    }).reset_index()
    Mo.to_csv(os.path.join(PROC, "ngxdol_monthly.csv"), index=False, float_format="%.15g")

    # ---- market totals ----
    Mk = D.groupby("date").agg(listed=("in_official_list", "sum"), traded=("traded", "sum"),
                               deals=("deals", "sum"), volume=("volume", "sum"), value_ngn=("value", "sum"),
                               mcap_ngn_reported=("mcap_ngn", lambda s: s[D.loc[s.index, "mcap_source"] == "reported"].sum()))
    Mk.reset_index().to_csv(os.path.join(PROC, "ngxdol_market_daily.csv"), index=False, date_format="%Y-%m-%d", float_format="%.15g")

    # ---- broker weekly + concentration ----
    B = pd.read_csv(os.path.join(INTERIM, "broker_weekly.csv")).drop_duplicates(["week_end", "measure", "rank"])
    B.to_csv(os.path.join(PROC, "ngxdol_broker_weekly.csv"), index=False)
    s = B.assign(sh=B.pct_share / 100)
    C = s.groupby(["week_start", "week_end", "measure"]).agg(
        cr10=("sh", "sum"), cr5=("sh", lambda x: x.nlargest(5).sum()),
        hhi_top10=("sh", lambda x: (x ** 2).sum()), n=("sh", "size")).reset_index()
    C.to_csv(os.path.join(PROC, "ngxdol_broker_concentration.csv"), index=False, float_format="%.15g")

    # ---- securities table ----
    S = D.groupby("symbol").agg(name=("name", "last"), isin=("isin", "last"), board_last=("board", "last"),
                                sector_last=("sector", "last"), first_date=("date", "min"), last_date=("date", "max"),
                                days_listed=("in_official_list", "sum"), days_traded=("traded", "sum")).reset_index()
    S = S.merge(dirj[["Symbol", "SharesOutstanding", "DateListed"]].rename(
        columns={"Symbol": "symbol", "SharesOutstanding": "shares_out_snapshot", "DateListed": "date_listed"}),
        on="symbol", how="left")
    S["snapshot_date"] = os.path.basename(snap)[17:27]
    S.to_csv(os.path.join(PROC, "ngxdol_securities.csv"), index=False, date_format="%Y-%m-%d")

    M.to_csv(os.path.join(INTERIM, "mcap_mapped.csv"), index=False)
    print("daily rows", len(D), "symbols", D.symbol.nunique(), "days", D.date.nunique())


if __name__ == "__main__":
    main()
