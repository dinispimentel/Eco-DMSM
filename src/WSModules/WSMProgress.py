from asyncio import Event
from typing import Tuple, Type, Callable

from websockets.server import WebSocketServerProtocol

from src.StateHolder.BaseStateHolder import BaseStateHolder
from src.WSModules.BaseWSModule import BaseWSModule


class WSMProgress (BaseWSModule):

    async def sendPastStateToInstance(self, instance_id: int, state: Tuple[float, float]):
        from src.WebSocketInterface import WSInterface
        print(instance_id, state)
        res = WSInterface.create_response(True, {'progress': float(f'{state[0]:.2f}'),
                                                 'timestamp': state[1]
                                           })
        self.state_holder.increment_states_served_on_instance(instance_id, [state])
        await self.get_instance_ws(instance_id).send(res)


    def __init__(self, get_instance_ws: Callable[[int], WebSocketServerProtocol], trigger: Event, state_holder: Type[BaseStateHolder], *args, **kwargs):
        super().__init__(get_instance_ws, trigger, state_holder, *args, **kwargs)




