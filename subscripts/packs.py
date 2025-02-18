from subscripts.cardUtils import Card, generateWeightedRandomCard
import random

class Pack():
    def __init__(self, subset, size):
        self.subset = subset
        self.size = size

    # returns the proper amount of cards if opened
    def open(self):
        cardList = []
        for iterator in range(subsetDict[self.size]):
            cardList.append(generateWeightedRandomCard("playing"))
        return cardList

    def toString(self):
        return f"{self.size.capitalize()} {self.subset.capitalize()} Pack"

subsetDict = {
    "normal": 3,
    "jumbo": 5,
    "mega": 5
}

packWeightDict = {
    "standard": [4, 2, 0.5],
    "arcana": [4, 2, 0.5],
    "celestial": [4, 2, 0.5],
    "buffoon": [1.2, 0.6, 0.15],
    "spectral": [0.6, 0.3, 0.07]
}

# TODO: add support for all the other packs once their cards are done, right now this can only generate standard ones
def generatePackForSale():
    sizes = ["normal", "jumbo", "mega"]
    weights = packWeightDict["standard"]
    return Pack(subset="standard", size=random.choices(sizes, weights)[0])