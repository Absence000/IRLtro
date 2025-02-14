from operator import truediv

from subscripts.planetCards import *
from subscripts.saveUtils import *
from subscripts.consumableCards import *

class Shop:

    def __init__(self, cards, boosters, vouchers):
        self.cards = cards
        self.boosters = boosters
        self.vouchers = vouchers

    def rollCards(self, save):
        cardList = []
        for i in range(2):
            cardForSale = generateCardForSale(save)
            price = calculatePrice(cardForSale, save)
            cardList.append([cardForSale, price])
        self.cards = cardList

    # returns a list of all the items in the shop without categories
    def toList(self):
        shopList = []
        for card in self.cards:
            shopList.append(card)
        for booster in self.boosters:
            shopList.append(booster)
        for voucher in self.vouchers:
            shopList.append(voucher)
        return shopList

    # displays in the CLI
    def toString(self):
        itemDisplayMessage = []
        itemNum = 1
        for item in self.toList():
            if item is not None:
                itemDisplayMessage.append(f"{itemNum}: {item[0].toString()} (${item[1]})")
            else:
                itemDisplayMessage.append(f"{itemNum}: Empty slot!")
            itemNum += 1
        return ("\n".join(itemDisplayMessage))

    # translates the displayed index of the item into the item type and true index
    # this is really dumb but idk how else to make it this nice for the CLI
    def buyItemByItemIndex(self, itemIndex, save):
        # I know this is a super shitty way to figure out which item it is by the index but this is just for the CLI
        currentIndex = 1
        itemTypes = ["cards", "boosters", "vouchers"]
        for itemType in itemTypes:
            trueIndex = 0
            for item in eval(f"self.{itemType}"):
                if currentIndex == itemIndex:
                    return self.buyItem(itemType, trueIndex, save)
                currentIndex += 1
                trueIndex += 1

    # returns the item, removes it from the shop, and subtracts the money if the user can afford it
    # returns False and does nothing if it can't afford it
    def buyItem(self, type, trueIndex, save):
        listing = eval(f"self.{type}")[trueIndex]
        if listing != None:
            if save.money >= listing[1]:
                save.money -= listing[1]
                item = listing[0]
                eval(f"self.{type}")[trueIndex] = None
                return item
            else:
                return "Can't afford"
        return "Slot is empty"

def loadShop(save):
    shop = Shop(cards=[None, None], boosters=[None, None], vouchers=[None])
    shop.rollCards(save)
    buying = True
    while buying:
        print("SHOP:")
        print(shop.toString())
        buyChoice = input("Type the number of the item you want to buy! Type 'none' to buy nothing!")
        if buyChoice == "none":
            buying = False
        elif buyChoice.isdigit() and 1 <= int(buyChoice) <= len(shop.toList()):
            item = shop.buyItemByItemIndex(int(buyChoice), save)
            if item == "Can't afford":
                print("You don't have enough money!")
            elif item == "Slot is empty":
                print("That slot is empty!")
            else:
                print("Bought " + item.toString() + "!")
                # if it's consumable it asks if it wants to use it immediately or put it into the consumables slot
                if newItemIsConsumable(item):
                    if consumableCanBeUsedImmediately(item):
                        if len(save.consumables) >= save.consumablesLimit:
                            print("You have no space for this consumable! Do you want to use it now?")
                            useConsumable(item, save)
                            askingAboutImmediateUse = False
                        else:
                            askingAboutImmediateUse = True
                        while askingAboutImmediateUse:
                            useImmediately = input("Do you want to use this immediately? Type \"y\" or \"n\".")
                            validResponses = ["y", "n"]
                            if useImmediately == "y":
                                useConsumable(item, save)
                                askingAboutImmediateUse = False
                            elif useImmediately == "n":
                                print("Putting your consumable into storage!")
                                save.consumables.append(item)
                                askingAboutImmediateUse = False
                            else:
                                print(f"Unexpected response: {useImmediately}")
                print(f"New Balance: ${save.money}")
        else:
            print(f"invalid input: {buyChoice}")

    # TODO: add credit card joker support in the price cost calculation



# TODO: only works with planet cards, add weighted choice: joker (20), tarot(4), planet(4)
def generateCardForSale(save):
    return generateShuffledListOfUnlockedPlanetCards(save)[0]


# TODO: add cost for joker rarities, playing cards, tarot, spectral, and vouchers
def calculatePrice(item, save):
    if type(item) == Card:
        if item.subset == "planet":
            return 3


# if the item is consumable it asks if the player wants to use it right away or not
def newItemIsConsumable(item):
    if isinstance(item, Card):
        if item.subset in ["planet", "tarot", "spectral"]:
            return True
    return False

# consumables that need a hand to work can't be used immediately
# TODO: make this work for non-planets
def consumableCanBeUsedImmediately(item):
    return True