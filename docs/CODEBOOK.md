# NGX-DOL Codebook (v1.0.0)

*Plain-language note: this file defines every column in every data file. You do not need to read it end to end; look up a column when you need it.*

Conventions: dates are `YYYY-MM-DD` (the date printed inside the NGX report, not the file title). Money is Nigerian naira (NGN). Empty cell = not available. Booleans are `True`/`False`.

Source codes: **PL** = Daily "Gainers and Price list" (PRICES1.pdf; PRICES_LIST2.pdf for market cap). **OL** = Daily Official List (Equities). **DS** = Daily Summary. **WK** = Weekly Summary Statistics (BRKR_TOPN, ACTIVITYSUMMARY). **DIR** = NGX company directory snapshot (date in `ngxdol_securities.csv`).

## ngxdol_daily.csv (one security, one trading day)

A row exists when the security is on that day's OL, or traded that day on PL, or was imputed as listed (see `universe_imputed`).

| Column | Definition | Source / transformation |
|---|---|---|
| date | Trading date | in-report date |
| symbol | NGX trading symbol as printed that day (symbols can change over time; not remapped in v1.0) | PL / OL |
| isin | ISIN from the directory snapshot, matched on current symbol; empty for delisted or renamed symbols | DIR |
| name | Security name from OL, carried within symbol | OL |
| board | Harmonised board: Premium, Main, Growth/ASeM, REIT/CEF, Non-Interest | OL board heading; else PL market-cap board |
| board_raw | Board as printed | OL / PL |
| sector, subsector | NGX sector and sub-sector headings | OL, carried within symbol |
| par | Par (nominal) value, NGN | OL "Public Quotation Price" column |
| in_official_list | Security appears on that day's OL | OL |
| traded | At least one share traded that day (False on `day_trades_missing` days, where it is unknown) | PL |
| pclose | Previous close, as printed by NGX (NGX's reference price, adjusted by NGX for corporate actions where it does so) | PL |
| open, high, low | Day's open, high, low (empty when no price movement printed) | PL |
| close | Close. PL close on traded days; OL official market price on untraded days; else carried forward | PL / OL |
| close_src | `price_list`, `official_list`, `carried_forward` | derived |
| deals | Number of deals (trades) | PL "TRADES" |
| volume | Shares traded | PL "VOLUME" |
| value | NGN value traded | PL "VALUE"; empty on `mcap_list` days |
| vwap | value / volume | derived |
| ret | Simple return. Traded days: close / pclose - 1. Other days: close / previous panel close - 1 | derived |
| ret_flag | 1 if abs(ret) > 11% (outside NGX's normal +/-10% daily band: corporate actions, relistings, or errors). Excluded from Amihud | derived |
| mcap_ngn | Market capitalisation, NGN | PL/DS "MARKET CAP(Nm)" x 1e6 (`reported`), or shares_out x close (`shares_carried`) |
| mcap_source | `reported` or `shares_carried` (implied shares carried up to 20 trading days across untraded days) | derived |
| shares_out | Implied shares outstanding = reported mcap / close, rounded to 1,000 | derived |
| turnover | volume / shares_out | derived |
| amihud | Daily Amihud ratio: abs(ret) / (value / 1e6). Unit: return per NGN million traded. Only on traded days with value > 0 and ret_flag = 0 | derived |
| zero_return | 1 if ret = 0 or not traded; empty on `day_trades_missing` days | derived |
| trade_source | `price_list` (full row) or `mcap_list` (day where NGX published only the market-cap list: close, deals, volume, no OHLC or value) | derived |
| universe_imputed | Row added because that day's OL file is missing from the archive; security was listed on the OL days before and after | derived |
| day_trades_missing | Day has an OL but no price list in the archive; trading unknown | derived |

## ngxdol_monthly.csv (one security, one calendar month)

| Column | Definition |
|---|---|
| symbol, month (`YYYY-MM`), board, sector | identifiers (last value in month) |
| days_listed | rows in the month |
| days_traded | days with trading |
| zero_return_share | mean of `zero_return` (Lesmond-Ogden-Trzcinka style zero-return proportion) |
| amihud_mean | mean of daily `amihud` |
| amihud_obs | days contributing to amihud_mean |
| volume, value_ngn, deals | monthly sums |
| turnover | sum of daily turnover |
| close_last, mcap_ngn_last | last close and market cap in month |

## ngxdol_liquidity_monthly.csv (v1.0 public release; one security, one month)

The public v1.0 release subset of `ngxdol_monthly.csv`: `symbol`, `month`, `board`, `sector`, `days_listed`, `days_traded`, `zero_return_share`, `amihud_mean`, `amihud_obs`, `turnover`, defined as above. Prices, volumes, values and market capitalisation are not included in the public file. `run_all.sh` rebuilds them.

## ngxdol_market_daily.csv (one trading day)

`listed` (securities on OL), `traded`, `deals`, `volume`, `value_ngn` (sums over equities in the panel), `mcap_ngn_reported` (sum of reported market caps; partial on days where not all securities are reported).

## ngxdol_broker_weekly.csv (one broker rank, one week, one measure)

| Column | Definition |
|---|---|
| week_start, week_end | Period printed on the NGX Broker Performance Report |
| measure | `volume` (shares) or `value` (NGN) |
| rank | 1-10 |
| broker_code, broker_name | As printed (names change over time) |
| amount | Shares or NGN traded by the broker |
| pct_share | NGX's printed % of total (NGX's basis; can sum above 100 in a few weeks, see LIMITATIONS) |

## ngxdol_broker_concentration.csv (one week, one measure)

`cr10` = sum of top-10 shares; `cr5` = top-5; `hhi_top10` = sum of squared top-10 shares (a lower bound on the full Herfindahl index, since brokers outside the top 10 are not published); `n` = brokers listed.

## ngxdol_securities.csv (one symbol)

`name`, `isin`, `board_last`, `sector_last`, `first_date`, `last_date`, `days_listed`, `days_traded`, `shares_out_snapshot` and `date_listed` (from DIR), `snapshot_date`.
