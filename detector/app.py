import asyncio
import time

import cv2

from detection_aggragate import DetectionAggregate
from detection_alarm import DetectionAlarm
from env import SECONDS_BETWEEN_DETECTIONS, STREAM_ID, QUIT_KEY
from image_collector import ImageCollector
from influx_collector import InfluxCollector
from multi_frame_detector import MultiFrameDetector
from video import VideoStream


def process_frame(frame, detector, detection_aggregate):
    detector.process(frame)
    frame_time = detection_aggregate.add_detector_frame(detector)
    return frame_time


async def handle_detections(detection_aggregate, alarm, frame_time):
    if detection_aggregate.has_detections():
        print(f"{time.ctime(frame_time)}: detections: {detection_aggregate.get_data()}")
        try:
            await alarm.add_detection(detection_aggregate, min_frames=5)
        except Exception as e:
            print(e)


def detection_aggregate_time_passed(old_epoch, frame_time):
    return frame_time - old_epoch >= SECONDS_BETWEEN_DETECTIONS


async def main():
    video_stream = VideoStream(stream_id=STREAM_ID)  # stream_id = 0 is for primary camera
    # video_stream = VideoStream(stream_id=1)  # stream_id = 0 is for primary camera
    # detector = SingleFrameDetector()
    detector = MultiFrameDetector()
    detection_aggregate = DetectionAggregate()
    influx = InfluxCollector()
    image_collector = ImageCollector()
    alarm = DetectionAlarm()
    await alarm.start()
    video_stream.start()
    image_collector.start()

    # processing frames in input stream
    num_frames_processed = 0

    start = time.time()
    old_time = start

    while not video_stream.stopped:

        frame = video_stream.read()
        detector.process(frame)
        frame_time = detection_aggregate.add_frame(detector)
        influx.collect(detector)
        image_collector.collect(detector)
        num_frames_processed += 1

        cv2.imshow('frame', frame)
        key = cv2.waitKey(1)
        if key == QUIT_KEY:
            break

        if detection_aggregate_time_passed(old_time, frame_time):
            old_time = frame_time
            await handle_detections(detection_aggregate, alarm, frame_time)
            detection_aggregate = DetectionAggregate()

    end = time.time()
    # stop the webcam stream
    video_stream.stop()
    # stop the alarm thread
    alarm.stop()

    # printing time elapsed and fps
    elapsed = end - start
    fps = num_frames_processed / elapsed
    print("FPS: {} , Elapsed Time: {} , Frames Processed: {}".format(fps, elapsed, num_frames_processed))

    # closing all windows
    cv2.destroyAllWindows()


if __name__ == '__main__':
    asyncio.run(main())
