from pathlib import Path

import pandas as pd

def save_records(
    records,
    output_file,
):

    path = Path(output_file)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = pd.DataFrame(
        records
    )

    df.to_parquet(
        path,
        index=False,
        compression="snappy",
    )

    return path

def read_records(
    input_file,
):

    return pd.read_parquet(
        input_file
    )