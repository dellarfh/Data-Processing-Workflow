import duckdb

con = duckdb.connect()

con.execute("""
    CREATE VIEW raw_orders AS
    SELECT * FROM read_csv_auto('data/orders.csv', HEADER=TRUE)
""")

# STAGING (modul 9.2): transformasi ringan
con.execute("""
    CREATE VIEW stg_orders AS
    SELECT
        order_id,
        customer_id,
        product_id,
        CAST(order_date AS DATE) AS order_date,
        quantity,
        unit_price
    FROM raw_orders
""")

# INTERMEDIATE (modul 9.3): business logic reusable
con.execute("""
    CREATE VIEW int_sales AS
    SELECT
        order_id,
        order_date,
        customer_id,
        product_id,
        quantity,
        unit_price,
        quantity * unit_price AS sales_amount
    FROM stg_orders
""")

print("=== Tipe kolom stg_orders ===")
tipe = con.execute("DESCRIBE stg_orders").df()
print(tipe[["column_name", "column_type"]].to_string(index=False))

print("\n=== 5 baris pertama int_sales ===")
print(con.execute("SELECT * FROM int_sales LIMIT 5").df().to_string(index=False))