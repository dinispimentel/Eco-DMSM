from Models.DMOfferBook import OfferBook


ob = OfferBook.loadFromCache(testing=False)
ob.print()
ob.printOffers()
