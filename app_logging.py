import os
import logging
from logging.config import dictConfig
import pathlib

logs_directory = os.getcwd()+"/logs"
pathlib.Path(logs_directory).mkdir(parents=True, exist_ok=True)


def setup_logging():
    logging_config = dict(
        version = 1,
        disable_existing_loggers = True,
        formatters = {
            'f': {
                'format':'%(asctime)s %(levelname)-8s %(message)s',
                'datefmt': "%Y/%m/%d %H:%M:%S %Z%z"
            },
            'simple': {
                'format': "%(asctime)s %(process)d %(filename)s %(lineno)s %(levelname)s %(message)s",
                'datefmt': "%Y/%m/%d %H:%M:%S %Z%z"
            },
            "extra": {
                "format": "%(asctime)s %(process)d %(thread)d %(filename)s %(lineno)s %(funcName)s %(levelname)s %(message)s",
                'datefmt': "%Y/%m/%d %H:%M:%S %Z%z"
            }
        },
        handlers = {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            'info_file_handler': {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": 'INFO',
                "formatter": "extra",
                "filename": logs_directory+"/event_tracker_info.log",
                "when": "midnight",
                "interval": 1,
                "backupCount": 31,
                "encoding": "utf8"
            },
            'error_file_handler': {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": 'ERROR',
                "formatter": "extra",
                "filename": logs_directory+"/event_tracker_errors.log",
                "when": "midnight",
                "interval": 1,
                "backupCount": 31,
                "encoding": "utf8"
            }
        },
        loggers = {
            "my_module": {
                "level": "ERROR",
                "handlers": ["console"],
                "propagate": "no"
            }
        },
        root = {
            "level": "INFO",
            "handlers": ["console", "info_file_handler", "error_file_handler"]
        }
    )

    dictConfig(logging_config)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)