from core.senders import senders
from core.recivers.reciver import recive, remove_old_heartbeat_messages
from core.recivers import reciver
import threading
import os

def start( name:str ):
    threading.Thread( target=senders.registry, args=( name, ), daemon=True ).start()
    threading.Thread( target=remove_old_heartbeat_messages, daemon=True ).start()
    threading.Thread( target=recive, daemon=True ).start()
    threading.Thread( target=reciver.heartbeat_listener, daemon=True ).start()

#sendfile <nome> <nome-arquivo>
def send_file( name:str, file_name:str ) -> bool:
    alives = get_registers()
    if name not in alives:
        return False
    file_size = os.path.getsize( file_name )
    with open( file_name, 'rb' ) as f:
        senders.send_file( file_name, file_size, alives.get(name)[0], alives.get(name)[1] )
        senders.file_chunk( f, alives.get(name)[0], alives.get(name)[1], file_size )


def talk( name:str, message:str ) -> bool:
    alives = get_registers()
    if name not in alives:
        print( "this name is not registered" )

    return senders.talk( message, alives.get(name)[0], alives.get(name)[1] )

def get_registers() -> dict[str, list]:
    with reciver.alive_lock:
        return reciver.alives


