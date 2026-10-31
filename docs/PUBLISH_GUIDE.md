# Publish guide: NGX-DOL v1.0

*Plain-language note: the exact clicks to publish, once your checklist is done and the publish check passes. Allow 30 minutes in one sitting. If you'd rather Claude do the GitHub and Zenodo steps, create the two tokens in section 0 and paste them when asked. A token is a temporary password that lets Claude upload for you, and you can cancel it anytime.*

## Copy-ready text

**Title:** NGX-DOL: an open daily panel of the Nigerian equity market, 2014-2026
**Version:** 1.0.0
**Author:** Amhanesi, John (ORCID 0009-0003-5520-3403), Independent Researcher, New York, USA
**License:** Creative Commons Attribution 4.0 International (data); MIT (code)
**Keywords:** Nigeria; Nigerian Exchange; NGX; equity market; market microstructure; liquidity; Amihud illiquidity; frontier markets; open data
**Description (paste into Zenodo):** use the README opening paragraph *after* you have rewritten it in your own words, followed by: "Source: Nigerian Exchange Limited Data Library. v1.0 contains derived measures only; raw NGX PDFs are not included; the parser at https://github.com/Osinoma/ngx-dol rebuilds every file."

## 0. Optional: let Claude do steps 1 and 2 (5 min)

- GitHub token: https://github.com/settings/tokens/new. Note: "ngx-dol", expiry 7 days, tick **repo**. Click Generate and copy it.
- Zenodo token: https://zenodo.org/account/settings/applications/tokens/new/. Name "ngx-dol", tick **deposit:write** and **deposit:actions**. Click Create and copy it.
- Paste both into the chat when Claude asks. Revoke them afterwards on the same pages.

## 1. GitHub (10 min)

1. Go to https://github.com/new. Owner **Osinoma**, name **ngx-dol**, Public. Do **not** add a README. Click **Create repository**.
2. In Terminal, inside the project folder:
   ```
   git remote add origin https://github.com/Osinoma/ngx-dol.git
   git push -u origin main
   ```
   The repository page should now show the README.
3. Click **Releases**, then **Draft a new release**. Tag `v1.0.0`, title "NGX-DOL v1.0.0". In notes, paste "First public release. See README and docs/LIMITATIONS.md." Click **Publish release**.

## 2. Zenodo (15 min)

1. Log in at https://zenodo.org with ORCID.
2. Click **New upload**. Drag in every file from the `release/` folder: six `.csv.gz` files, `qa_report.txt`, `CODEBOOK.md`, `LIMITATIONS.md`, `README.md`, `LICENSE-DATA.md` and `SHA256SUMS.txt`.
3. Resource type **Dataset**. Paste the title, author (search your ORCID), description, license, keywords and version from the top of this guide.
4. Under **Related works**: "Is supplemented by" https://github.com/Osinoma/ngx-dol (URL).
5. Click **Preview** and check it, then click **Publish**. Copy the DOI (it looks like 10.5281/zenodo.NNNNNNN).
6. Send the DOI to Claude. It updates README, CITATION.cff, the paper and the evidence log, then pushes the change.

## 3. Data paper (20 min, after the DOI)

Target: a data-descriptor journal such as *Data in Brief* (Elsevier, open access). Check the current article processing charge and any waiver on the journal site before submitting. Alternatives: *Scientific Data* (higher fee), or a preprint on SSRN (free) first.
1. Claude reformats `paper/ngxdol_data_paper.docx` to the journal template once you choose.
2. Register on the journal's submission site, choose article type "Data Article", upload the manuscript and figures, give the Zenodo DOI as the data link, and paste the competing-interests and AI-use statements from the paper.
3. Submit, then send Claude the manuscript ID for the evidence log.

## After every step

Write the evidence row the same day (`docs/evidence_log.csv`): date, what, where, link or DOI, status. Publications not logged the day they happen are the ones that go missing later.
