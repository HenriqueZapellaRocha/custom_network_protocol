from core.senders import senders
from core.recivers.reciver import recive, remove_old_heartbeat_messages
from core.recivers import reciver
import threading

def start():
    threading.Thread(target=senders.registry, args=("heartbeat",), daemon=True).start()
    threading.Thread(target=remove_old_heartbeat_messages, daemon=True).start()
    threading.Thread(target=recive, daemon=True).start()
    threading.Thread(target=reciver.heartbeat_listener, daemon=True).start()

#sendfile <nome> <nome-arquivo>
def talk( name:str, message:str ) -> None:
    alives = get_registers()
    if name not in alives:
        print( "this name is not registered" )
        return

    return senders.talk( message, alives.get(name)[0], alives.get(name)[1] )

def get_registers() -> dict[str, list]:
    return reciver.alives


