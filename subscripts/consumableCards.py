from subscripts.cardUtils import Card
from subscripts.planetCards import usePlanetCard

#TODO: get tarots and spectrals working here too
def useConsumable(consumable, save):
    if consumable.subset == "planet":
        usePlanetCard(consumable, save)