import reposter.handlers.on_message
import reposter.funcs.handle
import reposter.funcs.other
import reposter.core.common
import reposter.core.config
import pyrogram.raw.functions
import asyncio
import sys


async def main():
    set_handlers()
    try:
        if reposter.core.config.json.online_status_every_seconds:
            await stay_online()
        else:
            while True:
                await asyncio.sleep(1)
    except KeyboardInterrupt:
        reposter.funcs.other.before_shutdown()
        sys.exit()


async def stay_online():
    online = pyrogram.raw.functions.account.update_status.UpdateStatus(
        offline=False,
    )
    while True:
        await asyncio.sleep(
            reposter.core.config.json.online_status_every_seconds
        )
        await reposter.funcs.handle.run_excepted(
            callable=reposter.core.common.tg.client.invoke,
            to_raise=False,
            repeat=False,
            query=online,
        )


def chat_str_fix(chat: str | int) -> str | int:
    if isinstance(chat, int):
        return chat
    if 't.me/+' not in chat:
        chat = chat.replace('https://t.me/', '@')
        chat = chat.replace('http://t.me/', '@')
    try:
        return int(chat)
    except Exception:
        return chat


def set_handlers():
    notify = []
    for chat_to_fix in reposter.core.config.json.stream_notify_chats:
         notify.append(
            chat_str_fix(chat_to_fix)
         )
    reposter.core.config.json.stream_notify_chats = notify
    for source_to_fix, target_to_fix in reposter.core.config.json.chats.items():
        source = chat_str_fix(source_to_fix)
        if isinstance(target_to_fix, list):
            target = []
            for i in target_to_fix:
                target.append(chat_str_fix(i))
        else:
            target = chat_str_fix(target_to_fix)
        on_message = reposter.handlers.on_message.OnMessage(target_any=target)
        reposter.core.common.tg.client.add_handler(
            pyrogram.handlers.message_handler.MessageHandler(
                callback=on_message.handler,
                filters=pyrogram.filters.chat(source),
            )
        )
        reposter.core.common.log(
            f'[green]\\[added handler][/] [blue]{source}[/] -> [yellow]{target}'
        )


