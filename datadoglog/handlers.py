import logging
import socket
import ssl
from queue import Queue
from typing import Callable


class DatadogHandler(logging.handlers.SocketHandler):
    """
    DataDogHandler is a subclass of SocketHandler that sends logs to DD's
    Log intake endpoint.

    To understand the exact nature of what this Handler does, reference:
    https://github.com/python/cpython/blob/master/Lib/logging/handlers.py
    """

    def __init__(self, *, print_debug: bool = False):
        """
        Initialize the parent SocketHandler with datadog's info. Hardcoding
        this is fine, as, should this change we will likely need to fix this
        code anyway. This also gives less chance for users to mess things up
        as well
        """
        # Init parent with Datadog log intake endpoint
        #
        # See: https://docs.datadoghq.com/logs/log_collection/?tab=host#supported-endpoints  # noqa
        super().__init__("intake.logs.datadoghq.com", 10516)

        # print_debug flag
        self.print_debug = print_debug

    def close(self):
        """closes the parent handler"""
        if self.print_debug:
            print("datadoglog: close")
        super().close()

    def makePickle(self, record: logging.LogRecord) -> bytes:
        """prepares record for writing over the wire"""
        return f"{record.message}\n".encode()

    def makeSocket(self, timeout: int = 1) -> ssl.SSLSocket:
        """
        A factory method which allows subclasses to define the precise type of
        they (DD) want. Since our logging data is sensitive we want to send it
        over SSL so we subclass from an ssl and act accordingly.
        """
        context = ssl.create_default_context()

        # self.address should contain the (host, port) tuple that was
        # initialized by the SocketHandler.__init__. Here we rely on inner
        # workings of other peoples code ( people who encourage us to do so
        # while having no idea what parts of their code we are depending on ).
        #
        # NOTE: written and tested for python 3.6
        conn = socket.create_connection(self.address, timeout=timeout)
        sock = context.wrap_socket(conn, server_hostname=self.host)
        if self.print_debug:
            print(
                f"datadoglog: makeSocket connected {sock} to {self.address} "
                f"with {sock.version()}"
            )
        return sock

    def send(self, s):
        """sends serialized s over the wire"""
        if self.print_debug:
            print(f"datadoglog: send {s}")
        super().send(s)


def start_datadog_logger(
    queue: Queue, *, print_debug: bool = False
) -> Callable[[], None]:
    """
    This starts the QueueListener in separate thread, which will consume and
    forward all the messages to Datadog, so the logging should never block the
    client and can be used by any high performance apps. It returns a function,
    when called will properly shut down the listener thread and close the
    underlying TCP socket.
    """
    if print_debug:
        print(f"datadoglog: starting logger for queue {queue}")

    # intialize our handler and underlying threaded queue listener
    handler = DatadogHandler(print_debug=print_debug)
    listener = logging.handlers.QueueListener(queue, handler)

    # set the log format
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)

    # start the listener and return our cancel/stop function to the caller
    listener.start()

    def closer():
        # wait for anything in the queue to process
        listener.stop()
        # close the DatadogHandler
        handler.close()

    return closer
