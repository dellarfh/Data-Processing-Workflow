base_delay = 1

for attempt in range(1, 5):

    wait_time = (
        base_delay
        * (2 ** (attempt - 1))
    )

    print(
        f"Attempt {attempt}: "
        f"wait {wait_time}"
    )