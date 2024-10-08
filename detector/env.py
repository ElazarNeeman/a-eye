from environs import Env

env = Env()
env.read_env()

# STREAM_ID = env("STREAM_ID")  # the stream id of the camera
QUIT_KEY = ord('q')

# Influx db
INFLUXDB_TOKEN = env("INFLUXDB_TOKEN")
INFLUXDB_HOST = env("INFLUXDB_HOST")
INFLUXDB_ORG = env("INFLUXDB_ORG")
INFLUXDB_DB = env("INFLUXDB_DB")
CAMERA_COUNT = env.int("CAMERA_COUNT")

def get_stream_id(camera_id: int):
    return env(f"STREAM_ID_{camera_id}")