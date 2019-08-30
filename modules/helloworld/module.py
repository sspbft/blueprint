"""Contains code related to the event-driven failure detector module."""

# standard
import logging
import time

# local
from modules.constants import RUN_SLEEP
from resolve.enums import MessageType

# globals
logger = logging.getLogger(__name__)


class HelloWorldModule:
    """Sample module

    Continously broadcasts "hello world" to all other nodes in the system.
    """

    def __init__(self, id, resolver, n, f):
        """Initializes the module."""
        self.resolver = resolver
        self.id = id
        self.number_of_nodes = n
        self.number_of_byzantine = f
        self.msgs_sent = 0

    def run(self, testing=False):
        """Main loop for the hello world module

        This loop continuously broadcasts "hello world" to all other nodes.
        """
        # block until system is ready
        while not testing and not self.resolver.system_running():
            time.sleep(RUN_SLEEP)

        while True:
            # broadcast hello world to all other nodes forever
            self.broadcast("hello world")
            time.sleep(RUN_SLEEP)

    def receive_msg(self, msg):
        """Called whenever a message is received from another processor

        Good place for more exciting things than logging the message..
        """
        logger.info(f"Got msg {msg['data']['message']} from {msg['sender']}")

    def send_msg(self, processor_id, msg, owner_id):
        """Sends a token to another processor."""
        msg = {
            "type": MessageType.HELLO_WORD_MESSAGE,
            "sender": self.id,
            "data": {
                "message": msg
            }
        }
        self.resolver.send_to_node(processor_id, msg)
        self.msgs_sent += 1

    def broadcast(self, msg):
        """Broadcasts a message to all other processors."""
        for processor_id in range(self.number_of_nodes):
            if processor_id != self.id:
                self.send_msg(processor_id, msg, self.id)

    def get_data(self):
        """Called by the API, used to expose data to 3rd party services."""
        return {"msgs_sent": self.msgs_sent}
