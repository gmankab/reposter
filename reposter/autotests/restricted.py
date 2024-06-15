import reposter.funcs.other
import reposter.tg.restricted
import reposter.funcs.handle
import reposter.core.config
import reposter.core.types
import pyrogram.errors
import pyrogram


async def restricted(
    source_msg: pyrogram.types.Message
) -> str:
    resender = reposter.tg.restricted.Resender(
        source_msg=source_msg,
        target_chat=reposter.core.config.tests.target,
    )
    try:
        target_msg = await reposter.funcs.handle.run_excepted(
            resender.resend_anything,
            to_raise=True,
        )
    except reposter.core.types.SkipError:
        return f'skipped restrict=True {resender.media_value} {resender.link}'
    except pyrogram.errors.PremiumAccountRequired:
        return f'preium required {resender.link}'
    links = reposter.funcs.other.double_links(
        source_msg=source_msg,
        target_msg=target_msg,
    )
    return f'restrict=True {resender.media_value} {links}'

