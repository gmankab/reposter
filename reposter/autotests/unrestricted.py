import reposter.tg.unrestricted
import reposter.funcs.handle
import reposter.core.config
import pyrogram.types


async def unrestricted(
    msg: pyrogram.types.Message
) -> str:
    await reposter.funcs.handle.run_excepted(
        callable=reposter.tg.unrestricted.forward,
        source_msg=msg,
        target_chat=reposter.core.config.tests.target,
    )
    if msg.media:
        media = msg.media.value
    else:
        media = 'no_media'
    if msg.chat.username:
        link = f'{msg.chat.username}/{msg.id}'
    else:
        link = f'{msg.chat.full_name}/{msg.id}'
    return f'unrestricted {media} {link}'

