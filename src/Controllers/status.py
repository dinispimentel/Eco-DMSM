import time

from . import BasicController


class Status(BasicController.BasicController):
    from src.routing import Router
    @staticmethod
    def GET(R: Router, jbody: dict = None):
        return R.write_response(f'{R.RH.DMData.status} | {R.RH.DMData.locked}')


