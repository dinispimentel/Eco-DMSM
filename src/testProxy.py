from threading import Thread

import requests
import urllib3
from ecolib.threader import Threader
from urllib3.exceptions import InsecureRequestWarning

from Models.Proxy import Proxy
from Models.ProxyOrchestrator import ProxyOrchestrator
from dispatcher import Dispatcher
from proxies import PROXIES_SOCKS4
from src.config import Config

urllib3.disable_warnings(InsecureRequestWarning)

POO = ProxyOrchestrator.build_from_raw(PROXIES_SOCKS4)

thread_pool = []
INSTANCES = 30

def __dispatch():
    def the_request(P: Proxy):
        res = requests.get('https://ecogaming.ga/', proxies=P.getProxy(),
                     verify=False, timeout=Config.Proxying.TIME_OUT)
        if res:
            if res.status_code == 200:
                with open("./cache/testedgoodproxies.json", "a") as f:
                    f.write(P.getIPPORT() + "\n")
        return res

    resp = Dispatcher.dispatch_proxified(
        the_request, POO
    )

    print(f'{resp.status_code}')
    if not (resp and resp.status_code == 200):
        print("Nothing received.")

    #     page = BS(resp.text, "html.parser")
    #     inputs = page.find_all("input")
    #     clue = "/ip-lookup/?ip="
    #     for i in inputs:
    #         sidx = str(i['value']).find(clue)
    #         if sidx != -1:
    #             print("IP: " + str(i['value'])[sidx+1:-1])
    #             break




T = Threader(lambda: thread_pool, INSTANCES)

for i in range(0, 600):
    thread_pool.append(Thread(target=__dispatch))



T.dispatch(lambda s, e: print(f"Dispatched: {s}->{e} <{len(thread_pool)}>"))

for proxy in POO.proxies:
    print(proxy.getProxy())





