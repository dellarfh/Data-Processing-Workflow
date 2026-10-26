import sys
import duckdb

# read_only supaya tidak mengunci database
con = duckdb.connect("../analytics.duckdb", read_only=True)

print("=== Semua tabel/view di database ===")
daftar = con.execute("""
    SELECT table_schema, table_name, table_type
    FROM information_schema.tables
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
    ORDER BY 1, 2
""").fetchall()
for skema, nama, tipe in daftar:
    print(f"{skema:<12} {nama:<24} {tipe}")

# Hitung baris untuk nama model yang diberikan sebagai argumen
for nama in sys.argv[1:]:
    cocok = [s for s, n, _ in daftar if n == nama]
    if not cocok:
        print(f"\n{nama}: TIDAK DITEMUKAN")
        continue
    skema = cocok[0]
    n = con.execute(f'SELECT COUNT(*) FROM "{skema}"."{nama}"').fetchone()[0]
    print(f"\n{skema}.{nama}: {n} baris")
    print(con.execute(f'SELECT * FROM "{skema}"."{nama}" LIMIT 3').df().to_string(index=False))

con.close()