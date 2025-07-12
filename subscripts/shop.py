from subscripts.inputHandling import *
from subscripts.planetCards import *
from subscripts.consumableCards import *
from subscripts.priceCalcLogic import calculatePrice
from subscripts.packs import Pack, generatePackForSale
from subscripts.cardUtils import Card, generateWeightedRandomCard
from subscripts.tarotCards import useTarotCard, Tarot
from subscripts.inputHandling import CLDisplayHand
from subscripts.jokers import generateRandomWeightedJoker, generateShuffledListOfFinishedJokersByRarity, Joker

# TODO: add something for the voucher to remain the same until the Boss Blind is defeated
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
            packForSale = generatePackForSale()
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
            if item is not None and item[0] is not None:
                itemDisplayMessage.append(f"{itemNum}: {item[0].toString()} (${item[1]})")
            else:
                itemDisplayMessage.append(f"{itemNum}: Empty slot!")
            itemNum += 1
        return ("\n".join(itemDisplayMessage))

    def toDict(self):
        cardList = []
        for subCardList in self.cards:
            if subCardList is not None and subCardList[0] is not None:
                cardList.append([subCardList[0].toDict(), subCardList[1]])
            else:
                cardList.append([None, None])
        packList = []
        for subPackList in self.packs:
            if subPackList is not None and subPackList[0] is not None:
                packList.append([subPackList[0].toDict(), subPackList[1]])
            else:
                packList.append([None, None])
        # TODO: Put vouchers here too
        return {
            "cards": cardList,
            "packs": packList,
            "vouchers": [None],
            "rerollCost": self.rerollCost
        }

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
        if listing is not None:
            if save.money >= listing[1]:
                # checks if they have enough room
                item = listing[0]
                if isinstance(item, Joker):
                    if item.edition == "Negative" or len(save.jokers) < save.jokerLimit:
                        save.money -= listing[1]
                        eval(f"self.{type}")[trueIndex] = None
                        return item
                    return "Not enough space"
                elif isinstance(item, Pack):
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
    for subCardList in shopDict["cards"]:
        if subCardList is not None and subCardList[0] is not None:
            #TODO: Add support for spectrals and playing cards here since you can buy them with the voucher
            cardData = subCardList[0]
            if "type" not in cardData:
                newCard = Joker(cardData)
            elif cardData["type"] == "planet":
                newCard = Planet(cardData["name"], cardData["negative"])
            elif cardData["type"] == "tarot":
                newCard = Tarot(cardData["name"], cardData["negative"])
            cardList.append([newCard, subCardList[1]])
        else:
            cardList.append([None, None])
    packList = []
    for subPackList in shopDict["packs"]:
        packInfo = subPackList[0]
        if packInfo is not None:
            packList.append([Pack(packInfo["subset"], packInfo["size"]), subPackList[1]])
        else:
            packList.append([None, None])
    # TODO: Put vouchers here too
    return Shop(cardList, packList, [None], shopDict["rerollCost"])

