from core.heartbeat import register
from core.recivers import reciver
import threading


def start() -> None:
    heart_beat_send = threading.Thread(target=register.registry, args=("heartbeat",), daemon=True)
    heart_beat_send.start()

    heart_beat_recive = threading.Thread(target=register.receive_heartbeat_messages, daemon=True)
    heart_beat_recive.start()

    heart_beat_old = threading.Thread(target=register.remove_old_heartbeat_messages, daemon=True)
    heart_beat_old.start()

    channel = threading.Thread(target=reciver.recive, daemon=True)

def get_registers() -> dict[str, list]:
    return register.alives
