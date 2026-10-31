**Status: released 2026-10-30.** Version 1.0.0. DOI: https://doi.org/10.5281/zenodo.23823011

# NGX-DOL: an open daily panel of the Nigerian equity market, 2014-2026

**In plain language:** NGX-DOL turns twelve years of the Nigerian Exchange's official daily reports (June 2014 to October 2026) into an open, documented dataset covering 256 listed equities on 3,033 trading days. The code rebuilds the full daily table of prices and trades directly from NGX's public reports. Version 1.0 publishes monthly liquidity measures, daily market totals and weekly broker-concentration scores. Checked against a second NGX report, the trade counts and volumes match 100%.

**What this release contains:** Version 1.0 publishes the open parser and the derived measures only: a security-month liquidity panel (Amihud illiquidity, zero-return share, turnover, days traded), daily market totals, weekly broker-concentration indices (CR5, CR10, HHI of the top 10), and a securities reference table. The full security-day panel of prices and trades is not redistributed in v1.0; anyone can rebuild it from NGX's public reports with `run_all.sh`. A request to NGX for permission to redistribute the full panel is pending; if granted, it will be added as v1.1 under the same DOI. It was built by reading the exchange's own daily and weekly reports. Each number was checked against a second NGX report: deals and shares traded agree 100.0% and 100.0% with the exchange's separate Daily Summary over 42,798 stock-days.

To the author's knowledge, no open, security-level, multi-year dataset for the Nigerian equity market exists outside paid vendors. The full panel has 497,038 security-day rows with prices, deals, volume, value, board, sector and (from 2016-03-16) market capitalisation, plus weekly top-10 broker tables for 571 weeks.

## Files (on Zenodo, DOI: [10.5281/zenodo.23823011](https://doi.org/10.5281/zenodo.23823011))

| File | One row is |
|---|---|
| `ngxdol_liquidity_monthly.csv.gz` | one security in one month: Amihud, zero-return share, turnover, days listed and traded |
| `ngxdol_market_daily.csv.gz` | one trading day: securities listed and traded, total deals, volume, value (3033 rows) |
| `ngxdol_broker_concentration.csv.gz` | one week and measure: CR5, CR10, HHI of the published top 10 |
| `ngxdol_securities.csv.gz` | one security: name, ISIN, board, sector, first and last date (256 rows) |
| `qa_report.txt` | the quality report |

Every column is defined in [docs/CODEBOOK.md](docs/CODEBOOK.md). Read [docs/LIMITATIONS.md](docs/LIMITATIONS.md) before using the data.

## Rebuild it yourself

Requires Python 3.10+, `pdftotext` (poppler-utils), pandas, numpy, matplotlib.

```bash
pip install -r requirements.txt
bash run_all.sh            # download (about 9,400 files, ~40 min), parse, build, QA, figures
```

Raw NGX files are downloaded to `data/raw/` on your machine and are not redistributed. Each download is logged with its SHA-256 fingerprint in `data/raw/PROVENANCE.txt`.

| Step | Script | What it does |
|---|---|---|
| 1 | `code/01_fetch.py` | Lists and downloads the NGX Data Library folders |
| 2 | `code/02_parse_pricelist.py` | Daily price list: OHLC, deals, volume, value; per-security market cap |
| 3 | `code/03_parse_officiallist.py` | Daily Official List: full universe, board, sector, par, official price |
| 4 | `code/04_parse_weekly.py` | Weekly broker top-10 and activity summary |
| 5 | `code/05_parse_dailysummary.py` | Daily Summary, used for reconciliation and market-cap fill |
| 6 | `code/06_build.py` | Joins, harmonises, computes measures |
| 7 | `code/07_qa.py` | Quality report and `paper/stats.json` |
| 8 | `code/08_figures.py` | Figures |
| 9 | `code/09_package.py` | Release bundle with checksums |

## Source and permission

All data are derived from reports published by Nigerian Exchange Limited (NGX) in its public Data Library (https://ngxgroup.com/exchange/data/data-library/) and company directory. NGX is the source and owner of the underlying data. NGX-DOL is not produced, endorsed or verified by NGX. NGX-DOL v1.0 does not redistribute NGX's security-level daily prices or broker tables; it publishes derived measures and market aggregates, and code that downloads the original reports directly from NGX. Raw NGX PDFs are not mirrored.

## License

Code: MIT (`LICENSE`). Released derived measures and documentation: CC BY 4.0, with attribution to NGX as source (`LICENSE-DATA.md`).

## Competing interests

The author designs and operates settlement and market-making architecture for the Nigerian equity market.

## Citation

John Amhanesi (2026). *NGX-DOL: an open daily panel of the Nigerian equity market, 2014-2026* (v1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23823011

Maintainer: John Amhanesi, Independent Researcher, New York, USA, ORCID 0009-0003-5520-3403, amhanesijohn@gmail.com. Built with AI assistance (Claude) for code and drafting; every analytic decision and verification by the author.
