import time
from flask import Flask, g, request
from app_logging import setup_logging
import colors
from config.config import Config
from service.event_avro_producer_service import produce_event_with_schema
from service.event_producer_service import produce_event
from service.kafka_consumer import KafkaConsumer
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config())
app.config.from_pyfile('config.py')

setup_logging()


def run_kafka_consumer(topic_name, current_app):
    def callback(msg):
        print(msg)
    kafka_consumer = KafkaConsumer(topic_name, current_app, callback)
    kafka_consumer.consume()


# Uncomment below lines to use kafka consumers
# @app.before_first_request
# def run_kafka():
#     try:
#         for topic, topic_config in app.config['TOPICS_CONFIGURATION'].items():
#             consumers_pool = ThreadPoolExecutor(max_workers=topic_config['max_consumers'])
#             consumers_pool.submit(run_kafka_consumer, **{'topic_name': topic, 'current_app': app})
#     except Exception as e:
#         app.logger.exception(e)


@app.before_request
def start_timer():
    """ Starting timer for each request"""
    g.start = time.time()


@app.after_request
def after_request(response):
    """ Logging after every request. """

    if request.path == '/favicon.ico':
        return response
    elif request.path.startswith('/static'):
        return response

    now = time.time()
    duration = round(now - g.start, 2)

    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    host = request.host.split(':', 1)[0]
    args = dict(request.args)

    log_params = [
        ('method', request.method, 'cyan'),
        ('path', request.path, 'blue'),
        ('status', response.status_code, 'yellow'),
        ('ip', ip, 'red'),
        ('host', host, 'magenta'),
        ('params', args, 'blue'),
        ('duration', duration, 'green')
    ]

    request_id = request.headers.get('X-Request-ID')
    if request_id:
        log_params.append(('request_id', request_id, 'yellow'))

    parts = []
    for name, value, color in log_params:
        part = colors.color("{}={}".format(name, value), fg=color)
        parts.append(part)
    line = " ".join(parts)

    app.logger.info(line)

    return response


@app.route("/user/<int:user_id>/event/<event_name>", methods=['POST'])
def produce_event_controller(user_id, event_name):
    if event_name in app.config['EVENTS_WITH_SCHEMA']:
        event_message = {'userId': user_id, 'eventName': event_name, 'groupId': int(user_id)%2}
        produce_event_with_schema(app.config['TOPICS']['EVENTS_WITH_SCHEMA'], event_message)
    else:
        event_message = {**{'userId': user_id, 'eventName': event_name, 'groupId': int(user_id)%2},
                         **request.get_json()}
        produce_event(bytes(user_id), app.config['TOPICS']['EVENTS_WITHOUT_SCHEMA'], event_message)
    return '', 204


if __name__ == '__main__':
    app.run()
