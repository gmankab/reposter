import reposter.tg.restricted
import reposter.funcs.handle
import reposter.core.config
import reposter.core.types
import pyrogram.errors
import pyrogram


async def restricted(
    msg: pyrogram.types.Message
) -> str:
    resender = reposter.tg.restricted.Resender(
        source_msg=msg,
        target_chat=reposter.core.config.tests.target,
    )
    try:
        await reposter.funcs.handle.run_excepted(
            resender.resend_anything,
            to_raise=True,
        )
    except reposter.core.types.SkipError:
        return f'skipped restrict=True {resender.media_value} {resender.link}'
    except pyrogram.errors.PremiumAccountRequired:
        return f'preium required {resender.link}'
    return f'restrict=True {resender.media_value} {resender.link}'

