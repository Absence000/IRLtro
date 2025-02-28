import cv2
import numpy as np
from subscripts.cardUtils import *

def arucoBoardsToCard(lookupTable, image_path=None, debugging=None):
    """
    Detects ArUco markers and groups them into potential 1×2 ArUco GridBoards (4×4_100).
    Also checks if both markers in a board are upside down.

    :param image_path: (Optional) Path to an image file for detection. If None, it uses the webcam.
    """
    # Load ArUco dictionary and detector parameters
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    parameters = cv2.aruco.DetectorParameters()

    def rightSideUp(corners):
        top_left, top_right, bottom_right, bottom_left = corners  # Extract relevant corner points

        return (bottom_left[1] < top_left[1]) and (bottom_right[1] < top_right[1])

    def process_frame(frame, displayOnly=None):
        """Detects ArUco markers, groups them into valid 1×2 boards, and checks orientation."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect markers
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        corners, ids, _ = detector.detectMarkers(gray)

        detected_boards = []

        if ids is not None and len(ids) >= 2:
            # Draw detected markers
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            # Convert IDs and corners to lists
            ids_list = ids.flatten().tolist()
            corners_list = [c.reshape(-1, 2) for c in corners]  # Flatten corners

            # Sort markers by x-position for left-to-right pairing
            sorted_markers = sorted(zip(ids_list, corners_list), key=lambda x: np.mean(x[1][:, 0]))

            # Try forming 1×2 boards based on spatial proximity
            i = 0
            while i < len(sorted_markers) - 1:
                id1, corners1 = sorted_markers[i]
                id2, corners2 = sorted_markers[i + 1]

                # Compute the horizontal distance between marker centers
                center1 = np.mean(corners1, axis=0)
                center2 = np.mean(corners2, axis=0)
                distance_x = abs(center1[0] - center2[0])
                distance_y = abs(center1[1] - center2[1])

                # Compute marker size (average of height and width)
                marker_size = np.linalg.norm(corners1[0] - corners1[2])
                normalized_y_distance = distance_y / marker_size if marker_size > 0 else 0

                # Check if they form a 1-row, 2-column structure
                if distance_x < distance_y:
                    if rightSideUp(corners1):
                        if corners1[0][1] > corners2[0][1]:
                            upwards = True
                        else:
                            upwards = False
                    else:
                        if corners1[0][1] > corners2[0][1]:
                            upwards = False
                        else:
                            upwards = True
                    # upwards = rightSideUp(corners1) and corners1[0][1] > corners2[0][1]

                    id1 = correctID(id1)
                    id2 = correctID(id2)

                    # print(f"{id1} and {id2}: {upwards}")

                    if upwards:
                        combinedID = int(f"{id1}{id2}")
                    else:
                        combinedID = int(f"{id2}{id1}")
                    if normalized_y_distance < 1.1:
                        detected_boards.append({"id": combinedID, "rightSideUp": upwards})
                    i += 2  # Skip to the next possible pair
                else:
                    i += 1  # Move to the next marker

            # remove cards that appear twice
            unique_ids = {}

            for item in detected_boards:
                id_val = item["id"]
                if id_val not in unique_ids or item["rightSideUp"]:
                    unique_ids[id_val] = True

            if displayOnly == None:
                fixedCardIDs = list(unique_ids.keys())
                finishedCardDetectionList = []
                # Print detected board IDs
                for id in fixedCardIDs:
                    try:
                        detectedCard = createCardFromBinary(lookupTable[id])
                        print(f"{detectedCard.toString()}")
                        finishedCardDetectionList.append(detectedCard)
                    except Exception as e:
                        print(e)
                        print(f"Unrecognized card! {id}, {lookupTable[id]}")
                              #f"{createCardFromBinary(lookupTable[board['id']]).number}")
                return frame, finishedCardDetectionList
        return frame

    # If an image path is provided, process a single image
    if image_path:
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"⚠️ Error: Could not read image '{image_path}'")
            return

        # frame = cv2.resize(frame, (302*3, 403*3))
        processed_frame = process_frame(frame)
        # cv2.imshow("ArUco Board Detection", processed_frame[0])
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return processed_frame[1]

    # Otherwise, use webcam feed
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("⚠️ Error: Could not open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Error: Failed to capture frame.")
            break

        cv2.imshow("ArUco Board Detection", frame)
        processed_frame = process_frame(frame, True)
        cv2.imshow("Processed ArUco Board Detection", processed_frame)
        cv2.waitKey(0)  # Wait until user presses a key
        cv2.destroyWindow("Processed ArUco Board Detection")
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):  # Spacebar to capture and scan
            print("Cards detected:")
            return process_frame(frame.copy())[1]
            cv2.imshow("Processed ArUco Board Detection", processed_frame)
            cv2.waitKey(0)  # Wait until user presses a key
            cv2.destroyWindow("Processed ArUco Board Detection")

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


def generateBoardForCard(num):
    num = str(num).zfill(4)
    idArray = [num[:2], num[2:]]
    # print(idArray)
    # Load the 4x4_100 dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)

    # Define the 1x2 ArUco GridBoard (1 row, 2 columns)
    board = cv2.aruco.GridBoard(size=(1, 2),
                                markerLength=.04,
                                markerSeparation=.01,
                                dictionary=aruco_dict,
                                ids=np.array(idArray, dtype=np.int32))


    # Create a blank white image for the board
    board_size = (100, 200)  # Width × Height in pixels

    # Draw the board
    boardImage = board.generateImage(outSize=board_size, marginSize=5)

    # Save the board image
    cv2.imwrite("testBoard.png", boardImage)

def correctID(id):
    if id == 0:
        return "00"
    else:
        return str(id).zfill(2)

# generate_aruco_board_image(5678)

# arucoBoardsToCard(openjson("cardToArcuo.json", True))

# returnFoundCards(openjson("cardToArcuo.json", True))