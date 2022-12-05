import asyncio
from asyncio import Event
from typing import Tuple, Type, Callable

from websockets.server import WebSocketServerProtocol

from src.StateHolder.BaseStateHolder import BaseStateHolder
from src.WSModules.BaseWSModule import BaseWSModule


class WSMProgress (BaseWSModule):

    async def sendPastStateToInstance(self, instance_id: int, state: Tuple[float, str, int]):
        from src.WebSocketInterface import WSInterface
        print(instance_id, state)
        res = WSInterface.create_response(True, {'progress': float(f'{state[0]:.2f}'),
                                                 'progress_details': state[1],
                                                 'timestamp': state[2]
                                           })
        self.state_holder.increment_states_served_on_instance(instance_id, [state])
        try:
            await self.get_instance_ws(instance_id).send(res)
        except (BaseException, Exception):
            await asyncio.sleep(0)






