import duckdb

con = duckdb.connect()  # database sementara di memori

# Membuat "tabel" raw_orders dari CSV (nama sama seperti query di modul)
con.execute("""
    CREATE VIEW raw_orders AS
    SELECT * FROM read_csv_auto('data/orders.csv', HEADER=TRUE)
""")

# Query dari modul bagian 8.1
query = """
SELECT
    customer_id,
    SUM(quantity * unit_price) AS total_sales
FROM raw_orders
GROUP BY customer_id
ORDER BY total_sales DESC
"""

hasil = con.execute(query).df()
print("=== Total sales per customer ===")
print(hasil.to_string(index=False))

# Pengecekan total agar sesuai angka validasi modul
cek = """
SELECT
    COUNT(*) AS jumlah_baris,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(quantity * unit_price), 2) AS total_sales
FROM raw_orders
"""
print("\n=== Pengecekan total ===")
print(con.execute(cek).df().to_string(index=False))