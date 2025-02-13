from spacesavers import *

class Save:
    def __init__(self, deck, ante, blindIndex, money, handLevels, illegalHandsDiscovered):
        self.deck = deck
        self.ante = ante
        self.blindIndex = blindIndex
        self.money = money
        self.handLevels = handLevels
        self.illegalHandsDiscovered = illegalHandsDiscovered

    def toDict(self):
        return({
            "deck": self.deck,
            "ante": self.ante,
            "blindIndex": self.blindIndex,
            "money": self.money,
            "handLevels": self.handLevels,
            "illegalHandsDiscovered": self.illegalHandsDiscovered
        })

def createSaveFromDict(saveDict):
    return Save(deck=saveDict["deck"], ante=saveDict["ante"], blindIndex=saveDict["blindIndex"],
                money=saveDict["money"], handLevels=saveDict["handLevels"],
                illegalHandsDiscovered=saveDict["illegalHandsDiscovered"])

def saveGame(save):
    savejson("save", save.toDict())

def createBlankSave():
    handLevels = {"High Card": 1,
              "Pair": 1,
              "Two Pair": 1,
              "Three Of A Kind": 1,
              "Straight": 1,
              "Flush": 1,
              "Full House": 1,
              "Four Of A Kind": 1,
              "Straight Flush": 1,
              "Five Of A Kind": 1,
              "Flush House": 1,
              "Flush Five": 1}
    return Save(deck=openjson("decks")["standard"], ante=1, blindIndex=0, money=0, handLevels=handLevels,
                illegalHandsDiscovered=[])