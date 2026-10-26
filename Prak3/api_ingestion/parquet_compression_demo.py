from pathlib import Path

import pandas as pd

records = [
    {
        "id": i,
        "customer": f"customer_{i:03d}",
        "amount": i * 10000,
        "updated_at": "2026-09-01T08:00:00+00:00",
    }
    for i in range(1, 1001)
]

df = pd.DataFrame(records)

df.to_parquet(
    "data/compression_snappy.parquet",
    index=False,
    compression="snappy",
)

df.to_parquet(
    "data/compression_gzip.parquet",
    index=False,
    compression="gzip",
)

snappy_size = Path(
    "data/compression_snappy.parquet"
).stat().st_size

gzip_size = Path(
    "data/compression_gzip.parquet"
).stat().st_size

print(f"Snappy size: {snappy_size} bytes")
print(f"Gzip size: {gzip_size} bytes")