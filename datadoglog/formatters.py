import os
import json
import logging
import datetime
import traceback


class FormatFactory:

    app_key = None
    service = None
    source = None
    env = None

    def __init__(self, app_key: str, source: str, service: str, env: str) -> None:
        self.app_key = app_key
        self.service = service
        self.source = source
        self.env = env
        self.host = os.uname().nodename

    def my_format(self, record: logging.LogRecord) -> str:
        data = {
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, datetime.timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"),
            "host": self.host,
            "ddsource": self.source,
            "syslog.env": self.env,
            "service": self.service,
            "message": record.getMessage(),
            "level": record.levelname,
            "logger.name": record.name,
            "pathname": record.pathname,
            "lineno": record.lineno,
        }
        # work with exception here
        ex_info = record.exc_info
        if ex_info is not None:
            (extype, value, tb) = ex_info
            data["error.message"] = str(value)
            data["error.kind"] = str(extype)
            data["error.stack"] = "".join(traceback.format_tb(tb))
        return "{} {}".format(self.app_key, json.dumps(data))

    def format(self, record: logging.LogRecord) -> str:
        # yeah python logging expects formatting of a message to also adjust
        # internal attributes of LogRecord - so sad
        # on the other hand record.message is the only thing that will matter
        # from here on
        record.message = self.my_format(record)
        return record.message
