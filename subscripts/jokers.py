import math, random
from subscripts.spacesavers import *


class Joker:
    def __init__(self, jokerDict):
        # this is dumb since I mistakenly put the stuff that's in every joker in with the other stuff that isn't
        self.name = jokerDict[0]
        unsortedData = jokerDict[1]
        self.data = {k: v for k, v in unsortedData.items() if k not in {"id", "cost", "rarity", "description"}}
        self.id = unsortedData["id"]
        self.cost = unsortedData["cost"]
        self.rarity = unsortedData["rarity"]
        self.description = unsortedData["description"]
        self.additionalSellValue = unsortedData.get("additionalSellValue", 0)
        self.edition = unsortedData.get("edition")

    def getSellValue(self):
        # yes I know the joker is stored as a dict and all the other cards are objects deal with it
        # TODO: Figure out how to get this working with Gift Card
        if self.name == "Egg":
            return self.data["sellValue"]
        sellCost = max(1, math.floor(self.data["cost"] / 2))
        if "edition" in self.data:
            sellCost += editionSellValueDict[self.data["edition"]]
        return sellCost

    def toString(self):
        return (f"{self.name}: {self.description}")

    def toDict(self):
        return (self.name, self.data | {
            "id": self.id,
            "cost": self.cost,
            "rarity": self.rarity,
            "description": self.description,
            "additionalSellValue": self.additionalSellValue,
            "edition": self.edition
        })

editionSellValueDict = {
    "foil": 2,
    "holographic": 3,
    "polychrome": 5,
    "negative": 5
}

def generateShuffledListOfFinishedJokersByRarity(rarity, save):
    # TODO: there's some jokers that can't be spawned under specific conditions
    jokerDict = openjson("jokerDict")
    finishedJokers = []
    for joker in jokerDict.items():
        if joker[1]["rarity"] == rarity and "finished" in joker[1]:
            finishedJokers.append(Joker(joker))
    random.shuffle(finishedJokers)
    return finishedJokers