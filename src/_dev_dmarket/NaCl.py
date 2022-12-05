import datetime
import json

import requests
from nacl.bindings import crypto_sign

rootApiUrl = "https://api.dmarket.com"

with open("../secret.json", "r") as f:
    ENV = json.loads(f.read())

nonce = str(round(datetime.datetime.now().timestamp()))
# nonce = "1667666371"
api_url_path = "/price-aggregator/v1/aggregated-prices"
method = "GET"


with open("../../reqbody.json", "r") as f:
    # body = json.loads(f.read())
    pass
body = None
requestStr = api_url_path + "?" + \
                 'Titles=USP-S&Limit=10&Offset=0'
string_to_sign = method + requestStr + "&" + nonce
signature_prefix = "dmar ed25519 "
encoded = string_to_sign.encode('utf-8')
public_key = ENV["DMARKET_API_KEYS"]["PUBLIC"]
secret_key = ENV["DMARKET_API_KEYS"]["PRIVATE"]
print(f'Public {public_key}\nPrivate {secret_key}\n')
secret_bytes = bytes.fromhex(secret_key)

signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
signature = signature_bytes[:64].hex()

print(nonce)
print(string_to_sign)
headers = {
    "X-Api-Key": public_key,
    "X-Request-Sign": signature_prefix + signature,
    "X-Sign-Date": nonce
}

resp = requests.get(rootApiUrl + requestStr, json=body, headers=headers)
print(resp.status_code)
print(resp.text)
print(rootApiUrl + requestStr)
print(signature_prefix + signature)

