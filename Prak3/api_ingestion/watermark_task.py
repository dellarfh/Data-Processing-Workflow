import requests

from watermark import load_watermark, save_watermark

WATERMARK_FILE = "state/watermark.json"

url = "http://127.0.0.1:8000/transactions"


def fetch_all(watermark):

    page = 1
    limit = 10
    all_records = []

    while True:

        params = {
            "page": page,
            "limit": limit,
        }

        if watermark:
            params["updated_since"] = watermark

        response = requests.get(
            url,
            params=params,
            timeout=(3, 10),
        )

        response.raise_for_status()

        payload = response.json()

        data = payload.get("data", [])

        if not data:
            break

        all_records.extend(data)

        page += 1

    return all_records


def get_max_watermark(records):

    if not records:
        return None

    return max(
        record["updated_at"]
        for record in records
    )


print("=== RUN 1 ===")

watermark_before = load_watermark(WATERMARK_FILE)
print("Watermark before:", watermark_before)

records = fetch_all(watermark_before)
print("Records fetched:", len(records))

new_watermark = get_max_watermark(records)

if new_watermark:
    save_watermark(WATERMARK_FILE, new_watermark)

watermark_after = load_watermark(WATERMARK_FILE)
print("Watermark after:", watermark_after)