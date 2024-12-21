import cv2
import numpy as np
from imutils import build_montages
from sklearn.cluster import DBSCAN
import shutil
import os

from face_detector import FaceDetector


class FaceCluster:
    def __init__(self):
        self.data = []
        self.face_detector = FaceDetector()
        self.cluster = DBSCAN(min_samples=3)
        self.labelIDs = np.empty(1)
        self.numUniqueFaces = 0
        self.data_arr = np.empty(1)

    def add_image(self, img_path):
        print("Processing image: ", img_path)
        bgr = cv2.imread(img_path)
        boxes, encodings = self.face_detector.detect(bgr)
        d = [{"imagePath": img_path, "loc": box, "encoding": enc} for (box, enc) in zip(boxes, encodings)]
        self.data.extend(d)

    def cluster_images(self):
        print("Clustering the faces...")
        self.data_arr = np.array(self.data)
        encodings_arr = [item["encoding"] for item in self.data_arr]
        self.cluster.fit(encodings_arr)
        self.labelIDs = np.unique(self.cluster.labels_)
        self.numUniqueFaces = len(np.where(self.labelIDs > -1)[0])
        print("Clustering finished")

    def get_faces_cluster(self):
        for labelID in self.labelIDs:

            if labelID == -1:
                continue

            idxs = np.where(self.cluster.labels_ == labelID)[0]
            idxs = np.random.choice(idxs, size=min(15, len(idxs)), replace=False)
            faces = []
            whole_images = []

            dir_name = 'face#{}'.format(labelID + 1)
            os.mkdir(dir_name)

            for i in idxs:
                current_image = cv2.imread(self.data_arr[i]["imagePath"])
                rgb_current_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
                (top, right, bottom, left) = self.data_arr[i]["loc"]
                current_face = rgb_current_image[top:bottom, left:right]
                current_face = cv2.resize(current_face, (96, 96))
                whole_images.append(rgb_current_image)
                faces.append(current_face)

                face_image_name = 'image{}.jpg'.format(i)
                cv2.imwrite(os.path.join(dir_name, face_image_name), current_image)
                # draw rectangle near the face
                cv2.rectangle(rgb_current_image, (left, top), (right, bottom), color=(0, 255, 255), thickness=4)

            shutil.make_archive('zip_face#{}'.format(labelID + 1), 'zip', dir_name)
            shutil.rmtree('face#{}'.format(labelID + 1))

            montage = build_montages(faces, (96, 96), (2, 2))[0]
            yield labelID, montage, whole_images


if __name__ == "__main__":
    path = "c:\\src\\github\\a-eye\\detector\\images\\2024-11-03\\14-01-Ilay-01.jpg"
    FaceDetector().detect(path)
