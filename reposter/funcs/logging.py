from pathlib import Path
import reposter.core.common
import reposter.funcs.suppress
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

