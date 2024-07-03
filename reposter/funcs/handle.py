from reposter.core import common
from pathlib import Path
import reposter.core.types
import pyrogram.errors
import rich.progress
import datetime
import inspect
import asyncio
import typing


def get_now() -> float:
    return datetime.datetime.now().timestamp()


async def wait_the_flood_wait(
    seconds: int,
) -> None:
    await wait(
        seconds=seconds,
        text=f'floodwait for {seconds}s',
)


async def wait(
    seconds: int,
    text: str = '',
    hide = True,
    task_id: rich.progress.TaskID | None = None,
) -> None:
    started = get_now()
    if not task_id:
        if not text:
            text = f'{seconds} seconds timeout'
        task_id = common.app.progress.add_task(
            description=text,
            total=seconds,
        )
    while True:
        completed = get_now() - started
        if completed > seconds:
            break
        common.app.progress.update(
            task_id=task_id,
            completed=completed,
            total=seconds,
        )
        await asyncio.sleep(0.2)
    common.app.progress.update(
        task_id=task_id,
        completed=seconds,
        total=seconds,
    )
    if hide:
        common.app.progress.update(
            task_id=task_id,
            visible=False,
        )
        common.app.progress.stop_task(
            task_id=task_id,
        )


def get_caller(
    parents: int,
) -> str:
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
    repeat: bool = True,
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
            await wait_the_flood_wait(
                seconds=flood_to_wait.value,
            )
            common.tg.floodwait = 0
            if not repeat:
                file_str = get_caller(parents)
                common.log(
                    f'[yellow]\\[warn][/] name={callable.__name__}, file={file_str}, error={flood_to_wait}'
                )
                return
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

