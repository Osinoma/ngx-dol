# Start Here: NGX-DOL

*Read this first. It explains your project in plain language. Technical words are explained in [GLOSSARY.md](GLOSSARY.md).*

## What you are building

A free, citable table of every share listed on the Nigerian Exchange, for every trading day from 30 June 2014 to late 2026: its price, how many shares traded, how many deals, the naira value, its board and sector, and (where the exchange published it) its market value. Weekly tables of the ten busiest stockbrokers come with it.

## Why it matters

Researchers who study Nigerian stocks today must either buy data from a commercial vendor or retype numbers from thousands of PDF reports. Most cannot do either, so Nigeria is missing from a lot of research on emerging markets. This project turns the exchange's own daily reports into one clean table that anyone can download and cite. It also adds ready-made measures of how easy it is to trade each stock (liquidity), which is the question most market-structure research starts from.

Think of it as turning twelve years of the exchange's printed daily newspaper into a single spreadsheet, with a record of exactly which page every number came from.

## Where the information comes from

| Source | In plain terms | What one row looks like | Link |
|---|---|---|---|
| NGX Daily Price List | The exchange's list of every share that traded that day | One stock on one day: open, high, low, close, deals, shares traded, naira value | https://ngxgroup.com/exchange/data/data-library/ |
| NGX Daily Official List (Equities) | The formal list of every listed share, traded or not | One stock on one day: board, sector, sub-sector, par value, official price | same |
| NGX Weekly Summary Statistics | The Friday bundle of weekly reports | One broker in one week: rank, shares or naira traded, % of market | same |
| NGX Daily Summary | A second daily trade record, used to double-check | One stock on one day: deals, shares, value | same |
| NGX Company Directory | Today's company profiles | One company: ISIN code, shares outstanding, listing date | https://ngxgroup.com/exchange/data/company-profile/ |

All are published on the exchange's public website. Redistribution of the derived table rests on your written permission from NGX (reference to be added at the checking step).

## What you will have at the end

- [ ] **A public project page** on GitHub (Osinoma/ngx-dol) with the parser, codebook and quality log
- [ ] **A permanent citation number (DOI)** from Zenodo for NGX-DOL v1.0
- [ ] **The dataset files**: daily stock panel, monthly liquidity panel, weekly broker table, market totals
- [ ] **A short data paper** describing the dataset, ready to submit to a data journal
- [ ] **A 60-second talk track** for explaining it to anyone

## How it connects to your work

You build settlement and market-making systems for this market. This dataset is the public, citable base layer that your other projects (and other researchers' work on Nigerian market liquidity) can be built and checked on.

## What you need to do

| Your task | When | Time |
|---|---|---|
| Create accounts (done: ORCID, GitHub, Zenodo) | Now | done |
| Confirm your NGX permission (real reference) | At the checking step | 5 min |
| Check the results using the checklist | When the draft is ready | 1 to 2 hours |
| Approve publishing | After checking | 5 min |
| Submit the data paper yourself, using the guide | After publishing | 20 min |

## The steps ahead

1. **Data collected.** Download the exchange's reports and record where each came from.
2. **Data read and combined.** Turn the PDFs into one table per report type and join them.
3. **Quality checks.** Compare totals two independent ways and flag anything odd.
4. **Liquidity measures and first figure.**
5. **Draft data paper.** Every number in it comes straight from the data.
6. **Ready for your check.** You verify, then we publish.

*You are here: step 6, ready for your check.*
