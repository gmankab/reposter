from pathlib import Path
import pyrogram.client
import importlib.metadata
import rich.progress
import rich.console
import tomllib


class path:
    app = Path(__file__).parent.parent.parent.resolve()
    data = app / 'data'
    pyproject = app / 'pyproject.toml'
    data.mkdir(
        exist_ok=True,
        parents=True,
    )


class app:
    if path.pyproject.exists():
        with path.pyproject.open('rb') as file:
            project = tomllib.load(file)['project']
        version: str = project['version']
        name: str = project['name']
    else:
        name: str = path.app.name
        version: str = importlib.metadata.version(name)
    console: rich.console.Console = rich.console.Console()
    progress: rich.progress.Progress


class tg:
    client: pyrogram.client.Client


log = app.console.log

