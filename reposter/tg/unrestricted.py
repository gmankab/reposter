import pyrogram.types
import pyrogram.errors


async def forward(
    source_msg: pyrogram.types.Message,
    target_chat: int | str,
    drop_author: bool = True,
) -> None:
    if drop_author:
        if source_msg.venue:
            pass
            '''
            # pyrogram can't forward venue dropping author, so reposter resending it
            await resend()
            '''
            return
        if source_msg.poll:
            pass
            '''
            # pyrogram lib can\'t forward poll dropping author, so reposter resending it',
            await resend()
            '''
            return
    await source_msg.forward(
        chat_id=target_chat,
        drop_author=drop_author,
    )

