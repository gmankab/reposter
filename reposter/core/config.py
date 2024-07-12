class tests:
    source: str = '@autotests_source'
    target: str = '@autotests_target'
    min_id: int = 107
    max_id: int = 121


class env:
    XDG_CONFIG_HOME: str
    XDG_DATA_HOME: str
    session_name: str
    reposter_data_dir: str
    reposter_conf: str
    tg_session: str
    big_tests: str
    tests: str


class json:
    api_id: int
    api_hash: str
    tg_session: str
    drop_author: bool
    logs_chat: str | int
    online_status_every_seconds: int
    stream_notify_chats: list
    chats: dict


default = {
    'api_id': 0,
    'api_hash': '',
    'tg_session': '',
    'drop_author': True,
    'logs_chat': 'me',
    'online_status_every_seconds': 0,
    'stream_notify_chats': [],
    'chats': {
        tests.source: tests.target,
    }
}

