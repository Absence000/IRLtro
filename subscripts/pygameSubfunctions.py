import pygame, cv2, textwrap, time
import numpy as np
from cardCreationAndRecognition.finalArcuoTracking import pygameDisplayFoundCards
from subscripts.handFinderAndPointsAssigner import findBestHand
from PIL import Image
from subscripts.spacesavers import *

def drawWebcamAndReturnFoundCards(cap, lookupTable, screen, backupDetectedCardsScan, backupDetectedCardsScanTime,
                                  currentTime, save, frame=None):
    if frame is None:
        ret, frame = cap.read()
    rawFrame = frame.copy()
    frame, sortedDetectedCards = pygameDisplayFoundCards(lookupTable, frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # idk why I need to mirror and rotate it but whatever
    frame = np.fliplr(frame)
    frame = np.rot90(frame, k=1)

    # resizes to 540p
    # idk why this is height x width instead of width x height
    frame = cv2.resize(frame, (540, 960))
    surface = pygame.surfarray.make_surface(frame)
    screen.blit(surface, (320, 0))

    # it's easier to see where to put the cards if I draw lines on top
    drawRect(screen, (0, 0, 0), (320, 180, 960, 3))
    drawRect(screen, (0, 0, 0), (320, 360, 960, 3))

    # idk how much this really helps with flickering but if it can't find all the cards in the hand limit it goes to
    # an old scan less than 3 seconds old
    if len(sortedDetectedCards["middle"]) + len(sortedDetectedCards["lower"]) < save.handLimit:
        if currentTime - backupDetectedCardsScanTime < 3:
            sortedDetectedCards = backupDetectedCardsScan
    else:
        backupDetectedCardsScan = sortedDetectedCards
        backupDetectedCardsScanTime = currentTime


    return sortedDetectedCards, backupDetectedCardsScan, backupDetectedCardsScanTime, rawFrame

def openCamera(index):
    cap = cv2.VideoCapture(index)
    # right now it does 1080p but I might change this idk
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    return cap

# TODO: when it's the boss blind the outlines change to the color of the boss blind
def drawLeftBar(save, font, screen, colors, handType, level, score, chips, mult, camIndex):
    screenHeight = screen.height
    chipSymbol = pygame.image.load("cardSprites/white stake.png")

    leftBarOrigin = 20
    leftBarThickness = 300
    drawRect(screen, colors.lightUI, (leftBarOrigin, 0, leftBarThickness, screenHeight), colors.uiOutline)


    if save.state == "playing":
        # blind info display
        drawRect(screen, colors.darkUI, (leftBarOrigin, 20, leftBarThickness, 170), round=5)
        # TODO: Fix this it's dumb
        blindName = save.blindInfo[0]
        blindIndexList = ["Small Blind", "Big Blind", "Boss Blind"]
        blindIndex = blindIndexList.index(blindName)
        blindColor = colors.blindColors[blindIndex]
        drawRect(screen, colors.uiOutline, (leftBarOrigin + 5, 25, leftBarThickness - 10, 40), round=5)
        drawText(screen, blindName, font, colors.white, (leftBarOrigin + 150, 30), "center", 40)
        drawRect(screen, blindColor, (leftBarOrigin + 5, 70, leftBarThickness - 10, 115), round=5)
        screen.blit(getBlindSprite(blindName), (leftBarOrigin + 10, 125))
        drawRect(screen, colors.darkUI, (leftBarOrigin + 70, 120, 220, 60), round=5)
        drawText(screen, "Score at least", font, colors.white, (leftBarOrigin + 125, 122), "left", 20)
        smallerChipSymbol = pygame.transform.scale(chipSymbol, (20, 20))
        screen.blit(smallerChipSymbol, (leftBarOrigin + 75, 140))
        requiredScore = str(save.requiredScore)
        drawText(screen, requiredScore, font, colors.red, (leftBarOrigin + 100, 140), "left",
                 getOptimalTextSize(requiredScore, 30, 180))
        drawText(screen, "Reward:", font, colors.white, (leftBarOrigin + 75, 163), "left", 15)
        blindReward = save.blindInfo[2]
        dollarText = "$" * blindReward
        drawText(screen, dollarText, font, colors.yellow, (leftBarOrigin + 125, 160), "left", 20)


    # round score display
    roundScoreRectHeight = 200
    roundScoreRectThickness = 50
    drawRect(screen, colors.darkUI, (leftBarOrigin, roundScoreRectHeight, leftBarThickness, roundScoreRectThickness), round=5)
    drawText(screen, "Round\nscore", font, colors.white, (leftBarOrigin + 20, roundScoreRectHeight + 2), "left")
    innerRoundScoreRectOrigin = leftBarOrigin + 100
    innerRoundScoreRectThickness = leftBarThickness - 120
    drawRect(screen, colors.lightUI, (
    innerRoundScoreRectOrigin, roundScoreRectHeight + 5, innerRoundScoreRectThickness, roundScoreRectThickness - 10),
             round=5)
    screen.blit(chipSymbol, (innerRoundScoreRectOrigin + 5, roundScoreRectHeight + 10))

    score = str(score)

    drawText(screen, score, font, colors.white, (innerRoundScoreRectOrigin + 40, roundScoreRectHeight + 10),
             "left", getOptimalTextSize(score, 40, innerRoundScoreRectThickness - 40))

    # chips, mult, hand type, and level
    chipsXMultHeight = 260
    chipsXMultThickness = 150

    drawRect(screen, colors.darkUI, (leftBarOrigin, chipsXMultHeight, leftBarThickness, chipsXMultThickness), round=5)
    # hand type + level
    drawText(screen, handType, font, colors.white, (leftBarOrigin + 10, chipsXMultHeight + 20), "left",
             getOptimalTextSize(handType, 50, 250))
    # TODO: this changes color depending on the level
    if level != "":
        drawText(screen, f"lvl.{level}", font, colors.white, (leftBarOrigin + 260, chipsXMultHeight + 20),
                 "left")

    # chips and mult
    drawRect(screen, colors.blue, (leftBarOrigin + 10, chipsXMultHeight + 80, 120, 60), round=5)
    chips = str(chips)
    drawText(screen, chips, font, colors.white, (leftBarOrigin + 20, chipsXMultHeight + 90), "left",
             getOptimalTextSize(chips, 50, 110))

    drawRect(screen, colors.red, (leftBarOrigin + 170, chipsXMultHeight + 80, 120, 60), round=5)
    mult = str(mult)
    drawText(screen, mult, font, colors.white, (leftBarOrigin + 180, chipsXMultHeight + 90), "left",
             getOptimalTextSize(mult, 50, 110))

    drawText(screen, "X", font, colors.red, (leftBarOrigin + 150, chipsXMultHeight + 95), "center", 50)

    infoXOffset = leftBarOrigin + 100

    infoYOffset = 420
    # hands left
    handContainerX = infoXOffset + 10
    handContainerY = infoYOffset + 10
    drawRect(screen, colors.darkUI, (handContainerX, handContainerY, 80, 80), round=5)
    drawText(screen, "Hands", font, colors.white, (handContainerX + 40, handContainerY + 5), "center")
    drawRect(screen, colors.lightUI, (handContainerX + 10, handContainerY + 30, 60, 40), round=5)
    handsLeft = str(save.hands)
    drawText(screen, handsLeft, font, colors.blue, (handContainerX + 40, handContainerY + 35), "center",
             40)

    # discards left
    discardContainerX = handContainerX + 100
    drawRect(screen, colors.darkUI, (discardContainerX, handContainerY, 80, 80), round=5)
    drawText(screen, "Discards", font, colors.white, (discardContainerX + 40, handContainerY + 10),
             "center", size=20)
    drawRect(screen, colors.lightUI, (discardContainerX + 10, handContainerY + 30, 60, 40), round=5)
    discardsLeft = str(save.discards)
    drawText(screen, discardsLeft, font, colors.red, (discardContainerX + 40, handContainerY + 35), "center",
             40)

    # money
    moneyContainerY = handContainerY + 90
    drawRect(screen, colors.darkUI, (handContainerX, moneyContainerY, 180, 80), round=5)
    drawRect(screen, colors.lightUI, (handContainerX + 10, moneyContainerY + 5, 160, 70), round=5)
    money = f"${save.money}"
    drawText(screen, money, font, colors.yellow, (handContainerX + 90, moneyContainerY + 15), "center",
             getOptimalTextSize(money, 70, 160))

    # ante
    lastRowY = moneyContainerY + 90
    drawRect(screen, colors.darkUI, (handContainerX, lastRowY, 80, 80), round=5)
    drawText(screen, "Ante", font, colors.white, (handContainerX + 40, lastRowY + 10),
             "center", size=20)
    drawRect(screen, colors.lightUI, (handContainerX + 10, lastRowY + 30, 60, 40), round=5)
    ante = str(save.ante)
    drawText(screen, ante, font, colors.yellow, (handContainerX + 25, lastRowY + 35), "center",
             40)
    drawText(screen, "/8", font, colors.white, (handContainerX + 40, lastRowY + 40), "left")

    # round
    lastRowY = moneyContainerY + 90
    drawRect(screen, colors.darkUI, (discardContainerX, lastRowY, 80, 80), round=5)
    drawText(screen, "Round", font, colors.white, (discardContainerX + 40, lastRowY + 10),
             "center", size=20)
    drawRect(screen, colors.lightUI, (discardContainerX + 10, lastRowY + 30, 60, 40), round=5)
    round = str(save.round)
    drawText(screen, round, font, colors.yellow, (discardContainerX + 40, lastRowY + 35), "center",
             40)

    # run info
    # TODO: once everything else is done add functionality to this
    drawRect(screen, colors.red, (leftBarOrigin + 10, infoYOffset, 80, 130), round=5)
    drawText(screen, "Run\nInfo\n(event-\nually)", font, colors.white, (leftBarOrigin + 50, infoYOffset + 20),
             "center")

    # camera switching
    drawRect(screen, colors.darkUI, (leftBarOrigin + 10, infoYOffset + 140, 80, 130), round=5)
    drawText(screen, f"Cam {camIndex}", font, colors.white, (leftBarOrigin + 20, infoYOffset + 150),
             "left")

    camAddRect = (leftBarOrigin + 20, infoYOffset + 180, 60, 35)
    drawRect(screen, colors.yellow, camAddRect, round=5)
    drawText(screen, "+", font, colors.white, (leftBarOrigin + 43, infoYOffset + 183), "left", size=40)

    camSubRect = (leftBarOrigin + 20, infoYOffset + 225, 60, 35)
    drawRect(screen, colors.red, camSubRect, round=5)
    drawText(screen, "-", font, colors.white, (leftBarOrigin + 43, infoYOffset + 228), "left", size=40)

    return [{"name": "+",
             "rect": camAddRect},
            {"name": "-",
             "rect": camSubRect}]

blindImageDict = {
    "Small Blind": 0,
    "Big Blind": 1,
    "Boss Blind": 30
}

def getBlindSprite(name):
    blindSprites = Image.open("cardSprites/blindChips.png")
    blindImageIndex = blindImageDict[name]
    size = 34
    topLeftY = blindImageIndex * size
    bottomRightY = (blindImageIndex + 1) * size
    croppedImage = blindSprites.crop((0, topLeftY, size, bottomRightY))
    formattedImage = pygame.image.frombytes(croppedImage.tobytes(), (size, size), "RGBA")
    return pygame.transform.scale(formattedImage, (50, 50))

def drawButtons(save, screen, colors, font):
    buttonY = 580

    playRect = (370, 580, 200, 100)
    drawRect(screen, colors.darkUI, (370, buttonY+5, 202, 102), round=8)
    drawRect(screen, colors.blue, playRect, colors.lightUI, round=8)
    drawText(screen, "Play hand\nUse", font, colors.white, (380, buttonY + 10), "left", 40)

    discardX = 580
    discardRect = (discardX, 580, 200, 100)
    drawRect(screen, colors.darkUI, (discardX, buttonY + 5, 202, 102), round=8)
    drawRect(screen, colors.red, discardRect, colors.lightUI, round=8)
    drawText(screen, "Discard\nSell", font, colors.white, (discardX + 10, buttonY + 10), "left", 40)

    return [{"name": "play",
             "rect": playRect},
            {"name": "discard",
             "rect": discardRect}]

def drawCardCounter(save, font, screen, colors, foundCards):

    prunedFoundCards = foundCards.copy()
    del prunedFoundCards["unpairedTags"]

    xOrigin = 890
    yOrigin = 550

    drawRect(screen, colors.lightUI, (xOrigin - 10, yOrigin - 10, 420, 180))
    drawRect(screen, colors.darkUI, (xOrigin - 5, yOrigin - 5, 410, 170), round=8)

    mode = "handFinder"
    ind = 0
    handCards = prunedFoundCards["middle"]

    for card in handCards:
        cardType = type(card).__name__
        if cardType != "Card":
            mode = "analysis"
            cardToAnalyze = card
        ind += 1

    # probably should have called them these from the start but I probably would forget
    subsetDict = {
        "upper": "J/C",
        "middle": "Selection",
        "lower": "Hand"
    }

    iterator = 0
    for subset, cards in prunedFoundCards.items():
        trackedCardsInThirdOfScreen = []
        for card in cards:
            trackedCardsInThirdOfScreen.append(card.toString(mode="fancy"))
        finishedMessage = f"{subsetDict[subset]}\n{'\n'.join(trackedCardsInThirdOfScreen)}"
        yOffset = 0
        overflowTrackedCardsAmount = len(trackedCardsInThirdOfScreen) - 7
        if overflowTrackedCardsAmount > 0:
            yOffset = 20 * (overflowTrackedCardsAmount)
            drawRect(screen, colors.darkUI, (xOrigin + iterator - 5, yOrigin-yOffset - 5, 143, yOffset + 5), round=8)

        drawText(screen, finishedMessage, font, colors.white, (xOrigin + iterator, yOrigin - yOffset), "left",
                 getOptimalTextSize(finishedMessage, 20, 133))
        iterator += 133

    if mode == "analysis":
        return cardToAnalyze, None
    else:
        handType = findBestHand(handCards)[0]
        handInfo = save.handLevels[handType]
        return handType, handInfo

def drawAnalysisPopup(save, font, screen, colors, cardToAnalyze):
    xOrigin = 450
    yOrigin = 30

    drawRect(screen, colors.lightUI, (xOrigin - 10, yOrigin-10, 220, 220), round=7)
    drawRect(screen, colors.darkUI, (xOrigin - 5, yOrigin - 5, 210, 210), round=7)
    message = textwrap.fill(cardToAnalyze.toString(), 20)
    drawText(screen, message, font, colors.white, (xOrigin, yOrigin), "left")

# TODO: Figure out a way to get this displaying correctly if there's duplicate cards
def displayChainEvent(event, screen, font):

    # this is weird since the camera gets halved in size and offset 320 pixels to the right
    cardOrigin = event.card.coords
    newX = int((cardOrigin[0]/2) + 320)
    newY = int(cardOrigin[1]/2)

    drawRect(screen, event.color, (newX - 20, newY - 20, 40, 40), round=7)
    drawText(screen, event.text, font, (255, 255, 255), (newX, newY-10), "center")



def drawBlindSelectScreen(save, colors):
    return
    # selectedBlind = save.blindIndex
    # drawRect(screen, colors.darkUI)

def drawRect(screen, color, rect, outline=None, round=None):
    if round is not None:
        borderRadius = round
    else:
        borderRadius = 0
    if outline is not None:
        x, y, width, height = rect
        outlineRect = (x-3, y-3, width+6, height+6)
        pygame.draw.rect(screen, outline, outlineRect, border_radius=borderRadius)
    pygame.draw.rect(screen, color, rect, border_radius=borderRadius)

def getOptimalTextSize(text, defaultSize, sizeLimit):
    individualLines = text.split("\n")
    longestLineLength = len(max(individualLines, key=len))
    pixelLength = int(0.45 * defaultSize * longestLineLength)
    if pixelLength <= sizeLimit:
        return defaultSize
    else:
        return int(sizeLimit/(0.45*longestLineLength))

def drawText(screen, text, font, color, coords, centering="center", size=None):
    if size is None:
        label = font.render(text, True, color)
    else:
        font = pygame.font.Font("cardSprites/font/m6x11.ttf", size)
        label = font.render(text, True, color)
    textRect = label.get_rect()

    if centering == "left":
        textRect.topleft = coords
    elif centering == "right":
        textRect.topright = coords
    else:
        textRect.midtop = coords

    screen.blit(label, textRect)