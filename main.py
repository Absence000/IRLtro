from subscripts.handFinderAndPointsAssigner import calcPointsFromHand
from subscripts.inputHandling import prepareSelectedCards
from subscripts.pygameSubfunctions import *
from subscripts.saveUtils import *
from subscripts.colorManagement import Colors
import pygame, time

def main():
    pygame.init()
    screenWidth = 1280
    screenHeight = 720
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    pygame.display.set_caption("Realatro")
    font = pygame.font.Font("cardSprites/font/balatro.otf")
    clock = pygame.time.Clock()

    lookupTable = openjson("cardCreationAndRecognition/cardToArcuo.json", True)
    save = Save(openjson("save"))

    backupDetectedCardsScan = {
        "upper": [],
        "middle": [],
        "lower": [],
        "unpairedTags": []
    }
    backupDetectedCardsScanTime = time.time()

    # TODO: The outline changes color depending on the game state
    # TODO: Turn this into an object with all the colors as attributes
    colors = Colors()

    buttons = []
    pressedButton = ""
    canInteract = True
    calculatingHand = False

    camIndex = 1
    cap = openCamera(camIndex)

    running = True
    while running:
        currentTime = time.time()
        colors.switchOutline(save)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if pygame.Rect(button["rect"]).collidepoint(mouse_pos):
                        pressedButton = button["name"]
                        # I need these for like every state so they're up here
                        if pressedButton == "+":
                            pressedButton = ""
                            camIndex += 1
                            cap.release()
                            cap = openCamera(camIndex)
                            if not cap.isOpened():
                                camIndex -= 1
                                cap = openCamera(camIndex)

                        elif pressedButton == "-":
                            pressedButton = ""
                            if camIndex > 0:
                                camIndex -= 1
                                cap.release()
                                cap = openCamera(camIndex)
                                if not cap.isOpened():
                                    camIndex += 1
                                    cap = openCamera(camIndex)

        screen.fill(colors.backgroundColor)

        if save.state == "selectingBlind":
            drawBlindSelectScreen(save, colors)
            drawLeftBar(save, font, screen, colors, "", "", 0, 0, 0, camIndex)

        if save.state == "playing":
            if calculatingHand:
                freezeFrame = rawFrame
            else:
                freezeFrame = None

            # this is really confusing but it draws the webcam
            foundCards, backupDetectedCardsScan, backupDetectedCardsScanTime, rawFrame = (
                drawWebcamAndReturnFoundCards(cap, lookupTable, screen, backupDetectedCardsScan,
                                              backupDetectedCardsScanTime, currentTime, save, freezeFrame))

            if calculatingHand:
                # this part took so long to figure out holy shit
                if currentTime - lastEventTime > 0.5:
                    chainIndex += 1
                    lastEventTime = currentTime
                if len(chain.events) > chainIndex:
                    chainLink = chain.events[chainIndex]
                    displayChainEvent(chainLink, screen, font)
                    displayChips = chainLink.chips
                    displayMult = chainLink.mult
                    chainEndTime = currentTime
                else:
                    if currentTime - chainEndTime < 1:
                        handType = str(points)
                        displayChips = 0
                        displayMult = 0
                    else:
                        save.score += points
                        calculatingHand = False
                        canInteract = True
            else:
                handType, handInfo = drawCardCounter(save, font, screen, colors, foundCards)
                if handInfo is None:
                    # analysis mode, draws a popup saying what the joker/consumable does
                    analysisMode = True
                    drawAnalysisPopup(save, font, screen, colors, handType)
                    handType = ""
                    level = ""
                    score = save.score
                    displayChips = 0
                    displayMult = 0
                else:
                    analysisMode = False
                    level = handInfo["level"]
                    score = save.score
                    displayChips = handInfo["chips"]
                    displayMult = handInfo["mult"]

            buttons = drawLeftBar(save, font, screen, colors, handType, level, score, displayChips, displayMult, camIndex)

            # TODO: if it's in analysis mode put the sell price of the card on the discard/sell button
            buttons += drawButtons(save, screen, colors, font)

            if canInteract:
                if pressedButton == "play":
                    if analysisMode:
                        return
                    else:
                        selectedHand = prepareSelectedCards(save, foundCards)
                        if len(selectedHand) <= 5:
                            pressedButton = ""
                            calculatingHand = True
                            canInteract = False
                            points, chain, selectedHand = (
                                calcPointsFromHand(selectedHand, findBestHand(selectedHand), save.hand, save))
                            lastEventTime = currentTime
                            chainIndex = 0


        clock.tick(60)
        pygame.display.flip()

main()