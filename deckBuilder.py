import json

from subscripts.spacesavers import *
from subscripts.cardUtils import Card


# this was for testing the scoring system in the command line with weird decks
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