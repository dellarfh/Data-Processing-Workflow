import random

base_delay = 1

for attempt in range(1, 5):

    wait_time = (
        base_delay
        * (2 ** (attempt - 1))
    )

    jitter = random.uniform(0, 1)

    sleep_time = wait_time + jitter

    print(
        f"Attempt {attempt}: "
        f"base={wait_time}, "
        f"sleep_time={sleep_time:.2f}"
    )