import requests

MAX_PAGES = 1000

def fetch_pages(
    url,
    limit=10,
):

    page = 1

    while True:

        if page > MAX_PAGES:
            raise RuntimeError(
                "Maximum page limit exceeded"
            )

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

total = 0

for page_data in fetch_pages(url, limit=10):
    total += len(page_data)
    print("Fetched page, records:", len(page_data))

print("Total record:", total)