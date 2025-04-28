import socket

class IDGenerator:
    def __init__(self):
        self.counter = 0

    def next_id(self):
        self.counter += 1
        return f"id_{self.counter}"


sock_send = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock_send.settimeout( 1.0 )
ID_GEN = IDGenerator()

def talk( data:str, receiver_ip: str, receiver_port:int ) -> bool:

    message_id = ID_GEN.next_id()
    message = "TALK " + message_id + " " + data

    max_retries = 3
    for attempt in range( 1, max_retries + 1 ):
        sock_send.sendto( message.encode(), ( receiver_ip, receiver_port ))
        print(f"[Attempt {attempt}] Enviado: {message}")

        try:
            data_received, _ = sock_send.recvfrom(1024)
            text = data_received.decode()
            expected_ack = f"ACK {message_id}"
            if text == expected_ack:
                print(f"→ Recebido {text}, OK.")
                return True
            else:
                print(f"→ Recebido mensagem inesperada: {text}")
        except socket.timeout:
            print(f"→ Timeout aguardando ACK (tentativa {attempt}).")

    print("→ Número máximo de tentativas excedido. Desistindo.")
    return False
