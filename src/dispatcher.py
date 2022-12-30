import json

from typing import Callable

import requests
from requests import Response

from src.Models.Proxy import Proxy
from src.Models.ProxyOrchestrator import ProxyOrchestrator
from src.config import Config
from src.dmarketEx import dmarketRequest

proxies = {}


class Dispatcher:

    class Exceptions:

        class NoSucessFullResponse(Exception):
            """Status code received different from 200"""

    @staticmethod
    def dispatch_proxified(the_request: Callable[[Proxy], Response], PO: ProxyOrchestrator):
        _ProxyToUse = PO.getReadyProxy()
        try:
            print(f'Tentando request com: {_ProxyToUse.getIPPORT()}')
            res = the_request(_ProxyToUse)  # TODO ISTO TEM DE CHEGAR LA ABAIXO
            print(res.status_code)
            if res is not None:
                if res.status_code is not None:
                    if res.status_code == 429:
                        _ProxyToUse.strike(strike_type="too_many_requests")
                        _ProxyToUse.lock(Config.Proxying.TOO_MANY_REQUESTS_STACKABLE_LOCK*_ProxyToUse.too_many_requests_strikes)
                        print("TMRL: " + str(Config.Proxying.TOO_MANY_REQUESTS_STACKABLE_LOCK*_ProxyToUse.too_many_requests_strikes))
                        if _ProxyToUse.striked(specific_strike="too_many_requests"):
                            PO.removeBrokenProxy(_ProxyToUse)
                        return Dispatcher.dispatch_proxified(the_request, PO)
                    elif res.status_code == 403:
                        _ProxyToUse.strike(strike_type="forbidden")
                        if _ProxyToUse.striked(specific_strike="forbidden"):
                            PO.removeBrokenProxy(_ProxyToUse)
                        return Dispatcher.dispatch_proxified(the_request, PO)
                    elif res.status_code == 400:
                        return res.content
                    elif res.status_code < 400:
                        _ProxyToUse.clearStrikes()
                        return res
            else:
                print("resnone retrying")

            return Dispatcher.dispatch_proxified(the_request, PO)

        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout) as ex:
            _ProxyToUse.strike(strike_type="timeout")
            _ProxyToUse.lock(Config.Proxying.TIME_OUT_STACKABLE_LOCK*_ProxyToUse.timeout_strikes)
            if _ProxyToUse.striked(specific_strike="timeout"):
                print(f'Removing bcz {type(ex)} | {_ProxyToUse.checkLocked()}\n'
                      f'Strikes: TIME_OUT: {_ProxyToUse.timeout_strikes}')

                PO.removeBrokenProxy(_ProxyToUse)
            return Dispatcher.dispatch_proxified(the_request, PO)
        except (requests.exceptions.ConnectionError, requests.exceptions.SSLError,
                requests.exceptions.ProxyError) as ex:

            _ProxyToUse.strike(strike_type="fatal")
            _ProxyToUse.lock(Config.Proxying.FATAL_LOCK)
            if _ProxyToUse.striked(specific_strike="fatal"):
                print(f'Removing cz {type(ex)} | {_ProxyToUse.checkLocked()}')
                PO.removeBrokenProxy(_ProxyToUse)  # TODO AQUI AQUI
            return Dispatcher.dispatch_proxified(the_request, PO)
        except Exception as e:
            print(e)

    @staticmethod
    def requestDMarketItemInfoByTitle(title, limit):

        response = dmarketRequest('GET', '/exchange/v1/offers-by-title', {
            'Title': title,
            'Limit': limit
        })
        return response

    @staticmethod
    def requestAllDMarketItems(**kwargs):

        params = {
            "gameId": kwargs.get("gameId") or "a8db",
            "limit": kwargs.get("limit") or "100",
            "offset": kwargs.get("offset") or "0",
            "orderBy": kwargs.get("orderBy") or "best_discount",
            "orderDir": kwargs.get("orderDir") or "desc",
            "currency": kwargs.get("currency") or "USD",
            "types": kwargs.get("types") or "dmarket, p2p",
            "priceFrom": kwargs.get("priceFrom") or 0,
            "priceTo": kwargs.get("priceTo") or 1000,
            "treeFilters": kwargs.get('treeFilters') or "categoryPath[]=knife,categoryPath[]=rifle,"
                                                        "categoryPath[]=sniperrifle,categoryPath[]=pistol,"
                                                        "categoryPath[]=smg,categoryPath[]=shotgun,"
                                                        "categoryPath[]=machinegun"
        }

        if kwargs.get("cursor") is not None:
            params.update({"cursor": kwargs.get("cursor")})

        print(f"Params: {params}")

        response = dmarketRequest('GET', '/exchange/v1/market/items',
                                  params)
        return response

    @staticmethod
    def requestSteamMarketItem(appID, title, proxy_orchestrator: ProxyOrchestrator = None) -> requests.Response:
        url = f"https://steamcommunity.com/market/listings/{appID}/{title}"

        headers = {
            # "cookie": "sessionid=f61057601c3c20430f8ab92a; steamCountry=PT%257C6e01b352d886cff3d376e22f5246473b",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.9",
            # "Accept-Language": "pt-PT,pt;q=0.9,pt-BR;q=0.8,en;q=0.7,en-US;q=0.6,en-GB;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
            # (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"
        }

        if proxy_orchestrator:

            def the_request(p: Proxy) -> Response:
                return requests.request("GET", url, headers=headers,
                                proxies=p.getProxy(),
                                timeout=Config.Proxying.TIME_OUT,
                                verify=False)

            return Dispatcher.dispatch_proxified(the_request, proxy_orchestrator)

        else:
            response = requests.request("GET", url, headers=headers)
            return response

    @staticmethod
    def requestSteamOfferBooks(item_name_id: str, steam_currency=34, proxy_orchestrator=None) -> Response:
        headers = {
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',

        }

        params = {
            'country': 'AR',
            'language': 'portuguese',
            'currency': steam_currency,
            'item_nameid': item_name_id,
            'two_factor': '0',
        }

        if proxy_orchestrator:
            def the_request(p: Proxy) -> Response:
                return requests.get('https://steamcommunity.com/market/itemordershistogram', params=params,
                                        headers=headers, verify=False, proxies=p.getProxy(),
                                        timeout=Config.Proxying.TIME_OUT)

            return Dispatcher.dispatch_proxified(the_request, proxy_orchestrator)

        else:
            return requests.get('https://steamcommunity.com/market/itemordershistogram', params=params,
                                headers=headers)

    @staticmethod
    def ExRates_getRates():
        res = requests.get(Config.buildExRatesURL("/getExRates"))
        return json.loads(res.content)

    @staticmethod
    def ExRates_getBase():
        res = requests.get(Config.buildExRatesURL("/getBase"))
        o = json.loads(res.content)
        if "base" in o:
            return o["base"]
        else:
            raise Exception("No base retrieved")

    @staticmethod
    def ExRates_forceUpdate(base=None, currencies=None):
        payload = {}
        if base:
            payload.update({"base": base})
        if currencies:
            payload.update({"currencies": currencies})

        res = requests.post(Config.buildExRatesURL("/forceUpdate"), json=payload)
        if 200 > res.status_code >= 299:
            raise Exception(f"Não foi possível dar force update.\n {res.content}")
    @staticmethod
    def testHTTPPost(proxy_orchestrator: ProxyOrchestrator):
        def the_request(p: Proxy) -> Response:
            return requests.post('https://httpbin.org/post', json="{\"success\": true}",
                                verify=False, proxies=p.getProxy())

        return Dispatcher.dispatch_proxified(the_request, proxy_orchestrator)
    # OBSOLETE:

    # @staticmethod
    # def requestAggregatedPricesByTitle(title, limit, offset):
    #     params = {
    #         'Title': title,
    #         'Limit': limit,
    #         'Offset': offset
    #     }
    #     response = requests.get('https://api.dmarket.com/price-aggregator/v1/aggregated-prices', params=params,
    #     headers=headers)
    #     print(response.content)