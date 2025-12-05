import math, random, re
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
        if edition is None:
            self.edition = unsortedData.get("edition", None)
        self.coords = None
        self.debuffed = False
        self.trackingID = None

    def getSellValue(self):
        # yes I know the joker is stored as a dict and all the other cards are objects deal with it
        # TODO: Figure out how to get this working with Gift Card
        if self.name == "Egg":
            return self.data["sellValue"]
        sellCost = max(1, math.floor(self.cost / 2))
        sellCost += editionSellValueDict[self.edition]
        return sellCost

    def toString(self, mode=None):
        editionIndicator = ""
        description = self.getDescription()
        if self.edition is not None:
            editionIndicator = f"{self.edition.capitalize()} "
        if mode is None:
            return (f"{editionIndicator}{self.name}: {description}")
        elif mode == "description":
            return description
        else:
            return f"{editionIndicator}{self.name}"

    def getDescription(self):
        description = self.description

        pattern = r"\{([^}]+)\}"

        def replacer(match):
            expression = match.group(1)
            try:
                return str(eval(expression, {}, {"self": self}))
            except Exception as e:
                return f"<error:{e}>"

        return re.sub(pattern, replacer, description)




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

    # if I need to modify them in place
    def copy(self):
        return Joker(self.toDict())

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
        alreadyOwned = False
        if not save.hasJoker("Showman"):
            for ownedJoker in save.jokersInPlay:
                if joker[0] == ownedJoker.name:
                    alreadyOwned = True


        if joker[1]["rarity"] == rarity and "finished" in joker[1] and not alreadyOwned:
            chosenJoker = Joker(joker)
            # edition chances:
            # 0.3% negative, 0.3% polychrome, 1.4% holographic, 2% foil
            # TODO: Put code for Hone and Glow Up here
            editions = [None, "negative", "polychrome", "holographic", "foil"]
            editionChances = [96, 0.3, 0.3, 1.4, 2]
            chosenJoker.edition = random.choices(editions, editionChances)[0]
            finishedJokers.append(chosenJoker)
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

        # extra logic to prevent the same joker showing up twice in the same pack unless showman
        isDuplicate = False
        for joker in jokerList:
            if joker.name == chosenJoker.name:
                isDuplicate = True
        if not isDuplicate or save.hasJoker("Showman"):
            jokerList.append(chosenJoker)

    return jokerList