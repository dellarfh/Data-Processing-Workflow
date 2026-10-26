from pathlib import Path

from watermark import load_watermark, save_watermark

WATERMARK_FILE = "state/test_watermark_failure.json"


def save_records_that_fails(records, output_file):

    raise RuntimeError("Storage failed")


def test_storage_failure():

    Path(WATERMARK_FILE).unlink(missing_ok=True)

    watermark_before = load_watermark(WATERMARK_FILE)

    print("Watermark before:", watermark_before)

    records = [
        {
            "id": 1,
            "customer": "customer_001",
            "amount": 10000,
            "updated_at": "2026-09-01T08:10:00+00:00",
        }
    ]

    storage_succeeded = False

    try:

        save_records_that_fails(
            records,
            "data/does_not_matter.parquet",
        )

        storage_succeeded = True

    except RuntimeError as error:

        print("Storage failed as expected:", error)

    if storage_succeeded:

        new_watermark = max(
            record["updated_at"] for record in records
        )

        save_watermark(WATERMARK_FILE, new_watermark)

        print("Watermark updated (storage succeeded)")

    else:

        print("Watermark NOT updated (storage failed) - as expected")

    watermark_after = load_watermark(WATERMARK_FILE)

    print("Watermark after:", watermark_after)

    assert watermark_before == watermark_after, (
        "FAIL: watermark changed even though storage failed!"
    )


test_storage_failure()

print("test_storage_failure passed")