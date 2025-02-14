from subscripts.cardUtils import *
from subscripts.handFinderAndPointsAssigner import *
from subscripts.spacesavers import *
from subscripts.saveUtils import *
from subscripts.planetCards import *
from subscripts.shop import *
import random


# play a specific ante in the command line
# eventually all the input lines will be replaced with actual card reading
#TODO: boss bind support
def commandLinePlayRound(requiredScore, save):
    deck = save.deck
    random.shuffle(deck)
    hand = []
    discardedCards = []
    playedCards = []

    discardCount = 4
    handsCount = 4

    score = 0
    playing = True

    while playing:
        while len(hand) < 8:
            hand.append(createCardFromDict(deck[0]))
            del deck[0]
        handDisplay = []

        listNum = 1
        for handCard in hand:
            handDisplay.append(str(listNum) + ": " + handCard.toString())
            listNum += 1

        print(f"{handsCount} hands left, {discardCount} discards")
        print(f"{score}/{requiredScore} chips")
        print(f"Current hand:\n" + '\n'.join(handDisplay))
        # print(f"{len(deck) + len()} cards")
        selectionIsValid = False
        validResponses = ["play", "discard", "use", "inv"]
        while not selectionIsValid:
            choice = input("what do you want to do now? Type \"play\" to play, \"discard\" to discard, \"use\" to use/sell "
                           "a consumable, and \"inv\" to see your consumables.")
            if choice in validResponses:
                if choice == "discard" and discardCount <= 0:
                    print("You have no discards left!")
                if choice == "inv":
                    printConsumables(save)
                else:
                    selectionIsValid = True
                if choice == "use" and len(save.consumables) > 0:
                    print("You have no consumables!")
            else:
                print(f"Unrecognized action: {choice}")

        # consumable selection logic handling
        if choice == "use":
            selectionIsValid = False
            while not selectionIsValid:
                printConsumables(save)
                consumableSelect = input("Type the number of the consumable you want to buy or sell! Type \"cancel\" "
                                         " to cancel.")
                if consumableSelect == "cancel":
                    print("Cancelled!")
                    selectionIsValid = True

        # card selection logic handling
        if choice in ["play", "discard"]:
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
                selectedHand.append(hand[index-1])

            # deletes in reverse order so it doesn't screw up the other indexes
            for index in sorted(selectedHandIndexes, reverse=True):
                del hand[index-1]

            if choice == "play":
                points, affectedCards = calcPointsFromHand(selectedHand, findBestHand(selectedHand), hand, save)
                # handles glass card breaking, same reverse order trick as before
                for cardIndex in range(len(selectedHand) - 1, -1, -1):
                    playedCards.append(selectedHand[cardIndex])
                    if selectedHand[cardIndex].enhancement == "glass":
                        if selectedHand[cardIndex].number in affectedCards or affectedCards == "all":
                            if random.randint(1, 1) == 1:
                                print(f"{selectedHand[cardIndex].toString()} broke!")
                                del selectedHand[cardIndex]

                print(f"+{points} points! \n")
                score += points
                handsCount -= 1
                if score >= requiredScore:
                    print(f"Victory!\nScore:{score}")
                    # TODO: put blue seal stuff here
                    goldCardAmnt = 0
                    for card in hand:
                        if card.enhancement == "gold":
                            goldCardAmnt += 1
                            save.money += 3
                    if goldCardAmnt > 0:
                        print(f"Earned ${3 * goldCardAmnt} from {goldCardAmnt} gold cards in your hand!")
                    playing = False
                    win = True

                elif handsCount <= 0:
                    print(f"Defeat!\nScore:{score}")
                    playing = False
                    win = False

                if not playing:
                    # resets the deck
                    for card in discardedCards:
                        deck.append(card.toDict())
                    for card in playedCards:
                        deck.append(card.toDict())
                    for card in hand:
                        deck.append(card.toDict())

                    return {"win": win, "handsLeft": handsCount}
            elif choice == "discard":
                for discardedCard in selectedHand:
                    discardedCards.append(discardedCard)
                print("discarded!")
                discardCount -= 1



anteBaseChipsList = [100, 300, 800, 2000, 5000, 11000, 20000, 35000, 50000, 110000, 560000, 72000000, 300000000,
                     47000000000, 2.9E+13, 7.7E+16, 8.6E+20, 4.2E+25, 9.2E+30, 9.2E+36, 4.3E+43, 9.7E+50, 1.0E+59,
                     5.8E+67, 1.6E+77, 2.4E+87, 1.9E+98, 8.4E+109, 2.0E+122, 2.7E+135, 2.1E+149, 9.9E+163, 2.7E+179,
                     4.4E+195, 4.4E+212, 2.8E+230, 1.1E+249, 2.7E+268, 4.5E+288, 4.8E+309]

blindIndexToBlindInfo = [("Small Blind", 1, 3), ("Big Blind", 1.5, 4), ("Boss Blind", 2, 5)]

def play(fromSave):
    if fromSave:
        save = createSaveFromDict(openjson("save"))
    else:
        save = createBlankSave(deck="gold test")
    alive = True
    while alive:
        # while state == "selectingAndPlayingBlind":
            blindInfo = blindIndexToBlindInfo[save.blindIndex]
            requiredScore = anteBaseChipsList[save.ante]*blindInfo[1]
            print(f"ANTE {save.ante}\n{blindInfo[0]}: {requiredScore} CHIPS")
            selectionIsValid = False
            validResponses = ["play", "skip"]
            while not selectionIsValid:
                choice = input("play or skip?")
                if choice in validResponses:
                    if choice == "skip" and blindInfo[0] == "Boss Blind":
                        print("You can't skip the Boss Blind!")
                    else:
                        selectionIsValid = True
                else:
                    print(f"Unrecognized action: {choice}\nType \"play\" or \"skip\"!")

            if choice == "play":
                roundInfo = commandLinePlayRound(requiredScore, save)
                if roundInfo["win"]:
                    # advances to the next round
                    if save.blindIndex == 2:
                        save.ante += 1
                        save.blindIndex = 0
                    else:
                        save.blindIndex += 1
                    baseReward = blindInfo[2]
                    totalReward = baseReward + roundInfo['handsLeft']
                    save.money += totalReward
                    print(f"Rewards: ${baseReward} + {roundInfo['handsLeft']} hands left = +${totalReward}\n"
                          f"Money: ${save.money}")

                    #TODO: put in shop here
                    loadShop(save)


                    saveGame(save)
                else:
                    break
            if choice == "skip":
                print("skipped!")
                save.blindIndex += 1
                saveGame(save)


# commandLinePlayAnte(300, openjson("decks")["standard"])

play(False)