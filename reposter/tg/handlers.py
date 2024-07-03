import pyrogram.handlers.message_handler
import pyrogram.enums
import reposter.tg.restricted
import reposter.funcs.logging
import reposter.funcs.handle
import reposter.funcs.other
import reposter.core.config
import reposter.core.common
import reposter.core.types
import pyrogram.filters
import pyrogram.types
import asyncio
import typing
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
            service = Service(
                target_any=self.target_any,
                src_msg=src_msg,
            )
            await service.service_all()
            if src_msg.service == pyrogram.enums.MessageServiceType.VIDEO_CHAT_STARTED:
                stream_notify = StreamNotify(
                    target_any=self.target_any,
                )
                await stream_notify.notify_all()
            return
        if src_msg.has_protected_content or src_msg.chat.has_protected_content:
            real_time_resend = ResendRestricted(
                src_msg=src_msg,
                target_any=self.target_any,
            )
            await real_time_resend.resend_all()
        else:
            real_time_forward = ForwardUnrestricted(
                src_msg=src_msg,
                target_any=self.target_any,
            )
            await real_time_forward.forward_all()


class ResendRestricted:
    def __init__(
        self,
        target_any: reposter.core.types.target,
        src_msg: pyrogram.types.Message,
    ) -> None:
        self.target_any: reposter.core.types.target = target_any
        self.src_msg = src_msg
        assert isinstance(self.target_any, (str, int, list))

    async def resend_all(self) -> None:
        if isinstance(self.target_any, list):
            assert reposter.core.config.json.logs_chat
            resent_to_log_chat = await reposter.funcs.handle.run_excepted(
                self.resend_one,
                src_msg=self.src_msg,
                target=reposter.core.config.json.logs_chat,
            )
            real_time_forward = ForwardUnrestricted(
                src_msg=resent_to_log_chat,
                target_any=self.target_any,
            )
            await real_time_forward.forward_all()
        elif isinstance(self.target_any, (str, int)):
            await self.resend_one(
                src_msg=self.src_msg,
                target=self.target_any,
            )
        else:
            raise AssertionError

    async def resend_one(
        self,
        src_msg: pyrogram.types.Message,
        target: str | int,
    ) -> pyrogram.types.Message:
        resender = reposter.tg.restricted.Resender(
            source_msg=self.src_msg,
            target_chat=target,
        )
        target_msg = await reposter.funcs.handle.run_excepted(
            resender.resend_anything,
        )
        assert target_msg
        reposter.funcs.logging.log_msg(
            to_log='[green]\\[resend][/]',
            source_msg=src_msg,
            target_msg=target_msg,
        )
        return target_msg


class ForwardUnrestricted:
    def __init__(
        self,
        target_any: reposter.core.types.target,
        src_msg: pyrogram.types.Message,
    ) -> None:
        self.target_any: reposter.core.types.target = target_any
        self.src_msg = src_msg
        assert isinstance(self.target_any, (str, int, list))

    async def forward_all(
        self,
    ):
        await parse_targets(
            target_any=self.target_any,
            to_call=self.forward_one,
        )

    async def forward_one(
        self,
        target: str | int,
    ) -> None:
        target_msg = await reposter.funcs.handle.run_excepted(
            self.src_msg.forward,
            chat_id=target,
            drop_author=reposter.core.config.json.drop_author,
        )
        assert isinstance(target_msg, pyrogram.types.Message)
        reposter.funcs.logging.log_msg(
            to_log='[green]\\[forward][/]',
            source_msg=self.src_msg,
            target_msg=target_msg,
        )


class Service:
    def __init__(
        self,
        target_any: reposter.core.types.target,
        src_msg: pyrogram.types.Message,
    ) -> None:
        self.target_any: reposter.core.types.target = target_any
        self.src_msg = src_msg
        assert isinstance(self.target_any, (str, int, list))

    async def service_all(
        self,
    ):
        await parse_targets(
            target_any=self.target_any,
            to_call=self.service_one,
        )

    async def service_one(
        self,
        target: str | int,
    ) -> None:
        assert self.src_msg.service
        text = str(self.src_msg.service.value)
        target_msg = await reposter.funcs.handle.run_excepted(
            reposter.core.common.tg.client.send_message,
            chat_id=target,
            text=text,
        )
        assert isinstance(target_msg, pyrogram.types.Message)
        reposter.funcs.logging.log_msg(
            to_log=f'[green]\\[service][/] {text}',
            source_msg=self.src_msg,
            target_msg=target_msg,
        )

class StreamNotify:
    def __init__(
        self,
        target_any: reposter.core.types.target,
    ) -> None:
        self.delay: int = 5
        self.repeat_count: int = 40
        self.target_any: reposter.core.types.target = target_any
        self.progress = reposter.core.common.app.progress
        self.text: str = ''
        assert isinstance(self.target_any, (str, int, list))
        assert isinstance(reposter.core.config.json.stream_notify_chats, list)

    async def notify_all(
        self,
    ):
        task_id_big = self.progress.add_task(
            description='stream notifications',
            total=self.repeat_count,
        )
        task_id_little = self.progress.add_task(
            description=f'{self.delay} seconds delay',
        )
        for index in range(self.repeat_count):
            self.progress.update(
                task_id=task_id_big,
                completed=index,
            )
            self.text = f'stream notifications {index+1}/{self.repeat_count}'
            await parse_targets(
                target_any=reposter.core.config.json.stream_notify_chats,
                to_call=self.notify_one,
            )
            await reposter.funcs.handle.wait(
                seconds=self.delay,
                task_id=task_id_little,
                hide=False,
            )
        self.progress.update(
            task_id=task_id_big,
            completed=self.repeat_count,
            visible=False,
        )
        self.progress.stop_task(
            task_id=task_id_big,
        )

    async def notify_one(
        self,
        target: str | int,
    ):
        await reposter.funcs.handle.run_excepted(
            reposter.core.common.tg.client.send_message,
            chat_id=target,
            text=self.text,
            repeat=False,
            to_raise=False,
        )


async def parse_targets(
    target_any: reposter.core.types.target,
    to_call: typing.Callable,
) -> None:
    if isinstance(target_any, list):
        for subtarget in target_any:
            assert isinstance(subtarget, (str, int))
            await to_call(
                target=subtarget,
            )
    elif isinstance(target_any, (str, int)):
        await to_call(
            target=target_any,
        )
    else:
        raise AssertionError

