"""Contains code related to the module resolver."""

# standard
import logging
from threading import Thread
import os
import requests
import time

# local
from resolve.enums import Module, MessageType, SystemStatus
from conf.config import get_nodes
from communication.zeromq import rate_limiter
from metrics.messages import msgs_sent

# globals
logger = logging.getLogger(__name__)


class Resolver:
    """Module resolver that facilitates communication between modules."""

    def __init__(self, testing=False):
        """Initializes the resolver."""
        self.modules = None
        self.senders = {}
        self.fd_senders = {}
        self.receiver = None
        self.fd_receiver = None
        self.nodes = get_nodes()

        self.own_comm_ready = False
        self.other_comm_ready = False
        self.system_status = SystemStatus.BOOTING

        # check other nodes for system ready before starting system
        if not testing:
            t = Thread(target=self.wait_for_other_nodes)
            t.start()

        # inject resolver in rate limiter module
        rate_limiter.resolver = self

        # Support non-self-stabilizing mode
        self.self_stab = os.getenv("NON_SELF_STAB") is None

    def wait_for_other_nodes(self):
        """Write me."""
        if len(self.nodes) == 1:
            self.other_comm_ready = True
            return

        system_ready = False
        while not system_ready:
            nodes_ready = []
            for n_id, node in self.nodes.items():
                try:
                    r = requests.get(f"http://{node.hostname}:{4000 + n_id}")
                    is_ready = (r.status_code == 200 and
                                r.json()["status"] !=
                                SystemStatus.BOOTING.name)
                    nodes_ready.append(is_ready)
                except Exception:
                    nodes_ready.append(False)
            system_ready = all(nodes_ready)
            if not system_ready:
                time.sleep(0.1)
        self.system_status = SystemStatus.RUNNING
        logger.info(f"System running at UNIX time {time.time()}")

    def system_running(self):
        """Return True if the system as a whole i running."""
        return self.system_status == SystemStatus.RUNNING

    def set_modules(self, modules):
        """Sets the modules dict of the resolver."""
        self.modules = modules

    # inter-node communication methods
    def send_to_node(self, node_id, msg_dct, fd_msg=False):
        """Sends a message to a given node.

        Message should be a dictionary, which will be serialized to json
        and converted to a byte object before sent over the links to
        the other node.
        """
        if node_id not in self.senders and node_id not in self.fd_senders:
            logger.error(f"Non-existing sender for node {node_id}")

        try:
            sender = (self.senders[node_id] if not fd_msg else
                      self.fd_senders[node_id])
            sender.add_msg_to_queue(msg_dct)
        except Exception as e:
            logger.error(f"Something went wrong when sending msg {msg_dct} " +
                         f"to node {node_id}. Error: {e}")

    def broadcast(self, msg_dct):
        """Broadcasts a message to all nodes."""
        for node_id, _ in self.senders.items():
            self.send_to_node(node_id, msg_dct)

    def dispatch_msg(self, msg):
        """Routes received message to the correct module."""
        msg_type = msg["type"]
        if msg_type == MessageType.HELLO_WORD_MESSAGE:
            self.modules[Module.HELLO_WORLD_MODULE].receive_msg(msg)
        else:
            logger.error(f"Message with invalid type {msg_type} cannot be" +
                         " dispatched")

    def on_message_sent(self, msg={}, metric_data={}):
        """Callback function when a communication module has sent the message.

        Used for metrics.
        """
        id = int(os.getenv("ID"))
        # emit message sent message
        msgs_sent.labels(id).inc()

    def get_hello_world_module_data(self):
        return self.modules[Module.HELLO_WORLD_MODULE].get_data()
