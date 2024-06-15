import pyrogram.handlers.message_handler
import reposter.funcs.other
import pyrogram.filters
import pyrogram.types
import reposter.tg.restricted
import reposter.core.config
import reposter.core.common
import asyncio


async def main():
    set_handlers()
    while True:
        await asyncio.sleep(1)


def set_handlers():
    for source_chat, target_chat in reposter.core.config.json.chats.items():
        on_message = OnMessage(target_chat=target_chat)
        reposter.core.common.tg.client.add_handler(
            pyrogram.handlers.message_handler.MessageHandler(
                callback=on_message.handler,
                filters=pyrogram.filters.chat(source_chat),
            )
        )
        reposter.core.common.log(
            f'[green]\\[added handler][/] [blue]{source_chat}[/] -> [yellow]{target_chat}'
        )


class OnMessage:
    def __init__(
        self,
        target_chat: int | str,
    ) -> None:
        self.target_chat: int | str = target_chat
        self.log = reposter.core.common.log

    async def handler(
        self,
        _,
        source_msg: pyrogram.types.Message,
    ) -> None:
        self.source_msg = source_msg
        if self.source_msg.has_protected_content:
            await self.repost_restricted()
        else:
            await self.forward()

    async def repost_restricted(self) -> None:
        resender = reposter.tg.restricted.Resender(
            source_msg=self.source_msg,
            target_chat=self.target_chat,
        )
        target_msg = await resender.resend_anything()
        assert target_msg
        links = reposter.funcs.other.double_links(
            source_msg=self.source_msg,
            target_msg=target_msg,
        )
        self.log(
            f'[green]\\[{resender.media_value}][/] {links}'
        )

    async def forward(self) -> None:
        target_msg = await self.source_msg.forward(
            chat_id=self.target_chat,
            drop_author=reposter.core.config.json.drop_author,
        )
        assert isinstance(target_msg, pyrogram.types.Message)
        links = reposter.funcs.other.double_links(
            source_msg=self.source_msg,
            target_msg=target_msg,
        )
        self.log(
            f'[green]\\[forward][/] {links}'
        )

