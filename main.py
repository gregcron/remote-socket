import threading
import time

from websocket import WebSocket
from utils import load_events

def handler(eid, x):
    ws = WebSocket(eid, x)
    ws.start()

events = load_events()
for event in events:
    qty = 2
    if event['eid'] in ['300060CED8152349']:
        qty=4
    for x in range(qty):
        threading.Thread(target=handler,args=(event['eid'],x),daemon=True).start()
while True:
    time.sleep(5)