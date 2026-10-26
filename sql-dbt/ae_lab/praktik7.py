import duckdb

con = duckdb.connect()

# ---------- RAW ----------
for t in ["customers", "products", "orders"]:
    con.execute(f"""
        CREATE VIEW raw_{t} AS
        SELECT * FROM read_csv_auto('data/{t}.csv', HEADER=TRUE)
    """)

# ---------- 13.1 Staging customer ----------
con.execute("""
    CREATE VIEW stg_customers AS
    SELECT customer_id, customer_name, segment, region
    FROM raw_customers
""")

# ---------- 13.2 Staging product ----------
con.execute("""
    CREATE VIEW stg_products AS
    SELECT product_id, product_name, category_id, category_name,
           department, unit_price
    FROM raw_products
""")

# ---------- 13.3 Staging orders ----------
con.execute("""
    CREATE VIEW stg_orders AS
    SELECT order_id, customer_id, product_id,
           CAST(order_date AS DATE) AS order_date,
           quantity, unit_price
    FROM raw_orders
""")

# ---------- Dimension ----------
con.execute("""
    CREATE VIEW dim_customer AS
    SELECT customer_id, customer_name, segment, region
    FROM stg_customers
""")
con.execute("""
    CREATE VIEW dim_product AS
    SELECT product_id, product_name, category_id, category_name,
           department, unit_price
    FROM stg_products
""")
con.execute("""
    CREATE VIEW dim_date AS
    SELECT DISTINCT
        order_date AS full_date,
        EXTRACT(year FROM order_date)    AS year,
        EXTRACT(month FROM order_date)   AS month,
        EXTRACT(quarter FROM order_date) AS quarter
    FROM stg_orders
""")

# ---------- 13.4 Fact ----------
con.execute("""
    CREATE VIEW fct_sales AS
    SELECT order_id, order_date, customer_id, product_id,
           quantity, unit_price,
           ROUND(quantity * unit_price, 2) AS sales_amount
    FROM stg_orders
""")

# ---------- 13.5 Analytical mart ----------
con.execute("""
    CREATE VIEW sales_mart AS
    SELECT
        d.year,
        d.month,
        c.segment,
        c.region,
        p.category_name AS category,
        SUM(f.sales_amount) AS total_sales,
        SUM(f.quantity)     AS total_quantity
    FROM fct_sales f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    JOIN dim_product  p ON f.product_id  = p.product_id
    JOIN dim_date     d ON f.order_date  = d.full_date
    GROUP BY d.year, d.month, c.segment, c.region, p.category_name
""")

# ---------- Hasil mart ----------
print("=== 15 baris pertama sales_mart ===")
print(con.execute("""
    SELECT * FROM sales_mart
    ORDER BY year, month, total_sales DESC
    LIMIT 15
""").df().to_string(index=False))

# ---------- Ringkasan fact ----------
print("\n=== Ringkasan fct_sales ===")
print(con.execute("""
    SELECT COUNT(*) AS rows,
           SUM(quantity) AS quantity,
           ROUND(SUM(sales_amount), 2) AS sales_amount
    FROM fct_sales
""").df().to_string(index=False))

# ---------- 13.6 Validasi ----------
def q(sql):
    return con.execute(sql).fetchone()[0]

def check(nama, ok):
    print(f"{nama:<22} {'PASS' if ok else 'FAIL'}")

print("\n=== Validasi ===")
check("orders_count",
      q("SELECT COUNT(*) FROM raw_orders") == 500)
check("customers_unique",
      q("SELECT COUNT(*) - COUNT(DISTINCT customer_id) FROM dim_customer") == 0)
check("customers_not_null",
      q("SELECT COUNT(*) FROM dim_customer WHERE customer_id IS NULL") == 0)
check("fk_customer",
      q("""SELECT COUNT(*) FROM fct_sales f
           LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
           WHERE c.customer_id IS NULL""") == 0)
check("fk_product",
      q("""SELECT COUNT(*) FROM fct_sales f
           LEFT JOIN dim_product p ON f.product_id = p.product_id
           WHERE p.product_id IS NULL""") == 0)
check("mart_rows",
      q("SELECT COUNT(*) FROM sales_mart") > 0)
check("sales_positive",
      q("SELECT COUNT(*) FROM fct_sales WHERE sales_amount <= 0") == 0)

# Pengecekan tambahan (bukan dari modul): mart harus sama dengan fact
check("mart_sama_dengan_fact",
      abs(q("SELECT SUM(total_sales) FROM sales_mart")
          - q("SELECT SUM(sales_amount) FROM fct_sales")) < 0.01)