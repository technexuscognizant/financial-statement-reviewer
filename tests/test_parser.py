"""
tests/test_parser.py
====================
Smoke tests for PHASE 1. Owner: Member 1.

These do NOT test accounting rules — that is test_validator.py in Phase 2.
These only prove the parser reads the file correctly: right shape, right
labels, right numbers, no crashes.

Run:  pytest tests/ -v
"""

import os

import pandas as pd
import pytest  # type: ignore

from backend.ingestion.parser import ParserError, parse_screener_excel

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
TCS = os.path.join(SAMPLE_DIR, "TCS.xlsx")
HCL = os.path.join(SAMPLE_DIR, "HCL_Technologies.xlsx")

ALL_FILES = [TCS, HCL]


@pytest.fixture(scope="module")
def tcs():
    return parse_screener_excel(TCS)


# ── structure ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", ALL_FILES)
def test_all_five_sheets_are_found(path):
    data = parse_screener_excel(path)
    assert len(data["sheets_found"]) == 5


@pytest.mark.parametrize("path", ALL_FILES)
def test_ten_fiscal_years_are_parsed(path):
    data = parse_screener_excel(path)
    assert data["fiscal_years"] == [f"FY{y}" for y in range(2017, 2027)]


def test_company_name_is_read(tcs):
    assert "TATA CONSULTANCY" in tcs["company_name"].upper()


# ── labels are canonical (Members 2/3/4 depend on these exact strings) ───────

@pytest.mark.parametrize("path", ALL_FILES)
def test_pl_has_every_required_line_item(path):
    pl = parse_screener_excel(path)["pl"]
    for item in ["Sales", "Expenses", "Operating Profit", "Other Income",
                 "Depreciation", "Interest", "Profit Before Tax", "Tax",
                 "Net Profit", "EPS"]:
        assert item in pl.index, f"missing P&L row: {item}"


@pytest.mark.parametrize("path", ALL_FILES)
def test_balance_sheet_totals_are_disambiguated(path):
    """Screener names both totals 'Total'; we must split them apart."""
    bs = parse_screener_excel(path)["bs"]
    assert "Total Liabilities" in bs.index
    assert "Total Assets" in bs.index
    assert "Total" not in bs.index
    # each must be a Series (one row), not a DataFrame (duplicate rows)
    assert isinstance(bs.loc["Total Assets"], pd.Series)


@pytest.mark.parametrize("path", ALL_FILES)
def test_cash_flow_has_four_rows(path):
    cf = parse_screener_excel(path)["cf"]
    for item in ["Cash from Operating Activity", "Cash from Investing Activity",
                 "Cash from Financing Activity", "Net Cash Flow"]:
        assert item in cf.index


# ── junk removal ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", ALL_FILES)
def test_no_unlabelled_junk_rows_leak_through(path):
    """The P&L sheet has a floating TRENDS: block with blank row labels."""
    for key in ("pl", "quarters", "bs", "cf"):
        frame = parse_screener_excel(path)[key]
        for label in frame.index:
            assert label and str(label).lower() != "nan"


@pytest.mark.parametrize("path", ALL_FILES)
def test_forecast_columns_are_kept_out_of_the_statement(path):
    """
    Trailing / Best Case / Worst Case are projections. In those columns
    'Tax' is a RATE (0.24) not an amount, so letting them reach the
    validator would produce nonsense failures.
    """
    data = parse_screener_excel(path)
    for column in ("Trailing", "Best Case", "Worst Case"):
        assert column not in data["pl"].columns
        assert column in data["pl_projections"].columns


@pytest.mark.parametrize("path", ALL_FILES)
def test_screener_own_ratios_are_separated_not_mixed_into_pl(path):
    """We re-compute ratios ourselves; Screener's go in their own frame."""
    data = parse_screener_excel(path)
    assert "OPM" not in data["pl"].index
    assert "OPM" in data["pl_reported"].index
    assert "Dividend Payout" in data["pl_reported"].index


# ── values are numeric and correct ───────────────────────────────────────────

@pytest.mark.parametrize("path", ALL_FILES)
def test_every_value_is_numeric(path):
    for key in ("pl", "quarters", "bs", "cf"):
        frame = parse_screener_excel(path)[key]
        assert all(pd.api.types.is_numeric_dtype(frame[c]) for c in frame.columns)


def test_known_tcs_values_are_exact(tcs):
    """Spot-check against numbers read straight off the spreadsheet."""
    assert tcs["pl"].loc["Sales", "FY2026"] == 267021
    assert tcs["pl"].loc["Net Profit", "FY2026"] == 49210
    assert tcs["bs"].loc["Reserves", "FY2026"] == 106878
    assert tcs["cf"].loc["Net Cash Flow", "FY2026"] == -1925


def test_negative_values_survive(tcs):
    """FY2026 Other Income is negative — it must not be coerced to 0 or NaN."""
    assert tcs["pl"].loc["Other Income", "FY2026"] == -124


def test_share_count_is_read_from_data_sheet(tcs):
    assert 350 < tcs["meta"]["number_of_shares"] < 375


# ── quarter labelling (this is what makes cross-sheet tie-out work) ──────────

@pytest.mark.parametrize("path", ALL_FILES)
def test_quarters_use_indian_fiscal_labels(path):
    labels = parse_screener_excel(path)["quarter_labels"]
    assert labels[0] == "Q4FY24"      # 31-Mar-2024 closes FY2024
    assert labels[1] == "Q1FY25"      # 30-Jun-2024 opens FY2025
    assert len(labels) == 10


@pytest.mark.parametrize("path", ALL_FILES)
@pytest.mark.parametrize("fiscal_year", ["FY2025", "FY2026"])
def test_four_quarters_roll_up_into_the_annual_column(path, fiscal_year):
    """
    If the quarter labelling is wrong this test fails, and every cross-sheet
    check Member 1 writes in Phase 2 would be wrong too.
    """
    data = parse_screener_excel(path)
    quarters = data["quarters"]
    suffix = "FY" + fiscal_year[-2:]
    columns = [c for c in quarters.columns if c.endswith(suffix)]
    assert len(columns) == 4

    for item in ("Sales", "Net Profit"):
        rolled = quarters.loc[item, columns].sum()
        annual = data["pl"].loc[item, fiscal_year]
        assert abs(rolled - annual) <= 2, f"{item} {fiscal_year}: {rolled} vs {annual}"


# ── failure handling ─────────────────────────────────────────────────────────

def test_missing_file_raises_parser_error():
    with pytest.raises(ParserError):
        parse_screener_excel("does_not_exist.xlsx")


def test_non_screener_file_raises_parser_error(tmp_path):
    bogus = tmp_path / "random.xlsx"
    pd.DataFrame({"a": [1, 2]}).to_excel(bogus, index=False)
    with pytest.raises(ParserError):
        parse_screener_excel(str(bogus))