# Modul Praktikum Analytics Engineering: SQL & dbt

---

## 1. Tujuan Praktikum

Praktikum ini menerjemahkan seluruh kompetensi pada outline menjadi aktivitas yang dapat dijalankan.

Setelah menyelesaikan praktikum, peserta diharapkan mampu:

1. Menjelaskan posisi Analytics Engineering pada alur data modern.
2. Membedakan raw, staging, intermediate, dan marts.
3. Menentukan **grain**, fact table, dimension table, measure, primary key, dan foreign key.
4. Mendesain **Star Schema** dan **Snowflake Schema**.
5. Menulis SQL transformasi untuk data warehouse.
6. Membuat project dbt.
7. Menggunakan `source()` dan `ref()`.
8. Membuat model staging, intermediate, dimension, fact, dan mart.
9. Membuat incremental model.
10. Memahami unique key, watermark, late-arriving data, update, duplicate, dan merge strategy.
11. Mengimplementasikan `unique`, `not_null`, dan `relationships`.
12. Membuat dokumentasi model dan kolom.
13. Menghasilkan lineage graph dengan dbt docs.
14. Mengevaluasi kualitas model sebelum digunakan untuk analitik.

Kompetensi tersebut mengikuti outline yang menempatkan Analytics Engineering sebagai lapisan antara Data Warehouse dan Data Models/BI serta menekankan dimensional modeling, testing, dan dokumentasi. 

---

# 2. Studi Kasus

## 2.1 Skenario

Kita bekerja sebagai Analytics Engineer pada perusahaan retail teknologi. Perusahaan memiliki data operasional:

```text
raw.customers
raw.products
raw.orders
raw.payments
```

Manajemen membutuhkan analisis:

- total sales per customer;
- total sales per product;
- total sales per month;
- sales berdasarkan customer segment;
- sales berdasarkan region;
- sales berdasarkan product category.

Data harus:

- memiliki model dimensional;
- dapat ditelusuri dependency-nya;
- memiliki automated tests;
- terdokumentasi;
- mampu menerima transaksi baru secara incremental.

Kasus ini mengikuti studi kasus terpadu pada outline: `orders`, `customers`, `products`, dan `payments`, dengan target analitik penjualan serta kebutuhan testing, dokumentasi, dan incremental processing.

---

# 3. Struktur Materi Praktikum

```text
01  Persiapan lingkungan
02  Mengenal dataset
03  SQL dasar transformasi
04  Layer raw → staging → intermediate → marts
05  Menentukan grain
06  Star Schema
07  Snowflake Schema
08  Implementasi dimensional model dengan SQL
09  Instalasi dan struktur project dbt
10  source()
11  ref()
12  Staging → intermediate → dimension → fact → mart
13  Incremental model
14  Incremental strategy
15  dbt testing
16  Documentation
17  Lineage
18  Data quality troubleshooting
19  Mini project
20  Evaluasi
```

---

# 4. Persiapan Lingkungan

## 4.1 Perangkat lunak

Gunakan:

- Python 3.10+;
- DuckDB;
- dbt Core;
- adapter `dbt-duckdb`;
- editor teks/VS Code.

> Versi dbt dan adapter dapat berubah. Karena itu, gunakan versi yang kompatibel satu sama lain pada saat instalasi. Modul tidak mengunci versi paket agar tidak memaksa versi yang sudah usang.

## 4.2 Instalasi

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan di Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instal dbt DuckDB adapter:

```bash
python -m pip install dbt-duckdb
```

Verifikasi:

```bash
dbt --version
```

Pastikan adapter DuckDB muncul.

---

# 5. Dataset Praktikum

Dataset tersedia sebagai CSV:

| File | Isi | Jumlah |
|---|---|---:|
| `customers.csv` | Customer | 50 |
| `products.csv` | Product | 30 |
| `orders.csv` | Transaksi/order line | 500 |
| `payments.csv` | Payment | 500 |
| `orders_incremental.csv` | Data baru untuk simulasi incremental | 50 |

Karakteristik penting:

- `order_id` unik pada dataset latihan;
- setiap order mempunyai customer valid;
- setiap order mempunyai product valid;
- `quantity` positif;
- `unit_price` berasal dari product;
- periode awal transaksi Januari–Juni 2026;
- file incremental berisi transaksi tambahan Juli 2026.

## 5.1 Download

- [Download paket dataset + project dbt](analytics_engineering_practicum_dataset_and_dbt_project.zip)
- [Download modul Markdown](Analytics_Engineering_SQL_dbt_Modul_Praktikum.md)
- [Download customers.csv](ae_lab/data/customers.csv)
- [Download products.csv](ae_lab/data/products.csv)
- [Download orders.csv](ae_lab/data/orders.csv)
- [Download payments.csv](ae_lab/data/payments.csv)
- [Download orders_incremental.csv](ae_lab/data/orders_incremental.csv)

---

# 6. Pemeriksaan Dataset

