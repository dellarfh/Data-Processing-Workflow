import duckdb

con = duckdb.connect()

con.execute("""
    CREATE TABLE target AS
    SELECT * FROM (VALUES
        ('O1', DATE '2026-06-29', 2),
        ('O2', DATE '2026-06-30', 1),
        ('O3', DATE '2026-06-30', 5)
    ) t(order_id, order_date, quantity)
""")

# O2 berubah (quantity 1 -> 4), O3 dikirim ulang persis sama, O4 baru
con.execute("""
    CREATE TABLE incoming AS
    SELECT * FROM (VALUES
        ('O2', DATE '2026-06-30', 4),
        ('O3', DATE '2026-06-30', 5),
        ('O4', DATE '2026-07-01', 3)
    ) t(order_id, order_date, quantity)
""")

# A: tanpa unique_key (hanya menambahkan baris)
con.execute("CREATE TABLE hasil_a AS SELECT * FROM target")
con.execute("INSERT INTO hasil_a SELECT * FROM incoming")

# B: dengan unique_key (baris dengan key sama diganti)
con.execute("CREATE TABLE hasil_b AS SELECT * FROM target")
con.execute("DELETE FROM hasil_b WHERE order_id IN (SELECT order_id FROM incoming)")
con.execute("INSERT INTO hasil_b SELECT * FROM incoming")

for nama, judul in [("hasil_a", "A. TANPA unique_key"), ("hasil_b", "B. DENGAN unique_key")]:
    print(f"=== {judul} ===")
    print(con.execute(f"SELECT * FROM {nama} ORDER BY order_id, quantity").df().to_string(index=False))
    r = con.execute(f"SELECT COUNT(*), SUM(quantity) FROM {nama}").fetchone()
    print(f"jumlah baris = {r[0]}, total quantity = {r[1]}\n")