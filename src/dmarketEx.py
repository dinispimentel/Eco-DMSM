import json
from datetime import datetime

import requests
from nacl.bindings import crypto_sign

from .config import Config

public_key = Config.DMarket.APIKeys.PUBLIC
secret_key = Config.DMarket.APIKeys.PRIVATE

# change url to prod
rootApiUrl = "https://api.dmarket.com"


def __format_query_params(params: dict):
    s = "?"
    for key, value in params.items():
        s += key + "=" + str(value) + "&"
    return "" if s == "?" else ((s[0:len(s)-1]) if s[-1] == '&' else s)


def dmarketRequest(method, route, query_params, body: dict or None = None):

    nonce = str(round(datetime.now().timestamp()))
    # api_url_path = "/exchange/v1/target/create"
    # method = "POST"
    formated_query = __format_query_params(query_params)

    string_to_sign = method + route + formated_query + ("" if not body else json.dumps(body)) + nonce
    signature_prefix = "dmar ed25519 "
    encoded = string_to_sign.encode('utf-8')
    secret_bytes = bytes.fromhex(secret_key)
    signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
    signature = signature_bytes[:64].hex()
    headers = {
        "X-Api-Key": public_key,
        "X-Request-Sign": signature_prefix + signature,
        "X-Sign-Date": nonce
    }
    resp = None

    if method == "POST":
        resp = requests.post(rootApiUrl + route, json=body, headers=headers)
    elif method == "GET":
        resp = requests.get(rootApiUrl + route + formated_query, headers=headers)
    elif method == "PUT":
        resp = requests.put(rootApiUrl + route, json=body, headers=headers)
    return resp





# def get_offer_from_market():
#     market_response = requests.get(rootApiUrl + "/exchange/v1/market/items?gameId=a8db&limit=1&currency=USD")
#     offers = json.loads(market_response.text)["objects"]
#     return offers[0]
#
#
# def build_target_body_from_offer(offer):
#     return {"targets": [
#         {"amount": 1, "gameId": offer["gameId"], "price": {"amount": "2", "currency": "USD"},
#          "attributes": {"gameId": offer["gameId"],
#                         "categoryPath": offer["extra"]["categoryPath"],
#                         "title": offer["title"],
#                         "name": offer["title"],
#                         "image": offer["image"],
#                         "ownerGets": {"amount": "1", "currency": "USD"}}}
#     ]}

# dmarketRequest("GET", "/exchange/v1/market/items",
#                {
#                    "gameId": "a8db",
#                    "limit": 50,
#                    "offset": 0,
#                    "orderBy": "price",
#                    "orderDir": "asc",
#                    "currency": "USD",
#                    "priceFrom": 0,
#                    "priceTo": 20000,
#                })


# dmarketRequest("GET", "/price-aggregator/v1/aggregated-prices",
#                {
#                    "Titles": ["USP - Whiteout"]
#                })

# dmarketRequest("POST", "/exchange/v1/target/create",
#                {}, body=build_target_body_from_offer(get_offer_from_market()))
