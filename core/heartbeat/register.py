import socket
import time

alives = dict()

heart_beat_sock_send = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
heart_beat_sock_send.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )
broadcast_addr = ( '255.255.255.255', 12345 )

def registry( name:str ) -> None:
    count = 0
    while True:
        heart_beat_sock_send.sendto( str( f"HEARTBEAT {name}" ).encode(), broadcast_addr )
        time.sleep( 5 )
        count += 1
        if count > 2:
            break

