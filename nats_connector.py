from pynats import NATSClient
import json

class NatsManager:
    def setup(self):
        self.client = NATSClient(url="nats://54.185.180.254:4222", socket_keepalive=True)
        self.client.connect()

    def send(self, data):
        data = json.dumps(data)
        data = data.encode()
        self.client.publish(subject="socket_seat_data", payload=data)


nm = NatsManager()
nm.setup()

# nats_payload = {'nats_channel': 'socket_seat_data', 'eid': '100060CEE03C554D', 'data': [6612, 6614], 'timestamp': 1727289673.4988997, 'hash': -6732732839096453807}
##nats_payload = {'nats_channel': 'socket_seat_data', 'eid': '100060CEE03C554D', 'data': [1,2], 'timestamp': 1727289673.4988997, 'hash': -123096453807}

##nm.send(nats_payload)
