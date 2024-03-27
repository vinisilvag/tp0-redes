"""Define all possible errors that can be raised in the main program"""

from command import Command


class MissingArguments(Exception):
    """Raised when the number of arguments is insufficient"""

    def __init__(self, total: int, received: int):
        super().__init__(
            f"Expected at least {total} arguments but received {received}.")


class UnknownCommand(Exception):
    """Raised when an unknown command is received"""

    def __init__(self, command: Command):
        super().__init__(
            f"Unknown command: '{command}'.")


class WrongNumberOfArguments(Exception):
    """Raised when the number of arguments received is incorrect"""

    def __init__(self, command: Command):
        super().__init__(
            f"Wrong number of arguments for the command: '{command}'.")