Jika menggunakan Python/pandas:

```python
import pandas as pd

customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")
orders = pd.read_csv("data/orders.csv")
payments = pd.read_csv("data/payments.csv")

print(customers.shape)
print(products.shape)
print(orders.shape)
print(payments.shape)
```

Output yang diharapkan:

```text
(50, 4)
(30, 6)
(500, 6)
(500, 5)
```

Periksa duplikasi:

```python
print(orders["order_id"].duplicated().sum())
print(customers["customer_id"].duplicated().sum())
print(products["product_id"].duplicated().sum())
```

Output yang diharapkan:

```text
0
0
0
```

---

# 7. Praktik 1 — Memahami Posisi Analytics Engineering

## 7.1 Konsep

Alur yang digunakan:

```text
Data Sources
     ↓
Data Ingestion / EL
     ↓
Data Warehouse
     ↓
Analytics Engineering
     ↓
Data Models
     ↓
BI / Dashboard / Analytics
```

Analytics Engineering berfokus pada transformasi dan pengelolaan model data sehingga data menjadi terstruktur, konsisten, dapat diuji, dapat digunakan kembali, dan terdokumentasi.

## 7.2 Latihan

Jawab:

1. Apakah `orders.csv` merupakan analytical mart?
2. Apakah `fct_sales` merupakan raw source?
3. Mengapa staging diperlukan?
4. Apa perbedaan transformasi dengan ingestion?
5. Di mana posisi dbt pada arsitektur ini?

**Jawaban acuan:** dbt digunakan terutama untuk mengelola transformasi dan model di data warehouse, bukan sebagai alat utama mengambil data dari API/database sumber.

---

# 8. Praktik 2 — SQL Transformasi Dasar

## 8.1 Query agregasi

Gunakan SQLite atau database SQL pilihan.

```sql
SELECT
    customer_id,
    SUM(quantity * unit_price) AS total_sales
FROM raw_orders
GROUP BY customer_id
ORDER BY total_sales DESC;
```

Perhatikan bahwa SQL sudah mampu menghasilkan analytical result.

Masalahnya: ketika project membesar, query perlu dikelola sebagai model yang reusable, memiliki dependency, test, dan dokumentasi.

---

# 9. Praktik 3 — Layer Raw, Staging, Intermediate, Mart

Gunakan pola:

```text
RAW
 ↓
STAGING
 ↓
INTERMEDIATE
 ↓
MARTS
 ↓
BI / ANALYTICS
```

## 9.1 Raw

Raw mempertahankan data sumber dalam bentuk yang dekat dengan sumber.

Contoh:

```text
raw.orders
raw.customers
raw.products
raw.payments
```

## 9.2 Staging

Staging melakukan transformasi ringan:

- rename;
- casting;
- standardisasi;
- basic cleaning.

Contoh:

```sql
SELECT
    order_id,
    customer_id,
    product_id,
    CAST(order_date AS DATE) AS order_date,
    quantity,
    unit_price
FROM raw_orders;
```

## 9.3 Intermediate

Intermediate berisi business logic yang dapat digunakan kembali.

```sql
SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price AS sales_amount
FROM stg_orders;
```

## 9.4 Mart

Mart adalah model yang siap digunakan untuk analitik.

Contoh:

```text
dim_customer
dim_product
dim_date
fct_sales
sales_mart
```

---

# 10. Praktik 4 — Menentukan Grain

Sebelum membuat fact table, jawab:

> **Satu baris fact table mewakili apa?**

Untuk kasus ini:

```text
fct_sales = 1 row per order line
```

Kolom utama:

```text
order_id
order_date
customer_id
product_id
quantity
unit_price
sales_amount
```

## 10.1 Mengapa grain penting?

Grain menentukan:

- struktur fact table;
- aggregation;
- hubungan dengan dimension;
- risiko double counting.

## 10.2 Latihan

Jika satu order memiliki 3 produk:

```text
O00001 Product A
O00001 Product B
O00001 Product C
```

Jika grain adalah **one row per order line**, maka terdapat 3 baris fact.

Jika grain adalah **one row per order**, maka desain fact harus berbeda.

**Tugas:** jelaskan mengapa mencampurkan kedua grain tersebut dapat menyebabkan double counting.

---

# 11. Praktik 5 — Star Schema

Model:

```text
                 dim_customer
                      │
                      │
                      ▼
dim_date ───────── fct_sales ───────── dim_product
                      │
                      ▼
                 dim_region
```

Dalam implementasi dataset ini, region berada di `dim_customer`, sehingga struktur minimal menjadi:

```text
                 dim_customer
                      │
                      │
                      ▼
dim_date ───────── fct_sales ───────── dim_product
```

## 11.1 Fact

```text
fct_sales
---------
order_id
order_date
customer_id
product_id
quantity
unit_price
sales_amount
```

## 11.2 Dimension customer

```text
dim_customer
------------
customer_id
customer_name
segment
region
```

