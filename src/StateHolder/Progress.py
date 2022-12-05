from asyncio import Event

from src.StateHolder.BaseStateHolder import BaseStateHolder
from src.WebSocketInstantiator import Packets


class Progress(BaseStateHolder):

    def update(self):
        packet = self.recv()

        packet_code = packet["code"]
        if packet_code == Packets.CODES.EXIT:
            return

        packet_data = packet["data"]
        if packet_code == Packets.CODES.APPEND:
            progress, progress_details, timestamp = packet_data
            self.all_states.append((progress, progress_details, timestamp))

        elif packet_code == Packets.CODES.OVERWRITE:
            progress, progress_details, timestamp = packet_data
            self.all_states = [(progress, progress_details, timestamp)]

        self.trigger.set()
