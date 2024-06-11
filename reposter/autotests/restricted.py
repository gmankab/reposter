from reposter.core import common
import reposter.tg.unrestricted
import reposter.tg.restricted
import reposter.core.types
import reposter.funcs.handle


async def restricted() -> str:
    msgs_list = await common.tg.client.get_messages(
        chat_id='@tgparse_chat',
        message_ids=range(2, 13),
    )
    assert isinstance(msgs_list, list)
    for msg in msgs_list:
        if msg.empty:
            continue
        resender = reposter.tg.restricted.Resender(
            source_msg=msg,
            target_chat='me',
            remove_progress_bar=False,
        )
        await resender.resend_anything()
    return 'restricted respost test passed'

