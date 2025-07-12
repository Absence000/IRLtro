from subscripts.spacesavers import *
import random


class Planet:
    def __init__(self, name, negative=None):
        self.name = name
        self.negative = negative

    def toString(self):
        return f"{self.name} (Upgrade {openjson('consumables/planetDict')[self.name]['hand']})"

    def toDict(self):
        return{
            "name": self.name,
            "negative": self.negative,
            "type": "planet"
        }


def usePlanetCard(card, save):
    planetCardInfo = openjson("consumables/planetDict")[card.name]
    upgradeHandLevel(planetCardInfo["hand"], 1, planetCardInfo["addition"][1], planetCardInfo["addition"][0], save)

# TODO: make this work with downgrading as well


def upgradeHandLevel(hand, level, chipUpgrade, multUpgrade, save):
    for i in range(level):
        save.handLevels[hand]["level"] += 1
        save.handLevels[hand]["chips"] += chipUpgrade
        save.handLevels[hand]["mult"] += multUpgrade
    plural = ""
    if level > 1:
        plural = "s"
    print(f'{hand} upgraded {level} level{plural} (now at level {save.handLevels[hand]["level"]})!')