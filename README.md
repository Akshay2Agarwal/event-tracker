# Event-Tracker
##### Install Confluent Platform: 5.1.0, librdkafka, Cassandra 3.11.3, Apache Spark version 2.3.1

##### Create keyspace events in cassandra and create table in the same using:
    CREATE TABLE events.user_event (
    user_id int,
    group_id int,
    details map<text, text>,
    event_timestamp timestamp,
    name text,
    PRIMARY KEY (user_id, group_id)
    ) WITH CLUSTERING ORDER BY (group_id ASC)
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'chunk_length_in_kb': '64', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND crc_check_chance = 1.0
    AND dclocal_read_repair_chance = 0.1
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair_chance = 0.0
    AND speculative_retry = '99PERCENTILE';


##### Use pipenv to install required python environment and packages as:
    pipenv install --ignore-pipfile
    pipenv shell

##### Create instance package and config.py and define:
    KAFKA_BOOTSTRAP_SERVER = "localhost:9092"
    SCHEMA_REGISTRY_URL = 'http://localhost:8081'
    
##### Run spark job to consume from topics:
    spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.0,datastax:spark-cassandra-connector:2.4.0-s_2.11 --conf spark.cassandra.connection.host=127.0.0.1  service/event_creation_job.py 
