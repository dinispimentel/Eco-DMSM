import json
import time
from threading import Thread

from ecolib.threader import Threader

from .Models.DMOffer import Offer
from .Models.DMOfferBook import OfferBook
from .config import Config
from .dispatcher import Dispatcher


class DMarketConfig:
    class OrderBy:
        BEST_DISCOUNT = "best_discount"
        PRICE = "price"
        TITLE = "title"

    class OrderDir:
        ASCENDANT = "asc"
        DESCENDANT = "desc"



class DMarketScraper:

    @staticmethod
    def getAllOffers(**kwargs) -> OfferBook:
        res_len = -99
        maxLimit = kwargs.get('maxLimit') or 3
        done = False
        thread_pool = []

        offerbook = OfferBook(priceFrom=kwargs.get('priceFrom'), priceTo=kwargs.get('priceTo'))

        def __dispatchOffering(**kwargs2):
            scode = 0
            retries = 0
            res = None
            while scode != 200 and retries < Config.DMarket.Offering.MAX_RETRIES:
                res = Dispatcher.requestAllDMarketItems(**kwargs2)
                scode = res.status_code
                if scode != 200:
                    retries += 1
                    time.sleep(Config.DMarket.Offering.TOO_MANY_REQUESTS_DELAY*retries)

            jres = json.loads(res.text)
            offers = jres['objects']
            goodOffers = []
            for offer in offers:
                goodOffers.append(Offer.build_frow_raw(offer))
            offerbook.addOffers(goodOffers)
            global done
            if "cursor" not in jres:
                done = True
            else:
                if jres['cursor'] == "":

                    done = True
                else:
                    offerbook.updateLastCursor(jres['cursor'])

        offset = 0

        T = Threader(lambda: thread_pool, Config.DMarket.Offering.INSTANCES,
                     delay_config=Config.DMarket.Offering.DELAY_CONFIG)

        idone = 0

        while (not done) and (idone < maxLimit):
            thread_pool = []  # Limpar a thread_pool
            for t in range(0, Config.DMarket.Offering.INSTANCES):  # ver como que isto decorre e mete-lo a repetir ate
                #  ultimas instancias não terem mais offers por terem o cursor muito à frente devido ao 'offset'
                kwargs.update({"offset": offset})
                if offerbook.lastCursor and offerbook.lastCursor != "":
                    kwargs.update({"cursor": offerbook.lastCursor})
                if idone + kwargs.get('limit') > maxLimit:
                    kwargs.update({"limit": maxLimit - idone})
                thread_pool.append(
                    Thread(target=__dispatchOffering, kwargs=kwargs)
                )
                offset += int(kwargs.get("limit"))
                idone += int(kwargs.get('limit'))
            offset = 0

            T.dispatch(lambda s, e: print(f'Dispatched Offering: {s}->{e}'))


        offerbook.addFlag(offerbook.Flags.DMARKET_OFFERS_RECEIVED)
        return offerbook