## 11.3 Dimension product

```text
dim_product
-----------
product_id
product_name
category_id
category_name
department
unit_price
```

## 11.4 Dimension date

```text
dim_date
--------
full_date
year
month
quarter
```

## 11.5 Latihan

Tentukan:

- primary key setiap dimension;
- foreign key pada fact;
- measures;
- grain fact.

---

# 12. Praktik 6 — Snowflake Schema

Snowflake menormalisasi dimension lebih lanjut.

Contoh:

```text
                 dim_category
                      │
                      ▼
                 dim_product
                      │
                      ▼
dim_customer ───── fct_sales ───── dim_date
```

`dim_product`:

```text
product_id
product_name
category_id
```

`dim_category`:

```text
category_id
category_name
department
```

## 12.1 Latihan desain

Dari dataset:

```text
products.csv
```

Buat dua desain.

### Star

```text
fct_sales → dim_product
```

`category_name` dan `department` berada di `dim_product`.

### Snowflake

```text
fct_sales → dim_product → dim_category
```

`dim_category` menyimpan:

```text
category_id
category_name
department
```

## 12.2 Bandingkan

| Aspek | Star | Snowflake |
|---|---|---|
| Dimension | Lebih denormalisasi | Lebih ternormalisasi |
| Struktur | Lebih sederhana | Lebih kompleks |
| Query | Cenderung lebih sederhana | Dapat membutuhkan join tambahan |
| Redundansi | Lebih besar | Lebih kecil |
| Pemahaman analyst | Mudah | Relatif lebih kompleks |

---

# 13. Praktik 7 — Implementasi Dimensional Model dengan SQL

## 13.1 Staging customer

```sql
CREATE VIEW stg_customers AS
SELECT
    customer_id,
    customer_name,
    segment,
    region
FROM raw_customers;
```

## 13.2 Staging product

```sql
CREATE VIEW stg_products AS
SELECT
    product_id,
    product_name,
    category_id,
    category_name,
    department,
    unit_price
FROM raw_products;
```

## 13.3 Staging orders

```sql
CREATE VIEW stg_orders AS
SELECT
    order_id,
    customer_id,
    product_id,
    DATE(order_date) AS order_date,
    quantity,
    unit_price
FROM raw_orders;
```

## 13.4 Fact

```sql
SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    ROUND(quantity * unit_price, 2) AS sales_amount
FROM stg_orders;
```

## 13.5 Analytical mart

```sql
SELECT
    d.year,
    d.month,
    c.segment,
    c.region,
    p.category_name AS category,
    SUM(f.sales_amount) AS total_sales,
    SUM(f.quantity) AS total_quantity
FROM fct_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
JOIN dim_product p
    ON f.product_id = p.product_id
JOIN dim_date d
    ON f.order_date = d.full_date
GROUP BY
    d.year,
    d.month,
    c.segment,
    c.region,
    p.category_name;
```

## 13.6 Validasi nyata

SQL equivalent dari model di atas telah dieksekusi pada SQLite terhadap dataset yang disediakan.

Hasil validasi:

```text
orders_count      PASS
customers_unique  PASS
customers_not_null PASS
fk_customer       PASS
fk_product        PASS
mart_rows         PASS
sales_positive    PASS
```

Ringkasan fact yang tervalidasi:

```text
rows           = 500
quantity       = 1549
sales_amount   = 219137.50
```

---

# 14. Praktik 8 — Membuat Project dbt

Paket ZIP yang disediakan memiliki struktur:

```text
ae_lab/
├── data/
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── payments.csv
│   └── orders_incremental.csv
├── dbt_project/
│   ├── dbt_project.yml
│   ├── packages.yml
│   ├── profiles.yml.example
│   └── models/
│       ├── schema.yml
│       ├── staging/
│       ├── intermediate/
│       └── marts/
├── scripts/
│   └── bootstrap_raw.sql
└── SQL_VALIDATION_REPORT.txt
```

Buka direktori:

```bash
cd ae_lab/dbt_project
```

Salin `profiles.yml.example` menjadi `profiles.yml` untuk referensi lokal, kemudian letakkan konfigurasi aktif pada lokasi profile dbt, biasanya:

```text
~/.dbt/profiles.yml
```

Isi:

```yaml
analytics_engineering_lab:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../analytics.duckdb
      threads: 4
```

Verifikasi koneksi:

```bash
dbt debug
```

---

# 15. Praktik 9 — Menyiapkan Raw Schema di DuckDB

Buka DuckDB melalui client pilihan Anda, lalu jalankan isi:

```text
scripts/bootstrap_raw.sql
```

SQL:

