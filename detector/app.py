import asyncio

import cv2

from env import STREAM_ID, QUIT_KEY
from image_collector import ImageCollector
from influx_collector import InfluxCollector
from multi_frame_detector import MultiFrameDetector
from video import VideoStream


async def main():
    video_stream = VideoStream(stream_id=STREAM_ID)  # stream_id = 0 is for primary camera
    # video_stream = VideoStream(stream_id=1)  # stream_id = 0 is for primary camera
    # detector = SingleFrameDetector()
    detector = MultiFrameDetector()

    detections_collectors = [InfluxCollector(), ImageCollector()]

    video_stream.start()

    for detection_collector in detections_collectors:
        detection_collector.start()

    while not video_stream.stopped:

        frame = video_stream.read()
        detector.process(frame)

        for detection_collector in detections_collectors:
            detection_collector.collect(detector)

        cv2.imshow('frame', frame)
        key = cv2.waitKey(1)
        if key == QUIT_KEY:
            break

    # stop the webcam stream
    video_stream.stop()

    for detection_collector in detections_collectors:
        detection_collector.stop()

    # closing all windows
    cv2.destroyAllWindows()


if __name__ == '__main__':
    asyncio.run(main())
