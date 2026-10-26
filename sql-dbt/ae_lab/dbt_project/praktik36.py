import duckdb

con = duckdb.connect()

con.execute("CREATE VIEW raw_products AS SELECT * FROM read_csv_auto('../data/products.csv', HEADER=TRUE)")
con.execute("CREATE VIEW raw_orders AS SELECT * FROM read_csv_auto('../data/orders.csv', HEADER=TRUE)")

# ---- STAR ----
con.execute("""
    CREATE VIEW dim_product_star AS
    SELECT product_id, product_name, category_id, category_name, department, unit_price
    FROM raw_products
""")

# ---- SNOWFLAKE ----
con.execute("CREATE VIEW dim_department AS SELECT DISTINCT department FROM raw_products")
con.execute("""
    CREATE VIEW dim_category AS
    SELECT DISTINCT category_id, category_name, department FROM raw_products
""")
con.execute("""
    CREATE VIEW dim_product_snow AS
    SELECT product_id, product_name, category_id, unit_price FROM raw_products
""")

# ---- Apakah pemisahan valid? ----
n_prod, n_cat, n_dep = con.execute(
    "SELECT COUNT(*), COUNT(DISTINCT category_id), COUNT(DISTINCT department) FROM raw_products"
).fetchone()
n_tidak_konsisten = con.execute("""
    SELECT COUNT(*) FROM (
        SELECT category_id FROM raw_products
        GROUP BY category_id
        HAVING COUNT(DISTINCT category_name) > 1 OR COUNT(DISTINCT department) > 1
    )
""").fetchone()[0]
n_dim_category = con.execute("SELECT COUNT(*) FROM dim_category").fetchone()[0]

print("=== Struktur data ===")
print(f"jumlah product            : {n_prod}")
print(f"jumlah category           : {n_cat}")
print(f"jumlah department         : {n_dep}")
print(f"category tidak konsisten  : {n_tidak_konsisten}  (harus 0 agar snowflake valid)")
print(f"baris dim_category        : {n_dim_category}")

print("\n=== Ukuran kasar redundansi (nilai category_name + department yang disimpan) ===")
print(f"Star      : {n_prod * 2}   ({n_prod} product x 2 kolom)")
print(f"Snowflake : {n_dim_category * 2 + n_dep}   ({n_dim_category} category x 2 kolom + {n_dep} department)")

# ---- Query yang sama pada kedua desain ----
q_star = """
    SELECT p.department, p.category_name, ROUND(SUM(o.quantity * o.unit_price), 2) AS total_sales
    FROM raw_orders o
    JOIN dim_product_star p ON o.product_id = p.product_id
    GROUP BY p.department, p.category_name
"""
q_snow = """
    SELECT d.department, c.category_name, ROUND(SUM(o.quantity * o.unit_price), 2) AS total_sales
    FROM raw_orders o
    JOIN dim_product_snow p ON o.product_id = p.product_id
    JOIN dim_category c ON p.category_id = c.category_id
    JOIN dim_department d ON c.department = d.department
    GROUP BY d.department, c.category_name
"""

print("\n=== Jumlah JOIN untuk mendapatkan department/kategori ===")
print(f"Star      : {q_star.upper().count('JOIN')} join")
print(f"Snowflake : {q_snow.upper().count('JOIN')} join")

selisih_1 = con.execute(f"SELECT * FROM ({q_star}) EXCEPT SELECT * FROM ({q_snow})").fetchall()
selisih_2 = con.execute(f"SELECT * FROM ({q_snow}) EXCEPT SELECT * FROM ({q_star})").fetchall()
print("\n=== Hasil kedua desain ===")
print("HASIL SAMA: PASS" if not selisih_1 and not selisih_2 else "HASIL SAMA: FAIL")

print("\n=== Total penjualan per department (dari desain Snowflake) ===")
print(con.execute(f"""
    SELECT department, ROUND(SUM(total_sales), 2) AS total_sales
    FROM ({q_snow}) GROUP BY department ORDER BY total_sales DESC
""").df().to_string(index=False))