```sql
CREATE SCHEMA IF NOT EXISTS raw;

CREATE OR REPLACE TABLE raw.customers AS
SELECT * FROM read_csv_auto('../data/customers.csv', HEADER=TRUE);

CREATE OR REPLACE TABLE raw.products AS
SELECT * FROM read_csv_auto('../data/products.csv', HEADER=TRUE);

CREATE OR REPLACE TABLE raw.orders AS
SELECT * FROM read_csv_auto('../data/orders.csv', HEADER=TRUE);

CREATE OR REPLACE TABLE raw.payments AS
SELECT * FROM read_csv_auto('../data/payments.csv', HEADER=TRUE);
```

Verifikasi:

```sql
SELECT COUNT(*) FROM raw.customers;
SELECT COUNT(*) FROM raw.products;
SELECT COUNT(*) FROM raw.orders;
SELECT COUNT(*) FROM raw.payments;
```

Expected:

```text
50
30
500
500
```

> Jika Anda menjalankan bootstrap dari direktori lain, sesuaikan path CSV terhadap working directory DuckDB/client yang digunakan.

---

# 16. Praktik 10 — `source()`

File:

```text
models/staging/stg_orders.sql
```

Isi:

```sql
SELECT
    order_id,
    customer_id,
    product_id,
    CAST(order_date AS DATE) AS order_date,
    quantity,
    unit_price
FROM {{ source('raw', 'orders') }}
```

Definisi source berada di `models/schema.yml`:

```yaml
version: 2

sources:
  - name: raw
    schema: raw
    tables:
      - name: customers
      - name: products
      - name: orders
      - name: payments
```

## 16.1 Mengapa `source()`?

`source()` membuat dependency terhadap sumber data eksplisit dan memungkinkan source ikut terdokumentasi dalam lineage.

Jalankan:

```bash
dbt run --select stg_orders
```

Jika ingin membangun seluruh project:

```bash
dbt run
```

---

# 17. Praktik 11 — `ref()`

`ref()` digunakan untuk merujuk model dbt lain.

Dependency:

```text
stg_orders
    ↓
int_sales
    ↓
fct_sales
    ↓
sales_mart
```

File `models/intermediate/int_sales.sql`:

```sql
SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price AS sales_amount
FROM {{ ref('stg_orders') }}
```

Dengan `ref()`, dbt dapat mengetahui urutan pembangunan model.

---

# 18. Praktik 12 — Membangun Dimension

## 18.1 `dim_customer.sql`

```sql
SELECT
    customer_id,
    customer_name,
    segment,
    region
FROM {{ ref('stg_customers') }}
```

## 18.2 `dim_product.sql`

```sql
SELECT
    product_id,
    product_name,
    category_id,
    category_name,
    department,
    unit_price
FROM {{ ref('stg_products') }}
```

## 18.3 `dim_date.sql`

```sql
SELECT DISTINCT
    order_date AS full_date,
    EXTRACT(year FROM order_date) AS year,
    EXTRACT(month FROM order_date) AS month,
    EXTRACT(quarter FROM order_date) AS quarter
FROM {{ ref('stg_orders') }}
```

---

# 19. Praktik 13 — Membangun Fact

File:

```text
models/marts/fct_sales.sql
```

```sql
SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    sales_amount
FROM {{ ref('int_sales') }}
```

Bangun model:

```bash
dbt run --select fct_sales
```

Atau:

```bash
dbt build --select fct_sales
```

`dbt build` berguna ketika ingin membangun resource sekaligus menjalankan test yang relevan berdasarkan dependency.

---

# 20. Praktik 14 — Membuat Sales Mart

File:

```text
models/marts/sales_mart.sql
```

```sql
SELECT
    d.year,
    d.month,
    c.segment,
    c.region,
    p.category_name AS category,
    SUM(f.sales_amount) AS total_sales,
    SUM(f.quantity) AS total_quantity
FROM {{ ref('fct_sales') }} f
JOIN {{ ref('dim_customer') }} c
    ON f.customer_id = c.customer_id
JOIN {{ ref('dim_product') }} p
    ON f.product_id = p.product_id
JOIN {{ ref('dim_date') }} d
    ON f.order_date = d.full_date
GROUP BY
    d.year,
    d.month,
    c.segment,
    c.region,
    p.category_name
```

Jalankan:

```bash
dbt run --select sales_mart
```

Kemudian query hasil:

```sql
SELECT *
FROM sales_mart
ORDER BY year, month, total_sales DESC;
```

---

# 21. Praktik 15 — Memahami Incremental Model

Masalah:

```text
Hari 1 → 10 juta baris
Hari 2 → 10 juta baris diproses ulang
Hari 3 → 10 juta baris diproses ulang
```

Padahal mungkin hanya sebagian data baru/berubah.

Incremental model memungkinkan pemrosesan hanya subset yang relevan.

---

# 22. Praktik 16 — Membuat Incremental Model

File:

```text
models/marts/fct_sales_incremental.sql
```

Isi:

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    sales_amount
FROM {{ ref('int_sales') }}

{% if is_incremental() %}

WHERE order_date >= (
    SELECT
        COALESCE(
            MAX(order_date),
            CAST('1900-01-01' AS DATE)
        )
    FROM {{ this }}
)