def loadShop(save):
    from subscripts.saveUtils import saveGame
    buying = True
    while buying:
        print("SHOP:")
        print(save.shop.toString())
        print(f"Reroll: ${save.shop.rerollCost}")
        buyChoice = input("Type the number of the item you want to buy! Type 'inv' to see your consumables, 'use' to use/sell your consumables, 'reroll' to reroll, and 'exit' to leave!")
        if buyChoice == "exit":
            buying = False
        elif buyChoice.isdigit() and 1 <= int(buyChoice) <= len(save.shop.toList()):
            item = save.shop.buyItemByItemIndex(int(buyChoice), save)
            if item == "Can't afford":
                print("You don't have enough money!")
            elif item == "Slot is empty":
                print("That slot is empty!")
            elif item == "Not enough space":
                print("You don't have enough space!")
            else:
                print("Bought " + item.toString() + "!")
                # if it's consumable it asks if it wants to use it immediately or put it into the consumables slot
                if newItemIsConsumable(item):
                    if consumableCanBeUsedImmediately(item):
                        if len(save.consumables) >= save.consumablesLimit:
                            print("You have no space for this consumable! Using now!")
                            useConsumable(item, save)
                            askingAboutImmediateUse = False
                        else:
                            askingAboutImmediateUse = True
                        while askingAboutImmediateUse:
                            useImmediately = input("Do you want to use this immediately? Type \"y\" or \"n\".")
                            if useImmediately == "y":
                                useConsumable(item, save)
                                askingAboutImmediateUse = False
                            elif useImmediately == "n":
                                if playingIRL(save):
                                    prepareCardForPrinting(item)
                                    print("Print out your card in the \"print\" folder and put it on the top third of the screen!")
                                else:
                                    print("Putting your consumable into storage!")
                                    save.consumables.append(item)
                                    askingAboutImmediateUse = False
                            else:
                                print(f"Unexpected response: {useImmediately}")
                    else:
                        if playingIRL(save):
                            prepareCardForPrinting(item)
                            print("Print out your card in the \"print\" folder "
                                  "and put it on the top third of the screen!")
                        else:
                            print("Putting your consumable into storage!")
                            save.consumables.append(item)
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
                                save.hand.append(save.deck[0])
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
                            if isinstance(chosenCard, Card):
                                if not playingIRL(save):
                                    save.deck.append(chosenCard)
                                    print(f"Added {chosenCard.toString()} to deck!")
                                else:
                                    clearPrintFolder()
                                    createTaggedCardImage(chosenCard,
                                                          openjson(
                                                              "cardCreationAndRecognition/cardToArcuo old.json",
                                                              True))
                                    print(f"Print out your {chosenCard.toString()} in the \"print\" folder "
                                          f"and add it to the deck!")
                            elif isinstance(chosenCard, Tarot):
                                useTarotCard(chosenCard, save)
                            elif isinstance(chosenCard, Planet):
                                usePlanetCard(chosenCard, save)
                            del possibleCards[int(cardSelection)-1]
                            cardsPicked += 1
                            if cardsPicked > cardPickAmount:
                                openingPack = False
                                if not playingIRL(save):
                                    if item.needsHandToUse():
                                        for card in save.hand:
                                            save.deck.append(card)
                                        save.hand = []
                        else:
                            print(f"Invalid input: {cardSelection}")
                elif isinstance(item, Joker):
                    # jokers are the easiest for logic since you just add them
                    if playingIRL(save):
                        prepareCardForPrinting(item)
                        print("Print out the joker in the \"print\" folder and put it in the top third of the screen!")
                    else:
                        save.jokers.append(item)

                print(f"New Balance: ${save.money}")
                saveGame(save)
        elif buyChoice == "reroll":
            if save.money >= save.shop.rerollCost:
                save.shop.rollCards(save)
                save.money -= save.shop.rerollCost
                save.shop.rerollCost += 1
                print("Shop rerolled!")
                print(f"New Balance: ${save.money}")
                saveGame(save)
            else:
                print(f"You don't have enough money! ({save.money})")

        elif buyChoice == "inv":
            printConsumables(save)
        elif buyChoice == "use":
            # TODO: Move this to another function since I use this a lot with slight differences
            selectionIsValid = False
            while not selectionIsValid:
                printConsumables(save)
                consumableSelect = input("Type the number of the consumable you want to use or sell! Type \"cancel\" "
                                         " to cancel.")
                if consumableSelect == "cancel":
                    print("Cancelled!")
                    selectionIsValid = True
                elif consumableSelect.isdigit() and 0 < int(consumableSelect) <= len(save.consumables):
                    consumable = save.consumables[int(consumableSelect) - 1]
                    del save.consumables[int(consumableSelect) - 1]
                    useConsumable(consumable, save)
                    selectionIsValid = True
        else:
            print(f"invalid input: {buyChoice}")

    # TODO: add credit card joker support in the price cost calculation



# TODO: add weighted choice: joker (20), tarot(4), planet(4)
def generateCardForSale(save):
    options = ["tarot", "planet", "joker"]
    weights = [4, 4, 20]

    cardType = random.choices(options, weights)[0]
    return generateWeightedRandomCard(cardType, save)

# if the item is consumable it asks if the player wants to use it right away or not
def newItemIsConsumable(item):
    if isinstance(item, Card):
        return False
    if isinstance(item, Planet) or isinstance(item, Tarot): # TODO: When spectrals are added put them here
        return True
    return False

# consumables that need a hand to work can't be used immediately
# TODO: make this work for spectrals when they're added
def consumableCanBeUsedImmediately(consumable):
    if isinstance(consumable, Tarot):
        if openjson("consumables/tarotDict")[consumable.name]["type"] == "handModifier":
            return False
    return True
