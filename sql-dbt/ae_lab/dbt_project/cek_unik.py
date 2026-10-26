import sys
import duckdb

# Pemakaian: python cek_unik.py <nama_tabel> <nama_kolom>
tabel, kolom = sys.argv[1], sys.argv[2]

con = duckdb.connect("../analytics.duckdb", read_only=True)

hasil = con.execute(
    "SELECT table_schema FROM information_schema.tables WHERE table_name = ?",
    [tabel],
).fetchone()

if hasil is None:
    print(f"Tabel '{tabel}' tidak ditemukan")
else:
    skema = hasil[0]
    total, unik = con.execute(
        f'SELECT COUNT(*), COUNT(DISTINCT "{kolom}") FROM "{skema}"."{tabel}"'
    ).fetchone()
    print(f"{skema}.{tabel}.{kolom}: total={total}, unik={unik}")
    print("UNIK: PASS" if total == unik else "UNIK: FAIL (ada duplikat)")

con.close()