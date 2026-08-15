"""
backend/ingestion/parser.py
===========================
PHASE 1 — Data Ingestion.  Owner: Member 1 (+ Member 2 pairing).

Reads a Screener.in Excel export and returns clean, predictable Pandas
DataFrames that every other module in the project consumes.

THE ONLY PUBLIC FUNCTION ANYONE ELSE SHOULD CALL:

    from backend.ingestion.parser import parse_screener_excel
    data = parse_screener_excel("tests/sample_data/TCS.xlsx")

WHAT YOU GET BACK (this is the contract — do not change key names
without telling Members 2, 3, 4, 5, 6):

    {
      "company_name":  "TATA CONSULTANCY SERVICES LTD",
      "source_file":   "TCS.xlsx",
      "sheets_found":  ["Profit & Loss", "Quarters", ...],
      "fiscal_years":  ["FY2017", ..., "FY2026"],
      "quarter_labels":["Q4FY24", ..., "Q1FY27"],

      "pl":            DataFrame  rows=line items, cols=FY2017..FY2026
      "pl_projections":DataFrame  rows=line items, cols=Trailing/Best Case/Worst Case
      "pl_reported":   DataFrame  Screener's OWN ratios (Dividend Payout, OPM)
      "quarters":      DataFrame  rows=line items, cols=Q4FY24..Q1FY27
      "bs":            DataFrame  rows=line items, cols=FY2017..FY2026
      "cf":            DataFrame  rows=line items, cols=FY2017..FY2026
      "meta":          dict       number_of_shares, face_value, current_price, market_cap
      "extras":        DataFrame  Dividend Amount, Cash & Bank, share counts (from Data Sheet)
    }

DESIGN RULES WE FOLLOW HERE:
  1. This file ONLY reads and cleans. It never computes a ratio and never
     judges whether a number is right. That is validator.py and ratios.py.
  2. Numbers come out as floats. Missing cells come out as NaN, never as
     the string "NaN" and never as 0 (0 is a real value, absence is not).
  3. Row labels are normalised to a canonical name so Members 2/3/4 can
     write df.loc["Net Profit"] and never worry about "Net profit" vs
     "NET PROFIT" vs a trailing space.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List

import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

# In every Screener statement sheet the layout is:
#   row 0 -> company name in column A
#   row 1 -> blank
#   row 2 -> "Narration" + the date columns   <-- this is the real header
HEADER_ROW = 2

STATEMENT_SHEETS = {
    "pl": "Profit & Loss",
    "quarters": "Quarters",
    "bs": "Balance Sheet",
    "cf": "Cash Flow",
}
DATA_SHEET = "Data Sheet"

# Columns on the P&L that are FORECASTS, not history. They must never reach
# the validator — "Tax" in these columns is a *rate* (0.246) not an amount,
# so validating them would produce garbage failures.
PROJECTION_COLUMNS = ["Trailing", "Best Case", "Worst Case"]

# Screener writes the same concept with different casing across sheets.
# We map everything to ONE canonical spelling used by the whole codebase.
CANONICAL_LABELS = {
    "sales": "Sales",
    "expenses": "Expenses",
    "operating profit": "Operating Profit",
    "other income": "Other Income",
    "depreciation": "Depreciation",
    "interest": "Interest",
    "profit before tax": "Profit Before Tax",
    "tax": "Tax",
    "net profit": "Net Profit",
    "eps": "EPS",
    "price to earning": "Price to Earning",
    "price": "Price",
    "dividend payout": "Dividend Payout",
    "opm": "OPM",
    "equity share capital": "Equity Share Capital",
    "reserves": "Reserves",
    "borrowings": "Borrowings",
    "other liabilities": "Other Liabilities",
    "net block": "Net Block",
    "capital work in progress": "Capital Work in Progress",
    "investments": "Investments",
    "other assets": "Other Assets",
    "working capital": "Working Capital",
    "debtors": "Debtors",
    "receivables": "Debtors",
    "inventory": "Inventory",
    "debtor days": "Debtor Days",
    "inventory turnover": "Inventory Turnover",
    "return on equity": "Return on Equity",
    "return on capital emp": "Return on Capital Employed",
    "cash from operating activity": "Cash from Operating Activity",
    "cash from investing activity": "Cash from Investing Activity",
    "cash from financing activity": "Cash from Financing Activity",
    "net cash flow": "Net Cash Flow",
    "dividend amount": "Dividend Amount",
    "cash & bank": "Cash & Bank",
    "no. of equity shares": "No. of Equity Shares",
    "adjusted equity shares in cr": "Adjusted Equity Shares in Cr",
    "raw material cost": "Raw Material Cost",
    "change in inventory": "Change in Inventory",
    "power and fuel": "Power and Fuel",
    "other mfr. exp": "Other Mfr. Exp",
    "employee cost": "Employee Cost",
    "selling and admin": "Selling and Admin",
    "other expenses": "Other Expenses",
}


class ParserError(Exception):
    """Raised when the uploaded file is not a usable Screener export."""


# ─────────────────────────────────────────────────────────────────────────────
# SMALL HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _canonical(label: Any) -> str | None:
    """'  Net profit ' -> 'Net Profit'.  Junk/blank -> None."""
    if label is None or (isinstance(label, float) and pd.isna(label)):
        return None
    text = re.sub(r"\s+", " ", str(label)).strip()
    if not text or text.lower() == "nan":
        return None
    return CANONICAL_LABELS.get(text.lower(), text)


def _fiscal_year_label(value: Any) -> str:
    """
    Timestamp('2026-03-31') -> 'FY2026'.

    Indian companies close their books on 31 March, so the year printed on
    the column IS the fiscal year. Anything we cannot parse as a date is
    returned as a plain trimmed string (that is how 'Trailing', 'Best Case'
    and 'Worst Case' survive).
    """
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return re.sub(r"\s+", " ", str(value)).strip()
    return f"FY{ts.year}"


def _quarter_label(value: Any) -> str:
    """
    Timestamp('2024-06-30') -> 'Q1FY25'.

    Indian fiscal quarters:  Apr-Jun = Q1, Jul-Sep = Q2,
                             Oct-Dec = Q3, Jan-Mar = Q4.
    A quarter ending in Jan/Feb/Mar belongs to the fiscal year that carries
    that calendar year's number; every other quarter belongs to the NEXT one.
    Getting this right is what makes Member 1's cross_sheet_tie() work —
    four quarters labelled FY25 must add up to the FY2025 annual column.
    """
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return re.sub(r"\s+", " ", str(value)).strip()

    month = ts.month
    if month <= 3:                       # Jan, Feb, Mar
        quarter, fy = 4, ts.year
    elif month <= 6:                     # Apr, May, Jun
        quarter, fy = 1, ts.year + 1
    elif month <= 9:                     # Jul, Aug, Sep
        quarter, fy = 2, ts.year + 1
    else:                                # Oct, Nov, Dec
        quarter, fy = 3, ts.year + 1
    return f"Q{quarter}FY{str(fy)[-2:]}"


def _to_number(value: Any) -> float:
    """Anything -> float, with unparseable junk becoming NaN (never a crash)."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return float("nan")
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("₹", "")
    if text in ("", "-", "--", "nan", "NaN", "None"):
        return float("nan")
    if text.startswith("(") and text.endswith(")"):     # (123) means -123
        text = "-" + text[1:-1]
    text = text.rstrip("%")
    try:
        return float(text)
    except ValueError:
        return float("nan")


