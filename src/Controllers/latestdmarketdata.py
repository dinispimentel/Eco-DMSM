import json

from src.routing import Router
from .BasicController import BasicController


class LatestDMarketData (BasicController):

    @staticmethod
    def GET(R: Router, **kwargs):
        R.write_response(json.dumps({"success": True, "msg": R.RH.DMData.lastUpdate}))
