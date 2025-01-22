import reposter.core.common
import reposter.core.types
import pyrogram.types
import typing


async def parse_targets(
    target_any: reposter.core.types.target,
    to_call: typing.Callable,
) -> None:
    if isinstance(target_any, list):
        for subtarget in target_any:
            assert isinstance(subtarget, (str, int))
            await to_call(
                target=subtarget,
            )
    elif isinstance(target_any, (str, int)):
        await to_call(
            target=target_any,
        )
    else:
        raise AssertionError


async def on_logs_chat_msg(
    _,
    src_msg: pyrogram.types.Message,
) -> None:
    if src_msg.text in ['/s', '/stop']:
        if reposter.core.common.tg.stream_notificating_now:
            reposter.core.common.tg.stream_notificating_now = False
            await src_msg.reply('notifications are successfully stopped')
        else:
            await src_msg.reply('notifications are already stopped')