def _dedupe_index(labels: List[str]) -> List[str]:
    """
    The Balance Sheet has TWO rows literally called 'Total' — one closing the
    liabilities block, one closing the assets block. Pandas would let both
    exist and then df.loc['Total'] returns a DataFrame instead of a Series,
    which silently breaks arithmetic downstream. We name them explicitly.
    """
    seen: Dict[str, int] = {}
    out: List[str] = []
    for label in labels:
        if label not in seen:
            seen[label] = 0
            out.append(label)
        else:
            seen[label] += 1
            if label == "Total":
                # first Total = liabilities side, second = assets side
                out.append("Total Assets")
                out[out.index("Total")] = "Total Liabilities"
            else:
                out.append(f"{label} ({seen[label] + 1})")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# CORE SHEET READER
# ─────────────────────────────────────────────────────────────────────────────

def _read_statement_sheet(xls: pd.ExcelFile, sheet_name: str, label_fn,
                          drop_empty_rows: bool = True) -> pd.DataFrame:
    """
    Turn one Screener statement sheet into a tidy DataFrame.

    rows    = line item names (canonical)
    columns = FY2017..FY2026  (or Q4FY24..Q1FY27 for the Quarters sheet)
    values  = floats

    drop_empty_rows=False keeps divider rows like 'RATIOS:' that carry a
    label but no numbers. The P&L reader needs them to know where the
    statement ends and Screener's own ratio block begins.
    """
    raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
    if raw.shape[0] <= HEADER_ROW:
        raise ParserError(f"Sheet '{sheet_name}' is too short to be a Screener export.")

    header = raw.iloc[HEADER_ROW]
    body = raw.iloc[HEADER_ROW + 1:].reset_index(drop=True)

    row_labels = [_canonical(v) for v in body.iloc[:, 0]]
    column_names = [label_fn(v) for v in header[1:]]

    # Filter rows POSITIONALLY, before touching the index. Assigning a list
    # containing None to df.index makes pandas coerce it to NaN, and NaN is
    # not None — so an `is not None` test on the index silently keeps every
    # junk row. The Screener P&L has a floating "TRENDS:" block in its lower
    # right corner whose rows carry no label; this is what removes it.
    keep_rows = [i for i, label in enumerate(row_labels) if label is not None]

    frame = body.iloc[keep_rows, 1:].copy()
    frame.columns = column_names
    frame.index = _dedupe_index([row_labels[i] for i in keep_rows])

    # Drop spacer columns (blank header).
    frame = frame[[c for c in frame.columns if c and c.lower() != "nan"]]
    frame = frame.map(_to_number)

    if drop_empty_rows:
        frame = frame.dropna(how="all")
    frame.index.name = "Line Item"
    return frame


