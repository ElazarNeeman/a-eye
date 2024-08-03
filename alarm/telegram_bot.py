import asyncio
import threading
import time

from telethon import TelegramClient, events

from env import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_CHANNEL_ID
from influx_query import query_home_db, query_who_at_home, format_query_query_who_at_home


class TelegramBot:

    def __init__(self):
        self.client = None
        self.alarm_queue = asyncio.Queue()
        self.alarm_thread = threading.Thread(target=self.__bot_thread, args=())
        self.alarm_thread.daemon = True

    def __bot_thread(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.client = TelegramClient('telegram_bot_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
        self.client.start()

        @self.client.on(events.NewMessage(chats=TELEGRAM_CHANNEL_ID))
        async def on_message(event):
            print(f"!!! got from {event.peer_id}", event.raw_text)
            if 'hello' in event.raw_text:
                await event.reply('hi!')
            if 'who' in event.raw_text:
                print('got who')
                await self.__reply_who(event)
            if 'stats' in event.raw_text:
                await self.__send_stats(event)

        self.client.loop.run_until_complete(self.__bot_worker())
        self.client.loop.close()

    async def start(self):
        self.alarm_thread.start()

    async def __bot_worker(self):
        print("Alarm worker started")

        # welcome_message = ('Hello, a-eye! I am ready to raise alarms. send me "who" to get people in house, '
        #                    'and "reset" to reset detections')

        welcome_message = 'Hello, a-eye! I am ready to chat.'

        print("telegram channel:", TELEGRAM_CHANNEL_ID)
        await self.client.send_message(TELEGRAM_CHANNEL_ID, welcome_message)

        while True:
            alarm_data = await self.alarm_queue.get()
            if alarm_data is None:
                break
            await self.process_alarm(alarm_data)
            self.alarm_queue.task_done()

    async def process_alarm(self, alarm_data):
        name = alarm_data['name']
        print(f"{time.ctime()} Raising alarm for {name}")
        file_name = alarm_data.get('file_name', None)

        if self.client:
            if file_name is None:
                await self.client.send_message(TELEGRAM_CHANNEL_ID, alarm_data["message"])
            else:
                await self.client.send_file(TELEGRAM_CHANNEL_ID, file_name, caption= alarm_data["message"])

    async def raise_alarm(self, alarm_data):
        await self.alarm_queue.put(alarm_data)

    def stop(self):
        self.alarm_queue.put((None, None))
        self.alarm_thread.join()

    async def __reply_who(self, event):
        interval = '6 hours'
        data = query_who_at_home(interval)
        msg = format_query_query_who_at_home(data)
        await event.reply(f"People in house last {interval}:\n" + msg)

    async def __send_stats(self, _):
        try:
            file_name = query_home_db()
            await self.client.send_file(TELEGRAM_CHANNEL_ID, file_name, caption="People in last 12 hours")
        except Exception as e:
            print(e)
