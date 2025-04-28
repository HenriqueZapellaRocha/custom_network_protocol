import socket
import time
from itertools import count

alives = dict()

heart_beat_sock_send = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
heart_beat_sock_send.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )

heart_beat_sock_recive = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
heart_beat_sock_recive.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )

broadcast_addr = ( '255.255.255.255', 12345 )

def registry( name:str ) -> None:
    count = 0
    while True:
        heart_beat_sock_send.sendto( str( f"HEARTBEAT {name}" ).encode(), broadcast_addr )
        time.sleep( 5 )
        count += 1
        if count > 2:
            break

def receive_heartbeat_messages() -> None:
    heart_beat_sock_recive.bind( ('', 12345 ) )
    while True:
        data, address = heart_beat_sock_recive.recvfrom( 1024 )
        sender_ip, sender_port = address
        data_decoded = data.decode()
        data_decoded = data_decoded.split(" ")
        if len( data_decoded ) >= 2 and data_decoded[1] is not None:
            alives[ data_decoded[ 1 ] ] = ( sender_ip, sender_port, time.time() )
        time.sleep( 1 )

def remove_old_heartbeat_messages() -> None:
    while True:
        current_time = time.time()
        to_remove = [key for key, value in alives.items() if current_time - value[2] >= 10]
        for key in to_remove:
            del alives[key]

