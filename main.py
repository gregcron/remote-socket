import threading
import time

from websocket import WebSocket
from utils import load_events

def handler(eid):
    ws = WebSocket(eid)
    ws.start()

events = load_events()
for event in events:
    for x in range(2):
        threading.Thread(target=handler,args=(event['eid'],),daemon=True).start()
while True:
    time.sleep(5)