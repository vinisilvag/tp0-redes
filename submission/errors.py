"""
errors.py

Module containing custom exception classes.
"""

from constants import ERRORS


class MissingArguments(Exception):
    """
    Exception raised when the number of arguments is insufficient.

    Attributes:
        total (int): The total number of arguments expected.
        received (int): The number of arguments received.
    """

    def __init__(self, total: int, received: int):
        super().__init__(
            f"Expected at least {total} arguments but received {received}."
        )


class WrongCommandNumberArguments(Exception):
    """
    Exception raised when the number of arguments received is incorrect for a command.

    Attributes:
        command (str): The command for which the number of arguments is incorrect.
    """

    def __init__(self, command: str):
        super().__init__(f"Wrong number of arguments for the command: '{command}'.")


class UnknownCommand(Exception):
    """
    Exception raised when an unknown command is received.

    Attributes:
        command (str): The unknown command received.
    """

    def __init__(self, command: str):
        super().__init__(f"Unknown command: '{command}'.")


class InvalidHost(Exception):
    """
    Exception raised when unable to connect to a host.

    Attributes:
        host (str): The host that failed to connect.
        port (int): The port number of the host.
    """

    def __init__(self, host: str, port: int):
        super().__init__(f"Unable to connect to the host: {host}:{port}.")


class RequestFailed(Exception):
    """
    Exception raised when an error occurred during server-client communication.

    Attributes:
        error_code (int): The error code received from the server.
    """

    def __init__(self, error_code: int):
        super().__init__(
            f"Request failed with error code {error_code}: {ERRORS[error_code]}."
        )
