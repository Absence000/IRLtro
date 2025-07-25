from subscripts.handFinderAndPointsAssigner import *
from subscripts.spectralCards import Spectral
from subscripts.saveUtils import *
from subscripts.shop import *
from subscripts.inputHandling import *

# play a specific ante in the command line
# eventually all the input lines will be replaced with actual card reading
#TODO: boss bind support
def commandLinePlayRound(save):
    deck = save.deck
    if not save.irl:
        random.shuffle(deck)
    save.hand = []

    playing = True

    while playing:

        if not save.irl:
            while len(save.hand) < 8:
                save.hand.append(deck[0])
                del deck[0]
            # automatically sorts the deck numerically
            save.hand.sort(key=lambda card: card.getValue())

        # TODO: Add the ability to resort the deck here somewhere
        print(f"{save.hands} hands left, {save.discards} discards")
        print(f"{save.score}/{save.requiredScore} chips")
        if not save.irl:
            print(f"Current hand:\n" + CLDisplayHand(save.hand))
        # print(f"{len(deck) + len()} cards")
        selectionIsValid = False
        validResponses = ["play", "discard", "use", "inv", "sell"]
        while not selectionIsValid:
            choice = input("what do you want to do now? Type \"play\" to play, \"discard\" to discard, \"use\" to use/sell "
                           "a consumable, and \"inv\" to see your consumables.")
            if choice in validResponses:
                if choice == "discard" and save.discards <= 0:
                    print("You have no discards left!")
                if not save.irl():
                    if choice == "inv":
                        printConsumables(save)
                    elif choice == "use" and len(save.consumables) == 0:
                        print("You have no consumables!")
                    else:
                        selectionIsValid = True
                if choice in ["use", "sell"]:
                    selectionIsValid = True
            else:
                print(f"Unrecognized action: {choice}")

        # consumable selection logic handling
        # TODO: Figure out how using and selling consumables can work since you should be able to do it anywhere
        if choice == "use":
            if not save.irl:
                selectionIsValid = False
                while not selectionIsValid:
                    printConsumables(save)
                    consumableSelect = input("Type the number of the consumable you want to use or sell! Type \"cancel\" "
                                             " to cancel.")
                    if consumableSelect == "cancel":
                        print("Cancelled!")
                        selectionIsValid = True
                    elif consumableSelect.isdigit() and 0 < int(consumableSelect) <= len(save.consumables):
                        consumable = save.consumables[int(consumableSelect)-1]
                        del save.consumables[int(consumableSelect)-1]
                        useConsumable(consumable, save)
                        selectionIsValid = True
            else:
                if len(selectedHand) == 1:
                    consumableToUse = selectedHand[0]
                    if isinstance(consumableToUse, Tarot):
                        useTarotCard(consumableToUse, save)
                    elif isinstance(consumableToUse, Planet):
                        useTarotCard(consumableToUse, save)
                    elif isinstance(consumableToUse, Spectral):
                        useSpectralCard(consumableToUse, save)
                    else:
                        print("You can't use a non-consumable card!")
                else:
                    print("You can't use more than one consumable at once!")

        # card selection logic handling
        if choice in ["play", "p", "discard", "d"]:
            if not save.irl:
                selectionIsValid = False
                while not selectionIsValid:
                    cardSelection = input(f"Type the card indexes that you want to {choice}, separated by commas and a space.")
                    try:
                        selectedHandIndexes = [int(num) for num in cardSelection.split(", ")]

                        # makes sure the indexes work, are <= 5 and each one is between 1 and 8 inclusive
                        if len(selectedHandIndexes) > 5:
                            print("You can't select more than 5 cards at once!")
                        elif all(1 <= index <= 8 for index in selectedHandIndexes):
                            selectionIsValid = True
                        else:
                            print("Numbers out of range!")
                    except:
                        print(f"Unrecognized hand indexes: {cardSelection}")

                selectedHand = []
                for index in selectedHandIndexes:
                    selectedHand.append(save.hand[index-1])

                # deletes in reverse order so it doesn't screw up the other indexes
                for index in sorted(selectedHandIndexes, reverse=True):
                    del save.hand[index-1]
            else:
                selectedHand = pushIRLInputIntoSave(save)
                # finds the selected hand in the deck and takes it out
                deck = [card for card in deck if card not in selectedHand + save.hand]

            if choice in ["play", "p"]:
                points, affectedCards = calcPointsFromHand(selectedHand, findBestHand(selectedHand), save.hand, save)
                # handles glass card breaking, same reverse order trick as before
                for cardIndex in range(len(selectedHand) - 1, -1, -1):
                    save.playedCards.append(selectedHand[cardIndex])
                    if selectedHand[cardIndex].enhancement == "glass":
                        if selectedHand[cardIndex].number in affectedCards or affectedCards == "all":
                            if random.randint(1, 4) == 1:
                                print(f"{selectedHand[cardIndex].toString()} broke!")
                                if save.irl:
                                    print("Put it aside and don't use it for the rest of the game!")
                                # TODO: Glass joker stuff here
                                del selectedHand[cardIndex]

                print(f"+{points} points! \n")
                save.score += points
                save.hands -= 1
                if save.score >= save.requiredScore:
                    print(f"Victory!\nScore:{save.score}")
                    # TODO: put blue seal stuff here
                    # TODO: put gold card/blue seal retriggering from mime in here
                    goldCardAmnt = 0
                    for card in save.hand:
                        if card.enhancement == "gold":
                            goldCardAmnt += 1
                            save.money += 3
                    if goldCardAmnt > 0:
                        print(f"Earned ${3 * goldCardAmnt} from {goldCardAmnt} gold cards in your hand!")
                    playing = False
                    win = True

                elif save.hands <= 0:
                    print(f"Defeat!\nScore:{save.score}")
                    playing = False
                    win = False
                else:
                    saveGame(save)

                if not playing:
                    if not save.irl:
                        # resets the deck
                        for card in save.discardedCards:
                            deck.append(card)
                        for card in save.playedCards:
                            deck.append(card)
                        for card in save.hand:
                            deck.append(card)
                        save.hand = []
                        save.playedCards = []
                        save.discardedCards = []
                    return {"win": win, "handsLeft": save.hands}
            elif choice == ["discard", "d"]:
                for discardedCard in selectedHand:
                    save.discardedCards.append(discardedCard)
                print("discarded!")
                save.discards -= 1



