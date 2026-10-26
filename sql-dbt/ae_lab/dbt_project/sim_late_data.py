import duckdb

con = duckdb.connect()

con.execute("""
    CREATE TABLE incoming AS
    SELECT * FROM (VALUES
        ('O90', DATE '2026-06-25'),  -- terlambat masuk (lebih lama dari watermark)
        ('O91', DATE '2026-07-01'),  -- data baru biasa
        ('O92', DATE '2026-06-30')   -- tepat di tanggal watermark
    ) t(order_id, order_date)
""")

watermark = "DATE '2026-06-30'"

strategi = {
    "order_date >  MAX(order_date)": f"order_date > {watermark}",
    "order_date >= MAX(order_date)  (model kita)": f"order_date >= {watermark}",
    "order_date >= MAX - 7 hari  (lookback)": f"order_date >= CAST({watermark} - INTERVAL 7 DAY AS DATE)",
}

print(f"Watermark simulasi: 2026-06-30")
print("Record masuk: O90 (2026-06-25, terlambat), O91 (2026-07-01, baru), O92 (2026-06-30)\n")

for nama, kondisi in strategi.items():
    ids = [r[0] for r in con.execute(
        f"SELECT order_id FROM incoming WHERE {kondisi} ORDER BY order_id"
    ).fetchall()]
    terlewat = [x for x in ["O90", "O91", "O92"] if x not in ids]
    print(f"{nama}")
    print(f"   tertangkap: {ids}")
    print(f"   TERLEWAT  : {terlewat}\n")

# Bagian tambahan: watermark nyata di database praktikum (jika ada)
try:
    real = duckdb.connect("../analytics.duckdb", read_only=True)
    s = real.execute(
        "SELECT table_schema FROM information_schema.tables WHERE table_name='fct_sales_incremental'"
    ).fetchone()[0]
    wm = real.execute(f'SELECT MAX(order_date) FROM "{s}".fct_sales_incremental').fetchone()[0]
    print(f"Watermark NYATA saat ini di fct_sales_incremental: {wm}")
    real.close()
except Exception as e:
    print("Watermark nyata tidak dapat dibaca:", e)