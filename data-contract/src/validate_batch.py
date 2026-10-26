import csv
from datetime import datetime

from pydantic import ValidationError

from contract import OrderContract


def parse_datetime(value):
    if value is None or value == "":
        return None

    return datetime.fromisoformat(value)


def load_orders(path):
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        rows = []

        for row in reader:
            rows.append(
                {
                    "order_id": row["order_id"],
                    "customer_id": int(row["customer_id"]),
                    "amount": float(row["amount"]),
                    "status": row["status"],
                    "transaction_date": parse_datetime(
                        row["transaction_date"]
                    ),
                    "payment_date": parse_datetime(
                        row["payment_date"]
                    ),
                }
            )

        return rows


def validate_batch(rows):
    errors = []
    valid_orders = []

    for row_number, row in enumerate(rows, start=2):
        try:
            order = OrderContract.model_validate(row)
            valid_orders.append(order)

        except ValidationError as exc:
            errors.append(
                {
                    "row": row_number,
                    "order_id": row.get("order_id"),
                    "errors": exc.errors(),
                }
            )

    return valid_orders, errors

def save_to_warehouse(orders, output_path):
    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "order_id",
                "customer_id",
                "amount",
                "status",
                "transaction_date",
                "payment_date",
            ]
        )

        for order in orders:
            writer.writerow(
                [
                    order.order_id,
                    order.customer_id,
                    order.amount,
                    order.status,
                    order.transaction_date.isoformat(),
                    (
                        order.payment_date.isoformat()
                        if order.payment_date
                        else ""
                    ),
                ]
            )

rows = load_orders("../data/orders_invalid.csv")

valid_orders, errors = validate_batch(rows)

print(f"Jumlah record : {len(rows)}")
print(f"Valid         : {len(valid_orders)}")
print(f"Invalid       : {len(errors)}")

if errors:
    print("FAIL-FAST: batch ditolak.")
    raise SystemExit(1)

save_to_warehouse(
    valid_orders,
    "../data/warehouse_orders.csv",
)

print("Batch berhasil dimuat ke Data Warehouse.")