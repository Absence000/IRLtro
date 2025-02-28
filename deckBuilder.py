import json

from subscripts.spacesavers import *
from subscripts.cardUtils import Card


# used to make decks
# right now it just does the standard one
def createDeck(name):
    deck = openjson("decks")
    deck[name] = []
    suits = ["S", "C", "D", "H"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    for suit in suits:
        for value in values:
            deck[name].append(Card(subset="playing", number="A", suit="S", enhancement="gold").toDict())
    savejson("decks", deck)

# createDeck("gold test")