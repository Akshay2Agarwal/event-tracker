# Event-Tracker
##### Install confluent kafka, librdkafka
##### Use pipenv to install required python environment and packages as:
pipenv install --ignore-pipfile
pipenv shell

##### Create instance package and config.py and define:
    KAFKA_BOOTSTRAP_SERVER = "localhost:9092"
    SCHEMA_REGISTRY_URL = 'http://localhost:8081'
