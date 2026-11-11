"""Cash-flow table and CSV export (spec §6.2). Owner: M4."""
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
    return pd.DataFrame(
        [
            (flow.period, flow.time_years, flow.floating_rate * 100,
             flow.fixed_payment, flow.floating_payment,
             flow.net_settlement, flow.cumulative_net)
            for flow in cash_flows
        ],
        columns=COLUMNS,
    )


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """UTF-8 CSV, no index, money rounded to 2 dp."""
    export = df.copy()
    for column in COLUMNS[3:]:
        export[column] = export[column].map(lambda amount: f"{amount:.2f}")
    return export.to_csv(index=False).encode("utf-8")
