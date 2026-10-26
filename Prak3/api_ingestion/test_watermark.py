from watermark import (
    load_watermark,
    save_watermark,
)

FILE_PATH = (
    "state/watermark.json"
)

current = load_watermark(
    FILE_PATH
)

print(
    "Current watermark:",
    current,
)

new_value = (
    "2026-09-01T12:00:00+00:00"
)

save_watermark(
    FILE_PATH,
    new_value,
)

print(
    "Watermark saved"
)

print(
    "Reload:",
    load_watermark(FILE_PATH),
)