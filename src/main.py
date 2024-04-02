"""
main.py

Main module of the project. Serves as the entry point for the project and contains the main functionality.

Author: Vinicius Gomes
Date: 01/04/2024
"""

import sys
import socket
from constants import COMMANDS
from errors import (
    WrongCommandNumberArguments,
    MissingArguments,
    UnknownCommand,
    RequestFailed,
)
from utils import (
    get_address_family,
    valid_arg_count,
    encode_message,
    has_error,
    decode_response,
)


def main():
    """
    Main function of the project. It is executed when the script is run.
    """

    if len(sys.argv) < 4:
        raise MissingArguments(3, len(sys.argv) - 1)

    host, port, command = sys.argv[1:4]
    server_address = (host, int(port))
    args = sys.argv[4:]

    if command not in COMMANDS:
        raise UnknownCommand(command)

    if not valid_arg_count(command, args):
        raise WrongCommandNumberArguments(command)

    with socket.socket(get_address_family(host, int(port)), socket.SOCK_DGRAM) as sock:
        sock.settimeout(10)
        sock.connect(server_address)
        succeeded = False

        while not succeeded:
            try:
                message, n = encode_message(command, args)
                sock.send(message)
                response = sock.recv(1024)

                error, error_code = has_error(response)
                if error:
                    raise RequestFailed(error_code)

                print(decode_response(command, response, n))

                # if reached it means that the message was successfully sended
                # and an expected response was obtained
                succeeded = True
            except socket.timeout:
                print("Failed to sent the message. Resending.")


if __name__ == "__main__":
    main()
