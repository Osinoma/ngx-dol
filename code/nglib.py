"""
nglib.py - shared helpers for the NGX-DOL parsers.

PLAIN-LANGUAGE NOTE: small utility functions (open a zip, turn a PDF into text,
read Nigerian-format numbers). You do not need to open this file.
"""
import io, os, re, subprocess, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
INTERIM = os.path.join(ROOT, "data", "interim")
PROC = os.path.join(ROOT, "data", "processed")

NUM_RE = re.compile(r"^-?[\d,]*\.?\d+$")


def pdf_text(data: bytes, layout=True) -> str:
    """Convert PDF bytes to text with poppler's pdftotext (fast, position-preserving)."""
    args = ["pdftotext", "-q"] + (["-layout"] if layout else []) + ["-", "-"]
    return subprocess.run(args, input=data, capture_output=True).stdout.decode("utf-8", "replace")


def zip_members(path):
    """Yield (member_name, bytes) for every PDF inside a zip archive."""
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.lower().endswith(".pdf"):
                yield n, z.read(n)


def num(tok):
    """'1,234.50' -> 1234.5 ; '-' or '' -> None."""
    if tok is None:
        return None
    t = tok.strip()
    if t in ("", "-", "--"):
        return None
    t = t.replace(",", "")
    try:
        return float(t)
    except ValueError:
        return None


def is_num(tok):
    return tok == "-" or bool(NUM_RE.match(tok))
