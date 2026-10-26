import json
from pathlib import Path
import duckdb

hasil = []


def cek(nama, ok, info=""):
    hasil.append(ok)
    print(f"{nama:<48} {'PASS' if ok else 'FAIL'}  {info}")


models = Path("models")


def temukan(nama):
    f = list(models.rglob(nama))
    return f[0] if f else None


print("=== 10 file model wajib (source/ref) ===")
wajib = ["stg_orders", "stg_customers", "stg_products", "stg_payments",
         "dim_customer", "dim_product", "dim_date",
         "int_sales", "fct_sales", "sales_mart"]
for m in wajib:
    p = temukan(f"{m}.sql")
    if p is None:
        cek(f"{m}.sql ada", False)
        continue
    teks = p.read_text(encoding="utf-8").lower()
    if m.startswith("stg_"):
        cek(f"{m}.sql memakai source()", "source(" in teks)
    else:
        cek(f"{m}.sql memakai ref()", "ref(" in teks)

print("\n=== Incremental model ===")
p = temukan("fct_sales_incremental.sql")
teks = p.read_text(encoding="utf-8").lower() if p else ""
cek("fct_sales_incremental.sql ada", p is not None)
cek("materialized incremental + unique_key",
    "incremental" in teks and "unique_key" in teks)
cek("memakai is_incremental()", "is_incremental()" in teks)

print("\n=== schema.yml ===")
sy = (models / "schema.yml").read_text(encoding="utf-8").lower()
for kata in ["unique", "not_null", "relationships", "description"]:
    cek(f"schema.yml memuat {kata}", kata in sy)

print("\n=== Data di database ===")
con = duckdb.connect("../analytics.duckdb", read_only=True)


def skema(tabel):
    r = con.execute(
        "SELECT table_schema FROM information_schema.tables WHERE table_name = ?",
        [tabel]).fetchone()
    return r[0] if r else None


s_mart, s_inc = skema("sales_mart"), skema("fct_sales_incremental")
n_mart = con.execute(f'SELECT COUNT(*) FROM "{s_mart}".sales_mart').fetchone()[0] if s_mart else 0
cek("sales_mart menghasilkan data", n_mart > 0, f"{n_mart} baris")

raw_n = con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0]
cek("raw.orders = 550", raw_n == 550, str(raw_n))
if s_inc:
    n_inc, n_unik = con.execute(
        f'SELECT COUNT(*), COUNT(DISTINCT order_id) FROM "{s_inc}".fct_sales_incremental').fetchone()
    cek("incremental = 550 dan unik", n_inc == 550 and n_unik == 550, f"{n_inc}/{n_unik}")
    n_juli = con.execute(
        f'SELECT COUNT(*) FROM "{s_inc}".fct_sales_incremental '
        "WHERE CAST(order_date AS DATE) >= DATE '2026-07-01'").fetchone()[0]
    cek("50 order tambahan (Juli) ikut terproses", n_juli == 50, str(n_juli))
else:
    cek("fct_sales_incremental ada di database", False)
con.close()

print("\n=== Dokumentasi dan lineage ===")
target = Path("target")
for f in ["manifest.json", "catalog.json", "index.html"]:
    cek(f"target/{f} ada", (target / f).exists())

mf = target / "manifest.json"
if mf.exists():
    pm = json.loads(mf.read_text(encoding="utf-8")).get("parent_map", {})
    kunci = [k for k in pm if k.startswith("model.") and k.endswith(".sales_mart")]
    induk = {x.split(".")[-1] for x in pm[kunci[0]]} if kunci else set()
    perlu = {"fct_sales", "dim_customer", "dim_product", "dim_date"}
    cek("lineage sales_mart (4 model hulu)", perlu <= induk, ", ".join(sorted(induk)))

print("\n=== Hasil test terakhir (target/run_results.json) ===")
rr = target / "run_results.json"
if rr.exists():
    jenis = {"unique_": [0, 0], "not_null_": [0, 0], "relationships_": [0, 0]}
    for r in json.loads(rr.read_text(encoding="utf-8")).get("results", []):
        uid = r.get("unique_id", "")
        if not uid.startswith("test."):
            continue
        nama = uid.split(".")[2]
        for k in jenis:
            if nama.startswith(k):
                jenis[k][1] += 1
                if r.get("status") == "pass":
                    jenis[k][0] += 1
    for k, (ok_n, total) in jenis.items():
        cek(f"test {k[:-1]} PASS semua", total > 0 and ok_n == total, f"{ok_n}/{total}")
    print("(Jika total 0: jalankan 'dbt build' lagi sebagai perintah dbt TERAKHIR.)")
else:
    cek("run_results.json ada", False)

print(f"\nTOTAL: {sum(hasil)}/{len(hasil)} PASS")