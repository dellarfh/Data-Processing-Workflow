import time

import requests

BASE_URL = "http://127.0.0.1:8000"


def test_retry():

    # 1. Reset server
    requests.get(f"{BASE_URL}/reset")

    attempts = 0
    max_attempts = 5
    success = False

    while attempts < max_attempts:

        attempts += 1

        response = requests.get(
            f"{BASE_URL}/unstable",
            timeout=(3, 10),
        )

        if attempts == 1:

            # 3. Pastikan terjadi 500 di percobaan pertama
            assert response.status_code == 500, (
                f"Expected 500 on first attempt, got {response.status_code}"
            )

        if response.status_code == 200:

            success = True

            break

        # 4. Pastikan retry dilakukan (loop lanjut, ada jeda)
        time.sleep(1)

    # 5. Pastikan akhirnya 200
    assert success, "Request never succeeded after retries"

    print(f"Succeeded after {attempts} attempts")


test_retry()

print("test_retry passed")