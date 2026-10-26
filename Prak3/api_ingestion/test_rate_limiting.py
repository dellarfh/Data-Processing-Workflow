import time

import requests

BASE_URL = "http://127.0.0.1:8000"


def test_rate_limiting():

    # 1. Reset server
    requests.get(f"{BASE_URL}/reset")

    # 2. Request endpoint /rate-limited
    response = requests.get(
        f"{BASE_URL}/rate-limited",
        timeout=(3, 10),
    )

    # 3. Pastikan terjadi 429
    assert response.status_code == 429, (
        f"Expected 429, got {response.status_code}"
    )

    retry_after = response.headers.get(
        "Retry-After",
        "1",
    )

    wait_time = float(retry_after)

    # 4. Pastikan client menunggu
    print(f"Waiting {wait_time}s (as instructed by Retry-After)")
    time.sleep(wait_time)

    response = requests.get(
        f"{BASE_URL}/rate-limited",
        timeout=(3, 10),
    )

    # Server ini butuh 2x kena 429 dulu baru 200,
    # jadi request kedua kemungkinan masih 429 -
    # tunggu lagi sesuai Retry-After sebelum request ketiga
    if response.status_code == 429:

        retry_after = response.headers.get(
            "Retry-After",
            "1",
        )

        wait_time = float(retry_after)

        print(f"Waiting {wait_time}s again")
        time.sleep(wait_time)

        response = requests.get(
            f"{BASE_URL}/rate-limited",
            timeout=(3, 10),
        )

    # 5. Pastikan request berikutnya berhasil
    assert response.status_code == 200, (
        f"Expected 200 eventually, got {response.status_code}"
    )

    print("Final status:", response.status_code)


test_rate_limiting()

print("test_rate_limiting passed")