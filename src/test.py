from src.dispatcher import Dispatcher



res = Dispatcher.requestAllDMarketItems(
    gameId="a8db",
    limit=50000,
    offset="0",
    orderBy="best_discount",
    orderDir="desc",
    currency="USD",
    priceFrom=1*100,
    priceTo=100*100
)

print(res.status_code)


with open("cache/allDMarketItems.json", "wb") as f:
    f.write(res.text.encode("utf-8"))

# Dispatcher.requestAggregatedPricesByTitle(“AWP Fever Dream", 10, "+20$")

