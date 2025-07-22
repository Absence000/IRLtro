from subscripts.handFinderAndPointsAssigner import calcPointsFromHand
from subscripts.inputHandling import prepareSelectedCards
from subscripts.pygameSubfunctions import *
from subscripts.saveUtils import *
from subscripts.colorManagement import Colors
import pygame, time

blindIndexToBlindInfo = [("Small Blind", 1, 3), ("Big Blind", 1.5, 4), ("Boss Blind", 2, 5)]
anteBaseChipsList = [100, 300, 800, 2000, 5000, 11000, 20000, 35000, 50000, 110000, 560000, 72000000, 300000000,
                     47000000000, 2.9E+13, 7.7E+16, 8.6E+20, 4.2E+25, 9.2E+30, 9.2E+36, 4.3E+43, 9.7E+50, 1.0E+59,
                     5.8E+67, 1.6E+77, 2.4E+87, 1.9E+98, 8.4E+109, 2.0E+122, 2.7E+135, 2.1E+149, 9.9E+163, 2.7E+179,
                     4.4E+195, 4.4E+212, 2.8E+230, 1.1E+249, 2.7E+268, 4.5E+288, 4.8E+309]

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

    # temp blank save stuff
    # save = createBlankSave("standard", True)
    # save.blindInfo = blindIndexToBlindInfo[save.blindIndex]
    # save.requiredScore = anteBaseChipsList[save.ante] * save.blindInfo[1]
    # save.state = "playing"
    # save.discardedCards = []
    # save.playedCards = []
    # save.discards = 4
    # save.hands = 4
    # save.score = 0

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

        elif save.state == "playing":
            if calculatingHand:
                freezeFrame = rawFrame
            else:
                freezeFrame = None

            # this is really confusing but it draws the webcam
            foundCards, backupDetectedCardsScan, backupDetectedCardsScanTime, rawFrame = (
                drawWebcamAndReturnFoundCards(cap, lookupTable, screen, backupDetectedCardsScan,
                                              backupDetectedCardsScanTime, currentTime, save, freezeFrame, None))

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
                        save.hands -= 1
                        if save.score >= save.requiredScore:
                            # advances to the next round
                            if save.blindIndex == 2:
                                save.ante += 1
                                save.blindIndex = 0
                            else:
                                save.blindIndex += 1
                            baseReward = save.blindInfo[2]
                            totalReward = baseReward + save.hands
                            save.money += totalReward
                            save.state = "shop"
                            save.shop = Shop(cards=[None, None], packs=[None, None], vouchers=[None], rerollCost=5)
                            save.shop.rollCards(save)
                            save.shop.rollPacks(save)
                            saveGame(save)
                        elif save.hands <= 0:
                            save.state = "dead"
                            saveGame(save)

                        calculatingHand = False
                        canInteract = True
                        saveGame(save)
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
                elif pressedButton == "discard":
                    if analysisMode:
                        return
                    else:
                        selectedHand = prepareSelectedCards(save, foundCards)
                        if len(selectedHand) <= 5:
                            # TODO: Discard check stuff here
                            pressedButton = ""
                            save.discardedCards += selectedHand
                            save.discards -= 1

        elif save.state == "shop":
            drawLeftBar(save, font, screen, colors, "", "", 0, 0, 0, camIndex)

            if calculatingHand:
                freezeFrame = rawFrame
            else:
                freezeFrame = None

            # this is really confusing but it draws the webcam
            foundCards, backupDetectedCardsScan, backupDetectedCardsScanTime, rawFrame = (
                drawWebcamAndReturnFoundCards(cap, lookupTable, screen, backupDetectedCardsScan,
                                              backupDetectedCardsScanTime, currentTime, save, freezeFrame, "top"))

            drawShop(save, font, screen, colors)
            # TODO: Clear shop.images when the shop is exited



        clock.tick(60)
        pygame.display.flip()

main()