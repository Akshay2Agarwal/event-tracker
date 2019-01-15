import datetime
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import SQLContext
from pyspark.context import SparkContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql.functions import *
import json


def process_event(event):
    user_event_map = {
        'user_id': int(event['userId']),
        'group_id': int(event['groupId']),
        'event_timestamp': datetime.datetime.now(),
        'name': event['eventName'],
        'details': event['details']
    }

    return user_event_map


def update_event_info(events_rdd, user_event_tbl, sqlContext):

    events_userId = events_rdd.map(lambda event: event['userId']).distinct()
    past_user_events = user_event_tbl.filter(user_event_tbl['user_id'].isin(events_userId.collect()))
    events_map = events_rdd.map(lambda v: process_event(v))
    events_DF = sqlContext.createDataFrame(events_map, user_event_tbl.schema)

    final_events_DF = events_DF.alias('l').\
        join(past_user_events.alias('r'), events_DF.user_id == past_user_events.user_id, how="left")

    final_DF = final_events_DF.withColumn("merged_details", map_concat(col("l.details"), col("r.details"))).\
        select(["l.user_id", "r.group_id", "merged_details", "l.event_timestamp", "l.name"]).\
        withColumnRenamed("merged_details", "details")
    final_DF.write.format("org.apache.spark.sql.cassandra").mode('append').\
        options(table="user_event", keyspace="events").save()


if __name__ == "__main__":
    conf = SparkConf()

    conf.setMaster("local[2]")
    conf.setAppName("event_enrichment_job")
    conf.set("spark.executor.memory", "1g")
    conf.set("spark.cassandra.connection.host", "127.0.0.1")

    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")

    sqlContext = SQLContext(sc)
    user_event_table = sqlContext.read.format("org.apache.spark.sql.cassandra").options(table="user_event",
                                                                                        keyspace="events").load()
    str_ctxt = StreamingContext(sc, 1)
    kvs = KafkaUtils.createStream(str_ctxt, "localhost:2182", "spark-streaming-consumer", {"event": 2})
    events = kvs.map(lambda v: json.loads(v[1]))
    events.foreachRDD(lambda eventsRDD:
                      update_event_info(eventsRDD, user_event_table, sqlContext) if eventsRDD.count() > 0 else None)

str_ctxt.start()
str_ctxt.awaitTermination()