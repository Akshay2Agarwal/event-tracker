class Config:
    EVENTS_WITH_SCHEMA = ['add', 'delete']
    EVENTS_WITHOUT_SCHEMA = ['update']
    EVENTS_ID = {'add': 1, 'delete': 2, 'update': 3}
    TOPICS = {
        'EVENTS_WITHOUT_SCHEMA': 'event',
        'EVENTS_WITH_SCHEMA': 'event_schema'
    }

    TOPICS_CONFIGURATION = {
        'event': {
            'type': 'simple',
            'max_consumers': 2,
            'bootstrap.servers': "localhost:9092",
            'group.id': 'event',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'session.timeout.ms': 6000
        },
        'event_schema': {
            'type': 'avro',
            'max_consumers': 2,
            'bootstrap.servers': "localhost:9092",
            'group.id': 'event_schema',
            'schema.registry.url': 'http://localhost:8081',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'session.timeout.ms': 6000,
        }
    }