import json
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 8000

def create_transactions():
    base_time = datetime(
        2026,
        9,
        1,
        8,
        0,
        0,
        tzinfo=timezone.utc,
    )

    records = []

    for i in range(1, 61):
        updated_at = base_time + timedelta(minutes=i * 10)

        records.append(
            {
                "id": i,
                "customer": f"customer_{i:03d}",
                "amount": i * 10000,
                "updated_at": updated_at.isoformat(),
            }
        )

    return records

TRANSACTIONS = create_transactions()

class DemoHandler(BaseHTTPRequestHandler):

    rate_limit_counter = 0
    unstable_counter = 0

    def send_json(
        self,
        status_code,
        payload,
        headers=None,
    ):
        body = json.dumps(payload).encode("utf-8")

        self.send_response(status_code)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        if headers:
            for key, value in headers.items():
                self.send_header(key, str(value))

        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):

        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/transactions":
            self.handle_transactions(query)

        elif parsed.path == "/cursor-transactions":
            self.handle_cursor_transactions(query)

        elif parsed.path == "/rate-limited":
            self.handle_rate_limited()

        elif parsed.path == "/unstable":
            self.handle_unstable()

        elif parsed.path == "/reset":
            DemoHandler.rate_limit_counter = 0
            DemoHandler.unstable_counter = 0

            self.send_json(
                200,
                {
                    "message": "counter reset"
                },
            )

        else:
            self.send_json(
                404,
                {
                    "error": "endpoint not found"
                },
            )

    def handle_transactions(self, query):

        page = int(
            query.get("page", ["1"])[0]
        )

        limit = int(
            query.get("limit", ["10"])[0]
        )

        updated_since = query.get(
            "updated_since",
            [None],
        )[0]

        records = TRANSACTIONS.copy()

        if updated_since:
            records = [
                record
                for record in records
                if record["updated_at"] > updated_since
            ]

        start = (page - 1) * limit
        end = start + limit

        page_data = records[start:end]

        next_url = None

        if end < len(records):
            next_page = page + 1

            next_url = (
                f"http://{HOST}:{PORT}/transactions"
                f"?page={next_page}"
                f"&limit={limit}"
            )

            if updated_since:
                next_url += (
                    f"&updated_since={updated_since}"
                )

        payload = {
            "data": page_data,
            "page": page,
            "limit": limit,
            "total": len(records),
            "next": next_url,
        }

        self.send_json(200, payload)

    def handle_cursor_transactions(self, query):

        limit = int(
            query.get("limit", ["10"])[0]
        )

        cursor_value = query.get(
            "cursor",
            [None],
        )[0]

        start = int(cursor_value) if cursor_value else 0
        end = start + limit

        page_data = TRANSACTIONS[start:end]

        next_cursor = (
            str(end)
            if end < len(TRANSACTIONS)
            else None
        )

        payload = {
            "data": page_data,
            "next_cursor": next_cursor,
        }

        self.send_json(200, payload)

    def handle_rate_limited(self):

        DemoHandler.rate_limit_counter += 1

        if DemoHandler.rate_limit_counter <= 2:
            self.send_json(
                429,
                {
                    "error": "Too Many Requests"
                },
                headers={
                    "Retry-After": "1"
                },
            )
            return

        self.send_json(
            200,
            {
                "message": "request accepted"
            },
        )

    def handle_unstable(self):

        DemoHandler.unstable_counter += 1

        if DemoHandler.unstable_counter <= 2:
            self.send_json(
                500,
                {
                    "error": "temporary server error"
                },
            )
            return

        self.send_json(
            200,
            {
                "message": "server recovered"
            },
        )

    def log_message(self, format, *args):
        print(
            f"[MOCK API] "
            f"{self.address_string()} - "
            f"{format % args}"
        )

if __name__ == "__main__":

    server = HTTPServer(
        (HOST, PORT),
        DemoHandler,
    )

    print(
        f"Mock API running at "
        f"http://{HOST}:{PORT}"
    )

    print(
        "Endpoints:"
    )

    print(
        f"  /transactions"
    )

    print(
        f"  /cursor-transactions"
    )

    print(
        f"  /rate-limited"
    )

    print(
        f"  /unstable"
    )

    print(
        f"  /reset"
    )

    server.serve_forever()