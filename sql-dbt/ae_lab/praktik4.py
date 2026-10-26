import duckdb

con = duckdb.connect()

con.execute("""
    CREATE VIEW raw_orders AS
    SELECT * FROM read_csv_auto('data/orders.csv', HEADER=TRUE)
""")

# 1) Verifikasi grain pada data nyata
print("=== Verifikasi grain orders ===")
print(con.execute("""
    SELECT
        COUNT(*) AS jumlah_baris,
        COUNT(DISTINCT order_id) AS jumlah_order_id_unik,
        COUNT(*) - COUNT(DISTINCT order_id) AS selisih
    FROM raw_orders
""").df().to_string(index=False))

# 2) Demo double counting (data ilustrasi, bukan dari dataset)
print("\n=== Demo double counting ===")
print(con.execute("""
    WITH lines AS (
        SELECT * FROM (VALUES
            ('O00001', 'Product A', 100),
            ('O00001', 'Product B', 200),
            ('O00001', 'Product C', 300)
        ) AS t(order_id, product, line_sales)
    ),
    orders AS (
        SELECT 'O00001' AS order_id, 600 AS order_total
    )
    SELECT
        SUM(l.line_sales)           AS benar_per_order_line,
        SUM(o.order_total)          AS salah_double_count,
        COUNT(*)                    AS jumlah_baris,
        COUNT(DISTINCT l.order_id)  AS jumlah_order
    FROM lines l
    JOIN orders o ON l.order_id = o.order_id
""").df().to_string(index=False))