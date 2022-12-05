from __future__ import annotations

import time
from typing import Tuple, Callable

from src.config import Config


class Proxy:

    def __init__(self, host, port, method="socks4", lockStart=None, lockDuration=None, timeout_strikes=0,
                 forbidden_strikes=0, too_many_requests_strikes=0, fatal_strikes=0,
                 onUpdate: Callable = None):

        self.host = host
        self.port = port
        self.method = method
        self.lockStart: int = lockStart
        self.lockDuration: float or int = lockDuration
        self.timeout_strikes = timeout_strikes
        self.forbidden_strikes = forbidden_strikes
        self.too_many_requests_strikes = too_many_requests_strikes
        self.fatal_strikes = fatal_strikes
        self.onUpdate = onUpdate

    def checkLocked(self):

        if self.lockStart is not None and self.lockDuration is not None:

            return self.lockStart + self.lockDuration > int(time.time())  # Locked

        return False  # no lock


    def lock(self, lockduration=Config.Proxying.REUSABILITY_TIMEOUT):

        print(f"Locking: {self.getProxy()['https'].split('://')[1]}")

        self.lockStart = int(time.time())
        self.lockDuration = int(lockduration)

    def strike(self, strike_type: str = "timeout"):
        if strike_type == "timeout":
            self.timeout_strikes += 1
        if strike_type == "forbidden":
            self.forbidden_strikes += 1
        if strike_type == "too_many_requests":
            self.too_many_requests_strikes += 1
        if strike_type == "fatal":
            self.fatal_strikes += 1

    def striked(self, specific_strike=None):
        time_out_striked = self.timeout_strikes >= Config.Proxying.StrikeLimit.TIME_OUT
        forbidden_striked = self.forbidden_strikes >= Config.Proxying.StrikeLimit.FORBIDDEN
        too_many_requests_striked = self.too_many_requests_strikes >= Config.Proxying.StrikeLimit.TOO_MANY_REQUESTS
        fatal_striked = self.fatal_strikes >= Config.Proxying.StrikeLimit.FATAL
        if specific_strike:
            if specific_strike == "timeout":
                return time_out_striked
            elif specific_strike == "forbidden":
                return forbidden_striked
            elif specific_strike == "too_many_requests":
                return too_many_requests_striked
            elif specific_strike == "fatal":
                return fatal_striked
        else:
            return time_out_striked or forbidden_striked or too_many_requests_striked or fatal_striked


    def clearStrikes(self):
        self.timeout_strikes = 0
        self.forbidden_strikes = 0
        self.too_many_requests_strikes = 0
        self.fatal_strikes = 0
        if self.onUpdate:
            self.onUpdate()

    def getProxy(self):

        return {
            'http': f'{self.method}://{self.host}:{self.port}',
            'https': f'{self.method}://{self.host}:{self.port}'
        }

    def getIPPORT(self):

        return self.getProxy()['http'].split('://')[1]

    def toDICT(self):
        return self.__dict__

    def setOnUpdate(self, func: Callable):
        self.onUpdate = func

    def getHealth(self) -> Tuple[float, float, float, float]:
        r_tmr = self.too_many_requests_strikes / Config.Proxying.StrikeLimit.TOO_MANY_REQUESTS
        r_ts = self.timeout_strikes / Config.Proxying.StrikeLimit.TIME_OUT
        r_fb = self.forbidden_strikes / Config.Proxying.StrikeLimit.FORBIDDEN
        r_ft = self.fatal_strikes / Config.Proxying.StrikeLimit.FATAL

        return (100-(r_tmr*100)), (100-(r_ts*100)), (100-(r_fb*100)), (100-(r_ft*100))


