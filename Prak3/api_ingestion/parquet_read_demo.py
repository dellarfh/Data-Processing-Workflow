from storage import read_records

df = read_records(
    "data/transactions.parquet"
)

print(df)