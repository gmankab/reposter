from reposter.core import common
import reposter.funcs.logging
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
    except Exception:
        common.app.exit_code = 1
        reposter.funcs.logging.write_error()
    end = datetime.datetime.now()
    delta = end - start
    sec = delta.total_seconds()
    if msg:
        common.log(
            f'[green]\\[passed] {sec:.3f} sec[/] {msg}'
        )
    else:
        common.log(
            f'[red]\\[error] {sec:.3f} sec[/] {error}'
        )

