from reposter.core.config import env
import reposter.handlers.on_msg
import reposter.funcs.other
import reposter.tg.history


async def main() -> None:
    assert env.source
    assert env.target
    assert env.msg_start
    assert env.msg_stop
    assert env.msg_start.isdigit()
    assert env.msg_stop.isdigit()
    started = False
    on_msg = reposter.handlers.on_msg.OnMsg(
        target_any=reposter.funcs.other.chat_str_fix(env.target)
    )
    async for msg in reposter.tg.history.get_msgs(
        from_chat=reposter.funcs.other.chat_str_fix(env.source),
        start=int(env.msg_start),
        stop=int(env.msg_stop),
    ):
        started = True
        await on_msg.on_new_msg(_=None, src_msg=msg)
    if not started:
        raise AssertionError(
            f'bot should be in {env.source} chat and should have access to messages'
        )

