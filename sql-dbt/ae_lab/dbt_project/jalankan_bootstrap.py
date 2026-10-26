import duckdb

# Folder kerja harus ae_lab\dbt_project agar path ../data/... benar
con = duckdb.connect("../analytics.duckdb")

with open("../scripts/bootstrap_raw.sql", encoding="utf-8") as f:
    sql = f.read()

for statement in sql.split(";"):
    if statement.strip():
        con.execute(statement)

print("=== Verifikasi jumlah baris raw ===")
for tabel in ["customers", "products", "orders", "payments"]:
    n = con.execute(f"SELECT COUNT(*) FROM raw.{tabel}").fetchone()[0]
    print(f"raw.{tabel:<10} {n}")

con.close()