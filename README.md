# Event-Tracker
##### Install Confluent Platform: 5.1.0, librdkafka, Cassandra 3.11.3, Apache Spark version 2.3.1
##### Use pipenv to install required python environment and packages as:
    pipenv install --ignore-pipfile
    pipenv shell

##### Create instance package and config.py and define:
    KAFKA_BOOTSTRAP_SERVER = "localhost:9092"
    SCHEMA_REGISTRY_URL = 'http://localhost:8081'
    
##### Run spark job to consume from topics:
    spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.0,datastax:spark-cassandra-connector:2.4.0-s_2.11 --conf spark.cassandra.connection.host=127.0.0.1  jobs/event_creation_job.py
    spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.0,datastax:spark-cassandra-connector:2.4.0-s_2.11 --conf spark.cassandra.connection.host=127.0.0.1  jobs/event_enrichment_job.py  