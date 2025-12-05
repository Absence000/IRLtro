import cv2, os, shutil
from subscripts.spacesavers import *
from cardCreationAndRecognition.cardImageCreator import createTaggedCardImage

def clearPrintFolder():

    path = "print"

    if not os.path.exists(path):
        print(f"Error: Folder '{path}' does not exist.")
        return

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def prepareCardForPrinting(card, keep=True):
    if not keep:
        clearPrintFolder()
    lookupTable = openjson("cardCreationAndRecognition/cardToArcuo final.json", True)
    prunedCard = card.copy()
    if hasattr(prunedCard, "enhancement") and prunedCard.enhancement != "stone":
        prunedCard.enhancement = None
    prunedCard.edition = None
    prunedCard.seal = None
    createTaggedCardImage(prunedCard, lookupTable)

def CLDisplayHand(hand):
    handDisplay = []
    listNum = 1
    for handCard in hand:
        handDisplay.append(str(listNum) + ": " + handCard.toString())
        listNum += 1

    return('\n'.join(handDisplay))


def prepareSelectedCards(save, foundCards):
    selectedHand = foundCards["middle"]
    save.hand = foundCards["lower"]
    save.jokers = []
    for card in foundCards["upper"]:
        cardType = type(card).__name__
        if cardType == "Joker":
            for joker in save.jokersInPlay:
                if joker.id == card.id:
                    save.jokers.append(card)

    return selectedHand

def alreadyHasConsumable(save, consumable):
    for alreadyOwnedConsumable in save.consumables:
        if consumable.name == alreadyOwnedConsumable.name:
            return True
    return False