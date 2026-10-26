import duckdb

con = duckdb.connect()

con.execute("""
    CREATE VIEW raw_products AS
    SELECT * FROM read_csv_auto('data/products.csv', HEADER=TRUE)
""")

print("=== Ringkasan produk dan kategori ===")
print(con.execute("""
    SELECT
        COUNT(*)                        AS jumlah_product,
        COUNT(DISTINCT category_id)     AS jumlah_category_id,
        COUNT(DISTINCT department)      AS jumlah_department,
        (SELECT COUNT(*) FROM (
            SELECT DISTINCT category_id, category_name, department
            FROM raw_products
        ))                              AS kombinasi_unik_kategori
    FROM raw_products
""").df().to_string(index=False))

print("\n=== Isi dim_category (hasil snowflake) ===")
print(con.execute("""
    SELECT DISTINCT category_id, category_name, department
    FROM raw_products
    ORDER BY category_id
""").df().to_string(index=False))