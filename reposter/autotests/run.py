import reposter.funcs.other
import reposter.core.common
import reposter.core.config
import reposter.tg.history
import asyncio
import typing
from reposter.autotests import (
    pyright,
    timer,
    ruff,
    msgs,
)


async def main():
    to_run_list: list[typing.Coroutine] = []
    to_timer_list: list[typing.Coroutine] = [
        msgs.test_all(),
        pyright.pyright(),
        ruff.ruff(),
    ]
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

