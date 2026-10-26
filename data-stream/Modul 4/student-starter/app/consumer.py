import json
import os
import time
from confluent_kafka import Consumer

BROKER = "localhost:9092"
TOPIC = "dpw3-events"

GROUP = os.getenv("GROUP_ID", "dpw3-case")
FAIL_AFTER = int(os.getenv("FAIL_AFTER", "0"))

conf = {
    "bootstrap.servers": BROKER,
    "group.id": GROUP,
    "auto.offset.reset": os.getenv("AUTO_OFFSET_RESET", "earliest"),
    "enable.auto.commit": False,
}

consumer = Consumer(conf)
consumer.subscribe([TOPIC])

count = 0
print(f"[CONSUMER] group={GROUP}")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("[ERROR]", msg.error())
            continue

        event = json.loads(msg.value().decode("utf-8"))
        count += 1

        print(
            f"[PROCESS] event={event['event_id']} "
            f"order={event['order_id']} "
            f"type={event['event_type']} "
            f"partition={msg.partition()} offset={msg.offset()}"
        )

        time.sleep(0.8)

        if FAIL_AFTER and count == FAIL_AFTER:
            print("[FAILURE] intentional stop BEFORE commit")
            raise SystemExit(1)

        consumer.commit(message=msg, asynchronous=False)
        print(f"[COMMIT] partition={msg.partition()} offset={msg.offset()}")

finally:
    consumer.close()
