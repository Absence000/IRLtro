from collections import Counter
import random

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

            descriptor += self.number + suitAbrToName[self.suit]
            return(descriptor)


# takes in a dictionary of card values and returns a Card object
def createCardFromDict(cardDict):
    return Card(subset=cardDict["subset"], number=cardDict["number"], suit=cardDict["suit"],
                enhancement=cardDict["enhancement"], edition=cardDict["edition"],
                seal=cardDict["seal"], retriggerCount=cardDict["retriggerCount"])


# figures out what poker hand the player has, and specifies what cards to add the points to
# TODO: add an override for the joker that changes how many cards that get scored points
def findBestHand(hand):
    handValueList = []
    handSuitList = []
    handLength = 0
    for card in hand:
        if card.enhancement != "stone":
            handValueList.append(card.number)
            if card.enhancement == "wild":
                handSuitList.append("W")
            else:
                handSuitList.append(card.suit)
            handLength += 1
    straight = handIsStraight(handValueList)
    flush = handIsFlush(handSuitList)
    countList = numberOfMatchingCards(handValueList)


    #illegal hands
    if handLength == 5:
        if len(countList) == 1 and flush:
            return "Flush Five", "all"
        if len(countList) == 2 and flush:
            notAFourOfAKind = True
            for count in countList:
                if count[1] == 4:
                    notAFourOfAKind = False
            if notAFourOfAKind:
                return "Flush House", "all"
        if len(countList) == 1:
            return "Five Of A Kind", "all"


    # legal hands
    if straight and flush:
        return ("Royal Flush", "all") if "10" in handValueList and "A" in handValueList else ("Straight Flush", "all")
    for count in countList:
        if count[1] == 4:
            return "Four Of A Kind", [count[0]]
    if handLength == 5 and len(countList) == 2:
        return "Full House", "all"
    if flush:
        return "Flush", "all"
    if straight:
        return "Straight", "all"
    for count in countList:
        if count[1] == 3:
            return "Three Of A Kind", [count[0]]
    pairCount = 0
    pairCards = []
    for count in countList:
        if count[1] == 2:
            pairCount += 1
            pairCards.append(count[0])
    if pairCount == 2:
        return "Two Pair", pairCards
    if pairCount == 1:
        return "Pair", pairCards

    #all stone card error handling
    try:
        highestCard = [turnNumberBackIntoPlayingCardValue(turnHandValueIntoNumbersAndSort(handValueList)[-1])]
    except:
        highestCard = "all"
    return "High Card", highestCard


# returns true if the hand is a straight (all the numbers are in a row)
# aces can be either 1 or 14 in this but not both
# TODO: Add overrides for the hand value length requirement joker
def handIsStraight(handValueList):
    if len(handValueList) == 5:
        testLists = [turnHandValueIntoNumbersAndSort(handValueList), turnHandValueIntoNumbersAndSort(handValueList, 1)]
        for testList in testLists:
            if valuesAreConsecutive(testList):
                return True
    return False


# checks if all the values in the list are consecutive
# TODO: add something for the shortcut joker to work
def valuesAreConsecutive(testList):
    return all(testList[i] + 1 == testList[i + 1] for i in range(len(testList) - 1))


# returns true if the hand is a flush (all the suits are the same)
# works with wild cards
# TODO: add hand limit stuff
def handIsFlush(handSuitList):
    if len(handSuitList) == 5:
        if "W" not in handSuitList:
            return len(set(handSuitList)) == 1
        elif len(set(handSuitList)) <= 2:
            return True


# reformats the card number list as a list of [number, timesInHand]
# used in four of a kind, full house, three of a kind, two pair, and pair
def numberOfMatchingCards(handValueList):
    countDict = Counter(handValueList)
    return [[num, count] for num, count in countDict.items()]

faceCardValueDict = {
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14
}

# turns the list of hand values into a list of numbers sorted bottom to top
def turnHandValueIntoNumbersAndSort(handValueList, aceOverride=False):
    sortedNumList = []
    for number in handValueList:
        try:
            sortedNumList.append(int(number))
        except:
            if aceOverride and number == "A":
                sortedNumList.append(1)
            else:
                sortedNumList.append(faceCardValueDict[number])
    sortedNumList.sort()
    return sortedNumList


