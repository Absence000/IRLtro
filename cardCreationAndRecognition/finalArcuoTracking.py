import cv2
import numpy as np
from subscripts.cardUtils import createCardFromBinary
from subscripts.spacesavers import *


def is_marker_upside_down(corners):
    """
    Determines if a marker is upside down by checking if the bottom corners
    are higher than the top corners.
    """
    top_left, top_right, bottom_right, bottom_left = corners
    return (bottom_left[1] < top_left[1]) and (bottom_right[1] < top_right[1])


def get_detected_boards(frame, aruco_dict, parameters):
    """Detects ArUco markers, groups them into valid 1×2 boards, and checks orientation."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thirdOfFrameHeight = frame.shape[0]/3

    # Detect markers
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, _ = detector.detectMarkers(gray)

    detected_boards = []

    if ids is not None and len(ids) >= 2:
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
            if distance_x < distance_y:  # More separated in X than in Y
                if is_marker_upside_down(corners1):
                    if corners1[0][1] > corners2[0][1]:
                        upwards = True
                    else:
                        upwards = False
                else:
                    if corners1[0][1] > corners2[0][1]:
                        upwards = False
                    else:
                        upwards = True

                id1 = correctID(id1)
                id2 = correctID(id2)

                if upwards:
                    combinedID = int(f"{id1}{id2}")
                else:
                    combinedID = int(f"{id2}{id1}")

                if normalized_y_distance < 1.1:
                    # I could do this more accurately but it's way more math so no
                    boardYCenter = corners1[0][1]

                    if boardYCenter < thirdOfFrameHeight:
                        verticalPos = "upper"
                    elif boardYCenter < 2 * thirdOfFrameHeight:
                        verticalPos = "middle"
                    else:
                        verticalPos = "lower"

                    detected_boards.append(
                        {"id": combinedID, "rightSideUp": upwards, "verticalPos": verticalPos})
                i += 2  # Skip to the next possible pair
            else:
                i += 1  # Move to the next marker

    return detected_boards


def displayFoundCards(lookupTable):
    """
    Opens the webcam (index 2) and displays the feed, overlaying detected board information.
    Draws squares around detected markers. Press 'q' to exit.
    """
    # Load ArUco dictionary and detector parameters
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    parameters = cv2.aruco.DetectorParameters()

    # Open webcam at index 2
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("⚠️ Error: Could not open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Error: Failed to capture frame.")
            break

        detected_boards = get_detected_boards(frame, aruco_dict, parameters)

        # Detect markers and draw detected squares
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        finishedCardDetectionList = arcuoToCard(detected_boards, lookupTable)

        # Draw detected boards on the frame
        for card in finishedCardDetectionList:
            ids_text = card.toString(mode="fancy")
            position = (50, 50 + finishedCardDetectionList.index(card) * 30)
            cv2.putText(frame, ids_text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("ArUco Board Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


def get_tracking_info():
    """Returns detected board tracking information from the current webcam frame."""
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("⚠️ Error: Could not open webcam.")
        return []

    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("⚠️ Error: Failed to capture frame.")
        return []

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    parameters = cv2.aruco.DetectorParameters()
    return get_detected_boards(frame, aruco_dict, parameters)

def correctID(id):
    if id == 0:
        return "00"
    else:
        return str(id).zfill(2)

def arcuoToCard(detected_boards, lookupTable):
    unique_ids = {}
    id_to_position = {}

    for item in detected_boards:
        id_val = item["id"]
        position = item["verticalPos"]

        # Prefer rightSideUp cards if duplicates exist
        if id_val not in unique_ids or item["rightSideUp"]:
            unique_ids[id_val] = True
            id_to_position[id_val] = position

    categorized_cards = {
        "upper": [],
        "middle": [],
        "lower": []
    }

    for id in unique_ids:
        try:
            detectedCard = createCardFromBinary(lookupTable[id])
            position = id_to_position[id]
            categorized_cards[position].append(detectedCard)
        except Exception as e:
            print(e)
            print(f"Unrecognized card! {id}, {lookupTable[id]}")
    return categorized_cards


def returnFoundCards():
    """Captures a single frame from the webcam and returns detected card objects."""
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("⚠️ Error: Could not open webcam.")
        return []

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("⚠️ Error: Failed to capture frame.")
        return []

    frame = np.rot90(frame, k=1)
    frame = np.ascontiguousarray(frame)  # idk why but I need this or it'll break the aruco detector when it rotates

    # Detect ArUco boards
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    parameters = cv2.aruco.DetectorParameters()
    detected_boards = get_detected_boards(frame, aruco_dict, parameters)
    return arcuoToCard(detected_boards, openjson("cardCreationAndRecognition/cardToArcuo.json", True)
)

# displayFoundCards(openjson("cardToArcuo.json", True))  # Display webcam feed with overlayed tracking info

def pygameDisplayFoundCards(lookupTable, frame):
    # opens the webcam frame and draws all the cards and stuff
    # Load ArUco dictionary and detector parameters
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    parameters = cv2.aruco.DetectorParameters()

    detected_boards = get_detected_boards(frame, aruco_dict, parameters)

    # Detect markers and draw detected squares
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    sortedDetectedCards = arcuoToCard(detected_boards, lookupTable)

    # Draw detected boards on the frame
    # for card in finishedCardDetectionList:
    #     ids_text = card.toString(mode="fancy")
    #     position = (50, 50 + finishedCardDetectionList.index(card) * 60)
    #     cv2.putText(frame, ids_text, position, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
    return frame, sortedDetectedCards