import datetime
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import SQLContext
from pyspark.context import SparkContext
from pyspark.streaming.kafka import KafkaUtils
from confluent_kafka.avro.serializer.message_serializer import MessageSerializer
from confluent_kafka.avro.cached_schema_registry_client import CachedSchemaRegistryClient


def process_event(event):

    user_event_map = {
        'user_id': int(event['userId']),
        'group_id': int(event['groupId']),
        'event_timestamp': datetime.datetime.now(),
        'name': event['eventName'],
        'details': {
            'created_at': str(datetime.datetime.now())
        }
    }

    return user_event_map


if __name__ == "__main__":
    conf = SparkConf()
    conf.setMaster("local[2]")
    conf.setAppName("event_creation_job")
    conf.set("spark.executor.memory", "1g")
    conf.set("spark.cassandra.connection.host", "127.0.0.1")

    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")

    schema_registry_client = CachedSchemaRegistryClient(url='http://127.0.0.1:8081')
    serializer = MessageSerializer(schema_registry_client)

    def decoder(msg):
        decoded_message = serializer.decode_message(msg)
        return decoded_message


    str_ctxt = StreamingContext(sc, 1)
    kvs = KafkaUtils.createStream(str_ctxt, "localhost:2182", "spark-streaming-consumer", {"event_schema": 2},
                                  valueDecoder=decoder)
    events = kvs.mapValues(lambda v: process_event(v))
    sqlContext = SQLContext(sc)
    user_event_table = sqlContext.read.format("org.apache.spark.sql.cassandra").options(table="user_event",
                                                                                        keyspace="events").load()
    events.foreachRDD(lambda eventsRDD: sqlContext.createDataFrame(
        eventsRDD.map(lambda event: event[1]), user_event_table.schema).
                      write.format("org.apache.spark.sql.cassandra").mode('append').
                      options(table="user_event", keyspace="events").save() if not eventsRDD.isEmpty() else None)

str_ctxt.start()
str_ctxt.awaitTermination()