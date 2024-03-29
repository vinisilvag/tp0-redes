import sys
import socket
import struct


def make_sas(response: bytes):
    _, net_id, nonce, token = struct.unpack("!h 12s i 64s", response)
    net_id = net_id.decode().strip()
    token = token.decode()
    return f"{net_id}:{nonce}:{token}"


def make_gas():
    pass


def main():
    host, port, command = sys.argv[1:4]
    server_address = (host, int(port))
    args = sys.argv[4:]

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(server_address)
        match command:
            case "itr":
                net_id, nonce = args
                message = struct.pack(
                    "!h 12s i",
                    1,
                    net_id.ljust(12, " ").encode(),
                    int(nonce),
                )
                sock.send(message)
                response = sock.recv(82)
                print(make_sas(response))
            case "itv":
                sas = args[0]
                net_id, nonce, token = sas.split(":")
                message = struct.pack(
                    "!h 12s i 64s",
                    3,
                    net_id.ljust(12, " ").encode(),
                    int(nonce),
                    token.encode()
                )
                sock.send(message)
                response = sock.recv(83)
                _, _, _, _, valid = struct.unpack("!h 12s i 64s b", response)
                print(valid)


if __name__ == "__main__":
    main()
