from abc import ABCMeta, abstractmethod

from detector import DetectorAbs


class DetectionsCollector(metaclass=ABCMeta):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def collect(self, detector: DetectorAbs):
        pass
