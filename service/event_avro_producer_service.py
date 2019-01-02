from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from flask import current_app as app
import os


def message_acked(err, msg):
    if err is not None:
        app.logger.error("Failed to deliver message: {0}: {1}".format(msg.value(), err.str()))
        return True
    else:
        app.logger.info("Message produced to topic: {0}[{1}]".format(msg.topic(), msg.partition()))
        return False


def produce_event_with_schema(topic, event_message):
    event_schema = avro.load(os.path.abspath(os.getcwd())+"/schemas/event_schema.avsc")
    producer = AvroProducer({'bootstrap.servers': app.config["KAFKA_BOOTSTRAP_SERVER"],
                             'schema.registry.url': app.config["SCHEMA_REGISTRY_URL"]},
                            default_value_schema=event_schema)
    producer.poll(0)
    producer.produce(topic=topic, value=event_message, on_delivery=message_acked)
    producer.flush()
