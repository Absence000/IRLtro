from subscripts.spacesavers import *
from subscripts.inputHandling import CLDisplayHand, clearPrintFolder, prepareCardForPrinting, pushIRLInputIntoSave
import random


class Tarot:
    def __init__(self, name, negative=None):
        self.name = name
        self.negative = negative
        self.coords = None

    def toString(self, mode=None):
        isNegative = ""
        if self.negative:
            isNegative = "Negative "
        if mode is None:
            return f"{isNegative}{self.name}: {openjson('consumables/tarotDict')[self.name]['description']}"
        elif mode == "name":
            return f"{isNegative}{self.name}"
        elif mode == "description":
            return openjson('consumables/tarotDict')[self.name]['description']

    def toDict(self):
        return{
            "name": self.name,
            "negative": self.negative,
            "type": "Tarot"
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
def useTarotCard(card, otherCards, save):
    # unlike cards or jokers I can get away with using tarot card dictionaries since all this stuff is immutable for
    # all of them
    tarotCardInfo = openjson("consumables/tarotDict")[card.name]

    # if the tarot card needs you to select cards from your hand (most of them)
    if tarotCardInfo["type"] == "handModifier":
        maxCardSelectAmount = tarotCardInfo["amnt"]
        # death is the only one that needs exactly two cards picked
        canSelectLessThanMax = True
        if card.name == "Death (XIII)":
            canSelectLessThanMax = False

        if otherCards == []:
            return False

        if len(otherCards) > maxCardSelectAmount:
            return False

        if card.name == "Death (XIII)" and len(otherCards) == 1:
            return False

        # suit converters (star, moon, sun, world)
        if tarotCardInfo["modifier"] == "suit":
            for card in otherCards:
                newCard = card.copy()
                newCard.suit = tarotCardInfo["suit"]
                save.replaceCardInDeck(card, newCard)
                prepareCardForPrinting(newCard, keep=True)


        # enhancer converters (magician, empress, hierophant, lovers, chariot, justice, devil, tower)
        elif tarotCardInfo["modifier"] == "enhancer":
            for card in otherCards:
                newCard = card.copy()
                newCard.enhancement = tarotCardInfo["enhancement"]
                save.replaceCardInDeck(card, newCard)
                prepareCardForPrinting(newCard, keep=True)

        # rank converter (strength)
        elif tarotCardInfo["modifier"] == "rank":
            for card in otherCards:
                newCard = card.copy()
                newCard.number = increaseCardVal(card.number)
                save.replaceCardInDeck(card, newCard)
                prepareCardForPrinting(newCard, keep=True)

        # destroy converter (hanged man)
        elif tarotCardInfo["modifier"] == "destroy":
            for card in otherCards:
                save.replaceCardInDeck(card, None)

        # convert converter (death)
        elif tarotCardInfo["modifier"] == "convert":
            newCard = otherCards[1].copy()
            prepareCardForPrinting(newCard)
            save.replaceCardInDeck(otherCards[0], newCard)

        return True

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
