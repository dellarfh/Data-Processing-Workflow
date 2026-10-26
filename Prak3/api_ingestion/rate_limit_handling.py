import time
import requests

url = (
    "http://127.0.0.1:8000/"
    "rate-limited"
)

MAX_RETRIES = 5

for attempt in range(MAX_RETRIES):

    response = requests.get(
        url,
        timeout=(3, 10),
    )

    if response.status_code == 200:

        print(
            "Success:",
            response.json(),
        )

        break

    if response.status_code == 429:

        retry_after = response.headers.get(
            "Retry-After",
            "1",
        )

        wait_time = float(
            retry_after
        )

        print(
            f"Rate limited. "
            f"Wait {wait_time} seconds"
        )

        time.sleep(wait_time)

        continue

    response.raise_for_status()

else:

    raise RuntimeError(
        "Maximum retries exceeded"
    )