import requests

url = (
    "http://127.0.0.1:8000/"
    "rate-limited"
)

response = requests.get(
    url,
    timeout=(3, 10),
)

if response.status_code == 429:

    retry_after = response.headers.get(
        "Retry-After"
    )

    print(
        "Retry after:",
        retry_after,
    )