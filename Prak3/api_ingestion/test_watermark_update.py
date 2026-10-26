from pathlib import Path

from watermark import load_watermark, save_watermark

WATERMARK_FILE = "state/test_watermark_case.json"


def test_watermark_update():

    Path(WATERMARK_FILE).unlink(missing_ok=True)

    old_watermark = "2026-09-01T08:00:00+00:00"

    save_watermark(WATERMARK_FILE, old_watermark)

    loaded_old = load_watermark(WATERMARK_FILE)

    assert loaded_old == old_watermark, (
        f"Expected {old_watermark}, got {loaded_old}"
    )

    # Simulasikan data yang berhasil diproses pipeline
    processed_records = [
        {"updated_at": "2026-09-01T09:00:00+00:00"},
        {"updated_at": "2026-09-01T10:30:00+00:00"},
        {"updated_at": "2026-09-01T08:30:00+00:00"},
    ]

    new_watermark = max(
        record["updated_at"] for record in processed_records
    )

    save_watermark(WATERMARK_FILE, new_watermark)

    loaded_new = load_watermark(WATERMARK_FILE)

    assert loaded_new == "2026-09-01T10:30:00+00:00", (
        f"Expected max timestamp, got {loaded_new}"
    )

    assert loaded_new != old_watermark, (
        "Watermark should have advanced"
    )

    print("Old watermark:", old_watermark)
    print("New watermark:", loaded_new)


test_watermark_update()

print("test_watermark_update passed")