{% endif %}
```

## 22.1 First run

Pada first run:

```text
is_incremental() = false
```

Maka seluruh dataset diproses.

Jalankan:

```bash
dbt run --select fct_sales_incremental
```

## 22.2 Run berikutnya

Pada run berikutnya:

```text
is_incremental() = true
```

Query menggunakan watermark berdasarkan `MAX(order_date)` pada target.

---

# 23. Praktik 17 — Simulasi Data Baru

Dataset:

```text
orders_incremental.csv
```

berisi 50 transaksi tambahan.

Tambahkan data tersebut ke `raw.orders`.

Contoh DuckDB:

```sql
INSERT INTO raw.orders
SELECT *
FROM read_csv_auto('../data/orders_incremental.csv', HEADER=TRUE);
```

Verifikasi:

```sql
SELECT COUNT(*)
FROM raw.orders;
```

Expected:

```text
550
```

Kemudian jalankan:

```bash
dbt run --select fct_sales_incremental
```

Verifikasi:

```sql
SELECT COUNT(*)
FROM fct_sales_incremental;
```

Expected:

```text
550
```

> Perhatian: strategi `order_date >= max(order_date)` sengaja digunakan sebagai contoh pembelajaran. Untuk produksi, strategi incremental harus disesuaikan dengan late-arriving records, update, delete, unique key, partitioning, dan karakteristik warehouse.

---

# 24. Praktik 18 — Memahami Unique Key

Konfigurasi:

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}
```

Pertanyaan:

1. Mengapa `order_id` harus unik?
2. Apa yang terjadi jika source mengirim record yang sama?
3. Bagaimana jika order dapat berubah setelah pertama kali masuk?

Untuk kasus nyata, pikirkan:

```text
unique_key
watermark
merge
update
late-arriving data
delete
```

---

# 25. Praktik 19 — Late-Arriving Data

Misalnya watermark saat ini:

```text
2026-06-30
```

Kemudian sebuah transaksi dengan:

```text
order_date = 2026-06-25
```

baru masuk.

Jika hanya menggunakan:

```sql
WHERE order_date > MAX(order_date)
```

record tersebut tidak akan diproses.

Karena itu, production design dapat menggunakan:

- lookback window;
- ingestion timestamp;
- CDC;
- merge berdasarkan unique key;
- reprocessing period tertentu.

Contoh lookback sederhana:

```sql
WHERE order_date >= MAX(order_date) - INTERVAL 3 DAY
```

Namun jangan memilih angka 3 hari tanpa memahami karakteristik data.

---

# 26. Praktik 20 — Automated Testing

Testing dalam pipeline:

```text
Source
  ↓
Staging
  ↓
Transformation
  ↓
Dimension / Fact
  ↓
Automated Test
  ↓
Trusted Dataset
```

Tiga test utama:

```text
unique
not_null
relationships
```

---

# 27. Praktik 21 — Test `unique`

Pada `dim_customer`:

```yaml
- name: customer_id
  tests:
    - unique
```

Makna:

```text
Tidak boleh ada dua row
memiliki customer_id yang sama.
```

Lengkapi:

```yaml
- name: customer_id
  tests:
    - unique
    - not_null
```

---

# 28. Praktik 22 — Test `not_null`

```yaml
- name: customer_id
  tests:
    - not_null
```

Makna:

```text
customer_id tidak boleh NULL.
```

Test ini penting untuk key dimension/fact yang dibutuhkan oleh analitik.

---

# 29. Praktik 23 — Test `relationships`

Pada fact:

```yaml
- name: customer_id
  tests:
    - not_null
    - relationships:
        to: ref('dim_customer')
        field: customer_id
```

Makna:

```text
fct_sales.customer_id
        ↓
harus ditemukan pada
        ↓
dim_customer.customer_id
```

Untuk product:

```yaml
- name: product_id
  tests:
    - not_null
    - relationships:
        to: ref('dim_product')
        field: product_id
```

---

# 30. Praktik 24 — Menjalankan Test

Jalankan:

```bash
dbt test
```

atau:

```bash
dbt build
```

Interpretasikan:

```text
PASS → test berhasil
FAIL → ada pelanggaran data quality
WARN → warning sesuai konfigurasi
```

## 30.1 Prinsip troubleshooting

Jika test gagal, jangan langsung mengubah test agar PASS.

Telusuri:

```text
Source
 ↓
Staging
 ↓
Intermediate
 ↓
Dimension / Fact
 ↓
Test
```

Contoh jika relationship gagal:

```sql
SELECT f.customer_id
FROM fct_sales f
LEFT JOIN dim_customer c
    ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

Query tersebut mencari foreign key yang tidak mempunyai pasangan dimension.

---

# 31. Praktik 25 — Dokumentasi dbt

Tambahkan description pada model:

```yaml
- name: fct_sales
  description: "Fact table dengan grain satu baris per order line."
