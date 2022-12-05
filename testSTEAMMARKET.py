import random

from src.Models.DMOfferBook import OfferBook, SORTING
from src.Models.ProxyOrchestrator import ProxyOrchestrator
from src.SMarketScraper import SteamMarketScraper, STEAM_CURRENCIES
from src.proxies import PROXIES_SOCKS5
from src.DMarketScraper import DMarketScraper
PROXIES = PROXIES_SOCKS5
random.shuffle(PROXIES)
# page = Dispatcher.requestSteamMarketItem("730", "StatTrak™ Dual Berettas | Dezastre (Minimal Wear)").text
#

# big_ob = OfferBook.loadFromCache(testing=False)

# ob = big_ob.getSubsetOfferBook(50, offset=0)
#
# ob = DMarketScraper.getAllOffers(limit=100, priceFrom=50, priceTo=10000, maxLimit=100, types="p2p")
#
# PO = ProxyOrchestrator.build_from_raw(PROXIES, method='socks5')
#
# SteamMarketScraper.itemNameIDIt(ob, PO=PO)
# SteamMarketScraper.priceSkins(ob, steam_currency=STEAM_CURRENCIES.get("USD"), PO=PO, max_histogram_entries=5)
#
# ob.saveToCache(testing=True)
ob = OfferBook.loadFromCache(testing=True)

# ob = OfferBook.loadFromCache(testing=True)
# ob.convertDMPrices("ARS")
ob.sortOffers(SORTING.TYPE.MidPriceGapRatio, SORTING.DIRECTION.DESCENDANT)

ob.print()
ob.printOffers(showHistogram=True, max_entries=5)

