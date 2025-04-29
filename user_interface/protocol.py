from core.heartbeat import register
from core.recivers import reciver
from core.senders import senders
import threading


def start() -> None:
    heart_beat_send = threading.Thread(target=senders.registry, args=( "heartbeat",), daemon=True)
    heart_beat_send.start()

    heart_beat_old = threading.Thread( target=reciver.remove_old_heartbeat_messages, daemon=True )
    heart_beat_old.start()

    channel = threading.Thread( target=reciver.recive, daemon=True )
    channel.start()

#sendfile <nome> <nome-arquivo>
def talk( name:str, message:str ) -> None:
    alives = get_registers()
    if name not in alives:
        print( "this name is not registered" )
        return

    senders.talk( message, alives.get(name)[0], alives.get(name)[1] )

def get_registers() -> dict[str, list]:
    return reciver.alives


