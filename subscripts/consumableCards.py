from subscripts.planetCards import usePlanetCard, Planet
from subscripts.priceCalcLogic import calculatePrice
from subscripts.tarotCards import useTarotCard, Tarot
from subscripts.spectralCards import useSpectralCard, Spectral
from subscripts.spacesavers import *
import math


# once the user makes a selection for the consumable, this asks them whether they want to use or sell it
# and also checks if it can be used right now

# TODO: Finish this once the save system is working with the shop
def CLUseOrSellConsumables(consumable, save):
    if consumableCanBeUsedImmediately(consumable):
        return

# TODO: eventually this will replace all the garbage in main.py it's not finished yet
def useConsumable(consumable, save):
    if isinstance(consumable, Planet):
        usePlanetCard(consumable, save)
    if isinstance(consumable, Tarot):
        useTarotCard(consumable, save)
    if isinstance(consumable, Spectral):
        useSpectralCard(consumable, save)


def getConsumableSellPrice(consumable, save):
    buyPrice = calculatePrice(consumable, save)
    return math.floor(buyPrice/2)

def sellConsumable(consumable, save):
    sellPrice = getConsumableSellPrice(consumable, save)
    save.money += sellPrice
    save.consumables.remove(consumable)

# consumables that need a hand to work can't be used immediately
def consumableCanBeUsedImmediately(consumable):
    if isinstance(consumable, Tarot):
        if openjson("consumables/tarotDict")[consumable.name]["type"] == "handModifier":
            return False
    elif isinstance(consumable, Spectral):
        if openjson("consumables/tarotDict")[consumable.name]["type"] in ["handModifier", "destroyRandom"]:
            return False
    return True

def useImmediateConsumable(consumable, save):
    if isinstance(consumable, Tarot):
        useTarotCard(consumable, None, save)

    if isinstance(consumable, Planet):
        usePlanetCard(consumable, save)

    elif isinstance(consumable, Spectral):
        useSpectralCard(consumable, None, save)