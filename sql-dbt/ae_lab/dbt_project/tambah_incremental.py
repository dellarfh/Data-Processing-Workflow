import sys
import duckdb

CSV = "../data/orders_incremental.csv"
SUMBER = f"read_csv_auto('{CSV}', HEADER=TRUE)"

con = duckdb.connect("../analytics.duckdb")

sebelum = con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0]
print(f"raw.orders sebelum insert : {sebelum}")

n, tmin, tmax, n_unik = con.execute(
    f"SELECT COUNT(*), MIN(order_date), MAX(order_date), COUNT(DISTINCT order_id) FROM {SUMBER}"
).fetchone()
print(f"File incremental          : {n} baris, {n_unik} order_id unik")
print(f"Rentang order_date        : {tmin} s.d. {tmax}")

irisan = con.execute(
    f"SELECT COUNT(*) FROM {SUMBER} WHERE order_id IN (SELECT order_id FROM raw.orders)"
).fetchone()[0]
print(f"order_id sudah ada di raw : {irisan}")

# Pastikan nama dan urutan kolom sama, karena INSERT ... SELECT * bergantung pada urutan kolom
kolom_raw = [r[0] for r in con.execute("DESCRIBE raw.orders").fetchall()]
kolom_csv = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {SUMBER}").fetchall()]
if kolom_raw != kolom_csv:
    print("BERHENTI: kolom raw.orders dan CSV berbeda")
    print("raw.orders :", kolom_raw)
    print("csv        :", kolom_csv)
    con.close()
    sys.exit(1)

if irisan > 0:
    print("BERHENTI: data ini sudah ada di raw.orders (kemungkinan sudah pernah di-insert). Tidak ada yang diubah.")
    con.close()
    sys.exit(0)

# Perintah dari modul bagian 23
con.execute(f"INSERT INTO raw.orders SELECT * FROM {SUMBER}")

sesudah = con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0]
print(f"raw.orders sesudah insert : {sesudah}")
con.close()