# generate_datasets.py
import pandas as pd
import numpy as np

# 1. Dataset Utama: data_mahasiswa_pens.csv
data_pendaftaran = {
    'id': [1, 2, 2, 3, 4, 5, 6, 7],
    'nama': ['Budi Santoso', 'Siti Aminah', 'Siti Aminah', 'Ahmad Rizki', 'Dewi Lestari', 'Eko Prasetyo', 'Fany Noor', 'Gita Gutawa'],
    'nik': ['3578010101000001', '3578010101000002', '3578010101000002', '3578010101000003', '3578010101000004', '3578010101000005', '3578010101000006', '3578010101000007'],
    'umur': [20, 21, 21, -5, 19, 22, 20, 21],
    'email': ['budi@pens.ac.id', 'siti_at_pens.ac.id', 'siti_at_pens.ac.id', 'ahmad@pens.ac.id', 'dewi@pens.ac.id', 'eko@pens.ac.id', 'fany@gmail.com', 'gita@pens.ac.id'],
    'nilai_ipk': [3.75, 3.50, 3.50, 4.50, -1.00, 3.20, 3.10, 3.80],
    'tanggal_daftar': ['2026-01-10', '2026-01-11', '2026-01-11', '2026-01-12', '2026-03-01', None, '2024-05-01', '2026-02-01'],
    'status_pembayaran': ['Lunas', 'Lunas', 'Lunas', 'Belum Lunas', 'Lunas', 'Lunas', 'Tidak Valid', 'Lunas']
}

df_pendaftaran = pd.DataFrame(data_pendaftaran)
df_pendaftaran.to_csv('data_mahasiswa_pens.csv', index=False)
print('[SETUP] File data_mahasiswa_pens.csv berhasil dibuat.')

# 2. Golden Source Dataset (External Verifier untuk Dimensi Accuracy): golden_source_ktp.csv
data_ktp = {
    'nik': ['3578010101000001', '3578010101000002', '3578010101000003', '3578010101000004', '3578010101000005', '3578010101000006', '3578010101000007'],
    'nama_resmi_ktp': ['Budi Santoso', 'Siti Aminah', 'Ahmad Rizky Pratama', 'Dewi Lestari', 'Eko Prasetyo', 'Fanny Nur', 'Gita Gutawa']
}

df_ktp = pd.DataFrame(data_ktp)
df_ktp.to_csv('golden_source_ktp.csv', index=False)
print('[SETUP] File golden_source_ktp.csv berhasil dibuat.')