import sys
import duckdb

PERINTAH = ["status", "duplikat", "null", "fk", "pulihkan"]
if len(sys.argv) != 2 or sys.argv[1] not in PERINTAH:
    print("Pemakaian: python lab_kualitas.py [" + " | ".join(PERINTAH) + "]")
    sys.exit(1)
perintah = sys.argv[1]

con = duckdb.connect("../analytics.duckdb")


def hitung(sql):
    return con.execute(sql).fetchone()[0]


def status():
    kondisi = {
        "raw.customers (baris)": hitung("SELECT COUNT(*) FROM raw.customers"),
        "customer_id duplikat": hitung(
            "SELECT COUNT(*) FROM (SELECT customer_id FROM raw.customers "
            "WHERE customer_id IS NOT NULL GROUP BY customer_id HAVING COUNT(*) > 1)"
        ),
        "customer_id NULL": hitung(
            "SELECT COUNT(*) FROM raw.customers WHERE customer_id IS NULL"
        ),
        "raw.orders (baris)": hitung("SELECT COUNT(*) FROM raw.orders"),
        "order dengan customer tidak ada": hitung(
            "SELECT COUNT(*) FROM raw.orders o "
            "LEFT JOIN raw.customers c ON o.customer_id = c.customer_id "
            "WHERE o.customer_id IS NOT NULL AND c.customer_id IS NULL"
        ),
    }
    print("=== Status raw ===")
    for k, v in kondisi.items():
        print(f"{k:<34} {v}")
    return kondisi


def bersih(k):
    return (
        k["customer_id duplikat"] == 0
        and k["customer_id NULL"] == 0
        and k["order dengan customer tidak ada"] == 0
    )


if perintah == "status":
    status()

elif perintah == "pulihkan":
    con.execute("""
        CREATE OR REPLACE TABLE raw.customers AS
        SELECT * FROM read_csv_auto('../data/customers.csv', HEADER=TRUE)
    """)
    con.execute("""
        CREATE OR REPLACE TABLE raw.orders AS
        SELECT * FROM read_csv_auto('../data/orders.csv', HEADER=TRUE)
        UNION ALL
        SELECT * FROM read_csv_auto('../data/orders_incremental.csv', HEADER=TRUE)
    """)
    print("raw.customers dan raw.orders dipulihkan dari CSV (orders = 500 + 50).")
    status()

else:
    if not bersih(status()):
        print("\nBERHENTI: raw belum bersih. Jalankan 'python lab_kualitas.py pulihkan' dulu.")
        con.close()
        sys.exit(1)

    if perintah == "duplikat":
        # customer yang sudah ada dimasukkan lagi
        con.execute("""
            INSERT INTO raw.customers
            SELECT * FROM raw.customers WHERE customer_id IS NOT NULL LIMIT 1
        """)
        print("\nDisuntikkan: 1 customer duplikat ke raw.customers")
    elif perintah == "null":
        # satu row dengan customer_id NULL
        con.execute("""
            INSERT INTO raw.customers
            SELECT * REPLACE (NULL AS customer_id)
            FROM raw.customers WHERE customer_id IS NOT NULL LIMIT 1
        """)
        print("\nDisuntikkan: 1 customer dengan customer_id NULL ke raw.customers")
    elif perintah == "fk":
        # order dengan customer C999 yang tidak ada
        con.execute("""
            INSERT INTO raw.orders
            SELECT * REPLACE ('O_TEST_FK' AS order_id, 'C999' AS customer_id)
            FROM raw.orders LIMIT 1
        """)
        print("\nDisuntikkan: 1 order dengan customer_id = C999 ke raw.orders")
    print()
    status()

con.close()