from pymongo import MongoClient
from pandas import read_csv
import random
import time

from nats_connector import NatsManager
nm = NatsManager()
nm.setup()

client = MongoClient('mongodb+srv://jake:mgsBYJGDufIeZsyC@tix-dedicated.ysqyz.mongodb.net/?retryWrites=true&w=majority')
db = client['tm']

def get_db_proxies():
    proxyTable = db['proxies']
    proxies = proxyTable.find({})
    return [d['proxy'] for d in proxies]

proxies, pl = get_db_proxies(), []
for e in proxies:
    pl.append(e.split(':')[2]+':'+e.split(':')[3]+'@'+e.split(':')[0]+':'+e.split(':')[1])

def resi_proxies():
    return f'http://PP_F4MGBE5-country-US-session-{random.randint(0,99999)}:gofnxddc@event.porterproxies.com:61234'
    # return f'http://GregCronheim-res-us-sid-{random.randint(0,99999)}:RcoPEhFwFhfpATw@gw-am.ntnt.io:5959'

def isp_proxies():
    prx = random.choice(pl)
    return {
        "http": f"http://{prx}",
        "https": f"http://{prx}"
        }

def load_events():
    return read_csv('events.csv').to_dict('records')

def process_new_seats(eid, new_seats):
    print(f'processing new seats {eid}')
    nats_payload = {
        "nats_channel": "socket_seat_data",
        "eid": eid,
        "data": new_seats,
        "timestamp": time.time(),
        "hash": hash(tuple(sorted(new_seats)))
        }
    nm.send(nats_payload)