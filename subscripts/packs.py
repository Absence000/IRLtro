from subscripts.cardUtils import Card, generateWeightedRandomCard
import random

class Pack():
    def __init__(self, subset, size):
        self.subset = subset
        self.size = size

    # returns the proper amount of cards if opened
    def open(self, save):
        cardList = []
        subset = packTypeToCardTypeDict[self.subset]
        for iterator in range(sizeDict[self.size]):
            cardList.append(generateWeightedRandomCard(subset, save))
        return cardList

    def toString(self):
        return f"{self.size.capitalize()} {self.subset.capitalize()} Pack"

    def needsHandToUse(self):
        if self.subset in ["arcana", "spectral"]:
            return True
        return False

    def toDict(self):
        return {
            "subset": self.subset,
            "size": self.size
        }

sizeDict = {
    "normal": 3,
    "jumbo": 5,
    "mega": 5
}

packTypeToCardTypeDict = {
    "arcana": "tarot",
    "celestial": "planet",
    "standard": "playing",
    "buffoon": "joker"
}

packWeightDict = {
    "standard": [4, 2, 0.5],
    "arcana": [4, 2, 0.5],
    "celestial": [4, 2, 0.5],
    "buffoon": [1.2, 0.6, 0.15],
    "spectral": [0.6, 0.3, 0.07]
}

# TODO: add support for buffoon and spectral packs
def generatePackForSale():
    sizes = ["normal", "jumbo", "mega"]
    addedPacks = ["standard", "arcana", "celestial", "buffoon"]
    packOptions = []
    packWeights = []
    for subset in addedPacks:
        for size in sizes:
            packOptions.append(Pack(subset=subset, size=size))
            packWeights.append(packWeightDict[subset][sizes.index(size)])
    return random.choices(packOptions, packWeights)[0]