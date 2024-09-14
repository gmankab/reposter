import reposter.handlers.forward_unrestricted
import reposter.handlers.other
import reposter.funcs.handle
import reposter.funcs.logging
import reposter.funcs.other
import reposter.core.config
import reposter.core.common
import reposter.core.types
import reposter.tg.restricted
import reposter.db.models
import pyrogram.types


class ResendOne:
    def __init__(
        self,
        target_any: reposter.core.types.target,
        src_msg: pyrogram.types.Message,
    ) -> None:
        self.target_any: reposter.core.types.target = target_any
        self.src_msg = src_msg
        assert isinstance(self.target_any, (str, int, list))

    async def all(self):
        if isinstance(self.target_any, list):
            await self.multiple_targets()
        elif isinstance(self.target_any, (str, int)):
            await self.one_target(
                target=self.target_any,
                save_db=True,
            )
        else:
            raise AssertionError

    async def multiple_targets(self) -> None:
        assert reposter.core.config.json.logs_chat
        resent_to_log_chat = await self.one_target(
            target=reposter.core.config.json.logs_chat,
            save_db=False,
        )
        real_time_forward = reposter.handlers.forward_unrestricted.ForwardUnrestricted(
            target_any=self.target_any,
            src_to_forward=resent_to_log_chat,
            src_in_db=self.src_msg,
        )
        await real_time_forward.copy_all()

    async def one_target(
        self,
        target: str | int,
        save_db: bool,
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
            to_log='[green]\\[success resend][/]',
            src_msg=self.src_msg,
            target_msg=target_msg,
        )
        if save_db:
            await reposter.db.models.Msg.create(
                hash = reposter.funcs.other.get_hash(self.src_msg),
                src_msg=self.src_msg.id,
                src_chat=self.src_msg.chat.id,
                target_msg=target_msg.id,
                target_chat=target_msg.chat.id
            )
        return target_msg



class ResendMediaGroup:
    def __init__(
        self,
        target_any: reposter.core.types.target,
        src_msg: pyrogram.types.Message,
    ) -> None:
        self.target_any: reposter.core.types.target = target_any
        self.src_msg = src_msg
        self.media: list[reposter.core.types.input_media] = []
        self.src_media_group: list[pyrogram.types.Message]
        assert isinstance(self.target_any, (str, int, list))

    async def all(self) -> None:
        self.src_media_group = await self.src_msg.get_media_group()
        if self.src_msg.id != self.src_media_group[0].id:
            return
        for src_msg in self.src_media_group:
            self.media.append(
                await self.get_media(src_msg)
            )
        await reposter.handlers.other.parse_targets(
            target_any=self.target_any,
            to_call=self.one_target,
        )

    async def one_target(
        self,
        target: str | int,
    ):
        target_media_group = await reposter.core.common.tg.client.send_media_group(
            chat_id=target,
            media=self.media,
        )
        for src_msg, target_msg in zip(
            self.src_media_group,
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
                to_log='[green]\\[success resend media group][/]',
                src_msg=src_msg,
                target_msg=target_msg,
            )

    async def get_media(
        self,
        src_msg: pyrogram.types.Message,
    ) -> reposter.core.types.input_media:
        resend_one = ResendOne(
            target_any=reposter.core.config.json.logs_chat,
            src_msg=src_msg,
        )
        resent_to_log_chat = await resend_one.one_target(
            target=reposter.core.config.json.logs_chat,
            save_db=False,
        )
        if resent_to_log_chat.caption:
            caption: str = resent_to_log_chat.caption.markdown
        else:
            caption: str = ''
        media_value = str(resent_to_log_chat.media.value)
        media = getattr(resent_to_log_chat, media_value)
        assert isinstance(media, reposter.core.types.in_group_media)
        input_media = getattr(pyrogram.types, 'InputMedia' + media_value.capitalize())
        inputted = input_media(
            media=media.file_id,
            caption=caption
        )
        assert isinstance(inputted, reposter.core.types.input_media)
        return inputted