anteBaseChipsList = [100, 300, 800, 2000, 5000, 11000, 20000, 35000, 50000, 110000, 560000, 72000000, 300000000,
                     47000000000, 2.9E+13, 7.7E+16, 8.6E+20, 4.2E+25, 9.2E+30, 9.2E+36, 4.3E+43, 9.7E+50, 1.0E+59,
                     5.8E+67, 1.6E+77, 2.4E+87, 1.9E+98, 8.4E+109, 2.0E+122, 2.7E+135, 2.1E+149, 9.9E+163, 2.7E+179,
                     4.4E+195, 4.4E+212, 2.8E+230, 1.1E+249, 2.7E+268, 4.5E+288, 4.8E+309]

blindIndexToBlindInfo = [("Small Blind", 1, 3), ("Big Blind", 1.5, 4), ("Boss Blind", 2, 5)]

# command line version for bugfixing
# there's also an old irl mode but it's not integrated with pygame
def CLPlay(fromSave, deck, irl):
    oldSaveDict = openjson("save")
    if fromSave and oldSaveDict['state'] != "dead":
        save = createSaveFromDict(openjson("save"))
        if save.state != "selectingBlind":
            print(f"ANTE {save.ante}")
    else:
        save = createBlankSave(deck=deck, irl=irl)
    alive = True
    while alive:
        # blind select
        while save.state == "selectingBlind":
            save.blindInfo = blindIndexToBlindInfo[save.blindIndex]
            save.requiredScore = anteBaseChipsList[save.ante]*save.blindInfo[1]
            print(f"ANTE {save.ante}\n{save.blindInfo[0]}: {save.requiredScore} CHIPS")
            selectionIsValid = False
            validResponses = ["play", "skip"]
            while not selectionIsValid:
                choice = input("play or skip?")
                if choice in validResponses:
                    if choice == "skip" and save.blindInfo[0] == "Boss Blind":
                        print("You can't skip the Boss Blind!")
                    else:
                        selectionIsValid = True
                else:
                    print(f"Unrecognized action: {choice}\nType \"play\" or \"skip\"!")

            if choice == "play":
                save.state = "playing"
                save.discardedCards = []
                save.playedCards = []
                save.discards = 4
                save.hands = 4
                save.score = 0

                saveGame(save)
            if choice == "skip":
                print("skipped!")
                save.blindIndex += 1
                saveGame(save)

        # playing
        while save.state == "playing":
            roundInfo = commandLinePlayRound(save)
            if roundInfo["win"]:
                # advances to the next round
                if save.blindIndex == 2:
                    save.ante += 1
                    save.blindIndex = 0
                else:
                    save.blindIndex += 1
                baseReward = save.blindInfo[2]
                totalReward = baseReward + roundInfo['handsLeft']
                save.money += totalReward
                print(f"Rewards: ${baseReward} + {roundInfo['handsLeft']} hands left = +${totalReward}\n")
                save.state = "shop"
                save.shop = Shop(cards=[None, None], packs=[None, None], vouchers=[None], rerollCost=5)
                save.shop.rollCards(save)
                save.shop.rollPacks(save)
                saveGame(save)
            else:
                save.state = "dead"
                saveGame(save)
                alive = False
        # shopping
        while save.state == "shop":
            print(f"Money: ${save.money}")
            loadShop(save)
            save.state = "selectingBlind"
            saveGame(save)


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
                                if save.irl:
                                    prepareCardForPrinting(item)
                                    print("Print out your card in the \"print\" folder and put it on the top third of the screen!")
                                else:
                                    print("Putting your consumable into storage!")
                                    save.consumables.append(item)
                                    askingAboutImmediateUse = False
                            else:
                                print(f"Unexpected response: {useImmediately}")
                    else:
                        if save.irl:
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
                        # card selection logic
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
                                if not save.irl:
                                    save.deck.append(chosenCard)
                                    print(f"Added {chosenCard.toString()} to deck!")
                                else:
                                    prepareCardForPrinting(chosenCard)
                                    print(f"Print out your {chosenCard.toString()} in the \"print\" folder "
                                          f"and add it to the deck!")
                            elif isinstance(chosenCard, Tarot):
                                useTarotCard(chosenCard, save)
                            elif isinstance(chosenCard, Planet):
                                usePlanetCard(chosenCard, save)
                            # TODO: Joker stuff for buffoon packs
                            del possibleCards[int(cardSelection)-1]
                            cardsPicked += 1
                            if cardsPicked > cardPickAmount:
                                openingPack = False
                                if not save.irl:
                                    if item.needsHandToUse():
                                        for card in save.hand:
                                            save.deck.append(card)
                                        save.hand = []
                        else:
                            print(f"Invalid input: {cardSelection}")
                elif isinstance(item, Joker):
                    # jokers are the easiest for logic since you just add them
                    if save.irl:
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


