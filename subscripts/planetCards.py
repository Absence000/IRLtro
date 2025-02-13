from subscripts.cardUtils import Card
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