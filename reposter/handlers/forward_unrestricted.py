import reposter.handlers.other
import reposter.funcs.logging
import reposter.funcs.handle
import reposter.funcs.other
import reposter.core.config
import reposter.core.common
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

    async def copy_all(
        self,
    ) -> None:
        if self.src_msg.media_group_id:
            to_call = self.copy_media_group
        else:
            to_call = self.copy_one
        await reposter.handlers.other.parse_targets(
            target_any=self.target_any,
            to_call=to_call,
        )

    async def copy_one(
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
            hash = reposter.funcs.other.get_hash(self.src_msg),
            src_msg=self.src_in_db.id,
            src_chat=self.src_in_db.chat.id,
            target_msg=target_msg.id,
            target_chat=target_msg.chat.id
        )
        reposter.funcs.logging.log_msg(
            to_log='[green]\\[success forward][/]',
            src_msg=self.src_msg,
            target_msg=target_msg,
        )

    async def copy_media_group(
        self,
        target: str | int,
    ) -> None:
        src_media_group = await self.src_msg.get_media_group()
        if self.src_msg.id != src_media_group[0].id:
            return
        target_media_group = await reposter.core.common.tg.client.copy_media_group(
            chat_id=target,
            from_chat_id=self.src_msg.chat.id,
            message_id=self.src_msg.id,
        )
        for src_msg, target_msg in zip(
            src_media_group,
            target_media_group,
        ):
            await reposter.db.models.Msg.create(
                hash = reposter.funcs.other.get_hash(self.src_msg),
                src_msg=src_msg.id,
                src_chat=src_msg.chat.id,
                target_msg=target_msg.id,
                target_chat=target_msg.chat.id
            )
            reposter.funcs.logging.log_msg(
                to_log='[green]\\[success forward media group][/]',
                src_msg=src_msg,
                target_msg=target_msg,
            )