def _split_pl(pl_raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    The P&L sheet is really three tables stacked on top of each other:

        Sales ... Price          <- the actual statement    (we validate this)
        RATIOS:                  <- a divider row
        Dividend Payout, OPM     <- Screener's OWN ratios   (we RE-compute these
                                    ourselves and compare — never trust them)

    and three of its columns (Trailing / Best Case / Worst Case) are
    forecasts rather than history.

    Returns (statement, projections, reported_ratios).
    """
    labels = list(pl_raw.index)

    # Preferred: split on Screener's own divider row.
    if "RATIOS:" in labels:
        cut = labels.index("RATIOS:")
    else:
        # Fallback for exports that omit the divider: cut at the first row we
        # recognise as one of Screener's pre-computed ratios.
        ratio_rows = [labels.index(name)
                      for name in ("Dividend Payout", "OPM") if name in labels]
        cut = min(ratio_rows) if ratio_rows else len(labels)

    statement_all = pl_raw.iloc[:cut]
    reported = pl_raw.iloc[cut + 1:] if cut < len(labels) else pl_raw.iloc[0:0]

    history_cols = [c for c in pl_raw.columns if c not in PROJECTION_COLUMNS]
    forecast_cols = [c for c in pl_raw.columns if c in PROJECTION_COLUMNS]

    statement = statement_all[history_cols].dropna(how="all")
    projections = statement_all[forecast_cols].dropna(how="all")
    reported_ratios = reported[history_cols].dropna(how="all")

    return statement, projections, reported_ratios


# ─────────────────────────────────────────────────────────────────────────────
# DATA SHEET (different shape — it is a stack of labelled blocks)
# ─────────────────────────────────────────────────────────────────────────────

def _read_data_sheet(xls: pd.ExcelFile) -> tuple[Dict[str, Any], pd.DataFrame]:
    """
    The Data Sheet is not a table, it is sections separated by header rows
    (META, PROFIT & LOSS, BALANCE SHEET, CASH FLOW:, DERIVED:). We only need
    two things out of it that the other sheets do NOT contain:

      meta   -> share count, face value, price, market cap
      extras -> Dividend Amount, Cash & Bank, No. of Equity Shares
                (needed for Dividend Payout and for the EPS cross-check)
    """
    raw = pd.read_excel(xls, sheet_name=DATA_SHEET, header=None)

    meta: Dict[str, Any] = {}
    meta_keys = {
        "number of shares": "number_of_shares",
        "face value": "face_value",
        "current price": "current_price",
        "market capitalization": "market_capitalization",
    }
    for _, row in raw.iterrows():
        key = str(row.iloc[0]).strip().lower()
        if key in meta_keys:
            meta[meta_keys[key]] = _to_number(row.iloc[1])

    # Find the annual date row so we can label the extras columns.
    year_columns: List[str] = []
    for _, row in raw.iterrows():
        if str(row.iloc[0]).strip().lower() == "report date":
            candidate = [_fiscal_year_label(v) for v in row[1:] if not pd.isna(v)]
            if candidate and candidate[0].startswith("FY"):
                year_columns = candidate
                break

    wanted = {"dividend amount", "cash & bank", "no. of equity shares",
              "adjusted equity shares in cr"}
    rows: Dict[str, List[float]] = {}
    for _, row in raw.iterrows():
        key = str(row.iloc[0]).strip().lower()
        if key in wanted and key not in rows:
            rows[_canonical(row.iloc[0])] = [
                _to_number(v) for v in row[1:1 + len(year_columns)]
            ]

    extras = pd.DataFrame(rows).T if rows else pd.DataFrame()
    if not extras.empty:
        extras.columns = year_columns[:extras.shape[1]]
        extras.index.name = "Line Item"

    return meta, extras


# ─────────────────────────────────────────────────────────────────────────────
# THE PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def parse_screener_excel(filepath: str) -> Dict[str, Any]:
    """
    Parse a Screener.in Excel export into clean DataFrames.

    Raises ParserError with a human-readable message if the file is not a
    Screener export — Member 3 should catch this and return HTTP 400 so the
    user sees "this doesn't look like a Screener file" instead of a 500.
    """
    if not os.path.exists(filepath):
        raise ParserError(f"File not found: {filepath}")

    try:
        xls = pd.ExcelFile(filepath)
    except Exception as exc:
        raise ParserError(f"Could not open '{filepath}' as an Excel file: {exc}") from exc

    present = set(xls.sheet_names)
    required = set(STATEMENT_SHEETS.values())
    missing = required - present
    if missing:
        raise ParserError(
            "This does not look like a Screener export. "
            f"Missing sheet(s): {sorted(missing)}. Found: {sorted(present)}"
        )

    company_name = _read_company_name(xls)

    # Keep empty rows here: the 'RATIOS:' divider has a label but no numbers,
    # and _split_pl needs it to find where the statement ends.
    pl_raw = _read_statement_sheet(xls, "Profit & Loss", _fiscal_year_label,
                                   drop_empty_rows=False)
    pl, pl_projections, pl_reported = _split_pl(pl_raw)

    quarters = _read_statement_sheet(xls, "Quarters", _quarter_label)
    bs = _read_statement_sheet(xls, "Balance Sheet", _fiscal_year_label)
    cf = _read_statement_sheet(xls, "Cash Flow", _fiscal_year_label)

    meta, extras = ({}, pd.DataFrame())
    if DATA_SHEET in present:
        meta, extras = _read_data_sheet(xls)

    return {
        "company_name": company_name,
        "source_file": os.path.basename(filepath),
        "sheets_found": list(xls.sheet_names),
        "fiscal_years": [c for c in pl.columns if str(c).startswith("FY")],
        "quarter_labels": list(quarters.columns),
        "pl": pl,
        "pl_projections": pl_projections,
        "pl_reported": pl_reported,
        "quarters": quarters,
        "bs": bs,
        "cf": cf,
        "meta": meta,
        "extras": extras,
    }


def _read_company_name(xls: pd.ExcelFile) -> str:
    """Company name lives in A1 of the statement sheets, B1 of the Data Sheet."""
    if DATA_SHEET in xls.sheet_names:
        head = pd.read_excel(xls, sheet_name=DATA_SHEET, header=None, nrows=1)
        if head.shape[1] > 1 and not pd.isna(head.iloc[0, 1]):
            return str(head.iloc[0, 1]).strip()
    head = pd.read_excel(xls, sheet_name="Profit & Loss", header=None, nrows=1)
    value = head.iloc[0, 0]
    return str(value).strip() if not pd.isna(value) else "UNKNOWN COMPANY"


# ─────────────────────────────────────────────────────────────────────────────
# CLI — run this to eyeball the output, and to generate mock data for the
# frontend team before the API exists:
#
#     python -m backend.ingestion.parser tests/sample_data/TCS.xlsx
#     python -m backend.ingestion.parser tests/sample_data/TCS.xlsx --json out.json
# ─────────────────────────────────────────────────────────────────────────────

def to_json_safe(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """DataFrames -> nested dicts, so this can go over HTTP or into mock_data.py."""
    out: Dict[str, Any] = {}
    for key, value in parsed.items():
        if isinstance(value, pd.DataFrame):
            out[key] = {
                str(row): {str(col): (None if pd.isna(v) else float(v))
                           for col, v in series.items()}
                for row, series in value.iterrows()
            }
        else:
            out[key] = value
    return out


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(description="Parse a Screener.in Excel export.")
    ap.add_argument("filepath")
    ap.add_argument("--json", metavar="OUT", help="also write parsed output to JSON")
    args = ap.parse_args()

    data = parse_screener_excel(args.filepath)

    print(f"\nCompany : {data['company_name']}")
    print(f"File    : {data['source_file']}")
    print(f"Years   : {', '.join(data['fiscal_years'])}")
    print(f"Quarters: {', '.join(data['quarter_labels'])}")
    print(f"Shares  : {data['meta'].get('number_of_shares')} crore\n")

    for name in ("pl", "quarters", "bs", "cf"):
        frame = data[name]
        print(f"--- {name.upper()}  ({frame.shape[0]} rows x {frame.shape[1]} cols) ---")
        print(frame.iloc[:, -3:].to_string())
        print()

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(to_json_safe(data), fh, indent=2)
        print(f"Wrote {args.json}")