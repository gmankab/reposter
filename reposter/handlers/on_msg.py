import reposter.handlers.forward_unrestricted
import reposter.handlers.resend_restricted
import reposter.handlers.stream_notify
import reposter.handlers.service
import reposter.handlers.edit
import reposter.funcs.handle
import reposter.funcs.other
import reposter.core.common
import reposter.core.config
import reposter.core.types
import reposter.db.models
import pyrogram.types
import datetime


class OnMsg:
    def __init__(
        self,
        target_any: reposter.core.types.target
    ) -> None:
        self.target_any: reposter.core.types.target = target_any
        assert isinstance(self.target_any, (str, int, list))

    async def on_new_msg(
        self,
        _,
        src_msg: pyrogram.types.Message,
    ) -> None:
        link = reposter.funcs.other.single_link(src_msg)
        reposter.core.common.log(
            f'[green]\\[new msg] [blue]{link}'
        )
        if reposter.core.config.json.repost_delay_seconds:
            await reposter.funcs.handle.wait(
                reposter.core.config.json.repost_delay_seconds,
                text='repost delay',
            )
        if src_msg.service:
            service = reposter.handlers.service.Service(
                target_any=self.target_any,
                src_msg=src_msg,
            )
            await service.service_all()
            if src_msg.service == pyrogram.enums.MessageServiceType.VIDEO_CHAT_STARTED:
                stream_notify = reposter.handlers.stream_notify.StreamNotify(
                    target_any=self.target_any,
                )
                await stream_notify.notify_all()
            return
        if src_msg.has_protected_content or src_msg.chat.has_protected_content:
            if src_msg.media_group_id:
                resend_media_group = reposter.handlers.resend_restricted.ResendMediaGroup(
                    src_msg=src_msg,
                    target_any=self.target_any,
                )
                await resend_media_group.all()
            else:
                resend_one = reposter.handlers.resend_restricted.ResendOne(
                    src_msg=src_msg,
                    target_any=self.target_any,
                )
                await resend_one.all()
        else:
            real_time_forward = reposter.handlers.forward_unrestricted.ForwardUnrestricted(
                target_any=self.target_any,
                src_to_forward=src_msg,
                src_in_db=src_msg,
            )
            await real_time_forward.copy_all()

    async def on_edited_msg(
        self,
        _,
        src_msg: pyrogram.types.Message,
    ) -> None:
        link = reposter.funcs.other.single_link(src_msg)
        reposter.core.common.log(
            f'[bright_cyan]\\[new edit] [blue]{link}'
        )
        if reposter.core.config.json.edit_timeout_seconds:
            send_how_long_ago = src_msg.edit_date - src_msg.date
            timeout = datetime.timedelta(seconds=reposter.core.config.json.edit_timeout_seconds)
            if send_how_long_ago > timeout:
                reposter.core.common.log(
                    f'[yellow]\\[warn] [blue]{link} edited but send too long ago'
                )
                return
        db_msgs = await reposter.db.models.Msg.filter(
            src_msg=src_msg.id,
            src_chat=src_msg.chat.id
        )
        if not db_msgs:
            reposter.core.common.log(
                f'[yellow]\\[warn] [blue]{link} edited but was never saved in db'
            )
            return
        for db_msg in db_msgs:
            target_msg = await reposter.core.common.tg.client.get_messages(
                chat_id=db_msg.target_chat,
                message_ids=db_msg.target_msg,
            )
            assert isinstance(
                target_msg,
                pyrogram.types.Message,
            )
            edit = reposter.handlers.edit.Edit(
                target_msg=target_msg,
                src_msg=src_msg,
                db_msg=db_msg,
            )
            await edit.edit()

