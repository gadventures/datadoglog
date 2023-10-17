import json
import logging
import os
import traceback
from datetime import datetime
from datetime import timezone


class DatadogFormatter:
    """
    Formats our log record into a form that Datadog understands.

    More information here:
    https://docs.datadoghq.com/logs/log_configuration/attributes_naming_convention/
    """

    __slots__ = (
        "app_key",
        "env",
        "host",
        "service",
        "source",
    )

    def __init__(self, app_key: str, env: str, service: str, source: str) -> None:
        self.app_key = app_key
        self.env = env
        self.host = os.uname().nodename
        self.service = service
        self.source = source

    def _format(self, record: logging.LogRecord) -> str:
        data = {
            # when
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            # standard facets/attributes
            "dd.env": self.env,
            "dd.host": self.host,
            "dd.service": self.service,
            "dd.source": self.source,
            # the log info and message
            "logger.name": record.name,
            "message": record.getMessage(),
            "status": record.levelname,
            # where the log record came from
            "lineno": record.lineno,
            "pathname": record.pathname,
        }
        # work with exception info here
        exc_info = record.exc_info
        if exc_info:
            (exc_type, exc_value, exc_tb) = exc_info
            data["error.kind"] = str(exc_type)
            data["error.message"] = str(exc_value)
            # NOTE: format_tb, which calls format_list, will add newlines for
            #       us, hence the join on empty-string.
            data["error.stack"] = "".join(traceback.format_tb(exc_tb))

        return f"{self.app_key} {json.dumps(data)}"

    def format(self, record: logging.LogRecord) -> str:
        """
        Format this log record.

        Python logging expects formatting of a message to also adjust the
        internal attributes of LogRecord (so sad). On the other hand,
        record.message is the only thing that will matter from here on.
        """
        record.message = self._format(record)
        return record.message
