import json
import time
from threading import Thread
from typing import Callable

from ecolib.price import Price
from ecolib.threader import Threader

from .Models.DMOfferBook import OfferBook
from .Models.ProxyOrchestrator import ProxyOrchestrator
from .Models.SMHistogram import Histogram
from .RedisCache import RedisCache
from .SteamSieve import Sieve
from .config import Config
from .dispatcher import Dispatcher

STEAM_CURRENCIES = {
    "USD": 1,
    "GBY": 2,
    "EUR": 3,
    "ARS": 34
}


def __revSteam_Currencies(s_c):
    c_s = {}
    for k, v in s_c.items():
        c_s.update({str(v): str(k)})
    return c_s


CURRENCIES_STEAM = __revSteam_Currencies(STEAM_CURRENCIES)


class SteamMarketScraper:

    class Exceptions:

        class MissingFlagsError(Exception):
            """Missing flags on the request."""

    @staticmethod
    def itemNameIDIt(ob: OfferBook, appID="730", PO: ProxyOrchestrator = None,
                     progress_trigger: Callable[[float], None] = None,
                     annotateImediately: bool = True, useRedis=True, showUses=True):
        thread_pool = []
        to_cache = {}
        allflags, fm = ob.containsFlags([ob.Flags.DMARKET_OFFERS_RECEIVED])
        global redis_uses
        redis_uses = 0
        global proxy_uses
        proxy_uses = 0
        if not allflags:
            print(f"Missing flags: {ob.Flags.convertFlagNumbersToStrs(fm)} ")
            raise SteamMarketScraper.Exceptions.MissingFlagsError

        def __dispatchSteamNameId(offerIdx, proxy_orchestrator: ProxyOrchestrator, retries=0, annotateToCache=None,
                                  uses: Callable[[int], None] = None):

            def trigger_progress():
                if progress_trigger:
                    progress_trigger( # (offerIdx + 1) / len(ob.offers),
#                                     f'{offerIdx + 1} Offers item named of {len(ob.offers)}',
                                     time.time())

            if useRedis:
                rcid = RedisCache.getItemNameID(ob.offers[offerIdx].title)
                if rcid:
                    ob.offers[offerIdx].setSteamNameId(rcid)

                    trigger_progress()
                    if uses:
                        uses(1)
                    return # importante


            if retries < Config.Steam.ItemNaming.MAX_RETRIES:


                res = Dispatcher.requestSteamMarketItem(appID, ob.offers[offerIdx].title,
                                                        proxy_orchestrator=proxy_orchestrator)
                print("After req prox: ", res)
                if res.status_code != 200:
                    print(f'RES_CODE: {res.status_code}\nAwaiting {Config.Steam.ItemNaming.FORBIDDEN_TIMEOUT} secs')
                    time.sleep(Config.Steam.ItemNaming.FORBIDDEN_TIMEOUT)
                    __dispatchSteamNameId(offerIdx, proxy_orchestrator, retries=retries+1, annotateToCache=
                                          annotateToCache)
                    return

                page = res.text
                inid = Sieve.getItemNameID(page)
                if annotateToCache:
                    annotateToCache(ob.offers[offerIdx].title, inid)
                else:
                    RedisCache.saveItemNameIDs({ob.offers[offerIdx].title: inid})

                ob.offers[offerIdx].setSteamNameId(inid)
                if uses:
                    uses(0)
                trigger_progress()

        updateToCache = lambda t, inid: to_cache.update({
            t: inid
        })
        def uses(method):
            global redis_uses, proxy_uses
            if method == 1:
                redis_uses += 1
            else:
                proxy_uses += 1
        kwargs = ({} if annotateImediately is True else {"annotateToCache": updateToCache})
        if showUses:
            kwargs.update({"uses": uses})

        for i in range(0, len(ob.offers)):
            thread_pool.append(Thread(target=__dispatchSteamNameId, args=(i, PO), kwargs=kwargs))

        T = Threader(lambda: thread_pool, Config.Steam.ItemNaming.INSTANCES,
                     delay_config=Config.Steam.ItemNaming.DELAY_CONFIG)

        # midFunc = (lambda s, e: progress_trigger(e/len(ob.offers),
        #                                          f'{e} Offers item-named of {len(ob.offers)}')
        #            )if progress_trigger else (lambda s, e: print(f'Dispatched {s}->{e} <{len(ob.offers)}>'))

        T.dispatch()


        # cache what ins't cached yet

        print(f'USES: #Proxy: {proxy_uses} | #Redis: {redis_uses}')

        ob.addFlag(ob.Flags.STEAM_ITEM_NAMED)

    @staticmethod
    def priceSkins(ob: OfferBook, steam_currency=1, PO: ProxyOrchestrator = None, max_histogram_entries=None,
                   progress_trigger: Callable[[float], None]=None):
        thread_pool = []
        allflags, fm = ob.containsFlags([ob.Flags.STEAM_ITEM_NAMED])
        dict_itnid_histogram = {}  # int: Histogram
        if not allflags:
            print(f"Missing flags: {ob.Flags.convertFlagNumbersToStrs(fm)} ")
            raise SteamMarketScraper.Exceptions.MissingFlagsError

        # DONE:// ADICIONAR CACHE (SOMENTE INTERIOR DA FUNÇÃO) PARA PRICE DAS MESMAS SKINS (DOS MESMOS STEAM NAME ID)
        global pricing_saved
        pricing_saved = 0
        def psavedpp():
            global pricing_saved
            pricing_saved += 1
        def __dispatchSkinPricing(offerIdx, poo: ProxyOrchestrator, retries=0):


            if ob.offers[offerIdx].steam_name_id in list(dict_itnid_histogram.keys()):
                ob.offers[offerIdx].histogram = dict_itnid_histogram[ob.offers[offerIdx].steam_name_id]
                psavedpp()
            else:
                res = Dispatcher.requestSteamOfferBooks(ob.offers[offerIdx].steam_name_id, steam_currency=steam_currency,
                                                        proxy_orchestrator=poo)
                if res.status_code == 400:
                    print(res.content)
                if res.status_code != 200:
                    if retries < Config.Steam.SkinPricing.MAX_RETRIES:
                        # print(f"Sleeping forbidden thread for: {Config.Steam.SkinPricing.FORBIDDEN_TIMEOUT} secs")

                        time.sleep(Config.Steam.SkinPricing.FORBIDDEN_TIMEOUT)
                        __dispatchSkinPricing(offerIdx, poo, retries=retries+1)
                    return


                ob.offers[offerIdx].histogram = Histogram.build_raw_histogram(json.loads(res.text),
                                                                              max_entries=max_histogram_entries,
                                                                              currency=CURRENCIES_STEAM
                                                                              .get(str(steam_currency)))
                dict_itnid_histogram.update({ob.offers[offerIdx].steam_name_id: ob.offers[offerIdx].histogram})
            if progress_trigger:
                progress_trigger(time.time())
            ob.offers[offerIdx].sm_price = Price(ob.offers[offerIdx].histogram.bid,  # preço mais alto que o buyer compra auto
                                                 # que o comprador compra
                                                 ob.offers[offerIdx].histogram.currency)

        for i in range(0, len(ob.offers)):
            thread_pool.append(Thread(target=__dispatchSkinPricing, args=(i, PO)))

        T = Threader(lambda: thread_pool, Config.Steam.SkinPricing.INSTANCES, delay_config=
                     Config.Steam.SkinPricing.DELAY_CONFIG)

        T.dispatch(lambda s, e: print(f'Dispatched {s}->{e} <{len(ob.offers)}>'))
        print("Pricing saved: " + str(pricing_saved))
        ob.addFlag(ob.Flags.STEAM_MARKET_PRICED)
