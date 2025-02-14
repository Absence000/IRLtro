from subscripts.cardUtils import Card


# TODO: add cost for joker rarities, playing cards, tarot, spectral, and vouchers
def calculatePrice(item, save):
    if type(item) == Card:
        if item.subset == "planet":
            return 3
