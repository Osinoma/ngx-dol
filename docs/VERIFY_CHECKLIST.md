# Your verification checklist: NGX-DOL v1.0

*Plain-language version: before anything goes public under your name, you check it. Total time: about 1.5 to 2 hours, in one sitting. Tick each box. The publish check (`publish_gate.py`) handles the mechanical items; these are yours.*

## Part 1: Make sure the results can be rebuilt (20 to 45 min, mostly waiting)

Pick one:
- [ ] **Option A, run it yourself.** On a Mac or Linux computer with Python installed, open Terminal in the project folder and paste:
  ```
  pip install -r requirements.txt
  bash run_all.sh
  ```
  The download takes about 40 minutes. At the end the screen should show `daily rows 497038 symbols 256 days 3033`.
- [ ] **Option B, ask Claude.** In a new chat (Opus 5.5 or Fable 5), share the GitHub repository and say: "Re-run this pipeline from scratch and give me the headline numbers." Compare: 3033 trading days, 497,038 rows, 256 symbols, Daily Summary volume match 100.0%.

Then:
- [ ] Open `paper/ngxdol_data_paper.docx`. Spot-check three numbers against `paper/stats.json`. They should be identical.

## Part 2: Check the sources (15 min)

- [ ] Open https://ngxgroup.com/exchange/data/data-library/. Expand "Daily Official List (Equities)" and "Weekly Summary Statistics". Recent files should be listed.
- [ ] Open https://ngxgroup.com/terms-and-conditions/. It restricts republishing NGX content without written permission. **Confirm your NGX permission covers redistributing this derived dataset under CC BY 4.0.** If it does not, choose option 3 in Part 4.

## Part 3: Check rows by hand against the original NGX PDFs (40 min)

Each link downloads a small zip from NGX. Open it, open the PDF named `PRICES1` (or similar), and find the symbol.

**Well-known stocks**
- [ ] **Well-known stock**: `ngxdol_daily.csv`, date 2014-06-30, symbol **DANGCEM**: close 240.00, deals 32, volume 286,997, value 68,326,305.68. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/Gainers%20and%20Price%20list%20for%2030-06-2014.zip>, open PRICES1.pdf (or the 'PRICES' file), find DANGCEM. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Well-known stock**: `ngxdol_daily.csv`, date 2014-06-30, symbol **ACCESS**: close 9.55, deals 124, volume 6,705,075, value 64,309,213.65. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/Gainers%20and%20Price%20list%20for%2030-06-2014.zip>, open PRICES1.pdf (or the 'PRICES' file), find ACCESS. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Well-known stock**: `ngxdol_daily.csv`, date 2016-06-20, symbol **NESTLE**: close 794.88, deals 14, volume 189,975, value 151,007,328.00. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/Gainers%20and%20Price%20list%20for%2020-06-2016.zip>, open PRICES1.pdf (or the 'PRICES' file), find NESTLE. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Well-known stock**: `ngxdol_daily.csv`, date 2019-06-14, symbol **MTNN**: close 135.60, deals 85, volume 2,165,363, value 293,502,605.15. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/Gainers%20and%20Price%20List%20for%2014-06-2019.zip>, open PRICES1.pdf (or the 'PRICES' file), find MTNN. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Well-known stock**: `ngxdol_daily.csv`, date 2020-03-23, symbol **ZENITHBANK**: close 10.70, deals 1,517, volume 120,456,307, value 1,302,219,999.35. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/Gainers%20and%20Price%20List%20for%2023-03-2020.zip>, open PRICES1.pdf (or the 'PRICES' file), find ZENITHBANK. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Well-known stock**: `ngxdol_daily.csv`, date 2023-06-14, symbol **GTCO**: close 33.70, deals 930, volume 125,469,900, value 4,204,591,278.10. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/GAINERS%20AND%20PRICE%20LIST%20FOR%2014-06-2023.zip>, open PRICES1.pdf (or the 'PRICES' file), find GTCO. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Well-known stock**: `ngxdol_daily.csv`, date 2026-10-23, symbol **ARADEL**: close 1,405.00, deals 1,168, volume 2,999,502, value 4,201,546,421.10. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/GAINERS%20AND%20PRICE%20LIST%20FOR%2023-10-2026.zip>, open PRICES1.pdf (or the 'PRICES' file), find ARADEL. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Well-known stock**: `ngxdol_daily.csv`, date 2026-10-23, symbol **CHELLARAM**: close 9.70, deals 2, volume 12, value 119.80. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/GAINERS%20AND%20PRICE%20LIST%20FOR%2023-10-2026.zip>, open PRICES1.pdf (or the 'PRICES' file), find CHELLARAM. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___

