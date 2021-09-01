from init import *
from telethon import TelegramClient


async def upload_telegram():
    client = TelegramClient(Project.name, telegram.api_id[0], telegram.api_hash[0])
    await client.connect()

    # if not await client.is_user_authorized():
    #     await client.send_code_request(telegram['account_phone_number'])
    #     await client.sign_in(telegram['account_phone_number'], input('Enter code: '))


async def send_file(client):
    chat = await client.get_input_entity(telegram['phone_number'])

    def progress_callback(current, total):
        print(f'{round(current / total * 100, 1)}% Uploaded {nice(current)} out of {nice(total)}')

    await client.send_file(
        entity=chat,
        file="C:/Users/Gmank/Desktop/srv2.zip",
        caption="aboba",
        progress_callback=progress_callback
    )

print(telegram.T)
