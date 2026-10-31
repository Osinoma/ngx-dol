#!/usr/bin/env python3
"""
01_fetch.py - Download the NGX Data Library files that NGX-DOL is built from.

PLAIN-LANGUAGE NOTE: This script visits the Nigerian Exchange's public Data
Library and saves a private local copy of each daily and weekly report. You do
not need to open it. Raw files stay on the machine that runs the script; they
are NOT redistributed with the dataset. Every download is logged (file name,
size, fingerprint, web address, date) in data/raw/PROVENANCE.txt.

Folders used (NGX SharePoint list "DownloadsContent", FolderName/Id):
   5  Gainers and Price list (zip; PRICES1.pdf = daily per-security price list,
      PRICES_LIST2.pdf = per-security market cap, later years)
  10  Daily Official List - Equities (pdf; full listed universe, board, sector)
  13  Weekly Summary Statistics (zip; broker top-10, weekly activity, period stats)
   1  Daily Summary (pdf; market totals, used for reconciliation QA)
   7  Market Capitalization (pdf; board/sector capitalisation, used for QA)

Usage:
  python code/01_fetch.py                 # all folders, full history
  python code/01_fetch.py --folders 5 10  # subset
  python code/01_fetch.py --start 2014-06-30 --end 2014-12-31
Idempotent: files already present with a provenance record are skipped.
"""
import argparse, concurrent.futures as cf, datetime as dt, hashlib, os, re, sys, time
import urllib.parse, urllib.request, xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
API = ("https://doclib.ngxgroup.com/_api/Web/Lists/GetByTitle('DownloadsContent')/items"
       "?$select=Title,EncodedAbsUrl,Created&$filter=FolderName/Id%20eq%20{fid}"
       "&$orderby=Created%20asc&$top=5000")
FOLDERS = {5: "pricelist", 10: "officiallist", 13: "weekly", 1: "dailysummary", 7: "mktcap"}
NS = {"a": "http://www.w3.org/2005/Atom",
      "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
      "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"}
UA = {"User-Agent": "NGX-DOL research parser (open academic dataset; contact in README)"}
DATE_RE = re.compile(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})")


def get(url, tries=4):
    for k in range(tries):
        try:
            req = urllib.request.Request(urllib.parse.quote(url, safe=":/%?=&$(),'"), headers=UA)
            return urllib.request.urlopen(req, timeout=120).read()
        except Exception as e:  # network hiccup: back off and retry
            if k == tries - 1:
                raise
            time.sleep(2 ** k * 2)


def listing(fid):
    """Return [(created, title, url, date)] for one Data Library folder."""
    url, rows = API.format(fid=fid), []
    while url:
        x = ET.fromstring(get(url))
        for e in x.findall("a:entry", NS):
            p = e.find(".//m:properties", NS)
            t = (p.find("d:Title", NS).text or "").replace(" ", " ").strip()
            m = DATE_RE.search(t)
            d = dt.date(int(m[3]), int(m[2]), int(m[1])).isoformat() if m else ""
            rows.append((p.find("d:Created", NS).text, t, p.find("d:EncodedAbsUrl", NS).text, d))
        nx = [l.get("href") for l in x.findall("a:link", NS) if l.get("rel") == "next"]
        url = nx[0] if nx else None
    return rows


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folders", type=int, nargs="*", default=list(FOLDERS))
    ap.add_argument("--start", default="2014-01-01")
    ap.add_argument("--end", default="2026-12-31")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)
    prov_path = os.path.join(RAW, "PROVENANCE.txt")
    done = set()
    if os.path.exists(prov_path):
        done = {l.split(" | ")[1] for l in open(prov_path, encoding="utf-8") if " | " in l}
    today = dt.date.today().isoformat()

    for fid in a.folders:
        kind = FOLDERS[fid]
        rows = listing(fid)
        # catalogue of everything NGX lists, kept even if we skip some files
        with open(os.path.join(RAW, f"catalogue_{kind}.tsv"), "w", encoding="utf-8") as f:
            f.write("created\ttitle\turl\tdate\n")
            for r in rows:
                f.write("\t".join(r) + "\n")
        todo = []
        for created, title, url, d in rows:
            if not d or not (a.start <= d <= a.end):
                continue
            ext = os.path.splitext(urllib.parse.unquote(url))[1].lower() or ".bin"
            name = f"{kind}_{d}{ext}"
            # duplicates (re-uploads for the same date) get a suffix
            n = 2
            while name in {t[0] for t in todo}:
                name = f"{kind}_{d}_v{n}{ext}"; n += 1
            todo.append((name, url))
        os.makedirs(os.path.join(RAW, kind), exist_ok=True)
        todo = [t for t in todo if t[0] not in done]
        print(f"[{kind}] {len(rows)} listed, {len(todo)} to fetch", flush=True)

        def fetch(t):
            name, url = t
            b = get(url)
            open(os.path.join(RAW, kind, name), "wb").write(b)
            return f"{today} | {name} | {len(b)} bytes | sha256:{sha256(b)} | {url} | discovered via SharePoint REST folder {fid}"

        with cf.ThreadPoolExecutor(a.workers) as ex, open(prov_path, "a", encoding="utf-8") as log:
            for i, fut in enumerate(cf.as_completed([ex.submit(fetch, t) for t in todo])):
                try:
                    log.write(fut.result() + "\n"); log.flush()
                except Exception as e:
                    print("FAIL", e, file=sys.stderr)
                if i % 200 == 0:
                    print(f"  [{kind}] {i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
