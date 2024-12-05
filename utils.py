from pymongo import MongoClient
from pandas import read_csv
import random
import string
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
    def random_string(length=7):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f'http://tl-44c3254e3ec618f65249d960a3465f21580658b3c61a98a42c0e10b3796256bf-country-US-session-{random_string()}:yjp9qrbcms1q@zproxy.luminati.io:31111'
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