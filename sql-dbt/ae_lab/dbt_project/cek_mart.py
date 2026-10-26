import duckdb

con = duckdb.connect("../analytics.duckdb", read_only=True)

def skema_dari(tabel):
    return con.execute(
        "SELECT table_schema FROM information_schema.tables WHERE table_name = ?",
        [tabel],
    ).fetchone()[0]

s_mart = skema_dari("sales_mart")
s_fact = skema_dari("fct_sales")

print("=== 20 baris pertama sales_mart ===")
print(con.execute(f"""
    SELECT *
    FROM "{s_mart}".sales_mart
    ORDER BY year, month, total_sales DESC
    LIMIT 20
""").df().to_string(index=False))

jumlah = con.execute(f'SELECT COUNT(*) FROM "{s_mart}".sales_mart').fetchone()[0]
print(f"\nJumlah baris sales_mart: {jumlah}")

print("\n=== Total penjualan per bulan ===")
print(con.execute(f"""
    SELECT year, month,
           ROUND(SUM(total_sales), 2) AS total_sales,
           SUM(total_quantity)        AS total_quantity
    FROM "{s_mart}".sales_mart
    GROUP BY year, month
    ORDER BY year, month
""").df().to_string(index=False))

print("\n=== Rekonsiliasi mart vs fact ===")
m = con.execute(f'SELECT ROUND(SUM(total_sales),2), SUM(total_quantity) FROM "{s_mart}".sales_mart').fetchone()
f = con.execute(f'SELECT ROUND(SUM(sales_amount),2), SUM(quantity) FROM "{s_fact}".fct_sales').fetchone()
print(f"mart: sales={m[0]}, quantity={m[1]}")
print(f"fact: sales={f[0]}, quantity={f[1]}")
print("REKONSILIASI: PASS" if m == f else "REKONSILIASI: FAIL")

con.close()