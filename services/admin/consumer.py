
import os
import json
import django
from decouple import config
from confluent_kafka import Consumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


consumer = Consumer({
    'bootstrap.servers': config("KAFKA_BOOTSTRAP_SERVERS"),
    'security.protocol': config("KAFKA_SECURITY_PROTOCOL"),
    'sasl.username': config("KAFKA_SASL_USERNAME"),
    'sasl.password': config("KAFKA_SASL_PASSWORD"),
    'sasl.mechanism': config("KAFKA_SASL_MECHANISM"),
    'group.id': config("KAFKA_GROUP_ID"),
    'auto.offset.reset': 'earliest'
})

consumer.subscribe([config("KAFKA_TOPIC")])

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print(msg.key())

    import core.listeners

    getattr(core.listeners, msg.key().decode('utf-8'))(json.loads(msg.value()))


consumer.close()
