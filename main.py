import http
import random
from functools import partial
from http.server import HTTPServer
from threading import Thread

import redis

from src.DPHTTPRequestHandler import DPHTTPRequestHandler
from src.config import Config
from src.proxies import PROXIES_SOCKS5
import socketserver

webServer = None
webServer_Thread = None


def _checkRedisOn():

    try:
        r = redis.Redis(host=Config.Redis.HOST, port=Config.Redis.PORT)
        r.ping()
        r.close()
        print("Redis On!")
    except (ConnectionError, redis.exceptions.ConnectionError):
        raise RuntimeError("Redis is not responding.")


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True




if __name__ == '__main__':

    # TODO:
    # TODO: ADICIONAR VERIFICAÇÃO DE INTEGRIDADE DO REDIS
    # TODO: VERIFICAR STATUS DO SITE
    # TODO: INTEGRAR O QUE ESTÁ NO testSTEAMMARKET.py NUM ENDPOINT


    _checkRedisOn()
    PROXIES = PROXIES_SOCKS5
    random.shuffle(PROXIES)
    from src.Models.DMData import DMData
    from src.Models.DMOfferBook import OfferBook
    from src.Models.ProxyOrchestrator import ProxyOrchestrator
    DMData = DMData(offerbook=OfferBook.loadFromCache(testing=False))
    PO = ProxyOrchestrator.build_from_raw(PROXIES, method='socks5')

    handler = partial(DPHTTPRequestHandler, DMData, PO)
    webServer = ThreadedHTTPServer(("192.168.0.120", 8082), handler)

    try:
        webServer_Thread = Thread(target=webServer.serve_forever)
        webServer_Thread.start()
        print("Started")
        webServer_Thread.join()

    except KeyboardInterrupt:
        webServer.server_close()
        print("Closed")




