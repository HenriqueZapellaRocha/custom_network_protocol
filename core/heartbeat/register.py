import socket
import time

alives = dict()

heart_beat_sock_send = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
heart_beat_sock_send.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )

heart_beat_sock_recive = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
heart_beat_sock_recive.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )

broadcast_addr = ( '255.255.255.255', 12345 )

def registry( name:str ) -> None:
    while True:
        heart_beat_sock_send.sendto( str( f"HEARTBEAT {name}" ).encode(), broadcast_addr )
        time.sleep( 5 )

def receive_heartbeat_messages() -> None:
    heart_beat_sock_recive.bind( ('', 12345 ) )
    while True:
        data, address = heart_beat_sock_recive.recvfrom( 1024 )
        sender_ip, sender_port = address
        print(f"{data} {sender_ip}:{sender_port}")
        data_decoded = data.decode()
        data_decoded = data_decoded.split(" ")
        if len( data_decoded ) >= 2 and data_decoded[1] is not None:
            alives[ data_decoded[ 1 ] ] = ( sender_ip, sender_port )

        time.sleep( 1 )


