# datadoglog
Python logging handlers for sending logs to Data Dog

## Installation

to `requirements.txt` add

    -e git+https://github.com/gadventures/datadoglog.git@0.1.0#egg=datadoglog

## Setup

This package uses QueueHandler logger so first thing you need to start the logger thread and give it a Queue

```python
import atexit
from queue import Queue
from datadoglog import start_logger

que = Queue()
stop_func = start_logger(que)
atexit.register(stop_func)
```
    
Now that the consumer is runnning you can configure your logging
below is a sample config using python dictConfig

```python
from logging.config import dictConfig

log_config = {
    "version": 1,
    "formatters": {
        "data_dog": {
            "()": 'datadoglog.FormatFactory',
            "app_key": config.DATADOG_APP_KEY,
            "source": "sieve",
            "service": "server_log",
            "env": "production" if config.PROD else "staging",
        },
    },
    "handlers": {
        "my_handler": {
            "class": 'logging.handlers.QueueHandler',
            "queue": que,
            "level": 'INFO',
            "formatter": 'data_dog',
        },
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": ["my_handler"],
        },
    },
}

dictConfig(log_config)
```
