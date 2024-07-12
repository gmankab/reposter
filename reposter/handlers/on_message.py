import reposter.handlers.forward_unrestricted
import reposter.handlers.resend_restricted
import reposter.handlers.stream_notify
import reposter.handlers.service
import reposter.core.types
import pyrogram.types


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
            real_time_resend = reposter.handlers.resend_restricted.ResendRestricted(
                src_msg=src_msg,
                target_any=self.target_any,
            )
            await real_time_resend.resend_all()
        else:
            real_time_forward = reposter.handlers.forward_unrestricted.ForwardUnrestricted(
                src_msg=src_msg,
                target_any=self.target_any,
            )
            await real_time_forward.forward_all()

