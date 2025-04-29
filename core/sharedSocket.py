import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
sock.settimeout(1.0)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('', 12345))

def send(data: bytes, addr: tuple[str,int]) -> None:
    sock.sendto(data, addr)

def receive(bufsize: int = 1024) -> tuple[bytes, tuple[str,int]]:
    return sock.recvfrom(bufsize)
