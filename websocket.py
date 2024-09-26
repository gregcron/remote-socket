from pyroaring import BitMap
import traceback
import threading
import asyncio
import aiohttp
import random
import base64
import json

from utils import resi_proxies
from logger import Logger
from utils import process_new_seats

log = Logger()

def locate_roaring_header(data):
    for i in range(len(data)):
        if data[i] in (0x3b, 0x3a) and data[i+1] == 0x30:
            return i

def decode_roaring(data):
    ws_buffer = base64.b64decode(data)
    header_position = locate_roaring_header(ws_buffer)
    if not header_position:
        return None
    bmp = BitMap.deserialize(ws_buffer[header_position:])
    i = bmp.to_array()
    output = []
    for x in i:
        output.append(x)
    return output

class WebSocket():
    def __init__(self, eid, x):
        self.eid = eid
        self.prev_seats = []
        self.x = x

    async def connect_socket(self):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        url = "wss://marketplace.prod.pub-tmaws.io/avpp/v2/graphql?app=PRD2663_EDPAPP&sessionId=3%3AMcVO0lhBDLpXGH7e%2ByJnhA%3D%3D%3A6re2IvK%2BZ6zVTCPMozVowLfsK6TdQ3gi%2FLxWqIircP5Nt2WzBqPU6pFhNAqUFbUy5iYzXYSN0MVKAiSrI5SNI4pB0FUfMq502Sur84GJgp7TWxGtzV5bmeMJz1JEpr42ulTnfah03VPLgzdnKxwYB%2Bk4eQBztZM%2BJA7kONg%2FNXicKfuzPOChYGrylaP1yEmggopRE19OoIAQk1MEKCcJRRRD3fLrVm6%2FF2AVw5iDuQFHN%2B7L2guJo957vxTc4trLZEHWZZFO4In8uk3KbWoqDFQ4XTmrSs2I3pevOYYO8tzQCc0gBjVreLD4MDMHxPYUZpcKki7xVYZNOYktBSyxgO9WiHzVGkOzsqD1aZ8octSjdDJALC9%2FuceKHq9k4E1kCSvD7Wp6S1rRliynluMTTqpNyNEhDkxyNBwrQJpu%2FXyaol9boZo%2F4NGbsB7CJ3rQlyg%2F99dT0%2F9T8CE0Z1ZiEozfFmIK9l8k9vQ7UtI26Q0%3D%3Ac8ZEB3sV%2FOQYJmiqv3vdqIN8eeQ5PyyPlp%2FXa2Nms1k%3D"
        # log.warning(f"Connecting to {self.eid} Socket...")
        self.first_run = True
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(
                            url,
                            headers={"User-Agent": user_agent},
                            proxy = resi_proxies(),
                            # proxy=random_proxy(), #return f"http://{splitted[2]}:{splitted[3]}@{splitted[0]}:{splitted[1]}"
                    ) as ws:
                        self.websocket = ws
                        await self.subscribe()
                        async for m in ws:
                            # print('fot m')
                            data = json.loads(m.data)
                            if data.get("type") == "data":
                                # print('got m')
                                try:
                                    restocking_seats = decode_roaring(data["payload"]["data"]["availability"]["buffer"])
                                    if restocking_seats:
                                        new_seats = [d for d in restocking_seats if d not in self.prev_seats]
                                        self.prev_seats = restocking_seats
                                    else: new_seats = None

                                    if self.x == 1:
                                        await ws.close()
                                    
                                except Exception as e:
                                    continue

                                if new_seats and not self.first_run:
                                    ## SEND VIA NATS
                                    process_new_seats(self.eid, new_seats)
                                if new_seats and self.first_run:
                                    print(f'Skipping push for first run')
                                    self.first_run = False
                                self.first_run = False

            except asyncio.CancelledError:
                # log.warning(f"WebSocket connection for {self.eid} cancelled.")
                if session:
                    await session.close()
            except aiohttp.WebSocketError as e:
                # log.warning(f"Socket error for {self.eid} - {traceback.format_exc()}")
                # log.warning(f"Socket error for {self.eid} - {e}")
                await asyncio.sleep(3)
                continue
            except Exception as e:
                # log.warning(f"Socket error for {self.eid} - {traceback.format_exc()}")
                # log.warning(f"Socket error for {self.eid} - {e}")
                await asyncio.sleep(3)
                continue

    async def subscribe(self):
        await asyncio.sleep(random.randint(0,5))
        log.warning(f"Subscribing to {self.eid}...")
        await self.websocket.send_json({"type": "connection_init", "payload": {}})
        payload = {
            "id": "1",
            "type": "start",
            "payload": {
                "variables": {
                    "eventId": self.eid,
                    "lastReceivedVersion": None
                },
                "extensions": {},
                "operationName": "AvailabilityChanged",
                "query": "subscription AvailabilityChanged($eventId: String!, $unlockToken: String, $lastReceivedVersion: String, $displayId: String) {\n  availability(\n    eventId: $eventId\n    unlockToken: $unlockToken\n    lastReceivedVersion: $lastReceivedVersion\n    displayId: $displayId\n  ) {\n    buffer\n    __typename\n  }\n}\n"
            }
        }

        await self.websocket.send_json(payload)

    def run(self):
        """Run the asyncio event loop for the WebSocket connection."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_socket())

    def start(self):
        """Start the WebSocket client in a separate thread."""
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    async def shutdown(self):
        """Gracefully shuts down the WebSocket and loop."""
        if self.websocket is not None:
            await self.websocket.close()
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]  # Cancel all other running tasks
        await asyncio.gather(*tasks, return_exceptions=True)  # Gather to avoid pending task error
        self.loop.stop()

    def stop(self):
        """Stop the WebSocket client and close the thread."""
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.shutdown(), self.loop)  # Schedule shutdown
            self.thread.join()  # Wait for the thread to finish