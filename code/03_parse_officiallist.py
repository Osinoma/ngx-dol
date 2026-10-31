#!/usr/bin/env python3
"""
03_parse_officiallist.py - Parse the Daily Official List (Equities).

PLAIN-LANGUAGE NOTE: The Daily Official List is the exchange's formal record of
every listed share on a given day, traded or not. It tells us which board each
stock sits on (Premium, Main, Growth/ASeM, REIT), its sector and sub-sector, its
par value and its official market price. We use it to know which stocks were
listed but did NOT trade on a day (needed for "zero-return day" measures).
You do not need to open this file.

Output (data/interim/):
  officiallist_daily.csv   date, symbol, name, board, sector, subsector, par,
                           market_price
  parse_log_officiallist.csv
"""
import csv, glob, os, re, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from nglib import RAW, INTERIM, num

import subprocess

COLS = ["date", "symbol", "name", "board", "sector", "subsector", "par", "market_price"]
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
NUMSPAN = re.compile(r"-?\d[\d,]*\.\d+")
SYM_RE = re.compile(r"^ {2,4}([A-Z0-9][A-Z0-9.&/-]{1,15})(?: +)(\S.*)$")
BOARD_RE = re.compile(r"^\s{20,}([A-Z][A-Za-z&]*) - (.+?)\s*$")
SKIP = ("Published by", "Daily Official List", "Print Date", "Copyright", "Symbol ", "Public",
        "Quotation", "Final EPS", "Ex -", "Div Sc")


def parse(text, date):
    rows, notes = [], []
    board = sector = subsector = None
    mp_end = par_end = None  # header column ends ("Market Price", "Price (N)") on this page
    last = None
    for line in text.splitlines():
        if not line.strip():
            last = None if last is None else last
            continue
        m = BOARD_RE.match(line)
        if m and "Page" not in line and len(line.strip()) < 70:
            board = m.group(2).strip(); continue
        st = line.strip()
        if st.startswith("Symbol"):
            i = line.find("Market Price")
            mp_end = i + len("Market Price") if i >= 0 else None
            j = line.find("Price (N)")
            par_end = j + len("Price (N)") if j >= 0 else None
            continue
        if any(st.startswith(k) for k in SKIP) or st.startswith("Page"):
            continue
        indent = len(line) - len(line.lstrip())
        # sector heading: one leading space, all caps, no digits
        if indent <= 2 and st.isupper() and not re.search(r"\d", st):
            sector = st; subsector = None; last = None; continue
        # sub-sector heading: deep indent, mixed case, no digits, short
        if 8 <= indent <= 20 and not re.search(r"\d", st) and not st.isupper():
            subsector = st; last = None; continue
        m = SYM_RE.match(line)
        if m and re.search(r"\d", line):
            sym, rest = m.group(1), m.group(2)
            name = re.split(r"\s{2,}", rest.strip())[0]
            spans = [(x.start(), x.end(), x.group()) for x in NUMSPAN.finditer(line)]
            par = mp = None
            if par_end is not None:
                cand = [s for s in spans if par_end - 6 <= s[1] <= par_end + 4]
                par = num(cand[0][2]) if cand else None
            elif spans:
                par = num(spans[0][2])
            if mp_end is not None:
                cand = [s for s in spans if mp_end - 6 <= s[1] <= mp_end + 8 and (par_end is None or s[1] > par_end + 4)]
                if cand:
                    mp = num(cand[0][2])
            if NUMSPAN.fullmatch(name or ""):
                name = ""
            last = dict(date=date, symbol=sym, name=name, board=board, sector=sector,
                        subsector=subsector, par=par, market_price=mp)
            rows.append(last); continue
        # continuation of a wrapped security name (text in the name column, no digits)
        if last is not None and 12 <= indent <= 22 and not re.search(r"\d", st):
            last["name"] = (last["name"] + " " + st).strip()
    return rows, notes


def work(path):
    date = DATE_RE.search(os.path.basename(path)).group(1)
    try:
        t = subprocess.run(["pdftotext", "-q", "-layout", path, "-"], capture_output=True).stdout.decode("utf-8", "replace")
        m = re.search(r"For\s+(\d{2})/(\d{2})/(\d{4})", t[:300])
        notes = []
        if m and f"{m[3]}-{m[2]}-{m[1]}" != date:
            notes.append(f"title {date} -> content {m[3]}-{m[2]}-{m[1]}")
            date = f"{m[3]}-{m[2]}-{m[1]}"
        rows, n2 = parse(t, date); notes += n2
        return date, path, rows, ("ok" if rows else "no_rows"), notes
    except Exception as e:
        return date, path, [], "error", [repr(e)]


def main():
    os.makedirs(INTERIM, exist_ok=True)
    files = sorted(glob.glob(os.path.join(RAW, "officiallist", "*.pdf")))
    seen = set()
    with Pool(max(1, os.cpu_count())) as pool, \
            open(os.path.join(INTERIM, "officiallist_daily.csv"), "w", newline="") as f1, \
            open(os.path.join(INTERIM, "parse_log_officiallist.csv"), "w", newline="") as f2:
        w1 = csv.DictWriter(f1, COLS); w1.writeheader()
        w2 = csv.writer(f2); w2.writerow(["date", "file", "status", "rows", "notes"])
        for date, path, rows, status, notes in pool.imap(work, files, chunksize=8):
            if date in seen and rows:
                status, rows = "duplicate_skipped", []
            if rows:
                seen.add(date)
            w1.writerows(rows)
            w2.writerow((date, os.path.basename(path), status, len(rows), "; ".join(notes[:5])))
    print("done", len(files))


if __name__ == "__main__":
    main()
