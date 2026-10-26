import requests

url = (
    "http://127.0.0.1:8000/"
    "rate-limited"
)

response = requests.get(
    url,
    timeout=(3, 10),
)

print(
    "Status:",
    response.status_code,
)

print(
    "Headers:",
    dict(response.headers),
)

print(
    "Body:",
    response.text,
)