import os
from typing import Optional

from pandas import Timestamp

from env import CAMERA_COUNT


def get_file_name(base_folder, hour, minute, name, camera_id: Optional[int] = None):
    hour_str = "{:02}".format(hour)
    minute_str = "{:02}".format(minute)
    if camera_id is None:
        file_name = f"{hour_str}-{minute_str}-{name}.jpg"
    else:
        camera_str = "{:02}".format(camera_id)
        file_name = f"{hour_str}-{minute_str}-{name}-{camera_str}.jpg"

    full_path = base_folder + file_name
    return full_path


def get_detector_file_name(name: str, frame_timestamp: Timestamp):
    date_folder = frame_timestamp.strftime('%Y-%m-%d')
    base_folder = f"../detector/images/{date_folder}/"
    hour = frame_timestamp.hour
    minute = frame_timestamp.minute

    for camera_id in range(0, CAMERA_COUNT):
        full_path = get_file_name(base_folder, hour, minute, name, camera_id)
        # check if file exists
        if os.path.exists(full_path):
            return full_path

    for camera_id in range(0, CAMERA_COUNT):
        # try to check minute before
        if minute == 0:
            minute = 59
            hour = hour - 1 % 24
        else:
            minute = minute - 1

        full_path = get_file_name(base_folder, hour, minute, name, camera_id)

        if os.path.exists(full_path):
            return full_path

    hour = frame_timestamp.hour
    minute = frame_timestamp.minute

    for camera_id in range(0, CAMERA_COUNT):

        # try to check minute after
        if minute == 59:
            minute = 0
            hour = hour + 1 % 24
        else:
            minute = minute + 1

        full_path = get_file_name(base_folder, hour, minute, name, camera_id)

        if os.path.exists(full_path):
            return full_path

        return None


if __name__ == '__main__':
    t = Timestamp('2024-07-29 19:31:11.632039700+0300', tz='Asia/Tel_Aviv')
    print(get_detector_file_name('Ilay', t))
