from __future__ import annotations

from threading import Thread
from typing import List, Dict, Type, Tuple

from src.Controllers.BasicController import BasicController
from src.SMarketScraper import SteamMarketScraper
from src.WebSocketInterface import WSInterface
from src.config import Config
from src.routing import Router


class ItemNaming(BasicController):


    @staticmethod
    def GET(R: Router, **kwargs):
        R.write_response("Not implemented.")
        return

    @staticmethod
    def POST(R: Router, **kwargs):

        sucess, ob = R.RH.DMData.tryRetrieveOfferbook()
        if not sucess:
            R.DMDataLocked(R.RH.DMData.status)
            return

        allf, fm = ob.containsFlags([ob.Flags.DMARKET_OFFERS_RECEIVED])
        if not allf:
            R.OfferBookMissingFlags(fm)
            return
        R.actionSucceeded("Item NameIDing started.")

        def detach():
            try:
                R.RH.DMData.lock(status="Item Naming...")
                wsi = WSInterface()
                from src.WSModules.WSMProgress import WSMProgress
                from src.StateHolder.Progress import Progress
                from src.WSModules.WSMProxyHealth import WSMProxyHealth
                from src.StateHolder.ProxyHealth import ProxyHealth

                wsi.serve([(WSMProgress, Progress, [len(ob.offers)], None),
                           (WSMProxyHealth, ProxyHealth, None, None)])
                R.RH.PO.implementUpdateTracking(wsi.getModule(WSMProxyHealth).state_holder.update)

                SteamMarketScraper.itemNameIDIt(ob, PO=R.RH.PO, progress_trigger=wsi.getModule(WSMProgress).state_holder.update,
                                                annotateImediately=Config.Steam.ItemNaming.ANNOTATE_IMMEDIATELY,
                                                useRedis=True)
                wsi.getModule(WSMProgress).state_holder.force_end()

                ob.saveToCache(testing=False)
                R.RH.DMData.lock("Unbinding WS Socket...")
                wsi.quit()

                R.RH.DMData.unlock()
            except (Exception, BaseException) as ex:
                print(ex)
                R.RH.DMData.unlock()
        Thread(target=detach, daemon=True).start()


    @staticmethod
    def getRequiredParams() -> Dict[str, Type | Tuple]:
        return {}
