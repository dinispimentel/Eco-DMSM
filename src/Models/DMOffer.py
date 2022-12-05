from ecolib.price import Price

from .SMHistogram import Histogram


class Offer:

    def __init__(self, itemId: str, amount: int, inMarket: bool, lockedStatus: bool, title: str, status: bool,
                 dm_discount: int, dm_price: Price, sm_price: Price = None, steam_name_id=None,
                 histogram: Histogram = None):
        self.itemId = itemId
        self.amount = amount
        self.inMarket = inMarket
        self.lockedStatus = lockedStatus
        self.title = title
        self.status = status
        self.dm_discount = dm_discount
        self.dm_price = dm_price
        self.sm_price = sm_price
        self.steam_name_id = steam_name_id
        self.histogram = histogram

    def setSteamNameId(self, steam_name_id):
        self.steam_name_id = steam_name_id

    @staticmethod
    def build_frow_raw(dm_raw_json: dict):
        return Offer(dm_raw_json['itemId'], dm_raw_json['amount'], dm_raw_json['inMarket'], dm_raw_json['lockStatus'],
                     dm_raw_json['title'], dm_raw_json['status'], dm_raw_json['discount'],
                     Price(float(dm_raw_json['price']['USD']) / 100, "USD"))

    @staticmethod
    def rebuildOffer(od: dict):
        if od.get('dm_price'):
            od.update({"dm_price": Price(**od.get('dm_price'))})
        if od.get('sm_price'):
            od.update({"sm_price": Price(**od.get('sm_price'))})
        histogram_raw = od.get('histogram')
        if histogram_raw:
            od.update({'histogram': Histogram(histogram_raw['buy_offer_book'],
                                              histogram_raw['sell_offer_book'],
                                              histogram_raw['bid'],
                                              histogram_raw['ask']
                                              )})
        return Offer(**od)


    def toDICT(self):
        d = {**self.__dict__}
        if self.dm_price:
            d.update({'dm_price': self.dm_price.toDICT()})
        if self.sm_price:
            d.update({'sm_price': self.sm_price.toDICT()})
        if self.histogram:
            d.update({"histogram": self.histogram.toDICT()})
        return d

    def print(self):
        from src.Models.DMOfferBook import SORTING
        ST = SORTING.TYPE
        c = self.sm_price.currency
        print(f'''################################
Title: {self.title}
DM Disc: {self.dm_discount}%
DM Price: {(self.dm_price.cValue or self.dm_price.value)} {(self.dm_price.cCurrency or self.dm_price.currency)}
SM Price: {self.sm_price.value} {self.sm_price.currency}
DIFF (INST|MID|ASK): {ST.InstantPriceGap(self):.2f}{c} | {ST.MidPriceGap(self):.2f}{c} | {ST.AskPriceGap(self):.2f}{c}
DIFF% (INST|MID|ASK) : {(ST.InstantPriceGapRatio(self) * 100):.2f}% | {(ST.MidPriceGapRatio(self) * 100):.2f}% | {
    (ST.AskGapPriceRatio(self) * 100):.2f}%
lockedStatus: {self.lockedStatus}
SteamItemNameID: {self.steam_name_id}
''')
# ItemID: {self.itemId}
#
# Status: {self.status}
# Amount: {self.amount}
# inMarket: {self.inMarket}
# lockedStatus: {self.lockedStatus}
################################''')

    def printPrice(self, max_entries=5):

        print("----------------------------------")
        print(f'Max Buyer Price (BID): {self.histogram.bid}')
        print(f'Max Seller Price (ASK): {self.histogram.ask}')
        print("HISTOGRAM:")
        self.histogram.print(max_entries=max_entries)
        print("----------------------------------")