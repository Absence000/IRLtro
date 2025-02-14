from subscripts.cardUtils import Card
from subscripts.planetCards import usePlanetCard
from subscripts.priceCalcLogic import calculatePrice
import math

#TODO: move the function for adding consumables to the player's hand here

#TODO: get tarots and spectrals working here too
def useConsumable(consumable, save):
    if consumable.subset == "planet":
        usePlanetCard(consumable, save)


def getConsumableSellPrice(consumable, save):
    buyPrice = calculatePrice(consumable, save)
    return math.floor(buyPrice/2)

def sellConsumable(consumableIndex, save):
    consumableToSell = save.consumables[consumableIndex]
    sellPrice = getConsumableSellPrice(consumableToSell, save)
    save.money += sellPrice
    del save.consumables[consumableIndex]
    print(f"Sold {consumableToSell.toString()} for {save.money}")

def printConsumables(save):
    consumablesAmnt = len(save.consumables)
    if consumablesAmnt > 1:
        print(f"Consumables ({consumablesAmnt}/{save.consumablesLimit}):")
        iterator = 1
        for consumable in save.consumables:
            print(f"{iterator}: {consumable.toString()}")
    else:
        print("You have no consumables!")