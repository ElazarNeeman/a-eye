from detections_collector import DetectionsCollector
from detector import DetectorAbs


class NullCollector(DetectionsCollector):

    def start(self):
        pass

    def stop(self):
        pass

    def collect(self, detector: DetectorAbs):
        pass