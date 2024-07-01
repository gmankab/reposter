from reposter.core import common
from pathlib import Path
import reposter.core.types
import pyrogram.errors
import datetime
import inspect
import asyncio
import typing


def get_now() -> float:
    return datetime.datetime.now().timestamp()


async def wait_the_flood_wait(
    seconds: int,
):
    started = get_now()
    task_id = common.app.progress.add_task(
        description=f'floodwait for {seconds}s',
        total=seconds,
    )
    while True:
        completed = get_now() - started
        if completed > seconds:
            break
        common.app.progress.update(
            task_id=task_id,
            completed=completed,
        )
        await asyncio.sleep(0.2)
    common.app.progress.update(
        task_id=task_id,
        visible=False,
    )
    common.app.progress.stop_task(
        task_id=task_id,
    )


def get_caller(
    parents: int,
):
    caller = inspect.currentframe()
    assert caller
    for _ in range(parents + 1):
        caller = caller.f_back
        assert caller
    file = Path(caller.f_code.co_filename)
    return f'{file.name}:{caller.f_lineno}'


async def run_excepted(
    callable: typing.Callable,
    to_raise: bool = True,
    **kwargs,
) -> typing.Any:
    parents = 1
    while common.tg.floodwait:
        await asyncio.sleep(common.tg.floodwait)
    while True:
        try:
            return await callable(**kwargs)
        except pyrogram.errors.FloodWait as flood_to_wait:
            assert isinstance(flood_to_wait.value, int)
            common.tg.floodwait = flood_to_wait.value
            file_str = get_caller(parents)
            await wait_the_flood_wait(
                seconds=flood_to_wait.value,
            )
            common.tg.floodwait = 0
        except reposter.core.types.SkipError as error:
            raise error
        except Exception as error:
            if to_raise:
                raise error
            else:
                file_str = get_caller(parents)
                common.log(
                    f'[yellow]\\[warn][/] name={callable.__name__}, file={file_str}, error={error}'
                )
                return