```

Tambahkan description kolom:

```yaml
- name: sales_amount
  description: "Nilai penjualan transaksi."
```

Tujuannya bukan sekadar mempercantik dokumentasi, tetapi menjelaskan semantic model kepada analyst dan stakeholder.

---

# 32. Praktik 26 — Generate Documentation

Jalankan:

```bash
dbt docs generate
```

Kemudian:

```bash
dbt docs serve
```

Browser akan membuka dokumentasi project.

Periksa:

- model;
- columns;
- descriptions;
- source;
- dependency;
- lineage.

---

# 33. Praktik 27 — Membaca Lineage Graph

Target lineage:

```text
raw.orders
    │
    ▼
stg_orders
    │
    ▼
int_sales
    │
    ▼
fct_sales
    │
    ├──────────────┐
    │              │
    ▼              ▼
dim_customer   sales_mart
       ▲
       │
       └── digunakan oleh sales_mart
```

Secara keseluruhan:

```text
raw
 ↓
staging
 ↓
intermediate
 ↓
┌───────────────┐
│ dimensions    │
│ facts         │
└───────┬───────┘
        ↓
      marts
        ↓
   analytics
```

Pertanyaan:

1. Dari mana `fct_sales` berasal?
2. Model apa yang bergantung pada `stg_orders`?
3. Jika `raw.orders` berubah, model mana yang terdampak?
4. Mengapa `ref()` penting untuk lineage?

---

# 34. Praktik 28 — Menjalankan Pipeline Lengkap

Setelah seluruh konfigurasi selesai:

```bash
dbt build
```

Kemudian:

```bash
dbt docs generate
```

dan:

```bash
dbt docs serve
```

Urutan konseptual:

```text
RAW DATA
   ↓
SOURCE
   ↓
STAGING
   ↓
INTERMEDIATE
   ↓
DIMENSION + FACT
   ↓
MART
   ↓
TEST
   ↓
DOCUMENTATION
   ↓
TRUSTED ANALYTICS
```

---

# 35. Praktik 29 — Data Quality Failure Lab

Bagian ini digunakan untuk mengajarkan bahwa test harus mampu menemukan masalah.

## 35.1 Membuat duplicate customer

Tambahkan secara sengaja satu customer dengan `customer_id` yang sudah ada ke source.

Jalankan:

```bash
dbt test --select dim_customer
```

Expected:

```text
unique test → FAIL
```

Perbaiki source.

Jalankan kembali:

```bash
dbt test --select dim_customer
```

Expected:

```text
PASS
```

## 35.2 Membuat NULL customer_id

Masukkan satu row dengan `customer_id = NULL`.

Test:

```text
not_null → FAIL
```

## 35.3 Membuat foreign key invalid

Masukkan order dengan:

```text
customer_id = C999
```

padahal customer tersebut tidak ada.

Test:

```text
relationships → FAIL
```

**Tujuan pembelajaran:** peserta memahami bahwa test adalah mekanisme quality gate, bukan sekadar formalitas.

---

# 36. Praktik 30 — Star vs Snowflake Exercise

Diberikan:

```text
Product
Category
Department
```

## Tugas

Buat Star Schema:

```text
fct_sales → dim_product
```

Buat Snowflake Schema:

```text
fct_sales → dim_product → dim_category → dim_department
```

Kemudian jawab:

1. Di mana redundansi lebih besar?
2. Mana yang membutuhkan join lebih banyak?
3. Mana yang lebih mudah dipahami analyst?
4. Kapan normalisasi dimension menjadi relevan?

Tidak ada satu jawaban desain yang selalu benar; keputusan harus dikaitkan dengan kebutuhan analitik dan karakteristik data.

---

# 37. Praktik 31 — Incremental Design Exercise

Diberikan:

```text
Fact table = 500 juta rows
Data baru per hari = 2 juta rows
```

Diskusikan:

1. Apakah full refresh setiap hari perlu dibandingkan dengan incremental?
2. Apa unique key?
3. Apa watermark?
4. Bagaimana menangani late-arriving data?
5. Apakah data dapat di-update?
6. Apakah ada delete?
7. Apakah partitioning diperlukan?
8. Apakah merge strategy diperlukan?

**Target jawaban:** peserta harus dapat menjelaskan trade-off, bukan hanya mengatakan "pakai incremental".

---

# 38. Mini Project — Sales Analytics Mart

## 38.1 Business Question

> Berapa total penjualan berdasarkan bulan, customer segment, region, dan product category?

## 38.2 Output

```text
month
segment
region
category
total_sales
total_quantity
```

## 38.3 Model

```text
                    fct_sales
                   /    |     \
                  /     |      \
                 ▼      ▼       ▼
        dim_customer dim_product dim_date
                 \      |       /
                  \     |      /
                   ▼    ▼     ▼
                    sales_mart
