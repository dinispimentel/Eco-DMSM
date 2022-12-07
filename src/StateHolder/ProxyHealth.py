from asyncio import Event
from typing import Tuple, List

from src.StateHolder.BaseStateHolder import BaseStateHolder


class ProxyHealth (BaseStateHolder):

    def __init__ (self, module_trigger: Event):

        super().__init__(module_trigger)

    def update(self, proxies_health: Tuple[List[Tuple[str, Tuple[float, float, float, float], int]]]):
        self.all_states = [proxies_health]  # sobre-escreve o estado anterior, pois novas conexões não precisam do histórico
        self.trigger.set()
