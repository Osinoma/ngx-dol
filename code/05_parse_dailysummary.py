#!/usr/bin/env python3
"""
05_parse_dailysummary.py - Parse the NGX "Daily Summary" reports.

PLAIN-LANGUAGE NOTE: The Daily Summary is a second, independent daily record
published by the exchange. In earlier years it lists each traded stock's deals,
shares and value; in later years it repeats the price list with each stock's
market value. We use it (1) to double-check the price list and (2) to fill
market value on days the price-list bundle omits it. You do not need to open it.

Outputs (data/interim/):
  dailysummary_trades.csv  date, board, symbol, name, deals, price, volume, value
  dailysummary_mcap.csv    same columns as pricelist_mcap.csv
  parse_log_dailysummary.csv
"""
import csv, glob, importlib, os, re, subprocess, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from nglib import RAW, INTERIM, num, is_num

pl = importlib.import_module("02_parse_pricelist")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
TCOLS = ["date", "board", "symbol", "name", "deals", "price", "volume", "value"]


def parse_trades(t, date):
    rows, eq, board = [], False, None
    for line in t.splitlines():
        if "Daily Summary (Equities)" in line:
            eq = True; continue
        if "Daily Summary (Bonds)" in line or "Daily Summary (ETP" in line:
            eq = False; continue
        b = re.search(r"Activity Summary on Board (.+)$", line)
        if b:
            board = b.group(1).strip(); continue
        if not eq:
            continue
        toks = line.split()
        if len(toks) >= 6 and all(is_num(x) for x in toks[-4:]) and not is_num(toks[-5]) \
                and "Totals" not in line and "Symbol" not in line:
            rows.append(dict(date=date, board=board, symbol=toks[-5], name=" ".join(toks[:-5]),
                             deals=num(toks[-4]), price=num(toks[-3]), volume=num(toks[-2]), value=num(toks[-1])))
    return rows


def work(path):
    date = DATE_RE.search(os.path.basename(path)).group(1)
    try:
        t = subprocess.run(["pdftotext", "-q", "-layout", path, "-"], capture_output=True).stdout.decode("utf-8", "replace")
        d_in = pl.inner_date(t)
        if d_in:
            date = d_in
        if "MARKET CAP" in t:
            return date, path, [], pl.parse_mcap(t, date), "ok_mcap"
        tr = parse_trades(t, date)
        return date, path, tr, [], ("ok_trades" if tr else "no_rows")
    except Exception as e:
        return date, path, [], [], "error " + repr(e)


def main():
    files = sorted(glob.glob(os.path.join(RAW, "dailysummary", "*.pdf")))
    seen = set()
    with Pool(max(1, os.cpu_count())) as pool, \
            open(os.path.join(INTERIM, "dailysummary_trades.csv"), "w", newline="") as f1, \
            open(os.path.join(INTERIM, "dailysummary_mcap.csv"), "w", newline="") as f2, \
            open(os.path.join(INTERIM, "parse_log_dailysummary.csv"), "w", newline="") as f3:
        w1 = csv.DictWriter(f1, TCOLS); w1.writeheader()
        w2 = csv.DictWriter(f2, pl.MCAPCOLS); w2.writeheader()
        w3 = csv.writer(f3); w3.writerow(["date", "file", "status", "trade_rows", "mcap_rows"])
        for date, path, tr, mc, status in pool.imap(work, files, chunksize=8):
            if date in seen and (tr or mc):
                status, tr, mc = "duplicate_skipped", [], []
            if tr or mc:
                seen.add(date)
            w1.writerows(tr); w2.writerows(mc)
            w3.writerow((date, os.path.basename(path), status, len(tr), len(mc)))
    print("done", len(files))


if __name__ == "__main__":
    main()
