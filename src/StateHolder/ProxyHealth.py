from asyncio import Event
from typing import Tuple, List

from src.StateHolder.BaseStateHolder import BaseStateHolder
from src.WebSocketInstantiator import Packets


class ProxyHealth (BaseStateHolder):
    pass

    # def __init__ (self, module_trigger: Event):
    #
    #     super().__init__()

    def update(self, proxies_health: Tuple[List[Tuple[str, Tuple[float, float, float, float], int]]]):
        self.all_states = [proxies_health]
        packet = self.recv()

        packet_code = packet["code"]
        if packet_code == Packets.CODES.EXIT:
            return

        packet_data = packet["data"]
        if packet_code == Packets.CODES.APPEND:
            raise RuntimeError(f'Can\'t append on: {type(self)}')

        elif packet_code == Packets.CODES.OVERWRITE:
            progress, progress_details, timestamp = packet_data
            self.all_states = [(progress, progress_details, timestamp)]

        self.trigger.set()
    # sobre-escreve o estado anterior, pois novas conexões não precisam do histórico

