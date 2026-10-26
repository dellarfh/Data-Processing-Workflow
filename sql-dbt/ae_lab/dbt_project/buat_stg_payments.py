from pathlib import Path
import duckdb

target = Path("models/staging/stg_payments.sql")
if target.exists():
    print("stg_payments.sql sudah ada, tidak ditimpa. Isinya:\n")
    print(target.read_text(encoding="utf-8"))
    raise SystemExit

con = duckdb.connect("../analytics.duckdb", read_only=True)
kolom = con.execute("DESCRIBE raw.payments").fetchall()
con.close()

print("Kolom raw.payments:")
for nama, tipe, *_ in kolom:
    print(f"  {nama}: {tipe}")

sql = "SELECT\n" + ",\n".join(f"    {nama}" for nama, *_ in kolom)
sql += "\nFROM {{ source('raw', 'payments') }}\n"

target.write_text(sql, encoding="utf-8")
print(f"\nDitulis: {target}\n")
print(sql)