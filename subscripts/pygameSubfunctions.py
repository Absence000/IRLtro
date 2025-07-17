import pygame, cv2, textwrap
import numpy as np
from cardCreationAndRecognition.finalArcuoTracking import pygameDisplayFoundCards
from subscripts.handFinderAndPointsAssigner import findBestHand
from subscripts.spacesavers import *

def drawWebcamAndReturnFoundCards(cap, lookupTable, screen):
    ret, frame = cap.read()
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

    return sortedDetectedCards

def openCamera(index):
    cap = cv2.VideoCapture(index)
    # right now it does 1080p but I might change this idk
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    return cap

def drawLeftBar(save, font, screen, colors, handType, level, score, chips, mult):
    screenHeight = screen.height

    # yes ik this is dumb but I hate functions with a lot of arguments and I don't want to go through and turn every
    # color into a dict entry
    lightUI = colors["lightUI"]
    uiOutline = colors["uiOutline"]
    darkUI = colors["darkUI"]
    white = colors["white"]
    blue = colors["blue"]
    red = colors["red"]
    yellow = colors["yellow"]

    leftBarOrigin = 20
    leftBarThickness = 300
    drawRect(screen, lightUI, (leftBarOrigin, 0, leftBarThickness, screenHeight), uiOutline)

    # round score display
    roundScoreRectHeight = 200
    roundScoreRectThickness = 50
    drawRect(screen, darkUI, (leftBarOrigin, roundScoreRectHeight, leftBarThickness, roundScoreRectThickness), round=5)
    drawText(screen, "Round\nscore", font, white, (leftBarOrigin + 20, roundScoreRectHeight + 2), "left")
    innerRoundScoreRectOrigin = leftBarOrigin + 100
    innerRoundScoreRectThickness = leftBarThickness - 120
    drawRect(screen, lightUI, (
    innerRoundScoreRectOrigin, roundScoreRectHeight + 5, innerRoundScoreRectThickness, roundScoreRectThickness - 10),
             round=5)
    chipSymbol = pygame.image.load("cardSprites/white stake.png")
    screen.blit(chipSymbol, (innerRoundScoreRectOrigin + 5, roundScoreRectHeight + 10))

    score = str(score)

    drawText(screen, score, font, white, (innerRoundScoreRectOrigin + 40, roundScoreRectHeight + 10),
             "left", getOptimalTextSize(score, 40, innerRoundScoreRectThickness - 40))

    # chips, mult, hand type, and level
    chipsXMultHeight = 260
    chipsXMultThickness = 150

    drawRect(screen, darkUI, (leftBarOrigin, chipsXMultHeight, leftBarThickness, chipsXMultThickness), round=5)
    # hand type + level
    drawText(screen, handType, font, white, (leftBarOrigin + 10, chipsXMultHeight + 20), "left",
             getOptimalTextSize(handType, 50, 250))
    # TODO: this changes color depending on the level
    if level != "":
        drawText(screen, f"lvl.{level}", font, white, (leftBarOrigin + 260, chipsXMultHeight + 20),
                 "left")

    # chips and mult
    drawRect(screen, blue, (leftBarOrigin + 10, chipsXMultHeight + 80, 120, 60), round=5)
    chips = str(chips)
    drawText(screen, chips, font, white, (leftBarOrigin + 20, chipsXMultHeight + 90), "left",
             getOptimalTextSize(chips, 50, 110))

    drawRect(screen, red, (leftBarOrigin + 170, chipsXMultHeight + 80, 120, 60), round=5)
    mult = str(mult)
    drawText(screen, mult, font, white, (leftBarOrigin + 180, chipsXMultHeight + 90), "left",
             getOptimalTextSize(mult, 50, 110))

    drawText(screen, "X", font, red, (leftBarOrigin + 150, chipsXMultHeight + 95), "center", 50)

    infoXOffset = leftBarOrigin + 100

    infoYOffset = 420
    # hands left
    handContainerX = infoXOffset + 10
    handContainerY = infoYOffset + 10
    drawRect(screen, darkUI, (handContainerX, handContainerY, 80, 80), round=5)
    drawText(screen, "Hands", font, white, (handContainerX + 40, handContainerY + 5), "center")
    drawRect(screen, lightUI, (handContainerX + 10, handContainerY + 30, 60, 40), round=5)
    handsLeft = str(save.hands)
    drawText(screen, handsLeft, font, blue, (handContainerX + 40, handContainerY + 35), "center",
             40)

    # discards left
    discardContainerX = handContainerX + 100
    drawRect(screen, darkUI, (discardContainerX, handContainerY, 80, 80), round=5)
    drawText(screen, "Discards", font, white, (discardContainerX + 40, handContainerY + 10),
             "center", size=20)
    drawRect(screen, lightUI, (discardContainerX + 10, handContainerY + 30, 60, 40), round=5)
    discardsLeft = str(save.discards)
    drawText(screen, discardsLeft, font, red, (discardContainerX + 40, handContainerY + 35), "center",
             40)

    # money
    moneyContainerY = handContainerY + 90
    drawRect(screen, darkUI, (handContainerX, moneyContainerY, 180, 80), round=5)
    drawRect(screen, lightUI, (handContainerX + 10, moneyContainerY + 5, 160, 70), round=5)
    money = f"${save.money}"
    drawText(screen, money, font, yellow, (handContainerX + 90, moneyContainerY + 15), "center",
             getOptimalTextSize(money, 70, 160))

    # ante
    lastRowY = moneyContainerY + 90
    drawRect(screen, darkUI, (handContainerX, lastRowY, 80, 80), round=5)
    drawText(screen, "Ante", font, white, (handContainerX + 40, lastRowY + 10),
             "center", size=20)
    drawRect(screen, lightUI, (handContainerX + 10, lastRowY + 30, 60, 40), round=5)
    ante = str(save.ante)
    drawText(screen, ante, font, yellow, (handContainerX + 25, lastRowY + 35), "center",
             40)
    drawText(screen, "/8", font, white, (handContainerX + 40, lastRowY + 40), "left")

    # round
    lastRowY = moneyContainerY + 90
    drawRect(screen, darkUI, (discardContainerX, lastRowY, 80, 80), round=5)
    drawText(screen, "Round", font, white, (discardContainerX + 40, lastRowY + 10),
             "center", size=20)
    drawRect(screen, lightUI, (discardContainerX + 10, lastRowY + 30, 60, 40), round=5)
    round = str(save.round)
    drawText(screen, round, font, yellow, (discardContainerX + 40, lastRowY + 35), "center",
             40)

    # run info
    # TODO: once everything else is done add functionality to this
    drawRect(screen, red, (leftBarOrigin + 10, infoYOffset, 80, 130), round=5)
    drawText(screen, "Run\nInfo\n(event-\nually)", font, white, (leftBarOrigin + 50, infoYOffset + 20),
             "center")

    # camera switching
    drawRect(screen, darkUI, (leftBarOrigin + 10, infoYOffset + 140, 80, 130), round=5)
    cameraIndex = 0
    drawText(screen, f"Cam {cameraIndex}", font, white, (leftBarOrigin + 20, infoYOffset + 150),
             "left")
    drawRect(screen, yellow, (leftBarOrigin + 20, infoYOffset + 180, 60, 35), round=5)
    drawText(screen, "+", font, white, (leftBarOrigin + 43, infoYOffset + 183), "left", size=40)

    drawRect(screen, red, (leftBarOrigin + 20, infoYOffset + 225, 60, 35), round=5)
    drawText(screen, "-", font, white, (leftBarOrigin + 43, infoYOffset + 228), "left", size=40)

