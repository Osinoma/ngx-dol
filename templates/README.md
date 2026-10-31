**Status: DRAFT, not yet verified by the author.** Version {{version}}. Do not cite until released with a DOI.

# NGX-DOL: an open daily panel of the Nigerian equity market, 2014-2026

**In plain language:** NGX-DOL turns twelve years of the Nigerian Exchange's official daily reports ({{first_month_year}} to {{last_month_year}}) into an open, documented dataset covering {{symbols}} listed equities on {{trading_days_fmt}} trading days. The code rebuilds the full daily table of prices and trades directly from NGX's public reports. Version 1.0 publishes monthly liquidity measures, daily market totals and weekly broker-concentration scores. Checked against a second NGX report, the trade counts and volumes match {{recon_ds_deals_pct_int}}%.

**What this release contains:** {{release_scope}} It was built by reading the exchange's own daily and weekly reports. Each number was checked against a second NGX report: deals and shares traded agree {{recon_ds_deals_pct}}% and {{recon_ds_volume_pct}}% with the exchange's separate Daily Summary over {{recon_ds_n_fmt}} stock-days.

To the author's knowledge, no open, security-level, multi-year dataset for the Nigerian equity market exists outside paid vendors. The full panel has {{rows_daily_fmt}} security-day rows with prices, deals, volume, value, board, sector and (from {{mcap_first_reported}}) market capitalisation, plus weekly top-10 broker tables for {{broker_weeks}} weeks.

## Files (on Zenodo, DOI: [{{doi}}](https://doi.org/{{doi}}))

{{files_table}}

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

All data are derived from reports published by Nigerian Exchange Limited (NGX) in its public Data Library (https://ngxgroup.com/exchange/data/data-library/) and company directory. NGX is the source and owner of the underlying data. NGX-DOL is not produced, endorsed or verified by NGX. {{permission_text}}

## License

Code: MIT (`LICENSE`). Released derived measures and documentation: CC BY 4.0, with attribution to NGX as source (`LICENSE-DATA.md`).

## Competing interests

{{competing_interests}}

## Citation

{{author_name}} ({{year}}). *NGX-DOL: an open daily panel of the Nigerian equity market, 2014-2026* (v{{version}}) [Data set]. Zenodo. https://doi.org/{{doi}}

Maintainer: {{author_name}}, {{affiliation}}, ORCID {{orcid}}, {{email}}. Built with AI assistance (Claude) for code and drafting; every analytic decision and verification by the author.
