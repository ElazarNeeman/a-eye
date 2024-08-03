import os
from typing import List

import pandas as pd
from deepface import DeepFace


class DeepFaceRecognizer:

    def __init__(self, db_path="family"):
        self.db_path = db_path

    @staticmethod
    def get_name(deep_face_identities: List[pd.DataFrame]) -> str | None:
        if len(deep_face_identities) == 0:
            return None

        closest_identity = deep_face_identities[0]['identity']

        if len(closest_identity) == 0:
            return None

        closest_identity_path = closest_identity[0]
        _, identity_file = os.path.split(closest_identity_path)

        name = identity_file.split('-')[-2]
        return name

    def get_person_name(self, detected_face):
        res = DeepFace.find(img_path=detected_face, db_path=self.db_path, align=False,
                            detector_backend="skip",
                            enforce_detection=False, silent=True)

        name = self.get_name(res)

        # if name is not None:
        #     threshold = res[0]['threshold']
        #     print(name, threshold)

        return name

    def get_face_emotion(self, detected_face):
        face_emotions = DeepFace.analyze(img_path=detected_face, actions=("emotion",),
                                         detector_backend="skip",
                                         enforce_detection=False, silent=True)

        dominant_emotion = face_emotions[0]['dominant_emotion']
        return dominant_emotion

    def analyze_face(self, detected_face):
        name = self.get_person_name(detected_face)
        dominant_emotion = self.get_face_emotion(detected_face)
        return dominant_emotion, name
