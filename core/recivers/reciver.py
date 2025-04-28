import socket

sock_recive = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
ids_recived = set()


def recive():
    sock_recive.bind( ( "127.0.0.1", 12345 ) )
    while True:
        data, address = sock_recive.recvfrom( 1024 )
        sender_ip, sender_port = address
        print(f"{data} {sender_ip}:{sender_port}")
        data_text = data.decode()
        data_splited = data_text.split( ' ', 2 )

        if ( len( data_splited ) >= 2 ):
            if ( data_splited[0] == "TALK" ):
                _talk( data_splited, sender_ip, sender_port )

def _talk( data_splited:list[str], sender_ip:str, sender_port:str ):
    if ( ( data_splited[1], ( sender_ip + str( sender_port ) ) ) not in ids_recived ):
        ack_message = f"ACK {data_splited[1]}"
        ids_recived.add( ( data_splited[1], ( sender_ip + str( sender_port ) ) ) )
        sock_recive.sendto(ack_message.encode(), (sender_ip, sender_port))
        print(data_splited[2])