# used for returning the value of the card that was affected by the play
def turnNumberBackIntoPlayingCardValue(number):
    if 2 <= number <= 10:
        return str(number)
    else:
        return [key for key, value in faceCardValueDict.items() if value == number][0]

handDictionary = {
    "High Card": {"chips": 5, "mult": 1},
    "Pair": {"chips": 10, "mult": 2},
    "Two Pair": {"chips": 20, "mult": 2},
    "Three Of A Kind": {"chips": 30, "mult": 3},
    "Straight": {"chips": 30, "mult": 4},
    "Flush": {"chips": 35, "mult": 4},
    "Full House": {"chips": 40, "mult": 4},
    "Four Of A Kind": {"chips": 60, "mult": 7},
    "Straight Flush": {"chips": 100, "mult": 8},
    "Royal Flush": {"chips": 100, "mult": 8},
    "Five Of A Kind": {"chips": 120, "mult": 12},
    "Flush House": {"chips": 140, "mult": 14},
    "Flush Five": {"chips": 160, "mult": 16}
}


chips = 0
mult = 0
multmult = 1

# now that we identified the hand and the cards that need to be assigned the points, we can figure out how many points
# to add!
# TODO: this is where most of the joker effects come in oh god
def calcPointsFromHand(hand, handData, unselectedHand, save):
    # gets the base chips and mult
    handType = handData[0]
    affectedCards = handData[1]

    global chips
    global mult
    global multmult

    chips = 0
    mult = 0
    multmult = 1

    baseChips = handDictionary[handType]["chips"]
    baseMult = handDictionary[handType]["mult"]

    chips = baseChips
    mult = baseMult

    print(handType)
    print(f"Triggered cards: {affectedCards}")

    # iterates through each card in the hand to award points
    for card in hand:
        if affectedCards == "all" or card.number in affectedCards or card.enhancement == "stone":
            triggerCard(card, save)

    steelCardMult = 1

    # now does the same for steel cards in the unselected hand to multiply the multiplier independently of the multmult
    for card in unselectedHand:
        if card.enhancement == "steel":
            if card.seal == "red":
                steelCardMult *= 1.5
            steelCardMult *= 1.5
    #TODO: more joker stuff here
    print(f"{chips} X {mult * multmult * steelCardMult}")
    return(chips * mult * multmult, affectedCards)



def triggerCard(card, save):
    # A = 11 chips, face cards = 10 chips, all numbered cards are = their value
    global chips
    global mult
    global multmult
    try:
        baseCardChipAmount = int(card.number)
    except:
        if card.number == "A":
            baseCardChipAmount = 11
        elif card.number == "S":
            baseCardChipAmount = 50
        else:
            baseCardChipAmount = 10
    baseCardMultAmount = 0
    # TODO: put all the card effect stuff here
    if card.enhancement == "bonus":
        baseCardChipAmount += 30
    elif card.enhancement == "mult":
        baseCardMultAmount += 4
    elif card.enhancement == "lucky":
        if random.randint(1, 5) == 1:
            baseCardMultAmount += 20
            print("+20 mult from lucky card!")
        if random.randint(1, 15) == 1:
            save.money += 20
            print("Won $20 with a lucky card!")
    elif card.enhancement == "glass":
        multmult = multmult * 2

    if card.edition == "foil":
        baseCardChipAmount += 50
    elif card.edition == "holographic":
        baseCardMultAmount += 10
    elif card.edition == "polychrome":
        multmult = multmult * 1.5

    if card.seal == "red":
        if card.retriggerCount is None:
            card.retriggerCount = 1
            print(f"Retriggering {card.number}!")
            triggerCard(card)
    chips += baseCardChipAmount
    mult += baseCardMultAmount


def testPointSystem():
    hand = [Card(subset="playing", number="A", suit="S", seal="red", enhancement="wild"),
            Card(subset="playing", number="J", suit="S", seal="red", enhancement="wild"),
            Card(subset="playing", number="Q", suit="D", seal="red", enhancement="wild", edition="polychrome"),
            Card(subset="playing", number="A", suit="S", seal="red", enhancement="wild"),
            Card(subset="playing", number="A", suit="S", seal="red", enhancement="wild")]

    unselectedHand = [Card(subset="playing", number="A", suit="S", seal="red", enhancement="steel")]


    print(calcPointsFromHand(hand, findBestHand(hand), unselectedHand))


