import reposter.handlers.forward_unrestricted
import reposter.funcs.handle
import reposter.funcs.logging
import reposter.core.config
import reposter.core.types
import reposter.tg.restricted
import pyrogram.types


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
            real_time_forward = reposter.handlers.forward_unrestricted.ForwardUnrestricted(
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

