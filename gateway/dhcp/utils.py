import socket
import struct


def ip2int(addr: str) -> int:
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr: int) -> str:
    return socket.inet_ntoa(struct.pack("!I", addr))