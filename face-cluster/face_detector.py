from _operator import itemgetter

from deepface import DeepFace


class FaceDetector:
    def detect(self, bgr_img):
        def get_box(facial_area):
            x, y, w, h, left_eye, right_eye = itemgetter('x', 'y', 'w', 'h', 'left_eye', 'right_eye')(facial_area)
            return y, x + w, y + h, x

        embedding_objs = DeepFace.represent(
            # model_name="Dlib",
            # model_name="VGG-Face",
            model_name="VGG-Face",
            img_path=bgr_img,
            enforce_detection=False,
            # detector_backend="retinaface"
            detector_backend="opencv"
        )
        encodings = [e["embedding"] for e in embedding_objs]
        facial_box = [get_box(e["facial_area"]) for e in embedding_objs]
        return facial_box, encodings
