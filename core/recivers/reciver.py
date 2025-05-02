import base64
import socket
import time
import hashlib
from core import sharedSocket
import threading


ids_recived = set()
alives = dict()
ack = set()
nack = set()
nack_lock = threading.Lock()
alive_lock = threading.Lock()
ack_lock = threading.Lock()
actual_file_name = ''
chunk_package = {}
last_seq = 0


def recive():
    while True:
        try:
            data, address = sharedSocket.receive( 30000 )
            # print(f"{data}")
        except socket.timeout:
            continue
        sender_ip, sender_port = address
        data_text = data.decode()
        data_splited = data_text.split( ' ', 2 )

        if len(data_splited) >= 2:
            if data_splited[0] == "ACK":
                # print(f"ack received: {data_splited[1]}")
                with ack_lock:
                    ack.add( data_splited[1] )
            elif data_splited[0] == "NACK":
                with nack_lock:
                    nack.add( data_splited[1] )
            elif data_splited[0] == "TALK":
                _talk( data_splited, sender_ip, sender_port )
            elif data_splited[0] == "FILE":
                _file( data_splited, sender_ip, sender_port )
            elif data_splited[0] == "CHUNK":
                _chunk( data, data_splited, sender_ip, sender_port )
            elif data_splited[0] == "END":
                _end( data_splited, sender_ip, sender_port )

def _end( data_splited:list[str], sender_ip: str, sender_port: int ) -> None:
    if ( data_splited[1], ( sender_ip + str( sender_port ) ) ) not in ids_recived:
        global actual_file_name, chunk_package, last_seq
        actual_file_name = ''
        chunk_package = {}
        last_seq = 0
        ids_recived.add( ( data_splited[1], ( sender_ip + str( sender_port ) ) ) )
        sha256 = hashlib.sha256()
        header, message_id, hash = data_splited
        with open( 'd', 'rb' ) as f:
            while True:
                chunk_data = f.read( 4096 )
                if not chunk_data:
                    break
                sha256.update( chunk_data )

        if hash == sha256.hexdigest():
            _ack_send( data_splited, sender_ip, sender_port )
        else:
            _nack_send( data_splited, f"error, corrupted file" , sender_ip, sender_port )


def _chunk( raw_data:bytes, data_splited:list[str], sender_ip:str, sender_port:int ) -> None:
    if ( data_splited[1], ( sender_ip + str( sender_port ) ) ) not in ids_recived:
        ids_recived.add( ( data_splited[1], ( sender_ip + str( sender_port ) ) ) )
        global last_seq
        _ack_send( data_splited, sender_ip, sender_port )
        header, message_id, seq, file_data = raw_data.split( b' ', 3 )
        seq = int( seq )

        file_data = base64.b64decode( file_data + b'=' * ( -len( file_data ) % 4 ) )
        chunk_package[seq] = file_data
        with open( "d", 'ab' ) as f:
            while True:
                expected = last_seq + 1
                if expected in chunk_package:
                    f.write( chunk_package.pop( expected ) )
                    last_seq += 1
                else:
                    break

def _talk( data_splited:list[str], sender_ip:str, sender_port:int ):
    if ( data_splited[1], ( sender_ip + str( sender_port ) ) ) not in ids_recived:
        ids_recived.add( ( data_splited[1], ( sender_ip + str( sender_port ) ) ) )
        print( f"\nrecebi TALK: {data_splited[2]}")
        _ack_send( data_splited, sender_ip, sender_port )

def _file( data_splited:list[str], sender_ip:str, sender_port:int ):
    if ( data_splited[1], ( sender_ip + str( sender_port ) ) ) not in ids_recived:
        ids_recived.add( ( data_splited[1], ( sender_ip + str( sender_port ) ) ) )
        print( f"\nrecebi FILE: {data_splited[2]}")
        _ack_send( data_splited, sender_ip, sender_port )

def _ack_send( data_splited:list[str], sender_ip:str, sender_port:int ):
    ack_message = f"ACK {data_splited[1]}"
    sharedSocket.send( ack_message.encode(), (sender_ip, int( sender_port ) ) )

def _nack_send(data_splited: list[str], message:str, sender_ip: str, sender_port: int):
    nack_message = f"NACK {data_splited[1]} {message}"
    sharedSocket.send(nack_message.encode(), (sender_ip, int(sender_port)))

def heartbeat_listener():
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEPORT, 1 )
    sock.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )
    sock.bind( ( '', 1234 ) )

    while True:
        data, (ip, port) = sock.recvfrom( 1024 )
        text = data.decode()
        with alive_lock:
            if text.startswith( "HEARTBEAT " ):
                name = text.split(" ", 1)[1]
                alives[name] = ( ip, port, time.time() )

def remove_old_heartbeat_messages() -> None:
    while True:
        current_time = time.time()
        with alive_lock:
            to_remove = [key for key, value in alives.items() if current_time - value[2] >= 10]
            for key in to_remove:
                del alives[key]
