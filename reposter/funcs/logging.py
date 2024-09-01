from pathlib import Path
import reposter.core.common
import reposter.funcs.suppress
import reposter.funcs.other
import pyrogram.types
import rich.console
import datetime


def generate_filename(
    dir_path: Path,
    max_files_in_dir: int = 30,
    extension: str = 'txt',
) -> Path:
    dir_path.mkdir(
        exist_ok = True,
        parents = True,
    )
    all_files = list(
        dir_path.iterdir()
    )
    all_files.sort()
    while len(
        all_files
    ) >= max_files_in_dir:
        all_files[0].unlink()
        all_files.remove(all_files[0])
    file_date = datetime.datetime.now().strftime('%Y.%m.%d_%H.%M')
    test_file_path = dir_path / file_date
    file_path = Path(
        f'{test_file_path}.{extension}'
    )
    index = 2
    while file_path.exists():
        file_path = Path(
            f'{test_file_path}_{index}.{extension}'
        )
        index += 1
    return file_path


def write_error(
    print_error: bool = True,
    write_to_disk: bool = True,
    print_file_path: bool = True,
) -> None:
    error_path = generate_filename(
        dir_path=reposter.core.common.path.errors_dir,
    )
    with error_path.open(
        'w',
        encoding='utf-8',
    ) as file:
        if print_error:
            reposter.core.common.app.console.print_exception(
                show_locals=False,
                suppress=reposter.funcs.suppress.suppress
            )
        if write_to_disk:
            file_console = rich.console.Console(
                width = 80,
                file = file,
            )
            file_console.print_exception(
                show_locals=False,
                suppress=reposter.funcs.suppress.suppress
            )
        if print_file_path:
            reposter.core.common.app.console.log(
                f'[red]\\[error][/] {error_path}'
            )

def log_msg(
    to_log: str,
    src_msg: pyrogram.types.Message,
    target_msg: pyrogram.types.Message,
):
    links = reposter.funcs.other.double_links(
        src_msg=src_msg,
        target_msg=target_msg,
    )
    to_log += f' {links}'
    if src_msg.media:
        to_log += f' media={src_msg.media.value}'
    to_add = ''
    if src_msg.text:
        to_add = src_msg.text
    elif src_msg.caption:
        to_add = src_msg.caption
    if to_add:
        if len(to_add) > 30:
            to_add = f'{to_add[:30]}…'
        to_add = to_add.replace('\n', '')
        to_log += f" text='{to_add}'"
    reposter.core.common.log(to_log)

