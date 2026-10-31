#!/usr/bin/env python3
"""
02_parse_pricelist.py - Parse the daily "Gainers and Price list" archives.

PLAIN-LANGUAGE NOTE: For every trading day, NGX publishes a price list with one
line per stock that traded: yesterday's close, today's open/high/low/close, the
number of deals, the number of shares traded and their naira value. This script
reads every one of those files and writes them into one long table. From around
2019 the archive also contains a second list with each stock's market value
(market capitalisation); that is read too. You do not need to open this file.

Outputs (data/interim/):
  pricelist_daily.csv   date, symbol, pclose, oopen, open, high, low, spread_pct,
                        oclose, close, change, pct_change, deals, volume, value
  pricelist_mcap.csv    date, board, sector, subsector, sn, name, mcap_ngn_m,
                        price, pct_change, deals, volume
  parse_log_pricelist.csv  one row per file: status, rows, notes
"""
import csv, glob, os, re, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from nglib import RAW, INTERIM, pdf_text, zip_members, num, is_num

COLMAP = {"PCLOSE": "pclose", "OOPEN": "oopen", "OPEN": "open", "HIGH": "high", "LOW": "low",
          "%SPREAD": "spread_pct", "OCLOSE": "oclose", "CLOSE": "close", "CHANGE": "change",
          "%CHANGE": "pct_change", "TRADES": "deals", "DEALS": "deals", "VOLUME": "volume",
          "VALUE": "value"}
OUTCOLS = ["date", "symbol", "pclose", "oopen", "open", "high", "low", "spread_pct", "oclose",
           "close", "change", "pct_change", "deals", "volume", "value"]
MCAPCOLS = ["date", "board", "sector", "subsector", "sn", "name", "mcap_ngn_m", "price",
            "pct_change", "deals", "volume"]
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
ROW_RE = re.compile(r"^\s*(\d{1,4})\s+(\S+)\s+(.*)$")


MERGED = re.compile(r"-?\d{1,3}(?:,\d{3})*\.\d{2}")
GLUED_VOL_VAL = re.compile(r"^(\d{1,3}(?:,\d{3})+)(\d{1,3}(?:,\d{3})*\.\d{2})$")


def split_merged(toks):
    """Large prices sometimes print with no gap: '16,000.1016,000.10' -> two numbers."""
    out = []
    for t in toks:
        g = GLUED_VOL_VAL.match(t)
        if g and re.search(r",\d{4,}", t):  # '27,337,068,326191,359,391,586.20' (volume+value)
            out += [g.group(1), g.group(2)]; continue
        if t.count(".") > 1:
            parts = MERGED.findall(t)
            if "".join(parts) == t:
                out += parts; continue
        out.append(t)
    return out


def parse_prices(text, date):
    rows, notes, cols = [], [], None
    for line in text.splitlines():
        s = line.split()
        if not s:
            continue
        if s[0] == "S/N" and "VOLUME" in s:
            cols = [COLMAP.get(c) for c in s[2:]]
            if None in cols:
                notes.append("unknown header: " + " ".join(s))
                cols = None
            continue
        if cols is None:
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        toks = split_merged(m.group(3).split())
        sym = m.group(2)
        if sym.count(".") >= 1 and re.search(r"\d\.\d\d", sym):  # symbol glued to first price
            mm = re.match(r"^([A-Z][A-Z0-9]*?)(\d{1,3}(?:,\d{3})*\.\d.*)$", sym)
            if mm:
                sym = mm.group(1); toks = split_merged([mm.group(2)]) + toks
        # a symbol occasionally wraps onto a second token (rare); merge non-numeric tokens
        while toks and not is_num(toks[0]):
            sym += toks.pop(0)
        if len(toks) != len(cols):
            notes.append(f"col mismatch {sym}: {len(toks)}!={len(cols)}")
            continue
        r = dict.fromkeys(OUTCOLS)
        r["date"], r["symbol"] = date, sym
        for c, t in zip(cols, toks):
            r[c] = num(t)
        rows.append(r)
    return rows, notes


