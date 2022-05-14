from pathlib import Path
import stat
import sys
import os


def clean_path(path):
    path = str(path).replace('\\', '/')
    # conerting a\\b///\\\c\\/d/e/ to a//b//////c///d/e/

    # conerting a//b//////c///d/e/ to a/b/c/d/e/
    while '//' in path:
        path = path.replace('//', '/')
    return path


def parrent(
    file,
    depth = 1,
):
    path = Path(file).resolve()
    for _ in range(depth):
        path = path.parent
    return clean_path(
        path
    )


def mkdir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)


def auto_rename(file):
    file = Path(file)
    ls = os.listdir(file.parent)
    count = 0
    new_name = file.name
    while new_name in ls:
        count += 1
        new_name = f'{file.parent}/{file.stem}{count}{file.suffix}'
    os.rename(file, new_name)
    return clean_path(Path(file.parent, new_name))


def restart():
    command = f'{sys.executable} {sys.argv[0]}'
    globals().clear()
    import os as new_os
    import sys as new_sys
    new_os.system(command)
    new_sys.exit()


def rmtree(dir):
    try:
        for root, dirs, files in os.walk(
            dir,
            topdown=False,
        ):
            for name in files:
                filename = os.path.join(
                    root,
                    name,
                )
                os.chmod(
                    filename,
                    stat.S_IWUSR,
                )
                os.remove(filename)
            for name in dirs:
                os.rmdir(
                    os.path.join(
                        root,
                        name,
                    )
                )
    except PermissionError as error:
        raise PermissionError(
            f'Can\'t remove dir "{dir}", no permissions. Try remove it yourself'
        ) from error


def text_wrap(
    text: str,
    chunk_size: int = 4000,
):
    for chunk_start in range(0, len(text), chunk_size):
        yield text[chunk_start:chunk_start + chunk_size]
