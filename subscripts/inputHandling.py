import cv2, os, shutil
from subscripts.spacesavers import *
from cardCreationAndRecognition.cardImageCreator import createTaggedCardImage

def captureImage():
    cap = cv2.VideoCapture(2)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Capture a single frame
    ret, frame = cap.read()

    if ret:
        # Save the image to the specified path
        cv2.imwrite("hand.png", frame)
    else:
        print("Error: Could not capture image.")

    # Release the webcam
    cap.release()
    cv2.destroyAllWindows()

# def returnCardsFromImage():
#     return returnFoundCards(openjson("cardCreationAndRecognition/cardToArcuo old.json", True))


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
                shutil.rmtree(file_path)  # Deletes subdirectories and their contents
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

def prepareCardForPrinting(card, keep=True):
    if not keep:
        clearPrintFolder()
    lookupTable = openjson("cardCreationAndRecognition/cardToArcuo.json", True)
    createTaggedCardImage(card, lookupTable)

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
    save.consumables = []
    for card in foundCards["upper"]:
        cardType = type(card).__name__
        if cardType == "Joker":
            save.jokers.append(card)
        else:
            save.consumables.append(card)

    return selectedHand

def pushIRLInputIntoSave(save):
    from subscripts.cardUtils import Card
    from subscripts.jokers import Joker
    from subscripts.planetCards import Planet
    from subscripts.tarotCards import Tarot
    from subscripts.spectralCards import Spectral
    inputCardsDict = openjson("sortedDetectedCards")
    inputCards = {
        "upper": [],
        "middle": [],
        "lower": []
    }
    for key, cardList in inputCardsDict.items():
        for cardDict in cardList:
            if len(cardDict) == 2:
                inputCards[key].append(Joker(cardDict))
            elif "suit" in cardDict.keys():
                inputCards[key].append(Card(cardDict))
            elif "type" in cardDict.keys():
                type = cardDict["type"]
                name = cardDict["name"]
                negative = cardDict["negative"]
                inputCards[key].append(eval(type)(name, negative))
    # inputCards = {
    #     key: [Card(cardDict) for cardDict in cardList]
    #     for key, cardList in inputCardsDict.items()
    # }
    selectedHand = inputCards["middle"]
    save.hand = inputCards["lower"]
    jokers = []
    consumables = []
    for card in inputCards["upper"]:
        if isinstance(card, Joker):
            jokers.append(card)
        else:
            consumables.append(card)
    save.jokers = jokers
    save.consumables = consumables
    return selectedHand