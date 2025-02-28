import cv2, os, shutil
from cardCreationAndRecognition.finalArcuoTracking import returnFoundCards
from subscripts.spacesavers import *


def playingIRL(save):
    if save.deck == "irl":
        return True
    else:
        return False

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

def returnCardsFromImage():
    return returnFoundCards(openjson("cardCreationAndRecognition/cardToArcuo.json", True))


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
