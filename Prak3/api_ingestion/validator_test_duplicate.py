from validator import validate_unique_ids

records_ok = [
    {"id": 1},
    {"id": 2},
    {"id": 3},
]

validate_unique_ids(records_ok)
print("Unique check passed (no duplicates)")

records_duplicate = [
    {"id": 1},
    {"id": 2},
    {"id": 1},
]

validate_unique_ids(records_duplicate)
print("This line should NOT be printed")