from asyncio import Event

from src.StateHolder.BaseStateHolder import BaseStateHolder


class Progress(BaseStateHolder):

    def __init__(self, event_updated: Event):
        super().__init__(event_updated)

    def update(self, progress: float, progress_details: str, timestamp: int):
        self.all_states.append( (progress, progress_details, timestamp) )
        self.trigger.set()
