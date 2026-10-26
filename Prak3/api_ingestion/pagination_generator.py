import requests

def fetch_paginated_data(
    url,
    limit=10,
):

    page = 1

    while True:

        response = requests.get(
            url,
            params={
                "page": page,
                "limit": limit,
            },
            timeout=(3, 10),
        )

        response.raise_for_status()

        payload = response.json()

        data = payload.get(
            "data",
            [],
        )

        if not data:
            break

        yield data

        page += 1

url = (
    "http://127.0.0.1:8000/"
    "transactions"
)

for page_data in fetch_paginated_data(
    url,
):
    print(
        "Processing:",
        len(page_data),
        "records",
    )