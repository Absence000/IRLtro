from subscripts.inputHandling import *
import random


class Tarot:
    def __init__(self, name, negative=None):
        self.name = name
        self.negative = negative

    def toString(self, mode=None):
        isNegative = ""
        if self.negative:
            isNegative = "Negative "
        if mode is None:
            return f"{isNegative}{self.name}: {openjson('consumables/tarotDict')[self.name]['description']}"
        else:
            return f"{isNegative}{self.name}"

    def toDict(self):
        return{
            "name": self.name,
            "negative": self.negative,
            "type": "tarot"
        }

    def toBinary(self):
        nameIndex = list(openjson('consumables/tarotDict').keys()).index(self.name)
        negativeBit = "0"
        if self.negative:
            negativeBit = "1"
        binaryEncoder = "011" + str(format(nameIndex, '05b')) + negativeBit + "00000000"
        return int(binaryEncoder, 2)

def generateShuffledListOfFinishedTarotCards():
    finishedTarots = ["The Magician (I)", "The Empress (III)", "The Hierophant (V)", "The Lovers (VI)",
                      "The Chariot (VII)", "Justice (VIII)", "Strength (XI)", "The Hanged Man (XII)",
                      "Death (XIII)", "The Devil (XV)", "The Tower (XVI)", "The Star (XVII)", "The Moon (XVIII)",
                      "The Sun (XIX)", "The World (XXI)"]

    viableTarotCards = []
    for tarot in finishedTarots:
        viableTarotCards.append(Tarot(tarot))
    random.shuffle(viableTarotCards)
    return viableTarotCards
def useTarotCard(card, save):
    # unlike cards or jokers I can get away with using tarot card dictionaries since all this stuff is immutable for
    # all of them
    tarotCardInfo = openjson("consumables/tarotDict")[card.name]
    print(f"{card.toString()}")

    # if the tarot card needs you to select cards from your hand (most of them)
    if tarotCardInfo["type"] == "handModifier":
        maxCardSelectAmount = tarotCardInfo["amnt"]
        # death is the only one that needs exactly two cards picked
        canSelectLessThanMax = True
        upTo = "up to "
        if card.name == "Death (XIII)":
            canSelectLessThanMax = False
            upTo = "exactly "

        # makes sure the user selects the correct amount of cards plus error handling
        selectedHandIndexes = []
        selectionIsValid = False
        while not selectionIsValid:
            if not playingIRL(save):
                print(f"Your hand:\n{CLDisplayHand(save.hand)}")
                cardSelection = input(f"Select {upTo}{maxCardSelectAmount} cards, separated by commas and spaces! "
                                      f"Type \"cancel\" to cancel.")
                try:
                    selectedHandIndexes = [int(num) for num in cardSelection.split(", ")]
                    if len(selectedHandIndexes) > maxCardSelectAmount:
                        print(f"You can't select more than {maxCardSelectAmount} cards at once!")
                    elif all(1 <= index <= 8 for index in selectedHandIndexes):
                        if canSelectLessThanMax:
                            selectionIsValid = True
                        else:
                            if len(selectedHandIndexes) == maxCardSelectAmount:
                                selectionIsValid = True
                            else:
                                print(f"Select exactly {maxCardSelectAmount} cards!")
                    else:
                        print("Numbers out of range!")
                except:
                    print(f"Unrecognized hand indexes: {cardSelection}")
            else:
                # TODO: fix the messages so the user has time to choose
                while not selectionIsValid:
                    cardSelection = input(f"Put {upTo}{maxCardSelectAmount}  cards in the center and type \"play\" "
                                          f"to select them! Type \"cancel\" to cancel.")
                    if cardSelection == "play":
                        selectedHand = returnCardsFromImage()["middle"]
                        if len(selectedHand) > maxCardSelectAmount:
                            print(f"You can't select more than {maxCardSelectAmount} cards at once!")
                        elif canSelectLessThanMax:
                            selectionIsValid = True
                        else:
                            if len(selectedHand) == maxCardSelectAmount:
                                selectionIsValid = True
                            else:
                                print(f"Select exactly {maxCardSelectAmount} cards!")

        # I know this is a really shitty way of handling irl vs command line playing but who cares lmao

        # suit converters (star, moon, sun, world)
        if tarotCardInfo["modifier"] == "suit":
            if playingIRL(save):
                clearPrintFolder()
                for card in selectedHand:
                    card.suit = tarotCardInfo["suit"]
                    prepareCardForPrinting(card, keep=True)
                print("Print out the cards in the \"print\" folder, and replace the current cards with them!")

            else:
                for index in selectedHandIndexes:
                    save.hand[index-1].suit = tarotCardInfo["suit"]

        # enhancer converters (magician, empress, hierophant, lovers, chariot, justice, devil, tower)
        elif tarotCardInfo["modifier"] == "enhancer":
            if playingIRL(save):
                clearPrintFolder()
                for card in selectedHand:
                    card.enhancement = tarotCardInfo["enhancement"]
                    prepareCardForPrinting(card, keep=True)
                print("Print out the cards in the \"print\" folder, and replace the current cards with them!")

            else:
                for index in selectedHandIndexes:
                    save.hand[index-1].enhancement = tarotCardInfo["enhancement"]

        # rank converter (strength)
        elif tarotCardInfo["modifier"] == "rank":
            if playingIRL(save):
                clearPrintFolder()
                for card in selectedHand:
                    card.number = increaseCardVal(card.number)
                    prepareCardForPrinting(card, keep=True)
                print("Print out the cards in the \"print\" folder, and replace the current cards with them!")

            else:
                for index in selectedHandIndexes:
                    save.hand[index-1].number = increaseCardVal(save.hand[index-1].number)

        # destroy converter (hanged man)
        elif tarotCardInfo["modifier"] == "destroy":
            if playingIRL(save):
                print("Put the selected cards off to the side and don't use them for the rest of the game!")
            else:
                for index in selectedHandIndexes:
                    del save.hand[index-1]

        # convert converter (death)
        elif tarotCardInfo["modifier"] == "convert":
            if playingIRL(save):
                from cardCreationAndRecognition.cardImageCreator import createTaggedCardImage
                prepareCardForPrinting(selectedHand[1])
                print("Print out the card in the \"print\" folder, and replace the left card with it!")

            else:
                save.hand[selectedHandIndexes[0]] = save.hand[selectedHandIndexes[1]]

        print(f"Success! New hand:\n{CLDisplayHand(save.hand)}")


def increaseCardVal(oldVal):
    face_cards = {"J": 11, "Q": 12, "K": 13, "A": 14}
    reverse_face_cards = {v: k for k, v in face_cards.items()}

    if oldVal in face_cards:
        value = face_cards[oldVal]
    else:
        value = int(oldVal)

    new_value = value + 1

    if new_value > 14:  # Reset after Ace (A)
        return "2"  # Wrap around back to 2
    return reverse_face_cards.get(new_value, str(new_value))
