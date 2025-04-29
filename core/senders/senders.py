import time
from core import sharedSocket
from core.recivers import reciver

class IDGenerator:
    def __init__(self):
        self.counter = 0

    def next_id(self):
        self.counter += 1
        return self.counter


ID_GEN = IDGenerator()

broadcast_addr = ( '255.255.255.255', 1234 )

def registry(name: str, broadcast_addr=('255.255.255.255', 1234)):
    while True:
        sharedSocket.send(f"HEARTBEAT {name}".encode(), broadcast_addr)
        time.sleep(5)

def talk(data: str, receiver_ip: str, receiver_port: int) -> bool:
    message_id = ID_GEN.next_id()
    message = f"TALK {message_id} {data}".encode()

    for attempt in range(1, 4):
        sharedSocket.send(message, (receiver_ip, receiver_port))

        if str(message_id) in reciver.ack:
            print( f"ack recebido TALK_ID:{message_id}" )
            reciver.ack.remove( str( message_id ) )
            return True
        else:
            time.sleep(1)
            print( f"ack attempt TALK_ID:{message_id}" )

    print( f"desistindo do envio TALK {message_id}, timeout attempt" )
    return False
