import time
import requests

url = (
    "http://127.0.0.1:8000/"
    "unstable"
)

MAX_RETRIES = 5

for attempt in range(
    1,
    MAX_RETRIES + 1,
):

    response = requests.get(
        url,
        timeout=(3, 10),
    )

    print(
        f"Attempt {attempt}: "
        f"status={response.status_code}"
    )

    if response.status_code == 200:

        print(
            "Success:",
            response.json(),
        )

        break

    if response.status_code in (
        500,
        502,
        503,
        504,
    ):

        if attempt == MAX_RETRIES:
            break

        time.sleep(1)

        continue

    response.raise_for_status()

else:

    raise RuntimeError(
        "Request failed"
    )