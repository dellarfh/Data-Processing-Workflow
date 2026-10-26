from sqlalchemy import create_engine, text

# Konfigurasi Koneksi
DB_URI = "postgresql://admin:secretpassword@localhost:5432/olist_db"
engine = create_engine(DB_URI)

# Query SQL untuk tabel pertama
query_create_customers = text("""
CREATE TABLE IF NOT EXISTS olist_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix INT,
    customer_city VARCHAR(50),
    customer_state VARCHAR(5)
);
""")

# Query SQL untuk tabel kedua
query_create_orders = text("""
CREATE TABLE IF NOT EXISTS olist_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_status VARCHAR(50),
    order_purchase_timestamp VARCHAR(50),
    order_approved_at VARCHAR(50),
    order_delivered_carrier_date VARCHAR(50),
    order_delivered_customer_date VARCHAR(50),
    order_estimated_delivery_date VARCHAR(50)
);
""")

try:
    with engine.connect() as connection:
        # Eksekusi pembuatan kedua tabel secara berurutan
        connection.execute(query_create_customers)
        connection.execute(query_create_orders)
        connection.commit()
        print("✅ Tabel 'olist_customers' dan 'olist_orders' berhasil dibuat di database!")
except Exception as e:
    print(f"❌ Terjadi kesalahan saat membuat tabel: {e}")