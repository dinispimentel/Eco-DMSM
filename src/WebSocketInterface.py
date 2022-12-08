from __future__ import annotations

import asyncio
import json
import random
import time
from threading import Thread
from typing import Tuple, Dict, List, Type, Optional, Mapping

import websockets
from websockets.legacy.server import WebSocketServerProtocol

from src.StateHolder.BaseStateHolder import BaseStateHolder
from src.WSModules.BaseWSModule import BaseWSModule
from src.config import Config


class WSInterface:

    @staticmethod
    def create_response(success: bool, d: dict):
        msg = {"status": success, "data": d}
        return json.dumps(msg)


    def serve(self, modules_to_load: List[Tuple[Type[BaseWSModule], Type[BaseStateHolder], Optional[Tuple],
    Optional[Mapping]]], host=Config.ENV.LOCAL_IP, port=4000):
        for t in modules_to_load:
            module = t[0]
            state_holder = t[1]
            args: Tuple = ()
            kwargs: Mapping = {}
            if len(t) > 2:
                args = t[2]
            if len(t) > 3:
                kwargs = t[3]

            if args and kwargs:
                self.loadModule(module, state_holder, *args, **kwargs)
            elif args and not kwargs:
                self.loadModule(module, state_holder, *args)
            elif kwargs and not args:
                self.loadModule(module, state_holder, **kwargs)
            else:
                self.loadModule(module, state_holder)

        def _servingThreadFunc():


            asyncio.run(self._serve(modules_to_load,host=host, port=port))

        self.thread = Thread(target=_servingThreadFunc, daemon=True)
        self.thread.start()
            # asyncio.run(self._serve(modules_to_load, host=host, port=port))


        # loop.run_until_complete(coroutine)
        # self.thread = Thread(target=loop.run_until_complete, args=(coroutine,))
        # self.thread.start()


    async def _serve(self, modules_to_load: List[Tuple[Type[BaseWSModule], Type[BaseStateHolder], Optional[Tuple],
    Optional[Mapping]]],
                     host="127.0.0.1", port=4000):

        async def handler(ws, path):

            from src.WSModules.WSMProgress import WSMProgress
            from src.WSModules.WSMProxyHealth import WSMProxyHealth

            instance_id = random.randint(1, 50000)
            ws_in_instance = False


            for hashe in list(self.connects.keys()):
                if ws == self.connects[hashe]:
                    ws_in_instance = hashe

            if not ws_in_instance:
                self.connects.update({instance_id: ws})
            else:
                instance_id = ws_in_instance


            if path == "/progress":

                if not self.isLoaded(WSMProgress):
                    await ws.send(WSInterface.create_response(False, {'error': 'This path is not accesible on this'
                                                                                'operation.'}))

                else:
                    print("Someone awaiting trigger progress")
                    self.getModule(WSMProgress).subscribeToModule(instance_id)
                    await self.getModule(WSMProgress).startAwaintingUpdates()
                    await self.getModule(WSMProgress).startAwaintingStop(self)

            elif path == "/proxyhealth":
                if not self.isLoaded(WSMProxyHealth):
                    await ws.send(WSInterface.create_response(False, {'error': 'This path is not accesible on this'
                                                                               'operation.'}))
                else:
                    print("Someone awaiting proxy updates")
                    self.getModule(WSMProxyHealth).subscribeToModule(instance_id)
                    await self.getModule(WSMProxyHealth).startAwaintingUpdates()
                    await self.getModule(WSMProxyHealth).startAwaintingStop(self)

                # await ws.send(WSInterface._create_response(True, {'progress': 0.5, 'progress_details': "Staled"}))

        print("Starting serve")
        try:
            async with websockets.serve(handler, host, port):
                while not self.kill_event.is_set():
                    await asyncio.sleep(1)
                self.unbinded = True
            # await self.kill_event.wait()
        except TypeError as te:
            print("TE", te)
        except (BaseException, Exception) as ex:
            print("EX", ex)
        finally:
            self.unbinded = True
            print("Ending serve")

    def __init__(self, connects=None):
        self.connects: Dict[int, WebSocketServerProtocol] = connects or {}
        self.thread = None
        self.kill_event = asyncio.Event()
        self.unbinded = False
        self.modules: List[BaseWSModule] = []
        self.closing_all = False
    async def close_all_instances(self):

        for w in self.connects.values():
            await w.close()



    def quit(self):
        # self.thread = None
        print("Quitting WS")

        print("WS Stopping Modules")
        for m in self.modules:
            try:
                loop = asyncio.get_event_loop()
            except:
                loop = asyncio.new_event_loop()
            loop.run_until_complete(m.sendPastStates())

        self.stopModules()
        self.kill_event.set()
        # self.thread.join()
        while not self.unbinded:
            self.kill_event.set()
            time.sleep(0.2)
            print("Waiting WS Unbind")
        print("WS Exiting...")


    def loadModule(self, module: Type[BaseWSModule], state_holder: Type[BaseStateHolder],
                   *args, **kwargs):
        if not self.isLoaded(module):
            trigger = asyncio.Event()
            self.modules.append(module(self.connects.get, trigger, state_holder, *args, **kwargs))

    def isLoaded(self, module: Type[BaseWSModule]) -> bool:
        for _module in self.modules:
            if isinstance(_module, module):
                return True
        return False

    def getModule(self, module: Type) -> BaseWSModule:
        for mm in self.modules:
            print(f'MMMMM {mm} {module} {isinstance(mm, module)}')
            if isinstance(mm, module):
                mm: BaseWSModule
                return mm

    def stopModules(self):
        for mm in self.modules:
            mm.stop()

    def getStateHolderOfModule(self, module: Type) -> BaseStateHolder:

        return self.getModule(module).state_holder
