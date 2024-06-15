import reposter.funcs.handle
import reposter.core.config
import reposter.core.common
import pyrogram.types


async def unrestricted(
    msg: pyrogram.types.Message,
    drop_author: bool,
) -> str:
    await reposter.funcs.handle.run_excepted(
        msg.forward,
        chat_id=reposter.core.config.tests.target,
        drop_author=drop_author,
    )
    if msg.media:
        media = msg.media.value
    else:
        media = 'no_media'
    if msg.chat.username:
        link = f'{msg.chat.username}/{msg.id}'
    else:
        link = f'{msg.chat.full_name}/{msg.id}'
    return f'restrict=False drop={drop_author} {media} {link}'

