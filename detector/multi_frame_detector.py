import cv2
import numpy as np

from deep_face_detector import FaceDetector
from deep_face_recognizer import DeepFaceRecognizer
from detector import DetectorAbs
from ssd import SingleShotDetector
from tracker.sort import Sort


class MultiFrameDetector(DetectorAbs):

    def __init__(self):
        super().__init__()
        self.ssd = SingleShotDetector()
        # self.face_detector = ViolaJonesFaceDetector()
        self.face_detector = FaceDetector()
        self.detected_objects = []
        self.detected_identities = {}
        self.track_identities = {}
        self.detections = np.empty((0, 5))
        self.tracker = Sort(max_age=60, min_hits=2, iou_threshold=0.3)
        self.face_recognizer = DeepFaceRecognizer()

    def process(self, img):
        self.detected_objects = []
        self.detections = np.empty((0, 5))
        self.detected_identities = {}

        for x, y, w, h, obj_class_name, confidence in self.ssd.get_detected_objects(img):
            self.detected_objects.append((x, y, w, h, obj_class_name))
            # print(x, y, w, h, obj_class_name, confidence)

            if obj_class_name == "person":
                # print(x, y, w, h, obj_class_name, confidence)
                ins = np.array([x, y, x + w, y + h, confidence])
                self.detections = np.vstack((self.detections, ins))
                # cv2.rectangle(img, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=5)
                # cv2.putText(img, obj_class_name.upper(), (x, y - 10),
                #           cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (0, 255, 0), 2)
                # self.identify_person(img, (x, y, w, h))

        tracks = self.tracker.update(self.detections)
        for result in tracks:
            x1, y1, x2, y2, obj_id = result
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            # print(obj_id)
            cv2.rectangle(img, (x1, y1), (x2, y2), color=(int(50 * obj_id) % 255, 255, 255), thickness=3)
            # cv2.putText(img, str(obj_id).upper(), (x1, y1 - 10),
            #             cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (0, 255, 0), 2)
            w = x2 - x1
            h = y2 - y1
            self.identify_person(img, (x1, y1, w, h), obj_id)

    def identify_person(self, img, person_position, track_id):
        track_id = int(track_id)
        name = self.track_identities.get(track_id, None)
        (x, y, w, h) = person_position
        # person_img = img[y:y + h, x:x + w]
        if name is not None:
            cv2.putText(img, f"{name} ({track_id})", (x + 5, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                        (255, 255, 255), 2)

            self.detected_identities[name] = {
                'person': img,
                'track_id': track_id
            }
            return

        for (x, y, w, h, detected_face, person_img) in self.face_detector.detect_faces(img, person_position):
            # Draw a rectangle around the detected face
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            dominant_emotion, name = self.analyze_face(detected_face)

            # Display the recognized name and confidence level on the image
            cv2.putText(img, f"{name}, ({dominant_emotion})", (x + 5, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                        (255, 255, 255), 2)

            # cv2.imshow(f'Face {name}', detected_face)
            if name is not None:
                self.detected_identities[name] = {
                    'face': detected_face,
                    'person': img,
                    'emotion': dominant_emotion,
                    'track_id': track_id
                }
                self.track_identities[track_id] = name
            else:
                name = f"unknown {track_id}"
                self.detected_identities[name] = {
                    'face': detected_face,
                    'person': img,
                    'emotion': dominant_emotion,
                    'track_id': track_id
                }

            print(name, " ", dominant_emotion)

        if self.track_identities.get(track_id, None) is None:
            name = f"unknown {track_id}"
            cv2.putText(img, f"{name}", (x + 5, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                        (255, 255, 255), 2)
            self.detected_identities[name] = {
                'person': img,
                'track_id': track_id
            }

    def analyze_face(self, detected_face):
        return self.face_recognizer.analyze_face(detected_face)
