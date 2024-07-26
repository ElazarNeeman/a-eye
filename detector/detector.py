from abc import ABCMeta, abstractmethod


class DetectorAbs(metaclass=ABCMeta):
    def __init__(self):
        self.detected_identities = {}

    @abstractmethod
    def process(self, img):
        pass
