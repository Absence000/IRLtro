from subscripts.planetCards import Planet, generateShuffledListOfUnlockedPlanetCards
from subscripts.spectralCards import Spectral
from subscripts.tarotCards import Tarot, generateShuffledListOfFinishedTarotCards
from subscripts.jokers import Joker, generateRandomWeightedJokers
from subscripts.spacesavers import *
import random

suitAbrToName = {
    "S": "♠",
    "C": "♣",
    "D": "♦",
    "H": "♥"
}

fancySuitAbrToName = {
    "S": " of Spades",
    "C": " of Clubs",
    "D": " of Diamonds",
    "H": " of Hearts"
}
valueAbrToName = {
    "J": "Jack",
    "Q": "Queen",
    "K": "King",
    "A": "Ace"
}

class Card:
    def __init__(self, cardDict):
        self.number = cardDict["number"]
        self.suit = cardDict["suit"]
        self.enhancement = cardDict.get("enhancement")
        self.edition = cardDict.get("edition")
        self.seal = cardDict.get("seal")
        # TODO: Figure out why some of them are getting None as retriggeredBy but not all of them
        self.retriggeredBy = cardDict.get("retriggeredBy", [])
        self.coords = None
        self.id = None
        self.debuffed = cardDict.get("debuffed", False)

    def toDict(self):
        return {
            "number": self.number,
            "enhancement": self.enhancement,
            "edition": self.edition,
            "seal": self.seal,
            "suit": self.suit,
            "retriggeredBy": self.retriggeredBy,
            "id": self.id
        }

    def toString(self, mode=None):
        descriptor = ""
        if self.seal is not None:
            descriptor += self.seal.capitalize() + "-Sealed "
        if self.edition is not None:
            descriptor += self.edition.capitalize() + " "
        if self.enhancement is not None:
            descriptor += self.enhancement.capitalize() + " "

        #TODO: add fancy mode here for proper title
        if mode == "fancy":
            suit = fancySuitAbrToName[self.suit]
        else:
            suit = suitAbrToName[self.suit]

        # if self.number.isdigit():
        #     descriptor += self.number + " of "
        # else:
        #     descriptor += valueAbrToName[self.number] + " of "

        return descriptor + self.number + suit

    # TODO: add a joker list and all the other card stuff here
    # all cards are represented with 17 bits!
    # first 3 are identity bits
    def toBinary(card):
        if card.enhancement != "stone":
            # regular playing cards can't be negative so I do 2 bits for editions instead of 3
            binaryEncoder = ("010" + attributeToBinary("edition", card.edition, 2) +
                             attributeToBinary("enhancement", card.enhancement, 3) +
                             attributeToBinary("seal", card.seal, 3) +
                             attributeToBinary("suit", card.suit, 2) +
                             playingCardNumberToBinary(card.number))
        else:
            binaryEncoder = ("110" + attributeToBinary("edition", card.edition, 2) +
                             attributeToBinary("seal", card.seal, 3) + "000000000")
        return int(binaryEncoder, 2)

    #TODO: fix this this is dumb
    def getValue(self):
        numList = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        return numList.index(self.number) + 2

    # if I need to modify them in place
    def copy(self):
        return Card(self.toDict())

# takes in a dictionary of card values and returns a Card object
def createCardFromDict(cardDict):
    return Card(cardDict)


binaryDict = {
    "subset": [None, "Joker", "Card", "Tarot", "Planet", "Spectral", "stone"],
    "edition": [None, "foil", "holographic", "polychrome", "negative"],
    "enhancement": [None, "bonus", "mult", "wild", "glass", "steel", "gold", "lucky"],
    "seal": [None, "gold", "red", "blue", "purple"],
    "suit": ["S", "C", "H", "D"],
    "nonNumericalNumber": ["J", "Q", "K", "A"]
}

