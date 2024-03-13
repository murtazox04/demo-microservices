from confluent_kafka import Consumer

from decouple import config

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

    print("Received message: {}".format(msg.value()))
