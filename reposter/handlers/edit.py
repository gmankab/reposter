import reposter.funcs.logging
import reposter.funcs.other
import reposter.core.common
import reposter.db.models
import pyrogram.types


class Edit:
    def __init__(
        self,
        src_msg: pyrogram.types.Message,
        target_msg: pyrogram.types.Message,
        db_msg: reposter.db.models.Msg,
    ) -> None:
        self.src_msg = src_msg
        self.target_msg = target_msg
        self.db_msg = db_msg
        self.links = reposter.funcs.other.double_links(
            src_msg=src_msg,
            target_msg=target_msg,
        )

    async def log_and_save(self) -> None:
        self.db_msg.hash = self.new_hash
        await self.db_msg.save()
        reposter.funcs.logging.log_msg(
            to_log='[bright_cyan]\\[success edit][/]',
            src_msg=self.src_msg,
            target_msg=self.target_msg,
        )

    async def edit(self) -> None:
        self.new_hash = reposter.funcs.other.get_hash(self.src_msg)
        if self.db_msg.hash == self.new_hash:
            reposter.core.common.log(
                f'[yellow]\\[warn][/] can\'t see changes between {self.links}'
            )
            return
        if self.src_msg.text or self.target_msg.text:
            if self.src_msg.text.markdown != self.target_msg.text.markdown:
                await self.target_msg.edit_text(self.src_msg.text.markdown)
                return await self.log_and_save()
        if self.src_msg.caption or self.target_msg.caption:
            if not self.src_msg.caption:
                await self.target_msg.edit_caption('')
                return await self.log_and_save()
            if not self.target_msg.caption:
                await self.target_msg.edit_caption(self.src_msg.caption.markdown)
                return await self.log_and_save()
            if self.src_msg.caption.markdown != self.target_msg.caption.markdown:
                await self.target_msg.edit_caption(self.src_msg.caption.markdown)
                return await self.log_and_save()
        reposter.core.common.log(
            f'[yellow]\\[warn][/] can\'t see changes between {self.links}'
        )

