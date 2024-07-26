from operator import itemgetter

from deepface import DeepFace


class FaceDetector:
    def __init__(self):
        self.detector_backend = 'opencv'

    def detect_faces(self, img, person_position):
        (px, py, pw, ph) = person_position
        person = img[py:py + ph, px:px + pw]

        faces = DeepFace.extract_faces(person, detector_backend=self.detector_backend, align=True,
                                       enforce_detection=False)
        results = []
        for f in faces:
            x, y, w, h, left_eye, right_eye = itemgetter('x', 'y', 'w', 'h', 'left_eye', 'right_eye')(f['facial_area'])
            x = x + px
            y = y + py

            if f['confidence'] < 0.50:
                continue

            detected_face = img[y:y + h, x:x + w]
            results.append((x, y, w, h, detected_face, person))

        return results
