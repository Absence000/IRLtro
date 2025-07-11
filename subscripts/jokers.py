import math

editionSellValueDict = {
    "foil": 2,
    "holographic": 3,
    "polychrome": 5,
    "negative": 5
}
def getJokerSellValue(joker):
    # yes I know the joker is stored as a dict and all the other cards are objects deal with it
    # TODO: Figure out how to get this working with Gift Card
    jokerData = joker[1]
    if joker[0] == "Egg":
        return jokerData["sellValue"]
    sellCost = max(1, math.floor(jokerData["cost"]/2))
    if "edition" in jokerData:
        sellCost += editionSellValueDict[jokerData["edition"]]
    return sellCost
