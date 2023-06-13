import copy
import cv2
import mediapipe as mp
from shapely.geometry import Polygon
from pynput.keyboard import Key, Controller

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)


        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

        return lmList

def main():
    # INITIALISATION OF VARIABLES
    i = 0
    c = 0
    flag = 0
    lastLm = []
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    kb = Controller()

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        if (len(lmList) != 0):

            if i == 0:
                lastLm = copy.deepcopy(lmList)
                i = 1
            else:

                if c > 1:
                    c = 0

                    # Play/Pause the video
                    tip_polList = []
                    tip_polList.append(tuple(lmList[4][1:]))
                    tip_polList.append(tuple(lmList[8][1:]))
                    tip_polList.append(tuple(lmList[12][1:]))
                    tip_polList.append(tuple(lmList[16][1:]))
                    tip_polList.append(tuple(lmList[20][1:]))
                    tipPoly = Polygon(tip_polList)

                    pip_polList = []
                    pip_polList.append(tuple(lmList[2][1:]))
                    pip_polList.append(tuple(lmList[6][1:]))
                    pip_polList.append(tuple(lmList[10][1:]))
                    pip_polList.append(tuple(lmList[14][1:]))
                    pip_polList.append(tuple(lmList[18][1:]))
                    pipPoly = Polygon(pip_polList)

                    if tipPoly.area > pipPoly.area:
                        if flag == 0:
                            print("Play")
                            kb.press(Key.space)
                            kb.release(Key.space)
                            flag = 1

                        if lmList[8][1] > lastLm[8][1]:
                            print("<<")
                            kb.press(Key.left)
                            kb.release(Key.left)
                            # SEEK -10 Seconds
                        elif lmList[8][1] < lastLm[8][1]:
                            print(">>")
                            kb.press(Key.right)
                            kb.release(Key.right)
                            # SEEK +10 Seconds

                    else:
                        if flag == 1:
                            print("Pause")
                            flag = 0
                            kb.press(Key.space)
                            kb.release(Key.space)

                lastLm = copy.deepcopy(lmList)
                c+=1

                # DISPLAYING VIDEO FEED
                cv2.imshow("Image", img)
                cv2.waitKey(1)


if __name__ == "__main__":
    main()
