import logging

MAX_PAGES = 1000

logger = logging.getLogger("pagination")


def fetch_pages(
    fetch_function,
    watermark=None,
    page_size=10,
):

    page = 1

    while True:

        if page > MAX_PAGES:
            raise RuntimeError(
                "Maximum page limit exceeded"
            )

        logger.info(
            "Requesting page=%s",
            page,
        )

        payload = fetch_function(
            page,
            page_size,
            watermark,
        )

        data = payload.get(
            "data",
            [],
        )

        logger.info(
            "Fetched page=%s records=%s",
            page,
            len(data),
        )

        if not data:
            break

        yield data

        page += 1