```

## 38.4 Persyaratan

Mahasiswa harus membuat:

```text
stg_orders.sql
stg_customers.sql
stg_products.sql
stg_payments.sql
dim_customer.sql
dim_product.sql
dim_date.sql
int_sales.sql
fct_sales.sql
sales_mart.sql
```

Kemudian:

```text
source()
ref()
unique
not_null
relationships
documentation
incremental model
```

## 38.5 Acceptance criteria

Project dianggap selesai jika:

- source terdefinisi;
- staging berhasil dibangun;
- dependency antar-model menggunakan `ref()`;
- fact memiliki grain yang jelas;
- dimension mempunyai key yang jelas;
- test `unique` PASS;
- test `not_null` PASS;
- test `relationships` PASS;
- sales mart menghasilkan data;
- documentation dapat dibuat;
- lineage dapat ditelusuri;
- incremental model dapat memproses tambahan 50 order.

---

# 39. Checklist Praktikum

## Konsep

- [ ] Menjelaskan Analytics Engineering.
- [ ] Menjelaskan raw/staging/intermediate/mart.
- [ ] Menjelaskan fact/dimension/grain.
- [ ] Menjelaskan Star Schema.
- [ ] Menjelaskan Snowflake Schema.

## SQL

- [ ] Filtering.
- [ ] Join.
- [ ] Aggregation.
- [ ] Transformation.
- [ ] Analytical mart.

## dbt

- [ ] `dbt_project.yml`.
- [ ] `source()`.
- [ ] `ref()`.
- [ ] Staging model.
- [ ] Intermediate model.
- [ ] Dimension model.
- [ ] Fact model.
- [ ] Mart model.

## Incremental

- [ ] `materialized='incremental'`.
- [ ] `is_incremental()`.
- [ ] `unique_key`.
- [ ] Watermark.
- [ ] Late-arriving data.
- [ ] Update/delete/merge discussion.

## Testing

- [ ] `unique`.
- [ ] `not_null`.
- [ ] `relationships`.
- [ ] Membaca PASS/FAIL/WARN.
- [ ] Troubleshooting root cause.

## Documentation

- [ ] Model description.
- [ ] Column description.
- [ ] `dbt docs generate`.
- [ ] `dbt docs serve`.
- [ ] Lineage graph.

---

# 40. Pertanyaan Evaluasi Konseptual

1. Apa peran Analytics Engineering?
2. Mengapa SQL saja belum cukup untuk project transformasi yang besar?
3. Apa perbedaan Star Schema dan Snowflake Schema?
4. Apa yang dimaksud grain?
5. Mengapa grain ditentukan sebelum fact table dibuat?
6. Apa fungsi `source()`?
7. Apa fungsi `ref()`?
8. Mengapa dependency perlu eksplisit?
9. Apa perbedaan full refresh dan incremental?
10. Mengapa incremental model membutuhkan strategi yang lebih lengkap daripada sekadar `WHERE date > last_date`?
11. Apa fungsi `unique`?
12. Apa fungsi `not_null`?
13. Apa fungsi `relationships`?
14. Apa manfaat documentation?
15. Apa manfaat lineage?

---

# 41. Pertanyaan Analitis

Kasus:

```text
Fact table = 500 juta rows
Customer dimension = 5 juta rows
Data baru per hari = 2 juta rows
```

Jawab:

1. Bagaimana memilih full refresh atau incremental?
2. Apa kandidat unique key?
3. Bagaimana menentukan watermark?
4. Bagaimana menangani late-arriving data?
5. Test apa yang wajib diterapkan pada dimension?
6. Test apa yang wajib diterapkan pada fact?
7. Model mana yang perlu didokumentasikan?
8. Bagaimana dependency antar-model dibangun?
9. Bagaimana memastikan perubahan source tidak diam-diam merusak mart?

---

# 42. Rubrik Penilaian Praktikum

| Komponen | Bobot | Bukti |
|---|---:|---|
| Dimensional modeling | 20% | Star + Snowflake + grain |
| SQL transformation | 20% | SQL models |
| dbt models | 20% | Project dbt |
| Incremental | 15% | Incremental SQL + penjelasan |
| Testing | 15% | schema.yml + hasil test |
| Documentation | 10% | docs + lineage |

---

# 43. Troubleshooting

## 43.1 `dbt: command not found`

Periksa virtual environment:

```bash
python -m pip install dbt-duckdb
```

Kemudian:

```bash
dbt --version
```

## 43.2 Profile tidak ditemukan

Pastikan file berada di:

```text
~/.dbt/profiles.yml
```

dan nama profile sama dengan:

```yaml
profile: analytics_engineering_lab
```

## 43.3 Source tidak ditemukan

Periksa:

```yaml
sources:
  - name: raw
    schema: raw
```

Kemudian pastikan tabel:

```text
raw.customers
raw.products
raw.orders
raw.payments
```

benar-benar ada.

## 43.4 `relationships` gagal

Jalankan:

```sql
SELECT f.customer_id
FROM fct_sales f
LEFT JOIN dim_customer c
  ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

