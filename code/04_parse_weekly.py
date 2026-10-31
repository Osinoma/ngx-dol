#!/usr/bin/env python3
"""
04_parse_weekly.py - Parse the Weekly Summary Statistics archives.

PLAIN-LANGUAGE NOTE: Every Friday NGX publishes a bundle of weekly reports. We
read two of them: (1) the Broker Performance Report, which lists the ten
stockbroking firms that traded the most that week, by number of shares and by
naira value, with each firm's percentage share; and (2) the weekly Activity
Summary, which gives each stock's deals, shares traded and value for the week
(used to cross-check the daily data). You do not need to open this file.

Outputs (data/interim/):
  broker_weekly.csv     week_start, week_end, measure (volume|value), rank,
                        broker_code, broker_name, amount, pct_share
  activity_weekly.csv   week_start, week_end, board, symbol, name, deals, price,
                        volume, value     (equities only)
  parse_log_weekly.csv
"""
import csv, glob, os, re, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from nglib import RAW, INTERIM, pdf_text, zip_members, num, is_num

D = r"(\d{2})/(\d{2})/(\d{4})"
PERIOD_RE = re.compile(r"Start Date\s+" + D + r"\s+through End Date\s+" + D)
ACT_RE = re.compile(r"Activity Summary from\s+" + D + r"\s+to\s+" + D)
FDATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
BRK_ROW = re.compile(r"^\s*(\d{1,2})\s+([A-Z0-9&]{2,8})\s+(.+?)\s{2,}([\d,]+(?:\.\d+)?)\s+([\d.]+)\s*$")
BCOLS = ["week_start", "week_end", "measure", "rank", "broker_code", "broker_name", "amount", "pct_share"]
ACOLS = ["week_start", "week_end", "board", "symbol", "name", "deals", "price", "volume", "value"]


def iso(m, k):
    return f"{m.group(k+2)}-{m.group(k+1)}-{m.group(k)}"


def parse_brokers(t):
    m = PERIOD_RE.search(t)
    ws, we = (iso(m, 1), iso(m, 4)) if m else (None, None)
    rows, measure = [], None
    for line in t.splitlines():
        if "Top 10 Brokers by Volume" in line:
            measure = "volume"; continue
        if "Top 10 Brokers by Value" in line:
            measure = "value"; continue
        r = BRK_ROW.match(line)
        if r and measure:
            rows.append(dict(week_start=ws, week_end=we, measure=measure, rank=int(r[1]),
                             broker_code=r[2], broker_name=r[3].strip(), amount=num(r[4]),
                             pct_share=num(r[5])))
    return rows


def parse_activity(t):
    m = ACT_RE.search(t)
    ws, we = (iso(m, 1), iso(m, 4)) if m else (None, None)
    rows, equities, board = [], False, None
    for line in t.splitlines():
        if "Activity Summary (Equities)" in line:
            equities = True; continue
        if "Activity Summary (Bonds)" in line or "Activity Summary (ETP" in line:
            equities = False; continue
        b = re.search(r"Activity Summary on Board (.+)$", line)
        if b:
            board = b.group(1).strip(); continue
        if not equities:
            continue
        toks = line.split()
        if len(toks) >= 6 and all(is_num(x) for x in toks[-4:]) and not is_num(toks[-5]) \
                and "Totals" not in line and "Symbol" not in line:
            rows.append(dict(week_start=ws, week_end=we, board=board, symbol=toks[-5],
                             name=" ".join(toks[:-5]), deals=num(toks[-4]), price=num(toks[-3]),
                             volume=num(toks[-2]), value=num(toks[-1])))
    return rows


def work(path):
    b_rows, a_rows, notes = [], [], []
    try:
        for name, data in zip_members(path):
            u = name.upper().split("/")[-1]
            if ("BRKR" in u or "BROKER" in u) and not b_rows:
                b_rows += parse_brokers(pdf_text(data))
            elif "ACTIVITY" in u and not a_rows:  # some bundles carry the report twice
                a_rows += parse_activity(pdf_text(data))
        status = "ok" if b_rows else "no_broker_rows"
    except Exception as e:
        status, notes = "error", [repr(e)]
    return path, b_rows, a_rows, status, notes


def main():
    os.makedirs(INTERIM, exist_ok=True)
    files = sorted(glob.glob(os.path.join(RAW, "weekly", "*.zip")))
    with Pool(max(1, os.cpu_count())) as pool, \
            open(os.path.join(INTERIM, "broker_weekly.csv"), "w", newline="") as f1, \
            open(os.path.join(INTERIM, "activity_weekly.csv"), "w", newline="") as f2, \
            open(os.path.join(INTERIM, "parse_log_weekly.csv"), "w", newline="") as f3:
        w1 = csv.DictWriter(f1, BCOLS); w1.writeheader()
        w2 = csv.DictWriter(f2, ACOLS); w2.writeheader()
        w3 = csv.writer(f3); w3.writerow(["file", "status", "broker_rows", "activity_rows", "notes"])
        seen = set()
        for path, b, a, status, notes in pool.imap(work, files, chunksize=4):
            wk = (b or a or [{}])[0].get("week_end")
            if wk and wk in seen:  # NGX re-uploaded the same week's bundle: keep the first
                status, b, a = "duplicate_skipped", [], []
            elif wk:
                seen.add(wk)
            w1.writerows(b); w2.writerows(a)
            w3.writerow([os.path.basename(path), status, len(b), len(a), "; ".join(notes)])
    print("done", len(files))


if __name__ == "__main__":
    main()