def drawButtons(save, screen, colors, font):
    white = colors["white"]
    blue = colors["blue"]
    red = colors["red"]
    darkUI = colors["darkUI"]
    lightUI = colors["lightUI"]
    buttonY = 580

    drawRect(screen, darkUI, (370, buttonY+5, 202, 102), round=8)
    drawRect(screen, blue, (370, 580, 200, 100), lightUI, round=8)
    drawText(screen, "Play hand\nUse", font, white, (380, buttonY + 10), "left", 40)

    discardX = 580
    drawRect(screen, darkUI, (discardX, buttonY + 5, 202, 102), round=8)
    drawRect(screen, red, (discardX, 580, 200, 100), lightUI, round=8)
    drawText(screen, "Discard\nSell", font, white, (discardX + 10, buttonY + 10), "left", 40)

def drawCardCounter(save, font, screen, colors, foundCards):
    darkUI = colors["darkUI"]
    lightUI = colors["lightUI"]
    white = colors["white"]

    xOrigin = 890
    yOrigin = 550

    drawRect(screen, lightUI, (xOrigin - 10, yOrigin - 10, 420, 180))
    drawRect(screen, darkUI, (xOrigin - 5, yOrigin - 5, 410, 170), round=8)

    mode = "handFinder"
    ind = 0
    handCards = foundCards["middle"]

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
    for subset, cards in foundCards.items():
        trackedCardsInThirdOfScreen = []
        for card in cards:
            trackedCardsInThirdOfScreen.append(card.toString(mode="fancy"))
        finishedMessage = f"{subsetDict[subset]}\n{'\n'.join(trackedCardsInThirdOfScreen)}"
        drawText(screen, finishedMessage, font, white, (xOrigin + iterator, yOrigin), "left",
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

    lightUI = colors["lightUI"]
    darkUI = colors["darkUI"]
    white = colors["white"]

    drawRect(screen, lightUI, (xOrigin - 10, yOrigin-10, 220, 220), round=7)
    drawRect(screen, darkUI, (xOrigin - 5, yOrigin - 5, 210, 210), round=7)
    message = textwrap.fill(cardToAnalyze.toString(), 20)
    drawText(screen, message, font, white, (xOrigin, yOrigin), "left")

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