import random
from http.server import BaseHTTPRequestHandler

from .Models.DMData import DMData
from .Models.ProxyOrchestrator import ProxyOrchestrator
from .proxies import PROXIES_SOCKS5

PERSISTENT_DATA = {}
PROXIES = PROXIES_SOCKS5
random.shuffle(PROXIES)


class DPHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, dmdata, PO, *args, **kwargs):
        from .routing import Router
        # self.dmarket_data_update_timestamp = getPersistantData().get('dmarket_data_update_timestamp')
        # self.current_status = getPersistantData().get('c') or "inited"
        from src.Models.DMOfferBook import OfferBook
        self.DMData: DMData = dmdata
        # self.PO = getPersistantData().get('PO') or ProxyOrchestrator.build_from_raw(PROXIES,
        #                                                                             method='socks5')
        self.PO: ProxyOrchestrator = PO
        self.router = Router(self)
        # self.setPersistantData = setPersistantData
        # self.getPersistantData = getPersistantData
        super().__init__(*args, **kwargs)



    def do_GET(self):
        self.router.GET()
        # self.setPersistantData(self.__dict__)

    # {skin: "<nome da skin>"}
    def do_POST(self):
        self.router.POST()
        # self.setPersistantData(self.__dict__)

    def do_PATCH(self):
        self.router.PATCH()

ERRORS = {
    "null_json": {"success": False, "msg": "The JSON received did not contain the required params."},
    "internal_error": {"success": False, "msg": "Internal error occurred"},
    "data_locked": {"success": False, "msg": "Data is locked."},
    "offer_book_missing_flag": {"success": False,
                                "msg": "Internal OfferBook can't proceed to this action (Missing Flags)."},
    "offer_book_currency_mismatch": {"success": False, "msg": "One of the currencies is not equal to the other.\n"
                                                              "Please Convert:"},
    "bad_params": {"success": False, "msg": "Bad params."}
}
SUCCESSES = {
    "action_succeded": {"success": True, "msg": "Action performed successfuly."}
}
