import reposter.funcs.other
import reposter.core.common
import reposter.core.config
import reposter.tg.history
import asyncio
import typing
from reposter.autotests import (
    restricted,
    unrestricted,
    pyright,
    timer,
    ruff,
)


async def main():
    to_run_list: list[typing.Coroutine] = []
    to_timer_list: list[typing.Coroutine] = [
        pyright.pyright(),
        ruff.ruff(),
    ]
    async for msg in reposter.tg.history.get_msgs(
        from_chat=reposter.core.config.tests.source,
        min_id=107,
        max_id=116,
    ):
        to_timer_list.append(unrestricted.unrestricted(msg))
        to_timer_list.append(restricted.restricted(msg))
    for to_timer in to_timer_list:
        to_run_list.append(timer.timer(to_timer))
    tasks = asyncio.gather(*to_run_list)
    try:
        await asyncio.wait_for(
            tasks,
            timeout=360,
        )
        await tasks
    except asyncio.TimeoutError:
        print('timed out')
    await reposter.funcs.other.shutdown()

