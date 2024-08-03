import asyncio
import os

from pandas import Timestamp

from file_db import get_detector_file_name
from influx_alarm import InfluxAlarm
from telegram_bot import TelegramBot


async def alarms_scheduler(bot):
    def format_query_alarm_check(d):
        return f"""
Name: {d['name']}
Track ID: {d['track_id']}
Count: {d['person_detection_count']}
Last Seen :  {d['last_seen'].strftime('%H:%M:%S')}
"""

    alarm_client = InfluxAlarm()
    while True:
        await asyncio.sleep(5)  # wait for 10 seconds before the next iteration

        try:
            df = alarm_client.alarm_check()

            if len(df) <= 0:
                continue

            print(df)

            for record in df:
                msg = format_query_alarm_check(record)
                alarm_client.write_alarm(record['name'], record['track_id'])
                await bot.raise_alarm(
                    {
                        "name": record['name'],
                        "message": msg,
                        "file_name": get_detector_file_name(record['name'], record['last_seen'])
                    })

        except Exception as e:
            print(e)


async def daily_scheduler(bot):
    while True:
        print("Running daily scheduler")
        await asyncio.sleep(86400)  # wait for 24 hours before the next iteration


async def main():
    bot = TelegramBot()
    await bot.start()

    # Start the schedulers
    asyncio.create_task(alarms_scheduler(bot))
    asyncio.create_task(daily_scheduler(bot))

    while True:
        await asyncio.sleep(1000)


if __name__ == '__main__':
    # run this to initialize the telegram session
    asyncio.run(main())
