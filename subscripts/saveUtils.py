from subscripts.spacesavers import *
from subscripts.jokers import Joker
from subscripts.cardUtils import Card
from subscripts.planetCards import Planet
from subscripts.tarotCards import Tarot
from subscripts.shop import Shop, createShopFromDict

class Save:
    def __init__(self, saveDict):
        deck = []
        for card in saveDict["deck"]:
            deck.append(Card(card))
        self.deck = deck
        self.ante = saveDict["ante"]
        self.blindIndex = saveDict["blindIndex"]
        self.state = saveDict["state"]
        self.hands = saveDict["hands"]
        self.handLimit = saveDict["handLimit"]
        self.discards = saveDict["discards"]
        self.shop = createShopFromDict(saveDict["shop"])
        self.money = saveDict["money"]
        self.handLevels = saveDict["handLevels"]
        self.illegalHandsDiscovered = saveDict["illegalHandsDiscovered"]
        consumables = []
        for consumable in saveDict["consumables"]:
            if consumable["type"] == "planet":
                consumables.append(Planet(consumable["name"], consumable["negative"]))
            if consumable["type"] == "tarot":
                consumables.append(Tarot(consumable["name"], consumable["negative"]))
        self.consumables = consumables
        self.consumablesLimit = saveDict["consumablesLimit"]
        self.hand = saveDict["hand"]
        jokers = []
        for joker in saveDict["jokers"]:
            jokers.append(Joker(joker))
        self.jokers = jokers
        self.jokerLimit = saveDict["jokerLimit"]
        self.requiredScore = saveDict["requiredScore"]
        self.blindInfo = saveDict["blindInfo"]

        discardedCards = []
        for card in saveDict["discardedCards"]:
            discardedCards.append(Card(card))
        self.discardedCards = discardedCards

        playedCards = []
        for card in saveDict["playedCards"]:
            playedCards.append(Card(card))
        self.playedCards = playedCards
        self.score = saveDict["score"]
        self.round = saveDict["round"]
        self.irl = saveDict["irl"]


    def toDict(self):
        # turns the jokers, consumables, and deck into dicts
        consumables = []
        for consumable in self.consumables:
            consumables.append(consumable.toDict())
        jokers = []
        for joker in self.jokers:
            jokers.append(joker.toDict())

        deck = []
        for card in self.deck:
            deck.append(card.toDict())

        consumables = []
        for consumable in self.consumables:
            if isinstance(consumable, Planet):
                consumables.append(consumable.toDict())
            elif isinstance(consumable, Tarot):
                consumables.append(consumable.toDict())

        hand = []
        for card in self.hand:
            hand.append(card.toDict())

        discardedCards = []
        for card in self.discardedCards:
            discardedCards.append(card.toDict())

        playedCards = []
        for card in self.playedCards:
            playedCards.append(card.toDict())

        saveDict = {
            "deck": deck,
            "ante": self.ante,
            "blindIndex": self.blindIndex,
            "state": self.state,
            "hands": self.hands,
            "discards": self.discards,
            "shop": self.shop.toDict(),
            "money": self.money,
            "handLevels": self.handLevels,
            "illegalHandsDiscovered": self.illegalHandsDiscovered,
            "consumables": consumables,
            "consumablesLimit": self.consumablesLimit,
            "hand": hand,
            "handLimit": self.handLimit,
            "jokers": jokers,
            "jokerLimit": self.jokerLimit,
            "requiredScore": self.requiredScore,
            "blindInfo": self.blindInfo,
            "discardedCards": discardedCards,
            "playedCards": playedCards,
            "score": self.score,
            "round": self.round,
            "irl": self.irl
        }
        return saveDict

    def hasJoker(self, name):
        for joker in self.jokers:
            if joker.name == name:
                return True
        return False

def createSaveFromDict(saveDict):
    return Save(saveDict)

def saveGame(save):
    savejson("save", save.toDict())

def createBlankSave(deck, irl):
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
    deck = openjson("decks")[deck]
    return Save({
        "deck": deck,
        "ante": 1,
        "blindIndex": 0,
        "state": "selectingBlind",
        "hands": 4,
        "discards": 4,
        "shop": {
            "cards": [[None, None], [None, None]],
            "packs": [[None, None], [None, None]],
            "vouchers": [None],
            "rerollCost": 0
        },
        "money": 0,
        "handLevels": handLevels,
        "illegalHandsDiscovered": [],
        "consumables": [],
        "consumablesLimit": 2,
        "hand": [],
        "handLimit": 8,
        "jokers": [],
        "jokerLimit": 5,
        "requiredScore": 0,
        "blindInfo": 0,
        "discardedCards": [],
        "playedCards": [],
        "score": 0,
        "round": 1,
        "irl": irl
    })

def getJokerByName(save, name):
    for joker_name, joker_data in save.jokers:
        if joker_name == name:
            return joker_data
    return None