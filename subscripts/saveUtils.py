from subscripts.spacesavers import *

class Save:
    def __init__(self, deck, ante, blindIndex, money, handLevels, illegalHandsDiscovered, consumables,
                 consumablesLimit, hand, jokers, jokerLimit):
        self.deck = deck
        self.ante = ante
        self.blindIndex = blindIndex
        self.money = money
        self.handLevels = handLevels
        self.illegalHandsDiscovered = illegalHandsDiscovered
        self.consumables = consumables
        self.consumablesLimit = consumablesLimit
        self.hand = hand
        self.jokers = jokers
        self.jokerLimit = jokerLimit

    def toDict(self):
        # turns the jokers and consumables into dicts
        consumables = []
        for consumable in self.consumables:
            consumables.append(consumable.toDict())
        return({
            "deck": self.deck,
            "ante": self.ante,
            "blindIndex": self.blindIndex,
            "money": self.money,
            "handLevels": self.handLevels,
            "illegalHandsDiscovered": self.illegalHandsDiscovered,
            "consumables": consumables,
            "consumablesLimit": self.consumablesLimit,
            "hand": self.hand,
            "jokers": self.jokers,
            "jokerLimit": self.jokerLimit
        })

    def hasJoker(self, name):
        for joker in self.jokers:
            if name in joker:
                return True
        return False

def createSaveFromDict(saveDict):
    return Save(deck=saveDict["deck"], ante=saveDict["ante"], blindIndex=saveDict["blindIndex"],
                money=saveDict["money"], handLevels=saveDict["handLevels"],
                illegalHandsDiscovered=saveDict["illegalHandsDiscovered"], consumables=saveDict["consumables"],
                consumablesLimit=saveDict["consumablesLimit"], hand=saveDict["hand"],
                jokers=saveDict["jokers"], jokerLimit=saveDict["jokerLimit"])

def saveGame(save):
    savejson("save", save.toDict())

def createBlankSave(deck):
    handLevels = {
        "High Card": {"level": 1, "chips": 5, "mult": 1},
        "Pair": {"level": 1, "chips": 10, "mult": 2},
        "Two Pair": {"level": 1, "chips": 20, "mult": 2},
        "Three Of A Kind": {"level": 1, "chips": 30, "mult": 3},
        "Straight": {"level": 1, "chips": 30, "mult": 4},
        "Flush": {"level": 1, "chips": 35, "mult": 4},
        "Full House": {"level": 1, "chips": 40, "mult": 4},
        "Four Of A Kind": {"level": 1, "chips": 60, "mult": 7},
        "Straight Flush": {"level": 1, "chips": 100, "mult": 8},
        "Royal Flush": {"level": 1, "chips": 100, "mult": 8},
        "Five Of A Kind": {"level": 1, "chips": 120, "mult": 12},
        "Flush House": {"level": 1, "chips": 140, "mult": 14},
        "Flush Five": {"level": 1, "chips": 160, "mult": 16}
    }
    if deck != "irl":
        deck = openjson("decks")[deck]
    return Save(deck=deck, ante=1, blindIndex=0, money=0, handLevels=handLevels,
                illegalHandsDiscovered=[], consumables=[], consumablesLimit=2, hand=[], jokers=[], jokerLimit=5)