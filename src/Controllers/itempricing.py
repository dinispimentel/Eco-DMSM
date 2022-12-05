from __future__ import annotations

from threading import Thread
from typing import List, Dict, Type, Tuple

from ecolib.utils import Utils

from src.Controllers.BasicController import BasicController
from src.SMarketScraper import SteamMarketScraper, STEAM_CURRENCIES
from src.WebSocketInterface import WSInterface
from src.routing import Router


class ItemPricing(BasicController):

    @staticmethod
    def POST(R: Router, **kwargs):
        sucess, ob = R.RH.DMData.tryRetrieveOfferbook()
        if not sucess:
            R.DMDataLocked(R.RH.DMData.status)
            return

        allf, fm = ob.containsFlags([ob.Flags.DMARKET_OFFERS_RECEIVED, ob.Flags.STEAM_ITEM_NAMED])
        if not allf:
            R.OfferBookMissingFlags(fm)
            return

        jbody = kwargs.get('jbody')
        mp = ItemPricing.check_params_missing(jbody)
        if len(mp) > 0:
            R.missingParams(mp)
            return
        err_supp = ItemPricing.check_param_type(jbody)
        if len(err_supp) > 0:
            R.badParamsTypes(err_supp)
            return
        steam_cur = jbody.get('steam_currency')
        try:
            if isinstance(steam_cur, str):
                steam_cur = STEAM_CURRENCIES[steam_cur.upper()]
        except (KeyError, AttributeError, IndexError):
            R.badParams([("steam_currency", f'{steam_cur} !belongto ({STEAM_CURRENCIES})')])
            R.RH.DMData.unlock()
            return
        R.actionSucceeded(content="Item pricing started!")

        def detach():
            try:
                R.RH.DMData.lock(status="Item Pricing...")
                wsi = WSInterface()
                from src.WSModules.WSMProgress import WSMProgress
                from src.StateHolder.Progress import Progress
                from src.WSModules.WSMProxyHealth import WSMProxyHealth
                from src.StateHolder.ProxyHealth import ProxyHealth



                wsi.serve([(WSMProgress, Progress, None, None),
                           (WSMProxyHealth, ProxyHealth, None, None)])
                R.RH.PO.implementUpdateTracking(wsi.getModule(WSMProxyHealth).state_holder.update)
                SteamMarketScraper.priceSkins(ob, steam_currency=steam_cur,
                                              PO=R.RH.PO, max_histogram_entries=(jbody.get('max_histogram_entries') or 5))
                wsi.quit()
                R.RH.DMData.unlock()

            except (Exception, BaseException):
                R.RH.DMData.unlock()
        Thread(target=detach, daemon=True).start()

    @staticmethod
    def getRequiredParams() -> Dict[str, Type | Tuple]:

        return {
            "steam_currency": (str, int)  # STR que é conv em int
        }
