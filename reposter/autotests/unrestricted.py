import reposter.funcs.other
import reposter.funcs.handle
import reposter.core.config
import reposter.core.common
import pyrogram.types


async def unrestricted(
    source_msg: pyrogram.types.Message,
    drop_author: bool,
) -> str:
    target_msg = await reposter.funcs.handle.run_excepted(
        source_msg.forward,
        chat_id=reposter.core.config.tests.target,
        drop_author=drop_author,
    )
    if source_msg.media:
        media = source_msg.media.value
    else:
        media = 'no_media'
    links = reposter.funcs.other.double_links(
        source_msg=source_msg,
        target_msg=target_msg,
    )
    return f'restrict=False drop={drop_author} {media} {links}'

