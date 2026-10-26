import json
import time
from pathlib import Path
from confluent_kafka import Producer

BROKER = "localhost:9092"
TOPIC = "dpw3-events"

producer = Producer({"bootstrap.servers": BROKER})
events = json.loads((Path(__file__).parent.parent / "data/payment-events.json").read_text())

for event in events:
    # Tentukan sendiri key yang tepat untuk kebutuhan ordering.
    key = event["order_id"]
    producer.produce(
        TOPIC,
        key=key,
        value=json.dumps(event).encode("utf-8"),
    )
    producer.poll(0)
    print(f"[PRODUCER] {event['event_id']} order={event['order_id']} key={key}")
    time.sleep(0.3)

producer.flush()
print("[PRODUCER] done")
