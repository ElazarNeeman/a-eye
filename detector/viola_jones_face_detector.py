import cv2


class ViolaJonesFaceDetector:

    def __init__(self):
        self.faceCascade = cv2.CascadeClassifier("weights/haarcascade_frontalface_default.xml")
        # self.minW = 0.1 * webcam_stream.vcap.get(3)
        # self.minH = 0.1 * webcam_stream.vcap.get(4)
        self.minW = 48
        self.minH = 64

    def detect_faces(self, frame, person_position):
        # calculate minW by frame width and minH by frame height
        self.minW = 0.1 * frame.shape[1]
        self.minH = 0.1 * frame.shape[0]
        result = []
        try:
            (px, py, pw, ph) = person_position
            gray = cv2.cvtColor(frame[py:py + ph, px:px + pw], cv2.COLOR_BGR2GRAY)
        except Exception as e:
            print(e)
            return result

        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(self.minW), int(self.minH))
        )

        for (x, y, w, h) in faces:
            x = x + px
            y = y + py
            detected_face = frame[y:y + h, x:x + w]
            result.append((x, y, w, h, detected_face, gray))

        return result