**Extreme values (most likely to be errors)**
- [ ] **Largest value traded in the dataset**: `ngxdol_daily.csv`, date 2026-10-27, symbol **FIRSTHOLDCO**: close 155.00, deals 1,785, volume 4,876,774,621, value 416,289,664,448.55. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/GAINERS%20AND%20PRICE%20LIST%20FOR%2027-10-2026.zip>, open PRICES1.pdf (or the 'PRICES' file), find FIRSTHOLDCO. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Largest volume**: `ngxdol_daily.csv`, date 2022-05-30, symbol **UBN**: close 6.25, deals 20, volume 27,337,068,326, value 191,359,391,586.20. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/GAINERS%20AND%20PRICE%20LIST%20FOR%2030-05-2022.zip>, open PRICES1.pdf (or the 'PRICES' file), find UBN. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Highest price**: `ngxdol_daily.csv`, date 2024-08-29, symbol **AVAIF**: close 1,000,000.00, deals 4, volume 5, value 5,000,000.00. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/GAINERS%20AND%20PRICE%20LIST%20FOR%2029-08-2024.zip>, open PRICES1.pdf (or the 'PRICES' file), find AVAIF. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Most deals in one day**: `ngxdol_daily.csv`, date 2026-03-23, symbol **MTNN**: close 709.00, deals 16,576, volume 24,588,685, value 17,451,607,539.70. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/GAINERS%20AND%20PRICE%20LIST%20FOR%2023-03-2026.zip>, open PRICES1.pdf (or the 'PRICES' file), find MTNN. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Smallest value traded**: `ngxdol_daily.csv`, date 2018-05-08, symbol **UNIC**: close 0.20, deals 1, volume 1, value 0.20. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/Gainers%20and%20Price%20list%20for%2008-05-2018.zip>, open PRICES1.pdf (or the 'PRICES' file), find UNIC. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___

**Random rows**
- [ ] **Random row (seed 2026)**: `ngxdol_daily.csv`, date 2025-02-06, symbol **UBA**: close 38.00, deals 542, volume 20,448,431, value 775,568,275.45. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/GAINERS%20AND%20PRICE%20LIST%20FOR%2006-02-2025.zip>, open PRICES1.pdf (or the 'PRICES' file), find UBA. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Random row (seed 2026)**: `ngxdol_daily.csv`, date 2020-07-23, symbol **SEPLAT**: close 386.00, deals 8, volume 22,407, value 7,784,191.80. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/GAINERS%20AND%20PRICELIST%20FOR%2023-07-2020.zip>, open PRICES1.pdf (or the 'PRICES' file), find SEPLAT. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Random row (seed 2026)**: `ngxdol_daily.csv`, date 2014-12-08, symbol **MRS**: close 56.00, deals 2, volume 432, value 22,982.40. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/Gainers%20and%20Price%20list%20for%2008-12-2014.zip>, open PRICES1.pdf (or the 'PRICES' file), find MRS. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Random row (seed 2026)**: `ngxdol_daily.csv`, date 2019-10-09, symbol **BETAGLAS**: close 53.80, deals 1, volume 5, value 242.25. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/Gainers%20and%20Price%20List%20for%2009-10-2019.zip>, open PRICES1.pdf (or the 'PRICES' file), find BETAGLAS. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___
- [ ] **Random row (seed 2026)**: `ngxdol_daily.csv`, date 2021-12-03, symbol **WAPIC**: close 0.48, deals 12, volume 548,584, value 263,241.18. Open the zip at <https://doclib.ngxgroup.com/DownloadsContent/GAINERS%20AND%20PRICE%20LIST%20FOR%2003-12-2021.zip>, open PRICES1.pdf (or the 'PRICES' file), find WAPIC. The CLOSE, TRADES, VOLUME and VALUE columns should match. Match? ___

## Part 4: Your decisions (15 min)

- [ ] **NGX permission.** Option 1: paste the real reference (letter date, number, signatory) into `AUTHORS.json`. Option 2: Claude drafts a request to NGX Market Data and the release waits. Option 3: release v1.0 as code plus monthly, market and broker files only, with no stock-day prices, and say so in the README. Your choice: ___
- [ ] **Large returns.** 74 rows have daily returns above 11% and are excluded from Amihud. The largest are:
  - 2018-12-27 VALUEFUND: previous n/a, close 103.2, return +20540%
  - 2018-12-18 UHOMREIT: previous n/a, close 45.2, return +8940%
  - 2015-04-27 UNHOMES: previous n/a, close 6.4, return +1180%
  Option A: keep flagged as is (recommended). Option B: drop them from the daily file. Your choice: ___
- [ ] **2017-2018 step in Amihud illiquidity** (Figure 2b). Do you know of an NGX rule change, such as the minimum quantity needed to move a price, that explains it? If so, give the rule or notice so it can be cited in LIMITATIONS item 8. Your note: ___
- [ ] **Competing-interests wording** in `AUTHORS.json`: "The author designs and operates settlement and market-making architecture for the Nigerian equity market.". Edit to name your firm if appropriate. ___
- [ ] **"No open dataset exists" claim.** Search Google Scholar, Kaggle and GitHub for "Nigerian Stock Exchange daily data". Keep the claim only if nothing comparable turns up. ___

## Part 5: Before it goes public (20 min)

- [ ] Rewrite the README opening paragraph and the paper abstract in your own words (Claude can do it with you line by line).
- [ ] Name, ORCID 0009-0003-5520-3403, affiliation and email are correct in `AUTHORS.json`.
- [ ] You have read `docs/LIMITATIONS.md` and agree with it.
- [ ] Claude re-runs with `--final` and `publish_gate.py` passes.
- [ ] Evidence log row written on release day.

**When every box is ticked, tell Claude in your own words that you have checked the package and approve publishing.**
