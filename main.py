from core import senders
import threading
from core.heartbeat import register
import time

heart_beat_send = threading.Thread(target=register.registry, args=( "heartbeat", ), daemon=True)
heart_beat_send.start()

heart_beat_recive = threading.Thread(target=register.receive_heartbeat_messages, daemon=True )
heart_beat_recive.start()


while True:
    time.sleep(1)