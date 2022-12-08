import time
from asyncio import Event

from src.StateHolder.BaseStateHolder import BaseStateHolder


class Progress(BaseStateHolder):

    def __init__(self, event_updated: Event, job_count):
        self.done_jobs = 0
        self.max_jobs = job_count
        super().__init__(event_updated)

    def update(self, timestamp: int):
        self.done_jobs += 1

        self.all_states.append( (self.done_jobs/self.max_jobs, timestamp) )
        self.trigger.set()

    def force_end(self):
        self.done_jobs = self.max_jobs
        self.all_states.append((self.done_jobs / self.max_jobs, time.time()))
        self.trigger.set()
