from subscripts.cardUtils import *
from PIL import Image, ImageChops
from cardCreationAndRecognition.fiducialRecognizerTest import generateBoardForCard, arucoBoardsToCard
from subscripts.spacesavers import *

enhancersWidth = 69
enhancersHeight = 93
enhancersPixelGap = 2

# the origin is the top left
enhancersCoordsDict = {
    "base": [2, 1],
    "gold seal": [3, 1],
    "stone": [6, 1],
    "gold": [7, 1],
    "bonus": [2, 2],
    "mult": [3, 2],
    "wild": [4, 2],
    "lucky": [5, 2],
    "glass": [6, 2],
    "steel": [7, 2],
    "purple seal": [5, 5],
    "red seal": [6, 5],
    "blue seal": [7, 5],
}

editionsCoordsDict = {
    "foil": [2, 1],
    "holographic": [3, 1],
    "polychrome": [4, 1]
}

def createImageFromCard(card):
    if card.subset == "playing":
        cardImage = selectPlayingCardBackground(card)
        if card.enhancement != "stone":
            cardValueImage = returnCroppedImageByName("playing", card.number, card.suit)
            cardImage.paste(cardValueImage, (0, 0), cardValueImage)
        if card.edition is not None:
            cardEditionImage = returnCroppedImageByName("playing", card.edition)
            if card.edition == "polychrome":
                # reduces opacity if it's on glass
                if card.enhancement == "glass":
                    cardEditionImage = setOpacity(cardEditionImage, 0.5)
                # overlays only on nonwhite pixels
                r, g, b, a = cardImage.split()
                mask = ImageChops.invert(Image.merge("RGB", (r, g, b))).convert("L")
                cardImage.paste(cardEditionImage, (0, 0), mask)
            else:
                # cardEditionImage = setOpacity(cardEditionImage, 0.5)
                cardImage.paste(cardEditionImage, (0, 0), cardEditionImage)
        if card.seal != None:
            sealImage = returnCroppedImageByName("playing", card.seal + " seal")
            cardImage.paste(sealImage, (0, 0), sealImage)
    return cardImage


def selectPlayingCardBackground(card):
    if card.enhancement is None:
        return returnCroppedImageByName("playing", "base")
    else: return returnCroppedImageByName("playing", card.enhancement)


def selectPlayingCardValueImage(card):
    return

# polychrome only overlays on stuff that isn't white!
def selectPlayingCardOverlay(card):
    return

nonIntCoordsDict = {
    "H": 1,
    "C": 2,
    "D": 3,
    "S": 4,
    "J": 10,
    "Q": 11,
    "K": 12,
    "A": 13
}

def returnCroppedImageByName(subset, name, suit=None):
    if subset == "playing":
        if suit is not None:
            baseImageName = "cardSprites/playing.png"
            if name.isdigit():
                xCoord = int(name) - 1
            else:
                xCoord = nonIntCoordsDict[name]
            coords = [xCoord, nonIntCoordsDict[suit]]

        else:
            if name in ["polychrome", "holographic", "foil"]:
                baseImageName = "cardSprites/editions.png"
                coordsDict = editionsCoordsDict
            else:
                baseImageName = "cardSprites/enhancers.png"
                coordsDict = enhancersCoordsDict
            coords = coordsDict[name]
        baseImage = Image.open(baseImageName)
        topLeftX = ((coords[0] - 1) * enhancersWidth) + ((coords[0] - 1) * enhancersPixelGap) + 1
        topLeftY = ((coords[1] - 1) * enhancersHeight) + ((coords[1] - 1) * enhancersPixelGap) + 1
        crop = baseImage.crop((topLeftX, topLeftY, topLeftX + enhancersWidth, topLeftY + enhancersHeight))
        # if name == "glass":
        #     crop = fixGlass(crop)
        return crop


def fixGlass(image):
    baseImage = returnCroppedImageByName("playing", "base")
    baseImage.paste(image, (0, 0), image)
    pixels = baseImage.load()
    width, height = baseImage.size

    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            if a == 136:
                pixels[x, y] = (209, 230, 232, 255)

    return baseImage

    return

def setOpacity(image, amnt):
    image.putalpha(image.split()[3].point(lambda x: int(x * amnt)))
    return image


# createImageFromCard(Card(subset="playing", number="A", suit="H", edition="foil"))
def createTaggedCardImage(card, lookupTable):
    cardImage = createImageFromCard(card)
    lookupIndex = lookupTable.index(card.toBinary())
    generateBoardForCard(lookupIndex)
    fiducialImage = Image.open("testBoard.png")
    cardImage = cardImage.resize((690, 966), Image.Resampling.NEAREST)
    cardImage.paste(fiducialImage, (555, 50))
    fiducialImage = fiducialImage.rotate(180)
    cardImage.paste(fiducialImage, (30, 716))
    cardImage.save("test.png")


#TODO: Add tarot, joker, planet, spectral, and stone cards here
def generateCardPairingList():
    iterator = 0
    pairList = openjson("cardToArcuo.json", True)
    for suit in ["S", "C", "H", "D"]:
        for number in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]:
            for enhancement in [None, "bonus", "mult", "wild", "glass", "steel", "gold", "lucky"]:
                for edition in [None, "foil", "holographic", "polychrome"]:
                    for seal in [None, "gold", "red", "blue", "purple"]:
                        card = Card(subset="playing", suit=suit, number=number,
                                    enhancement=enhancement, edition=edition, seal=seal)
                        pairList.append(card.toBinary())
    savejson("cardToArcuo.json", pairList, True)

# createTaggedCardImage(Card(subset="playing", suit="S", number="A"), openjson("cardToArcuo.json", True))
# print("created!")
arucoBoardsToCard(openjson("cardToArcuo.json", True))