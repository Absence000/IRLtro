from subscripts.cardUtils import Card
from PIL import Image, ImageChops

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
        cardValueImage = returnCroppedImageByName("playing", card.number, card.suit)
        cardImage.paste(cardValueImage, (0, 0), cardValueImage)
        if card.edition is not None:
            cardEditionImage = returnCroppedImageByName("playing", card.edition)
            if card.edition == "polychrome":
                # reduces opacity to 50%
                cardEditionImage.putalpha(cardEditionImage.split()[3].point(lambda x: int(x * 0.5)))
                # overlays only on nonwhite pixels
                r, g, b, a = cardImage.split()
                mask = ImageChops.invert(Image.merge("RGB", (r, g, b))).convert("L")
                cardImage.paste(cardEditionImage, (0, 0), mask)
            elif card.edition is not None:
                cardImage.paste(cardEditionImage, (0, 0), cardEditionImage)
    cardImage.show()

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
            print(coords)

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
        return crop


def turnTransparentPixelsIntoSpecifiedColor():
    return


createImageFromCard(Card(subset="playing", number="A", suit="H", edition="polychrome"))