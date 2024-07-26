import time
from typing import Optional

import numpy as np

from detector import DetectorAbs


class DetectionAggregate:

    def __init__(self, detections=None, total_frames=0, faces=None):
        self.detections = {} if detections is None else detections
        self.total_frames = total_frames
        self.faces = {} if faces is None else faces

    def add_face_detection(self, _name: str, _confidence_numeric: int, _dominant_emotion: Optional[str],
                           _frame_time_epoch: float,
                           _face: np.ndarray) -> None:
        # add detection
        _name_detections = self.detections.get(_name,
                                               {'confidence_sum': 0,
                                                'confidence_max': 0,
                                                'count': 0,
                                                'first_frame_time_epoch': 0.0,
                                                'last_frame_time_epoch': 0.0,
                                                'emotions': {}
                                                })
        _name_detections['confidence_sum'] += _confidence_numeric
        _name_detections['count'] += 1

        if not _name_detections['first_frame_time_epoch']:
            _name_detections['first_frame_time_epoch'] = _frame_time_epoch

        _name_detections['last_frame_time_epoch'] = max(_name_detections['last_frame_time_epoch'], _frame_time_epoch)

        # remember the face
        if _confidence_numeric > _name_detections['confidence_max']:
            self.faces[_name] = _face.copy()

        _name_detections['confidence_max'] = max(_name_detections['confidence_max'], _confidence_numeric)

        if _dominant_emotion:
            _emotions = _name_detections.get('emotions', {})
            _emotions[_dominant_emotion] = _emotions.get(_dominant_emotion, 0) + 1
            _name_detections['emotions'] = _emotions
        self.detections[_name] = _name_detections

    def has_detections(self) -> bool:
        return len(self.detections) > 0

    def get_data(self):
        return {
            'total_frames': self.total_frames,
            'detections': self.detections
        }

    @staticmethod
    def combine(first, second, min_frames=5):

        def pass_detection_threshold(name: str, detection: DetectionAggregate) -> bool:
            t = 40 if name.startswith("unknown") else min_frames
            return detection.detections[name]['count'] > t

        combined_detections = {name: first.detections[name] for name in first.detections if
                               pass_detection_threshold(name, first)}

        for name in second.detections:
            if combined_detections.get(name) is None:
                if pass_detection_threshold(name, second):
                    combined_detections[name] = second.detections[name]
            else:
                combined = combined_detections[name]
                sd = second.detections[name]
                combined['confidence_sum'] = combined['confidence_sum'] + sd['confidence_sum']
                combined['confidence_max'] = max(combined['confidence_max'], sd['confidence_max'])
                combined['count'] = combined['count'] + sd['count']
                combined['first_frame_time_epoch'] = min(combined['first_frame_time_epoch'],
                                                         sd['first_frame_time_epoch'])

                combined['last_frame_time_epoch'] = max(combined['last_frame_time_epoch'], sd['last_frame_time_epoch'])

                combined_emotions = combined['emotions'].copy()
                for emotion in second.detections[name].get('emotions', {}):
                    se = second.detections[name]['emotions'][emotion]
                    fe = combined_emotions.get(emotion)
                    combined_emotions[emotion] = se if fe is None else se + fe

                combined['emotions'] = combined_emotions
                combined_detections[name] = combined

        combined_faces = first.faces.copy()
        for face in second.faces:

            if combined_faces.get(face) is None or first.detections.get(face) is None:
                combined_faces[face] = second.faces[face]
                continue

            # print(first)
            # print(second)
            first_conf = first.detections[face]['confidence_max']
            second_conf = second.detections[face]['confidence_max']
            combined_faces[face] = second.faces[face] if second_conf > first_conf else combined_faces[face]

        return DetectionAggregate(combined_detections,
                                  total_frames=first.total_frames + second.total_frames,
                                  faces=combined_faces)

    def add_frame(self, detector: DetectorAbs):
        frame_time = time.time()
        self.total_frames += 1
        # iterate key value detected_identities
        for name, detected_identity in detector.detected_identities.items():
            person_img = detected_identity['person']
            emotion = detected_identity.get('emotion', None)
            self.add_face_detection(name, 1, emotion, frame_time, person_img)

        return frame_time
