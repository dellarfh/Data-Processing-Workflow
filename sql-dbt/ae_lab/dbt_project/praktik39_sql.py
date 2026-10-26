import duckdb

con = duckdb.connect("../analytics.duckdb", read_only=True)


def skema(t):
    return con.execute(
        "SELECT table_schema FROM information_schema.tables WHERE table_name = ?", [t]
    ).fetchone()[0]


f, c = skema("fct_sales"), skema("dim_customer")

print("=== Filtering: order Juli 2026 (WHERE) ===")
print(con.execute(f"""
    SELECT order_id, order_date, quantity, sales_amount
    FROM "{f}".fct_sales
    WHERE order_date >= DATE '2026-07-01'
    ORDER BY order_date, order_id LIMIT 5
""").df().to_string(index=False))

print("\n=== Join + Aggregation + Transformation: 5 customer teratas ===")
print(con.execute(f"""
    SELECT cu.customer_name, cu.region, ROUND(SUM(fs.sales_amount), 2) AS total_sales
    FROM "{f}".fct_sales fs
    JOIN "{c}".dim_customer cu ON fs.customer_id = cu.customer_id
    GROUP BY cu.customer_name, cu.region
    ORDER BY total_sales DESC LIMIT 5
""").df().to_string(index=False))
con.close()