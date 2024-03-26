import sys
import socket
import struct


def valid_command(command):
    """Validate if the received command is a valid one."""

    match command:
        case 'itr':
            return True
        case 'itv':
            return True
        case 'gtr':
            return True
        case 'gtv':
            return True
        case _:
            return False


def valid_command_arguments(command, arguments):
    """Validate if the received arguments match the command."""

    match command:
        case 'itr':
            return len(arguments) == 2
        case 'itv':
            return len(arguments) == 1
        case 'gtr':
            return len(arguments) >= 2
        case 'gtv':
            return len(arguments) == 1
        case _:
            print("Unknown number of arguments for an unknown command.",
                  "Should be unreachable.", sep="\n")
            sys.exit()


def main():
    if len(sys.argv) < 4:
        print("Missing arguments.",
              "Correct usage is: python3 src/main.py <host> <port> <command>",
              sep="\n")
        sys.exit()

    host, port, command = sys.argv[1:4]

    if not valid_command(command):
        print("Unknown command.",
              "Available commands are: 'itr', 'itv', 'gtr' and 'gtv'.", sep="\n")
        sys.exit()

    if not valid_command_arguments(command, sys.argv[4:]):
        print("Wrong number of arguments.",
              "Correct usage is:",
              "itr <id> <nonce>",
              "itv <SAS>",
              "gtr <N> <SAS-1> <SAS-2> ... <SAS-N>",
              "gtv <GAS>", sep="\n")
        sys.exit()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((host, int(port)))
        match command:
            case 'itr':
                message = struct.pack('h12si', 1, bytes(
                    "2021421869  ", encoding="ascii"), 1)
                print("Message sent: ", message)
                s.send(message)
                response = s.recv(82)
                print("Response received: ", response)
            case 'itv':
                pass
            case 'gtr':
                pass
            case 'gtv':
                pass
            case _:
                print("Unreachable.")
                sys.exit()


if __name__ == "__main__":
    main()
