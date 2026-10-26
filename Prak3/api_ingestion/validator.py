REQUIRED_FIELDS = {
    "id",
    "customer",
    "amount",
    "updated_at",
}

def validate_record(
    record,
):

    missing_fields = (
        REQUIRED_FIELDS
        - set(record.keys())
    )

    if missing_fields:

        raise ValueError(
            "Missing fields: "
            f"{sorted(missing_fields)}"
        )

    if not isinstance(
        record["id"],
        int,
    ):
        raise ValueError(
            "id must be int"
        )

    if not isinstance(
        record["customer"],
        str,
    ):
        raise ValueError(
            "customer must be str"
        )

    if not isinstance(
        record["amount"],
        (int, float),
    ):
        raise ValueError(
            "amount must be numeric"
        )

def validate_records(
    records,
):

    if not isinstance(
        records,
        list,
    ):
        raise ValueError(
            "records must be a list"
        )

    for record in records:
        validate_record(record)

    return True

def validate_unique_ids(
    records,
):

    ids = [
        record["id"]
        for record in records
    ]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate id detected"
        )