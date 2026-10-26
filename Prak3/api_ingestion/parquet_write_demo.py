from storage import save_records

records = [
    {
        "id": 1,
        "customer": "Andi",
        "amount": 10000,
        "updated_at": (
            "2026-09-01T08:00:00+00:00"
        ),
    },
    {
        "id": 2,
        "customer": "Budi",
        "amount": 20000,
        "updated_at": (
            "2026-09-01T09:00:00+00:00"
        ),
    },
]

output_file = (
    "data/transactions.parquet"
)

save_records(
    records,
    output_file,
)

print(
    "Parquet saved"
)