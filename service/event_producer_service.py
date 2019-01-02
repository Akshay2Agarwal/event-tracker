from confluent_kafka import Producer
from flask import current_app as app
from json import dumps


def message_acked(err, msg):
    if err is not None:
        app.logger.error("Failed to deliver message: {0}: {1}".format(msg.value(), err.str()))
        return True
    else:
        app.logger.info("Message produced: {0} to topic: {1}[{2}]".format(msg.value(), msg.topic(), msg.partition()))
        return False


def produce_event(msg_key, topic, event_message):
    producer = Producer({'bootstrap.servers': app.config["KAFKA_BOOTSTRAP_SERVER"]})
    producer.poll(0)
    producer.produce(topic=topic, value=dumps(event_message).encode('UTF-8'),
                     key=msg_key, on_delivery=message_acked)
    return producer.flush()
