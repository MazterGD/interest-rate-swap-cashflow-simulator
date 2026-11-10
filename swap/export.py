"""Cash-flow table and CSV export (spec §6.2). Owner: M4.

PLACEHOLDER from the kickoff skeleton — M4 replaces the bodies below.
"""
import pandas as pd

from swap.models import PeriodCashFlow

COLUMNS = [
    "Period",
    "Time (yrs)",
    "Floating rate (%)",
    "Fixed payment",
    "Floating payment",
    "Net settlement",
    "Cumulative net",
]


def cash_flows_to_dataframe(cash_flows: list[PeriodCashFlow]) -> pd.DataFrame:
    """One row per period, columns in COLUMNS order, rates x100, money unrounded."""
    # TODO(M4): fill rows from cash_flows. Placeholder returns an empty table.
    return pd.DataFrame(columns=COLUMNS)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """UTF-8 CSV, no index, money rounded to 2 dp."""
    # TODO(M4): round money to 2 dp.
    return df.to_csv(index=False).encode()
