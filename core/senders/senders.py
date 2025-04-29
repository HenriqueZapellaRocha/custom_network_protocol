import socket
import time
from core import sharedSocket

class IDGenerator:
    def __init__(self):
        self.counter = 0

    def next_id(self):
        self.counter += 1
        return self.counter


sock_ack = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock_ack.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEPORT, 1 )
sock_ack.settimeout( 1.0 )
ID_GEN = IDGenerator()
sock_ack.bind( ( '', 1234 ) )

broadcast_addr = ( '255.255.255.255', 12345 )

def registry(name: str, broadcast_addr=('255.255.255.255', 1234)):
    while True:
        sharedSocket.send(f"HEARTBEAT {name}".encode(), broadcast_addr)
        time.sleep(5)

def talk(data: str, receiver_ip: str, receiver_port: int) -> bool:
    message_id = ID_GEN.next_id()
    message = f"TALK {message_id} {data}".encode()

    for attempt in range(1, 4):
        sharedSocket.send(message, (receiver_ip, receiver_port))
        print(f"[Attempt {attempt}] Enviado: {message.decode()}")

        try:
            data_received, _ = sock_ack.recvfrom(1024)
            text = data_received.decode()
            if text == f"ACK {message_id}":
                print(f"→ Recebido {text}, OK.")
                return True
            else:
                print(f"→ Recebido inesperado: {text}")
        except socket.timeout:
            print(f"→ Timeout aguardando ACK (tentativa {attempt}).")

    print("→ Máximo de tentativas excedido.")
    return False
