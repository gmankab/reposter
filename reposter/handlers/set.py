import pyrogram.handlers.message_handler
import reposter.funcs.other
import reposter.core.common
import reposter.core.config
import reposter.core.types
import reposter.handlers.forward_unrestricted
import reposter.handlers.resend_restricted
import reposter.handlers.stream_notify
import reposter.handlers.service
import asyncio
import sys


async def main():
    set_handlers()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        reposter.funcs.other.before_shutdown()
        sys.exit()


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
        on_message = OnMessage(target_any=target)
        reposter.core.common.tg.client.add_handler(
            pyrogram.handlers.message_handler.MessageHandler(
                callback=on_message.handler,
                filters=pyrogram.filters.chat(source),
            )
        )
        reposter.core.common.log(
            f'[green]\\[added handler][/] [blue]{source}[/] -> [yellow]{target}'
        )


class OnMessage:
    def __init__(
        self,
        target_any: reposter.core.types.target
    ) -> None:
        self.target_any: reposter.core.types.target = target_any
        assert isinstance(self.target_any, (str, int, list))

    async def handler(
        self,
        _,
        src_msg: pyrogram.types.Message,
    ) -> None:
        if src_msg.service:
            service = reposter.handlers.service.Service(
                target_any=self.target_any,
                src_msg=src_msg,
            )
            await service.service_all()
            if src_msg.service == pyrogram.enums.MessageServiceType.VIDEO_CHAT_STARTED:
                stream_notify = reposter.handlers.stream_notify.StreamNotify(
                    target_any=self.target_any,
                )
                await stream_notify.notify_all()
            return
        if src_msg.has_protected_content or src_msg.chat.has_protected_content:
            real_time_resend = reposter.handlers.resend_restricted.ResendRestricted(
                src_msg=src_msg,
                target_any=self.target_any,
            )
            await real_time_resend.resend_all()
        else:
            real_time_forward = reposter.handlers.forward_unrestricted.ForwardUnrestricted(
                src_msg=src_msg,
                target_any=self.target_any,
            )
            await real_time_forward.forward_all()

