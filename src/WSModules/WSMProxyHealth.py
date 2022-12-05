from typing import Tuple, Type, Callable

from websockets.server import WebSocketServerProtocol

from src.StateHolder.BaseStateHolder import BaseStateHolder
from src.WSModules.BaseWSModule import BaseWSModule


class WSMProxyHealth (BaseWSModule):

    def __init__ (self, get_instance_ws: Callable[[int], WebSocketServerProtocol], trigger, state_holder: Type[BaseStateHolder], *args):
        super().__init__(get_instance_ws, trigger, state_holder, *args)

    async def sendPastStateToInstance(self, instance_id: int, state: Tuple):
        from src.WebSocketInterface import WSInterface
        res = WSInterface.create_response(True,
                                          {
                                              "proxy_health": state[0]
                                          })
        self.state_holder.increment_states_served_on_instance(instance_id, [state])
        await self.get_instance_ws(instance_id).send(res)
