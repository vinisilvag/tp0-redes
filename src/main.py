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
              "Correct usage is:",
              "  python3 src/main.py <host> <port> <command>",
              sep="\n")
        sys.exit()

    host, port, command = sys.argv[1:4]

    if not valid_command(command):
        print("Unknown command.",
              "Available commands are: 'itr', 'itv', 'gtr' and 'gtv'.", sep="\n")
        sys.exit()

    args = sys.argv[4:]

    if not valid_command_arguments(command, args):
        print("Wrong number of arguments for the selected command.",
              "Correct usage is:",
              "  itr <id> <nonce>",
              "  itv <SAS>",
              "  gtr <N> <SAS-1> <SAS-2> ... <SAS-N>",
              "  gtv <GAS>", sep="\n")
        sys.exit()

    # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    #     s.connect((host, int(port)))
    match command:
        case 'itr':
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
        case 'itv':
            net_id, nonce, token = args[0].split(":")
            print(net_id, nonce, token)
        case 'gtr':
            n = args[0]
            sas = args[1:]
            print(n)
            print(sas)
        case 'gtv':
            splitted = args[0].split("+")
            sas = splitted[:-1]
            token = splitted[-1]
            print(sas, token)
        case _:
            print("Unreachable.")
            sys.exit()


if __name__ == "__main__":
    main()
