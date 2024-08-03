import os
import queue

import schedule
import threading
import time

import cv2

from detections_collector import DetectionsCollector
from detector import DetectorAbs


class ImageCollector(DetectionsCollector):
    def __init__(self, camera_id: int = 0, folder_name: str = 'images'):

        self.camera_id = camera_id
        self.camera_str = "{:02}".format(camera_id)

        # output folder name
        self.folder_name = folder_name

        # Create a Queue object
        self.queue = queue.Queue()

        # Start a new thread that runs the write_data method
        self.write_thread = threading.Thread(target=self.write_data)

        self.stopped = True

    def start(self):
        self.stopped = False
        self.create_daily_image_dir()
        schedule.every().day.at("00:00:00").do(self.create_daily_image_dir)
        self.write_thread.start()

    def stop(self):
        self.stopped = True
        self.write_thread.join()

    def create_daily_image_dir(self):
        timestamp = time.time()
        # get year month day hour minute second
        alarm_time = time.localtime(timestamp)
        year = alarm_time.tm_year
        month = "{:02}".format(alarm_time.tm_mon)
        day = "{:02}".format(alarm_time.tm_mday)
        os.makedirs(f'{self.folder_name}/{year}-{month}-{day}', exist_ok=True)

    def collect(self, detector: DetectorAbs):

        timestamp = time.time()
        img = None
        for key in detector.detected_identities:
            identity = detector.detected_identities[key].get("identity", None)
            person_img = detector.detected_identities[key].get("person", None)

            if img is None and identity is not None:
                # image is similar to the first image as it is same frame
                img = person_img.copy()

            if identity is not None and person_img is not None:
                self.queue.put({
                    'timestamp': timestamp,
                    'identity': identity,
                    'image': img
                })

    def write_data(self):
        while True:

            if self.stopped:
                break

            try:
                # Get a point from the queue with a timeout
                write_msg = self.queue.get(timeout=10)
                schedule.run_pending()

                timestamp, img, identity = write_msg['timestamp'], write_msg['image'], write_msg['identity']

                # get year month day hour minute second
                alarm_time = time.localtime(timestamp)
                year = alarm_time.tm_year
                month = "{:02}".format(alarm_time.tm_mon)
                day = "{:02}".format(alarm_time.tm_mday)
                hour = "{:02}".format(alarm_time.tm_hour)
                minute = "{:02}".format(alarm_time.tm_min)

                # os.makedirs(f'{self.folder_name}/{year}-{month}-{day}', exist_ok=True)
                file_name = f'{self.folder_name}/{year}-{month}-{day}/{hour}-{minute}-{identity}-{self.camera_str}.jpg'

                # Save the image to a file
                cv2.imwrite(file_name, img)


            except queue.Empty:
                # The queue is empty, continue the loop
                continue
