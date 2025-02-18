from subscripts.spacesavers import *
import random

suitAbrToName = {
    "S": "♠",
    "C": "♣",
    "D": "♦",
    "H": "♥"
}
valueAbrToName = {
    "J": "Jack",
    "Q": "Queen",
    "K": "King",
    "A": "Ace"
}

class Card:
    def __init__(self, subset, number, suit=None, enhancement=None, edition=None, seal=None, retriggerCount=None):
        self.subset = subset
        self.number = number
        self.enhancement = enhancement
        self.edition = edition
        self.seal = seal
        self.suit = suit
        self.retriggerCount = retriggerCount

    def toDict(self):
        return {
            "subset": self.subset,
            "number": self.number,
            "enhancement": self.enhancement,
            "edition": self.edition,
            "seal": self.seal,
            "suit": self.suit,
            "retriggerCount": self.retriggerCount
        }

    def toString(self):
        if self.subset == "playing":
            descriptor = ""
            if self.seal is not None:
                descriptor += self.seal.capitalize() + "-Sealed "
            if self.edition is not None:
                descriptor += self.edition.capitalize() + " "
            if self.enhancement is not None:
                descriptor += self.enhancement.capitalize() + " "

            #TODO: add fancy mode here for proper title

            # if self.number.isdigit():
            #     descriptor += self.number + " of "
            # else:
            #     descriptor += valueAbrToName[self.number] + " of "

            return descriptor + self.number + suitAbrToName[self.suit]
        if self.subset == "planet":
            return f"{self.number} (Upgrade {openjson('planetCards/planetCardsDict')[self.number]['hand']})"

    # TODO: add a joker list and all the other card stuff here
    def toBinary(card):
        if card.subset == "playing":
            if card.enhancement != "stone":
                # regular playing cards can't be negative so I do 2 bits for editions instead of 3
                binaryEncoder = ("010" + attributeToBinary("edition", card.edition, 2) +
                                 attributeToBinary("enhancement", card.enhancement, 3) +
                                 attributeToBinary("seal", card.seal, 3) +
                                 attributeToBinary("suit", card.suit, 2) +
                                 playingCardNumberToBinary(card.number))
            else:
                binaryEncoder = ("110" + attributeToBinary("edition", card.edition, 2) +
                                 attributeToBinary("seal", card.seal, 3))
            return int(binaryEncoder, 2)

        elif card.subset == "tarot":
            return
        elif card.subset == "planet":
            return
        elif card.subset == "spectral":
            return


# takes in a dictionary of card values and returns a Card object
def createCardFromDict(cardDict):
    return Card(subset=cardDict["subset"], number=cardDict["number"], suit=cardDict["suit"],
                enhancement=cardDict["enhancement"], edition=cardDict["edition"],
                seal=cardDict["seal"], retriggerCount=cardDict["retriggerCount"])


binaryDict = {
    "subset": [None, "joker", "playing", "tarot", "planet", "spectral", "stone"],
    "edition": [None, "foil", "holographic", "polychrome", "negative"],
    "enhancement": [None, "bonus", "mult", "wild", "glass", "steel", "gold", "lucky"],
    "seal": [None, "gold", "red", "blue", "purple"],
    "suit": ["S", "C", "H", "D"],
    "nonNumericalNumber": ["J", "Q", "K", "A"]
}

def createCardFromBinary(binary):
    binary = str(bin(binary)[2:]).zfill(17)
    subset = binaryToAttribute("subset", binary[0:3])
    if subset == "playing":
        return Card(subset=subset,
                    edition=binaryToAttribute("edition", binary[3:5]),
                    enhancement=binaryToAttribute("enhancement", binary[5:8]),
                    seal=binaryToAttribute("seal", binary[8:11]),
                    suit=binaryToAttribute("suit", binary[11:13]),
                    number=binaryToPlayingCardNumber(binary[13:17]))
    elif subset == "tarot":
        return
    elif subset == "planet":
        return
    elif subset == "spectral":
        return
    elif subset == "stone":
        # since stone cards don't show their suit or number, I just init them as an ace of spades
        # if vampire removes the stone enhancement, the number and suit will be randomized
        return Card(subset="playing",
                    edition=binaryToAttribute("edition", binary[5:7]),
                    enhancement="stone",
                    seal=binaryToAttribute("seal", binary[7:10]),
                    suit="S",
                    number="A")


def attributeToBinary(type, attribute, bits):
    attributeIndex = binaryDict[type].index(attribute)
    return str(format(attributeIndex, f'0{bits}b'))

def binaryToAttribute(type, attribute):
    return binaryDict[type][int(attribute, 2)]

def playingCardNumberToBinary(num):
    if num.isdigit():
        return(format(int(num), '04b'))
    else:
        attributeIndex = binaryDict["nonNumericalNumber"].index(num)
        return str(format(attributeIndex + 11, '04b'))

def binaryToPlayingCardNumber(binary):
    number = int(binary, 2)
    if number > 10:
        return binaryDict["nonNumericalNumber"][number-11]
    else:
        return str(number)

# TODO: get this working with vouchers eventually
def generateWeightedRandomCard(subset):
    if subset == "playing":
        # editions: 1.2% for poly, 2.8% for holo, 4% for foil
        editionOptions = ["polychrome", "holographic", "foil", None]
        editionProbabilities = [0.012, 0.028, 0.04, 0.92]
        edition = random.choices(editionOptions, editionProbabilities)[0]

        # 40% chance for an enhancement, equal weights for each
        enhancementRoll = random.randint(1, 10)
        enhancement = None
        if enhancementRoll > 6:
            enhancementList = ["bonus", "mult", "wild", "glass", "steel", "gold", "lucky", "stone"]
            random.shuffle(enhancementList)
            enhancement = enhancementList[0]

        # 20% chance for a seal, also equal weights
        sealRoll = random.randint(1, 5)
        seal = None
        if sealRoll == 1:
            sealList = ["red", "blue", "gold", "purple"]
            random.shuffle(sealList)
            seal = sealList[0]

        numList = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        random.shuffle(numList)

        suitList = ["S", "C", "D", "H"]
        random.shuffle(suitList)

        # the card number and suit is completely random
        return Card(subset=subset,
                    number=numList[0],
                    suit=suitList[0],
                    edition=edition,
                    enhancement=enhancement,
                    seal=seal)