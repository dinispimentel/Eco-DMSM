import asyncio
from abc import abstractmethod
from asyncio import Event
from multiprocessing.connection import Connection
from threading import Thread
from typing import Callable, Tuple, List, Type

from websockets.server import WebSocketServerProtocol

from src.StateHolder.BaseStateHolder import BaseStateHolder


class BaseWSModule:

    def __init__(self, get_instance_ws: Callable[[int], WebSocketServerProtocol],
                 state_holder: Type[BaseStateHolder], child_pipe: Connection,
                 *args, **kwargs):

        self.get_instance_ws = get_instance_ws
        # self.trigger = trigger
        self.trigger = asyncio.Event()
        self.pipe = child_pipe
        self.state_holder = state_holder(self.trigger, self.pipe.recv, *args, **kwargs)
        self.awaiting = False
        self.awaiting_sh = False
        self.awaiting_stop = False
        self.shu_thread = None
        self.stop_all_bound_instances = False

    async def sendPastStatesToInstance(self, instance_id: int, states: List[Tuple]):
        for state in states:
            await self.sendPastStateToInstance(instance_id, state)

    @abstractmethod
    async def sendPastStateToInstance(self, instance_id: int, states: Tuple):
        pass

    async def sendPastStates(self):
        """Sends data from the State Holder to those in need"""
        is_intbs = self.state_holder.get_instance_and_states_in_need_to_be_served()
        # instance|states in need to be sent

        for is_in in is_intbs:
            await self.sendPastStatesToInstance(is_in[0], is_in[1])

    async def startAwaintingUpdates(self):
        if not self.awaiting:
            self.awaiting = True
            while self.awaiting:
                await self._onUpdate()

        else:
            return

    async def startAwaitingStateHolderUpdates(self):
        if not self.awaiting_sh:
            self.awaiting_sh = True

            while self.awaiting_sh:
                self.shu_thread = Thread(target=self.state_holder.update, daemon=True)
                self.shu_thread.start()
                while self.shu_thread.is_alive():
                    await asyncio.sleep(0)

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

    def clean(self):

        self.awaiting = False
        self.awaiting_sh = False
        self.awaiting_stop = False
        self.shu_thread = None
        self.stop_all_bound_instances = False
        self.state_holder.clean()
        self.trigger.clear()

    def stop(self):
        self.stop_all_bound_instances = True
        self.awaiting_sh = False
        self.awaiting = False