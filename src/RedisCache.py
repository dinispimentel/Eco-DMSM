
import hashlib

import redis

from src.config import Config

r = redis.Redis(host=Config.Redis.HOST, port=Config.Redis.PORT)


class RedisCache:

    @staticmethod
    def __hash_it(txt):
        return hashlib.sha1(str(txt).encode("utf-8")).hexdigest()

    @staticmethod
    def saveItemNameIDs(mapping_unhashed: dict):
        # mapping_unhashed = {title => item_name_id}
        if not mapping_unhashed or len(mapping_unhashed.keys()) < 1:

            return
        hashed_map = dict()

        for k, v in mapping_unhashed.items():
            hashed_map.update({RedisCache.__hash_it(k): str(v)})

        r.mset(hashed_map)

    @staticmethod
    def getItemNameID(title: str):
        inid = r.get(RedisCache.__hash_it(title))
        if inid:
            return inid.decode('utf-8')
        else:
            return None



