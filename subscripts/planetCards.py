from subscripts.cardUtils import Card
from subscripts.spacesavers import *
import random

defaultplanetCards = [Card(subset="planet", number="Pluto"),
                      Card(subset="planet", number="Mercury"),
                      Card(subset="planet", number="Uranus"),
                      Card(subset="planet", number="Venus"),
                      Card(subset="planet", number="Saturn"),
                      Card(subset="planet", number="Jupiter"),
                      Card(subset="planet", number="Earth"),
                      Card(subset="planet", number="Mars"),
                      Card(subset="planet", number="Neptune")]

secretPlanetCardDict = {"Five Of A Kind": Card(subset="planet", number="Planet X"),
                        "Flush House": Card(subset="planet", number="Ceres"),
                        "Flush Five": Card(subset="planet", number="Eris"),}


def generateShuffledListOfUnlockedPlanetCards(save):
    viablePlanetCards = defaultplanetCards
    for illegalHand in save.illegalHandsDiscovered:
        viablePlanetCards.append(secretPlanetCardDict[illegalHand])

    random.shuffle(viablePlanetCards)
    return viablePlanetCards

def usePlanetCard(card, save):
    planetCardInfo = openjson("planetCards/planetCardsDict")[card.number]
    upgradeHandLevel(planetCardInfo["hand"], 1, planetCardInfo["addition"][1], planetCardInfo["addition"][0], save)

#TODO: make this work with downgrading as well
def upgradeHandLevel(hand, level, chipUpgrade, multUpgrade, save):
    for i in range(level):
        save.handLevels[hand]["level"] += 1
        save.handLevels[hand]["chips"] += chipUpgrade
        save.handLevels[hand]["mult"] += multUpgrade
    plural = ""
    if level > 1:
        plural = "s"
    print(f'{hand} upgraded {level} level{plural} (now at level {save.handLevels[hand]["level"]})!')