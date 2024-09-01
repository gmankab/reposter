import reposter.handlers.other
import reposter.funcs.logging
import reposter.funcs.handle
import reposter.core.config
import reposter.core.types
import reposter.db.models
import pyrogram.types


class ForwardUnrestricted:
    def __init__(
        self,
        target_any: reposter.core.types.target,
        src_to_forward: pyrogram.types.Message,
        src_in_db: pyrogram.types.Message,
    ) -> None:
        self.target_any: reposter.core.types.target = target_any
        self.src_msg = src_to_forward
        self.src_in_db: pyrogram.types.Message = src_in_db
        assert isinstance(self.target_any, (str, int, list))

    async def forward_all(
        self,
    ) -> None:
        await reposter.handlers.other.parse_targets(
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
        await reposter.db.models.Msg.create(
            src_msg=self.src_in_db.id,
            src_chat=self.src_in_db.chat.id,
            target_msg=target_msg.id,
            target_chat=target_msg.chat.id
        )
        reposter.funcs.logging.log_msg(
            to_log='[green]\\[forward][/]',
            src_msg=self.src_msg,
            target_msg=target_msg,
        )

