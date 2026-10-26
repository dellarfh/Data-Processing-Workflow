import sys
import duckdb

# Pemakaian: python cek_ringkasan.py <nama_tabel>
tabel = sys.argv[1]

con = duckdb.connect("../analytics.duckdb", read_only=True)

hasil = con.execute(
    "SELECT table_schema FROM information_schema.tables WHERE table_name = ?",
    [tabel],
).fetchone()

if hasil is None:
    print(f"Tabel '{tabel}' tidak ditemukan")
else:
    skema = hasil[0]
    print(f"=== Ringkasan {skema}.{tabel} ===")
    print(con.execute(f"""
        SELECT
            COUNT(*)                              AS jumlah_baris,
            COUNT(DISTINCT order_id)              AS order_id_unik,
            SUM(quantity)                         AS total_quantity,
            ROUND(SUM(sales_amount), 2)           AS total_sales_amount
        FROM "{skema}"."{tabel}"
    """).df().to_string(index=False))

con.close()