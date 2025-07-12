from subscripts.tarotCards import Tarot
from subscripts.planetCards import Planet
from subscripts.packs import Pack
from subscripts.jokers import Joker


priceDict = {
    "pack": {"normal": 4, "jumbo": 6, "mega": 8}
}

# TODO: add cost for joker rarities, playing cards, tarot, spectral, and vouchers
# TODO: add the sale voucher thing
def calculatePrice(item, save):
    if type(item) in [Planet, Tarot]:
        return 3
    elif type(item) == Pack:
        return priceDict["pack"][item.size]
    elif type(item) == Joker:
        return item.cost
