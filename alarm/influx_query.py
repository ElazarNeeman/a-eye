from influxdb_client_3 import InfluxDBClient3
import plotly.express as px
import plotly.io as pio

from env import INFLUXDB_HOST, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_DB


def query_home_db():
    query = """
    SELECT name,
    DATE_BIN(INTERVAL '5 minutes', time AT TIME ZONE 'UTC') AS _time,
    SUM(count) as "person_detection_count"
    FROM "home_db"
    WHERE time >= now() - interval '12 hours'
    GROUP BY name, _time
    ORDER BY _time
    """

    client = get_influx_client()

    # Execute the query
    table = client.query(query=query, database=INFLUXDB_DB, language="sql")

    # Convert to dataframe
    df = table.to_pandas()
    df['_time'] = df['_time'].dt.tz_convert('Asia/Tel_Aviv')
    fig = px.bar(df, x='_time', y='person_detection_count', color='name', title='Person Detections Over Time')
    file_name = 'bar_chart.jpg'
    pio.write_image(fig, 'bar_chart.jpg')
    return file_name


def query_who_at_home():
    query = """
    SELECT name,
    SUM(count) as "person_detection_count",
    max(TIME) as "last_seen",
    min(TIME) as "first_seen"
    FROM "home_db"
    WHERE time >= now() - interval '6 hours'
    GROUP BY name
    ORDER BY last_seen DESC
    """

    client = get_influx_client()

    # Execute the query
    table = client.query(query=query, database=INFLUXDB_DB, language="sql")

    # Convert to dataframe
    df = table.to_pandas()
    df['last_seen'] = df['last_seen'].dt.tz_localize('UTC').dt.tz_convert('Asia/Tel_Aviv')
    df['first_seen'] = df['first_seen'].dt.tz_localize('UTC').dt.tz_convert('Asia/Tel_Aviv')
    return df.to_records()


def format_query_results(df):
    msg = ""
    for record in df:
        msg += f"""
Name: {record['name']}
Count: {record['person_detection_count']}
Last Seen :  {record['last_seen'].strftime('%H:%M:%S')}
First Seen: {record['first_seen'].strftime('%H:%M:%S')}
-----------------------------------"""
    return msg


def get_influx_client():
    return InfluxDBClient3(
        host=INFLUXDB_HOST,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG,
        database=INFLUXDB_DB,
    )


if __name__ == '__main__':
    df = query_who_at_home()
    # pretty print the dataframe
    msg = format_query_results(df)
    print(msg)
