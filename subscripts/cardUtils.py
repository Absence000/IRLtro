from subscripts.spacesavers import *

suitAbrToName = {
    "S": "♠",
    "C": "♣",
    "D": "♦",
    "H": "♥"
}
valueAbrToName = {
    "J": "Jack",
    "Q": "Queen",
    "K": "King",
    "A": "Ace"
}

class Card:
    def __init__(self, subset, number, suit=None, enhancement=None, edition=None, seal=None, retriggerCount=None):
        self.subset = subset
        self.number = number
        self.enhancement = enhancement
        self.edition = edition
        self.seal = seal
        self.suit = suit
        self.retriggerCount = retriggerCount

    def toDict(self):
        return {
            "subset": self.subset,
            "number": self.number,
            "enhancement": self.enhancement,
            "edition": self.edition,
            "seal": self.seal,
            "suit": self.suit,
            "retriggerCount": self.retriggerCount
        }

    def toString(self):
        if self.subset == "playing":
            descriptor = ""
            if self.edition is not None:
                descriptor += self.edition.capitalize() + " "
            if self.enhancement is not None:
                descriptor += self.enhancement.capitalize() + " "

            #TODO: add fancy mode here for proper title

            # if self.number.isdigit():
            #     descriptor += self.number + " of "
            # else:
            #     descriptor += valueAbrToName[self.number] + " of "

            return descriptor + self.number + suitAbrToName[self.suit]
        if self.subset == "planet":
            return f"{self.number} (Upgrade {openjson('planetCards/planetCardsDict')[self.number]['hand']})"


# takes in a dictionary of card values and returns a Card object
def createCardFromDict(cardDict):
    return Card(subset=cardDict["subset"], number=cardDict["number"], suit=cardDict["suit"],
                enhancement=cardDict["enhancement"], edition=cardDict["edition"],
                seal=cardDict["seal"], retriggerCount=cardDict["retriggerCount"])