import socket
import time

class IDGenerator:
    def __init__(self):
        self.counter = 0

    def next_id(self):
        self.counter += 1
        return self.counter


sock_send = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock_send.settimeout( 1.0 )
ID_GEN = IDGenerator()
sock_send.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )

broadcast_addr = ( '255.255.255.255', 12345 )

def registry( name:str ) -> None:
    count = 0
    while True:
        sock_send.sendto( str( f"HEARTBEAT {name}" ).encode(), broadcast_addr )
        time.sleep( 5 )
        count += 1
        if count > 2:
            break

def talk( data:str, receiver_ip: str, receiver_port:int ) -> bool:

    message_id = ID_GEN.next_id()
    message = "TALK " + str( message_id ) + " " + data

    max_retries = 3
    for attempt in range( 1, max_retries + 1 ):
        sock_send.sendto( message.encode(), ( receiver_ip, receiver_port ))
        print(f"[Attempt {attempt}] Enviado: {message}")

        try:
            data_received, _ = sock_send.recvfrom(1024)
            text = data_received.decode()
            expected_ack = f"ACK {message_id}"
            if text == expected_ack:
                print( f"→ Recebido {text}, OK." )
                return True
            else:
                print(f"→ Recebido mensagem inesperada: {text}")
        except socket.timeout:
            print(f"→ Timeout aguardando ACK (tentativa {attempt}).")

    print("→ Número máximo de tentativas excedido. Desistindo.")
    return False
