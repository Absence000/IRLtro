import pygame, time, cv2
import numpy as np
from cardCreationAndRecognition.finalArcuoTracking import pygameDisplayFoundCards
from subscripts.spacesavers import *
from subscripts.handFinderAndPointsAssigner import findBestHand

# TODO: once you figure out pygame replace the input system with this, right now it's a separate program that talks
#  to the main one by reading the save and outputting the card read info as json which is really stupid

def showDetailedCamFeed():
    # Constants
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    SIDEBAR_WIDTH = 200
    VIDEO_WIDTH = WINDOW_WIDTH - SIDEBAR_WIDTH
    VIDEO_HEIGHT = WINDOW_HEIGHT

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("IRLatro")
    font = pygame.font.SysFont(None, 30)

    lookupTable = openjson("cardCreationAndRecognition/cardToArcuo.json", True)

    # Colors
    WHITE = (255, 255, 255)
    GRAY = (180, 180, 180)
    BLACK = (0, 0, 0)

    # Button factory
    def create_button(text, x, y, w, h):
        rect = pygame.Rect(x, y, w, h)
        label = font.render(text, True, BLACK)
        return {"rect": rect, "label": label, "text": text}

    def open_camera(index):
        cap = cv2.VideoCapture(index)
        # right now it does 1080p but I might change this idk
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        return cap

    # Button positions (vertical layout in sidebar)
    button_width = 140
    button_height = 40
    button_x = (SIDEBAR_WIDTH - button_width) // 2

    buttons = [
        create_button("Cam -1", button_x, 50, button_width, button_height),
        create_button("Cam +1", button_x, 100, button_width, button_height),
        create_button("Rotate", button_x, 160, button_width, button_height),
    ]

    # State
    camera_index = 1
    rotation = 0  # 0, 90, 180, 270 degrees
    cap = open_camera(camera_index)

    # sorry matlab teacher in engineering school who said it was bad practice to not use input flags
    oldSortedDetectedCards = {}
    sortedDetectedCards = {}
    lastArucoTime = 0

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Button click handling
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        if button["text"] == "Cam -1":
                            camera_index -= 1
                            cap.release()
                            cap = open_camera(camera_index)
                            if not cap.isOpened():
                                camera_index += 1
                                cap = open_camera(camera_index)
                        elif button["text"] == "Cam +1":
                            camera_index += 1
                            cap.release()
                            cap = open_camera(camera_index)
                            if not cap.isOpened():
                                camera_index -= 1
                                cap = open_camera(camera_index)
                        elif button["text"] == "Rotate":
                            rotation = (rotation + 90) % 360

        # Capture frame
        ret, frame = cap.read()
        if not ret:
            continue

        # Rotate
        frame = np.rot90(frame, k=rotation // 90)
        frame = np.ascontiguousarray(frame) # idk why but I need this or it'll break the aruco detector when it rotates

        frame, sortedDetectedCards = pygameDisplayFoundCards(lookupTable, frame)

        # only checks the cards once a second or it tanks performance
        # currentTime = time.time()
        # if currentTime - lastArucoTime >= 1:
        #     lastArucoTime = currentTime

        if oldSortedDetectedCards != sortedDetectedCards:
            sortedDetectedCardsDict = {
                key: [card.toDict() for card in cards]
                for key, cards in sortedDetectedCards.items()
            }
            savejson("sortedDetectedCards", sortedDetectedCardsDict)
        # Convert color
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Flip horizontally (mirror effect)
        frame = np.fliplr(frame)

        # rotate again after it's done
        frame = np.rot90(frame, k=1)

        # Get original dimensions
        h, w, _ = frame.shape

        # Calculate aspect-correct scaling
        scale = min(VIDEO_WIDTH / w, VIDEO_HEIGHT / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        frame = cv2.resize(frame, (new_w, new_h))

        # Convert to Pygame surface
        surface = pygame.surfarray.make_surface(frame)

        # Draw background
        screen.fill(GRAY)

        # Compute position to center image in video area
        video_x = SIDEBAR_WIDTH + (VIDEO_WIDTH - new_w) // 2
        video_y = (VIDEO_HEIGHT - new_h) // 2

        # Draw webcam frame
        screen.blit(surface, (video_x, video_y))

        # Draw buttons
        for button in buttons:
            pygame.draw.rect(screen, WHITE, button["rect"])
            text_rect = button["label"].get_rect(center=button["rect"].center)
            screen.blit(button["label"], text_rect)

        # Draw camera index
        index_text = font.render(f"Cam {camera_index}", True, BLACK)
        index_rect = index_text.get_rect(center=(SIDEBAR_WIDTH // 2, 220))
        screen.blit(index_text, index_rect)

        # shows the cards it finds
        handCards = sortedDetectedCards["middle"]
        nonSelectedCards = sortedDetectedCards["lower"]
        jokersAndConsumables = sortedDetectedCards["upper"]

        # hand display (left)
        mode = "handFinder"
        ind = 0
        for card in handCards:
            cardType = type(card).__name__
            if cardType != "Card":
                mode = "analysis"
                analysisCardIndex = ind
            ind += 1


        if mode == "handFinder":
                handType = findBestHand(handCards)[0]
                try:
                    handInfo = openjson("save")["handLevels"][handType]
                    handMessage = f"{handType} lvl {handInfo['level']}:\n{handInfo['chips']} x {handInfo['mult']}"
                except:
                    handMessage = "loading..."
        elif mode == "analysis":
            cardToAnalyze = handCards[analysisCardIndex]
            handMessage = cardToAnalyze.toString()

        handText = font.render(handMessage, True, BLACK)
        handRect = handText.get_rect()
        handRect.midleft = (20, 300)
        screen.blit(handText, handRect)

        # specific hand card display
        specificHandMessage = []
        for card in handCards:
            specificHandMessage.append(card.toString(mode="fancy"))

        specificNonselectedMessage = []
        for card in nonSelectedCards:
            specificNonselectedMessage.append(card.toString(mode="fancy"))

        jokersAndConsumablesMessage = []
        for card in jokersAndConsumables:
            jokersAndConsumablesMessage.append(card.toString(mode="fancy"))

        specificMessage = (f"Jokers and Consumables:\n{'\n'.join(jokersAndConsumablesMessage)}\n"
                           f"Hand:\n{'\n'.join(specificHandMessage)}\n"
                           f"Unselected:\n{'\n'.join(specificNonselectedMessage)}")

        specificHandText = font.render(specificMessage, True, BLACK)
        specificHandRect = specificHandText.get_rect(center=(400, 500))
        screen.blit(specificHandText, specificHandRect)

        pygame.display.update()

    # Cleanup
    cap.release()
    pygame.quit()

showDetailedCamFeed()