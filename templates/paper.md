---
title: "NGX-DOL: an open daily security-level panel of the Nigerian equity market, 2014-2026"
author: "{{author_name}} ({{affiliation}}; ORCID {{orcid}}; {{email}})"
date: "DRAFT {{build_date}}, not for circulation"
---

**DRAFT. Not verified by the author. Every number in this draft is generated from `paper/stats.json`.**

# Abstract

NGX-DOL turns twelve years of the Nigerian Exchange's official daily reports ({{first_month_year}} to {{last_month_year}}) into an open, documented dataset covering {{symbols}} listed equities on {{trading_days_fmt}} trading days. The code rebuilds the full daily table of prices and trades directly from NGX's public reports. Version 1.0 publishes monthly liquidity measures, daily market totals and weekly broker-concentration scores. Checked against a second NGX report, the trade counts and volumes match {{recon_ds_deals_pct_int}}%.

The dataset contains {{rows_daily_fmt}} security-day observations parsed from {{files_total_fmt}} NGX Data Library reports, with board, sector, par value and, from {{mcap_first_reported}}, exchange-reported market capitalisation, plus weekly top-10 broker tables for {{broker_weeks}} weeks. Derived measures are Amihud illiquidity, turnover, zero-return days and broker concentration.

# Background and motivation

Nigeria is one of Africa's largest equity markets by listings, yet security-level historical data are available mainly through commercial vendors. Liquidity in such markets is commonly studied with low-frequency proxies such as the Amihud (2002) ratio and the zero-return proportion of Lesmond, Ogden and Trzcinka (1999), which require exactly this kind of daily security-level history. NGX publishes daily and weekly reports as PDF files in its public Data Library. They are complete and official, but not machine-readable at scale. NGX-DOL converts them into a harmonised panel with a published quality log.

# Data sources

NGX-DOL uses five report families from the NGX Data Library and one directory snapshot:

| Report | Files parsed | Content used |
|---|---|---|
| Gainers and Price list (daily) | {{files_pricelist}} | OHLC, deals, volume, value; per-security market cap |
| Daily Official List, Equities | {{files_officiallist}} | listed universe, board, sector, par, official price |
| Daily Summary | {{files_dailysummary}} | independent trade record; market-cap fill |
| Weekly Summary Statistics | {{files_weekly}} | top-10 brokers by volume and value; weekly activity |
| Company directory (snapshot {{snapshot_date}}) | 1 | ISIN, shares outstanding |

# Methods

Files are listed through the Data Library's public index and downloaded with a provenance log (file, size, SHA-256, URL, date). PDFs are converted to position-preserving text with poppler `pdftotext`. Rows are parsed with column-aware rules that cover the layout changes over the twelve years. The trade date is taken from inside each report, because some files are mis-titled. The panel is the union of securities on the Official List and securities traded on the price list. Days missing an Official List have their untraded universe imputed from adjacent days and flagged. Days missing a price list are flagged, with trading left unknown. ETFs, bonds and sukuk that appear in the same reports are excluded.

Derived measures follow standard definitions. Daily Amihud illiquidity is |r|/(value in NGN million), computed on traded days with positive value and |r| <= 11%. The zero-return indicator is 1 when the return is zero or the security did not trade. Turnover is volume over implied shares outstanding. Broker concentration is CR5, CR10 and the Herfindahl index of the published top-10 shares.

# Data records

The release (Zenodo, https://doi.org/{{doi}}): {{release_scope}} A codebook, quality report and SHA-256 checksums are included. Figure 1 summarises market activity.

![Figure 1. Monthly value traded and securities listed vs. traded per day.](figures/fig1_activity.png)

# Technical validation

1. **Independent daily reconciliation.** For {{recon_ds_n_fmt}} security-days on which NGX's Daily Summary carries trade rows, deals agree in {{recon_ds_deals_pct}}%, volume in {{recon_ds_volume_pct}}% and value within NGN 1 in {{recon_ds_value_pct}}% of cases.
2. **Weekly reconciliation.** In the {{recon_wkc_weeks}} weeks where every trading day has a complete price list, summed daily volumes equal NGX's weekly activity totals exactly for {{recon_wkc_vol_exact_pct}}% of {{recon_wkc_n_fmt}} security-weeks.
3. **Range checks.** No non-positive closes and no high-below-low rows. {{ret_flag_rows}} returns exceed 11% in absolute value; these are flagged and excluded from Amihud.
4. **Coverage.** {{trading_days}} trading days, with three calendar gaps longer than five days.

Figure 2 shows the liquidity measures. The mean stock-month had zero returns on {{zr_2015_pct}}% of days in 2015 and {{zr_last_pct}}% in {{last_year}}.

![Figure 2. Zero-return days and Amihud illiquidity by year.](figures/fig2_illiquidity.png)

![Figure 3. Share of weekly trading by the ten most active brokers.](figures/fig3_broker_cr10.png)

The median top-10 broker share is {{cr10_value_pct}}% of value and {{cr10_volume_pct}}% of volume.

# Usage notes

Users should read the limitations file. In particular: per-security market cap begins in March 2016; ISINs cover currently listed issuers; symbol changes are not linked; and corporate actions are not adjusted.

# Code availability

Parser and build code (MIT): https://github.com/{{github}}/ngx-dol. Running `run_all.sh` reproduces every file and every number in this paper.

# Data availability and permissions

Derived from reports published by Nigerian Exchange Limited, which is the source and owner of the underlying data. {{permission_text}}

# Competing interests

{{competing_interests}}

# AI assistance

Code and first-draft text were produced with AI assistance (Anthropic Claude). The author made all analytic decisions, verified the data against source reports, and takes responsibility for the content.

# References

Amihud, Y. (2002). Illiquidity and stock returns: cross-section and time-series effects. *Journal of Financial Markets*, 5(1), 31-56.

Lesmond, D. A., Ogden, J. P., & Trzcinka, C. A. (1999). A new estimate of transaction costs. *Review of Financial Studies*, 12(5), 1113-1141.

Nigerian Exchange Limited. Data Library. https://ngxgroup.com/exchange/data/data-library/ (accessed 30 October 2026).
