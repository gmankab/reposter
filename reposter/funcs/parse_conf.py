from reposter.core import common, config
from pathlib import Path
import json
import os


def write_config(
    dict_to_write: dict,
) -> None:
    str_to_write = json.dumps(
        obj=dict_to_write,
        indent=4,
        ensure_ascii=False,
    )
    common.path.config_json.write_text(
        data=str_to_write,
        encoding='utf-8'
    )


def read_config() -> None:
    if common.path.config_json.exists():
        should_write: bool = False
        loaded_config: dict = json.loads(
            common.path.config_json.read_text()
        )
        assert isinstance(loaded_config, dict)
        for key, value in config.default.items():
            if key not in loaded_config:
                loaded_config[key] = value
                should_write = True
        if should_write:
            write_config(loaded_config)
    else:
        write_config(config.default)
        loaded_config = config.default
    for key, val in loaded_config.items():
        setattr(config.json, key, val)


def read_env() -> None:
    for key in config.env.__annotations__.keys():
        value = os.getenv(key) or ''
        assert isinstance(value, str)
        setattr(config.env, key, value)
    if config.env.reposter_data_dir:
        common.path.data_dir = Path(config.env.reposter_data_dir)
    if config.env.XDG_DATA_HOME:
        common.path.data_dir = Path(config.env.XDG_DATA_HOME) / common.app.name
    else:
        common.path.data_dir = common.path.config_json = common.path.app_dir / 'data'
    if config.env.reposter_conf:
        assert config.env.reposter_conf.endswith('.json')
        common.path.config_json = Path(config.env.reposter_conf)
    elif config.env.reposter_data_dir:
        common.path.config_json = common.path.data_dir / 'config.json'
    elif config.env.XDG_CONFIG_HOME:
        common.path.config_json = Path(config.env.XDG_CONFIG_HOME) / common.app.name / 'reposter.json'
    else:
        common.path.config_json = common.path.data_dir / 'config.json'
    common.path.data_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    common.path.config_json.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    common.path.errors_dir = common.path.data_dir / 'error'
    assert common.path.data_dir.is_dir()

