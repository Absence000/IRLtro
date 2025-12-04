from subscripts.planetCards import usePlanetCard, Planet
from subscripts.priceCalcLogic import calculatePrice
from subscripts.tarotCards import useTarotCard, Tarot
from subscripts.spacesavers import *
import math


# once the user makes a selection for the consumable, this asks them whether they want to use or sell it
# and also checks if it can be used right now

# TODO: Finish this once the save system is working with the shop
def CLUseOrSellConsumables(consumable, save):
    if consumableCanBeUsedImmediately(consumable):
        return

# TODO: move the function for adding consumables to the player's hand here

# TODO: get spectrals working here too
def useConsumable(consumable, save):
    if isinstance(consumable, Planet):
        usePlanetCard(consumable, save)
    if isinstance(consumable, Tarot):
        useTarotCard(consumable, save)


def getConsumableSellPrice(consumable, save):
    buyPrice = calculatePrice(consumable, save)
    return math.floor(buyPrice/2)

def sellConsumable(consumable, save):
    sellPrice = getConsumableSellPrice(consumable, save)
    save.money += sellPrice
    save.consumables.remove(consumable)

def printConsumables(save):
    consumablesAmnt = len(save.consumables)
    if consumablesAmnt >= 1:
        print(f"Consumables ({consumablesAmnt}/{save.consumablesLimit}):")
        iterator = 1
        for consumable in save.consumables:
            print(f"{iterator}: {consumable.toString()}")
            iterator += 1
    else:
        print("You have no consumables!")

# consumables that need a hand to work can't be used immediately
# TODO: make this work for spectrals when they're added
def consumableCanBeUsedImmediately(consumable):
    if isinstance(consumable, Tarot):
        if openjson("consumables/tarotDict")[consumable.name]["type"] == "handModifier":
            return False
    return True

def useImmediateConsumable(consumable, save):
    if isinstance(consumable, Tarot):
        useTarotCard(consumable, None, save)

    if isinstance(consumable, Planet):
        usePlanetCard(consumable, save)
    # TODO: spectrals here
