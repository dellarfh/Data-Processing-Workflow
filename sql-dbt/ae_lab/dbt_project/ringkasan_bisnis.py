import duckdb

con = duckdb.connect("../analytics.duckdb", read_only=True)
s = con.execute(
    "SELECT table_schema FROM information_schema.tables WHERE table_name = 'sales_mart'"
).fetchone()[0]

for judul, kolom in [("bulan", "year, month"), ("segment", "segment"),
                     ("region", "region"), ("category", "category")]:
    print(f"=== Total penjualan per {judul} ===")
    print(con.execute(f"""
        SELECT {kolom},
               ROUND(SUM(total_sales), 2) AS total_sales,
               SUM(total_quantity)        AS total_quantity
        FROM "{s}".sales_mart
        GROUP BY {kolom} ORDER BY {kolom}
    """).df().to_string(index=False))
    print()

mart = con.execute(f'SELECT ROUND(SUM(total_sales),2) FROM "{s}".sales_mart').fetchone()[0]
src = con.execute("SELECT ROUND(SUM(quantity * unit_price),2) FROM raw.orders").fetchone()[0]
print(f"Total mart  : {mart}")
print(f"Total source: {src}")
print("REKONSILIASI MART vs SOURCE: PASS" if mart == src else "REKONSILIASI MART vs SOURCE: FAIL")
con.close()