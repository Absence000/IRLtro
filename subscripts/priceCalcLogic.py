from subscripts.cardUtils import Card
from subscripts.packs import Pack


priceDict = {
    "pack": {"normal": 4, "jumbo": 6, "mega": 8}
}

# TODO: add cost for joker rarities, playing cards, tarot, spectral, and vouchers
# TODO: add the sale voucher thing
def calculatePrice(item, save):
    if type(item) == Card:
        if item.subset == "planet":
            return 3
    if type(item) == Pack:
        return priceDict["pack"][item.size]

