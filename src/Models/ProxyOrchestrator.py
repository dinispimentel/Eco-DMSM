from __future__ import annotations

import time
from typing import List, Tuple, Callable

from src.config import Config
from .Proxy import Proxy


class ProxyOrchestrator:

    def __init__(self, proxies: List[Proxy]):

        self.proxies = proxies

    def getReadyProxy(self, retries=0):

        for proxy in self.proxies:

            if not proxy.checkLocked():
                proxy.lock(lockduration=Config.Proxying.REUSABILITY_TIMEOUT)
                return proxy

        if retries < 10:
            time.sleep(Config.Proxying.WAIT_FOR_PROXIES_TO_BE_REUSABLE_TIMER)
            return self.getReadyProxy(retries=retries + 1)
        else:
            raise RuntimeError("ProxyOrchestrator: proxies não ficaram prontas a tempo")

    @staticmethod
    def build_from_raw(arr: list[str], method='socks5') -> ProxyOrchestrator:
        pList = []

        for sp in arr:
            host, port = sp.split(':')
            pList.append(Proxy(host, port, method=method))

        return ProxyOrchestrator(pList)

    def removeBrokenProxy(self, p: Proxy):

        for pidx in range(0, len(self.proxies)):

            if p.__dict__ == self.proxies[pidx].__dict__:
                # print(f"Removing proxy {self.proxies[pidx].__dict__}")
                self.proxies.pop(pidx)

                return
        self.saveToCache()

    def saveToCache(self):

        with open(Config.Proxying.Files.PROXY_ORCHESTRATOR_CACHE, "w") as f:
            d_ps = []
            for p in self.proxies:
                d_ps.append(p.toDICT())
            d = {**self.__dict__}
            d.update({'proxies': d_ps})
            f.write(str(d))

    def getHealths(self) -> Tuple[List[Tuple[str, Tuple[float, float, float, float], int]]]:
        healths: List[Tuple[str, Tuple[float, float, float, float], int]] = []
        for p in self.proxies:
            healths.append((p.getIPPORT(), p.getHealth(), int(time.time())))
        return healths,

    def implementUpdateTracking(self, updateHealth: Callable[
        [
            Tuple[List[Tuple[str, Tuple[float, float, float, float], int]]]
        ]

        , None]):
        """Implemente o callback para o WebServer em caso de update de status health"""

        def onProxyHealthUpdate():
            updateHealth(self.getHealths())

        self._setOnProxyUpdate(onProxyHealthUpdate)

    def _setOnProxyUpdate(self, func):  # Para adicionar
        for p in self.proxies:
            p.setOnUpdate(func)
        # self.onUpdate = func