def createCardFromBinary(id, binary, save, printedCards, sentToPrinter):
    formattedBinary = str(bin(binary)[2:]).zfill(17)
    subset = binaryToAttribute("subset", formattedBinary[0:3])
    if subset == "Card":
        suit = binaryToAttribute("suit", formattedBinary[11:13])
        number = binaryToPlayingCardNumber(formattedBinary[13:17])
        trueCard = Card({
            "suit": suit,
            "number": number,
            "debuffed": True
        })

        # dynamic remapping:
        # to stop people from needing to scan their entire deck at the start of each round it scans as it goes and
        # stores the ids automatically within the save's deck
        cardIsAccountedFor = False
        for card in save.deck:
            if card.number == number and card.suit == suit:
                if card.id is None:
                    cardIsAccountedFor = True
                    card.id = id
                    break
                elif card.id == id:
                    cardIsAccountedFor = True
                    break


        # if this ID has never been seen before it adds it to printedCards.json
        # fingers crossed it doesn't scan a bunch of things as IDs and clog it up
        # to stop this, if the new ID was never seen on sentToPrinter.json it won't be added to printedCards.json
        if id not in printedCards and id in sentToPrinter:
            printedCards.append(id)
            print(f"New ID found! {id}")
            savejson("printedCards", printedCards)
        if cardIsAccountedFor:
            return card
        else:
            return trueCard


    elif subset == "stone":
        # since stone cards don't show their suit or number, I just init them as an ace of spades
        # if vampire removes the stone enhancement, the number and suit will be randomized
        return Card({
            "subset": "playing",
            "edition": binaryToAttribute("edition", binary[5:7]),
            "enhancement": "stone",
            "seal": binaryToAttribute("seal", binary[7:10]),
            "suit": "S",
            "number": "A"
        })

    else:
        return returnNonPlayingCardFromBinary(binary, subset)


NonPlayingCardTypeToBinaryIndexes = {
    "Tarot": {
        "index": [3, 8],
        "jsonPath": "consumables/tarotDict"
    },
    "Planet": {
        "index": [3, 6],
        "jsonPath": "consumables/planetDict"
    },
    "Spectral": {
        "index": [3, 7],
        "jsonPath": "consumables/spectralDict"
    },
    "Joker": {
        "index": [3, 11],
        "jsonPath": "jokerDict"
    },
}

def returnNonPlayingCardFromBinary(binary, subset):
    cardData = NonPlayingCardTypeToBinaryIndexes[subset]
    cardDict = openjson(cardData["jsonPath"])
    nameStartBit, nameEndBit = cardData["index"]
    nameIndex = int(binary[nameStartBit:nameEndBit], 2)
    if subset == "Joker":
        editionIndex = int(binary[11:13], 2)
        edition = [None, "foil", "holographic", "polychrome", "negative"][editionIndex]
        data = list(cardDict.items())[nameIndex]
        return Joker(data, edition)
    else:
        negative = True
        if binary[nameEndBit + 1] == "0":
            negative = False
        return eval(subset)(name=list(cardDict)[nameIndex], negative=negative)


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
# TODO: consumable blocking!
def generateWeightedRandomCards(subset, save, amount):
    # TODO: Showman stuff for packs
    if subset == "playing":
        return generateListOfRandomPlayingCards(save, amount)
    elif subset == "tarot":
        return generateShuffledListOfFinishedTarotCards()[0:amount]
    elif subset == "planet":
        return generateShuffledListOfUnlockedPlanetCards(save)[0:amount]
    elif subset == "joker":
        return generateRandomWeightedJokers(save, amount)

def generateListOfRandomPlayingCards(save, amount):
    cardList = []
    for i in range(amount):
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
        cardList.append(Card({
            "number": numList[0],
            "suit": suitList[0],
            "edition": edition,
            "enhancement": enhancement,
            "seal": seal
        }))
    return cardList

# I have pointers to differentiate the consumable types but I don't need them for cards or jokers since they have
# unique keys
# ik it's good practice to have them anyway but whatever
# I won't need this once the visual component is integrated into the program instead of its own thing
def unsortedDictToCard(cardDict):
    cardName, cardItems = cardDict
    if ["suit"] in cardDict:
        return Card()

def addTarotCardIfRoom(save):
    if len(save.consumables) <= save.consumablesLimit:
        save.consumables.append(generateShuffledListOfFinishedTarotCards([0]))
        return True
    return False


def cardCountsAsFaceCard(card, save):
    if save.hasJoker("Pareidolia"):
        return True
    elif isinstance(card.number, str):
        return True
    return False