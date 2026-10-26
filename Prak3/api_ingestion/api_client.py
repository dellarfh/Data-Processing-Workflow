import logging
import random
import time

import requests

RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}

logger = logging.getLogger("api_client")


def get_json(
    session,
    url,
    params=None,
    timeout=(3, 10),
    max_retries=5,
    base_delay=1,
):

    for attempt in range(1, max_retries + 1):

        try:

            response = session.get(
                url,
                params=params,
                timeout=timeout,
            )

            if response.status_code == 200:
                logger.info(
                    "HTTP 200 OK for %s (attempt %s)",
                    url,
                    attempt,
                )
                return response.json()

            if response.status_code not in RETRYABLE_STATUS_CODES:
                response.raise_for_status()

            if attempt == max_retries:
                response.raise_for_status()

            if response.status_code == 429:

                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    wait_time = float(retry_after)
                else:
                    wait_time = base_delay * (2 ** (attempt - 1))

            else:
                wait_time = base_delay * (2 ** (attempt - 1))

            jitter = random.uniform(0, 1)
            sleep_time = wait_time + jitter

            logger.warning(
                "Attempt %s failed with status %s. Waiting %.2fs before retry.",
                attempt,
                response.status_code,
                sleep_time,
            )

            time.sleep(sleep_time)

        except requests.exceptions.RequestException as error:

            if attempt == max_retries:
                logger.error(
                    "Request failed after %s attempts: %s",
                    max_retries,
                    error,
                )
                raise

            wait_time = base_delay * (2 ** (attempt - 1))
            jitter = random.uniform(0, 1)
            sleep_time = wait_time + jitter

            logger.warning(
                "Network error on attempt %s: %s. Waiting %.2fs before retry.",
                attempt,
                error,
                sleep_time,
            )

            time.sleep(sleep_time)

    raise RuntimeError(
        "Maximum retries exceeded"
    )