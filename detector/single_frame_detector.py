import cv2

from deep_face_detector import FaceDetector
from deep_face_recognizer import DeepFaceRecognizer
from detector import DetectorAbs
from ssd import SingleShotDetector


class SingleFrameDetector(DetectorAbs):

    def __init__(self):
        super().__init__()
        self.ssd = SingleShotDetector()
        self.face_detector = FaceDetector()
        self.detected_objects = []
        self.face_recognizer = DeepFaceRecognizer()

    def process(self, img):
        self.detected_objects = []
        self.detected_identities = {}

        for x, y, w, h, obj_class_name, _ in self.ssd.get_detected_objects(img):
            self.detected_objects.append((x, y, w, h, obj_class_name))
            print(x, y, w, h, obj_class_name)

            if obj_class_name == "person":
                cv2.rectangle(img, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=5)
                cv2.putText(img, obj_class_name.upper(), (x, y - 10),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (0, 255, 0), 2)
                self.identify_person(img, (x, y, w, h))

    def identify_person(self, img, person_position):
        for (x, y, w, h, detected_face, person_img) in self.face_detector.detect_faces(img, person_position):
            # Draw a rectangle around the detected face
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            dominant_emotion, name = self.analyze_face(detected_face)

            # Display the recognized name and confidence level on the image
            cv2.putText(img, f"{name}, ({dominant_emotion})", (x + 5, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                        (255, 255, 255), 2)

            print(name, " ", dominant_emotion)
            cv2.imshow(f'Face {name}', detected_face)
            self.detected_identities[name] = {
                'face': detected_face,
                'person': person_img,
                'emotion': dominant_emotion,
            }

    def analyze_face(self, detected_face):
        return self.face_recognizer.analyze_face(detected_face)
