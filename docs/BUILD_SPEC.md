# Build spec: NGX-DOL v1.0

*Plain-language note: the one-page plan the build followed. The right-hand notes say what each line means for you.*

| Field | Spec | What it means for you |
|---|---|---|
| PROJECT | NGX-DOL. Archetype: open dataset, plus a data-descriptor paper | A citable dataset first, with a short paper describing it |
| QUESTION | What did trading in every listed Nigerian equity look like each day, 2014-2026, and how liquid was it? | The one sentence the dataset answers |
| SOURCES | NGX Data Library (ngxgroup.com/exchange/data/data-library/), SharePoint folders 5, 10, 13 and 1, accessed 30 Oct 2026; NGX company directory API snapshot, 30 Oct 2026. Terms: NGX T&C restrict republication without written permission | All from the exchange; redistribution rests on your NGX permission |
| UNIT | Security-day (main); security-month; broker-week; market-day | Each row of the main file is one stock on one day |
| MEASURES | OHLC, deals, volume, value (as printed); return; market cap (reported, from Mar 2016); implied shares; turnover; Amihud; zero-return; CR5, CR10, HHI-top10 | Standard liquidity measures researchers expect |
| OUTPUTS | 6 gzip CSVs, CODEBOOK, LIMITATIONS, qa_report, 3 figures, data paper (md + docx), talk track | What goes on Zenodo and GitHub |
| VENUES | GitHub (code), Zenodo (data + DOI), then a data journal (Data in Brief or similar) | Code public, data citable, then a peer-reviewed paper |
| VERIFY POINTS | NGX permission; flagged returns; 2018 Amihud step; competing-interests text; novelty claim; hand checks of 18 rows | Decisions only you can make |
| LICENSE | Code MIT; data and docs CC BY 4.0 with NGX attribution, subject to NGX permission | Anyone may reuse, with credit |
| ASSUMPTIONS | Equities only (ETFs, bonds and sukuk excluded); symbols not linked across renames in v1.0 | Scope choices stated up front |
