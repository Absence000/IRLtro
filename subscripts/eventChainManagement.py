from subscripts.spacesavers import *

class EventChain:
    def __init__(self):
        self.events = []

    def save(self):
        finishedChain = []
        for link in self.events:
            finishedChain.append(link.toDict())
        savejson("eventChain", finishedChain)

    def add(self, type, text, card, chips, mult):
        self.events.append(Event(type, text, card, chips, mult))

class Event:
    def __init__(self, type, text, card, chips, mult):
        self.type = type
        if self.type is not "visual":
            self.value = text
            if self.type == "multmult":
                symbol = "x"
            else:
                symbol = "+"
            self.text = f"{symbol}{text}"
        else:
            self.value = None
            self.text = text

        if self.type == "chip":
            self.color = (0, 0, 255)
        if self.type == "mult" or self.type == "multmult":
            self.color = (255, 0, 0)
        else:
            self.color = (255, 255, 0)
        self.card = card

        self.chips = chips
        self.mult = mult

    def toDict(self):
        return {
            "type": self.type,
            "value": self.value,
            "text": self.text,
            "color": self.color,
            "card": self.card.toDict(),
            "chips": self.chips,
            "mult": self.mult
        }