import asyncio
from abc import abstractmethod
from asyncio import Event
from typing import Callable, Tuple, List, Type

from websockets.server import WebSocketServerProtocol

from src.StateHolder.BaseStateHolder import BaseStateHolder


class BaseWSModule:


    def __init__(self, get_instance_ws: Callable[[int], WebSocketServerProtocol], trigger: Event, state_holder: Type[BaseStateHolder],
                 *args, **kwargs):

        self.get_instance_ws = get_instance_ws
        self.trigger = trigger
        self.state_holder = state_holder(self.trigger, *args, **kwargs)
        self.awaiting = False
        self.awaiting_stop = False
        self.stop_all_bound_instances = False


    async def sendPastStatesToInstance(self, instance_id: int, states: List[Tuple]):
        for state in states:
            await self.sendPastStateToInstance(instance_id, state)

    @abstractmethod
    async def sendPastStateToInstance(self, instance_id: int, states: Tuple):
        pass

    async def sendPastStates(self):
        """Sends data from the State Holder to those in need"""
        is_intbs = self.state_holder.get_instance_and_states_in_need_to_be_served() # instance|states in need to be send

        for is_in in is_intbs:
            await self.sendPastStatesToInstance(is_in[0], is_in[1])


    async def startAwaintingUpdates(self):
        if not self.awaiting:
            self.awaiting = True
            while self.awaiting:
                await self._onUpdate()

        else:
            return

    async def startAwaintingStop(self, wsi):
        if not self.awaiting_stop:
            self.awaiting_stop = True
            while not self.stop_all_bound_instances:
                await asyncio.sleep(0)
            await self.state_holder.close_all_instances(wsi)

    async def _onUpdate(self):
        """Dispatch data sending (from the StateHolder) when internal trigger is triggered"""
        await self.trigger.wait()
        await self.sendPastStates()
        self.trigger.clear()


    def subscribeToModule(self, instance_id: int):
        self.state_holder.register_instance(instance_id)


    def stop(self):
        self.stop_all_bound_instances = True
        self.awaiting = False