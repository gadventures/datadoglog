import logging
import socket
import ssl
import typing
from queue import Queue


def do_debug() -> bool:
    return False

# reference to fuly grasp what is happening here
# https://github.com/python/cpython/blob/master/Lib/logging/handlers.py


class DogHandler(logging.handlers.SocketHandler):

    def __init__(self):
        # initialize parent with datadogs info
        # hardcoding is fine given that should this change
        # we likely need to fix this code anyway
        # gives less chance for users to mess things up
        # as well
        super().__init__("intake.logs.datadoghq.com", 10516)

    def makePickle(self, record):
        """prepares record for writing over wire"""
        return "{}\n".format(record.message).encode("utf8")

    def send(self, s):
        """sends serialized data s over wire"""
        if do_debug():
            print("DOGDEBUG send", s)
        super().send(s)

    def makeSocket(self, timeout=1):
        """
        A factory method which allows subclasses to define the precise
        type of socket they want.
        Since our logging data is sensitive we most def want to send it
        over SSL so we subclass and act accordingly
        """
        context = ssl.create_default_context()

        # self.address should contain the host port tuple
        # that was initialized by the SocketHandler.__init__
        # here we rely on inner workings of other peoples code
        # people who encourage us to do so while having no idea
        # what parts of their code we are depending on
        # but hey this is official python code and docs
        # surely they know what they are doing, right?
        # personally if any of this breaks in future versions of python
        # not least bit surprised
        # written and tested for python 3.6
        s = socket.create_connection(self.address, timeout=timeout)
        conn = context.wrap_socket(s, server_hostname=self.host)
        if do_debug():
            print("DOGDEBUG makeSocket connected {} to {} with {}".format(
                str(conn), str(self.address), conn.version()))
        return conn


def start_logger(que: Queue) -> typing.Callable:
    """
    this starts the QueueListener in separate thread
    that will just consume and forward all the messages to datadog
    so logging should never ever block
    and can be used by any high performance apps
    it returns a function which called will properly shut down the listener thread
    and close tcp sockets
    """
    if do_debug():
        print('Starting logger for queue', que)
    handler = DogHandler()
    listener = logging.handlers.QueueListener(que, handler)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    listener.start()
    return listener.stop
