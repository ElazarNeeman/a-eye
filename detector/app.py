import asyncio
from multiprocessing import Process

import cv2

from env import get_stream_id, QUIT_KEY, CAMERA_COUNT
from image_collector import ImageCollector
from influx_collector import InfluxCollector
from multi_frame_detector import MultiFrameDetector
from video import VideoStream


async def main(camera_id: int):
    window_name = f'Camera {camera_id}'

    video_stream = VideoStream(stream_id=get_stream_id(camera_id))  # stream_id = 0 is for primary camera
    # video_stream = VideoStream(stream_id=1)  # stream_id = 0 is for primary camera
    # detector = SingleFrameDetector()
    detector = MultiFrameDetector()

    detections_collectors = [InfluxCollector(camera_id), ImageCollector(camera_id)]

    video_stream.start()

    for detection_collector in detections_collectors:
        detection_collector.start()

    while not video_stream.stopped:

        frame = video_stream.read()
        detector.process(frame)

        for detection_collector in detections_collectors:
            detection_collector.collect(detector)

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1)
        if key == QUIT_KEY:
            break

    # stop the webcam stream
    video_stream.stop()

    for detection_collector in detections_collectors:
        detection_collector.stop()

    # closing all windows
    cv2.destroyAllWindows()


def run_main(camera_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(camera_id))
    loop.close()


if __name__ == '__main__':
    # asyncio.run(main(1))
    stream_ids = range(0, CAMERA_COUNT)

    # Create and start a new process for each stream_id
    processes = []
    for stream_id in stream_ids:
        p = Process(target=run_main, args=(stream_id,))
        p.start()
        processes.append(p)

    # Wait for all processes to finish
    for p in processes:
        p.join()
