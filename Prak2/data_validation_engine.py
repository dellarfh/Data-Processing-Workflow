import pandas as pd
import numpy as np
import re
from datetime import datetime

class DataQualityEngine:
    def __init__(self, filepath, golden_source_path=None):
        self.filepath = filepath
        self.golden_source_path = golden_source_path
        self.df = None
        self.df_golden = None
        self.report = []

    def load_and_observe(self):
        '''[OBSERVABILITY] Pilar Volume & Schema'''
        try:
            self.df = pd.read_csv(self.filepath)
            print('='*70)
            print(f'[OBSERVABILITY - INGESTION] Memuat data dari: {self.filepath}')
            print(f'[OBSERVABILITY - VOLUME] Jumlah Baris: {len(self.df)}, Jumlah Kolom: {len(self.df.columns)}')
            print(f'[OBSERVABILITY - SCHEMA] Struktur Tipe Data:\n{self.df.dtypes}')
            print('='*70 + '\n')
            
            if self.golden_source_path:
                self.df_golden = pd.read_csv(self.golden_source_path)
        except Exception as e:
            print(f'[ERROR] Gagal memuat data: {e}')

    def check_completeness(self):
        '''1. Dimensi Completeness'''
        total_records = len(self.df)
        null_counts = self.df.isnull().sum()
        total_nulls = null_counts.sum()
        completeness_ratio = (1 - (total_nulls / (total_records * len(self.df.columns)))) * 100

        if total_nulls == 0:
            self.report.append({'Dimension': '1. Completeness', 'Ratio': f'{completeness_ratio:.2f}%', 'Status': 'PASS', 'Detail': 'Tidak ada missing values.'})
        else:
            missing_cols = null_counts[null_counts > 0].to_dict()
            self.report.append({'Dimension': '1. Completeness', 'Ratio': f'{completeness_ratio:.2f}%', 'Status': 'FAIL', 'Detail': f'Missing values pada: {missing_cols}'})

    def check_uniqueness(self, key_column):
        '''2. Dimensi Uniqueness'''
        total_records = len(self.df)
        unique_keys = self.df[key_column].nunique()
        uniqueness_ratio = (unique_keys / total_records) * 100
        
        duplicates = self.df[self.df.duplicated(subset=[key_column], keep=False)]
        if duplicates.empty:
            self.report.append({'Dimension': '2. Uniqueness', 'Ratio': f'{uniqueness_ratio:.2f}%', 'Status': 'PASS', 'Detail': f'Primary Key {key_column} 100% unik.'})
        else:
            dup_ids = duplicates[key_column].unique().tolist()
            self.report.append({'Dimension': '2. Uniqueness', 'Ratio': f'{uniqueness_ratio:.2f}%', 'Status': 'FAIL', 'Detail': f'Duplikasi ditemukan pada ID: {dup_ids}'})

    def check_validity(self):
        '''3. Dimensi Validity (Regex Email & Domain Range IPK)'''
        email_pattern = r'^[\w\.-]+@pens\.ac\.id$'
        invalid_email_mask = ~self.df['email'].astype(str).str.match(email_pattern, na=False)
        
        invalid_ipk_mask = (self.df['nilai_ipk'] < 0.0) | (self.df['nilai_ipk'] > 4.0)
        
        invalid_rows = self.df[invalid_email_mask | invalid_ipk_mask]
        validity_ratio = ((len(self.df) - len(invalid_rows)) / len(self.df)) * 100
        
        issues = []
        if invalid_email_mask.sum() > 0:
            issues.append(f'Email Non-PENS: {self.df[invalid_email_mask]["email"].tolist()}')
        if invalid_ipk_mask.sum() > 0:
            issues.append(f'IPK Out of Range [0-4]: {self.df[invalid_ipk_mask]["nilai_ipk"].tolist()}')

        status = 'PASS' if not issues else 'FAIL'
        self.report.append({'Dimension': '3. Validity', 'Ratio': f'{validity_ratio:.2f}%', 'Status': status, 'Detail': ' | '.join(issues) if issues else 'Semua data valid.'})

    def check_consistency(self):
        '''4. Dimensi Consistency (Umur Logis & Domain Status)'''
        invalid_age = self.df['umur'] <= 0
        valid_statuses = ['Lunas', 'Belum Lunas']
        invalid_status = ~self.df['status_pembayaran'].isin(valid_statuses)
        
        inconsistent_rows = self.df[invalid_age | invalid_status]
        consistency_ratio = ((len(self.df) - len(inconsistent_rows)) / len(self.df)) * 100
        
        issues = []
        if invalid_age.sum() > 0:
            issues.append(f'Umur Tidak Logis: {self.df[invalid_age]["umur"].tolist()}')
        if invalid_status.sum() > 0:
            issues.append(f'Status Pembayaran Asing: {self.df[invalid_status]["status_pembayaran"].dropna().tolist()}')

        status = 'PASS' if not issues else 'FAIL'
        self.report.append({'Dimension': '4. Consistency', 'Ratio': f'{consistency_ratio:.2f}%', 'Status': status, 'Detail': ' | '.join(issues) if issues else 'Konsistensi data terjaga.'})

    def check_accuracy(self, join_key='nik', name_col='nama'):
        '''5. Dimensi Accuracy (Verifikasi Eksternal terhadap Golden Source KTP)'''
        if self.df_golden is None:
            self.report.append({'Dimension': '5. Accuracy', 'Ratio': 'N/A', 'Status': 'SKIPPED', 'Detail': 'Golden Source tidak disediakan.'})
            return

        merged = pd.merge(self.df, self.df_golden, on=join_key, how='inner')
        matched = merged[merged[name_col] == merged['nama_resmi_ktp']]
        accuracy_ratio = (len(matched) / len(merged)) * 100 if len(merged) > 0 else 0
        
        mismatches = merged[merged[name_col] != merged['nama_resmi_ktp']]
        issues = mismatches[[join_key, name_col, 'nama_resmi_ktp']].to_dict(orient='records')
        
        status = 'PASS' if len(mismatches) == 0 else 'FAIL'
        self.report.append({'Dimension': '5. Accuracy', 'Ratio': f'{accuracy_ratio:.2f}%', 'Status': status, 'Detail': f'Ketidaksesuaian Fakta KTP: {issues}' if issues else '100% akurat sesuai KTP.'})

    def check_timeliness_and_freshness(self, date_column, max_year=2026):
        '''6. Dimensi Timeliness & Observability Freshness'''
        dates = pd.to_datetime(self.df[date_column], errors='coerce')
        outdated_mask = dates.dt.year < max_year
        outdated_count = outdated_mask.sum()
        
        timeliness_ratio = ((len(self.df) - outdated_count) / len(self.df)) * 100
        outdated_records = self.df[outdated_mask][date_column].tolist()

        status = 'PASS' if outdated_count == 0 else 'FAIL'
        self.report.append({'Dimension': '6. Timeliness', 'Ratio': f'{timeliness_ratio:.2f}%', 'Status': status, 'Detail': f'Data usang sebelum tahun {max_year}: {outdated_records}' if outdated_records else 'Data mutakhir (Fresh).'})

    def check_distribution_drift(self, column_name, sigma_threshold=3):
        '''[OBSERVABILITY] Pilar Distribution (3-Sigma Outlier Detection)'''
        series = self.df[column_name].dropna()
        mean = series.mean()
        std = series.std()
        
        outliers = series[np.abs(series - mean) > (sigma_threshold * std)]
        
        print('\n' + '='*70)
        print(f'[OBSERVABILITY - DISTRIBUTION DRIFT] Analisis Kolom {column_name}')
        print(f'Mean: {mean:.4f} | Std Dev: {std:.4f}')
        print(f'Batas Upper ({sigma_threshold}σ): {mean + sigma_threshold*std:.4f}')
        print(f'Batas Lower (-{sigma_threshold}σ): {mean - sigma_threshold*std:.4f}')
        if not outliers.empty:
            print(f'[ALERT DRIFT DETECTED] Nilai Anomali/Outlier Terdeteksi: {outliers.tolist()}')
        else:
            print('[INFO] Distribusi normal. Tidak ada drift/outlier terdeteksi.')
        print('='*70 + '\n')

    # KODE JAWABAN TUGAS 3:
    def remediate_data(self):
        print('\n[REMEDIATION] Memulai Pembersihan Data Otomatis...')
        # 1. Hapus Duplikat
        self.df = self.df.drop_duplicates(subset=['id'], keep='first')
    
        # 2. Imputasi IPK Cacat dengan Median IPK Valid
        valid_ipk_median = self.df[(self.df['nilai_ipk'] >= 0.0) & (self.df['nilai_ipk'] <= 4.0)]['nilai_ipk'].median()
        invalid_ipk_mask = (self.df['nilai_ipk'] < 0.0) | (self.df['nilai_ipk'] > 4.0)
        self.df.loc[invalid_ipk_mask, 'nilai_ipk'] = valid_ipk_median
    
        # 3. Imputasi Missing Tanggal dengan Tanggal Hari Ini
        today_str = datetime.now().strftime('%Y-%m-%d')
        self.df['tanggal_daftar'] = self.df['tanggal_daftar'].fillna(today_str)
    
        print('[REMEDIATION COMPLETED] Dataset berhasil dibersihkan dan siap dikonsumsi model ML.')
        return self.df

    def run_all(self):
        self.load_and_observe()
        self.check_completeness()
        self.check_uniqueness(key_column='id')
        self.check_validity()
        self.check_consistency()
        self.check_accuracy(join_key='nik', name_col='nama')
        self.check_timeliness_and_freshness(date_column='tanggal_daftar')
        
        report_df = pd.DataFrame(self.report)
        print('='*70)
        print('          LAPORAN UTAMA DATA QUALITY (6 DIMENSI)')
        print('='*70)
        print(report_df.to_string(index=False))
        print('='*70)
        
        self.check_distribution_drift(column_name='nilai_ipk')

if __name__ == '__main__':
    engine = DataQualityEngine(filepath='data_mahasiswa_pens.csv', golden_source_path='golden_source_ktp.csv')
    engine.run_all()

    df_bersih = engine.remediate_data()
    print(df_bersih)