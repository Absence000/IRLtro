from subscripts.inputHandling import *
from subscripts.planetCards import *
from subscripts.consumableCards import *
from subscripts.priceCalcLogic import calculatePrice
from subscripts.packs import Pack, generatePackForSale
from subscripts.cardUtils import generateWeightedRandomCards
from subscripts.tarotCards import Tarot
from subscripts.jokers import Joker
from subscripts.spectralCards import Spectral


class ShopItem:
    def __init__(self, item, price):
        self.item = item
        self.price = price

    def toList(self):
        return [self.item.toDict(), self.price]


# TODO: add something for the voucher to remain the same until the Boss Blind is defeated
class Shop:
    def __init__(self, cards, packs, vouchers, rerollCost):
        self.cards = cards
        self.packs = packs
        self.vouchers = vouchers
        self.rerollCost = rerollCost
        self.images = {}

    def rollCards(self, save):
        cardList = []
        for i in range(2):
            cardForSale = generateCardForSale(save)
            price = calculatePrice(cardForSale, save)
            cardList.append(ShopItem(cardForSale, price))
        self.cards = cardList

    def rollPacks(self, save):
        # TODO: First shop has a guaranteed buffoon pack
        packList = []
        for i in range(2):
            packForSale = generatePackForSale()
            price = calculatePrice(packForSale, save)
            packList.append(ShopItem(packForSale, price))
        self.packs = packList

    def toDict(self):
        cardList = []
        for cardForSale in self.cards:
            if cardForSale is not None:
                cardList.append(cardForSale.toList())
            else:
                cardList.append(None)
        packList = []
        for packForSale in self.packs:
            if packForSale is not None:
                packList.append(packForSale.toList())
            else:
                packList.append(None)
        # TODO: Put vouchers here too
        return {
            "cards": cardList,
            "packs": packList,
            "vouchers": [None],
            "rerollCost": self.rerollCost
        }

    # returns the item, removes it from the shop, and subtracts the money if the user can afford it
    # returns an error message and does nothing if it can't afford it
    # if I do this by item instead of index then shop duplicates won't work
    def buyItem(self, type, trueIndex, save):
        listing = eval(f"self.{type}")[trueIndex]
        if listing is not None:
            item = listing.item
            price = listing.price
            if save.money >= listing.price:
                # checks if they have enough room
                if isinstance(item, Joker):
                    if item.edition == "Negative" or len(save.jokers) < save.jokerLimit:
                        save.money -= price
                        eval(f"self.{type}")[trueIndex] = None
                        return item
                    return "Not enough space"
                elif isinstance(item, Pack):
                    save.money -= price
                    eval(f"self.{type}")[trueIndex] = None
                    return item
                elif newItemIsConsumable(item):
                    if consumableCanBeUsedImmediately(item):
                        eval(f"self.{type}")[trueIndex] = None
                        return item
                    elif len(save.consumables) < save.consumablesLimit:
                        eval(f"self.{type}")[trueIndex] = None
                        return item
                    else:
                        return "Not enough space"
            else:
                return "Can't afford"
        return "Slot is empty"

def createShopFromDict(shopDict):
    cardList = []
    for cardForSale in shopDict["cards"]:
        #TODO: Add support for spectrals and playing cards here since you can buy them with the voucher
        cardData = cardForSale[0]
        if cardData is not None:
            if "type" not in cardData:
                newCard = Joker(cardData)
            elif cardData["type"] == "Planet":
                newCard = Planet(cardData["name"], cardData["negative"])
            elif cardData["type"] == "Tarot":
                newCard = Tarot(cardData["name"], cardData["negative"])
            cardList.append(ShopItem(newCard, cardForSale[1]))
        else:
            cardList.append(None)

    packList = []
    for packForSale in shopDict["packs"]:
        packInfo = packForSale[0]
        if packInfo is not None:
            packList.append(ShopItem(Pack(packInfo["subset"], packInfo["size"]), packForSale[1]))
        else:
            packList.append(None)
    # TODO: Put vouchers here too
    return Shop(cardList, packList, [None], shopDict["rerollCost"])


# TODO: a bunch of voucher code goes here
def generateCardForSale(save):
    options = ["tarot", "planet", "joker"]
    weights = [4, 4, 20]

    cardType = random.choices(options, weights)[0]
    return generateWeightedRandomCards(cardType, save, 1)[0]

# if the item is consumable it asks if the player wants to use it right away or not
def newItemIsConsumable(item):
    if isinstance(item, Planet) or isinstance(item, Tarot) or isinstance(item, Spectral):
        return True
    return False
