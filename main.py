from cardCreationAndRecognition.finalArcuoTracking import returnFoundCards
from subscripts.handFinderAndPointsAssigner import *
from subscripts.saveUtils import *
from subscripts.shop import *
from subscripts.inputHandling import *
from cardCreationAndRecognition.cardImageCreator import makeStandardDeck
import random, pygame


# play a specific ante in the command line
# eventually all the input lines will be replaced with actual card reading
#TODO: boss bind support
def commandLinePlayRound(save):
    if not playingIRL(save):
        deck = save.deck
        random.shuffle(deck)
    save.hand = []

    playing = True

    while playing:

        if not playingIRL(save):
            while len(save.hand) < 8:
                save.hand.append(deck[0])
                del deck[0]
            # automatically sorts the deck numerically
            save.hand.sort(key=lambda card: card.getValue())

        # TODO: Add the ability to resort the deck here somewhere
        print(f"{save.hands} hands left, {save.discards} discards")
        print(f"{save.score}/{save.requiredScore} chips")
        if not playingIRL(save):
            print(f"Current hand:\n" + CLDisplayHand(save.hand))
        # print(f"{len(deck) + len()} cards")
        selectionIsValid = False
        validResponses = ["play", "discard", "use", "inv"]
        while not selectionIsValid:
            choice = input("what do you want to do now? Type \"play\" to play, \"discard\" to discard, \"use\" to use/sell "
                           "a consumable, and \"inv\" to see your consumables.")
            if choice in validResponses:
                if choice == "discard" and save.discards <= 0:
                    print("You have no discards left!")
                elif choice == "inv":
                    printConsumables(save)
                elif choice == "use" and len(save.consumables) == 0:
                    print("You have no consumables!")
                else:
                    selectionIsValid = True
            else:
                print(f"Unrecognized action: {choice}")

        # consumable selection logic handling
        if choice == "use":
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

        # card selection logic handling
        if choice in ["play", "discard"]:
            if not playingIRL(save):
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
                inputCardsDict = openjson("sortedDetectedCards")
                inputCards = {
                    key: [Card(cardDict) for cardDict in cardList]
                    for key, cardList in inputCardsDict.items()
                }
                selectedHand = inputCards["middle"]
                save.hand = inputCards["lower"]
                jokers = []
                consumables = []
                for card in inputCards["upper"]:
                    if isinstance(card, Joker):
                        jokers.append(card)
                    else:
                        consumables.append(card)
                save.jokers = jokers
                save.consumables = consumables

            if choice == "play":
                points, affectedCards = calcPointsFromHand(selectedHand, findBestHand(selectedHand), save.hand, save)
                # handles glass card breaking, same reverse order trick as before
                for cardIndex in range(len(selectedHand) - 1, -1, -1):
                    save.playedCards.append(selectedHand[cardIndex])
                    if selectedHand[cardIndex].enhancement == "glass":
                        if selectedHand[cardIndex].number in affectedCards or affectedCards == "all":
                            if random.randint(1, 1) == 1:
                                print(f"{selectedHand[cardIndex].toString()} broke!")
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
                    if not playingIRL(save):
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
            elif choice == "discard":
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
def CLPlay(fromSave, deck):
    if fromSave:
        save = createSaveFromDict(openjson("save"))
        if save.state != "selectingBlind":
            print(f"ANTE {save.ante}")
    else:
        save = createBlankSave(deck=deck)
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
                break
        # shopping
        while save.state == "shop":
            print(f"Money: ${save.money}")
            loadShop(save)
            save.state = "selectingBlind"
            saveGame(save)


def main(loadSave=False):
    # startup
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("IRLatro")
    font = pygame.font.SysFont(None, 30)

    running = True

    if not loadSave:
        gameState = "blindSelect"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # shows the 3 blinds with the options to play or skip
        if gameState == "blindSelect":
            return

        elif gameState == "round":
            return

    # Cleanup
    # cap.release()
    pygame.quit()

# CLPlay(fromSave=True, deck="gold test")

createTaggedCardImage(Card({
    "number": "A",
    "suit": "S",
    "enhancement": "glass",
    "edition": "polychrome"
}), openjson("cardCreationAndRecognition/cardToArcuo.json", True))