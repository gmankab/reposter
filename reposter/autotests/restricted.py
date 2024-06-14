import pyrogram
import reposter.tg.unrestricted
import reposter.tg.restricted
import reposter.funcs.handle
import reposter.core.config
import reposter.core.types


async def restricted(
    msg: pyrogram.types.Message
) -> str:
    resender = reposter.tg.restricted.Resender(
        source_msg=msg,
        target_chat=reposter.core.config.tests.target,
    )
    await reposter.funcs.handle.run_excepted(
        resender.resend_anything,
    )
    return f'restricted {resender.media_value} {resender.link}'

