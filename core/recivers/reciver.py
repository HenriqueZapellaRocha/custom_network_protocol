import socket
import time
from core import sharedSocket
import threading


ids_recived = set()
alives = dict()
ack = set()
alive_lock = threading.Lock()



def recive():
    while True:
        try:
            data, address = sharedSocket.receive(1024)
        except socket.timeout:
            continue
        sender_ip, sender_port = address
        print(f"{data} {sender_ip}:{sender_port}")
        data_text = data.decode()
        data_splited = data_text.split( ' ', 2 )

        if len(data_splited) >= 2:
            if data_splited[0] == "ACK":
                ack.add( data_splited[1] )
            elif data_splited[0] == "TALK":
                _talk( data_splited, sender_ip, sender_port )


def _talk( data_splited:list[str], sender_ip:str, sender_port:int ):
    if ( data_splited[1], ( sender_ip + str( sender_port ) ) ) not in ids_recived:
        ack_message = f"ACK {data_splited[1]}"
        ids_recived.add( ( data_splited[1], ( sender_ip + str( sender_port ) ) ) )
        sharedSocket.send( ack_message.encode(), (sender_ip, int( sender_port ) ) )
        print(data_splited[2])

def heartbeat_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', 1234))

    while True:
        data, (ip, port) = sock.recvfrom(1024)
        text = data.decode()
        with alive_lock:
            if text.startswith("HEARTBEAT "):
                name = text.split(" ", 1)[1]
                alives[name] = (ip, port, time.time())



def remove_old_heartbeat_messages() -> None:
    while True:
        current_time = time.time()
        with alive_lock:
            to_remove = [key for key, value in alives.items() if current_time - value[2] >= 10]
            for key in to_remove:
                del alives[key]
