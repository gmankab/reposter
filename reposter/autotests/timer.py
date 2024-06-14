from reposter.core import common
import reposter.core.types
import datetime


async def timer(
    to_run: reposter.core.types.cor_str,
) -> None:
    start = datetime.datetime.now()
    error: str = ''
    msg: str = ''
    try:
        msg = await to_run
    except reposter.core.types.NotPassedError as e:
        common.app.exit_code = 1
        error = e.msg
    except Exception as e:
        common.app.exit_code = 1
        raise e
    end = datetime.datetime.now()
    delta = end - start
    ms = int(delta.total_seconds() * 1000)
    if msg:
        common.log(
            f'[green]\\[passed] {ms} ms[/] {msg}'
        )
    else:
        common.log(
            f'[red]\\[error] {ms} ms[/] {error}'
        )

