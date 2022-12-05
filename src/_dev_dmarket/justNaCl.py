import json
from datetime import datetime

from nacl.bindings import crypto_sign

with open("../secret.json", "r") as f:
    ENV = json.loads(f.read())

a = "/price-aggregator/v1/aggregated-prices?Titles=%22USP-S%22&Limit=10&Offset=%220%22"
method = "GET"
nonce = str(round(datetime.now().timestamp()))

string_to_sign = method + a + "&" + nonce
signature_prefix = "dmar ed25519 "
encoded = string_to_sign.encode('utf-8')
public_key = ENV["DMARKET_API_KEYS"]["PUBLIC"]
secret_key = ENV["DMARKET_API_KEYS"]["PRIVATE"]
print(f'Public {public_key}\nPrivate {secret_key}\n')
secret_bytes = bytes.fromhex(secret_key)

signature_bytes = crypto_sign(encoded, bytes.fromhex(secret_key))
signature = signature_bytes[:64].hex()
print(signature)
print(nonce)