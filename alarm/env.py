from environs import Env

env = Env()
env.read_env()

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
TELEGRAM_API_ID = env("TELEGRAM_APP_ID")  # 123456
TELEGRAM_API_HASH = env("TELEGRAM_API_HASH")  # '8a09818d578d4950bd26a475f765b44e'
TELEGRAM_CHANNEL_ID = env.int("TELEGRAM_CHANNEL_ID")  # -1001485389244

# Influx db stats
INFLUXDB_TOKEN = env("INFLUXDB_TOKEN")
INFLUXDB_HOST = env("INFLUXDB_HOST")
INFLUXDB_ORG = env("INFLUXDB_ORG")
INFLUXDB_DB = env("INFLUXDB_DB")