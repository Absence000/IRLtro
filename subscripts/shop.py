from operator import truediv

from subscripts.planetCards import *
from subscripts.saveUtils import *
from subscripts.consumableCards import *
from subscripts.priceCalcLogic import calculatePrice
from subscripts.packs import Pack, generatePackForSale
from subscripts.cardUtils import Card, createCardFromDict, CLDisplayHand, generateShuffledListOfUnlockedPlanetCards, \
    generateWeightedRandomCard
from subscripts.tarotCards import useTarotCard


#TODO: add something for the voucher to remain the same until the Boss Blind is defeated
class Shop:

    def __init__(self, cards, packs, vouchers, rerollCost):
        self.cards = cards
        self.packs = packs
        self.vouchers = vouchers
        self.rerollCost = rerollCost

    def rollCards(self, save):
        cardList = []
        for i in range(2):
            cardForSale = generateCardForSale(save)
            price = calculatePrice(cardForSale, save)
            cardList.append([cardForSale, price])
        self.cards = cardList

    def rollPacks(self, save):
        packList = []
        for i in range(2):
            packForSale =generatePackForSale()
            price = calculatePrice(packForSale, save)
            packList.append([packForSale, price])
        self.packs = packList


    # returns a list of all the items in the shop without categories
    def toList(self):
        shopList = []
        for card in self.cards:
            shopList.append(card)
        for pack in self.packs:
            shopList.append(pack)
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
        itemTypes = ["cards", "packs", "vouchers"]
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
    shop = Shop(cards=[None, None], packs=[None, None], vouchers=[None], rerollCost=5)
    shop.rollCards(save)
    shop.rollPacks(save)
    buying = True
    while buying:
        print("SHOP:")
        print(shop.toString())
        print(f"Reroll: ${shop.rerollCost}")
        buyChoice = input("Type the number of the item you want to buy! Type 'reroll' to reroll, and 'exit' to leave!")
        if buyChoice == "exit":
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
                # pack
                elif isinstance(item, Pack):
                    possibleCards = item.open(save)
                    cardPickAmount = 1
                    if item.size == "mega":
                        cardPickAmount = 2
                    cardsPicked = 1
                    openingPack = True
                    print("Cards:")
                    while openingPack:
                        if item.needsHandToUse():
                            while len(save.hand) < 8:
                                save.hand.append(createCardFromDict(save.deck[0]))
                                del save.deck[0]
                            print(f"Hand:\n{CLDisplayHand(save.hand)}")
                        iterator = 1
                        for card in possibleCards:
                            print(f"{iterator}: {card.toString()}")
                            iterator += 1
                        cardSelection = input(f"Pick {cardsPicked}/{cardPickAmount} cards! Type \"skip\" to skip!")
                        if cardSelection  == "skip":
                            openingPack = False
                            print("Pack skipped!")
                        elif cardSelection.isdigit() and 0 < int(cardSelection) <= len(possibleCards):
                            chosenCard = possibleCards[int(cardSelection)-1]
                            # TODO: Move this to a separate function once I have all the other card stuff
                            if chosenCard.subset == "playing":
                                save.deck.append(chosenCard.toDict())
                                print(f"Added {chosenCard.toString()} to deck!")
                            elif chosenCard.subset == "tarot":
                                useTarotCard(chosenCard, save)
                            del possibleCards[int(cardSelection)-1]
                            cardsPicked += 1
                            if cardsPicked > cardPickAmount:
                                openingPack = False
                                if item.needsHandToUse():
                                    for card in save.hand:
                                        save.deck.append(card.toDict())
                                    save.hand = []

                        else:
                            print(f"Invalid input: {cardSelection}")


                print(f"New Balance: ${save.money}")
        elif buyChoice == "reroll":
            if save.money >= shop.rerollCost:
                shop.rollCards(save)
                save.money -= shop.rerollCost
                shop.rerollCost += 1
                print("Shop rerolled!")
                print(f"New Balance: ${save.money}")
            else:
                print(f"You don't have enough money! ({save.money})")

        else:
            print(f"invalid input: {buyChoice}")

    # TODO: add credit card joker support in the price cost calculation



# TODO: add weighted choice: joker (20), tarot(4), planet(4)
def generateCardForSale(save):
    options = ["tarot", "planet"]
    weights = [4, 4]

    cardType = random.choices(options, weights)[0]
    return generateWeightedRandomCard(cardType, save)

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