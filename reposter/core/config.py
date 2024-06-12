class env:
    XDG_CONFIG_HOME: str
    XDG_DATA_HOME: str
    reposter_data_dir: str
    reposter_conf: str
    tests: str


class json:
    api_id: int
    api_hash: str
    tg_session: str


default = {
    'api_id': 0,
    'api_hash': '',
    'tg_session': '',
}

