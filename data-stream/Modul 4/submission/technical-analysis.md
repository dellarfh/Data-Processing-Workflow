# Technical Analysis

## Architecture Decision

Partition: 3 partition.

Consumer Group: satu group, dpw3-case.

Consumer: 3 consumer.

Event Key / Ordering: key = order_id; satu order selalu ke partition yang sama sehingga urutan terjaga.

Offset / Commit: auto.offset.reset earliest; commit manual setelah event selesai diproses.

Delivery Semantics: at-least-once.

Alasan: Ada 3 order, jadi 3 partition memungkinkan order berbeda diproses paralel, sedangkan event satu order tetap berurutan karena satu partition. Maksimal paralelisme sama dengan jumlah partition, sehingga 3 consumer cukup. Commit setelah proses mencegah event hilang saat consumer gagal; konsekuensinya event yang belum ter-commit dapat diproses ulang, sehingga pemrosesan harus idempoten berdasarkan event_id. Exactly-once tidak dipilih karena starter hanya membaca (tanpa topic output atau transaksi).

## Failure Analysis

Action: Menjalankan 3 consumer pada group dpw3-case-failure (satu dengan FAIL_AFTER=2), mengirim 8 event dengan producer, lalu menjalankan kembali consumer yang gagal tanpa FAIL_AFTER pada group yang sama.

Observation: Consumer pemilik partition 0 (ORD-01) men-commit PAY-001 (offset 0), memproses PAY-003 (offset 1) lalu berhenti sebelum commit, kemudian partition 0 diambil alih consumer pemilik partition 1 (group menjadi 2 member) yang memproses ulang PAY-003 pada partition 0 offset 1 lalu PAY-006 (offset 2), sehingga urutan CREATED → PAID → SHIPPED tetap terjaga.

Diagnosis: Karena commit dilakukan setelah proses (at-least-once), offset 1 belum ter-commit saat consumer gagal sehingga PAY-003 diproses dua kali (duplicate processing) tanpa ada event yang hilang.

Fix: Consumer yang gagal dijalankan kembali tanpa FAIL_AFTER pada group yang sama sehingga rebalance mengembalikan group menjadi 3 member.

Verification: Describe group menunjukkan 3 consumer aktif dengan LAG 0 dan CURRENT-OFFSET 3, 2, 3 pada partition 0, 1, 2 sehingga seluruh 8 event telah diproses.