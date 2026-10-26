import json
from pathlib import Path

DEFAULT_WATERMARK = (
    "1970-01-01T00:00:00+00:00"
)

def load_watermark(
    file_path,
):

    path = Path(file_path)

    if not path.exists():
        return DEFAULT_WATERMARK

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    return data.get(
        "watermark",
        DEFAULT_WATERMARK,
    )

def save_watermark(
    file_path,
    watermark,
):

    path = Path(file_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "watermark": watermark
            },
            file,
            indent=2,
        )