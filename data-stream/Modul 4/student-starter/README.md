# Starter Modul 3 — Bagian 4

1. Jalankan broker:
   docker compose up -d

2. Buat topic sesuai keputusan Anda.

3. Jalankan producer:
   python app/producer.py

4. Jalankan consumer:
   python app/consumer.py

Failure injection:
   FAIL_AFTER=3 python app/consumer.py

Environment variable yang tersedia:
- GROUP_ID
- AUTO_OFFSET_RESET
- FAIL_AFTER

Starter sengaja memberikan kerangka kerja, bukan konfigurasi jawaban.
