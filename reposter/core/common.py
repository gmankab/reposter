from pathlib import Path
import importlib.metadata
import pyrogram.client
import rich.progress
import rich.console
import tomllib


class path:
    app_dir = Path(__file__).parent.parent.parent.resolve()
    pyproject_toml: Path = app_dir / 'pyproject.toml'
    config_json: Path
    data_dir: Path
    errors_dir: Path


class app:
    if path.pyproject_toml.exists():
        with path.pyproject_toml.open('rb') as file:
            project = tomllib.load(file)['project']
        version: str = project['version']
        name: str = project['name']
    else:
        name: str = path.app_dir.name
        version: str = importlib.metadata.version(name)
    console: rich.console.Console = rich.console.Console()
    progress: rich.progress.Progress
    exit_code: int = 0


class tg:
    client: pyrogram.client.Client
    floodwait: int = 0


log = app.console.log

