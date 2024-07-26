import cv2
import numpy as np

# we are not going to bother with objects less than 50% probability
THRESHOLD = 0.4
# the lower the value: the fewer bounding boxes will remain
SUPPRESSION_THRESHOLD = 0.3
SSD_INPUT_SIZE = 320


# read the class labels
def construct_class_names(file_name=r'weights/class_names'):
    with open(file_name, 'rt') as file:
        names = file.read().rstrip('\n').split('\n')

    return names


class SingleShotDetector:
    def __init__(self):
        self.class_names = construct_class_names()
        self.neural_network = cv2.dnn_DetectionModel('weights/ssd_weights.pb', 'weights/ssd_mobilenet_coco_cfg.pbtxt')

        # define whether we run the algorithm with CPU or with GPU
        # WE ARE GOING TO USE CPU !!!
        self.neural_network.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.neural_network.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        self.neural_network.setInputSize(SSD_INPUT_SIZE, SSD_INPUT_SIZE)
        self.neural_network.setInputScale(1.0 / 127.5)
        self.neural_network.setInputMean((127.5, 127.5, 127.5))
        self.neural_network.setInputSwapRB(True)

    def get_detected_objects(self, frame: cv2.typing.MatLike) -> list:
        class_label_ids, confidences, bbox = self.neural_network.detect(frame)
        bbox = list(bbox)
        confidences = np.array(confidences).reshape(1, -1).tolist()[0]

        # these are the indexes of the bounding boxes we have to keep
        box_to_keep = cv2.dnn.NMSBoxes(bbox, confidences, THRESHOLD, SUPPRESSION_THRESHOLD)
        detected_objects = []
        for index in box_to_keep:
            box = bbox[index]
            x, y, w, h = box[0], box[1], box[2], box[3]
            obj_class_name = self.class_names[class_label_ids[index] - 1]
            confidence = confidences[index]
            detected_objects.append((x, y, w, h, obj_class_name, confidence))

        return detected_objects

