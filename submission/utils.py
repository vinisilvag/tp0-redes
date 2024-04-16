"""
utils.py

Module with utility functions.
"""

import struct
import socket
from errors import InvalidHost, UnknownCommand


def has_connection_family_available(addr_family, available):
    """Check if a certain connection type is available."""

    if addr_family in [conn[0] for conn in available]:
        return True

    return False


def get_address_family_and_ip(host: str, port: int):
    """Get the address family socket type for the given host and port."""

    addr_info = socket.getaddrinfo(host, port, 0, socket.SOCK_DGRAM)
    available = [(info[0], info[4]) for info in addr_info]
    if len(available) == 0:
        raise InvalidHost(host, port)

    try:
        socket.inet_pton(socket.AF_INET, host)
        if has_connection_family_available(socket.AF_INET, available):
            return socket.AF_INET, host
    except socket.error:
        pass

    try:
        socket.gethostbyname(host)
        # get the first address family available
        return available[0][0], available[0][1][0]
    except socket.gaierror:
        pass

    raise InvalidHost(host, port)


def valid_arg_count(command: str, args: list[str]):
    """Check if the number of arguments is valid for the given command."""

    match command:
        case "itr":
            return len(args) == 2
        case "itv":
            return len(args) == 1
        case "gtr":
            return len(args) >= 2
        case "gtv":
            return len(args) == 1


def make_sas(response: bytes):
    """Receive a server response and unpack it into an SAS string."""

    _, net_id, nonce, sas_token = struct.unpack("!h12si64s", response)
    net_id = net_id.decode().strip()
    sas_token = sas_token.decode()
    return f"{net_id}:{nonce}:{sas_token}"


def make_gas(n: int, response: bytes):
    """Receive a server response and unpack it into an GAS string."""

    gas = []
    _, _, *group_members_sas, gas_token = struct.unpack(
        f"!hh{'80s' * int(n)}64s", response
    )
    for sas in group_members_sas:
        net_id, nonce, sas_token = struct.unpack("!12si64s", sas)
        net_id = net_id.decode().strip()
        sas_token = sas_token.decode()
        gas.append(f"{net_id}:{nonce}:{sas_token}")
    gas.append(gas_token.decode())
    return "+".join(gas)


def encode_multiple_sas(group_members_sas):
    """Receive an array of SAS strings and encode it all in a byte string"""

    request = []
    for sas in group_members_sas:
        net_id, nonce, token = sas.split(":")
        request.append(
            struct.pack(
                "!12si64s", net_id.encode("ascii"), int(nonce), token.encode("ascii")
            )
        )
    return request


def encode_message(command: str, args: list[str]):
    """Encode a message based on the given command and arguments."""

    match command:
        case "itr":
            net_id, nonce = args
            return struct.pack(
                "!h12si",
                1,
                net_id.encode("ascii"),
                int(nonce),
            )
        case "itv":
            member_sas = args[0]
            net_id, nonce, token = member_sas.split(":")
            return struct.pack(
                "!h12si64s",
                3,
                net_id.encode("ascii"),
                int(nonce),
                token.encode("ascii"),
            )
        case "gtr":
            n = int(args[0])
            group_members_sas = args[1:]
            return struct.pack(
                f"!hh{'80s' * n}",
                5,
                n,
                *encode_multiple_sas(group_members_sas),
            )
        case "gtv":
            gas = args[0]
            gas_token = gas.split("+")[-1]
            group_members_sas = gas.split("+")[:-1]
            n = len(group_members_sas)
            return struct.pack(
                f"!hh{'80s' * n}64s",
                7,
                n,
                *encode_multiple_sas(group_members_sas),
                gas_token.encode("ascii"),
            )
        case _:
            raise UnknownCommand(command)


def decode_response(command: str, response, args: list[str]):
    """Decode a response based on the given command and response data."""

    match command:
        case "itr":
            return make_sas(response)
        case "itv":
            *_, valid = struct.unpack("!h12si64sb", response)
            return valid
        case "gtr":
            n = int(args[0])
            return make_gas(n, response)
        case "gtv":
            n = len(args[0].split("+")[:-1])
            *_, valid = struct.unpack(f"!hh{'80s' * n}64sb", response)
            return valid
        case _:
            raise UnknownCommand(command)


def has_error(response):
    """Check if a response contains an error code."""

    try:
        _, error_code = struct.unpack("!hh", response)
        return True, error_code
    except struct.error:
        return False, None
