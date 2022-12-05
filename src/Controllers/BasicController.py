from __future__ import annotations

from abc import abstractmethod
from typing import List, Dict, Type, Tuple, Iterable

from ecolib.utils import Utils


class BasicController:
    from ..routing import Router

    @staticmethod
    @abstractmethod
    def GET(R: Router, **kwargs):
        print("Not implemented.")


    @staticmethod
    @abstractmethod
    def POST(R: Router, **kwargs):
        print("Not implemented.")

    @staticmethod
    def PATCH(R: Router, **kwargs):
        print("Not implemented.")

    @staticmethod
    @abstractmethod
    def getRequiredParams() -> Dict[str, Type | Tuple]:
        pass


    @classmethod
    def getRequiredOnlyKVPairs(cls, jbody: dict):
        req_kv = {}
        for rk in cls.getRequiredParams():
            req_kv.update({rk: jbody[rk]})
        return req_kv

    @classmethod
    def check_params_missing(cls, jbody: Dict) -> list:

        p_t = cls.getRequiredParams()
        p = list(p_t.keys())
        if jbody is not None:
            jp = list(jbody.keys())
        else:
            jp = []

        return Utils.a_minus_b(p, jp)

    @classmethod
    def check_param_type(cls, jbody: Dict) -> List[Tuple[str, Type, List[Type]]]:

        req_kv = cls.getRequiredOnlyKVPairs(jbody)
        type_dict = cls.getRequiredParams()
        bad_params = []

        for k, v in req_kv.items():
            # Retorna a Lista de Tuplas (param_errored_str, param_errored_supossed_type)

            if not isinstance(v, type_dict.get(k)):
                bad_params.append((k, type(v), (type_dict.get(k) if isinstance(type_dict.get(k), Iterable)
                                                else [type_dict.get(k)])))

        return bad_params
