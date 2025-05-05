import time
from io import BufferedReader
from core import sharedSocket
from core.recivers import reciver
import base64
import hashlib
import sys

class IDGenerator:
    def __init__(self):
        self.counter = 0

    def next_id(self):
        self.counter += 1
        return self.counter


ID_GEN = IDGenerator()
broadcast_addr = ( '255.255.255.255', 1234 )
_window_size = 100
_chunk_size = 1460
waiting_acks = {}

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
            bytes_sent += len( base64.b64decode( chunk_data ) )
            
            percent = (bytes_sent / file_size) * 100
            sys.stdout.write("\033[2K\r")  
            sys.stdout.write(f"Enviado: {percent:.2f}%")
            sys.stdout.flush()

        error = _window_slide_ack_wait( receiver_ip, receiver_port )
        if not error:
            break
    _end( data, receiver_ip, receiver_port )

def _send_chunk( message_id:int, seq:int, data:bytes, receiver_ip:str, receiver_port:int ) -> None:
    sharedSocket.send( f"CHUNK {message_id} {seq} ".encode() + data, ( receiver_ip, receiver_port ) )
    waiting_acks[message_id] = (seq, data)
    return

def _window_slide_ack_wait( receiver_ip: str, receiver_port: int ) -> bool:
    max_retries = 3
    retry_interval = 1.0
    global waiting_acks

    while waiting_acks:
        time.sleep(0.1)
        for message_id, ( seq, data ) in list(waiting_acks.items()):
            with reciver.ack_lock:
                if str( message_id ) in reciver.ack:
                    waiting_acks.pop( message_id )
                    continue
                
            for attempt in range(1, max_retries + 1):
                _send_chunk( message_id, seq, data, receiver_ip, receiver_port )

                start = time.time()
                while time.time() - start < retry_interval:
                    with reciver.ack_lock:
                        if str( message_id ) in reciver.ack:
                            waiting_acks.pop( message_id )
                            break
                    time.sleep(0.05)
                else:
                    continue
                break
            else:
                print( f"[ERRO] cancelando envio do bloco {message_id}: excedeu {max_retries} tentativas" )
                waiting_acks = {}
                return False
    return True


def _end( f:BufferedReader, receiver_ip: str, receiver_port: int ):
    file_hash = _calculate_sha256( f )
    message_id = ID_GEN.next_id()
    for attempt in range( 1, 4 ):
        sharedSocket.send( f"END {message_id} {file_hash}".encode(), ( receiver_ip, receiver_port ) )
        time.sleep( 1 )
        if str( message_id ) in reciver.ack:
            print( f"\nack recebido END_ID:{message_id}, arquivo enviado está integro" )
            reciver.ack.remove( str( message_id ) )
            return message_id
        elif str( message_id ) in reciver.nack:
            print( f"\nnack recebido END_ID:{message_id},arquivo enviado não está integro" )
            reciver.nack.remove( str( message_id ) )
            return message_id
        else:
            print( f"\nack attempt END_ID:{message_id}" )

    print( f"\ndesistindo do envio de end {message_id}, timeout attempt" )
    return -1

def _calculate_sha256( f:BufferedReader ) -> str:
    sha256 = hashlib.sha256()
    f.seek( 0 )
    while True:
        chunk_data = f.read( _chunk_size )
        if not chunk_data:
            break
        sha256.update( chunk_data )

    return sha256.hexdigest()

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


def registry( name: str, broadcast_addr=( '255.255.255.255', 1234 ) ) -> None:
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
