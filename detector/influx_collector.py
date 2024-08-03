from influxdb_client_3 import InfluxDBClient3, Point, WriteOptions, write_client_options, InfluxDBError

from detections_collector import DetectionsCollector
from env import INFLUXDB_HOST, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_DB
import time

from multi_frame_detector import DetectorAbs

import threading
import queue


class InfluxCollector(DetectionsCollector):
    def __init__(self, camera_id: int = 0):

        self.camera_id = camera_id

        # Instantiate WriteOptions for batching
        write_options = WriteOptions()

        # Create a Queue object
        self.queue = queue.Queue()
        wco = write_client_options(success_callback=self.success,
                                   error_callback=self.error,
                                   retry_callback=self.retry,
                                   write_options=write_options)

        self.client = InfluxDBClient3(
            host=INFLUXDB_HOST,
            token=INFLUXDB_TOKEN, org=INFLUXDB_ORG,
            database=INFLUXDB_DB,
            write_client_options=wco)

        # Start a new thread that runs the write_data method
        self.write_thread = threading.Thread(target=self.write_data)
        self.stopped = True

    def start(self):
        self.stopped = False
        self.write_thread.start()

    def stop(self):
        self.stopped = True
        self.write_thread.join()

    def collect(self, detector: DetectorAbs):

        for key in detector.detected_identities:

            emotion = detector.detected_identities[key].get("emotion", None)
            tracking_id = detector.detected_identities[key]["track_id"]

            name = key
            if key.startswith("unknown"):
                name = None

            point = Point("home_db")

            if tracking_id is not None:
                point.tag("track_id", tracking_id)

            if name is not None:
                point.tag("name", name)

            if emotion is not None:
                point.tag("emotion", emotion)

            point.tag("camera_id", self.camera_id)
            point.field("count", 1)
            point.time(time.time_ns())

            # Put the point into the queue instead of writing it directly
            self.queue.put(point)

    def success(self, db: str, data: str):
        status = f"Success writing batch: {db} data: {data}"
        print(status)

    def error(self, data: str, err: InfluxDBError):
        status = f"Error writing batch:  data: {data}, error: {err}"
        print(status)

    def retry(self, data: str, err: InfluxDBError):
        status = f"Retry error writing , data: {data}, error: {err}"
        print(status)

    def write_data(self):

        while True:

            if self.stopped:
                break

            try:
                # Get a point from the queue with a timeout
                point = self.queue.get(timeout=1)

                # Write the point to the database
                self.client.write(point)

            except queue.Empty:
                # The queue is empty, continue the loop
                continue
