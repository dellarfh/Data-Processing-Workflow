import pandas as pd

input_records = [
    {
        "id": 1,
        "customer": "Andi",
        "amount": 10000,
        "updated_at": "2026-09-01",
    }
]

df = pd.DataFrame(
    input_records
)

output_file = (
    "data/validation.parquet"
)

df.to_parquet(
    output_file,
    index=False,
)

result = pd.read_parquet(
    output_file
)

assert len(result) == len(df)

assert list(result.columns) == list(
    df.columns
)

print(
    "Parquet validation passed"
)