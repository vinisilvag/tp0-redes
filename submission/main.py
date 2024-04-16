"""
main.py

Main module of the project. Serves as the entry point for the project and contains
the main functionality.

Author: Vinicius Gomes - 2021421869
Date: 09/04/2024
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
    get_address_family_and_ip,
    valid_arg_count,
    encode_message,
    decode_response,
    has_error,
)


def main():
    """Main function of the project. It is executed when the script is run."""

    if len(sys.argv) < 4:
        raise MissingArguments(3, len(sys.argv) - 1)

    host, port, command = sys.argv[1:4]
    args = sys.argv[4:]

    if command not in COMMANDS:
        raise UnknownCommand(command)
    if not valid_arg_count(command, args):
        raise WrongCommandNumberArguments(command)

    addr_family, ip = get_address_family_and_ip(host, int(port))
    server_address = (ip, int(port))
    with socket.socket(addr_family, socket.SOCK_DGRAM) as sock:
        sock.settimeout(10.0)
        sock.connect(server_address)
        succeeded = False
        retries = 0

        while not succeeded and retries != 3:
            try:
                message = encode_message(command, args)
                sock.send(message)
                response = sock.recv(1024)

                error, error_code = has_error(response)
                if error and error_code:
                    raise RequestFailed(error_code)

                print(decode_response(command, response, args))

                # the message was successfully sended
                # and an expected response was obtained
                succeeded = True
            except socket.timeout:
                print("Failed to sent the message. Resending.")
                retries += 1

            if retries == 3:
                print("Maximum number of retries achieved. Stopping the program.")


if __name__ == "__main__":
    main()
