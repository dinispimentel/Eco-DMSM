from __future__ import annotations

import time
from threading import Thread
from typing import List, Dict, Type, Tuple

from ecolib.utils import Utils

from .BasicController import BasicController
from ..DMarketScraper import DMarketScraper, DMarketConfig
from ..config import Config
from ..routing import Router


class UpdateInternalDMarket(BasicController):

    @staticmethod
    def __areAllParamsValid(jbody) -> Tuple[bool, List[Tuple[str, str]]]:
        # kvreq = UpdateInternalDMarket.getRequiredOnlyKVPairs(jbody) # Isto não porque tem os opcionais

        bad_params: List[Tuple[str, str]] = []
        for k, v in jbody.items():
            if k == "gameId":
                if v != "a8db":
                    bad_params.append((k, "any gameId besides a8db (CSGO) is not supported yet."))
            elif k == "limit":
                if int(v) > 100 or int(v) < 0:
                    bad_params.append((k, f'{int(v)} !< 100 & {int(v)} !> 0.'))
            elif k == "maxLimit":
                if int(v) < 1:
                    bad_params.append((k, 'should not be less than 1.'))
                if int(v) > Config.DMarket.Offering.Constrains.MAX_SINGLE_MAX_LIMIT:
                    bad_params.append((k, f'should not be higher than '
                                          f'{Config.DMarket.Offering.Constrains.MAX_SINGLE_MAX_LIMIT}.'
                                          f'This can be incresead. Ask webmaster.'))

            elif k == "offset":
                if v > jbody.get('maxLimit'):
                    bad_params.append((k, f'should not be greater than maxLimit ({v}>{jbody.get("maxLimit")}).'))
            elif k == "orderBy":
                if v not in list(DMarketConfig.OrderBy.__dict__.values()):
                    bad_params.append((k, f'not in: {list(DMarketConfig.OrderBy.__dict__.values())}.'))
            elif k == "orderDir":
                if v not in list(DMarketConfig.OrderDir.__dict__.values()):
                    bad_params.append((k, f'not in: {list(DMarketConfig.OrderDir.__dict__.values())}.'))
            elif k == "currency":
                if str(v).upper() != "USD":
                    bad_params.append((k, "at the moment, DMarket only supports getting prices in USD."))
            elif k == "types":
                if str(v).find(",") != -1:
                    tps = str(v).split(",")
                    for i in range(0, len(tps)):
                        tps[i] = tps[i].strip()
                else:
                    tps = [str(v)]
                for t in tps:
                    if t not in Config.DMarket.Offering.Constrains.ALLOWED_TYPES:
                        bad_params.append((k, f'not in {Config.DMarket.Offering.Constrains.ALLOWED_TYPES}.'))
                    if tps.count(t) > 1:
                        bad_params.append((k, f'param dupped {t} (thx OOF).'))
            elif k == "priceFrom":
                if int(v) < 1:
                    bad_params.append((k, "can't be lower than 1."))
                if int(v) > jbody.get('priceTo'):
                    bad_params.append((k, f'can\'t be higher than priceTo ({int(v)} > {jbody.get("priceTo")})'))
            elif k == "priceTo":
                if int(v) < 1:
                    bad_params.append((k, "can't be lower than 1."))
                if int(v) < jbody.get('priceFrom'):
                    bad_params.append((k, f'can\'t be lower than priceFrom ({int(v)} < {jbody.get("priceFrom")})'))
            elif k == "treeFilters":
                wrongPrefix = False
                if str(v).find(",") != -1:
                    catPaths = str(v).split(",")
                else:
                    catPaths = [str(v)]
                for cPath in catPaths:
                    if (not cPath.startswith("categoryPath[]")) and not wrongPrefix:
                        wrongPrefix = True
                        bad_params.append((k, "must be a List of [categoryPath[]=..,categoryPath[]=..]"))
                    try:
                        cPValue = cPath.split("=")[1]
                        if cPValue not in Config.DMarket.Offering.Constrains.ALLOWED_TF_CATEGORIES_PATH:
                            bad_params.append((f'{k} |{cPValue}|',
                                               f'not in {Config.DMarket.Offering.Constrains.ALLOWED_TF_CATEGORIES_PATH}'))
                    except IndexError:
                        bad_params.append((f'{catPaths}{cPath}', ' "=" is needed between categoryPath[]x..'))
                    if catPaths.count(cPath) > 1:
                        bad_params.append((f'{catPaths} |{cPath}|', f' dupped.'))
        return len(bad_params) < 1, bad_params
    @staticmethod
    def POST(R: Router, **kwargs):
        old_data = R.RH.DMData  # retorna-la em caso de exception ou outro problema
        if R.RH.DMData.locked:
            R.DMDataLocked()
            return
        jbody: dict = kwargs.get("jbody")
        mp = UpdateInternalDMarket.check_params_missing(jbody)
        if len(mp) > 0:
            R.missingParams(mp)
            return
        err_supp = UpdateInternalDMarket.check_param_type(jbody)
        if len(err_supp) > 0:
            R.badParamsTypes(err_supp)
            return
        allValid, bp = UpdateInternalDMarket.__areAllParamsValid(jbody)
        if not allValid:
            R.badParams(bp)
            return

        R.actionSucceeded("DMarket internal Data update started.")

        def detach():
            try:

                R.RH.DMData.lock(status="Retrieving data from DMarket.")

                R.RH.DMData.offerbook = DMarketScraper.getAllOffers(
                    **UpdateInternalDMarket.getRequiredOnlyKVPairs(jbody)
                )

                R.RH.DMData.offerbook.saveToCache(testing=kwargs.get('testing'))
                R.RH.DMData.unlock()
                print(f"Update in: {time.time()}")
            except (Exception, BaseException) as ex:
                R.RH.DMData = old_data
                print(ex)
                print('No changes took place to the prod data."')


        Thread(target=detach, daemon=True).start()


    @staticmethod
    def GET(R: Router, **kwargs):
        print("Not Supported.")

    @staticmethod
    def getRequiredParams() -> Dict[str, Type | Tuple]:
        return {"gameId": str,
                "limit": int,
                "offset": int,
                "orderBy": str,
                "orderDir": str,
                "currency": str,
                "types": str,
                "priceFrom": int,
                "priceTo": int,
                # "treeFilters": str,
                "maxLimit": int
                }
