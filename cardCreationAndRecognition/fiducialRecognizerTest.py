import cv2
import numpy as np
from subscripts.cardUtils import *

def arucoBoardsToCard(lookupTable, image_path=None):
    """
    Detects ArUco markers and groups them into potential 1×2 ArUco GridBoards (4×4_100).
    Also checks if both markers in a board are upside down.

    :param image_path: (Optional) Path to an image file for detection. If None, it uses the webcam.
    """
    # Load ArUco dictionary and detector parameters
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    parameters = cv2.aruco.DetectorParameters()

    def rightSideUp(corners):
        """
        Computes the angle of an ArUco marker relative to the horizontal axis.
        Returns the angle in degrees.
        """
        top_left, top_right, bottom_right, bottom_left = corners  # Extract relevant corner points

        return (bottom_left[1] < top_left[1]) or (bottom_right[1] < top_right[1])

    def process_frame(frame):
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
                if distance_x < distance_y:  # More separated in X than in Y
                    # if rightSideUp(corners1):
                    #     combinedID = int(f"{id1}{id2}")
                    # else:
                    #     combinedID = int(f"{id2}{id1}")
                    if normalized_y_distance < 1.1:
                        detected_boards.append({"id": int(f"{id2}{id1}"), "rightSideUp": rightSideUp(corners1)})
                    i += 2  # Skip to the next possible pair
                else:
                    i += 1  # Move to the next marker

            # Print detected board IDs
            for board in detected_boards:
                try:
                    cardTest = createCardFromBinary(lookupTable[board['id']]).toString()
                    print(f"={cardTest} ({board['id']}), {board['rightSideUp']}")
                except Exception as e:
                    print(e)
                    print(f"Unrecognized card! {board['id']}, {board['rightSideUp']}, {lookupTable[board['id']]}")
                          #f"{createCardFromBinary(lookupTable[board['id']]).number}")

        return frame

    # If an image path is provided, process a single image
    if image_path:
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"⚠️ Error: Could not read image '{image_path}'")
            return

        processed_frame = process_frame(frame)
        cv2.imshow("ArUco Board Detection", processed_frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # Otherwise, use webcam feed
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("⚠️ Error: Could not open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Error: Failed to capture frame.")
            break

        processed_frame = process_frame(frame)
        cv2.imshow("ArUco Board Detection", processed_frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

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

# generate_aruco_board_image(5678)