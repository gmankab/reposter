import reposter.tg.history
import reposter.core.config
from reposter.autotests import(
    unrestricted,
    restricted,
    timer,
)


async def test_all() -> str:
    started = False
    async for msg in reposter.tg.history.get_msgs(
        from_chat=reposter.core.config.tests.source,
        start=reposter.core.config.tests.max_id,
        stop=reposter.core.config.tests.min_id,
    ):
        started = True
        await timer.timer(unrestricted.unrestricted(msg, True))
        await timer.timer(unrestricted.unrestricted(msg, False))
        await timer.timer(restricted.restricted(msg))
    if not started:
        raise AssertionError(
            f'bot should be in {reposter.core.config.tests.source} and should have access to messages'
        )
    return 'messages tests'

