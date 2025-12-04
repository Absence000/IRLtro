import math, random
from subscripts.spacesavers import *


class Joker:
    def __init__(self, jokerDict, edition=None):
        # this is dumb since I mistakenly put the stuff that's in every joker in with the other stuff that isn't
        self.name = jokerDict[0]
        unsortedData = jokerDict[1]
        self.data = {k: v for k, v in unsortedData.items() if k not in {"id", "cost", "rarity", "description"}}
        self.id = unsortedData["id"]
        self.cost = unsortedData["cost"]
        self.rarity = unsortedData["rarity"]
        self.description = unsortedData["description"]
        self.additionalSellValue = unsortedData.get("additionalSellValue", 0)
        self.edition = edition
        self.coords = None
        self.debuffed = False

    def getSellValue(self):
        # yes I know the joker is stored as a dict and all the other cards are objects deal with it
        # TODO: Figure out how to get this working with Gift Card
        if self.name == "Egg":
            return self.data["sellValue"]
        sellCost = max(1, math.floor(self.data["cost"] / 2))
        sellCost += editionSellValueDict[self.data["edition"]]
        return sellCost

    def toString(self, mode=None):
        editionIndicator = ""
        if self.edition is not None:
            editionIndicator = f"{self.edition.capitalize()} "
        if mode is None:
            return (f"{editionIndicator}{self.name}: {self.description}")
        elif mode == "description":
            return self.description
        else:
            return f"{editionIndicator}{self.name}"

    def toDict(self):
        return (self.name, self.data | {
            "id": self.id,
            "cost": self.cost,
            "rarity": self.rarity,
            "description": self.description,
            "additionalSellValue": self.additionalSellValue,
            "edition": self.edition
        })

    def toBinary(self):
        nameIndex = list(openjson('jokerDict').keys()).index(self.name)
        editionIndex = editionBinaryDecodingList.index(self.edition)
        binaryEncoder = "001" + str(format(nameIndex, '08b')) + str(format(editionIndex, '03b')) + "000"
        return int(binaryEncoder, 2)

editionSellValueDict = {
    None: 0,
    "foil": 2,
    "holographic": 3,
    "polychrome": 5,
    "negative": 5
}

editionBinaryDecodingList = [None, "foil", "holographic", "polychrome", "negative"]

def generateShuffledListOfFinishedJokersByRarity(rarity, save):
    # TODO: there's some jokers that can't be spawned under specific conditions
    jokerDict = openjson("jokerDict")
    finishedJokers = []
    for joker in jokerDict.items():
        if joker[1]["rarity"] == rarity and "finished" in joker[1]:
            finishedJokers.append(Joker(joker))
    random.shuffle(finishedJokers)
    return finishedJokers

# TODO: I think the main game classifies duplicate jokers as type regardless of edition but make sure
def generateRandomWeightedJokers(save, amount):
    jokerList = []
    while len(jokerList) < amount:
        rarities = ["Common", "Uncommon", "Rare"]
        weights = [70, 25, 5]
        rarity = random.choices(rarities, weights)[0]
        chosenJoker = generateShuffledListOfFinishedJokersByRarity(rarity, save)[0]

        # edition chances:
        # 0.3% negative, 0.3% polychrome, 1.4% holographic, 2% foil
        # TODO: Put code for Hone and Glow Up here
        editions = [None, "negative", "polychrome", "holographic", "foil"]
        editionChances = [96, 0.3, 0.3, 1.4, 2]
        chosenJoker.edition = random.choices(editions, editionChances)[0]
        isDuplicate = False
        for joker in jokerList:
            if joker.name == chosenJoker.name:
                isDuplicate = True
        if not isDuplicate:
            jokerList.append(chosenJoker)

    return jokerList