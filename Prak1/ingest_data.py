import pandas as pd
from sqlalchemy import create_engine

# Konfigurasi Koneksi
DB_URI = "postgresql://admin:secretpassword@localhost:5432/olist_db"
engine = create_engine(DB_URI)

try:
    print("Mulai membaca data CSV...")
    # Membaca kedua file CSV
    df_customers = pd.read_csv('./data/raw/olist_customers_dataset.csv')
    df_orders = pd.read_csv('./data/raw/olist_orders_dataset.csv')
    print("✅ Kedua data CSV berhasil dibaca!")
    
    print("Mengirim data ke database...")
    # Memasukkan data ke tabel olist_customers
    df_customers.to_sql('olist_customers', con=engine, if_exists='append', index=False)
    print("✅ Data customers berhasil dimasukkan!")
    
    # Memasukkan data ke tabel olist_orders
    df_orders.to_sql('olist_orders', con=engine, if_exists='append', index=False)
    print("✅ Data orders berhasil dimasukkan!")
    
    print("🎉 Semua proses ingest data selesai dengan sukses!")
except Exception as e:
    print(f"❌ Terjadi kesalahan saat ingest data: {e}")