# CLPlay(fromSave=True, deck="standard", irl=True)

# jokerDict = openjson("jokerDict")
# name = "Crazy Joker"
# joker = Joker((name, jokerDict[name]))
# card = createCardFromBinary(joker.toBinary())
# card = Card(cardDict={"number": "3", "suit": "S", "seal": "purple"})
# print(card.toString())
# print(card.toBinary())
# lookupTable = openjson("cardCreationAndRecognition/cardToArcuo.json", True)
# print(lookupTable.index(card.toBinary()))
# createTaggedCardImage(joker, openjson("cardCreationAndRecognition/cardToArcuo.json", True))

# here's some old shop CLI code in case I need it later

    # translates the displayed index of the item into the item type and true index
    # this is really dumb but idk how else to make it this nice for the CLI
    # def buyItemByItemIndex(self, itemIndex, save):
    #     # I swear this isn't in the final thing I know how much it sucks
    #     currentIndex = 1
    #     itemTypes = ["cards", "packs", "vouchers"]
    #     for itemType in itemTypes:
    #         trueIndex = 0
    #         for item in eval(f"self.{itemType}"):
    #             if currentIndex == itemIndex:
    #                 return self.buyItem(itemType, trueIndex, save)
    #             currentIndex += 1
    #             trueIndex += 1

    # returns a list of all the items in the shop without categories
    # this is just for CLI testing
    # def toList(self):
    #     shopList = []
    #     for card in self.cards:
    #         shopList.append(card)
    #     for pack in self.packs:
    #         shopList.append(pack)
    #     for voucher in self.vouchers:
    #         shopList.append(voucher)
    #     return shopList
    #
    #     # displays in the CLI
    #
    # def toString(self):
    #     itemDisplayMessage = []
    #     itemNum = 1
    #     for item in self.toList():
    #         if item is not None and item[0] is not None:
    #             itemDisplayMessage.append(f"{itemNum}: {item[0].toString()} (${item[1]})")
    #         else:
    #             itemDisplayMessage.append(f"{itemNum}: Empty slot!")
    #         itemNum += 1
    #     return ("\n".join(itemDisplayMessage))

    # def useTarotCard(card, otherCards, save):
    #     # unlike cards or jokers I can get away with using tarot card dictionaries since all this stuff is immutable for
    #     # all of them
    #     tarotCardInfo = openjson("consumables/tarotDict")[card.name]
    #     print(f"{card.toString()}")
    #
    #     # if the tarot card needs you to select cards from your hand (most of them)
    #     if tarotCardInfo["type"] == "handModifier":
    #         maxCardSelectAmount = tarotCardInfo["amnt"]
    #         # death is the only one that needs exactly two cards picked
    #         canSelectLessThanMax = True
    #         upTo = "up to "
    #         if card.name == "Death (XIII)":
    #             canSelectLessThanMax = False
    #             upTo = "exactly "
    #
    #         # makes sure the user selects the correct amount of cards plus error handling
    #         selectedHandIndexes = []
    #         selectionIsValid = False
    #         while not selectionIsValid:
    #             if not save.irl:
    #                 print(f"Your hand:\n{CLDisplayHand(save.hand)}")
    #                 cardSelection = input(f"Select {upTo}{maxCardSelectAmount} cards, separated by commas and spaces! "
    #                                       f"Type \"cancel\" to cancel.")
    #                 try:
    #                     selectedHandIndexes = [int(num) for num in cardSelection.split(", ")]
    #                     if len(selectedHandIndexes) > maxCardSelectAmount:
    #                         print(f"You can't select more than {maxCardSelectAmount} cards at once!")
    #                     elif all(1 <= index <= 8 for index in selectedHandIndexes):
    #                         if canSelectLessThanMax:
    #                             selectionIsValid = True
    #                         else:
    #                             if len(selectedHandIndexes) == maxCardSelectAmount:
    #                                 selectionIsValid = True
    #                             else:
    #                                 print(f"Select exactly {maxCardSelectAmount} cards!")
    #                     else:
    #                         print("Numbers out of range!")
    #                 except:
    #                     print(f"Unrecognized hand indexes: {cardSelection}")
    #             else:
    #                 # TODO: fix the messages so the user has time to choose
    #                 while not selectionIsValid:
    #                     cardSelection = input(f"Put {upTo}{maxCardSelectAmount}  cards in the center and type \"play\" "
    #                                           f"to select them! Type \"cancel\" to cancel.")
    #                     if cardSelection == "play":
    #
    #                         selectedHand = pushIRLInputIntoSave(save)
    #                         if len(selectedHand) > maxCardSelectAmount:
    #                             print(f"You can't select more than {maxCardSelectAmount} cards at once!")
    #                         elif canSelectLessThanMax:
    #                             selectionIsValid = True
    #                         else:
    #                             if len(selectedHand) == maxCardSelectAmount:
    #                                 selectionIsValid = True
    #                             else:
    #                                 print(f"Select exactly {maxCardSelectAmount} cards!")
    #
    #         # I know this is a really shitty way of handling irl vs command line playing but who cares lmao
    #
    #         # suit converters (star, moon, sun, world)
    #         if tarotCardInfo["modifier"] == "suit":
    #             if save.irl:
    #                 clearPrintFolder()
    #                 for card in selectedHand:
    #                     card.suit = tarotCardInfo["suit"]
    #                     prepareCardForPrinting(card, keep=True)
    #                 print("Print out the cards in the \"print\" folder, and replace the current cards with them!")
    #
    #             else:
    #                 for index in selectedHandIndexes:
    #                     save.hand[index - 1].suit = tarotCardInfo["suit"]
    #
    #         # enhancer converters (magician, empress, hierophant, lovers, chariot, justice, devil, tower)
    #         elif tarotCardInfo["modifier"] == "enhancer":
    #             if save.irl:
    #                 clearPrintFolder()
    #                 for card in selectedHand:
    #                     card.enhancement = tarotCardInfo["enhancement"]
    #                     prepareCardForPrinting(card, keep=True)
    #                 print("Print out the cards in the \"print\" folder, and replace the current cards with them!")
    #
    #             else:
    #                 for index in selectedHandIndexes:
    #                     save.hand[index - 1].enhancement = tarotCardInfo["enhancement"]
    #
    #         # rank converter (strength)
    #         elif tarotCardInfo["modifier"] == "rank":
    #             if save.irl:
    #                 clearPrintFolder()
    #                 for card in selectedHand:
    #                     card.number = increaseCardVal(card.number)
    #                     prepareCardForPrinting(card, keep=True)
    #                 print("Print out the cards in the \"print\" folder, and replace the current cards with them!")
    #
    #             else:
    #                 for index in selectedHandIndexes:
    #                     save.hand[index - 1].number = increaseCardVal(save.hand[index - 1].number)
    #
    #         # destroy converter (hanged man)
    #         elif tarotCardInfo["modifier"] == "destroy":
    #             if save.irl:
    #                 print("Put the selected cards off to the side and don't use them for the rest of the game!")
    #             else:
    #                 for index in selectedHandIndexes:
    #                     del save.hand[index - 1]
    #
    #         # convert converter (death)
    #         elif tarotCardInfo["modifier"] == "convert":
    #             if save.irl:
    #                 prepareCardForPrinting(selectedHand[1])
    #                 print("Print out the card in the \"print\" folder, and replace the left card with it!")
    #
    #             else:
    #                 save.hand[selectedHandIndexes[0]] = save.hand[selectedHandIndexes[1]]
    #
    #         print(f"Success! New hand:\n{CLDisplayHand(save.hand)}")