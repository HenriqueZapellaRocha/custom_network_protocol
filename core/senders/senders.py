import time
from io import BufferedReader
from core import sharedSocket
from core.recivers import reciver
import base64

class IDGenerator:
    def __init__(self):
        self.counter = 0

    def next_id(self):
        self.counter += 1
        return self.counter


ID_GEN = IDGenerator()
broadcast_addr = ( '255.255.255.255', 1234 )
_window_size = 6
_chunk_size = 20000
waiting_acks = {}

#CHUNK <id> <seq> <dados>
def file_chunk( data:BufferedReader, receiver_ip:str, receiver_port:int, file_size:int ) -> None:
    seq = 0
    bytes_sent = 0
    while bytes_sent < file_size:
        for window in range( _window_size ):
            chunk_data = data.read( _chunk_size )
            if not chunk_data:
                break
            chunk_data = base64.b64encode( chunk_data )
            message_id = ID_GEN.next_id()
            seq += 1
            time.sleep( 0.01 )
            _send_chunk( message_id, seq, chunk_data, receiver_ip, receiver_port )
            bytes_sent += len(base64.b64decode(chunk_data))

        _window_slide_ack_wait( receiver_ip, receiver_port )

def _send_chunk( message_id:int, seq:int, data:bytes, receiver_ip:str, receiver_port:int ) -> None:
    sharedSocket.send( f"CHUNK {message_id} {seq} ".encode() + data, ( receiver_ip, receiver_port ) )
    waiting_acks[message_id] = (seq, data)
    return

def _window_slide_ack_wait( receiver_ip:str, receiver_port:int ):
    while waiting_acks:
        time.sleep(0.1)
        for message_id, (seq, data) in list( waiting_acks.items() ):
            with reciver.ack_lock:
                if str( message_id ) in reciver.ack:
                    waiting_acks.pop( message_id )
                else:
                    for i in range( 3 ):
                        print(reciver.ack)
                        _send_chunk( message_id, seq, data, receiver_ip, receiver_port )
                        time.sleep(0.1)
                        if str( message_id ) in reciver.ack:
                            waiting_acks.pop(message_id)
                    print( f"cancelando envio do arquivo, muitos attempts em um bloco de arquivo" )
                    return





#sendfile <nome> <nome-arquivo>
def send_file( file_name:str, file_size:float, receiver_ip: str, receiver_port: int ) -> int:
    message_id = ID_GEN.next_id()

    for attempt in range( 1, 4 ):
        sharedSocket.send(f"FILE {message_id} {file_name} {file_size}".encode(), (receiver_ip, receiver_port))
        time.sleep( 0.1 )
        if str( message_id ) in reciver.ack:
            print( f"ack recebido FILE_ID:{message_id}" )
            reciver.ack.remove( str( message_id ) )
            return message_id
        else:
            print( f"ack attempt FILE_ID:{message_id}" )

    print( f"desistindo do envio FILE {message_id}, timeout attempt" )
    return -1


def registry( name: str, broadcast_addr=( '255.255.255.255', 1234 ) ):
    while True:
        sharedSocket.send( f"HEARTBEAT {name}".encode() , broadcast_addr )
        time.sleep( 5 )

def talk( data: str, receiver_ip: str, receiver_port: int ) -> bool:
    message_id = ID_GEN.next_id()
    message = f"TALK {message_id} {data}".encode()

    for attempt in range( 1, 4 ):
        sharedSocket.send( message, ( receiver_ip, receiver_port ) )
        time.sleep( 0.1 )
        if str( message_id ) in reciver.ack:
            print( f"ack recebido TALK_ID:{message_id}" )
            reciver.ack.remove( str( message_id ) )
            return True
        else:
            print( f"ack attempt TALK_ID:{message_id}" )

    print( f"desistindo do envio TALK {message_id}, timeout attempt" )
    return False
