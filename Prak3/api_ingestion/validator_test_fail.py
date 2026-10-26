from validator import validate_records

records = [
    {
        "id": 1,
        "customer": "customer_001",
        "updated_at": "2026-09-01",
    }
]

validate_records(records)

print(
    "Validation passed"
)