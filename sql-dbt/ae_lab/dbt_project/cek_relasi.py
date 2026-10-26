import duckdb

con = duckdb.connect("../analytics.duckdb", read_only=True)

def skema_dari(tabel):
    r = con.execute(
        "SELECT table_schema FROM information_schema.tables WHERE table_name = ?",
        [tabel],
    ).fetchone()
    return r[0] if r else None

s_fact, s_cust, s_prod = (skema_dari(t) for t in ["fct_sales", "dim_customer", "dim_product"])

print("=== Foreign key customer tanpa pasangan di dim_customer ===")
print(con.execute(f"""
    SELECT f.customer_id
    FROM "{s_fact}".fct_sales f
    LEFT JOIN "{s_cust}".dim_customer c ON f.customer_id = c.customer_id
    WHERE c.customer_id IS NULL
""").df().to_string(index=False))

print("\n=== Foreign key product tanpa pasangan di dim_product ===")
print(con.execute(f"""
    SELECT f.product_id
    FROM "{s_fact}".fct_sales f
    LEFT JOIN "{s_prod}".dim_product p ON f.product_id = p.product_id
    WHERE p.product_id IS NULL
""").df().to_string(index=False))

print("\n=== customer_id duplikat di dim_customer ===")
print(con.execute(f"""
    SELECT customer_id, COUNT(*) AS n
    FROM "{s_cust}".dim_customer
    GROUP BY customer_id
    HAVING COUNT(*) > 1
""").df().to_string(index=False))

con.close()