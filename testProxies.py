import random
import time
from threading import Thread

from src.Models.ProxyOrchestrator import ProxyOrchestrator
from src.dispatcher import Dispatcher
from src.proxies import PROXIES_SOCKS5
PROXIES = PROXIES_SOCKS5
random.shuffle(PROXIES)

po = ProxyOrchestrator.build_from_raw(PROXIES)

from ecolib.threader import Threader

thread_pool = []

def __dispatch():
    Dispatcher.testHTTPPost(po)

p1 = time.time()

for i in range(0, 49):
    thread_pool.append(Thread(target=__dispatch))

T = Threader(lambda: thread_pool, 12, delay_config= {"delay": 0, "instances_before_delay": 50000})

T.dispatch()

p2 = time.time()

print(p2-p1)
