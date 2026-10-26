import requests

url = (
    "http://127.0.0.1:8000/"
    "cursor-transactions"
)

cursor = None
total = 0

while True:

    params = {
        "limit": 10,
    }

    if cursor:
        params["cursor"] = cursor

    response = requests.get(
        url,
        params=params,
        timeout=(3, 10),
    )

    response.raise_for_status()

    payload = response.json()

    data = payload.get(
        "data",
        [],
    )

    total += len(data)

    cursor = payload.get(
        "next_cursor"
    )

    if not cursor:
        break

print(
    "Total:",
    total,
)