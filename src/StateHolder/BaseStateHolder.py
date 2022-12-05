from abc import abstractmethod
from asyncio import Event
from typing import List, Dict, Tuple


class BaseStateHolder:

    """Base class for state"""

    # State é uma Tuple que corresponde aos conteúdos do que virá a ser parte da key data do json enviado

    def __init__(self, module_trigger: Event, *args, **kwargs):
        """Init StateHolder properties."""
        self.all_states: List[Tuple] = [()]
        self.trigger = module_trigger
        self.instances_states: Dict[int, List[Tuple]] = {}

    @abstractmethod
    def update(self, *args, **kwargs):
        """Adds data to the State Holder and triggers the Module-Trigger."""


    def register_instance(self, instance_id: int):
        if not instance_id in list(self.instances_states.keys()):
            self.instances_states.update({instance_id: [()]})

    def increment_states_served_on_instance(self, instance_id: int, states_served: List[Tuple]):
        _pre_states = self.instances_states.get(instance_id) or []
        self.instances_states.update({instance_id: (_pre_states + states_served)})

    def get_instance_and_states_in_need_to_be_served(self) -> List[Tuple[int, List[Tuple]]]:  # int, List states needing
        i_s_needed_to_be_served = []
        for iid in list(self.instances_states.keys()):  # O(n)
            a_not_b = [s for s in self.all_states if s not in self.instances_states[iid]]  # O(n^2)
            # a_not_b = list(set(self.all_states) - set(self.instances_states[iid]))
            cardinal = len(a_not_b)
            if cardinal != 0:
                i_s_needed_to_be_served.append((iid, a_not_b))

        return i_s_needed_to_be_served

    # from src.WebSocketInterface import WSInterface
    async def close_all_instances(self, wsi):

        for iid in list(self.instances_states.keys()):
            await wsi.connects.get(iid).close()
