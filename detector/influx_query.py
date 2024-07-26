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

    client = InfluxDBClient3(
        host=INFLUXDB_HOST,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG,
        database=INFLUXDB_DB,
    )

    # Execute the query
    table = client.query(query=query, database=INFLUXDB_DB, language="sql")

    # Convert to dataframe
    df = table.to_pandas()
    df['_time'] = df['_time'].dt.tz_convert('Asia/Tel_Aviv')
    fig = px.bar(df, x='_time', y='person_detection_count', color='name', title='Person Detections Over Time')
    file_name = 'bar_chart.jpg'
    pio.write_image(fig, 'bar_chart.jpg')
    return file_name
