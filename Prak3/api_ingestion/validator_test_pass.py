from validator import validate_records

records = [
    {
        "id": 1,
        "customer": "customer_001",
        "amount": 10000,
        "updated_at": (
            "2026-09-01T08:10:00+00:00"
        ),
    }
]

validate_records(records)

print(
    "Validation passed"
)