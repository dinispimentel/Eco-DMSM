from __future__ import annotations

from threading import Thread
from typing import List, Dict, Type, Tuple

from src.Controllers.BasicController import BasicController
from src.Models.DMOfferBook import OfferBook
from src.config import Config


class ConvertCurrency (BasicController):

    from src.routing import Router

    @staticmethod
    def __areAllParamsValid(jbody: Dict) -> Tuple[bool, List[Tuple[str, str]]]:
        ttc = str(jbody.get('target_to_convert')).lower()
        target_cur = jbody.get('target_currency')
        bad_params: List[Tuple[str, str]] = []
        if ttc not in ['dm', 'sm']:
            bad_params.append(("target_to_convert", " Not equal to dm or sm"))
        if ttc == "sm":
            bad_params.append(("target_to_convert", " Not implemented SM conversion yet, ask DP."))
        if target_cur not in Config.CurrencyConversion.AVAILABLE_CURRENCIES:
            bad_params.append(("target_currency", f' Not in available currencies: '
                                                  f'{Config.CurrencyConversion.AVAILABLE_CURRENCIES}'))
        return len(bad_params) < 1, bad_params

    @staticmethod
    def PATCH(R: Router, **kwargs):

        jbody: Dict = kwargs.get('jbody')
        mp = ConvertCurrency.check_params_missing(jbody)
        if len(mp) > 0:
            R.missingParams(mp)
            return
        err_supp = ConvertCurrency.check_param_type(jbody)
        if len(err_supp) > 0:
            R.badParamsTypes(err_supp)
            return
        allValid, bp = ConvertCurrency.__areAllParamsValid(jbody)
        if not allValid:
            R.badParams(bp)
            return

        R.actionSucceeded("Offerbook conversion started...")
        def detach():
            success, ob = R.RH.DMData.tryRetrieveOfferbook()
            if success:
                try:
                    R.RH.DMData.lock("OfferBook currency conversion ongoing...")
                    ob: OfferBook
                    if str(jbody.get('target_to_convert')).lower() == "dm":
                        ob.convertDMPrices(targetcur=str(jbody.get('target_currency')).upper())
                        print("Converted")
                    R.RH.DMData.unlock()
                except (Exception, BaseException):
                    R.RH.DMData.unlock()
        Thread(target=detach, daemon=True).start()

    @staticmethod
    def getRequiredParams() -> Dict[str, Type | Tuple]:
        return {
            "target_to_convert": str,
            "target_currency": str
        }
