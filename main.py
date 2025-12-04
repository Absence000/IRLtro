from subscripts.consumableCards import consumableCanBeUsedImmediately, sellConsumable, useImmediateConsumable
from subscripts.handFinderAndPointsAssigner import calcPointsFromHand
from subscripts.inputHandling import prepareSelectedCards, prepareCardForPrinting
from subscripts.pygameSubfunctions import *
from subscripts.saveUtils import *
from subscripts.colorManagement import Colors
from subscripts.eventChainManagement import EventChain, Event
from subscripts.packs import Pack
from subscripts.cardUtils import Card
from subscripts.jokers import Joker
from subscripts.planetCards import Planet, usePlanetCard
from subscripts.shop import newItemIsConsumable
from subscripts.tarotCards import Tarot, useTarotCard
from subscripts.spectralCards import Spectral
import pygame, time

def main():
    pygame.init()
    screenWidth = 1280
    screenHeight = 720
    screen = pygame.Surface((screenWidth, screenHeight))

    screenInfo = pygame.display.Info()
    actualWidth = screenInfo.current_w
    actualHeight = screenInfo.current_h

    actualScreen = pygame.display.set_mode((actualWidth, actualHeight), pygame.RESIZABLE)

    pygame.display.set_caption("Realatro")
    font = pygame.font.Font("cardSprites/font/balatro.otf")
    clock = pygame.time.Clock()

    lookupTable = openjson("cardCreationAndRecognition/cardToArcuo.json", True)
    # save = Save(openjson("save"))

    # temp blank save stuff
    save = createBlankSave("standard", True)
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
    backupDetectedCardsScanTime = {
        "upper": time.time(),
        "middle": time.time(),
        "lower": time.time()
    }

    # TODO: The outline changes color depending on the game state
    # TODO: Turn this into an object with all the colors as attributes
    colors = Colors()

    buttons = []
    pressedButton = ""
    canInteract = True
    calculatingHand = False

    camIndex = 1
    cap = openCamera(camIndex)

    shopChain = EventChain()
    packChain = EventChain()
    askingAboutImmediateUse = False

    running = True
    while running:
        rawMouseX, rawMouseY = pygame.mouse.get_pos()
        scaleX = screenWidth / actualWidth
        scaleY = screenHeight / actualHeight
        mousePos = [rawMouseX * scaleX, rawMouseY * scaleY]
        currentTime = time.time()
        colors.switchOutline(save)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if pygame.Rect(button["rect"]).collidepoint(mousePos):
                        pressedButton = button["name"]
                        pressedButtonInfo = button
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
            if calculatingHand:
                freezeFrame = rawFrame
            else:
                freezeFrame = None

            buttons = drawLeftBar(save, font, screen, colors, "", "", 0, 0, 0, camIndex)

            foundCards, backupDetectedCardsScan, backupDetectedCardsScanTime, rawFrame = (
                drawWebcamAndReturnFoundCards(cap, lookupTable, screen, backupDetectedCardsScan,
                                              backupDetectedCardsScanTime, currentTime, save, freezeFrame, "middle"))

            buttons += drawBlindSelectScreen(save, font, screen, colors)

            consumableButtons, selectedConsumable = drawConsumables(save, screen, colors, font, mousePos)
            buttons += consumableButtons

            if canInteract:
                if pressedButton == "select":
                    pressedButton = ""
                    save.state = "playing"
                    save.discardedCards = []
                    save.playedCards = []
                    save.discards = 4
                    save.hands = 3
                    save.score = 0

                elif pressedButton == "skip":
                    pressedButton = ""
                    save.nextBlind()

                elif pressedButton == "use":
                    pressedButton = ""
                    if consumableCanBeUsedImmediately(selectedConsumable):
                        useImmediateConsumable(selectedConsumable, save)


                elif pressedButton == "sell":
                    pressedButton = ""
                    sellConsumable(selectedConsumable, save)

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
                    if not analysisMode:
                        if currentTime - chainEndTime < 1:
                            handType = str(points)
                            displayChips = 0
                            displayMult = 0
                        else:
                            save.score += points
                            save.hands -= 1
                            if save.score >= save.requiredScore:
                                # advances to the next round
                                baseReward = save.blindInfo[2]
                                save.nextBlind()
                                totalReward = baseReward + save.hands
                                interest = min(save.money // 5, 5)
                                save.money += totalReward + interest
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
                        calculatingHand = False
                        canInteract = True
                        saveGame(save)
            else:
                handType, handInfo = drawCardCounter(save, font, screen, colors, foundCards)
                handTypeType = type(handType).__name__
                if handTypeType in ["Joker", "Planet", "Tarot", "Spectral"]:
                    # analysis mode, draws a popup saying what the joker/consumable does
                    analysisMode = True
                    drawAnalysisPopup(save, font, screen, colors, handType)
                    consumable = handType
                    otherCards = handInfo
                    handType = ""
                    level = ""
                    score = save.score
                    displayChips = 0
                    displayMult = 0
                else:
                    consumable = None
                    otherCards = None
                    analysisMode = False
                    level = handInfo["level"]
                    score = save.score
                    displayChips = handInfo["chips"]
                    displayMult = handInfo["mult"]

            buttons = drawLeftBar(save, font, screen, colors, handType, level, score, displayChips, displayMult, camIndex)

            buttons += drawButtons(save, screen, colors, font)
            consumableButtons, selectedConsumable = drawConsumables(save, screen, colors, font, mousePos)
            buttons += consumableButtons
            if canInteract:
                if pressedButton == "play":
                    pressedButton = ""
                    # TODO: delete all the analysis mode stuff now that the consumables are digital
                    selectedHand = prepareSelectedCards(save, foundCards)
                    if len(selectedHand) <= 5:
                        calculatingHand = True
                        canInteract = False
                        points, chain, selectedHand = (
                            calcPointsFromHand(selectedHand, findBestHand(selectedHand), save.hand, save))
                        lastEventTime = currentTime
                        chainIndex = 0
                elif pressedButton == "discard":
                    selectedHand = prepareSelectedCards(save, foundCards)
                    if len(selectedHand) <= 5:
                        # TODO: Discard check stuff here
                        pressedButton = ""
                        save.discardedCards += selectedHand
                        save.discards -= 1


                elif pressedButton == "use":
                    pressedButton = ""
                    if isinstance(selectedConsumable, Tarot):
                        selectedHand = prepareSelectedCards(save, foundCards)
                        success, successMessage = useTarotCard(selectedConsumable, selectedHand, save, True)
                        chain = EventChain()
                        canInteract = False
                        lastEventTime = currentTime
                        chainIndex = 0
                        if success:
                            chain.add("chips", successMessage, selectedConsumable, 0, 0)
                            save.lastUsedTarotOrPlanet = chosenCard
                            save.consumables.remove(selectedConsumable)
                        else:
                            chain.add("mult", successMessage, selectedConsumable, 0, 0)

                    elif isinstance(selectedConsumable, Planet):
                        usePlanetCard(selectedConsumable, save)
                        save.consumables.remove(selectedConsumable)
                        save.lastUsedTarotOrPlanet = chosenCard

                elif pressedButton == "sell":
                    pressedButton = ""
                    sellConsumable(selectedConsumable, save)

        elif save.state == "shop":
            buttons = drawLeftBar(save, font, screen, colors, "", "", 0, 0, 0, camIndex)

            if calculatingHand:
                freezeFrame = rawFrame
            else:
                freezeFrame = None

            foundCards, backupDetectedCardsScan, backupDetectedCardsScanTime, rawFrame = (
                drawWebcamAndReturnFoundCards(cap, lookupTable, screen, backupDetectedCardsScan,
                                              backupDetectedCardsScanTime, currentTime, save, freezeFrame, "top"))


            if askingAboutImmediateUse: buttons += drawImmediateUsePopup(save, font, screen, colors, item)
            else: buttons += drawShop(save, font, screen, colors, mousePos)

            if len(shopChain.events) > 0:
                if currentTime - lastEventTime < 0.25:
                    displayChainEvent(shopChain.events[0], screen, font)
                else:
                    del shopChain.events[0]
            else:
                canInteract = True

            # TODO: Non hand-requiring consumables should be usable here
            consumableButtons, selectedConsumable = drawConsumables(save, screen, colors, font, mousePos)
            buttons += consumableButtons
            if canInteract:
                if not askingAboutImmediateUse:
                    if pressedButton == "Reroll":
                        pressedButton = ""
                        if save.money >= save.shop.rerollCost:
                            save.money -= save.shop.rerollCost
                            save.shop.rollCards(save)
                            save.shop.rerollCost += 1
                    if pressedButton == "Next Round":
                        pressedButton = ""
                        # TODO: end of shop checks go here
                        save.state = "selectingBlind"
                    if pressedButton == "buy":
                        pressedButton = ""
                        buyStatus = save.shop.buyItem(pressedButtonInfo["type"], pressedButtonInfo["index"], save)
                        if isinstance(buyStatus, str):
                            shopChain.add("visual", buyStatus, pressedButtonInfo["coords"], 0, 0)
                            canInteract = False
                        else:
                            shopChain.add("visual", "Bought!", pressedButtonInfo["coords"], 0, 0)
                            canInteract = False
                            item = buyStatus
                            needsToBePrinted = True
                            if isinstance(item, Pack):
                                needsToBePrinted = False
                                save.state = "openingPack"
                                pickAmount = item.pickAmount
                                doneOpeningPack = False
                                canInteract = True
                                items = item.open(save)
                            elif newItemIsConsumable(item):
                                # TODO: when consumable usage is implemented finish this
                                if consumableCanBeUsedImmediately(item):
                                    askingAboutImmediateUse = True
                                else:
                                    save.consumables.append(item)

                        lastEventTime = currentTime
                    elif pressedButton == "use":
                        pressedButton = ""
                        if isinstance(selectedConsumable, Tarot):
                            selectedHand = prepareSelectedCards(save, foundCards)
                            success, successMessage = useTarotCard(selectedConsumable, selectedHand, save, True)
                            shopChain = EventChain()
                            canInteract = False
                            lastEventTime = currentTime
                            chainIndex = 0
                            if success:
                                shopChain.add("chips", successMessage, selectedConsumable, 0, 0)
                                save.consumables.remove(selectedConsumable)
                                save.lastUsedTarotOrPlanet = chosenCard
                            else:
                                shopChain.add("mult", successMessage, selectedConsumable, 0, 0)
                        elif isinstance(selectedConsumable, Planet):
                            usePlanetCard(selectedConsumable, save)
                            save.consumables.remove(selectedConsumable)
                            save.lastUsedTarotOrPlanet = chosenCard

                    elif pressedButton == "sell":
                        pressedButton = ""
                        sellConsumable(selectedConsumable, save)
                else:
                    if pressedButton == "yes":
                        pressedButton = ""
                        askingAboutImmediateUse = False
                        # TODO: Move this to a separate function once you figure out the circular import stuff
                        if isinstance(item, Card) or isinstance(item, Joker):
                            prepareCardForPrinting(item, keep=True)
                        elif isinstance(item, Tarot):
                            useTarotCard(item, None, save, False)
                            save.lastUsedTarotOrPlanet = chosenCard
                        elif isinstance(item, Planet):
                            usePlanetCard(item, save)
                            save.lastUsedTarotOrPlanet = chosenCard
                        # TODO: spectrals here
                    elif pressedButton == "no":
                        askingAboutImmediateUse = False
                        pressedButton = ""
                        save.consumables.append(item)
        elif save.state in ["openingPack", "openingPackFromTag"]:
            buttons = drawLeftBar(save, font, screen, colors, "", "", 0, 0, 0, camIndex)

            if calculatingHand:
                freezeFrame = rawFrame
            else:
                freezeFrame = None

            foundCards, backupDetectedCardsScan, backupDetectedCardsScanTime, rawFrame = (
                drawWebcamAndReturnFoundCards(cap, lookupTable, screen, backupDetectedCardsScan,
                                              backupDetectedCardsScanTime, currentTime, save, freezeFrame, cutoff=None))

            drawCardCounter(save, font, screen, colors, foundCards)
            if len(packChain.events) > 0:
                if currentTime - lastEventTime < 0.25:
                    displayChainEvent(packChain.events[0], screen, font)
                else:
                    del packChain.events[0]
                    calculatingHand = False
                    canInteract = True
            else:
                if doneOpeningPack:
                    if save.state == "openingPack":
                        save.state = "shop"
                    elif save.state == "openingPackFromTag":
                        save.state = "selectingBlind"

            buttons += drawPackButtons(save, items, pickAmount, font, screen, colors, mousePos)
            consumableButtons, selectedConsumable = drawConsumables(save, screen, colors, font, mousePos)
            buttons += consumableButtons
            if canInteract:
                if pressedButton == "skip":
                    pressedButton = ""
                    doneOpeningPack = True
                elif pressedButton == "buy":
                    pressedButton = ""
                    chosenItemIndex = pressedButtonInfo["index"]
                    chosenCard = items[chosenItemIndex]

                    if isinstance(chosenCard, Card) or isinstance(chosenCard, Joker):
                        prepareCardForPrinting(chosenCard, keep=True)
                        del items[chosenItemIndex]
                        pickAmount -= 1
                    elif isinstance(chosenCard, Planet):
                        usePlanetCard(chosenCard, save)
                        save.lastUsedTarotOrPlanet = chosenCard
                        del items[chosenItemIndex]
                        pickAmount -= 1
                    # TODO: spectrals here
                    elif isinstance(chosenCard, Tarot):
                        selectedHand = prepareSelectedCards(save, foundCards)
                        success, successMessage = useTarotCard(chosenCard, selectedHand, save, False)
                        canInteract = False
                        lastEventTime = currentTime
                        if success:
                            packChain.add("chips", successMessage, chosenCard, 0, 0)
                            pickAmount -= 1
                            del items[chosenItemIndex]
                            save.lastUsedTarotOrPlanet = chosenCard
                        else:
                            packChain.add("mult", successMessage, chosenCard, 0, 0)

                    if pickAmount <= 0:
                        doneOpeningPack = True

                elif pressedButton == "use":
                    pressedButton = ""
                    if isinstance(selectedConsumable, Tarot):
                        selectedHand = prepareSelectedCards(save, foundCards)
                        success, successMessage = useTarotCard(selectedConsumable, selectedHand, save, True)
                        packChain = EventChain()
                        canInteract = False
                        lastEventTime = currentTime
                        chainIndex = 0
                        if success:
                            packChain.add("chips", successMessage, selectedConsumable, 0, 0)
                            save.consumables.remove(selectedConsumable)
                            save.lastUsedTarotOrPlanet = chosenCard
                        else:
                            packChain.add("mult", successMessage, selectedConsumable, 0, 0)
                    elif isinstance(selectedConsumable, Planet):
                        usePlanetCard(selectedConsumable, save)
                        save.consumables.remove(selectedConsumable)
                        save.lastUsedTarotOrPlanet = chosenCard

                elif pressedButton == "sell":
                    pressedButton = ""
                    sellConsumable(selectedConsumable, save)

        elif save.state == "dead":
            running = False
        scaled = pygame.transform.smoothscale(screen, (actualWidth, actualHeight))
        actualScreen.blit(scaled, (0, 0))
        clock.tick(60)
        pygame.display.flip()

main()