#!/usr/bin/env bash
# Rebuild NGX-DOL from scratch. Plain-language note: runs every step in order.
set -euo pipefail
cd "$(dirname "$0")"
python3 code/01_fetch.py --folders 5 10 13 1 --workers 6
python3 code/02_parse_pricelist.py
python3 code/03_parse_officiallist.py
python3 code/04_parse_weekly.py
python3 code/05_parse_dailysummary.py
python3 code/06_build.py
python3 code/07_qa.py | tail -n 25
python3 code/08_figures.py "$@"
python3 code/10_docs.py "$@"
python3 code/09_package.py
