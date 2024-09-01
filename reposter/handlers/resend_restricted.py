import reposter.handlers.forward_unrestricted
import reposter.funcs.handle
import reposter.funcs.logging
import reposter.core.config
import reposter.core.types
import reposter.tg.restricted
import reposter.db.models
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
                target_any=self.target_any,
                src_to_forward=resent_to_log_chat,
                src_in_db=self.src_msg,
            )
            return await real_time_forward.forward_all()
        elif isinstance(self.target_any, (str, int)):
            target_msg = await self.resend_one(
                src_msg=self.src_msg,
                target=self.target_any,
            )
            await reposter.db.models.Msg.create(
                src_msg=self.src_msg.id,
                src_chat=self.src_msg.chat,
                target_msg=target_msg.id,
                target_chat=target_msg.chat.id
            )
        else:
            raise AssertionError

    async def resend_one(
        self,
        src_msg: pyrogram.types.Message,
        target: str | int,
    ) -> pyrogram.types.Message:
        resender = reposter.tg.restricted.Resender(
            src_msg=self.src_msg,
            target_chat=target,
        )
        target_msg = await reposter.funcs.handle.run_excepted(
            resender.resend_anything,
        )
        assert target_msg
        reposter.funcs.logging.log_msg(
            to_log='[green]\\[resend][/]',
            src_msg=src_msg,
            target_msg=target_msg,
        )
        return target_msg