Jika menghasilkan row, ada foreign key yang tidak mempunyai dimension record.

## 43.5 `unique` gagal

Cari duplicate:

```sql
SELECT
    customer_id,
    COUNT(*) AS n
FROM dim_customer
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

---

# 44. Validasi Teknis yang Sudah Dilakukan

Pada lingkungan penyusunan modul:

```text
Dataset generation             PASS
SQLite SQL transformation     PASS
Customer uniqueness           PASS
Customer not-null             PASS
Customer relationship         PASS
Product relationship          PASS
Sales mart non-empty          PASS
Positive sales amount         PASS
```

Dataset SQL menghasilkan:

```text
customers = 50
products  = 30
orders    = 500
payments  = 500
```

Fact validation:

```text
rows         = 500
quantity     = 1549
sales_amount = 219137.50
```

## Batas validasi

Perintah berikut belum dapat dieksekusi pada lingkungan penyusunan karena binary/package `dbt` dan DuckDB tidak tersedia dan instalasi online gagal:

```bash
dbt debug
dbt run
dbt build
dbt test
dbt docs generate
dbt docs serve
```

Karena itu, hasil tersebut harus dijalankan pada komputer/lab yang sudah memiliki dbt + DuckDB.

---

# 45. File Pendukung

Paket pendamping berisi:

```text
ae_lab/
├── data/
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── payments.csv
│   └── orders_incremental.csv
├── dbt_project/
│   ├── dbt_project.yml
│   ├── packages.yml
│   ├── profiles.yml.example
│   └── models/
│       ├── schema.yml
│       ├── staging/
│       ├── intermediate/
│       └── marts/
├── scripts/
│   └── bootstrap_raw.sql
├── analytics_validation.sqlite
└── SQL_VALIDATION_REPORT.txt
```

---

# 46. Alur Praktikum 120 Menit

| Waktu | Aktivitas |
|---|---|
| 0–10 | Konsep Analytics Engineering |
| 10–25 | SQL transformation |
| 25–45 | Grain, Star, Snowflake |
| 45–60 | dbt project, source, ref |
| 60–75 | Staging → dimension → fact → mart |
| 75–90 | Incremental model |
| 90–105 | Testing |
| 105–115 | Documentation + lineage |
| 115–120 | Evaluasi |

---

# 47. Ringkasan Konsep

```text
                 ANALYTICS ENGINEERING
                         │
                 ┌───────┴───────┐
                 ▼               ▼
                SQL             dbt
                 │               │
                 ▼               ▼
          Transformation      Models
                 │          ┌────┼─────┐
                 ▼          ▼    ▼     ▼
        Dimensional Model  Test Docs Lineage
             │
        ┌────┴─────┐
        ▼          ▼
       STAR     SNOWFLAKE
        │
        ▼
 FACT + DIMENSION
        │
        ▼
 INCREMENTAL MODEL
        │
        ▼
 TRUSTED ANALYTICS
```

---

# 48. Pesan Kunci

1. SQL adalah bahasa utama transformasi, tetapi project analytics membutuhkan struktur dan governance.
2. Grain harus ditentukan sebelum mendesain fact table.
3. Star dan Snowflake mempunyai trade-off desain yang berbeda.
4. `source()` mendefinisikan sumber data eksternal.
5. `ref()` membuat dependency antar-model eksplisit.
6. Incremental model mengurangi pemrosesan ulang ketika hanya sebagian data yang baru/berubah.
7. Incremental production design harus mempertimbangkan late-arriving data, update, duplicate, delete, watermark, partitioning, dan merge.
8. Testing harus menjadi bagian pipeline.
9. `unique`, `not_null`, dan `relationships` membantu menjaga kualitas model.
10. Dokumentasi dan lineage membuat transformasi mudah dipahami dan dipelihara.
11. Tujuan akhirnya bukan sekadar query yang berhasil, tetapi **trusted analytics**.

---

# 49. Deliverable Mahasiswa

Mahasiswa mengumpulkan:

```text
1. Diagram Star Schema
2. Diagram Snowflake Schema
3. dbt project
4. SQL staging models
5. SQL intermediate models
6. SQL dimension models
7. SQL fact model
8. SQL mart
9. Incremental model
10. schema.yml
11. Hasil dbt test
12. Dokumentasi dbt
13. Lineage graph
14. Jawaban evaluasi
15. Penjelasan strategi incremental
```

---

# 50. Target Akhir

Pada akhir praktikum peserta harus mampu menghubungkan:

```text
SQL
 ↓
Dimensional Modeling
 ↓
dbt Models
 ↓
Dependency
 ↓
Incremental Processing
 ↓
Automated Testing
 ↓
Documentation
 ↓
Lineage
 ↓
Trusted Analytics
```

Target ini selaras dengan capaian pada outline: membangun arsitektur pemodelan dimensional serta mengotomatisasi pengujian dan dokumentasi transformasi data menggunakan SQL dan dbt.
