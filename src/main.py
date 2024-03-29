import sys
import socket
import struct


def make_sas(response: bytes):
    """
    Receive a server response and unpack it into an SAS string
    """

    _, net_id, nonce, sas_token = struct.unpack("!h12si64s", response)
    net_id = net_id.decode().strip()
    sas_token = sas_token.decode()
    return f"{net_id}:{nonce}:{sas_token}"


def make_gas(n: int, response: bytes):
    """
    Receive a server response and unpack it into an GAS string
    """

    gas = []
    _, _, * \
        group_members_sas, gas_token = struct.unpack(
            f"!hh{'80s' * int(n)}64s", response)
    for sas in group_members_sas:
        net_id, nonce, sas_token = struct.unpack("!12si64s", sas)
        net_id = net_id.decode().strip()
        sas_token = sas_token.decode()
        gas.append(f"{net_id}:{nonce}:{sas_token}")
    gas.append(gas_token.decode())
    return "+".join(gas)


def encode_multiple_sas(group_members_sas):
    """
    Receive an array of SAS strings and encode it all in a byte string
    """

    request = []
    for sas in group_members_sas:
        net_id, nonce, token = sas.split(":")
        request.append(struct.pack("!12si64s", net_id.ljust(
            12, " ").encode(), int(nonce), token.encode()))
    return request


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
                    "!h12si",
                    1,
                    net_id.ljust(12, " ").encode(),
                    int(nonce),
                )
                sock.send(message)
                response = sock.recv(82)
                print(make_sas(response))
            case "itv":
                member_sas = args[0]
                net_id, nonce, token = member_sas.split(":")
                message = struct.pack(
                    "!h12si64s",
                    3,
                    net_id.ljust(12, " ").encode(),
                    int(nonce),
                    token.encode()
                )
                sock.send(message)
                response = sock.recv(83)
                _, _, _, _, valid = struct.unpack("!h12si64sb", response)
                print(valid)
            case "gtr":
                n = args[0]
                group_members_sas = args[1:]
                message = struct.pack(
                    f"!hh{'80s' * int(n)}",
                    5,
                    int(n),
                    *encode_multiple_sas(group_members_sas),
                )
                sock.send(message)
                response = sock.recv(4 + (80 * int(n)) + 64)
                print(make_gas(int(n), response))
            case "gtv":
                gas = args[0]
                gas_token = gas.split("+")[-1]
                group_members_sas = gas.split("+")[:-1]
                n = len(group_members_sas)
                message = struct.pack(
                    f"!hh{'80s' * n}64s",
                    7,
                    n,
                    *encode_multiple_sas(group_members_sas),
                    gas_token.encode()
                )
                sock.send(message)
                response = sock.recv(4 + (80 * n) + 64 + 1)
                _, _, * \
                    _, valid = struct.unpack(
                        f"!hh{'80s' * n}64sb", response)
                print(valid)


if __name__ == "__main__":
    main()
