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


def test_pagination():

    total = 0

    for page_data in fetch_paginated_data(
        url=(
            "http://127.0.0.1:8000/"
            "transactions"
        ),
        limit=10,
    ):
        total += len(page_data)

    assert total == 60


test_pagination()

print("test_pagination passed")