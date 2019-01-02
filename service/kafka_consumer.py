from confluent_kafka.avro import AvroConsumer, SerializerError
from confluent_kafka.cimpl import KafkaError
from confluent_kafka import Consumer


class KafkaConsumer:
    def __init__(self, topic, current_app, consumer_callback):
        try:
            with current_app.app_context():
                self.app = current_app
                self.topic = topic
                self.consumer_callback = consumer_callback
                self.topic_config = self.app.config['TOPICS_CONFIGURATION'][self.topic]
                if self.topic_config['type'] == "simple":
                    settings = {
                        'bootstrap.servers': self.topic_config['bootstrap.servers'],
                        'group.id': self.topic_config['group.id'],
                        'enable.auto.commit': self.topic_config['enable.auto.commit'],
                        'session.timeout.ms': self.topic_config['session.timeout.ms'],
                    }
                    self.consumer = Consumer(settings)
                elif self.topic_config['type'] == "avro":
                    settings = {
                        'bootstrap.servers': self.topic_config['bootstrap.servers'],
                        'group.id': self.topic_config['group.id'],
                        'schema.registry.url': self.topic_config['schema.registry.url'],
                        'enable.auto.commit': self.topic_config['enable.auto.commit'],
                        'session.timeout.ms': self.topic_config['session.timeout.ms'],
                    }
                    self.consumer = AvroConsumer(settings)
                else:
                    self.app.logger.info("Invalid topic config")
                    raise ValueError("Invalid topic config")
                self.consumer.subscribe([self.topic])
        except Exception as e:
            print(e)

    def consume(self):
        try:
            while True:
                message = self.consumer.poll(1.0)
                if message is None:
                    continue
                elif not message.error():
                    self.consumer_callback(message.value())
                elif message.error().code() == KafkaError._PARTITION_EOF:
                    self.app.logger.info("Reached End of Partition {topic}[{partition}]".
                          format(topic=message.topic(), partition=message.partition()))
                    continue
                else:
                    self.app.logger.exception(message.error())
                    continue
        except KeyboardInterrupt:
            pass
        except SerializerError as e:
            self.app.logger.exception("Message deserialization failed for {}: {}".format(message, e))
        finally:
            self.consumer.close()
