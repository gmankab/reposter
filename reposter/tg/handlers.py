import pyrogram.handlers.message_handler
import reposter.tg.restricted
import reposter.funcs.logging
import reposter.funcs.other
import reposter.core.config
import reposter.core.common
import reposter.core.types
import pyrogram.filters
import pyrogram.types
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


def set_handlers():
    for source, target in reposter.core.config.json.chats.items():
        on_message = OnMessage(target_any=target)
        if isinstance(source, str):
            if 't.me/+' not in source:
                source = source.replace('https://t.me/', '@')
                source = source.replace('http://t.me/', '@')
            try:
                source = int(source)
            except Exception:
                pass
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
        source_msg: pyrogram.types.Message,
    ) -> None:
        if source_msg.has_protected_content or source_msg.chat.has_protected_content:
            real_time_resend = RealTimeResend(
                source_msg=source_msg,
                target_any=self.target_any,
            )
            await real_time_resend.resend_anything()
        else:
            real_time_forward = RealTimeForward(
                source_msg=source_msg,
                target_any=self.target_any,
            )
            await real_time_forward.forward_anything()


class RealTimeResend:
    def __init__(
        self,
        target_any: reposter.core.types.target,
        source_msg: pyrogram.types.Message,
    ) -> None:
        self.target_any: reposter.core.types.target = target_any
        self.source_msg = source_msg
        assert isinstance(self.target_any, (str, int, list))

    async def resend_anything(self) -> None:
        if isinstance(self.target_any, list):
            assert reposter.core.config.json.logs_chat
            resent_to_log_chat = await self.resend_one(
                source_msg=self.source_msg,
                target_id=reposter.core.config.json.logs_chat,
            )
            real_time_forward = RealTimeForward(
                source_msg=resent_to_log_chat,
                target_any=self.target_any,
            )
            await real_time_forward.forward_anything()
        elif isinstance(self.target_any, (str, int)):
            await self.resend_one(
                source_msg=self.source_msg,
                target_id=self.target_any,
            )
        else:
            raise AssertionError

    async def resend_one(
        self,
        source_msg: pyrogram.types.Message,
        target_id: str | int,
    ) -> pyrogram.types.Message:
        resender = reposter.tg.restricted.Resender(
            source_msg=self.source_msg,
            target_chat=target_id,
        )
        target_msg = await resender.resend_anything()
        assert target_msg
        reposter.funcs.logging.log_msg(
            to_log=f'[green]\\[{resender.media_value}][/]',
            source_msg=source_msg,
            target_msg=target_msg,
        )
        return target_msg


class RealTimeForward:
    def __init__(
        self,
        target_any: reposter.core.types.target,
        source_msg: pyrogram.types.Message,
    ) -> None:
        self.target_any: reposter.core.types.target = target_any
        self.source_msg = source_msg
        assert isinstance(self.target_any, (str, int, list))

    async def forward_anything(
        self,
    ) -> None:
        if isinstance(self.target_any, list):
            for subtarget in self.target_any:
                await self.forward_one(
                    source_msg=self.source_msg,
                    target_id=subtarget,
                )
        elif isinstance(self.target_any, (str, int)):
            await self.forward_one(
                source_msg=self.source_msg,
                target_id=self.target_any,
            )
        else:
            raise AssertionError

    async def forward_one(
        self,
        source_msg: pyrogram.types.Message,
        target_id: str | int,
    ) -> None:
        target_msg = await source_msg.forward(
            chat_id=target_id,
            drop_author=reposter.core.config.json.drop_author,
        )
        assert isinstance(target_msg, pyrogram.types.Message)
        reposter.funcs.logging.log_msg(
            to_log='[green]\\[forward][/]',
            source_msg=source_msg,
            target_msg=target_msg,
        )

