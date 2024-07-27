import asyncio

from influx_query import query_who_at_home
from telegram_bot import TelegramBot


async def alarms_scheduler(bot):
    while True:
        print("Running alarms_scheduler")
        df = query_who_at_home()
        print(df)
        await asyncio.sleep(30)  # wait for 5 seconds before the next iteration


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
