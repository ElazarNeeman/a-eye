from environs import Env

env = Env()
env.read_env()

# STREAM_ID = env("STREAM_ID")  # the stream id of the camera
QUIT_KEY = ord('q')

# Influx db
INFLUXDB_TOKEN = env("INFLUXDB_TOKEN", None)
INFLUXDB_HOST = env("INFLUXDB_HOST", None)
INFLUXDB_ORG = env("INFLUXDB_ORG", None)
INFLUXDB_DB = env("INFLUXDB_DB", None)
CAMERA_COUNT = env.int("CAMERA_COUNT")
DB_PATH = env("DB_PATH", "family")


def get_stream_id(camera_id: int):
    stream_id = env(f"STREAM_ID_{camera_id}")

    if stream_id.isdigit():
        # web-cam case
        return int(stream_id)

    return stream_id
