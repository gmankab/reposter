from reposter.core.common import log, app
from pathlib import Path
import pyrogram.errors
import datetime
import inspect
import asyncio
import typing


def get_now() -> float:
    return datetime.datetime.now().timestamp()


async def wait_the_flood_wait(
    seconds: int,
    method_name: str,
    file_str,
):
    log(f'[yellow]\\[floodwait][/] {seconds}s by {method_name} in {file_str}')
    started = get_now()
    task_id = app.progress.add_task(
        description=f'floodwait for {seconds}s',
        total=seconds,
    )
    while True:
        completed = get_now() - started
        if completed > seconds:
            break
        app.progress.update(
            task_id=task_id,
            completed=completed,
        )
        await asyncio.sleep(0.2)
    app.progress.update(
        task_id=task_id,
        visible=False,
    )
    app.progress.stop_task(
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
    **kwargs,
) -> typing.Any:
    parents = 1
    while True:
        try:
            return await callable(**kwargs)
        except pyrogram.errors.FloodWait as flood_to_wait:
            assert isinstance(flood_to_wait.value, int)
            file_str = get_caller(parents)
            await wait_the_flood_wait(
                seconds=flood_to_wait.value,
                method_name=callable.__name__,
                file_str=file_str,
            )
        except Exception as error:
            file_str = get_caller(parents)
            log(
                f'[yellow]\\[warn][/] name={callable.__name__}, file={file_str}, error={error}'
            )
            return

