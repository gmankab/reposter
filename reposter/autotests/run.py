from reposter.autotests import restricted, unrestricted, timer
import reposter.funcs.other
import reposter.core.common
import reposter.tg.history
import asyncio
import typing


async def main():
    to_run_list: list[typing.Coroutine] = [
    ]
    async for msg in reposter.tg.history.get_msgs(
        from_chat='@tgparse_chat',
        min_id=107,
        max_id=116,
    ):
        to_run_list.append(timer.timer(unrestricted.unrestricted(msg)))
        to_run_list.append(timer.timer(restricted.restricted(msg)))
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

