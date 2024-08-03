import time
from typing import Optional

from influxdb_client_3 import Point

from env import INFLUXDB_DB
from influx import get_influx_client


class InfluxAlarm:
    def __init__(self):
        self.client = get_influx_client()

    def alarm_check(self, alarm_check_period='15 seconds', alarm_raise_interval='15 minutes',
                    last_seen_interval='5 minutes'):
        query = f"""
        SELECT name,
        SUM(count) as "person_detection_count",
        max(TIME) as "last_seen",
        min(track_id) as "track_id"    
        FROM "home_db"
        WHERE time >= now() - interval '{alarm_check_period}'
        AND name NOT in (SELECT DISTINCT name FROM "home_db_alarm" WHERE time >= now() - interval '{alarm_raise_interval}')
        AND name NOT in (SELECT DISTINCT name FROM "home_db" WHERE time BETWEEN now() - interval '{last_seen_interval} {alarm_check_period}' AND now() - interval '{alarm_check_period}')
        AND name is NOT NULL
        GROUP BY name
        ORDER BY last_seen DESC    
        """

        # Execute the query
        table = self.client.query(query=query, database=INFLUXDB_DB, language="sql")

        # Convert to dataframe
        df = table.to_pandas()
        df['last_seen'] = df['last_seen'].dt.tz_localize('UTC').dt.tz_convert('Asia/Tel_Aviv')
        return df.to_records()

    def write_alarm(self, name: str, tracking_id: Optional[int] = None):

        point = Point("home_db_alarm")

        point.field("count", 1)
        point.time(time.time_ns())

        if tracking_id is not None:
            point.tag("track_id", tracking_id)

        if name is not None:
            point.tag("name", name)

        # Write the alarm to the database
        self.client.write(point)


if __name__ == '__main__':
    influx_alarm = InfluxAlarm()
    influx_alarm.write_alarm("test_name", 42)
    print("Alarm written to InfluxDB")
