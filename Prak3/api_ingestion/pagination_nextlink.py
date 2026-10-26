import requests

url = (
    "http://127.0.0.1:8000/"
    "transactions?page=1&limit=10"
)

total = 0

while url:

    response = requests.get(
        url,
        timeout=(3, 10),
    )

    response.raise_for_status()

    payload = response.json()

    data = payload.get(
        "data",
        [],
    )

    total += len(data)

    print(
        "Fetched:",
        len(data),
    )

    url = payload.get("next")

print(
    "Total:",
    total,
)