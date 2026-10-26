import logging
from pathlib import Path

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


configure_logging("logs/demo.log")

logging.info(
    "Pipeline started"
)

logging.info(
    "Fetching page=%s",
    1,
)

logging.warning(
    "Rate limit reached"
)

logging.error(
    "Failed to save data"
)