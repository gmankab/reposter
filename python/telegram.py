from init import *
from telethon import TelegramClient
import betterdata as bd
import asyncio


def progress_callback(current, total):
    print(f'{round(current / total * 100, 1)}% Uploaded {nice(current)} out of {nice(total)}')


async def send_file(client):
    chat = await client.get_input_entity(telegram['phone_number'])
    await client.send_file(
        entity=chat,
        file="C:/Users/Gmank/Desktop/100MB",
        caption="aboba",
        progress_callback=progress_callback
    )


async def main():
    if 'client.pickle' not in os.listdir('data'):
        client = TelegramClient(Project.name, telegram.api_id, telegram.api_hash)
        client.name = 'client.pickle'
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(telegram.phone_number)
            await client.sign_in(telegram.phone_number, input(
                'please input your phone number,\n'
                'so that we can make a bot and send world saves to telegram:\n'
            ))
    else:
        client = bd.load('client.pickle')
        await client.connect()

    client.__qualname__ = 'client'
    bd.dump(client)

    await send_file(client)


asyncio.run(main())
