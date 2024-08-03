from influxdb_client_3 import InfluxDBClient3
from env import INFLUXDB_HOST, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_DB

def get_influx_client():
    return InfluxDBClient3(
        host=INFLUXDB_HOST,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG,
        database=INFLUXDB_DB,
    )
