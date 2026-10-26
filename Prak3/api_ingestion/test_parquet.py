import pandas as pd

from storage import save_records

OUTPUT_FILE = "data/test_parquet_output.parquet"


def test_parquet():

    records = [
        {
            "id": 1,
            "customer": "customer_001",
            "amount": 10000,
            "updated_at": "2026-09-01T08:10:00+00:00",
        },
        {
            "id": 2,
            "customer": "customer_002",
            "amount": 20000,
            "updated_at": "2026-09-01T08:20:00+00:00",
        },
    ]

    save_records(records, OUTPUT_FILE)

    expected_count = len(records)

    result = pd.read_parquet(
        OUTPUT_FILE
    )

    assert len(result) == expected_count

    assert "id" in result.columns
    assert "updated_at" in result.columns

    print("Row count:", len(result))
    print("Columns:", list(result.columns))


test_parquet()

print("test_parquet passed")