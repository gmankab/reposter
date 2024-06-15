class tests:
    source: str = '@autotests_source'
    target: str = '@autotests_target'
    min_id: int = 107
    max_id: int = 121


class env:
    XDG_CONFIG_HOME: str
    XDG_DATA_HOME: str
    reposter_data_dir: str
    reposter_conf: str
    big_tests: str
    tests: str


class json:
    api_id: int
    api_hash: str
    tg_session: str
    drop_author: bool
    chats: dict


default = {
    'api_id': 0,
    'api_hash': '',
    'tg_session': '',
    'drop_author': True,
    'chats': {
        tests.source: tests.target,
    }
}

