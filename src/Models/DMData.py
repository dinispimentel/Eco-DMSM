import time
from typing import Tuple, Callable

from .DMOfferBook import OfferBook


class DMData:


    def __init__(self, offerbook: OfferBook = None, lastUpdate=None, status=None, progress=None):
        self.locked: bool = False
        self.offerbook: OfferBook = offerbook
        self.lastUpdate: int = lastUpdate
        self.status: str = status or "Idle"
        self.progress: Callable[[float, int], bool] = progress  # em ratio [0 ; 1]


    def tryRetrieveOfferbook(self) -> Tuple[bool, OfferBook or str]:
        if self.locked:
            return False , self.status
        else:
            return True , self.offerbook

    def lock(self, status="Processing..."):
        self.locked = True
        self.status = status
        self.timeUpdate()

    def unlock(self):
        self.locked = False
        self.status = "Idle"
        self.timeUpdate()

    def timeUpdate(self):
        self.lastUpdate = int(time.time())

    def setStatus(self, newStatus: str):
        self.status = newStatus





