import logging
import time

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

url = (
    "http://127.0.0.1:8000/"
    "rate-limited"
)

MAX_RETRIES = 5

for attempt in range(1, MAX_RETRIES + 1):

    response = requests.get(
        url,
        timeout=(3, 10),
    )

    print(
        f"Attempt {attempt}: status={response.status_code}"
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

        wait_time = float(retry_after)

        logging.warning(
            "429 received on attempt %s. Retry-After=%s",
            attempt,
            retry_after,
        )

        print(
            f"Rate limited. Wait {wait_time} seconds"
        )

        time.sleep(wait_time)

        continue

    response.raise_for_status()

else:

    raise RuntimeError(
        "Maximum retries exceeded"
    )