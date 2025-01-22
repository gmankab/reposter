import reposter.handlers.stream_notify
import reposter.handlers.other
import reposter.funcs.logging
import reposter.funcs.handle
import reposter.core.common
import reposter.core.types
import pyrogram.types


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
        await reposter.handlers.other.parse_targets(
            target_any=self.target_any,
            to_call=self.service_one,
        )
        if self.src_msg.service == pyrogram.enums.MessageServiceType.VIDEO_CHAT_STARTED:
            stream_notify = reposter.handlers.stream_notify.StreamNotify(
                target_any=self.target_any,
            )
            await stream_notify.notify_all()

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
            to_log=f'[green]\\[success service][/] {text}',
            src_msg=self.src_msg,
            target_msg=target_msg,
        )

