# datadoglog

Python logging handlers for sending logs to Datadog

## Installation

to `requirements.txt` add

    -e git+https://github.com/gadventures/datadoglog.git@0.2.0#egg=datadoglog

## Usage

This package uses the `QueueHandler` logger, so you need to start the logger
thread and give it a `Queue`.

```python
import atexit
from queue import Queue

from datadoglog import start_datadog_logger

queue = Queue()
stop_logger = start_datadog_logger(queue)
atexit.register(stop_logger)
```

Now that the handler is running you can configure your logging. Below is a
sample config using python's `dictConfig`.

```python
from logging.config import dictConfig

log_config = {
    "version": 1,
    "formatters": {
        "data_dog": {
            "()": 'datadoglog.DatadogFormatter',
            "app_key": "<datadog_api_key>",
            "env": "production",
            "service": "project-web",
            "source": "project",
        },
    },
    "handlers": {
        "dd_handler": {
            "class": 'logging.handlers.QueueHandler',
            "formatter": 'data_dog',
            "level": 'INFO',
            "queue": queue,
        },
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": ["dd_handler"],
        },
    },
}

# set the config
dictConfig(log_config)
```
