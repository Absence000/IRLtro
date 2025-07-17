from subscripts.handFinderAndPointsAssigner import *
from subscripts.spectralCards import Spectral
from subscripts.saveUtils import *
from subscripts.shop import *
from subscripts.inputHandling import *
from subscripts.pygameSubfunctions import *
import random, pygame, time


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


def main(save):
    pygame.init()
    screenWidth = 1280
    screenHeight = 720
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    pygame.display.set_caption("Realatro")
    font = pygame.font.Font("cardSprites/font/balatro.otf")

    lookupTable = openjson("cardCreationAndRecognition/cardToArcuo.json", True)

    backupDetectedCardsScan = {
        "upper": [],
        "middle": [],
        "lower": [],
        "unpairedTags": []
    }
    backupDetectedCardsScanTime = time.time()

    # TODO: The outline changes color depending on the game state
    colors = {
        "backgroundColor": (60, 120, 90),
        "red": (254, 76, 64),
        "green": (52, 189, 133),
        "blue": (0, 146, 255),
        "white": (255, 255, 255),
        "yellow": (245, 179, 68),
        "uiOutline": (125, 62, 62),
        "darkUI": (27, 38, 40),
        "lightUI": (59, 80, 85)
    }

    cap = openCamera(1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False



        screen.fill(colors["backgroundColor"])

        foundCards = drawWebcamAndReturnFoundCards(cap, lookupTable, screen)

        # idk how much this really helps with flickering but if there's partial scans of tags it'll switch to a scan
        # without any unpaired tags less than 3 seconds old
        currentTime = time.time()
        if len(foundCards["unpairedTags"]) > 0:
            if currentTime - backupDetectedCardsScanTime < 3:
                foundCards = backupDetectedCardsScan
        else:
            backupDetectedCardsScan = foundCards
            backupDetectedCardsScanTime = currentTime

        handType, handInfo = drawCardCounter(save, font, screen, colors, foundCards)

        # analysis mode, draws a popup saying what the joker/consumable does
        if handInfo is None:
            drawAnalysisPopup(save, font, screen, colors, handType)
            handType = ""
            level = ""
            score = 0
            displayChips = 0
            displayMult = 0
        else:
            level = handInfo["level"]
            score = 0
            displayChips = handInfo["chips"]
            displayMult = handInfo["mult"]

        drawLeftBar(save, font, screen, colors, handType, level, score, displayChips, displayMult)

        drawButtons(save, screen, colors, font)

        pygame.display.flip()

main(Save(openjson("save")))
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