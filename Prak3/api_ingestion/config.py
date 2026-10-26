API_BASE_URL = (
    "http://127.0.0.1:8000"
)

TRANSACTIONS_URL = (
    f"{API_BASE_URL}/transactions"
)

PAGE_SIZE = 10

CONNECT_TIMEOUT = 3
READ_TIMEOUT = 10

MAX_RETRIES = 5
BASE_DELAY = 1

WATERMARK_FILE = (
    "state/watermark.json"
)

DATA_DIRECTORY = "data"

LOG_FILE = (
    "logs/ingestion.log"
)