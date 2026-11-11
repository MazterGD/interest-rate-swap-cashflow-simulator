"""M4 export contracts using fixtures independent of the engine."""
from io import BytesIO

import pandas as pd
import pytest

from swap.export import cash_flows_to_dataframe, to_csv_bytes
from swap.models import PeriodCashFlow


EXPECTED_COLUMNS = [
    "Period", "Time (yrs)", "Floating rate (%)", "Fixed payment",
    "Floating payment", "Net settlement", "Cumulative net",
]


@pytest.fixture
def cash_flows():
    return [
        PeriodCashFlow(1, 0.5, 0.035, 20000, 17500, -2500, -2500),
        PeriodCashFlow(2, 1.0, 0.04, 20000, 20000, 0, -2500),
        PeriodCashFlow(3, 1.5, 0.045, 20000, 22500, 2500, 0),
        PeriodCashFlow(4, 2.0, 0.05, 20000, 25000, 5000, 5000),
    ]


def test_worked_example_dataframe(cash_flows):
    df = cash_flows_to_dataframe(cash_flows)
    assert list(df.columns) == EXPECTED_COLUMNS
    assert df["Period"].tolist() == [1, 2, 3, 4]
    assert df["Time (yrs)"].tolist() == [0.5, 1, 1.5, 2]
    assert df["Floating rate (%)"].tolist() == pytest.approx([3.5, 4, 4.5, 5])
    assert df["Fixed payment"].tolist() == [20000] * 4
    assert df["Floating payment"].tolist() == [17500, 20000, 22500, 25000]
    assert df["Net settlement"].tolist() == [-2500, 0, 2500, 5000]
    assert df["Cumulative net"].tolist() == [-2500, -2500, 0, 5000]


def test_csv_round_trip(cash_flows):
    df = cash_flows_to_dataframe(cash_flows)
    data = to_csv_bytes(df)
    assert isinstance(data, bytes)
    assert data.decode("utf-8").splitlines()[0] == ",".join(EXPECTED_COLUMNS)
    restored = pd.read_csv(BytesIO(data))
    pd.testing.assert_frame_equal(restored, df, check_dtype=False)


def test_rounding_only_at_export_without_mutating_dataframe():
    df = cash_flows_to_dataframe([
        PeriodCashFlow(1, 0.25, -0.0123456, 1234.5678, -12.3456, -1246.9134, -1246.9134)
    ])
    before = df.copy(deep=True)
    assert df.loc[0, "Fixed payment"] == 1234.5678
    assert df.loc[0, "Floating rate (%)"] == pytest.approx(-1.23456)
    data = to_csv_bytes(df)
    assert data.decode().splitlines()[1].endswith(",1234.57,-12.35,-1246.91,-1246.91")
    restored = pd.read_csv(BytesIO(data))
    assert restored.loc[0, "Floating rate (%)"] == pytest.approx(-1.23456)
    pd.testing.assert_frame_equal(df, before)


def test_empty_export_preserves_headers():
    df = cash_flows_to_dataframe([])
    assert df.empty
    assert list(df.columns) == EXPECTED_COLUMNS
    restored = pd.read_csv(BytesIO(to_csv_bytes(df)))
    assert restored.empty
    assert list(restored.columns) == EXPECTED_COLUMNS
