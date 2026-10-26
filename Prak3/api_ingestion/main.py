import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from api_client import get_json
from config import (
    BASE_DELAY,
    CONNECT_TIMEOUT,
    DATA_DIRECTORY,
    LOG_FILE,
    MAX_RETRIES,
    PAGE_SIZE,
    READ_TIMEOUT,
    TRANSACTIONS_URL,
    WATERMARK_FILE,
)
from pagination import fetch_pages
from storage import (
    read_records,
    save_records,
)
from validator import (
    validate_records,
    validate_unique_ids,
)
from watermark import (
    load_watermark,
    save_watermark,
)

def configure_logging(
    log_file,
):

    path = Path(log_file)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(
                path,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
        force=True,
    )

def fetch_transaction_page(
    session,
    page,
    limit,
    watermark,
):

    params = {
        "page": page,
        "limit": limit,
    }

    if watermark:
        params[
            "updated_since"
        ] = watermark

    return get_json(
        session=session,
        url=TRANSACTIONS_URL,
        params=params,
        timeout=(
            CONNECT_TIMEOUT,
            READ_TIMEOUT,
        ),
        max_retries=MAX_RETRIES,
        base_delay=BASE_DELAY,
    )

def get_max_watermark(
    records,
):

    if not records:
        return None

    return max(
        record["updated_at"]
        for record in records
    )

def build_output_file():

    now = datetime.now()

    partition = (
        f"transaction_date="
        f"{now:%Y-%m-%d}"
    )

    return (
        Path(DATA_DIRECTORY)
        / "transactions"
        / partition
        / "transactions.parquet"
    )

def run_pipeline():

    configure_logging(
        LOG_FILE
    )

    logger = logging.getLogger(
        "pipeline"
    )

    logger.info(
        "Pipeline started"
    )

    watermark = load_watermark(
        WATERMARK_FILE
    )

    logger.info(
        "Watermark loaded: %s",
        watermark,
    )

    session = requests.Session()

    all_records = []

    def fetch_function(
        page,
        limit,
        watermark,
    ):

        return fetch_transaction_page(
            session=session,
            page=page,
            limit=limit,
            watermark=watermark,
        )

    for page_records in fetch_pages(
        fetch_function=fetch_function,
        watermark=watermark,
        page_size=PAGE_SIZE,
    ):

        validate_records(
            page_records
        )

        all_records.extend(
            page_records
        )

        logger.info(
            "Records collected=%s",
            len(all_records),
        )

    if not all_records:

        logger.info(
            "No new records"
        )

        return

    validate_unique_ids(
        all_records
    )

    new_watermark = (
        get_max_watermark(
            all_records
        )
    )

    output_file = (
        build_output_file()
    )

    save_records(
        all_records,
        output_file,
    )

    logger.info(
        "Parquet saved: %s",
        output_file,
    )

    result = read_records(
        output_file
    )

    if len(result) != len(
        all_records
    ):

        raise RuntimeError(
            "Stored record count mismatch"
        )

    if not isinstance(
        result,
        pd.DataFrame,
    ):

        raise RuntimeError(
            "Output is not a DataFrame"
        )

    # PENTING:
    # Update watermark hanya setelah:
    # 1. validasi berhasil
    # 2. data berhasil disimpan
    # 3. output berhasil dibaca kembali

    save_watermark(
        WATERMARK_FILE,
        new_watermark,
    )

    logger.info(
        "Watermark updated: %s",
        new_watermark,
    )

    logger.info(
        "Pipeline finished successfully"
    )

if __name__ == "__main__":

    run_pipeline()