def parse_mcap(text, date):
    rows, board, sector, subsector = [], None, None, None
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        m = re.match(r"PRICES FOR (.+?) SECURITIES", s)
        if m:
            board = m.group(1).strip(); continue
        if s.startswith("S/N") and "MARKET CAP" in s:
            subsector = re.sub(r"\s+MARKET CAP.*", "", s[3:]).strip(); continue
        toks = s.split()
        if re.match(r"^\d{1,4}$", toks[0]) and len(toks) >= 7 and all(is_num(t) for t in toks[-5:]):
            r = dict(date=date, board=board, sector=sector, subsector=subsector, sn=int(toks[0]),
                     name=" ".join(toks[1:-5]), mcap_ngn_m=num(toks[-5]), price=num(toks[-4]),
                     pct_change=num(toks[-3]), deals=num(toks[-2]), volume=num(toks[-1]))
            rows.append(r); continue
        if s.isupper() and not any(ch.isdigit() for ch in s) and "PRICE" not in s:
            sector = s  # sector heading (subtotal lines carry digits)
    return rows


INNER = re.compile(r"(?:as of|For)\s+(\d{2})/(\d{2})/(\d{4})")


def inner_date(t):
    """Date printed inside the report; None if absent or implausible (NGX sometimes prints junk)."""
    m = INNER.search(t[:400])
    if not m or not (2014 <= int(m[3]) <= 2026 and 1 <= int(m[2]) <= 12 and 1 <= int(m[1]) <= 31):
        return None
    return f"{m[3]}-{m[2]}-{m[1]}"


def work(path):
    title_date = DATE_RE.search(os.path.basename(path)).group(1)
    date = title_date
    out, mc, notes, got = [], [], [], set()
    try:
        for name, b in zip_members(path):
            u = name.upper().split("/")[-1]
            if "GAIN" in u or "SUMMARY" in u:
                continue
            t = pdf_text(b)
            d_in = inner_date(t)
            if d_in and d_in != date:
                if d_in != title_date or date == title_date:
                    notes.append(f"title {title_date} -> content {d_in}")
                date = d_in
            if "MARKET CAP" in t:
                mc += parse_mcap(t, date); got.add("mcap")
            elif "S/N" in t:
                r, n = parse_prices(t, date); out += r; notes += n; got.add("prices")
        status = "ok" if out else "no_price_rows"
    except Exception as e:
        status, notes = "error", [repr(e)]
    for r in out + mc:
        r["date"] = date
    return date, path, out, mc, status, notes, sorted(got)


def main():
    os.makedirs(INTERIM, exist_ok=True)
    files = sorted(glob.glob(os.path.join(RAW, "pricelist", "*.zip")))
    seen = set()
    with Pool(max(1, os.cpu_count())) as pool, \
            open(os.path.join(INTERIM, "pricelist_daily.csv"), "w", newline="") as f1, \
            open(os.path.join(INTERIM, "pricelist_mcap.csv"), "w", newline="") as f2, \
            open(os.path.join(INTERIM, "parse_log_pricelist.csv"), "w", newline="") as f3:
        w1 = csv.DictWriter(f1, OUTCOLS); w1.writeheader()
        w2 = csv.DictWriter(f2, MCAPCOLS); w2.writeheader()
        w3 = csv.writer(f3); w3.writerow(["date", "file", "status", "price_rows", "mcap_rows", "parts", "notes"])
        for date, path, out, mc, status, notes, got in pool.imap(work, files, chunksize=8):
            if date in seen and out:  # re-uploaded duplicate for the same date: keep first
                status = "duplicate_skipped"; out, mc = [], []
            if out:
                seen.add(date)
            w1.writerows(out); w2.writerows(mc)
            w3.writerow((date, os.path.basename(path), status, len(out), len(mc), "+".join(got), "; ".join(notes[:5])))
    print("done", len(files), "files")


if __name__ == "__main__":
    main()
