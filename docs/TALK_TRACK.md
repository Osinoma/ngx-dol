# Talk track: NGX-DOL

*Plain-language note: what to say when someone asks what you built. Every number matches the verified data. Practise it out loud once.*

## 60 seconds

Researchers who want to study the Nigerian stock market hit a wall. The history exists only as thousands of PDF reports on the exchange's website, or behind paid data vendors. So I built NGX-DOL: a free, citable toolkit and dataset of every listed Nigerian share, every trading day from 2014 to 2026. That's 3033 days and about half a million stock-day records. The code rebuilds the full table, and the published release carries the liquidity measures, market totals and broker-concentration scores.

I checked it against a second set of the exchange's own reports, and the trades and volumes match 100.0 percent. It shows, for example, that on a typical day 56 percent of stock-days still see no price change, down from 76 percent in 2015.

The code is open, so anyone can rebuild or extend it. It's published on Zenodo with a permanent DOI, so other researchers, regulators and market operators can cite it and build on it.

## Two sentences

I turned twelve years of the Nigerian Exchange's official PDF reports into an open, citable daily dataset of every listed Nigerian stock, the first of its kind as far as I know. It is checked against the exchange's own records and comes with ready-made liquidity measures for research and market-structure work.

## Likely questions

**Is it legal to share?** Version 1.0 shares only the code and derived measures, such as liquidity ratios and market totals, not the exchange's daily price tables. It credits NGX as the source. I've asked NGX for permission to publish the full daily table as well.

**How do you know it's accurate?** Every row was cross-checked against a second, independent NGX report. Deals and volumes agree 100.0%, and the remaining gaps are documented in a public quality report.

**Why does it matter for your work?** I build settlement and market-making systems for this market. A trusted, open baseline of liquidity lets anyone measure whether market-structure changes actually help.
