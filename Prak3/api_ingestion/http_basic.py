import requests

url = (
    "http://127.0.0.1:8000/"
    "transactions?page=1&limit=5"
)

response = requests.get(
    url,
    timeout=(3, 10),
)

response.raise_for_status()

data = response.json()

print(data)