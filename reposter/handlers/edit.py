import reposter.funcs.logging
import reposter.funcs.other
import reposter.core.common
import pyrogram.types


class Edit:
    def __init__(
        self,
        src_msg: pyrogram.types.Message,
        target_msg: pyrogram.types.Message,
    ) -> None:
        self.src_msg = src_msg
        self.target_msg = target_msg
        self.links = reposter.funcs.other.double_links(
            src_msg=src_msg,
            target_msg=target_msg,
        )

    def log(self) -> None:
        reposter.funcs.logging.log_msg(
            to_log='[green]\\[edit][/]',
            src_msg=self.src_msg,
            target_msg=self.target_msg,
        )

    async def edit(self) -> None:
        if self.src_msg.text or self.target_msg.text:
            if self.src_msg.text.markdown != self.target_msg.text.markdown:
                await self.target_msg.edit_text(self.src_msg.text.markdown)
                return
        if self.src_msg.caption or self.target_msg.caption:
            if not self.src_msg.caption:
                await self.target_msg.edit_caption('')
                return self.log()
            if not self.target_msg.caption:
                await self.target_msg.edit_caption(self.src_msg.caption.markdown)
                return self.log()
            if self.src_msg.caption.markdown != self.target_msg.caption.markdown:
                await self.target_msg.edit_caption(self.src_msg.caption.markdown)
                return self.log()
        reposter.core.common.log(
            f'[yellow]\\[warn][/] can\'t see changes between {self.links}'
        )

