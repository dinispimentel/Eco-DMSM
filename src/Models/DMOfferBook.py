from __future__ import annotations

import json
from typing import List, Tuple, Callable

from src.config import Config
from .DMOffer import Offer
from ..dispatcher import Dispatcher


class SORTING:
    class TYPE:

        @staticmethod
        def InstantPriceGap(elem: Offer):
            return elem.sm_price.value - (elem.dm_price.cValue or elem.dm_price.value)

        @staticmethod
        def MidPriceGap(elem: Offer):
            if len(elem.histogram.buy_offer_book) > 0 and len(elem.histogram.sell_offer_book) > 0:
                return ((elem.histogram.sell_offer_book[0][0] + elem.histogram.buy_offer_book[0][0]) / 2) \
                       - (elem.dm_price.cValue or elem.dm_price.value)

            return 2 ** 31

        @staticmethod
        def AskPriceGap(elem: Offer):
            return elem.histogram.ask - (elem.dm_price.cValue or elem.dm_price.value)

        @staticmethod
        def InstantPriceGapRatio(elem: Offer):
            return (elem.sm_price.value - (elem.dm_price.cValue or elem.dm_price.value)) / (elem.dm_price.cValue or elem.dm_price.value)

        @staticmethod
        def MidPriceGapRatio(elem: Offer):
            if len(elem.histogram.buy_offer_book) > 0 and len(elem.histogram.sell_offer_book) > 0:
                return (((elem.histogram.sell_offer_book[0][0] + elem.histogram.buy_offer_book[0][0]) / 2)
                        - (elem.dm_price.cValue or elem.dm_price.value)) / (elem.dm_price.cValue or elem.dm_price.value)

            return 2 ** 31

        @staticmethod
        def AskGapPriceRatio(elem: Offer):
            return (elem.histogram.ask - (elem.dm_price.cValue or elem.dm_price.value)) / (elem.dm_price.cValue or elem.dm_price.value)

    @staticmethod
    def createConvDict():
        method_list = [func for func in dir(SORTING.TYPE) if callable(getattr(SORTING.TYPE, func))
                       and not func.startswith("__")]
        goodDict = {}

        for func in method_list:
            goodDict.update({func: getattr(SORTING.TYPE, func)})

        return goodDict

    @staticmethod
    def convertNameToFunc(name: str):
        return SORTING.createConvDict()[name]

    class DIRECTION:

        ASCENDANT = 0
        DESCENDANT = 1


class OfferBook:
    class Flags:
        DMARKET_OFFERS_RECEIVED = 0
        STEAM_ITEM_NAMED = 1
        STEAM_MARKET_PRICED = 2

        @staticmethod
        def createConvDict():
            __convDict = dict(OfferBook.Flags.__dict__)
            __goodDict = {}
            for k, v in __convDict.items():
                if k[0] != "_" and type(v) == type(1):
                    __goodDict.update({str(v): k})
            return __goodDict

        @staticmethod
        def convertFlagNumbersToStrs(nums: List[int]):
            ss = []
            convDict = OfferBook.Flags.createConvDict()

            for num in nums:
                ss.append(convDict[str(num)])
            return ss

    def __init__(self, offers=None, sortType=None,
                 sortDir=None, priceFrom=None, priceTo=None,
                 cursor=None, done=None, lastCursor=None, flags=None, histogram=None):
        if offers is None:
            offers = []
        if flags is None:
            flags = []
        self.offers: List[Offer] = offers
        self.sortType = sortType
        self.sortDir = sortDir
        self.priceFrom = priceFrom
        self.priceTo = priceTo
        self.lastCursor: str = cursor or lastCursor
        self.done = done
        self.flags = flags

    def addOffer(self, offer: Offer):
        self.offers.append(offer)

    def addOffers(self, offers: List[Offer]):
        self.offers += offers

    def sortOffers(self, sortFunc: Callable[[Offer], int or float], sortDir: int):
        self.offers.sort(key=sortFunc, reverse=bool(sortDir))

    def updateLastCursor(self, newcursor):
        self.lastCursor = newcursor

    def print(self):

        print(
            f'''
Offer Count: {len(self.offers)}
            '''
        )

    def printOffers(self, showHistogram=False, max_entries=5):

        for offer in self.offers:
            offer.print()
            if showHistogram:
                offer.printPrice(max_entries=max_entries)

    def toDICT(self):
        d = {**self.__dict__}
        d_o = []
        for offer in self.offers:
            d_o.append(offer.toDICT())

        d.update({'offers': d_o})
        return d

    def addFlag(self, flag):
        if flag not in self.flags:
            self.flags.append(flag)

    def containsFlags(self, flags: List[int]) -> Tuple[bool, List[int]]:
        flags_not_found = []
        for flag in flags:
            if not (flag in self.flags):
                flags_not_found.append(flag)

        return True if len(flags_not_found) < 1 else False, flags_not_found

    def saveToCache(self, testing):
        with open(Config.DMarket.OfferBook.Files.getSaveDir(testing=testing), "w+") as f:
            f.write(json.dumps(self.toDICT()))

    @staticmethod
    def loadFromCache(testing) -> OfferBook:
        with open(Config.DMarket.OfferBook.Files.getSaveDir(testing=testing), "r") as f:
            r: dict = json.loads(f.read())
        offers_raw = r.get('offers')
        offers = []
        for offer in offers_raw:
            offers.append(Offer.rebuildOffer(offer))

        r.update({'offers': offers})
        return OfferBook(**r)

    def getSubsetOfferBook(self, offer_limit: int, offset=0) -> OfferBook:
        try:
            if offer_limit < 1:
                raise ArithmeticError("Limit must be greater than 1")

            this_ob = self.__dict__
            this_ob.update({'offers': self.offers[offset:offer_limit + offset]})
            return OfferBook(**this_ob)
        except (IndexError, Exception):
            return self

    def convertDMPrices(self, targetcur: str):
        cur_req = ["EUR", "USD", "ARS"]
        if targetcur not in cur_req:
            cur_req.append(targetcur)

        if self.offers[0].dm_price.currency != Dispatcher.ExRates_getBase():
            Dispatcher.ExRates_forceUpdate(base=self.offers[0].dm_price.currency, currencies=cur_req)

        rates = Dispatcher.ExRates_getRates()

        for o in self.offers:
            o.dm_price.cValue = round(float(o.dm_price.value) * float(rates[o.dm_price.currency + str(targetcur)]), 3)
            o.dm_price.cCurrency = targetcur
