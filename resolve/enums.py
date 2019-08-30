"""Enums related to the resolver and inter-module communication."""
from enum import Enum, IntEnum


class SystemStatus(IntEnum):
    """Represents system status."""

    BOOTING = 1
    READY = 2
    RUNNING = 3


class Module(Enum):
    """Represents a module."""

    HELLO_WORLD_MODULE = 1


class Function(Enum):
    """Represents an interface function in a module."""

    FOO = 1


class MessageType(IntEnum):
    """Represents a message type sent between nodes."""

    HELLO_WORD_MESSAGE = 1
