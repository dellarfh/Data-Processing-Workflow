from sqlalchemy import create_engine

# Format URI: postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]
DB_URI = "postgresql://admin:secretpassword@localhost:5432/olist_db"

try:
    engine = create_engine(DB_URI)
    connection = engine.connect()
    print("Berhasil terhubung ke database PostgreSQL!")
    connection.close()
except Exception as e:
    print(f"Gagal terhubung: {e}")