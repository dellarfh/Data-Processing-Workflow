import duckdb

con = duckdb.connect("../analytics.duckdb", read_only=True)

hasil = con.execute(
    "SELECT table_schema FROM information_schema.tables WHERE table_name = 'fct_sales_incremental'"
).fetchone()
if hasil is None:
    print("fct_sales_incremental tidak ditemukan. Jalankan dbt run dulu.")
    raise SystemExit
s = hasil[0]

raw_n = con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0]
tgt_n = con.execute(f'SELECT COUNT(*) FROM "{s}".fct_sales_incremental').fetchone()[0]
print(f"raw.orders            : {raw_n}")
print(f"fct_sales_incremental : {tgt_n}")

print("\n=== Jumlah baris per bulan ===")
print(con.execute(f"""
    SELECT strftime(order_date, '%Y-%m') AS bulan, COUNT(*) AS jumlah_baris
    FROM "{s}".fct_sales_incremental
    GROUP BY 1 ORDER BY 1
""").df().to_string(index=False))

hilang = con.execute(f"""
    SELECT COUNT(*) FROM raw.orders r
    LEFT JOIN "{s}".fct_sales_incremental f ON r.order_id = f.order_id
    WHERE f.order_id IS NULL
""").fetchone()[0]
print(f"\nOrder di raw yang belum masuk ke target: {hilang}")
print("SINKRON: PASS" if raw_n == tgt_n and hilang == 0 else "SINKRON: FAIL")

con.close()