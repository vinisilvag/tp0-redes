import sys
import socket
import struct
from command import Command
from errors import MissingArguments, UnknownCommand, WrongNumberOfArguments


def valid_command_arguments(command: Command, arguments: list[str]):
    """Validate if the received arguments match the command."""

    match command:
        case Command.ITR:
            return len(arguments) == 2
        case Command.ITV:
            return len(arguments) == 1
        case Command.GTR:
            return len(arguments) >= 2
        case Command.GTV:
            return len(arguments) == 1


def main():
    """Main program function"""

    if len(sys.argv) < 4:
        raise MissingArguments(3, len(sys.argv) - 1)

    host, port, command = sys.argv[1:4]

    try:
        command = Command(command)
    except Exception as exc:
        raise UnknownCommand(command) from exc

    args = sys.argv[4:]

    if not valid_command_arguments(command, args):
        raise WrongNumberOfArguments(command)

    # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    #     s.connect((host, int(port)))
    match command:
        case Command.ITR:
            net_id, nonce = args
            print(net_id, nonce)
            message = struct.pack('h12si', 1,
                                  bytes(
                                      net_id.ljust(12, " "),
                                      encoding="ascii"
                                  ),
                                  int(nonce))
            print("Message sent: ", message)
            # s.send(message)
            # response = s.recv(82)
            # print("Response received: ", response)
        case Command.ITV:
            net_id, nonce, token = args[0].split(":")
            print(net_id, nonce, token)
        case Command.GTR:
            n = args[0]
            sas = args[1:]
            print(n)
            print(sas)
        case Command.GTV:
            splitted = args[0].split("+")
            sas = splitted[:-1]
            token = splitted[-1]
            print(sas, token)


if __name__ == "__main__":
    main()
